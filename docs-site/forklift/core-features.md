---
layout: doc
---

# Forklift — 核心功能分析

本章深入剖析 Forklift 的六大核心功能模組：Provider 抽象層、遷移排程演算法、Warm Migration 增量遷移、virt-v2v 磁碟轉換、Network Mapping 以及 Storage Mapping 與 XCOPY Offload。每個段落皆附有原始碼引用與流程圖解，協助讀者理解系統內部運作。

::: info 相關章節
- [系統架構](./architecture) — 專案總覽、目錄結構、Binary 入口
- [控制器與 API](./controllers-api) — Controller 架構、CRD 型別、Webhook
- [外部整合](./integration) — KubeVirt/CDI/vSphere/oVirt/OpenStack 整合
:::

---

## 1. Provider 抽象層

Forklift 透過 **Factory + Strategy** 設計模式，為每個來源平台提供統一的遷移介面。所有 Provider 都實作同一套介面，Controller 端僅需透過 Factory 取得對應的 Adapter 即可操作。

### 1.1 Factory 入口

`adapter.New()` 根據 Provider 類型回傳對應的 Adapter 實作：

```go
// 檔案: pkg/controller/plan/adapter/doc.go

type Adapter = base.Adapter
type Builder = base.Builder
type Ensurer = base.Ensurer
type Client = base.Client
type Validator = base.Validator
type DestinationClient = base.DestinationClient

// Adapter factory.
func New(provider *api.Provider) (adapter Adapter, err error) {
    switch provider.Type() {
    case api.VSphere:
        adapter = &vsphere.Adapter{}
    case api.OVirt:
        adapter = &ovirt.Adapter{}
    case api.OpenStack:
        adapter = &openstack.Adapter{}
    case api.OpenShift:
        adapter = &ocp.Adapter{}
    case api.Ova:
        adapter = &ova.Adapter{}
    case api.EC2:
        adapter = ec2adapter.New()
    case api.HyperV:
        adapter = &hyperv.Adapter{}
    default:
        err = liberr.New("provider not supported.")
    }
    return
}
```

### 1.2 核心介面定義

`base.Adapter` 是頂層抽象，負責建構 Provider 專屬的 Builder、Client、Validator 等子元件：

```go
// 檔案: pkg/controller/plan/adapter/base/doc.go

// Adapter API.
// Constructs provider-specific implementations
// of the Builder, Client, and Validator.
type Adapter interface {
    Builder(ctx *plancontext.Context) (Builder, error)
    Client(ctx *plancontext.Context) (Client, error)
    Validator(ctx *plancontext.Context) (Validator, error)
    DestinationClient(ctx *plancontext.Context) (DestinationClient, error)
    Ensurer(ctx *plancontext.Context) (ensure Ensurer, err error)
}
```

**Builder** 負責建構遷移所需的 Kubernetes 資源（Secret、ConfigMap、DataVolume、VirtualMachine 等），共定義了 22 個方法：

```go
// 檔案: pkg/controller/plan/adapter/base/doc.go

type Builder interface {
    Secret(vmRef ref.Ref, in, object *core.Secret) error
    ConfigMap(vmRef ref.Ref, secret *core.Secret, object *core.ConfigMap) error
    VirtualMachine(vmRef ref.Ref, object *cnv.VirtualMachineSpec,
        persistentVolumeClaims []*core.PersistentVolumeClaim,
        usesInstanceType bool, sortVolumesByLibvirt bool) error
    DataVolumes(vmRef ref.Ref, secret *core.Secret, configMap *core.ConfigMap,
        dvTemplate *cdi.DataVolume, vddkConfigMap *core.ConfigMap) (dvs []cdi.DataVolume, err error)
    Tasks(vmRef ref.Ref) ([]*planapi.Task, error)
    TemplateLabels(vmRef ref.Ref) (labels map[string]string, err error)
    PodEnvironment(vmRef ref.Ref, sourceSecret *core.Secret) (env []core.EnvVar, err error)
    LunPersistentVolumes(vmRef ref.Ref) (pvs []core.PersistentVolume, err error)
    LunPersistentVolumeClaims(vmRef ref.Ref) (pvcs []core.PersistentVolumeClaim, err error)
    SupportsVolumePopulators() bool
    PopulatorVolumes(vmRef ref.Ref, annotations map[string]string, secretName string) ([]*core.PersistentVolumeClaim, error)
    PopulatorTransferredBytes(pvc *core.PersistentVolumeClaim) (transferredBytes int64, err error)
    ConversionPodConfig(vmRef ref.Ref) (*ConversionPodConfigResult, error)
    // ... 其餘方法省略
}
```

**Client** 負責與來源平台互動，管理 VM 電源、快照與磁碟操作：

