---
layout: doc
title: Ceph — OSD 詳解
---

# Ceph — OSD 詳解

::: tip 核心定位
OSD（Object Storage Daemon）是 Ceph 真正承載資料的核心程序。它負責物件寫入、複本同步、故障恢復、資料檢查與磁碟後端互動，是整個資料平面的主角。
:::

::: info 相關章節
- 想先理解控制平面如何發布叢集狀態，請參閱 [Ceph — Monitor (MON) 詳解](./monitor)
- 想了解指標、模組與編排能力，請參閱 [Ceph — Manager (MGR) 與模組系統](./manager)
- 想了解 CephFS metadata 如何建立在 OSD 之上，請參閱 [Ceph — Metadata Server (MDS) 詳解](/ceph/mds)
:::

## OSD 的角色：實際儲存、複寫、恢復

在 `src/osd/OSD.h` 中可以看到兩個核心類別：

```cpp
// 檔案: ceph/src/osd/OSD.h
class OSDService : public Scrub::ScrubSchedListener {
```

```cpp
// 檔案: ceph/src/osd/OSD.h
class OSD : public Dispatcher,
            public md_config_obs_t,
            public AdminSocketHook {
```

這兩者通常可分工理解為：

- **OSD**：整個 daemon 的訊息入口與狀態協調者
- **OSDService**：提供 PG、scrub、recovery、reservation 等執行期服務

OSD 負責的主軸包括：

1. **實際資料存放**：把 object 寫到 BlueStore 等後端。
2. **複本同步**：Primary OSD 協調 replica OSD 寫入與確認。
3. **Recovery / Backfill**：節點故障或拓撲改變後，補回缺失副本。
4. **Scrubbing**：定期驗證資料與 metadata 一致性。

## BlueStore：預設儲存後端

自 Luminous 以後，BlueStore 成為 Ceph 預設 object store。其核心類別在 `src/os/bluestore/BlueStore.h`：

```cpp
// 檔案: ceph/src/os/bluestore/BlueStore.h
class BlueStore : public ObjectStore,
                  public md_config_obs_t {
```

BlueStore 的設計重點是：

- **直接存取原始 block device**，避開傳統檔案系統的額外層次與 page cache 干擾。
- **資料與 metadata 分流**：物件資料直接放在原始裝置區段，metadata 則交給 RocksDB。
- **BlueFS** 作為 RocksDB 的專用輕量檔案系統，協助管理 DB / WAL 所需空間。

可以把 BlueStore 想成：

```text
// 檔案: docs-site/ceph/osd.md
Object 寫入
   |
   v
+-----------+      +----------------+
| BlueStore | ---> | 原始 block 空間 |
+-----------+      +----------------+
      |
      +-----------> RocksDB metadata
      |
      +-----------> BlueFS 管理 DB/WAL 檔案
```

::: tip 為什麼不用一般檔案系統
BlueStore 直接對 raw device 管理配置與校驗，能減少雙重快取與 inode / journal 額外負擔，這也是 Ceph 在大型儲存場景下偏好 BlueStore 的關鍵原因。
:::

## PG：OSD 內真正的資料管理單位

Ceph 並不是直接以「pool -> object -> OSD」管理，而是先經過 **Placement Group（PG）**。`src/osd/PG.h` 中：

```cpp
// 檔案: ceph/src/osd/PG.h
class PG
```

PG 的角色可以理解成：

- object 的邏輯分桶
- 一組副本的狀態機
- recovery、backfill、scrub 的協調單位
- peering 與 acting set 判定的邊界

這也是為什麼 Ceph 的許多行為都以「每個 PG」而非「每個 object」來處理：因為這樣能在大量 object 之上保留可管理的控制粒度。

## OSDService：支撐 PG 執行的共享服務層

`OSDService` 雖然不是資料平面最顯眼的名字，卻是 OSD 執行期的重要共用基礎。從類別宣告可看到它持有：

- `ObjectStore * const store`
- `PGRecoveryStats &pg_recovery_stats`
- scrub scheduler 相關介面
- 與 reservation、map、排程密切相關的共享狀態

換句話說，PG 是邏輯單元，但很多實際資源管理，例如 recovery 配額、scrub 排程、store 存取，都是透過 `OSDService` 協調。

