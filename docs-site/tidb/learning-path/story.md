---
layout: doc
title: TiDB — 學習路徑：阿倫的分散式資料庫之旅
---

# 📖 TiDB 學習之旅：阿倫的故事

> 跟著阿倫，從接到「評估 TiDB 是否能取代公司 MySQL 叢集」這個任務開始，一步步理解分散式資料庫的世界。
> 每個章節都是阿倫真實遭遇的技術挑戰——你會看到他怎麼查資料、怎麼測試、怎麼把拼圖一塊塊拼起來。

---

## 序章：MySQL 的天花板

星期三下午，阿倫正在緊盯著監控畫面上那條快要碰頂的折線。

訂單資料庫的寫入 QPS 又創新高了。這個 MySQL 主節點已經是公司有史以來配置最高的機器——128GB RAM、32 核心、NVMe SSD——但每到大促時間，那條 CPU 使用率曲線還是毫不留情地爬向 100%。

三年前，技術總監第一次提起「資料庫分片」的時候，阿倫還挺興奮的。他花了半年時間設計分片鍵、改寫應用程式的 DAO 層、處理跨分片的 JOIN 查詢。結果呢？應用程式碼的複雜度翻了三倍，跨分片的交易始終無法保證一致性，而且每次業務要加一個「按時間範圍查所有訂單」的報表需求，他就頭大一次——因為那需要同時掃所有分片。

「老問題，沒完沒了，」他嘆了口氣，轉開那個視窗。

這時候 Slack 的訊息跳出來。是 CTO。

「阿倫，聽說 PingCAP 的 TiDB 可以做到 MySQL 相容、無限水平擴展，而且支援分散式交易。你研究一下，下週給我一份評估報告。如果可行，Q2 我們就推動遷移。」

*MySQL 相容、水平擴展、分散式交易——這三個需求我已經碰壁很多次了，有可能同時做到嗎？*

阿倫打開 TiDB 的 GitHub 頁面，看到那行簡介：「A distributed SQL database compatible with MySQL protocol.」他沉默了幾秒。不是因為不信，而是因為這句話如果是真的，那代表過去幾年他花在 MySQL 分片上的時間……算了，先看看它怎麼做到的。

他建了一個新的筆記本，在第一頁寫下：「TiDB 評估——阿倫 Q1」。

---

> ### 📚 去這裡深入了解
>
> - [專案總覽](/tidb/) — TiDB 是什麼、解決什麼問題、與 MySQL 的相容程度
>
> 讀完後，你應該能回答：TiDB 宣稱的「MySQL 相容」是什麼程度的相容？有哪些已知的不相容點？

---

## 第一章：「計算層和儲存層，為什麼要分開？」

第一天的研究，阿倫就被 TiDB 的架構圖震撼了一下。

他習慣的 MySQL 是這樣的：一個 mysqld 進程，裡面同時負責解析 SQL、查詢優化、執行計劃、儲存資料——全部在一個地方。水平擴展的方式就是「加一個 slave 來分攤讀請求」，或者「分片，把資料硬切成幾份分到不同機器」。

TiDB 的架構完全不一樣。它把資料庫拆成了三個相互獨立的部分：

- **TiDB Server**：無狀態的計算層，只負責接收 SQL、解析、優化、生成執行計劃，然後把存取請求發到 TiKV。因為它無狀態，你可以隨時橫向加 TiDB Server 實例，不需要遷移任何資料。
- **TiKV**：有狀態的儲存層，以 Region（預設 96MB 的 key-value 區塊）為單位儲存所有資料，每個 Region 有三個副本分散在不同節點，用 Raft 保持一致性。
- **PD（Placement Driver）**：整個叢集的「大腦」，管理所有 Region 的元資料、分配 TSO（全域時間戳）、負責把熱點 Region 搬到不同節點以均衡負載。

阿倫拿起筆，在紙上畫了一個對比圖：

```
MySQL（傳統）：
  [應用] → [mysqld：SQL解析 + 儲存引擎] → [單一磁碟]

TiDB（分散式）：
  [應用] → [TiDB Server（無狀態，可多台）]
              ↓
           [PD（元資料 + 時間戳）]
              ↓
  [TiKV Node 1] [TiKV Node 2] [TiKV Node 3] ...
```

