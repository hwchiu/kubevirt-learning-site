---
layout: doc
title: Cluster API — 故事驅動式學習
---

# Cluster API — 故事驅動式學習

## 情境：雲原生平台工程師的一天

小明是某金融科技公司的平台工程師。公司的工程團隊快速成長，每個業務線都需要自己的 Kubernetes 叢集，而且要求快速佈建、統一規格、並能在不同基礎設施上運行（公有雲 + 私有雲）。

傳統方式需要寫大量 Terraform + Ansible 腳本，維護成本極高。主管建議小明評估 **Cluster API（CAPI）**。

---

## 第一章：認識 CAPI 架構

小明首先要理解 CAPI 的核心概念。

> 「所以 CAPI 就是用 Kubernetes 管理 Kubernetes？」

正是！CAPI 引入了 **Management Cluster** 的概念：

```
公司內網的 Kubernetes（Management Cluster）
    │
    ├─ 管理 dev-cluster（AWS ap-northeast-1）
    ├─ 管理 staging-cluster（AWS ap-northeast-1）
    └─ 管理 prod-cluster（vSphere 私有雲）
```

每個 Workload Cluster 都是一個 `Cluster` CRD：

```go
// 檔案: api/core/v1beta2/cluster_types.go
const (
    ClusterFinalizer = "cluster.cluster.x-k8s.io"
    ClusterKind      = "Cluster"
)

// 每個 Cluster 物件代表一個目標 Kubernetes 叢集
type Cluster struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   ClusterSpec   `json:"spec,omitempty,omitzero"`
    Status ClusterStatus `json:"status,omitempty,omitzero"`
}
```

小明理解了：Management Cluster 是控制平面，CAPI Core CRD 定義了「期望狀態」，Provider 負責讓基礎設施達到那個狀態。

---

## 第二章：初始化 Management Cluster

小明決定先在本機用 Docker Provider（CAPD）實驗。

```bash
# 建立 kind 叢集作為 Management Cluster
kind create cluster --name capi-management

# 安裝 CAPI Core + Docker Provider
clusterctl init --infrastructure docker
```

背後發生了什麼？`clusterctl init` 會：
1. 安裝 CAPI Core CRD（`Cluster`, `Machine`, `MachineSet` 等）
2. 部署 CAPI Core Controller Manager
3. 安裝 Bootstrap Provider（kubeadm）
4. 安裝 ControlPlane Provider（KubeadmControlPlane）
5. 安裝 Infrastructure Provider（DockerCluster）

---

## 第三章：建立第一個 Workload Cluster

```bash
# 產生叢集 YAML
clusterctl generate cluster dev-cluster \
  --flavor development \
  --kubernetes-version v1.31.0 \
  --control-plane-machine-count=1 \
  --worker-machine-count=2 > dev-cluster.yaml

# 套用
kubectl apply -f dev-cluster.yaml
```

套用後，Management Cluster 上出現了一系列物件：

| 物件 | 說明 |
|------|------|
| `Cluster/dev-cluster` | 主要叢集物件 |
| `KubeadmControlPlane/dev-cluster-control-plane` | 控制平面（1 台）|
| `MachineDeployment/dev-cluster-md-0` | Worker 節點池（2 台）|
| `DockerCluster/dev-cluster` | Docker 基礎設施 |

小明觀察到整個建立流程：

```
Cluster Controller 偵測到 Cluster
→ DockerCluster status.ready = true
→ KubeadmControlPlane 建立第一台控制平面 Machine
→ Machine Controller 呼叫 DockerMachine（建立容器模擬 VM）
→ KubeadmConfig 產生 cloud-init（kubeadm init 腳本）
→ 節點加入叢集，Machine status.phase = Running
→ MachineDeployment 建立 2 台 Worker Machine
→ 叢集就緒！
```

---

## 第四章：ClusterClass 讓叢集標準化

公司有多個業務線，每個都要建相似的叢集，但每次都要寫複雜的 YAML。

小明的主管說：「用 ClusterClass 吧！」

