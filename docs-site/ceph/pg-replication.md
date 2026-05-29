---
layout: doc
title: Ceph — PG 機制與複製策略
---

# PG 機制與複製策略

PG（Placement Group，放置群組）是 Ceph 分散式儲存中一個關鍵的間接層。它把「物件 → OSD」的映射問題分解為兩個步驟：**物件 → PG**，**PG → OSD**，讓 Ceph 能在不做大規模資料搬移的情況下應對節點的加入、退出與故障。

::: tip 為什麼要有 PG？
如果每個物件直接對應 OSD，OSD 數量變動時每個物件的位置都要重新計算，overhead 極大。PG 作為中間層，讓 CRUSH 只需要計算「PG 放哪些 OSD」，再由 PG 批次管理其中所有物件。
:::

## 物件 → PG → OSD 映射

整個流程分為兩步：

```text
物件名稱 → hash → PG ID
                      ↓
              CRUSH(PG ID, pool, rule) → [osd.3, osd.17, osd.42]
```

### 步驟 1：物件 → PG

```text
pg_id = pool_id + "." + hex(hash(object_name) % pg_num)
```

例如 object `foo` 在 pool 1（pg_num=128）中：

```text
hash("foo") % 128 = 42
pg_id = 1.2a
```

### 步驟 2：PG → OSD（CRUSH）

CRUSH 以 `pg_id` 為 seed，根據 pool 的 CRUSH rule，從 CRUSH map 計算出目標 OSD 列表：

```text
CRUSH(1.2a, rule=replicated_rule) → [osd.3, osd.17, osd.42]
osd.3  → primary（處理讀寫請求）
osd.17 → replica 1
osd.42 → replica 2
```

## PG 在原始碼中的實作

```cpp
// 檔案: src/osd/PG.h
class PG : public DoutPrefixProvider,
           public PeeringState::PeeringListener,
           public Scrub::PgScrubBeListener {
    // PG 狀態機管理
    // peering, recovery, scrubbing
    spg_t pg_id;
    ...
};
```

每個 PG 在 OSD 上以一個 `PG` 物件表示，管理其生命週期中的所有狀態轉換。

## PG 狀態機

PG 的狀態非常豐富，常見的有：

| 狀態 | 說明 |
|------|------|
| `active+clean` | 正常狀態，所有副本就緒 |
| `active+degraded` | 有副本缺失，但主副本正常可讀寫 |
| `active+undersized` | 副本數少於 min_size |
| `peering` | OSD 重啟或故障後重新協商 PG 狀態 |
| `active+remapped` | PG 正在搬移到新 OSD |
| `active+backfilling` | 正在複製完整資料到新 OSD |
| `active+recovering` | 正在恢復缺失的物件 |
| `inactive` | PG 不可用（無法確立 acting set） |
| `stale` | Monitor 未收到 PG 狀態更新 |

```text
PG 狀態轉換（簡化）：

  OSD 啟動
      ↓
  Peering（協商哪些 OSD 構成 acting set，確認 PG log）
      ↓
  Active（可處理 I/O）
      ↓
  Active+Clean（所有副本完整）
       |
       +→ Active+Degraded（副本缺失）→ Active+Recovering
       +→ Active+Backfilling（新 OSD 加入）
```

## Peering 過程

Peering 是 PG 在 acting set 成員變化後重新建立一致性的過程：

1. **Primary OSD 確立**：Monitor 根據 OSDMap 選出 Primary
2. **收集 PG log**：Primary 向所有 replica 收集各自的 PG log
3. **確定 authoritative log**：找出最完整的 log 作為權威
4. **Missing list**：計算哪些物件還缺副本
5. **宣告 Active**：所有條件滿足後，PG 進入 active 狀態

::: info PeeringState
Peering 的狀態機實作在 `src/osd/PeeringState.h` 的 `class PeeringState`，是一個完整的狀態機框架。
:::

## Acting Set vs Up Set

這兩個概念容易混淆：

| 名稱 | 說明 |
|------|------|
| **Up set** | CRUSH 根據當前 OSDMap 計算出的 OSD 列表 |
| **Acting set** | 實際負責處理 PG 請求的 OSD 列表 |

通常兩者相同。當 PG 正在搬移（remapped）時，acting set 可能指向舊的 OSD，直到 backfill 完成才切換到 up set。

## 複製策略：Replicated vs Erasure Coding

### Replicated Pool（預設）

```text
寫入流程：
Client → Primary OSD
              ↓（同步寫）
       Replica OSD 1, Replica OSD 2
              ↓（ack）
       Primary → Client（ack）
```

- 每個物件存 size 份完整副本（預設 size=3, min_size=2）
- 讀取只需 primary，效能高
- 空間利用率：1/size（預設 33%）

### Erasure Coding Pool

```text
k 個 data chunks + m 個 parity chunks
任意 k 個 chunk 可重建完整資料
```

- 空間利用率：k/(k+m)，例如 4+2 = 66.7%
- 讀取需要至少 k 個 chunk
- 實作在 `src/osd/ECBackend.h`

```cpp
// 檔案: src/osd/ECBackend.h
class ECBackend : public PGBackend {
    // Erasure coding I/O 路徑
    // 使用 ec_impl (jerasure, isa, etc.)
};
```

## PG 分裂與合併

`pg_num` 可以在線上增加（PG 分裂），每次分裂舊 PG 拆成 2 個：

```bash
ceph osd pool set <pool> pg_num 256      # 先增加 pg_num
ceph osd pool set <pool> pgp_num 256     # 再調整 pgp_num 觸發資料遷移
```

::: warning pg_num vs pgp_num
`pg_num` 決定映射計算用的 PG 數量，`pgp_num` 決定 CRUSH 計算時實際使用的數量。先調整 pg_num、後調整 pgp_num 可以控制資料搬移的速度。
:::

## 常用 PG 診斷指令

```bash
# 查看所有 pool 的 PG 狀態總覽
ceph pg stat

# 查看特定 PG 詳情
ceph pg 1.2a query

# 找出 degraded/stuck 的 PG
ceph pg dump_stuck

# 查看 PG 到 OSD 的映射
ceph pg map 1.2a

# 強制重新 peering（謹慎使用）
ceph pg repair 1.2a
```

## 相關頁面

::: info 相關章節
- [CRUSH 演算法深度分析](./crush) — PG 到 OSD 的映射計算
- [OSD 詳解](./osd) — OSD 如何管理 PG
- [整體架構概述](./architecture) — RADOS 整體設計
:::
