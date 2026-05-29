---
layout: doc
title: Ceph — 整體架構概述
---

# Ceph — 整體架構概述

Ceph 的整體設計可以分成兩個層次來看：

- **控制面（control plane）**：由 MON、MGR、MDS 等 daemon 維護叢集狀態、地圖與管理功能。
- **資料面（data plane）**：由 OSD 與 RADOS 負責實際資料放置、複寫、回復與一致性流程。

Ceph 最關鍵的特性，是 client 不需要把每一次讀寫都經過中心節點；只要先取得最新 cluster map，就能自行計算資料應該落到哪些 OSD。

::: tip 核心理解
理解 Ceph 時，請先把它當成「以 RADOS 為核心、再往外提供多種儲存介面」的平台，而不是單純的分散式檔案系統。
:::

## RADOS 是什麼？

RADOS 全名是 **Reliable Autonomic Distributed Object Store**。它是 Ceph 的核心儲存抽象，主要負責以下能力：

- 把資料切分到 Placement Group（PG）
- 依照 CRUSH 規則計算資料應該放到哪些 OSD
- 處理資料複寫、故障轉移、回復與 scrub
- 提供上層介面（RBD、CephFS、RGW、librados）一致的底層資料平面

換句話說，**RBD 是建在 RADOS 上的區塊層、CephFS 是建在 RADOS 上的檔案層、RGW 則是把 RADOS 包裝成物件 API**。

## 整體架構與網路拓樸

<pre>
                       Client / Hypervisor / Application
                 +------------------------------------------+
                 | librados | librbd | kernel client | RGW |
                 +----------------------+-------------------+
                                        |
                           取得 cluster maps / auth
                                        |
                              +---------v---------+
                              |   MON quorum      |
                              | MonMap / OSDMap   |
                              | CRUSHMap / PGMap  |
                              +---------+---------+
                                        |
                           telemetry / modules / commands
                                        |
                              +---------v---------+
                              |      MGR          |
                              | dashboard / orch  |
                              +-------------------+

          Public / Client Network ================================
                |                         |                      |
                v                         v                      v
          +-----------+             +-----------+          +-----------+
          |  OSD.0    |<===========>|  OSD.1    |<========>|  OSD.2    |
          | data I/O  |  backfill   | data I/O  | recovery | data I/O  |
          +-----------+  / peer     +-----------+ / scrub  +-----------+

          Cluster / Replication Network ==========================
                |                         |                      |
                +-------------------------+----------------------+

                         +-----------------------------+
                         | MDS (only for CephFS)       |
                         | inode / dentry / metadata   |
                         +-----------------------------+
</pre>

::: warning 不要把所有元件都視為資料路徑必經點
MON、MGR 與 MDS 並不是所有 I/O 的共同瓶頸。一般 RADOS / RBD client 在取得 map 後，主要是直接與 OSD 通訊；只有 CephFS metadata 操作才會進入 MDS 路徑。
:::

## 各類 daemon 的角色

### MON（Monitor）

MON 維護整個叢集的共識狀態，包括 MonMap、OSDMap、CRUSHMap、MDSMap、認證資訊與多種 service map。它的重點不是搬運資料，而是提供一致、可仲裁的叢集觀點。

```cpp
// 檔案: src/mon/Monitor.h
class Monitor : public Dispatcher,
		public AuthClient,
		public AuthServer,
                public md_config_obs_t {
public:
  int orig_argc = 0;
  const char **orig_argv = nullptr;
```

從 `src/mon/Monitor.h` 第 113 行可以看到 `Monitor` 繼承 `Dispatcher`，代表它本質上就是處理訊息與叢集狀態變更的控制面 daemon。

### OSD（Object Storage Daemon）

OSD 是 Ceph 真正承載資料的核心元件，負責：

- 物件資料讀寫
- PG peering
- 複寫與 recovery
- scrub / deep-scrub
- 與其他 OSD 交換副本狀態

```cpp
// 檔案: src/osd/OSD.h
class OSD : public Dispatcher,
	    public md_config_obs_t {
  using OpSchedulerItem = ceph::osd::scheduler::OpSchedulerItem;

  /** OSD **/
  // global lock
  ceph::mutex osd_lock = ceph::make_mutex("OSD::osd_lock");
```

`src/osd/OSD.h` 第 1243 行顯示 OSD 同樣是一個訊息驅動的 daemon，但它承載的是資料面複雜度，而不是叢集仲裁。

### MGR（Manager）

MGR 不是資料一致性的根源，但它負責大量「可觀測性與管理擴充」。像 Dashboard、orchestrator、metric collector、各類 module 都建在這一層。

```cpp
// 檔案: src/mgr/DaemonServer.h
/**
 * Server used in ceph-mgr to communicate with Ceph daemons like
 * MDSs and OSDs.
 */
class DaemonServer : public Dispatcher, public md_config_obs_t
{
protected:
  boost::scoped_ptr<Throttle> client_byte_throttler;
```

`DaemonServer` 直接說明了 MGR 需要與 OSD、MDS 等 daemon 溝通，這也是它能提供集中觀測與管理模組的基礎。

