---
layout: doc
title: KubeVirt 隨堂測驗
---

<script setup>
import QuizQuestion from '../.vitepress/theme/components/QuizQuestion.vue'
</script>

# KubeVirt 隨堂測驗

本測驗涵蓋 **7 大主題領域，共 210 道題目**，適合用來驗收團隊對 KubeVirt 的學習成效。

> 每道題目皆有詳細解說，建議先作答再查看答案。

Agent completed. agent_id: quiz-kubevirt-architecture, agent_type: general-purpose, status: completed, description: Generate 基礎架構 30 questions, elapsed: 536s, total_turns: 0, duration: 527s

Now I have all the content needed. Let me generate the 30 questions:

## 🏗️ 基礎架構

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

---

## ⚙️ 核心元件

<QuizQuestion
  question="1. virt-operator 監聽哪個 Port 提供 Metrics 與 Leader Election 服務？"
  :options='[
    "8182",
    "8185",
    "8186",
    "8443",
  ]'
  :answer="2"
  explanation="根據 virt-operator 原始碼 pkg/virt-operator/application.go，defaultPort = 8186，virt-operator 的 Metrics 與 Leader Election 均透過此埠提供服務。"
/>

<QuizQuestion
  question="2. 安裝 KubeVirt 時，哪個元件是「唯一需要手動部署」的？"
  :options='[
    "virt-controller",
    "virt-api",
    "virt-handler",
    "virt-operator",
  ]'
  :answer="3"
  explanation="virt-operator 是整個 KubeVirt 安裝流程中唯一需要用 kubectl apply 手動部署的元件。建立 KubeVirt CR 之後，virt-operator 才會自動部署 virt-api、virt-controller、virt-handler 等所有其他元件。"
/>

<QuizQuestion
  question="3. virt-operator 的 Leader Election 使用哪種 Kubernetes 資源，且 Lease Duration 為多少秒？"
  :options='[
    "ConfigMap，30 秒",
    "Endpoint，15 秒",
    "Kubernetes Lease，15 秒",
    "Kubernetes Lease，30 秒",
  ]'
  :answer="2"
  explanation="virt-operator 部署資訊表格指出：Leader Election 使用 Kubernetes Lease，duration: 15s。透過 Lease 資源確保多個副本中只有一個 active leader 執行協調邏輯。"
/>

<QuizQuestion
  question="4. virt-operator 的預設 Rate Limiting QPS 與 Burst 各是多少？"
  :options='[
    "QPS=30，Burst=50",
    "QPS=50，Burst=100",
    "QPS=100，Burst=200",
    "QPS=10，Burst=20",
  ]'
  :answer="1"
  explanation="virt-operator 原始碼定義 DefaultVirtOperatorQPS = 50，DefaultVirtOperatorBurst = 100。這些值可透過環境變數 VIRT_OPERATOR_CLIENT_QPS 與 VIRT_OPERATOR_CLIENT_BURST 調整。"
/>

<QuizQuestion
  question="5. virt-operator 升級 KubeVirt 版本時，新版本的 Install Strategy 以哪種 Kubernetes 資源形式儲存？"
  :options='[
    "Secret",
    "ConfigMap",
    "CRD annotation",
    "Deployment label",
  ]'
  :answer="1"
  explanation="升級流程說明中，步驟 2 為「載入新版本的 Install Strategy（以 ConfigMap 形式存儲在 kubevirt namespace）」。virt-operator 讀取此 ConfigMap 以決定如何滾動更新各元件。"
/>

<QuizQuestion
  question="6. KubeVirt CR 的 status.phase 在所有元件都就緒後，會顯示什麼值？"
  :options='[
    "Running",
    "Ready",
    "Deployed",
    "Available",
  ]'
  :answer="2"
  explanation="KubeVirt CR Status 追蹤章節指出，phase 的可能值為 Deploying、Deployed、Deleting、Deleted。當所有元件完成部署後，phase 會從 Deploying 更新為 Deployed，且條件 Available 的 reason 為 AllComponentsReady。"
/>

<QuizQuestion
  question="7. virt-api 的 Mutating Webhook 預設會將 VMI 的 terminationGracePeriodSeconds 補齊為多少秒？"
  :options='[
    "60 秒",
    "120 秒",
    "180 秒",
    "300 秒",
  ]'
  :answer="2"
  explanation="virt-api Mutating Webhook 補齊內容章節列出：terminationGracePeriodSeconds 預設值為 180 秒。此值在使用者建立 VMI 時若未指定，由 Mutating Webhook 自動補齊。"
/>

<QuizQuestion
  question="8. virt-api 的 Mutating Webhook 在 x86 架構下，預設補齊的 domain.machine.type 是什麼？"
  :options='[
    "pc",
    "i440fx",
    "q35",
    "virt",
  ]'
  :answer="2"
  explanation="virt-api Mutating Webhook 補齊內容中明確指出：domain.machine.type 預設為 &quot;q35&quot;（x86 架構）。q35 是現代 Intel 晶片組模擬型態，支援 PCIe 裝置。ARM64 架構則使用 &quot;virt&quot;。"
/>

<QuizQuestion
  question="9. virt-api 提供 HTTPS 服務的對外 Port 是多少？"
  :options='[
    "6443",
    "8080",
    "8443",
    "443",
  ]'
  :answer="3"
  explanation="virt-api 部署資訊表格指出 Port 為 443（外部）、8443（內部 TLS）、8186（Metrics）。外部請求（kubectl / virtctl / REST）透過 Port 443 進入 virt-api。"
/>

<QuizQuestion
  question="10. virt-api 預設的 Rate Limiting QPS 與 Burst 分別是多少？"
  :options='[
    "QPS=50，Burst=100",
    "QPS=20，Burst=40",
    "QPS=30，Burst=50",
    "QPS=10，Burst=30",
  ]'
  :answer="2"
  explanation="virt-api 原始碼定義 DefaultVirtAPIQPS = 30，DefaultVirtAPIBurst = 50。virt-api 支援動態重新載入 rate limiter，可透過 ClusterConfig 變更觸發。"
/>

<QuizQuestion
  question="11. virt-api 使用哪種機制驗證請求者是否有權限執行特定操作（例如連接 console）？"
  :options='[
    "JWT Token 驗證",
    "Kubernetes SubjectAccessReview",
    "mTLS 憑證驗證",
    "API Key 比對",
  ]'
  :answer="1"
  explanation="根據 pkg/virt-api/rest/authorizer.go，virt-api 使用 Kubernetes SubjectAccessReview 驗證請求者權限。例如執行 console 操作，使用者需要 apiGroups: [subresources.kubevirt.io]、resources: [virtualmachineinstances/console]、verbs: [get]。"
/>

<QuizQuestion
  question="12. virt-api 的 Validating Webhook 會驗證哪些安全性限制？"
  :options='[
    "禁止使用超過 8 個 CPU 核心",
    "普通用戶不能使用 hostPID 或 hostNetwork",
    "禁止使用 PVC 作為根磁碟",
    "強制所有 VM 必須使用 virtio 網卡",
  ]'
  :answer="1"
  explanation="virt-api Validating Webhook 驗證項目中明確列出：安全性驗證「普通用戶不能使用 hostPID/hostNetwork」。此外也會驗證 CPU > 0、Memory 合理、Disk 與 Volume 名稱一致、FeatureGates 是否啟用等。"
/>

<QuizQuestion
  question="13. virt-controller 中，VMI 控制器的 Worker Goroutine 數量是多少，為何設定較高？"
  :options='[
    "3 個，因為 VMI 操作簡單",
    "6 個，與 Snapshot 控制器相同",
    "10 個，因為 VMI 事件最頻繁",
    "16 個，因為需要高並發",
  ]'
  :answer="2"
  explanation="多控制器執行緒數設定：vmiControllerThreads = 10，因為 VMI 事件最頻繁，需要最多 worker 並行處理。其他控制器（VM、Migration、ReplicaSet、Pool、Node、Evacuation）均為 3 個，Snapshot 為 6 個。"
/>

<QuizQuestion
  question="14. virt-controller 的 Leader Election 設定中，Renew Deadline 是多少秒？"
  :options='[
    "5 秒",
    "10 秒",
    "15 秒",
    "20 秒",
  ]'
  :answer="1"
  explanation="virt-controller Leader Election 設定：Lease Duration = 15 秒、Renew Deadline = 10 秒、Retry Period = 2 秒。只有 Leader 才會執行協調邏輯，可透過 --leader-election-* 參數調整。"
/>

