---
layout: doc
title: KubeVirt — ⚙️ 核心元件測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# ⚙️ 核心元件測驗

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
