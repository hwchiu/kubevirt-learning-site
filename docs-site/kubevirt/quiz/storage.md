---
layout: doc
title: KubeVirt — 💾 儲存與輔助元件測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# 💾 儲存與輔助元件測驗

<QuizQuestion
  question="1. 在 KubeVirt 中，DataVolume 資源由哪個元件負責管理和填充？"
  :options='["virt-controller","virt-handler","CDI（Containerized Data Importer）","virt-operator"]'
  :answer="2"
  explanation="DataVolume 是 CDI（Containerized Data Importer）提供的 CRD。CDI 監聽 DataVolume 的建立，根據 spec.source 派出 importer Pod 執行資料填充（從 HTTP URL、S3、PVC、Registry 等來源），完成後 PVC 可供 VM 使用。"
/>

<QuizQuestion
  question="2. DataVolume spec.source.http 匯入來源的 URL 若指向一個 .qcow2 檔案，CDI 會如何處理磁碟格式？"
  :options='[
    "直接將 .qcow2 檔案寫入 PVC，不做任何轉換",
    "CDI importer 自動將 .qcow2 轉換為 raw 格式後寫入 PVC",
    "CDI 不支援 .qcow2 格式，需先手動轉換",
    "CDI 依照 StorageClass 決定是否轉換格式",
  ]'
  :answer="1"
  explanation="CDI importer Pod 使用 qemu-img 工具，支援自動轉換 qcow2、vmdk、vhd、vhdx 等格式為目標格式（通常是 raw 或 qcow2，取決於 PVC 設定）。這讓管理員可以直接提供原始格式的 VM 映像，無需預先手動轉換。"
/>

<QuizQuestion
  question="3. DataVolume 的 Phase 達到 Succeeded 代表什麼？"
  :options='[
    "DataVolume 已成功綁定到 PVC（資料可能尚未完整）",
    "資料匯入/填充完成，PVC 已可供 VM 使用",
    "VM 已成功掛載此 DataVolume",
    "DataVolume 的備份快照已建立",
  ]'
  :answer="1"
  explanation="DataVolume Phase Succeeded 表示 CDI importer/cloner/uploader Pod 已成功完成資料填充操作，PVC 中的資料完整且已可供 VM 使用。在此之前的 Phase 包括：Pending（等待 PVC 綁定）→ ImportScheduled（Import Pod 排程中）→ ImportInProgress（資料填充中）→ Succeeded。"
/>

<QuizQuestion
  question="4. 以下哪個 DataVolume source 類型允許從叢集內另一個 Namespace 複製 PVC？"
  :options='["sourceRef","pvc（使用 namespace/name 指定）","clone","http"]'
  :answer="1"
  explanation="DataVolume spec.source.pvc 可指定 namespace 和 name 來跨 Namespace 複製 PVC。當來源和目標不在同一 Namespace 時，CDI 使用 Smart Clone（CSI 快照）或 Host Assisted Clone（資料傳輸 Pod），並需要 DataVolume 的 Source Namespace 建立 DataVolumeImportCron 或 CloneSourceRef 授權。"
/>

<QuizQuestion
  question="5. Containerized Data Importer（CDI）的 cdi-uploadproxy Service 的用途是什麼？"
  :options='[
    "將 VM 磁碟匯出到外部儲存系統",
    "接收 virtctl image-upload 指令的本地檔案上傳，轉發給 importer Pod",
    "提供 CDI Web UI 讓管理員監控匯入進度",
    "管理 CDI 元件間的內部 API 通訊",
  ]'
  :answer="1"
  explanation="cdi-uploadproxy 是 CDI 的上傳代理 Service，virtctl image-upload 指令將本地磁碟檔案的位元流發送到 cdi-uploadproxy，再由它轉發給對應的 upload Pod 寫入 PVC。通常需要透過 NodePort、LoadBalancer 或 kubectl port-forward 才能從叢集外部存取。"
