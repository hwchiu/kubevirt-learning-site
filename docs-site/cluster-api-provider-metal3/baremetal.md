---
layout: doc
title: Cluster API Provider Metal3 — 裸金屬管理機制
---

# Cluster API Provider Metal3 — 裸金屬管理機制

本章節說明 CAPM3 如何透過 BareMetalHost（BMH）選取機制與 provisioning 流程，管理實體裸金屬伺服器。

## BareMetalHost 概念

`BareMetalHost` 是 Baremetal Operator（BMO）定義的 CRD，代表一台實體伺服器。CAPM3 不直接呼叫 Ironic API，而是透過修改 BMH 的 Spec 來間接控制機器的 provisioning。

```
CAPM3 Metal3Machine
    │ 讀寫 BareMetalHost spec
    ▼
Baremetal Operator（BMO）
    │ 呼叫 Ironic API
    ▼
Ironic（PXE Boot、映像寫入、IPMI/Redfish 控制）
    │ 物理操作
    ▼
實體伺服器
```

## BareMetalHost 選取機制

`chooseHost` 函數從可用的 BareMetalHost 池中選取合適的主機：

```go
// 檔案: baremetal/metal3machine_manager.go
func (m *MachineManager) chooseHost(
    ctx context.Context,
) (*bmov1alpha1.BareMetalHost, *patch.Helper, string, error) {
    // 1. 取得 HostSelector 產生的 label selector
    labelSelector, err := hostLabelSelectorForMachine(m.Metal3Machine, m.Log)

    // 2. 列出所有符合 label 的 BareMetalHost
    // 3. 優先選取已有 nodeReuse label 且相符的 BMH（node reuse 功能）
    // 4. 從未被使用的 BMH 中隨機選取一台
}
```

### 選取優先順序

| 優先級 | 條件 | 說明 |
|--------|------|------|
| 1（最高）| 已有對應的 consumerRef | BMH 已與此 Metal3Machine 綁定 |
| 2 | nodeReuseLabel 相符 | Node Reuse 功能：重用舊節點的 BMH |
| 3 | 無 consumerRef 且符合 HostSelector | 一般未使用的可用 BMH |

### HostSelector 轉換為 Label Selector

```go
// 檔案: baremetal/metal3machine_manager.go
func hostLabelSelectorForMachine(
    machine *infrav1.Metal3Machine, log logr.Logger,
) (labels.Selector, error) {
    // 將 Metal3Machine.spec.hostSelector 轉換為 labels.Selector
    // 支援 matchLabels 與 matchExpressions
}
```

## BMH Spec 設定

選取 BMH 後，`setHostSpec` 函數設定機器的啟動設定：

```go
// 檔案: baremetal/metal3machine_manager.go
func (m *MachineManager) setHostSpec(
    _ context.Context, host *bmov1alpha1.BareMetalHost,
) error {
    // 設定映像 URL、checksum、diskFormat
    // 設定 userData、metaData、networkData Secret 引用
    // 設定 automatedCleaningMode（依 Metal3Machine spec）
    // 設定 host.Spec.Online = true 觸發開機
}
```

### 自動化清理模式

| AutomatedCleaningMode | 說明 |
|----------------------|------|
| `metadata`（預設）| deprovisioning 時清理硬碟 metadata |
| `disabled` | 跳過清理，加快 deprovisioning 速度 |

```go
// 檔案: api/v1beta2/metal3machine_types.go
const (
    CleaningModeDisabled = "disabled"
    CleaningModeMetadata = "metadata"
)
```

## ConsumerRef：BMH 使用者追蹤

CAPM3 透過設定 `host.Spec.ConsumerRef` 標記 BMH 已被某個 Metal3Machine 使用：

```go
// 檔案: baremetal/metal3machine_manager.go
func (m *MachineManager) setHostConsumerRef(
    _ context.Context, host *bmov1alpha1.BareMetalHost,
) error {
    // 設定 host.Spec.ConsumerRef 指向此 Metal3Machine
    // 格式: {APIVersion, Kind, Name, Namespace}
}

func consumerRefMatches(
    consumer *corev1.ObjectReference, m3machine *infrav1.Metal3Machine,
) bool {
    // 驗證 consumerRef 是否指向此 Metal3Machine
}
```

