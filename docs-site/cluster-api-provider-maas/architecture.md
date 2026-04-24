---
layout: doc
title: Cluster API Provider MAAS — 系統架構
---

# Cluster API Provider MAAS — 系統架構

## 整體架構概覽

CAPMAAS 作為 Cluster API（CAPI）的 Infrastructure Provider，架構上分為三層：

```
┌─────────────────────────────────────────────────┐
│              管理叢集（Management Cluster）        │
│                                                   │
│  ┌─────────────────┐   ┌──────────────────────┐  │
│  │  CAPI Core       │   │  CAPMAAS Controller  │  │
│  │  (Cluster/       │   │  (MaasCluster/       │  │
│  │   Machine)       │   │   MaasMachine        │  │
│  │                  │◄──│   Reconcilers)       │  │
│  └─────────────────┘   └──────────┬───────────┘  │
│                                    │               │
└────────────────────────────────────┼───────────────┘
                                     │ MAAS REST API
                              ┌──────▼──────┐
                              │  MAAS Server │
                              │  (裸金屬管理) │
                              └──────┬──────┘
                                     │
              ┌──────────────────────┼──────────────────┐
              │                      │                   │
        ┌─────▼─────┐         ┌─────▼─────┐      ┌─────▼─────┐
        │  Node-01   │         │  Node-02   │      │  Node-03  │
        │ (CP)       │         │ (CP)       │      │ (Worker)  │
        └───────────┘         └───────────┘      └───────────┘
```

## CRD 物件關係

CAPMAAS 定義了三種自訂資源，與 CAPI 核心物件一一對應：

| CAPI 核心物件 | CAPMAAS 對應物件 | 功能 |
|-------------|----------------|------|
| `Cluster` | `MaasCluster` | 叢集基礎設施（DNS Domain、ControlPlane Endpoint）|
| `Machine` | `MaasMachine` | 單一機器（系統 ID、資源需求、映像檔）|
| `MachineTemplate` | `MaasMachineTemplate` | 機器規格模板（供 KubeadmControlPlane 和 MachineDeployment 引用）|

### 物件引用鏈

```
Cluster ──infrastructureRef──► MaasCluster
Machine ──infrastructureRef──► MaasMachine
KubeadmControlPlane ──machineTemplate.infrastructureRef──► MaasMachineTemplate
MachineDeployment ──template.infrastructureRef──► MaasMachineTemplate
```

## Controller 架構

### MaasClusterReconciler

```go
// 檔案: controllers/maascluster_controller.go

// MaasClusterReconciler reconciles a MaasCluster object
type MaasClusterReconciler struct {
    client.Client
    Log                 logr.Logger
    Scheme              *runtime.Scheme
    Recorder            record.EventRecorder
    GenericEventChannel chan event.GenericEvent
    Tracker             *remote.ClusterCacheTracker
}
```

`MaasClusterReconciler` 負責：
1. 管理 DNS Resource（作為 API Server 的軟性負載平衡）
2. 追蹤所有 Control Plane 機器的 IP 並更新 DNS 記錄
3. 設定 `ControlPlaneEndpoint`（Host:Port）
4. 非同步輪詢 API Server 是否上線（透過 `ClusterCacheTracker`）

### MaasMachineReconciler

```go
// 檔案: controllers/maasmachine_controller.go

// MaasMachineReconciler reconciles a MaasMachine object
type MaasMachineReconciler struct {
    client.Client
    Log      logr.Logger
    Scheme   *runtime.Scheme
    Recorder record.EventRecorder
    Tracker  *remote.ClusterCacheTracker
}
```

`MaasMachineReconciler` 負責：
1. 透過 MAAS API 申請（Allocate）符合條件的裸金屬機器
2. 部署（Deploy）映像檔，同時注入 bootstrap user-data
3. 追蹤機器狀態（Allocated → Deploying → Deployed）
4. Control Plane 機器：等待叢集 DNS 附加完成
5. 在 Workload 叢集 Node 上設定 ProviderID

## Scope 模式

CAPMAAS 採用 CAPI 生態的 **Scope Pattern**，將每次 Reconcile 的上下文封裝為 Scope 物件：

```go
// 檔案: pkg/maas/scope/cluster.go

// ClusterScope defines the basic context for an actuator to operate upon.
type ClusterScope struct {
    logr.Logger
    client      client.Client
    patchHelper *patch.Helper

    Cluster             *clusterv1.Cluster
    MaasCluster         *infrav1beta1.MaasCluster
    controllerName      string
    tracker             *remote.ClusterCacheTracker
    clusterEventChannel chan event.GenericEvent
}
```

```go
// 檔案: pkg/maas/scope/machine.go

// MachineScope defines the basic context for an actuator to operate upon.
type MachineScope struct {
    logr.Logger
    client      client.Client
    patchHelper *patch.Helper

    Cluster      *clusterv1.Cluster
    ClusterScope *ClusterScope
    Machine      *clusterv1.Machine
    MaasMachine  *infrav1beta1.MaasMachine

    controllerName string
    tracker        *remote.ClusterCacheTracker
}
```

::: tip Scope 的設計意義
Scope 物件在每次 Reconcile 開始時建立，並在函數結束時透過 `defer scope.Close()` 呼叫 `PatchObject()` 將變更寫回 Kubernetes API。這確保了所有狀態變更都能在函數結束後被持久化，即使中途發生錯誤也不遺失。
:::

## 事件流程圖（叢集建立）

```
使用者 apply Cluster CR
         │
         ▼
CAPI Cluster Controller
  設定 OwnerRef 到 MaasCluster
         │
         ▼
MaasClusterReconciler.reconcileNormal()
  1. 建立 DNS Resource (MAAS)
  2. 設定 ControlPlaneEndpoint
  3. 標記 MaasCluster.Status.Ready = true
  4. 開始非同步輪詢 API Server
         │
         ▼
CAPI Machine Controller
  設定 OwnerRef 到 MaasMachine
         │
         ▼
MaasMachineReconciler.reconcileNormal()
  1. 等待 Bootstrap Data Secret
  2. 透過 MAAS API Allocate 裸金屬
  3. Deploy 映像檔 + user-data
  4. 追蹤 state: Deploying → Deployed
  5. 設定 ProviderID
  6. 若 CP 機器：等待 DNS 附加
```

## 子服務模組

| 模組 | 路徑 | 職責 |
|------|------|------|
| `machine.Service` | `pkg/maas/machine/machine.go` | GetMachine、DeployMachine、ReleaseMachine、PowerOnMachine |
| `dns.Service` | `pkg/maas/dns/dns.go` | ReconcileDNS、UpdateDNSAttachments、MachineIsRegisteredWithAPIServerDNS |
| `scope.NewMaasClient` | `pkg/maas/scope/client.go` | 讀取環境變數建立 maas-client-go 認證客戶端 |

::: info 相關章節
- [核心功能](./core-features) — 機器佈建與 DNS 管理的詳細流程
- [控制器與 API](./controllers-api) — CRD 欄位與 Condition 定義
- [外部整合](./integration) — MAAS API 連線設定
:::