```go
// 檔案: pkg/controller/plan/adapter/base/doc.go

type Client interface {
    PowerOn(vmRef ref.Ref) error
    PowerOff(vmRef ref.Ref) error
    PowerState(vmRef ref.Ref) (planapi.VMPowerState, error)
    PoweredOff(vmRef ref.Ref) (bool, error)
    CreateSnapshot(vmRef ref.Ref, hostsFunc util.HostsFunc) (string, string, error)
    RemoveSnapshot(vmRef ref.Ref, snapshot string, hostsFunc util.HostsFunc) (string, error)
    CheckSnapshotReady(vmRef ref.Ref, precopy planapi.Precopy, hosts util.HostsFunc) (bool, string, error)
    CheckSnapshotRemove(vmRef ref.Ref, precopy planapi.Precopy, hosts util.HostsFunc) (bool, error)
    SetCheckpoints(vmRef ref.Ref, precopies []planapi.Precopy, datavolumes []cdi.DataVolume,
        final bool, hostsFunc util.HostsFunc) error
    Finalize(vms []*planapi.VMStatus, planName string)
    DetachDisks(vmRef ref.Ref) error
    PreTransferActions(vmRef ref.Ref) (ready bool, err error)
    GetSnapshotDeltas(vmRef ref.Ref, snapshot string, hostsFunc util.HostsFunc) (map[string]string, error)
    Close()
}
```

**Validator** 執行 Provider 專屬的遷移前驗證，包含 17 個驗證方法：

```go
// 檔案: pkg/controller/plan/adapter/base/doc.go

type Validator interface {
    StorageMapped(vmRef ref.Ref) (bool, error)
    DirectStorage(vmRef ref.Ref) (bool, error)
    NetworksMapped(vmRef ref.Ref) (bool, error)
    MaintenanceMode(vmRef ref.Ref) (bool, error)
    WarmMigration() bool
    MigrationType() bool
    StaticIPs(vmRef ref.Ref) (bool, error)
    UdnStaticIPs(vmRef ref.Ref, client client.Client) (bool, error)
    SharedDisks(vmRef ref.Ref, client client.Client) (bool, string, string, error)
    ChangeTrackingEnabled(vmRef ref.Ref) (bool, error)
    HasSnapshot(vmRef ref.Ref) (bool, string, string, error)
    MacConflicts(vmRef ref.Ref) ([]MacConflict, error)
    GuestToolsInstalled(vmRef ref.Ref) (bool, error)
    // ... 其餘方法省略
}
```

### 1.3 Provider 實作對照

每個 Provider 的 Adapter 結構完全一致，差異在於子元件內部邏輯：

| Provider | 套件路徑 | Builder | Client | Validator |
|----------|---------|---------|--------|-----------|
| vSphere | `adapter/vsphere/` | ✅ VDDK + CDI DataVolume | ✅ 快照 + CBT | ✅ ChangeTracking、SharedDisks |
| oVirt | `adapter/ovirt/` | ✅ ImageIO 傳輸 | ✅ 快照管理 | ✅ DirectStorage (LUN/FC) |
| OpenStack | `adapter/openstack/` | ✅ Cinder Volume 傳輸 | ✅ Volume Snapshot | ✅ Storage/Network 驗證 |
| Hyper-V | `adapter/hyperv/` | ✅ VHD/VHDX 磁碟 | ✅ 電源管理 | ✅ StaticIPs 驗證 |
| OVA | `adapter/ova/` | ✅ OVA 檔案解析 | ✅ 基礎操作 | ✅ 格式驗證 |
| OpenShift | `adapter/ocp/` | ✅ PVC 複製 | ✅ VM 操作 | ✅ PVC/Network 驗證 |
| EC2 | `provider/ec2/` | ✅ EBS Snapshot | ✅ EC2 API | ✅ 磁碟格式驗證 |

![Forklift Provider Adapter 對照圖](/diagrams/forklift/forklift-provider-adapter.png)

### 1.4 ConversionPodConfig — Provider 層級的轉換 Pod 設定

每個 Provider 可透過 `ConversionPodConfig()` 方法注入 Node 選擇器、Labels 與 Annotations：

```go
// 檔案: pkg/controller/plan/adapter/base/doc.go

type ConversionPodConfigResult struct {
    // Provider 要求的 Node 選擇限制，會與 Plan.Spec.ConvertorNodeSelector 合併
    NodeSelector map[string]string
    // Provider 專用的 Labels
    Labels       map[string]string
    // Provider 專用的 Annotations
    Annotations  map[string]string
}
```

---

## 2. 遷移排程演算法

遷移排程是 Forklift 中最精密的演算法之一。不同 Provider 採用不同的排程策略，其中 **vSphere Scheduler** 最為複雜，實作了 per-host 磁碟數量節流機制。

### 2.1 vSphere Scheduler — Per-Host 磁碟節流

vSphere 的排程以 ESXi Host 為粒度，透過 `MaxInFlight` 限制每個 Host 同時傳輸的磁碟數量：

```go
// 檔案: pkg/controller/plan/scheduler/vsphere/scheduler.go

// Scheduler for migrations from ESX hosts.
type Scheduler struct {
    *plancontext.Context
    // Maximum number of disks per host that can be
    // migrated at once.
    MaxInFlight int
    // Mapping of hosts by ID to the number of disks
    // on each host that are currently being migrated.
    inFlight map[string]int
    // Mapping of hosts by ID to lists of VMs
    // that are waiting to be migrated.
    pending map[string][]*pendingVM
}

type pendingVM struct {
    status *plan.VMStatus
    cost   int
}
```

