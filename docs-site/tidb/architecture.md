---
layout: doc
---

# TiDB — 系統架構

::: tip 分析版本
本文件基於 commit [`6f4dd4fd`](https://github.com/pingcap/tidb/commit/6f4dd4fdab3774e5d7355039df79112dbe59cc6e) 進行分析。
:::

::: info 相關章節
- 專案簡介與總覽請參閱 [專案總覽](./index)
- SQL 執行與交易機制請參閱 [核心功能分析](./core-features)
- HTTP API 與 Session 管理請參閱 [控制器與 API](./controllers-api)
- 備份、匯入與外部整合請參閱 [外部整合](./integration)
:::

## 專案目錄結構

TiDB 主要目錄及其用途如下：

| 目錄 | 說明 |
|------|------|
| `pkg/` | 核心套件，包含 parser、planner、executor、session、server 等所有主要邏輯 |
| `cmd/` | 可執行檔入口，包含 tidb-server 與各種工具 binary |
| `br/` | Backup & Restore 子專案，分散式備份與還原工具 |
| `lightning/` | TiDB Lightning 資料匯入工具子專案 |
| `dumpling/` | Dumpling 資料匯出工具子專案 |
| `build/` | 建置腳本與工具 |
| `tools/` | 開發輔助工具（ut 測試執行器、xprog 等） |
| `tests/` | 整合測試與系統測試 |
| `docs/` | 開發者文件 |
| `hooks/` | Git hooks 腳本 |

## TiDB Server 內部架構

TiDB Server 是整個系統的 SQL 引擎,負責解析 MySQL 協定、解析 SQL、優化查詢並分發執行計劃。

![TiDB Server 內部架構](/diagrams/tidb/tidb-architecture-server-1.png)

## `cmd/` 可執行檔一覽

| 目錄 | Binary 名稱 | 說明 |
|------|------------|------|
| `cmd/tidb-server` | `tidb-server` | TiDB 主伺服器程式（MySQL 協定監聽、SQL 執行引擎） |
| `cmd/benchdb` | `benchdb` | 資料庫層級效能基準測試工具 |
| `cmd/benchkv` | `benchkv` | KV 層級效能基準測試工具 |
| `cmd/benchraw` | `benchraw` | 原始 KV 讀寫效能基準測試工具 |
| `cmd/ddltest` | `ddltest` | DDL 壓力測試工具 |
| `cmd/importer` | `importer` | 資料匯入輔助工具 |
| `cmd/mirror` | `mirror` | 鏡像輔助工具 |
| `cmd/pluginpkg` | `pluginpkg` | Plugin 套件打包工具 |

## `pkg/` 主要套件一覽

| 套件 | 功能說明 |
|------|---------|
| `pkg/parser` | SQL 語法解析器（yacc/goyacc 生成，內建 AST 定義） |
| `pkg/planner` | 查詢優化器（邏輯計劃、物理計劃、代價估算） |
| `pkg/planner/core` | 核心優化規則與物理計劃選擇 |
| `pkg/planner/cardinality` | 基數估算，統計資訊驅動 |
| `pkg/planner/cascades` | Cascades 優化框架實作 |
| `pkg/executor` | SQL 執行引擎（火山模型，各算子實作） |
| `pkg/ddl` | DDL 非同步執行框架（online schema change） |
| `pkg/session` | Session 管理、事務協調 |
| `pkg/store` | 儲存引擎抽象層（TiKV / unistore 本地模式） |
| `pkg/statistics` | 統計資訊收集與維護（直方圖、TopN、CM-Sketch） |
| `pkg/server` | MySQL 協定伺服器（連線處理、封包解析） |
| `pkg/infoschema` | Information Schema 實作（in-memory 快取） |
| `pkg/domain` | Domain 物件（DDL Owner 選舉、schema 載入） |
| `pkg/expression` | 表達式求值框架（函數庫、向量化） |
| `pkg/kv` | KV 抽象介面（Transaction、Snapshot、Iter） |
| `pkg/meta` | 元資料 KV 編碼（table/index/database 鍵值佈局） |
| `pkg/privilege` | 權限管理（MySQL 相容的 GRANT/REVOKE） |
| `pkg/metrics` | Prometheus 指標、Grafana Dashboard 定義 |
| `pkg/lightning` | TiDB Lightning 核心匯入邏輯（physical import mode） |
| `pkg/ttl` | TTL（Time-To-Live）資料自動過期刪除 |
| `pkg/resourcegroup` | Resource Group 資源管控（TiDB 7.x+） |
| `pkg/autoid_service` | 分散式 Auto-Increment ID 服務 |
| `pkg/bindinfo` | SQL Binding（SQL Plan Management） |
| `pkg/disttask` | 分散式任務框架 |
| `pkg/owner` | Owner 選舉（DDL Owner 等分散式角色選舉） |
| `pkg/util` | 通用工具函式庫 |

## 儲存層設計

### TiKV — 行式儲存

TiKV 是 TiDB 的主要 OLTP 儲存引擎，以 Rust 編寫，採用以下設計：

| 概念 | 說明 |
|------|------|
| **Region** | 資料分片單位，預設大小 96MB，由 Raft 組管理 |
| **Raft 組** | 每個 Region 有 3 個副本，組成獨立的 Raft 組 |
| **Leader / Follower** | Raft Leader 負責讀寫，Follower 同步資料 |
| **RocksDB** | 底層儲存引擎，Region 資料以 SST 檔案存放 |
| **Coprocessor** | 下推計算框架，TiDB 可將過濾/聚合下推至 TiKV |
| **Percolator 2PC** | 分散式交易協定，以 TiKV 儲存鎖與版本資訊 |
| **MVCC** | 多版本並行控制，以時間戳區分資料版本 |

### TiFlash — 列式儲存

TiFlash 以 C++ 編寫，使用 ClickHouse 列式引擎：

| 特性 | 說明 |
|------|------|
| **同步機制** | Multi-Raft Learner：以只讀副本方式加入 TiKV Raft 組，非同步複製資料 |
| **資料格式** | 列式儲存（Delta Tree 結構），針對 OLAP 掃描優化 |
| **MPP 計算** | 支援多節點 MPP（Massively Parallel Processing）查詢 |
| **一致性** | Snapshot Isolation，與 TiKV 保持最終一致 |

## 典型 SQL 查詢執行序列

![典型 SQL 查詢執行序列](/diagrams/tidb/tidb-architecture-sequence-2.png)

## 建置工具鏈

| 工具 | 用途 |
|------|------|
| `go build` | 主要編譯工具 |
| `bazel` | ABI 驗證、授權標頭檢查 |
| `golangci-lint` | 綜合靜態分析 |
| `revive` | Go 程式碼規範 linter |
| `gofmt` | 程式碼格式化 |
| `tools/bin/ut` | 自訂單元測試執行器 |
| `errdoc-gen` | 錯誤碼文件產生器 |
