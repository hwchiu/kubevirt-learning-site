---
layout: doc
---

# TiDB — 外部整合

::: tip 分析版本
本文件基於 commit [`6f4dd4fd`](https://github.com/pingcap/tidb/commit/6f4dd4fdab3774e5d7355039df79112dbe59cc6e) 進行分析。
:::

::: info 相關章節
- 專案簡介與總覽請參閱 [專案總覽](./index)
- 系統元件與目錄結構請參閱 [系統架構](./architecture)
- SQL 執行與交易機制請參閱 [核心功能分析](./core-features)
- HTTP API 與 Session 管理請參閱 [控制器與 API](./controllers-api)
:::

## BR（Backup & Restore）

**BR** 是 TiDB 叢集的分散式備份與還原命令列工具，原始碼位於 `br/` 目錄。

### 主要功能

| 功能 | 說明 |
|------|------|
| **全量備份** | 備份整個叢集或指定資料庫/資料表至外部儲存 |
| **增量備份** | 備份指定時間範圍內的增量資料 |
| **PITR（Point-in-Time Recovery）** | 基於全量備份 + 日誌備份實現任意時間點還原 |
| **資料表備份** | 僅備份指定資料表，支援精細粒度控制 |
| **EBS 卷快照備份** | 支援 AWS EBS 卷快照備份（近乎零 RTO） |

### 支援的儲存目標

| 儲存類型 | URI 格式 |
|---------|---------|
| Amazon S3 | `s3://bucket/path` |
| Google Cloud Storage | `gcs://bucket/path` |
| Azure Blob Storage | `azure://container/path` |
| 本地端檔案系統 | `local:///path/to/dir` |

### 常用指令

```bash
# 建置 BR
make build_br

# 全量備份至 S3
br backup full \
  --pd "127.0.0.1:2379" \
  --storage "s3://my-bucket/backup" \
  --s3.region "us-east-1"

# 還原全量備份
br restore full \
  --pd "127.0.0.1:2379" \
  --storage "s3://my-bucket/backup"
```

## TiDB Lightning

**TiDB Lightning** 是用於將 TB 級資料快速匯入 TiDB 的工具，原始碼位於 `lightning/` 目錄，核心邏輯在 `pkg/lightning/`。

### 匯入模式對比

| 特性 | Physical Import Mode | Logical Import Mode |
|------|---------------------|---------------------|
| **原理** | 直接產生 SST 檔案，繞過 SQL 層寫入 TiKV | 透過 SQL 語句（INSERT / REPLACE）寫入 |
| **速度** | 極快（通常 GB/s 級別） | 較慢（受 SQL 執行效能限制） |
| **對叢集影響** | 較大（需要獨佔 Region） | 較小（線上並行寫入） |
| **適用場景** | 初次資料載入、大規模遷移 | 增量資料匯入、需要線上服務的場景 |

### 支援的資料來源

| 格式 | 說明 |
|------|------|
| **SQL Dump** | `mysqldump` 或 `Dumpling` 輸出的 SQL 文件 |
| **CSV** | 標準 CSV 格式，支援自訂分隔符與轉義字元 |
| **Parquet** | Apache Parquet 列式格式 |
| **Amazon Aurora** | 透過 Amazon Aurora 匯出的 Parquet 格式 |

### 常用指令

```bash
# 建置 TiDB Lightning
make build_lightning

# Physical Import Mode 匯入
tidb-lightning \
  --backend=local \
  --sorted-kv-dir=/tmp/sorted-kv \
  -d /path/to/data

# Logical Import Mode 匯入（推薦線上使用）
tidb-lightning \
  --backend=tidb \
  --tidb.host=127.0.0.1 \
  --tidb.port=4000 \
  -d /path/to/data
```

## Dumpling

**Dumpling** 是用於從 MySQL 相容資料庫匯出 SQL dump 的工具，位於 `dumpling/` 目錄，定位為 `mysqldump` 與 `mydumper` 的現代化替代品。

### 主要特性

| 特性 | 說明 |
|------|------|
| **平行匯出** | 多資料表同時並行匯出，大幅提升效率 |
| **檔案分割** | 自動將大資料表分割為多個檔案（預設 256MB） |
| **多種輸出格式** | 支援 SQL 與 CSV 格式 |
| **雲端儲存** | 原生支援 S3、GCS 直接上傳 |
| **資料表過濾** | 強大的 Table Filter 語法，精確控制匯出範圍 |
| **一致性快照** | 使用 SNAPSHOT 確保匯出資料一致性 |

### 常用指令

```bash
# 建置 Dumpling
make build_dumpling

# 基本匯出（輸出至本地目錄）
dumpling \
  --host 127.0.0.1 \
  --port 4000 \
  --user root \
  --output /tmp/export

# 匯出至 S3
dumpling \
  --host 127.0.0.1 \
  --port 4000 \
  --user root \
  --output "s3://my-bucket/export" \
  --s3.region "us-east-1"

# 匯出指定資料庫，CSV 格式
dumpling \
  --host 127.0.0.1 \
  --filter "mydb.*" \
  --filetype csv \
  --output /tmp/export
```

## TiCDC（Change Data Capture）

**TiCDC** 是 TiDB 的 Change Data Capture 服務（獨立專案 [pingcap/tiflow](https://github.com/pingcap/tiflow)），可將 TiDB 的資料變更事件即時同步至下游系統。

| 下游目標 | 說明 |
|---------|------|
| **MySQL / TiDB** | 同構或異構資料庫同步（DML + DDL） |
| **Apache Kafka** | 以 Kafka Protocol 或 Avro/Canal/Maxwell 格式輸出 |
| **Amazon S3 / GCS** | 以 CSV 或 Canal-JSON 格式輸出至物件儲存（資料湖） |
| **Confluent Cloud** | 整合 Confluent Schema Registry |
| **Pulsar** | 輸出至 Apache Pulsar |

## 雲端儲存整合

TiDB 及其工具透過統一的儲存抽象層（`br/pkg/storage/`）支援多種雲端儲存：

| 雲端平台 | SDK | 功能 |
|---------|-----|------|
| **AWS** | `github.com/aws/aws-sdk-go-v2` | S3 備份、KMS 加密、IAM 認證 |
| **Google Cloud** | `cloud.google.com/go/storage` | GCS 備份、服務帳號認證 |
| **Azure** | `github.com/Azure/azure-sdk-for-go` | Blob Storage 備份、Managed Identity 認證 |

## Prometheus 監控整合

TiDB 原生整合 Prometheus，`pkg/metrics/` 定義了完整的指標集：

| 指標分類 | 說明 |
|---------|------|
| Query 計數 / 耗時 | `tidb_server_query_total`、`tidb_server_query_duration_seconds` |
| 連線數 | `tidb_server_connections` |
| 交易耗時 | `tidb_session_transaction_duration_seconds` |
| TiKV 退避重試 | `tidb_tikvclient_backoff_seconds` |
| 分散式 SQL | `tidb_distsql_handle_query_duration_seconds` |

官方提供預建的 Grafana Dashboard，可直接匯入 Grafana 使用。

## Kubernetes 部署

### TiDB Operator

[TiDB Operator](https://github.com/pingcap/tidb-operator) 是 TiDB 的 Kubernetes Operator，提供：

- **自動化部署**：透過 TidbCluster CRD 宣告式定義整個叢集
- **滾動升級**：零停機升級 TiDB、TiKV、PD
- **自動擴縮容**：支援水平擴縮容 TiDB Server 與 TiKV
- **備份排程**：整合 BR 實現定期備份（BackupSchedule CRD）
- **故障自動修復**：節點故障時自動重調度副本

```yaml
# TidbCluster 宣告式定義範例
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: my-tidb
spec:
  version: v8.5.0
  pd:
    replicas: 3
  tidb:
    replicas: 2
  tikv:
    replicas: 3
```

### TiDB Cloud

[TiDB Cloud](https://tidbcloud.com/) 為全託管 DBaaS 服務，支援 AWS 與 GCP，提供 Serverless 與 Dedicated 兩種部署模式。
