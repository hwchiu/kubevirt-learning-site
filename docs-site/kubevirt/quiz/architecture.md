---
layout: doc
title: KubeVirt — 🏗️ 基礎架構測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# 🏗️ 基礎架構測驗

<QuizQuestion
  question="1. KubeVirt 的設計準則「KubeVirt Razor」的核心精神是什麼？"
  :options='[
    "如果某個功能對 Pod 也有用，就不應該只為 VM 實作它",
    "所有 VM 功能都必須獨立於 Kubernetes 之外自行實作",
    "KubeVirt 應該取代 Kubernetes 的排程器來管理 VM",
    "VM 必須使用與 Pod 完全隔離的專屬網路和儲存層",
  ]'
  :answer="0"
  explanation="KubeVirt Razor 原則：如果某個功能對 Pod 也有用，就不應該只為 VM 實作它。這讓 KubeVirt 盡可能重用 Kubernetes 現有基礎設施：網路使用 CNI/Multus、儲存使用 PVC/StorageClass、排程使用 kube-scheduler、安全模型與 Pod 保持一致，讓 KubeVirt 完全融入 Kubernetes 生態系統而非另起爐灶。"
/>

<QuizQuestion
  question="2. virt-handler 在 Kubernetes 叢集中以哪種部署型態運行？"
  :options='[
    "StatefulSet（每節點一個固定 Pod）",
    "Deployment（≥2 副本，高可用）",
    "DaemonSet（每節點一個）",
    "Job（按需執行後終止）",
  ]'
  :answer="2"
  explanation="virt-handler 以 DaemonSet 形式部署，確保叢集中每個節點上都有一個實例。它是節點級別的代理程序（節點代理），負責同步 VMI 狀態、呼叫 virt-launcher、管理網路/儲存，並具有 HostPID 與 HostNetwork 特殊宿主機存取權限。"
/>

<QuizQuestion
  question="3. VMI 正常關機（Guest OS 執行乾淨關機）後，會進入哪個 Phase？"
  :options='[
    "Stopped",
    "Halted",
    "Succeeded",
    "Terminated",
  ]'
  :answer="2"
  explanation="根據 staging/src/kubevirt.io/api/core/v1/types.go 的定義，VMI 正常關機後進入 Succeeded Phase，代表 Guest OS 執行了乾淨關機（ACPI shutdown 或 virtctl stop）。若 VM 的 RunStrategy=Always，virt-controller 在偵測到 VMI 進入 Succeeded 後，會自動重新建立 VMI。"
/>

<QuizQuestion
  question="4. 在 KubeVirt 的 CRD 中，哪個資源代表「正在執行的 VM 實例」，且關機後會被刪除？"
  :options='[
    "VirtualMachineInstance (VMI)：暫態物件，代表執行中的 VM",
    "VirtualMachine (VM)：持久存在，停止後資料保留",
    "VirtualMachinePool：高階 VM 池管理",
    "VirtualMachineInstanceReplicaSet：VM 水平擴展",
  ]'
  :answer="0"
  explanation="VirtualMachineInstance (VMI) 是暫態物件，代表正在執行的 VM。關機後 VMI 物件被刪除，但 VirtualMachine (VM) 物件仍持久存在。VMI 包含 spec.nodeName（被調度到哪個節點）、IP 位址等執行時資訊。VM 與 VMI 的關係類似 Deployment 與 ReplicaSet。"
/>

<QuizQuestion
  question="5. virt-launcher Pod 內部執行哪兩個核心程式來實際運行 VM？"
  :options='[
    "containerd 與 runc",
    "Docker 與 KVM 模組",
    "libvirtd 與 QEMU",
    "virsh 與 systemd-nspawn",
  ]'
  :answer="2"
  explanation="每個 VMI 對應一個 virt-launcher Pod，內部執行 libvirtd（libvirt 守護程序）與 QEMU（快速模擬器）。virt-handler 透過 Unix Socket 呼叫 virt-launcher，後者透過 pkg/virt-launcher/virtwrap/manager.go 中的 SyncVMI() 將 VMI spec 轉換為 libvirt domain XML，再透過 libvirt API 呼叫 virDomainCreate() 啟動 QEMU 程序。"
/>