/>

<QuizQuestion
  question="6. ContainerDisk 的 Volume 底層資料是如何傳遞給 QEMU 進程的？"
  :options='[
    "直接作為 Block Device 掛載到 QEMU",
    "OCI 映像由 virt-launcher 的 init container 解壓，以臨時 disk.img 檔案透過 hostPath 共享給 QEMU",
    "透過 CSI Driver 動態建立一個臨時 PVC",
    "透過 Docker Registry API 直接串流到 QEMU",
  ]'
  :answer="1"
  explanation="ContainerDisk 的工作方式：1. virt-launcher Pod 有一個 init container 執行 OCI 映像，將其中的 disk.img 複製到共享的 emptyDir；2. 主 QEMU 進程通過 file 後端存取這個臨時磁碟映像。整個流程在 Pod 生命週期內完成，Pod 刪除後 emptyDir 資料消失。"
/>

<QuizQuestion
  question="7. Hotplug Volume 功能要求 VM 滿足哪個先決條件？"
  :options='[
    "VM 必須使用 EFI 韌體",
    "VM 必須安裝 QEMU Guest Agent（qemu-guest-agent）",
    "StorageClass 必須支援 ReadWriteMany",
    "VM 必須已啟用 CPU Pinning",
  ]'
  :answer="1"
  explanation="Hotplug Volume（virtctl addvolume/removevolume）要求 VM 內部安裝並運行 QEMU Guest Agent（qemu-guest-agent）。Guest Agent 負責通知 Guest OS 新磁碟已連接（類似 udev 事件），使 OS 能識別並掛載新裝置。沒有 Guest Agent 時，熱插拔在硬體層面完成但 OS 可能不識別。"
/>

<QuizQuestion
  question="8. 執行 virtctl addvolume 後，新的磁碟在 VM 中的設備名稱（如 vdb）由什麼決定？"
  :options='[
    "virtctl addvolume 指令的 --device-name 參數",
    "VM YAML 中預先定義的磁碟名稱清單",
    "QEMU virtio-blk 或 virtio-scsi 控制器按順序分配，通常是第一個可用名稱",
    "CDI DataVolume 的名稱直接對應到設備名稱",
  ]'
  :answer="2"
  explanation="熱插拔磁碟的設備名稱由 QEMU 的磁碟控制器按 PCI/SCSI 地址順序分配。Hotplug 磁碟通常掛載到獨立的 virtio-scsi 控制器，設備名稱（如 sda、sdb）依接入順序決定。可以在 VM Guest 中使用 lsblk 確認實際裝置名稱。"
/>

<QuizQuestion
  question="9. 在 KubeVirt 中，VM 的記憶體 Balloon Device（virtio-balloon）的作用是什麼？"
  :options='[
    "動態調整 VM 的 CPU 資源分配",
    "允許 Hypervisor 動態回收 VM 部分記憶體，在主機記憶體不足時優化整體利用率",
    "Balloon Device 已棄用，建議使用 Memory Hotplug",
    "提供 VM 記憶體使用率監控的 Metrics",
  ]'
  :answer="1"
  explanation="virtio-balloon 是一種記憶體虛擬化技術，允許 Hypervisor（QEMU）動態調整 VM 實際使用的物理記憶體。當主機記憶體緊張時，Hypervisor 可指示 Balloon Driver 在 Guest 內「充氣」（balloon up），讓 Guest OS 釋放部分記憶體還給 Hypervisor，提升多 VM 環境的記憶體利用率。"
/>

