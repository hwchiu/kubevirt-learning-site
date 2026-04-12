---
layout: doc
---

# TiDB — 控制器與 API

::: tip 分析版本
本文件基於 commit [`6f4dd4fd`](https://github.com/pingcap/tidb/commit/6f4dd4fdab3774e5d7355039df79112dbe59cc6e) 進行分析。
:::

::: info 相關章節
- 專案簡介與總覽請參閱 [專案總覽](./index)
- 系統元件與目錄結構請參閱 [系統架構](./architecture)
- SQL 執行與交易機制請參閱 [核心功能分析](./core-features)
- 備份、匯入與外部整合請參閱 [外部整合](./integration)
:::

## MySQL 協定伺服器（`pkg/server`）

`pkg/server/` 實作了 TiDB 的 MySQL 協定伺服器，主要檔案包括：

| 檔案 | 說明 |
|------|------|
| `server.go` | TCP 監聽、連線建立、Graceful Shutdown |
| `conn.go` | 單一客戶端連線的完整生命週期管理 |
| `http_status.go` | HTTP Status API 端點（監控與診斷用） |
| `driver_tidb.go` | TiDB Session Driver，橋接 server 層與 session 層 |
| `packetio.go` | MySQL 封包讀寫緩衝 |

### 連線處理流程

![TiDB 連線處理流程](/diagrams/tidb/tidb-connection-flow.png)

## HTTP Status API（`pkg/server/http_status.go`）

TiDB Server 預設在 `:10080` 埠提供 HTTP 診斷 API：

| 端點 | 方法 | 說明 |
|------|------|------|
| `/status` | GET | 回傳伺服器基本狀態（版本、連線數、uptime） |
| `/metrics` | GET | Prometheus 指標匯出（scrape endpoint） |
| `/settings` | GET/POST | 動態讀取／修改系統變數 |
| `/schema` | GET | 取得 Database Schema 資訊 |
| `/schema/{db}/{table}` | GET | 取得指定資料表的 Schema 詳情 |
| `/tables/{colID}/{rowID}` | GET | 依 Column ID / Row ID 查詢資料 |
| `/ddl/history` | GET | 查看 DDL 歷史記錄 |
| `/ddl/owner/resign` | POST | 讓當前 DDL Owner 主動放棄 Owner 身份 |
| `/info` | GET | 叢集所有 TiDB Server 的版本與狀態資訊 |
| `/info/all` | GET | 所有節點的詳細資訊 |
| `/regions/meta` | GET | Region 元資料列表 |
| `/regions/hot` | GET | 熱點 Region 資訊 |
| `/debug/pprof/` | GET | Go pprof 效能分析端點 |
| `/optimize_trace` | POST | SQL 優化追蹤（Optimizer Trace） |

## Session 管理（`pkg/session`）

Session 是 TiDB 中每個客戶端連線的核心抽象，主要檔案：

| 檔案 | 說明 |
|------|------|
| `session.go` | Session 介面定義與主要實作（`sessionCtx`） |
| `txn.go` | 事務狀態機、Commit/Rollback 邏輯 |
| `txnmanager.go` | 事務管理器，處理 BEGIN/START TRANSACTION |
| `bootstrap.go` | TiDB Server 啟動時的 Bootstrap 邏輯（建立系統資料表） |
| `tidb.go` | 對外的 SQL 執行入口 |

### Session 生命週期

![TiDB Session 生命週期](/diagrams/tidb/tidb-session-lifecycle.png)

## Information Schema（`pkg/infoschema`）

Information Schema 在 TiDB 中以 **in-memory** 快取實作，而非每次查詢都去 TiKV 讀取：

| 機制 | 說明 |
|------|------|
| **版本化快取** | 每個 Schema 版本對應一份 infoschema 快取 |
| **快取回收** | 維護最近 N 個版本的快取，老舊版本被 GC 回收 |
| **事件監聽** | DDL 執行後觸發 infoschema 版本升級 |
| **延遲載入** | Table 的詳細資訊（欄位、索引）採用懶載入策略 |

## Plugin 系統（`pkg/plugin`）

TiDB Plugin 系統允許在不修改核心原始碼的情況下擴充功能：

| 插件類型 | 說明 |
|---------|------|
| **Audit** | 審計日誌，記錄 SQL 操作（企業版常用） |
| **Schema Validator** | 自訂 Schema 驗證邏輯 |
| **Password Validation** | 密碼強度驗證規則 |
| **Auth** | 自訂認證後端 |

Plugin 以 Go Plugin（`.so` 動態函式庫）形式載入，透過 `--plugin-dir` 和 `--plugin-load` 參數啟用。

## Privilege 管理系統（`pkg/privilege`）

TiDB 的權限系統完全相容 MySQL，核心設計：

| 表格 | 說明 |
|------|------|
| `mysql.user` | 全域使用者帳號與全域權限 |
| `mysql.db` | 資料庫級別權限 |
| `mysql.tables_priv` | 資料表級別權限 |
| `mysql.columns_priv` | 欄位級別權限 |

- 支援 `GRANT`、`REVOKE`、`SHOW GRANTS` 語句
- 支援 **基於角色的存取控制（RBAC）**：`CREATE ROLE`、`GRANT role TO user`
- 支援 **Dynamic Privilege**（動態權限），如 `BACKUP_ADMIN`、`RESTORE_ADMIN`
- 支援 **列級別安全（Column-Level Privilege）**

## Prometheus 指標（`pkg/metrics`）

TiDB 向 Prometheus 匯出豐富的觀測指標：

| 指標分類 | 說明 |
|---------|------|
| `tidb_server_query_total` | SQL 查詢計數（依類型分類） |
| `tidb_server_query_duration_seconds` | SQL 執行耗時直方圖 |
| `tidb_server_connections` | 當前連線數 |
| `tidb_session_transaction_duration_seconds` | 交易執行耗時 |
| `tidb_tikvclient_backoff_seconds` | TiKV 退避重試統計 |
| `tidb_owner_watch_owner_duration_seconds` | DDL Owner 選舉延遲 |
| `tidb_executor_statement_total` | 算子執行計數 |
| `tidb_domain_load_schema_duration_seconds` | Schema 載入耗時 |
| `tidb_distsql_handle_query_duration_seconds` | 分散式 SQL 查詢耗時 |

官方提供預建的 [Grafana Dashboard](https://github.com/pingcap/tidb/tree/master/metrics)，可直接匯入 Grafana 使用。