<QuizQuestion
  question="15. virt-controller 的 Metrics Port 是多少？"
  :options='[
    "8182",
    "8185",
    "8186",
    "8443",
  ]'
  :answer="0"
  explanation="virt-controller 部署資訊表格指出：Metrics Port = 8182，Leader Election Port = 8443。注意與 virt-handler（8185）、virt-operator（8186）的 Port 不同。"
/>

<QuizQuestion
  question="16. virt-controller VM 控制器中，RunStrategy 設為 RerunOnFailure 代表什麼行為？"
  :options='[
    "永遠確保 VMI 存在，即使手動停止也重啟",
    "只要使用者沒有 stop request 就持續執行",
    "VM 失敗或 VMI 不存在時自動重啟",
    "VM 只執行一次，完成後不再重啟",
  ]'
  :answer="2"
  explanation="shouldStartVM 邏輯中，RunStrategy = RerunOnFailure 時呼叫 vm.lastVMIFailedOrMissing()，意思是當上次 VMI 失敗或 VMI 不存在時才重啟。Always 代表永遠確保 VMI 存在，Once 代表只跑一次，Halted 代表從不自動啟動。"
/>

<QuizQuestion
  question="17. virt-controller 的 Work Queue 失敗重試機制採用哪種策略，最長退避時間為何？"
  :options='[
    "固定間隔 5 秒重試，無上限",
    "指數退避，最長不超過 16 秒",
    "指數退避，最長不超過 60 秒",
    "線性退避，每次加 2 秒",
  ]'
  :answer="1"
  explanation="Work Queue 機制說明：失敗後以指數退避重新入列（第 1 次失敗 1 秒後重試，第 2 次 2 秒，第 3 次 4 秒...），最長不超過 16 秒。成功則不重新入列。"
/>

<QuizQuestion
  question="18. virt-handler 的部署型態是什麼，且每個節點部署幾個？"
  :options='[
    "Deployment，每個節點 2 個（High Availability）",
    "DaemonSet，每個 Linux 節點 1 個",
    "StatefulSet，每個節點 1 個",
    "ReplicaSet，整個叢集共 3 個",
  ]'
  :answer="1"
  explanation="virt-handler 部署資訊：部署型態為 DaemonSet，副本為每個 Linux 節點一個。這確保每個有 VM 工作負載的節點都有一個 virt-handler 作為節點代理，監控並管理該節點上的 VMI。"
/>

<QuizQuestion
  question="19. virt-handler 需要哪些特殊的 Pod 安全設定？"
  :options='[
    "runAsRoot: true，hostIPC: true",
    "hostPID: true，hostNetwork: true",
    "privileged: true，allowPrivilegeEscalation: true",
    "seccompProfile: Unconfined，hostPID: true",
  ]'
  :answer="1"
  explanation="virt-handler 部署資訊中指出特殊權限為 hostPID: true 與 hostNetwork: true，並掛載 hostPath: /proc、/var/run/kubevirt、/var/lib/kubelet。hostPID 用於隔離偵測找到 virt-launcher 的 PID，hostNetwork 用於 Migration Proxy 的網路操作。"
/>

<QuizQuestion
  question="20. virt-handler 與 virt-launcher 通訊時，Unix Domain Socket 的路徑格式是什麼？"
  :options='[
    "/var/run/kubevirt/{VMI-Name}/cmd-server.sock",
    "/var/run/kubevirt-private/{VMI-UID}/cmd-server.sock",
    "/tmp/kubevirt/{VMI-UID}/grpc.sock",
    "/run/kubevirt/launcher/{namespace}/cmd.sock",
  ]'
  :answer="1"
  explanation="virt-handler 與 virt-launcher 通訊章節明確指出 Socket 路徑為 /var/run/kubevirt-private/{VMI-UID}/cmd-server.sock，使用 gRPC（Protocol Buffers）協定進行通訊。"
/>

<QuizQuestion
  question="21. virt-handler 負責 VM 網路設定的哪個階段，為什麼？"
  :options='[
    "Phase 2（Unprivileged），因為不需要特殊權限",
    "Phase 1（Privileged），因為需要 CAP_NET_ADMIN 修改 Pod network namespace",
    "Phase 0（Pre-flight），在 Pod 建立前先行設定",
    "Phase 3（Post-boot），在 VM 啟動後設定",
  ]'
  :answer="1"
  explanation="virt-handler 負責 Phase 1（Privileged）網路設定，原因是需要 CAP_NET_ADMIN 才能修改 Pod 的 network namespace（建立 bridge、veth pair、移除 eth0 的 IP 等）。virt-launcher 只有最小權限，無法自行設定橋接，因此需要 virt-handler 代為執行。"
/>

<QuizQuestion
  question="22. virt-handler 在節點上加上的哪個標籤表示該節點可以排程 VM？"
  :options='[
    "node.kubernetes.io/vm-ready=true",
    "kubevirt.io/schedulable=true",
    "kubevirt.io/enabled=true",
    "vm.kubevirt.io/node=active",
  ]'
  :answer="1"
  explanation="virt-handler 節點標籤管理章節指出，啟動時會為節點加上 kubevirt.io/schedulable: &quot;true&quot; 標籤，以及 CPU 型號、CPU 功能（vmx/svm）、設備（kvm）等能力標籤，供調度時使用。"
/>

<QuizQuestion
  question="23. virt-handler 執行 Migration 時，預設的並行通道（multifd）數量是多少？"
  :options='[
    "4",
    "6",
    "8",
    "16",
  ]'
  :answer="2"
  explanation="virt-handler migration-source.go 中 MigrationOptions 的 Parallelism 設為 8，且常數 parallelMultifdMigrationThreads = 8。多通道並行可以提升 Live Migration 的記憶體傳輸頻寬。"
/>

<QuizQuestion
  question="24. virt-handler 進行 Live Migration 時，目標節點網路介面的選擇優先順序為何？"
  :options='[
    "先用 eth0，再用 migration0",
    "先用 Pod IP，再用 migration0",
    "先用 migration0（專用遷移網路），再用 Pod 網路",
    "只使用 Pod 網路，不支援專用遷移網路",
  ]'
  :answer="2"
  explanation="FindMigrationIP 函數邏輯：優先使用名為 migration0 的介面（專用遷移網路）；若不存在，退而求其次使用 Pod 網路（podIP）。使用專用遷移網路可以避免 VM 資料流量與業務流量互相干擾。"
/>

<QuizQuestion
  question="25. virt-launcher 是以哪種 Kubernetes 資源型態運行，且數量與 VMI 的關係為何？"
  :options='[
    "DaemonSet，整個叢集一個",
    "Deployment，每個 namespace 一個",
    "Pod，每個執行中的 VMI 一個",
    "StatefulSet，根據副本數動態調整",
  ]'
  :answer="2"
  explanation="virt-launcher 部署資訊：部署型態為 Pod（由 virt-controller 建立），數量為每個執行中的 VMI 一個。每個 virt-launcher Pod 包含 virt-launcher 程序與 libvirtd 程序，獨立管理一個 QEMU 虛擬機器。"
/>

<QuizQuestion
  question="26. virt-launcher 啟動 VM 的預設超時時間（defaultStartTimeout）是多少？"
  :options='[
    "1 分鐘",
    "2 分鐘",
    "3 分鐘",
    "5 分鐘",
  ]'
  :answer="2"
  explanation="virt-launcher 重要常數中定義 defaultStartTimeout = 3 * time.Minute（3 分鐘）。此外 LibvirtLocalConnectionTimeout = 15 秒，用於 virt-launcher 連接到本機 libvirtd 的超時設定。"
/>

<QuizQuestion
  question="27. virt-launcher 啟動後，如何通知 virt-handler 它已就緒可以接受指令？"
  :options='[
    "透過 HTTP healthz endpoint 回傳 200",
    "更新 Pod 的 label kubevirt.io/ready=true",
    "重新命名 ready file（socket），讓 virt-handler 偵測到",
    "傳送 gRPC Ready 訊號給 virt-handler",
  ]'
  :answer="2"
  explanation="virt-launcher 啟動流程步驟 6 說明：markReady(readyFile) 透過重新命名 socket 檔案，讓 virt-handler 知道 virt-launcher 已就緒。virt-handler 的隔離偵測（podIsolationDetector）會偵測此 ready file 的出現。"
/>