*這個設計的好處是什麼？* 阿倫想了一下。計算層無狀態意味著你可以隨需求增加 TiDB Server，不用遷移資料。儲存層用 Raft 多副本，自動容錯，不需要手動做主從切換。而且計算和儲存分開擴展——如果 CPU 是瓶頸，加 TiDB Server；如果容量是瓶頸，加 TiKV 節點。

這就是他在 MySQL 架構裡做不到的事：計算和儲存是耦合在一起的，你很難說「我只想加更多 CPU 來處理查詢，但不想搬資料」。

但阿倫也發現了一個新問題：TiDB Server 要存取分散在多個 TiKV 節點的資料，那它怎麼知道某一行資料在哪個 TiKV 上？這個問題的答案，就在 PD 的 Region Map 裡——他把這個問題記下來，準備在下一章深入研究。

---

> ### 📚 去這裡深入了解
>
> - [系統架構](/tidb/architecture) — TiDB Server、TiKV、PD、TiFlash 的職責劃分與元件互動
>
> 讀完後，你應該能解釋：一條 `SELECT` 查詢從應用程式發出，到拿到結果，中間經過了哪些元件？各自負責什麼？

---

## 第二章：「資料怎麼在多台機器上保持一致？」

研究 TiDB 的第二天，阿倫把焦點放在 TiKV 上。

他做過 MySQL 主從複製，也踩過很多坑：主從延遲、半同步複製在高負載下失效、slave 升主的時候資料可能缺幾行。這些經驗讓他對「資料複製」這件事格外謹慎。TiDB 宣稱「強一致性」，那 TiKV 底層是怎麼做到的？

答案是 **Raft**。

TiKV 把所有資料切割成 **Region**——每個 Region 是一段連續的 key 範圍，預設大小約 96MB。每個 Region 會在三個（或更多）TiKV 節點上各有一個副本，這三個副本構成一個 **Raft Group**。每個 Raft Group 選出一個 **Leader**，所有寫入請求都必須先打到 Leader。

Leader 收到寫入後，會把這筆操作記錄到 Raft Log，然後把 Log 同步給 Follower。**只有當超過半數的節點（通常是 2/3）確認已寫入 Raft Log，這筆寫入才算成功**，Leader 才會回覆客戶端。這就是 Raft 的核心：多數決（Quorum）保證了強一致性。

阿倫在筆記本上寫下和 MySQL 複製的對比：

| | MySQL 主從複製 | TiKV Raft |
|---|---|---|
| **一致性模型** | 最終一致（async）或半同步 | 強一致（多數決確認） |
| **Leader 選舉** | 手動或外部工具（MHA） | 自動選舉，秒級切換 |
| **資料範圍** | 整個資料庫 | 每個 Region 獨立選主 |
| **節點故障** | 需要手動介入 | 自動重新選主，對應用透明 |

最後一點讓阿倫眼睛一亮。TiKV 的 Region 粒度是 96MB，這意味著不同 Region 的 Leader 可以分散在不同的節點上——負載天然均衡，而且某個節點故障時，只有它上面的 Region Leader 需要重選，其他 Region 不受影響。這比 MySQL 的「整個主庫掛掉所有寫入全部暫停」要健壯得多。

*不過，* 他想，*Region 和 Region 之間的跨行交易呢？一筆訂單涉及兩張表，這兩張表的資料可能在不同的 Region 上，那要怎麼保證這兩個 Region 的修改是原子的？*

這個問題把他引向了第四章——分散式交易 2PC。但在那之前，他決定先弄清楚 PD 的角色。

---

> ### 📚 去這裡深入了解
>
> - [系統架構](/tidb/architecture) — TiKV 的 Region 模型、Raft 副本機制
>
> 讀完後，你應該能解釋：TiKV 的「強一致性」和 MySQL 的「半同步複製」在保證層面有什麼根本差異？為什麼 TiKV 的故障轉移是自動的？

---

## 第三章：「誰在幕後排程和調控？」

阿倫在筆記本上標了一個問題：「PD 到底在做什麼？它和 MySQL 裡完全沒有對應的東西。」

**PD（Placement Driver）** 是 TiDB 叢集裡看起來最不起眼、但實際上最關鍵的元件。它不處理任何用戶 SQL，也不儲存任何業務資料，但整個叢集沒有它就無法運作。

