---
layout: doc
title: Cluster API Provider Metal3 — 系統架構
---

# Cluster API Provider Metal3 — 系統架構

本章節說明 CAPM3 在 Metal3 技術棧中的定位，以及各元件之間如何協同運作，實現裸金屬 Kubernetes 叢集的自動化部署。

## Metal3 技術棧整體概覽

Metal3 技術棧由多個層次的元件組成，從最上層的 Cluster API 框架到最底層的 Ironic 伺服器管理服務：

```
┌─────────────────────────────────────────────────────────────┐
│                  使用者 / GitOps 工具                         │
│  kubectl apply -f cluster.yaml / clusterctl / ArgoCD        │
└───────────────────┬─────────────────────────────────────────┘
                    │ Kubernetes API
┌───────────────────▼─────────────────────────────────────────┐
│              Cluster API Core（Management Cluster）          │
│  Cluster  Machine  MachineDeployment  MachineHealthCheck    │
└───────────────────┬─────────────────────────────────────────┘
                    │ InfrastructureRef
┌───────────────────▼─────────────────────────────────────────┐
│        CAPM3 — Cluster API Provider Metal3（本專案）         │
│  Metal3Cluster  Metal3Machine  Metal3DataTemplate           │
│  Metal3Data  Metal3Remediation  Metal3LabelSync             │
└──────────┬──────────────────────────┬───────────────────────┘
           │ BareMetalHost API        │ IPClaim API
┌──────────▼──────────────┐  ┌────────▼────────────────────────┐
│   Baremetal Operator    │  │   ip-address-manager（IPAM）    │
│   BareMetalHost CRD     │  │   IPPool  IPAddress  IPClaim    │
└──────────┬──────────────┘  └─────────────────────────────────┘
           │ Ironic API
┌──────────▼──────────────────────────────────────────────────┐
│              Ironic（裸金屬管理服務）                         │
│   PXE Boot  Image Deploy  IPMI/Redfish  Hardware Introspect │
└──────────┬──────────────────────────────────────────────────┘
           │ 物理網路 / IPMI
┌──────────▼──────────────────────────────────────────────────┐
│              物理裸金屬伺服器（Bare Metal Servers）           │
└─────────────────────────────────────────────────────────────┘
```

## CAPM3 的角色：Infrastructure Provider

Cluster API 定義了一套標準介面，讓各個雲端或硬體平台實作自己的 Infrastructure Provider。CAPM3 實作的核心介面包括：

| CAPI 介面 | CAPM3 實作 | 說明 |
|-----------|-----------|------|
| `InfrastructureCluster` | `Metal3Cluster` | 叢集層級的基礎設施（API endpoint、failure domain）|
| `InfrastructureMachine` | `Metal3Machine` | 機器層級的基礎設施（映像、BMH 選取、user data）|

```go
// 檔案: controllers/metal3cluster_controller.go
// Metal3ClusterReconciler reconciles a Metal3Cluster object.
type Metal3ClusterReconciler struct {
    Client           client.Client
    ClusterCache     clustercache.ClusterCache
    ManagerFactory   baremetal.ManagerFactoryInterface
    Log              logr.Logger
    WatchFilterValue string
}
```

```go
// 檔案: controllers/metal3machine_controller.go
// Metal3MachineReconciler reconciles a Metal3Machine object.
type Metal3MachineReconciler struct {
    Client           client.Client
    ManagerFactory   baremetal.ManagerFactoryInterface
    ClusterCache     clustercache.ClusterCache
    Log              logr.Logger
    CapiClientGetter baremetal.ClientGetter
    WatchFilterValue string
}
```

## 元件分層架構

CAPM3 內部採用清晰的分層設計：

### Controller 層（controllers/）

Controller 層負責監聽 Kubernetes 事件、觸發 reconciliation，並將業務邏輯委派給 Manager 層：