<QuizQuestion
  question="28. virt-launcher 的 Guest Agent 輪詢間隔是多少，可以取得哪類資訊？"
  :options='[
    "每 5 秒，只取得網路介面資訊",
    "每 10-30 秒，取得 OS 資訊、網路介面、檔案系統、登入使用者等",
    "每 60 秒，只取得 CPU 與記憶體使用量",
    "每 1 分鐘，取得完整 VM 狀態快照",
  ]'
  :answer="1"
  explanation="virt-launcher Guest Agent 整合章節：輪詢間隔 10-30 秒，取得資訊包括 Guest OS 資訊（OS 名稱、版本、核心）、網路介面清單（含 Guest 內部 IP）、掛載的檔案系統、登入使用者列表、系統負載，並更新到 VMI.Status.GuestOSInfo。"
/>

<QuizQuestion
  question="29. virt-launcher 執行 VM 網路設定的哪個階段，其主要工作是什麼？"
  :options='[
    "Phase 1，建立 bridge 與 veth pair",
    "Phase 2（Unprivileged），讀取 Phase 1 快取並注入 domain XML，以及啟動 DHCP server",
    "Phase 0，設定 CNI 網路插件",
    "Phase 3，在 VM 啟動後更新 MAC 地址",
  ]'
  :answer="1"
  explanation="virt-launcher 執行 Network Phase 2（Unprivileged），主要步驟：1. 讀取 Phase 1 快取的網路資訊；2. 將網路配置（MAC、MTU、tap/bridge）注入到 domain XML；3. 若為 masquerade 模式則啟動 DHCP server。Phase 1 由 virt-handler 以特權方式完成。"
/>

<QuizQuestion
  question="30. virt-launcher 的 libvirt 連線本地超時（LibvirtLocalConnectionTimeout）是多少秒？"
  :options='[
    "5 秒",
    "10 秒",
    "15 秒",
    "30 秒",
  ]'
  :answer="2"
  explanation="virt-launcher 重要常數定義 LibvirtLocalConnectionTimeout = 15 * time.Second（15 秒）。這是 virt-launcher 嘗試連接到本機 libvirtd/virtqemud（使用 &quot;qemu:///system&quot; URI）的超時時間。virt-handler 的 watchdog timeout 則為 30 秒。"
/>

---

## 🌐 API 與網路

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

---

## 💾 儲存與輔助元件

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

---

Agent completed. agent_id: quiz-kubevirt-advanced, agent_type: general-purpose, status: completed, description: Generate 進階功能 30 questions, elapsed: 204s, total_turns: 0, duration: 198s

Now I have all the content needed. Let me generate the 30 questions:

## 🚀 進階功能

<QuizQuestion
  question="1. KubeVirt Live Migration 預設採用哪種記憶體遷移算法？"
  :options='[
    "Post-copy：先切換 VM 到目標節點，再按需補傳記憶體頁面",
    "Pre-copy：在 VM 持續運行時逐步將記憶體複製到目標節點",
    "Cold copy：停止 VM 後一次性複製所有記憶體",
    "Delta-copy：只傳輸記憶體差異，不傳輸完整頁面",
  ]'
  :answer="1"
  explanation="KubeVirt 預設使用 pre-copy（預先複製）算法。其流程為：在目標節點啟動 QEMU process、建立 migration channel，然後逐輪傳輸記憶體頁面。第一輪傳輸所有頁面，後續輪次只傳輸上一輪被修改的 dirty pages，直到 dirty set 夠小後才進入短暫停機（downtime）完成最後切換。"
/>

<QuizQuestion
  question="2. 在 pre-copy migration 中，若 VM 的記憶體 dirty rate 持續大於網路傳輸速率，應啟用哪個機制來強制讓 migration 收斂？"
  :options='[
    "allowBlockMigration：允許磁碟同時遷移",
    "allowPostCopy：切換至 post-copy 模式，先完成切換再補傳頁面",
    "allowAutoConverge：自動降低 vCPU 速度以減少 dirty page 產生",
    "unsafeMigrationOverride：強制跳過收斂等待直接完成",
  ]'
  :answer="2"
  explanation="auto-converge 機制會在 KVM 偵測到 migration 收斂困難時，自動降低 guest 的 vCPU 執行速度（throttling），從而降低 dirty rate。vCPU 最低可被降至 20%。此設定可透過 MigrationPolicy 的 allowAutoConverge: true 或 KubeVirt CR 的 migrationConfiguration.allowAutoConverge: true 啟用。"
/>

<QuizQuestion
  question="3. Post-copy migration 與 pre-copy migration 相比，最大的風險是什麼？"
  :options='[
    "Post-copy 需要更多網路頻寬，可能影響 VM 業務流量",
    "Post-copy 的 downtime 比 pre-copy 更長",
    "Post-copy 進行中若來源節點或網路發生故障，目標節點的 VM 將立即 crash",
    "Post-copy 無法與 MigrationPolicy 搭配使用",
  ]'
  :answer="2"
  explanation="在 post-copy 進行中，VM 已切換到目標節點執行，但仍有大量記憶體頁面留在來源節點，需透過網路按需拉取。若此時來源節點或網路連線發生故障，目標節點上的 VM 將因無法取得記憶體頁面而立即 crash。因此 post-copy 僅建議在網路非常穩定的環境下使用。"
/>

<QuizQuestion
  question="4. MigrationPolicy 中的 bandwidthPerMigration 設定為 &quot;1Gi&quot; 代表什麼含義？"
  :options='[
    "每次 migration 最多可傳輸 1 GiB 的總資料量",
    "每次 migration 的網路頻寬上限為每秒 1 GiB",
    "migration 超時時間計算基準為每 GiB 1 秒",
    "migration 所用的 PVC 最大容量為 1 GiB",
  ]'
  :answer="1"
  explanation="MigrationPolicy 中的 bandwidthPerMigration 欄位設定的是單次 migration 的最大網路頻寬限制（bytes/s）。設定為 &quot;1Gi&quot; 表示每秒最多傳輸 1 GiB 的資料，可避免 migration 流量佔用過多網路資源而影響 VM 業務。若不設定此值（空白），則不限制頻寬。"
/>

<QuizQuestion
  question="5. KubeVirt 全域設定中，parallelOutboundMigrationsPerNode 預設值為何？"
  :options='[
    "1",
    "2",
    "5",
    "10",
  ]'
  :answer="1"
  explanation="parallelOutboundMigrationsPerNode 的預設值為 2，表示每個節點同時最多允許 2 個 VM 向外遷移。parallelMigrationsPerCluster（整個叢集同時進行的 migration 總上限）預設為 5。對於 10GbE 網路建議最多 2-3 個並行 migration，25GbE 最多 4-5 個。"
/>

<QuizQuestion
  question="6. VMI 的 evictionStrategy 設定為 LiveMigrateIfPossible 時，若該 VMI 無法 Live Migrate，節點 drain 時會發生什麼？"
  :options='[
    "drain 操作會失敗並回傳錯誤",
    "VMI 會被直接刪除（驅逐）",
    "VMI 繼續在原節點運行，忽略 drain 請求",
    "VMI 會被暫停（Paused）等待手動處理",
  ]'
  :answer="1"
  explanation="evictionStrategy 有四個值：LiveMigrate（必須 migrate，否則 drain 失敗）、LiveMigrateIfPossible（盡量 migrate，不可能時直接刪除 VMI）、None（不處理，直接驅逐）、External（由外部工具處理）。LiveMigrateIfPossible 在無法遷移時選擇直接刪除 VMI，讓 drain 得以完成。"
/>

<QuizQuestion
  question="7. 使用 SR-IOV 網路的 VMI 嘗試進行 Live Migration 時，會出現什麼結果？"
  :options='[
    "Migration 成功，但 SR-IOV 介面會被替換成 virtio 介面",
    "Migration 會自動改用 block migration 模式進行",
    "Migration 立即失敗，IsMigratable condition 為 False",
    "Migration 進入 Pending 狀態等待使用者確認",
  ]'
  :answer="2"
  explanation="SR-IOV VF（Virtual Function）是特定物理網卡上的硬體資源，與特定節點強綁定，無法跟隨 VM 移動。使用 SR-IOV 網路的 VMI 的 IsMigratable condition 為 False，嘗試 migration 將立即失敗，錯誤訊息為 &quot;cannot migrate VMI with sriov network interface&quot;。PCI Passthrough（GPU/FPGA）和 HostDisk 也有同樣的限制。"
/>

<QuizQuestion
  question="8. Multifd（Multiple file descriptors）技術在 KubeVirt Live Migration 中的預設 channel 數量是多少？"
  :options='[
    "4 個",
    "8 個",
    "16 個",
    "32 個",
  ]'
  :answer="1"
  explanation="KubeVirt 預設啟用 multifd，使用 8 個 TCP channel 並行傳輸記憶體頁面，以充分利用現代高頻寬網路（25GbE、100GbE）。在 10GbE 以上的網路環境中 multifd 能顯著提升 migration 速度，但在低頻寬網路（1GbE）中效果不明顯。"
