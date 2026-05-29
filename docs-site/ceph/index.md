---
layout: doc
title: Ceph — 專案總覽
---

# Ceph — 專案總覽

Ceph 是一套以 **RADOS** 為核心的分散式儲存系統，能同時提供物件儲存、區塊儲存與檔案系統介面。它的設計目標不是把所有 I/O 都集中到單一控制節點，而是透過叢集地圖、CRUSH 演算法與大量 OSD 節點，把資料與流量分散到整個叢集中。

對平台工程師而言，Ceph 的價值在於：同一套底層資料平面，可以同時支撐虛擬機磁碟、Kubernetes PVC、S3 相容物件儲存與共享檔案系統。

## 架構速覽

<pre>
                         +----------------------+
                         |        Clients       |
                         | librados / librbd /  |
                         |      libcephfs       |
                         +----------+-----------+
                                    |
                                    v
+---------+    +---------+    +-----------+    +---------+    +---------+
|  MON    |    |  MGR    |    |   RADOS   |    |  MDS    |    |  RGW    |
| quorum  |    | modules |    |  core +   |    | CephFS  |    | S3/Swift|
| maps    |    | metrics |    |  CRUSH    |    | metadata|    | gateway |
+----+----+    +----+----+    +-----+-----+    +----+----+    +----+----+
     |              |                |               |              |
     +--------------+----------------+---------------+--------------+
                                    |
                                    v
                          +-------------------+
                          |    OSD daemons    |
                          | data / replica /  |
                          | recovery / scrub  |
                          +-------------------+
</pre>

## Ceph 在做什麼？

- **MON（Monitor）**：維護叢集地圖與 quorum，提供一致的控制面資訊。
- **OSD（Object Storage Daemon）**：實際負責資料寫入、複寫、回復與 scrub。
- **MGR（Manager）**：補強監控、模組化功能與叢集管理整合。
- **MDS（Metadata Server）**：只在 CephFS 場景中負責目錄與 inode 類型的 metadata。
- **RGW（RADOS Gateway）**：把 RADOS 能力包裝成 S3 / Swift 相容 API。
- **librados / librbd / libcephfs**：讓應用程式、虛擬化平台與檔案系統客戶端直接使用 Ceph。

::: tip 閱讀順序建議
如果你是第一次接觸 Ceph，建議先看「整體架構概述」，再看「部署架構與 cephadm」，最後依序閱讀 MON、OSD、RADOS、RBD 與 CephFS。
:::

## 文件導覽

下表整理本章節預計涵蓋的頁面。已完成頁面提供可直接點擊的連結；其餘頁面先列出檔名與主題，方便後續擴充。

| 分類 | 頁面 | 檔案 | 說明 | 狀態 |
|------|------|------|------|------|
| 系統架構 | [整體架構概述](/ceph/architecture) | `architecture.md` | Ceph 與 RADOS 的整體設計 | 已完成 |
| 系統架構 | [部署架構與 cephadm](/ceph/deployment) | `deployment.md` | cephadm、bootstrap 與服務佈署 | 已完成 |
| 核心元件 | MON | `monitor.md` | Monitor quorum 與各類 cluster map | 規劃中 |
| 核心元件 | OSD | `osd.md` | 資料寫入、複寫、回復、scrub | 規劃中 |
| 核心元件 | MGR | `manager.md` | Manager 模組與觀測能力 | 規劃中 |
| 核心元件 | MDS | `mds.md` | CephFS metadata 平面 | 規劃中 |
| 儲存介面 | RADOS / librados | `rados.md` | 物件層與原生 API | 規劃中 |
| 儲存介面 | RBD | `rbd.md` | 區塊裝置映像與快照 | 規劃中 |
| 儲存介面 | CephFS | `cephfs.md` | POSIX 風格共享檔案系統 | 規劃中 |
| 儲存介面 | RGW Gateway | `rgw.md` | S3 / Swift 相容閘道 | 規劃中 |
| 核心演算法 | CRUSH 演算法 | `crush.md` | 放置演算法與 failure domain | 規劃中 |
| 核心演算法 | PG 機制 | `pg-replication.md` | Placement Group、peering 與複寫 | 規劃中 |
| 維運管理 | [cephadm 深入分析](/ceph/cephadm) | `cephadm.md` | Orchestrator 模組、spec 與 host / service 管理 | 已完成 |
| 維運管理 | [Dashboard](/ceph/dashboard) | `dashboard.md` | Web UI、Prometheus / Grafana 整合與 REST API | 已完成 |
| 維運管理 | [日常維運](/ceph/operations) | `operations.md` | 巡檢、擴容、故障排查、升級 | 已完成 |
| 學習路徑 | [學習路徑入口](/ceph/learning-path/) | `learning-path/index.md` | 控制面與資料面閱讀順序 | 已完成 |
| 學習路徑 | [故事驅動式學習](/ceph/learning-path/story) | `learning-path/story.md` | 以一次寫入流程串起 Ceph 核心概念 | 已完成 |
| 學習測驗 | 架構測驗 | `quiz/architecture.md` | 架構與資料流測驗 | 規劃中 |
| 學習測驗 | 元件測驗 | `quiz/components.md` | MON / OSD / MGR / MDS 測驗 | 規劃中 |
| 學習測驗 | 儲存介面測驗 | `quiz/storage.md` | RADOS / RBD / CephFS / RGW 測驗 | 規劃中 |

## 建議關注主題

1. **RADOS 如何讓 client 直接找到 OSD**：這是 Ceph 可水平擴充的核心。
2. **MON 為何只處理控制面**：理解這點才能掌握 Ceph 的擴充上限。
3. **PG 與 CRUSH 的關係**：Ceph 的資料放置不是單純 hash，而是 map + policy 的組合。
4. **MDS 為何只服務 CephFS**：它不是所有 Ceph I/O 的必經元件。
5. **cephadm 為何依賴容器與 declarative spec**：這是現代 Ceph 維運模式的關鍵。

::: info 相關章節
- [Ceph — 整體架構概述](/ceph/architecture)
- [Ceph — 部署架構與 cephadm](/ceph/deployment)
- [Ceph — cephadm 深入分析](/ceph/cephadm)
- [Ceph — Dashboard](/ceph/dashboard)
- [Ceph — 日常維運](/ceph/operations)
- [Ceph — 學習路徑入口](/ceph/learning-path/)
:::
