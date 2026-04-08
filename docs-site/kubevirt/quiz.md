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

## 🚀 進階主題

### 🔀 Live Migration

<QuizQuestion
  question="21. 哪些情況可以觸發 KubeVirt 的 Live Migration？"
  :options="[
    '只有手動建立 VirtualMachineInstanceMigration CR 時',
    '手動建立 VMIM CR、節點被標記 kubevirt.io/evacuate，或搭配 NodeMaintenanceOperator 進行節點維護',
    '只有節點執行 kubectl drain 時自動觸發',
    '只有 virt-operator 升級時才會觸發',
  ]"
  :answer="1"
  explanation="Live Migration 可由多種方式觸發：1) 手動建立 VirtualMachineInstanceMigration CR；2) 節點被標記 kubevirt.io/evacuate annotation，Evacuation Controller 自動建立 VMIM；3) 搭配 NodeMaintenanceOperator 進行節點維護時自動疏散 VM。"
/>

<QuizQuestion
  question="22. Live Migration 流程中，哪個元件負責在目標節點建立新的 virt-launcher Pod？"
  :options="[
    '來源節點的 virt-handler',
    'virt-api',
    'virt-controller 的 Migration Controller',
    'kube-scheduler',
  ]"
  :answer="2"
  explanation="當偵測到 VirtualMachineInstanceMigration CR 時，virt-controller 的 Migration Controller 負責在目標節點建立新的 virt-launcher Pod（target pod），並協調整個 Live Migration 流程的狀態機轉換。"
/>

<QuizQuestion
  question="23. KubeVirt Live Migration 預設使用哪種記憶體遷移模式？"
  :options="[
    'Post-copy（先切換到目標節點，再從來源補傳記憶體）',
    'Cold migration（先關機再複製磁碟與記憶體映像）',
    'Pre-copy（VM 持續執行的同時迭代複製記憶體，最後短暫停機完成同步）',
    'Checkpoint-based（定期建立 checkpoint，再以最後一個 checkpoint 遷移）',
  ]"
  :answer="2"
  explanation="KubeVirt Live Migration 預設使用 Pre-copy 模式：VM 在來源節點持續執行的同時，記憶體頁面逐步複製到目標節點；當髒頁（dirty pages）數量縮小到閾值以下後，短暫停機完成最後同步，再於目標節點恢復執行，確保服務中斷時間最短。"
/>

<QuizQuestion
  question="24. 來源節點的 virt-handler 在 Live Migration 完成後，主要負責什麼工作？"
  :options="[
    '繼續監控來源節點上的舊 domain，確保雙活',
    '呼叫 libvirt migrate API 啟動記憶體複製，並在遷移完成後清理來源 domain',
    '將 VMI CR 的 nodeName 欄位從來源節點改為目標節點',
    '向 kube-scheduler 申請目標節點的 CPU/Memory 資源',
  ]"
  :answer="1"
  explanation="來源節點的 virt-handler 透過 libvirt 的 migrate API 驅動記憶體頁面的迭代複製（pre-copy）。遷移完成、VM 在目標節點成功啟動後，來源節點的 virt-handler 負責清理來源 domain（virDomainDestroy），釋放資源。"
/>

### 💾 Storage

<QuizQuestion
  question="25. DataVolume (DV) 在 KubeVirt 中的作用是什麼？"
  :options="[
    '直接儲存 VM 的磁碟映像檔，本身就是儲存後端',
    '是 Containerized Data Importer (CDI) 提供的 CRD，自動化「建立 PVC + 填充資料」的完整流程',
    '管理 VM 使用的 StorageClass 和 QoS 策略',
    '提供 VM 之間共享記憶體（shared memory）的機制',
  ]"
  :answer="1"
  explanation="DataVolume 是 Containerized Data Importer (CDI) 提供的 CRD，封裝了「建立 PVC + 匯入資料」的流程。使用者指定資料來源（HTTP URL、容器映像、現有 PVC 等），CDI 會自動建立對應 PVC 並將資料填充進去，簡化 VM 磁碟準備工作。"
/>

<QuizQuestion
  question="26. VMI spec 中的 containerDisk volume 類型有什麼特點？"
  :options="[
    '資料持久保存於 PVC，VM 刪除後仍然存在',
    '將磁碟映像打包在 OCI container image 中，每次 VM 啟動都是全新副本，資料不持久化',
    '必須搭配特定 StorageClass 才能運作',
    '只能用於 Windows VM 的系統磁碟',
  ]"
  :answer="1"
  explanation="containerDisk 將磁碟映像打包在 OCI container image 中。VM 啟動時，映像會被複製到節點的暫存目錄，資料不會持久化，VM 刪除後資料消失。適合無狀態的測試環境、唯讀的基底映像層，或搭配 PVC 作為額外的 ephemeral 磁碟使用。"