<QuizQuestion
  question="10. KubeVirt 中的 Hook Sidecar 設計模式解決什麼問題？"
  :options='[
    "讓 VM 可以在不同 Namespace 之間遷移",
    "允許在不修改 KubeVirt 核心程式碼的情況下，透過外掛程式方式客製化 VMI XML 或生命週期 Hook",
    "提供 VM 的監控和日誌收集能力",
    "讓 virt-handler 可以並行處理更多 VMI",
  ]'
  :answer="1"
  explanation="Hook Sidecar 是 KubeVirt 的擴充機制，允許使用者在 virt-launcher Pod 中注入額外的 Sidecar Container，透過 gRPC 介面掛鉤 VMI 生命週期事件（如 onDefineDomain），動態修改 QEMU XML 設定，添加 KubeVirt 未原生支援的硬體設備或設定，無需修改 KubeVirt 原始碼。"
/>

<QuizQuestion
  question="11. 在 KubeVirt VM 中使用 HugePages 的主要效益是什麼？"
  :options='[
    "提升 VM 磁碟 I/O 效能",
    "減少 TLB（Translation Lookaside Buffer）未命中，降低記憶體存取延遲，提升記憶體密集型工作負載的效能",
    "允許 VM 使用超過節點實體記憶體的虛擬記憶體",
    "HugePages 讓 VM 可以使用 NUMA 架構",
  ]'
  :answer="1"
  explanation="HugePages（2Mi 或 1Gi 大頁面）通過減少 TLB 條目數量，降低 TLB Miss 率，從而減少記憶體存取延遲。對於記憶體密集型工作負載（資料庫、SAP HANA）效益顯著。KubeVirt 可配置 VM 的 QEMU Backend 使用 HugePages 分配 Guest 記憶體。"
/>

<QuizQuestion
  question="12. 在 VMI spec 中設定使用 1Gi HugePages 的正確欄位路徑是？"
  :options='[
    "spec.domain.memory.hugePages.pageSize: 1Gi",
    "spec.domain.memory.hugepages.pageSize: 1Gi",
    "spec.domain.resources.hugepages-1Gi: 4Gi",
    "spec.nodeSelector: hugepages.kubernetes.io/1Gi: 1",
  ]'
  :answer="1"
  explanation="KubeVirt VMI spec 中使用 HugePages 的設定是 spec.domain.memory.hugepages.pageSize（注意：hugepages 是小寫）。KubeVirt 自動對應到 Kubernetes 的 hugepages-1Gi/hugepages-2Mi 資源請求，並配置 QEMU 使用 HugePages 後端分配 Guest 記憶體。"
/>

<QuizQuestion
  question="13. 在 KubeVirt 中使用 GPU Passthrough，需要在節點和叢集設定哪些主要元件？"
  :options='[
    "只需在 VMI spec.domain.devices.gpus 中設定，Kubernetes 自動處理",
    "需要：IOMMU 啟用、VFIO 驅動、GPU 設備插件（如 NVIDIA GPU Operator 或 kubevirt-gpu-plugin），以及在 VMI spec 中宣告 GPU 資源",
    "只需啟用 NVIDIA Driver，在 VMI 中指定 GPU model 即可",
    "使用 SR-IOV Operator 即可完成 GPU Passthrough，不需要 VFIO",
  ]'
  :answer="1"
  explanation="GPU Passthrough 需要：1. 節點啟用 IOMMU（intel_iommu=on）；2. 載入 VFIO 驅動（vfio-pci），將 GPU 從 Host 驅動解除綁定；3. 安裝 GPU 設備插件（如 NVIDIA GPU Operator 的 vfio-pci mode）；4. 在 VMI spec.domain.devices.gpus 中宣告使用的 GPU 資源（deviceName: nvidia.com/GV100GL）。"
/>

<QuizQuestion
  question="14. virt-exportserver 和 VirtualMachineExport 資源的用途是什麼？"
  :options='[
    "用於 VM Live Migration 的資料傳輸通道",
    "提供 REST API 讓使用者可以匯出 VM 磁碟映像（PVC 資料）到外部系統",
    "將 VM 的設定匯出為 OVF/OVA 格式",
    "用於 KubeVirt 元件間的磁碟資料同步",
  ]'
  :answer="1"
  explanation="VirtualMachineExport CR 建立一個臨時的 virt-exportserver Pod 和 Service，提供 HTTP(S) 端點允許外部工具下載 VM 的 PVC 資料（支援 raw、gzip 格式，和 manifest 形式的 ConfigMap）。是 VM 備份和跨叢集遷移的基礎功能（KubeVirt >= v0.52）。"
