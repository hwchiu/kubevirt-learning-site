---
layout: doc
title: Cluster API Provider Metal3 — 控制器與 CRD API
---

# Cluster API Provider Metal3 — 控制器與 CRD API

本章節深入剖析 CAPM3 各控制器的 Reconcile 邏輯，並說明每個 CRD 的 API 設計。

## Manager Factory 設計模式

CAPM3 使用 Factory 模式建立各種 Manager，讓 Controller 與業務邏輯解耦：

```go
// 檔案: baremetal/manager_factory.go
type ManagerFactoryInterface interface {
    NewClusterManager(cluster *clusterv1.Cluster,
        metal3Cluster *infrav1.Metal3Cluster,
        clusterLog logr.Logger,
    ) (ClusterManagerInterface, error)
    NewMachineManager(*clusterv1.Cluster, *infrav1.Metal3Cluster, *clusterv1.Machine,
        *infrav1.Metal3Machine, logr.Logger,
    ) (MachineManagerInterface, error)
    NewDataTemplateManager(*infrav1.Metal3DataTemplate, logr.Logger) (
        DataTemplateManagerInterface, error,
    )
    NewDataManager(*infrav1.Metal3Data, logr.Logger) (
        DataManagerInterface, error,
    )
    NewRemediationManager(*infrav1.Metal3Remediation, *infrav1.Metal3Machine,
        *clusterv1.Machine, logr.Logger,
    ) (RemediationManagerInterface, error)
}
```

## Metal3ClusterReconciler

### Reconciler 結構

```go
// 檔案: controllers/metal3cluster_controller.go
const (
    clusterControllerName = "Metal3Cluster-controller"
    requeueAfter          = time.Second * 30
)

type Metal3ClusterReconciler struct {
    Client           client.Client
    ClusterCache     clustercache.ClusterCache
    ManagerFactory   baremetal.ManagerFactoryInterface
    Log              logr.Logger
    WatchFilterValue string
}
```

### Reconcile 流程

`Metal3ClusterReconciler.Reconcile` 的主要邏輯：

1. 取得 `Metal3Cluster` 物件
2. 找到關聯的 CAPI `Cluster` 物件（OwnerReference）
3. 若叢集已暫停（Paused）則跳過
4. 建立 `ClusterManager`
5. 依據刪除時間戳判斷走 **reconcileDelete** 或 **reconcileNormal**

**reconcileNormal 步驟：**
- 設定 Finalizer
- 呼叫 `ClusterManager.Create()` 確認 ControlPlaneEndpoint 有效
- 呼叫 `ClusterManager.UpdateClusterStatus()` 更新狀態

### ClusterManager 核心函數

```go
// 檔案: baremetal/metal3cluster_manager.go
func (s *ClusterManager) Create(_ context.Context) error {
    // 驗證 ControlPlaneEndpoint 設定
}

func (s *ClusterManager) UpdateClusterStatus() error {
    // 更新 Metal3Cluster status，設定 Ready condition
}

func (s *ClusterManager) CountDescendants(ctx context.Context) (int, error) {
    // 計算此叢集底下尚存在的 Machine 數量
    // 刪除時使用，確保所有 Machine 清理完畢後才刪除叢集
}
```

| 函數 | 說明 |
|------|------|
| `SetFinalizer()` | 設定 `metal3cluster.infrastructure.cluster.x-k8s.io` Finalizer |
| `UnsetFinalizer()` | 清除 Finalizer |
| `Create()` | 驗證叢集設定（主要驗證 ControlPlaneEndpoint）|
| `ControlPlaneEndpoint()` | 回傳 control plane 端點資訊 |
| `Delete()` | 叢集刪除前置處理 |
| `UpdateClusterStatus()` | 更新 Ready 狀態與 Condition |
| `CountDescendants()` | 計算仍存在的後代機器數量 |

## Metal3MachineReconciler

### Reconcile 流程

Metal3Machine 的 reconcile 是 CAPM3 中最複雜的部分，涵蓋 provisioning 完整生命週期：

```go
// 檔案: controllers/metal3machine_controller.go
func (r *Metal3MachineReconciler) reconcileNormal(
    ctx context.Context,
    machineMgr baremetal.MachineManagerInterface,
    log logr.Logger,
) (ctrl.Result, error) {
    // 1. 設定 Finalizer
    machineMgr.SetFinalizer()

    // 2. 如果已 provisioned 且有 NodeRef，直接更新並返回
    if machineMgr.IsProvisioned() && machineMgr.MachineHasNodeRef() {
        return ctrl.Result{}, machineMgr.Update(ctx)
    }

    // 3. 等待 bootstrap data 就緒
    if !machineMgr.IsBootstrapReady() {
        return ctrl.Result{}, nil
    }

    // 4. 若尚未關聯 BMH，執行 Associate
    if !machineMgr.HasAnnotation() {
        chosenHostReason, err := machineMgr.Associate(ctx)
        // ...
        return ctrl.Result{}, nil
    }

    // 5. 處理 MetaData / NetworkData
    // 6. 確認 BMH provisioning 狀態
    // 7. 更新 ProviderID 到 CAPI Machine
}
```

### MachineManager 關鍵函數

```go
// 檔案: baremetal/metal3machine_manager.go
func (m *MachineManager) Associate(ctx context.Context) (string, error) {
    // 從可用的 BareMetalHost 池中選取合適主機
    // 設定 BMH 的 spec（image、userData 等）
    // 在 Metal3Machine 上加入 BMH 參考 annotation
}

func (m *MachineManager) chooseHost(ctx context.Context) (
    *bmov1alpha1.BareMetalHost, *patch.Helper, string, error,
) {
    // 列出所有符合 HostSelector 的 BareMetalHost
    // 過濾出未被使用（無 consumerRef）的主機
    // 隨機選取一台（或依 node reuse 邏輯選取）
}

func (m *MachineManager) setHostSpec(
    _ context.Context, host *bmov1alpha1.BareMetalHost,
) error {
    // 設定 BMH spec：image、online=true、automatedCleaningMode
}
```

