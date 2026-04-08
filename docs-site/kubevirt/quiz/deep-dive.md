---
layout: doc
title: KubeVirt — 🔬 深入剖析測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# 🔬 深入剖析測驗

<QuizQuestion
  question="1. KubeVirt 採用三層架構管理虛擬機，負責將 VirtualMachineInstance（VMI）規格轉換為 libvirt Domain 物件的核心函式名稱為何？"
  :options='[
    "SyncVMI()",
    "DomainDefineXML()",
    "Convert_v1_VirtualMachineInstance_To_api_Domain()",
    "BuildDomainSpec()",
  ]'
  :answer="2"
  explanation="KubeVirt 三層架構中，第二層 Converter 的核心函式為 Convert_v1_VirtualMachineInstance_To_api_Domain()，它採用 Configurator 模式，依序執行 27+ 個 Configurator（如 CPUDomainConfigurator、MemoryConfigurator 等），將 VMI 規格轉換為完整的 Domain XML，再透過 DomainDefineXML() 交給 libvirtd 啟動 QEMU。"
/>

<QuizQuestion
  question="2. KubeVirt 的 Configurator 模式中，每個 Configurator 需實作統一介面。下列哪個方法簽名正確描述了這個介面？"
  :options='[
    "Build(vmi *v1.VirtualMachineInstance) (*api.Domain, error)",
    "Configure(vmi *v1.VirtualMachineInstance, domain *api.Domain) error",
    "Transform(spec *api.DomainSpec) error",
    "Apply(ctx *ConverterContext, domain *api.Domain) error",
  ]'
  :answer="1"
  explanation="根據 pkg/virt-launcher/virtwrap/converter/types/builder.go，Configurator 介面定義為 Configure(vmi *v1.VirtualMachineInstance, domain *api.Domain) error。每個 Configurator（CPU、Memory、Clock 等）都實作此方法，在方法中修改傳入的 domain 物件，實現各自的 Domain XML 配置職責。"
/>

<QuizQuestion
  question="3. KubeVirt 選擇透過 libvirt 操作 QEMU，而非直接操作 QEMU 命令列，主要原因不包含下列哪項？"
  :options='[
    "libvirt 提供版本穩定的 C/Go binding，避免直接依賴 QEMU 命令列參數的變化",
    "libvirt 提供標準化的 AttachDevice / DetachDevice API 支援設備熱插拔",
    "libvirt 內建完整的生命週期事件回調機制",
    "libvirt 提供圖形化管理介面以方便操作員手動調整 VM 設定",
  ]'
  :answer="3"
  explanation="KubeVirt 選用 libvirt 的原因包含：穩定的 API（避免依賴 QEMU 命令列變化）、安全性（libvirt 提供權限隔離與 SELinux/AppArmor 整合）、事件系統（完整的生命週期事件回調）、設備熱插拔（標準化的 AttachDevice/DetachDevice API）、以及原生的 Live Migration 協議支援。圖形化管理介面並不在其中。"
/>

<QuizQuestion
  question="4. 每個 VMI 運行在獨立的 virt-launcher Pod 中，Pod 內部包含哪三個關鍵程序？"
  :options='[
    "virt-api、virt-controller、virt-handler",
    "virt-launcher (Go)、libvirtd/virtqemud、qemu-system-x86_64",
    "containerd、libvirtd、qemu-system-x86_64",
    "virt-handler、libvirtd、kubelet",
  ]'
  :answer="1"
  explanation="根據文件，virt-launcher Pod 內部有三個關鍵程序：virt-launcher（Go 程式，負責 CMD Server、Domain Notifier、Agent Poller，透過 gRPC 與 virt-handler 通訊）、libvirtd/virtqemud（負責 Domain XML 管理與事件處理）、以及 qemu-system-x86_64（虛擬機實際執行進程）。"
/>

<QuizQuestion
  question="5. 在 KubeVirt 產生的典型 Domain XML 中，預設使用的 machine type 是什麼？"
  :options='[
    "i440fx",
    "q35",
    "virt",
    "microvm",
  ]'
  :answer="1"
  explanation="根據文件中的典型 Domain XML 輸出範例，KubeVirt 預設使用 q35 machine type：&lt;type arch=&quot;x86_64&quot; machine=&quot;q35&quot;&gt;hvm&lt;/type&gt;。q35 是現代 Intel PCH 晶片組模擬，支援 PCIe、NVMe 等現代硬體介面，是比舊式 i440fx 更推薦的選擇。"
