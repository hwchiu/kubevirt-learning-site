---
layout: doc
title: Cluster API — ClusterClass 與 Topology
---

# Cluster API — ClusterClass 與 Topology

## 什麼是 ClusterClass？

ClusterClass 是 CAPI 提供的「叢集範本」機制，讓平台工程師定義一套標準的叢集架構（包含 Infrastructure、ControlPlane、Workers 的範本），讓開發團隊只需填寫少量參數即可建立符合標準的叢集。

::: tip 使用前提
ClusterClass 需要啟用 `ClusterTopology` Feature Gate。在 CAPI v1.3+ 版本中，此功能已預設啟用。
:::

## ClusterClass 結構

```go
// 檔案: api/core/v1beta2/clusterclass_types.go
const (
    ClusterClassKind = "ClusterClass"

    // ClusterClassVariablesReadyCondition 所有變數（inline + external）就緒時為 true
    ClusterClassVariablesReadyCondition = "VariablesReady"
)

// ClusterClassSpec 定義叢集範本的完整結構
type ClusterClassSpec struct {
    // Infrastructure 定義 InfraCluster 的範本引用
    Infrastructure InfrastructureClass `json:"infrastructure,omitempty,omitzero"`

    // ControlPlane 定義控制平面的範本引用與健康檢查設定
    ControlPlane ControlPlaneClass `json:"controlPlane,omitempty,omitzero"`

    // Workers 定義 Worker 節點池的範本清單
    Workers WorkersClass `json:"workers,omitempty,omitzero"`
}
```

### ClusterClass 組成元件

```go
// 檔案: api/core/v1beta2/clusterclass_types.go

// InfrastructureClass 定義基礎設施範本
type InfrastructureClass struct {
    // Ref 引用 InfraClusterTemplate 資源
}

// ControlPlaneClass 定義控制平面範本
type ControlPlaneClass struct {
    // healthCheck 為此 ControlPlaneClass 定義 MachineHealthCheck
}

// WorkersClass 包含所有 Worker 節點池的範本
type WorkersClass struct {
    // MachineDeployments 定義多個 Worker 節點池範本
    MachineDeployments []MachineDeploymentClass
}

// MachineDeploymentClass 定義一組 Worker 節點的範本
type MachineDeploymentClass struct {
    // healthCheck 定義此節點池的健康檢查策略
}
```

## ClusterClass YAML 範例

```yaml
# 檔案: config/samples/clusterclass-quick-start.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: ClusterClass
metadata:
  name: quick-start
  namespace: default
spec:
  infrastructure:
    ref:
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
      kind: DockerClusterTemplate
      name: quick-start-cluster
  controlPlane:
    ref:
      apiVersion: controlplane.cluster.x-k8s.io/v1beta1
      kind: KubeadmControlPlaneTemplate
      name: quick-start-control-plane
    machineInfrastructure:
      ref:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: DockerMachineTemplate
        name: quick-start-control-plane
  workers:
    machineDeployments:
    - class: default-worker
      template:
        bootstrap:
          ref:
            apiVersion: bootstrap.cluster.x-k8s.io/v1beta1
            kind: KubeadmConfigTemplate
            name: quick-start-default-worker-bootstraptemplate
        infrastructure:
          ref:
            apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
            kind: DockerMachineTemplate
            name: quick-start-default-worker-machinetemplate
  variables:
  - name: imageRepository
    required: true
    schema:
      openAPIV3Schema:
        type: string
        default: "k8s.gcr.io"
```

## Topology — 拓撲化叢集

使用 ClusterClass 建立的叢集稱為「拓撲化叢集（Topology Cluster）」，在 `Cluster.spec.topology` 欄位設定：

```go
// 檔案: api/core/v1beta2/cluster_types.go

// Topology 封裝所有被 ClusterClass 管理的資源資訊
type Topology struct {
    // ControlPlane 定義控制平面的拓撲設定（副本數、版本等）
    ControlPlane ControlPlaneTopology `json:"controlPlane,omitempty,omitzero"`

    // Workers 定義各 Worker 節點池的拓撲設定
    Workers WorkersTopology `json:"workers,omitempty,omitzero"`
}
```

### 使用 ClusterClass 建立叢集

```yaml
# 檔案: config/samples/cluster-topology.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: my-cluster
  namespace: default
spec:
  topology:
    class: quick-start              # 引用 ClusterClass 名稱
    version: v1.31.0                # Kubernetes 版本
    controlPlane:
      replicas: 3                   # 控制平面副本數
    workers:
      machineDeployments:
      - class: default-worker       # 對應 ClusterClass.workers.machineDeployments[].class
        name: md-0
        replicas: 2
    variables:
    - name: imageRepository
      value: "registry.k8s.io"
```

## Topology Reconciler 機制

`TopologyReconciler` 負責根據 ClusterClass + Cluster topology 設定，自動生成並管理底層的 Infrastructure、ControlPlane 和 MachineDeployment 資源：

| Topology 狀態 | 說明 |
|--------------|------|
| `TopologyReconciled: True` | 所有拓撲資源已按照 ClusterClass 設定協調完成 |
| `TopologyReconciled: False` | 正在協調中（叢集建立、升級等過程）|
| `ClusterTopologyReconciledCondition` | 詳細協調狀態（`ReconcileSucceeded`, `ReconcileFailed` 等）|

## ClusterClass 變數與 Patches

ClusterClass 支援**變數（Variables）**和**補丁（Patches）**機制，讓範本更加靈活：

| 機制 | 說明 |
|------|------|
| **Variables** | 使用者可在 Cluster.spec.topology.variables 傳入值 |
| **Inline Patches** | ClusterClass 內定義的 JSONPatch，根據變數動態修改範本 |
| **External Patches** | 透過 Runtime Extension Webhook 動態生成補丁 |

::: warning 使用限制
ClusterClass 建立的叢集，其底層 Infrastructure/ControlPlane 資源由 TopologyReconciler 全權管理，不應直接手動修改這些資源，否則會被 reconcile 覆寫。
:::

::: info 相關章節
- [核心功能](./core-features)
- [控制器與 API](./controllers-api)
- [叢集生命週期](./lifecycle)
:::
