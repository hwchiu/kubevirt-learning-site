---
layout: doc
title: Ceph — 部署架構與 cephadm
---

# Ceph — 部署架構與 cephadm

在現代 Ceph 版本中，**cephadm** 是官方主推的部署與生命週期管理工具。它的核心思路不是讓管理者手動在每台機器上安裝 daemon，而是以 **container-based** 的方式，把 MON、MGR、OSD、RGW、監控元件與各類輔助服務轉成可宣告、可調和的 service spec。

## 為什麼是 cephadm？

cephadm 有三個關鍵特性：

- **容器化部署**：Ceph daemon 以容器執行，降低主機環境差異。
- **宣告式管理**：以 service spec 描述「想要的叢集狀態」。
- **內建 orchestrator**：透過 ceph-mgr 的 cephadm module 長期調和主機、daemon 與 service。

```python
# 檔案: src/pybind/mgr/cephadm/module.py
class CephadmOrchestrator(orchestrator.Orchestrator, MgrModule):
    CLICommand = CephadmCLICommand
    _STORE_HOST_PREFIX = "host"

    instance = None
    NOTIFY_TYPES = [NotifyType.mon_map, NotifyType.pg_summary]
    NATIVE_OPTIONS = []  # type: List[Any]
    MODULE_OPTIONS = [
        Option(
            'ssh_config_file',
```

從 `CephadmOrchestrator` 可以看出，cephadm 並不是單純的安裝腳本，而是整合在 `ceph-mgr` 裡的 orchestrator。

```python
# 檔案: src/pybind/mgr/cephadm/serve.py
from ceph.deployment.service_spec import (
    ArgumentList,
    ArgumentSpec,
    CustomContainerSpec,
    PlacementSpec,
    RGWSpec,
    ServiceSpec,
    IngressSpec,
)

class CephadmServe:
    """
    This module contains functions that are executed in the
    serve() thread. Thus they don't block the CLI.
```

`CephadmServe` 代表 cephadm 會在背景執行調和迴圈，持續把實際叢集狀態拉向 spec 所描述的目標狀態。

::: tip 實務觀點
cephadm 比較像「Ceph 內建的 orchestrator + 容器部署框架」，而不是一次性安裝器。
:::

## cephadm module 的實作位置

官方 cephadm manager module 位於 `src/pybind/mgr/cephadm/`，其中常見檔案包括：

- `module.py`：orchestrator 入口、CLI handler、service apply 邏輯
- `serve.py`：背景調和迴圈與 daemon refresh
- `schedule.py`：主機選擇與排程
- `inventory.py`：主機與裝置盤點
- `ssh.py`：遠端命令與 SSH 管理
- `services/`：各種 daemon / service 類型的部署細節
- `upgrade.py`：升級流程控制

這個目錄本身就反映了 cephadm 的責任範圍：**不只部署，還包含 inventory、排程、調和、升級與服務生命週期管理**。

## Service Spec：cephadm 的宣告式核心

Ceph 的 service spec 定義在 `src/python-common/ceph/deployment/service_spec.py`。這個檔案是 cephadm 能用統一模型處理 `mon`、`mgr`、`mds`、`osd`、`rgw`、監控堆疊等服務的基礎。

### PlacementSpec

`PlacementSpec` 用來描述 daemon 應該部署到哪些 host、label 或 host pattern。

```python
# 檔案: src/python-common/ceph/deployment/service_spec.py
class PlacementSpec(object):
    """
    For APIs that need to specify a host subset
    """

    def __init__(self,
                 label: Optional[str] = None,
                 hosts: Union[List[str], List[HostPlacementSpec], None] = None,
                 count: Optional[int] = None,
                 count_per_host: Optional[int] = None,
                 host_pattern: HostPatternType = None,
                 ):
```

這表示 cephadm 可以用 `hosts`、`label`、`count`、`count_per_host`、`host_pattern` 等方式描述服務佈署目標。

### ServiceSpec

`ServiceSpec` 則定義服務類型、service id、placement、network 與額外參數。

