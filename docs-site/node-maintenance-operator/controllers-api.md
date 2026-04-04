---
layout: doc
---

# NMO — 控制器與 API

本章深入分析 Node Maintenance Operator 的 CRD 型別定義、控制器結構、Webhook 驗證邏輯、RBAC 權限規則，以及輔助工具函式。

::: info 相關章節
- 系統整體架構請參閱 [系統架構](./architecture)
- Reconcile 與 Drain 核心邏輯請參閱 [核心功能分析](./core-features)
- 與 NHC 和 OpenShift 的整合請參閱 [外部整合](./integration)
:::

## NodeMaintenance CRD 型別

::: info 原始碼路徑
`api/v1beta1/nodemaintenance_types.go`、`api/v1beta1/groupversion_info.go`
:::

### GroupVersion 註冊

CRD 隸屬於 `nodemaintenance.medik8s.io` API Group，版本為 `v1beta1`：

```go
// +kubebuilder:object:generate=true
// +groupName=nodemaintenance.medik8s.io
package v1beta1

var (
    GroupVersion = schema.GroupVersion{
        Group:   "nodemaintenance.medik8s.io",
        Version: "v1beta1",
    }
    SchemeBuilder = &scheme.Builder{GroupVersion: GroupVersion}
    AddToScheme   = SchemeBuilder.AddToScheme
)
```

### MaintenancePhase

維護狀態以字串型別表示，共有三個階段：

```go
type MaintenancePhase string

const (
    // 維護正在進行中 — 已開始 cordon/drain 處理
    MaintenanceRunning   MaintenancePhase = "Running"
    // 維護成功完成 — 節點已被封鎖，所有可驅逐的 Pod 均已遷移
    MaintenanceSucceeded MaintenancePhase = "Succeeded"
    // 維護失敗
    MaintenanceFailed    MaintenancePhase = "Failed"
)
```

| 階段 | 說明 |
|------|------|
| `Running` | Reconciler 正在執行 cordon + drain 流程 |
| `Succeeded` | drain 完成，`DrainProgress` 設為 100，`PendingPods` 清空 |
| `Failed` | 節點不存在、Lease 連續錯誤超過閾值、或其他無法恢復的錯誤 |

### NodeMaintenanceSpec

定義使用者期望的維護狀態，僅包含兩個欄位：

```go
type NodeMaintenanceSpec struct {
    // 要進行維護的節點名稱
    //+operator-sdk:csv:customresourcedefinitions:type=spec
    NodeName string `json:"nodeName"`

    // 維護原因（選填）
    //+operator-sdk:csv:customresourcedefinitions:type=spec
    Reason string `json:"reason,omitempty"`
}
```

| 欄位 | 型別 | JSON Tag | 必填 | 說明 |
|------|------|----------|------|------|
| `NodeName` | `string` | `nodeName` | ✅ | 目標節點名稱，建立後不可更改 |
| `Reason` | `string` | `reason` | ❌ | 描述為什麼進行維護 |

### PodReference

記錄尚未被驅逐的 Pod 參考資訊：

```go
type PodReference struct {
    // Pod 所屬的 Namespace
    Namespace string `json:"namespace,omitempty"`
    // Pod 名稱
    Name string `json:"name,omitempty"`
}
```

### NodeMaintenanceStatus

反映維護作業的實際進度與狀態：

```go
type NodeMaintenanceStatus struct {
    // 維護進度階段 (Running / Succeeded / Failed)
    Phase MaintenancePhase `json:"phase,omitempty"`

    // Drain 進度百分比 (0–100)
    DrainProgress int `json:"drainProgress,omitempty"`

    // 最近一次狀態更新時間
    LastUpdate metav1.Time `json:"lastUpdate,omitempty"`

    // 最近一次 reconcile 的錯誤訊息
    LastError string `json:"lastError,omitempty"`

    // 等待驅逐的 Pod 名稱清單
    PendingPods []string `json:"pendingPods,omitempty"`

    // 等待驅逐的 Pod 參考清單（含 Namespace）
    PendingPodsRefs []PodReference `json:"pendingPodsRefs,omitempty"`

    // 維護開始時節點上所有 Pod 的總數
    TotalPods int `json:"totalpods,omitempty"`

    // 維護開始時需要驅逐的 Pod 數量
    EvictionPods int `json:"evictionPods,omitempty"`

    // 連續取得 Lease 失敗的次數
    ErrorOnLeaseCount int `json:"errorOnLeaseCount,omitempty"`
}
```

