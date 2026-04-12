---
layout: doc
---

# Apache Kafka — 核心模組深度解析

::: tip 分析版本
本文件基於 commit [`7b8549f3`](https://github.com/apache/kafka/commit/7b8549f3c4cc26fd2153ef024c2fb743cfe83461) 進行分析。
:::

::: info 相關章節
- 專案簡介與總覽請參閱 [專案總覽](./index)
- 叢集架構與儲存機制請參閱 [系統架構](./architecture)
- Producer/Consumer API 與交易機制請參閱 [核心功能分析](./core-features)
- Kafka Connect 與外部系統整合請參閱 [外部整合](./integration)
:::

## `core` 模組（Scala）

`core/` 是 Kafka Broker 的核心實作，以 **Scala** 編寫，包含所有伺服器端邏輯。

### 主要元件

| 套件 / 類別 | 說明 |
|------------|------|
| `kafka.server.KafkaBroker` | Broker 主程序，啟動所有子系統的生命週期管理 |
| `kafka.server.KafkaApis` | 所有 Kafka 協定請求（60+ 種）的處理分派層 |
| `kafka.server.ReplicaManager` | 管理本地 Partition 副本，處理 Leader/Follower 讀寫 |
| `kafka.log.LogManager` | 管理所有 Topic Partition 的本地磁碟 Log |
| `kafka.log.UnifiedLog` | 單一 Partition Log 的讀寫操作封裝 |
| `kafka.log.LogSegment` | Log Segment 讀寫（含 .log、.index、.timeindex） |
| `kafka.log.LogCleaner` | Log Compaction 後台執行緒 |
| `kafka.network.SocketServer` | TCP 網路層，管理 Acceptor 與 Processor 執行緒 |
| `kafka.network.RequestChannel` | Processor 與 Handler 之間的請求/回應通道 |
| `kafka.admin.AdminManager` | Topic 建立/刪除、Partition 重分配等管理操作 |
| `kafka.coordinator.group.GroupCoordinator` | Consumer Group 協調器（已移至 group-coordinator 模組） |
| `kafka.coordinator.transaction.TransactionCoordinator` | 事務協調器（已移至 transaction-coordinator 模組） |

### LogManager 架構

![LogManager 架構](/diagrams/kafka/kafka-modules-logmanager-1.png)

## `clients` 模組（Java）

`clients/` 是官方 Java 用戶端程式庫，Java Release Target 設為 `11`，向後相容。

### 主要類別

| 類別 | 說明 |
|------|------|
| `KafkaProducer<K,V>` | 執行緒安全的訊息生產者，含 RecordAccumulator 與 Sender 執行緒 |
| `KafkaConsumer<K,V>` | 單一執行緒消費者（非執行緒安全），含 Fetcher 與 ConsumerCoordinator |
| `AdminClient` | 叢集管理用戶端（建立/刪除 Topic、查詢 Consumer Group 等） |
| `MockProducer<K,V>` | 單元測試用 Mock 實作 |
| `MockConsumer<K,V>` | 單元測試用 Mock 實作 |

### 序列化介面

```java
// 自訂序列化器介面
public interface Serializer<T> extends Closeable {
    byte[] serialize(String topic, T data);
    // 含 Header 的序列化（版本協商）
    default byte[] serialize(String topic, Headers headers, T data) {
        return serialize(topic, data);
    }
}
```

內建序列化器：`StringSerializer`、`IntegerSerializer`、`LongSerializer`、`ByteArraySerializer`、`ByteBufferSerializer`、`DoubleSerializer`、`UUIDSerializer`、`VoidSerializer`

### 子模組

| 子模組 | 說明 |
|--------|------|
| `clients:clients-integration-tests` | 用戶端整合測試 |

## `streams` 模組（Java）

`streams/` 是 Kafka Streams 串流處理程式庫，Java Release Target 設為 `11`。

### 核心類別層次

![Kafka Streams 核心類別層次](/diagrams/kafka/kafka-modules-streams-2.png)

### StreamsBuilder 主要 API

| API | 說明 |
|-----|------|
| `stream(topic)` | 建立 KStream（無界流） |
| `table(topic)` | 建立 KTable（變更日誌表） |
| `globalTable(topic)` | 建立 GlobalKTable（廣播給所有 Task） |
| `KStream.filter()` | 過濾訊息 |
| `KStream.map()` / `mapValues()` | 轉換訊息 |
| `KStream.flatMap()` | 一對多轉換 |
| `KStream.groupByKey()` | 按 Key 分組，返回 KGroupedStream |
| `KGroupedStream.count()` | 計數聚合 |
| `KGroupedStream.aggregate()` | 自訂聚合函數 |
| `KStream.join(KTable)` | Stream-Table Join |
| `KStream.join(KStream)` | Stream-Stream Join（需指定視窗） |
| `KTable.toStream()` | 轉換 KTable 為 KStream（changelog） |

### 子模組

| 子模組 | 說明 |
|--------|------|
| `streams:streams-scala` | Scala API 包裝（Implicit Conversions） |
| `streams:test-utils` | 測試工具（TopologyTestDriver） |
| `streams:examples` | 範例應用程式 |
| `streams:integration-tests` | 整合測試 |
| `streams:upgrade-system-tests-*` | 版本升級系統測試（從 0.11.0 到 4.1） |

## `connect` 模組（Java）

Kafka Connect 是資料整合框架，分為多個子模組：

### 子模組架構

![Connect 子模組架構](/diagrams/kafka/kafka-modules-connect-3.png)

### Connector 開發介面

```java
// Source Connector 開發介面
public abstract class SourceConnector extends Connector {
    public abstract List<Map<String, String>> taskConfigs(int maxTasks);
    public abstract Class<? extends Task> taskClass();
}

// Source Task 開發介面
public abstract class SourceTask extends Task {
    public abstract List<SourceRecord> poll() throws InterruptedException;
    public abstract void commitRecord(SourceRecord record, RecordMetadata metadata);
}

// Single Message Transform 介面
public interface Transformation<R extends ConnectRecord<R>> extends Configurable, Closeable {
    R apply(R record);
}
```

### 內建 SMT（Single Message Transforms）

| Transform | 說明 |
|-----------|------|
| `ReplaceField` | 新增、重命名或刪除欄位 |
| `MaskField` | 遮蔽欄位值（替換為 null 或預設值） |
| `ExtractField` | 從 Struct 或 Map 中提取單一欄位 |
| `InsertField` | 插入靜態欄位（如 topic、partition、offset） |
| `SetSchemaMetadata` | 設定或修改 Schema 名稱/版本 |
| `ValueToKey` | 以 Value 欄位替換 Record Key |
| `HoistField` | 將 Value 包裝於指定欄位名稱的 Struct 中 |
| `Cast` | 欄位型別轉換 |
| `TimestampConverter` | 時間戳格式轉換 |
| `Filter` | 條件過濾（配合 Predicate 使用） |
| `HeaderFrom` | 從 Header 移動值到 Key/Value |

## `raft` 模組（Java）

`raft/` 實作了 **KRaft（Kafka Raft）** 協定，取代 Apache ZooKeeper：

### 核心類別

| 類別 | 說明 |
|------|------|
| `KafkaRaftClient` | KRaft 用戶端主程序，管理選舉與 Log 複製 |
| `KafkaRaftManager` | KRaft 管理器，整合 RaftClient 與 Kafka 網路層 |
| `QuorumState` | Raft 成員狀態機（Candidate / Leader / Voted / Unattached / Observer） |
| `ReplicatedLog` | Raft Log 抽象，儲存所有 Metadata 記錄 |
| `BatchAccumulator` | 批次累積 Metadata 變更記錄 |

### Raft 狀態機

![Raft 狀態機](/diagrams/kafka/kafka-modules-raft-4.png)

## `metadata` 模組（Java）

`metadata/` 管理 KRaft 模式下的叢集元資料：

| 元素 | 說明 |
|------|------|
| **MetadataImage** | 叢集元資料的不可變快照（Broker、Topic、Partition、Config 等） |
| **MetadataPublisher** | 訂閱並消費 Metadata Log 變更事件的介面 |
| **MetadataLoader** | 從 Metadata Log 載入並重放（Replay）元資料 |
| **MetadataDelta** | 兩個 MetadataImage 之間的差異 |
| **BrokerRegistration** | Broker 節點註冊資訊（rack、endpoints、features） |

## `storage` 模組（Java）

`storage/` 提供統一儲存層抽象，目前 Tiered Storage（分層儲存）功能基於此模組實作：

| 功能 | 說明 |
|------|------|
| **Tiered Storage** | 將 Log Segment 自動 offload 至遠端儲存（S3/GCS/HDFS） |
| **RemoteLogManager** | 管理 Remote Log Segment 的上傳、查詢、刪除 |
| **RemoteStorageManager** | 遠端儲存後端的可插拔介面（Plugin SPI） |
| **RemoteLogMetadataManager** | 遠端 Log 元資料的可插拔儲存介面 |

::: tip Tiered Storage
Kafka 4.x 的 Tiered Storage 功能允許將冷資料 offload 至物件儲存（如 S3），大幅降低 Broker 本地磁碟需求，同時保持完整的訊息存取能力。
:::