/>

<QuizQuestion
  question="27. cloudInitNoCloud volume 的主要用途是什麼？"
  :options="[
    '直接連線到公有雲的物件儲存（S3、GCS）下載 VM 映像',
    '提供 cloud-init 的 NoCloud 資料來源，讓 VM 在首次啟動時執行使用者自訂的初始化腳本',
    '僅用於 OpenStack 環境中提供 instance metadata',
    '管理 KubeVirt 與 cloud provider 的 CSI 整合設定',
  ]"
  :answer="1"
  explanation="cloudInitNoCloud volume 提供 cloud-init 的 NoCloud 資料來源，可在 VMI spec 中直接嵌入 userData（啟動腳本）和 networkData（網路配置）。VM 啟動時，cloud-init 讀取這些資料執行初始化，常用於設定使用者密碼、SSH key、安裝套件等。"
/>

### 🌐 Network

<QuizQuestion
  question="28. KubeVirt VM 預設使用哪種網路繫結方式（binding）？"
  :options="[
    'bridge — 直接橋接到宿主機物理網路介面',
    'masquerade — 透過 NAT 讓 VM 流量經由 Pod 網路命名空間路由',
    'SR-IOV — 直接使用物理 NIC 的 Virtual Function',
    'macvlan — 在宿主機 NIC 上建立獨立的 MAC 位址',
  ]"
  :answer="1"
  explanation="KubeVirt VM 預設使用 masquerade 繫結方式，透過 NAT/iptables 讓 VM 的流量經由 virt-launcher Pod 的網路命名空間路由。這讓 VM 完全整合 Kubernetes 的 Service、NetworkPolicy 等功能，且不需要特殊的宿主機網路設定。"
/>

<QuizQuestion
  question="29. Multus CNI 在 KubeVirt 中扮演什麼角色？"
  :options="[
    '取代 Kubernetes 預設 CNI，提供效能更高的 overlay 網路',
    '讓 VM 能同時擁有多個網路介面（pod network + 額外的 NetworkAttachmentDefinition）',
    '僅用於 SR-IOV 網路的 VF 分配',
    '管理 VM 之間的 NetworkPolicy 規則',
  ]"
  :answer="1"
  explanation="Multus CNI 是 meta-CNI plugin，允許 Pod（及 KubeVirt VM）同時擁有多個網路介面。VM 可保有一個主要的 pod network，再透過 NetworkAttachmentDefinition 附加額外網路（如 VLAN、macvlan、SR-IOV VF 等），滿足多網卡的企業級需求。"
/>

<QuizQuestion
  question="30. SR-IOV 在 KubeVirt 網路場景中的主要優勢是什麼？"
  :options="[
    '提供更完善的網路隔離，防止 VM 之間的流量外洩',
    '讓 VM 直接使用物理 NIC 的 Virtual Function (VF)，繞過 software networking 層，獲得接近裸機的網路效能',
    '自動管理 VM 的 Security Group 和防火牆規則',
    '簡化 Kubernetes Service 的 LoadBalancer 配置流程',
  ]"
  :answer="1"
  explanation="SR-IOV (Single Root I/O Virtualization) 讓一張物理 NIC 虛擬化為多個 Virtual Function (VF)，VM 可直接使用 VF 繞過 kernel networking stack，獲得高頻寬、低延遲、低 CPU 開銷的網路效能，適合需要高效能網路的工作負載（如 NFV、HPC）。"
/>

### 📸 Snapshot / Restore

<QuizQuestion
  question="31. VirtualMachineSnapshot 建立了什麼內容？"
  :options="[
    '只備份 VM 的 spec 設定，不包含磁碟資料',
    'VM spec 設定 + 相關所有 PVC 的 VolumeSnapshot，提供完整時間點快照',
    '將 VM 的記憶體狀態（RAM）備份到遠端物件儲存',
    '建立 VM 的完整 OCI container image',
  ]"
  :answer="1"
  explanation="VirtualMachineSnapshot 建立 VM 的時間點快照，包含 VM spec 以及所有相關 PVC 的 VolumeSnapshot（底層儲存快照）。搭配 VirtualMachineRestore 可將 VM 完整還原到快照建立時的狀態，是 VM 備份與災難恢復的核心機制。"
/>