| 函數 | 說明 |
|------|------|
| `IsProvisioned()` | 判斷 BMH 是否已完成 provisioning |
| `IsBootstrapReady()` | 判斷 bootstrap secret 是否就緒 |
| `Associate()` | 選取並綁定 BareMetalHost |
| `Delete()` | 觸發 BMH deprovisioning |
| `Update()` | 更新 ProviderID、地址等狀態 |
| `chooseHost()` | 從可用 BMH 池選取主機 |
| `setHostSpec()` | 設定 BMH 映像與啟動設定 |
| `RemovePauseAnnotation()` | 移除 BMH 的 pause annotation |

### Watch 設定

```go
// 檔案: controllers/metal3machine_controller.go
// SetupWithManager 設定 Metal3Machine 的 Watch 對象
func (r *Metal3MachineReconciler) SetupWithManager(
    ctx context.Context, mgr ctrl.Manager, options controller.Options,
) error {
    // Watch: Metal3Machine、Machine、BareMetalHost
    // BareMetalHost 變更時，透過 BareMetalHostToMetal3Machines 找出對應的 Metal3Machine
}
```

Metal3MachineReconciler 監聽以下資源的變化：

| Watch 資源 | 觸發原因 |
|-----------|---------|
| `Metal3Machine` | 主要 reconcile 對象 |
| `Machine`（CAPI）| bootstrap data 就緒通知 |
| `BareMetalHost` | BMH provisioning 狀態變更 |
| `Metal3Cluster` | 叢集基礎設施就緒通知 |
| `Cluster`（CAPI）| 叢集就緒通知 |

## Metal3DataTemplateReconciler 與 Metal3DataReconciler

### 協同工作流程

```
Metal3Machine（spec.dataTemplate）
    │ 建立
    ▼
Metal3DataClaim
    │ DataTemplate 處理
    ▼
Metal3DataTemplate Reconciler
    │ 分配 index，建立
    ▼
Metal3Data
    │ Data Reconciler 渲染
    ▼
兩個 Secret（metaData + networkData）
    │ 引用回填
    ▼
Metal3Machine（spec.metaData / spec.networkData）
```

### DataManager 核心函數

```go
// 檔案: baremetal/metal3data_manager.go
func (m *DataManager) Reconcile(ctx context.Context) error {
    // 呼叫 createSecrets() 渲染模板並建立 Secret
}

func (m *DataManager) createSecrets(ctx context.Context) error {
    // 解析 Metal3DataTemplate 中的 metaData / networkData 定義
    // 從 IPAM 獲取 IP 位址（若有 fromPoolRef）
    // 渲染模板，建立 Kubernetes Secret
}

func (m *DataManager) ReleaseLeases(ctx context.Context) error {
    // Metal3Data 刪除時，歸還 IPAM 的 IP 位址
}
```

## Metal3RemediationReconciler

### Remediation 狀態機

```go
// 檔案: api/v1beta2/metal3remediation_types.go
const (
    PhaseRunning  = "Running"
    PhaseWaiting  = "Waiting"
    PhaseDeleting = "Deleting machine"
    PhaseFailed   = "Failed"
)
```

### reconcileNormal 邏輯

```go
// 檔案: controllers/metal3remediation_controller.go
func (r *Metal3RemediationReconciler) reconcileNormal(
    ctx context.Context,
    remediationMgr baremetal.RemediationManagerInterface,
) (ctrl.Result, error) {
    // 1. 取得修復策略（目前只支援 Reboot）
    // 2. 若未達重試上限，執行 remediateRebootStrategy
    // 3. 若已達重試上限，進入 PhaseDeleting，刪除不健康的 Machine
}

func (r *Metal3RemediationReconciler) remediateRebootStrategy(
    ctx context.Context,
    remediationMgr baremetal.RemediationManagerInterface,
) (ctrl.Result, error) {
    // Running → 對 BMH 設定 power off annotation
    // Waiting → 等待重啟完成，確認 BMH 回到 online
    // 若逾時，增加 retry count
}
```

| Phase | 說明 |
|-------|------|
| `Running` | 正在執行修復（送出 power off 指令）|
| `Waiting` | 等待修復結果（等待 BMH 上線）|
| `Deleting machine` | 修復失敗達上限，刪除 Machine |
| `Failed` | BMH offline 或其他原因導致修復無法進行 |

## Metal3LabelSyncReconciler

Metal3LabelSyncReconciler 負責將 `Metal3Machine` 的 label 同步到對應的 Kubernetes Node，使 Metal3 的 label 策略能在節點層級生效。

```go
// 檔案: controllers/metal3labelsync_controller.go
// 監聽 Metal3Machine 的 label 變更，更新對應 Node 的 label
```

::: warning 關於 Webhook
CAPM3 的 webhook 實作位於 `internal/webhooks/v1beta2/`，為各 CRD 提供 admission 驗證與 defaulting，確保欄位在進入 API Server 前完成驗證。
:::

::: info 相關章節
- [系統架構](/cluster-api-provider-metal3/architecture)
- [裸金屬管理](/cluster-api-provider-metal3/baremetal)
- [節點修復](/cluster-api-provider-metal3/remediation)
- [外部整合](/cluster-api-provider-metal3/integration)
:::
