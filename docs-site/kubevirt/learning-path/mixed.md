---
layout: doc
title: KubeVirt — 學習路徑 D：整合式
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# 學習路徑 D：整合式

> **適合對象**：熟悉 Kubernetes 但完全沒有使用過 KubeVirt 的工程師。
> 本路徑依照「理解 → 架構 → 實作 → 深入」的順序設計，每個階段包含情境導引、精選閱讀與自我測驗。

---

## 階段一：建立問題意識

::: tip 為什麼要學這個？
當你遇到需要在 K8s 上跑 VM 的需求時（例如：遺留系統無法容器化、需要 Windows 授權環境、效能需要近裸機等），KubeVirt 是目前最成熟的解決方案。你不需要拋棄現有的 K8s 工具鏈，只需要在上面新增 VM 的能力。
:::

### 📚 精選閱讀

| 文件 | 說明 |
|------|------|
| [架構總覽](/kubevirt/architecture/overview) | 理解 KubeVirt 是什麼、解決什麼問題、核心設計哲學 |

### ✅ 自我測驗

<QuizQuestion
  question="1. KubeVirt 的核心設計理念是什麼？"
  :options='[
    "讓 VM 在 Container Runtime 內部運行",
    "讓 VM 成為 Kubernetes 的原生資源，用 K8s API 管理",
    "替代 Docker 成為新的容器引擎",
    "把 K8s API Server 直接移植到 Hypervisor",
  ]'
  :answer="1"
  explanation="KubeVirt 的核心設計理念是讓 VM 成為 K8s 原生資源，通過 CRD（VirtualMachine、VirtualMachineInstance）讓開發者用同一套 K8s API 管理 Container 和 VM。"
/>

<QuizQuestion
  question="2. VM（VirtualMachine）和 VMI（VirtualMachineInstance）的關係，最像 K8s 中的哪一對？"
  :options='[
    "ConfigMap 和 Secret",
    "Deployment 和 Pod",
    "Service 和 Endpoint",
    "Namespace 和 Node",
  ]'
  :answer="1"
  explanation="VM 像 Deployment 代表期望狀態（定義要跑一台 VM），VMI 像 Pod 代表實際運行的實例。VM 可以控制 VMI 的生命週期，重啟 VM 會建立新的 VMI。"
/>

---

## 階段二：架構心智模型

::: tip 為什麼要學這個？
知道 KubeVirt 是什麼之後，你需要理解它的內部是怎麼組織的。沒有這層認識，遇到問題時你不知道該看哪個元件的 log、該在哪裡下斷點。這個階段建立你的除錯地圖。
:::

### 📚 精選閱讀

| 文件 | 說明 |
|------|------|
| [VM 生命週期](/kubevirt/architecture/lifecycle) | VM 從建立到刪除的完整狀態機，以及各元件在每個階段的角色 |
| [virt-api](/kubevirt/components/virt-api) | API 層的職責：Webhook 驗證、請求路由 |
| [virt-controller](/kubevirt/components/virt-controller) | 控制平面：監控 VM/VMI 資源並驅動狀態收斂 |
| [virt-handler](/kubevirt/components/virt-handler) | Node 上的代理人：同步 VMI 狀態到本機 |
| [virt-launcher](/kubevirt/components/virt-launcher) | VM 專屬 Pod：包裝 libvirtd 和 QEMU 進程 |

### ✅ 自我測驗

<QuizQuestion
  question="1. 當你執行 kubectl apply 建立 VM 資源時，KubeVirt 元件的處理順序是？"
  :options='[
    "virt-launcher → virt-handler → virt-controller → virt-api",
    "virt-api → virt-controller → virt-handler → virt-launcher",
    "virt-controller → virt-api → virt-handler → virt-launcher",
    "virt-handler → virt-api → virt-controller → virt-launcher",
  ]'
  :answer="1"
  explanation="請求先到 virt-api（Webhook 驗證），virt-controller 建立 VMI 並排程，virt-handler 在目標 Node 準備環境，最後 virt-launcher 啟動 QEMU 進程。"
