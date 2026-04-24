---
layout: doc
title: Cluster API — 核心功能
---

# Cluster API — 核心功能

## 核心 CRD 概覽

Cluster API v1beta2 定義了以下核心資源（位於 `api/core/v1beta2/`）：

| 資源 | Kind | 說明 |
|------|------|------|
| 叢集 | `Cluster` | 代表一個完整的 Kubernetes 叢集 |
| 叢集類別 | `ClusterClass` | 叢集範本，支援 Topology 管理 |
| 機器 | `Machine` | 代表叢集中的一個節點（VM/實體機） |
| 機器集合 | `MachineSet` | 管理一組相同設定的 Machine（類似 ReplicaSet）|
| 機器部署 | `MachineDeployment` | 管理 MachineSet 滾動升級（類似 Deployment）|
| 機器池 | `MachinePool` | 以雲端提供商原生機制管理節點群組 |
| 機器健康檢查 | `MachineHealthCheck` | 定義並執行節點健康監控與自動修復 |

## Cluster — 叢集資源

`Cluster` 是 CAPI 最核心的資源，代表一個目標 Kubernetes 叢集。

```go
// 檔案: api/core/v1beta2/cluster_types.go
const (
    // ClusterFinalizer 用於確保刪除時正確清理資源
    ClusterFinalizer = "cluster.cluster.x-k8s.io"

    // ClusterKind 代表 Cluster 的 Kind 名稱
    ClusterKind = "Cluster"
)

type Cluster struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   ClusterSpec   `json:"spec,omitempty,omitzero"`
    Status ClusterStatus `json:"status,omitempty,omitzero"`
}
```

### ClusterSpec 關鍵欄位

`ClusterSpec` 透過 `infrastructureRef` 和 `controlPlaneRef` 引用對應的 Provider 資源：

```yaml
# 檔案: config/samples/cluster.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: my-cluster
  namespace: default
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["192.168.0.0/16"]
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: DockerCluster
    name: my-cluster
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: my-cluster-control-plane
```

### Cluster 可用性條件

```go
// 檔案: api/core/v1beta2/cluster_types.go
const (
    // ClusterAvailableCondition 在以下條件均為 true 時設為 true：
    // RemoteConnectionProbe、InfrastructureReady、ControlPlaneAvailable、WorkersAvailable
    ClusterAvailableCondition = AvailableCondition

    // ClusterTopologyReconciledCondition 僅在使用 ClusterClass 時存在
    ClusterTopologyReconciledCondition = "TopologyReconciled"
)
```

## Machine — 節點資源

`Machine` 代表叢集中的一個節點，封裝了節點生命週期管理：

```go
// 檔案: api/core/v1beta2/machine_types.go
const (
    MachineFinalizer = "machine.cluster.x-k8s.io"

    // MachineControlPlaneLabel 標記控制平面節點
    MachineControlPlaneLabel = "cluster.x-k8s.io/control-plane"

    // ExcludeNodeDrainingAnnotation 跳過節點 drain（用於測試或特殊場景）
    ExcludeNodeDrainingAnnotation = "machine.cluster.x-k8s.io/exclude-node-draining"

    // PreTerminateDeleteHookAnnotationPrefix 實現 pre-terminate hook
    PreTerminateDeleteHookAnnotationPrefix = "pre-terminate.delete.hook.machine.cluster.x-k8s.io"
)
```

### Machine 生命週期 Phase

| Phase | 說明 |
|-------|------|
| `Pending` | Machine 已建立，等待 Bootstrap |
| `Provisioning` | Infrastructure Provider 正在佈建 VM |
| `Provisioned` | VM 已佈建，Bootstrap 尚未完成 |
| `Running` | Machine 對應的 Node 已加入叢集 |
| `Deleting` | Machine 正在被刪除（drain → 刪除 infra）|
| `Failed` | Machine 遭遇不可恢復的錯誤 |
| `Unknown` | Machine 狀態未知 |

## MachineSet — 副本管理

`MachineSet` 類似 Kubernetes 的 `ReplicaSet`，確保指定數量的 Machine 持續運行：

```go
// 檔案: api/core/v1beta2/machineset_types.go
const (
    MachineSetFinalizer = "cluster.x-k8s.io/machineset"

    // MachineSetTopologyFinalizer 用於 Topology 管理的 MachineSet
    MachineSetTopologyFinalizer = "machineset.topology.cluster.x-k8s.io"
)

type MachineSet struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   MachineSetSpec   `json:"spec,omitempty"`
    Status MachineSetStatus `json:"status,omitempty"`
}
```

## MachineDeployment — 滾動升級

`MachineDeployment` 類似 Kubernetes 的 `Deployment`，管理多個 `MachineSet` 實現滾動升級：

```go
// 檔案: api/core/v1beta2/machinedeployment_types.go
const (
    MachineDeploymentFinalizer = "cluster.x-k8s.io/machinedeployment"
)

// MachineDeploymentRolloutStrategyType 定義滾動升級策略
type MachineDeploymentRolloutStrategyType string

const (
    // RollingUpdateMachineDeploymentStrategyType 漸進式替換：先 scale up 新 MachineSet，再 scale down 舊 MachineSet
    RollingUpdateMachineDeploymentStrategyType MachineDeploymentRolloutStrategyType = "RollingUpdate"

    // OnDeleteMachineDeploymentStrategyType 等待舊 Machine 被刪除後才建立新的
    OnDeleteMachineDeploymentStrategyType MachineDeploymentRolloutStrategyType = "OnDelete"
)
```

### MachineDeployment vs MachineSet 比較

| 特性 | MachineSet | MachineDeployment |
|------|-----------|-------------------|
| 副本管理 | ✅ | ✅（透過 MachineSet）|
| 滾動升級 | ❌ | ✅ |
| 版本歷史 | ❌ | ✅ |
| 適用場景 | 靜態 Worker Pool | 需要升級的 Worker Pool |

## MachinePool — 雲端原生節點池

`MachinePool` 利用雲端平台原生的伸縮機制（如 AWS ASG、Azure VMSS）管理節點，適合大規模叢集：

```go
// 檔案: api/core/v1beta2/machinepool_types.go
const (
    MachinePoolFinalizer = "machinepool.cluster.x-k8s.io"
)
```

::: tip MachinePool vs MachineDeployment
`MachinePool` 將節點管理委派給雲端平台原生機制，而 `MachineDeployment` 由 CAPI 自行管理每一台 Machine。前者適合大規模彈性擴縮，後者有更精細的控制能力。
:::

## MachineHealthCheck — 健康監控

`MachineHealthCheck` 定義健康監控策略，自動偵測並修復不健康的節點：

```yaml
# 檔案: config/samples/machinehealthcheck.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: MachineHealthCheck
metadata:
  name: my-cluster-mhc
spec:
  clusterName: my-cluster
  selector:
    matchLabels:
      nodepool: worker
  unhealthyConditions:
  - type: Ready
    status: "False"
    timeout: 300s
  - type: Ready
    status: Unknown
    timeout: 300s
  maxUnhealthy: "33%"
```

::: warning 注意 maxUnhealthy
`maxUnhealthy` 設定上限以防止大量節點同時觸發修復，避免導致叢集不可用。建議生產環境設為 33%~50%。
:::

::: info 相關章節
- [系統架構](./architecture)
- [控制器與 API](./controllers-api)
- [叢集生命週期](./lifecycle)
:::