## Node Reuse 機制

Node Reuse 是 CAPM3 的進階功能，讓升級時可以重用同一台物理機器，避免不必要的 deprovisioning/provisioning 循環：

```go
// 檔案: baremetal/metal3machine_manager.go
const (
    nodeReuseLabelName = "infrastructure.cluster.x-k8s.io/node-reuse"
)

func (m *MachineManager) nodeReuseLabelMatches(
    ctx context.Context, host *bmov1alpha1.BareMetalHost,
) bool {
    // 確認 BMH 上的 nodeReuseLabel 值與目前的 ControlPlane 或 MachineDeployment 名稱相符
}
```

**Node Reuse 流程：**
1. 節點準備刪除時，CAPM3 在 BMH 上設定 `nodeReuseLabelName` 標籤
2. 新的 Metal3Machine 建立時，`chooseHost` 優先選取有對應 nodeReuse label 的 BMH
3. 直接跳過 deprovisioning，重新 provisioning 到新的映像

## BMH Name-Based Preallocation

```go
// 檔案: baremetal/metal3data_manager.go
var (
    EnableBMHNameBasedPreallocation bool
)
```

當 `EnableBMHNameBasedPreallocation = true` 時，IPAM 的 IPClaim 名稱將基於 BMH 名稱而非隨機生成，讓同一台物理機器每次都獲得相同的 IP 位址。

此功能透過 `--enable-bmh-name-based-preallocation` 啟動參數控制：

```go
// 檔案: main.go
baremetal.EnableBMHNameBasedPreallocation = enableBMHNameBasedPreallocation
```

## Provisioning 狀態流程

BMH 的 provisioning 狀態由 Baremetal Operator 管理，CAPM3 透過讀取 BMH 狀態來判斷 Metal3Machine 的就緒狀態：

| BMH 狀態 | Metal3Machine 行為 |
|---------|------------------|
| `available` | 等待 CAPM3 設定 image 與 consumerRef |
| `provisioning` | 等待 Ironic 完成映像寫入 |
| `provisioned` | 設定 Metal3Machine Ready = true |
| `deprovisioning` | 等待清理完成 |
| `available`（deprovisioning 後）| 移除 Metal3Machine Finalizer |

```go
// 檔案: baremetal/metal3machine_manager.go
func (m *MachineManager) IsProvisioned() bool {
    // 判斷 Metal3Machine 是否已完成 provisioning
    // 依據: spec.providerID 是否已設定
}

func (m *MachineManager) IsBaremetalHostProvisioned(ctx context.Context) bool {
    // 直接查詢 BMH 的狀態欄位，確認 BMH 是否已 provisioned
}
```

## Pause Annotation

CAPM3 使用 pause annotation 暫停 BMH 的 reconciliation，在某些操作期間（如修復）防止 BMO 干預：

```go
// 檔案: baremetal/metal3machine_manager.go
func (m *MachineManager) RemovePauseAnnotation(ctx context.Context) error {
    // 移除 BMH 上的 "baremetalhost.metal3.io/paused" annotation
    // Metal3Machine 正常 reconcile 時呼叫
}

func (m *MachineManager) SetPauseAnnotation(ctx context.Context) error {
    // 設定 BMH 的 pause annotation，暫停 BMO reconciliation
}
```

::: tip BMC 密鑰管理
CAPM3 也處理 BMC（Baseboard Management Controller）Secret 的 label 管理，確保 BMC 密鑰被正確標記並可被 BMO 存取。相關函數：`getBMCSecret()`、`setBMCSecretLabel()`。
:::

::: info 相關章節
- [核心功能](/cluster-api-provider-metal3/core-features)
- [控制器與 API](/cluster-api-provider-metal3/controllers-api)
- [外部整合](/cluster-api-provider-metal3/integration)
- [節點修復](/cluster-api-provider-metal3/remediation)
:::