### 2.2 排程主流程 — Next()

`Next()` 方法以 **package-level mutex** 保護，防止多個 Reconcile 同時搶佔排程 slot：

```go
// 檔案: pkg/controller/plan/scheduler/vsphere/scheduler.go

var mutex sync.Mutex

func (r *Scheduler) Next() (vm *plan.VMStatus, hasNext bool, err error) {
    mutex.Lock()
    defer mutex.Unlock()
    err = r.buildSchedule()
    if err != nil {
        return
    }
    for _, vms := range r.schedulable() {
        if len(vms) > 0 {
            vm = vms[0].status
            hasNext = true
        }
    }
    return
}
```

### 2.3 buildInFlight() — 掃描所有同 Provider 的 Plan

此方法遍歷**所有 Plan**（不僅限於當前 Plan），累加每個 Host 正在傳輸的磁碟數：

```go
// 檔案: pkg/controller/plan/scheduler/vsphere/scheduler.go

func (r *Scheduler) buildInFlight() (err error) {
    r.inFlight = make(map[string]int)

    // 步驟 1: 計算當前 Plan 中正在執行的 VM 磁碟數
    for _, vmStatus := range r.Plan.Status.Migration.VMs {
        if vmStatus.HasCondition(Canceled) {
            continue
        }
        vm := &model.VM{}
        err = r.Source.Inventory.Find(vm, vmStatus.Ref)
        if err != nil {
            return
        }
        if vmStatus.Running() {
            r.inFlight[vm.Host] += r.cost(vm, vmStatus)
        }
    }

    // 步驟 2: 掃描所有其它使用相同 Source Provider 的 Plan
    planList := &api.PlanList{}
    err = r.List(context.TODO(), planList)
    if err != nil {
        return liberr.Wrap(err)
    }
    for _, p := range planList.Items {
        if p.Name == r.Plan.Name && p.Namespace == r.Plan.Namespace {
            continue // 跳過自身
        }
        if p.Spec.Provider.Source != r.Plan.Spec.Provider.Source {
            continue // 跳過不同 Provider
        }
        if p.Spec.Archived {
            continue // 跳過已歸檔
        }
        snapshot := p.Status.Migration.ActiveSnapshot()
        if !snapshot.HasCondition("Executing") {
            continue // 跳過非執行中
        }
        for _, vmStatus := range p.Status.Migration.VMs {
            if !vmStatus.Running() {
                continue
            }
            vm := &model.VM{}
            err = r.Source.Inventory.Find(vm, vmStatus.Ref)
            if err != nil { /* 略過找不到的 VM */ }
            r.inFlight[vm.Host] += r.cost(vm, vmStatus)
        }
    }
    return
}
```

### 2.4 buildPending() — 收集等待中的 VM

```go
// 檔案: pkg/controller/plan/scheduler/vsphere/scheduler.go

func (r *Scheduler) buildPending() (err error) {
    r.pending = make(map[string][]*pendingVM)
    for _, vmStatus := range r.Plan.Status.Migration.VMs {
        if vmStatus.HasCondition(Canceled) {
            continue
        }
        vm := &model.VM{}
        err = r.Source.Inventory.Find(vm, vmStatus.Ref)
        if err != nil {
            return
        }
        if !vmStatus.MarkedStarted() && !vmStatus.MarkedCompleted() {
            pending := &pendingVM{
                status: vmStatus,
                cost:   r.cost(vm, vmStatus),
            }
            r.pending[vm.Host] = append(r.pending[vm.Host], pending)
        }
    }
    return
}
```

### 2.5 Cost 計算 — 磁碟數量為權重

Cost 計算依據**遷移模式**有不同的邏輯。核心思想是：已完成磁碟傳輸的階段 cost 為 0，讓其它 VM 可以開始：

```go
// 檔案: pkg/controller/plan/scheduler/vsphere/scheduler.go

func (r *Scheduler) cost(vm *model.VM, vmStatus *plan.VMStatus) int {
    useV2vForTransfer, _ := r.Plan.ShouldUseV2vForTransfer(vmStatus.Ref)
    if useV2vForTransfer {
        switch vmStatus.Phase {
        case CreateVM, PostHook, Completed:
            // 磁碟已經傳輸完成，cost 歸零讓其它 VM 繼續
            return 0
        default:
            return 1
        }
    } else {
        switch vmStatus.Phase {
        case CreateVM, PostHook, Completed, CopyingPaused, ConvertGuest, CreateGuestConversionPod:
            // Warm/Remote 遷移在這些階段磁碟已傳輸完成
            return 0
        default:
            // CDI 平行傳輸磁碟，cost = 剩餘未完成的磁碟數
            return len(vm.Disks) - r.finishedDisks(vmStatus)
        }
    }
}

func (r *Scheduler) finishedDisks(vmStatus *plan.VMStatus) int {
    var resp = 0
    for _, step := range vmStatus.Pipeline {
        if step.Name == DiskTransfer {
            for _, task := range step.Tasks {
                if task.Phase == Completed {
                    resp += 1
                }
            }
        }
    }
    return resp
}
```

### 2.6 schedulable() — 容量判斷