<QuizQuestion
  question="6. 在建立 VM 的資料流中，哪個元件負責建立 VirtualMachineInstance (VMI) CR？"
  :options='[
    "virt-controller（VM 控制器，pkg/virt-controller/watch/vm/vm.go）",
    "virt-api（Admission Webhook 處理後）",
    "virt-handler（節點代理）",
    "virt-operator（安裝管理器）",
  ]'
  :answer="0"
  explanation="當 virt-api 將 VirtualMachine CR 寫入 etcd 後，virt-controller 的 VM 控制器（pkg/virt-controller/watch/vm/vm.go 中的 sync() 函式）偵測到 VM 物件，計算期望狀態（running=true → 需要 VMI）後建立對應的 VMI CR。接著 VMI 控制器（vmi/vmi.go）再建立 virt-launcher Pod。"
/>

<QuizQuestion
  question="7. RunStrategy 設定為 Always 時，virt-controller 的行為是什麼？"
  :options='[
    "等待使用者手動執行 virtctl start 才啟動 VM",
    "僅在 VMI 因錯誤失敗時才重啟，正常關機後不重啟",
    "只啟動一次，停止後永遠不再重啟",
    "VMI 停止後（無論原因）自動重新建立 VMI",
  ]'
  :answer="3"
  explanation="RunStrategy=Always 表示不論 VMI 因何原因停止（正常關機或異常崩潰），virt-controller 都會自動重新建立 VMI。對比其他策略：RerunOnFailure 僅在失敗時重啟；Manual 由使用者手動控制 start/stop；Halted 不自動啟動；Once 只啟動一次；WaitAsReceiver 等待作為 Migration 接收方。"
/>

<QuizQuestion
  question="8. virt-api、virt-controller 與 virt-operator 各自以哪種型態部署，最少需要幾個副本以確保高可用？"
  :options='[
    "三者皆為 DaemonSet，每節點一個",
    "三者皆為 Deployment，≥1 副本",
    "三者皆為 Deployment，≥2 副本",
    "virt-api 為 StatefulSet，其他為 Deployment，≥2 副本",
  ]'
  :answer="2"
  explanation="virt-api、virt-controller、virt-operator 三者皆以 Deployment 形式部署，各需要 ≥2 副本以實現高可用。virt-controller 額外使用 Kubernetes Lease 進行 Leader Election，確保同一時間只有一個主動副本執行協調邏輯。只有 virt-handler 是 DaemonSet（每節點一個）。"
/>

<QuizQuestion
  question="9. KubeVirt 採用「協作 (Choreography)」而非「編排 (Orchestration)」模式，各元件透過什麼共享狀態進行協調？"
  :options='[
    "KubeVirt CR（安裝設定物件）",
    "virt-controller 的 ConfigMap",
    "VMI CR（VirtualMachineInstance 物件）",
    "virt-handler 的 DaemonSet 狀態",
  ]'
  :answer="2"
  explanation="KubeVirt 使用協作模式：每個元件各自觀察狀態並採取行動，沒有中央指揮官，而是透過 VMI CR 作為共享狀態。virt-controller 建立 VMI 和 Pod，virt-handler 觀察 VMI.spec.nodeName 變化後在目標節點介入，類似 Kubernetes 本身的 level-triggered 協調機制，讓系統更具彈性與可擴展性。"
/>

<QuizQuestion
  question="10. virt-api 的 Mutating Webhook 在處理 VM 建立時，預設補齊的 terminationGracePeriodSeconds 值為多少秒？"
  :options='[
    "30 秒",
    "60 秒",
    "120 秒",
    "180 秒",
  ]'
  :answer="3"
  explanation="virt-api 的 Mutating Webhook（mutators/vmi-mutator.go）在 VM 建立時會補齊預設值，其中 terminationGracePeriodSeconds 預設為 180 秒。這個值也決定了 VM 刪除時 virt-handler 等待 QEMU 優雅關機的 grace period——超過 180 秒後，virt-launcher 會強制終止 QEMU 程序。"
/>

<QuizQuestion
  question="11. virt-handler 在節點上運行時，具有哪些特殊的宿主機存取權限？"
  :options='[
    "HostPID 與 HostNetwork",
    "HostIPC 與 HostPID",
    "HostNetwork 與 HostIPC",
    "僅 HostNetwork，不需要其他特殊權限",
  ]'
  :answer="0"
  explanation="virt-handler 以 DaemonSet 形式部署，具有 HostPID（存取宿主機 PID 命名空間）與 HostNetwork（使用宿主機網路命名空間）權限。這些權限讓 virt-handler 能夠在 virt-launcher Pod 的 network namespace 中執行 Phase 1 網路配置，收集 CNI 分配的 IP/MAC/路由資訊並建立 bridge/veth pair 基礎設施。"
