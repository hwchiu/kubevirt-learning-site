---
layout: doc
title: Ceph — 故事驅動式學習路徑
---

# Ceph — 故事驅動式學習路徑

## 第零步：為什麼需要分散式儲存？

在進入 Ceph 的任何技術細節之前，值得先思考一個根本問題：**為什麼不能只用一台伺服器的磁碟就好？**

### 單機儲存的三道牆

| 問題 | 說明 |
|---|---|
| 容量上限 | 一台伺服器能插的磁碟數量有限，當資料量超過這個上限，就沒有辦法繼續縱向擴充 |
| 單點故障 | 一塊磁碟或一台機器壞掉，資料就可能遺失或無法讀取 |
| 效能瓶頸 | 所有讀寫都集中在同一台機器，網路卡、CPU、I/O 通道都可能成為瓶頸 |

一旦你的應用規模超過單台機器，就需要把資料「散布到多台機器上」。這就是分散式儲存要解決的核心問題。

### 分散式儲存的三個根本挑戰

把資料散布到多台機器聽起來簡單，但實際上牽涉三個彼此關聯的難題：

**1. 資料要放在哪裡？（定位問題）**

如果有 100 台機器，一筆資料應該存在哪幾台？Client 之後要讀資料，又要怎麼找到它？
- 最簡單的做法：維護一個「中央目錄」，記錄每筆資料放在哪裡。
- 問題：這個中央目錄本身就成了瓶頸，所有讀寫都需要先查它。

**2. 資料壞掉怎麼辦？（冗餘問題）**

分散式環境下，機器故障是常態，不是例外。一旦有節點故障，放在那台機器上的資料怎麼辦？
- 典型做法：把同一份資料複製到多台機器（副本策略），或把資料切片後用 erasure coding 分散保護。
- 挑戰：誰來決定複製幾份？副本放在哪裡？故障後如何自動恢復？

**3. 多台機器的資料如何保持一致？（一致性問題）**

當資料有多個副本，更新其中一份時，其他副本也要跟著更新。如果更新到一半機器掛了，怎麼確保資料不會處於「一半新、一半舊」的不一致狀態？

### Ceph 的設計哲學：用計算取代中心查詢

傳統的分散式儲存系統，通常會用一個「中央 Metadata 節點」來回答「這筆資料在哪台機器」這個問題。好處是架構簡單；壞處是所有 I/O 都要先過一道中央節點，容易形成瓶頸，也容易出現單點故障。

Ceph 選擇了一條不同的路：**Client 不查中央目錄，而是用演算法自己算出資料應該在哪裡。**

這個演算法叫做 **CRUSH（Controlled Replication Under Scalable Hashing）**。只要 Client 拿到最新的叢集地圖（cluster map），就能在本機計算出任何一筆資料的位置，不需要詢問任何中介節點。

```
傳統模式：
Client → 中央 Metadata 節點 → 取得資料位置 → OSD

Ceph 模式：
Client → 用 CRUSH 本機計算位置 → 直接聯繫 OSD
```

這個設計帶來的效果是：
- **MON（Monitor）不是 I/O 的必經路徑**，只負責維護叢集狀態的地圖
- **叢集可以橫向擴充**，加機器不需要改中央目錄
- **Client 的讀寫可以平行散布**到大量 OSD，不會集中在同一個入口

理解了「為什麼要分散式儲存」與「Ceph 怎麼解決定位問題」之後，接下來我們可以用一條真實的寫入流程，把其他關鍵概念串起來。

---

## 故事的核心問題

> **當應用程式寫入一筆資料時，Ceph 到底做了哪些事？**

如果你能順著這條路把 client、PG、OSD、commit、監控與維運串起來，Ceph 的核心概念就會變得非常清楚。

## 故事導覽

