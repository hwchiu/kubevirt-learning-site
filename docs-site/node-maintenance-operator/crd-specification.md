---
layout: doc
---

# Node Maintenance Operator — NodeMaintenance CRD 規格

**對象：** Operators、Developers｜**章節：** 核心功能

---

## CRD 基本資訊

| 屬性 | 值 |
|------|----|
| Kind | `NodeMaintenance` |
| Group | `nodemaintenance.medik8s.io` |
| Version | `v1beta1` |
| Scope | Cluster-scoped |
| Short name | `nm` |
| Finalizer | `foregroundDeleteNodeMaintenance` |

---

## Spec 欄位

> 來源：`api/v1beta1/nodemaintenance_types.go` lines 43–54

| 欄位 | 類型 | 必填 | 說明 |
|------|------|:----:|------|
| `nodeName` | `string` | ✅ | 要進行維護的節點名稱（建立後不可修改） |
| `reason` | `string` | ❌ | 維護原因說明 |

---

## Status 欄位

> 來源：`api/v1beta1/nodemaintenance_types.go` lines 67–99

| 欄位 | 類型 | 說明 | 可能值 |
|------|------|------|--------|
| `phase` | `MaintenancePhase` | 維護進度狀態 | `Running`、`Succeeded`、`Failed` |
| `drainProgress` | `int` | 排空完成百分比 | `0`–`100` |
| `lastUpdate` | `metav1.Time` | 最後狀態更新時間 | RFC3339 timestamp |
| `lastError` | `string` | 最近一次 reconcile 錯誤訊息 | 任意錯誤字串 |
| `pendingPods` | `[]string` | 尚未驅逐的 Pod 名稱清單 | Pod name strings |
| `pendingPodsRefs` | `[]PodReference` | 尚未驅逐的 Pod 參照清單 | `PodReference` 陣列 |
| `totalPods` | `int` | 維護開始時節點上的總 Pod 數 | 整數 |
| `evictionPods` | `int` | 需要驅逐的 Pod 總數 | 整數 |
| `errorOnLeaseCount` | `int` | 連續 lease 取得失敗次數（上限 3） | `0`–`3+` |

---

## Phase 列舉

```go
// 檔案: api/v1beta1/nodemaintenance_types.go
const (
    MaintenanceRunning   MaintenancePhase = "Running"   // 維護進行中
    MaintenanceSucceeded MaintenancePhase = "Succeeded" // 維護完成，所有 Pod 已驅逐
    MaintenanceFailed    MaintenancePhase = "Failed"    // 維護失敗
)
```

---

## PodReference 結構

```go
// 檔案: api/v1beta1/nodemaintenance_types.go
type PodReference struct {
    Namespace string `json:"namespace,omitempty"`
    Name      string `json:"name,omitempty"`
}
```

---

## 完整範例 CR

### 最小配置

```yaml
# 建立維護請求
apiVersion: nodemaintenance.medik8s.io/v1beta1
kind: NodeMaintenance
metadata:
  name: maintain-node02
spec:
  nodeName: node02
  reason: "硬體更換 - RAM 升級"
```

### 維護進行中的 Status 範例

```yaml
apiVersion: nodemaintenance.medik8s.io/v1beta1
kind: NodeMaintenance
metadata:
  name: maintain-node02
spec:
  nodeName: node02
  reason: "硬體更換 - RAM 升級"
status:
  phase: Running
  drainProgress: 60
  lastUpdate: "2024-05-10T08:23:41Z"
  lastError: ""
  totalPods: 10
  evictionPods: 6
  pendingPods:
    - coredns-7db6d8ff4d-xkpqz
    - my-app-5f9b8c6d4-rlmwt
  pendingPodsRefs:
    - namespace: kube-system
      name: coredns-7db6d8ff4d-xkpqz
    - namespace: default
      name: my-app-5f9b8c6d4-rlmwt
  errorOnLeaseCount: 0
```

---

## 不可變欄位

::: warning spec.nodeName 建立後不可修改
Webhook 的 `ValidateUpdate` 會拒絕任何修改 `spec.nodeName` 的請求，錯誤訊息：

```
"updating spec.NodeName isn't allowed"
```

若需要對不同節點進行維護，請刪除現有的 `NodeMaintenance` 資源並重新建立。
:::

---

## kubectl 常用操作

```bash
# 列出所有維護請求
kubectl get nm

# 查看詳細狀態
kubectl describe nm maintain-node02

# 刪除（觸發節點恢復）
kubectl delete nm maintain-node02
```

::: tip 使用 -o wide 取得更多資訊
```bash
kubectl get nm -o wide
```
輸出中可見 `PHASE`、`NODENAME` 等欄位，方便快速掌握各節點維護狀態。
:::

---

::: info 相關章節
- [架構總覽](./architecture) — 了解 Node Maintenance Operator 的整體設計與元件互動
- [節點排空流程](./node-drainage-process) — 深入了解 drain 機制與 Pod 驅逐順序
- [驗證 Webhooks](./validation-webhooks) — 了解 `spec.nodeName` 不可變限制的實作細節
:::
