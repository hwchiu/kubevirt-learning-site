---
layout: doc
title: Cluster API Provider Metal3 — 節點修復機制
---

# Cluster API Provider Metal3 — 節點修復機制

本章節說明 CAPM3 的 Metal3Remediation 控制器如何與 Cluster API MachineHealthCheck 整合，實現裸金屬節點的自動修復。

## 設計架構

CAPM3 的修復機制建立在 CAPI 的 MachineHealthCheck 框架上：

```
Cluster API MachineHealthCheck（MHC）
    │ 偵測到不健康 Node
    │ 建立 Metal3Remediation
    ▼
Metal3RemediationReconciler（CAPM3）
    │ 讀取修復策略
    │ 對 BareMetalHost 操作
    ▼
Baremetal Operator
    │ 執行 IPMI/Redfish 重啟
    ▼
Ironic → 物理伺服器重啟
```

## Metal3Remediation CRD

```go
// 檔案: api/v1beta2/metal3remediation_types.go
type RemediationType string

const (
    RemediationFinalizer       = "metal3remediation.infrastructure.cluster.x-k8s.io"
    RebootRemediationStrategy  RemediationType = "Reboot"
)

type Metal3RemediationSpec struct {
    Strategy *RemediationStrategy `json:"strategy,omitempty"`
}

type RemediationStrategy struct {
    // Type 目前只支援 "Reboot"
    Type         RemediationType `json:"type,omitempty"`
    // RetryLimit 最大重試次數，最小值 1，預設 1
    RetryLimit   int32           `json:"retryLimit,omitempty"`
    // TimeoutSeconds 每次重試之間的等待時間，最小 100 秒，預設 600 秒
    TimeoutSeconds int32         `json:"timeoutSeconds,omitempty"`
}
```

### 修復狀態（Phase）

```go
// 檔案: api/v1beta2/metal3remediation_types.go
const (
    PhaseRunning  = "Running"         // 正在執行修復
    PhaseWaiting  = "Waiting"         // 等待修復結果
    PhaseDeleting = "Deleting machine" // 修復失敗，刪除 Machine
    PhaseFailed   = "Failed"          // BMH offline，無法修復
)
```

| Phase | 說明 |
|-------|------|
| `Running` | 已送出 power off 指令，等待 BMH 斷電 |
| `Waiting` | BMH 已斷電，送出 power on 指令，等待節點恢復 |
| `Deleting machine` | 修復失敗達上限，觸發 Machine 刪除 |
| `Failed` | BMH `spec.online = false`，無法修復 |

## Reconcile 邏輯詳解

### 進入修復的前提條件

```go
// 檔案: controllers/metal3remediation_controller.go
func (r *Metal3RemediationReconciler) reconcileNormal(
    ctx context.Context,
    remediationMgr baremetal.RemediationManagerInterface,
    log logr.Logger,
) (ctrl.Result, error) {
    // 1. 取得不健康 BMH
    host, _, err := remediationMgr.GetUnhealthyHost(ctx)

    // 2. 若 BMH.spec.online = false，設為 Failed 並退出
    if !remediationMgr.OnlineStatus(host) {
        remediationMgr.SetRemediationPhase(infrav1.PhaseFailed)
        return ctrl.Result{}, nil
    }

    // 3. 判斷修復策略（目前僅支援 Reboot）
    remediationType := remediationMgr.GetRemediationType()

    // 4. 依 phase 執行對應邏輯
    switch remediationMgr.GetRemediationPhase() {
    case infrav1.PhaseRunning:
        return r.remediateRebootStrategy(...)
    case infrav1.PhaseWaiting:
        // 等待節點恢復...
    }
}
```

### Reboot 策略流程

**Phase: Running**

1. 備份 Node 上的 label（`backupNode()`）
2. 刪除 Kubernetes Node 物件（讓 cloud-controller-manager 或其他元件可以重新建立）
3. 對 BMH 設定 power off annotation（`SetPowerOffAnnotation()`）
4. 切換到 `PhaseWaiting`

**Phase: Waiting**

1. 若 power off annotation 尚未移除（BMH 尚未斷電），移除 annotation 觸發開機
2. 等待 BMH `status.poweredOn = true`
3. 等待 Kubernetes Node 物件重新出現並恢復（`restoreNode()`）
4. 確認 Node Ready 後，修復完成

