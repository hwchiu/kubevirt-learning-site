---
layout: doc
title: KubeVirt — 🚀 進階功能測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# 🚀 進階功能測驗

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
/>