/>

<QuizQuestion
  question="2. virt-handler 和 virt-launcher 的主要職責差異是？"
  :options='[
    "virt-handler 管理 VM 的網路，virt-launcher 管理 VM 的儲存",
    "virt-handler 是 Node 上的代理人負責同步狀態，virt-launcher 是 VM 專屬進程負責運行 QEMU",
    "virt-handler 處理 API 請求，virt-launcher 處理排程",
    "兩者功能相同，只是部署在不同位置",
  ]'
  :answer="1"
  explanation="virt-handler 以 DaemonSet 方式在每個 Node 運行，監控 VMI 狀態並執行 Node 層級操作。virt-launcher 是每台 VM 專屬的 Pod，包含 libvirtd 和 QEMU，負責實際的虛擬機運行。"
/>

---

## 階段三：網路與儲存

::: tip 為什麼要學這個？
VM 需要網路才能通訊，需要儲存才能保存資料。這兩個是實際部署 KubeVirt 時最常踩到坑的地方。網路模式選錯會讓 VM 無法外部訪問；儲存沒配好會讓 VM 資料在重啟後消失。這個階段讓你在動手前先有正確預期。
:::

### 📚 精選閱讀

| 文件 | 說明 |
|------|------|
| [網路總覽](/kubevirt/networking/overview) | Masquerade、Bridge、Multus 等網路模式的選擇指南 |
| [儲存總覽](/kubevirt/storage/overview) | PVC、DataVolume、不同 AccessMode 的使用情境 |
| [PVC 與 DataVolume](/kubevirt/storage/pvc-datavolume) | 如何用 DataVolume 從外部來源匯入 VM 磁碟映像 |

### ✅ 自我測驗

<QuizQuestion
  question="1. KubeVirt 預設的網路模式 Masquerade 和 Bridge 最主要的差別是？"
  :options='[
    "Masquerade 速度比 Bridge 快",
    "Masquerade 透過 NAT 讓 VM 有獨立 IP，Bridge 讓 VM 直接在 Pod 網路上，兩者對 VM 內部的感知不同",
    "Bridge 只能用在特定 CNI 上，Masquerade 沒有限制",
    "兩者功能完全相同",
  ]'
  :answer="1"
  explanation="Masquerade 模式下 VM 的流量透過 NAT 處理，VM 看到的 IP 和 Pod IP 不同。Bridge 模式讓 VM 直接橋接到 Pod 網路，VM 可以感知到自己的 IP 就是 Pod IP。"
/>

<QuizQuestion
  question="2. DataVolume 和直接使用 PVC 的主要優點是？"
  :options='[
    "DataVolume 比 PVC 有更好的讀寫效能",
    "DataVolume 提供從 URL/映像檔匯入資料的能力，並整合 CDI 管理資料生命週期",
    "DataVolume 支援更多的 StorageClass",
    "DataVolume 是 KubeVirt 1.0 後廢棄 PVC 的替代方案",
  ]'
  :answer="1"
  explanation="DataVolume 是 CDI（Containerized Data Importer）提供的抽象層，允許從 HTTP URL、S3、Registry 等來源匯入 VM 映像，並管理整個 PVC 的生命週期，是建議的 KubeVirt 儲存使用方式。"
/>

---

## 階段四：動手操作

::: tip 為什麼要學這個？
前面都是理論，現在是時候動手了。讀完文件後，實際跑一遍安裝流程、建立第一台 VM、用 virtctl 連入，這個過程會讓你把所有概念串起來。沒有動手的理解是脆弱的。
:::

### 📚 精選閱讀