/>

<QuizQuestion
  question="15. 在 StorageProfile 資源中，KubeVirt 和 CDI 使用它來解決什麼問題？"
  :options='[
    "定義不同 StorageClass 的計費策略",
    "自動為 DataVolume/PVC 選擇最適合的 Access Mode 和 Volume Mode，避免使用者錯誤設定",
    "管理儲存配額（Storage Quota）",
    "定義 Snapshot 策略和保留期限",
  ]'
  :answer="1"
  explanation="StorageProfile 是 CDI 的 CR，記錄每個 StorageClass 已知的最佳 Access Mode 和 Volume Mode 組合（如 ReadWriteOnce + Block 或 ReadWriteMany + Filesystem）。CDI 在建立 DataVolume 或 PVC 時，自動根據 StorageProfile 選擇最適合的設定，避免因設定錯誤導致 VM 無法啟動或 Migration 失敗。"
/>

<QuizQuestion
  question="16. DataVolumeSource pvc 和 DataVolumeSource snapshot 的主要區別是什麼？"
  :options='[
    "兩者都一樣，只是語法不同",
    "pvc source 從現有 PVC 複製完整資料；snapshot source 從 VolumeSnapshot 還原，通常由 CSI 快速 Clone 完成，效率更高",
    "snapshot source 需要 VM 停止，pvc source 可以在線上複製",
    "snapshot source 只支援 Block Volume，pvc source 支援 Filesystem",
  ]'
  :answer="1"
  explanation="DataVolume pvc source 需要完整複製來源 PVC 的資料；snapshot source 從 VolumeSnapshot 還原，CSI 驅動通常用 Copy-on-Write 快速 Clone，幾乎無需資料複製，速度遠快於完整資料複製，特別適合從黃金映像快速建立大量 VM。"
/>

<QuizQuestion
  question="17. 若要讓同一個磁碟映像同時供多個 VM 唯讀使用，應該使用哪種 Access Mode？"
  :options='["ReadWriteOnce（RWO）","ReadWriteMany（RWX）","ReadOnlyMany（ROX）","ReadWriteOncePod（RWOP）"]'
  :answer="2"
  explanation="ReadOnlyMany（ROX）允許多個節點同時以唯讀方式掛載同一個 PVC，適合共享的基礎 OS 映像或 ISO 映像。ReadWriteMany（RWX）允許多個節點讀寫（需要 NFS 或 Ceph RBD with multi-attach），適合共享可寫磁碟。ReadWriteOnce（RWO）只允許一個節點掛載（最常見）。"
/>

<QuizQuestion
  question="18. CDI Smart Clone 使用哪種機制來加速 PVC 複製？"
  :options='[
    "將 PVC 資料壓縮後透過網路快速傳輸",
    "使用 CSI VolumeSnapshot 快速 Clone，利用儲存後端的 Copy-on-Write 機制，幾乎零資料複製",
    "在後端儲存系統直接複製 Block Device，繞過 Kubernetes API",
    "Smart Clone 使用 DRBD 同步複製技術",
  ]'
  :answer="1"
  explanation="CDI Smart Clone 的工作原理：1. 對來源 PVC 建立 VolumeSnapshot；2. 從 VolumeSnapshot 建立新的 PVC。現代 CSI 驅動（Ceph RBD、NetApp、HPE 等）支援 Clone from Snapshot，利用 Copy-on-Write 機制幾乎無需複製資料，速度遠快於 Host Assisted Clone（需要實際讀取並傳輸所有資料）。"
/>

