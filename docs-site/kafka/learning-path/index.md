---
layout: doc
title: Kafka — 故事驅動學習路徑
---

# Kafka 故事驅動學習路徑

## 你適合這條路徑嗎？

這條學習路徑是為 **後端工程師** 設計的，特別是正在面對微服務架構挑戰的你。

如果你符合以下條件，那這條路徑很適合你：

- ✅ 有基本後端開發經驗（REST API、資料庫操作）
- ✅ 了解什麼是微服務，且正在或即將面對跨服務資料同步問題
- ✅ 聽說過 Kafka，但不確定它實際解決什麼問題
- ✅ 喜歡透過「情境故事」而非純理論來學習技術

如果你是完全沒有程式背景的讀者，建議先補充基本的 HTTP API 和資料庫概念再回來。

---

## 前置條件

| 條件 | 說明 |
|------|------|
| **程式語言** | 能看懂 Java/Kotlin 虛擬碼即可（不需要動手實作） |
| **分散式概念** | 知道「服務」和「資料庫」是分開的節點就夠了 |
| **訊息佇列** | 有聽過 RabbitMQ 或 SQS 更好，但非必要 |
| **Docker** | 了解容器的基本概念（選修） |

---

## 故事簡介

主角 **小蔡** 是一位後端工程師，任職於一間電商新創公司。公司的訂單系統和庫存系統靠 REST API 互相呼叫，隨著業務成長，這種設計帶來了越來越多問題：

- 庫存系統一掛，訂單系統也跟著出錯
- 扣庫存和建訂單沒有原子性，常常資料不一致
- 每加一個新服務（物流、通知），就要改訂單系統的程式碼

架構師說：「我們需要引入 Kafka。」

小蔡開始了他的 Kafka 探索之旅——從「什麼是 Topic」到「KRaft 是什麼鬼」，每一章都是他在實際開發中遇到問題、找到答案的過程。

---

## 學習路徑地圖

| 章節 | 主題 | 核心概念 |
|------|------|----------|
| 第 1 章 | 為什麼要有 Kafka | 耦合問題、事件驅動模式 |
| 第 2 章 | Topic 和 Partition | 訊息組織、水平擴展 |
| 第 3 章 | 寫第一個 Producer | 發送訊息、批次、壓縮 |
| 第 4 章 | 寫第一個 Consumer | Offset、Consumer Group |
| 第 5 章 | Rebalance | 消費者掛掉時發生什麼事 |
| 第 6 章 | Exactly-Once 語義 | 重複消費、Idempotent Producer |
| 第 7 章 | Kafka Connect | CDC、不寫程式碼的整合 |
| 第 8 章 | KRaft 模式 | 告別 ZooKeeper |
| 第 9 章 | Kafka Streams | 在 Kafka 裡做串流計算 |
| 第 10 章 | 效能調優 | 吞吐量 vs 延遲 |

---

## 開始閱讀

👉 **[進入故事：小蔡的事件驅動之旅](./story)**

---

## 相關技術文件

閱讀故事後，可以透過以下技術文件深入原始碼實作：

- [專案總覽](/kafka/) — Kafka 架構全貌、模組介紹
- [系統架構](/kafka/architecture) — KRaft 叢集拓撲、Broker/Controller 角色、Log 儲存機制
- [核心功能](/kafka/core-features) — Producer/Consumer API、訊息格式、Transaction
- [核心模組深度解析](/kafka/modules) — core、clients、streams、connect、raft、metadata 模組
- [外部整合](/kafka/integration) — Kafka Connect、MirrorMaker 2、Schema Registry

::: info 學習建議
建議先讀完故事的前 4 章，對 Producer/Consumer 有基本感覺之後，再交叉閱讀技術文件中的 [核心功能](/kafka/core-features) 頁面，效果最佳。
:::