1. [Step 1：client 送出寫入](#step-1client-送出寫入)
2. [Step 2：object 被映射到 PG](#step-2object-被映射到-pg)
3. [Step 3：primary OSD 協調副本寫入](#step-3primary-osd-協調副本寫入)
4. [Step 4：副本回覆 commit，client 收到成功](#step-4副本回覆-commitclient-收到成功)
5. [Step 5：控制面與觀測面如何看到這件事](#step-5控制面與觀測面如何看到這件事)
6. [Step 6：當流程出錯時，維運者怎麼排查](#step-6當流程出錯時維運者怎麼排查)

## 先看整體畫面

<pre>
Application
   |
   v
librados / client
   |
   v
Objecter 計算 object -> PG -> target OSD
   |
   v
Primary OSD 接手請求
   |
   +--> Replica OSD A
   +--> Replica OSD B
   |
   v
所有必要 commit / ack 完成
   |
   v
client 收到成功
   |
   v
Dashboard / Prometheus / ceph status 反映結果
</pre>

## Step 1：client 送出寫入

Ceph 的第一個關鍵觀念是：**client 不一定要經過中央 metadata / control node 才能寫資料**。在 RADOS 路徑中，client 會先透過 map 與定位邏輯找出目標 OSD，再直接送出 I/O。

在 `src/osdc/Objecter.cc` 裡，`Objecter::_op_submit()` 是提交 object operation 的核心路徑之一：

```cpp
// 檔案: src/osdc/Objecter.cc
void Objecter::_op_submit(Op *op, ...)
{
  int r = _calc_target(&op->target);
  ...
  r = _get_session(op->target.osd, &s, sul);
  ...
  ldout(cct, 10) << "_op_submit oid " << op->target.base_oid
                 << " ... osd." << (!s->is_homeless() ? s->osd : -1)
                 << dendl;
}
```

這段實作直接說明：Objecter 在送出請求前，會先計算 target，然後取得對應 OSD session。

### 你應該記住什麼？

- client 不是盲目廣播請求
- 它會先決定要送去哪個 OSD
- 這正是 Ceph 能水平擴充的關鍵之一

## Step 2：object 被映射到 PG

真正把 object 轉成 PG 的關鍵，在同一個檔案中：

```cpp
// 檔案: src/osdc/Objecter.cc
int ret = osdmap->object_locator_to_pg(t->target_oid, t->target_oloc, pgid);
ldout(cct,20) << __func__ << " target " << t->target_oid
              << " " << t->target_oloc << " -> pgid " << pgid << dendl;
```

這一步很重要，因為 Ceph 並不是直接把 object hash 到單一磁碟，而是先映射到 **Placement Group（PG）**，再由 PG 對應到 acting set / primary OSD。

### 為什麼多一層 PG？

因為這讓 Ceph 可以：

- 批次管理資料分布
- 以 PG 為單位做 peering、recovery、scrub
- 在 OSD 數量變化時，控制資料搬移的粒度

如果你把 PG 理解成「object 與實際 OSD 之間的管理中介層」，後面很多維運現象都會更容易理解。

## Step 3：primary OSD 協調副本寫入

當請求送到 primary OSD 後，接下來就不是 client 直接處理所有副本，而是由 primary 負責協調。

從 `src/osd/ReplicatedBackend.cc` 可以看到，`submit_transaction()` 會建立 transaction、記錄 log、追蹤正在等待 commit 的副本集合，然後送出 replication 操作：

```cpp
// 檔案: src/osd/ReplicatedBackend.cc
void ReplicatedBackend::submit_transaction(...)
{
  ...
  op.waiting_for_commit.insert(
    parent->get_acting_recovery_backfill_shards().begin(),
    parent->get_acting_recovery_backfill_shards().end());

  issue_op(...);
  parent->log_operation(...);
  parent->queue_transactions(tls, op.op);
}
```

### 這段流程代表什麼？

- primary OSD 不只是本地寫資料
- 它還要協調 acting set 內其他 shard / replica
- 寫入不只是 data path，也包含 PG log 與版本追蹤

這也是為什麼 OSD 寫入問題，常常不是「單一磁碟慢」那麼簡單，而會牽涉 PG、peer、network 與 commit 狀態。

## Step 4：副本回覆 commit，client 收到成功

同一個檔案接著展示 commit 完成條件：

```cpp
// 檔案: src/osd/ReplicatedBackend.cc
void ReplicatedBackend::op_commit(const ceph::ref_t<InProgressOp>& op)
{
  op->waiting_for_commit.erase(get_parent()->whoami_shard());

  if (op->waiting_for_commit.empty()) {
    op->on_commit->complete(0);
    op->on_commit = 0;
    in_progress_ops.erase(op->tid);
  }
}
```

以及收到 replica reply 時，會把對方從等待集合移除：

```cpp
// 檔案: src/osd/ReplicatedBackend.cc
if (r->ack_type & CEPH_OSD_FLAG_ONDISK) {
  ceph_assert(ip_op.waiting_for_commit.count(from));
  ip_op.waiting_for_commit.erase(from);
}
```

### 這告訴我們什麼？

- client 成功不是單看 primary 寫完沒有
- 對 replicated pool 而言，primary 需要等必要副本回覆 commit / ondisk ack
- 因此網路、peer OSD、磁碟延遲都可能拖慢整體寫入完成時間

## Step 5：控制面與觀測面如何看到這件事

單筆寫入完成後，維運者不會去讀 `Objecter.cc` 或 `ReplicatedBackend.cc` 排查；更常見的是從控制面與觀測面看整體症狀。

### CLI 會看到什麼？

- `ceph status`：整體摘要
- `ceph health detail`：是否有 degraded / backfill / slow ops
- `ceph pg stat`：PG 是否異常
- `ceph osd perf`：OSD latency 是否上升

### Dashboard 會看到什麼？

Dashboard frontend 直接查詢：

- `ceph_cluster_total_used_bytes`
- `sum(rate(ceph_pool_wr[1m]))`
- `sum(rate(ceph_pool_rd[1m]))`
- `avg_over_time(ceph_osd_apply_latency_ms[1m])`
- `avg_over_time(ceph_osd_commit_latency_ms[1m])`

所以如果一筆寫入背後其實引發了某些 OSD commit 變慢，Dashboard 通常會先從 throughput / latency 卡片把異常放大成可觀察訊號。

## Step 6：當流程出錯時，維運者怎麼排查

現在把前面故事換成維運語言：

### 症狀 A：寫入變慢

可能對應到：

- primary OSD 壓力高
- replica commit 太慢
- OSD apply / commit latency 上升
- host 或 network 異常

建議路徑：

1. 先看 [Dashboard](/ceph/dashboard)
2. 再跑 `ceph osd perf`
3. 補 `ceph pg stat`
4. 必要時看 `cephadm logs`

### 症狀 B：PG degraded / undersized

代表故事停在「primary 找不到足夠健康副本」這一段。

建議路徑：

1. `ceph health detail`
2. `ceph pg stat`
3. `ceph orch ps`
4. `ceph log last`

### 症狀 C：擴容後資料重分布很久

代表 PG 與 CRUSH 對應關係改變，Ceph 正在把故事中的 object / PG / acting set 重新平衡。

這時要把它當作正常資料面行為來看，而不是立刻判斷為故障。

## 把整個故事濃縮成一句話

> **Ceph 的寫入流程，本質上是 client 先定位 PG，primary OSD 再協調副本與 commit，最後由控制面與觀測面把整體狀態呈現給維運者。**

當你能把這句話與 `Objecter.cc`、`ReplicatedBackend.cc`、Dashboard 指標、`ceph status` 串在一起，Ceph 的主幹就算真的抓住了。

## 下一步怎麼學？

- 想補控制面：看 [cephadm 深入分析](/ceph/cephadm)
- 想補觀測面：看 [Dashboard](/ceph/dashboard)
- 想補實務排錯：看 [日常維運](/ceph/operations)

::: info 相關章節
- [Ceph — 整體架構概述](/ceph/architecture)
- [Ceph — cephadm 深入分析](/ceph/cephadm)
- [Ceph — Dashboard](/ceph/dashboard)
- [Ceph — 日常維運](/ceph/operations)
:::
