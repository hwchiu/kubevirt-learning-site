---
layout: doc
title: KubeVirt — 🌐 API 與網路測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# 🌐 API 與網路測驗

<QuizQuestion
  question="1. 在 KubeVirt 中，VirtualMachine (VM) 資源類比哪個 Kubernetes 資源？"
  :options='["Pod","Deployment","ReplicaSet","StatefulSet"]'
  :answer="1"
  explanation="VM 是 VMI 的宣告式包裝器，負責管理期望狀態並跨越重啟持久存在，類比 Kubernetes 的 Deployment；而 VMI（VirtualMachineInstance）是實際執行實體，類比 Pod。"
/>

<QuizQuestion
  question="2. VM 的 runStrategy 設為 Always 時，當 VMI 因錯誤失敗後，會發生什麼行為？"
  :options='["VMI 不重建，需手動操作","Controller 自動重建 VMI","VM 也一起被刪除","VM 進入 Halted 狀態"]'
  :answer="1"
  explanation="runStrategy: Always 表示永遠保持 VMI 執行，類似 Deployment 的 replicas: 1。無論 VMI 失敗或被刪除，VM Controller 都會自動重建新的 VMI，確保服務持續運行。"
/>

<QuizQuestion
  question="3. 哪個 RunStrategy 值代表 VM 已關機、不建立 VMI 的狀態？"
  :options='["Manual","Once","Halted","RerunOnFailure"]'
  :answer="2"
  explanation="Halted 代表停止 VM、不建立 VMI，等同於虛擬機器的關機狀態。Manual 需手動透過 virtctl start/stop 控制；Once 只啟動一次後不重建；RerunOnFailure 只在失敗時重建。"
/>

<QuizQuestion
  question="4. VMI 的 evictionStrategy 設為 LiveMigrate 時，當節點被 drain（驅逐）會發生什麼？"
  :options='["VMI 立即被強制終止","嘗試執行 Live Migration 到其他節點","VM 被暫停（Paused）","驅逐失敗，VMI 維持在原節點"]'
  :answer="1"
  explanation="evictionStrategy: LiveMigrate 表示節點驅逐時嘗試 Live Migration。若 VMI 不可遷移，驅逐會失敗。相對地，LiveMigrateIfPossible 在無法遷移時直接刪除 VMI；None 則是直接強制終止。"
/>

<QuizQuestion
  question="5. containerDisk Volume 類型的主要特性是什麼？"
  :options='["資料持久保存，重啟後仍存在","VMI 結束後資料消失（ephemeral）","需要 PVC 支援才能使用","支援 ReadWriteMany 存取模式"]'
  :answer="1"
  explanation="containerDisk 是從 OCI 映像提供的磁碟，屬於 ephemeral（暫存）類型。每次 VMI 啟動都從映像取得一份新的磁碟，VMI 結束後資料完全消失，適合快速測試或無狀態 VM。"
/>

<QuizQuestion
  question="6. 在 VMI spec 的 networks 區段中，引用 Kubernetes Pod 預設網路的正確語法是？"
  :options='["pod: {}","multus: {}","bridge: {}","default: {}"]'
  :answer="0"
  explanation="在 VMI 的 networks 定義中，使用 pod: {} 來引用 Pod 的預設網路（由叢集 CNI 管理）；multus: { networkName: &quot;...&quot; } 用於引用 Multus 的附加網路。interfaces 中的 name 需與 networks 中的 name 對應。"
/>

<QuizQuestion
  question="7. 建立 VirtualMachineInstanceMigration 時，唯一必填的 spec 欄位是？"
  :options='["targetNode","vmiName","migrationUID","bandwidthPerMigration"]'
  :answer="1"
  explanation="VirtualMachineInstanceMigration 的 spec 只有一個必填欄位：vmiName，指定要遷移的 VMI 名稱，且 VMI 必須存在於同一個 Namespace。其他如目標節點等由 KubeVirt Controller 自動決定。"
/>