| 文件 | 說明 |
|------|------|
| [快速入門](/kubevirt/guides/quickstart) | 從零安裝 KubeVirt 到建立第一台 VM 的完整步驟 |
| [virtctl 使用指南](/kubevirt/virtctl/guide) | 管理 VM 生命週期的 CLI 工具完整說明 |
| [virtctl 連線存取](/kubevirt/virtctl/access) | 透過 VNC、SSH、serial console 連入 VM |

::: warning 常見錯誤與排查
實作時最常遇到的問題：

**VM 卡在 `Pending` 狀態**
→ 先看 VMI 的 Events：`kubectl describe vmi <name>`
→ 確認 Node 上有 `/dev/kvm`（虛擬化支援）：`ls -la /dev/kvm`
→ 確認 virt-handler Pod 在目標 Node 上正常運行

**virtctl console 連不上**
→ 確認 VM 狀態是 `Running`：`kubectl get vmi`
→ 確認 virtctl 版本與 KubeVirt 版本相符
→ 嘗試用 `virtctl vnc <vm-name>` 代替

**VM 啟動後網路不通**
→ 確認網路模式（Masquerade 下 VM 內部 IP 是 `10.0.2.2`，不是 Pod IP）
→ 檢查 virt-launcher Pod 的 log：`kubectl logs <virt-launcher-pod>`

**DataVolume 匯入失敗**
→ 查看 CDI Importer Pod 的 log：`kubectl logs -l app=importer`
→ 確認 URL 可以從 cluster 內部存取
:::

---

## 階段五：選擇你的深入路徑

::: info 現在你有了基礎
完成前四個階段後，你已經能夠在 K8s 上部署和操作 VM。接下來根據你的工作職責，選擇對應的深入方向。
:::

### 🌐 網路工程師路線

深入理解 KubeVirt 的網路架構、多介面配置與 SR-IOV 等高效能網路方案。

| 文件 | 說明 |
|------|------|
| [網路模式深入](/kubevirt/networking/overview) | 各種網路模式的底層實作原理 |
| [Multus 多網路介面](/multus-cni/) | 為 VM 配置多張網路卡的完整方案 |
| [網路效能調教](/kubevirt/networking/overview) | SR-IOV、DPDK 等高效能網路配置 |

### 💾 儲存工程師路線

深入理解 VM 磁碟管理、快照、備份與 CDI 的完整功能。

| 文件 | 說明 |
|------|------|
| [PVC 與 DataVolume 深入](/kubevirt/storage/pvc-datavolume) | DataVolume 的進階用法與資料來源配置 |
| [CDI 架構](/containerized-data-importer/) | Containerized Data Importer 的完整架構 |
| [儲存效能優化](/kubevirt/storage/overview) | virtio-blk vs virtio-scsi、存取模式選擇 |

### ⚡ 效能調教路線

針對需要接近裸機效能的使用情境，學習 CPU pinning、NUMA topology、大頁記憶體等配置。

| 文件 | 說明 |
|------|------|
| [效能配置指南](/kubevirt/guides/quickstart) | CPU pinning、huge pages、NUMA 拓撲配置 |
| [資源管理](/kubevirt/architecture/overview) | KubeVirt 如何與 K8s 資源管理整合 |
| [Node 維護操作](/node-maintenance-operator/) | 不中斷 VM 的 Node 維護流程 |

### 🏗️ 平台維運路線

負責 KubeVirt 平台的日常維護、版本升級與觀測性建置。

| 文件 | 說明 |
|------|------|
| [監控與告警](/monitoring/) | Prometheus metrics、Alertmanager 規則配置 |
| [Node 維護操作](/node-maintenance-operator/) | 安全地對跑著 VM 的 Node 進行維護 |
| [版本升級策略](/kubevirt/architecture/lifecycle) | KubeVirt 版本升級的注意事項與策略 |

---

::: info 相關章節
- [KubeVirt 文件首頁](/kubevirt/learning-path/)
- [架構總覽](/kubevirt/architecture/overview)
- [互動式測驗](/kubevirt/quiz/)
:::
