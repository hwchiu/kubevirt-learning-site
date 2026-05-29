---
layout: doc
title: Ceph — Monitor (MON) 詳解
---

# Ceph — Monitor (MON) 詳解

::: tip 核心定位
Ceph Monitor（MON）不是資料平面，而是整個叢集的**控制平面與一致性中樞**。它負責維護叢集地圖、仲裁成員、處理 CephX 身分驗證，並透過 Paxos 確保多個 Monitor 對關鍵狀態有一致觀點。
:::

::: info 相關章節
- 若想了解實際資料寫入與副本流程，請參閱 [Ceph — OSD 詳解](./osd)
- 若想了解指標、模組與 REST API，請參閱 [Ceph — Manager (MGR) 與模組系統](./manager)
- 若想了解 CephFS 中繼資料協調，請參閱 [Ceph — Metadata Server (MDS) 詳解](/ceph/mds)
:::

## MON 的角色：叢集狀態管理與 Paxos 一致性

從 `src/mon/Monitor.h` 可以看到 `Monitor` 本身是訊息分派核心：

```cpp
// 檔案: ceph/src/mon/Monitor.h
class Monitor : public Dispatcher,
                public AuthClient,
                public AuthServer,
                public md_config_obs_t {
```

這個繼承結構很直接地反映 MON 的三個責任：

1. **Dispatcher**：接收與分派各類 monitor 訊息。
2. **AuthClient / AuthServer**：同時參與叢集內部與外部客戶端的驗證流程。
3. **組態觀察者**：能根據執行期設定變動調整行為。

MON 並不保存使用者物件資料，而是保存「**誰應該擁有資料、叢集目前健康狀態如何、哪些服務可被信任**」這類高價值控制資訊。任何 OSD、MDS、MGR 或 client 想要正確行動，都必須先相信 MON 公布的狀態。

## MON 具體保存哪些資料

Ceph 的 Monitor 子系統會維護多種 map 或權限資訊，常見的包括：

| 名稱 | 用途 |
|---|---|
| `MonMap` | 記錄 Monitor 成員、位址、仲裁基礎資訊 |
| `OSDMap` | 記錄 OSD 拓撲、up/in 狀態、pool 設定、CRUSH 關聯 |
| `CRUSHMap` | 描述資料放置拓撲與故障領域 |
| `MDSMap` | 記錄 CephFS 的 MDS rank 與狀態 |
| `PGMap` | 彙整 Placement Group 與容量、健康、IO 統計 |
| `AuthMap` | 儲存 CephX 實體、金鑰、capabilities |

這些結構分散在不同 monitor service 中維護。例如：

- `src/mon/OSDMonitor.h` 管理 `OSDMap`
- `src/mon/MDSMonitor.h` 管理 `MDSMap`
- `src/mon/PGMap.h` 定義 `PGMap`
- `src/mon/AuthMonitor.h` 管理驗證與授權狀態

```cpp
// 檔案: ceph/src/mon/OSDMonitor.h
class OSDMonitor : public PaxosService,
                   public md_config_obs_t {
  OSDMap osdmap;
  OSDMap::Incremental pending_inc;
```

這代表 MON 不是一個單一巨大狀態機，而是由多個 **PaxosService** 各自管理不同類型的叢集真相，再由 Monitor 作為統一入口協調。

## Paxos 在 Ceph Monitor 裡的實作方式

`src/mon/Paxos.h` 中的 `Paxos` 類別是 MON 一致性機制的核心：

```cpp
// 檔案: ceph/src/mon/Paxos.h
class Paxos {
public:
  enum {
    STATE_RECOVERING,
    STATE_ACTIVE,
    STATE_UPDATING,
    STATE_UPDATING_PREVIOUS,
    STATE_WRITING,
    STATE_WRITING_PREVIOUS,
    STATE_REFRESH,
    STATE_SHUTDOWN
  };
```

Ceph 的 Paxos 實作重點不是教科書式地暴露 prepare / accept 名詞，而是把 Monitor 需要的流程包成可操作的狀態機：

- **Recovering**：重新加入 quorum 後先把本地狀態追到最新。
- **Active**：目前可服務、可讀取已提交狀態。
- **Updating / Writing**：Leader 準備提案、落盤、等待多數確認。
- **Refresh**：提交後重新整理本地快取與外部可見狀態。

可以把它簡化成下面的流程：

```text
// 檔案: docs-site/ceph/monitor.md
Client / Daemon 更新請求
          |
          v
     Leader MON 收到提案
          |
          v
  對應 PaxosService 產生新版本
          |
          v
 多數 MON 接受並持久化到 MonitorDBStore
          |
          v
      提交 commit 版本
          |
          v
  對外發布新的 map / auth 狀態
```

::: warning 觀念釐清
MON 的 Paxos 保護的是**控制平面狀態**，不是每一筆 object 寫入資料。實際物件資料複寫與恢復主要由 OSD 與 PG 狀態機負責。
:::

## 選舉邏輯：誰成為新的 Leader