| 欄位 | JSON Tag | 型別 | 說明 |
|------|----------|------|------|
| `Phase` | `phase` | `MaintenancePhase` | 維護進度階段 |
| `DrainProgress` | `drainProgress` | `int` | 計算公式：`(EvictionPods - len(PendingPods)) * 100 / EvictionPods` |
| `LastUpdate` | `lastUpdate` | `metav1.Time` | 每次狀態變更時更新 |
| `LastError` | `lastError` | `string` | 最後一次錯誤訊息 |
| `PendingPods` | `pendingPods` | `[]string` | Pod 名稱列表 |
| `PendingPodsRefs` | `pendingPodsRefs` | `[]PodReference` | 帶有 Namespace 的 Pod 參考 |
| `TotalPods` | `totalpods` | `int` | 初始化時統計節點上所有 Pod |
| `EvictionPods` | `evictionPods` | `int` | 初始化時統計需驅逐的 Pod |
| `ErrorOnLeaseCount` | `errorOnLeaseCount` | `int` | 超過 3 次即判定維護失敗 |

### NodeMaintenance 與 NodeMaintenanceList

```go
//+kubebuilder:object:root=true
//+kubebuilder:subresource:status
//+kubebuilder:resource:scope=Cluster,shortName=nm

// NodeMaintenance is the Schema for the nodemaintenances API
type NodeMaintenance struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec              NodeMaintenanceSpec   `json:"spec,omitempty"`
    Status            NodeMaintenanceStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// NodeMaintenanceList contains a list of NodeMaintenance
type NodeMaintenanceList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []NodeMaintenance `json:"items"`
}
```

::: tip Kubebuilder 標記重點
- `scope=Cluster`：這是一個叢集層級資源（非 Namespace 限定）
- `shortName=nm`：可使用 `kubectl get nm` 快速查詢
- `subresource:status`：Status 有獨立的子資源端點，需要專門的 RBAC 權限
:::

### Finalizer

```go
const NodeMaintenanceFinalizer string = "foregroundDeleteNodeMaintenance"
```

Finalizer 確保刪除 CR 時先完成清理作業（uncordon 節點、移除 taint、釋放 Lease），再實際移除物件。

## NodeMaintenanceReconciler

::: info 原始碼路徑
`controllers/nodemaintenance_controller.go`
:::

### Reconciler 結構

```go
type NodeMaintenanceReconciler struct {
    client.Client                    // controller-runtime 的 K8s client
    Scheme       *runtime.Scheme     // 用於 runtime 型別對應
    MgrConfig    *rest.Config        // 建立 kubernetes.Clientset 使用
    LeaseManager lease.Manager       // medik8s/common Lease 管理器
    Recorder     record.EventRecorder // 發送 K8s Event
    logger       logr.Logger         // per-reconcile 的 logger
}
```

| 欄位 | 型別 | 說明 |
|------|------|------|
| `Client` | `client.Client` | 嵌入式 controller-runtime Client，用於 CRD/Node 的 CRUD 操作 |
| `Scheme` | `*runtime.Scheme` | GVK ↔ Go 型別映射 |
| `MgrConfig` | `*rest.Config` | 建立 `drain.Helper` 所需的 REST 設定 |
| `LeaseManager` | `lease.Manager` | 來自 `github.com/medik8s/common/pkg/lease`，管理節點維護 Lease |
| `Recorder` | `record.EventRecorder` | 發送 Normal/Warning Event |
| `logger` | `logr.Logger` | 每次 Reconcile 從 context 取得 |