/>

<QuizQuestion
  question="6. 在 Windows VM 的 HyperV Enlightenments 設定中，Relaxed 功能的主要作用是什麼？"
  :options='[
    "啟用半虛擬化 APIC，減少 VM-Exit 次數",
    "放寬 Windows 核心的 watchdog timeout，避免 BSOD",
    "最佳化 TLB 刷新路徑，降低記憶體存取延遲",
    "啟用合成中斷控制器，提升中斷處理效率",
  ]'
  :answer="1"
  explanation="HyperV 的 Relaxed 功能告知 Windows 核心放寬 watchdog timeout 限制。在虛擬化環境中，CPU 排程延遲可能觸發 Windows 嚴格的 watchdog timer，導致 BSOD（藍屏）。文件指出不啟用 Relaxed 是 Windows VM BSOD 最常見的原因之一，強烈建議所有 Windows VM 都啟用此功能。"
/>

<QuizQuestion
  question="7. KubeVirt Windows VM 工廠函式中，Spinlocks 的建議 Retries 值為多少？這個值的意義是什麼？"
  :options='[
    "值為 4096；超過此次自旋後改用 hypercall 通知 hypervisor",
    "值為 8191；超過此次自旋後改用 hypercall 通知 hypervisor，此為微軟推薦最佳值",
    "值為 1024；超過此次自旋後直接放棄鎖",
    "值為 16383；此為 QEMU 硬體上限",
  ]'
  :answer="1"
  explanation="根據 tests/libvmifact/factory.go 的程式碼，const featureSpinlocks = 8191，KubeVirt 設定 Spinlocks Retries 為 8191，這是微軟推薦的最佳值。其意義是：Windows 核心在虛擬環境中大量使用 spinlock，超過 8191 次自旋後，改用 hypercall 通知 hypervisor 讓出 CPU，避免持有 lock 的 vCPU 被 host 調度出去時，等待的 vCPU 持續空轉浪費 CPU 時間。"
/>

<QuizQuestion
  question="8. 針對 Windows VM 的時鐘配置，文件建議將 HPET 設為停用。原因為何？"
  :options='[
    "HPET 不支援 Windows 10 以上版本",
    "HPET 在虛擬化環境中模擬成本極高，每次讀取需要 VM-Exit",
    "HPET 會與 HyperV Timer 發生衝突",
    "HPET 佔用過多的 CPU 中斷資源",
  ]'
  :answer="1"
  explanation="文件明確指出 HPET（High Precision Event Timer）在虛擬化環境中模擬成本極高，每次讀取都需要 VM-Exit。Windows 推薦時鐘配置為：HPET Enabled: false、PIT TickPolicy: delay、RTC TickPolicy: catchup、Hyperv Timer Enabled: true。HyperV Timer 提供 Windows 專用的半虛擬化時鐘，效能最佳，應取代 HPET。"
/>

<QuizQuestion
  question="9. KubeVirt 中 HyperV VendorID 功能常用於繞過 NVIDIA 消費級 GPU 驅動的偵測。通常需要搭配哪個設定一起使用效果最佳？"
  :options='[
    "hyperv.ipi: {} 搭配 hyperv.evmcs: {}",
    "kvm.hidden: true 搭配 hyperv.vendorid.vendorid: \\\"randomstring\\\"",
    "features.acpi 停用",
    "hyperv.tlbflush.direct: {} 搭配 hyperv.reenlightenment: {}",
  ]'
  :answer="1"
  explanation="根據文件，NVIDIA 消費級 GPU 驅動（GeForce 系列）會偵測虛擬化環境並拒絕啟動。設定自定義 VendorID 可繞過此偵測，搭配 kvm.hidden: true 一起使用效果最佳。kvm.hidden 會隱藏 KVM 虛擬化特徵，而自定義 VendorID 則替換 hypervisor 識別字串，雙管齊下才能有效繞過 NVIDIA 的檢測機制。"
/>