`src/mon/Elector.h` 的 `Elector` 類別負責處理選舉訊息與本地選舉狀態：

```cpp
// 檔案: ceph/src/mon/Elector.h
class Elector : public ElectionOwner, RankProvider {
```

檔案中的註解已經清楚說明其職責：它維護 `ElectionLogic`，接收 proposal、ack、victory 等訊息，並決定本節點最後成為：

- **Leader**：主導 Paxos 提案與新狀態提交。
- **Peon**：追隨 Leader，接受已提交狀態。

從 `handle_propose`、`handle_ack`、`handle_victory` 這些方法名稱可看出 Ceph 將選舉拆成明確訊息階段。實務上還會搭配：

- peer feature 檢查
- quorum feature 相容性驗證
- ping / timeout 機制
- 連線品質追蹤（`ConnectionTracker`）

因此選舉不是單純比 rank，而是要同時考慮**能否形成合法 quorum** 與 **節點是否仍可信賴**。

## MonitorDBStore：Monitor 的持久化儲存層

MON 的一致性不能只停在記憶體。`src/mon/MonitorDBStore.h` 定義了持久化儲存抽象：

```cpp
// 檔案: ceph/src/mon/MonitorDBStore.h
class MonitorDBStore
{
  std::string path;
  boost::scoped_ptr<KeyValueDB> db;
```

這裡的 `KeyValueDB` 在實際部署中通常由 **RocksDB** 提供後端，因此可以把 MonitorDBStore 理解成：

- 上層：Monitor / PaxosService 以 transaction 方式寫入版本狀態
- 下層：RocksDB 負責 key-value 持久化

同一個檔案裡也能看到 `Transaction`、`put`、`erase`、`erase_range` 等操作，表示 MON 會把 map、auth、增量版本等內容以鍵值形式存進本地資料庫。這使得 Monitor 在重啟後能重新載入最後已提交的叢集狀態，而不是從零開始推導。

## CephX：客戶端與叢集服務的驗證入口

MON 也是 CephX 驗證的重要控制點。`src/auth/cephx/CephxKeyServer.h` 可以看到金鑰伺服結構：

```cpp
// 檔案: ceph/src/auth/cephx/CephxKeyServer.h
struct KeyServerData {
  version_t version{0};
  std::map<EntityName, EntityAuth> secrets;
  std::map<uint32_t, RotatingSecrets> rotating_secrets;
```

這裡保存的是：

- 實體名稱（例如 client、osd、mds、mgr）對應的 secret
- 各服務類型的 rotating secret
- 對應 capability（caps）資訊

MON 透過 CephX 提供兩層保護：

1. **身分驗證**：你是誰？
2. **授權控制**：你能存取哪些 pool、哪些 monitor command、哪些 filesystem？

也就是說，client 在真正與 OSD 或 MDS 深度互動前，通常會先從 MON 取得可信任的叢集地圖與驗證結果。

## MON 與其他 daemon 的協作關係

```text
// 檔案: docs-site/ceph/monitor.md
                +----------------------+
                |   Ceph Monitor MON   |
                | Paxos / Maps / Auth  |
                +----------+-----------+
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
   OSD 取得 OSDMap     MDS 取得 MDSMap    Client 取得 MonMap
   與 CRUSH 規則        與 CephFS 狀態      與 CephX 授權
```

MON 的工作像是「**發布真相**」：

- OSD 根據 `OSDMap` 與 `CRUSHMap` 決定資料位置
- MDS 根據 `MDSMap` 決定 rank 角色與故障接手
- client 根據 map 與 auth 資訊選擇正確目標

只要 MON 無法形成 quorum，整個叢集的控制平面就會失去可更新能力。

## 實作觀察重點

::: tip 閱讀原始碼時建議的主線
1. 先看 `Monitor.h` 了解總控角色。
2. 再看 `Paxos.h` 與 `PaxosService` 理解一致性框架。
3. 接著看 `OSDMonitor.h`、`MDSMonitor.h`、`AuthMonitor.h` 如何把不同 map 套進 Paxos。
4. 最後看 `Elector.h` 與 `MonitorDBStore.h`，理解 leader 選舉與持久化如何支撐整體穩定性。
:::

## 關鍵原始碼索引

- `ceph/src/mon/Monitor.h:113` — `class Monitor : public Dispatcher`
- `ceph/src/mon/Paxos.h:176` — `class Paxos`
- `ceph/src/mon/OSDMonitor.h` — OSD map 管理
- `ceph/src/mon/Elector.h` — 選舉邏輯
- `ceph/src/mon/MonitorDBStore.h` — 持久化儲存
- `ceph/src/auth/cephx/CephxKeyServer.h` — CephX 驗證資料

## 相關章節

::: info 延伸閱讀
- 下一步建議閱讀 [Ceph — OSD 詳解](./osd)
- 若想理解控制面外掛與 API，請閱讀 [Ceph — Manager (MGR) 與模組系統](./manager)
- 若要掌握 CephFS metadata path，請閱讀 [Ceph — Metadata Server (MDS) 詳解](/ceph/mds)
:::
