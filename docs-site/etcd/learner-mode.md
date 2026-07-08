---
layout: doc
title: etcd - Learner Mode
---

# etcd - Learner Mode

## What a Learner Is

A learner is a **Raft non-voting member**. At the type level, etcd models it as a raft attribute of a member:

```go
// File: etcd/server/etcdserver/api/membership/member.go
type RaftAttributes struct {
    PeerURLs []string `json:"peerURLs"`
    IsLearner bool `json:"isLearner,omitempty"`
}
```

Adding a learner is not "add a normal member and flip a flag later". etcd creates it explicitly through `NewMemberAsLearner`:

```go
// File: etcd/server/etcdserver/api/membership/member.go
func NewMemberAsLearner(...) *Member {
    return newMember(name, peerURLs, memberID, true)
}
```

## Why Learner Mode Exists

The core value of learner mode is simple: **sync data first, join the voting set later**. That lowers the risk of changing quorum while a new node is still catching up.

The CLI exposes this directly:

```go
// File: etcd/etcdctl/ctlv3/command/member_command.go
cc.Flags().BoolVar(&isLearner, "learner", false, "indicates if the new member is raft learner")
```

![Quorum and standby-member architecture with learner mode](/diagrams/etcd/etcd-learner-1.png)

## Architecture View: Why Primary/Standby Needs Learner Mode

Architecturally, a learner should not be thought of as just another feature bit. It is a **buffer layer for membership change**.

In a production-oriented 5-member primary etcd cluster, the steady-state looks like this:

```text
                +---------------------+
                |   Leader (voter)    |
                +---------------------+
          / raft log   / raft log   / raft log   \ raft log
         v            v            v              v
 +------------------+ +------------------+ +------------------+ +------------------+
 | Follower (voter) | | Follower (voter) | | Follower (voter) | | Follower (voter) |
 +------------------+ +------------------+ +------------------+ +------------------+

Quorum = 3 / 5
```

The key properties are:

- the leader accepts writes and replicates the Raft log
- voting members define quorum
- a 5-member cluster tolerates two unavailable voters while keeping quorum
- any membership change still affects failure tolerance and quorum math

### The problem: a new node can count toward quorum before it has caught up

Without learner mode, adding a new node directly as a voting member changes the architecture immediately:

```text
                +---------------------+
                |   Leader (voter)    |
                +---------------------+
      /      |        |        \            \
     v       v        v         v            v
+------------------+ +------------------+ +------------------+ +------------------+ +----------------------+
| Follower (voter) | | Follower (voter) | | Follower (voter) | | Follower (voter) | | New Member (voter)   |
+------------------+ +------------------+ +------------------+ +------------------+ +----------------------+
                                                                 data still catching up

Quorum = 4 / 6
```

The risk is not that the node exists. The risk is:

- quorum moves from `3/5` to `4/6`
- but the new node may still be receiving snapshots, replaying Raft log, and warming its disk state
- in other words, **the quorum requirement rises before data synchronization is complete**

That is the architectural problem learner mode solves.

### What learner mode changes

With a learner, the cluster looks more like this:

```text
                +---------------------+
                |   Leader (voter)    |
                +---------------------+
      /      |        |        \            \
     v       v        v         v            v
+------------------+ +------------------+ +------------------+ +------------------+ +----------------------+
| Follower (voter) | | Follower (voter) | | Follower (voter) | | Follower (voter) | | Learner (non-voter)  |
+------------------+ +------------------+ +------------------+ +------------------+ +----------------------+
                                                                 sync snapshot/log

Quorum = still 3 / 5
```

That is the architectural value of a learner:

- it can receive snapshots and Raft log from the leader
- it does not immediately join the voting path
- it does not immediately change quorum from `3/5` to `4/6`
- only after it catches up does promotion become the next step

So learner mode is not mainly about "one more replica". It is about **separating data synchronization from voting-topology change**.

## Why This Matters for Primary/Standby Thinking

Many people approach primary/standby etcd using the mental model of a traditional primary/replica database:

- the primary serves traffic
- the standby keeps following data
- the standby takes over when the primary fails

But etcd is not a classic single-primary replication system. It is a **Raft membership system**. What matters is:

- which nodes count toward quorum
- which nodes only synchronize state without affecting votes
- when a synchronized node can safely become a voting member

So in etcd, the more precise model is not "primary cluster + standby cluster". It is:

- **primary cluster**
- **standby members inside that cluster**

Learner mode solves a **cluster membership transition** problem, not a **cross-cluster disaster recovery replication** problem.

## Three Risks Learner Mode Solves

### 1. Quorum grows before the new node is ready

This is the most direct risk. Without learner mode, a newly added member changes the voting topology first. With learner mode, the original quorum remains in place until the node is actually ready.

### 2. A replacement node enters the voting path while still unstable

During Kubernetes control-plane replacement, a new node often has to handle:

- disk initialization
- network and certificate setup
- snapshot intake
- Raft log catch-up

Learner mode moves that initialization cost into a non-voting phase instead of pushing it directly into the voting path.

### 3. "Data synchronized" and "safe to vote" become one step

That coupling is a common architecture mistake. Learner mode splits the flow into:

1. data synchronization
2. membership promotion

Once separated, the system can check:

- whether the learner is really in sync with the leader
- whether quorum still stays safe after promotion

That is exactly why `IsReadyToPromoteMember` and the related error paths exist.

## When Promotion Is Allowed

etcd does not allow arbitrary learner promotion. The most important limits are visible in the errors and tests:

