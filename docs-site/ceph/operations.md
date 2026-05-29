---
layout: doc
title: Ceph — 日常維運
---

# Ceph — 日常維運

這一頁的目標不是列出所有 Ceph CLI，而是整理出 **每天最常用、最能對應原始碼實作邏輯** 的維運路徑：健康檢查、容量觀察、OSD / pool 管理、log 追查，以及 cephadm orchestrator 的 day-2 操作。

## 先建立一條固定巡檢路徑

建議每天都用相同順序看叢集：

1. `ceph status`
2. `ceph health detail`
3. `ceph pg stat`
4. `ceph osd df` / `ceph osd perf`
5. `ceph orch ps` / `ceph orch ls`
6. 必要時再看 `ceph log last` 或 `cephadm logs`

這個順序的好處是：先看整體，再下鑽到 PG、OSD、service 與 daemon。

## 健康檢查：先看 monitor 註冊的核心命令

`src/mon/MonCommands.h` 很適合拿來當「哪些是核心 cluster health 命令」的權威來源。

```cpp
// 檔案: src/mon/MonCommands.h
COMMAND("status", "show cluster status", "mon", "r")
COMMAND("health name=detail,type=CephChoices,strings=detail,req=false",
	"show cluster health", "mon", "r")
COMMAND("log last "
        "name=num,type=CephInt,range=1,req=false "
        "name=level,type=CephChoices,strings=debug|info|sec|warn|error,req=false "
        "name=channel,type=CephChoices,strings=*|cluster|audit|cephadm,req=false",
	"print last few lines of the cluster log",
	"mon", "r")
```

### 這三個命令各自回答什麼問題？

| 命令 | 用途 |
|---|---|
| `ceph status` | 叢集是否整體正常、有哪些 daemon / PG 摘要 |
| `ceph health detail` | 具體是哪一條 health check 失敗 |
| `ceph log last` | 近期 cluster log，特別適合看 `cephadm` channel |

如果只看 `ceph -s`，通常只知道「有問題」；真正開始排錯時，最好立刻接 `health detail` 與 log。

## PG 與 OSD 狀態：確認問題是在資料面還是控制面

`src/mgr/MgrCommands.h` 註冊了很多日常觀察命令：

```cpp
// 檔案: src/mgr/MgrCommands.h
COMMAND("pg stat", "show placement group status.", "pg", "r")
COMMAND("osd perf", "print dump of OSD perf summary stats", "osd", "r")
COMMAND("osd df ...", "show OSD utilization", "osd", "r")
COMMAND("osd reweight-by-utilization ...",
        "reweight OSDs by utilization ...", "osd", "rw")
```

這些命令最適合回答：

- PG 是否 `degraded`、`undersized`、`inactive`
- 某些 OSD 是否延遲特別高
- 是否有容量傾斜
- 是否需要以 utilization 為基準做 reweight

### 建議判讀方式

- `pg stat` 異常：優先看 peering、backfill、recovery 進度
- `osd perf` 異常：懷疑磁碟、網路、host 負載不均
- `osd df` 異常：懷疑 CRUSH 分布、pool 熱點或資料成長偏斜

## Pool 管理：建立、刪除、配額

`MonCommands.h` 也清楚註冊了 pool 生命週期操作：

```cpp
// 檔案: src/mon/MonCommands.h
COMMAND("osd pool create ...", "create pool", "osd", "rw")
COMMAND("osd pool rm ...", "remove pool", "osd", "rw")
COMMAND("osd pool set ...", "set pool parameter <var> to <val>", "osd", "rw")
COMMAND("osd pool set-quota ...", "set object or byte limit on pool", "osd", "rw")
```

### 實務建議

- 新建 pool 前先想清楚：用途、replicated / erasure、CRUSH rule、PG autoscale
- 刪除 pool 前務必確認上層應用是否已停用
- `set-quota` 很適合避免單一租戶或服務把整個叢集吃滿

::: warning `osd pool rm` 是高風險操作
原始碼要求多個 `yes_i_really_really_mean_it` 類型參數，不是多此一舉；這反映了 Ceph 把 pool 刪除視為危險且不可逆的動作。
:::

## OSD 管理：in / out / reweight / CRUSH

常見 OSD 動作也都在 `MonCommands.h`：

```cpp
// 檔案: src/mon/MonCommands.h
COMMAND("osd out ...", "set osd(s) ... out", "osd", "rw")
COMMAND("osd in ...", "set osd(s) ... in", "osd", "rw")
COMMAND("osd reweight ...", "reweight osd to 0.0 < <weight> < 1.0", "osd", "rw")
COMMAND("osd crush add ...", ...)
COMMAND("osd crush move ...", ...)
```

### 什麼時候用哪個？