阿倫找出 PD 的三個核心職責：

**1. 元資料管理（Region Map）**

PD 維護了一張全域的 Region 地圖：每個 Region 的 key 範圍是什麼、它的 Leader 在哪個 TiKV 節點、Follower 在哪裡。TiDB Server 每次要存取資料，都先向 PD 查詢「這個 key 在哪個 TiKV 的哪個 Region 上」，拿到位置後才直接去找那個 TiKV。

**2. TSO（Timestamp Oracle）——全域時間戳服務**

這是 PD 最精妙的設計之一。TiDB 的分散式交易需要一個全域一致的時間戳來判斷「交易的先後順序」。PD 提供 TSO 服務：每次需要開始一筆交易，TiDB Server 就向 PD 申請一個 TSO（一個單調遞增的 64-bit 時間戳）。這個 TSO 同時編碼了物理時間和邏輯序號，確保即使在同一毫秒內發起的多筆交易，也有明確的先後順序。

*阿倫想了一下：* 這有點像 MySQL 的 binlog position，但 MySQL 的 binlog position 只在單機有意義，TiDB 的 TSO 是全叢集共享的全域排序——這才能讓分散式交易有意義。

**3. Region 排程——熱點均衡**

PD 持續監控每個 TiKV 節點的資料量和存取熱度。如果某個 Region 的寫入量遠高於其他 Region（熱點 Region），PD 會自動把這個 Region 的 Leader 遷移到負載較低的 TiKV 節點，或者把 Region 分裂成兩個更小的 Region，分散壓力。這就是 TiDB 宣稱「自動負載均衡」的底層機制——不需要 DBA 手動決定分片鍵，PD 會動態調整。

阿倫回想起他當年設計 MySQL 分片時的痛苦：一旦選定了分片鍵，如果某個分片的資料量或存取量遠高於其他分片（熱點分片），幾乎無法自動修復，必須手動重新分片和遷移資料。TiDB 的 Region 自動分裂和遷移，從根本上解決了這個問題。

不過阿倫注意到一個潛在風險：「如果 PD 掛掉怎麼辦？TSO 服務停了，所有新交易都無法開始。」他去查了一下，PD 本身也有三個副本，用 etcd 做 Raft 共識——高可用的設計一路貫徹到底。

---

> ### 📚 去這裡深入了解
>
> - [系統架構](/tidb/architecture) — PD 的 TSO 機制、Region 排程策略
> - [核心功能](/tidb/core-features) — 統計資訊收集與查詢優化器
>
> 讀完後，你應該能說明：TSO 為什麼對分散式交易至關重要？PD 的 Region 排程如何解決傳統分片方案的熱點問題？

---

## 第四章：「跨節點的 ACID，到底怎麼做到？」

這是阿倫認為最燒腦的一章。

他是一個對交易非常謹慎的 DBA。在 MySQL 裡，一個交易的 ACID 是 InnoDB 的 MVCC 加上 WAL 日誌實現的，所有資料都在同一個 mysqld 進程裡，保證起來相對直接。但在 TiDB 裡，一筆訂單的寫入可能涉及 `orders` 表和 `order_items` 表，這兩張表的資料可能分布在完全不同的 TiKV 節點的不同 Region 上——要保證這兩個跨節點的修改是原子的，是 TiDB 最核心的技術挑戰之一。

TiDB 的答案是 **Percolator 模型**，也就是業界熟知的 **2PC（Two-Phase Commit，兩階段提交）**。

阿倫整理出一筆訂單交易的完整流程：

**Phase 1：Prewrite（預寫）**

1. TiDB Server 向 PD 申請一個 `start_ts`（交易開始時間戳）。
2. TiDB Server 選定交易中第一個要修改的 key 作為 **Primary Key**（主鎖）。
3. 對交易中的每個要修改的 key，TiDB Server 向對應的 TiKV 節點發送 Prewrite 請求：寫入資料的暫存版本，並記錄一個鎖（Lock）指向 Primary Key。
4. 如果所有 TiKV 節點都成功回應 Prewrite，進入 Phase 2。如果任何一個失敗（例如發現 key 已被其他交易鎖住），交易回滾。

