---
layout: doc
title: Kafka — 學習路徑：小蔡的事件驅動之旅
---

# 小蔡的事件驅動之旅

> 這是一個後端工程師從 API 耦合地獄，一步步走進 Kafka 世界的故事。

---

## 第 1 章：「為什麼我的訂單系統要管庫存的事？」

那是一個週五下午四點半。

小蔡盯著監控面板，看著訂單服務的錯誤率從 0% 緩緩爬升到 12%。他快速翻出 log，發現問題：`InventoryServiceUnavailableException`——庫存服務的資料庫在做例行維護，掛了五分鐘，然後訂單系統也跟著炸了。

*這他媽的是我的問題嗎？* 小蔡心裡嘀咕著，但他知道答案是「是的」。

訂單建立流程長這樣：

```
客戶下單
  → 訂單服務呼叫 /api/inventory/reserve（扣庫存）
  → 庫存服務回 200 OK
  → 訂單服務寫資料庫
  → 訂單服務呼叫 /api/notification/send（發通知）
  → 通知服務回 200 OK
  → 回傳「訂單建立成功」給客戶
```

每一步都是同步 HTTP 呼叫。任何一個服務一掉，整條鏈就斷。而且每次新增功能，比如「物流系統也要知道新訂單」，就要修改訂單服務的程式碼、加一個新的 HTTP 呼叫、測試整條鏈。

架構師阿龍在週會上說了一句話，讓小蔡記到現在：

> 「訂單服務應該只負責『訂單被建立了』這件事，其他系統要自己決定要不要關心這件事。」

*事件驅動。* 小蔡想起了這個詞。他以前在文章裡看過，但從沒真正理解為什麼要這樣設計，直到現在。

Kafka 的核心概念其實很簡單：

1. 訂單服務建立訂單後，往 Kafka 發一個事件：「`order.created`，訂單 ID 是 123，金額是 500 元」
2. 庫存服務「訂閱」這個事件，收到後自己去扣庫存
3. 通知服務「訂閱」這個事件，收到後自己去發簡訊
4. 物流系統想加入？自己去訂閱，不用改訂單服務一行程式碼

訂單服務不再關心下游。它只是「通知世界」，世界自己決定要怎麼反應。

*這就是解耦。* 小蔡第一次真正理解這個詞的意義。

---

> ### 📚 去這裡深入了解
> - [專案總覽](/kafka/) — 了解 Kafka 的設計哲學與整體架構定位
> - [系統架構](/kafka/architecture) — 從 Broker 角色看 Kafka 怎麼儲存和傳遞事件
>
> 讀完後，你應該能說出 Kafka 和傳統訊息佇列（如 RabbitMQ）的關鍵差異，以及為什麼 Kafka 能作為「事件日誌」而非只是「訊息中繼站」。

---

## 第 2 章：「訊息放在哪裡？Topic 和 Partition 的設計」

阿龍給小蔡看了 Kafka 的基本結構圖，然後說：「你先搞懂 Topic 和 Partition，其他的都好談。」

小蔡打開文件，第一個概念是 **Topic**。

Topic 就像資料庫的「表格」，但只能追加（append-only）。你可以把所有訂單建立事件都丟到 `order.created` 這個 Topic，把所有庫存異動事件丟到 `inventory.updated`。

*好理解，繼續。*

接下來是 **Partition**。一個 Topic 可以分成多個 Partition，每個 Partition 是一個獨立的有序 log 檔案。

小蔡畫了一張草圖：

```
Topic: order.created（4 個 Partition）

Partition 0: [msg0] [msg3] [msg6] ...
Partition 1: [msg1] [msg4] [msg7] ...
Partition 2: [msg2] [msg5] [msg8] ...
Partition 3: ...
```

訊息會被分配到哪個 Partition？由 **Partitioner** 決定。預設策略是對訊息的 Key 做 hash，相同 Key 的訊息永遠落在同一個 Partition，保證**同一個 Key 的訊息是有序的**。

