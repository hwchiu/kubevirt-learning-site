---
layout: doc
---

# 📝 KubeVirt 架構隨堂測驗

本測驗涵蓋 KubeVirt 的系統架構、核心元件、CRD 資源、VM 生命週期等重要知識點。
完成所有題目後，請對照解析確認自己是否正確理解了 KubeVirt 的設計理念與實作細節。

::: info 📖 相關章節
建議先閱讀以下章節再作答：
- [系統架構概述](/kubevirt/architecture/overview)
- [VM 生命週期流程](/kubevirt/architecture/lifecycle)
- [架構深入剖析](/kubevirt/architecture/deep-dive)
- [核心元件](/kubevirt/components/virt-controller)
:::

---

## 🏗️ 架構設計

<QuizQuestion
  question="1. KubeVirt 的核心設計理念是什麼？"
  :options="[
    '取代 Kubernetes，建立全新的虛擬化平台',
    '擴展 Kubernetes，讓使用者在現有叢集中管理虛擬機器',
    '在 Kubernetes 外部獨立運行虛擬機器',
    '僅為 Kubernetes 提供容器化的 QEMU 映像檔',
  ]"
  :answer="1"
  explanation="KubeVirt 的核心理念是「擴展而非取代」，透過 CRD、Controller 和 DaemonSet 為 Kubernetes 加入虛擬化能力，讓 VM 和容器在同一叢集中共存。"
/>

<QuizQuestion
  question="2. KubeVirt Razor（設計準則）的含義是什麼？"
  :options="[
    '所有功能都應該針對 VM 特別最佳化',
    '如果某個功能對 Pod 也有用，就不應該只為 VM 實作',
    '虛擬機器的效能必須優先於容器',
    'VM 功能應該由 libvirt 社區提供，KubeVirt 僅做整合',
  ]"
  :answer="1"
  explanation="KubeVirt Razor 意味著「如果某個功能對 Pod 也有用，就不應該只為 VM 實作它」，讓 KubeVirt 盡可能重用 Kubernetes 現有基礎設施（CNI、PVC、kube-scheduler 等）。"
/>

<QuizQuestion
  question="3. KubeVirt 使用哪種架構模式來協調各元件？"
  :options="[
    '編排 (Orchestration) 模式 — 由中央指揮官統一調度',
    '協作 (Choreography) 模式 — 各元件觀察狀態並自主行動',
    '發佈/訂閱 (Pub/Sub) 模式 — 透過訊息佇列傳遞事件',
    '管線 (Pipeline) 模式 — 資料依序流過各處理階段',
  ]"
  :answer="1"
  explanation="KubeVirt 使用協作 (Choreography) 模式，每個元件各自觀察狀態並採取行動，透過 VMI CR 作為共享狀態，類似 Kubernetes 本身的 level-triggered 協調機制。"
/>

---

## ⚙️ 核心元件

<QuizQuestion
  question="4. KubeVirt 的五大核心元件分別是哪些？"
  :options="[
    'virt-operator, virt-api, virt-controller, virt-handler, virt-launcher',
    'virt-operator, virt-proxy, virt-scheduler, virt-handler, virt-runtime',
    'virt-api, virt-controller, virt-handler, virt-launcher, virt-monitor',
    'kubevirt-manager, virt-api, virt-controller, virt-daemon, virt-launcher',
  ]"
  :answer="0"
  explanation="KubeVirt 五大核心元件為：virt-operator（安裝與管理）、virt-api（API 入口）、virt-controller（叢集級控制）、virt-handler（節點代理）、virt-launcher（VM 執行環境）。"
/>

<QuizQuestion
  question="5. virt-handler 的部署型態是什麼？"
  :options="[
    'Deployment（多副本）',
    'StatefulSet（每節點一個）',
    'DaemonSet（每個節點一個）',
    'Job（按需執行）',
  ]"
  :answer="2"
  explanation="virt-handler 以 DaemonSet 形式在每個 Kubernetes 節點上運行，負責監控本節點上的 VMI 狀態並透過 Unix socket 與 virt-launcher 通訊。它需要 hostPID 和 hostNetwork 特殊權限。"
/>

