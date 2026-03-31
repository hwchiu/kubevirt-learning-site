# virt-controller

virt-controller 是 KubeVirt 的**叢集級控制平面**，內建多個控制器（Controller），負責管理 VM、VMI、Migration、Snapshot 等資源的完整生命週期。

## 職責概述

```
virt-controller
├── VM Controller       — 管理 VirtualMachine 狀態
├── VMI Controller      — 管理 VMI → Pod 的對應關係
├── Migration Controller— 協調 Live Migration
├── ReplicaSet Controller— 管理 VMI 副本數
├── Pool Controller     — 管理 VirtualMachinePool
├── Node Controller     — 同步節點拓樸資訊
├── Evacuation Controller— 處理節點疏散 (Drain)
└── Snapshot Controller — 管理 VM 快照/還原
```

## 部署資訊

| 項目 | 值 |
|------|-----|
| 部署型態 | Kubernetes Deployment |
| 副本數 | ≥ 2 (Leader Election，只有一個 active) |
| Metrics Port | 8182 |
| Leader Election Port | 8443 |
| Namespace | `kubevirt` |

## 核心資料結構

```go
// pkg/virt-controller/watch/application.go
type VirtControllerApp struct {
    service.ServiceListen
    clientSet        kubecli.KubevirtClient
    templateService  *services.TemplateService   // 產生 Pod template

    // 各個 Controller
    nodeController        *node.Controller
    vmiController         *vmi.Controller
    rsController          *replicaset.Controller
    poolController        *pool.Controller
    vmController          *vm.Controller
    migrationController   *migration.Controller
    evacuationController  *evacuation.EvacuationController

    // 快取 (Informers)
    vmiCache          cache.Store
    vmiInformer       cache.SharedIndexInformer
    vmInformer        cache.SharedIndexInformer
    migrationInformer cache.SharedIndexInformer
    podInformer       cache.SharedIndexInformer

    clusterConfig *virtconfig.ClusterConfig
    leaderElector *leaderelection.LeaderElector
}
```

## VMI 控制器深度解析

VMI 控制器是最核心的控制器，負責確保每個 VMI 都有對應的 Pod 執行。

```go
// pkg/virt-controller/watch/vmi/vmi.go
type Controller struct {
    templateService  templateService           // 產生 Pod spec
    clientset        kubecli.KubevirtClient

    // Work Queue — 待處理的 VMI key (namespace/name)
    Queue workqueue.TypedRateLimitingInterface[string]

    vmiIndexer   cache.Indexer    // VMI 快取索引
    vmStore      cache.Store      // VM 快取
    podIndexer   cache.Indexer    // Pod 快取索引
    migrationIndexer cache.Indexer

    topologyHinter topology.Hinter   // NUMA 拓樸提示

    // Expectations — 追蹤預期的 Pod 建立/刪除
    // 避免在 Pod 還未出現在快取時重複建立
    podExpectations *controller.UIDTrackingControllerExpectations
    vmiExpectations *controller.UIDTrackingControllerExpectations
}
```

### VMI 協調邏輯

```go
func (c *Controller) sync(vmi *v1.VirtualMachineInstance, pod *k8sv1.Pod) error {

    // 狀態：VMI 剛建立，無對應 Pod
    if pod == nil && !vmi.IsFinal() {
        // 建立 virt-launcher Pod
        templatePod, err := c.templateService.RenderLaunchManifest(vmi)
        c.clientset.CoreV1().Pods(vmi.Namespace).Create(templatePod)
    }

    // 狀態：Pod 已啟動，更新 VMI nodeName
    if pod != nil && pod.Status.Phase == Running {
        if vmi.Status.NodeName == "" {
            vmi.Status.NodeName = pod.Spec.NodeName
            c.clientset.VirtV1().VirtualMachineInstances(ns).Update(vmi)
        }
    }

    // 狀態：VMI 被刪除
    if vmi.DeletionTimestamp != nil {
        // 刪除對應的 Pod
        c.clientset.CoreV1().Pods(ns).Delete(pod.Name)
    }

    // 更新 VMI 狀態 (phase, conditions, etc.)
    c.updateVMIStatus(vmi, pod)
}
```

### 多控制器執行緒數

```go
// 每個 Controller 的 Worker Goroutine 數量
var (
    vmiControllerThreads        = 10  // VMI 最多，因為最頻繁
    vmControllerThreads         = 3
    migrationControllerThreads  = 3
    rsControllerThreads         = 3
    poolControllerThreads       = 3
    nodeControllerThreads       = 3
    evacuationControllerThreads = 3
    snapshotControllerThreads   = 6   // 快照需要較多並發
)
```

