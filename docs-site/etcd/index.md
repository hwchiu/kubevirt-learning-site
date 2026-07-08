---
layout: doc
title: etcd — 專案總覽
---

# etcd — Kubernetes 控制平面的資料核心

::: tip 分析版本
本文件基於 commit [`6e470567`](https://github.com/etcd-io/etcd/commit/6e4705678926d5d0982538896acc087d21e09db5) 進行分析。
:::

## 專案簡介

**etcd** 是以 **Raft** 為核心的分散式 Key-Value Store，提供 Kubernetes 控制平面最重要的持久化儲存層。`README.md` 明確將其定位為 reliable key-value store，而 `client/v3`、`server`、`raft` 模組分別承擔 API、儲存引擎與共識邏輯。

![etcd 在 Kubernetes 中的角色總覽](/diagrams/etcd/etcd-overview-1.png)

- **GitHub**: [etcd-io/etcd](https://github.com/etcd-io/etcd)
- **License**: Apache 2.0
- **語言**: Go
- **關鍵角色**: Kubernetes API Server 的後端狀態儲存

## 為什麼這個章節只聚焦 Defrag 與 Learner

在 Kubernetes 維運情境裡，etcd 最常見且最容易出問題的兩個主題是：

| 主題 | 為什麼重要 |
|------|------|
| **Defrag** | 刪除與 Compact 不會立刻縮小 bbolt 檔案；如果長期不整理，磁碟使用量與 I/O 壓力會持續累積 |
| **Learner Mode** | 擴容或替換成員時，可先用非投票節點同步資料，降低直接加入 voting member 對 quorum 的風險 |

## 文件導覽

| 文件 | 說明 |
|------|------|
| [為什麼需要 Defrag](./defrag) | 從 backend 與 metrics 解釋 Defrag 的根因、代價與執行流程 |
| [Kubernetes 中的 Defrag 操作](./kubernetes-defrag) | 說明 Defrag 對 kube-apiserver 的影響、建議操作順序與觀察指標 |
| [Learner Mode](./learner-mode) | 分析 learner member 的新增、限制、升級條件與 quorum 保護 |

## 關鍵來源檔案

- `etcd/README.md`
- `etcd/client/v3/maintenance.go`
- `etcd/server/storage/backend/backend.go`
- `etcd/server/storage/mvcc/metrics.go`
- `etcd/server/etcdserver/api/membership/cluster.go`
- `etcd/server/etcdserver/api/membership/member.go`
- `etcd/tests/integration/clientv3/cluster_test.go`
- `etcd/tests/integration/clientv3/kv_test.go`

::: info 相關章節
- [為什麼需要 Defrag](./defrag)
- [Kubernetes 中的 Defrag 操作](./kubernetes-defrag)
- [Learner Mode](./learner-mode)
:::