<QuizQuestion
  question="10. 啟用 CPU Pinning（dedicatedCPUPlacement）需要在 Kubernetes 節點層級滿足哪個前提條件？"
  :options='[
    "節點需要安裝 NUMA Balancing kernel module",
    "kubelet 必須啟用 --cpu-manager-policy=static 並且 Pod 使用 Guaranteed QoS class",
    "節點必須安裝 RT kernel（kernel-rt）",
    "需要在 KubeVirt CR 中啟用 CPUPinning Feature Gate",
  ]'
  :answer="1"
  explanation="根據文件，CPU Pinning 需要 Kubernetes 節點啟用 static CPU Manager Policy（--cpu-manager-policy=static），並且 Pod 必須使用 Guaranteed QoS class（requests == limits）。否則 KubeVirt 無法取得專屬 CPU 核心。kubelet 也需設定預留 CPU（--reserved-cpus），且 VM 的 CPU 請求必須是整數。"
/>

<QuizQuestion
  question="11. isolateEmulatorThread 功能的目的是什麼？啟用後會有什麼額外代價？"
  :options='[
    "將 QEMU 主執行緒隔離到獨立 CPU 核心，額外消耗一個 CPU 核心",
    "將 Guest Agent 隔離到獨立 CPU 核心，效能無損耗",
    "隔離 NUMA 節點間的記憶體存取，消耗額外 10% 記憶體",
    "隔離網路 IO 執行緒，消耗一個額外的網路佇列",
  ]'
  :answer="0"
  explanation="根據文件，QEMU 除了 vCPU 執行緒外，還有一個主要的 emulator thread 負責 IO 模擬和管理工作。isolateEmulatorThread 將這個執行緒分配到獨立的 CPU 核心，避免與 vCPU 執行緒競爭。代價是額外消耗一個 CPU 核心（例如設定 4 cores + isolateEmulatorThread，實際佔用 5 個核心），但可以避免 emulator thread 搶佔 vCPU 的執行時間，對 IO 密集型工作負載特別有效。"
/>

<QuizQuestion
  question="12. 在選擇 HugePages 大小時，1Gi 與 2Mi 各有哪些考量？下列描述何者正確？"
  :options='[
    "1Gi HugePages 可以動態調整分配，適合所有場景",
    "2Mi HugePages TLB 效能優於 1Gi，但需要更多連續記憶體",
    "1Gi HugePages TLB 效能最佳，但需要連續 1GB 記憶體區塊，可能導致分配失敗；2Mi 更靈活",
    "兩者效能完全相同，僅影響記憶體對齊方式",
  ]'
  :answer="2"
  explanation="根據文件，1Gi HugePages 提供最佳 TLB 效能，但需要連續的 1GB 記憶體區塊，可能導致分配失敗，適合大記憶體 VM。2Mi HugePages 分配更靈活，適合中小型 VM，效能略低於 1Gi 但遠優於普通 4KB 分頁。相較於普通 4KB 分頁，8GB 記憶體需管理 2,097,152 個分頁條目，而 1Gi HugePages 只需 8 個，大幅減少 TLB miss。"
/>

<QuizQuestion
  question="13. 在 NUMA 架構中，CPU Pinning 與 HugePages 未正確對齊到同一 NUMA 節點時，可能造成多大的記憶體存取延遲增加？"
  :options='[
    "約 5-10%",
    "約 10-20%",
    "約 40-100%",
    "約 200-300%",
  ]'
  :answer="2"
  explanation="根據文件，當 vCPU 和記憶體分佈在不同 NUMA 節點時，記憶體存取延遲可能增加 40-100%，嚴重影響資料庫和高效能運算工作負載。文件警告：務必確保 CPU Pinning 和 HugePages 配合 NUMA 對齊使用。建議搭配 numa.guestMappingPassthrough 將 Host NUMA 拓撲直接映射給 Guest，以確保 CPU 和記憶體在同一 NUMA 節點。"
/>