```go
// 檔案: controllers/metal3remediation_controller.go
func (r *Metal3RemediationReconciler) remediateRebootStrategy(
    ctx context.Context,
    remediationMgr baremetal.RemediationManagerInterface,
    clusterClient client.Client,
    node *corev1.Node,
    log logr.Logger,
) (ctrl.Result, error) {
    // PhaseRunning: 備份、刪除節點、送出 power off
    // 切換到 PhaseWaiting
}
```

### Node 備份與還原

修復過程中會備份 Node 的 label，重啟後自動還原：

```go
// 檔案: controllers/metal3remediation_controller.go
func (r *Metal3RemediationReconciler) backupNode(
    remediationMgr baremetal.RemediationManagerInterface,
    node *corev1.Node,
) {
    // 將 node labels 序列化，存入 Metal3Remediation annotation
}

func (r *Metal3RemediationReconciler) restoreNode(
    ctx context.Context,
    remediationMgr baremetal.RemediationManagerInterface,
    clusterClient client.Client,
    node *corev1.Node,
) error {
    // 讀取備份的 label，還原到新的 Node 物件
}
```

### 重試邏輯

```go
// 檔案: baremetal/metal3remediation_manager.go
func (r *RemediationManager) TimeToRemediate(
    timeoutSeconds int32,
) (bool, time.Duration) {
    // 計算距上次修復是否已超過 timeoutSeconds
    // 回傳是否可再次嘗試修復，以及需等待的時間
}

func (r *RemediationManager) HasReachRetryLimit() bool {
    // 判斷是否已達 spec.strategy.retryLimit
}
```

| 函數 | 說明 |
|------|------|
| `SetPowerOffAnnotation()` | 設定 `reboot.metal3.io/capm3-remediation-v1` annotation，觸發 BMH 重啟 |
| `RemovePowerOffAnnotation()` | 移除 power off annotation，讓 BMH 上線 |
| `IsPowerOffRequested()` | 確認 power off annotation 是否存在 |
| `IsPoweredOn()` | 確認 BMH 目前是否已上電 |
| `SetUnhealthyAnnotation()` | 修復失敗達上限時，標記 BMH 為不健康 |
| `GetUnhealthyHost()` | 找出與此 Metal3Remediation 對應的 BMH |

## MachineHealthCheck 整合

在 CAPI 層面，透過 `MachineHealthCheck` 與 `Metal3RemediationTemplate` 組合使用：

```yaml
# 檔案: docs/remediation-controller.md（參考範例）
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: worker-healthcheck
  namespace: metal3
spec:
  clusterName: test1
  selector:
    matchLabels:
      nodepool: nodepool-0
  unhealthyConditions:
  - type: Ready
    status: Unknown
    timeout: 300s
  - type: Ready
    status: "False"
    timeout: 300s
  remediation:
    templateRef:
      kind: Metal3RemediationTemplate
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
      name: worker-remediation-request
```

```yaml
# 檔案: docs/remediation-controller.md（參考範例）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: Metal3RemediationTemplate
metadata:
  name: worker-remediation-request
  namespace: metal3
spec:
  template:
    spec:
      strategy:
        type: Reboot
        retryLimit: 1
        timeout: 300s
```

## Out-of-Service Taint 支援

CAPM3 支援 Kubernetes 1.28+ 的 out-of-service taint 機制，讓 Pod 能更快地從不健康節點驅逐：

```go
// 檔案: main.go
const (
    minK8sMajorVersionOutOfServiceTaint   = 1
    minK8sMinorVersionGAOutOfServiceTaint = 28
)
```

```go
// 檔案: controllers/metal3remediation_controller.go
type Metal3RemediationReconciler struct {
    // ...
    IsOutOfServiceTaintEnabled bool  // 依 Kubernetes 版本自動啟用
}
```

::: tip 修復完成條件
MachineHealthCheck 控制器在確認節點恢復健康後，會刪除 `Metal3Remediation` 物件，修復流程即告完成。CAPM3 修復控制器在此之前會持續 watch。
:::

::: warning 修復失敗處理
若 `retryLimit` 達到且節點仍未恢復，CAPM3 會：
1. 設定 BMH 的 `capm3.metal3.io/unhealthy` annotation
2. 在 CAPI Machine 設定 `MachineOwnerRemediatedCondition = False`
3. CAPI 開始刪除該 Machine 物件，Cluster Autoscaler 可建立新機器補充
:::

::: info 相關章節
- [核心功能](/cluster-api-provider-metal3/core-features)
- [控制器與 API](/cluster-api-provider-metal3/controllers-api)
- [裸金屬管理](/cluster-api-provider-metal3/baremetal)
:::