**Phase 2：Commit（提交）**

1. TiDB Server 向 PD 申請一個 `commit_ts`（提交時間戳），這個 ts 必須大於 `start_ts`。
2. 先向 Primary Key 所在的 TiKV 節點發送 Commit 請求，寫入 Primary Key 的提交記錄。一旦 Primary Key 提交成功，這筆交易從邏輯上就已經「成功」了——即使後續的 Secondary Key 的提交請求還沒發出。
3. 非同步地向所有 Secondary Key 的 TiKV 節點發送 Commit 請求，清除暫存的鎖。

*阿倫看到這裡，眼睛一亮：* 「Primary Key 提交成功就代表交易成功」——這個設計讓 Commit 階段有了一個明確的原子點。如果 TiDB Server 在發出所有 Secondary Commit 之前崩潰了，其他交易在讀到那些還有 Lock 的 Secondary Key 時，會去查 Primary Key 的狀態：如果 Primary 已提交，就幫忙清除 Secondary 的鎖（稱為 Resolve Lock）；如果 Primary 還沒提交，就認定交易失敗，回滾所有鎖。

這個機制讓整個分散式交易的原子性只依賴於 Primary Key 的提交成功與否——一個單點操作，完全由 Raft 強一致性保障。

阿倫把這個流程和他過去在 MySQL XA 交易上踩的坑對比了一下。MySQL 的 XA 交易在 prepare 階段掛掉時，需要 DBA 手動查詢並 rollback 或 commit 懸掛的交易。TiDB 的 Percolator 則透過 Primary Key 的狀態自動解決這個問題，對應用程式完全透明。

---

> ### 📚 去這裡深入了解
>
> - [核心功能](/tidb/core-features) — 2PC 分散式交易的 Percolator 模型、MVCC 版本控制
>
> 讀完後，你應該能畫出 TiDB 一筆跨多個 TiKV 節點的交易，從 `start_ts` 到 `commit_ts` 的完整時序圖。

---

## 第五章：「同一份資料，怎麼同時服務 OLTP 和 OLAP？」

評估報告寫到一半，阿倫突然想起一個需求。

業務部門每個月月底都要跑一批統計報表——「過去 30 天各品類的訂單金額彙總」、「用戶複購率趨勢」這種查詢。這類 OLAP 查詢會掃描幾億行資料，在訂單資料庫上跑幾分鐘，每次都把主庫的 IO 打滿，影響線上交易。他之前的解法是把資料同步到一個獨立的 data warehouse，但同步延遲讓報表的資料始終比線上慢幾個小時。

他在 TiDB 的文件裡找到了 **TiFlash**，官方說它是「HTAP（Hybrid Transactional and Analytical Processing）」的關鍵。

TiFlash 是一個**列式儲存**節點，它從 TiKV 非同步地複製資料，但不是存成行格式（row format），而是存成列格式（column format）。為什麼列式格式對 OLAP 有優勢？因為 OLAP 查詢通常只需要少數幾個欄位，但需要掃描大量行——列式儲存讓你可以只讀取需要的列，大幅減少 IO。

阿倫整理出這個架構的關鍵特性：

- **非同步複製，不影響寫入路徑**：TiFlash 的複製流量不經過 Raft 的 commit 路徑，對 TiKV 的寫入延遲幾乎沒有影響。
- **資料最終一致**：TiFlash 的資料比 TiKV 晚幾毫秒到幾秒，適合分析查詢，不適合需要讀取最新寫入資料的 OLTP 查詢。
- **智慧查詢路由**：TiDB 的 SQL 執行器（Coprocessor）會根據查詢特性自動決定從 TiKV 還是 TiFlash 讀取資料。一個掃描大量行的聚合查詢會自動路由到 TiFlash；一個點查（通過主鍵查單行）會走 TiKV。這個路由對應用程式完全透明。

*阿倫想：* 這就解決了他的問題。月底的統計報表會自動走 TiFlash，不會和線上交易的 TiKV 搶資源。而且資料不需要手動同步到獨立的 data warehouse——TiFlash 的資料就是 TiKV 的即時映像（幾秒延遲）。

他在評估報告裡加了一節：「TiFlash 可以取代目前的 MySQL → data warehouse 同步架構，減少一個維護點，並將報表的資料新鮮度從小時級提升到秒級。」

