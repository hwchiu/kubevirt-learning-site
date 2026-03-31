# KubeVirt 學習指南 📘

> 為工程團隊打造的 KubeVirt 深度學習網站 — 涵蓋架構設計、核心元件、QEMU/KVM 深入剖析、Windows 最佳化、Live Migration 實作、效能調校、安全架構、VMware 轉換指南等。

🌐 **線上閱讀：[https://hwchiu.github.io/kubevirt-learning-site/](https://hwchiu.github.io/kubevirt-learning-site/)**

---

## 📖 內容總覽

本站共 **37 頁**詳細繁體中文技術文件，約 **28,000+** 行，系統性地解析 [KubeVirt](https://kubevirt.io/) 專案的設計與實作。

| 章節 | 頁數 | 說明 |
|------|:----:|------|
| **🏗️ 架構總覽** | 2 | 系統架構全景、元件關係圖、VM 生命週期狀態機 |
| **⚙️ 核心元件** | 5 | virt-operator、virt-api、virt-controller、virt-handler、virt-launcher 深入剖析 |
| **📋 API 資源** | 5 | VM/VMI、ReplicaSet/Pool、Migration、Instancetype/Preference、Snapshot/Clone/Export |
| **🌐 網路** | 3 | 兩階段網路架構、Bridge/Masquerade 模式、SR-IOV 與進階網路 |
| **💾 儲存** | 4 | 儲存架構總覽、ContainerDisk、PVC/DataVolume、Hotplug 熱插拔 |
| **🖥️ virtctl** | 2 | 完整指令參考手冊、VM 存取操作詳解（Console/VNC/SSH） |
| **🚀 進階功能** | 3 | Live Migration、Snapshot & Restore、Observability（Metrics/日誌） |
| **🔬 深入剖析** | 6 | QEMU/KVM 核心、Windows VM 最佳化、Migration 實作、效能調校、安全架構、GPU 直通 |
| **📖 實用指南** | 4 | Quick Start、VMware 轉換指南、高可用 & 災難恢復、故障排除手冊 |
| **🛠️ 開發指南** | 2 | 開發環境設置、程式碼架構導覽 |

### 🔥 亮點內容

- **QEMU/KVM 虛擬化核心** — 三層架構、15+ Configurator 模式、DomainManager 35 個方法、libvirt XML 產生流程
- **Windows VM 最佳化** — 14 種 Hyper-V Enlightenment、時脈配置、EFI/TPM/Secure Boot
- **Live Migration 完整實作** — 8 階段狀態機、Pre-copy/Post-copy/Multifd 策略、Migration Proxy
- **VMware 工程師專屬指南** — vSphere 概念一對一對應、操作指令對照、遷移策略
- **GPU/vGPU 直通** — VFIO、Mediated Devices、Device Plugin 架構
- **高可用 & 災難恢復** — EvictionStrategy、RunStrategy、Velero 整合

### 適合對象

- 從 VMware vSphere 轉換到 KubeVirt 的 **虛擬化工程師**
- 準備導入 KubeVirt 的 **平台工程師**
- 需要理解 KubeVirt 內部機制的 **SRE / DevOps 工程師**
- 想要貢獻 KubeVirt 的 **開發者**
- 正在評估 Kubernetes 上虛擬化方案的 **架構師**

---

## 🚀 快速開始

### 線上閱讀

直接前往 **[https://hwchiu.github.io/kubevirt-learning-site/](https://hwchiu.github.io/kubevirt-learning-site/)**，無需安裝任何工具。

### 本地開發

```bash
# 克隆專案
git clone https://github.com/hwchiu/kubevirt-learning-site.git
cd kubevirt-learning-site

# 安裝依賴
npm install

# 啟動本地開發伺服器（支援 Hot Reload）
npm run dev

# 建置靜態網站
npm run build

# 預覽建置結果
npm run preview
```

> **環境需求：** Node.js >= 18

---

## 📁 專案結構

```
kubevirt-learning-site/
├── docs/
│   ├── .vitepress/
│   │   └── config.js          # VitePress 設定（導覽列、側邊欄、搜尋）
│   ├── index.md               # 首頁
│   ├── architecture/          # 架構總覽
│   │   ├── overview.md        #   系統架構
│   │   └── lifecycle.md       #   VM 生命週期
│   ├── components/            # 核心元件
│   │   ├── virt-operator.md
│   │   ├── virt-api.md
│   │   ├── virt-controller.md
│   │   ├── virt-handler.md
│   │   └── virt-launcher.md
│   ├── api-resources/         # API 資源
│   │   ├── vm-vmi.md
│   │   ├── replica-pool.md
│   │   ├── migration.md
│   │   ├── instancetype.md
│   │   └── snapshot-clone.md
│   ├── networking/            # 網路
│   │   ├── overview.md
│   │   ├── bridge-masquerade.md
│   │   └── sriov.md
│   ├── storage/               # 儲存
│   │   ├── overview.md
│   │   ├── container-disk.md
│   │   ├── pvc-datavolume.md
│   │   └── hotplug.md
│   ├── deep-dive/             # 🔬 深入剖析
│   │   ├── qemu-kvm.md        #   QEMU/KVM 虛擬化核心
│   │   ├── windows-optimization.md  # Windows VM 最佳化
│   │   ├── migration-internals.md   # Live Migration 實作
│   │   ├── performance-tuning.md    # 效能調校
│   │   ├── security.md        #   安全架構
│   │   └── gpu-passthrough.md #   GPU/vGPU 直通
│   ├── guides/                # 📖 實用指南
│   │   ├── quickstart.md      #   快速開始
│   │   ├── vmware-to-kubevirt.md  # VMware 轉換指南
│   │   ├── ha-dr.md           #   高可用 & 災難恢復
│   │   └── troubleshooting.md #   故障排除
│   ├── virtctl/               # CLI 工具
│   │   ├── guide.md
│   │   └── access.md
│   ├── advanced/              # 進階功能
│   │   ├── live-migration.md
│   │   ├── snapshots.md
│   │   └── observability.md
│   └── dev-guide/             # 開發指南
│       ├── getting-started.md
│       └── code-structure.md
└── package.json
```

---

## 🔧 技術棧

- **[VitePress](https://vitepress.dev/)** v1.6 — Vue 驅動的靜態網站生成器
- **GitHub Pages** — 靜態網站託管（`gh-pages` branch）
- 內建全文搜尋（VitePress Local Search）

---

## 🤝 貢獻

歡迎提交 Pull Request 補充或修正內容：

1. Fork 這個 repo
2. 建立你的分支：`git checkout -b feature/improve-networking-docs`
3. 編輯 `docs/` 目錄下的 Markdown 檔案
4. 本地預覽確認：`npm run dev`
5. 提交變更：`git commit -m 'docs: 改進網路章節說明'`
6. 推送並建立 PR

### 內容撰寫原則

- 使用**繁體中文**
- 技術名詞保留英文原文（如 Pod、Node、CRD）
- 提供可執行的 YAML 範例
- 善用 VitePress 提示框（`::: tip`、`::: warning`、`::: danger`）

---

## 📜 授權

本文件內容基於 [KubeVirt](https://github.com/kubevirt/kubevirt) 開源專案整理而成。  
KubeVirt 採用 [Apache License 2.0](https://github.com/kubevirt/kubevirt/blob/main/LICENSE) 授權。