```python
# 檔案: src/python-common/ceph/deployment/service_spec.py
class ServiceSpec(object):
    """
    Details of service creation.

    Request to the orchestrator for a cluster of daemons
    such as MDS, RGW, iscsi gateway, nvmeof gateway, MONs, MGRs, Prometheus

    This structure is supposed to be enough information to
    start the services.
    """

    KNOWN_SERVICE_TYPES = [
        'agent',
        'alertmanager',
        'ceph-exporter',
        'cephfs-mirror',
        'container',
        'crash',
        'elasticsearch',
        'grafana',
        'ingress',
        'mgmt-gateway',
        'oauth2-proxy',
        'iscsi',
        'jaeger-agent',
        'jaeger-collector',
        'jaeger-query',
        'jaeger-tracing',
        'loki',
        'mds',
        'mgr',
        'mon',
        'nfs',
        'node-exporter',
        'node-proxy',
        'nvmeof',
        'osd',
        'prometheus',
        'promtail',
        'alloy',
        'rbd-mirror',
        'rgw',
        'smb',
        'snmp-gateway',
    ]
```

這份清單直接揭露 cephadm 能管理的服務面向：不只 Ceph 核心 daemon，也包含 gateway、監控與延伸服務。

## cephadm 如何套用 spec？

在 cephadm module 中，服務規格最後會被送入 `_apply_service_spec()`，並為不同服務補上預設 placement。

```python
# 檔案: src/pybind/mgr/cephadm/module.py
@handle_orch_error
def apply_mon(self, spec: ServiceSpec) -> str:
    return self._apply(spec)

def _apply(self, spec: GenericSpec) -> str:
    if spec.service_type == 'host':
        return self._add_host(cast(HostSpec, spec))

    if spec.service_type == 'osd':
        self._trigger_preview_refresh(specs=[cast(DriveGroupSpec, spec)])

    return self._apply_service_spec(cast(ServiceSpec, spec))
```

```python
# 檔案: src/pybind/mgr/cephadm/module.py
def _apply_service_spec(self, spec: ServiceSpec) -> str:
    if spec.placement.is_empty():
        # fill in default placement
        defaults = {
            'mon': PlacementSpec(count=5),
            'mgr': PlacementSpec(count=2),
            'mds': PlacementSpec(count=2),
            'rgw': PlacementSpec(count=2),
            'ingress': PlacementSpec(count=2),
            'iscsi': PlacementSpec(count=1),
            'nvmeof': PlacementSpec(count=1),
            'rbd-mirror': PlacementSpec(count=2),
            'cephfs-mirror': PlacementSpec(count=1),
```

這段程式很重要，因為它說明 cephadm 的本質是「根據 spec 調和服務」，而不是逐台主機手工執行命令。

## 最小叢集需求

從高可用角度來看，最小可用 Ceph 叢集通常至少需要：

- **3 個 MON**：形成 quorum，避免單點故障
- **1 個以上 OSD**：至少要有資料落地節點；實務上通常會是多個 OSD
- **1 個 MGR**：cephadm 與 dashboard、模組功能都依賴 MGR；實務上建議 2 個

::: warning 最小可用不等於可用於正式環境
只有 1 個 OSD 的叢集可以拿來學習，但不具備真正的容錯能力。正式環境通常會同時考慮 OSD 數量、failure domain、網路分離與磁碟類型。
:::

## Bootstrap 流程概觀

Ceph 初始叢集通常從 `cephadm bootstrap` 開始。實作位於 `src/cephadm/cephadm.py`。

```python
# 檔案: src/cephadm/cephadm.py
def command_bootstrap(ctx):
    # type: (CephadmContext) -> int

    ctx.error_code = 0

    if not ctx.output_config:
        ctx.output_config = os.path.join(ctx.output_dir, CEPH_CONF)
    if not ctx.output_keyring:
        ctx.output_keyring = os.path.join(ctx.output_dir, CEPH_KEYRING)
    if not ctx.output_pub_ssh_key:
        ctx.output_pub_ssh_key = os.path.join(ctx.output_dir, CEPH_PUBKEY)
```

```python
# 檔案: src/cephadm/cephadm.py
def command_bootstrap(ctx):
    if not ctx.skip_prepare_host:
        command_prepare_host(ctx)

    logger.info('Cluster fsid: %s' % fsid)
    hostname = get_hostname()
    mon_id = ctx.mon_id or get_short_hostname()
    mgr_id = ctx.mgr_id or generate_service_id()

    (addr_arg, ipv6, mon_network) = prepare_mon_addresses(ctx)
    cluster_network, ipv6_cluster_network = prepare_cluster_network(ctx)

    config = prepare_bootstrap_config(ctx, fsid, addr_arg, ctx.image)
```

