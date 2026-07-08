---
layout: doc
title: etcd - Defrag Operations in Kubernetes
---

# etcd - Defrag Operations in Kubernetes

## Framing the Problem

When etcd is the backend for Kubernetes, defrag is no longer just internal housekeeping. It **directly affects kube-apiserver latency and control-plane stability**. Every API write, read, and watch path eventually lands in etcd.

![Operational flow of etcd defrag in Kubernetes](/diagrams/etcd/etcd-kubernetes-defrag-1.png)

In this chapter, the operational diagrams use a **5-member etcd cluster** as the default production mental model. That is not because smaller clusters are invalid, but because 5 members make the maintenance tradeoffs more realistic: you still defrag one member at a time, but you have a clearer picture of quorum and service margin while one backend is stalled.

## Why Kubernetes Operations Must Be More Conservative

`client/v3/maintenance.go` already says defrag is expensive, and `backend.go` shows that it locks transaction and read paths:

```go
// File: etcd/server/storage/backend/backend.go
b.batchTx.LockOutsideApply()
b.mu.Lock()
b.readTx.Lock()
```

For a Kubernetes control plane, that can surface as:

- higher API request latency
- slower watch and list handling
- short timeouts if the affected member is serving meaningful traffic

So in Kubernetes, defrag should be treated as an **operational event**, not as a harmless background command.

## Why etcdctl Processes Members One by One

`etcdctl defrag` is implemented as a per-endpoint loop, not as a parallel fan-out:

```go
// File: etcd/etcdctl/ctlv3/command/defrag_command.go
for _, ep := range endpointsFromCluster(cmd) {
    cfg.Endpoints = []string{ep}
    _, err := c.Defragment(ctx, ep)
}
```

That implementation is already an operational hint: **do not defrag multiple members at the same time**.

In Kubernetes this matters even more because:

- while one member stalls, healthy members can still absorb traffic
- if several members are defragged together, control-plane latency and quorum risk rise much faster
- even in a 5-member cluster, the goal is to preserve your extra fault margin rather than spend it on parallel maintenance

## Recommended Sequence in Kubernetes

### 1. First decide whether defrag is worth it

Check:

- `etcd_mvcc_db_total_size_in_bytes`
- `etcd_mvcc_db_total_size_in_use_in_bytes`
- `etcd_server_quota_backend_bytes`

If `db_total_size` and `db_total_size_in_use` are already close, defrag benefit is limited. If the gap is large, there is a stronger reason to accept the stall cost.

There is one critical prerequisite here: **read compaction and defrag separately**.

### 1.1 Read compaction first, then defrag

`tests/integration/metrics_test.go` verifies:

- after compaction, `etcd_mvcc_db_total_size_in_use_in_bytes` goes down
- after defrag, `etcd_mvcc_db_total_size_in_bytes` goes down

So in Kubernetes, the interpretation should be:

| Metric | Operational meaning |
|------|------|
| `etcd_mvcc_db_total_size_in_use_in_bytes` | live logical data size; better signal for compaction effect |
| `etcd_mvcc_db_total_size_in_bytes` | physical DB file size on disk; better signal for defrag effect |

If you see:

- `in_use` already lower, but `db_total_size` still high: **compaction happened, defrag has not**
- `in_use` barely moved: the issue may be **insufficient compaction**, not missing defrag

That is why defrag should not be treated as step one. It is usually step two after compaction.

### 2. Process one member at a time

Defrag each member individually. This is not only a best practice; it matches the way `etcdctl` itself is written.

For a 5-member cluster, a practical sequence is:

1. pick one member with the largest reclaimable gap
2. defrag that member only
3. wait for metrics and API latency to normalize
4. continue to the next member only after the cluster is fully steady again

### 3. Observe recovery before moving on

At minimum, verify:

- `etcd_disk_defrag_inflight` is back to `0`
- `etcd_mvcc_db_total_size_in_bytes` has dropped as expected
- kube-apiserver and controller-manager are not seeing sustained timeouts

### 4. Avoid control-plane peak periods

Because backend locks directly amplify request latency, avoid scheduling defrag during:

- large CRD or operator rollouts
- heavy Pod churn
- intense namespace, Lease, or Event write bursts

## Built-In Automation Clue from etcd

etcd itself exposes an automatic defrag threshold during bootstrap:

```go
// File: etcd/server/embed/config.go
fs.UintVar(&cfg.BootstrapDefragThresholdMegabytes, "bootstrap-defrag-threshold-megabytes", 0, ...)
```

The logic lives in `server/etcdserver/bootstrap.go`:

```go
// File: etcd/server/etcdserver/bootstrap.go
freeableMemory := uint(size - sizeInUse)
thresholdBytes := cfg.BootstrapDefragThresholdMegabytes * 1024 * 1024
if freeableMemory < thresholdBytes {
    return nil
}
return be.Defrag()
```

That shows etcd itself already uses the same principle: only defrag when `size - sizeInUse` is large enough to justify it.

## Mistakes to Avoid in Kubernetes

1. **Treating compaction as defrag**. Compaction does not guarantee that the DB file shrinks.
2. **Treating defrag as compaction**. Defrag does not replace revision cleanup.
3. **Defragging multiple members at the same time**. That goes against the intended execution model.
4. **Looking only at total DB size**. Without comparing `in_use`, you cannot judge benefit.
5. **Running defrag during a busy control-plane window**. The main cost is an observable latency spike.

To keep the mental model clean:

- **Compaction**: first reduce `etcd_mvcc_db_total_size_in_use_in_bytes`
- **Defrag**: then reduce `etcd_mvcc_db_total_size_in_bytes`

## A Simple Team-Level Explanation

The most practical way to explain this to operators is:

> In Kubernetes, etcd defrag is not "clearing cache". It is rewriting a member's backend file.  
> It can return disk space, but the cost is a real stall on that member, so it should be run one member at a time, during low load, while watching the right metrics.

::: info Related Pages
- [Why Defrag Matters](./defrag)
- [Learner Mode](./learner-mode)
:::