### SetupWithManager

```go
func (r *NodeMaintenanceReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&v1beta1.NodeMaintenance{}).
        Complete(r)
}
```

控制器僅 Watch `NodeMaintenance` 資源本身，不額外 Watch Node 或 Pod 等次要資源。所有對 Node 的操作都在 Reconcile 循環中按需執行。

### RBAC 標記

控制器透過 kubebuilder RBAC 標記自動生成 ClusterRole：

```go
//+kubebuilder:rbac:groups=nodemaintenance.medik8s.io,resources=nodemaintenances,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=nodemaintenance.medik8s.io,resources=nodemaintenances/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=nodemaintenance.medik8s.io,resources=nodemaintenances/finalizers,verbs=update
//+kubebuilder:rbac:groups="",resources=nodes,verbs=get;list;update;patch;watch
//+kubebuilder:rbac:groups="",resources=pods,verbs=get;list;watch
//+kubebuilder:rbac:groups="",resources=pods/eviction,verbs=create
//+kubebuilder:rbac:groups="",resources=namespaces,verbs=get;create
//+kubebuilder:rbac:groups="apps",resources=deployments;daemonsets;replicasets;statefulsets,verbs=get;list;watch
//+kubebuilder:rbac:groups="coordination.k8s.io",resources=leases,verbs=get;list;update;patch;watch;create
//+kubebuilder:rbac:groups="policy",resources=poddisruptionbudgets,verbs=get;list;watch
//+kubebuilder:rbac:groups="monitoring.coreos.com",resources=servicemonitors,verbs=get;create
//+kubebuilder:rbac:groups="oauth.openshift.io",resources=*,verbs=*
```

### Reconcile 核心常數

```go
const (
    maxAllowedErrorToUpdateOwnedLease = 3               // Lease 錯誤容忍上限
    waitDurationOnDrainError          = 5 * time.Second  // Drain 失敗後固定重試間隔
    LeaseHolderIdentity               = "node-maintenance"
    LeaseDuration                     = 3600 * time.Second // Lease 有效期 1 小時
    DrainerTimeout                    = 30 * time.Second   // 單次 Drain 逾時
)
```

### 控制器輔助函式

::: info 原始碼路徑
`controllers/utils.go`
:::

```go
// 檢查字串陣列是否包含特定字串
func ContainsString(slice []string, s string) bool

// 從字串陣列移除特定字串
func RemoveString(slice []string, s string) (result []string)

// 從 Pod 列表提取名稱清單
func GetPodNameList(pods []corev1.Pod) (result []string)

// 從 Pod 列表建立 PodReference 清單（含 Namespace + Name）
func GetPodRefList(pods []corev1.Pod) (result []v1beta1.PodReference)
```

### Taint 管理

::: info 原始碼路徑
`controllers/taint.go`
:::

維護期間會對節點套用兩個 Taint：

```go
const (
    medik8sDrainTaintKey      = "medik8s.io/drain"
    nodeUnschedulableTaintKey = "node.kubernetes.io/unschedulable"
)

var maintenanceTaints = []corev1.Taint{
    {Key: "node.kubernetes.io/unschedulable", Effect: NoSchedule},
    {Key: "medik8s.io/drain",                Effect: NoSchedule},
}
```

`AddOrRemoveTaint` 函式透過 JSON Patch（含 test 操作的樂觀鎖）原子更新節點 Taint：

```go
func AddOrRemoveTaint(clientset kubernetes.Interface, add bool, node *corev1.Node, ctx context.Context) error
```

- **新增 Taint**：使用 `op: add` 將 `maintenanceTaints` 合併到現有 Taint
- **移除 Taint**：使用 `op: replace` 過濾掉維護相關的 Taint
- 兩者都先使用 `op: test` 驗證目前 Taint 值，避免競爭條件