*所以如果我用訂單 ID 當 Key，同一張訂單的所有事件都會在同一個 Partition？* 對，小蔡猜對了。

Partition 帶來的好處是**水平擴展**：
- 不同 Partition 可以存在不同的 Broker（伺服器）上
- 消費者可以並行讀取不同 Partition，吞吐量線性提升

但也有代價：**全域順序不保證**。`order.created` Topic 裡，你只能保證單一 Partition 內的訊息有序，不同 Partition 之間沒有順序關係。

另一個重要概念是 **Offset**。每個 Partition 裡的每則訊息都有一個單調遞增的編號，叫做 Offset。消費者透過 Offset 記住「我讀到哪裡了」，下次接著讀。

*這和資料庫的 auto-increment ID 有點像，但是是 per-Partition 的。* 小蔡在筆記本上寫下這句話。

---

> ### 📚 去這裡深入了解
> - [系統架構](/kafka/architecture) — Log 儲存機制、Partition 副本（Replica）與 Leader/Follower 設計
> - [核心功能](/kafka/core-features) — 分區分配策略的原始碼細節
>
> 讀完後，你應該能解釋為什麼增加 Partition 數量可以提升吞吐量，以及 Replica 機制如何保證資料不因單一 Broker 故障而遺失。

---

## 第 3 章：「把訊息丟進去：寫第一個 Producer」

「好，理論夠了，你寫個 Producer 試試。」阿龍說。

小蔡打開 IDE，引入 Kafka clients 依賴，開始寫：

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer",
    "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer",
    "org.apache.kafka.common.serialization.StringSerializer");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

ProducerRecord<String, String> record = new ProducerRecord<>(
    "order.created",   // Topic
    "order-123",       // Key（訂單 ID）
    "{\"orderId\":123, \"amount\":500}"  // Value（JSON）
);

producer.send(record);
producer.close();
```

*這比我想像的簡單。* 但小蔡知道「寫得出來」和「寫得好」是兩回事。

**批次（Batching）**

Kafka Producer 不是每呼叫一次 `send()` 就立刻發一個網路請求。它會在內部緩衝訊息，累積到一定大小（`batch.size`，預設 16KB）或等待一段時間（`linger.ms`，預設 0ms）後，再一次打包發送。

*這就是為什麼 Kafka 吞吐量高，但 linger.ms=0 的時候延遲最低。*

**壓縮（Compression）**

```java
props.put("compression.type", "snappy");
```

一行設定，Producer 會在 batch 層級壓縮訊息。對於重複結構的 JSON，snappy 可以壓到原始大小的 20-40%，網路頻寬省非常多。

**acks 設定**

```java
props.put("acks", "all");
```

`acks=all` 表示 Leader Partition 和所有 In-Sync Replica（ISR）都確認收到後，才算發送成功。這是最高的耐久性保證，代價是略高的延遲。

小蔡在測試環境把訂單建立的 HTTP 呼叫替換成 Kafka `send()`，跑了幾百筆測試訂單。Kafka Dashboard 上，`order.created` Topic 的訊息計數開始往上跳。

*它真的在運作了。* 這種感覺有點奇怪——訂單服務不再關心下游發生什麼事，它只是「喊了一聲」，然後繼續下一個任務。

---

> ### 📚 去這裡深入了解
> - [核心功能](/kafka/core-features) — Producer API 設計、訊息格式、batch 機制的原始碼分析
> - [核心模組深度解析](/kafka/modules) — clients 模組的 RecordAccumulator 和 Sender 執行緒架構
>
> 讀完後，你應該能說明 Producer 的 `send()` 從呼叫到訊息抵達 Broker 中間經過哪些步驟，以及如何透過 `acks`、`retries`、`linger.ms` 組合來平衡延遲、吞吐量和可靠性。

---

## 第 4 章：「讀出來：Consumer 和 Consumer Group」

Producer 搞定了，接下來小蔡要讓庫存服務「消費」這些訊息。

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("group.id", "inventory-service");
props.put("key.deserializer",
    "org.apache.kafka.common.serialization.StringDeserializer");
props.put("value.deserializer",
    "org.apache.kafka.common.serialization.StringDeserializer");

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Collections.singletonList("order.created"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        System.out.printf("Offset: %d, Key: %s, Value: %s%n",
            record.offset(), record.key(), record.value());
        // 處理庫存扣減邏輯...
    }
}
```