<QuizQuestion
  question="8. VirtualMachineInstanceMigration 的 Phase 正確順序是？"
  :options='[
    "Pending → TargetReady → PreparingTarget → Running → Succeeded",
    "Pending → PreparingTarget → TargetReady → Running → Succeeded",
    "Running → PreparingTarget → TargetReady → Pending → Succeeded",
    "PreparingTarget → Pending → TargetReady → Running → Succeeded",
  ]'
  :answer="1"
  explanation="Migration 的狀態機順序為：Pending → PreparingTarget（目標節點準備中）→ TargetReady（目標 virt-launcher 就緒）→ Running（記憶體傳輸中）→ Succeeded/Failed/Cancelled。"
/>

<QuizQuestion
  question="9. Post-Copy Migration 模式的主要風險是什麼？"
  :options='[
    "Migration 速度太慢，停機時間更長",
    "無法在 Running 階段取消",
    "若網路中斷或來源節點故障，目標 VM 將崩潰",
    "Post-Copy 會消耗過多 CPU，影響 VM 效能",
  ]'
  :answer="2"
  explanation="Post-Copy 模式先切換 CPU 狀態，再按需從來源節點拉取缺少的記憶體頁面（page fault）。若網路中斷或來源節點故障，目標 VM 無法取得記憶體頁面，導致 VM 崩潰。Pre-Copy 模式較為安全。"
/>

<QuizQuestion
  question="10. MigrationPolicy 的 allowAutoConverge 設為 true 時，會執行什麼操作？"
  :options='[
    "自動選擇效能最佳的目標節點",
    "自動降低 Guest CPU 速度，以協助記憶體髒頁率收斂",
    "自動增加遷移頻寬上限",
    "在失敗時自動重試 Migration",
  ]'
  :answer="1"
  explanation="allowAutoConverge 允許自動收斂機制。當 VM 記憶體寫入速度過快導致 dirty page 產生速度超過傳輸速度時，系統自動降低 Guest CPU 頻率，減慢記憶體髒頁產生速率，協助 Migration 完成收斂。"
/>

<QuizQuestion
  question="11. 在 KubeVirt 的 Instancetype/Preference 系統中，Instancetype 定義的值具有什麼性質？"
  :options='[
    "建議性，VM spec 中可以覆蓋",
    "強制性，VM spec 中不能覆蓋",
    "可選的，僅作為排程提示",
    "僅影響 virt-launcher 的資源請求",
  ]'
  :answer="1"
  explanation="Instancetype 負責資源規格（CPU 數量、Memory 大小等），這些值是強制性的，VM spec 中不能覆蓋。Preference 負責硬體偏好（磁碟 bus、網卡型號等），是建議性的，VM spec 中明確指定的值優先。"
/>

<QuizQuestion
  question="12. VirtualMachineClusterInstancetype 與 VirtualMachineInstancetype 最主要的差別是什麼？"
  :options='[
    "ClusterInstancetype 支援 GPU 設定，Instancetype 不支援",
    "ClusterInstancetype 是 Cluster-scoped，可被所有 Namespace 使用",
    "ClusterInstancetype 由 virt-controller 管理，效能更高",
    "ClusterInstancetype 不允許使用者自訂，只能使用預設規格",
  ]'
  :answer="1"
  explanation="VirtualMachineClusterInstancetype 是 Cluster-scoped（縮寫 vmcit），可被叢集所有 Namespace 使用，通常由叢集管理員建立作為全叢集標準規格；VirtualMachineInstancetype 是 Namespace-scoped（縮寫 vmit），僅限同一 Namespace 使用。"
/>

<QuizQuestion
  question="13. 在 Instancetype spec 中，指定 VM Guest 所看到的 vCPU 數量的欄位路徑是？"
  :options='["spec.cpu.cores","spec.cpu.guest","spec.cpu.count","spec.cpu.sockets"]'
  :answer="1"
  explanation="在 VirtualMachineInstancetype 的 spec 中，cpu.guest 欄位（必填）指定分配給 VM Guest 的 vCPU 數量。這與 VMI DomainSpec 中的 cpu.cores/sockets/threads 不同，Instancetype 統一以 guest 欄位表示。"
/>

