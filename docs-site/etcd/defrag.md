---
layout: doc
title: etcd — 為什麼需要 Defrag
---

# etcd — 為什麼需要 Defrag

## 結論先講

etcd 需要 Defrag，不是因為資料還在成長，而是因為**資料刪掉之後，底層 bbolt 檔案往往不會自動縮小**。`Compact` 會清掉歷史 revision，讓空間變成「可重用」；`Defrag` 才會把這些空頁真正重寫到新檔案並釋放回檔案系統。

## 根因：邏輯空間釋放，不等於實體檔案縮小

`server/storage/mvcc/metrics.go` 定義了兩個最重要的 gauge：

```go
// 檔案: etcd/server/storage/mvcc/metrics.go
Name: "db_total_size_in_bytes"
Help: "Total size of the underlying database physically allocated in bytes."

Name: "db_total_size_in_use_in_bytes"
Help: "Total size of the underlying database logically in use in bytes."
```

這兩個指標對應兩種不同概念：

- `etcd_mvcc_db_total_size_in_bytes`：目前 bbolt 檔案實際占用多少磁碟
- `etcd_mvcc_db_total_size_in_use_in_bytes`：目前真正還在使用的資料量

當兩者差距愈大，代表「已刪除但尚未還給檔案系統」的空間愈多，也就愈有 Defrag 價值。

在 Kubernetes 維運裡，最常看的也就是這兩個指標：

1. `etcd_mvcc_db_total_size_in_use_in_bytes`
2. `etcd_mvcc_db_total_size_in_bytes`

它們各自反映的不是同一件事：

- `db_total_size_in_use_in_bytes` 比較接近「目前資料實際還需要多少空間」
- `db_total_size_in_bytes` 則是「底層 DB 檔案目前真的占了多少磁碟」

這個差異非常重要，因為 **compaction 與 defrag 分別影響的是不同指標**。

## 先講 compaction：為什麼也要一起理解

若只談 Defrag，會少掉一半的判斷依據。`tests/integration/metrics_test.go` 的流程其實是：

1. 先大量寫入資料
2. 執行 `CompactionRequest{Physical: true}`
3. 驗證 `db_total_size_in_use_in_bytes` 下降
4. 再做 Defrag
5. 驗證 `db_total_size_in_bytes` 下降

程式碼裡寫得很明確：

```go
// 檔案: etcd/tests/integration/metrics_test.go
// clear out historical keys, in use bytes should free pages
creq := &pb.CompactionRequest{Revision: int64(numPuts), Physical: true}

// defrag should give freed space back to fs
mc.Defragment(t.Context(), &pb.DefragmentRequest{})
```

也就是說：

- **Compaction** 先把歷史 revision 與不再需要的內容清掉，讓 `in use` 下降
- **Defrag** 再把已空出的頁面真正回收給檔案系統，讓 `db size` 下降

如果沒有先理解 compaction，就很容易誤以為 Defrag 應該同時讓兩個指標都大幅下降。

## API 本身怎麼定義 Defrag

`client/v3/maintenance.go` 對 Defragment 的註解已經直接說明使用時機：

```go
// 檔案: etcd/client/v3/maintenance.go
// Defragment releases wasted space from internal fragmentation on a given etcd member.
// Defragment is only needed when deleting a large number of keys and want to reclaim
// the resources.
// Defragment is an expensive operation.
```

重點有三個：

1. 它處理的是 **internal fragmentation**
2. 典型觸發情境是 **大量刪除 key**
3. 它是 **expensive operation**

## Defrag 實際做了什麼

真正的動作在 `server/storage/backend/backend.go`。流程不是「整理 page metadata」而已，而是**建立一個暫存 DB，逐個 bucket 複製活資料，最後 rename 覆蓋原檔**。

```go
// 檔案: etcd/server/storage/backend/backend.go
temp, err := os.CreateTemp(dir, "db.tmp.*")
tmpdb, err := bolt.Open(tdbp, 0o600, &options)
err = defragdb(b.db, tmpdb, defragLimit)
err = b.db.Close()
err = tmpdb.Close()
err = os.Rename(tdbp, dbp)
```

這段流程說明 Defrag 的本質是：

- 讀出舊 DB 的有效資料
- 寫入新的乾淨 DB
- 用新檔取代舊檔

所以它一定比單純 `Compact` 更重，也更接近一次「局部重建資料庫檔案」。

## 為什麼 Defrag 會影響線上流量

Defrag 之前，backend 會先鎖住三個重要路徑：

```go
// 檔案: etcd/server/storage/backend/backend.go
b.batchTx.LockOutsideApply()
b.mu.Lock()
b.readTx.Lock()
```

這代表 Defrag 期間：

- backend commit 路徑會被卡住
- read transaction reset 會阻擋讀路徑
- 不是單純背景低優先序任務

也因此 `etcdctl defrag` 沒有並行打全部節點，而是逐個 endpoint 執行：

```go
// 檔案: etcd/etcdctl/ctlv3/command/defrag_command.go
for _, ep := range endpointsFromCluster(cmd) {
    cfg.Endpoints = []string{ep}
    _, err := c.Defragment(ctx, ep)
}
```

## 怎麼判斷該不該做 Defrag

最直接的方法是觀察：

- `etcd_mvcc_db_total_size_in_bytes`
- `etcd_mvcc_db_total_size_in_use_in_bytes`
- `etcd_disk_defrag_inflight`
- `etcd_disk_backend_defrag_duration_seconds`

`server/storage/backend/metrics.go` 也把後兩者定義得很明確：

```go
// 檔案: etcd/server/storage/backend/metrics.go
Name: "backend_defrag_duration_seconds"
Name: "defrag_inflight"
```

其中：

- `defrag_inflight=1` 代表該 member 正在執行 Defrag
- `backend_defrag_duration_seconds` 可用來估算不同資料量下的停頓成本

### 這兩個核心 metrics 要怎麼判讀

| Metric | 主要受什麼影響 | 代表意義 |
|------|------|------|
| `etcd_mvcc_db_total_size_in_use_in_bytes` | **Compaction** | 邏輯上仍在使用的資料量 |
| `etcd_mvcc_db_total_size_in_bytes` | **Defrag** | 實體 DB 檔案目前占用的磁碟大小 |

實務上可以用這個心智模型：

- `in_use` 先掉了，但 `db_total_size` 還沒掉：代表已經 compact，但尚未 defrag
- `db_total_size` 跟著掉了：代表 defrag 真的把空頁回收回檔案系統
- 兩者幾乎沒有差距：代表 defrag 收益通常不高

## 測試怎麼證明 Defrag 真的有效

`tests/integration/metrics_test.go` 先大量寫入、再做 physical compaction、最後執行 Defrag，驗證結果是：

- compaction 後 `db_total_size_in_use_in_bytes` 下降
- defrag 後 `db_total_size_in_bytes` 才真正下降

這正好對應實務上的觀察：

- **Compaction 回收邏輯空間**
- **Defrag 回收實體磁碟空間**

如果用你在 Kubernetes 裡監看的兩個 metrics 來說，就是：

- `etcd_mvcc_db_total_size_in_use_in_bytes` 會先反映 compaction 的成果
- `etcd_mvcc_db_total_size_in_bytes` 則會在 defrag 後才明顯下降

::: info 相關章節
- [Kubernetes 中的 Defrag 操作](./kubernetes-defrag)
- [Learner Mode](./learner-mode)
:::