## Webhook 驗證

::: info 原始碼路徑
`api/v1beta1/nodemaintenance_webhook.go`
:::

### Webhook 設定

```go
func (r *NodeMaintenance) SetupWebhookWithManager(isOpenShift bool, mgr ctrl.Manager) error {
    return ctrl.NewWebhookManagedBy(mgr).
        WithValidator(&NodeMaintenanceValidator{
            client:      mgr.GetClient(),
            isOpenShift: isOpenShift,
        }).
        For(r).
        Complete()
}
```

Webhook 路徑由 kubebuilder 標記定義：

```go
//+kubebuilder:webhook:path=/validate-nodemaintenance-medik8s-io-v1beta1-nodemaintenance,
//  mutating=false,failurePolicy=fail,sideEffects=None,
//  groups=nodemaintenance.medik8s.io,resources=nodemaintenances,
//  verbs=create;update,versions=v1beta1,
//  name=vnodemaintenance.kb.io,admissionReviewVersions=v1
```

### NodeMaintenanceValidator 結構

```go
type NodeMaintenanceValidator struct {
    client      client.Client  // 用於查詢 Node 和現有 NM 資源
    isOpenShift bool           // 是否為 OpenShift 叢集
}
```

### ValidateCreate 驗證規則

建立時依序執行三項驗證：

```go
func (v *NodeMaintenanceValidator) ValidateCreate(_ context.Context, obj runtime.Object) (admission.Warnings, error) {
    // 1. 驗證節點存在
    v.validateNodeExists(nodeName)
    // 2. 驗證該節點尚未有 NodeMaintenance
    v.validateNoNodeMaintenanceExists(nodeName)
    // 3. 驗證 control-plane 節點的 etcd quorum
    v.validateControlPlaneQuorum(nodeName)
}
```

| 驗證項目 | 錯誤訊息 | 說明 |
|----------|----------|------|
| 節點存在 | `invalid nodeName, no node with name %s found` | 透過 API Server 查詢節點 |
| 不重複維護 | `invalid nodeName, a NodeMaintenance for node %s already exists` | 列出所有 NM 資源比對 NodeName |
| etcd Quorum | `can not put master/control-plane node into maintenance...` | 僅在 OpenShift 叢集檢查 |

### etcd Quorum 保護邏輯

```go
func (v *NodeMaintenanceValidator) validateControlPlaneQuorum(nodeName string) error {
    if !v.isOpenShift {
        return nil  // 非 OpenShift 直接放行
    }
    // 檢查節點是否為 control-plane
    if !nodes.IsControlPlane(node) {
        return nil  // 非 control-plane 節點直接放行
    }
    // 透過 medik8s/common 的 etcd 套件檢查是否允許中斷
    isDisruptionAllowed, err := etcd.IsEtcdDisruptionAllowed(ctx, v.client, log, node)
    if !isDisruptionAllowed {
        return fmt.Errorf(ErrorControlPlaneQuorumViolation, nodeName)
    }
}
```

相關的 PDB 名稱常數：

```go
const (
    EtcdQuorumPDBNewName   = "etcd-guard-pdb"     // OCP 4.11+
    EtcdQuorumPDBOldName   = "etcd-quorum-guard"   // OCP ≤ 4.10
    EtcdQuorumPDBNamespace = "openshift-etcd"
)
```

### ValidateUpdate 驗證規則

更新時只驗證一項：`spec.NodeName` 不可變更。

```go
func (v *NodeMaintenanceValidator) ValidateUpdate(_ context.Context, oldObj, newObj runtime.Object) (admission.Warnings, error) {
    if nmNew.Spec.NodeName != nmOld.Spec.NodeName {
        return nil, fmt.Errorf(ErrorNodeNameUpdateForbidden)
    }
    return nil, nil
}
```

### ValidateDelete

刪除驗證目前不執行任何檢查，僅記錄日誌：