<QuizQuestion
  question="19. 在 VMI spec 中，disk 的 bus 類型設為 virtio 與 sata 相比，哪個效能更好且為何？"
  :options='[
    "sata 效能更好，因為是業界標準協議，驅動最成熟",
    "virtio 效能更好，因為是為虛擬化設計的半虛擬化協議，Host-Guest 通訊開銷更低",
    "兩者效能相同，只是設備名稱不同（vda vs sda）",
    "virtio 僅在 Linux Guest 上效能更好，Windows Guest 必須使用 sata",
  ]'
  :answer="1"
  explanation="virtio-blk 和 virtio-scsi 是為虛擬化環境設計的半虛擬化（paravirtualization）協議，Guest OS 和 Hypervisor 都知道在虛擬化環境中運行，I/O 路徑更短，傳輸開銷更低。sata/ide 使用完整硬體模擬（Full Emulation），需要模擬完整的實體控制器行為，開銷較高。Windows 客戶端需要安裝 virtio-win 驅動包。"
/>

<QuizQuestion
  question="20. 在 VM spec 中，哪個欄位允許從 ConfigMap 或 Secret 資源注入 Cloud-Init 配置？"
  :options='[
    "spec.volumes[].cloudInitNoCloud.userData 直接內嵌 YAML",
    "spec.volumes[].cloudInitConfigDrive.secretRef 和 spec.volumes[].cloudInitConfigDrive.networkDataSecretRef",
    "spec.volumes[].cloudInitNoCloud.userDataSecretRef（引用 Secret 的 userdata 欄位）",
    "spec.domain.devices.cloudInit.configMapRef",
  ]'
  :answer="2"
  explanation="在 VMI volumes 中，cloudInitNoCloud（或 cloudInitConfigDrive）支援以下方式注入 cloud-init 資料：1. userData 直接內嵌（Base64 或文字）；2. userDataSecretRef 引用 Secret（Secret 需要有 userdata 欄位）；3. networkDataSecretRef 引用網路配置 Secret。Secret 方式更安全，避免在 VM YAML 中暴露敏感設定。"
/>

<QuizQuestion
  question="21. Live Migration 過程中，VM 的 PVC 需要支援哪種 Access Mode？"
  :options='[
    "只要 ReadWriteOnce（RWO）即可，Migration 自動處理",
    "需要 ReadWriteMany（RWX），允許來源和目標節點同時掛載同一 PVC",
    "Migration 期間 PVC 不需要同時掛載，所以 RWO 即可",
    "只支援使用 containerDisk 的 VM，PVC 不支援 Migration",
  ]'
  :answer="1"
  explanation="Live Migration 時，來源節點和目標節點的 virt-launcher 需要同時存取同一個 PVC（來源讀、目標寫）。若 PVC 使用 ReadWriteOnce（RWO），只允許一個節點掛載，Migration 會失敗。PVC 必須使用 ReadWriteMany（RWX）存取模式（如 NFS、CephFS、Ceph RBD with multi-attach）。"
/>

<QuizQuestion
  question="22. CDI 的 DataVolumeTemplateBound Feature Gate 的作用是什麼？"
  :options='[
    "允許 DataVolumeTemplates 在 VM 建立前預先填充磁碟",
    "確保 VM 等待所有 dataVolumeTemplates 完成後才啟動（WaitForFirstConsumer 語義）",
    "允許多個 VM 共享同一個 DataVolumeTemplate",
    "功能 Gate 不存在，CDI 自動處理 DataVolume 綁定",
  ]'
  :answer="1"
  explanation="當 VM 使用 dataVolumeTemplates 且 StorageClass 的 volumeBindingMode 為 WaitForFirstConsumer 時，CDI 和 KubeVirt 協調確保：1. PVC 先被建立但等待綁定；2. 等 VM 排程到特定節點後，告知 CDI 在該節點可用的 StorageClass 填充 DataVolume；3. DataVolume Succeeded 後，VMI 才真正啟動。"