<QuizQuestion
  question="14. 在 Instancetype 或 VMI 中使用 dedicatedCpuPlacement: true 需要滿足哪個前提條件？"
  :options='[
    "節點需啟用 Memory Manager",
    "節點需啟用 CPU Manager（--cpu-manager-policy=static），且 Pod QoS 為 Guaranteed",
    "VM 必須使用 EFI 韌體",
    "需先安裝 SR-IOV Network Operator",
  ]'
  :answer="1"
  explanation="dedicatedCpuPlacement（CPU Pinning）需要：1. Kubernetes 節點啟用 CPU Manager Policy=static，2. Pod 的 QoS 等級必須是 Guaranteed（request==limit），3. 節點有足夠的可分配專屬 CPU。任一條件不符合，VM 將無法排程。"
/>

<QuizQuestion
  question="15. VirtualMachineInstanceReplicaSet (VMIRS) 中，所有 VMI 的儲存特性是？"
  :options='[
    "每個 VMI 有獨立的 PVC，資料持久保存",
    "所有 VMI 共享同一個 PVC",
    "VMI 無持久狀態，刪除後資料消失",
    "使用 DataVolumeTemplates 自動建立獨立磁碟",
  ]'
  :answer="2"
  explanation="VMIRS 管理的 VMI 共享相同的模板（包含 containerDisk），所有 VMI 無持久狀態——刪除後資料消失。這與 Kubernetes ReplicaSet 管理 Pod 的概念相同，適合無狀態、可替換的 VM 工作負載。"
/>

<QuizQuestion
  question="16. 使用 VirtualMachineSnapshot 功能的前提條件是什麼？"
  :options='[
    "叢集需安裝 Velero 備份工具",
    "叢集需安裝支援 VolumeSnapshot 的 CSI 驅動，且存在 VolumeSnapshotClass",
    "VM 必須處於停止（Stopped）狀態才能建立快照",
    "需使用 NFS 作為後端儲存",
  ]'
  :answer="1"
  explanation="VirtualMachineSnapshot 底層依賴 Kubernetes 的 VolumeSnapshot 機制，因此需要：1. 叢集安裝支援 VolumeSnapshot 的 CSI 驅動（如 Ceph RBD CSI）；2. 叢集存在 VolumeSnapshotClass 資源；3. KubeVirt >= v0.35.0。VM 可在線上時建立快照。"
/>

<QuizQuestion
  question="17. VirtualMachineSnapshot status 中的 indication GuestAgent 代表什麼？"
  :options='[
    "VM 目前沒有安裝任何 Guest Agent",
    "快照建立時有 Guest Agent，成功執行了 quiesce（檔案系統凍結），達到 Application-consistent",
    "快照建立時 VM 已被暫停",
    "快照包含完整的 Guest OS 映像備份",
  ]'
  :answer="1"
  explanation="Indication GuestAgent 表示建立快照時有 QEMU Guest Agent 在線，KubeVirt 成功請求 Guest Agent 執行 fsfreeze（quiesce），確保檔案系統一致性，達到 Application-consistent 快照品質。"
/>

<QuizQuestion
  question="18. 執行 VirtualMachineRestore 時，目標 VM 必須處於什麼狀態？"
  :options='["執行中（Running）","遷移中（Migrating）","停止（Stopped）","任何狀態都可以"]'
  :answer="2"
  explanation="VirtualMachineRestore 要求 VM 必須處於停止（Stopped）狀態，否則操作會被拒絕。這是因為還原操作不可逆，需要替換現有的 PVC 資料。"
/>

<QuizQuestion
  question="19. VirtualMachineClone 資源的 apiVersion 是什麼？"
  :options='[
    "kubevirt.io/v1",
    "snapshot.kubevirt.io/v1beta1",
    "clone.kubevirt.io/v1beta1",
    "cdi.kubevirt.io/v1beta1",
  ]'
  :answer="2"
  explanation="VirtualMachineClone 的 apiVersion 是 clone.kubevirt.io/v1beta1，屬於獨立的 API 群組。VirtualMachineSnapshot/Restore 使用 snapshot.kubevirt.io/v1beta1，VM/VMI 使用 kubevirt.io/v1，CDI 資源使用 cdi.kubevirt.io/v1beta1。"
/>

