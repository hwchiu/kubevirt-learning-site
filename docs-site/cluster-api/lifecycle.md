---
layout: doc
title: Cluster API — 叢集生命週期
---

# Cluster API — 叢集生命週期

## 生命週期總覽

CAPI 管理的叢集有完整的生命週期，從建立到刪除，每個階段都由對應的控制器負責：

| 階段 | 觸發條件 | 主要動作 |
|------|---------|---------|
| **建立** | 使用者建立 Cluster CRD | 佈建 Infrastructure → 初始化 ControlPlane → 建立 Workers |
| **運行** | 叢集正常運作 | 持續 reconcile，確保狀態符合期望 |
| **擴縮** | 修改 replicas 欄位 | MachineSet/MachineDeployment 自動增減 Machine |
| **升級** | 修改 version 欄位 | 滾動替換控制平面與 Worker 節點 |
| **修復** | MachineHealthCheck 偵測到異常 | 刪除並重建不健康的 Machine |
| **刪除** | 使用者刪除 Cluster CRD | 排空節點 → 刪除 Machine → 刪除 Infrastructure |

## 叢集建立流程

```
使用者 apply Cluster YAML
        │
        ▼
ClusterReconciler 偵測到新 Cluster
        │
        ├─ 協調 Infrastructure（呼叫 InfraProvider）
        │   └─ InfraCluster status.ready = true
        │
        ├─ 協調 ControlPlane（呼叫 KubeadmControlPlane）
        │   ├─ 建立第一台控制平面 Machine
        │   ├─ kubeadm init → 產生 kubeconfig
        │   └─ KCP status.initialized = true
        │
        ├─ 若有多台控制平面，繼續 join
        │
        └─ 建立 Worker MachineDeployment/MachineSet
            └─ MachineSet 建立對應 Machine → 加入叢集
```

### 建立叢集的關鍵欄位

```go
// 檔案: api/core/v1beta2/cluster_types.go
const (
    // ClusterFinalizer 確保刪除時正確清理所有子資源
    ClusterFinalizer = "cluster.cluster.x-k8s.io"
)

type ClusterSpec struct {
    // Paused 暫停所有協調（可用於維護）
    // Topology 拓撲設定（使用 ClusterClass 時）
    // InfrastructureRef 引用 InfraCluster 資源
    // ControlPlaneRef 引用 ControlPlane 資源
    // ClusterNetwork 定義叢集網路 CIDR
}
```

## 節點擴縮

### 手動擴縮（Worker 節點）

直接修改 `MachineDeployment.spec.replicas`：

```yaml
# 檔案: config/samples/machinedeployment-scale.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: MachineDeployment
metadata:
  name: my-cluster-md-0
  namespace: default
spec:
  clusterName: my-cluster
  replicas: 5           # 從 3 擴充到 5
  template:
    spec:
      version: "v1.31.0"
      clusterName: my-cluster
      bootstrap:
        configRef:
          apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
          kind: KubeadmConfigTemplate
          name: my-cluster-worker
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: DockerMachineTemplate
        name: my-cluster-worker
```

### 擴縮策略

| 策略類型 | 說明 | 適用場景 |
|---------|------|---------|
| `RollingUpdate` | 先建新再刪舊，保持最低可用副本 | 一般升級場景 |
| `OnDelete` | 等舊 Machine 被手動刪除後才建新的 | 需要精細控制的場景 |

## 叢集升級

叢集升級分為**控制平面升級**和 **Worker 節點升級**兩個階段。

### 控制平面升級（KubeadmControlPlane）

修改 `KubeadmControlPlane.spec.version` 觸發升級：

```yaml
# 檔案: config/samples/kubeadmcontrolplane-upgrade.yaml
apiVersion: controlplane.cluster.x-k8s.io/v1beta2
kind: KubeadmControlPlane
metadata:
  name: my-cluster-control-plane
spec:
  version: v1.32.0          # 更新版本號觸發滾動升級
  replicas: 3
  rolloutStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1            # 最多同時有 1 台額外節點
```

::: warning 升級順序限制
CAPI 強制要求先升級控制平面，再升級 Worker 節點。且控制平面版本不能低於 Worker 節點版本（符合 Kubernetes 版本偏差政策）。
:::

### Worker 節點升級

修改 `MachineDeployment.spec.template.spec.version`：

```go
// 檔案: api/core/v1beta2/machinedeployment_types.go
const (
    // RevisionAnnotation 記錄 MachineSet 的滾動升級序號
    RevisionAnnotation = "machinedeployment.clusters.x-k8s.io/revision"

    // MachineDeploymentUniqueLabel 用於唯一識別 MachineSet 的 Machine
    MachineDeploymentUniqueLabel = "machine-template-hash"
)
```

升級流程：
1. `MachineDeploymentReconciler` 建立新的 `MachineSet`（新版本）
2. 逐步 scale up 新 `MachineSet`，scale down 舊 `MachineSet`
3. 新 `Machine` 建立並加入叢集後，對應舊 `Machine` 被 drain 並刪除

## Machine 刪除流程

Machine 刪除涉及多個 Hook 機制確保安全：

```go
// 檔案: api/core/v1beta2/machine_types.go
const (
    // PreDrainDeleteHookAnnotationPrefix 阻止節點 drain，直到所有 Hook 移除
    PreDrainDeleteHookAnnotationPrefix = "pre-drain.delete.hook.machine.cluster.x-k8s.io"

    // PreTerminateDeleteHookAnnotationPrefix 阻止基礎設施刪除，直到所有 Hook 移除
    // KCP 會加入 kcp-cleanup hook，確保 etcd member 在最後才移除
    PreTerminateDeleteHookAnnotationPrefix = "pre-terminate.delete.hook.machine.cluster.x-k8s.io"
)
```

### 刪除順序

```
Machine 被標記刪除
    │
    ├─ 執行 pre-drain hooks（等待外部 hook 完成）
    │
    ├─ Node Drain（驅逐 Pod，等待 PDB）
    │
    ├─ 執行 pre-terminate hooks
    │   └─ KCP 的 kcp-cleanup：移除 etcd member
    │
    └─ 呼叫 Infrastructure Provider 刪除 VM
```

## 叢集暫停（Pause）

在維護期間，可以暫停 CAPI 對特定叢集的協調：

```yaml
# 檔案: config/samples/cluster-pause.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: my-cluster
  annotations:
    cluster.x-k8s.io/paused: "true"    # 暫停整個叢集的協調
```

::: tip 暫停的用途
暫停功能常用於：1）手動修復時避免 reconcile 干擾；2）`clusterctl move` 遷移過程中；3）Provider 升級維護。
:::

::: info 相關章節
- [核心功能](./core-features)
- [ClusterClass 與 Topology](./clusterclass)
- [外部整合](./integration)
:::
