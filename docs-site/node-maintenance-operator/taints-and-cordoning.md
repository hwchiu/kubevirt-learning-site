---
layout: doc
---

# Node Maintenance Operator — Taint 管理與 Cordoning

## 核心功能

本章說明 NMO 如何在節點維護生命週期中管理 Kubernetes Taint 與 Cordon 狀態，包括雙重保護機制、原子性 Patch 策略，以及與其他 medik8s 元件的協作標記。

---

## 1. 兩種 Taint 的語意

NMO 使用兩個不同的 Taint 來標記受管理的節點：

```go
// 檔案: controllers/taint.go
var medik8sDrainTaint = &corev1.Taint{
    Key:    "medik8s.io/drain",
    Effect: corev1.TaintEffectNoSchedule,
}

var nodeUnschedulableTaint = &corev1.Taint{
    Key:    "node.kubernetes.io/unschedulable",
    Effect: corev1.TaintEffectNoSchedule,
}

var maintenanceTaints = []corev1.Taint{*nodeUnschedulableTaint, *medik8sDrainTaint}
```

| Taint Key | 類型 | 用途 |
|-----------|------|------|
| `node.kubernetes.io/unschedulable` | 標準 Kubernetes Taint | 節點被 cordon 時由 Kubernetes 加入，沒有對應 toleration 的 Pod 將不被排程到此節點 |
| `medik8s.io/drain` | medik8s 專屬 Taint | 作為 NMO 正在管理此節點的標記，讓 NHC 等其他 medik8s operator 能夠偵測並協調行為 |

::: tip 為什麼需要兩個 Taint？
`node.kubernetes.io/unschedulable` 是 Kubernetes 原生機制，提供排程層面的隔離；`medik8s.io/drain` 則是 medik8s 生態系統的溝通信號，讓多個 operator 共同協作時不會互相干擾。
:::

---

## 2. AddOrRemoveTaint 函式邏輯

`AddOrRemoveTaint` 負責在節點上新增或移除維護用 Taint，邏輯如下：

### 新增 Taint（`add=true`）

1. 以 `maintenanceTaints` 作為基礎清單
2. 將節點現有 Taint 中尚未包含在清單內的項目附加進去（保留原有 Taint）
3. 若與現狀相同 → 跳過 Patch，不發出 API 請求
4. 執行 JSON Patch：

```json
{"op": "add", "path": "/spec/taints", "value": <new taints>}
```

### 移除 Taint（`add=false`）

1. 複製節點現有 Taint 清單
2. 從清單中移除兩個維護用 Taint
3. 若與現狀相同 → 跳過 Patch
4. 執行 JSON Patch：

```json
{"op": "replace", "path": "/spec/taints", "value": <remaining taints>}
```

::: warning 保留使用者自訂 Taint
移除流程只會刪除 `maintenanceTaints` 中定義的兩個 Taint，節點上其他自訂 Taint 不受影響。
:::

---

## 3. 原子性 Patch 策略

NMO 使用「先測試、再修改」的 JSON Patch 策略來確保操作的原子性：

```go
// 檔案: controllers/taint.go
patchData := []interface{}{
    map[string]interface{}{"op": "test", "path": "/spec/taints", "value": currentTaints},
    map[string]interface{}{"op": "add", "path": "/spec/taints", "value": newTaints},
}
```

**運作原理：**

1. `test` 操作驗證當前 `/spec/taints` 是否與讀取時的值一致
2. 若中間有其他控制器修改了 Taint，`test` 操作**失敗**，整個 Patch 被拒絕
3. Controller 捕捉錯誤後重新 reconcile，重新讀取最新狀態再嘗試

這個機制避免了 TOCTOU（Time-Of-Check-Time-Of-Use）競態條件，確保在多控制器環境下 Taint 操作不會覆蓋彼此的變更。

---

## 4. Cordon vs Taint 的差異

NMO 同時使用 Cordon 與 Taint 兩種機制，提供雙重排程保護：

| 機制 | API 欄位 | 效果 | 工具 |
|------|---------|------|------|
| Cordon | `node.Spec.Unschedulable = true` | 阻止新 Pod 排程到此節點 | `drain.RunCordonOrUncordon()` |
| Taint `NoSchedule` | `node.Spec.Taints` | 阻止沒有對應 toleration 的 Pod | `AddOrRemoveTaint()` |

::: tip 雙重保護的必要性
Cordon 透過 `Unschedulable` 欄位防止排程器分配新 Pod；Taint 則在 Pod 層面提供更細緻的控制，並允許有特定 toleration 的系統元件（如 DaemonSet）繼續在節點上運行。兩者並用才能完整隔離維護中的節點。
:::

---

## 5. exclude-from-remediation Label

在完成 Taint 標記、開始 Drain 之前，Controller 會為節點加上一個協調標記：

```go
// 檔案: controllers/nodemaintenance_controller.go
labels["medik8s.io/exclude-from-remediation"] = "true"
```

此 Label 通知 medik8s 生態系統中的其他 operator（例如 NHC — Node Health Check），這個節點**已由 NMO 負責處理**，不需要再觸發其他補救流程。

維護結束後，Controller 會清除此 Label：

```go
// 檔案: controllers/nodemaintenance_controller.go
delete(node.Labels, "medik8s.io/exclude-from-remediation")
```

---

## 6. 完整節點狀態變化圖

以下 Mermaid 圖展示節點物件在整個維護生命週期中的狀態變化：

![NodeMaintenance 節點狀態變化圖](/diagrams/node-maintenance-operator/nmo-taints-cordoning-1.png)

---

## 7. 驗證目前 Taint 狀態

使用以下指令查看節點的維護相關狀態：

```bash
# 查看節點 taint 和 cordon 狀態
kubectl get node <node-name> -o jsonpath='{.spec.taints}' | jq .
kubectl get node <node-name> -o jsonpath='{.spec.unschedulable}'

# 查看 medik8s label
kubectl get node <node-name> -o jsonpath='{.metadata.labels.medik8s\.io/exclude-from-remediation}'
```

**預期輸出範例（維護中）：**

```json
[
  {
    "effect": "NoSchedule",
    "key": "node.kubernetes.io/unschedulable"
  },
  {
    "effect": "NoSchedule",
    "key": "medik8s.io/drain"
  }
]
```

```
true
```

```
true
```

::: warning 若 Taint 殘留未清除
如果 NodeMaintenance CR 已刪除但節點仍有維護 Taint，可能是 Controller 在清除過程中異常中斷。請參考[疑難排解章節](./troubleshooting-and-debugging)了解手動恢復步驟。
:::

---

::: info 相關章節
- [Node Drainage Process](./node-drainage-process) — 了解 Drain 流程如何在 Taint/Cordon 之後進行 Pod 驅逐
- [Architecture](./architecture) — NMO 整體架構與各元件職責說明
- [Troubleshooting and Debugging](./troubleshooting-and-debugging) — 常見問題診斷與手動恢復操作
:::