```go
// 檔案: pkg/controller/plan/scheduler/vsphere/scheduler.go

func (r *Scheduler) schedulable() (schedulable map[string][]*pendingVM) {
    schedulable = make(map[string][]*pendingVM)
    for host, vms := range r.pending {
        if r.inFlight[host] >= r.MaxInFlight {
            continue
        }
        for i := range vms {
            if vms[i].cost+r.inFlight[host] <= r.MaxInFlight {
                schedulable[host] = append(schedulable[host], vms[i])
            }
            // 特殊情況：VM 磁碟數超過 MaxInFlight，但 Host 閒置時仍可排程
            if vms[i].cost > r.MaxInFlight && r.inFlight[host] == 0 {
                schedulable[host] = append(schedulable[host], vms[i])
            }
        }
    }
    return
}
```

### 2.7 排程流程圖

![Forklift vSphere 排程流程圖](/diagrams/forklift/forklift-vsphere-scheduler.png)

### 2.8 與 oVirt/OpenStack Scheduler 比較

oVirt 與 OpenStack 採用**簡化版排程器**，以整個 Provider 為粒度計算 in-flight VM 數量：

```go
// 檔案: pkg/controller/plan/scheduler/ovirt/scheduler.go

type Scheduler struct {
    *plancontext.Context
    // Maximum number of VMs that can be
    // migrated at once per provider.
    MaxInFlight int
}

func (r *Scheduler) Next() (vm *plan.VMStatus, hasNext bool, err error) {
    mutex.Lock()
    defer mutex.Unlock()

    planList := &api.PlanList{}
    err = r.List(context.TODO(), planList)
    if err != nil { return }

    if r.calcInFlight(planList) >= r.MaxInFlight {
        return
    }
    for _, vmStatus := range r.Plan.Status.Migration.VMs {
        if vmStatus.HasCondition(Canceled) { continue }
        if !vmStatus.MarkedStarted() && !vmStatus.MarkedCompleted() {
            vm = vmStatus
            hasNext = true
            return
        }
    }
    return
}
```

| 特性 | vSphere | oVirt / OpenStack |
|------|---------|-------------------|
| 節流粒度 | 每個 ESXi Host | 整個 Provider |
| 計量單位 | 磁碟數量 (disk count) | VM 數量 |
| Cost 計算 | 動態 — 已完成磁碟即時扣除 | 無 — Running 即計 1 |
| 跨 Plan 感知 | ✅ 掃描所有同 Provider Plan | ✅ 掃描所有同 Provider Plan |
| 大 VM 特例 | ✅ Host 閒置時可排程超限 VM | 無 |

---

## 3. Warm Migration（增量遷移）

Warm Migration 是 Forklift 用於**最小化停機時間**的遷移策略。核心原理是透過 **CBT（Changed Block Tracking）** 技術，在 VM 持續運行的狀態下先傳輸大部分資料，最終 Cutover 時僅需傳輸少量差異。

### 3.1 資料結構

```go
// 檔案: pkg/apis/forklift/v1beta1/plan/vm.go

// Warm Migration status
type Warm struct {
    Successes           int        `json:"successes"`
    Failures            int        `json:"failures"`
    ConsecutiveFailures int        `json:"consecutiveFailures"`
    NextPrecopyAt       *meta.Time `json:"nextPrecopyAt,omitempty"`
    Precopies           []Precopy  `json:"precopies,omitempty"`
}

type Precopy struct {
    Start        *meta.Time  `json:"start,omitempty"`
    End          *meta.Time  `json:"end,omitempty"`
    Snapshot     string      `json:"snapshot,omitempty"`
    CreateTaskId string      `json:"createTaskId,omitempty"`
    RemoveTaskId string      `json:"removeTaskId,omitempty"`
    Deltas       []DiskDelta `json:"deltas,omitempty"`
}

type DiskDelta struct {
    Disk    string `json:"disk"`
    DeltaID string `json:"deltaId"`
}
```

### 3.2 CBT 機制（vSphere）

CBT（Changed Block Tracking）是 VMware vSphere 的磁碟追蹤技術。當 CBT 啟用後，ESXi 會記錄自上次快照以來**變更過的磁碟區塊**。Forklift 透過 Client 介面存取 CBT 資料：

- `CreateSnapshot()` — 建立 VM 快照，鎖定磁碟狀態
- `GetSnapshotDeltas()` — 取得自上次 checkpoint 以來的 delta（變更區塊參照）
- `SetCheckpoints()` — 設定 CDI DataVolume 的 checkpoint annotation，使 CDI 僅傳輸 delta
- `CheckSnapshotReady()` — 確認快照就緒可傳輸
- `RemoveSnapshot()` — 傳輸完成後清理快照

Validator 也會驗證 CBT 前置條件：
- `ChangeTrackingEnabled()` — 確認來源 VM 已啟用 CBT
- `HasSnapshot()` — 確認 Warm Migration 開始前沒有殘留快照

### 3.3 Precopy 迴圈

Warm Migration 的核心是 **Precopy 迴圈**，反覆執行快照 → 差異複製 → 刪除快照的循環：

