---
layout: doc
title: Ceph — CRUSH 演算法深度分析
---

# CRUSH 演算法深度分析

CRUSH（Controlled Replication Under Scalable Hashing）是 Ceph 最核心的創新之一。它讓每個客戶端都能**自行計算**資料落在哪些 OSD，而不需要查詢中央索引表，大幅提升了系統的可擴展性。

::: tip 核心設計哲學
CRUSH 的本質是「在拓撲限制（failure domain）與權重之下，做可重現的偽隨機放置」。相同的輸入（PG ID + CRUSH map）永遠得到相同的輸出（OSD 列表），因此叢集節點之間不需要額外通訊協調。
:::

## 為什麼需要 CRUSH？

傳統的分散式儲存靠中央 metadata server 記錄「哪個物件在哪個節點」，這個架構在規模擴大後會成為瓶頸。Ceph 的 `src/crush/crush.h` 開頭就點明了設計目標：

```cpp
// 檔案: src/crush/crush.h
/*
 * CRUSH is a pseudo-random data distribution algorithm that
 * efficiently distributes input values (typically, data objects)
 * across a heterogeneous, structured storage cluster.
 */

#define CRUSH_MAGIC 0x00010000ul
#define CRUSH_MAX_DEPTH 10       /* max crush hierarchy depth */
#define CRUSH_MAX_RULES (1<<8)   /* max crush rule id */
```

`CRUSH_MAX_DEPTH 10` 表示 hierarchy 最多 10 層（root → region → datacenter → row → rack → host → osd）。

## CRUSH Map 結構

CRUSH map 描述了叢集的實體拓撲，分為三個部分：

### 1. Devices（葉節點）

對應到實際的 OSD。每個 device 有一個整數 ID 和一個權重（weight），權重通常對應磁碟容量（以 TB 為單位 × 65536）。

### 2. Buckets（內部節點）

Bucket 代表邏輯或實體上的分組層級：

```text
root
└── datacenter
    └── rack
        └── host
            └── osd.0, osd.1, ...
```

常見的 bucket 類型：`root`、`datacenter`、`region`、`row`、`rack`、`host`、`chassis`

### 3. Rules（放置規則）

Rule 定義了如何遍歷這棵樹來選出目標 OSD，是 CRUSH 的「行動指令」。

## crush_rule_step：最小執行單元

每條 rule 由一系列的 `step` 組成，每個 step 只有三個欄位：

```cpp
// 檔案: src/crush/crush.h
struct crush_rule_step {
    __u32 op;    // opcode
    __s32 arg1;  // 第一個參數（依 op 而定）
    __s32 arg2;  // 第二個參數（依 op 而定）
};
```

對應的 opcode 定義：

```cpp
// 檔案: src/crush/crush.h
enum crush_opcodes {
    CRUSH_RULE_NOOP = 0,
    CRUSH_RULE_TAKE = 1,               /* arg1 = 起始 bucket */
    CRUSH_RULE_CHOOSE_FIRSTN = 2,      /* arg1 = 選幾個, arg2 = bucket type */
    CRUSH_RULE_CHOOSE_INDEP = 3,
    CRUSH_RULE_EMIT = 4,
    CRUSH_RULE_CHOOSELEAF_FIRSTN = 6,  /* 選 bucket 再取 leaf */
    CRUSH_RULE_CHOOSELEAF_INDEP = 7,
};
```

一條典型的 replicated pool rule 等效的 step 序列：

```text
TAKE root
CHOOSELEAF_FIRSTN 3 type host   ← 選 3 個不同 host 下的 leaf OSD
EMIT
```

## crush_rule 完整結構

```cpp
// 檔案: src/crush/crush.h
struct crush_rule {
    __u32 len;
    __u8  __unused_was_rule_mask_ruleset;
    __u8  type;
    __u8  deprecated_min_size;
    __u8  deprecated_max_size;
    struct crush_rule_step steps[0];
};

enum crush_rule_type {
    CRUSH_RULE_TYPE_REPLICATED = 1,
    CRUSH_RULE_TYPE_ERASURE = 3,
};
```

`type` 欄位區分了複製池（1）和 erasure code 池（3），這讓 CRUSH 能針對不同的副本策略做不同的放置計算。

## CrushWrapper：C++ 封裝

在 Ceph 實作中，CRUSH map 的操作透過 `CrushWrapper` 統一封裝：

```cpp
// 檔案: src/crush/CrushWrapper.h
class CrushWrapper {
    // 封裝 struct crush_map
    // 提供 encode/decode, add/remove bucket,
    // do_rule (執行放置計算) 等介面
};
```

`CrushWrapper::do_rule()` 是執行 CRUSH 放置計算的核心函式，輸入 PG ID 和 rule，輸出目標 OSD 列表。

## CRUSH 演算法步驟（概念流程）

```text
輸入: pool_id, pg_seed, crush_rule, crush_map

1. TAKE:
   選擇 rule 指定的起始 bucket（通常是 root）

2. CHOOSE / CHOOSELEAF:
   對每個 replica（或 EC shard）：
   a. 用 hash(input, r) 對 bucket 中的子節點做 pseudo-random 選擇
   b. 若選到的節點 down/out，嘗試 retry（有上限）
   c. CHOOSELEAF 會遞迴到 leaf（device）為止

3. EMIT:
   輸出已選中的 OSD 列表

輸出: [primary OSD, replica1 OSD, replica2 OSD, ...]
```

::: info Failure Domain 保證
若 rule 要求 `CHOOSELEAF type=host`，CRUSH 會保證選出的 leaf OSD 不在同一台 host 上。這就是 Ceph 能自動防止單台主機故障導致資料完全不可用的原因。
:::

## 權重與資料分布

每個 OSD 的 weight 通常由磁碟容量決定（1TB ≈ 1.0）。CRUSH 在計算時會根據 weight 做加權隨機選擇，確保大容量 OSD 承載更多資料。

```bash
# 查看 CRUSH 樹狀結構
ceph osd tree

# 查看特定 pool 的 CRUSH rule
ceph osd pool get <pool-name> crush_rule

# 匯出 CRUSH map
ceph osd getcrushmap -o /tmp/crushmap
crushtool -d /tmp/crushmap -o /tmp/crushmap.txt
```

## Erasure Code 與 CRUSH

Erasure coding pool 的 rule 類型為 `CRUSH_RULE_TYPE_ERASURE = 3`，k+m 個 shard 需要落在不同的 failure domain。CRUSH 用 `CHOOSE_INDEP`（而非 FIRSTN）模式，確保即使某些 OSD 不可用，每個 shard 位置仍能獨立確定：

```text
TAKE root
CHOOSE_INDEP k+m type host
EMIT
```

::: warning INDEP vs FIRSTN
FIRSTN 模式下如果某個選擇失敗，後面的選擇會連帶移位（像排隊）。INDEP 模式每個位置獨立重試，失敗位置以 CRUSH_ITEM_NONE 填充，適用於 EC 場景。
:::

## 相關頁面

::: info 相關章節
- [整體架構概述](./architecture) — CRUSH 在系統中的位置
- [OSD 詳解](./osd) — OSD 如何使用 CRUSH map
- [PG 機制與複製策略](./pg-replication) — PG 到 OSD 的映射流程
:::