```go
func (v *NodeMaintenanceValidator) ValidateDelete(_ context.Context, obj runtime.Object) (admission.Warnings, error) {
    nodemaintenancelog.Info("validate delete", "name", nmo.Name)
    return nil, nil
}
```

### Webhook 測試案例

::: info 原始碼路徑
`api/v1beta1/nodemaintenance_webhook_test.go`
:::

測試使用 Ginkgo/Gomega 框架，涵蓋以下場景：

**建立驗證 (ValidateCreate)**

| 測試情境 | 預期結果 |
|----------|----------|
| 節點不存在 | 拒絕，錯誤包含 `ErrorNodeNotExists` |
| 節點已有 NodeMaintenance | 拒絕，錯誤包含 `ErrorNodeMaintenanceExists` |
| Control-plane 節點 + etcd guard pod Ready=True | 拒絕，錯誤包含 `ErrorControlPlaneQuorumViolation` |
| Control-plane 節點 + etcd guard pod Ready=False | 允許（Pod 已失效，不影響 quorum） |
| Control-plane 節點 + 無 etcd guard pod | 允許（該節點沒有 etcd member） |
| Control-plane 節點 + PDB `DisruptionsAllowed=1` | 允許（PDB 允許中斷） |
| Control-plane 節點 + 無 etcd quorum guard PDB | 拒絕 |

**更新驗證 (ValidateUpdate)**

| 測試情境 | 預期結果 |
|----------|----------|
| 修改 `spec.NodeName` | 拒絕，錯誤包含 `ErrorNodeNameUpdateForbidden` |

## RBAC 規則

::: info 原始碼路徑
`config/rbac/role.yaml`（ClusterRole）、`config/rbac/leader_election_role.yaml`（Role）
:::

### manager-role（ClusterRole）

此 ClusterRole 由 kubebuilder RBAC 標記自動產生，涵蓋控制器所有需要的權限：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: manager-role
rules:
  # --- 核心資源 ---
  - apiGroups: [""]
    resources: [namespaces]
    verbs: [create, get]
  - apiGroups: [""]
    resources: [nodes]
    verbs: [get, list, patch, update, watch]
  - apiGroups: [""]
    resources: [pods]
    verbs: [get, list, watch]
  - apiGroups: [""]
    resources: [pods/eviction]
    verbs: [create]

  # --- Apps 資源（drain 需要判斷 owner） ---
  - apiGroups: [apps]
    resources: [daemonsets, deployments, replicasets, statefulsets]
    verbs: [get, list, watch]

  # --- Lease 管理 ---
  - apiGroups: [coordination.k8s.io]
    resources: [leases]
    verbs: [create, get, list, patch, update, watch]

  # --- 監控 ---
  - apiGroups: [monitoring.coreos.com]
    resources: [servicemonitors]
    verbs: [create, get]

  # --- CRD 自身 ---
  - apiGroups: [nodemaintenance.medik8s.io]
    resources: [nodemaintenances]
    verbs: [create, delete, get, list, patch, update, watch]
  - apiGroups: [nodemaintenance.medik8s.io]
    resources: [nodemaintenances/finalizers]
    verbs: [update]
  - apiGroups: [nodemaintenance.medik8s.io]
    resources: [nodemaintenances/status]
    verbs: [get, patch, update]

  # --- OpenShift OAuth（用於 OAuth 代理） ---
  - apiGroups: [oauth.openshift.io]
    resources: ["*"]
    verbs: ["*"]

  # --- PodDisruptionBudget（etcd quorum 檢查） ---
  - apiGroups: [policy]
    resources: [poddisruptionbudgets]
    verbs: [get, list, watch]
