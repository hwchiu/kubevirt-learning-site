---
layout: doc
title: TiDB — 學習路徑
---

# 📖 TiDB 故事驅動學習路徑

> 這是一條為「MySQL/資料庫熟手、TiDB 新手」設計的學習路徑。透過一個真實的情境故事，你將跟著主角阿倫逐步理解 TiDB 的核心概念與實作細節。

---

## 你適合這條路徑嗎？

這條路徑假設你：

- ✅ 熟悉 MySQL 的基本操作與管理（索引、交易、備份）
- ✅ 了解資料庫擴展的困境（分片、主從複製的限制）
- ✅ 對分散式系統的基本概念有一點了解（不用精通）
- ❌ 不需要有任何 TiDB 使用或操作經驗

---

## 前置條件

在開始這條路徑之前，建議你具備以下知識：

| 知識領域 | 說明 |
|----------|------|
| **MySQL 基礎** | 熟悉 SQL 查詢、DDL、交易（BEGIN/COMMIT/ROLLBACK） |
| **資料庫管理** | 了解備份（mysqldump）、主從複製、慢查詢排查 |
| **水平擴展挑戰** | 曾經遭遇或了解分片（Sharding）的複雜性 |
| **Linux / 命令列** | 能看懂基本的系統操作指令 |

---

## 📖 [故事驅動式學習路徑](./story)

**主角**：阿倫，一位公司 DBA + Platform Engineer，管理多個 MySQL 實例多年。

**任務觸發**：公司訂單資料庫已達 MySQL 的擴展上限——單機寫入瓶頸、分片方案維護成本爆炸。老闆要求他評估 TiDB，判斷能否作為下一代資料庫平台。

**風格**：跟著阿倫從「MySQL DBA 的視角」出發，一章章遭遇問題、尋找答案。每個 TiDB 核心概念都在他解決具體問題時自然出現——為什麼需要計算儲存分離？Raft 怎麼保持一致性？分散式交易到底怎麼運作？

**適合**：喜歡有情境脈絡、想先理解「為什麼」再看「是什麼」的學習者，尤其是有 DBA 背景的工程師。

**[→ 開始閱讀故事](./story)**

---

## 旅程地圖

| 章節 | 主題 | 核心概念 |
|------|------|----------|
| 序章 | MySQL 的天花板 | 水平擴展的困境、TiDB 的承諾 |
| 第一章 | 計算與儲存分離 | TiDB Server、TiKV、PD 的角色 |
| 第二章 | Raft 與資料一致性 | TiKV Region、Raft 共識協議 |
| 第三章 | PD 的幕後工作 | TSO 時間戳、Region 負載均衡 |
| 第四章 | 分散式交易 2PC | Percolator、Prewrite/Commit |
| 第五章 | HTAP 與 TiFlash | 列式複製、智慧查詢路由 |
| 第六章 | 資料遷移實戰 | TiDB Lightning、Dumpling |
| 第七章 | 備份與還原 | BR 工具、增量備份 |
| 第八章 | Change Data Capture | TiCDC、下游 Kafka/MySQL |
| 第九章 | 叢集觀測 | TiDB Dashboard、慢查詢分析 |

---

::: info 📚 相關技術文件
讀完故事後，可深入閱讀各主題的技術文件：

- [專案總覽](/tidb/) — TiDB 架構概觀與專案資訊
- [系統架構](/tidb/architecture) — TiDB Server、TiKV、PD、TiFlash 詳解
- [核心功能](/tidb/core-features) — SQL 執行、2PC 交易、HTAP 路由、DDL
- [控制器與 API](/tidb/controllers-api) — HTTP Status API、Dashboard、Session 管理
- [外部整合](/tidb/integration) — BR 備份還原、TiDB Lightning、Dumpling、TiCDC
:::
