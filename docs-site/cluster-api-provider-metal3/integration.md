---
layout: doc
title: Cluster API Provider Metal3 — 外部整合
---

# Cluster API Provider Metal3 — 外部整合

本章節說明 CAPM3 如何與 Cluster API 框架、Baremetal Operator（Ironic）、IPAM 等外部系統整合。

## 與 Cluster API 框架的整合

CAPM3 完整實作 Cluster API 的 Infrastructure Provider 契約，透過 CAPI 的標準機制與核心控制器溝通。

### Scheme 註冊

```go
// 檔案: main.go
func init() {
    _ = scheme.AddToScheme(myscheme)

    // metal3Ipam 和 capi IPAM schemes
    _ = ipamv1.AddToScheme(myscheme)
    _ = capipamv1beta1.AddToScheme(myscheme)
    _ = capipamv1.AddToScheme(myscheme)

    // CAPM3 infra provider schemes
    _ = infrav1beta1.AddToScheme(myscheme)
    _ = infrav1.AddToScheme(myscheme)

    // CAPI core schemes
    _ = clusterv1.AddToScheme(myscheme)

    // BMO Operator schemes
    _ = bmov1alpha1.AddToScheme(myscheme)

    // API extensions（for CRD Migrator）
    _ = apiextensionsv1.AddToScheme(myscheme)
}
```

### ClusterCache 整合

CAPM3 使用 CAPI 的 `clustercache.ClusterCache` 管理對 workload cluster 的連線，用於讀取目標叢集的節點狀態：

```go
// 檔案: controllers/metal3machine_controller.go
type Metal3MachineReconciler struct {
    Client           client.Client
    ManagerFactory   baremetal.ManagerFactoryInterface
    ClusterCache     clustercache.ClusterCache  // 管理 workload cluster 連線
    Log              logr.Logger
    CapiClientGetter baremetal.ClientGetter
    WatchFilterValue string
}
```

`ClusterCache` 的主要用途：
- 讀取 workload cluster 的 Node 資源，取得 providerID
- 確認節點是否已成功加入叢集
- 支援叢集升級時的節點重用邏輯

### CRD Migrator

```go
// 檔案: main.go
import "sigs.k8s.io/cluster-api/controllers/crdmigrator"
```

CAPM3 整合了 CAPI 的 `crdmigrator`，在 CAPM3 從 v1beta1 升級到 v1beta2 時，自動將舊版 CRD 資源遷移到新版 API 格式。

| CRD | 遷移說明 |
|-----|---------|
| `Metal3Cluster` | v1beta1 → v1beta2 |
| `Metal3Machine` | v1beta1 → v1beta2 |
| `Metal3DataTemplate` | v1beta1 → v1beta2 |
| `Metal3Data` | v1beta1 → v1beta2 |

### RBAC 權限設計

```go
// 檔案: controllers/metal3machine_controller.go
// +kubebuilder:rbac:groups=infrastructure.cluster.x-k8s.io,resources=metal3machines,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=cluster.x-k8s.io,resources=machines;machines/status,verbs=get;list;watch
// +kubebuilder:rbac:groups=metal3.io,resources=baremetalhosts,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=metal3.io,resources=baremetalhosts/status,verbs=get;update;patch
```

CAPM3 對 `metal3.io/baremetalhosts` 擁有完整的 CRUD 權限，因為它需要直接修改 BMH spec 來觸發 provisioning。

## 與 Baremetal Operator 的整合

CAPM3 不直接呼叫 Ironic，而是透過修改 `BareMetalHost` 物件，由 BMO 負責實際與 Ironic 通訊。

### BareMetalHost 欄位對應

CAPM3 設定 BMH 的以下欄位來控制 provisioning：

| BMH 欄位 | 來源 | 說明 |
|---------|------|------|
| `spec.image.url` | `Metal3Machine.spec.image.url` | 映像下載 URL |
| `spec.image.checksum` | `Metal3Machine.spec.image.checksum` | 映像校驗值 |
| `spec.image.diskFormat` | `Metal3Machine.spec.image.diskFormat` | 磁碟格式 |
| `spec.userData.name` | `Metal3Machine.spec.userData` | cloud-init user data Secret |
| `spec.metaData.name` | `Metal3Data` 渲染後的 Secret | cloud-init meta data Secret |
| `spec.networkData.name` | `Metal3Data` 渲染後的 Secret | 網路設定 Secret |
| `spec.consumerRef` | Metal3Machine 自身 | 標記 BMH 使用者 |
| `spec.online` | 固定設為 `true` | 觸發開機並開始 provisioning |
| `spec.automatedCleaningMode` | `Metal3Machine.spec.automatedCleaningMode` | 清理策略 |

### BMH 不使用快取

```go
// 檔案: main.go
Client: client.Options{
    Cache: &client.CacheOptions{
        DisableFor: []client.Object{
            &bmov1alpha1.BareMetalHost{},  // BMH 不快取
            &corev1.ConfigMap{},
            &corev1.Secret{},
        },
    },
},
```