1. **建立快照**：呼叫 `CreateSnapshot()` 鎖定當前磁碟狀態
2. **取得 Delta**：呼叫 `GetSnapshotDeltas()` 取得變更區塊
3. **差異複製**：透過 CDI DataVolume 的 checkpoint 機制僅傳輸增量資料
4. **記錄 Precopy**：更新 `Warm.Precopies` 清單，記錄快照 ID 與 Delta 資訊
5. **清理快照**：呼叫 `RemoveSnapshot()` 移除已複製的快照
6. **排程下次**：設定 `NextPrecopyAt` 排程下一輪 precopy

### 3.4 Cutover（最終切換）

當使用者觸發 Cutover 時：

1. 建立**最終快照**（`AnnFinalCheckpoint` annotation）
2. **關閉來源 VM** — `PowerOff()`
3. 傳輸**最後一次 delta**（通常資料量很小）
4. **建立目標 VM** — 進入 CreateVM Phase
5. 清理所有快照 — `Finalize()`

### 3.5 錯誤處理

`ConsecutiveFailures` 欄位追蹤連續失敗次數。當達到閾值時，Forklift 會將遷移標記為失敗，避免無限重試：

```go
// 檔案: pkg/apis/forklift/v1beta1/plan/vm.go

type Warm struct {
    Successes           int        `json:"successes"`
    Failures            int        `json:"failures"`
    ConsecutiveFailures int        `json:"consecutiveFailures"`  // 達到閾值即停止
    NextPrecopyAt       *meta.Time `json:"nextPrecopyAt,omitempty"`
    Precopies           []Precopy  `json:"precopies,omitempty"`
}
```

- `Successes`：成功的 precopy 次數
- `Failures`：失敗的 precopy 總次數
- `ConsecutiveFailures`：**連續**失敗次數，成功後歸零

### 3.6 Warm Migration 序列圖

![Warm Migration Precoy 序列圖](/diagrams/forklift/forklift-warm-precopy.png)

---

## 4. virt-v2v 磁碟轉換

virt-v2v 是 Forklift 內建的 Guest OS 轉換引擎，負責將來源 VM 的磁碟格式轉換為 KubeVirt 相容格式，並安裝必要驅動程式。

### 4.1 轉換管線入口

整個轉換流程由 `cmd/virt-v2v/entrypoint.go` 編排：

```go
// 檔案: cmd/virt-v2v/entrypoint.go

func main() {
    env := &config.AppConfig{}
    err := env.Load()
    // ...
    convert, err := conversion.NewConversion(env)

    if env.IsRemoteInspection {
        // 遠端檢查模式：僅執行 virt-v2v-inspector
        err = convert.RunRemoteV2vInspection()
    } else {
        if convert.IsInPlace {
            if convert.LibvirtUrl != "" {
                // In-place + Libvirt：取得 Domain XML → virt-v2v-in-place -i libvirtxml
                domainXML, _ := convert.GetDomainXML()
                os.WriteFile(convert.LibvirtDomainFile, []byte(domainXML), 0644)
                err = convert.RunVirtV2vInPlace()
            } else {
                // In-place + Disk mode：直接 virt-v2v-in-place -i disk（如 EC2）
                err = convert.RunVirtV2vInPlaceDisk()
            }
        } else {
            // 標準轉換：virt-v2v → virt-v2v-inspector → virt-customize
            err = convert.RunVirtV2v()
        }
        // 檢查與客製化
        convert.RunVirtV2VInspection()
        convert.RunCustomize(inspection.OS)

        // 本地遷移時啟動 HTTP Server 供 Controller 取得轉換結果
        if convert.IsLocalMigration {
            s := server.Server{AppConfig: env}
            s.Start()  // 監聽 :8080
        }
    }
}
```

### 4.2 支援的輸入來源與格式

| 來源 Provider | 輸入模式 (`-i`) | 磁碟格式 | 傳輸方式 |
|--------------|----------------|---------|---------|
| vSphere | `libvirt` + VDDK | VMDK | `-it vddk` + thumbprint |
| OVA | `ova` | VMDK (OVF 內嵌) | 本地檔案路徑 |
| Hyper-V | `disk` | VHD / VHDX | 逗號分隔磁碟路徑 |
| EC2 | `disk` (in-place) | RAW / IMG | Block device / 掛載檔案 |
| oVirt / OpenStack | `disk` (in-place) | RAW / QCOW2 | CDI 已下載至 PVC |

磁碟偵測使用 glob 模式：

```go
// 檔案: pkg/virt-v2v/config/variables.go

const (
    FS    = "/mnt/disks/disk[0-9]*"   // Filesystem 模式
    BLOCK = "/dev/block[0-9]*"         // Block device 模式
)
```

### 4.3 In-place 與 Full Conversion

**Full Conversion**（標準模式）— 適用於 vSphere、OVA、Hyper-V：

