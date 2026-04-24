---
layout: doc
title: Cluster API Provider MAAS — 專案簡介
---

# Cluster API Provider MAAS — 專案簡介

**CAPMAAS**（Cluster API Provider for MAAS）是 Spectro Cloud 維護的 Cluster API Infrastructure Provider，負責讓 Cluster API（CAPI）框架能夠在 Canonical MAAS（Metal-as-a-Service）裸金屬管理平台上自動佈建 Kubernetes 叢集。

::: info 什麼是 MAAS？
[MAAS（Metal as a Service）](https://maas.io/) 是 Canonical 開發的裸金屬管理平台，提供類似雲端的機器生命週期管理，包括：自動探索（PXE/IPMI）、映像檔部署、網路配置，以及完整的 REST API。CAPMAAS 透過此 API 來驅動 Kubernetes 節點的佈建與回收。
:::

## 核心定位

CAPMAAS 在整體 Cluster API 生態系中扮演 **Infrastructure Provider** 的角色：

| 層級 | 元件 | 職責 |
|------|------|------|
| CAPI Core | `Cluster` / `Machine` | 宣告式叢集設計，協調生命週期 |
| Bootstrap Provider | `KubeadmControlPlane` / `KubeadmConfigTemplate` | 產生節點初始化腳本（user-data）|
| Infrastructure Provider | `MaasCluster` / `MaasMachine` | 對接 MAAS API，實際申請/部署裸金屬 |

## 主要特性

- **裸金屬佈建**：透過 MAAS API 申請（Allocate）符合條件的裸金屬機器，並以 Custom image 部署 Kubernetes 節點映像檔
- **Resource Pool 篩選**：支援依 `resourcePool` 欄位限定機器資源池
- **Tag 篩選**：支援依 `tags` 欄位選擇帶有特定標籤的機器
- **DNS 負載平衡**：利用 MAAS DNS Resource 作為 API Server 的軟性負載平衡（不依賴外部 LB）
- **In-Memory 部署**：支援將機器部署於記憶體（RAM），適合短暫或測試工作負載
- **Failure Domain**：支援透過 MAAS Zone（可用區）做故障隔離
- **Webhook 驗證**：MaasCluster、MaasMachine、MaasMachineTemplate 均有 admission webhook

## 文件導覽

| 頁面 | 內容摘要 |
|------|---------|
| [系統架構](./architecture) | CAPI 框架整合、Controller 設計、Scope 模式 |
| [核心功能](./core-features) | 機器佈建流程、DNS 管理、In-Memory 部署 |
| [控制器與 API](./controllers-api) | CRD 欄位說明、Condition 定義、Controller 邏輯 |
| [外部整合](./integration) | MAAS API 用法、環境變數設定、clusterctl 部署 |
| [學習路徑](./learning-path/) | 從零到佈建完整叢集的學習指引 |

## 版本相容性

| CAPMAAS 版本 | CAPI 版本 | API Group |
|-------------|----------|-----------|
| v0.7.0+ | v1beta1 | `infrastructure.cluster.x-k8s.io/v1beta1` |

::: warning In-Memory 部署的 MAAS 版本限制
使用 `deployInMemory: true` 功能需要以下 MAAS 版本之一：**≥ 3.5.10**、**≥ 3.6.3** 或 **≥ 3.7.1**，且機器需配備至少 **16 GB RAM**。
:::

::: info 相關章節
- [系統架構](./architecture) — 深入了解 CAPMAAS 與 CAPI 的整合方式
- [核心功能](./core-features) — 裸金屬機器佈建流程詳解
- [學習路徑](./learning-path/) — 從概念到實作的完整路徑
:::