/>

<QuizQuestion
  question="23. 在 KubeVirt 中，如何讓 VM 使用節點本地儲存（Local Storage）同時支援 Live Migration？"
  :options='[
    "本地儲存（Local Storage）本質上不支援 Live Migration，必須改用網路儲存",
    "使用 CDI 的 Hotplug 功能在 Migration 前先掛載網路儲存，Migration 後卸除本地磁碟",
    "使用 ReadWriteOncePod（RWOP）Access Mode 即可支援",
    "本地儲存的 VM 可以 Migration，只是 Migration 後 PVC 會在目標節點重新建立（資料不遷移）",
  ]'
  :answer="0"
  explanation="本地儲存（如 Kubernetes Local Persistent Volume）的 PVC 是節點綁定的，無法跨節點掛載，因此使用本地儲存的 VM 確實不支援 Live Migration。生產環境若需要 Migration，需使用支援 ReadWriteMany 的網路儲存（NFS、CephFS、Ceph RBD、iSCSI multi-path 等）。"
/>

<QuizQuestion
  question="24. 若要讓 DataVolume 從受密碼保護的 HTTP URL 下載映像，需要怎麼設定？"
  :options='[
    "直接在 URL 中嵌入 http://user:password@server/image.qcow2",
    "在 DataVolume spec.source.http 中指定 secretRef，對應 Secret 包含 accessKeyId 和 secretKey",
    "只能使用無密碼的公開 URL",
    "使用 DataVolume spec.source.s3 而非 http 來支援認證",
  ]'
  :answer="1"
  explanation="DataVolume source.http 支援透過 secretRef 引用 Secret 來提供 HTTP 認證。Secret 需要包含 accessKeyId（使用者名稱）和 secretKey（密碼）欄位，CDI importer Pod 將這些認證資訊作為環境變數，在下載映像時進行 HTTP Basic Authentication。"
/>

<QuizQuestion
  question="25. VMI spec.domain.resources.requests 和 spec.domain.resources.limits 的設定對 Kubernetes Pod QoS 有什麼影響？"
  :options='[
    "KubeVirt VM 不受 Kubernetes QoS 影響，有獨立的資源管理機制",
    "若 requests == limits，virt-launcher Pod 為 Guaranteed QoS，可提高穩定性和 CPU Manager 相容性",
    "KubeVirt 強制所有 virt-launcher Pod 為 BestEffort QoS",
    "只有使用 Instancetype 才能設定 QoS 等級",
  ]'
  :answer="1"
  explanation="KubeVirt virt-launcher Pod 的 QoS 等級由 VMI resources.requests 和 resources.limits 決定，遵循標準 Kubernetes QoS 規則：requests == limits → Guaranteed（最高優先級，不被驅逐）；只有 requests → Burstable；都沒有 → BestEffort（最容易被驅逐）。Guaranteed QoS 也是使用 CPU Manager（dedicatedCpuPlacement）的前提。"
/>

<QuizQuestion
  question="26. 在 KubeVirt 中，Emulated TPM（vTPM）的用途是什麼？"
  :options='[
    "提升 VM 的效能，減少記憶體延遲",
    "模擬 TPM 2.0 晶片，讓 Windows 11 等需要 TPM 的 OS 可以安裝和啟動",
    "提供 VM 間的安全通訊加密通道",
    "vTPM 是實體 TPM 的替代品，提供等同的安全等級",
  ]'
  :answer="1"
  explanation="Emulated TPM（vTPM）使用 swtpm 軟體模擬 TPM 2.0 晶片，讓 VM Guest 看到標準 TPM 設備。這對 Windows 11（強制要求 TPM 2.0）、BitLocker 加密、某些安全啟動需求非常重要。vTPM 的狀態持久化存在 Secret 中，VM 重啟後可恢復。安全等級低於實體 TPM（因為 swtpm 是軟體模擬）。"
