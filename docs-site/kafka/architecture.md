---
layout: doc
---

# Apache Kafka — 系統架構

::: tip 分析版本
本文件基於 commit [`7b8549f3`](https://github.com/apache/kafka/commit/7b8549f3c4cc26fd2153ef024c2fb743cfe83461) 進行分析。
:::

::: info 相關章節
- 專案簡介與總覽請參閱 [專案總覽](./index)
- Producer/Consumer API 與交易機制請參閱 [核心功能分析](./core-features)
- 各模組原始碼深度解析請參閱 [核心模組深度解析](./modules)
- Kafka Connect 與外部系統整合請參閱 [外部整合](./integration)
:::

## 專案目錄結構

Kafka 採用 Gradle Multi-Project 建置，根目錄下每個子目錄對應一個獨立模組：

| 目錄 / 模組 | 語言 | 說明 |
|------------|------|------|
| `core/` | Scala | Kafka Broker 核心實作（KafkaBroker、ReplicaManager、LogManager） |
| `clients/` | Java | 官方用戶端程式庫（Producer、Consumer、AdminClient） |
| `streams/` | Java | Kafka Streams DSL 與 Processor API |
| `connect/` | Java | Kafka Connect 資料整合框架（含多個子模組） |
| `raft/` | Java | KRaft（Kafka Raft）協定實作 |
| `metadata/` | Java | 叢集元資料管理（KRaft Metadata Log） |
| `storage/` | Java | 統一儲存層抽象 |
| `server/` | Java | 伺服器端共用邏輯 |
| `server-common/` | Java | Broker 與 Controller 共用程式碼 |
| `coordinator-common/` | Java | 協調器共用抽象 |
| `group-coordinator/` | Java | Consumer Group 協調器 |
| `transaction-coordinator/` | Java | 事務協調器 |
| `share-coordinator/` | Java | Share Group 協調器（KIP-932） |
| `tools/` | Java/Scala | 管理命令列工具 |
| `shell/` | Java | Kafka Shell 框架 |
| `generator/` | Java | RPC 訊息程式碼自動生成器 |
| `trogdor/` | Java | 分散式測試與壓力測試框架 |
| `jmh-benchmarks/` | Java | JMH 微基準測試套件 |
| `config/` | 設定 | Broker、Producer、Consumer 等設定檔範例 |
| `bin/` | Shell | 管理腳本（kafka-topics.sh、kafka-server-start.sh 等） |

## KRaft 模式架構

### ZooKeeper 移除歷程

| 版本 | 里程碑 |
|------|--------|
| 2.8 | KRaft 模式以早期存取（EA）形式引入 |
| 3.3 | KRaft 模式正式 GA（生產就緒） |
| 3.7 | ZooKeeper 模式標記為 Deprecated |
| 4.0 | ZooKeeper 模式完全移除，KRaft 成為唯一選項 |

### KRaft 叢集拓撲

![KRaft 叢集拓撲](/diagrams/kafka/kafka-architecture-1.png)

::: tip Controller 與 Broker 合設
在 KRaft 模式下，Controller 與 Broker 可以合設於同一程序（`process.roles=broker,controller`），也可以分離部署（`process.roles=controller` 或 `process.roles=broker`）。生產環境建議分離部署以提高隔離性。
:::

## Broker 內部架構

### 請求處理流程

![Broker 請求處理流程](/diagrams/kafka/kafka-architecture-2.png)

### 主要 Scala 元件（`core/src/main/scala/kafka/`）

| 元件 | 說明 |
|------|------|
| `KafkaBroker` | Broker 主程序，負責啟動所有子系統 |
| `KafkaApis` | 所有 Kafka 協定請求的處理分派層 |
| `ReplicaManager` | 管理本地 Partition 副本、處理 Leader 選舉與 ISR 維護 |
| `LogManager` | 管理所有 Topic Partition 的本地 Log 儲存（含 Log Segment 輪轉） |
| `Partition` | 單一 Partition 的副本狀態機（Leader 寫入、Follower 複製） |
| `KafkaController` | （已移至 `raft/` 與 `metadata/`）叢集控制器邏輯 |
| `GroupCoordinator` | Consumer Group 協調（已移至 `group-coordinator/`） |
| `TransactionCoordinator` | 事務協調（已移至 `transaction-coordinator/`） |

## Log 儲存機制

### Topic Partition Log 結構

每個 Topic Partition 在磁碟上對應一個目錄（`<topic>-<partition>/`），目錄內包含：

```
/kafka-logs/
  my-topic-0/
    00000000000000000000.log        # 訊息資料 (Log Segment)
    00000000000000000000.index      # Offset 索引（稀疏）
    00000000000000000000.timeindex  # 時間戳索引
    00000000000000100000.log        # 下一個 Segment（輪轉後）
    00000000000000100000.index
    leader-epoch-checkpoint         # Leader Epoch 記錄
```

### Log Segment 管理

| 參數 | 說明 |
|------|------|
| `log.segment.bytes` | 單個 Segment 最大大小（預設 1GB），超過後輪轉新 Segment |
| `log.roll.ms` | 按時間輪轉 Segment 的間隔 |
| `log.retention.bytes` | Log 保留的最大總大小 |
| `log.retention.ms` | Log 保留時間（預設 7 天） |
| `log.cleanup.policy` | 清理策略：`delete`（刪除過期）或 `compact`（保留最新 key） |

### Log Compaction

Log Compaction 保留每個 Key 最新的訊息版本，常用於狀態儲存：

![Log Compaction 示意](/diagrams/kafka/kafka-architecture-3.png)

## 副本複製協定

### ISR（In-Sync Replicas）機制

![ISR 副本複製協定](/diagrams/kafka/kafka-architecture-4.png)

| 概念 | 說明 |
|------|------|
| **ISR（In-Sync Replicas）** | 與 Leader Log 進度在 `replica.lag.time.max.ms` 內同步的副本集合 |
| **High Watermark（HW）** | 所有 ISR 成員都已寫入的最大 Offset，Consumer 只能讀到此位置 |
| **Log End Offset（LEO）** | 該副本 Log 最後一條訊息的下一個 Offset |
| **Leader Epoch** | 每次 Leader 切換遞增的版本號，用於處理副本不一致情況 |

## 網路協定層

### Kafka 二進位協定

Kafka 使用自訂的二進位協定（TCP），每個請求結構：

```
Request Header:
  api_key (INT16)        - API 類型（如 Produce=0, Fetch=1）
  api_version (INT16)    - API 版本（支援版本協商）
  correlation_id (INT32) - 請求關聯 ID
  client_id (STRING)     - 用戶端標識

Request Body:
  （依 api_key 不同而異）
```

目前支援超過 **60 種** API（Request Types），從 Produce/Fetch 到元資料管理，均使用同一套二進位協定框架。協定版本協商允許用戶端與 Broker 之間向後相容。

### 網路執行緒模型

| 元件 | 說明 |
|------|------|
| `Acceptor` | 單一執行緒，負責接受新 TCP 連線 |
| `Processor`（N 個） | 每個 Listener 有多個 Processor 執行緒，負責讀取/寫入 Socket |
| `KafkaRequestHandlerPool` | M 個 Handler 執行緒，從 RequestQueue 取出請求並實際處理 |
| 參數：`num.network.threads` | 控制 Processor 執行緒數（預設 3） |
| 參數：`num.io.threads` | 控制 Handler 執行緒數（預設 8） |
