---
layout: doc
title: Cluster API Provider MAAS — 控制器與 CRD API
---

# Cluster API Provider MAAS — 控制器與 CRD API

## CRD 概覽

CAPMAAS 定義以下三個 CRD，均屬於 `infrastructure.cluster.x-k8s.io/v1beta1` API Group：

| CRD | Kind | 用途 |
|-----|------|------|
| `maasclusters` | `MaasCluster` | 描述叢集基礎設施（DNS Domain、CP Endpoint）|
| `maasmachines` | `MaasMachine` | 描述單一裸金屬機器的期望狀態 |
| `maasmachinetemplates` | `MaasMachineTemplate` | 機器規格模板，供批次建立機器使用 |

## MaasCluster API

### MaasClusterSpec

```go
// 檔案: api/v1beta1/maascluster_types.go

type MaasClusterSpec struct {
    // DNSDomain configures the MaaS domain to create the cluster on (e.g maas)
    // +kubebuilder:validation:MinLength=1
    DNSDomain string `json:"dnsDomain"`

    // ControlPlaneEndpoint represents the endpoint used to communicate with the control plane.
    // +optional
    ControlPlaneEndpoint APIEndpoint `json:"controlPlaneEndpoint"`

    // FailureDomains are not usually defined on the spec.
    // but useful for MaaS since we can limit the domains to these
    // +optional
    FailureDomains []string `json:"failureDomains,omitempty"`
}
```

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `dnsDomain` | `string` | **是** | MAAS DNS 域名，用於生成 API Server FQDN（例如 `maas`）|
| `controlPlaneEndpoint.host` | `string` | 否 | 若指定則直接使用，不自動生成 |
| `controlPlaneEndpoint.port` | `int` | 否 | API Server 端口，預設 6443 |
| `failureDomains` | `[]string` | 否 | MAAS Zone 名稱列表，限制 CP 機器的可用區 |

### MaasClusterStatus

```go
// 檔案: api/v1beta1/maascluster_types.go

type MaasClusterStatus struct {
    Ready          bool                      `json:"ready"`
    Network        Network                   `json:"network,omitempty"`
    FailureDomains clusterv1.FailureDomains  `json:"failureDomains,omitempty"`
    Conditions     clusterv1.Conditions      `json:"conditions,omitempty"`
}

type Network struct {
    DNSName string `json:"dnsName,omitempty"`
}
```

| 欄位 | 說明 |
|------|------|
| `ready` | 基礎設施就緒（DNS 已建立，CP Endpoint 已設定）|
| `network.dnsName` | 自動或手動指定的 API Server DNS 名稱 |
| `failureDomains` | 從 Spec 轉換後的 FailureDomain Map |
| `conditions` | 詳見 Condition 說明 |

### MaasCluster Conditions

| Condition | 說明 |
|-----------|------|
| `LoadBalancerReady`（`DNSReadyCondition`）| DNS Resource 建立成功並取得 DNS 名稱 |
| `APIServerAvailable`（`APIServerAvailableCondition`）| API Server 已可接受請求 |

## MaasMachine API

### MaasMachineSpec

```go
// 檔案: api/v1beta1/maasmachine_types.go

type MaasMachineSpec struct {
    FailureDomain  *string  `json:"failureDomain,omitempty"`
    SystemID       *string  `json:"systemID,omitempty"`
    ProviderID     *string  `json:"providerID,omitempty"`
    ResourcePool   *string  `json:"resourcePool,omitempty"`
    MinCPU         *int     `json:"minCPU"`
    MinMemoryInMB  *int     `json:"minMemory"`
    Tags           []string `json:"tags,omitempty"`
    Image          string   `json:"image"`
    DeployInMemory bool     `json:"deployInMemory,omitempty"`
}
```

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `minCPU` | `*int` | **是** | 申請機器所需最小 CPU 核心數 |
| `minMemory` | `*int` | **是** | 申請機器所需最小記憶體（MB）|
| `image` | `string` | **是** | MAAS Custom Image 名稱（例如 `custom/u-2204-0-k-1264-0`）|
| `resourcePool` | `*string` | 否 | 限定在指定 MAAS Resource Pool 中申請 |
| `tags` | `[]string` | 否 | 篩選帶有特定 MAAS Tag 的機器 |
| `failureDomain` | `*string` | 否 | 指定 MAAS Zone（可用區）|
| `deployInMemory` | `bool` | 否 | 是否部署至記憶體（In-Memory），預設 `false` |
| `providerID` | `*string` | 否 | 由 Controller 自動設定，格式 `maas:///<zone>/<systemID>` |
| `systemID` | `*string` | 否 | 由 Controller 自動設定，為 MAAS 機器的唯一識別碼 |

### MaasMachineStatus