- `osd out`：要把資料逐步遷出某顆 OSD
- `osd in`：恢復參與資料放置
- `osd reweight`：做更細緻的容量 / 流量調整
- `osd crush add` / `move`：修正 failure domain 或階層位置

### 常見誤區

- `out` 不等於 daemon 停掉；它代表資料放置策略改變
- `reweight` 不等於 CRUSH 權重永久重構；它較像執行期調整旋鈕
- 只看單顆 OSD 很容易誤判，最好搭配 `osd df tree` 與 pool / PG 分布一起看

## 監控：CLI 與 Dashboard 要一起看

如果只看 Dashboard，容易忽略底層命令的細節；如果只看 CLI，又會失去趨勢圖與告警聚合。比較好的做法是：

- Dashboard 看總覽、趨勢、警報、nearfull / full 風險
- CLI 看精準狀態與可操作命令

Dashboard 前端實際使用的 PromQL 包含：

- `ceph_cluster_total_used_bytes`
- `sum(rate(ceph_pool_wr[1m]))`
- `sum(rate(ceph_pool_rd[1m]))`
- `avg_over_time(ceph_osd_apply_latency_ms[1m])`
- `avg_over_time(ceph_osd_commit_latency_ms[1m])`

因此當你在 Dashboard 上看到 IOPS 或 latency 異常時，可以直接意識到問題已經下探到 pool / OSD 層級，而不是單純 UI 顯示錯誤。

## Log 管理：cluster log 與 daemon journald 是兩條線

### cluster log

當你要看整個叢集最近發生什麼事，優先使用：

- `ceph log last`
- `ceph log last <num> <level> cephadm`

這很適合找：

- cephadm reconcile 失敗
- audit / cluster 層級事件
- 最近 health warning 的上下文

### daemon journald

當你要看某個 daemon 容器自身輸出，則應切到 `cephadm logs`。`src/cephadm/cephadm.py` 明確註冊了這個子命令：

```python
# 檔案: src/cephadm/cephadm.py
parser_logs = subparsers.add_parser(
    'logs', help='print journald logs for a daemon container')
parser_logs.set_defaults(func=command_logs)
parser_logs.add_argument('--fsid', help='cluster FSID')
parser_logs.add_argument('--dry-run', action='store_true')
parser_logs.add_argument('command', nargs='*', help='additional journalctl args')
```

這代表 `cephadm logs` 本質上是在幫你包裝 daemon 對應的 journald 查詢，而不是另一套獨立日誌系統。

## cephadm day-2：host 維護與升級

日常維運不只資料面，還包括 orchestrator 管理面。從 `src/pybind/mgr/orchestrator/module.py` 可以看到常見操作：

- `ceph orch host add`
- `ceph orch host drain`
- `ceph orch host maintenance enter`
- `ceph orch host maintenance exit`
- `ceph orch daemon add osd`
- `ceph orch upgrade check`
- `ceph orch upgrade start`
- `ceph orch upgrade status`
- `ceph orch upgrade pause`
- `ceph orch upgrade resume`

### 維護主機的推薦流程

1. 先確認 `ceph status` 與 `pg stat` 沒有已存在的大型異常
2. `ceph orch host drain <host>`
3. 視情況進入 maintenance
4. 完成硬體或系統維護後再 exit maintenance
5. 回頭確認 PG、OSD、service 是否回到穩定狀態

## 三個高頻故障排查模式

### 1. 容量快滿

觀察順序：

1. `ceph osd df tree`
2. `ceph osd reweight-by-utilization test`
3. 看 Dashboard nearfull / full 指標
4. 檢查熱 pool、資料成長趨勢與 CRUSH 分布

### 2. PG 長時間 degraded / undersized

觀察順序：

1. `ceph health detail`
2. `ceph pg stat`
3. `ceph osd tree` / `ceph orch ps`
4. `ceph log last`
5. 目標 daemon 的 `cephadm logs`

### 3. 升級或 reconcile 卡住

觀察順序：

1. `ceph orch upgrade status`
2. `ceph orch ps`
3. `ceph log last ... cephadm`
4. `cephadm logs --name mgr.<id>` 或相關 daemon logs

## 最後的實務建議

- 先用 `status` / `health detail` 確認是全域問題還是局部問題
- 再用 `pg stat` / `osd perf` / `osd df` 切到資料面
- 如果涉及 service 生命週期，再切到 `ceph orch` 與 `cephadm logs`

把這個順序固定下來，你會比背一堆命令更快找到問題。

::: info 相關章節
- [Ceph — Dashboard](/ceph/dashboard)
- [Ceph — cephadm 深入分析](/ceph/cephadm)
- [Ceph — 部署架構與 cephadm](/ceph/deployment)
- [Ceph — 故事驅動式學習路徑](/ceph/learning-path/story)
:::
