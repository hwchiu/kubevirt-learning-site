---
layout: doc
title: Ceph — Metadata Server (MDS) 詳解
---

# Ceph — Metadata Server (MDS) 詳解

::: tip 核心定位
MDS（Metadata Server）是 CephFS 的 metadata 控制平面。它不保存使用者檔案內容本身，而是管理目錄樹、inode、dentry、session 與快取一致性，讓 CephFS 能提供接近 POSIX 的目錄與檔案語意。
:::

::: info 相關章節
- 叢集 map 與控制平面請參閱 [Ceph — Monitor (MON) 詳解](./monitor)
- 底層物件資料存放請參閱 [Ceph — OSD 詳解](./osd)
- 指標、觀測與模組系統請參閱 [Ceph — Manager (MGR) 與模組系統](./manager)
:::

## MDS 的角色：CephFS metadata 管理

MDS 是 CephFS 和 RADOS 之間的重要橋梁：

- **檔案內容** 最終仍放在 RADOS / OSD
- **檔名、目錄階層、inode、權限、session** 則由 MDS 管理

在 `src/mds/MDSRank.h` 裡可以看到 `MDSRank` 是主要執行核心，並定義大量 metadata 服務相關的 perf counter：

```cpp
// 檔案: ceph/src/mds/MDSRank.h
enum {
  l_mds_first = 2000,
  l_mds_request,
  l_mds_reply,
  l_mds_reply_latency,
```

這些計數器反映 MDS 的主要工作就是持續處理 metadata request / reply，而不是資料區塊寫入本身。

## MDS 狀態機：從 standby 到 active

MDS 的狀態明確定義在 `src/mds/MDSMap.h`。其中包含：

- `STATE_STANDBY`
- `STATE_STANDBY_REPLAY`
- `STATE_REPLAY`
- `STATE_RESOLVE`
- `STATE_RECONNECT`
- `STATE_REJOIN`
- `STATE_CLIENTREPLAY`
- `STATE_ACTIVE`
- `STATE_STOPPING`

```cpp
// 檔案: ceph/src/mds/MDSMap.h
STATE_STANDBY  = CEPH_MDS_STATE_STANDBY,
STATE_STANDBY_REPLAY = CEPH_MDS_STATE_STANDBY_REPLAY,
STATE_REPLAY = CEPH_MDS_STATE_REPLAY,
STATE_RESOLVE = CEPH_MDS_STATE_RESOLVE,
STATE_RECONNECT = CEPH_MDS_STATE_RECONNECT,
STATE_REJOIN = CEPH_MDS_STATE_REJOIN,
STATE_CLIENTREPLAY = CEPH_MDS_STATE_CLIENTREPLAY,
STATE_ACTIVE = CEPH_MDS_STATE_ACTIVE,
```

`MDSRank.h` 也提供對應 helper：`is_standby()`、`is_replay()`、`is_standby_replay()`、`is_reconnect()`、`is_rejoin()`、`is_active()`，顯示這些狀態不是文件概念，而是執行期決策依據。

### 常見狀態如何理解

| 狀態 | 意義 |
|---|---|
| `up:standby` | daemon 已啟動，等待被指派 rank |
| `up:standby-replay` | 追隨 active rank 的 journal，準備快速接手 |
| `up:replay` | 故障後重掃 journal，重建 metadata 狀態 |
| `up:reconnect` | 等待 client 重新連回 |
| `up:rejoin` | 重新加入分散式 metadata cache |
| `up:active` | 正式服務 CephFS metadata 請求 |

## Dynamic Subtree Partitioning：多個 MDS 如何分工

CephFS 能做多 active MDS，關鍵不是把整棵目錄樹硬切，而是靠 **dynamic subtree partitioning** 動態切分熱門目錄子樹。

從 `src/mds/CDir.h` 可以看到多個與 subtree 相關的狀態，例如 `PIN_SUBTREE`、`PIN_SUBTREETEMP`，以及 `is_subtree_root()` 這類方法，代表 CephFS 會把目錄快取樹中的某些節點當成**可遷移的子樹邊界**。

這帶來兩個效果：

1. 熱門路徑可以分散到不同 active MDS 上。
2. failover 或 rebalance 時，不必搬動整個 filesystem namespace。

可以簡化理解如下：

