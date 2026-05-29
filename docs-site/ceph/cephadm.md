---
layout: doc
title: Ceph — cephadm 深入分析
---

# Ceph — cephadm 深入分析

如果把 `deployment.md` 視為 Ceph 的安裝入口，那這一頁要回答的問題就是：**叢集起來之後，cephadm 到底如何長期管理 host、daemon、service 與升級流程？**

從原始碼來看，cephadm 並不是單純的 shell installer，而是由三個層次組成：

1. `src/cephadm/cephadm.py`：本機端 bootstrap / prepare / logs 等命令入口。
2. `src/pybind/mgr/cephadm/module.py`：`ceph-mgr` 內的 orchestrator 模組。
3. `src/pybind/mgr/orchestrator/module.py`：`ceph orch ...` CLI 的共用命令註冊層。

## cephadm 的心智模型

<pre>
cephadm bootstrap
        |
        v
建立初始 mon / mgr + dashboard + ssh / config
        |
        v
ceph-mgr 載入 cephadm module
        |
        v
使用 ServiceSpec / PlacementSpec 描述目標狀態
        |
        v
背景 serve loop 持續 reconcile host / daemon / service
        |
        v
透過 ceph orch 完成擴容、維護、升級與監控整合
</pre>

::: tip 關鍵觀察
cephadm 真正重要的不是「把容器跑起來」，而是「把叢集持續拉回宣告式目標狀態」。
:::

## bootstrap 與容器執行環境

初始叢集入口在 `src/cephadm/cephadm.py`。`bootstrap` parser 明確定義了 dashboard、SSH、監控堆疊、registry 與網路等 day-1 參數。

```python
# 檔案: src/cephadm/cephadm.py
parser_bootstrap = subparsers.add_parser(
    'bootstrap', help='bootstrap a cluster (mon + mgr daemons)')
parser_bootstrap.set_defaults(func=command_bootstrap)
parser_bootstrap.add_argument('--mon-ip', help='mon IP')
parser_bootstrap.add_argument('--initial-dashboard-user', default='admin')
parser_bootstrap.add_argument('--skip-dashboard', action='store_true')
parser_bootstrap.add_argument(
    '--skip-monitoring-stack',
    action='store_true',
    help='Do not automatically provision monitoring stack (prometheus, grafana, alertmanager, node-exporter)')
parser_bootstrap.add_argument('--apply-spec', help='Apply cluster spec after bootstrap')
```

這段定義說明了兩件事：

- bootstrap 不只建立 `mon` / `mgr`，也會把 dashboard 與 monitoring stack 納入 day-1 流程。
- `--apply-spec` 代表 Ceph 一開始就把「後續宣告式管理」當成標準操作模式。

### Podman 優先，必要時可切 Docker

容器引擎的選擇在 `src/cephadm/cephadmlib/container_engines.py`：

```python
# 檔案: src/cephadm/cephadmlib/container_engines.py
class Podman(ContainerEngine):
    EXE = 'podman'

class Docker(ContainerEngine):
    EXE = 'docker'

CONTAINER_PREFERENCE = (Podman, Docker)  # prefer podman to docker
```

而 `command_prepare_host()` 會先驗證容器引擎與 `lvm2`：

```python
# 檔案: src/cephadm/cephadm.py
logger.info('Verifying podman|docker is present...')
check_container_engine(ctx)
```

因此在實務上，可以把 cephadm 理解成「以 Podman 為優先的容器化 host preparation + daemon lifecycle framework」。

## 真正的核心：CephadmOrchestrator

cephadm 的控制中樞在 `src/pybind/mgr/cephadm/module.py`。

```python
# 檔案: src/pybind/mgr/cephadm/module.py
class CephadmOrchestrator(orchestrator.Orchestrator, MgrModule):
    CLICommand = CephadmCLICommand
    _STORE_HOST_PREFIX = "host"
    instance = None
    NOTIFY_TYPES = [NotifyType.mon_map, NotifyType.pg_summary]
```

這裡可以讀出三個重點：

- 它是 `MgrModule`，所以 cephadm 的長期控制面其實跑在 `ceph-mgr` 內。
- 它同時實作 `orchestrator.Orchestrator`，所以能掛進 `ceph orch` 指令系統。
- 它訂閱 `mon_map`、`pg_summary` 等通知，代表 cephadm 不是被動腳本，而是會持續感知叢集狀態變化。

### `cli.py` 其實很薄

`src/pybind/mgr/cephadm/cli.py` 幾乎只做一件事：建立 cephadm 專用的 CLI registry subtype。這表示大量命令定義其實集中在 orchestrator 共用層，而不是散落在一堆 ad-hoc script 裡。

## ServiceSpec 與 PlacementSpec：宣告式管理的資料模型

Ceph 用 `src/python-common/ceph/deployment/service_spec.py` 來定義 service model。這是 cephadm 能統一管理 `mon`、`mgr`、`osd`、`rgw`、`grafana`、`prometheus` 等服務的基礎。

### PlacementSpec 負責「放哪裡」

`PlacementSpec` 支援 `hosts`、`label`、`count`、`count_per_host`、`host_pattern` 等欄位；這讓 cephadm 可以同時表達：