<QuizQuestion
  question="6. virt-controller 的主要職責是什麼？"
  :options="[
    '在每個節點上管理 libvirt domain 的執行',
    '提供 HTTP/WebSocket API 入口與 Admission Webhook',
    '叢集級 VM 生命週期管理，建立/刪除 virt-launcher Pod',
    '安裝與升級 KubeVirt 各元件',
  ]"
  :answer="2"
  explanation="virt-controller 是叢集級控制平面，內建多個控制器（VM、VMI、Migration、Snapshot 等），負責管理 VM 生命週期，包含建立和刪除 virt-launcher Pod。"
/>

<QuizQuestion
  question="7. virt-launcher Pod 的角色是什麼？"
  :options="[
    '負責 Kubernetes 叢集中所有 VM 的調度',
    '提供 cgroups/namespaces 隔離，執行 libvirtd + QEMU',
    '管理 VM 的網路策略和防火牆規則',
    '負責 VM 映像檔的下載和快取',
  ]"
  :answer="1"
  explanation="每個 VMI 對應一個 virt-launcher Pod，Pod 內運行 libvirtd 和 QEMU 程序。virt-launcher 提供 cgroups 和 namespaces 隔離，讓 VM 對 Kubernetes 來說就是一個 Pod。"
/>

<QuizQuestion
  question="8. virt-api 提供了哪些功能？（選擇最完整的描述）"
  :options="[
    '僅提供 REST API 入口',
    'REST API 入口、Admission Webhook、Console/VNC 代理',
    'REST API 入口和 VM 生命週期管理',
    '僅提供 Admission Webhook 和驗證功能',
  ]"
  :answer="1"
  explanation="virt-api 以 Deployment 形式部署（≥2 副本），提供 HTTP/WebSocket API 入口、Mutating/Validating Admission Webhook、以及 Console/VNC 代理功能。"
/>

<QuizQuestion
  question="9. virt-operator 的主要職責是什麼？"
  :options="[
    '管理 VM 的日常運行和監控',
    '負責 Kubernetes 叢集的整體運維',
    '安裝與管理所有 KubeVirt 元件，監控 KubeVirt CR',
    '處理 VM 的網路配置和安全策略',
  ]"
  :answer="2"
  explanation="virt-operator 是 KubeVirt 的安裝與生命週期管理器，負責部署和升級所有 KubeVirt 元件（virt-api、virt-controller、virt-handler），並監控 KubeVirt CR 的狀態。"
/>

---

## 📦 CRD 資源

<QuizQuestion
  question="10. VirtualMachine (VM) 和 VirtualMachineInstance (VMI) 的關係是什麼？"
  :options="[
    'VM 和 VMI 是完全相同的物件，只是名稱不同',
    'VM 是持久物件，VMI 是暫態物件代表正在執行的 VM',
    'VMI 是持久物件，VM 是暫態物件代表正在執行的 VMI',
    'VM 管理多個 VMI 的副本集',
  ]"
  :answer="1"
  explanation="VirtualMachine (VM) 是持久存在的物件，即使 VM 停止也會保留。VirtualMachineInstance (VMI) 是暫態物件，代表正在執行的 VM 實例，關機後會被刪除。"
/>

<QuizQuestion
  question="11. 以下哪個 RunStrategy 會在 VMI 停止後自動重啟？"
  :options="[
    'Halted',
    'Manual',
    'Always',
    'Once',
  ]"
  :answer="2"
  explanation="RunStrategy 為 Always 時，如果 VMI 停止就會自動重啟。Halted 不自動啟動；Manual 由使用者手動控制；Once 只啟動一次；RerunOnFailure 僅在失敗時重啟。"
/>

<QuizQuestion
  question="12. VirtualMachineInstanceMigration 這個 CRD 的用途是什麼？"
  :options="[
    '管理 VM 映像檔的匯入',
    '管理 VM 的備份和還原',
    '表示 Live Migration 請求物件',
    '管理 VM 的網路遷移策略',
  ]"
  :answer="2"
  explanation="VirtualMachineInstanceMigration 是 Live Migration 的請求物件，用於觸發和追蹤 VMI 從一個節點遷移到另一個節點的過程。"
/>

---

## 🔄 VM 生命週期

<QuizQuestion
  question="13. 使用者建立 VM 後，最先處理請求的元件是哪個？"
  :options="[
    'virt-controller',
    'virt-handler',
    'virt-api',
    'virt-launcher',
  ]"
  :answer="2"
  explanation="使用者 kubectl apply 後，請求先經過 virt-api（Mutating Webhook 補齊預設值 → Validating Webhook 驗證 spec → 寫入 CR），然後才由 virt-controller 的 watch 機制接手。"
