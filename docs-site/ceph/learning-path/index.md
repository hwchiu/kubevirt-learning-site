---
layout: doc
title: Ceph — 學習路徑入口
---

# Ceph — 學習路徑入口

如果你第一次系統性學 Ceph，最容易卡住的地方通常不是單一名詞，而是：**MON、OSD、CRUSH、PG、cephadm、Dashboard 到底該先學哪一個？**

這個入口頁把 Ceph 拆成兩條路徑：

- **控制面路徑**：先理解叢集如何被部署、管理與觀測
- **資料面路徑**：再理解資料如何被定位、寫入、複寫與修復

## 推薦學習順序

| 階段 | 先讀什麼 | 你會得到什麼 |
|---|---|---|
| 1 | [專案總覽](/ceph/) | 建立 Ceph 全貌與元件角色 |
| 2 | [整體架構概述](/ceph/architecture) | 理解控制面 / 資料面分工 |
| 3 | [部署架構與 cephadm](/ceph/deployment) | 知道現代 Ceph 如何被建起來 |
| 4 | [cephadm 深入分析](/ceph/cephadm) | 看懂 orchestrator、spec 與 day-2 管理 |
| 5 | [Dashboard](/ceph/dashboard) | 把 UI、Prometheus、Grafana 與 alert 串起來 |
| 6 | [日常維運](/ceph/operations) | 建立巡檢、排錯與升級流程 |
| 7 | [故事驅動式學習](/ceph/learning-path/story) | 用一條資料流把前面概念重新串起來 |

## 兩條建議路徑

### 路徑 A：平台工程 / SRE 視角

適合想先掌握部署、升級、監控與排障的人。

1. [部署架構與 cephadm](/ceph/deployment)
2. [cephadm 深入分析](/ceph/cephadm)
3. [Dashboard](/ceph/dashboard)
4. [日常維運](/ceph/operations)
5. 回頭補 [整體架構概述](/ceph/architecture)

### 路徑 B：儲存系統 / 架構視角

適合想先理解 RADOS、PG、CRUSH、OSD 資料路徑的人。

1. [整體架構概述](/ceph/architecture)
2. [故事驅動式學習](/ceph/learning-path/story)
3. [部署架構與 cephadm](/ceph/deployment)
4. [Dashboard](/ceph/dashboard)
5. [日常維運](/ceph/operations)

## 你可以帶著哪些問題閱讀？

### 控制面問題

- Ceph 為什麼把 cephadm 放在 `ceph-mgr` 內？
- `ceph orch` 和 `cephadm` 的邊界在哪裡？
- Dashboard 為什麼能同時看到 health、Prometheus 與 Grafana？

### 資料面問題

- client 怎麼知道 object 應該去哪個 PG？
- primary OSD 與 replica OSD 怎麼協調 commit？
- 什麼情況會讓 PG 變成 degraded、undersized 或 backfilling？

## 最佳使用方式

- **第一次閱讀**：照表格順序看，不要急著鑽太深
- **第二次閱讀**：改用故事頁把零散概念串成一條資料流
- **實務維運時**：直接把 [日常維運](/ceph/operations) 當成巡檢索引

::: tip 建議節奏
如果你只有 30 分鐘，先看 `architecture` + `cephadm` + `dashboard`。這三頁最能快速建立「Ceph 是怎麼被管理、又怎麼被觀測」的主幹概念。
:::

## 接下來去哪裡？

- 想先看完整故事：前往 [故事驅動式學習](/ceph/learning-path/story)
- 想先補控制面：前往 [cephadm 深入分析](/ceph/cephadm)
- 想直接進維運：前往 [日常維運](/ceph/operations)

::: info 相關章節
- [Ceph — 專案總覽](/ceph/)
- [Ceph — 整體架構概述](/ceph/architecture)
- [Ceph — cephadm 深入分析](/ceph/cephadm)
- [Ceph — 故事驅動式學習路徑](/ceph/learning-path/story)
:::