---

> ### 📚 去這裡深入了解
>
> - [系統架構](/tidb/architecture) — TiFlash 的列式複製機制與 HTAP 查詢路由
> - [核心功能](/tidb/core-features) — HTAP 查詢路由決策邏輯
>
> 讀完後，你應該能解釋：TiFlash 和獨立的 data warehouse 相比，有什麼架構上的優勢和限制？什麼樣的查詢應該走 TiFlash？

---

## 第六章：「怎麼把 MySQL 的資料搬過去？」

評估報告獲得 CTO 批准，阿倫接到了下一個任務：規劃遷移方案。

公司的訂單資料庫目前有大約 2TB 的資料，日增量約 5GB。業務要求遷移期間不能停機超過 30 分鐘。這個要求讓阿倫立刻意識到，他不能用最簡單的「停機匯出 dump、匯入 TiDB」方案——2TB 的 mysqldump 匯入要好幾個小時。

他在 TiDB 的文件裡找到了兩個工具：

**Dumpling**：TiDB 官方的資料匯出工具，針對大型資料庫優化。它比 mysqldump 快很多，因為它支援多執行緒並行匯出，並且可以匯出成 SQL 或 CSV 格式。更重要的是，它支援「一致性匯出」——會在匯出開始時記錄一個 binlog position（或 GTID），確保匯出的快照是一個時間點的一致性視圖。

**TiDB Lightning**：高速批量匯入工具。它不走 SQL 協議插入資料，而是直接把資料轉換成 TiKV 的 SST 格式並 ingest 到 TiKV，速度可以達到每小時數百 GB。阿倫看了一下效能數據，心想 2TB 的資料用 TiDB Lightning 大概需要 3-5 小時，但這段時間業務是可以繼續寫入 MySQL 的。

阿倫設計的遷移流程如下：

```
Phase 1（全量匯入，不停機）：
  MySQL ──Dumpling──> 快照資料（記錄 binlog position）
                        ↓
                 TiDB Lightning ──> TiDB 叢集
                 （預計 3-5 小時）

Phase 2（增量同步，不停機）：
  MySQL binlog ──Dumpling/CDC──> TiDB（追 binlog，追上後延遲 < 1 秒）

Phase 3（切換，30 分鐘停機）：
  1. 停止應用寫入 MySQL
  2. 確認 TiDB 與 MySQL 完全同步
  3. 切換應用連接字串到 TiDB
  4. 驗證業務正常
```

*這個流程的關鍵在於 Phase 2：* 全量匯入期間，MySQL 的增量資料透過 binlog 持續同步到 TiDB，讓兩邊的差距縮小到秒級。當差距夠小的時候，才做那 30 分鐘的停機切換窗口。

阿倫特別注意了一點：TiDB Lightning 的 `local` 模式在匯入期間會讓 TiDB 叢集無法提供正常服務（因為它直接操作 TiKV 的 SST 文件），所以全量匯入要用獨立的 TiDB 叢集，而不是直接匯入生產叢集。他在方案裡加了一個「準備一個暫存 TiDB 叢集」的步驟。

---

> ### 📚 去這裡深入了解
>
> - [外部整合](/tidb/integration) — TiDB Lightning 的 local/tidb 模式差異、Dumpling 的一致性匯出機制
>
> 讀完後，你應該能設計一個「2TB MySQL 資料庫、最大 30 分鐘停機」的 TiDB 遷移方案，並說明每個工具的職責。

---

## 第七章：「遷移後，備份怎麼做？」

切換到 TiDB 之後，阿倫面臨的第一個實際運維問題就是備份。

在 MySQL 時代，他的備份流程很簡單：每天凌晨用 Percona XtraBackup 做物理備份，加上持續的 binlog 備份，RTO/RPO 都控制在小時級。現在換成了分散式資料庫，資料分散在多個 TiKV 節點上，他不能再直接備份磁碟文件了。

TiDB 官方的備份工具是 **BR（Backup & Restore）**。阿倫研究了它的工作原理：

