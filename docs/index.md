---
layout: home

hero:
  name: "KubeVirt 學習指南"
  text: "基於 Kubernetes 的虛擬機器管理平台"
  tagline: 深入淺出 KubeVirt — 讓你的工程師快速上手，從架構到實作全面掌握
  image:
    src: https://raw.githubusercontent.com/kubevirt/community/main/logo/KubeVirt_icon.png
    alt: KubeVirt
  actions:
    - theme: brand
      text: 🏗️ 開始學習架構
      link: /architecture/overview
    - theme: alt
      text: 🔬 深入剖析 QEMU/KVM
      link: /deep-dive/qemu-kvm
    - theme: alt
      text: 📖 VMware 工程師指南
      link: /guides/vmware-to-kubevirt

features:
  - icon: 🖥️
    title: VM 與 Kubernetes 整合
    details: KubeVirt 透過 CRD 擴展 Kubernetes，讓 VM 與容器工作負載在同一叢集中並存，使用相同的 API、RBAC 與調度機制。

  - icon: ⚙️
    title: 五大核心元件
    details: virt-operator、virt-api、virt-controller、virt-handler、virt-launcher — 五個元件各司其職，構成完整的虛擬化管理平台。

  - icon: 🌐
    title: 彈性網路支援
    details: 支援 Pod 網路、Bridge、Masquerade、SR-IOV、Multus 多網卡，與 Kubernetes CNI 生態系完整整合。

  - icon: 💾
    title: 多元儲存方案
    details: 支援 PVC、DataVolume、ContainerDisk、EmptyDisk、HostPath，並提供執行時熱插拔 (Hotplug) 能力。

  - icon: 🚀
    title: 即時遷移 (Live Migration)
    details: 不中斷服務地將 VM 從一個節點遷移到另一個節點，支援記憶體頁面增量傳輸與儲存遷移。

  - icon: 📸
    title: 快照、備份與還原
    details: 完整的 VM 生命週期管理 — 快照 (Snapshot)、克隆 (Clone)、備份 (Backup)、匯出 (Export)，確保資料安全。

  - icon: 🔬
    title: QEMU/KVM 深入剖析
    details: 深入 virt-launcher 三層架構、Configurator 模式、DomainManager 介面、libvirt XML 產生流程，掌握虛擬化核心。

  - icon: 🪟
    title: Windows VM 最佳化
    details: 14 種 Hyper-V Enlightenment、時脈配置、EFI/TPM/Secure Boot、VirtIO 驅動安裝，打造生產級 Windows VM。

  - icon: 🔄
    title: Live Migration 實作細節
    details: 8 階段狀態機、Pre-copy/Post-copy/Multifd 策略、Migration Proxy 架構、libvirt API 呼叫流程完整解析。

  - icon: 🛡️
    title: 安全與效能調校
    details: SELinux/Namespace 隔離、SEV/TDX 機密運算、CPU Pinning、NUMA 拓撲、HugePages、網路與磁碟效能最佳化。

  - icon: 🔀
    title: VMware 工程師轉換指南
    details: 從 VMware vSphere/ESXi 概念對應到 KubeVirt，一對一功能對照表、操作指令對比、遷移策略。
---

## 📚 本指南涵蓋範圍

本學習指南基於 **KubeVirt 主幹程式碼**深入分析而成，涵蓋以下主題：

| 章節 | 說明 |
|------|------|
| [🏗️ 架構總覽](/architecture/overview) | 系統設計理念、技術棧、元件互動圖、VM 生命週期 |
| [⚙️ 核心元件](/components/virt-operator) | virt-operator、virt-api、virt-controller、virt-handler、virt-launcher 深度解析 |
| [📦 API 資源](/api-resources/vm-vmi) | 所有 CRD 型別完整說明：VM、VMI、Migration、Instancetype 等 |
| [🌐 網路](/networking/overview) | 網路架構、Bridge、Masquerade、SR-IOV、網路綁定插件 |
| [💾 儲存](/storage/overview) | ContainerDisk、PVC、DataVolume、Hotplug、儲存遷移 |
| [🛠️ virtctl](/virtctl/guide) | 完整 virtctl 指令參考手冊 |
| [🚀 進階功能](/advanced/live-migration) | Live Migration、Snapshot/Restore、Observability |
| [🔬 深入剖析](/deep-dive/qemu-kvm) | QEMU/KVM 核心、Windows 最佳化、Migration 實作、效能調校、安全架構 |
| [📖 實用指南](/guides/vmware-to-kubevirt) | VMware 轉換指南、故障排除手冊 |
| [👨‍💻 開發指南](/dev-guide/getting-started) | 開發環境設置、程式碼結構導覽 |

## 🔑 快速索引

### 我想了解…

- **KubeVirt 是什麼？** → [架構總覽](/architecture/overview)
- **VM 如何建立並啟動？** → [VM 生命週期流程](/architecture/lifecycle)
- **各元件的職責？** → [核心元件](/components/virt-operator)
- **VM 與 VMI 的差別？** → [VM 與 VMI](/api-resources/vm-vmi)
- **如何連線進 VM？** → [virtctl 存取操作](/virtctl/access)
- **如何做 Live Migration？** → [Live Migration](/advanced/live-migration) | [深入實作](/deep-dive/migration-internals)
- **如何管理 VM 儲存？** → [儲存架構](/storage/overview)
- **QEMU/KVM 如何運作？** → [QEMU/KVM 深入剖析](/deep-dive/qemu-kvm)
- **Windows VM 怎麼跑最快？** → [Windows VM 最佳化](/deep-dive/windows-optimization)
- **從 VMware 轉過來？** → [VMware 工程師指南](/guides/vmware-to-kubevirt)
- **效能不夠好？** → [效能調校指南](/deep-dive/performance-tuning)
- **出問題了？** → [故障排除手冊](/guides/troubleshooting)

## 🏷️ KubeVirt 核心概念速覽

```
Kubernetes Cluster
├── KubeVirt 系統元件
│   ├── virt-operator   (Deployment) — 負責安裝與管理所有 KubeVirt 元件
│   ├── virt-api        (Deployment) — HTTP API 入口點、Admission Webhook
│   ├── virt-controller (Deployment) — 叢集級控制器，管理 VM/VMI 生命週期
│   └── virt-handler    (DaemonSet)  — 節點代理，與 libvirt 溝通
│
├── VM 工作負載 (每個 VM 一個 Pod)
│   └── virt-launcher Pod
│       ├── virt-launcher 程序 — 命令接收與轉發
│       └── libvirtd + QEMU   — 實際執行虛擬機器
│
└── KubeVirt CRDs (自定義資源)
    ├── VirtualMachine (VM)          — 有狀態 VM，可停止/啟動
    ├── VirtualMachineInstance (VMI) — 正在執行中的 VM 實例
    ├── VirtualMachineInstancetype   — CPU/記憶體規格模板
    ├── VirtualMachinePreference     — 設備偏好配置
    ├── VirtualMachineSnapshot       — VM 快照
    └── VirtualMachineClone          — VM 克隆
```