<QuizQuestion
  question="14. VFIO（Virtual Function I/O）框架透過哪個硬體機制確保虛擬機只能存取被分配的裝置記憶體區域，無法越界存取？"
  :options='[
    "VT-d（Intel Virtualization Technology for Directed I/O）指令集",
    "IOMMU（Input-Output Memory Management Unit）",
    "SR-IOV（Single Root I/O Virtualization）",
    "EPT（Extended Page Table）",
  ]'
  :answer="1"
  explanation="根據文件，VFIO 透過 IOMMU（Input-Output Memory Management Unit）實現安全的裝置直通。IOMMU 確保虛擬機只能存取被分配的裝置記憶體區域，無法越界存取主機或其他 VM 的記憶體。PCI Device Plugin 從 sysfs 路徑 /sys/bus/pci/devices/{pciAddress}/iommu_group 讀取裝置的 IOMMU group ID，並將 /dev/vfio/{iommuGroupId} 裝置節點分配給 Pod。"
/>

<QuizQuestion
  question="15. 關於 IOMMU Group 的限制，下列描述何者正確？"
  :options='[
    "每個 IOMMU Group 最多只能包含一個 PCI 裝置",
    "同一 IOMMU Group 中的所有裝置必須一起直通給同一個 VM",
    "IOMMU Group 可以在不同 VM 之間分享",
    "IOMMU Group 的大小由驅動程式決定，與硬體無關",
  ]'
  :answer="1"
  explanation="根據文件，同一 IOMMU Group 中的所有裝置必須一起直通給同一個 VM，這是硬體層級的限制——IOMMU 以 group 為單位進行 DMA 隔離。若 GPU 與其他裝置（如 PCIe bridge）共用同一個 IOMMU Group，則這些裝置都必須被直通。文件建議可使用 ACS（Access Control Services）來分割 IOMMU Group，解決此限制。"
/>

<QuizQuestion
  question="16. KubeVirt PCI Device Plugin 在 Allocate() 被呼叫時，會回傳哪些資源給 Pod？"
  :options='[
    "只回傳環境變數，不提供裝置節點",
    "環境變數（PCI_RESOURCE_{resourceName}）、/dev/vfio/vfio 以及 /dev/vfio/{iommuGroupId}",
    "只提供 /dev/vfio/{iommuGroupId} 裝置節點",
    "環境變數與 /dev/dri 圖形裝置節點",
  ]'
  :answer="1"
  explanation="根據文件，當 Kubelet 呼叫 Allocate() gRPC 方法時，PCI Device Plugin 回傳：(1) 環境變數 PCI_RESOURCE_{resourceName}，包含分配的 PCI 位址（逗號分隔）；(2) 裝置節點 /dev/vfio/vfio（VFIO 容器裝置，所有 VFIO 裝置共用）；(3) 裝置節點 /dev/vfio/{iommuGroupId}（特定 IOMMU Group 的裝置檔案）。"
/>

<QuizQuestion
  question="17. KubeVirt 產生的 GPU 直通 libvirt XML 中，managed=&quot;no&quot; 屬性的意義為何？"
  :options='[
    "libvirt 不會自動啟動此裝置",
    "此裝置由 KubeVirt 管理驅動程式的綁定與解綁，而非 libvirt",
    "此裝置在 VM 關機後不會自動釋放",
    "此裝置不支援熱插拔",
  ]'
  :answer="1"
  explanation="根據文件，GPU 直通的 libvirt XML 為 &lt;hostdev type='pci' managed='no'&gt;，其中 managed='no' 表示由 KubeVirt（而非 libvirt）管理驅動程式的綁定與解綁。KubeVirt 自行處理 vfio-pci 驅動的綁定，不依賴 libvirt 的自動管理機制。PCI 位址的 domain、bus、slot、function 從 BDF 格式位址（如 0000:3b:00.0）解析而來。"
/>

<QuizQuestion
  question="18. 關於 NVIDIA vGPU 的 mdev（Mediated Devices）框架，下列哪項描述正確說明了 ring-based 分配策略？"
  :options='[
    "將 mdev 實例以輪詢方式分配給不同的 VM，確保公平",
    "優先從負載較低的父 GPU 上分配新實例，將 vGPU 均勻分佈在多張實體 GPU 上",
    "根據 GPU 型號自動選擇最適合的 mdev 類型",
    "依照 VM 的記憶體需求動態調整每個 mdev 實例的 VRAM 大小",
  ]'
  :answer="1"
  explanation="根據文件，KubeVirt 採用 ring-based 分配策略，Device Plugin 追蹤每張父 GPU 上已分配的 mdev 實例數量，優先從負載較低的父 GPU 上分配新實例，避免熱點集中在單一 GPU 上。例如，Tesla T4 可分割為 GRID T4-1Q（16 instances）、GRID T4-2Q（8 instances）等不同 Profile，此策略確保多張 GPU 的使用均衡。"