跑起來後，`order.created` 裡積累的訊息開始被一條條讀出來。

**Consumer Group 是什麼？**

注意到 `group.id = "inventory-service"` 了嗎？這就是 Consumer Group ID。

當多個 Consumer 使用相同的 `group.id` 時，Kafka 會自動把 Partition 分配給這些 Consumer——每個 Partition 在同一個 Group 內**只會被一個 Consumer 讀取**。

小蔡的 `order.created` 有 4 個 Partition，他啟動了 3 個庫存服務實例：

```
Partition 0 → 庫存服務 A
Partition 1 → 庫存服務 B
Partition 2 → 庫存服務 C
Partition 3 → 庫存服務 A（A 多分到一個）
```

這就是 Kafka 的**並行消費**機制。Consumer 數量不超過 Partition 數量時，增加 Consumer 可以線性提升處理速度。

**Offset 怎麼管理？**

每次 `poll()` 回來處理完後，Consumer 需要「提交 Offset」告訴 Kafka：「我已經處理到這個位置了。」下次服務重啟，就從這個位置繼續，不會重讀舊訊息（也不會漏掉未讀訊息）。

預設是 `enable.auto.commit=true`，每隔 5 秒自動提交。但小蔡翻了一下文件後，把它改成手動提交：

```java
consumer.commitSync();
```

*因為如果 poll 完還沒處理完就自動提交了，服務這時候掛掉，那些訊息就永遠不會被處理了。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/kafka/core-features) — Consumer API、Offset 提交機制、Fetch 請求設計
> - [核心模組深度解析](/kafka/modules) — clients 模組的 ConsumerCoordinator 和 Fetcher 架構
>
> 讀完後，你應該能解釋 `auto.offset.reset`（`earliest` vs `latest`）的差異，以及手動提交 Offset 的時機選擇如何影響訊息處理的可靠性。

---

## 第 5 章：「服務掛了：Rebalance 的黑暗面」

上線第三天，小蔡接到告警：庫存服務 B 的 Pod 因為 OOM 被 Kubernetes 殺掉了。

他觀察了一下日誌，發現 Kafka 自動把 B 原來負責的 Partition 重新分配給 A 和 C——這個過程叫做 **Rebalance**。聽起來很美好，但實際情況讓小蔡皺眉頭：

**Rebalance 期間，整個 Consumer Group 停止消費。**

從 B 掛掉開始，Kafka 需要等待 `session.timeout.ms`（預設 45 秒）才確認 B 真的死了，然後開始 Rebalance，重新分配 Partition，這個過程又要幾秒鐘。這段時間，A 和 C 什麼訊息都讀不到。

*45 秒的空窗期，在高流量場景下，這是很長的時間。*

更麻煩的是 **Stop-the-World Rebalance**（舊版行為）：Rebalance 期間，所有 Consumer 的現有 Partition 分配全部撤銷，重新從零分配。即使你的 Consumer 好好的，它也要放下手邊的工作，等 Rebalance 完成再重新領取 Partition。

**Kafka 怎麼解決這個問題？**

Kafka 2.4+ 引入了 **Cooperative Rebalance**（透過 `CooperativeStickyAssignor`）。新版策略下：

- Rebalance 只撤銷「需要移動」的 Partition 分配
- 沒有受影響的 Consumer 可以繼續消費
- 整個過程分兩輪進行，影響範圍最小化