```text
// 檔案: docs-site/ceph/mds.md
/
├── home/        -> MDS rank 0
├── project/     -> MDS rank 1
└── shared/team/ -> 視負載再切出 subtree
```

也就是說，MDS 擴展性來自「metadata subtree 的動態分工」，不是單純 round-robin 派送請求。

## SessionMap：追蹤客戶端 session

`src/mds/SessionMap.h` 用來管理連到 MDS 的 client session。這對 CephFS 很重要，因為 MDS 必須知道：

- 哪些 client 仍在線
- 哪些 capability 已發放給誰
- failover 後哪些 session 需要 reconnect 或回收

沒有 session 管理，MDS 就無法安全地處理 cache consistency、cap revoke 與 client recovery。

## CDir / CDentry：metadata 快取樹的基本構件

CephFS 的 namespace cache 並不是抽象概念，而是由一組 C++ 結構具體承載：

- `CDir.h`：目錄片段（directory fragment）與 subtree 邊界
- `CDentry.h`：目錄項目（dentry）

因此 MDS 在處理 `lookup`、`readdir`、`rename`、`unlink` 時，實際上會在這些快取物件上操作，再決定哪些內容需要寫 journal、同步到 backing store、或跨 rank 協調。

## Journal 與 Recovery

MDS 是高狀態、強互動的 metadata 服務，因此故障後不能只靠背景掃描慢慢猜回狀態。這也是為什麼 `MDSMap` 明確定義：

- `STATE_REPLAY`：掃描 journal
- `STATE_RESOLVE`：釐清分散式操作
- `STATE_RECONNECT`：等待 client 回連
- `STATE_REJOIN`：重新加入 metadata cache 拓撲

這條恢復路徑說明了 MDS recovery 的本質：

1. 先從 journal 重放已知 metadata 變更。
2. 再處理故障瞬間未完成的跨節點操作。
3. 接著重建 client 與 cache 關係。
4. 最後才回到 `up:active` 對外服務。

```text
// 檔案: docs-site/ceph/mds.md
失效或接手
   |
   v
replay journal
   |
   v
resolve 分散式操作
   |
   v
reconnect clients
   |
   v
rejoin cache / subtree
   |
   v
up:active
```

::: warning 為什麼 MDS failover 較複雜
OSD 的重建重點是資料副本完整性；MDS 的重建重點則是 metadata 操作語意、client session 與分散式 cache 關係，因此狀態轉換通常更細緻。
:::

## Beacon：MDS 對外宣告生命跡象

`src/mds/Beacon.h` 定義了 MDS 的 heartbeat / beacon 邏輯。Monitor 會根據 beacon 了解：

- 哪個 daemon 還活著
- 它宣告自己處於哪個狀態
- 是否需要觸發 rank failover 或重排

因此 Beacon 對 MDS 而言，就像是把本地狀態機結果持續同步給控制平面。

## MDS 與其他元件的關係

```text
// 檔案: docs-site/ceph/mds.md
Client
  |
  v
+-------------------+
|        MDS        |
| inode / dentry /  |
| session / subtree |
+---------+---------+
          |
          v
+-------------------+
|    RADOS / OSD    |
| file data objects |
+-------------------+
```

MDS 讓 CephFS 看起來像檔案系統；OSD 則讓 Ceph 最終有地方存放物件。兩者缺一不可。

## 關鍵原始碼索引

- `ceph/src/mds/MDSRank.h` — `MDSRank` 類別與 perf counters（如 `l_mds_request`、`l_mds_reply`）
- `ceph/src/mds/MDSMap.h` — MDS rank / daemon 狀態定義
- `ceph/src/mds/SessionMap.h` — client session 管理
- `ceph/src/mds/CDir.h`、`ceph/src/mds/CDentry.h` — metadata cache / subtree 結構
- `ceph/src/mds/Beacon.h` — MDS heartbeat / beacon

## 相關章節

::: info 延伸閱讀
- 共識、叢集地圖與 CephX 請閱讀 [Ceph — Monitor (MON) 詳解](./monitor)
- 物件資料存放與 recovery/backfill 請閱讀 [Ceph — OSD 詳解](./osd)
- 指標蒐集、dashboard 與 cephadm 請閱讀 [Ceph — Manager (MGR) 與模組系統](./manager)
:::