/>

<QuizQuestion
  question="12. UIDTrackingControllerExpectations 機制的主要目的是什麼？"
  :options='[
    "追蹤 VMI 的 UUID 以便在叢集中快速查詢定位",
    "管理 virt-launcher Pod 的最大存活時間（TTL）",
    "記錄每次 VM Phase 轉換的時間戳以供 SLA 監控",
    "防止控制器在 Informer 尚未確認之前重複建立相同的 Pod",
  ]'
  :answer="3"
  explanation="UIDTrackingControllerExpectations（pkg/controller/expectations.go）是防止競態條件的關鍵機制。控制器建立 Pod 前先記錄預期的 UID，Informer 收到 Add 事件後才標記已觀察到，只有當所有 expectations 都已滿足時才繼續執行建立邏輯。Expectations 有 TTL，避免因事件遺失而永久阻塞。"
/>

<QuizQuestion
  question="13. KubeVirt 的 CA 憑證有效期限為多長？各元件（virt-api、virt-handler 等）的憑證有效期限又是多長？"
  :options='[
    "CA 30 天，元件憑證 7 天",
    "CA 7 天，元件憑證 24 小時",
    "CA 365 天，元件憑證 30 天",
    "CA 24 小時，元件憑證 1 小時",
  ]'
  :answer="1"
  explanation="根據 pkg/certificates/certificates.go，KubeVirt 刻意使用極短的憑證有效期：CA 有效期 7 天（time.Hour*24*7），元件憑證有效期 24 小時（time.Hour*24）。CA 的 Common Name 為 &quot;kubevirt.io&quot;，元件憑證 SAN 格式為 {name}.{namespace}.pod.cluster.local。virt-operator 負責在憑證到期前自動輪替，採用頻繁輪替策略降低憑證洩漏風險。"
/>

<QuizQuestion
  question="14. virt-controller 的 Leader Election 中，Lease 的有效期 (DefaultLeaseDuration) 預設為多少秒？"
  :options='[
    "5 秒",
    "10 秒",
    "15 秒",
    "30 秒",
  ]'
  :answer="2"
  explanation="根據 pkg/virt-controller/leaderelectionconfig/config.go，Leader Election 的預設配置為：DefaultLeaseDuration=15 秒（Lease 有效期）、DefaultRenewDeadline=10 秒（續約截止時間）、DefaultRetryPeriod=2 秒（重試間隔），ResourceLock 使用 LeasesResourceLock。virt-controller 和 virt-operator 都使用此機制確保同一時間只有一個主動副本。"
/>

<QuizQuestion
  question="15. KubeVirt 控制器使用的 DefaultTypedControllerRateLimiter 令牌桶算法，預設每秒可處理多少個操作？突發量（burst）為多少？"
  :options='[
    "每秒 10 個操作，突發量 100",
    "每秒 5 個操作，突發量 50",
    "每秒 20 個操作，突發量 200",
    "每秒 100 個操作，突發量 1000",
  ]'
  :answer="0"
  explanation="KubeVirt 使用 Kubernetes 內建的 DefaultTypedControllerRateLimiter，包含兩層機制：指數退避（基礎延遲 5ms，最大延遲 1000s）以及整體速率限制（令牌桶算法，每秒 10 個操作，突發量 100）。同一個 key 在佇列中只出現一次，後續事件自動合併去重複。當大量 VMI 同時變更狀態時，此速率限制可能成為瓶頸。"
/>

<QuizQuestion
  question="16. 在 KubeVirt 的兩階段網路配置中，Phase 1 由哪個元件執行？網路配置快取存放在哪個路徑格式下？"
  :options='[
    "virt-launcher 執行 Phase 1，快取於 /etc/kubevirt/network/",
    "virt-handler 執行 Phase 1，快取於 /var/run/kubevirt-private/vif-cache-xxx.json",
    "virt-controller 執行 Phase 1，快取於 /run/kubevirt/vif/",
    "virt-api 執行 Phase 1，快取於 /var/lib/kubevirt/network/",
  ]'
  :answer="1"
  explanation="Phase 1（Privileged）由 virt-handler 在 virt-launcher Pod 的 network namespace 中執行，負責收集 CNI 分配的 IP/MAC/路由資訊，建立 bridge/veth pair 基礎設施，並將網路配置快取到 /var/run/kubevirt-private/vif-cache-xxx.json。Phase 2（Unprivileged）由 virt-launcher 讀取快取，產生 libvirt domain XML 的網路部分，並在需要時啟動 DHCP server。"