<QuizQuestion
  question="32. 使用 VirtualMachineSnapshot 功能的必要前提條件是什麼？"
  :options="[
    'VM 必須先關機（Stopped 狀態）才能建立快照',
    '叢集必須安裝支援 CSI VolumeSnapshot 的 storage driver',
    '必須先安裝 Velero 備份工具',
    '只有 virt-operator 管理員才能建立快照',
  ]"
  :answer="1"
  explanation="VirtualMachineSnapshot 依賴底層儲存的 VolumeSnapshot 功能（CSI 標準介面），因此叢集必須安裝支援 CSI VolumeSnapshot 的 storage driver（如 Longhorn、Ceph CSI 等）。VM 可在 Running 或 Stopped 狀態下建立快照，Running 狀態下建議搭配 QEMU guest agent 以確保磁碟資料一致性。"
/>

### 🖥️ Resource Management

<QuizQuestion
  question="33. 如何在 KubeVirt VMI spec 中設定 VM 的 CPU 拓撲？"
  :options="[
    '直接修改 QEMU 的命令列參數 -smp',
    '在 domain.cpu 中設定 cores、sockets、threads，KubeVirt 自動對應到 virt-launcher Pod 的 CPU requests/limits',
    '直接設定 Kubernetes Node 的 CPU 配額（ResourceQuota）',
    'CPU 拓撲由 KubeVirt 根據節點剩餘資源自動決定，使用者無法設定',
  ]"
  :answer="1"
  explanation="VMI spec 的 domain.cpu 欄位可設定 CPU 拓撲（cores、sockets、threads），KubeVirt 根據這些值計算總 vCPU 數量，並對應設定 virt-launcher Pod 的 CPU requests/limits，讓 kube-scheduler 能正確考量 VM 的 CPU 資源需求進行排程。"
/>

<QuizQuestion
  question="34. CPU model 設定（如 host-model vs host-passthrough）對 Live Migration 有什麼影響？"
  :options="[
    'CPU model 只影響 VM 開機速度，與 Live Migration 無關',
    'host-passthrough 獲得最佳效能但限制可遷移的目標節點（目標節點 CPU 須相同或更新），host-model 相容性較佳',
    'host-model 無法進行 Live Migration，只有 host-passthrough 才支援',
    'CPU model 設定越新，Live Migration 成功率越高',
  ]"
  :answer="1"
  explanation="CPU model 決定 VM 內看到的 CPU 功能集（CPUID）。host-passthrough 直接透傳宿主機 CPU 能力，效能最佳，但目標節點 CPU 必須具備相同或更多的 CPU features，限制了可遷移的節點範圍。host-model 使用通用 CPU model 提升跨節點相容性，是 Live Migration 場景的推薦選項。"
/>

### 🔄 VMI Phase 詳解

<QuizQuestion
  question="35. VMI 的 Succeeded 和 Failed 終止狀態有什麼不同？"
  :options="[
    'Succeeded 代表 VM 正常執行中，Failed 代表 VM 啟動失敗',
    'Succeeded 代表 VM 正常關機（graceful shutdown），Failed 代表 VM 異常終止（crash、OOM 等）',
    'Succeeded 代表 Live Migration 成功，Failed 代表 Live Migration 失敗',
    'Succeeded 和 Failed 意義相同，都表示 VM 已停止執行',
  ]"
  :answer="1"
  explanation="Succeeded 代表 VM 正常完成其生命週期（VM 內部執行 poweroff 等正常關機）；Failed 代表 VM 異常終止（程序崩潰、OOM killed 等）。RunStrategy 為 RerunOnFailure 時，Failed 的 VMI 會被重啟；Succeeded 的不會，讓 KubeVirt 能管理批次工作負載型 VM（run-to-completion）。"
/>

<QuizQuestion
  question="36. VMI 進入 Paused 狀態的方式是什麼？"
  :options="[
    '叢集資源不足時，KubeVirt 自動暫停優先權較低的 VM',
    '透過 virtctl pause vm <name> 指令，virt-handler 呼叫 libvirt virDomainSuspend API 暫停 QEMU 程序',
    '在 VMI spec 中將 running 欄位設為 false',
    'VM 磁碟空間耗盡時系統自動觸發 Pause',
  ]"
  :answer="1"
  explanation="VMI 可透過 virtctl pause vm <name> 指令進入 Paused 狀態，virt-handler 呼叫 libvirt 的 virDomainSuspend API 暫停 QEMU 程序執行。Paused 狀態下 VM 資料保留在記憶體，可用 virtctl unpause vm <name> 恢復執行，適合需要暫停檢查但不想關機的維護場景。"