```

各權限用途說明：

| API Group | 資源 | 用途 |
|-----------|------|------|
| `""` (core) | `nodes` | Cordon/Uncordon、新增/移除 Taint、設定 OwnerRef |
| `""` (core) | `pods` | 列舉待驅逐的 Pod |
| `""` (core) | `pods/eviction` | 建立 Eviction 子資源以安全驅逐 Pod |
| `""` (core) | `namespaces` | Lease 所在的 Namespace 管理 |
| `apps` | `daemonsets` 等 | `drain.Helper` 判斷 Pod Owner（跳過 DaemonSet） |
| `coordination.k8s.io` | `leases` | 維護 Lease 的取得、續約、釋放 |
| `nodemaintenance.medik8s.io` | `nodemaintenances` | CRD 本身的完整 CRUD |
| `policy` | `poddisruptionbudgets` | Webhook 檢查 etcd quorum PDB |
| `monitoring.coreos.com` | `servicemonitors` | Prometheus 監控整合 |
| `oauth.openshift.io` | `*` | OpenShift OAuth Proxy 所需 |

### leader-election-role（Role）

用於 controller-runtime 的 leader election 機制：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: leader-election-role
rules:
  - apiGroups: [""]
    resources: [configmaps]
    verbs: [get, list, watch, create, update, patch, delete]
  - apiGroups: [coordination.k8s.io]
    resources: [leases]
    verbs: [get, list, watch, create, update, patch, delete]
  - apiGroups: [""]
    resources: [events]
    verbs: [create, patch]
```

::: tip Leader Election 與節點維護 Lease 的區別
- **Leader Election Lease**：存放於 Operator 部署的 Namespace，確保只有一個 Reconciler 副本在運作
- **節點維護 Lease**：透過 `LeaseManager` 管理，每個維護中的節點都有對應的 Lease（`LeaseHolderIdentity = "node-maintenance"`，有效期 3600 秒）
:::

## 工具函式

### Event 輔助函式

::: info 原始碼路徑
`pkg/utils/events.go`
:::

封裝 Kubernetes Event 的建立，統一管理事件原因與訊息：

```go
// 事件原因常數
const (
    EventReasonBeginMaintenance   = "BeginMaintenance"
    EventReasonFailedMaintenance  = "FailedMaintenance"
    EventReasonSucceedMaintenance = "SucceedMaintenance"
    EventReasonUncordonNode       = "UncordonNode"
    EventReasonRemovedMaintenance = "RemovedMaintenance"
)

// 事件訊息常數
const (
    EventMessageBeginMaintenance   = "Begin a node maintenance"
    EventMessageFailedMaintenance  = "Failed a node maintenance"
    EventMessageSucceedMaintenance = "Node maintenance was succeeded"
    EventMessageUncordonNode       = "Uncordon a node"
    EventMessageRemovedMaintenance = "Removed a node maintenance"
)

// 記錄 Normal 級別事件
func NormalEvent(recorder record.EventRecorder, object runtime.Object, reason, message string)

// 記錄 Warning 級別事件
func WarningEvent(recorder record.EventRecorder, object runtime.Object, reason, message string)
```

事件在 Reconcile 循環中的觸發時機：

| 函式 | 事件類型 | 觸發時機 |
|------|----------|----------|
| `NormalEvent` + `BeginMaintenance` | Normal | 新增 Finalizer 時（維護開始） |
| `NormalEvent` + `SucceedMaintenance` | Normal | Drain 完成時 |
| `NormalEvent` + `UncordonNode` | Normal | 停止維護並 Uncordon |
| `NormalEvent` + `RemovedMaintenance` | Normal | 移除 Finalizer 時（CR 被刪除） |
| `WarningEvent` + `FailedMaintenance` | Warning | 節點不存在或 Lease 錯誤過多 |

### OpenShift 驗證工具

::: info 原始碼路徑
`pkg/utils/validation.go`
:::

透過 Discovery API 判斷叢集是否為 OpenShift：

```go
type OpenshiftValidator struct {
    isOpenshiftSupported bool
}

func NewOpenshiftValidator(config *rest.Config) (*OpenshiftValidator, error)
func (v *OpenshiftValidator) IsOpenshiftSupported() bool
```