/>

<QuizQuestion
  question="17. virt-operator 的 Install Strategy 使用哪種 Kubernetes 資源類型來儲存各版本的完整部署資訊？"
  :options='[
    "Secret（加密儲存敏感配置）",
    "CustomResourceDefinition（擴展 API 定義）",
    "Deployment Annotation（版本標記）",
    "ConfigMap（儲存各版本所有需要部署的資源定義）",
  ]'
  :answer="3"
  explanation="根據 pkg/virt-operator/resource/generate/install/strategy.go，每個 KubeVirt 版本對應一個 ConfigMap，包含該版本所有需要部署的 Kubernetes 資源定義（ServiceAccount、ClusterRole、CRD、Service、Deployment、DaemonSet、ValidatingWebhookConfiguration、MutatingWebhookConfiguration、APIService 等）。virt-operator 使用 atomic.Value 無鎖快取 Strategy 以避免每次 reconcile 都反序列化。"
/>

<QuizQuestion
  question="18. 記憶體熱插拔中，標準記憶體的對齊要求常數 HotplugBlockAlignmentBytes 的值是多少？"
  :options='[
    "2 MiB (0x200000)",
    "4 KiB (0x1000)",
    "1 MiB (0x100000)",
    "4 MiB (0x400000)",
  ]'
  :answer="0"
  explanation="根據 pkg/liveupdate/memory/memory.go，HotplugBlockAlignmentBytes=0x200000（2 MiB）。1G Hugepages 的對齊要求更嚴格：Hotplug1GHugePagesBlockAlignmentBytes=0x40000000（1 GiB）。最低 Guest 記憶體需求（requiredMinGuestMemory）也是 0x40000000（1 GiB）。不符合對齊要求的請求會被 ValidateLiveUpdateMemory() 拒絕。記憶體以 DIMM 裝置形式熱插入 libvirt domain。"
/>

<QuizQuestion
  question="19. VMI 在什麼情況下會進入 WaitingForSync Phase？"
  :options='[
    "等待 PVC 綁定完成，儲存尚未就緒",
    "作為 Live Migration 接收端，等待來源端資料同步完成",
    "與 virt-handler 通訊中斷，無法確認當前狀態",
    "DataVolume 資料準備中，尚未達到 Ready 狀態",
  ]'
  :answer="1"
  explanation="WaitingForSync Phase 是 KubeVirt Live Migration 特有的狀態：當 VMI 作為 Migration 目標（接收端）時，它會進入 WaitingForSync，等待來源端的記憶體/儲存資料同步完成。同步完成後，VMI 切換為 Running 成為活躍端。若遷移失敗或來源端取消，則轉換為 Failed。virt-handler 通訊中斷則進入 Unknown Phase。"
/>

<QuizQuestion
  question="20. VirtualMachineInstancetype 與 VirtualMachineClusterInstancetype 的主要差異是什麼？"
  :options='[
    "Instancetype 管理 CPU 規格，ClusterInstancetype 管理記憶體規格",
    "Instancetype 用於開發環境，ClusterInstancetype 用於生產環境",
    "Instancetype 是 namespace-scoped，ClusterInstancetype 是 cluster-scoped",
    "兩者功能完全相同，只是命名長度不同",
  ]'
  :answer="2"
  explanation="VirtualMachineInstancetype 是 namespace-scoped 的 CRD，僅在特定命名空間內有效；VirtualMachineClusterInstancetype 則是 cluster-scoped，可供整個叢集共用。兩者都用於定義 CPU/記憶體規格模板，搭配 VirtualMachinePreference（設備偏好配置）使用，讓多個 VM 可以共享標準化的硬體配置，類似雲端供應商的機器規格（如 m5.large）概念。"
/>

<QuizQuestion
  question="21. VM 的 PrintableStatus（kubectl get vm 所見狀態）中，哪個狀態表示 VM 正在等待 DataVolume 準備完成？"
  :options='[
    "Initializing（初始化中）",
    "WaitingForVolumeBinding（等待 PVC 綁定）",
    "Starting（正在啟動中）",
    "Provisioning（等待 DataVolume 準備）",
  ]'
  :answer="3"
  explanation="VM 的 PrintableStatus 中，Provisioning 表示等待 DataVolume 準備完成，DataVolume 是 CDI（Containerized Data Importer）管理的資料卷物件。WaitingForVolumeBinding 則是等待 PVC 綁定，兩者不同。其他重要狀態：Stopped（VM 已停止，VMI 不存在）、CrashLoopBackOff（持續崩潰）、Migrating（Live Migration 中）、DataVolumeError（DataVolume 錯誤）、ErrorUnschedulable（找不到合適節點）。"