/>

<QuizQuestion
  question="19. KubeVirt virt-launcher Pod 的 securityContext 中，預設使用哪種 Seccomp Profile 類型？"
  :options='[
    "Unconfined（無限制）",
    "Localhost（自定義 profile 檔案）",
    "RuntimeDefault（容器運行時預設 profile）",
    "Audited（審計模式）",
  ]'
  :answer="2"
  explanation="根據文件，virt-launcher 的 securityContext 設定為 seccompProfile.type: RuntimeDefault，使用 Kubernetes 容器運行時的預設 Seccomp profile 來限制可使用的系統呼叫。此設定搭配 runAsNonRoot: true、runAsUser: 107（qemu 使用者）、allowPrivilegeEscalation: false 等安全設定，確保最小權限原則。若需更嚴格控制，可在 KubeVirt CR 的 seccompConfiguration 中設定 customProfile。"
/>

<QuizQuestion
  question="20. 在啟用 SELinux 的環境中，KubeVirt 為每個 VM 分配唯一的 MCS（Multi-Category Security）label 的目的是什麼？"
  :options='[
    "使 VM 能夠存取主機的 /dev/kvm 裝置",
    "確保不同 VM 的 QEMU 進程無法存取彼此的資源",
    "允許 virt-handler 透過 SELinux 驗證 VM 的身份",
    "控制 VM 可以連接的網路介面",
  ]'
  :answer="1"
  explanation="根據文件，KubeVirt 為每個 VM 的 virt-launcher 分配唯一的 MCS label（例如 s0:c1,c2）。這確保不同 VM 的 QEMU 進程無法存取彼此的資源——SELinux 以 MCS label 作為隔離邊界，不同 label 的進程無法讀寫對方的檔案。Live Migration 時，目標端必須使用與源端相同的 SELinux MCS label，否則 QEMU 將無法存取共享儲存上的磁碟映像。"
/>

<QuizQuestion
  question="21. Live Migration 時，KubeVirt 如何處理 SELinux Level 的匹配問題？"
  :options='[
    "自動為目標端生成新的 SELinux Level，然後重新掛載磁碟",
    "在遷移前將源端的 SELinux MCS label 傳遞給目標端，確保兩端使用相同 label",
    "停用 SELinux，遷移完成後重新啟用",
    "目標端使用全域 label s0，確保能存取所有共享儲存",
  ]'
  :answer="1"
  explanation="根據文件，Live Migration 時，KubeVirt 確保目標端的 virt-launcher 使用與源端相同的 SELinux MCS label。這是透過在遷移前將源端的 SELinux label 傳遞給目標端來實現的。文件指出，這也是 Target Pod 的建立方式之一——Target Pod 的 SELinux Level 必須匹配源端 Level，確保共享儲存可存取。若 label 不匹配，QEMU 將無法存取共享儲存上的磁碟映像。"
/>

<QuizQuestion
  question="22. KubeVirt Live Migration 涉及四個核心元件的協作。下列哪個元件負責建立目標 Pod 並管理整個遷移的狀態機？"
  :options='[
    "virt-handler (Source)",
    "virt-launcher (Source)",
    "virt-controller（Migration Controller）",
    "virt-api",
  ]'
  :answer="2"
  explanation="根據文件，四個核心元件各有分工：virt-controller 是遷移調度器，負責建立目標 Pod、管理遷移狀態機、協調整體流程；virt-handler (Source) 是源端代理，負責啟動 migration proxy、監控遷移進度；virt-handler (Target) 是目標端代理，負責準備目標環境；virt-launcher (Source/Target) 是 libvirt 執行器，實際呼叫 libvirt API 執行記憶體與磁碟資料傳輸。"
/>

