---
layout: doc
title: etcd - Overview
---

# etcd - The Data Core of the Kubernetes Control Plane

::: tip Analyzed Version
This chapter is based on commit [`6e470567`](https://github.com/etcd-io/etcd/commit/6e4705678926d5d0982538896acc087d21e09db5).
:::

## Introduction

**etcd** is a distributed key-value store built around **Raft**. In Kubernetes, it is the persistence layer for the control plane. The upstream `README.md` positions etcd as a reliable key-value store, while the `client/v3`, `server`, and `raft` modules provide the API surface, storage engine, and consensus machinery.

![High-level role of etcd in Kubernetes](/diagrams/etcd/etcd-overview-1.png)

- **GitHub**: [etcd-io/etcd](https://github.com/etcd-io/etcd)
- **License**: Apache 2.0
- **Language**: Go
- **Primary role**: backend state store for the Kubernetes API server

## Why This Chapter Focuses on Defrag and Learner Mode

In real Kubernetes operations, two etcd topics repeatedly cause confusion and incidents:

| Topic | Why it matters |
|------|------|
| **Defrag** | Deletes and compaction do not automatically shrink the underlying bbolt file, so disk usage and I/O pressure can keep growing |
| **Learner Mode** | A new member can sync data first as a non-voting node, reducing the risk of changing quorum too early |

## Reading Guide

| Page | Purpose |
|------|------|
| [Why Defrag Matters](./defrag) | Explains the storage root cause of defrag, the cost of the operation, and how the key metrics behave |
| [Defrag Operations in Kubernetes](./kubernetes-defrag) | Covers control-plane impact, operational sequencing, and how to read the metrics in Kubernetes |
| [Learner Mode](./learner-mode) | Explains learner membership, promote safety checks, quorum protection, and standby-member architecture |

## Key Source Files

- `etcd/README.md`
- `etcd/client/v3/maintenance.go`
- `etcd/server/storage/backend/backend.go`
- `etcd/server/storage/mvcc/metrics.go`
- `etcd/server/etcdserver/api/membership/cluster.go`
- `etcd/server/etcdserver/api/membership/member.go`
- `etcd/tests/integration/clientv3/cluster_test.go`
- `etcd/tests/integration/clientv3/kv_test.go`

::: info Related Pages
- [Why Defrag Matters](./defrag)
- [Defrag Operations in Kubernetes](./kubernetes-defrag)
- [Learner Mode](./learner-mode)
:::