BR 並不走 SQL 協議，它直接和 TiKV 的每個節點通訊，讓每個 TiKV 節點把自己負責的 Region 資料匯出成 SST 文件，儲存到共享的物件儲存（S3、GCS 或本地 NFS）。這個備份是分散式的——所有 TiKV 節點同時備份，速度和叢集的節點數量成正比，2TB 的叢集用 BR 備份通常只需要幾十分鐘。

更重要的是，BR 支援**增量備份**（Incremental Backup）：第一次做全量備份之後，後續只需要備份有變更的 Region，大幅減少備份時間和儲存空間。

阿倫設計了新的備份策略：

| 備份類型 | 頻率 | 工具 | 儲存位置 |
|---------|------|------|---------|
| 全量備份 | 每週一次 | BR full | S3 bucket |
| 增量備份 | 每小時一次 | BR log | S3 bucket |
| 快速驗證 | 每次備份後 | BR validate | 本地暫存 |

他還特別測試了還原流程——這是很多 DBA 會忽略的步驟。BR 的還原同樣是分散式的：每個 TiKV 節點同時 ingest 自己對應的 SST 文件，還原速度和備份速度差不多。他在測試環境還原了一份全量備份加兩小時的增量備份，整個過程不到一小時，比 MySQL 的 XtraBackup 還原速度快了很多。

「備份的事解決了，」阿倫在筆記本上打了個勾。「接下來要解決的是資料異動通知的問題。」

---

> ### 📚 去這裡深入了解
>
> - [外部整合](/tidb/integration) — BR 備份還原的工作原理、增量備份機制、S3 整合
>
> 讀完後，你應該能比較 BR 和 MySQL XtraBackup 的工作原理差異，並解釋為什麼 BR 的備份速度能隨叢集節點數擴展。

---

## 第八章：「資料異動要怎麼通知下游？」

公司有一個訂單審計系統，它的資料來源是 MySQL 的 binlog——每當訂單狀態有變更，就從 binlog 解析出事件，發到 Kafka，再由審計系統消費。這個架構換到 TiDB 之後要怎麼維持？

阿倫去查了 TiDB 的 **TiCDC（TiDB Change Data Capture）**。

TiCDC 是 TiDB 官方的 CDC 工具，功能類似 MySQL 生態中的 Debezium 或 Maxwell。它監聽 TiKV 的資料變更，把每一筆 DML（INSERT/UPDATE/DELETE）轉換成變更事件，並推送到下游系統。TiCDC 支援的下游包括：

- **Kafka**：把變更事件以 JSON 或 Avro 格式發到 Kafka topic，下游的 consumer 可以做任意的資料流處理。
- **MySQL / TiDB**：直接把變更應用到另一個 MySQL 或 TiDB 實例，常用於資料庫複製和跨地域的備援。
- **S3 等物件儲存**：把變更事件歸檔到物件儲存，用於合規審計或歷史重播。

TiCDC 的工作原理和 MySQL binlog 複製有幾個關鍵差異：

- **TiCDC 基於 TiKV 的 change event，不是 SQL binlog**：它捕獲的是 TiKV 層的 key-value 變更，然後在 TiCDC 內部還原成 SQL 層的 row 變更事件。
- **Exactly-once 語義**：TiCDC 使用 checkpoint 機制，確保每個變更事件恰好被下游消費一次，即使 TiCDC 本身發生重啟或故障。
- **多路複製**：一個 TiDB 叢集可以同時有多個 TiCDC Changefeed，分別把資料送到不同的下游（例如一個 Changefeed 送 Kafka，另一個做跨叢集備援）。

阿倫把現有的 MySQL binlog → Kafka pipeline 遷移方案確定下來：部署 TiCDC，建立一個 Changefeed 指向同一個 Kafka broker，輸出格式設成和現有 Debezium 相容的 schema（讓審計系統的 consumer 不需要修改）。

「CDC 的部分比我預期的順，」他想。「最後剩下一個問題：切換之後，叢集出問題了怎麼排查？」

---

> ### 📚 去這裡深入了解
>
> - [外部整合](/tidb/integration) — TiCDC 的架構、Changefeed 設定、Kafka 整合
>
> 讀完後，你應該能設計一個「MySQL binlog → Kafka」架構遷移到 TiDB 之後的等效 TiCDC 方案，並說明 TiCDC 和 MySQL binlog 複製在語義保證上的差異。

---

## 第九章：「叢集出問題，從哪裡開始排查？」