/>

<QuizQuestion
  question="22. KubeVirt 整體安裝與設定的 Custom Resource 的 Kind 名稱是什麼？"
  :options='[
    "KubeVirtConfig",
    "KubeVirt",
    "KubeVirtOperator",
    "VirtualizationCluster",
  ]'
  :answer="1"
  explanation="KubeVirt 安裝與設定的 CR Kind 名稱就是 KubeVirt，定義在 staging/src/kubevirt.io/api/core/v1/ 下。virt-operator 監控這個 CR 來管理所有 KubeVirt 元件的安裝、升級與配置。升級時，使用者更新 KubeVirt CR 的 spec.imageTag，virt-operator 偵測到版本變更後執行滾動更新，完成後將 CR status.phase 更新為 Deployed。"
/>

<QuizQuestion
  question="23. virt-handler 透過什麼通訊方式與 virt-launcher 互動來管理 libvirt domain？"
  :options='[
    "Unix Domain Socket（本地 Socket 通訊，搭配 TLS）",
    "HTTP REST API（透過 Pod ClusterIP）",
    "gRPC over TCP（透過 Kubernetes Service）",
    "共享記憶體（mmap）",
  ]'
  :answer="0"
  explanation="virt-handler 透過 Unix Domain Socket 與 virt-launcher 通訊，並搭配 TLS 加密（Unix Socket + TLS）。這種本地 Socket 通訊不需要透過網路，延遲低且安全。virt-handler 透過這個 Socket 將 VMI spec 傳遞給 virt-launcher，後者再呼叫 libvirtd API 管理 QEMU domain（定義 domain、啟動、停止、遷移等操作）。"
/>

<QuizQuestion
  question="24. VMI Phase 常數（VmPhaseUnset、Pending、Running 等）的型別定義位於 KubeVirt 原始碼的哪個檔案路徑？"
  :options='[
    "staging/src/kubevirt.io/api/core/v1/types.go",
    "pkg/virt-controller/watch/vmi/vmi.go",
    "pkg/virt-handler/controller.go",
    "cmd/virt-api/main.go",
  ]'
  :answer="0"
  explanation="VMI Phase 的 const 定義位於 staging/src/kubevirt.io/api/core/v1/types.go，包含 VmPhaseUnset、Pending、Scheduling、Scheduled、Running、Succeeded、Failed、WaitingForSync、Unknown 等九個 Phase。這個路徑遵循 Kubernetes API staging 目錄慣例，是所有 KubeVirt CRD 型別定義（VM、VMI、KubeVirt CR 等）的集中位置。"
/>

<QuizQuestion
  question="25. 執行 kubectl delete vm 後，virt-handler 預設等待 QEMU 優雅關機的 grace period 為多少秒？超時後如何處理？"
  :options='[
    "30 秒，超時後發送 SIGTERM 給 QEMU",
    "60 秒，超時後直接刪除 virt-launcher Pod",
    "120 秒，超時後重試發送 ACPI 關機訊號",
    "180 秒，超時後強制終止 QEMU 程序",
  ]'
  :answer="3"
  explanation="刪除 VM 時，virt-handler 偵測到 VMI 的 DeletionTimestamp 後，呼叫 virt-launcher 向 QEMU 發送 ACPI 關機訊號，並等待 VM 優雅關機，grace period 為 180 秒。若超時，virt-launcher 會強制終止 QEMU 程序。這個 180 秒與 Mutating Webhook 補齊的 terminationGracePeriodSeconds 預設值一致，確保 VM 有足夠時間執行資料刷新等清理工作。"
/>

