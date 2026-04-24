---
layout: doc
title: Cluster API — 系統架構
---

# Cluster API — 系統架構

## 整體架構概覽

Cluster API 採用雙叢集架構：**Management Cluster**（管理叢集）負責運行 CAPI 控制器與 CRD，**Workload Cluster**（工作負載叢集）是被管理的目標叢集。

```
Management Cluster
┌─────────────────────────────────────────────┐
│  CAPI Core Controller Manager               │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Cluster     │  │  Machine             │ │
│  │  Controller  │  │  Controller          │ │
│  └──────────────┘  └──────────────────────┘ │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │  MachineSet  │  │  MachineDeployment   │ │
│  │  Controller  │  │  Controller          │ │
│  └──────────────┘  └──────────────────────┘ │
│                                             │
│  Infrastructure Provider (e.g. CAPV)        │
│  Bootstrap Provider (kubeadm)               │
│  ControlPlane Provider (KCP)                │
└─────────────────────────────────────────────┘
         │ reconcile → creates/manages
         ▼
Workload Cluster (target Kubernetes cluster)
```

## Management Cluster

Management Cluster 是 CAPI 的核心，本身是一個普通的 Kubernetes 叢集，其上安裝了：

- **CAPI Core CRD**：`Cluster`、`Machine`、`MachineSet`、`MachineDeployment`、`ClusterClass` 等
- **CAPI Controller Manager**：監聽並 reconcile 上述 CRD
- **Provider Controllers**：各 Provider 自行部署的控制器

::: warning 注意
Management Cluster 本身不是 Workload Cluster 的一部分。生產環境中應確保 Management Cluster 的高可用性。
:::

## Workload Cluster

Workload Cluster 是實際運行應用程式的 Kubernetes 叢集，其建立、升級、刪除均由 Management Cluster 上的控制器負責：

| 階段 | 動作 |
|------|------|
| 建立 | CAPI 呼叫 Infrastructure Provider 佈建 VM；Bootstrap Provider 提供 cloud-init；ControlPlane Provider 初始化控制平面 |
| 運行 | Machine Controller 監控節點健康；MachineHealthCheck 觸發自動修復 |
| 升級 | MachineDeployment 滾動更新策略，依序替換節點 |
| 刪除 | 先排空節點（drain），再呼叫 Infrastructure Provider 刪除資源 |

## Provider 架構

CAPI 的擴展性透過 **Provider** 實現，每種 Provider 實作特定的合約介面（Contract）。

### 三大 Provider 類型

```
┌─────────────────────────────────────────────────────────┐
│                    CAPI Core                            │
│  Cluster CRD  →  spec.infrastructureRef                 │
│              →  spec.controlPlaneRef                    │
│  Machine CRD  →  spec.infrastructureRef                 │
│              →  spec.bootstrap.configRef                │
└──────────────────┬──────────────────────────────────────┘
                   │ references (cross-GVK)
    ┌──────────────┼──────────────────┐
    ▼              ▼                  ▼
InfraProvider  BootstrapProvider  ControlPlaneProvider
(e.g. AWSCluster) (KubeadmConfig) (KubeadmControlPlane)
```

| Provider 類型 | 負責範疇 | 代表資源 |
|--------------|---------|---------|
| **Infrastructure** | VM/實體機佈建、網路、磁碟 | `AWSCluster`, `VSphereCluster`, `Metal3Cluster` |
| **Bootstrap** | 節點初始化腳本（cloud-init/ignition） | `KubeadmConfig`, `TalosConfig` |
| **ControlPlane** | 控制平面節點生命週期、etcd 管理 | `KubeadmControlPlane` |

## 控制器架構

CAPI Core Controller Manager 在啟動時會設定所有核心控制器：

```go
// 檔案: main.go
controllerName = "cluster-api-controller-manager"

// 主要 Controller 清單（透過 setup 套件初始化）
// - Cluster Controller
// - Machine Controller
// - MachineSet Controller
// - MachineDeployment Controller
// - MachineHealthCheck Controller
// - ClusterClass Controller (需要 ClusterTopology feature gate)
// - ExtensionConfig Controller
```

### 控制器間的關係

| 控制器 | Watch 對象 | 主要動作 |
|--------|-----------|---------|
| ClusterReconciler | Cluster | 協調 Infrastructure + ControlPlane |
| MachineReconciler | Machine | 協調 Bootstrap + Infrastructure |
| MachineSetReconciler | MachineSet | 管理 Machine 副本數 |
| MachineDeploymentReconciler | MachineDeployment | 管理 MachineSet 滾動升級 |
| MachineHealthCheckReconciler | MachineHealthCheck | 偵測並修復不健康節點 |
| TopologyReconciler | Cluster (with topology) | 根據 ClusterClass 協調整個拓撲 |

## ClusterCache — 遠端連線管理

CAPI 需要對 Workload Cluster 進行操作（如 Node 管理），透過 `ClusterCache` 維護 Management Cluster 到各 Workload Cluster 的連線：

```go
// 檔案: controllers/clustercache/clustercache.go
// ClusterCache 管理對 Workload Cluster 的 client 連線
// 使用 kubeconfig（存於 Management Cluster 的 Secret）建立連線
type ClusterCache interface {
    // GetClient 取得指定 Workload Cluster 的 client
    GetClient(ctx context.Context, cluster client.ObjectKey) (client.Client, error)
}
```

::: tip 設計原則
CAPI 的每個 Provider 都遵循「合約（Contract）」設計，Core 控制器僅依賴合約中定義的欄位，而非 Provider 的具體實作，達到真正的解耦。
:::

::: info 相關章節
- [核心功能](./core-features)
- [Provider 模型](./providers)
- [控制器與 API](./controllers-api)
:::
