---
layout: doc
---

# Node Maintenance Operator — Lease 分散式協調機制

## 1. 為什麼需要 Lease？

在同一個 Kubernetes 叢集中，可能同時存在多個 medik8s 系列的 operator，例如 **Node Maintenance Operator (NMO)** 與 **Node Health Check (NHC)**。兩者都有能力對節點施加 taint、觸發 eviction 或進行排水（drain）操作。若缺乏協調機制，就可能發生以下衝突：

- 同一節點被兩個 operator 同時 drain，造成 Pod 反覆驅逐
- Taint 互相覆蓋，導致節點狀態不一致
- 維護完成後 uncordon 被另一個 operator 的 cordon 抵消

**解決方案**：使用 Kubernetes 原生的 `coordination.k8s.io/v1.Lease` 物件作為**每個節點的分散式鎖（distributed lock）**，確保同一時間只有一個 operator 能對該節點執行維護操作。

## 2. Lease 架構設計

NMO 透過 `medik8s/common` 函式庫提供的 `Manager` 介面操作 Lease：

```go
// 檔案: vendor/github.com/medik8s/common/pkg/lease/manager.go
type Manager interface {
    RequestLease(ctx context.Context, obj client.Object, leaseDuration time.Duration) error
    InvalidateLease(ctx context.Context, obj client.Object) error
    GetLease(ctx context.Context, obj client.Object) (*coordv1.Lease, error)
}
```

控制器層定義相關常數：

```go
// 檔案: controllers/nodemaintenance_controller.go
LeaseHolderIdentity = "node-maintenance"
LeaseDuration       = 3600 * time.Second  // 1 小時
maxAllowedErrorToUpdateOwnedLease = 3
```

## 3. Lease 儲存位置

| 項目 | 值 |
|------|-----|
| Kubernetes 資源類型 | `coordination.k8s.io/v1.Lease` |
| Namespace | `medik8s-leases`（可透過 `LEASE_NAMESPACE` 環境變數覆寫） |
| 命名規則 | `node-<nodename>`，例如 `node-worker01` |

查詢範例：

```bash
kubectl get lease -n medik8s-leases
kubectl get lease node-worker01 -n medik8s-leases -o yaml
```

## 4. RequestLease 詳細流程

![RequestLease 詳細流程 - 包含 Lease 建立、更新、接管等各種情境](/diagrams/node-maintenance-operator/nmo-lease-1.png)

## 5. AlreadyHeldError 型別

當 Lease 已被其他 operator 持有且尚未過期時，`RequestLease` 會回傳 `AlreadyHeldError`：

```go
// 檔案: vendor/github.com/medik8s/common/pkg/lease/manager.go
type AlreadyHeldError struct {
    holderIdentity string
}

func (e AlreadyHeldError) Error() string {
    return fmt.Sprintf("can't update or invalidate the lease because it is held by different owner: %s", e.holderIdentity)
}
```

呼叫端可透過型別斷言判斷是否為此錯誤，以決定要等待還是直接標記失敗。

## 6. ErrorOnLeaseCount 機制

NMO 會追蹤連續 Lease 取得失敗的次數，超過閾值時自動退出維護狀態，避免節點永久被 cordon：

![ErrorOnLeaseCount 機制 - 追蹤連續 Lease 失敗次數，超過閾值後自動退出維護以避免節點永久被 cordon](/diagrams/node-maintenance-operator/nmo-lease-2.png)

相關程式碼：

```go
// 檔案: controllers/nodemaintenance_controller.go
if nm.Status.ErrorOnLeaseCount > maxAllowedErrorToUpdateOwnedLease {
    // uncordon node, set MaintenanceFailed
}
```

::: warning 注意
`ErrorOnLeaseCount` 只會在**已開始排水（DrainProgress > 0）後**的 `AlreadyHeldError` 才計數，確保節點不會因為正常的競爭等待而被提前放棄。
:::

## 7. 多實例協調場景

| 場景 | 行為 |
|------|------|
| 單一 NMO 實例 | 正常取得 lease，持續更新 RenewTime |
| 兩個 NMO 實例競爭 | 第一個取得 lease；第二個收到 `AlreadyHeldError`，等待下次 reconcile |
| NMO + NHC 競爭同一節點 | 後到者收到 `AlreadyHeldError`，不得對節點操作，等待或失敗 |
| NMO 實例崩潰 | Lease 在 1 小時後過期，另一存活的實例可接管（LeaseTransitions++） |

## 8. InvalidateLease（維護結束）

當 `NodeMaintenance` 物件被刪除或維護完成時，控制器會呼叫 `InvalidateLease` 釋放鎖：

```go
// 檔案: controllers/nodemaintenance_controller.go
err = r.LeaseManager.InvalidateLease(ctx, node)
```

`InvalidateLease` 的行為：

- **由當前 operator 持有** → 刪除（DELETE）該 Lease 物件
- **由其他實體持有** → 記錄 warning log，繼續執行（不強制刪除）
- **Lease 不存在** → 靜默繼續，視為已釋放

## 9. LeaseManager 初始化

`LeaseManager` 在程式啟動時透過 `Runnable` 介面延遲初始化，確保 controller-manager 的 client cache 就緒後再建立：

```go
// 檔案: main.go
func (ls *leaseManagerInitializer) Start(context.Context) error {
    var err error
    ls.Manager, err = lease.NewManager(ls.cl, controllers.LeaseHolderIdentity)
    return err
}
```

初始化完成後，`LeaseManager` 實例會注入 `NodeMaintenanceReconciler`，供後續所有 reconcile 迴圈使用。

::: tip Lease 與 Controller Leader Election 的差異
**Controller leader election**（`--leader-elect` 旗標）決定哪個 NMO Pod 實例成為主控制器（leader），其他 Pod 進入待命狀態。

**Lease 機制**是跨不同 operator（NMO、NHC 等）的**節點級別協調鎖**，即便在 leader election 之外，也需要確保不同 operator 不會同時操作同一個節點。

兩者目的不同、層次不同，可同時運作。
:::

::: info 相關章節
- [架構概覽](./architecture.md) — 了解 NMO 整體元件設計與控制迴圈
- [節點排水流程](./node-drainage-process.md) — Lease 取得成功後的排水詳細步驟
- [故障排除與除錯](./troubleshooting-and-debugging.md) — 如何診斷 Lease 競爭、AlreadyHeldError 等問題
:::
