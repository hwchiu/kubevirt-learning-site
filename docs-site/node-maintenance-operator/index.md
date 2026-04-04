---
layout: doc
---

# Node Maintenance Operator 原始碼分析

::: tip 分析版本
本文件基於 commit [`d1a537be`](https://github.com/medik8s/node-maintenance-operator/commit/d1a537be397a0afb2fd034650a1ed329e72699a2) 進行分析。
:::

## 專案簡介

**Node Maintenance Operator (NMO)** 是一個 Kubernetes Operator，用於管理節點維護作業。當建立 NodeMaintenance 資源時，自動封鎖節點並安全驅逐 Pod；刪除時自動解除封鎖。特別針對 KubeVirt VirtualMachineInstance 工作負載進行了最佳化。

- **GitHub**: [medik8s/node-maintenance-operator](https://github.com/medik8s/node-maintenance-operator)
- **License**: Apache 2.0
- **語言**: Go (Operator SDK / kubebuilder v3)

## 文件導覽

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | 專案結構、Binary 入口、CRD 定義、建置系統 |
| [核心功能分析](./core-features) | Reconcile 狀態機、Drain 邏輯、Taint 管理、Lease 協調 |
| [控制器與 API](./controllers-api) | NodeMaintenance 型別、Webhook 驗證、RBAC 規則 |
| [外部整合](./integration) | KubeVirt/medik8s/OpenShift 整合、NHC 協調、etcd 保護 |