/>

<QuizQuestion
  question="9. KubeVirt Migration 狀態機中，哪個狀態表示已在目標節點建立 virt-launcher pod 並完成 QEMU migration channel 建立，即將開始記憶體傳輸？"
  :options='[
    "Pending",
    "PreparingTarget",
    "TargetReady",
    "Running",
  ]'
  :answer="2"
  explanation="Migration 狀態機的流程為：Pending（已建立 VMIM CR）→ PreparingTarget（正在目標節點建立 virt-launcher pod）→ TargetReady（目標端就緒，QEMU migration channel 已建立）→ Running（開始 pre-copy 記憶體傳輸）→ Succeeded 或 Failed 或 Cancelled。TargetReady 表示準備工作完成，即將開始實際的記憶體傳輸。"
/>

<QuizQuestion
  question="10. Migration 失敗後，來源節點上的 VM 狀態為何？"
  :options='[
    "VM 被停止，需要手動重新啟動",
    "VM 繼續在來源節點正常運行，服務不受影響",
    "VM 進入 Paused 狀態等待管理員介入",
    "VM 被刪除並重建在其他節點",
  ]'
  :answer="1"
  explanation="Migration 失敗時，VM 會繼續在來源節點正常運行，不會影響服務。這是 Live Migration 的重要保障機制：migration 是非破壞性的，失敗後直接回到原狀態。失敗的 migration CR（VMIM）會被保留供排查問題使用。"
/>

<QuizQuestion
  question="11. 設定獨立 migration network 的主要目的是什麼？"
  :options='[
    "提供更高的安全加密，保護遷移資料不被竊取",
    "避免 migration 流量佔用 VM 業務網路，提升隔離性",
    "讓 migration 能突破 parallelOutboundMigrationsPerNode 的限制",
    "允許跨 VLAN 的 VM 進行 migration",
  ]'
  :answer="1"
  explanation="KubeVirt 支援使用獨立的 migration network，設定在 KubeVirt CR 中並搭配 Multus 建立專用的 NetworkAttachmentDefinition。其三大優點：避免 migration 流量影響 VM 業務網路品質、限制 migration 使用特定網路路徑、提升安全性（migration 流量不經過業務 VLAN）。"
/>

<QuizQuestion
  question="12. 建立 Online Snapshot（線上快照）時，為確保資料一致性，KubeVirt 會透過 qemu-guest-agent 執行什麼操作？"
  :options='[
    "暫停 VM 的 vCPU 執行，確保記憶體靜止",
    "執行 fs-freeze 凍結 filesystem I/O，快照後再執行 fs-thaw 解凍",
    "將 VM 的記憶體內容完整寫入磁碟後再建立快照",
    "強制停止所有應用程式程序，快照後重新啟動",
  ]'
  :answer="1"
  explanation="Online Snapshot 使用 guest agent quiescing 機制：先通知 guest OS 執行 fs-freeze（將 journal 和 dirty cache flush 到磁碟，暫停後續寫入），在靜默狀態下建立磁碟快照，完成後執行 fs-thaw 解凍恢復正常 I/O。此流程確保 filesystem 層面的一致性，但不包含記憶體狀態。"
/>

<QuizQuestion
  question="13. VirtualMachineSnapshot 的 status.indications 出現 NoGuestAgent 時，代表什麼情況？"
  :options='[
    "快照在 VM 停止狀態下建立，資料完全靜止",
    "VM 沒有安裝 qemu-guest-agent，快照為 crash-consistent（崩潰一致性）",
    "Guest agent 的 quiescing 超時，快照只完成了部分 flush",
    "快照在 VM 暫停（Paused）狀態下建立",
  ]'
  :answer="1"
  explanation="Indications 欄位反映快照建立時的情況：NoGuestAgent 表示 VM 沒有安裝 qemu-guest-agent，無法進行 quiescing，快照為 crash-consistent（就像突然斷電後的狀態），資料一致性最低。GuestAgent 表示成功 quiescing（一致性高），QuiesceTimeout 表示 quiescing 超時（中等），Paused 表示 VM 在暫停狀態下建立（一致性高）。"
/>

<QuizQuestion
  question="14. KubeVirt 快照功能需要哪項 Kubernetes 基礎設施支援才能運作？"
  :options='[
    "Kubernetes Admission Webhook 和 CRD 支援",
    "CSI Driver 的 VolumeSnapshot 能力、snapshot-controller 以及 VolumeSnapshotClass",
    "Persistent Volume 的 ReadWriteMany 存取模式",
    "MetalLB 或其他 LoadBalancer 提供外部 IP",
  ]'
  :answer="1"
  explanation="KubeVirt 快照功能建立在 Kubernetes CSI 快照框架之上，需要三個條件：1) 儲存後端的 CSI driver 必須實作 CREATE_DELETE_SNAPSHOT 能力；2) 叢集需安裝 snapshot-controller（external-snapshotter）；3) 需建立對應的 VolumeSnapshotClass。hostPath 和 local 儲存不支援 VolumeSnapshot。"
/>

<QuizQuestion
  question="15. VirtualMachineSnapshot 建立後，KubeVirt 會自動建立哪個中間資源來儲存快照的實際內容？"
  :options='[
    "VolumeSnapshotContent",
    "VirtualMachineSnapshotContent",
    "VirtualMachineBackup",
    "PersistentVolumeSnapshotContent",
  ]'
  :answer="1"
  explanation="KubeVirt 快照資源層次結構為：使用者建立 VirtualMachineSnapshot（頂層請求資源），KubeVirt 自動建立 VirtualMachineSnapshotContent（儲存 VM spec 和所有 VolumeSnapshot 的參考），每個 PVC 對應一個 VolumeSnapshot（Kubernetes 標準快照資源），底層由 CSI driver 管理 VolumeSnapshotContent。"
/>

<QuizQuestion
  question="16. 對 VM 執行 VirtualMachineRestore（還原操作）時，若 VM 當時正在運行，會發生什麼？"
  :options='[
    "還原操作會失敗，要求使用者先手動停止 VM",
    "KubeVirt 會自動停止 VM，完成還原後再重新啟動",
    "還原操作會在 VM 運行中以 hot-swap 方式替換磁碟",
    "還原操作會建立新的 VM 而不影響現有運行中的 VM",
  ]'
  :answer="1"
  explanation="還原操作流程：使用者建立 VirtualMachineRestore CR → KubeVirt 自動停止 VM（若正在運行）→ 從 VolumeSnapshot 建立新的 PVC → 更新 VM 使用新的 PVC → 重新啟動 VM → 更新 status.complete = true。還原需要 VM 處於停止狀態，KubeVirt 會自動處理停止與重啟。"
/>

<QuizQuestion
  question="17. 下列哪個情況下建議使用 Offline Snapshot 而非 Online Snapshot？"
  :options='[
    "需要每小時自動建立 checkpoint 的開發環境",
    "需要最高資料一致性保證的生產環境重要備份",
    "測試環境需要快速反覆還原至初始狀態",
    "VM 必須持續提供服務不能停機的場景",
  ]'
  :answer="1"
  explanation="Offline Snapshot 在 VM 停止後建立，資料完全靜止，具有最高一致性保證，且不需要 guest agent。Online Snapshot 雖便利但有限制：不包含記憶體狀態、應用層事務可能不一致、freeze 期間會短暫影響 I/O 效能。文件明確建議：對重要的生產環境備份優先使用 Offline Snapshot。"
/>

<QuizQuestion
  question="18. KubeVirt 快照的 quiesceDeadlineSeconds 欄位超時後，快照建立流程會如何處理？"
  :options='[
    "快照建立失敗並回傳錯誤，不會保留任何資料",
    "繼續建立快照，但在 indications 中標記 QuiesceTimeout",
    "自動改為 Offline Snapshot 模式，先停止 VM",
    "等待使用者手動介入決定是否繼續",
  ]'
  :answer="1"
  explanation="quiesceDeadlineSeconds（預設 300 秒）是 guest agent quiescing 的超時時間。超過此時間後，KubeVirt 不會放棄快照建立，而是繼續進行但在 status.indications 中標記 QuiesceTimeout，表示 quiescing 未完全成功，快照的資料一致性為中等程度（部分 flush）。"
/>