<QuizQuestion
  question="23. Migration Proxy 使用的兩個固定 TCP Port 分別為何？"
  :options='[
    "LibvirtDirectMigrationPort: 49152；LibvirtBlockMigrationPort: 49153",
    "LibvirtDirectMigrationPort: 16509；LibvirtBlockMigrationPort: 16514",
    "LibvirtDirectMigrationPort: 8443；LibvirtBlockMigrationPort: 8444",
    "LibvirtDirectMigrationPort: 4444；LibvirtBlockMigrationPort: 4445",
  ]'
  :answer="0"
  explanation="根據文件 pkg/virt-handler/migration-proxy/migration-proxy.go，const LibvirtDirectMigrationPort = 49152（libvirt 直接遷移通道，用於記憶體傳輸）、const LibvirtBlockMigrationPort = 49153（Block migration 通道，用於磁碟資料傳輸）。Migration Proxy 架構為 Source Node 的 Unix Socket → TCP（這兩個 Port）→ Target Node 的 Unix Socket，再連接到目標端的 libvirtd。"
/>

<QuizQuestion
  question="24. 在 Pre-copy 遷移模式中，若記憶體的 dirty rate 持續超過網路傳輸速度，會發生什麼情況？"
  :options='[
    "系統自動增加網路頻寬來跟上 dirty rate",
    "遷移永遠無法收斂——每一輪傳送的 dirty pages 都比上一輪多",
    "QEMU 自動暫停 VM 等待傳輸完成",
    "系統自動切換到 Storage Migration 模式",
  ]'
  :answer="1"
  explanation="根據文件，Pre-copy 採用迭代式記憶體複製策略。當 VM 的記憶體 dirty rate（每秒修改的記憶體量）持續超過網路傳輸速度時，Pre-copy 遷移永遠無法收斂——因為每一輪新產生的 dirty pages 都多於可傳輸的量。解決方案包括：Auto-converge（逐步降低 vCPU 速度減少 dirty rate）或切換到 Post-copy 模式（先切換執行再按需取回頁面）。"
/>

<QuizQuestion
  question="25. Post-copy 遷移為何不支援具有 VFIO（GPU passthrough）設備的 VM？"
  :options='[
    "VFIO 設備的記憶體頻寬不足以支援 Post-copy",
    "VFIO 設備狀態無法透過 page-fault 機制按需取回",
    "VFIO 設備在遷移過程中需要重新初始化驅動",
    "Kubernetes Device Plugin 不支援 Post-copy 模式",
  ]'
  :answer="1"
  explanation="根據文件，Post-copy 不支援 VFIO 設備，原因是 VFIO 設備的狀態無法透過 page-fault 機制按需取回。Post-copy 的核心機制是先切換執行，再透過 page-fault 請求從源端取回缺少的記憶體頁面。但 GPU 等 VFIO 設備的 DMA 狀態與記憶體狀態緊密耦合，無法分離按需傳輸。對此類 VM，KubeVirt 改用暫停 VM 並設定大 downtime 的方式完成遷移。"
/>

<QuizQuestion
  question="26. Multifd（Multiple File Descriptor）並行傳輸的原理為何？在 10 Gbps 網路環境下啟用 4 個並行通道，效能提升幅度約為多少？"
  :options='[
    "開啟多個 TCP 連線並行傳輸記憶體頁面，可提升 2-3 倍遷移速度",
    "使用 UDP 代替 TCP 來提高傳輸效率，可提升 5 倍速度",
    "透過壓縮記憶體資料來減少傳輸量，可提升 4-6 倍速度",
    "使用 RDMA 直接記憶體存取，可提升 10 倍速度",
  ]'
  :answer="0"
  explanation="根據文件，傳統遷移使用單一 TCP 連線傳送所有記憶體資料，受限於 Linux 核心 TCP 視窗大小與 CPU 加密效能。Multifd 允許開啟多個並行 TCP 通道，將記憶體頁面分散到多個連線上同時傳輸。文件指出在 10 Gbps 網路環境下，啟用 4 個並行通道可以將遷移速度提升 2-3 倍。配置方式為在 KubeVirt CR 的 migrationConfiguration 中設定 parallelMigrationThreads。"
/>