### MDS（Metadata Server）

MDS 只在 CephFS 場景中出現，專門處理 metadata，例如 inode、目錄樹、rename、分散式 cache 協調等。

```cpp
// 檔案: src/mds/MDSRank.h
/**
 * The public part of this class's interface is what's exposed to all
 * the various subsystems (server, mdcache, etc), such as pointers
 * to the other subsystems, and message-sending calls.
 */
class MDSRank {
  public:
    friend class C_Flush_Journal;
```

`src/mds/MDSRank.h` 第 164 行的 `MDSRank` 代表 CephFS 中的 rank 執行個體；這種 rank 概念，正是 CephFS metadata 可以水平切分的基礎。

### RGW（RADOS Gateway）

RGW 把 RADOS 包成 S3 / Swift 相容的物件閘道。它不是另一套獨立儲存後端，而是利用 RADOS 作為底層物件與 metadata 儲存基礎。

## Cluster Map 概念

Ceph client 不會在每次 I/O 時都詢問 MON，而是先取得 map，再用本地計算決定路由。這套設計的前提，就是多種 cluster map。

### MonMap

MonMap 描述 monitor 成員、位址與 epoch，是 client 連入叢集控制面的入口資訊。

```cpp
// 檔案: src/mon/MonMap.h
class MonMap {
 public:
  epoch_t epoch{0};       // what epoch/version of the monmap
  uuid_d fsid;
  utime_t last_changed;
  utime_t created;

  std::map<std::string, mon_info_t> mon_info;
```

### OSDMap

OSDMap 是 client 與 OSD 都極度依賴的地圖，記錄 OSD 狀態、pool、epoch 與增量更新資訊。

```cpp
// 檔案: src/osd/OSDMap.h
/** OSDMap
 */
class OSDMap {
public:
  MEMPOOL_CLASS_HELPERS();

  class Incremental {
  public:
    MEMPOOL_CLASS_HELPERS();

    /// feature bits we were encoded with.  the subsequent OSDMap
```

此外，`src/osd/OSDMap.h` 一開始就註明它用來 *describe properties of the OSD cluster*，並且直接引入 `crush/CrushWrapper.h`，這表示 OSDMap 與 CRUSH 放置規則是緊密耦合的。

### CRUSHMap

CRUSHMap 定義失效域（host、rack、row、room、datacenter）與資料放置規則。client 取得 OSDMap / CRUSHMap 後，就能自行計算資料副本位置。

### MDSMap

MDSMap 描述 CephFS 的 metadata 服務狀態與 rank 狀態機。

```cpp
// 檔案: src/mds/MDSMap.h
class MDSMap {
public:
  /* These states are the union of the set of possible states of an MDS daemon,
   * and the set of possible states of an MDS rank. See
   * doc/cephfs/mds-states.rst for state descriptions and a visual state diagram, and
   * doc/cephfs/mds-state-diagram.dot to update the diagram.
   */
  typedef enum {
```

### PGMap

PGMap 主要追蹤 PG 與 OSD 統計狀態，常用於叢集健康度、容量與狀態觀測。

```cpp
// 檔案: src/mon/PGMap.h
class PGMap : public PGMapDigest {
public:
  MEMPOOL_CLASS_HELPERS();

  // the map
  version_t version;
  epoch_t last_osdmap_epoch;   // last osdmap epoch i applied to the pgmap
  epoch_t last_pg_scan;  // osdmap epoch
```

::: info 為什麼 map 要分這麼多種？
Ceph 把 monitor 成員、OSD 叢集狀態、CephFS rank 狀態與 PG 統計拆成不同 map，目的是讓控制面資訊可以各自演進、增量更新，而不是把所有狀態塞進單一巨型結構。
:::

## Client 如何找到 OSD？

這是 Ceph 與傳統集中式儲存架構最不同的地方。

1. Client 先向 MON 取得最新的 `MonMap`、`OSDMap`、`CRUSHMap` 與認證資訊。
2. Client 依據 pool、object、PG 計算規則，先算出 object 應該落在哪個 PG。
3. 接著根據 OSDMap + CRUSHMap，在本地端計算該 PG 應該對應哪些 acting / up OSD。
4. 真正的資料讀寫直接送往對應 OSD。
5. 只有 map 過期、OSD 狀態變化或需要重新認證時，client 才再次回到 MON。

這種模式的效果是：

- **MON 不會變成每次 I/O 的中心瓶頸**
- **client 可以直接 fan-out 到大量 OSD**
- **叢集擴充時，控制面與資料面壓力可以分離**

## 架構重點總結

- Ceph 的核心是 **RADOS + OSD + CRUSH**。
- MON 提供一致的 cluster maps，但不是每次 I/O 的 proxy。
- MGR 主要負責觀測、模組與 orchestrator 能力。
- MDS 只服務 CephFS metadata，不在一般 RADOS / RBD 路徑上。
- RGW 是對外 API 閘道，底層仍回到 RADOS。

::: info 相關章節
- [Ceph — 專案總覽](/ceph/)
- [Ceph — 部署架構與 cephadm](/ceph/deployment)
:::