<QuizQuestion
  question="19. KubeVirt 透過哪個元件（component）向 Prometheus 暴露 VMI 層級的指標？"
  :options='[
    "virt-api",
    "virt-controller",
    "virt-handler",
    "virt-operator",
  ]'
  :answer="2"
  explanation="virt-handler 是運行在每個 worker node 上的 DaemonSet，負責節點層級的 VMI 管理，同時也是暴露 VMI 層級 metrics 的主要元件。ServiceMonitor 設定中，針對 virt-handler 建議使用較短的抓取間隔（15s），因為它包含豐富的 VMI 即時指標。"
/>

<QuizQuestion
  question="20. Prometheus metric kubevirt_vmi_phase_count 的用途是什麼？"
  :options='[
    "記錄單一 VMI 在各 phase 停留的累計時間（秒）",
    "統計叢集中各 phase（如 Running、Pending）的 VMI 數量分佈",
    "記錄 VMI 發生 phase 轉換的事件次數",
    "追蹤 VMI 的 CPU 在各執行狀態的時間",
  ]'
  :answer="1"
  explanation="kubevirt_vmi_phase_count 是 Gauge 類型的 metric，標籤包含 phase、node、os、workload、flavor，用於統計叢集中各 phase 的 VMI 數量分佈。例如可查詢特定節點上 Running 狀態的 VMI 數量：kubevirt_vmi_phase_count{phase=&quot;Running&quot;, node=&quot;worker-1&quot;}。"
/>

<QuizQuestion
  question="21. kubevirt_vmi_vcpu_seconds_total 中的 state=&quot;steal&quot; 代表什麼含義？"
  :options='[
    "vCPU 正在執行 guest 的使用者態指令",
    "vCPU 等待磁碟 I/O 完成的時間",
    "hypervisor 拿走了原本應給 vCPU 的 host CPU 時間",
    "vCPU 空閒並執行 HLT 省電指令的時間",
  ]'
  :answer="2"
  explanation="kubevirt_vmi_vcpu_seconds_total 的 state 標籤有四個值：run（vCPU 執行 guest 指令）、idle（vCPU 空閒執行 HLT）、wait（vCPU 等待 I/O 完成）、steal（hypervisor 拿走了 vCPU 應得的 host CPU 時間）。steal 時間過高表示節點 CPU 資源不足，是效能問題的重要指標。"
/>

<QuizQuestion
  question="22. kubevirt_vmi_memory_balloon_size_bytes 指標過高時代表什麼問題？"
  :options='[
    "VM 的記憶體設定超過節點的實體記憶體，需要縮小 VM",
    "Host 正在從 VM 回收記憶體，guest OS 可能面臨記憶體壓力",
    "VM 的 huge pages 配置過大，影響其他 VM",
    "VM 記憶體使用率過低，建議降低 VM 記憶體設定以節省資源",
  ]'
  :answer="1"
  explanation="Balloon driver 是 KVM 的記憶體過提交機制：balloon size 越大表示 host 回收了越多 VM 的記憶體。kubevirt_vmi_memory_balloon_size_bytes 過大時，guest OS 的可用記憶體減少，可能導致記憶體壓力。建議告警規則：balloon size / domain bytes total > 30% 時觸發 warning。"
/>

<QuizQuestion
  question="23. 以下哪個 PromQL 查詢可以判斷 migration 是否正在收斂？"
  :options='[
    "kubevirt_vmi_migration_data_bytes / kubevirt_vmi_migration_data_processed",
    "kubevirt_vmi_migration_transfer_rate - kubevirt_vmi_migration_dirty_memory_rate",
    "rate(kubevirt_vmi_migration_succeeded[1h]) > 0",
    "kubevirt_vmi_migrations_in_running_phase < kubevirt_vmi_migrations_in_pending_phase",
  ]'
  :answer="1"
  explanation="判斷 migration 收斂的關鍵是比較傳輸速率與 dirty memory 產生速率。kubevirt_vmi_migration_transfer_rate - kubevirt_vmi_migration_dirty_memory_rate 若結果為正數（傳輸速率 > dirty rate），表示 migration 正在收斂；若為負數，則可能無法完成，應考慮啟用 auto-converge。"
/>

<QuizQuestion
  question="24. 建立 ServiceMonitor 讓 Prometheus 抓取 KubeVirt metrics 時，需要與哪個 label 匹配以找到 KubeVirt 的 Service？"
  :options='[
    "app.kubernetes.io/name: kubevirt",
    "prometheus.kubevirt.io: \\\"\\\"（空字串）",
    "kubevirt.io/component: metrics",
    "monitoring.kubevirt.io/enabled: \\\"true\\\"",
  ]'
  :answer="1"
  explanation="KubeVirt 安裝後會自動建立 Service，這些 Service 帶有 prometheus.kubevirt.io: &quot;&quot; 的 label。ServiceMonitor 的 selector 需要 matchLabels: {prometheus.kubevirt.io: &quot;&quot;} 才能正確匹配。virt-handler 的 ServiceMonitor 則使用 kubevirt.io: virt-handler 作為 selector。"
/>

<QuizQuestion
  question="25. KubeVirt 官方 Grafana Dashboard 中，專門用於 migration 監控的 Dashboard ID 是什麼？"
  :options='[
    "11115",
    "11116",
    "11117",
    "11118",
  ]'
  :answer="3"
  explanation="KubeVirt 社群提供三個官方 Grafana Dashboard：11116（KubeVirt Overview，VM 總覽含數量和狀態分佈）、11117（KubeVirt VMI Details，單一 VMI 的詳細指標）、11118（KubeVirt Migration，Migration 監控專用）。這些 Dashboard 可直接從 Grafana.com 匯入。"
/>

<QuizQuestion
  question="26. 哪個 Prometheus metric 用於監控 virt-controller 是否為當前的 leader？"
  :options='[
    "kubevirt_virt_controller_ready",
    "kubevirt_virt_controller_leading",
    "kubevirt_virt_controller_active",
    "kubevirt_virt_controller_elected",
  ]'
  :answer="1"
  explanation="kubevirt_virt_controller_leading 是 Gauge 類型，值為 1 表示該 virt-controller 是當前 leader，值為 0 表示備用節點。告警規則 sum(kubevirt_virt_controller_leading) == 0 可偵測「沒有 leading virt-controller」的緊急情況，此時 KubeVirt 控制面失效，severity 為 critical。"
/>

<QuizQuestion
  question="27. KubeVirtVirtHandlerDown 告警規則中，觸發條件 kubevirt_virt_handler_up == 0 持續多久才會發出告警？"
  :options='[
    "1 分鐘",
    "5 分鐘",
    "10 分鐘",
    "15 分鐘",
  ]'
  :answer="1"
  explanation="KubeVirtVirtHandlerDown 告警設定為 for: 5m，即 kubevirt_virt_handler_up == 0 的條件持續 5 分鐘後才觸發，severity 為 critical。告警訊息為「節點的 virt-handler 已停止工作超過 5 分鐘，該節點上的 VM 可能受影響」。for 設定可避免短暫抖動造成的誤報。"
/>

<QuizQuestion
  question="28. kubevirt_vmi_non_evictable 指標追蹤的是哪類 VMI？"
  :options='[
    "當前正在進行 migration 的 VMI",
    "設定 evictionStrategy=None、無法被驅逐的 VMI 數量",
    "因資源不足而卡在 Pending 狀態的 VMI",
    "使用了 SR-IOV 或 PCI Passthrough 的 VMI",
  ]'
  :answer="1"
  explanation="kubevirt_vmi_non_evictable 是 Gauge 類型指標，標籤為 node，記錄每個節點上設定 evictionStrategy=None（不可驅逐）的 VMI 數量。這類 VMI 可能阻礙節點維護（drain）操作，PromQL 查詢 kubevirt_vmi_non_evictable > 0 可識別潛在的維護障礙。"
/>

<QuizQuestion
  question="29. MigrationPolicy 的 completionTimeoutPerGiB 設定為 800 秒，若 VM 有 8 GiB 記憶體，總超時時間為多少秒？"
  :options='[
    "800 秒",
    "1600 秒",
    "6400 秒",
    "無法預測，取決於實際 dirty rate",
  ]'
  :answer="2"
  explanation="completionTimeoutPerGiB 的計算方式為：每 GiB 記憶體乘以設定的秒數。8 GiB × 800 秒/GiB = 6400 秒。此為整體 migration 的最大允許時間，若超過此時間 migration 未完成，將被視為失敗。全域預設值為 800 秒/GiB，可透過 MigrationPolicy 針對特定 VM 群組覆蓋。"
/>

