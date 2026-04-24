---
layout: doc
title: Cluster API Provider MAAS — 學習路徑
---

# Cluster API Provider MAAS — 學習路徑

本學習路徑幫助工程師從基本概念出發，逐步掌握 CAPMAAS 的完整知識，直到能夠獨立佈建裸金屬 Kubernetes 叢集。

## 建議學習路線

### 路線 A：概念優先（適合新手）

如果你對 Cluster API 或 MAAS 還不熟悉，建議按以下順序學習：

1. **[專案簡介](../)**  
   了解 CAPMAAS 的定位與核心功能

2. **[系統架構](../architecture)**  
   理解 CAPI 框架、CRD 物件關係、Controller 設計

3. **[核心功能](../core-features)**  
   深入佈建流程：Allocate → Deploy → DNS 管理

4. **[控制器與 API](../controllers-api)**  
   查閱完整 CRD 欄位說明與 Condition 定義

5. **[外部整合](../integration)**  
   了解 MAAS API 連線設定與 clusterctl 操作

6. **[故事驅動式學習](./story)**  
   透過情境故事鞏固知識

### 路線 B：實作優先（適合有 CAPI 經驗者）

如果你熟悉 Cluster API 生態，可直接從實作切入：

1. **[外部整合](../integration)** — 設定環境，初始化 Provider
2. **[控制器與 API](../controllers-api)** — 查閱 YAML 欄位
3. **[核心功能](../core-features)** — 理解佈建流程細節
4. **[故事驅動式學習](./story)** — 排查常見問題場景

## 核心概念速查

| 概念 | 說明 |
|------|------|
| MAAS | Canonical 裸金屬管理平台，提供類雲端的 REST API |
| Infrastructure Provider | CAPI 中負責對接底層基礎設施的角色 |
| MaasCluster | 叢集層級基礎設施：DNS Domain、CP Endpoint |
| MaasMachine | 機器層級基礎設施：資源需求、映像檔、部署選項 |
| Allocate | MAAS 申請可用機器的操作 |
| Deploy | MAAS 在機器上部署作業系統映像檔的操作 |
| ProviderID | 機器的唯一識別字串，格式 `maas:///<zone>/<systemID>` |
| DNS Resource | MAAS 提供的 DNS 記錄，CAPMAAS 用作 API Server 負載平衡 |
| Resource Pool | MAAS 中的機器分組，用於資源隔離 |
| In-Memory Deploy | 將 OS 載入 RAM 執行，不寫入磁碟 |

## 常見問題索引

| 問題 | 參閱 |
|------|------|
| 叢集建立後 MaasCluster 停在 `LoadBalancerReady=False` | [核心功能 — DNS 管理](../core-features#dns-管理作為-api-server-負載平衡) |
| MaasMachine 停在 `WaitingForBootstrapData` | [核心功能 — 佈建流程](../core-features#機器佈建流程machine-provisioning) |
| 如何篩選特定 Resource Pool 的機器 | [核心功能 — 篩選](../core-features#resource-pool-與-tag-篩選) |
| 如何使用 In-Memory 部署 | [核心功能 — In-Memory](../core-features#in-memory-部署記憶體內部署) |
| 如何設定 MAAS 連線認證 | [外部整合 — 認證方式](../integration#maas-api-整合) |
| MaasMachine 刪除後卡住不動 | [控制器與 API — Finalizer](../controllers-api#finalizer-定義) |

::: info 相關章節
- [故事驅動式學習](./story) — 透過情境故事理解完整佈建流程
- [系統架構](../architecture) — 從架構角度全覽 CAPMAAS
:::