小蔡把 Consumer 的 `partition.assignment.strategy` 改成 `CooperativeStickyAssignor`，再加上適當調低 `heartbeat.interval.ms`（讓 Kafka 更快偵測到 Consumer 離線），情況好多了。

另一個技巧是調低 `session.timeout.ms`，但這個值不能低於 3 倍的 `heartbeat.interval.ms`，否則正常的 Consumer 可能因為網路抖動被誤判死亡，反而觸發更多不必要的 Rebalance。

*分散式系統裡沒有免費的午餐。每個參數背後都是一個取捨。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/kafka/core-features) — Consumer Group 協調機制與 Rebalance 協議
> - [核心模組深度解析](/kafka/modules) — clients 模組的 ConsumerCoordinator 如何處理 Group 成員變動
>
> 讀完後，你應該能說明 Eager Rebalance 和 Cooperative Rebalance 的協議差異，以及 `session.timeout.ms`、`heartbeat.interval.ms`、`max.poll.interval.ms` 三個參數各自管控什麼。

---

## 第 6 章：「重複了還是漏掉了？Exactly-Once 的真相」

小蔡在日誌裡發現一個異常：同一筆訂單的庫存被扣了兩次。

追查後發現：庫存服務 A 處理了 Partition 0 的第 47 筆訊息，扣庫存成功，但在呼叫 `commitSync()` 之前 Pod 重啟了。重啟後，A 從上次提交的 Offset（第 46 筆）重新開始，第 47 筆訊息被重新消費，庫存又扣了一次。

這就是 **At-Least-Once**——訊息至少被處理一次，但可能多次。

**三種語義**

| 語義 | 說明 | 代價 |
|------|------|------|
| At-Most-Once | 最多一次，可能漏掉 | 最低延遲 |
| At-Least-Once | 至少一次，可能重複 | 預設行為 |
| Exactly-Once | 恰好一次，不漏不重複 | 最高代價 |

**在消費端實現 Idempotency（冪等性）**

最務實的做法：讓消費端的「處理邏輯」是冪等的。對同一筆訊息執行兩次，結果和執行一次一樣。

```java
// 改成 UPSERT，而非直接扣減
UPDATE inventory SET reserved = reserved - :qty
WHERE order_id = :orderId AND reserved >= :qty
```

加上「已處理訊息 ID」的去重表，重複的訊息直接略過。

**Kafka 的 Exactly-Once**

如果你需要端到端的 Exactly-Once（從 Producer 到 Consumer），Kafka 提供了 **Idempotent Producer** 和 **Transactional API**：

```java
// Idempotent Producer：重試不會產生重複訊息
props.put("enable.idempotence", "true");

// Transactional Producer：原子性寫入多個 Partition
props.put("transactional.id", "order-service-tx-1");
producer.initTransactions();
producer.beginTransaction();
producer.send(record1);
producer.send(record2);
producer.commitTransaction();  // 兩條訊息同時可見，或同時回滾
```

*但 Exactly-Once 不是免費的。* 它需要 Broker 端維護更多狀態，Producer 和 Broker 之間有額外的協調開銷，整體吞吐量會下降約 20%。

小蔡最後選擇了「Idempotent Producer + 消費端去重」的組合，而不是全鏈路 Exactly-Once。*大多數情況下，設計良好的 At-Least-Once + Idempotent Consumer 就足夠了。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/kafka/core-features) — Idempotent Producer、Transaction API、Exactly-Once 實作細節
> - [核心模組深度解析](/kafka/modules) — core 模組的 TransactionCoordinator 設計
>
> 讀完後，你應該能解釋 Kafka Transaction 的「Two-Phase Commit」機制，以及 `isolation.level`（`read_committed` vs `read_uncommitted`）如何影響 Consumer 看到的訊息。

---

## 第 7 章：「不寫程式碼的整合：Kafka Connect 和 CDC」