判斷邏輯：查詢 API Server 的 ServerGroups，若存在 `config.openshift.io/v1` 的 `ClusterVersion` 資源，即判定為 OpenShift。

```go
func (v *OpenshiftValidator) validateIsOpenshift(config *rest.Config) error {
    dc, _ := discovery.NewDiscoveryClientForConfig(config)
    apiGroups, _ := dc.ServerGroups()
    kind := schema.GroupVersionKind{
        Group: "config.openshift.io", Version: "v1", Kind: "ClusterVersion",
    }
    for _, apiGroup := range apiGroups.Groups {
        for _, ver := range apiGroup.Versions {
            if ver.GroupVersion == kind.GroupVersion().String() {
                v.isOpenshiftSupported = true
                return nil
            }
        }
    }
    return nil
}
```

此結果會傳遞給 `SetupWebhookWithManager(isOpenShift, mgr)`，決定是否啟用 etcd quorum 驗證。

## CRD YAML 定義

::: info 原始碼路徑
`config/crd/bases/nodemaintenance.medik8s.io_nodemaintenances.yaml`
:::

### 基本資訊

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.20.0
  name: nodemaintenances.nodemaintenance.medik8s.io
spec:
  group: nodemaintenance.medik8s.io
  names:
    kind: NodeMaintenance
    listKind: NodeMaintenanceList
    plural: nodemaintenances
    shortNames: [nm]
    singular: nodemaintenance
  scope: Cluster
```

| 屬性 | 值 | 說明 |
|------|------|------|
| `group` | `nodemaintenance.medik8s.io` | API Group |
| `scope` | `Cluster` | 叢集範圍資源 |
| `shortNames` | `nm` | 簡稱，可用 `kubectl get nm` |
| `controller-gen` | `v0.20.0` | 程式碼產生器版本 |

### OpenAPI v3 Schema

**Spec 欄位驗證：**

```yaml
spec:
  description: NodeMaintenanceSpec defines the desired state of NodeMaintenance
  properties:
    nodeName:
      description: Node name to apply maintanance on/off
      type: string
    reason:
      description: Reason for maintanance
      type: string
  required:
    - nodeName
  type: object
```

- `nodeName` 是唯一的必填欄位（CRD 層級驗證）
- `reason` 為選填字串

**Status 欄位定義：**

```yaml
status:
  description: NodeMaintenanceStatus defines the observed state of NodeMaintenance
  properties:
    phase:
      description: "Phase is the represtation of the maintenance progress (Running,Succeeded,Failed)"
      type: string
    drainProgress:
      description: Percentage completion of draining the node
      type: integer
    lastUpdate:
      description: The last time the status has been updated
      format: date-time
      type: string
    lastError:
      description: LastError represents the latest error if any
      type: string
    pendingPods:
      description: PendingPods is a list of pending pods for eviction
      type: array
      items:
        type: string
    pendingPodsRefs:
      description: PendingPodsRefs is a list of refs of pending pods for eviction
      type: array
      items:
        properties:
          namespace:
            type: string
          name:
            type: string
        type: object
    totalpods:
      description: TotalPods is the total number of all pods on the node
      type: integer
    evictionPods:
      description: EvictionPods is the total number of pods up for eviction
      type: integer
    errorOnLeaseCount:
      description: Consecutive number of errors upon obtaining a lease
      type: integer
  type: object
```

### 子資源與版本

```yaml
versions:
  - name: v1beta1
    served: true
    storage: true
    subresources:
      status: {}
```

::: tip 注意事項
- **`served: true`**：API Server 會提供此版本的端點
- **`storage: true`**：etcd 中以此版本格式儲存
- **`subresources.status`**：Status 透過 `/status` 子端點獨立更新，主 Spec 更新不會影響 Status
- 目前 CRD 沒有定義額外的 **printer columns**，`kubectl get nm` 僅顯示預設欄位（NAME、AGE）
:::