## VM 控制器

```go
// pkg/virt-controller/watch/vm/vm.go
func (c *Controller) sync(vm *v1.VirtualMachine) error {

    vmi, err := c.getVMI(vm)

    // 計算期望狀態
    if c.shouldStartVM(vm) && vmi == nil {
        // 從 VM template 建立 VMI
        vmi := c.createVMIFromVM(vm)
        c.clientset.VirtV1().VirtualMachineInstances(ns).Create(vmi)
    }

    if c.shouldStopVM(vm) && vmi != nil {
        // 刪除 VMI (會觸發 VM 關機)
        c.clientset.VirtV1().VirtualMachineInstances(ns).Delete(vmi.Name)
    }

    // 處理 DataVolumeTemplates (建立/刪除 DataVolume)
    c.handleDataVolumeTemplates(vm)

    // 更新 VM status
    c.updateVMStatus(vm, vmi)
}
```

### shouldStartVM 邏輯

```go
func (c *Controller) shouldStartVM(vm *v1.VirtualMachine) bool {
    switch *vm.Spec.RunStrategy {
    case Always:
        return true  // 永遠確保 VMI 存在
    case Halted:
        return false // 從不自動啟動
    case Manual:
        return vm.hasStartRequest()  // 檢查 StateChangeRequests
    case RerunOnFailure:
        return vm.lastVMIFailedOrMissing()  // 失敗後重啟
    case Once:
        return !vm.hasRunBefore()   // 只跑一次
    }
}
```

## Migration 控制器

```go
// pkg/virt-controller/watch/migration/migration.go
func (c *Controller) sync(migration *v1.VirtualMachineInstanceMigration) error {

    vmi := c.getVMI(migration.Spec.VMIName)

    switch migration.Status.Phase {

    case Pending:
        // 選定目標節點
        // 建立目標 virt-launcher Pod
        targetPod := c.createTargetPod(vmi, migration)

    case PreparingTarget:
        // 等待目標 Pod 準備完成
        // 呼叫 virt-handler 準備目標端

    case TargetReady:
        // 通知 virt-handler 開始遷移
        // virt-handler 呼叫 libvirt migrate API

    case Running:
        // 監控遷移進度
        // 更新 migration status

    case Succeeded:
        // 刪除來源 Pod
        // 更新 VMI nodeName → 目標節點

    case Failed:
        // 清理目標 Pod
        // 更新 VMI status
    }
}
```

## Node 控制器

負責同步節點的 CPU 拓撲、記憶體、設備資訊，供調度時使用：

```go
// 更新節點標籤，例如：
// kubevirt.io/schedulable = true
// kubevirt.io/cpu-model = Skylake-Client
// kubevirt.io/cpu-feature-vmx = true
// kubevirt.io/memory.numa.hugepages-2Mi = 512
```

## Work Queue 機制

所有控制器都使用 Kubernetes 的 **Rate-Limiting Work Queue**：

```
事件觸發 (Add/Update/Delete)
    │
    ▼
Informer Callback
    │ 將 "namespace/name" 加入 Queue
    ▼
Work Queue
    │ (有 Rate Limiting: 指數退避)
    ▼
Worker Goroutine
    │ 取出 key，執行協調邏輯
    ▼
Execute() → sync()
    │
    ▼
成功 → 不重新入列
失敗 → 重新入列 (with backoff)
```

**指數退避範例：**
```
第 1 次失敗 → 1 秒後重試
第 2 次失敗 → 2 秒後重試
第 3 次失敗 → 4 秒後重試
...最長不超過 16 秒
```

## Leader Election

```go
// 只有 Leader 才會執行協調邏輯
// 透過 Kubernetes Lease 實現
// 
// 預設設定：
// - Lease Duration: 15 秒
// - Renew Deadline: 10 秒
// - Retry Period:    2 秒
//
// 可透過 virt-controller --leader-election-* 參數調整
```

## 重要原始碼位置

| 功能 | 路徑 |
|------|------|
| 主程式入口 | `cmd/virt-controller/main.go` |
| Application 結構 | `pkg/virt-controller/watch/application.go` |
| VMI 控制器 | `pkg/virt-controller/watch/vmi/vmi.go` |
| VM 控制器 | `pkg/virt-controller/watch/vm/vm.go` |
| Migration 控制器 | `pkg/virt-controller/watch/migration/` |
| ReplicaSet 控制器 | `pkg/virt-controller/watch/replicaset/` |
| Pool 控制器 | `pkg/virt-controller/watch/pool/` |
| Snapshot 控制器 | `pkg/virt-controller/watch/snapshot/` |
| Pod Template 服務 | `pkg/virt-controller/services/` |
