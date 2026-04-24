---
layout: doc
title: Cluster API — Provider 模型
---

# Cluster API — Provider 模型

## Provider 概念

CAPI 的核心設計哲學是「核心框架 + Provider 插件」：Core 控制器只了解**合約（Contract）**，不直接依賴任何特定基礎設施實作。這使得相同的 CAPI Core 能在 AWS、Azure、vSphere、裸機等環境上運作。

```
CAPI Core                    Provider
┌─────────────────┐          ┌────────────────────────────┐
│ Cluster CRD     │ ─ref──►  │ AWSCluster / VSphereCluster│
│ Machine CRD     │ ─ref──►  │ AWSMachine / VSphereMachine│
│ KubeadmConfig   │ ─ref──►  │ KubeadmConfig（內建）       │
│ KCP             │ ─ref──►  │ KubeadmControlPlane（內建） │
└─────────────────┘          └────────────────────────────┘
```

## Infrastructure Provider

Infrastructure Provider 負責在目標平台上佈建計算資源（VM、裸機等）。

### 合約介面

每個 Infrastructure Provider 必須實作以下合約：

| 合約欄位 | 位置 | 說明 |
|---------|------|------|
| `spec.providerID` | InfraMachine | 節點的 Provider ID（如 `aws:///us-east-1a/i-xxx`）|
| `status.ready` | InfraMachine | 資源是否佈建完成 |
| `status.addresses` | InfraMachine | 節點 IP 位址列表 |
| `status.ready` | InfraCluster | 叢集基礎設施是否就緒 |

### 範例 Provider 列表

| Provider | 平台 | 程式庫 |
|---------|------|--------|
| CAPD（Docker） | Docker（本地開發） | `sigs.k8s.io/cluster-api` 內建 |
| CAPA | Amazon Web Services | `sigs.k8s.io/cluster-api-provider-aws` |
| CAPZ | Azure | `sigs.k8s.io/cluster-api-provider-azure` |
| CAPV | VMware vSphere | `sigs.k8s.io/cluster-api-provider-vsphere` |
| CAPM3 | Bare Metal（Metal3） | `sigs.k8s.io/cluster-api-provider-metal3` |
| CAPMAAS | MAAS | `github.com/spectrocloud/cluster-api-provider-maas` |

### 引用方式

```yaml
# 檔案: config/samples/cluster-with-infra.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: my-cluster
spec:
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: DockerCluster    # Infrastructure Provider 提供的 CRD
    name: my-cluster
    namespace: default
```

## Bootstrap Provider

Bootstrap Provider 負責為每台 Machine 產生節點初始化資料（通常是 cloud-init 或 ignition 格式）。

### 合約介面

| 合約欄位 | 位置 | 說明 |
|---------|------|------|
| `status.ready` | BootstrapConfig | Bootstrap 資料是否已準備好 |
| `status.dataSecretName` | BootstrapConfig | 存放初始化腳本的 Secret 名稱 |

### KubeadmConfig（內建 Bootstrap Provider）

CAPI 內建的 Bootstrap Provider，使用 kubeadm 初始化節點：

```go
// 檔案: api/bootstrap/kubeadm/v1beta2/kubeadmconfig_types.go
type KubeadmConfigSpec struct {
    // InitConfiguration 用於第一個控制平面節點
    InitConfiguration *bootstrapv1.InitConfiguration `json:"initConfiguration,omitempty"`
    // JoinConfiguration 用於後續節點加入叢集
    JoinConfiguration *bootstrapv1.JoinConfiguration `json:"joinConfiguration,omitempty"`
    // ClusterConfiguration 定義叢集層級的 kubeadm 設定
    ClusterConfiguration *bootstrapv1.ClusterConfiguration `json:"clusterConfiguration,omitempty"`
    // Files 在初始化前寫入的檔案清單
    Files []File `json:"files,omitempty"`
    // PreKubeadmCommands 在 kubeadm 執行前運行的命令
    PreKubeadmCommands []string `json:"preKubeadmCommands,omitempty"`
    // PostKubeadmCommands 在 kubeadm 執行後運行的命令
    PostKubeadmCommands []string `json:"postKubeadmCommands,omitempty"`
}
```

### Machine 引用 Bootstrap Config

```yaml
# 檔案: config/samples/machine-with-bootstrap.yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Machine
metadata:
  name: worker-1
spec:
  clusterName: my-cluster
  version: "v1.31.0"
  bootstrap:
    configRef:
      apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
      kind: KubeadmConfig
      name: worker-1-bootstrap
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: DockerMachine
    name: worker-1
```

## ControlPlane Provider

ControlPlane Provider 負責管理控制平面節點群組，包含高可用設定與 etcd 管理。

### 合約介面

| 合約欄位 | 位置 | 說明 |
|---------|------|------|
| `spec.replicas` | ControlPlane | 控制平面副本數 |
| `spec.version` | ControlPlane | Kubernetes 版本 |
| `status.ready` | ControlPlane | 控制平面是否就緒 |
| `status.initialized` | ControlPlane | 第一個控制平面是否初始化完成 |
| `status.version` | ControlPlane | 實際運行版本 |

### KubeadmControlPlane（內建 ControlPlane Provider）

```go
// 檔案: api/controlplane/kubeadm/v1beta2/kubeadm_control_plane_types.go
const (
    KubeadmControlPlaneFinalizer = "kubeadm.controlplane.cluster.x-k8s.io"

    // SkipCoreDNSAnnotation 跳過 CoreDNS reconciliation
    SkipCoreDNSAnnotation = "controlplane.cluster.x-k8s.io/skip-coredns"

    // RemediationInProgressAnnotation 追蹤 KCP 修復進度
    RemediationInProgressAnnotation = "controlplane.cluster.x-k8s.io/remediation-in-progress"
)
```

## IPAM Provider（IP 位址管理）

CAPI 內建 IPAM 支援，透過 `IPAddressClaim` 和 `IPAddress` 資源管理 IP 位址分配：

```go
// 檔案: api/ipam/v1beta2
// IPAddressClaim 由 Infrastructure Provider 建立，請求分配一個 IP
// IPAddress 由 IPAM Provider 建立，回應 IP 分配結果

// 相關 API 群組：ipam.cluster.x-k8s.io
```

## Runtime Extension（執行期擴展）

CAPI v1.2 引入 Runtime Extension，允許在叢集生命週期的特定時機點注入自定義邏輯（Webhook 形式）：

```go
// 檔案: api/runtime/hooks/v1alpha1
// 支援的 Hook 點：
// - BeforeClusterCreate  - 叢集建立前
// - AfterControlPlaneInitialized - 控制平面初始化後
// - BeforeClusterUpgrade - 叢集升級前
// - AfterControlPlaneUpgrade - 控制平面升級後
// - BeforeClusterDelete - 叢集刪除前
```

::: tip 如何選擇 Provider
對於生產環境，建議根據基礎設施平台選擇官方維護的 Provider（CAPA/CAPZ/CAPV）。對於開發測試，CAPD（Docker Provider）是最快的選擇，無需任何雲端帳號。
:::

::: warning Provider 版本相容性
每個 Provider 有對應支援的 CAPI 版本範圍。升級時請先確認 Provider 是否支援目標 CAPI 版本，可透過 `clusterctl upgrade plan` 查看。
:::

::: info 相關章節
- [系統架構](./architecture)
- [控制器與 API](./controllers-api)
- [外部整合](./integration)
:::
