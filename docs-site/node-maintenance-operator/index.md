---
layout: doc
---

# Node Maintenance Operator — 專案總覽

::: tip 分析版本
本文件基於 commit [`d1a537be`](https://github.com/medik8s/node-maintenance-operator/commit/d1a537be397a0afb2fd034650a1ed329e72699a2) 進行分析。
- **operator-sdk**: v1.37.0
- **controller-runtime**: v0.22.5
- **Kubernetes**: 1.34
:::

## 專案簡介

**Node Maintenance Operator (NMO)** 是由 [medik8s](https://github.com/medik8s) 社群維護的 Kubernetes/OpenShift Operator（前身隸屬於 KubeVirt 專案）。其 Go module 為 `github.com/medik8s/node-maintenance-operator`，程式進入點為單一的 `main.go`。

核心職責：監看 `NodeMaintenance` Custom Resource（CR），自動執行等同 `kubectl drain` 的節點排空流程：

| 事件 | Operator 行為 |
|------|--------------|
| CR 建立 | 封鎖（cordon）節點、套用 taint、驅逐所有 Pod |
| CR 刪除 | 取消封鎖（uncordon）節點、移除 taint |

**額外協調機制**

- **Lease**：與同屬 medik8s 的 Node Health Check (NHC) 等 operator 協調，避免同時維護多個節點。
- **OpenShift etcd quorum 保護**：在允許 control-plane 節點進入維護前，驗證 etcd quorum 是否健全。

- **GitHub**: [medik8s/node-maintenance-operator](https://github.com/medik8s/node-maintenance-operator)
- **License**: Apache 2.0
- **語言**: Go (operator-sdk / controller-runtime)

## 運作流程

![Node Maintenance Operator 運作流程](/diagrams/node-maintenance-operator/nmo-workflow.png)

## 快速開始

### 建立 NodeMaintenance CR

```yaml
apiVersion: nodemaintenance.medik8s.io/v1beta1
kind: NodeMaintenance
metadata:
  name: nodemaintenance-sample
spec:
  nodeName: node02
  reason: "Test node maintenance"
```

```bash
# 套用 CR，開始節點維護
kubectl apply -f nodemaintenance-sample.yaml

# 觀察維護進度
kubectl get nodemaintenance nodemaintenance-sample -o yaml

# 完成後刪除 CR，解除節點封鎖
kubectl delete nodemaintenance nodemaintenance-sample
```

::: info 狀態欄位說明
套用 CR 後，可透過 `status` 欄位追蹤進度：

| 欄位 | 說明 |
|------|------|
| `phase` | 目前階段：`Running` / `Succeeded` / `Failed` |
| `drainProgress` | 驅逐進度百分比（0–100） |
| `pendingPods` | 尚未驅逐的 Pod 名稱清單 |
| `lastError` | 最新錯誤訊息 |
| `totalPods` | 開始時的 Pod 總數 |
| `evictionPods` | 需要驅逐的 Pod 數量 |
:::

## 文件導覽

### 系統架構

| 頁面 | 說明 |
|------|------|
| [系統架構](./architecture) | 系統元件、Reconcile 流程、狀態機 |
| [部署與設定](./installation-and-deployment) | OLM bundle、kustomize、設定參數 |

### 核心功能

| 頁面 | 說明 |
|------|------|
| [NodeMaintenance CRD 規格](./crd-specification) | Spec/Status 所有欄位、Phase 列舉 |
| [節點排空工作流程](./node-drainage-process) | kubectl drain 整合、Pod 驅逐邏輯 |
| [Admission Validation](./validation-webhooks) | Webhook 檢查邏輯、錯誤訊息 |
| [Lease 分散式協調](./lease-based-coordination) | 多實例協調、AlreadyHeldError |
| [Taint 管理與 Cordoning](./taints-and-cordoning) | 兩種 taint、JSON Patch 策略 |

### 維運進階

| 頁面 | 說明 |
|------|------|
| [RBAC 與權限](./rbac-and-permissions) | ClusterRole 清單、各權限用途 |
| [故障排除](./troubleshooting-and-debugging) | 常見失敗模式、must-gather |
| [事件與可觀測性](./event-recording-and-observability) | Kubernetes Events、健康探針 |

::: info 相關章節
依使用情境快速跳轉：

- 想了解 CR 所有欄位定義 → [NodeMaintenance CRD 規格](./crd-specification)
- 想了解 Pod 驅逐的細節流程 → [節點排空工作流程](./node-drainage-process)
- 想了解多 Operator 協調機制 → [Lease 分散式協調](./lease-based-coordination)
- 想排查維護卡住或失敗 → [故障排除](./troubleshooting-and-debugging)
- 想了解 OpenShift etcd 保護 → [Admission Validation](./validation-webhooks)
:::
