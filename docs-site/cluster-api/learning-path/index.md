---
layout: doc
title: Cluster API — 學習路徑入口
---

# Cluster API — 學習路徑入口

歡迎來到 Cluster API 的學習路徑！本路徑為您規劃了由淺入深的閱讀順序，無論您是初學者還是有一定基礎的工程師，都能找到適合的切入點。

## 學習路徑概覽

```
Level 1：概念理解
  → 專案總覽（index）
  → 系統架構（architecture）

Level 2：核心 API
  → 核心功能（core-features）
  → Provider 模型（providers）

Level 3：進階主題
  → 控制器與 API（controllers-api）
  → ClusterClass 與 Topology（clusterclass）
  → 叢集生命週期（lifecycle）

Level 4：實際操作
  → 外部整合（integration）
```

## 推薦學習路徑

### 路徑 A：平台工程師（Operations）

適合需要**建立和管理多個 Kubernetes 叢集**的工程師：

| 步驟 | 頁面 | 重點 |
|------|------|------|
| 1 | [系統架構](../architecture) | 了解 Management/Workload Cluster 模型 |
| 2 | [外部整合](../integration) | 學習 clusterctl 工具 |
| 3 | [叢集生命週期](../lifecycle) | 掌握叢集建立、升級、刪除 |
| 4 | [ClusterClass](../clusterclass) | 標準化叢集範本 |

### 路徑 B：平台開發者（Provider 開發）

適合需要**開發自定義 Provider** 的工程師：

| 步驟 | 頁面 | 重點 |
|------|------|------|
| 1 | [系統架構](../architecture) | 理解 Provider 合約 |
| 2 | [Provider 模型](../providers) | 三種 Provider 類型與介面 |
| 3 | [控制器與 API](../controllers-api) | 核心 CRD 結構 |
| 4 | [核心功能](../core-features) | Machine 生命週期細節 |

### 路徑 C：故事驅動式學習

透過完整的情境故事，帶您體驗一個企業團隊如何從零開始使用 CAPI 管理多個叢集：

→ **[開始故事之旅](./story)**

## 快速參考表

| 我想了解… | 去哪裡看 |
|-----------|---------|
| CAPI 是什麼 | [專案總覽](../index) |
| Management vs Workload Cluster | [系統架構](../architecture) |
| Cluster / Machine CRD 結構 | [核心功能](../core-features) |
| 如何初始化 Management Cluster | [外部整合](../integration) |
| ClusterClass 怎麼用 | [ClusterClass 與 Topology](../clusterclass) |
| 叢集升級流程 | [叢集生命週期](../lifecycle) |
| 如何開發 Provider | [Provider 模型](../providers) |
| 各控制器的 Reconcile 邏輯 | [控制器與 API](../controllers-api) |

::: tip 給完全初學者
建議先閱讀 [故事驅動式學習](./story)，透過完整情境快速建立整體概念，再回頭閱讀各技術頁面。
:::

::: info 相關章節
- [專案總覽](../index)
- [系統架構](../architecture)
- [故事驅動式學習](./story)
:::
