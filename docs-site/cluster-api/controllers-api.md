---
layout: doc
title: Cluster API — 控制器與 CRD API
---

# Cluster API — 控制器與 CRD API

## 控制器架構總覽

CAPI 的控制器分佈在多個套件中，並在啟動時統一由 `internal/setup` 初始化：

| 套件路徑 | 控制器 | 說明 |
|---------|--------|------|
| `internal/controllers/cluster` | `ClusterReconciler` | 協調叢集基礎設施與控制平面 |
| `internal/controllers/machine` | `MachineReconciler` | 協調單一 Machine 生命週期 |
| `internal/controllers/machineset` | `MachineSetReconciler` | 管理 Machine 副本數 |
| `internal/controllers/machinedeployment` | `MachineDeploymentReconciler` | 管理滾動升級 |
| `internal/controllers/machinehealthcheck` | `MachineHealthCheckReconciler` | 健康監控與修復 |
| `internal/controllers/topology/cluster` | `TopologyReconciler` | ClusterClass 拓撲協調 |
| `internal/controllers/clusterclass` | `ClusterClassReconciler` | ClusterClass 本身協調 |

## Cluster Controller

`ClusterReconciler` 是 CAPI 最核心的控制器，負責協調整個叢集的生命週期：

```go
// 檔案: internal/controllers/cluster/cluster_controller.go
// Reconciler reconciles a Cluster object.
type Reconciler struct {
    Client       client.Client
    APIReader    client.Reader
    ClusterCache clustercache.ClusterCache
    // ... 其他欄位
}

func (r *Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (retRes ctrl.Result, reterr error) {
    // 1. 取得 Cluster 物件
    // 2. 處理 Pause 狀態
    // 3. 協調 Infrastructure（呼叫 InfraProvider）
    // 4. 協調 ControlPlane（呼叫 ControlPlaneProvider）
    // 5. 協調 Workers（更新 MachineSet/MachineDeployment）
    // 6. 更新 Status
}
```

### Cluster RBAC 設定

```go
// 檔案: internal/controllers/cluster/cluster_controller.go
// +kubebuilder:rbac:groups=infrastructure.cluster.x-k8s.io;bootstrap.cluster.x-k8s.io;controlplane.cluster.x-k8s.io,resources=*,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=cluster.x-k8s.io,resources=clusters;clusters/status;clusters/finalizers,verbs=get;list;watch;update;patch
```

## ClusterClass Controller

`ClusterClassReconciler` 負責 ClusterClass 資源的協調，確保引用的 Template 版本正確：

```go
// 檔案: api/core/v1beta2/clusterclass_types.go
const (
    ClusterClassKind = "ClusterClass"

    // ClusterClassVariablesReadyCondition 當所有 inline/external 變數就緒時為 true
    ClusterClassVariablesReadyCondition = "VariablesReady"

    // ClusterClassRefVersionsUpToDateCondition 確認所有引用使用最新 apiVersion
    ClusterClassRefVersionsUpToDateCondition = "RefVersionsUpToDate"
)

// ClusterClass 是拓撲化叢集的範本
// +kubebuilder:resource:path=clusterclasses,shortName=cc,scope=Namespaced,categories=cluster-api
type ClusterClass struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   ClusterClassSpec   `json:"spec,omitempty,omitzero"`
    Status ClusterClassStatus `json:"status,omitempty,omitzero"`
}
```

## KubeadmControlPlane Controller

`KubeadmControlPlane`（KCP）是內建的 ControlPlane Provider，負責管理使用 kubeadm 初始化的控制平面：

```go
// 檔案: api/controlplane/kubeadm/v1beta2/kubeadm_control_plane_types.go
const (
    KubeadmControlPlaneFinalizer = "kubeadm.controlplane.cluster.x-k8s.io"

    // SkipCoreDNSAnnotation 跳過 CoreDNS reconcile
    SkipCoreDNSAnnotation = "controlplane.cluster.x-k8s.io/skip-coredns"

    // SkipKubeProxyAnnotation 跳過 kube-proxy reconcile
    SkipKubeProxyAnnotation = "controlplane.cluster.x-k8s.io/skip-kube-proxy"

    // PreTerminateHookCleanupAnnotation 確保 etcd member 在機器終止前正確移除
    PreTerminateHookCleanupAnnotation = clusterv1.PreTerminateDeleteHookAnnotationPrefix + "/kcp-cleanup"
)

// KubeadmControlPlane 管理使用 kubeadm 的控制平面
// KubeadmControlPlaneAvailableCondition 在以下條件均滿足時為 true：
// - CertificatesAvailable
// - 至少一台 Machine 的控制平面元件健康
// - etcd 有足夠成員維持 quorum
type KubeadmControlPlane struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   KubeadmControlPlaneSpec
    Status KubeadmControlPlaneStatus
}
```

### KCP 滾動升級策略

```go
// 檔案: api/controlplane/kubeadm/v1beta2/kubeadm_control_plane_types.go
// KubeadmControlPlaneRolloutStrategyType 目前僅支援 RollingUpdate
type KubeadmControlPlaneRolloutStrategyType string

const (
    // RollingUpdateStrategyType 漸進式替換舊的控制平面節點
    RollingUpdateStrategyType KubeadmControlPlaneRolloutStrategyType = "RollingUpdate"
)
```

## Bootstrap Controller — KubeadmConfig

`KubeadmConfig` 負責為每台 Machine 產生 kubeadm 初始化腳本（cloud-init）：

```go
// 檔案: api/bootstrap/kubeadm/v1beta2/kubeadmconfig_types.go
type KubeadmConfig struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   KubeadmConfigSpec   `json:"spec,omitempty"`
    Status KubeadmConfigStatus `json:"status,omitempty"`
}
```

## CRD 版本對照

| API Group | 版本 | 資源 |
|-----------|------|------|
| `cluster.x-k8s.io` | `v1beta2` | Cluster, Machine, MachineSet, MachineDeployment, MachinePool, MachineHealthCheck, ClusterClass |
| `controlplane.cluster.x-k8s.io` | `v1beta2` | KubeadmControlPlane |
| `bootstrap.cluster.x-k8s.io` | `v1beta2` | KubeadmConfig, KubeadmConfigTemplate |
| `addons.cluster.x-k8s.io` | `v1beta2` | ClusterResourceSet |
| `ipam.cluster.x-k8s.io` | `v1beta2` | IPAddress, IPAddressClaim |
| `runtime.cluster.x-k8s.io` | `v1beta2` | ExtensionConfig |

## Feature Gates

CAPI 使用 Kubernetes Feature Gate 機制控制實驗性功能：

```go
// 檔案: feature/gates.go
var (
    // MutableGates 是可修改的 FeatureGate，供頂層命令設定使用
    MutableGates featuregate.MutableFeatureGate = featuregate.NewFeatureGate()

    // Gates 是共用的唯讀 FeatureGate
    Gates featuregate.FeatureGate = MutableGates
)
```

::: tip 重要 Feature Gate
`ClusterTopology`（控制 ClusterClass 與 Topology 功能）預設在 v1.3+ 版本啟用。實驗性功能如 `MachinePool` 需要手動啟用。
:::

::: info 相關章節
- [系統架構](./architecture)
- [Provider 模型](./providers)
- [ClusterClass 與 Topology](./clusterclass)
:::