<QuizQuestion
  question="20. VirtualMachineSnapshot 的 deletionPolicy 設為 Retain 時，代表什麼行為？"
  :options='[
    "快照將在 7 天後自動刪除",
    "即使關聯的 VM 被刪除，底層 VolumeSnapshot 仍然保留",
    "禁止任何人刪除此快照",
    "快照在成功還原後自動刪除",
  ]'
  :answer="1"
  explanation="deletionPolicy: Retain 表示即使關聯的 VM 被刪除，底層 VolumeSnapshot 資源仍然保留，確保快照資料不因 VM 刪除而消失。預設值 OnVMDelete 則是當 VM 被刪除時快照自動刪除。"
/>

<QuizQuestion
  question="21. KubeVirt 中每個 VM 實際上執行在哪個基礎設施元件內？"
  :options='[
    "直接執行在 Kubernetes Node 的 Hypervisor 上",
    "執行在 virt-controller Pod 中",
    "執行在一個 virt-launcher Pod 內的 QEMU Process 中",
    "執行在獨立的 KVM 節點上，與 Kubernetes 網路隔離",
  ]'
  :answer="2"
  explanation="KubeVirt 的每個 VM 執行在一個 Kubernetes Pod（稱為 virt-launcher Pod）內，Pod 中有 QEMU/KVM 進程負責實際執行虛擬機器。所有 Kubernetes NetworkPolicy 對 virt-launcher Pod 同樣有效。"
/>

<QuizQuestion
  question="22. Kubernetes NetworkPolicy 對 KubeVirt VM 流量控制的效果是什麼？"
  :options='[
    "NetworkPolicy 對 VM 完全無效，需另設 VM 防火牆規則",
    "NetworkPolicy 套用到 virt-launcher Pod，因此對 VM 的流量同樣有效",
    "只有使用 Calico CNI 時，NetworkPolicy 才對 VM 有效",
    "NetworkPolicy 只能控制 VM 的 Ingress，無法控制 Egress",
  ]'
  :answer="1"
  explanation="由於 VM 執行在 virt-launcher Pod 內，Kubernetes NetworkPolicy 套用到 virt-launcher Pod，對 VM 的進出流量同樣有效。平台工程師可以使用標準 NetworkPolicy 控制 VM 的網路存取。"
/>

<QuizQuestion
  question="23. Masquerade 模式下，VM Guest 預設取得的 IP 地址是什麼？"
  :options='[
    "直接使用 virt-launcher Pod 的 IP",
    "10.0.2.1（tap 介面 Gateway IP）",
    "10.0.2.2（virt-launcher 內建 DHCP 分配）",
    "169.254.0.1（Link-Local 地址）",
  ]'
  :answer="2"
  explanation="Masquerade 模式使用 NAT + 內建 DHCP Server。virt-launcher 的 DHCP Server 分配 VM IP 為 10.0.2.2/24，Gateway 為 10.0.2.1，DNS 為 10.0.2.3。VM 的私有 IP 對叢集不可見，出站流量透過 MASQUERADE 規則改寫成 Pod IP。"
/>

<QuizQuestion
  question="24. 以下哪個網路綁定模式支援 VM 的 Live Migration？"
  :options='["Bridge","SR-IOV","Masquerade","Macvtap"]'
  :answer="2"
  explanation="Masquerade 模式支援 Live Migration，因為 VM 使用私有 IP（10.0.2.2），與 Pod IP 解耦，VM 遷移到新節點後取得新的 Pod IP，NAT 規則重新建立即可。Bridge 模式因 VM 共享 Pod IP 導致 Migration 複雜；SR-IOV 因 VF 綁定到特定硬體不支援。"
/>

<QuizQuestion
  question="25. Masquerade 模式中，virt-launcher 內建 DHCP Server 提供給 VM 的 Gateway IP 是什麼？"
  :options='["10.0.2.2","10.0.2.1","10.0.2.3","與 virt-launcher Pod 的 Gateway 相同"]'
  :answer="1"
  explanation="virt-launcher 內建 DHCP Server 回應 VM 的 DHCP 請求時，提供：VM IP=10.0.2.2、Gateway=10.0.2.1（tap 介面 IP，由 virt-launcher 持有）、DNS=10.0.2.3（對應 Cluster DNS 如 CoreDNS）。預設 Gateway CIDR 為 10.0.2.0/24，可自訂。"
