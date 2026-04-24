---
layout: doc
title: Cluster API Provider Metal3 — 核心功能
---

# Cluster API Provider Metal3 — 核心功能

本章節深入介紹 CAPM3 的三大核心功能模組：Metal3Cluster（叢集基礎設施）、Metal3Machine（機器 provisioning）、Metal3Data（資料模板化）。

## Metal3Cluster：叢集基礎設施管理

`Metal3Cluster` 是 CAPI `Cluster` 物件的 Infrastructure 實作，負責描述裸金屬叢集的網路端點與可用區域。

### Metal3ClusterSpec 欄位

```go
// 檔案: api/v1beta2/metal3cluster_types.go
type Metal3ClusterSpec struct {
    // controlPlaneEndpoint 是與 control plane 通訊的端點
    ControlPlaneEndpoint APIEndpoint `json:"controlPlaneEndpoint,omitempty,omitzero"`

    // cloudProviderEnabled 決定是否使用外部 cloud provider 設定 providerID
    CloudProviderEnabled *bool `json:"cloudProviderEnabled,omitempty"`

    // failureDomains 是從 infrastructure provider 同步的 failure domain 列表
    FailureDomains []clusterv1.FailureDomain `json:"failureDomains,omitempty"`
}
```

```go
// 檔案: api/v1beta2/common_types.go
type APIEndpoint struct {
    Host string `json:"host,omitempty"`
    Port int32  `json:"port,omitempty"`
}
```

### Metal3Cluster 範例

```yaml
# 檔案: examples/metal3cluster-sample.yaml（參考範例）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: Metal3Cluster
metadata:
  name: my-cluster
  namespace: metal3
spec:
  controlPlaneEndpoint:
    host: 192.168.0.200
    port: 6443
  cloudProviderEnabled: false
```

### Finalizer 與生命週期

```go
// 檔案: api/v1beta2/metal3cluster_types.go
const (
    // ClusterFinalizer 防止 Metal3Cluster 在資源清理前被刪除
    ClusterFinalizer = "metal3cluster.infrastructure.cluster.x-k8s.io"
)
```

| 階段 | 觸發條件 | 動作 |
|------|---------|------|
| 建立 | Metal3Cluster 新增 | 設定 Finalizer，等待 ControlPlaneEndpoint 設定 |
| Ready | ControlPlaneEndpoint 設定完成 | 設定 `initialization.provisioned = true` |
| 刪除 | Metal3Cluster 收到刪除請求 | 確認無 Machine descendant，移除 Finalizer |

## Metal3Machine：裸金屬機器 Provisioning

`Metal3Machine` 對應一台裸金屬伺服器，CAPM3 透過它來選取、設定並追蹤 `BareMetalHost` 的 provisioning 狀態。

### Metal3MachineSpec 欄位

```go
// 檔案: api/v1beta2/metal3machine_types.go
type Metal3MachineSpec struct {
    // providerID 格式為 metal3://<namespace>/<bmh-name>/<m3m-name>
    ProviderID string `json:"providerID,omitempty"`

    // image 是要部署的映像（與 customDeploy 擇一）
    Image Image `json:"image,omitempty,omitzero"`

    // customDeploy 用於自訂部署流程（與 image 擇一）
    CustomDeploy CustomDeploy `json:"customDeploy,omitempty,omitzero"`

    // userData 指向存放 cloud-init user data 的 Secret
    UserData *corev1.SecretReference `json:"userData,omitempty"`

    // hostSelector 用來篩選可用的 BareMetalHost
    HostSelector *HostSelector `json:"hostSelector,omitempty"`

    // dataTemplate 引用 Metal3DataTemplate，提供 metadata 與 networkdata
    DataTemplate *Metal3ObjectRef `json:"dataTemplate,omitempty"`

    // metaData 指向 cloud-init metadata Secret（由 Metal3Data 產生）
    MetaData *corev1.SecretReference `json:"metaData,omitempty"`

    // networkData 指向 cloud-init networkdata Secret（由 Metal3Data 產生）
    NetworkData *corev1.SecretReference `json:"networkData,omitempty"`
}
```

### Image 欄位

```go
// 檔案: api/v1beta2/common_types.go
type Image struct {
    // URL 是映像的下載位置
    URL          string  `json:"url,omitempty"`
    // Checksum 是映像的校驗值或校驗值的 URL
    Checksum     *string `json:"checksum,omitempty"`
    // ChecksumType 可為 md5、sha256、sha512
    ChecksumType string  `json:"checksumType,omitempty"`
    // DiskFormat 可為 raw、qcow2、vdi、vmdk、live-iso
    DiskFormat   string  `json:"diskFormat,omitempty"`
}
```

### HostSelector：BareMetalHost 篩選