```
controllers/
├── metal3cluster_controller.go       # Metal3Cluster reconciler
├── metal3machine_controller.go       # Metal3Machine reconciler
├── metal3data_controller.go          # Metal3Data reconciler
├── metal3datatemplate_controller.go  # Metal3DataTemplate reconciler
├── metal3machinetemplate_controller.go
├── metal3labelsync_controller.go     # 節點標籤同步
└── metal3remediation_controller.go   # 修復控制器
```

### Manager 層（baremetal/）

Manager 層封裝實際的業務邏輯，透過 `ManagerFactory` 建立：

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

### API 層（api/v1beta2/）

API 層定義 CRD 的 Go 結構，透過 kubebuilder 標記生成 CRD YAML：

```
api/
├── v1beta1/   # 舊版 API（用於版本轉換）
└── v1beta2/   # 目前主版本
    ├── metal3cluster_types.go
    ├── metal3machine_types.go
    ├── metal3datatemplate_types.go
    ├── metal3data_types.go
    ├── metal3remediation_types.go
    └── common_types.go
```

## CAPI 與 CAPM3 的協作流程

建立一個裸金屬叢集的完整流程如下：

**第一階段：叢集基礎設施就緒**

1. 使用者建立 `Cluster` 物件，`spec.infrastructureRef` 指向 `Metal3Cluster`
2. CAPI 建立 `Metal3Cluster` 物件
3. `Metal3ClusterReconciler` 處理 `Metal3Cluster`，設定 Control Plane Endpoint
4. `Metal3Cluster` 狀態變為 Ready，CAPI Cluster 進入下一階段

**第二階段：節點機器 provisioning**

1. CAPI 建立 `Machine` 物件，`spec.infrastructureRef` 指向 `Metal3Machine`
2. `Metal3MachineReconciler` 開始處理，從可用 `BareMetalHost` 池中選取主機
3. 設定 BMH 的 image、userData、networkData
4. Baremetal Operator 觸發 Ironic 開始 provisioning
5. Ironic 執行 PXE 開機 → 映像寫入 → 重新開機
6. Metal3Machine 狀態變為 Ready，CAPI Machine 加入叢集

**第三階段：資料管理**

- `Metal3DataTemplate` 為每台機器定義 cloud-init metadata/networkdata 模板
- `Metal3DataReconciler` 依模板渲染出 `Metal3Data`，生成 Kubernetes Secret
- Secret 的引用注入到 BMH 的 `spec.userData` / `spec.networkData`

## Manager 啟動設定

```go
// 檔案: main.go
mgr, err := ctrl.NewManager(restConfig, ctrl.Options{
    Scheme:           myscheme,
    LeaderElection:   enableLeaderElection,
    LeaderElectionID: "controller-leader-election-capm3",
    Client: client.Options{
        Cache: &client.CacheOptions{
            DisableFor: []client.Object{
                &bmov1alpha1.BareMetalHost{},
                &corev1.ConfigMap{},
                &corev1.Secret{},
            },
        },
    },
})
```

::: info 快取策略
BareMetalHost、ConfigMap、Secret 預設**不使用快取**，確保讀取的是最新狀態。叢集 Secret 採用 label-based 快取，僅快取帶有 `cluster.x-k8s.io/cluster-name` 標籤的 Secret。
:::

## 關鍵設計決策

| 設計 | 說明 |
|------|------|
| Leader Election | 使用 Kubernetes Lease 資源，確保同時只有一個 manager 實例在運作 |
| 多 Concurrency 設定 | 每個 controller 可獨立設定並行數（預設 10） |
| BMH 不快取 | BareMetalHost 狀態頻繁變化，直接向 API Server 讀取 |
| 分層 Manager | Controller 與業務邏輯分離，易於單元測試 |
| Webhook 驗證 | 對重要 CRD 提供 admission webhook 進行欄位驗證 |

::: info 相關章節
- [專案簡介](/cluster-api-provider-metal3/)
- [核心功能](/cluster-api-provider-metal3/core-features)
- [控制器與 API](/cluster-api-provider-metal3/controllers-api)
- [外部整合](/cluster-api-provider-metal3/integration)
:::