<QuizQuestion
  question="30. 下列哪種儲存類型明確不支援 KubeVirt 的快照功能？"
  :options='[
    "Ceph RBD (rook-ceph)",
    "Longhorn",
    "AWS EBS CSI",
    "hostPath / local storage",
  ]'
  :answer="3"
  explanation="KubeVirt 快照功能依賴 CSI VolumeSnapshot 能力。支援的儲存包括 Ceph RBD、Ceph CephFS、Longhorn、OpenEBS cStor、AWS EBS、GCP Persistent Disk、Azure Disk 等。hostPath 和 local storage 明確標示為不支援（❌），因為這類儲存沒有 CSI driver 實作 VolumeSnapshot 能力。NFS 依 CSI driver 而定（⚠️ 部分支援）。"
/>___BEGIN___COMMAND_DONE_MARKER___0

---

Agent completed. agent_id: quiz-kubevirt-deepdive, agent_type: general-purpose, status: completed, description: Generate 深入剖析 30 questions, elapsed: 371s, total_turns: 0, duration: 363s

Now I have enough content to generate all 30 questions. Let me produce them:

```
## 🔬 深入剖析

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
```

---

## 📖 實用指南

<QuizQuestion
  question="1. 使用 virtctl 啟動一個名為 my-vm 的 VM 的指令是？"
  :options='[
    "kubectl start vm my-vm",
    "virtctl start my-vm",
    "kubectl patch vm my-vm --type merge -p 以 JSON 修改 spec.running:true",
    "kubectl create vm my-vm --run",
  ]'
  :answer="1"
  explanation="virtctl start my-vm 是標準方式，內部會更新 VM 的 spec.running 為 true 或 runStrategy。雖然 kubectl patch 也能達到效果，但 virtctl 提供更友善的 UX，並支援額外選項如 --paused。"
/>

<QuizQuestion
  question="2. virtctl ssh user@my-vm 連線成功需要滿足哪些主要前提？"
  :options='[
    "VM 必須有公開的 NodePort Service",
    "VM 的 SSH Service 已開啟，且已將公鑰注入 VM（透過 cloud-init 或 AccessCredentials）",
    "必須先在 VM 上執行 virtctl port-forward 後才能 SSH",
    "virtctl ssh 只支援 Windows VM，Linux VM 需用 virtctl console",
  ]'
  :answer="1"
  explanation="virtctl ssh 底層使用 SSH 協議連接 VM。需要：1. VM 內部 SSH Server 在運行，2. VM 有分配 IP，3. 使用者的 SSH 公鑰已注入 VM（通常用 cloud-init 或 VirtualMachineCluster-InstanceAccessCredentials）。virtctl ssh 會自動處理通道建立，不需要手動 port-forward。"
/>

<QuizQuestion
  question="3. virtctl console my-vmi 連接的是什麼？"
  :options='[
    "VM 的圖形界面（VNC）",
    "VM 的 Serial Console（串列控制台），可在無圖形界面時操作 OS",
    "VM 的 UEFI Shell",
    "VM 的 SSH Session",
  ]'
  :answer="1"
  explanation="virtctl console 連接到 VM 的 Serial Console（串列控制台）。這對於 VM 無法 SSH、OS 錯誤除錯、GRUB 設定等非常有用。需要 VM OS 已啟用 serial console（如在 GRUB 設定 console=ttyS0）。VNC 連接使用 virtctl vnc。"
/>

<QuizQuestion
  question="4. virtctl port-forward vm/my-vm 8080:80 指令的作用是？"
  :options='[
    "在 VM 上開啟 8080 port，轉發到外部 80 port",
    "將本機 8080 port 轉發到 VM 內部的 80 port",
    "建立 NodePort Service 將 8080 暴露到叢集外",
    "在 virt-launcher Pod 上設定 iptables 規則",
  ]'
  :answer="1"
  explanation="virtctl port-forward 類似 kubectl port-forward，將 localhost 的 8080 port 通過隧道轉發到 VM 的 80 port。這讓開發者不需要 Service 就能測試 VM 上的服務。連線通過 Kubernetes API Server 隧道，不需要直接存取 VM IP。"
/>

<QuizQuestion
  question="5. 若要強制暫停（freeze）一個正在執行的 VM，應使用哪個 virtctl 指令？"
  :options='[
    "virtctl stop --grace-period=0 my-vm",
    "virtctl freeze my-vmi",
    "virtctl pause vm my-vm",
    "virtctl suspend my-vm",
  ]'
  :answer="2"
  explanation="virtctl pause vm my-vm 將 VM 暫停（vCPU 停止執行，記憶體保留），VM 狀態顯示為 Paused。virtctl freeze my-vmi 則是對 VMI 執行 Guest OS 的 fsfreeze（檔案系統凍結）用於快照，兩者目的不同。"
/>

<QuizQuestion
  question="6. virtctl image-upload 指令的主要用途是什麼？"
  :options='[
    "將 VM 的磁碟映像匯出到 S3",
    "上傳本地 disk image（如 .qcow2、.raw、.iso）到 CDI PVC 或 DataVolume",
    "更新 KubeVirt 元件的容器映像",
    "將 OCI 映像轉換為 VM disk",
  ]'
  :answer="1"
  explanation="virtctl image-upload 是 CDI（Containerized Data Importer）的客戶端工具，用於直接上傳本地磁碟映像（qcow2、raw、vmdk、iso 等）到 PVC 或 DataVolume，透過 cdi-uploadproxy Service 完成傳輸。常用於 air-gapped 環境或匯入舊有 VM 磁碟。"
/>

<QuizQuestion
  question="7. KubeVirt HyperConverged (HCO) Operator 的主要作用是什麼？"
  :options='[
    "管理 KubeVirt 的高可用性，確保 virt-controller 有多個副本",
    "整合管理 KubeVirt、CDI、SSP、NetworkAddonsOperator 等多個相關元件，提供統一的安裝和設定入口",
    "提供 VM 的超融合儲存解決方案（將 Ceph 整合到 KubeVirt）",
    "HCO 已被棄用，官方建議直接安裝 KubeVirt",
  ]'
  :answer="1"
  explanation="HyperConverged Operator（HCO）是上層 Operator，以 HyperConverged CR 為單一入口，統一管理和協調 KubeVirt、CDI、SSP（Scheduling Scale Performance）、NetworkAddonsOperator、SRIOV Operator 等多個子 Operator 的安裝和設定，大幅簡化 OpenShift Virtualization 和 KubeVirt 生態的部署。"
/>

<QuizQuestion
  question="8. KubeVirt 安裝時，KubeVirtConfig（KubeVirt CR）的 certificateRotateStrategy 預設值是什麼？"
  :options='["Manual","External","None（關閉自動輪換）","Self（KubeVirt 自動管理）"]'
  :answer="3"
  explanation="KubeVirt CR 的 certificateRotateStrategy.selfSigned 預設為 Self，由 KubeVirt 自動管理 webhook 和內部元件所使用的 TLS 憑證輪換，不需要外部 cert-manager。也可設為 External 讓 cert-manager 管理。"
/>

<QuizQuestion
  question="9. 安裝 KubeVirt 時，若叢集不支援 KVM 硬體虛擬化，需要啟用哪個 Feature Gate？"
  :options='["SoftEmulation","UseEmulation","DisableKVM","AllowSoftwareEmulation"]'
  :answer="1"
  explanation="當節點不支援 KVM 時（如巢狀虛擬化環境、CI 環境），需在 KubeVirt CR spec.configuration.developerConfiguration.useEmulation 設為 true，啟用軟體模擬模式（QEMU TCG）。此模式效能極低，僅建議用於開發/測試環境。"
/>

<QuizQuestion
  question="10. 如何確認 KubeVirt 元件已成功安裝且狀態正常？"
  :options='[
    "檢查 kubeadm version 輸出",
    "執行 kubectl get kubevirt -n kubevirt 確認 PHASE 為 Deployed",
    "檢查 /etc/kubevirt/config.json 設定檔是否存在",
    "執行 virtctl version 確認 Client 版本",
  ]'
  :answer="1"
  explanation="kubectl get kubevirt -n kubevirt 可查看 KubeVirt CR 的狀態，PHASE 欄位 Deployed 表示所有元件已成功部署且就緒。也可用 kubectl describe kubevirt -n kubevirt 查看詳細的 Conditions 資訊，了解各子元件狀態。"
/>

<QuizQuestion
  question="11. 匯入一個 VMDK（VMware 磁碟格式）到 KubeVirt 最推薦的方法是什麼？"
  :options='[
    "直接將 VMDK 掛載為 hostPath Volume",
    "使用 CDI DataVolume，source 設為 http/s3/upload，CDI 自動將 VMDK 轉換為 qcow2",
    "先在本機將 VMDK 轉換為 raw 格式，再建立 PVC 後使用 kubectl cp 複製",
    "只能使用 qcow2 格式，VMDK 必須先在 VMware 上匯出",
  ]'
  :answer="1"
  explanation="CDI（Containerized Data Importer）支援自動轉換多種磁碟格式（VMDK、VHD、VHDX、raw、qcow2）為 qcow2（儲存到 PVC）。只需建立 DataVolume 並指定 source（http URL 或 S3），CDI importer Pod 自動下載並轉換，無需手動操作。"