```go
// 檔案: pkg/virt-v2v/conversion/conversion.go

func (c *Conversion) RunVirtV2v() error {
    v2vCmdBuilder := c.CommandBuilder.New("virt-v2v")
    err := c.addVirtV2vArgs(v2vCmdBuilder)  // 加入 -o kubevirt -os workdir
    v2vCmd := v2vCmdBuilder.Build()

    // virt-v2v-monitor 讀取 stdout 追蹤進度
    monitorCmd := c.CommandBuilder.New("/usr/local/bin/virt-v2v-monitor").Build()
    pipe, writer := io.Pipe()
    monitorCmd.SetStdin(pipe)
    v2vCmd.SetStdout(writer)
    v2vCmd.SetStderr(writer)

    monitorCmd.Start()
    v2vCmd.Run()
    writer.Close()
    monitorCmd.Wait()
    return nil
}
```

**In-place Conversion** — 磁碟已透過 CDI 下載到 PVC，直接原地轉換：

```go
// 檔案: pkg/virt-v2v/conversion/conversion.go

func (c *Conversion) RunVirtV2vInPlace() error {
    v2vCmdBuilder := c.CommandBuilder.New("virt-v2v-in-place").
        AddFlag("-v").AddFlag("-x").
        AddArg("-i", "libvirtxml")
    c.addCommonArgs(v2vCmdBuilder)
    c.addConversionExtraArgs(v2vCmdBuilder)
    v2vCmdBuilder.AddPositional(c.LibvirtDomainFile)
    return v2vCmdBuilder.Build().Run()
}

// EC2 等無 Libvirt 的場景使用 disk mode
func (c *Conversion) RunVirtV2vInPlaceDisk() error {
    v2vCmdBuilder := c.CommandBuilder.New("virt-v2v-in-place").
        AddFlag("-v").AddFlag("-x").
        AddArg("-i", "disk")
    c.addCommonArgs(v2vCmdBuilder)
    for _, disk := range c.Disks {
        v2vCmdBuilder.AddPositional(disk.Link)
    }
    return v2vCmdBuilder.Build().Run()
}
```

### 4.4 virt-v2v-monitor 進度追蹤

`RunVirtV2v()` 使用 `io.Pipe` 將 virt-v2v 的 stdout 導入 `virt-v2v-monitor` 程式。Monitor 解析輸出，產生結構化的進度資訊供 Controller 讀取。

### 4.5 vSphere 專用參數 — VDDK 整合

```go
// 檔案: pkg/virt-v2v/conversion/conversion.go

func (c *Conversion) addVirtV2vVsphereArgs(cmd utils.CommandBuilder) error {
    cmd.AddArg("-i", "libvirt").
        AddArg("-ic", c.LibvirtUrl).
        AddArg("-ip", c.SecretKey).
        AddArg("--hostname", c.HostName)
    c.addCommonArgs(cmd)
    c.addConversionExtraArgs(cmd)
    if info, _ := os.Stat(c.VddkLibDir); info != nil && info.IsDir() {
        cmd.AddArg("-it", "vddk")
        cmd.AddArg("-io", fmt.Sprintf("vddk-libdir=%s", c.VddkLibDir))
        cmd.AddArg("-io", fmt.Sprintf("vddk-thumbprint=%s", c.Fingerprint))
        if _, err := os.Stat(c.VddkConfFile); !errors.Is(err, os.ErrNotExist) {
            cmd.AddArg("-io", fmt.Sprintf("vddk-config=%s", c.VddkConfFile))
        }
    }
    cmd.AddPositional("--")
    cmd.AddPositional(c.VmName)
    return nil
}
```

### 4.6 共用參數 — addCommonArgs

所有 virt-v2v 指令（含 inspector、in-place）共享以下參數：

```go
// 檔案: pkg/virt-v2v/conversion/conversion.go

func (c *Conversion) addCommonArgs(cmd utils.CommandBuilder) error {
    if c.RootDisk != "" {
        cmd.AddArg("--root", c.RootDisk)
    } else {
        cmd.AddArg("--root", "first")
    }
    if c.MemSize > 0 {
        cmd.AddArg("--memsize", fmt.Sprintf("%d", c.MemSize))
    }
    if c.Smp > 0 {
        cmd.AddArg("--smp", fmt.Sprintf("%d", c.Smp))
    }
    // Static IP MAC mapping（用於 Windows 靜態 IP 保留）
    if c.StaticIPs != "" {
        for _, mac := range strings.Split(c.StaticIPs, "_") {
            cmd.AddArg("--mac", mac)
        }
    }
    // LUKS 磁碟解密
    if c.NbdeClevis {
        cmd.AddArgs("--key", "all:clevis")
    } else if c.Luksdir != "" {
        utils.AddLUKSKeys(c.fileSystem, cmd, c.Luksdir)
    }
    return nil
}
```

### 4.7 ConversionPodConfig — 每 Provider 客製化

`Builder.ConversionPodConfig()` 讓每個 Provider 為 virt-v2v Pod 注入客製化設定：

```go
// 檔案: pkg/controller/plan/adapter/base/doc.go

type ConversionPodConfigResult struct {
    NodeSelector map[string]string  // 如 vSphere 可指定特定 Node
    Labels       map[string]string  // Provider 專用 label
    Annotations  map[string]string  // 如 UDN 需要 open-default-ports
}
```

### 4.8 轉換管線流程圖

![virt-v2v 轉換管線流程圖](/diagrams/forklift/forklift-virt-v2v-pipeline.png)