/>

<QuizQuestion
  question="27. 在 KubeVirt 中設定 NUMA 拓撲（numaTopologyPolicy）的主要目的是什麼？"
  :options='[
    "讓 VM 可以跨多個節點分散記憶體",
    "確保 VM 的 vCPU 和記憶體分配在相同的 NUMA 節點，最大化記憶體存取效能，降低遠端記憶體存取延遲",
    "NUMA 設定允許 VM 使用比節點更多的記憶體（記憶體超售）",
    "讓 KubeVirt 自動平衡不同 NUMA 節點上的 VM 分佈",
  ]'
  :answer="1"
  explanation="NUMA（Non-Uniform Memory Access）拓撲確保 VM 的 vCPU 和分配的記憶體位於相同的 NUMA 節點。跨 NUMA 節點的記憶體存取延遲顯著高於本地存取。numaTopologyPolicy 讓 KubeVirt 告知 Kubernetes Topology Manager，以 NUMA 感知方式分配 CPU 和記憶體資源，特別適合延遲敏感的 HPC 和資料庫工作負載。"
/>

<QuizQuestion
  question="28. 以下哪個欄位讓 VMI 磁碟以 Block Device 模式掛載（而非 Filesystem 模式）？"
  :options='[
    "spec.domain.devices.disks[].disk.blockDevice: true",
    "spec.volumes[].persistentVolumeClaim.hotpluggable: true",
    "spec.domain.devices.disks[].disk.io: native（Block Device 需此設定）",
    "spec.volumes[].persistentVolumeClaim.claimName 加上 PVC volumeMode: Block",
  ]'
  :answer="3"
  explanation="VMI 磁碟以 Block Device 模式運作，需要 PVC 的 volumeMode: Block。KubeVirt 自動檢測 PVC 的 volumeMode，若為 Block，則將磁碟以 Block Device（裸設備）方式提供給 QEMU，繞過 Filesystem Layer，可降低 I/O 延遲。通常與 io: native 搭配使用進一步提升 I/O 效能。"
/>

<QuizQuestion
  question="29. CDI Preallocation 功能（spec.preallocation: true in DataVolume）的作用是什麼？"
  :options='[
    "預先下載磁碟映像到節點快取，加速 VM 啟動",
    "在填充 DataVolume 時預先分配完整的磁碟空間，避免 thin provisioning 導致的延遲",
    "預先建立 VolumeSnapshot 以加速 Clone 操作",
    "預先分配 VM 的 CPU 和記憶體資源",
  ]'
  :answer="1"
  explanation="CDI preallocation: true 讓 importer Pod 在建立磁碟映像時預先分配完整的磁碟空間（fallocate），確保 VM 執行時不會因為後端儲存空間不足而發生 I/O 錯誤。代價是需要更長的填充時間和立即消耗完整的儲存空間。適合生產環境中對穩定性要求高的場景。"
/>

<QuizQuestion
  question="30. 在 KubeVirt 中，VIRTIOFS（virtio-fs）允許 VM 掛載什麼類型的資源？"
  :options='[
    "允許 VM 直接掛載 S3 物件儲存為本地目錄",
    "允許 VM 掛載 Host（virt-launcher Pod）的目錄，透過共享記憶體（DAX）高效存取",
    "VIRTIOFS 是 virtio-scsi 的替代協議，用於提升磁碟效能",
    "允許多個 VM 共享同一個目錄，實現 VM 間的快速資料交換",
  ]'
  :answer="1"
  explanation="VIRTIOFS（virtio-fs）是一個共享檔案系統協議，允許 VM Guest 掛載 Host 端（即 virt-launcher Pod）的目錄。透過 DAX（Direct Access）機制，Guest 可以透過共享記憶體直接存取 Host 的 Page Cache，避免資料複製，提供接近原生的檔案系統效能。適合 VM 和 Host 間需要快速共享資料的場景。"
/>