<QuizQuestion
  question="27. Auto-converge 機制如何解決 Pre-copy 遷移不收斂的問題？"
  :options='[
    "自動增加遷移頻寬直到超過 dirty rate",
    "逐步降低 vCPU 執行速度以減少記憶體 dirty rate，最高可降至 99% CPU 節流",
    "自動壓縮記憶體頁面以加快傳輸",
    "透過暫停非關鍵 vCPU 來集中資源給關鍵執行緒",
  ]'
  :answer="1"
  explanation="根據文件，Auto-converge 透過逐步降低 vCPU 執行速度來減少 dirty rate：第一次偵測到不收斂時降低 vCPU 速度 20%，若仍不收斂繼續降低每次增加 10%，最高可降至 99% 的 CPU 節流。雖然效果顯著，但會嚴重降低 VM 內部工作負載的效能。文件建議：兩者可以同時啟用，KubeVirt 會先嘗試 Auto-converge，若仍超時，再切換到 Post-copy（若 AllowWorkloadDisruption 為 true）。"
/>

<QuizQuestion
  question="28. KubeVirt 計算遷移完成超時（CompletionTimeout）的公式為何？對於一個 16 GiB 記憶體的 VM，預設的完成超時為多少秒？"
  :options='[
    "固定 600 秒，與記憶體大小無關",
    "CompletionTimeoutPerGiB × VM 遷移資料大小（GiB），預設 150 × 16 = 2400 秒",
    "ProgressTimeout × 2 = 300 秒",
    "每 GiB 允許 300 秒，16 GiB = 4800 秒",
  ]'
  :answer="1"
  explanation="根據文件，acceptableCompletionTime = options.CompletionTimeoutPerGiB × getVMIMigrationDataSize(vmi)。預設值 MigrationCompletionTimeoutPerGiB = 150 秒。因此 16 GiB 記憶體的 VM 完成超時為 150 × 16 = 2400 秒（40 分鐘）。另外 ProgressTimeout 固定為 150 秒（無進度超時，與記憶體大小無關）。超過 CompletionTimeout 後，若 AllowWorkloadDisruption = true，則觸發 Post-copy 或暫停；否則取消遷移。"
/>

<QuizQuestion
  question="29. KubeVirt 支援專用遷移網路介面，此介面的名稱為何？若節點沒有此介面，系統如何處理？"
  :options='[
    "介面名稱為 mignet0；若不存在則遷移失敗",
    "介面名稱為 migration0；若不存在則 fallback 使用 Pod 的 IP 位址",
    "介面名稱為 kubevirt-migration；若不存在則使用 NodeIP",
    "介面名稱為 virt-migrate；若不存在則等待建立",
  ]'
  :answer="1"
  explanation="根據文件，KubeVirt 專用遷移網路介面名稱為 migration0（定義為常數 MigrationInterfaceName）。FindMigrationIP() 函式嘗試找到 migration0 介面，若節點沒有此介面（err != nil），則直接回傳原始的 migrationIp 參數（通常為 Pod 的 IP 位址），遷移流量會走一般的 Pod 網路。若有 migration0 介面，會優先使用 Global Unicast IPv6 位址（透過 To16() 轉換）。"
/>

<QuizQuestion
  question="30. Migration Controller 使用優先級佇列處理遷移任務。QueuePriorityRunning 的值為 1000，QueuePriorityPending 的值為 -100，這樣設計的主要意義是什麼？"
  :options='[
    "確保使用者手動觸發的遷移優先於系統觸發的遷移",
    "確保正在傳輸資料的遷移（Running）優先獲得處理時間，不被新建立的 Pending 遷移阻塞",
    "確保關鍵系統遷移（SystemCritical）永遠排在最前面",
    "限制同時進行的遷移數量不超過優先級差值",
  ]'
  :answer="1"
  explanation="根據文件，Migration Controller 使用優先級佇列確保已在 Running 狀態（優先級 1000）的遷移優先獲得 controller 的處理時間，新建立的 Pending 遷移（優先級 -100）不會搶佔進行中的遷移。其他優先級包括 QueuePrioritySystemCritical = 100、QueuePriorityUserTriggered = 50、QueuePrioritySystemMaintenance = 20、QueuePriorityDefault = 0。文件特別指出此設計確保正在傳輸資料的遷移不會被新建立的遷移阻塞，保障遷移流程的連續性。"
/>