## 複寫協定：Primary 主導，Replica 跟隨

在 replicated pool 中，寫入大致會經過以下路徑：

```text
// 檔案: docs-site/ceph/osd.md
Client
  |
  v
Primary OSD (依 CRUSH / PG 選出)
  |
  +--> 本地寫入 BlueStore
  |
  +--> 傳送複寫操作給 Replica OSD
           |
           v
       Replica 持久化後回 ACK
  |
  v
Primary 聚合完成後回覆 Client
```

這裡的核心不是「每顆 OSD 都各自獨立」，而是 **Primary OSD 對一個 PG 擁有協調責任**。它必須根據目前 `OSDMap` 決定 acting set，並確保寫入在足夠副本上達成正確順序與確認。

## Recovery 與 Backfill：節點故障後如何補齊資料

當 OSD down、重新加入、或 CRUSH / pool 參數變更時，PG 可能失去完整副本。這時就會進入 recovery 或 backfill 路徑：

- **Recovery**：對已知缺口做增量補齊，通常是較精準的同步。
- **Backfill**：當一方缺少完整歷史或需要大量重建時，以掃描方式重建內容。

在 Ceph 原始碼中，`OSD.h`、`PG.h` 與 `src/osd/PeeringState.*` 周邊有大量 `recovery`、`backfill` 相關欄位與狀態，顯示這不是單一函式，而是一整套跨 PG 狀態機與排程系統協作的機制。

::: warning 常見誤解
Recovery 與 backfill 都會搬動資料，但兩者不完全相同。前者偏向「補齊已知差異」，後者偏向「重新灌整塊缺失內容」。實務上 backfill 往往更重、更耗 IO。
:::

## Scrubbing：資料一致性檢查

Scrubbing 是 OSD 長期維持資料可靠性的另一個重點。

- **scrub**：檢查 object metadata、omap、基本一致性
- **deep scrub**：更深入地檢查實際資料內容與 checksum

從 `OSDService : public Scrub::ScrubSchedListener` 可看出 scrub 在 OSD 中不是附屬功能，而是被當成正式的排程子系統來管理。這很合理，因為 scrub 需要和前景 IO、recovery、磁碟壓力共享資源，不能無限制地同時執行。

## OSD、PG 與 BlueStore 的關係

```text
// 檔案: docs-site/ceph/osd.md
+-----------------------------+
|            OSD              |
| Dispatcher / Network / Map  |
+-------------+---------------+
              |
              v
+-----------------------------+
|             PG              |
| Peering / Replication /     |
| Recovery / Scrub            |
+-------------+---------------+
              |
              v
+-----------------------------+
|         BlueStore           |
| Raw device / RocksDB /      |
| BlueFS                      |
+-----------------------------+
```

這個分層非常重要：

- **OSD** 解決 daemon 級別的生命週期與訊息處理
- **PG** 解決副本集合的一致性與恢復問題
- **BlueStore** 解決最終落盤與 metadata 管理問題

## 實作觀察重點

::: tip 建議閱讀順序
1. 先看 `src/osd/OSD.h` 了解 daemon 與 service 的邊界。
2. 再看 `src/osd/PG.h`，把 PG 視為主要狀態機單位。
3. 接著看 `src/os/bluestore/BlueStore.h` 與 BlueFS / RocksDB 相關檔案，理解實際儲存層。
4. 若要更深入 peering、recovery、backfill，可延伸閱讀 `PeeringState` 與 `PrimaryLogPG` 相關實作。
:::

## 關鍵原始碼索引

- `ceph/src/osd/OSD.h:1243` — `class OSD : public Dispatcher`
- `ceph/src/osd/OSD.h:99` — `class OSDService`
- `ceph/src/osd/PG.h:169` — `class PG`
- `ceph/src/os/bluestore/BlueStore.h:261` — `class BlueStore : public ObjectStore`

## 相關章節

::: info 延伸閱讀
- 控制平面與 map 一致性請閱讀 [Ceph — Monitor (MON) 詳解](./monitor)
- 模組系統、Prometheus 與 dashboard 請閱讀 [Ceph — Manager (MGR) 與模組系統](./manager)
- CephFS metadata path 請閱讀 [Ceph — Metadata Server (MDS) 詳解](/ceph/mds)
:::