上線之後的第一個月，阿倫陸陸續續收到幾個問題回報：「訂單查詢比之前慢了」、「某個批次任務跑比預期久」。這些問題在 MySQL 時代，他會去看 `slow_query_log`，然後用 `EXPLAIN` 分析執行計劃。TiDB 有沒有類似的工具？

答案是 **TiDB Dashboard**。

TiDB Dashboard 是內建在 PD 的一個 Web UI，不需要另外安裝。阿倫打開它，發現這個工具的資訊密度比他預期的高很多：

**慢查詢分析**：TiDB Dashboard 自動收集所有超過閾值（預設 300ms）的慢查詢，以視覺化方式呈現查詢時間分布、最慢的查詢列表、每個查詢的詳細執行計劃（包括每個算子在哪個 TiKV 節點上執行、花了多少時間）。阿倫找到了「訂單查詢比較慢」的根本原因：某個查詢的執行計劃選了一個 full table scan，而不是走索引——統計資訊過時了，觸發了不良的查詢計劃選擇。解法是 `ANALYZE TABLE orders`。

**Key Visualizer**：這是 TiDB 特有的工具，用熱圖（heatmap）顯示每個 Region 的讀寫熱度，以時間為橫軸、key 範圍為縱軸。阿倫第一次看到這個工具的時候，心想「這在 MySQL 裡根本沒辦法做到」。他用它找到了一個持續寫入熱點——批次任務在某個時間段集中寫入的 key 範圍很窄，導致特定 Region 過熱。解法是把批次任務改成隨機打散寫入順序，讓 PD 有機會均衡負載。

**叢集拓撲視圖**：清楚顯示目前有幾個 TiDB Server、幾個 TiKV 節點、幾個 PD 節點，以及每個節點的健康狀態和版本。任何節點離線，這裡都會立刻反映。

**SQL 綁定（SQL Binding）**：當查詢計劃不理想時，可以直接在 Dashboard 上強制綁定一個特定的執行計劃 hint，不需要修改應用程式 SQL。

阿倫在筆記本的最後一頁寫下：「TiDB Dashboard 是我用過最好用的資料庫 observability 工具，沒有之一。它把原本要靠經驗和工具拼湊的排查流程，整合到了一個介面裡。」

---

> ### 📚 去這裡深入了解
>
> - [控制器與 API](/tidb/controllers-api) — TiDB Dashboard 的功能、HTTP Status API、慢查詢日誌
>
> 讀完後，你應該能描述：面對一個「查詢比預期慢」的問題，在 TiDB Dashboard 裡的完整排查路徑是什麼？

---

## 結語：DBA 轉型的第一步

三個月後，阿倫的評估報告早已成為歷史，訂單資料庫已經在 TiDB 上穩定跑了整整一季。

上週大促期間，寫入 QPS 達到了 MySQL 時代的三倍——但那條 CPU 曲線只到 60%，因為 TiDB Server 早已橫向擴展成六個節點。PD 在後台悄悄把熱點 Region 搬了幾十次，沒有任何一次需要 DBA 介入。月底的統計報表從 TiFlash 拉資料，沒有影響到線上交易的任何一個 TiKV 節點。

阿倫坐在同樣的椅子上，看著監控畫面，喝著還熱的咖啡。

他知道這段旅程只是開始。TiDB 還有很多他沒有深入研究的部分——Security 的 TLS 設定、多租戶的 Resource Control、跨資料中心的 Geo-Distributed 部署。但最重要的事情他已經搞清楚了：TiDB 不是「更好的 MySQL」，它是一個根本上不同的系統——只是剛好說著 MySQL 的語言。

*理解這個差異，是成為一個合格的 TiDB DBA 的第一步。*

---

::: info 📚 繼續深入
完整的技術細節，請閱讀技術文件：

- [系統架構](/tidb/architecture) — TiDB Server、TiKV、PD、TiFlash 完整架構
- [核心功能](/tidb/core-features) — 2PC 交易、HTAP 路由、DDL 非同步、SQL 優化器
- [控制器與 API](/tidb/controllers-api) — Dashboard、HTTP API、Session 管理
- [外部整合](/tidb/integration) — BR、TiDB Lightning、Dumpling、TiCDC
:::
