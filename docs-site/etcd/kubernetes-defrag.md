---
layout: doc
title: etcd — Kubernetes 中的 Defrag 操作
---

# etcd — Kubernetes 中的 Defrag 操作

## 先定義問題

當 etcd 是 Kubernetes 的後端資料庫時，Defrag 不再只是 etcd 自己的 housekeeping，而是**直接影響 kube-apiserver 延遲與控制平面穩定性**。原因很簡單：API Server 的寫入、讀取、watch 狀態最終都會落到 etcd。

![Kubernetes 中的 etcd Defrag 維運流程](/diagrams/etcd/etcd-kubernetes-defrag-1.png)

## 為什麼在 Kubernetes 中要更保守

`client/v3/maintenance.go` 已明確標註 Defrag 是 expensive operation，而 `backend.go` 又顯示它會鎖住交易與讀路徑：

```go
// 檔案: etcd/server/storage/backend/backend.go
b.batchTx.LockOutsideApply()
b.mu.Lock()
b.readTx.Lock()
```

對 Kubernetes 來說，這意味著執行中的 member 可能出現：

- API 請求延遲上升
- watch / list 操作變慢
- 該 member 若正好承擔較多流量，可能出現短暫 timeout

因此 Defrag 在 Kubernetes 叢集裡必須視為**維運事件**，而不是「隨時可以安全執行的輕量指令」。

## etcdctl 為什麼是逐台處理

`etcdctl defrag` 的程式碼不是平行發送，而是逐個 endpoint 呼叫：

```go
// 檔案: etcd/etcdctl/ctlv3/command/defrag_command.go
for _, ep := range endpointsFromCluster(cmd) {
    cfg.Endpoints = []string{ep}
    _, err := c.Defragment(ctx, ep)
}
```

這個設計本身就是操作暗示：**不要同時 Defrag 多個 member**。在 Kubernetes 控制平面場景，這個原則尤其重要，因為：

- 單一 member 停頓時，其他 healthy member 還能承接請求
- 若同時對多個 member 做 Defrag，容易把控制平面推向高延遲甚至 quorum 風險

## 建議的 Kubernetes 操作順序

### 1. 先看是否真的值得做

優先檢查：

- `etcd_mvcc_db_total_size_in_bytes`
- `etcd_mvcc_db_total_size_in_use_in_bytes`
- `etcd_server_quota_backend_bytes`

如果 `db_total_size` 與 `db_total_size_in_use` 差距很小，Defrag 收益有限；若差距很大，才有足夠理由承擔停頓成本。

這裡要特別補一個關鍵前提：**先把 compaction 和 defrag 分開看**。

### 1.1 先看 compaction，再看 defrag

`tests/integration/metrics_test.go` 的驗證流程清楚表明：

- compaction 後，`etcd_mvcc_db_total_size_in_use_in_bytes` 下降
- defrag 後，`etcd_mvcc_db_total_size_in_bytes` 才下降

所以在 Kubernetes 環境裡，這兩個 metrics 的判讀建議是：

| Metric | 你應該怎麼解讀 |
|------|------|
| `etcd_mvcc_db_total_size_in_use_in_bytes` | 目前實際仍在使用的資料量；較能反映 compaction 後的結果 |
| `etcd_mvcc_db_total_size_in_bytes` | 目前 DB 檔案實體占用磁碟量；較能反映 defrag 後的結果 |

如果你看到：

- `in_use` 已下降，但 `db_total_size` 還很高：代表**已 compact，但還沒 defrag**
- `in_use` 沒怎麼降：代表問題可能不是 defrag 時機，而是**還沒有先做足夠的 compaction**

也就是說，Defrag 不應該被當成第一步；它通常是 compaction 之後的第二步。

### 2. 逐一處理 member

對每個 member 個別執行，不要同時打全部節點。這不只是經驗法則，而是 etcdctl 實作本身的預設行為。

### 3. 每做完一台就觀察

建議至少確認：

- `etcd_disk_defrag_inflight` 已回到 `0`
- `etcd_mvcc_db_total_size_in_bytes` 已下降
- kube-apiserver 與 controller manager 沒有持續 timeout

### 4. 避開控制平面高峰

因為 backend 鎖會直接放大請求延遲，所以最好避開：

- 大量 CRD/Operator rollout
- 大量 Pod churn
- 大規模 namespace、Lease、Event 寫入高峰

## Kubernetes 裡的自動化線索

etcd 自身也提供 bootstrap 時的自動 Defrag 閾值：

```go
// 檔案: etcd/server/embed/config.go
fs.UintVar(&cfg.BootstrapDefragThresholdMegabytes, "bootstrap-defrag-threshold-megabytes", 0, ...)
```

對應邏輯在 `server/etcdserver/bootstrap.go`：

```go
// 檔案: etcd/server/etcdserver/bootstrap.go
freeableMemory := uint(size - sizeInUse)
thresholdBytes := cfg.BootstrapDefragThresholdMegabytes * 1024 * 1024
if freeableMemory < thresholdBytes {
    return nil
}
return be.Defrag()
```

這表示 etcd 官方已把「`size - sizeInUse` 足夠大才值得 Defrag」做成正式機制。即使在 Kubernetes 手動維運時，判斷邏輯也應該一致。

## 在 Kubernetes 裡最該避免的錯誤

1. **把 Compact 當成 Defrag**。Compact 不會保證磁碟檔案縮小。
2. **把 Defrag 當成 Compact**。Defrag 不會取代 revision 歷史清理。
3. **同時對多個 member 做 Defrag**。這與 etcdctl 的設計方向相反。
4. **只看 DB 總大小，不看 in-use 大小**。沒有差值就沒有 Defrag 收益。
5. **在控制平面繁忙時操作**。Defrag 的主要代價是可觀察到的 latency spike。

為了避免歧義，實務上可把這兩步記成：

- **Compaction**：先讓 `etcd_mvcc_db_total_size_in_use_in_bytes` 降下來
- **Defrag**：再讓 `etcd_mvcc_db_total_size_in_bytes` 降下來

## 可以怎麼向團隊解釋這件事

最實用的說法是：

> 在 Kubernetes 中，etcd Defrag 不是「清 cache」，而是「重寫 member 的 backend 檔案」。  
> 它可以回收磁碟，但代價是該 member 會有明顯停頓，所以必須逐台、低峰、看指標執行。

::: info 相關章節
- [為什麼需要 Defrag](./defrag)
- [Learner Mode](./learner-mode)
:::