/>

<QuizQuestion
  question="12. Forklift 工具在 VM 遷移流程中扮演什麼角色？"
  :options='[
    "管理 KubeVirt VM 的 Live Migration",
    "將 VMware vSphere、oVirt、OVA 等平台的 VM 批量遷移到 KubeVirt/OpenShift Virtualization",
    "將 KubeVirt VM 遷移到公有雲（AWS、GCP、Azure）",
    "將 Hyper-V VM 遷移到 Docker Container",
  ]'
  :answer="1"
  explanation="Forklift（MTV - Migration Toolkit for Virtualization）是 Red Hat 的開源工具，負責將傳統虛擬化平台（VMware vSphere、oVirt/RHV、Red Hat OpenStack、OVA 檔案）的 VM 批量遷移到 OpenShift Virtualization（KubeVirt）。支援 Cold Migration 和 Warm Migration（使用 CDI）。"
/>

<QuizQuestion
  question="13. Warm Migration（熱遷移）相比 Cold Migration（冷遷移）的主要優點是什麼？"
  :options='[
    "Warm Migration 不需要停機，VM 可以無縫切換到 KubeVirt",
    "Warm Migration 在正式切割前先進行多次增量資料同步（類似 pre-copy），大幅縮短最終停機時間",
    "Warm Migration 支援更多來源平台格式",
    "Warm Migration 自動設定 KubeVirt VM 的最佳化參數",
  ]'
  :answer="1"
  explanation="Warm Migration 透過 CBT（Changed Block Tracking）先將 VM 資料持續同步到 KubeVirt，多次增量複製後，最終停機切割（cutover）時間極短，通常只需數分鐘。Cold Migration 需要完全停止來源 VM 後才開始資料複製，停機時間更長。"
/>

<QuizQuestion
  question="14. 為了追蹤 VM 資源使用情況，KubeVirt 提供哪個 Prometheus Metrics 端點？"
  :options='[
    "virt-handler 在 /metrics 端點暴露每個節點的 VM 指標（CPU、記憶體、網路、磁碟 I/O）",
    "VM 指標只能透過 VMI 的 status 欄位讀取",
    "KubeVirt 不原生支援 Prometheus，需要安裝 kube-state-metrics",
    "只有 virt-controller 暴露指標，沒有 per-VM 的詳細指標",
  ]'
  :answer="0"
  explanation="每個節點上的 virt-handler DaemonSet 在 :8443/metrics（或設定的端點）暴露 Prometheus 指標，包含每個 VMI 的 CPU 使用率、記憶體使用量、網路流量、磁碟 I/O 等詳細指標。virt-controller 也暴露指標但主要是 controller 層面的資訊。"
/>

<QuizQuestion
  question="15. 當 VMI 卡在 Scheduling 狀態很長時間，最可能的排查方向是？"
  :options='[
    "查看 virt-api Pod 的 log，因為 API 層面卡住了",
    "查看 VMI 的 Events 和相關 Pod 的 Events，確認節點是否有足夠資源（CPU、GPU、HugePages）符合排程要求",
    "重啟 virt-controller 通常能解決排程問題",
    "VMI Scheduling 狀態是正常的初始化過程，不需要排查",
  ]'
  :answer="1"
  explanation="VMI 卡在 Scheduling 通常表示排程器無法找到符合要求的節點。排查步驟：1. kubectl describe vmi my-vmi 查看 Events；2. 確認節點是否有 KVM 設備、GPU、HugePages、SR-IOV VF 等特殊資源；3. 確認 NodeSelector/Affinity 規則不會導致無法排程；4. kubectl describe nodes 確認資源可用量。"
/>

<QuizQuestion
  question="16. 收集 KubeVirt 除錯資訊最全面的工具是什麼？"
  :options='[
    "kubectl get all -n kubevirt",
    "virtctl adm collect 或 must-gather 工具，自動收集所有 KubeVirt 元件 log 和狀態",
    "kubectl describe kubevirt -n kubevirt",
    "直接 ssh 到所有節點收集 journalctl 輸出",
  ]'
  :answer="1"
  explanation="KubeVirt 提供 must-gather 工具（oc adm must-gather 或 virtctl adm collect），自動收集所有 KubeVirt 相關元件（virt-api、virt-controller、virt-handler、virt-launcher）的 log、CR 狀態、Events、節點資訊等，打包成壓縮檔，方便送交技術支援或進行複雜問題分析。"
/>

<QuizQuestion
  question="17. KubeVirt Feature Gates 的設定位置在哪裡？"
  :options='[
    "每個 VMI 的 spec.domain.features 中設定",
    "KubeVirt CR（kubevirt/kubevirt）的 spec.configuration.developerConfiguration.featureGates",
    "/etc/kubevirt/feature-gates.yaml 設定檔",
    "kubevirt-config ConfigMap 的 feature-gates 欄位",
  ]'
  :answer="1"
  explanation="KubeVirt Feature Gates 在 KubeVirt CR（kubectl get kubevirt -n kubevirt）的 spec.configuration.developerConfiguration.featureGates 陣列中設定，是叢集級別的設定。舊版本（v0.58 前）使用 kubevirt-config ConfigMap，但現在以 KubeVirt CR 為主。"
/>

<QuizQuestion
  question="18. 在 VM YAML 中使用 nodeSelector 要求 VM 只排程到 GPU 節點，正確的路徑是？"
  :options='[
    "spec.nodeSelector",
    "spec.template.spec.nodeSelector",
    "spec.template.spec.domain.resources.requests 中指定 GPU",
    "spec.affinity.nodeAffinity",
  ]'
  :answer="1"
  explanation="VM 資源的 nodeSelector 設定在 spec.template.spec.nodeSelector（VMI 模板的 spec 下，不是 VM spec 下）。這等同於在 VMI spec.nodeSelector 設定，排程器會確保 VMI 只排程到具有這些 Label 的節點。"
/>

<QuizQuestion
  question="19. 執行 virtctl migrate my-vm 後，如何確認 Migration 完成且 VM 在新節點上執行？"
  :options='[
    "查看 kubectl get vmi my-vm -o yaml 中的 status.nodeName 確認節點改變，以及 kubectl get vmim 確認 Phase 為 Succeeded",
    "Migration 完成後 VM 會自動重啟，從重啟 Event 可確認",
    "執行 virtctl status my-vm 查看遷移狀態",
    "查看 virt-controller log 中的 migration completed 訊息",
  ]'
  :answer="0"
  explanation="Migration 完成後，可以：1. kubectl get vmi my-vm -o yaml 查看 status.nodeName 確認節點已改變（若成功）；2. kubectl get vmim -n <ns> 查看 VirtualMachineInstanceMigration 資源的 Phase 是否為 Succeeded；3. 查看 VMI Events 有 Migration Completed 相關記錄。"
/>

<QuizQuestion
  question="20. 在 Kubernetes 上部署 KubeVirt VM 時，哪個設定可以確保 VM 在節點維護期間自動遷移？"
  :options='[
    "在 NodeMaintenance 資源中設定 migrationPolicy",
    "在 VMI spec 的 evictionStrategy 設為 LiveMigrate",
    "為 VM 建立 PodDisruptionBudget（PDB）",
    "在 kubelet 設定 --eviction-hard 相關參數",
  ]'
  :answer="1"
  explanation="VMI spec.evictionStrategy: LiveMigrate（或 VM spec.template.spec.evictionStrategy）確保當 Kubernetes 對節點執行 drain（如節點維護、Cluster Autoscaler 縮容）時，自動觸發 Live Migration 而非強制終止 VMI，最大限度減少 VM 服務中斷。"
/>

<QuizQuestion
  question="21. 如何讓 KubeVirt VM 在重啟後保留自訂 cloud-init 設定的使用者密碼？"
  :options='[
    "cloud-init 資料每次重啟都重新套用，密碼每次都會重設，不應依賴 cloud-init 設定永久密碼",
    "在 userData 中使用 ssh_pwauth: true 並設定 chpasswd，首次啟動後密碼寫入 OS，後續重啟不再重設",
    "使用 AccessCredentials 資源注入的密碼才能持久保存",
    "需要安裝 Guest Agent 才能持久保存 cloud-init 密碼",
  ]'
  :answer="1"
  explanation="cloud-init 只在 VM 首次啟動時套用（使用 NoCloud 資料源時）。userData 中設定的 chpasswd 和 ssh_pwauth 在首次啟動寫入 OS 後即持久化存在 VM 磁碟中，後續重啟使用 VM 磁碟的密碼，不受 cloud-init 影響（除非磁碟重建）。"