需求來了：行銷部門想要把訂單資料同步到 Elasticsearch，方便搜尋和分析。資料科學團隊想要把訂單資料放進 S3，做歷史分析。

*如果每個整合都要自己寫 Producer/Consumer，這會沒完沒了。*

阿龍說：「Kafka Connect。」

**Kafka Connect 是什麼？**

Kafka Connect 是 Kafka 生態系內建的整合框架，提供兩種 Connector：

- **Source Connector**：從外部系統讀資料，寫進 Kafka Topic
- **Sink Connector**：從 Kafka Topic 讀資料，寫進外部系統

小蔡要把訂單資料推到 Elasticsearch，只需要在 Kafka Connect 上設定一個 Elasticsearch Sink Connector：

```json
{
  "name": "elasticsearch-orders-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "3",
    "topics": "order.created",
    "connection.url": "http://elasticsearch:9200",
    "key.ignore": "false",
    "schema.ignore": "true"
  }
}
```

一個 HTTP POST 請求發出去，訂單資料開始流進 Elasticsearch。不需要寫任何 Consumer 程式碼。

**CDC：直接讀資料庫的異動**

更強大的場景是 **CDC（Change Data Capture）**：透過讀取 MySQL 的 binlog 或 PostgreSQL 的 WAL，把每一筆資料庫異動（INSERT/UPDATE/DELETE）都轉成 Kafka 事件。

Debezium 是最主流的 CDC Source Connector。設定好之後，資料庫的每一筆異動都會自動出現在對應的 Kafka Topic 裡，不需要修改任何應用程式程式碼。

*這意味著即使是不支援事件驅動的舊系統，只要接上 Debezium，也可以成為事件來源。*

小蔡花了兩個小時設定好 Debezium + Elasticsearch Sink，原本需要一週開發的整合需求就這樣搞定了。他心裡有種複雜的感覺：*我是不是之前做了太多不必要的工作？*

---

> ### 📚 去這裡深入了解
> - [外部整合](/kafka/integration) — Kafka Connect 架構、Connector 生命週期、Distributed Mode vs Standalone Mode
> - [核心模組深度解析](/kafka/modules) — connect 模組的 Worker、Task、Connector 設計
>
> 讀完後，你應該能說明 Kafka Connect 的 Distributed Mode 如何在多個 Worker 之間分配 Task，以及 Source Connector 如何保證資料不遺失（Source Offset 管理）。

---

## 第 8 章：「ZooKeeper 去哪了？KRaft 的故事」

某天小蔡在設定測試環境時，注意到一件事：最新版的 Kafka 文件裡，幾乎找不到 ZooKeeper 的設定說明了。

他去問阿龍。

「KRaft 模式，Kafka 3.3+ 預設啟用，Kafka 4.0 之後完全移除 ZooKeeper 支援。」阿龍說，「你現在跑的環境就是 KRaft。」

*原來我一直在用 KRaft 但完全不知道。*

**為什麼要移除 ZooKeeper？**

傳統 Kafka 架構下，ZooKeeper 負責儲存 Cluster 元資料（Broker 列表、Topic 設定、Partition Leader 選舉等），這帶來幾個問題：

1. **兩套系統**：部署 Kafka 必須同時部署和維運 ZooKeeper，運維複雜度翻倍
2. **元資料同步延遲**：Broker 從 ZooKeeper 同步元資料有延遲，大型叢集啟動時間很長
3. **擴展瓶頸**：ZooKeeper 的設計不適合儲存大量元資料，限制了 Kafka 的 Topic/Partition 規模

**KRaft 怎麼運作？**

KRaft 把 Cluster 元資料管理移到 Kafka 自己內部，用 Raft 共識協議維護一個「元資料日誌」。

架構上分成兩種角色：
- **Controller**：負責元資料管理（Leader 選舉、Topic 建立等），組成 Raft Quorum
- **Broker**：負責儲存和轉發訊息