```yaml
# 檔案: config/samples/clusterclass.yaml
# 平台團隊定義一次，業務線重複使用
apiVersion: cluster.x-k8s.io/v1beta2
kind: ClusterClass
metadata:
  name: company-standard
spec:
  infrastructure:
    ref:
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
      kind: DockerClusterTemplate
      name: company-standard-infra
  controlPlane:
    ref:
      apiVersion: controlplane.cluster.x-k8s.io/v1beta1
      kind: KubeadmControlPlaneTemplate
      name: company-standard-control-plane
  workers:
    machineDeployments:
    - class: worker
      template:
        bootstrap:
          ref:
            apiVersion: bootstrap.cluster.x-k8s.io/v1beta1
            kind: KubeadmConfigTemplate
            name: company-standard-worker
        infrastructure:
          ref:
            apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
            kind: DockerMachineTemplate
            name: company-standard-worker
```

現在業務線只需要這樣建叢集：

```yaml
# 檔案: config/samples/cluster-topology-simple.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: payment-cluster
spec:
  topology:
    class: company-standard       # 引用公司標準範本
    version: v1.31.0
    controlPlane:
      replicas: 3
    workers:
      machineDeployments:
      - class: worker
        name: md-0
        replicas: 5
```

---

## 第五章：叢集升級

三個月後，Kubernetes v1.32 發布了，小明需要升級 production 叢集。

```bash
# 查看可升級的版本
clusterctl upgrade plan

# 使用 ClusterClass，只需修改 version
kubectl patch cluster payment-cluster \
  --type merge \
  -p '{"spec":{"topology":{"version":"v1.32.0"}}}'
```

CAPI 的升級順序：

```
1. TopologyReconciler 更新 KubeadmControlPlane.spec.version
2. KCP Controller 開始滾動升級控制平面
   ├─ 建立新的控制平面 Machine（v1.32）
   ├─ 等待新 Machine 健康
   └─ 刪除舊的控制平面 Machine（v1.31）
3. Worker MachineDeployment.spec.template.spec.version 更新
4. MachineDeploymentReconciler 建立新 MachineSet（v1.32）
5. 滾動替換 Worker 節點
```

```go
// 檔案: api/core/v1beta2/machinedeployment_types.go
const (
    // MachineDeploymentFinalizer 確保 MachineSet 有序清理
    MachineDeploymentFinalizer = "cluster.x-k8s.io/machinedeployment"

    // RevisionAnnotation 記錄升級序號
    RevisionAnnotation = "machinedeployment.clusters.x-k8s.io/revision"
)
```

---

## 第六章：機器故障自動修復

某天，production 叢集的一台 Worker 節點突然出現 `NotReady` 狀態。

小明之前已設定 `MachineHealthCheck`：

```yaml
# 檔案: config/samples/machinehealthcheck.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: MachineHealthCheck
metadata:
  name: payment-cluster-worker-mhc
spec:
  clusterName: payment-cluster
  selector:
    matchLabels:
      cluster.x-k8s.io/deployment-name: md-0
  unhealthyConditions:
  - type: Ready
    status: "False"
    timeout: 300s
  maxUnhealthy: "33%"
```

CAPI 自動處理：
1. `MachineHealthCheckReconciler` 偵測到節點 `Ready=False` 超過 300 秒
2. 標記該 Machine 為「需要修復」
3. 刪除該 Machine（觸發 drain → 刪除 Docker 容器）
4. MachineSet Controller 自動建立新的替換 Machine
5. 新節點加入叢集，服務恢復正常

---

## 小明的心得

> CAPI 讓我用 GitOps 的方式管理多個叢集：叢集定義存在 Git，PR 審查後自動套用。比起維護複雜的腳本，現在我只需要維護少量 YAML 就能管理整個公司的 Kubernetes 基礎設施。

**CAPI 的核心價值：**
- **宣告式管理**：叢集狀態由 CRD 定義，Controller 自動維持
- **Provider 插件化**：同一套 CAPI 管理 AWS、vSphere 等不同平台
- **ClusterClass 標準化**：平台團隊定義一次，業務線重複使用
- **自動修復**：MachineHealthCheck 無需人工介入

::: info 相關章節
- [學習路徑入口](./index)
- [系統架構](../architecture)
- [核心功能](../core-features)
- [ClusterClass 與 Topology](../clusterclass)
:::