<QuizQuestion
  question="26. 在 KubeVirt 建立 VM 的資料流中，哪個元件負責選定 virt-launcher Pod 的執行節點？"
  :options='[
    "virt-controller（VMI 控制器，依 nodeSelector 選節點）",
    "kube-scheduler（Kubernetes 原生排程器）",
    "virt-handler（節點代理，主動爭搶）",
    "kubelet（節點 Agent，本地決策）",
  ]'
  :answer="1"
  explanation="virt-controller 的 VMI 控制器建立 virt-launcher Pod 後，由 Kubernetes 原生的 kube-scheduler 負責選定節點並綁定 Pod。Pod 被調度到節點後，virt-controller 將 VMI.spec.nodeName 更新為選定節點名稱，virt-handler 偵測到 nodeName 改變（watch 事件觸發）後才開始在該節點上執行 VMI 配置工作。KubeVirt 直接重用 kube-scheduler，不另起爐灶。"
/>

<QuizQuestion
  question="27. VMI 狀態更新的完整鏈路，從底層事件到使用者可見狀態，正確的順序是哪一個？"
  :options='[
    "virt-handler 更新 → virt-launcher 通知 → API Server → virt-controller 同步",
    "virt-controller 觸發 → API Server 記錄 → virt-handler 執行 → virt-launcher 回報",
    "API Server watch → virt-controller 協調 → virt-handler 同步 → virt-launcher 執行",
    "QEMU 域事件 → virt-launcher 偵測 → virt-handler 更新 API Server → virt-controller 更新 VM",
  ]'
  :answer="3"
  explanation="VMI 狀態更新的完整鏈路為：QEMU 域事件（如 domain 狀態改變）→ virt-launcher 監聽 libvirt 事件，偵測到 domain 狀態改變 → virt-handler 接收 launcher 通知，更新 VMI.Status 到 Kubernetes API Server → virt-controller watch 到 VMI 狀態改變，更新 VM.Status → 使用者透過 kubectl get vm 看到最新的 PrintableStatus。"
/>

<QuizQuestion
  question="28. virt-operator 的 Install Strategy 快取中，用於判斷快取是否仍有效的 key 格式是什麼？"
  :options='[
    "{namespace}/{version} 格式（命名空間加版本號）",
    "{version}-{resourceVersion} 格式（版本號加 ConfigMap 的 resourceVersion）",
    "{name}-{imageTag} 格式（元件名稱加映像檔標籤）",
    "{version}/{timestamp} 格式（版本號加時間戳）",
  ]'
  :answer="1"
  explanation="根據 pkg/virt-operator/kubevirt.go，Install Strategy 快取 key 的格式為 {version}-{resourceVersion}，常數定義為 installStrategyKeyTemplate = &quot;%s-%d&quot;，以版本號（string）加上 ConfigMap 的 resourceVersion（整數）組成。virt-operator 使用 atomic.Value 實現無鎖的執行緒安全快取，快取命中時直接回傳已解析的 Strategy 物件，避免反序列化開銷。"
/>

<QuizQuestion
  question="29. virt-controller 的 Leader Election 中，預設使用的 Lease 資源名稱（DefaultLeaseName）是什麼？"
  :options='[
    "kubevirt-controller",
    "virt-controller-leader",
    "virt-controller",
    "kubevirt-leader",
  ]'
  :answer="2"
  explanation="根據 pkg/virt-controller/leaderelectionconfig/config.go，DefaultLeaseName = &quot;virt-controller&quot;。Leader Election 使用 Kubernetes Lease 資源（LeasesResourceLock），搭配 DefaultLeaseDuration=15 秒、DefaultRenewDeadline=10 秒、DefaultRetryPeriod=2 秒的設定。virt-operator 也有類似的 Leader Election 機制，確保多副本部署下只有一個主動副本執行協調邏輯。"
/>

<QuizQuestion
  question="30. 在 KubeVirt 的 CPUDomainConfigurator 中，哪個欄位用來判斷當前平台是否支援 CPU 熱插拔功能？"
  :options='[
    "isCPUPinningEnabled",
    "allowCPULiveUpdate",
    "isHotplugSupported",
    "hotplugCPUEnabled",
  ]'
  :answer="2"
  explanation="根據 pkg/virt-launcher/virtwrap/converter/compute/cpu.go，CPUDomainConfigurator 包含 isHotplugSupported 與 requiresMPXCPUValidation 兩個欄位。當 isHotplugSupported=true 且 VMI spec 設定了 MaxSockets 時，Configure() 呼叫 domainVCPUTopologyForHotplug() 產生支援動態增減的 vCPU 拓撲——在 domain XML 中預先定義 maxSockets 數量的 vCPU 槽位，啟動時只啟用指定數量，熱插拔時透過 libvirt API 啟用額外 vCPU 裝置。"
/>