```go
// 檔案: api/v1beta2/common_types.go
type HostSelector struct {
    // matchLabels 指定 BareMetalHost 必須具備的 label
    MatchLabels map[string]string `json:"matchLabels,omitempty"`

    // matchExpressions 支援更複雜的 label 選取條件
    MatchExpressions []HostSelectorRequirement `json:"matchExpressions,omitempty"`
}
```

**HostSelector 範例：**

```yaml
# 檔案: examples/metal3machine-with-selector.yaml（參考範例）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: Metal3Machine
metadata:
  name: worker-01
  namespace: metal3
spec:
  image:
    url: "http://192.168.0.1/images/ubuntu-22.04.qcow2"
    checksum: "abc123..."
    checksumType: "sha256"
    diskFormat: "qcow2"
  hostSelector:
    matchLabels:
      environment: production
      rack: "rack-1"
```

### Metal3Machine Conditions

| Condition | 說明 |
|-----------|------|
| `Ready` | Metal3Machine 整體就緒狀態 |
| `AssociateBareMetalHost` | BMH 是否已與 Metal3Machine 關聯 |
| `AssociateMetal3MachineMetaData` | MetaData/NetworkData 是否已關聯 |
| `Metal3DataReady` | Metal3Data 是否已渲染完成 |

::: tip ProviderID 格式
CAPM3 v1.12 起，ProviderID 格式改為 `metal3://<namespace>/<bmh-name>/<m3m-name>`。舊版格式 `metal3://<bmh-uuid>` 將在 v1.14 移除。
:::

## Metal3DataTemplate：資料模板化

`Metal3DataTemplate` 定義 cloud-init metadata 和 network configuration 的模板，可為每台機器生成唯一的設定。

### DataTemplate 欄位

```go
// 檔案: api/v1beta2/metal3datatemplate_types.go
const (
    DataTemplateFinalizer = "metal3datatemplate.infrastructure.cluster.x-k8s.io"
)

// MetaDataIndex 定義如何將 index 渲染為 metadata 值
type MetaDataIndex struct {
    Key    string `json:"key,omitempty"`
    Offset *int32 `json:"offset,omitempty"`
    Step   int32  `json:"step,omitempty"`
    Prefix string `json:"prefix,omitempty"`
    Suffix string `json:"suffix,omitempty"`
}

// IndexEntry 記錄每台 Metal3Machine 的 index 分配
type IndexEntry struct {
    Name  string `json:"name,omitempty"`
    Index *int32 `json:"index,omitempty"`
}
```

### Metal3Data：渲染後的資料

```go
// 檔案: api/v1beta2/metal3data_types.go
type Metal3DataSpec struct {
    // index 是此 Metal3Data 在 DataTemplate 中的 index 值
    Index *int32 `json:"index,omitempty"`

    // metaData 指向渲染後的 MetaData Secret
    MetaData *corev1.SecretReference `json:"metaData,omitempty"`

    // networkData 指向渲染後的 NetworkData Secret
    NetworkData *corev1.SecretReference `json:"networkData,omitempty"`

    // claim 指向建立此 Metal3Data 的 Metal3DataClaim
    Claim *Metal3ObjectRef `json:"claim,omitempty"`

    // template 指向來源 Metal3DataTemplate
    Template *Metal3ObjectRef `json:"template,omitempty"`
}
```

### 資料流程：從模板到 Secret

1. `Metal3Machine` 的 `spec.dataTemplate` 指向 `Metal3DataTemplate`
2. `Metal3MachineReconciler` 建立 `Metal3DataClaim`，聲明需要資料
3. `Metal3DataTemplateReconciler` 分配 index，建立 `Metal3Data`
4. `Metal3DataReconciler` 渲染模板內容，建立兩個 Secret（metaData、networkData）
5. Secret 引用回填到 `Metal3Machine.spec.metaData` 與 `.spec.networkData`
6. BMH 設定 `spec.userData`、`spec.metaData`、`spec.networkData`

### DataTemplate 範例

```yaml
# 檔案: examples/metal3datatemplate-sample.yaml（參考範例）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: Metal3DataTemplate
metadata:
  name: worker-data-template
  namespace: metal3
spec:
  metaData:
    strings:
    - key: node-name
      value: "worker"
    indexes:
    - key: node-index
      offset: 0
      step: 1
      prefix: "worker-"
  networkData:
    networks:
      ipv4:
      - id: "baremetal"
        fromPoolRef:
          name: "worker-ip-pool"
          namespace: "metal3"
```

::: info 相關章節
- [系統架構](/cluster-api-provider-metal3/architecture)
- [控制器與 API](/cluster-api-provider-metal3/controllers-api)
- [裸金屬管理](/cluster-api-provider-metal3/baremetal)
- [外部整合](/cluster-api-provider-metal3/integration)
:::