---

## 5. Network Mapping 機制

Network Mapping 將來源 VM 的虛擬網路對映至目標 Kubernetes 叢集的網路設定。支援三種目標類型：Pod Network、Multus（NAD）與 Ignored。

### 5.1 核心型別

```go
// 檔案: pkg/apis/forklift/v1beta1/mapping.go

type DestinationNetwork struct {
    // "pod": Kubernetes Pod 網路
    // "multus": Multus 額外網路（NAD）
    // "ignored": 排除此網路
    Type      string `json:"type"`
    Namespace string `json:"namespace,omitempty"`  // 僅 Multus 使用
    Name      string `json:"name,omitempty"`
}

type NetworkPair struct {
    Source      ref.Ref            `json:"source"`
    Destination DestinationNetwork `json:"destination"`
}

type NetworkMapSpec struct {
    Provider provider.Pair `json:"provider"`
    Map      []NetworkPair `json:"map"`
}
```

### 5.2 NetworkMap CRD

`NetworkMap` 是一個 Kubernetes Custom Resource，定義來源到目標的網路對映關係：

```go
// 檔案: pkg/apis/forklift/v1beta1/mapping.go

type NetworkMap struct {
    meta.TypeMeta   `json:",inline"`
    meta.ObjectMeta `json:"metadata,omitempty"`
    Spec            NetworkMapSpec `json:"spec,omitempty"`
    Status          MapStatus      `json:"status,omitempty"`
    Referenced      `json:"-"`
}

// 查詢方法
func (r *NetworkMap) FindNetwork(networkID string) (NetworkPair, bool)
func (r *NetworkMap) FindNetworkByType(networkType string) (NetworkPair, bool)
func (r *NetworkMap) FindNetworkByNameAndNamespace(namespace, name string) (NetworkPair, bool)
```

### 5.3 NetworkNameTemplate — 自訂介面命名

使用者可透過 Go Template 語法自訂目標 VM 的網路介面名稱：

```go
// 檔案: pkg/apis/forklift/v1beta1/plan/vm.go

// NetworkNameTemplate 可用變數：
//   - .NetworkName:      Multus NAD 名稱（Pod 網路為空）
//   - .NetworkNamespace: Multus NAD 命名空間
//   - .NetworkType:      "Multus" 或 "Pod"
//   - .NetworkIndex:     介面序號（0-based）
//
// 範例：
//   "net-{{.NetworkIndex}}"
//   "{{if eq .NetworkType \"Pod\"}}pod{{else}}multus-{{.NetworkIndex}}{{end}}"
NetworkNameTemplate string `json:"networkNameTemplate,omitempty"`
```

此 Template 可在 VM 層級或 Plan 層級設定，VM 層級優先。

### 5.4 Static IP 保留（vSphere / Hyper-V）

vSphere 與 Hyper-V 遷移支援保留來源 VM 的靜態 IP 設定。靜態 IP 資訊透過 `V2V_staticIPs` 環境變數傳遞給 virt-v2v：

```go
// 檔案: pkg/virt-v2v/config/variables.go

// 格式: <mac:network|bridge|ip>_<mac:network|bridge|ip>
EnvStaticIPsName = "V2V_staticIPs"
```

Validator 介面提供專門的驗證方法：
- `StaticIPs(vmRef)` — 驗證是否有每個 NIC 的靜態 IP 資訊
- `UdnStaticIPs(vmRef, client)` — 驗證 UDN 子網段是否與 VM IP 相符

### 5.5 MAC Address 衝突偵測

Validator 的 `MacConflicts()` 方法會檢查來源 VM 的 MAC 地址是否與目標叢集中已存在的 VM 衝突，避免網路層級的問題。

### 5.6 UDN（User-Defined Network）驗證

Forklift 支援 OVN-Kubernetes 的 User-Defined Network。在目標命名空間有 UDN 時，需要特殊處理：

```go
// 檔案: pkg/controller/plan/adapter/base/doc.go

// UDN 相關 Annotation
const (
    // 在 UDN 命名空間中開啟 Pod 網路的預設端口
    AnnOpenDefaultPorts = "k8s.ovn.org/open-default-ports"
    // UDN L2 bridge binding，KubeVirt VM 需要此設定
    UdnL2bridge = "l2bridge"
    // 靜態 UDN IP 設定
    // 格式: {"iface1": ["192.168.0.1/24", "fd23:3214::123/64"]}
    AnnStaticUdnIp = "network.kubevirt.io/addresses"
)
```

驗證邏輯包括：
- 檢查命名空間是否有 `k8s.ovn.org/primary-user-defined-network` 標籤
- 驗證 NAD 是否標記為 `k8s.ovn.org/user-defined-network`
- **Layer 3 UDN 不支援**（`UnsupportedUdn` Condition）
- 驗證 VM IP 是否在 UDN 的 CIDR 範圍內

---

## 6. Storage Mapping 與 XCOPY Offload

Storage Mapping 將來源 Datastore（或 Storage Domain）對映至目標 Kubernetes StorageClass。XCOPY Offload 則利用儲存陣列原生的複製能力來加速磁碟傳輸。

### 6.1 核心型別