/>

<QuizQuestion
  question="14. 在 VM 建立流程中，哪個元件負責建立 virt-launcher Pod？"
  :options="[
    'virt-api',
    'virt-handler',
    'virt-controller',
    'kube-scheduler',
  ]"
  :answer="2"
  explanation="virt-controller 的 VMI 控制器負責建立 virt-launcher Pod。流程為：VM 控制器建立 VMI CR → VMI 控制器建立 virt-launcher Pod → kube-scheduler 排程 → virt-handler 啟動 VM。"
/>

<QuizQuestion
  question="15. VMI 的狀態轉換順序是什麼？"
  :options="[
    'Running → Pending → Scheduled → Scheduling',
    'Pending → Scheduling → Scheduled → Running',
    'Scheduling → Pending → Running → Scheduled',
    'Scheduled → Pending → Scheduling → Running',
  ]"
  :answer="1"
  explanation="VMI 的正確狀態轉換為：Pending（等待調度）→ Scheduling（正在調度）→ Scheduled（已調度到節點）→ Running（VM 執行中）。"
/>

<QuizQuestion
  question="16. virt-handler 如何與 virt-launcher 通訊？"
  :options="[
    '透過 Kubernetes API Server',
    '透過 HTTP REST API',
    '透過 Unix Socket',
    '透過 gRPC over TCP',
  ]"
  :answer="2"
  explanation="virt-handler 透過 Unix Socket 與 virt-launcher 通訊，將 VMI spec 轉換為 libvirt domain XML，並呼叫 libvirtd 啟動 QEMU 程序。"
/>

---

## 🔬 進階概念

<QuizQuestion
  question="17. virt-handler 需要哪些特殊權限？"
  :options="[
    '不需要任何特殊權限',
    'hostPID 和 hostNetwork',
    '僅需要 hostNetwork',
    '僅需要 privileged: true',
  ]"
  :answer="1"
  explanation="virt-handler 需要 hostPID: true（存取宿主機程序資訊）和 hostNetwork: true（管理 VM 網路），並掛載 /proc、/var/run/kubevirt、/var/lib/kubelet 等 hostPath。"
/>

<QuizQuestion
  question="18. virt-controller 的部署如何實現高可用？"
  :options="[
    '使用 StatefulSet 確保順序啟動',
    '部署多個副本並使用 Leader Election，僅一個 active',
    '每個節點部署一個副本形成叢集',
    '透過外部負載均衡器實現故障轉移',
  ]"
  :answer="1"
  explanation="virt-controller 以 Deployment 形式部署 ≥2 副本，使用 Leader Election 機制確保同一時間僅有一個 active 實例處理控制邏輯，其他副本作為備援。"
/>

<QuizQuestion
  question="19. 在 KubeVirt 架構中，VM 對 Kubernetes 來說本質上是什麼？"
  :options="[
    '一個獨立的虛擬機器程序',
    '一個自定義資源 (Custom Resource)',
    '一個 Pod (virt-launcher Pod)',
    '一個節點 (Node)',
  ]"
  :answer="2"
  explanation="對 Kubernetes 而言，VM 就是一個 virt-launcher Pod。Kubernetes 負責調度、網路、儲存的基礎，KubeVirt 在 Pod 內部管理 VM 的具體執行。同一 namespace 可同時存在 Pod 和 VM。"
/>

<QuizQuestion
  question="20. virt-controller 內建了哪些控制器？"
  :options="[
    '僅有 VM Controller 和 VMI Controller',
    'VM、VMI、Migration、ReplicaSet、Pool、Node、Evacuation、Snapshot Controller',
    'VM、VMI、Network、Storage Controller',
    'VM、VMI、Migration Controller',
  ]"
  :answer="1"
  explanation="virt-controller 內建多個控制器：VM Controller、VMI Controller、Migration Controller、ReplicaSet Controller、Pool Controller、Node Controller、Evacuation Controller 和 Snapshot Controller。"
/>

---

::: tip 🎯 完成測驗
恭喜你完成了 KubeVirt 架構測驗！如果有答錯的題目，建議回頭閱讀相關章節加深理解。

重點複習：
- **五大元件**的角色與部署型態
- **VM/VMI** 的關係與生命週期
- **協作模式**的設計理念
- **KubeVirt Razor** 設計準則
:::
