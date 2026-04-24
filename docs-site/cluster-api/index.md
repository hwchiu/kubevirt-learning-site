---
layout: doc
title: Cluster API — 專案總覽
---

# Cluster API — 專案總覽

Cluster API（CAPI）是 Kubernetes SIG Cluster Lifecycle 下的子專案，旨在以宣告式 Kubernetes 風格 API 自動化管理多個 Kubernetes 叢集的完整生命週期，包括佈建、升級與操作。

::: info 官方定義
Cluster API 使用 Kubernetes 風格的 API 與模式，讓平台工程師能以與應用程式部署相同的方式管理叢集基礎設施（VM、Network、LB、VPC 等）。
:::

## 什麼是 Cluster API？

傳統的 Kubernetes 叢集管理往往高度依賴各家雲端廠商或基礎設施平台的自定義腳本，難以跨環境複用。Cluster API 解決這個問題的方式是：

- **統一抽象**：將「叢集」本身定義為 Kubernetes CRD（Custom Resource Definition）
- **Provider 插件化**：將基礎設施差異封裝到 Provider 中（AWS、Azure、vSphere 等）
- **宣告式管理**：叢集狀態透過 Kubernetes Reconciliation 自動維持

## 核心架構概念

| 概念 | 說明 |
|------|------|
| **Management Cluster** | 運行 CAPI 控制器的 Kubernetes 叢集，管理其他叢集 |
| **Workload Cluster** | 由 CAPI 管理、運行實際工作負載的目標叢集 |
| **Provider** | 實作基礎設施、Bootstrap 或 ControlPlane 介面的元件 |
| **clusterctl** | CAPI 官方 CLI 工具，用於初始化 Management Cluster 與建立叢集 |
| **ClusterClass** | 叢集範本（Template），支援拓撲化（Topology）管理 |

## 專案版本資訊

- **模組路徑**：`sigs.k8s.io/cluster-api`
- **API 版本**：`v1beta2`（core, addons, ipam, runtime）
- **最低 Go 版本**：Go 1.25

```go
// 檔案: go.mod
module sigs.k8s.io/cluster-api

go 1.25.0
```

## Provider 生態系

CAPI 支援多種 Provider 類型，社群已有豐富的實作：

| Provider 類型 | 範例 | 說明 |
|--------------|------|------|
| **Infrastructure Provider** | AWS, Azure, GCP, vSphere, Metal3, MAAS | 管理 VM/實體機器佈建 |
| **Bootstrap Provider** | kubeadm（內建）, Talos, MicroK8s | 管理節點初始化 |
| **Control Plane Provider** | KubeadmControlPlane（內建）, Talos | 管理控制平面節點 |
| **IPAM Provider** | in-cluster IPAM（內建） | 管理 IP 位址分配 |

## 文件導覽

| 頁面 | 說明 |
|------|------|
| [系統架構](./architecture) | Management Cluster、Provider 模型、整體架構 |
| [核心功能](./core-features) | Cluster、Machine、MachineSet、MachineDeployment 生命週期 |
| [控制器與 API](./controllers-api) | 各控制器邏輯與 CRD 結構 |
| [Provider 模型](./providers) | InfrastructureProvider、BootstrapProvider、ControlPlaneProvider |
| [ClusterClass 與 Topology](./clusterclass) | 拓撲化叢集管理 |
| [叢集生命週期](./lifecycle) | 建立、擴縮、升級、刪除完整流程 |
| [外部整合](./integration) | clusterctl、Tilt 開發流程 |

::: tip 建議閱讀順序
新讀者建議從 [學習路徑入口](./learning-path/) 或 [系統架構](./architecture) 開始，再依需求深入各主題頁面。
:::

::: info 相關章節
- [系統架構](./architecture)
- [核心功能](./core-features)
- [學習路徑](./learning-path/)
:::