```go
// 檔案: api/v1beta1/maasmachine_types.go

type MaasMachineStatus struct {
    Ready          bool                        `json:"ready"`
    MachineState   *MachineState               `json:"machineState,omitempty"`
    MachinePowered bool                        `json:"machinePowered,omitempty"`
    Hostname       *string                     `json:"hostname,omitempty"`
    DNSAttached    bool                        `json:"dnsAttached,omitempty"`
    Addresses      []clusterv1.MachineAddress  `json:"addresses,omitempty"`
    Conditions     clusterv1.Conditions        `json:"conditions,omitempty"`
    FailureReason  *errors.MachineStatusError  `json:"failureReason,omitempty"`
    FailureMessage *string                     `json:"failureMessage,omitempty"`
}
```

| 欄位 | 說明 |
|------|------|
| `ready` | 機器是否進入 `Deployed` 狀態且電源開啟 |
| `machineState` | 當前 MAAS 機器狀態（見狀態列表）|
| `machinePowered` | 機器電源是否開啟 |
| `hostname` | MAAS 機器的 hostname |
| `dnsAttached` | CP 機器是否已加入 DNS 記錄（僅 CP 適用）|
| `addresses` | 機器的 IP 及 DNS 地址列表 |
| `failureReason` / `failureMessage` | 不可恢復錯誤時的原因說明 |

### MaasMachine Conditions

| Condition | 說明 |
|-----------|------|
| `MachineDeployed`（`MachineDeployedCondition`）| 機器部署狀態 |
| `DNSAttached`（`DNSAttachedCondition`）| 僅 CP 機器，是否已加入 DNS 記錄 |

#### MachineDeployed 的 Reason 值

| Reason | 嚴重性 | 說明 |
|--------|--------|------|
| `WaitingForClusterInfrastructure` | Info | 等待 MaasCluster 就緒 |
| `WaitingForBootstrapData` | Info | 等待 Bootstrap Secret |
| `MachineDeployStartedReason` | Info | 已開始 Deploy |
| `MachineDeploying` | Warning | 正在部署中 |
| `MachineDeployFailed` | Error | 部署失敗 |
| `MachineTerminatedReason` | Error | 機器進入非預期終止狀態 |
| `MachinePoweredOff` | Warning | 機器電源關閉 |
| `MachineNotFound` | Unknown | 無法找到機器 |

## MaasMachineTemplate API

```go
// 檔案: api/v1beta1/maasmachinetemplate_types.go

type MaasMachineTemplateSpec struct {
    Template MaasMachineTemplateResource `json:"template"`
}

type MaasMachineTemplateResource struct {
    Spec MaasMachineSpec `json:"spec"`
}
```

`MaasMachineTemplate` 的 `spec.template.spec` 與 `MaasMachineSpec` 完全相同，作為建立多台機器的規格來源。

## 完整 YAML 範例

### MaasCluster

```yaml
# 檔案: templates/cluster-template.yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: MaasCluster
metadata:
  name: my-cluster
spec:
  dnsDomain: maas
  failureDomains:
    - zone-a
    - zone-b
```

### MaasMachineTemplate（含 In-Memory）

```yaml
# 檔案: README.md（in-memory 範例）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: MaasMachineTemplate
metadata:
  name: mt-worker-memory
  namespace: test
spec:
  template:
    spec:
      deployInMemory: true
      image: custom/your-image
      minCPU: 4
      minMemory: 16384
      resourcePool: default
      tags:
        - memory
```

## Machine 類型定義

```go
// 檔案: api/v1beta1/types.go

type Machine struct {
    ID               string
    Hostname         string
    State            MachineState
    Powered          bool
    AvailabilityZone string
    Addresses        []clusterv1.MachineAddress
    DeployedInMemory bool
}
```

此為 CAPMAAS 內部使用的機器表示，從 MAAS SDK 回傳的物件轉換而來（`fromSDKTypeToMachine`），並非 CRD。

## Finalizer 定義

| Finalizer | 保護對象 |
|-----------|---------|
| `maascluster.infrastructure.cluster.x-k8s.io` | `MaasCluster` — 確保 DNS 相關資源完全清理後再刪除 |
| `maasmachine.infrastructure.cluster.x-k8s.io` | `MaasMachine` — 確保 MAAS 機器 Release 後再刪除 |

::: warning Finalizer 與刪除順序
`MaasCluster` 的 Finalizer 會等待所有 `MaasMachine` 都被刪除後才放行。因此刪除叢集時，需確保 `MaasMachine` 能成功呼叫 MAAS Release API，否則叢集刪除流程將停滯。
:::

::: info 相關章節
- [系統架構](./architecture) — Scope 模式與 Controller 設計
- [核心功能](./core-features) — 機器佈建與 DNS 管理詳解
- [外部整合](./integration) — MAAS API 設定與 clusterctl 使用
:::
