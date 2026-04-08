---
layout: doc
---

# Node Maintenance Operator — 系統架構

## 架構概覽

Node Maintenance Operator 採用**單一控制器**架構：一個 binary（`main.go`）、一個 reconciler（`NodeMaintenanceReconciler`）、一個 CRD（`NodeMaintenance`）。

```mermaid
graph LR
    User["👤 使用者"] -->|"kubectl apply"| CR["NodeMaintenance CR"]
    CR -->|"watch"| Controller["NodeMaintenanceReconciler"]
    Controller -->|"taint / cordon / drain"| Node["☸ Node"]
```

::: tip 設計哲學
單一 CRD、單一控制器，職責明確。使用者只需建立或刪除一個 `NodeMaintenance` CR，Operator 即自動完成節點的封鎖與驅逐（或恢復）。
:::

## Reconcile 流程（完整步驟）

以下為每次 reconcile 執行的完整步驟：

1. **Fetch NodeMaintenance CR** — 若不存在則直接結束（已刪除且 finalizer 已清除）
2. **建立 drain.Helper** — 依設定初始化 drainer（Force、DeleteEmptyDirData、IgnoreAllDaemonSets 等）
3. **Finalizer 處理**：
   - 若 CR 尚無 finalizer → 新增 `foregroundDeleteNodeMaintenance`，並觸發 `BeginMaintenance` 事件
   - 若 `DeletionTimestamp` 已設定 → 執行 `stopMaintenance`（uncordon + 移除 taint + 釋放 lease），移除 finalizer，觸發 `RemovedMaintenance` 事件
4. **初始化 Status** — 若 `phase == ""` → 設為 `Running`，統計 `TotalPods` 與 `EvictionPods`
5. **取得節點** — 依 `spec.nodeName` 查詢 Node；若找不到 → 觸發 `FailedMaintenance` 事件，設 phase = `Failed`
6. **Lease 檢查** — 若 `ErrorOnLeaseCount > 3` → uncordon 節點並設 `Failed`；否則呼叫 `RequestLease(node, 3600s)`
7. **Patch 節點標籤** — 加入 `medik8s.io/exclude-from-remediation=true`
8. **新增 Taint** — 加入 `medik8s.io/drain:NoSchedule` 與 `node.kubernetes.io/unschedulable:NoSchedule`
9. **Cordon 節點** — 設定 `node.Spec.Unschedulable = true`
10. **drain.RunNodeDrain** — 若失敗：requeue 5 秒；若成功：設 phase = `Succeeded`，`DrainProgress = 100`

```mermaid
flowchart TD
    A([開始 Reconcile]) --> B{Fetch NM CR}
    B -->|不存在| Z([結束])
    B -->|存在| C[建立 drain.Helper]
    C --> D{Finalizer 檢查}
    D -->|無 finalizer| E[新增 finalizer\n觸發 BeginMaintenance]
    D -->|DeletionTimestamp 已設| F[stopMaintenance\n移除 finalizer\n觸發 RemovedMaintenance]
    F --> Z
    E --> G{phase == ''}
    G -->|是| H[設 Running\n統計 TotalPods / EvictionPods]
    G -->|否| I[取得 Node]
    H --> I
    I -->|Node 不存在| J[觸發 FailedMaintenance\n設 Failed]
    J --> Z
    I -->|Node 存在| K{ErrorOnLeaseCount > 3?}
    K -->|是| L[Uncordon\n設 Failed]
    L --> Z
    K -->|否| M[RequestLease 3600s]
    M --> N[Patch 標籤\nexclude-from-remediation=true]
    N --> O[新增 Taint\nmedik8s.io/drain\nnode.kubernetes.io/unschedulable]
    O --> P[Cordon 節點\nUnschedulable=true]
    P --> Q[drain.RunNodeDrain]
    Q -->|error| R[Requeue 5s]
    Q -->|success| S[設 Succeeded\nDrainProgress=100]
    S --> Z
    R --> Z
```

## 狀態機

```mermaid
stateDiagram-v2
    [*] --> Running : CR 建立，新增 finalizer
    Running --> Running : drain 進行中，error 時 requeue 5s
    Running --> Succeeded : 所有 Pod 驅逐完成
    Running --> Failed : Node 不存在 OR ErrorOnLeaseCount > 3
    Succeeded --> [*] : CR 刪除，節點 uncordon
    Failed --> [*] : CR 刪除，節點 uncordon（若可行）
```

