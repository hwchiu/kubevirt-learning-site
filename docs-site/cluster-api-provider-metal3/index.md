---
layout: doc
title: Cluster API Provider Metal3 — 專案簡介
---

# Cluster API Provider Metal3 — 專案簡介

Cluster API Provider Metal3（CAPM3）是 [Cluster API（CAPI）](https://cluster-api.sigs.k8s.io/) 的 Infrastructure Provider，讓使用者能以 Kubernetes 原生的宣告式 API 在**裸金屬（Bare Metal）**伺服器上部署與管理 Kubernetes 叢集。

CAPM3 是 [Metal3 生態系](https://metal3.io/) 的核心元件之一，結合 Ironic 裸金屬管理服務與 BareMetalHost（BMH）CRD，實現完整的伺服器 provisioning 自動化流程。

## 專案定位

```
// 檔案: main.go
var (
    controllerName = "cluster-api-provider-metal3-manager"
)
```

CAPM3 在 Kubernetes 生態系中扮演以下角色：

| 角色 | 說明 |
|------|------|
| Infrastructure Provider | 實作 CAPI InfrastructureCluster 與 InfrastructureMachine 介面 |
| Ironic 整合橋接 | 透過 BareMetalHost CRD 與 Ironic API 溝通 |
| IPAM 協調者 | 與 ip-address-manager 整合，管理裸金屬節點的 IP 位址 |
| 自動修復控制器 | 透過 Metal3Remediation 實作 CAPI MachineHealthCheck 的修復策略 |

## Metal3 技術棧概覽

CAPM3 的運作需要以下元件協同工作：

```
// 檔案: main.go
import (
    bmov1alpha1 "github.com/metal3-io/baremetal-operator/apis/metal3.io/v1alpha1"
    infrav1 "github.com/metal3-io/cluster-api-provider-metal3/api/v1beta2"
    ipamv1 "github.com/metal3-io/ip-address-manager/api/v1alpha1"
    clusterv1 "sigs.k8s.io/cluster-api/api/core/v1beta2"
)
```

**元件關係：**
- **Cluster API Core**：提供 Cluster、Machine、MachineDeployment 等核心物件
- **CAPM3**：實作 Metal3Cluster 與 Metal3Machine，對接 CAPI 框架
- **Baremetal Operator（BMO）**：管理 BareMetalHost，與 Ironic 通訊
- **Ironic**：實際執行伺服器 PXE 開機、映像寫入等低階操作
- **ip-address-manager（IPAM）**：為節點配置 IP 位址

## 主要 CRD 一覽

| CRD | API Group | 用途 |
|-----|-----------|------|
| `Metal3Cluster` | `infrastructure.cluster.x-k8s.io` | 代表一個裸金屬叢集的基礎設施設定 |
| `Metal3ClusterTemplate` | `infrastructure.cluster.x-k8s.io` | Metal3Cluster 的模板 |
| `Metal3Machine` | `infrastructure.cluster.x-k8s.io` | 代表一台裸金屬伺服器（對應一個 CAPI Machine）|
| `Metal3MachineTemplate` | `infrastructure.cluster.x-k8s.io` | Metal3Machine 的模板 |
| `Metal3DataTemplate` | `infrastructure.cluster.x-k8s.io` | 定義 metadata/networkdata 的模板 |
| `Metal3Data` | `infrastructure.cluster.x-k8s.io` | 渲染後的 metadata/networkdata 資料 |
| `Metal3DataClaim` | `infrastructure.cluster.x-k8s.io` | 向 DataTemplate 申請資料的請求 |
| `Metal3Remediation` | `infrastructure.cluster.x-k8s.io` | 觸發裸金屬節點修復 |
| `Metal3RemediationTemplate` | `infrastructure.cluster.x-k8s.io` | Metal3Remediation 的模板 |

## 版本相容性

| CAPM3 版本 | Cluster API 版本 | API 版本 |
|-----------|----------------|---------|
| v1.8.X – v1.11.X | v1beta1 | v1beta1 |
| v1.12.X | v1beta2 | v1beta2 |

::: tip 目前版本
本文件以 CAPM3 v1.12.x（API v1beta2）為基礎撰寫，主要 API 版本為 `infrastructure.cluster.x-k8s.io/v1beta2`。
:::

## 控制器清單

```
// 檔案: main.go
var (
    metal3MachineConcurrency         int
    metal3ClusterConcurrency         int
    metal3DataTemplateConcurrency    int
    metal3DataConcurrency            int
    metal3LabelSyncConcurrency       int
    metal3MachineTemplateConcurrency int
    metal3RemediationConcurrency     int
)
```

CAPM3 manager 啟動以下控制器：

| 控制器 | 檔案 | 負責物件 |
|--------|------|---------|
| `Metal3ClusterReconciler` | `controllers/metal3cluster_controller.go` | Metal3Cluster |
| `Metal3MachineReconciler` | `controllers/metal3machine_controller.go` | Metal3Machine |
| `Metal3DataTemplateReconciler` | `controllers/metal3datatemplate_controller.go` | Metal3DataTemplate |
| `Metal3DataReconciler` | `controllers/metal3data_controller.go` | Metal3Data |
| `Metal3MachineTemplateReconciler` | `controllers/metal3machinetemplate_controller.go` | Metal3MachineTemplate |
| `Metal3LabelSyncReconciler` | `controllers/metal3labelsync_controller.go` | Node Label Sync |
| `Metal3RemediationReconciler` | `controllers/metal3remediation_controller.go` | Metal3Remediation |

## 快速安裝

使用 `clusterctl` 安裝 Metal3 provider：

```bash
# 檔案: docs/getting-started.md（參考指令）
# 1. 安裝 CAPI core、bootstrap、control-plane providers
clusterctl init --core cluster-api:v1.12.0 \
    --bootstrap kubeadm:v1.12.0 \
    --control-plane kubeadm:v1.12.0

# 2. 安裝 Metal3 infrastructure provider
clusterctl init --infrastructure metal3:v1.12.0
```

::: warning 注意
從 v0.5.0 起，Baremetal Operator 已與 CAPM3 部署解耦。使用 `clusterctl init --infrastructure metal3` 時，BMO **不會**自動安裝，需要額外手動部署。
:::

## 文件導覽

| 頁面 | 說明 |
|------|------|
| [系統架構](/cluster-api-provider-metal3/architecture) | Metal3 Stack 整體架構與元件關係 |
| [核心功能](/cluster-api-provider-metal3/core-features) | Metal3Cluster/Metal3Machine/Metal3Data 的功能詳解 |
| [控制器與 API](/cluster-api-provider-metal3/controllers-api) | 各控制器的 Reconcile 邏輯與 CRD 詳解 |
| [裸金屬管理](/cluster-api-provider-metal3/baremetal) | BareMetalHost 選取、provisioning 狀態機 |
| [外部整合](/cluster-api-provider-metal3/integration) | Ironic、CAPI 框架、IPAM 整合說明 |
| [節點修復](/cluster-api-provider-metal3/remediation) | Metal3Remediation 修復策略 |
| [學習路徑](/cluster-api-provider-metal3/learning-path/) | 推薦學習順序 |

::: info 相關章節
- [系統架構](/cluster-api-provider-metal3/architecture)
- [核心功能](/cluster-api-provider-metal3/core-features)
- [學習路徑](/cluster-api-provider-metal3/learning-path/)
:::