在小型叢集中，同一個節點可以同時擔任 Controller 和 Broker（`process.roles=broker,controller`）。

```
# server.properties（KRaft 模式）
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
```

*沒有 ZooKeeper 位址了。Kafka 自己管自己。*

KRaft 的另一個好處是元資料變更的傳播速度大幅提升：所有 Broker 都訂閱元資料日誌，Controller 的決策幾乎即時同步到全叢集，不再需要 Broker 去輪詢 ZooKeeper。

---

> ### 📚 去這裡深入了解
> - [系統架構](/kafka/architecture) — KRaft 叢集拓撲、Controller 選舉、元資料日誌（`__cluster_metadata` Topic）
> - [核心模組深度解析](/kafka/modules) — raft 模組的 KafkaRaftClient 與 metadata 模組的 MetadataImage
>
> 讀完後，你應該能說明 KRaft Controller 的 Active-Standby 選舉流程，以及 Broker 如何從 `__cluster_metadata` Topic 訂閱元資料變更（MetadataFollower 設計）。

---

## 第 9 章：「在 Kafka 裡計算：Kafka Streams 入門」

訂單系統穩定一個月後，PM 提了新需求：「我想在 Dashboard 上看到每個商品類別最近一小時的訂單總金額，即時更新的那種。」

小蔡的第一個反應是：*寫一個 Consumer 讀 `order.created`，維護一個 in-memory 的計數器，定期寫到 Redis...* 但這個設計有很多邊緣問題：服務重啟計數器歸零、多個實例之間狀態不一致...

阿龍說：「Kafka Streams。」

**Kafka Streams 是什麼？**

Kafka Streams 是一個 Java 程式庫，讓你直接在應用程式的 JVM 中做串流計算，不需要獨立的計算叢集（不需要 Spark、Flink）。它的狀態儲存在 Kafka 自己的 Topic 裡，天然具備容錯性。

小蔡的需求：按商品類別分組，計算最近一小時的訂單金額總和。

```java
StreamsBuilder builder = new StreamsBuilder();

KStream<String, Order> orders = builder.stream("order.created");

KTable<Windowed<String>, Long> hourlySales = orders
    .groupBy((key, order) -> order.getCategory())
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(1)))
    .aggregate(
        () -> 0L,
        (category, order, total) -> total + order.getAmount(),
        Materialized.as("hourly-sales-store")
    );

hourlySales.toStream().to("hourly-sales-by-category");
```

程式碼看起來像 Java Stream API，但它是連續運行的：每來一筆新訂單，計算結果即時更新。

**狀態怎麼管理？**

`Materialized.as("hourly-sales-store")` 建立了一個 **State Store**，底層是 RocksDB。Kafka Streams 會自動把 State Store 的異動寫到一個 changelog Topic（`hourly-sales-store-changelog`）。如果服務重啟，State Store 從 changelog Topic 重建，計算結果不會遺失。

*這就解決了 in-memory 計數器的問題。狀態活在 Kafka 裡，服務是 stateless 的。*

當多個 Kafka Streams 實例跑同一個 Application（相同 `application.id`），Partition 會分配給不同實例，狀態也跟著分開——和 Consumer Group 的邏輯類似，但 Kafka Streams 自動幫你處理好了。

---

> ### 📚 去這裡深入了解
> - [核心功能](/kafka/core-features) — Kafka Streams 的 DSL 與 Processor API
> - [核心模組深度解析](/kafka/modules) — streams 模組的 StreamThread、Task、StateStore 架構
>
> 讀完後，你應該能說明 KTable 和 KStream 的語義差異（事件流 vs 變更日誌），以及 Windowed Aggregation 如何在有限記憶體內維護時間窗口狀態。

---

## 第 10 章：「要快還是要穩？效能調優的取捨藝術」

系統跑了三個月，業績衝上去了，每秒訂單量從 200 筆漲到 2000 筆。監控告警：`order.created` Topic 的消費延遲開始攀升。