::: warning Failed 狀態說明
進入 `Failed` 狀態後，Operator 不再自動重試。需由使用者手動刪除 CR，Operator 將在刪除流程中嘗試 uncordon 節點。
:::

## 主要元件表格

| 元件 | 位置 | 職責 |
|------|------|------|
| `NodeMaintenanceReconciler` | `controllers/nodemaintenance_controller.go` | 主控制器，協調所有維護操作 |
| `LeaseManager` | `vendor/github.com/medik8s/common/pkg/lease` | 分散式 lease 協調 |
| `drain.Helper` | `k8s.io/kubectl/pkg/drain` | Pod 驅逐與節點排空 |
| `NodeMaintenanceValidator` | `api/v1beta1/nodemaintenance_webhook.go` | Admission webhook 驗證 |
| `EventRecorder` | `pkg/utils/events.go` | Kubernetes 事件記錄 |

## Drainer 設定

```go
// 檔案: controllers/nodemaintenance_controller.go
drainer := &drain.Helper{
    Client:              r.drainerClient,
    Force:               true,
    DeleteEmptyDirData:  true,
    IgnoreAllDaemonSets: true,
    GracePeriodSeconds:  -1,
    Timeout:             30 * time.Second,
    Out:                 writer{klog.Info},
    ErrOut:              writer{klog.Error},
    Ctx:                 ctx,
}
```

| 參數 | 值 | 原因 |
|------|----|------|
| `Force` | `true` | 驅逐無 controller 的 Pod（VirtualMachineInstance） |
| `DeleteEmptyDirData` | `true` | 刪除含 emptyDir 的 Pod（VM 暫存資料） |
| `IgnoreAllDaemonSets` | `true` | 跳過 DaemonSet Pod（virt-handler 等） |
| `GracePeriodSeconds` | `-1` | 使用 Pod 預設 grace period |
| `Timeout` | `30秒` | 等待所有 Pod 終止的最大時間 |

::: warning Force 模式注意事項
`Force: true` 會驅逐沒有 owner reference 或 owner 不是 ReplicaSet/DaemonSet 的 Pod，這是為了正確處理 KubeVirt 的 `VirtualMachineInstance` Pod。使用時請確認叢集上不存在其他需要保護的孤立 Pod。
:::

## 啟動設定（main.go）

```go
// 檔案: main.go
flag.StringVar(&metricsAddr,     "--metrics-bind-address",      ":8080",  "Metrics 端點位址")
flag.StringVar(&probeAddr,       "--health-probe-bind-address",  ":8081",  "Health probe 端點位址")
flag.BoolVar(&enableLeaderElect, "--leader-elect",               false,    "啟用 Leader Election")
flag.BoolVar(&enableHTTP2,       "--enable-http2",               false,    "啟用 HTTP/2（預設停用以緩解 CVE）")
```

| Flag | 預設值 | 說明 |
|------|--------|------|
| `--metrics-bind-address` | `:8080` | Prometheus metrics 端點 |
| `--health-probe-bind-address` | `:8081` | Health / Ready 探針端點 |
| `--leader-elect` | `false` | 啟用 Leader Election |
| `--enable-http2` | `false` | 啟用 HTTP/2（預設關閉以緩解 CVE） |

```go
// 檔案: main.go
const (
    WebhookCertDir  = "/apiserver.local.config/certificates/"
    WebhookCertName = "apiserver.crt"
    WebhookKeyName  = "apiserver.key"
)

LeaderElectionID: "135b1886.medik8s.io"
```

::: tip HTTP/2 預設停用
`--enable-http2` 預設為 `false`，目的是緩解已知的 HTTP/2 相關 CVE（如 CVE-2023-44487 Rapid Reset Attack）。Webhook 與 Metrics 伺服器強制使用 HTTP/1.1，除非明確啟用。
:::

::: info 相關章節
- [CRD 規格說明](./crd-specification)
- [節點排空流程](./node-drainage-process)
- [Lease 協調機制](./lease-based-coordination)
:::