/>

<QuizQuestion
  question="26. Bridge 模式中，ARP Proxy 設定的主要目的是什麼？"
  :options='[
    "提升 Bridge 模式的網路吞吐量",
    "代替 VM 回應 ARP 請求，確保外部流量正確路由到 Pod，再透過 tap 送達 VM",
    "防止 ARP 廣播造成網路風暴",
    "讓 VM 支援 IPv6 雙棧網路",
  ]'
  :answer="1"
  explanation="Bridge 模式下，VM 與 Pod 共享同一個 IP。當外部節點透過 ARP 查詢此 IP 時，Pod 的 Linux Bridge（k6t-eth0）透過 ARP Proxy 代替 VM 回應，確保流量路由到 Pod，再透過 tap 介面送達 VM。"
/>

<QuizQuestion
  question="27. SR-IOV 技術中，一張實體網卡（Physical Function, PF）可分裂出多個什麼？"
  :options='["Virtual Interface（VI）","Virtual Function（VF）","Virtual NIC（vNIC）","Virtual Port（VP）"]'
  :answer="1"
  explanation="SR-IOV（Single Root I/O Virtualization）是 PCIe 硬體虛擬化技術。實體網卡稱為 Physical Function（PF），可分裂為多個 Virtual Function（VF）。每個 VF 可直接分配給一個 VM，VM 透過 VFIO 驅動直接存取硬體。"
/>

<QuizQuestion
  question="28. SR-IOV 硬體直通需要哪個系統功能支援才能安全進行記憶體隔離？"
  :options='["NUMA（Non-Uniform Memory Access）","HugePages","IOMMU（Input-Output Memory Management Unit）","SR-IOV Device Plugin 即可，不需要硬體支援"]'
  :answer="2"
  explanation="IOMMU 是 SR-IOV 安全的基礎。沒有 IOMMU，VF 可以存取任意主機記憶體，存在 DMA 攻擊風險。啟用 IOMMU 後，每個 VF 只能存取分配給它的記憶體區域，確保 VM 間的記憶體隔離安全。Intel 平台使用 intel_iommu=on，AMD 使用 amd_iommu=on。"
/>

<QuizQuestion
  question="29. 為何 SR-IOV 模式的 VM 不支援 Live Migration？"
  :options='[
    "因為 SR-IOV 效能太高，遷移時資料量無法即時同步",
    "因為 VF（Virtual Function）是直接綁定到特定節點的實體網卡硬體，無法跨節點遷移",
    "因為 SR-IOV 不支援 TCP/IP 協議，只能用於純二層通訊",
    "因為 KubeVirt 尚未實作 SR-IOV 的 Migration 支援，未來版本將支援",
  ]'
  :answer="1"
  explanation="SR-IOV 的 VF 是直接分配自特定節點上的特定實體網卡（PF），與特定硬體緊密綁定。Live Migration 需要將 VM 的所有資源遷移到另一個節點，但 VF 是節點本地的硬體資源，無法跟著 VM 遷移到另一台實體機器。"
/>

<QuizQuestion
  question="30. Multus CNI 在 KubeVirt 網路中解決了什麼核心問題？"
  :options='[
    "標準 Kubernetes 每個 Pod 只有一個網路介面；Multus 允許 Pod 同時連接到多個網路，讓 VM 可以有多張虛擬網卡",
    "Multus 提供 SR-IOV 的硬體 VF 資源管理",
    "Multus 取代了叢集 CNI 插件，提供統一的高效能網路",
    "Multus 讓 VM 能使用 Kubernetes Service 的 Layer 7 負載均衡",
  ]'
  :answer="0"
  explanation="標準 Kubernetes 每個 Pod 只有一個網路介面（加上 loopback）。Multus 是 meta-CNI 插件，允許 Pod 透過 NetworkAttachmentDefinition（NAD）連接到多個網路，讓 KubeVirt VM 可以擁有多張虛擬網卡，滿足 NFV、多租戶等進階場景需求。"
/>