/>

<QuizQuestion
  question="22. KubeVirt 的 AccessCredentials 資源主要用於解決什麼問題？"
  :options='[
    "管理 KubeVirt API 的 RBAC 存取控制",
    "在 VM 執行中動態注入 SSH 公鑰，無需修改 cloud-init 或重建 VM",
    "管理 VM 存取 PVC 的許可權控制",
    "設定 VM 的網路 ACL 規則",
  ]'
  :answer="1"
  explanation="AccessCredentials 允許動態注入 SSH 公鑰到執行中的 VM，不需要重建 VM 或重新啟動。透過 QEMU Guest Agent（SSH Public Key Injection）或 cloud-init（User Data），可以在 VM 執行時即時更新允許的 SSH 公鑰，非常適合需要輪換 SSH 金鑰的安全需求。"
/>

<QuizQuestion
  question="23. 為什麼建議在 KubeVirt VM 中安裝 QEMU Guest Agent？"
  :options='[
    "沒有 Guest Agent，VM 無法正常啟動",
    "提供 IP 地址回報、Application-consistent 快照、SSH 公鑰注入、凍結/解凍等功能，大幅提升 VM 可管理性",
    "Guest Agent 是 SR-IOV 網路的必要元件",
    "沒有 Guest Agent 無法執行 Live Migration",
  ]'
  :answer="1"
  explanation="QEMU Guest Agent 提供的功能：1. 向 KubeVirt 回報 VM 內部 IP（包含 Multus 網路）；2. Application-consistent 快照（fsfreeze/fsthaw）；3. SSH 公鑰動態注入（AccessCredentials）；4. 通知 KubeVirt OS 是否就緒；5. 執行 fsfreeze/fsthaw 指令。建議所有生產 VM 安裝。"
/>

<QuizQuestion
  question="24. KubeVirt 的 DataVolumeTemplates 欄位在 VM spec 中的用途是什麼？"
  :options='[
    "定義 VM 使用的 PVC 清單（預先建立好的）",
    "讓 VM 自動建立 DataVolume，CDI 負責匯入/填充磁碟，VM 在磁碟就緒後才啟動",
    "管理 VM 的儲存配額",
    "定義 VM 磁碟的備份排程",
  ]'
  :answer="1"
  explanation="VM spec.dataVolumeTemplates 允許在 VM 定義中內嵌 DataVolume 規格，當 VM 首次建立時，自動建立並觸發 CDI 匯入/填充流程。VM 的 WaitForVolumeBinding（readinessGate）確保 VM 在 DataVolume 的磁碟完全就緒前不啟動，避免使用空磁碟。"
/>

<QuizQuestion
  question="25. 執行 kubectl delete vm my-vm 後，關聯的 PVC 會發生什麼？"
  :options='[
    "PVC 和資料一起被刪除（Kubernetes Cascading Delete）",
    "取決於 VM 是否使用 DataVolumeTemplates；用 dataVolumeTemplates 建立的 DataVolume 和 PVC 會被刪除，預先存在的 PVC 不受影響",
    "PVC 永遠不會被刪除，需要手動清理",
    "只有 StorageClass 設為 Retain 時 PVC 才保留",
  ]'
  :answer="1"
  explanation="行為取決於 PVC 的建立方式：1. 透過 VM dataVolumeTemplates 建立的 DataVolume 和 PVC，在 VM 刪除時一起刪除（Owner Reference）；2. 預先存在的 PVC（VM 直接引用）不會因 VM 刪除而刪除，資料保留，需要手動清理。"
/>

<QuizQuestion
  question="26. 如何確認 KubeVirt 節點已正確啟用 KVM 虛擬化支援？"
  :options='[
    "執行 lscpu 確認 CPU 型號",
    "確認 /dev/kvm 裝置存在，且 kubectl describe node 中有 devices.kubevirt.io/kvm: 1 資源",
    "執行 systemctl status libvirtd 確認服務運行",
    "查看 virt-handler log 中的 KVM enabled 訊息",
  ]'
  :answer="1"
  explanation="確認 KVM 支援的方法：1. ls /dev/kvm 確認裝置存在；2. kubectl describe node <node> | grep kvm 確認節點有 devices.kubevirt.io/kvm: 1 資源（由 virt-handler DaemonSet 暴露）。若節點沒有 /dev/kvm，VM 將無法使用硬體加速，除非啟用 useEmulation。"
/>

<QuizQuestion
  question="27. KubeVirt 支援的 CPU 模式中，host-passthrough 模式有什麼特別限制？"
  :options='[
    "host-passthrough 只支援 Intel CPU，不支援 AMD",
    "使用 host-passthrough 的 VM 無法執行 Live Migration，因為目標節點可能有不同的 CPU 特性",
    "host-passthrough 需要 SR-IOV 網路才能使用",
    "host-passthrough 不支援 Windows VM",
  ]'
  :answer="1"
  explanation="host-passthrough 模式將主機 CPU 的所有特性直接傳遞給 VM，提供最佳 CPU 效能。但問題在於：若目標節點 CPU 型號不同，VM 遷移後可能遭遇 CPU 特性不符合，導致 Live Migration 失敗。生產環境建議使用 host-model（傳遞基準 CPU 特性集）以平衡效能和遷移能力。"
/>

<QuizQuestion
  question="28. 在 VM spec 中，如何指定 VM 使用 EFI（UEFI）韌體而非傳統 BIOS？"
  :options='[
    "spec.domain.firmware.bios: {useSeaBIOS: false}",
    "spec.domain.firmware: {bootloader: {efi: {}}}",
    "spec.domain.uefi: {enabled: true}",
    "spec.domain.features.smm: {enabled: true}",
  ]'
  :answer="1"
  explanation="在 VMI/VM spec.domain.firmware.bootloader.efi 中設定 UEFI 韌體，可選擇性設定 secureBoot: true（需要 Secure Boot）。EFI 通常配合 spec.domain.features.smm.enabled: true（System Management Mode，Secure Boot 需要）使用。Windows 11 虛擬機器需要 EFI + SMM + TPM。"
/>

<QuizQuestion
  question="29. 如何設定 VM 只能排程到特定的 Kubernetes 節點群組（例如只在 GPU 節點上運行）？"
  :options='[
    "在 KubeVirt CR 的 nodePlacement 設定全域排程限制",
    "在 VM spec.template.spec 中設定 nodeSelector 或 affinity，指定目標節點的 Label",
    "在 VMI 建立後使用 virtctl node-assign 指定節點",
    "設定 VM spec.template.spec.hostname 為目標節點名稱",
  ]'
  :answer="1"
  explanation="VM 排程限制透過 VM spec.template.spec.nodeSelector 或 spec.template.spec.affinity 設定，與 Kubernetes Pod 的排程機制完全一致。nodeSelector 是簡單的 Label 精確比對；affinity 支援更複雜的規則（Required/Preferred、In/NotIn 等）。這些設定最終套用到 virt-launcher Pod 的排程上。"
/>

<QuizQuestion
  question="30. 定期輪換 KubeVirt 內部 TLS 憑證（如 webhook 憑證）的機制是什麼？"
  :options='[
    "需要手動重建 KubeVirt Secrets 並重啟相關 Pod",
    "KubeVirt 的 virt-operator 內建憑證管理功能，定期自動輪換 TLS Secrets，無需人工介入",
    "透過外部 cert-manager 強制輪換，KubeVirt 本身不處理憑證輪換",
    "憑證有效期設為 100 年，實際上不需要輪換",
  ]'
  :answer="1"
  explanation="KubeVirt 的 virt-operator 內建憑證輪換機制（Certificate Rotation Controller），在憑證到期前自動輪換所有 KubeVirt 元件使用的 TLS Secrets（virt-api webhook、virt-handler、virt-exportproxy 等），整個過程無停機時間。KubeVirt CR 的 selfSigned 配置可調整輪換策略。"
/>
::: tip 🎯 完成測驗
恭喜完成全部 210 道 KubeVirt 測驗！

**建議學習路徑：**
- 答錯題目請回顧對應文件章節
- 基礎架構 → 核心元件 → API 與網路 → 儲存 → 進階功能 → 深入剖析 → 實用指南
- 建議分數：180 分（86%）以上代表掌握度良好
:::