```python
# 檔案: src/cephadm/cephadm.py
(mon_key, mgr_key, admin_key, bootstrap_keyring, admin_keyring) = create_initial_keys(ctx, uid, gid, mgr_id)

monmap = create_initial_monmap(ctx, uid, gid, fsid, mon_id, addr_arg)
(mon_dir, log_dir) = prepare_create_mon(ctx, uid, gid, fsid, mon_id,
                                        bootstrap_keyring.name, monmap.name)

create_mon(ctx, uid, gid, fsid, mon_id)
wait_for_mon(ctx, mon_id, mon_dir, admin_keyring.name, tmp_config.name)
finish_bootstrap_config(ctx, fsid, config, mon_id, mon_dir,
                        mon_network, ipv6, cli,
                        cluster_network, ipv6_cluster_network)
```

從上述程式可以整理出 bootstrap 的核心步驟：

1. 準備輸出檔案、SSH 與 host 環境。
2. 建立 FSID、初始設定檔與容器映像檢查。
3. 產生 MON / MGR / admin / bootstrap 金鑰。
4. 建立初始 monmap。
5. 啟動第一個 MON，等待 cluster 可回應。
6. 完成 bootstrap 設定，寫出 `ceph.conf`、keyring 與 SSH 金鑰。
7. 後續再透過 `ceph orch` / spec 方式擴增其他 MON、MGR、OSD 與附屬服務。

## Bootstrap 指令入口

`cephadm.py` 也清楚定義了 `bootstrap` 子命令的 CLI 參數。

```python
# 檔案: src/cephadm/cephadm.py
parser_bootstrap = subparsers.add_parser(
    'bootstrap', help='bootstrap a cluster (mon + mgr daemons)')
parser_bootstrap.set_defaults(func=command_bootstrap)
parser_bootstrap.add_argument(
    '--mon-ip',
    help='mon IP')
parser_bootstrap.add_argument(
    '--output-dir',
    default='/etc/ceph',
    help='directory to write config, keyring, and pub key files')
parser_bootstrap.add_argument(
    '--ssh-user',
    default='root',
    help='set user for SSHing to cluster hosts, passwordless sudo will be needed for non-root users')
parser_bootstrap.add_argument(
    '--apply-spec',
    help='Apply cluster spec after bootstrap (copy ssh key, add hosts and apply services)')
```

這代表 bootstrap 階段本身就已經考慮到初始 MON 位址、輸出目錄、SSH 與後續批次套用 spec 的流程。

## 部署指令範例

以下是常見的 cephadm 部署流程示例：

1. 安裝並 bootstrap 第一個節點：`cephadm bootstrap --mon-ip 192.168.122.10`
2. 將其他主機加入 orchestrator 管理：`ceph orch host add node2 192.168.122.11`
3. 佈署額外 monitor：`ceph orch apply mon --placement="count:3"`
4. 佈署 manager：`ceph orch apply mgr --placement="count:2"`
5. 依磁碟條件建立 OSD：`ceph orch apply osd --all-available-devices`

如果要走 declarative 方式，也可以先準備 spec，再於 bootstrap 階段使用 `--apply-spec`，或之後執行 `ceph orch apply -i cluster.yaml`。

::: info 實務上的部署節奏
常見做法是先完成單節點 bootstrap，確認第一個 MON/MGR 正常，再逐步加入 hosts、MON、MGR 與 OSD。這比一次把所有服務灌進去更容易排查網路、SSH、磁碟辨識與時間同步問題。
:::

## 總結

- cephadm 是官方主推的 **container-based** 部署工具。
- 其核心抽象是 `PlacementSpec` 與 `ServiceSpec`。
- ceph-mgr 內的 cephadm module 會長期調和叢集實際狀態與 spec。
- bootstrap 只負責建立初始叢集入口，後續擴充則依賴 `ceph orch` 與 service spec。

::: info 相關章節
- [Ceph — 專案總覽](/ceph/)
- [Ceph — 整體架構概述](/ceph/architecture)
:::