- `server/etcdserver/errors/errors.go`: `can only promote a learner member which is in sync with leader`
- `tests/integration/clientv3/cluster_test.go`: a learner that is not started or not caught up must fail promotion

In addition, `RaftCluster.IsReadyToPromoteMember` checks whether the post-promotion quorum remains safe:

```go
// File: etcd/server/etcdserver/api/membership/cluster.go
nmembers := 1 // We count the learner to be promoted for the future quorum
nstarted := 1 // and we also count it as started.
nquorum := nmembers/2 + 1
if nstarted < nquorum {
    return false
}
```

The meaning is clear: **even if a learner has finished syncing, promotion must still be rejected if it would lead to an unsafe quorum position**.

## Constraints of Learner Mode

### 1. A learner cannot be part of initial bootstrap

The integration tests state this directly:

```go
// File: etcd/tests/integration/clientv3/kv_test.go
// bootstrapping a cluster with learner member is not supported.
```

So learner mode is for **existing-cluster expansion and replacement**, not initial cluster creation.

### 2. A learner only accepts serializable reads

`TestKVForLearner` verifies that a learner:

- succeeds on `OpGet(..., WithSerializable())`
- fails on normal linearizable `Get`
- fails on `Put`, `Delete`, and `Txn`

So a learner is not a read-write member, and not even a full read member. It offers a limited, non-linearizable read path.

### 3. A learner cannot become a leadership transfer target

`tests/integration/v3_leadership_test.go` verifies that leadership transfer to a learner must fail. That follows naturally from the fact that the learner is non-voting.

### 4. The number of learners is configurable, but limited

`server/embed/config.go` defines:

```go
// File: etcd/server/embed/config.go
fs.IntVar(&cfg.MaxLearners, "max-learners", membership.DefaultMaxLearners, ...)
```

And the corresponding failure exists in `server/etcdserver/api/membership/errors.go`:

- `ErrTooManyLearners`

So learner mode is not a mechanism for building an unlimited pool of passive observer nodes.

## Where Learner Mode Is Most Useful in Kubernetes

For Kubernetes operations, the two most practical uses are:

1. **replacing an etcd member on a failed control-plane node**
2. **expanding a stacked or external etcd cluster by syncing first and promoting later**

In a 5-member production cluster, that reduces the risk of consuming your maintenance margin by counting a still-cold node toward the future quorum too early.

## Can Learner Mode Build a Standby etcd Cluster for a Primary Cluster?

Short answer: **no, not directly**. Learner mode can create a **warm standby member inside the same etcd cluster**, but not a separate standby cluster that can be promoted independently.

That conclusion follows from the code and test behavior:

1. `etcdctl member add --learner` modifies the membership of an existing cluster. It does not create a second cluster.
2. `NewMemberAsLearner` only sets `IsLearner=true` on a member inside the same `RaftCluster`.
3. `tests/integration/clientv3/kv_test.go` explicitly says that bootstrapping with a learner is not supported, so learner mode is not how you initialize a standby cluster.
4. `max-learners` and `ErrTooManyLearners` also show that learners are controlled transitional members, not a built-in cross-site replication topology.

### The more precise statement

Learner mode is good for:

- pre-joining a new node to the same primary cluster
- letting it receive snapshots and Raft log first
- promoting it only after it catches up
- replacing an old member or completing a safe expansion

Learner mode is not a direct mechanism for:

- creating a separate standby etcd cluster with its own cluster ID
- maintaining a second cluster that continuously follows the primary as a learner
- turning that second cluster into the new primary with a built-in learner promotion path

Architecturally, the contrast looks like this:

**What learner mode can do**

```text
Primary etcd cluster
  ├─ voter
  ├─ voter
  ├─ voter
  ├─ voter
  ├─ voter
  └─ learner   <- warm standby inside the same cluster
```

**What learner mode does not directly do**

```text
Primary etcd cluster          Standby etcd cluster
  ├─ voter                      ├─ voter
  ├─ voter        X             ├─ voter
  ├─ voter                      ├─ voter
  ├─ voter                      ├─ voter
  └─ voter                      └─ voter

No built-in "learner link" between two independent clusters
```

### If your actual goal is a DR standby cluster

From the current etcd implementation, a learner is better understood as a **warm spare inside the cluster**, not as a **disaster-recovery replica outside the cluster**.

If your real goal is a cross-zone or cross-site standby cluster, the operational model is usually based on:

- periodic snapshot and restore
- backup distribution
- re-bootstrap during disaster recovery

That is not a capability directly provided by learner membership. This is an inference grounded in the current membership API, bootstrap limitations, and integration tests.

### How learner mode can still support a "near-standby" model

A practical primary-cluster workflow is:

1. run `member add --learner` on the existing primary cluster
2. start the new node and let it catch up with the leader
3. confirm that the learner is ready and meets `MemberPromote` requirements
4. promote it into a voting member
5. if the goal is replacement, remove the old member afterwards

That is a **safe rolling replacement / expansion** model. It gives you standby capacity inside the same cluster, not a second standby cluster.

## The Team-Level Mental Model

Learner mode is not a "cheap member". It is a **safety buffer before a node enters the voting set**:

- it can receive snapshots and Raft log
- it does not vote
- it does not accept normal writes
- it is promoted only after it catches up

::: info Related Pages
- [Why Defrag Matters](./defrag)
- [Defrag Operations in Kubernetes](./kubernetes-defrag)
:::