::: warning 設計決策
BareMetalHost 狀態頻繁變化（provisioning 進度、硬體狀態等），若使用快取可能讀到舊狀態而導致 reconcile 邏輯錯誤。因此 CAPM3 對 BMH 一律直接向 API Server 讀取最新狀態。
:::

### Pause Annotation 機制

CAPM3 在特定操作期間（如節點修復）會在 BMH 上設定 pause annotation，告知 BMO 暫停對此 BMH 的 reconciliation：

```go
// 檔案: baremetal/metal3machine_manager.go
func (m *MachineManager) SetPauseAnnotation(ctx context.Context) error {
    // 設定 "baremetalhost.metal3.io/paused" annotation
}

func (m *MachineManager) RemovePauseAnnotation(ctx context.Context) error {
    // 移除 pause annotation，讓 BMO 恢復 reconciliation
}
```

## 與 IPAM 的整合

CAPM3 支援兩種 IPAM 來源：

| IPAM 類型 | API Group | 說明 |
|---------|---------|------|
| Metal3 IPAM | `ipam.metal3.io/v1alpha1` | Metal3 專用的 ip-address-manager |
| CAPI IPAM | `ipam.cluster.x-k8s.io/v1beta1` | Cluster API 標準 IPAM 介面 |

### IPAM 整合流程

```go
// 檔案: baremetal/metal3data_manager.go
const (
    IPPoolKind     = "IPPool"
    IPPoolAPIGroup = "ipam.metal3.io"
)

var (
    EnableBMHNameBasedPreallocation bool
)

// getAddressesFromPool 從所有 IP Pool 分配 IP 位址
func (m *DataManager) getAddressesFromPool(
    ctx context.Context,
    m3dt infrav1.Metal3DataTemplate,
    // ...
) (map[string]AddressFromPool, error) {
    // 遍歷 Metal3DataTemplate 中的所有 IPPool 引用
    // 依 isMetal3IPPoolRef() 判斷使用 Metal3 IPAM 或 CAPI IPAM
    // 建立 IPClaim，等待 IPAM 分配位址
    // 回傳 IP 位址、Gateway、DNS 設定
}
```

### IPAM 資料類型

```go
// 檔案: baremetal/metal3data_manager.go
type AddressFromPool struct {
    Address    ipamv1.IPAddressStr
    Prefix     int
    Gateway    ipamv1.IPAddressStr
    dnsServers []ipamv1.IPAddressStr
}
```

### IPClaim 生命週期

1. `Metal3DataReconciler` 解析 `Metal3DataTemplate` 的 `networkData.networks.ipv4[].fromPoolRef`
2. `DataManager.ensureM3IPClaim()` 建立 `IPClaim`，向 IPAM 請求 IP 位址
3. IPAM 控制器看到 `IPClaim`，從 `IPPool` 中分配一個位址，建立 `IPAddress`
4. `DataManager` 讀取 `IPClaim.status.address`，填入 networkdata Secret
5. 刪除 `Metal3Data` 時，`DataManager.ReleaseLeases()` 刪除 `IPClaim`，IPAM 回收 IP 位址

### BMH Name-Based Preallocation

當 `EnableBMHNameBasedPreallocation = true`（透過 `--enable-bmh-name-based-preallocation` 啟用）：

```go
// 檔案: baremetal/metal3data_manager.go
func (m *DataManager) m3IPClaimObjectMeta(
    name, poolRefName string, preallocationEnabled bool,
) *metav1.ObjectMeta {
    // preallocationEnabled=true 時，IPClaim 名稱基於 BMH 名稱
    // 確保同一台物理機器每次都獲得相同的 IP 位址
}
```

## 與 Kubernetes 核心元件的整合

### Secret 管理

CAPM3 建立並管理多種 Secret：

| Secret 類型 | 建立者 | 用途 |
|-----------|------|------|
| user data Secret | CAPI bootstrap provider | cloud-init 設定 |
| metaData Secret | `Metal3DataReconciler` | cloud-init metadata（主機名、索引等）|
| networkData Secret | `Metal3DataReconciler` | 網路介面設定 |

### Node Label 同步

`Metal3LabelSyncReconciler` 將 Metal3Machine 的 label 同步到 Kubernetes Node，讓 Metal3 的標籤策略在節點層級生效：

```go
// 檔案: controllers/metal3labelsync_controller.go
// 監聽 Metal3Machine label 變更，同步到對應的 Kubernetes Node
```

::: tip Leader Election
CAPM3 使用 Kubernetes Lease 資源實作 leader election，確保多個副本下只有一個 controller manager 主動 reconcile：
```go
LeaderElectionID: "controller-leader-election-capm3"
LeaderElectionResourceLock: resourcelock.LeasesResourceLock
```
:::

::: info 相關章節
- [系統架構](/cluster-api-provider-metal3/architecture)
- [核心功能](/cluster-api-provider-metal3/core-features)
- [裸金屬管理](/cluster-api-provider-metal3/baremetal)
- [控制器與 API](/cluster-api-provider-metal3/controllers-api)
:::