- 指定某些主機
- 依 label 分群部署
- 每台主機跑幾個 daemon
- 用 pattern 做大範圍選擇

### ServiceSpec 負責「要什麼服務」

`ServiceSpec` 建構子中常見欄位包括：

| 欄位 | 用途 |
|---|---|
| `service_type` | 服務類型，如 `mon`、`mgr`、`osd`、`rgw`、`prometheus` |
| `service_id` | 同類服務的識別名稱 |
| `placement` | 部署位置與數量策略 |
| `config` | 服務專屬設定 |
| `unmanaged` | 是否暫停由 orchestrator 調和 |
| `networks` | 綁定網段 |
| `extra_container_args` | 額外容器啟動參數 |
| `custom_configs` | 額外設定檔片段 |

另外，`service_name()` 會把 `service_type` 與 `service_id` 組成實際名稱，這也是許多 `ceph orch ls` / `ceph orch ps` 輸出的基礎識別方式。

## `ceph orch` 命令從哪裡來？

很多維運者會把 `cephadm` 與 `ceph orch` 混在一起。從原始碼看，這兩者關係可以這樣理解：

- `cephadm`：本機端工具，偏向 bootstrap、host preparation、daemon logs。
- `ceph orch`：叢集內 orchestrator CLI，偏向宣告式操作與長期管理。

在 `src/pybind/mgr/orchestrator/module.py` 可以看到大量命令註冊，例如：

- `orch host add`
- `orch daemon add osd`
- `orch host drain`
- `orch host maintenance enter`
- `orch host maintenance exit`
- `orch upgrade check`
- `orch upgrade start`
- `orch upgrade pause`
- `orch upgrade resume`
- `orch resume`

### day-1 常見流程

1. `cephadm bootstrap --mon-ip <ip>`
2. `ceph orch host add <host> <addr>`
3. `ceph orch daemon add osd <host>:<device>` 或套用 OSD spec
4. `ceph orch apply ...` 逐步把服務模型補齊

### day-2 常見流程

- **擴容**：加 host、加 OSD、加 `mgr` / `rgw` / `mds`
- **維護**：`host drain` 後進入 maintenance
- **升級**：`upgrade check` → `upgrade start` → `upgrade status`
- **中斷恢復**：透過 `orch resume` 或 `upgrade resume` 繼續 reconcile / upgrade pipeline

::: warning 不要把 `ceph orch` 當成單次命令集合
它背後依賴的是 cephadm module 的狀態、inventory、cache 與背景調和邏輯；如果 manager module 狀態異常，CLI 看起來像「命令失敗」，本質上往往是 orchestrator 狀態失衡。
:::

## service discovery 與監控整合

使用者常以為 cephadm 只管 Ceph daemon，但 `src/pybind/mgr/cephadm/services/service_discovery.py` 顯示它也負責監控整合的 discovery 端點。

這個模組會提供像是：

- `/prometheus/sd-config`
- `/prometheus/rules`

它的用途是讓 Prometheus、Alertmanager、node-exporter 等服務可以由 cephadm 控制面動態發現與下發規則，而不是要求管理者手動維護大量靜態 target 清單。

## Agent 與遠端執行

`src/pybind/mgr/cephadm/agent.py` 裡的 `AgentEndpoint` 與 `NodeProxyEndpoint` 顯示，cephadm 除了 SSH 之外，也有以 CherryPy 端點承接 agent / node proxy 資訊的能力，並且包含 TLS / cert 驗證流程。

這代表 Ceph 團隊在設計上，已經把「host 資訊收集與代理通訊」納入 orchestrator 架構，而不只是遠端執行幾個 shell 命令。

## 維運時最值得記住的三件事

### 1. cephadm 的真相是「MGR module + spec + reconcile」

如果只記得 `cephadm bootstrap`，很容易把 Ceph 誤解成一次性安裝器。真正長期運作的，是 `CephadmOrchestrator` 與其背景調和流程。

### 2. Host / daemon / service 是三個不同層次

- host：機器是否已納入 inventory
- daemon：單一 `mon.a`、`osd.3`、`mgr.x`
- service：一組有共同 spec 的 daemon 集合

排錯時一定要分清楚自己是在看哪個層次。

### 3. 先看 spec，再看實際 daemon

當叢集狀態不如預期時，先問：

- spec 想要什麼？
- inventory 看到什麼？
- orchestrator 為什麼沒有 reconcile 成功？

這通常比直接登入主機查容器更快找到根因。

## 推薦閱讀順序

1. 先看 [部署架構與 cephadm](/ceph/deployment) 建立全貌。
2. 再看本頁，把 `cephadm` 與 `ceph orch` 的責任邊界釐清。
3. 最後接到 [Dashboard](/ceph/dashboard) 與 [日常維運](/ceph/operations)，把控制面與觀測面串起來。

::: info 相關章節
- [Ceph — 部署架構與 cephadm](/ceph/deployment)
- [Ceph — Dashboard](/ceph/dashboard)
- [Ceph — 日常維運](/ceph/operations)
- [Ceph — 學習路徑入口](/ceph/learning-path/)
:::