/>

### 🔧 virt-handler 操作細節

<QuizQuestion
  question="37. virt-handler 如何知道本節點上有哪些 VMI 需要管理？"
  :options="[
    'virt-controller 定期透過 HTTP API 推送任務清單給 virt-handler',
    'virt-handler watch Kubernetes API Server 上 nodeName 為本節點的 VMI CR 變更',
    'virt-handler 直接掃描節點上的 QEMU 程序清單',
    'virt-handler 透過 etcd 訂閱 VMI 事件',
  ]"
  :answer="1"
  explanation="virt-handler 透過 informer/watch 機制監控 Kubernetes API Server，只處理 spec.nodeName 等於本節點的 VMI CR。當 VMI CR 發生變更（建立、更新、刪除）時，virt-handler 的 reconcile loop 會依據期望狀態呼叫 libvirt API 進行相應操作。"
/>

<QuizQuestion
  question="38. virt-handler 將 VMI spec 轉換為什麼格式，再交給 libvirtd 執行？"
  :options="[
    'YAML 格式的 QEMU 設定檔',
    'JSON 格式的 container runtime spec (OCI)',
    'libvirt domain XML，描述 VM 的硬體設備、CPU、記憶體、磁碟、網路等設定',
    '直接組合 QEMU 命令列參數字串',
  ]"
  :answer="2"
  explanation="virt-handler 從 virt-launcher 取得 VMI spec 後，透過 virt-launcher 內建的轉換邏輯將其轉換為 libvirt domain XML 格式，再呼叫 libvirtd 的 API（virDomainDefineXML + virDomainCreate）啟動對應的 QEMU 程序，實現 Kubernetes 資源宣告到 hypervisor 執行的橋接。"
/>

### 🛡️ Eviction 與節點維護

<QuizQuestion
  question="39. 執行 kubectl drain 對 KubeVirt virt-launcher Pod 的影響是什麼？"
  :options="[
    'drain 會立即刪除 virt-launcher Pod，VM 直接停機',
    'drain 會被 virt-launcher Pod 的 PodDisruptionBudget (PDB) 阻擋，無法直接驅逐 VM Pod',
    'drain 對 VM 完全沒有影響，VM 會持續執行',
    'drain 會自動觸發 Live Migration 並等待完成',
  ]"
  :answer="1"
  explanation="KubeVirt 為每個 virt-launcher Pod 自動建立 PodDisruptionBudget (PDB)，阻止 kubectl drain 直接驅逐 VM Pod，避免 VM 意外停機。正確的節點維護流程應使用 NodeMaintenanceOperator，它會先透過 Evacuation Controller 觸發 Live Migration 疏散所有 VM，再允許節點維護。"
/>

<QuizQuestion
  question="40. LiveMigrationPolicy（MigrationPolicy CRD）的用途是什麼？"
  :options="[
    '全域強制要求所有 VMI 必須支援 Live Migration',
    '為不同的 VM 群組（透過 label selector）設定客製化的 Live Migration 策略，如頻寬限制、完成逾時、允許 post-copy 等',
    '全域關閉叢集的 Live Migration 功能',
    '管理 Live Migration 流量的網路路由和 QoS 策略',
  ]"
  :answer="1"
  explanation="LiveMigrationPolicy（MigrationPolicy CRD）讓管理員透過 label selector 為不同 VM 群組套用客製化的 Live Migration 策略，包含：頻寬限制（bandwidthPerMigration）、完成逾時（completionTimeoutPerGiB）、允許 post-copy 轉換、允許自動切換至 post-copy 等精細控制，無需修改全域 KubeVirt 設定。"
/>

---

::: tip 🎯 完成測驗
恭喜你完成了 KubeVirt 完整 40 題架構測驗！如果有答錯的題目，建議回頭閱讀相關章節加深理解。

重點複習：
- **五大元件**的角色與部署型態
- **VM/VMI** 的關係與生命週期
- **協作模式**的設計理念
- **KubeVirt Razor** 設計準則
- **Live Migration** 流程、觸發條件與 virt-handler 角色
- **Storage**：DataVolume / containerDisk / cloudInitNoCloud
- **Network**：masquerade、Multus CNI、SR-IOV
- **Snapshot/Restore**：CSI VolumeSnapshot 依賴
- **Resource Management**：CPU topology 與 CPU model 對遷移的影響
- **VMI Phase**：Succeeded vs Failed、Paused 狀態
- **節點維護**：PDB 保護、Evacuation Controller、NodeMaintenanceOperator
:::
