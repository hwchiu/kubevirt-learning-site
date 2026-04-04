---
layout: home

hero:
  name: "KubeVirt 生態系"
  text: "原始碼深度分析"
  tagline: 深入剖析 KubeVirt 生態系各專案的架構設計、核心元件與實作細節
  image:
    src: https://raw.githubusercontent.com/kubevirt/community/main/logo/KubeVirt_icon.png
    alt: KubeVirt
  actions:
    - theme: brand
      text: 🖥️ KubeVirt
      link: /kubevirt/architecture/overview
    - theme: alt
      text: 💾 CDI
      link: /containerized-data-importer/
    - theme: alt
      text: 📊 Monitoring
      link: /monitoring/
    - theme: alt
      text: 📋 Instancetypes
      link: /common-instancetypes/
    - theme: alt
      text: 🔧 NMO
      link: /node-maintenance-operator/
    - theme: alt
      text: 🚚 Forklift
      link: /forklift/

features:
  - icon: 🖥️
    title: KubeVirt
    details: 基於 Kubernetes 的虛擬機器管理平台 — 架構設計、五大核心元件、CRD 資源、網路/儲存/遷移等完整原始碼分析。
    link: /kubevirt/architecture/overview
    linkText: 開始閱讀

  - icon: 💾
    title: Containerized Data Importer (CDI)
    details: Kubernetes 持久化資料卷的資料匯入框架 — 負責將 VM 映像檔匯入 PVC，支援多種資料來源與傳輸方式。
    link: /containerized-data-importer/
    linkText: 開始閱讀

  - icon: 📊
    title: Monitoring
    details: KubeVirt 生態系集中式監控基礎設施 — 75 個告警 Runbook、100+ Prometheus 指標、Grafana 儀表板與 Linter 工具。
    link: /monitoring/
    linkText: 開始閱讀

  - icon: 📋
    title: Common Instancetypes
    details: 標準化 VM 實例類型與偏好設定 — 7 大系列 43 種 Instancetype、18+ OS Preference，類似 AWS EC2 Instance Types。
    link: /common-instancetypes/
    linkText: 開始閱讀

  - icon: 🔧
    title: Node Maintenance Operator
    details: Kubernetes 節點維護自動化 — 自動封鎖/驅逐/解封節點，針對 KubeVirt VM 工作負載最佳化的 Operator。
    link: /node-maintenance-operator/
    linkText: 開始閱讀

  - icon: 🚚
    title: Forklift
    details: VM 遷移平台 — 支援 vSphere、oVirt、OpenStack、Hyper-V、OVA 等多來源至 KubeVirt 的自動化遷移，含增量遷移與 XCOPY 加速。
    link: /forklift/
    linkText: 開始閱讀
---

## 📚 專案總覽

本站針對 KubeVirt 生態系的開源專案進行**原始碼級別**的深度分析，幫助工程師快速理解各專案的設計理念與實作細節。

| 專案 | 說明 | 狀態 |
|------|------|------|
| [KubeVirt](/kubevirt/architecture/overview) | 在 Kubernetes 上運行虛擬機器的核心平台 | ✅ 完整分析 |
| [CDI](/containerized-data-importer/) | 將 VM 映像匯入 Kubernetes PVC 的資料管理框架 | ✅ 完整分析 |
| [Monitoring](/monitoring/) | KubeVirt 生態系集中式監控基礎設施 | ✅ 完整分析 |
| [Common Instancetypes](/common-instancetypes/) | 標準化 VM 實例類型與 OS 偏好設定 | ✅ 完整分析 |
| [Node Maintenance Operator](/node-maintenance-operator/) | Kubernetes 節點維護自動化 Operator | ✅ 完整分析 |
| [Forklift](/forklift/) | 多來源 VM 遷移至 KubeVirt 的自動化平台 | ✅ 完整分析 |

## 🔗 原始碼連結

所有分析皆基於以下 GitHub 專案的原始碼：

- **KubeVirt**: [github.com/kubevirt/kubevirt](https://github.com/kubevirt/kubevirt)
- **CDI**: [github.com/kubevirt/containerized-data-importer](https://github.com/kubevirt/containerized-data-importer)
- **Monitoring**: [github.com/kubevirt/monitoring](https://github.com/kubevirt/monitoring)
- **Common Instancetypes**: [github.com/kubevirt/common-instancetypes](https://github.com/kubevirt/common-instancetypes)
- **Node Maintenance Operator**: [github.com/medik8s/node-maintenance-operator](https://github.com/medik8s/node-maintenance-operator)
- **Forklift**: [github.com/kubev2v/forklift](https://github.com/kubev2v/forklift)
