---
layout: doc
title: etcd - Why Defrag Matters
---

# etcd - Why Defrag Matters

## The Short Version

etcd needs defragmentation not because the live dataset is always growing, but because **deleting data does not automatically shrink the underlying bbolt database file**. `Compact` removes historical revisions and turns space into reusable free pages. `Defrag` is the operation that rewrites the backend and returns those free pages to the filesystem.

## Root Cause: Logical Reclamation Is Not Physical Shrinkage

![Compaction and defrag space semantics](/diagrams/etcd/etcd-defrag-1.png)

`server/storage/mvcc/metrics.go` defines the two most important gauges for understanding this behavior:

```go
// File: etcd/server/storage/mvcc/metrics.go
Name: "db_total_size_in_bytes"
Help: "Total size of the underlying database physically allocated in bytes."

Name: "db_total_size_in_use_in_bytes"
Help: "Total size of the underlying database logically in use in bytes."
```

These two metrics represent different things:

- `etcd_mvcc_db_total_size_in_bytes`: how much disk the bbolt file physically occupies
- `etcd_mvcc_db_total_size_in_use_in_bytes`: how much space is still logically in use by live data

The larger the gap between them, the more deleted-but-not-yet-returned space exists, and the stronger the case for defrag.

In Kubernetes operations, these are usually the two first metrics people watch:

1. `etcd_mvcc_db_total_size_in_use_in_bytes`
2. `etcd_mvcc_db_total_size_in_bytes`

They do not answer the same question:

- `db_total_size_in_use_in_bytes` is closer to "how much space the live dataset still needs"
- `db_total_size_in_bytes` is "how much disk the DB file actually occupies right now"

This distinction matters because **compaction and defrag affect different metrics**.

## Why Compaction Must Be Explained Together with Defrag

If you discuss defrag alone, you miss half the operational picture. The flow in `tests/integration/metrics_test.go` is:

1. write enough data to expand the DB
2. run `CompactionRequest{Physical: true}`
3. verify that `db_total_size_in_use_in_bytes` drops
4. run defrag
5. verify that `db_total_size_in_bytes` drops

The test makes the intent explicit:

```go
// File: etcd/tests/integration/metrics_test.go
// clear out historical keys, in use bytes should free pages
creq := &pb.CompactionRequest{Revision: int64(numPuts), Physical: true}

// defrag should give freed space back to fs
mc.Defragment(t.Context(), &pb.DefragmentRequest{})
```

In practice, that means:

- **Compaction** clears obsolete revisions and reduces `in use`
- **Defrag** rewrites the backend and reduces physical `db size`

Without that distinction, it is easy to expect defrag to make both metrics drop in the same way.

## How the API Defines Defrag

`client/v3/maintenance.go` describes defragmentation directly:

```go
// File: etcd/client/v3/maintenance.go
// Defragment releases wasted space from internal fragmentation on a given etcd member.
// Defragment is only needed when deleting a large number of keys and want to reclaim
// the resources.
// Defragment is an expensive operation.
```

Three points matter:

1. it addresses **internal fragmentation**
2. it is most relevant after **large amounts of deletion**
3. it is an **expensive operation**

## What Defrag Actually Does

The real work happens in `server/storage/backend/backend.go`. The operation is not just metadata cleanup. etcd **creates a temporary database, copies only live bucket data into it, then replaces the original DB file**.

```go
// File: etcd/server/storage/backend/backend.go
temp, err := os.CreateTemp(dir, "db.tmp.*")
tmpdb, err := bolt.Open(tdbp, 0o600, &options)
err = defragdb(b.db, tmpdb, defragLimit)
err = b.db.Close()
err = tmpdb.Close()
err = os.Rename(tdbp, dbp)
```

So the operation is effectively:

- read live data from the old DB
- write it into a clean new DB
- replace the old file with the new one

That is why defrag is far heavier than compaction and is closer to a backend file rebuild.

## Why Defrag Affects Online Traffic

Before defrag starts, the backend locks several critical paths:

```go
// File: etcd/server/storage/backend/backend.go
b.batchTx.LockOutsideApply()
b.mu.Lock()
b.readTx.Lock()
```

That means:

- backend commit activity is blocked
- read transaction reset blocks read-side progress
- this is not just a cheap background cleanup task

This is also why `etcdctl defrag` iterates endpoint by endpoint rather than blasting all members at once:

```go
// File: etcd/etcdctl/ctlv3/command/defrag_command.go
for _, ep := range endpointsFromCluster(cmd) {
    cfg.Endpoints = []string{ep}
    _, err := c.Defragment(ctx, ep)
}
```

## How to Decide Whether Defrag Is Worth It

The most direct signals are:

- `etcd_mvcc_db_total_size_in_bytes`
- `etcd_mvcc_db_total_size_in_use_in_bytes`
- `etcd_disk_defrag_inflight`
- `etcd_disk_backend_defrag_duration_seconds`

`server/storage/backend/metrics.go` defines the last two clearly:

```go
// File: etcd/server/storage/backend/metrics.go
Name: "backend_defrag_duration_seconds"
Name: "defrag_inflight"
```

Meaning:

- `defrag_inflight=1` means defrag is currently running on that member
- `backend_defrag_duration_seconds` helps estimate stall cost for different backend sizes

### How to Read the Two Core Metrics

| Metric | Mainly affected by | Meaning |
|------|------|------|
| `etcd_mvcc_db_total_size_in_use_in_bytes` | **Compaction** | logical size still used by live data |
| `etcd_mvcc_db_total_size_in_bytes` | **Defrag** | physical size of the DB file on disk |

A useful operational model is:

- `in_use` drops first but `db_total_size` does not: compaction happened, defrag has not
- `db_total_size` drops afterwards: defrag actually returned free pages to the filesystem
- both values are already close: defrag usually has limited benefit

## How the Tests Prove the Behavior

`tests/integration/metrics_test.go` writes enough data to grow the DB, performs physical compaction, then runs defrag. The expected result is:

- after compaction, `db_total_size_in_use_in_bytes` goes down
- after defrag, `db_total_size_in_bytes` finally goes down

This matches production behavior exactly:

- **compaction reclaims logical space**
- **defrag reclaims physical disk space**

Using the two metrics from Kubernetes:

- `etcd_mvcc_db_total_size_in_use_in_bytes` reflects the effect of compaction first
- `etcd_mvcc_db_total_size_in_bytes` drops later when defrag finishes

::: info Related Pages
- [Defrag Operations in Kubernetes](./kubernetes-defrag)
- [Learner Mode](./learner-mode)
:::