```go
// 檔案: pkg/apis/forklift/v1beta1/mapping.go

type DestinationStorage struct {
    StorageClass string                          `json:"storageClass"`
    VolumeMode   core.PersistentVolumeMode       `json:"volumeMode,omitempty"`   // Filesystem | Block
    AccessMode   core.PersistentVolumeAccessMode  `json:"accessMode,omitempty"`   // ReadWriteOnce | ReadWriteMany | ReadOnlyMany
}

type StoragePair struct {
    Source        ref.Ref            `json:"source"`
    Destination   DestinationStorage `json:"destination"`
    OffloadPlugin *OffloadPlugin     `json:"offloadPlugin,omitempty"`
}

type StorageMapSpec struct {
    Provider provider.Pair `json:"provider"`
    Map      []StoragePair `json:"map"`
}
```

### 6.2 StorageMap CRD

```go
// 檔案: pkg/apis/forklift/v1beta1/mapping.go

type StorageMap struct {
    meta.TypeMeta   `json:",inline"`
    meta.ObjectMeta `json:"metadata,omitempty"`
    Spec            StorageMapSpec `json:"spec,omitempty"`
    Status          MapStatus      `json:"status,omitempty"`
    Referenced      `json:"-"`
}

func (r *StorageMap) FindStorage(storageID string) (StoragePair, bool)
func (r *StorageMap) FindStorageByName(storageName string) (StoragePair, bool)
```

### 6.3 VolumeMode 與 AccessMode

使用者在 `DestinationStorage` 中指定目標 PVC 的儲存模式：

| 設定 | 選項 | 說明 |
|------|------|------|
| VolumeMode | `Filesystem` | 以檔案系統形式掛載，適合大多數場景 |
| VolumeMode | `Block` | 原始區塊裝置，效能較佳但需 CSI 支援 |
| AccessMode | `ReadWriteOnce` | 單節點讀寫，最常見 |
| AccessMode | `ReadWriteMany` | 多節點讀寫，需 CSI 支援（如 CephFS） |
| AccessMode | `ReadOnlyMany` | 多節點唯讀 |

### 6.4 XCOPY Offload Plugin

XCOPY Offload 是一種**儲存層級的複製加速**機制。當來源 vSphere 的 Datastore 與目標 Kubernetes 使用**同一組儲存陣列**時，可透過陣列內部的 XCOPY 指令直接搬移資料，無需經過網路。

```go
// 檔案: pkg/apis/forklift/v1beta1/mapping.go

type OffloadPlugin struct {
    VSphereXcopyPluginConfig *VSphereXcopyPluginConfig `json:"vsphereXcopyConfig"`
}

type VSphereXcopyPluginConfig struct {
    // 儲存憑證 Secret 名稱（與 Source Provider 同命名空間）
    SecretRef            string               `json:"secretRef"`
    // 儲存廠商產品識別
    StorageVendorProduct StorageVendorProduct `json:"storageVendorProduct"`
}
```

### 6.5 支援的 9 種儲存廠商

```go
// 檔案: pkg/apis/forklift/v1beta1/mapping.go

type StorageVendorProduct string

const (
    StorageVendorProductFlashSystem    StorageVendorProduct = "flashsystem"     // IBM FlashSystem
    StorageVendorProductVantara        StorageVendorProduct = "vantara"          // Hitachi Vantara
    StorageVendorProductOntap          StorageVendorProduct = "ontap"            // NetApp ONTAP
    StorageVendorProductPrimera3Par    StorageVendorProduct = "primera3par"      // HPE Primera / 3PAR
    StorageVendorProductPureFlashArray StorageVendorProduct = "pureFlashArray"   // Pure Storage FlashArray
    StorageVendorProductPowerFlex      StorageVendorProduct = "powerflex"        // Dell EMC PowerFlex
    StorageVendorProductPowerMax       StorageVendorProduct = "powermax"         // Dell EMC PowerMax
    StorageVendorProductPowerStore     StorageVendorProduct = "powerstore"       // Dell EMC PowerStore
    StorageVendorProductInfinibox      StorageVendorProduct = "infinibox"        // Infinidat InfiniBox
)
```

### 6.6 XCOPY 使用方式

在 `StorageMap` 的 `StoragePair` 中配置 `OffloadPlugin`：

```yaml
apiVersion: forklift.konveyor.io/v1beta1
kind: StorageMap
metadata:
  name: example-storage-map
spec:
  provider:
    source:
      name: vsphere-provider
      namespace: openshift-mtv
    destination:
      name: host
      namespace: openshift-mtv
  map:
    - source:
        id: datastore-123
      destination:
        storageClass: "ontap-san"
        volumeMode: Block
        accessMode: ReadWriteOnce
      offloadPlugin:
        vsphereXcopyConfig:
          secretRef: "ontap-storage-secret"
          storageVendorProduct: "ontap"
```

此設定會使 Forklift 使用 **vSphere XCOPY Volume Populator** 取代傳統的 CDI 資料傳輸路徑，大幅提升遷移效率。

### 6.7 Storage Mapping 流程圖

![Storage Mapping 流程圖](/diagrams/forklift/forklift-storage-mapping.png)
