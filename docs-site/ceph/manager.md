---
layout: doc
title: Ceph — Manager (MGR) 與模組系統
---

# Ceph — Manager (MGR) 與模組系統

::: tip 核心定位
Ceph Manager（MGR）是 Ceph 在 MON 之外補上的「觀測、擴充與對外整合層」。它不負責 Paxos 仲裁，也不直接保存 object 資料，而是聚焦在 metrics、模組化擴充、REST API 與外部編排整合。
:::

::: info 相關章節
- 叢集控制平面與一致性請參閱 [Ceph — Monitor (MON) 詳解](./monitor)
- 資料平面與 BlueStore 請參閱 [Ceph — OSD 詳解](./osd)
- CephFS metadata 服務請參閱 [Ceph — Metadata Server (MDS) 詳解](/ceph/mds)
:::

## MGR 的角色：指標蒐集、REST API、編排整合

MGR 可以視為一個「站在控制平面旁邊的營運層 daemon」，主要負責：

- 蒐集 OSD、MDS、MON 等 daemon 的統計與健康資訊
- 對外提供模組化介面
- 暴露 dashboard / REST API / Prometheus exporter
- 承接 cephadm 等編排整合能力

與 MON 相比，MGR 更像是 **operations hub**，而不是共識核心。

## DaemonServer：接收 OSD / MDS 回報的入口

`src/mgr/DaemonServer.h` 中可以看到：

```cpp
// 檔案: ceph/src/mgr/DaemonServer.h
class DaemonServer : public Dispatcher, public md_config_obs_t
```

這個類別的職責很關鍵：它負責接收來自各類 daemon 的報告，並把資訊送進 MGR 內部狀態管理。從名稱就能看出它像是 MGR 的前門：

- OSD 回報效能與健康資料
- MDS 回報 CephFS metadata 相關統計
- 其他 daemon 回報事件、命令結果或狀態變更

`ClusterState` 則扮演本地快取與聚合層角色，將來自各 daemon 的觀測資訊整理成 MGR 可供模組使用的叢集視圖。

## Active vs Standby MGR

MGR 採用 active / standby 模式：

- **Active MGR**：實際載入模組、處理報告、提供 dashboard / exporter 等服務。
- **Standby MGR**：待命節點，通常維持基本同步狀態，當 active 故障時接手。

在 `src/mgr/ActivePyModules.h` 可以看到大量與 active beacon、模組啟動完成、通知模組有關的介面，代表「哪個 MGR 真正對外工作」是被明確管理的，而不是所有 MGR 同時對外提供相同功能。

::: warning 與 MON 的差異
MON 的 leader / quorum 是強一致控制平面的一部分；MGR 的 active / standby 則較偏向高可用服務切換。兩者都會選主，但責任與一致性要求不同。
:::

## Python 模組系統：MGR 最有特色的部分

Ceph MGR 的一大特色是 Python 模組系統。`ActivePyModules` 與 `mgr_module.py` 是理解這一層的關鍵入口。

```cpp
// 檔案: ceph/src/mgr/ActivePyModules.h
class ActivePyModules
```

```python
# 檔案: ceph/src/pybind/mgr/mgr_module.py
class MgrModule(object):
```

這表示 Ceph 不是把所有營運功能都寫死在 C++ 裡，而是提供一個 C++ core + Python extension model：

- C++ 層：維護 daemon 通訊、叢集狀態與模組執行框架
- Python 層：以較高開發效率快速擴充營運功能

### `src/pybind/mgr/` 中的重要模組

根據原始碼目錄，可直接看到多個常用模組：

- `dashboard`
- `prometheus`
- `cephadm`
- `balancer`
- `crash`
- `alerts`

這些模組大致各自扮演：

| 模組 | 角色 |
|---|---|
| `dashboard` | Web UI 與 REST API 入口 |
| `prometheus` | 暴露 Prometheus 可抓取的 metrics |
| `cephadm` | 容器化部署與編排整合 |
| `balancer` | 根據叢集分布狀態提出或套用平衡策略 |
| `crash` | 收集與管理 crash 報告 |
| `alerts` | 整理告警與通知相關能力 |

## REST API 與 dashboard 模組

Ceph 的 REST API 並不是由核心 C++ daemon 直接硬編碼提供，而是高度依賴 `dashboard` 模組。這種做法的好處是：

- UI 與 API 可以獨立演進
- 不需把所有 HTTP 邏輯混進核心 daemon
- 權限控管與業務流程能在模組層快速迭代

對使用者來說，常見的體驗是「透過 dashboard 跟 Ceph 互動」；對程式架構來說，實際上是「MGR 載入 dashboard 模組，由其實作對外介面」。

## ClusterState：模組可見的叢集快照

`src/mgr/ClusterState.h` / `.cc` 負責整理叢集中的 daemon 資訊、狀態與快取，使得 Python 模組不需要直接和每個 OSD / MDS 線上對話，而是透過 MGR 聚合後的視圖做決策。

這種設計有兩個重要效果：

1. **降低模組複雜度**：模組作者不必自己重建整個 daemon 訊息流。
2. **統一觀測來源**：dashboard、prometheus、alerts 等模組可共享同一份叢集狀態基底。

## MGR 模組系統的整體資料流

```text
// 檔案: docs-site/ceph/manager.md
OSD / MDS / MON 報告
        |
        v
+-------------------+
|   DaemonServer    |
+-------------------+
        |
        v
+-------------------+
|   ClusterState    |
+-------------------+
        |
        v
+-------------------+
| ActivePyModules   |
+-------------------+
   |      |      |
   v      v      v
dashboard prometheus cephadm ...
```

這個資料流顯示 MGR 的價值不是單純「又一個 daemon」，而是把叢集觀測資料轉化成可擴充功能的平台。

## 為什麼 Ceph 把這些能力放進 MGR

如果把指標、告警、REST API、編排整合全部塞進 MON：

- 會讓共識核心過度膨脹
- 功能迭代速度受限於核心控制平面
- Python 這種高生產力擴充路徑會很難導入

把這些能力移到 MGR 後，Ceph 就能把架構分層得更乾淨：

- **MON**：一致性與 cluster maps
- **OSD**：資料儲存與複寫
- **MDS**：CephFS metadata
- **MGR**：觀測、API、營運與整合

## 關鍵原始碼索引

- `ceph/src/mgr/DaemonServer.h` — `class DaemonServer`
- `ceph/src/mgr/ActivePyModules.h` — active Python 模組框架
- `ceph/src/mgr/ClusterState.cc` / `ceph/src/mgr/ClusterState.h` — 叢集狀態聚合
- `ceph/src/pybind/mgr/mgr_module.py` — Python 模組基底

## 相關章節

::: info 延伸閱讀
- 叢集地圖與共識請閱讀 [Ceph — Monitor (MON) 詳解](./monitor)
- 資料落盤與副本同步請閱讀 [Ceph — OSD 詳解](./osd)
- CephFS metadata 與 rank 狀態請閱讀 [Ceph — Metadata Server (MDS) 詳解](/ceph/mds)
:::
