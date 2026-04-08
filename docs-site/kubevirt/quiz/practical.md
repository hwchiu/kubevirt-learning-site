---
layout: doc
title: KubeVirt — 📖 實用指南測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# 📖 實用指南測驗

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
