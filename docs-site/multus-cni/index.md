---
layout: doc
---

# Multus CNI 原始碼分析

::: tip 分析版本
本文件基於 commit [`522324ce`](https://github.com/k8snetworkplumbingwg/multus-cni/commit/522324cea1f8f936fa9b32985ed356be1f1f3cc5) 進行分析。
:::

## 專案簡介

**Multus CNI** 是 Kubernetes 生態系中用於為 Pod 附加多張網路介面的 CNI Meta-Plugin（元外掛）。標準 Kubernetes 叢集中每個 Pod 僅有一個網路介面（除 loopback 外），而 Multus 允許一個 Pod 同時擁有多個網路介面，實現多宿主（multi-homed）Pod。

- **GitHub**: [k8snetworkplumbingwg/multus-cni](https://github.com/k8snetworkplumbingwg/multus-cni)
- **License**: Apache 2.0
- **語言**: Go
- **模組名稱**: `gopkg.in/k8snetworkplumbingwg/multus-cni.v4`
- **所屬組織**: Kubernetes Network Plumbing Working Group（k8snetworkplumbingwg）

## 核心概念

Multus 作為 **Meta-Plugin**：

1. **預設網路（Default Network）**：由叢集原有的 CNI 外掛（如 Flannel、Calico）提供，每個 Pod 都有的 `eth0`
2. **附加網路（Additional Networks）**：透過 `NetworkAttachmentDefinition` CRD 定義，由 Pod Annotation 指定
3. **委派（Delegate）**：Multus 讀取設定後，依序呼叫各個下游 CNI 外掛（delegates）

## 文件導覽

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | 專案結構、8 個 Binary、套件設計、Thin vs Thick Plugin 模式 |
| [核心功能分析](./core-features) | CNI 委派流程、NetworkAttachmentDefinition、Pod Annotation 解析、NAD 查詢 |
| [Thick Plugin 深入剖析](./thick-plugin) | multus-daemon 伺服器架構、multus-shim 用戶端、Unix Socket 通訊、Prometheus 指標 |
| [設定參考](./configuration) | NetConf、NetworkSelectionElement、ControllerNetConf 完整欄位說明 |
