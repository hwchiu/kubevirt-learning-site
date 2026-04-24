---
layout: doc
title: Cluster API Provider Metal3 — 學習路徑
---

# Cluster API Provider Metal3 — 學習路徑

歡迎來到 CAPM3 學習路徑！本指南幫助你根據背景知識與學習目標，規劃最適合的學習順序。

## 你是哪種學習者？

### 路線 A：我是 Kubernetes 管理員，想了解裸金屬叢集

**目標**：能夠部署並管理基於 Metal3 的裸金屬 Kubernetes 叢集

推薦順序：
1. [專案簡介](/cluster-api-provider-metal3/) — 了解 CAPM3 的定位與 Metal3 技術棧
2. [系統架構](/cluster-api-provider-metal3/architecture) — 理解元件關係與部署架構
3. [核心功能](/cluster-api-provider-metal3/core-features) — 掌握 Metal3Cluster 與 Metal3Machine 的設定
4. [外部整合](/cluster-api-provider-metal3/integration) — 了解與 CAPI、Ironic、IPAM 的整合
5. [節點修復](/cluster-api-provider-metal3/remediation) — 設定自動修復策略

### 路線 B：我是開發者，想深入了解 CAPM3 的實作

**目標**：理解 CAPM3 的程式碼架構，能夠貢獻或修改功能

推薦順序：
1. [系統架構](/cluster-api-provider-metal3/architecture) — 了解分層設計與元件職責
2. [控制器與 API](/cluster-api-provider-metal3/controllers-api) — 深入 Reconcile 邏輯
3. [裸金屬管理](/cluster-api-provider-metal3/baremetal) — 理解 BMH 選取與 provisioning 機制
4. [核心功能](/cluster-api-provider-metal3/core-features) — CRD API 設計細節
5. [節點修復](/cluster-api-provider-metal3/remediation) — Remediation 狀態機設計

### 路線 C：我想快速評估 CAPM3 是否適合我的需求

**目標**：快速了解 CAPM3 的能力與限制

推薦順序：
1. [專案簡介](/cluster-api-provider-metal3/) — 10 分鐘了解全貌
2. [故事驅動式學習](/cluster-api-provider-metal3/learning-path/story) — 透過實際場景理解工作流程

## 各頁面重點摘要

| 頁面 | 關鍵概念 | 建議讀者 |
|------|---------|---------|
| [專案簡介](/cluster-api-provider-metal3/) | CAPM3 定位、CRD 清單、快速安裝 | 所有人 |
| [系統架構](/cluster-api-provider-metal3/architecture) | Metal3 技術棧、分層設計、元件協作 | 架構師、開發者 |
| [核心功能](/cluster-api-provider-metal3/core-features) | Metal3Cluster/Machine/Data 詳解 | 管理員、開發者 |
| [控制器與 API](/cluster-api-provider-metal3/controllers-api) | Reconcile 流程、Manager 設計 | 開發者 |
| [裸金屬管理](/cluster-api-provider-metal3/baremetal) | BMH 選取、provisioning 狀態機 | 管理員、開發者 |
| [外部整合](/cluster-api-provider-metal3/integration) | CAPI/Ironic/IPAM 整合 | 架構師、管理員 |
| [節點修復](/cluster-api-provider-metal3/remediation) | MachineHealthCheck、Reboot 策略 | 管理員、SRE |

## 先備知識檢查

學習 CAPM3 前，建議具備以下基礎知識：

- **Kubernetes 基礎**：Pod、Deployment、Namespace、CRD 的概念
- **Cluster API 基礎**：了解 CAPI 的 Cluster、Machine、Infrastructure Provider 概念
- **裸金屬基礎**：了解 PXE boot、IPMI/Redfish、磁碟 provisioning 的基本概念
- **Go 語言**（開發者路線）：基本的 Go 語法與 controller-runtime 框架

::: tip 從哪裡開始？
如果你完全不熟悉 CAPM3，建議從 [故事驅動式學習](/cluster-api-provider-metal3/learning-path/story) 開始，透過一個完整的裸金屬叢集部署場景來建立直覺。
:::

::: info 相關章節
- [故事驅動式學習](/cluster-api-provider-metal3/learning-path/story)
- [專案簡介](/cluster-api-provider-metal3/)
- [系統架構](/cluster-api-provider-metal3/architecture)
:::