小蔡拉出 Kafka 的指標，開始做效能調優。這是他學到的幾個關鍵取捨：

**Producer 側：吞吐量 vs 延遲**

```properties
# 高吞吐量設定
linger.ms=20              # 等 20ms 收集更多訊息再打包發送
batch.size=65536          # 批次大小調大到 64KB
compression.type=lz4      # 壓縮（CPU 換網路頻寬）
acks=1                    # 只等 Leader 確認（犧牲部分耐久性）

# 低延遲設定
linger.ms=0               # 立即發送，不等待
batch.size=16384          # 預設值
acks=all                  # 最高耐久性（延遲較高）
```

*大多數電商場景是「高吞吐量優先，毫秒級延遲不是硬需求」，選高吞吐量設定。*

**Consumer 側：並行度**

Consumer 數量要和 Partition 數量匹配。如果 Consumer 數量超過 Partition 數量，多出來的 Consumer 閒置。

小蔡把 `order.created` 的 Partition 數量從 4 增加到 12，同時把庫存服務的 Pod 數量從 3 增加到 9，消費延遲立即下降。

**Broker 側：磁碟 I/O**

Kafka 的寫入效能高度依賴 OS 的 Page Cache。把 Kafka 的 log 目錄放在 NVMe SSD 上，並且確保 JVM Heap 不要太大（留更多記憶體給 Page Cache）。

```properties
log.dirs=/data/kafka-logs  # 確保在 SSD 上
```

**訊息保留策略**

```properties
log.retention.hours=168    # 保留 7 天（預設）
log.retention.bytes=107374182400  # 或者限制 100GB
```

保留時間越長，磁碟用量越多，但下游服務可以重新消費更久的歷史訊息。小蔡把它設為 7 天，足夠任何服務在故障後重新追補。

---

消費延遲降下來了。小蔡在 Slack 上看到 PM 傳來「Dashboard 很順！」的訊息，嘴角微微上揚。

*三個月前，他還不知道 Topic 是什麼。*

Kafka 不是萬能的——它不適合需要低延遲查詢的場景（那是資料庫的工作），也不適合訊息量很少但需要複雜路由邏輯的場景（那是 RabbitMQ 更擅長的地方）。但對於「高吞吐量、跨服務資料流、需要重播歷史事件」的場景，它幾乎是無可取代的選擇。

*小蔡合上筆電，準備下班。訂單還在流，Kafka 還在跑。*

---

> ### 📚 去這裡深入了解
> - [系統架構](/kafka/architecture) — Broker 的 Log 儲存機制、Page Cache 利用策略
> - [核心功能](/kafka/core-features) — Producer 配置參數的完整說明
> - [核心模組深度解析](/kafka/modules) — storage 模組的 UnifiedLog 和 LogSegment 設計
>
> 讀完後，你應該能設計一個針對特定場景（高吞吐 or 低延遲）的 Kafka Producer/Consumer 配置，並說明每個參數調整背後的原理與代價。

---

## 結語

小蔡的旅程還沒結束——Kafka 的世界很深，還有 Schema Registry、MirrorMaker 2 跨資料中心複製、Tiered Storage 冷熱分層等等主題等著探索。

但最重要的事情，他已經學會了：

> **Kafka 不是訊息佇列，它是事件日誌。訂閱它的人決定要對事件做什麼，發布它的人只管忠實記錄發生了什麼。**

這個思維的轉變，比任何一個 API 都重要。

---

::: info 繼續探索
- [回到學習路徑首頁](./index) — 查看所有章節地圖
- [系統架構](/kafka/architecture) — 深入 KRaft 與 Broker 內部設計
- [核心功能](/kafka/core-features) — Producer/Consumer/Transaction 原始碼分析
- [外部整合](/kafka/integration) — Kafka Connect、MirrorMaker 2 完整說明
:::
