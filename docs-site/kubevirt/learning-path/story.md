---
layout: doc
title: KubeVirt — 學習路徑 B：故事驅動式
---
<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>


# 📖 KubeVirt 學習之旅：阿明的故事

> 跟著阿明，從接到「把公司 VMware VM 搬進 K8s」這個任務開始，一步步理解 KubeVirt 的世界。
> 每個章節都是阿明真實遭遇的問題——你會看到他怎麼查文件、怎麼犯錯、怎麼一點一點把拼圖拼起來。

---

## 序章：一封改變阿明命運的信

星期一早上九點，阿明正靠在椅背上刷 Slack，咖啡還沒喝完。辦公室裡只有空調的白噪音，今天感覺會是個平靜的一天。

一封來自 VP Engineering 的信突然跳出來，主旨只有短短一行：「VM 遷移計畫——請 follow up」。

信的內容大意是：「阿明，我們決定在今年 Q3 把現有的 VMware 環境全部遷移到 Kubernetes 上。公司已經把大部分的 stateless service 容器化了，現在剩下一批跑在 vSphere 上的 VM——包括幾台資料庫、一台舊版的 Windows Server、還有 Legacy 的 .NET 應用，這些短期內無法容器化。業界有人把這種 VM 跑進 K8s 的方案，研究一下，這件事就交給你負責了。請你先做一份評估報告。」

阿明盯著螢幕，腦袋瞬間當機。

*K8s？我懂 K8s。VMware VM？我也懂。但是……怎麼把 VM 跑在 K8s 上？K8s 不是跑 Container 的嗎？*

他立刻打開瀏覽器，搜尋「run VM on Kubernetes」。第一個出現的是 KubeVirt 的官網。他點進去，看到一句話：

> *KubeVirt technology addresses the needs of development teams that have adopted or want to adopt Kubernetes but possess existing VM-based workloads that cannot be easily containerized.*

阿明愣了幾秒。「原來有人已經解決這個問題了。」

他把咖啡推到一旁，開始認真研究。KubeVirt 的核心想法其實很直覺——既然 K8s 已經是管理工作負載的標準平台，何不讓 VM 也成為 K8s 裡的「一等公民」？你不需要換掉 K8s，也不需要另立門戶，只要在 K8s 上加裝 KubeVirt，就能用 `kubectl` 管理 VM，就像管理 Deployment 一樣自然。

這個想法的吸引力在於**統一的管理面**。如果 VM 也能用 K8s 的 RBAC、監控、CI/CD pipeline 管理，那公司就不需要同時維護兩套截然不同的基礎設施——一套給容器，一套給 VM。整個 Platform Team 只要懂 K8s，就能同時管兩種工作負載。

但阿明心裡還有一個問題沒解答：「這到底是怎麼做到的？K8s 底層是 cgroups 和 namespace，VM 底層是 hypervisor——QEMU、KVM——這兩個東西的抽象層差很遠吧？」

他把這個問題記在筆記本上，打算繼續往下挖。今天要喝的咖啡估計涼了也不會想到去喝。

---

> ### 📚 去這裡深入了解
> 阿明的那個疑問——「K8s 本來就能跑 Container，為什麼還需要 KubeVirt？」——在這裡有完整的答案：
>
> - [系統架構概述](/kubevirt/architecture/overview) — 了解 KubeVirt 解決的核心問題，以及它的設計哲學，為什麼選擇「擴展 K8s」而不是「取代 K8s」
>
> 讀完後，你應該能清楚說明：KubeVirt 對 K8s 做了什麼樣的擴展？

<QuizQuestion
  question="阿明的老闆說：&quot;K8s 本來就能跑 Container，為什麼還需要 KubeVirt？&quot; 下列哪個答案最正確？"
  :options='[
    "KubeVirt 把 QEMU 包進 Pod，讓 VM 能繼承 K8s 的調度、監控、網路等整個生態系",
    "KubeVirt 是 K8s 的 fork 版本，專門為虛擬機最佳化",
    "KubeVirt 讓 K8s 不再需要 Container，改用 VM 來部署所有服務",
    "KubeVirt 是 VMware 官方出的 K8s 整合方案",
  ]'
  :answer="0"
  explanation="KubeVirt 透過 CRD 擴展 K8s，把 QEMU 跑在 Pod 裡，讓 VM 的生命週期、調度、網路都能接進 K8s 的標準工具鏈。它不是 fork、不是取代，而是 &quot;讓 VM 成為 K8s 一等公民&quot; 的擴充層。"
/>

---

## 第一章：KubeVirt 的基本輪廓

調查的第一天，阿明試著畫出 KubeVirt 的架構圖。他查了官方文件、翻了幾篇 blog，逐漸拼出一個輪廓。

KubeVirt 透過 Kubernetes 的 **Custom Resource Definition（CRD）** 機制，在 K8s 裡新增了兩種資源：

- **`VirtualMachine`（VM）**：代表一台 VM 的「期望狀態」，就像 Deployment 描述你想要幾個 Pod 一樣。
- **`VirtualMachineInstance`（VMI）**：代表一台實際**正在跑**的 VM 實例，就像 Pod 代表一個正在跑的容器。

阿明眼睛一亮：「所以 VM 跟 VMI 的關係，就像 Deployment 跟 Pod？」他試著寫下來：

```
VirtualMachine（VM）  →  管理生命週期（開機、關機、重啟策略）
        │
        └── 建立/管理 →  VirtualMachineInstance（VMI）  →  實際執行中的 VM
```

這個類比讓他瞬間有了方向感。你可以光建立一個 VMI（就像直接跑一個 Pod，刪掉就沒了）；也可以建立一個 VM，讓它幫你管理 VMI 的生命週期——VM 關機後 VMI 消失，但 VM 資源還在，下次開機再建新的 VMI。這讓「VM 的持久性」有了明確的語義：VM 的存在代表「我希望有這台機器」，VMI 的存在代表「這台機器現在正在跑」。

不過阿明還是有個疑惑：「那 VMI 到底是一個 Pod 嗎？它跑在哪裡？」

他繼續翻文件，找到了答案——每個 VMI 確實對應一個 Pod（叫做 `virt-launcher` Pod），QEMU 進程就跑在這個 Pod 裡面。這讓阿明有點驚訝，但細想又覺得合理：用 Pod 當容器，讓 K8s 原生的調度、資源管理、網路都能直接套用。換句話說，K8s 的 scheduler 在幫你決定 VM 跑在哪個 Node，K8s 的 resource quota 在限制 VM 能用多少 CPU 和記憶體——這些都不需要 KubeVirt 重新發明。

他還發現了一個細節：VMI 的 Pod 並不是一個普通的 Pod。它的 `securityContext` 需要特殊的 privilege 才能啟動 QEMU，而且它的 lifecycle 是被 `virt-handler`（後面章節會提到）嚴格控管的，不會像普通 Pod 一樣被 K8s 直接 restart。

「這設計還蠻聰明的，」他在筆記本上寫道，「用 K8s 的框架，但在框架裡塞了一個完全不同的執行引擎。」

---

> ### 📚 去這裡深入了解
> 阿明畫的那個架構圖，可以在這裡找到更完整的版本：
>
> - [系統架構概述](/kubevirt/architecture/overview) — 整體元件關係與設計理念
> - [VM 與 VMI 資源詳解](/kubevirt/api-resources/vm-vmi) — 深入了解 VM/VMI 這兩種 CRD 的欄位定義、生命週期與使用情境
>
> 讀完後，你應該能解釋：什麼時候要建 VM？什麼時候只建 VMI 就夠了？

<QuizQuestion
  question="阿明在圖上畫了 VirtualMachine 和 VirtualMachineInstance 兩個框。它們最關鍵的差別是什麼？"
  :options='[
    "VM 是持久化宣告（可開機關機），VMI 代表正在運行的實例（VM 開著才存在）",
    "VM 跑在 Master Node，VMI 跑在 Worker Node",
    "VM 是舊版 API，VMI 是新版 API，功能相同",
    "VM 定義網路設定，VMI 定義磁碟設定",
  ]'
  :answer="0"
  explanation="VM 是長期存在的資源物件，記錄了你的意圖（這台 VM 應該運行）；VMI 是 VM 開機後才產生的運行實例。關機後 VMI 消失，但 VM 物件仍在。這個分離讓 KubeVirt 可以做到 &quot;重開機後保持設定&quot;。"
/>

---

## 第二章：追蹤一台 VM 的誕生

調查的第三天，阿明決定用最笨的方式學習——跑一台 VM，然後一步步追蹤「到底發生了什麼事」。

他在測試環境 `kubectl apply` 了一個最簡單的 VM YAML。接著他同時開了三個終端機：一個跑 `kubectl get events -w`，一個跑 `kubectl get pods -n kubevirt -w`，一個跑 `kubectl get vmi -w`。他想親眼看到每個步驟，就像看一部慢動作影片。

他發現整個流程大概是這樣的：

**1. `virt-api`** — 請求進來時的第一道關卡。它是 KubeVirt 的 Webhook server，負責驗證和修改 VM/VMI 資源。你的 `kubectl apply` 最先打到它，它確認格式正確後才讓資源進 etcd。阿明在這裡故意寫了一個有錯的 YAML（把 `disk.bus` 寫成不存在的值），看到了 virt-api 直接回傳 validation error，這讓他理解了這個元件的功能。

**2. `virt-controller`** — K8s 裡的 Reconcile loop 主角。它監聽 VM 資源的變化，一旦發現「有 VM 應該要跑但還沒有對應的 VMI」，就幫你建立 VMI，再建出對應的 `virt-launcher` Pod。阿明看到在他 apply VM 後的幾秒鐘內，VMI 和一個新的 Pod 自動出現了。

**3. `virt-handler`** — 跑在每個 Node 上的 DaemonSet。當 `virt-launcher` Pod 被調度到某個 Node 後，那個 Node 上的 `virt-handler` 就接手，負責準備 VM 需要的資源（網路介面、磁碟），然後通知 `virt-launcher` 可以啟動了。這個元件讓阿明想到了 `kubelet`——同樣是每個 Node 上的 agent，負責把抽象的規格變成真實的執行環境。

**4. `virt-launcher`** — 每個 VMI 專屬的 Pod。它裡面跑著一個小型的 monitor 進程和一個 **QEMU/KVM** 進程，真正的 VM 就在這個 QEMU 裡執行。

阿明把這個流程畫在白板上：

```
kubectl apply VM
      │
      ▼
  virt-api（驗證 + Admission Webhook）
      │
      ▼
  virt-controller（Reconcile：建立 VMI + virt-launcher Pod）
      │
      ▼
  K8s Scheduler（決定 Pod 跑在哪個 Node）
      │
      ▼
  virt-handler（節點準備：網路/磁碟/cgroup 設定）
      │
      ▼
  virt-launcher Pod
      └── libvirtd + QEMU 進程 → VM 開機！
```

他在每個箭頭旁邊加上了問號——這些步驟的詳細實作他還不完全懂，但至少整個鏈條的輪廓清晰了。

「好，現在我知道整個鏈條了。」阿明自言自語，第一次覺得這件事是可以掌握的。接下來只需要把每個元件的細節填進去。

---

> ### 📚 去這裡深入了解
> 每個元件在這個流程中扮演的角色，都有詳細的原始碼層級分析：
>
> - [VM 生命週期](/kubevirt/architecture/lifecycle) — 從 apply 到 QEMU 啟動的完整狀態機
> - [virt-api](/kubevirt/components/virt-api) — Webhook 驗證與 API 入口
> - [virt-controller](/kubevirt/components/virt-controller) — Reconcile loop 設計
> - [virt-handler](/kubevirt/components/virt-handler) — 節點層的準備工作
> - [virt-launcher](/kubevirt/components/virt-launcher) — QEMU 的容器化包裝
>
> 如果你想真的理解「K8s 怎麼跑 VM」，這五篇是核心。

<QuizQuestion
  question="阿明 kubectl apply 了一個 VirtualMachine 物件後，是哪個元件負責偵測到這個事件並啟動後續流程？"
  :options='[
    "virt-controller — 它監聽 VM 物件的變化，建立對應的 VMI 並觸發調度",
    "virt-handler — 它在每個 Node 上監聽 API Server 的所有 VM 事件",
    "virt-api — 它接收 kubectl apply 後直接把 VM 交給 QEMU",
    "kubelet — K8s 的 kubelet 直接把 VM 當作特殊的 Pod 處理",
  ]'
  :answer="0"
  explanation="apply 之後的流程是：virt-api 驗證 → virt-controller 建立 VMI → kube-scheduler 調度 → virt-handler 在 Node 上準備環境 → virt-launcher Pod 啟動 QEMU。virt-controller 是這個鏈條的第一個執行者。"
/>

---

## 第三章：「這台 VM 要怎麼上網？」

VM 跑起來了，但阿明發現自己卡在網路這關。

業務單位的需求是：「這台 VM 要能從公司內網連進去，最好要有固定 IP。另外有一台舊系統的 VM 需要直接廣播 L2 封包，不能走 NAT。」

阿明打開 KubeVirt 的網路文件，發現光是 interface type 就有好幾種：`masquerade`、`bridge`、`sr-iov`……他看了五分鐘，腦袋開始打結。

他決定先從最常見的兩種搞清楚：

**Masquerade（偽裝模式）**：VM 的流量透過 `virt-launcher` Pod 的網路做 NAT。外面看到的是 Pod 的 IP，VM 本身在一個私有的網段裡（預設 `10.0.2.0/24`）。優點是設定簡單，K8s 環境裡幾乎不需要額外設定就能用；缺點是外部無法直接連進 VM——你必須透過 K8s Service 暴露 port，或用 `virtctl port-forward`。對於一般的 stateless 服務，masquerade 已經夠用了。

**Bridge（橋接模式）**：VM 的網路介面直接橋接到宿主機的某個介面，VM 可以拿到一個和宿主機同網段的 IP，外部可以直接連，L2 流量也能通過。看起來很美好，但阿明在測試時踩到一個坑——在某些 CNI 設定下，bridge 模式和 K8s 的 Pod 網路會互相干擾，需要搭配 **Multus CNI** 才能正常運作，讓 VM 同時有一張 CNI 管的網卡（給 K8s 用）和一張 bridge 管的網卡（給 VM 的外部存取用）。

他翻了半天文件，才搞清楚自己的問題：公司用的是 Calico 作為 CNI，預設情況下如果直接用 bridge 模式，Calico 的 policy enforcement 會出問題。解法是透過 Multus 建立第二張 network attachment，把 bridge interface 獨立出來。

阿明在 Jira 上新開了一張 ticket：「評估 Multus CNI 整合需求」，心裡想著：*這件事比我預期的複雜，但至少知道往哪個方向走了。*

「網路這塊真的比我想像的複雜。」阿明嘆了口氣，開了一張新的 Confluence 頁面開始記錄踩到的坑——以免下個接手的人也踩一遍。

---

> ### 📚 去這裡深入了解
> 網路是 KubeVirt 中最容易踩坑的地方，這兩篇讀完你會省很多時間：
>
> - [網路模型概述](/kubevirt/networking/overview) — 了解 KubeVirt 支援的各種網路模式與使用情境
> - [Bridge 與 Masquerade 深入解析](/kubevirt/networking/bridge-masquerade) — 兩種模式的原理差異、適用場景、與 CNI 的互動關係
>
> 讀完後，你應該能針對自己的 CNI 環境，選擇正確的網路模式。

<QuizQuestion
  question="阿明需要一台 VM 可以直接廣播 L2 封包（ARP broadcast），但又要讓另一台普通 VM 能對外上網。他應該分別選用哪種網路模式？"
  :options='[
    "L2 廣播需求選 bridge 模式；普通上網選 masquerade 模式（預設）",
    "兩台都用 masquerade，masquerade 本來就支援 L2 廣播",
    "L2 廣播需求選 masquerade；普通上網選 bridge",
    "兩台都用 SR-IOV，這樣效能最好也最靈活",
  ]'
  :answer="0"
  explanation="masquerade 是預設模式，透過 NAT 讓 VM 上網，但 VM 的 IP 對外不可見，也無法做 L2 廣播。bridge 模式讓 VM 直接接進宿主機的網路橋接器，可以廣播，但需要 Multus CNI 支援多個網路介面。"
/>

---

## 第四章：「資料存在哪裡？」

網路的問題暫時擱一旁，阿明轉向另一個更根本的問題：**VM 的磁碟要放哪裡？**

他在第一次測試時用的是 `containerDisk`——把 VM 的 disk image 打包成一個 Container image，從 registry 拉下來直接用。跑起來很快，VM 幾秒就起來了。但他很快就發現問題：在 VM 裡裝了一些套件、改了設定，然後用 `virtctl stop` 停機，再 `virtctl start` 重開——所有變更都消失了。

「這……是 ephemeral storage 嗎？」阿明查了文件，確認了自己的理解：`containerDisk` 本來就是設計成 read-only 的，它的 image 在每次 VMI 啟動時都是一個全新的 snapshot，適合測試、CI 環境、或 stateless 的工作負載，絕對不適合需要持久化資料的生產環境。

那正式環境要怎麼做？阿明找到了兩個方向：

**PVC（PersistentVolumeClaim）**：用 K8s 原生的 PVC 當 VM 的磁碟。這是最直覺的方式——你在 K8s 裡申請一塊 StorageClass 提供的持久化空間，然後掛到 VM 上。VM 重啟資料還在，因為資料在 PV 裡，不在 Pod 裡。阿明在測試環境把 StorageClass 換成 Longhorn，`hostPath`，直接用 PVC 掛磁碟，資料持久化問題解決了。

**DataVolume**：這是 CDI（Containerized Data Importer）提供的 CRD，可以說是「聰明版的 PVC」。你可以在 DataVolume 裡指定一個 source（比如 HTTP URL、S3 bucket、或另一個 PVC），CDI 會幫你把資料匯入到一個新的 PVC，匯入完成後自動讓 VM 可以使用。這對「從現有 VM image 建立 VM」的情境特別有用——阿明公司的 VMware VM 都有現成的 VMDK 或 QCOW2 image，透過 DataVolume 可以直接指定一個 HTTP URL，CDI 就會幫你把 image 拉下來、轉成正確的格式、存進 PVC，整個流程自動化。

阿明用 DataVolume 成功把一個測試用的 QCOW2 image 匯入後，對著螢幕說：「終於，有個辦法可以把現有的 VM image 搬進來了。」

這是他在整個調查過程中第一次感覺到整件事「有可能做到」的時刻。他在筆記本上寫下：*CDI 是這個計畫的關鍵拼圖之一。*

---

> ### 📚 去這裡深入了解
> 儲存這塊牽涉到 KubeVirt 和 CDI 兩個專案的互動，值得仔細讀：
>
> - [儲存架構概述](/kubevirt/storage/overview) — 了解 KubeVirt 支援的儲存類型與選擇策略
> - [ContainerDisk 詳解](/kubevirt/storage/container-disk) — 什麼情況適合用、什麼情況一定不能用
> - [PVC 與 DataVolume](/kubevirt/storage/pvc-datavolume) — 如何從現有 image 匯入、如何讓 VM 使用持久化磁碟
>
> 讀完後，你應該能根據工作負載特性，選擇正確的儲存方案。

<QuizQuestion
  question="阿明的資料庫 VM 需要儲存持久化資料，但 CI 環境的測試 VM 每次都要全新乾淨的系統。下列哪個組合最合適？"
  :options='[
    "資料庫 VM 用 DataVolume（PVC backed），測試 VM 用 containerDisk",
    "兩台都用 containerDisk，比較簡單",
    "兩台都用 DataVolume，比較安全",
    "資料庫 VM 用 containerDisk，測試 VM 用 DataVolume",
  ]'
  :answer="0"
  explanation="containerDisk 是 ephemeral 的，VM 重啟後資料消失，適合每次都要全新環境的測試 VM。DataVolume 背後是 PVC，資料持久保存，適合資料庫這類需要狀態的工作負載。"
/>

---

## 第五章：阿明的第一次實操

看了兩個禮拜的文件，阿明覺得是時候真的動手了。評估報告的第一個 milestone 是：「在測試環境跑起一台可以 SSH 進去的 Linux VM」。

他在自己的測試 cluster 上裝好 KubeVirt，打算跑一台簡單的 Fedora Cloud VM。他照著 quickstart 寫了一個 VM YAML：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: fedora-test
spec:
  running: false
  template:
    spec:
      domain:
        devices:
          disks:
            - name: containerdisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
        resources:
          requests:
            memory: 1Gi
      networks:
        - name: default
          pod: {}
      volumes:
        - name: containerdisk
          containerDisk:
            image: quay.io/kubevirt/fedora-cloud-container-disk-demo
```

`kubectl apply` 成功了，但 VM 沒有自動啟動。阿明等了一分鐘，VM 一直是 `Stopped` 狀態。他翻了一下 VM 的 spec，發現 `running: false`——他沿用了文件裡的範例，忘了改這個值。

這是他遇到的第一個坑，也是最蠢的一個。

他學到了 **`virtctl`** 這個 CLI 工具——它是 KubeVirt 的配套指令，讓你用人話操作 VM：

```bash
virtctl start fedora-test      # 開機
virtctl stop fedora-test       # 關機（ACPI shutdown）
virtctl pause fedora-test      # 暫停（保持記憶體狀態）
virtctl console fedora-test    # 接上 serial console（救命用）
virtctl ssh fedora-test        # SSH 進去（需要 VM 裡有 SSH server）
```

VM 終於跑起來後，阿明試著用 `virtctl console` 進去，卻發現畫面一直在等待，沒有 login prompt，只有幾行 BIOS 訊息後就靜止了。他 Google 了一下，發現問題出在 Fedora Cloud image 需要設定 **cloud-init** 才會啟動 getty。他少加了一個 `cloudInitNoCloud` volume——這個 volume 要提供一個 user-data 設定，告訴 cloud-init 要建立哪些使用者、要不要啟動 SSH server。

加上去之後：

```yaml
- name: cloudinit
  cloudInitNoCloud:
    userDataBase64: |
      I2Nsb3VkLWNvbmZpZwp1c2VyczogW3tuYW1lOiBmZWRvcmEsIHBhc3N3b3JkOiB0ZXN0MTIzLCBzdWRvOiBBTEw9KEFMTCkgTk9QQVNTV0Q6IFRSVUV9XQpzc2hfcHdhdXRoOiB0cnVl
```

VM 終於正常開機，login prompt 出現了。阿明用 `fedora / test123` 登入成功。

他對著終端機螢幕笑了出來，截圖傳給同事：「我在 K8s 裡跑了一台 VM！」

---

> ### 📚 去這裡深入了解
> 第一次操作最容易在這兩個地方卡住，建議搭配讀：
>
> - [快速入門指南](/kubevirt/guides/quickstart) — 從零到第一台 VM 的完整步驟，包含常見錯誤排除
> - [virtctl 操作手冊](/kubevirt/virtctl/guide) — 所有常用指令的說明與範例
>
> 讀完後，你應該能獨立跑起一台 VM，並用 virtctl 進行基本操作。

<QuizQuestion
  question="阿明的 VM 已經在 Running 狀態，但沒有設定 NodePort Service。他想直接 SSH 進 VM，正確的 virtctl 指令是什麼？"
  :options='[
    "virtctl ssh <vm-name>",
    "virtctl console <vm-name>（用序列埠連入後再執行 sshd）",
    "kubectl exec -it virt-launcher-<hash> -- ssh root@localhost",
    "virtctl port-forward <vm-name> 22:22 然後 ssh localhost",
  ]'
  :answer="0"
  explanation="virtctl ssh 直接建立一條透過 K8s API 的 SSH tunnel 連入 VM，不需要 NodePort 或 LoadBalancer。virtctl console 是連序列埠，適合沒有 SSH 的緊急場景，但不是 SSH。port-forward 雖然可行但比較麻煩。"
/>

---

## 第六章：「客戶說 VM 不能停機」

就在阿明準備提交評估報告時，業務主管突然補了一個需求：「順便確認一下，我們在更新 KubeVirt 版本或做 Node 維護的時候，VM 不能被強制停機——我們有幾台 VM 跑的是 24/7 的金融服務，就算是維護視窗，停機也需要走一個月的申請流程。」

阿明停頓了一秒。他知道這個需求在 VMware 世界有個名字：**vMotion**。

在 KubeVirt 裡，對應的功能叫 **Live Migration**。

原理是：在 VM 還在跑的情況下，把 VM 的記憶體狀態（Memory State）從一個 Node 逐步複製到另一個 Node，等差異量夠小了，瞬間切換，整個過程 VM 幾乎不會感覺到中斷——網路連線還在，硬碟還在，進程還在跑，只是「換了一台宿主機」。

觸發 Live Migration 的方式是建立一個 `VirtualMachineInstanceMigration` 資源：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstanceMigration
metadata:
  name: migration-job
spec:
  vmiName: my-vm
```

KubeVirt 接收到這個資源後，`virt-controller` 就會找一個合適的目標 Node，開始啟動 migration 流程。你可以透過 `kubectl get vmim migration-job -o yaml` 追蹤進度。

但阿明很快發現，Live Migration 有幾個前提條件——如果環境不符合，migration 會直接失敗，甚至連試都不讓你試：

1. **儲存必須是 ReadWriteMany（RWX）**：VM 的磁碟必須能讓 source Node 和 target Node 同時掛載（因為在 migration 期間，兩邊都需要存取）。一般的 RWO PVC 是不行的，必須用支援 RWX 的 StorageClass，例如 NFS、CephFS、或 Longhorn 的 RWX 模式。
2. **CPU 型號要相容**：Source 和 Target Node 的 CPU 如果差異太大（例如 Intel vs AMD），VM 裡的 CPU feature flag 可能在 target 上不支援，migration 就會失敗。KubeVirt 提供了 `cpu.model: host-passthrough` 的選項，但這樣就只能在相同 CPU 型號的 Node 上 migrate。
3. **網路頻寬**：Migration 期間需要大量頻寬傳輸記憶體，如果 VM 記憶體很大（例如 64GB）且記憶體寫入速度很快，migration 的 pre-copy 過程可能遲遲無法收斂，最終 timeout。

「這比我想的要複雜，」阿明在 Confluence 上寫道，「但至少是可行的。需要在 storage 選型時就考慮 RWX，這要列進 Prerequisites。」

他把這三個限制列進了評估報告的「前提條件」章節，並在旁邊標注：*這是整個計畫的 critical path，storage 架構要優先確定。*

---

> ### 📚 去這裡深入了解
> Live Migration 是 KubeVirt 裡最精彩的技術之一，原理值得深入了解：
>
> - [Live Migration 概述](/kubevirt/advanced/live-migration) — 什麼是 Live Migration、如何觸發、有哪些限制
> - [Migration 內部機制深度剖析](/kubevirt/deep-dive/migration-internals) — 記憶體複製的細節、Pre-copy 策略、如何追蹤 migration 進度
>
> 讀完後，你應該能規劃一個支援 Live Migration 的 KubeVirt 部署方案。

<QuizQuestion
  question="客戶說 VM 不能停機，所以阿明計畫使用 Live Migration。下列哪個條件是 Live Migration 的必要前提？"
  :options='[
    "VM 的磁碟必須掛載 ReadWriteMany (RWX) 的 PVC，讓兩個 Node 能同時存取",
    "Node 必須使用相同廠牌的 CPU，確保指令集相容",
    "VM 必須使用 masquerade 網路模式，bridge 模式不支援遷移",
    "VM 必須事先關機，KubeVirt 的 Live Migration 其實是冷遷移",
  ]'
  :answer="0"
  explanation="Live Migration 的核心前提是磁碟需要 RWX（ReadWriteMany）存取模式，讓來源 Node 和目標 Node 能同時讀寫同一份資料。containerDisk 也支援（因為是 image 不是 block device）。CPU 相容性 K8s 調度器會處理，網路模式不影響遷移能力。"
/>

---

## 第七章：「這台 VM 好慢，老闆在催了」

Live Migration 的問題還沒完全解決，業務單位已經開始用第一批遷移進來的 VM 了。

壞消息在某個週三下午傳來——是一封釘釘訊息，來自業務部門的 PM：「阿明，那台跑我們訂單系統的 VM，在塞車時段跑起來超慢的，CPU 是不是不夠？當初在 VMware 上跑得好好的，現在怎麼這樣？」

阿明看了一眼監控，VM 分配了 4 個 vCPU、8GB 記憶體，使用率頂多 60%，不像是資源不足的樣子。但 PM 說慢，他不能只說「看起來沒問題」就算了。

他決定深入查一下 vCPU 是怎麼運作的。

原來問題在於**預設的 vCPU 排程方式**。在 KubeVirt 預設模式下，vCPU 是作為普通的執行緒在宿主機的 CPU 上排程。這意味著 K8s 的 CPU manager 可能把這個 Pod 的執行緒排到不同的 NUMA node 上，造成記憶體存取延遲變高。對於一般的 web service，這幾乎沒差；但對於計算密集、或對延遲敏感的工作負載，這就是一個隱形的效能殺手。

解法之一是啟用 **CPU 固定（CPU Pinning）**——讓 VM 的 vCPU 固定綁定在宿主機的特定 physical CPU 上，不再和其他 Pod 競爭 CPU time，也確保 NUMA 親和性。要用這個功能，需要在 VM spec 裡設定 `cpu.dedicatedCpuPlacement: true`，同時 K8s 端的 CPU manager policy 必須是 `static`，而且 VM 的 CPU request 必須設成 integer（不能是小數）。

阿明在測試環境把這些條件都設好，重跑 benchmark，延遲 p99 從 340ms 掉到 89ms。

他呆了幾秒。「就這樣？」

他繼續挖，又發現了另一個問題：VM 的磁碟用的是 `sata` bus，而不是 `virtio`。`sata` 是模擬的設備，走的是軟體模擬的 I/O stack；`virtio` 是半虛擬化的設備，Guest OS 知道自己在虛擬環境裡，可以直接和 hypervisor 溝通，I/O 效率高很多。他把磁碟改成 `virtio`，順道把網卡也從 `e1000` 換成 `virtio`，重新測試，磁碟 IOPS 成長了將近三倍。

「我之前根本不知道這些東西。」他在 Confluence 上開了一篇「VM 效能調教最佳實踐」，把這些發現全部記下來，列成一個 checklist：在建立 production VM 時，這些選項都應該預設確認一遍。

他回覆 PM：「調整了幾個效能設定，再測一下看看。」兩天後 PM 回說「好多了」。

---

> ### 📚 去這裡深入了解
> VM 效能是一個很深的兔子洞，從 CPU 拓樸到記憶體大頁都有影響：
>
> - [VM 最佳化進階指南](/kubevirt/deep-dive/vm-optimization) — CPU Pinning、NUMA 親和性、Realtime VM、Hugepages 的完整設定與原理分析
> - [效能調校指南](/kubevirt/deep-dive/performance-tuning) — virtio 設備選型、I/O 效能基準測試方法、Guest OS 側的調校
>
> 讀完後，你應該能為不同類型的 VM workload 制定效能調教策略，而不是靠猜測。

<QuizQuestion
  question="老闆說那台跑財務計算的 VM 太慢。阿明發現 vCPU 一直在不同實體 Core 之間跳來跳去。他應該開啟哪個設定來改善這個問題？"
  :options='[
    "CPU Pinning — 把 vCPU 固定在特定實體 CPU core，避免跨 core 遷移造成 cache miss",
    "Huge Pages — 讓 VM 使用大記憶體頁，降低 TLB miss 頻率",
    "NUMA Topology — 把 VM 的 CPU 和記憶體放在同一個 NUMA node 上",
    "Realtime vCPU — 賦予 vCPU 最高的系統排程優先權",
  ]'
  :answer="0"
  explanation="CPU Pinning 把每個 vCPU 固定對應到特定的實體 CPU Core，避免 vCPU 在不同 Core 間遷移造成的 CPU cache 失效（cache thrashing）。這是提升計算密集型 VM 效能最直接有效的手段。Huge Pages 和 NUMA 是進一步的補充優化。"
/>

---

## 第八章：「VM 掛掉了，我是最後一個知道的」

某個週五深夜 2:17，阿明的手機震動了。

不是 KubeVirt 的告警，是應用層的告警——訂單系統沒有回應，業務部門的 oncall 打來了。

阿明爬起來查，花了快 20 分鐘才確定是那台 VM 的問題。不是網路，不是應用 bug，是 VM 本身莫名其妙進入了 `Failed` 狀態，Pod crash 了。查 `kubectl describe vmi` 才看到 `virt-launcher` Pod 在一個小時前就已經 OOMKilled——記憶體設定太保守了。

但那一個小時什麼都沒發生，沒有告警，沒有人知道。

「我根本不知道 VM 有沒有在跑，有沒有異常。」阿明意識到一個盲點：他在 K8s 的應用層有完整的 Prometheus + Grafana 監控，但對 VM 本身的狀態是瞎的。

他開始研究 KubeVirt 的可觀測性。KubeVirt 本身暴露了相當豐富的 Prometheus metrics，涵蓋 VMI 的生命週期狀態、Live Migration 的進度、vCPU 使用率、記憶體 balloon 狀態等。這些 metrics 的 endpoint 在 `virt-api` 和 `virt-handler` 上都有，只要 Prometheus 有抓到這些 target，就能把 VM 的狀態接進現有的告警系統。

他設定了幾條核心的告警規則：
- VMI 進入 `Failed` 或 `Unknown` 狀態立刻觸發
- Live Migration 超過 15 分鐘未完成觸發警告
- `virt-launcher` Pod 被 OOMKilled 觸發告警

他把這些接進公司既有的 PagerDuty，做了一個 Grafana dashboard，把所有 VM 的狀態一覽無遺地呈現出來。

「如果上週有這個，我就不用凌晨兩點才知道 VM 掛了。」他提交了 PR，把監控設定接進公司的 GitOps repo 裡，讓它成為 KubeVirt 部署的標準配置之一。

---

> ### 📚 去這裡深入了解
> 沒有可觀測性的系統就像開車不看儀表板——遲早出問題：
>
> - [Observability 與監控](/kubevirt/advanced/observability) — KubeVirt 暴露的 Prometheus metrics 完整列表、如何設定 ServiceMonitor、建議的告警規則與 Grafana dashboard 設計
>
> 讀完後，你應該能為 KubeVirt 環境建立足以在生產環境使用的監控告警體系。

<QuizQuestion
  question="凌晨 2 點的 OOM 讓阿明決定建立告警。為了在記憶體問題發生前就收到通知，最適合設定的 alert 條件是什麼？"
  :options='[
    "VM 記憶體使用率超過 85%（預警）和 95%（緊急）的閾值告警",
    "只在 VM 已經 OOM Killed 後才觸發告警，避免誤報",
    "監控 Node 的總記憶體，在整個 Node 記憶體不足時告警",
    "監控 virt-launcher Pod 的 CPU usage，間接推斷記憶體壓力",
  ]'
  :answer="0"
  explanation="好的告警設計是在問題發生前就預警。設定 85% 的 warning 和 95% 的 critical 可以讓你在 OOM 真正發生前就有時間處理。事後告警（OOM 後才通知）等於是事後報告，無法避免停機。"
/>

---

## 第九章：「那台資料庫 VM 如果磁碟壞了呢？」

凌晨 2 點那次事件讓阿明的神經緊繃了整整一週。

那台 VM 只是 OOM，資料沒有損失，重啟就好了。但他腦子裡有個問題一直揮不去：*如果是磁碟壞了呢？如果是 PV 的底層儲存出問題，資料直接消失了呢？*

最讓他擔心的是那台 PostgreSQL 資料庫 VM。它存著公司過去三年的訂單資料，任何一次資料遺失都是災難性的。

他去查了 KubeVirt 的 Snapshot 功能。

**`VirtualMachineSnapshot`** 是 KubeVirt 提供的 CRD，讓你可以在不停機的狀態下對 VM 建立 consistent snapshot（需要 Guest Agent 配合）。Snapshot 的底層依賴 CSI VolumeSnapshot，也就是說，你的 StorageClass 必須支援 CSI snapshot 才能用這個功能。

阿明建了第一個 snapshot：

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: postgres-snap-20240310
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: postgres-vm
```

幾分鐘後 snapshot 的 `ReadyToUse` 變成 `true`。他試著用 **`VirtualMachineRestore`** 把 snapshot 還原到一個新的 VM 上，確認資料完整——成功了。

他發現 snapshot 還可以用來做**環境複製**：從 production VM 的 snapshot clone 出一個 staging VM，讓 QA 可以在幾乎完全相同的環境下測試，而不需要手動搬資料。他試了一下，用 `VirtualMachineClone` 從 snapshot 建出一台 staging-postgres，完整複製了 production 的磁碟狀態。

「這個我可以自動化。」他在腦子裡已經開始規劃：每天凌晨 3 點對幾台關鍵 VM 建 snapshot，保留七天，老的自動刪除——就像 RDS 的 automated backup，只是這次是他自己用 CronJob 實現的。

他把這個計畫寫進了運維 runbook：*「KubeVirt VM 快照與備份策略」*。

---

> ### 📚 去這裡深入了解
> 快照、複製、還原——這三個功能共同構成了 VM 的資料保護基礎：
>
> - [Snapshot & Restore](/kubevirt/advanced/snapshots) — 如何建立 VirtualMachineSnapshot、觸發條件、Guest Agent 的必要性、常見的失敗原因
> - [Snapshot、Clone 與 Export API](/kubevirt/api-resources/snapshot-clone) — VirtualMachineSnapshot、VirtualMachineRestore、VirtualMachineClone 的 CRD 欄位與使用情境
> - [高可用與災難恢復](/kubevirt/guides/ha-dr) — 如何規劃 KubeVirt 的 HA 架構、storage 選型對 DR 的影響、備份策略的設計原則
>
> 讀完後，你應該能為生產環境的 VM 設計一套完整的備份與恢復方案。

<QuizQuestion
  question="阿明想建立一個資料庫 VM 的快照，然後用它建立一個給 QA 測試用的複製環境。下列哪個工作流程最正確？"
  :options='[
    "建立 VirtualMachineSnapshot → 從 Snapshot 建立 VirtualMachineClone → QA 取得完整的 VM 複製品",
    "直接 kubectl cp 把 VM 的 QCOW2 檔案複製出來，再建一台新 VM 掛上去",
    "先把 VM 關機，複製 PVC，再把複製的 PVC 掛到新 VM 上",
    "用 velero 備份整個 namespace 然後 restore 到 QA namespace",
  ]'
  :answer="0"
  explanation="VirtualMachineSnapshot 可以在 VM 運行中建立一致性快照（不只是磁碟，還有完整的 VM 設定）。VirtualMachineClone 可以從 snapshot 建立完整的 VM 副本，包含設定和資料。這整套 API 是 KubeVirt 原生支援的備份/複製工作流程。"
/>

---

## 第十章：「KubeVirt 要升版了，但 VM 不能停」

季度安全檢查的時候，資安團隊丟來一份 CVE 清單，其中一條是 KubeVirt 的安全漏洞——`virt-api` 的某個 validation path 有問題，需要升版修補。

阿明看了一下版本，目前跑的是 v1.1.0，需要升到 v1.2.1。

他的第一反應是恐慌：「升版會不會讓 VM 重開機？」

他翻了升版文件，才慢慢冷靜下來。KubeVirt 的升版由 **virt-operator** 全程管理——你只需要把 `KubeVirt` CR 裡的版本號改掉，virt-operator 就會按照 `InstallStrategy` 開始滾動升版：先升 virt-api、virt-controller（這些是 stateless 的 Deployment，rolling update 幾乎無感），然後是 virt-handler（DaemonSet，每個 Node 依序升）。

最複雜的部分是 **WorkloadUpdateController**。當 virt-handler 版本更新後，已經跑著的 VMI 用的是舊版的 `virt-launcher`，新舊版本之間可能有相容性問題。KubeVirt 的預設策略是：

1. **LiveMigrate 優先**：先嘗試把 VMI live migrate 到另一個 Node，新的 virt-launcher 就是新版本的。
2. **Evict 備用**：如果 VMI 不支援 Live Migration（例如磁碟是 RWO），就把 VM stop 然後在原地重啟，用新的 virt-launcher 啟動。
3. **批次節流**：預設每 60 秒最多處理 10 台，避免大批 VM 同時 migrate 把網路打爆。

阿明整個升版過程盯著 `kubectl get vmi -w` 看，看著 VM 們一台一台靜靜地被 migrate 到新節點，然後繼續跑，整個過程業務完全無感。只有一台跑 batch job 的 VM 因為用 RWO PVC 不能 migrate，被 stop 後重啟，停了大概 30 秒——但那台本來就是可以短暫停機的 VM。

「原來升版可以這麼安靜。」他看著最後一台 VMI 完成 migration，發了一封 email 給資安團隊：「KubeVirt 已升級至 v1.2.1，修補完成，無服務中斷。」

---

> ### 📚 去這裡深入了解
> 升版策略是 KubeVirt 裡設計最精緻的部分之一，值得從原始碼層級理解：
>
> - [升級策略與機制](/kubevirt/deep-dive/upgrade-strategy) — virt-operator InstallStrategy 的實作、WorkloadUpdateController 的批次邏輯（defaultBatchDeletionIntervalSeconds、defaultBatchDeletionCount）、LiveMigrate vs Evict 的決策流程
>
> 讀完後，你應該能在升版前規劃好哪些 VM 需要提前遷移、哪些可以接受短暫停機，並且知道如何監控升版進度。

<QuizQuestion
  question="阿明要把 KubeVirt 從 v0.58 升到 v0.60，他設定了 workloadUpdateStrategy: LiveMigrate。這代表升版時會發生什麼事？"
  :options='[
    "所有使用舊版 virt-launcher 的 VMI 會透過 Live Migration 自動遷移到新版的 Pod，VM 不需要重開機",
    "所有 VM 會立刻被強制關機，等新版 virt-launcher 就緒後再自動開機",
    "LiveMigrate 只影響網路設定，磁碟和記憶體的升版仍需手動重啟",
    "升版後需要手動對每台 VM 執行 virtctl migrate 才能觸發遷移",
  ]'
  :answer="0"
  explanation="WorkloadUpdateStrategy: LiveMigrate 讓 KubeVirt 的 WorkloadUpdateController 自動把運行中的 VMI 透過 Live Migration 遷移到新版的 virt-launcher Pod。整個過程對 VM 內部幾乎無感，業務不需要停機。"
/>

---

## 第十一章：那台 Windows Server 的特殊個性

遷移計畫進入收尾階段，剩下最後一台：一台跑著 IIS 和舊版 ASP.NET 應用的 **Windows Server 2019**。

這台 VM 從一開始就讓阿明覺得它不好對付。Linux VM 有 cloud-init 可以在第一次開機時自動設定 hostname、SSH key、帳號密碼；Windows 有自己的初始化機制叫做 **Sysprep**，而且它對虛擬化環境的設備驅動有特別的要求。

首先是驅動的問題。Windows 原生不認識 virtio 設備——它認識 IDE、SATA、e1000 網卡，因為那些都是標準的模擬設備。但如果要有像樣的 I/O 效能，就必須裝 **virtio-win 驅動**，讓 Windows 能使用 virtio 磁碟和網卡。阿明的做法是：在 DataVolume 裡準備好 Windows 的 ISO，同時用另一個 DataVolume 掛入 virtio-win 的 ISO，在 VM 第一次開機時進到安裝程式，先把 virtio 驅動裝好，再繼續安裝 Windows。

這個過程有點繁瑣，但只需要做一次。裝好之後，他把這個 Windows 磁碟 snapshot 起來，作為後續 Windows VM 的基礎映像。

接著是初始化。他在 VM spec 裡設定了 `cloudInitNoCloud`（KubeVirt 支援用 cloud-init 傳入 Sysprep 設定），但第一次嘗試時 VM 開機後根本沒有執行 Sysprep——阿明後來才發現原來 cloud-init for Windows 需要在 Guest 裡裝 **cloudbase-init**，才能接收 KubeVirt 傳入的設定。他補裝了 cloudbase-init，重新測試，VM 終於在第一次開機時自動設定好 hostname 和 Administrator 密碼。

整個過程花了他整整兩天，踩了快十個坑，每個坑都記在 Confluence 上。他在頁面頂端寫了一句話：

> *Windows VM 的遷移步驟比 Linux 複雜兩倍，但只要照這份 runbook 做，應該不用再踩我踩過的坑。*

最後這台 Windows Server 上線的時候，阿明喝了一口咖啡，感覺整件事終於真的結束了。

---

> ### 📚 去這裡深入了解
> Windows VM 有一套和 Linux 完全不同的初始化流程，值得事先讀清楚再動手：
>
> - [VM 初始化深入分析](/kubevirt/deep-dive/vm-initialization) — CloudInit、Sysprep、ContainerDisk 在 VM 開機時的完整執行鏈，從 spec 到 QEMU 的每一個步驟
> - [Windows VM 最佳化](/kubevirt/deep-dive/windows-optimization) — virtio-win 驅動安裝、cloudbase-init 設定、Windows 特有的效能調教（ACPI、Hyper-V enlightenments）
>
> 讀完後，你應該能獨立完成一台 Windows Server VM 的從零遷移，而不需要靠碰運氣。

<QuizQuestion
  question="阿明的 Windows Server VM 開機了，但磁碟速度奇慢，網路也半死不活。最可能的原因是什麼？"
  :options='[
    "VM 使用了模擬的 IDE/e1000 設備，沒有安裝 virtio-win 半虛擬化驅動",
    "Windows VM 需要比 Linux VM 多分配兩倍的 CPU 才能正常運行",
    "KubeVirt 對 Windows 的 Live Migration 有 bug，會影響效能",
    "Windows 需要 GPU passthrough 才能讓磁碟和網路正常工作",
  ]'
  :answer="0"
  explanation="在 KubeVirt 上，Windows VM 預設可能使用模擬的低效設備（如 IDE 磁碟控制器、e1000 網卡）。安裝 virtio-win 驅動後，Windows 就能使用 virtio-blk/virtio-net 等半虛擬化設備，效能可以提升數倍。這是 Windows VM 效能調教的第一步。"
/>

---

## 第十二章：「這張網卡不夠用——SR-IOV 上場」

第一批 VM 上線一個月後，有一個新的需求找上門了。

負責網路封包處理的團隊想把一個舊的 DPDK 應用從實體機搬進來。阿明看了一下這個應用的需求：它需要直接操作網卡的 DMA，繞過 kernel network stack，延遲要求在微秒級。

阿明皺起眉頭。這個不是普通的 VM，這是一個對網路效能有極端要求的工作負載。他試了一下用 masquerade 跑，延遲爆到毫秒級，完全不行。bridge 模式好一些，但仍然有軟體轉發的開銷。

同事說：「能不能用 SR-IOV？」

阿明這才認真去研究 SR-IOV 的原理。SR-IOV（Single Root I/O Virtualization）是一個 PCIe 規格，讓一張實體網卡（PF，Physical Function）可以切出多個虛擬網卡（VF，Virtual Function），每個 VF 可以直接分配給一個 VM，讓 VM 的網路流量完全繞過 hypervisor 的虛擬化層，直接和硬體對話。延遲可以逼近裸機，幾乎沒有 overhead。

代價是靈活性——SR-IOV 的 VF 綁定在特定的 Node 和 PF 上，VM 就沒辦法 live migrate 到一個沒有相同 SR-IOV 設備的 Node。另外，設定比 masquerade 複雜很多：要先在 Node 上開啟 SR-IOV、設定 VF 數量、讓 K8s 的 device plugin 管理這些 VF，最後才能在 VM spec 裡宣告要用 SR-IOV 的網卡。

阿明和網路團隊花了整整一天配置環境，踩到了一個坑：Node 上的 BIOS 預設沒開 SR-IOV，要進 BIOS 手動開。這件事在文件上寫得很隱晦，是靠一個 Stack Overflow 的回答才找到解法的。

最後 DPDK 應用跑起來，延遲降到了 50 微秒。網路團隊的人站在螢幕前說：「比我預期的好。」阿明難得得意地笑了一下。

---

> ### 📚 去這裡深入了解
> SR-IOV 的設定涉及 Node 層的硬體配置，值得從頭讀清楚再動手：
>
> - [SR-IOV 與進階網路](/kubevirt/networking/sriov) — SR-IOV 的工作原理、K8s device plugin 的角色、VM spec 的設定方式、Live Migration 限制與替代方案
>
> 讀完後，你應該能判斷什麼時候需要 SR-IOV、什麼時候 bridge 已經夠用。

<QuizQuestion
  question="DPDK 應用跑在 KubeVirt VM 裡，用 SR-IOV VF 直通給 VM。但阿明發現這台 VM 無法 Live Migration。原因是什麼？"
  :options='[
    "SR-IOV VF 綁定在特定 Node 的特定實體網卡（PF）上，無法像普通 PVC 一樣在遷移時跟著 VM 移動",
    "SR-IOV 模式下 KubeVirt 的 virt-handler 不支援遷移協議",
    "Live Migration 需要 masquerade 網路模式，SR-IOV 和 masquerade 互不相容",
    "DPDK 應用佔用了 100% CPU，導致 Live Migration 的計算資源不足",
  ]'
  :answer="0"
  explanation="SR-IOV 的 VF（Virtual Function）是實體網卡 PF（Physical Function）切出來的，它綁定在特定 Node 和特定硬體上。Live Migration 需要把 VM 的所有資源（包括網路）搬到另一台 Node，但 SR-IOV VF 做不到這件事，所以使用 SR-IOV 的 VM 本質上不支援 Live Migration。"
/>

---

## 第十三章：「資料庫 VM 快撐不住了——能不能不停機加磁碟？」

某個週三下午，DBA 傳訊息給阿明：「那台 PostgreSQL VM 的磁碟用了 90% 了，要快點擴容，但今天晚上有個重要的報表要跑，不能停機。」

阿明的第一直覺是 PVC resize——K8s 支援在線擴大 PVC 的容量，只要 StorageClass 支援 `allowVolumeExpansion`。他試了一下，成功把 PVC 從 200GB 擴到 300GB，VM 裡的磁碟也自動擴大了，問題暫時解決。

但 DBA 的下一個需求更有趣：「我想在不停機的情況下，把備份用的 log 磁碟接到 VM 上——這樣備份不會佔用主要磁碟的 IOPS。能做嗎？」

阿明去查了 KubeVirt 的 **Hotplug** 功能——它讓你可以在 VM 運行中動態掛載或卸除磁碟，不需要重啟。操作方式是用 `virtctl`：

```bash
# 先建立一個 PVC 作為備份磁碟
kubectl apply -f backup-pvc.yaml

# 在 VM 運行中熱插拔
virtctl addvolume postgres-vm --volume-name=backup-disk \
  --claim-name=backup-pvc --persist
```

`--persist` 參數讓這個磁碟在 VM 重啟後還在，否則重開機就消失了。VM 裡面會看到一顆新的磁碟 `/dev/vdb`，DBA 自己 `fdisk` 分割、`mkfs`、`mount`——完全不用重開機。

「這跟在實體機上插熱插拔硬碟一樣，」DBA 說，「沒想到 VM 也可以。」

阿明有點自豪——這個功能他以前在 VMware 上也用過，但沒想到 KubeVirt 也實作了類似的體驗。而且 KubeVirt 的 hotplug 完全透過 API 操作，可以納進 GitOps 流程：加磁碟這件事，現在也可以開一個 PR 來做。

---

> ### 📚 去這裡深入了解
> 熱插拔是一個實用但容易忽略的功能，在緊急擴容時特別好用：
>
> - [熱插拔磁碟 (Hotplug)](/kubevirt/storage/hotplug) — Hotplug 的工作原理、`virtctl addvolume` 的完整參數、persist vs 非 persist 的差異、支援的 volume 類型限制
>
> 讀完後，你應該能在不停機的情況下，替 VM 動態新增或移除磁碟。

<QuizQuestion
  question="阿明執行了 virtctl addvolume postgres-vm --volume-name=backup-disk --claim-name=backup-pvc。但 VM 重啟後那顆磁碟消失了。他應該加上哪個參數？"
  :options='[
    "--persist（讓熱插拔的磁碟在 VM 重啟後仍然保留）",
    "--permanent（把磁碟設為 VM 的主要系統磁碟）",
    "--keep（讓磁碟在刪除 VM 後仍然保留在叢集中）",
    "--sticky（讓磁碟和 VM 的生命週期綁定）",
  ]'
  :answer="0"
  explanation="不加 --persist 的熱插拔磁碟只在 VM 的當前運行週期存在，VM 重啟後會自動移除。加上 --persist 後，KubeVirt 會把這個 volume 加進 VM 的 spec，讓它在重啟後繼續掛載。"
/>

---

## 第十四章：「每次建 VM 都要複製一大段 YAML，煩死了」

遷移計畫推進到第三個月，阿明開始幫各個部門建 VM。

每次有人要一台新 VM，他就複製一份舊的 YAML，改改名稱和資源配置。漸漸地，他的 VM YAML template 資料夾裡有了十幾種不同的「標準配置」：`small-linux.yaml`、`medium-linux.yaml`、`large-linux-cpu-pinned.yaml`、`medium-windows.yaml`……

每次有人問：「我要一台 4 core 8GB 的 Linux VM」，阿明都要手動去找對應的 template，改個名字，apply 上去。這個流程不到三分鐘，但阿明覺得可以更好。

他發現了 **Instancetype** 和 **Preference** 這兩個 KubeVirt 的 API 資源。

**`VirtualMachineInstancetype`** 定義了 VM 的**硬體規格**（有點像 AWS 的 EC2 instance type）：CPU 數量、記憶體大小、CPU Pinning 設定。你可以定義一批標準規格，然後讓 VM 直接引用，而不是在每份 YAML 裡重複寫：

```yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineInstancetype
metadata:
  name: medium
spec:
  cpu:
    guest: 4
  memory:
    guest: 8Gi
```

**`VirtualMachinePreference`** 定義的則是 VM 的**軟體偏好**——用什麼 disk bus（virtio 還是 sata）、什麼網卡型號、預設的 clock 設定、適合 Linux 還是 Windows。兩者分開讓你可以自由組合：`medium` instancetype + `linux` preference，或是 `large` instancetype + `windows` preference。

阿明花了一個下午定義好公司的標準 instancetype 和 preference 清單，存進公司的 GitOps repo，然後在公司 wiki 上貼了一張表：「想要什麼規格的 VM，對著這張表填，三行 YAML 就搞定。」

部門的人拿到這張表，第一反應是：「這就像選 EC2 機型一樣，但跑在我們自己的 K8s 上。」

---

> ### 📚 去這裡深入了解
> Instancetype 是讓 KubeVirt 「平台化」的關鍵功能——讓使用者不需要懂 VM spec 細節：
>
> - [Instancetype & Preference](/kubevirt/api-resources/instancetype) — VirtualMachineInstancetype vs VirtualMachineClusterInstancetype 的差異、Preference 的欄位設計、如何用 `virtctl` 查詢可用的 instancetype、官方預設的 common-instancetypes 清單
>
> 讀完後，你應該能為自己的組織設計一套標準的 VM 規格清單，讓使用者用最簡潔的方式開 VM。

<QuizQuestion
  question="阿明定義了一個 medium Instancetype（4 core, 8Gi）和一個 linux Preference（virtio-blk, virtio-net, UTC clock）。如果今天要開一台 Windows VM，他應該怎麼做？"
  :options='[
    "保留 medium Instancetype（硬體規格不變），換用 windows Preference（適合 Windows 的設備偏好）",
    "複製 medium Instancetype 並重新命名為 medium-windows，在裡面加入 Windows 設定",
    "Instancetype 和 Preference 必須成套使用，Windows 需要重新定義一組全新的 Instancetype",
    "Windows VM 不支援 Instancetype，必須手動寫完整的 VM spec",
  ]'
  :answer="0"
  explanation="Instancetype 和 Preference 的設計就是為了正交組合：硬體規格（Instancetype）和軟體偏好（Preference）獨立定義、自由搭配。medium 規格可以搭 linux preference 也可以搭 windows preference，不需要重複定義硬體部分。"
/>

---

## 第十五章：「QA 說他們需要同時跑二十台一樣的 VM」

QA 團隊找到阿明，需求很直接：「我們要做壓力測試，需要同時跑 20 台相同規格的 Linux VM，測完可以全部刪掉。下次測試可能要 30 台，或 50 台。」

阿明的第一個念頭是：「那我手動建 20 次？」他立刻否定了這個想法。

他去查了 KubeVirt 的文件，找到了 **`VirtualMachinePool`**（以及更底層的 `VirtualMachineInstanceReplicaSet`）。這是 KubeVirt 參考 K8s ReplicaSet 設計的資源：你定義一個 VM 的 template，然後設定 `replicas: 20`，KubeVirt 就會幫你建出 20 台完全相同的 VM，還會維持這個數量（如果有 VM 掛掉，就自動補起來）。

```yaml
apiVersion: pool.kubevirt.io/v1alpha1
kind: VirtualMachinePool
metadata:
  name: qa-load-test
spec:
  replicas: 20
  selector:
    matchLabels:
      kubevirt.io/vmpool: qa-load-test
  virtualMachineTemplate:
    spec:
      instancetype:
        name: small
      preference:
        name: linux
      # ... 其他設定
```

QA 的壓測跑了四個小時，20 台 VM 同時在跑。結束後，`kubectl delete vmpool qa-load-test` 一條指令，20 台 VM 全部消失。

「這就是我要的，」QA 的 Lead 說，「下次測試我自己來。」

阿明心裡想：*這才是 VM 管理應該有的體驗——宣告式、可重複、可自動化。VMware 的時代，建 20 台 VM 要手動點好幾個小時。*

---

> ### 📚 去這裡深入了解
> VM Pool 讓 VM 的彈性伸縮成為可能，適合測試、CI/CD、或有批次需求的場景：
>
> - [ReplicaSet 與 Pool](/kubevirt/api-resources/replica-pool) — VirtualMachineInstanceReplicaSet 和 VirtualMachinePool 的差異、selector 設計、scale up/down 的行為、與 HPA 的整合可能性
>
> 讀完後，你應該能用 Pool 快速建立和清理一批相同規格的 VM。

<QuizQuestion
  question="QA 的壓測進行到一半，其中 3 台 VM 因為 Node 資源不足被強制終止。VirtualMachinePool 控制器會怎麼回應？"
  :options='[
    "自動建立 3 台新 VM 來補足 replicas 設定的數量，維持目標狀態",
    "Pool 進入 degraded 狀態，發出告警但不自動修復，需要人工介入",
    "Pool 自動縮小 replicas 數量，把目標從 20 改成 17",
    "等所有 VM 都跑完後，在下一次壓測開始時才補足數量",
  ]'
  :answer="0"
  explanation="VirtualMachinePool 和 K8s ReplicaSet 的設計理念相同——它是一個宣告式控制器，持續確保實際運行的 VM 數量等於 replicas 設定值。有 VM 消失，控制器就自動補上，這是 &quot;desired state reconciliation&quot; 的核心概念。"
/>

---

## 第十六章：「資安說，virt-launcher 的權限太高了」

季度安全審查。

資安工程師 Julie 找到阿明，打開一份報告：「你知道 virt-launcher Pod 用了哪些 capability 嗎？我看到 `SYS_PTRACE`、`NET_ADMIN`，在我們的安全政策下這些都是 high risk。」

阿明承認他之前沒認真想過這件事。他知道 virt-launcher 需要特殊的 privilege 才能跑 QEMU，但具體是什麼 capability，為什麼需要，他說不清楚。

他開始研究 KubeVirt 的安全架構。

首先是 **virt-launcher 的最小化 privilege 原則**。KubeVirt 的設計目標是「用盡量少的 privilege 跑 QEMU」，但 QEMU 本身需要一些 Linux capability 才能做到虛擬化該做的事：
- `NET_ADMIN`：配置 VM 的網路介面
- `SYS_PTRACE`：讓 virt-handler 可以監控 QEMU 進程的狀態
- `SYS_NICE`：設定 QEMU vCPU 執行緒的優先權（Realtime VM 需要）

KubeVirt 新版已經引入了更嚴格的 **seccomp profile**，把 QEMU 允許的 syscall 限制在必要的最小集合，大幅縮減了攻擊面。另外，`virt-launcher` 也支援用 **user namespace** 進一步隔離，讓 VM 裡的 root 和宿主機的 root 不是同一個 UID——這是容器安全的基本防線，KubeVirt 把它帶進了 VM 的世界。

阿明把這些發現整理成一份回覆給 Julie：「這些 capability 是 QEMU 正常運作的最低需求，但我們可以確認你們公司的 KubeVirt 部署有開啟 seccomp profile 和 user namespace 隔離——以下是確認步驟。」

Julie 讀完，點點頭：「好，這樣我能寫進 exception 裡，加上 compensating control。謝謝你解釋清楚。」

阿明想到，如果當初他也不懂，這個問題可能就會演變成一場「資安說要關掉，業務說不能停」的拉鋸戰。懂底層讓他能精確地說明風險在哪裡、緩解措施是什麼，而不是含糊地說「應該沒問題吧」。

---

> ### 📚 去這裡深入了解
> 安全架構是生產環境部署前必須弄清楚的事：
>
> - [安全架構](/kubevirt/deep-dive/security) — virt-launcher 的 capability 清單與必要性分析、seccomp profile 的設定方式、user namespace 隔離、NetworkPolicy 在 VM 流量上的適用性、常見的安全加固配置
>
> 讀完後，你應該能用具體的技術語言跟資安團隊解釋 KubeVirt 的安全模型，而不是「應該沒問題」。

<QuizQuestion
  question="資安審查發現 virt-launcher 使用了 SYS_PTRACE capability。阿明如何向 Julie 解釋這個 capability 的必要性？"
  :options='[
    "virt-handler 需要用 SYS_PTRACE 監控 virt-launcher Pod 內 QEMU 進程的運行狀態",
    "SYS_PTRACE 是讓 QEMU 能讀取 VM 磁碟檔案的必要權限",
    "SYS_PTRACE 用來讓 VM 裡的 guest OS 能直接存取 Host 的記憶體",
    "這是 KubeVirt 的 bug，新版本已修復，不再需要 SYS_PTRACE",
  ]'
  :answer="0"
  explanation="virt-handler 需要 SYS_PTRACE 來監控同一個 Pod 內的 QEMU 進程狀態（進程追蹤）。這讓 KubeVirt 能感知 QEMU 的健康狀態並做出對應處理。了解每個 capability 的具體用途，才能和資安團隊做有意義的風險評估對話。"
/>

---

## 第十七章：「AI 團隊說他們需要 GPU」

公司的 ML 團隊一直在用雲端 GPU 訓練模型，成本高得嚇人。有人提議：「我們機房裡有幾張 A100，能不能讓 AI 團隊的 VM 直接用這些 GPU 來訓練？」

這個需求找到了阿明。他看了一下那幾台 Node 的硬體規格，確認了有 NVIDIA A100。然後開始研究 KubeVirt 的 GPU 支援。

KubeVirt 支援兩種 GPU 使用方式：

**GPU Passthrough（直通）**：把整張 GPU 完整地分配給一台 VM。VM 裡的 driver 直接和 GPU 硬體溝通，效能接近裸機，但一張 GPU 只能給一台 VM 用，無法共享。

**vGPU（虛擬 GPU）**：用 NVIDIA 的 MIG（Multi-Instance GPU）或 vGPU 技術，把一張 GPU 切成多個虛擬 GPU，每個 VM 可以拿到一份虛擬 GPU。效能比 passthrough 稍低，但可以讓多台 VM 共用同一張卡，提高硬體使用率。

要在 KubeVirt 裡用 GPU，需要：
1. 在 Node 上安裝 NVIDIA GPU Operator
2. 讓 K8s 的 device plugin 把 GPU 作為可分配的資源暴露出來
3. 在 VM spec 裡宣告需要 GPU

```yaml
spec:
  domain:
    devices:
      gpus:
        - deviceName: nvidia.com/GA100_A100_PCIE_40GB
          name: gpu1
```

阿明配置好後，ML 工程師在 VM 裡跑 `nvidia-smi`，看到了 A100，眼睛一亮。第一次訓練任務跑完，比雲端快了 30%，而且成本只有雲端的零頭。

「以後訓練任務在這裡跑，」ML 的 Lead 說，「阿明，謝謝你。」

阿明悄悄把「GPU Passthrough 設定 SOP」加進了公司的 GitBook，想到以後如果有人問，他可以直接丟連結。

---

> ### 📚 去這裡深入了解
> GPU 支援讓 KubeVirt 可以服務 ML/AI 這類計算密集型工作負載：
>
> - [GPU/vGPU 直通](/kubevirt/deep-dive/gpu-passthrough) — GPU Passthrough 和 vGPU 的配置差異、NVIDIA GPU Operator 的角色、device plugin 的工作原理、常見的設定錯誤與排查方法
>
> 讀完後，你應該能替需要 GPU 的 VM 設定硬體直通，並了解 GPU 共享方案的取捨。

<QuizQuestion
  question="ML 團隊有 4 張 A100 GPU，有 8 個研究員同時需要跑訓練任務。如果用 GPU Passthrough 模式，最多能讓幾個研究員同時使用？"
  :options='[
    "4 個（每張 GPU 只能分配給一台 VM，不能共享）",
    "8 個（KubeVirt 自動把每張 GPU 虛擬化成 2 個 vGPU）",
    "無限（Passthrough 只是一個設定名稱，實際上支援多個 VM 共享）",
    "1 個（Passthrough 模式下所有 GPU 合成一張大 GPU 分配給一台 VM）",
  ]'
  :answer="0"
  explanation="GPU Passthrough 把整張實體 GPU 直通給一台 VM，一張 GPU 同時只能給一台 VM 用。4 張 A100 最多同時給 4 台 VM 使用。要讓 8 個人同時用，需要改用 vGPU（MIG 或 NVIDIA vGPU 技術）把每張 GPU 切成多份。"
/>

---

## 第十八章：「VM 出問題了，我要去哪裡找線索？」

六個月下來，阿明已經是組裡唯一一個真正懂 KubeVirt 的人。每次有 VM 出問題，最後都會找到他。

他在處理過幾十次不同類型的問題後，總結出了一套**排查順序**，每次出問題都照這個順序走，很少找不到原因：

**第一層：K8s 事件**
```bash
kubectl describe vmi <vmi-name>
kubectl get events --field-selector involvedObject.name=<vmi-name>
```
大多數問題在這一層就有線索——調度失敗、PVC 沒 bound、網路設定錯誤，都會在 events 裡出現。

**第二層：virt-launcher Pod**
```bash
kubectl logs virt-launcher-<hash> -c compute
kubectl exec -it virt-launcher-<hash> -c compute -- virsh list --all
```
VM 在 running 狀態但行為異常，通常要去 virt-launcher 的 log 找。`virsh` 指令可以在 launcher 裡直接查 libvirt domain 的狀態。

**第三層：virt-handler**
```bash
kubectl logs -n kubevirt -l kubevirt.io=virt-handler --follow
```
如果是 VM 無法啟動、網路設定沒生效、Node 層的問題，通常要去 virt-handler 看。

**第四層：QEMU log**
```bash
kubectl exec -it virt-launcher-<hash> -c compute -- \
  cat /var/run/libvirt/qemu/<domain>.log
```
這是最底層的日誌，QEMU 本身的 error message。如果看到 `Device not found` 或 `Failed to initialize`，通常是 VM spec 的設備設定有問題。

阿明把這個排查流程寫成了公司的 runbook，配合真實案例——那個 OOM 的凌晨 2 點、那次 bridge + Calico 衝突、那次 Windows virtio 驅動沒裝——每個案例都附上了當時的症狀、查到的日誌、最後的解法。

「有了這份 runbook，」他想，「就算我哪天請假，別人也能自己查。」

---

> ### 📚 去這裡深入了解
> 系統性的排查方法是 on-call 工程師最值錢的技能：
>
> - [故障排除手冊](/kubevirt/guides/troubleshooting) — 按問題類型分類的排查流程、各層級 log 的位置與解讀方式、常見錯誤 message 的對照表、`virtctl` 和 `virsh` 的實用除錯指令
>
> 讀完後，你應該能系統性地定位 VM 問題，而不是靠直覺亂猜。

<QuizQuestion
  question="阿明的 VM 卡在 Scheduling 狀態很久。他應該先查哪個指令？"
  :options='[
    "kubectl get events --field-selector involvedObject.name=<vmi-name>（查 K8s 事件找調度失敗原因）",
    "kubectl logs virt-launcher-<hash> -c compute（查 virt-launcher 的 QEMU log）",
    "kubectl logs -n kubevirt -l kubevirt.io=virt-handler（查 virt-handler 的 Node 層 log）",
    "virtctl console <vm-name>（直接連進 VM 看 guest OS 的開機 log）",
  ]'
  :answer="0"
  explanation="VM 卡在 Scheduling 表示還沒到 virt-launcher 的層次，問題在 K8s 調度層。最快的診斷路徑是先看 K8s events，它會直接告訴你調度失敗的原因（資源不足、NodeSelector 不符、PVC 沒 bound 等）。後面幾個指令是在 VM 已經調度成功後才有意義的。"
/>

---

## 第十九章：「阿明，我們能不能做一個自訂的 VM 初始化動作？」

DevOps 團隊找來了一個新需求：每台新建的 VM 啟動時，要自動執行一個 registration script，把 VM 的資訊（hostname、IP、服務類型）回報給公司的 CMDB（Configuration Management Database）。

這個需求讓阿明思考：「我要怎麼在 VM 啟動時注入一段自訂的邏輯，但又不要去改每一份 VM YAML？」

他查到了 **Hook Sidecar** 機制。

Hook Sidecar 是 KubeVirt 提供的一個擴充點：你可以在 `virt-launcher` Pod 旁邊掛一個 sidecar container，這個 sidecar 可以攔截 VM 生命週期中的特定時間點（Hook），執行自訂的邏輯，甚至修改 VM domain 的 XML 定義（在 QEMU 啟動前）。

可以攔截的 hook 包括：
- `onDefineDomain`：在 libvirt domain XML 被建立時觸發，可以修改 XML（例如注入特殊的 CPU feature 或 device 設定）
- `postStartCommand`：VM 啟動後執行自訂命令

阿明用 `postStartCommand` hook 實現了 CMDB registration：sidecar container 等 VM 的 agent 回應後，呼叫公司內部的 API 把 VM 資訊寫進 CMDB，整個過程不需要改任何 VM spec，只要在需要 registration 的 VM namespace 上掛這個 hook。

「這就像 K8s 的 Admission Webhook，但是給 VM 的，」阿明解釋給同事聽，「你可以在不碰 VM spec 的情況下，在特定時間點插入自訂邏輯。」

他想到了更多應用場景：自動修改 QEMU 的 CPU feature、在 VM 啟動後自動更新 inventory、在 VM 關機前執行 cleanup script。Hook Sidecar 開了一扇門，讓 KubeVirt 的行為變得可以高度客製化，而且不需要改 KubeVirt 本身的程式碼。

---

> ### 📚 去這裡深入了解
> Hook Sidecar 是 KubeVirt 裡最強大的擴充機制之一，但文件相對隱晦：
>
> - [Hook Sidecar 機制](/kubevirt/components/hook-sidecars) — Hook 的種類（onDefineDomain、postStartCommand）、sidecar 的開發方式、annotation 的設定、實際的使用案例
>
> 讀完後，你應該能為組織設計客製化的 VM 生命週期擴充，而不需要 fork KubeVirt。

<QuizQuestion
  question="阿明想在不修改任何 VM spec 的前提下，讓特定 namespace 的每台 VM 啟動後都自動回報資訊給 CMDB。他選擇了 Hook Sidecar 的哪個 hook？"
  :options='[
    "postStartCommand — 在 VM 啟動後執行自訂命令（呼叫 CMDB API）",
    "onDefineDomain — 在 libvirt domain XML 建立時觸發，修改設備設定",
    "preStopCommand — 在 VM 關機前執行，做 cleanup",
    "onSchedule — 在 VM 被調度到 Node 時觸發，記錄 Node 資訊",
  ]'
  :answer="0"
  explanation="postStartCommand 是 &quot;VM 啟動後執行&quot; 的 hook，適合阿明的 CMDB registration 場景——等 VM 的 agent 就緒後，呼叫 CMDB API 回報。onDefineDomain 是在 QEMU 啟動前修改 XML 設定，用途不同。preStopCommand 和 onSchedule 是其他生命週期的 hook。"
/>

---

## 第二十章：「原來 VMware 遷移有專門的工具……」

計畫進入尾聲，剩最後五台 VMware VM 要遷移。

這幾台 VM 的情況最複雜——有的有多塊磁碟、有的用了 VMware 特有的設備驅動、有的 VMDK 超過 500GB。阿明一直用手動的方式：把 VMDK 匯出成 QCOW2，透過 DataVolume 的 HTTP source 把 image 拉進來，再建 VM 掛上去。這個流程每台要花一到兩天。

直到有個同事說：「你知道有 Forklift 這個工具嗎？」

阿明查了一下，才發現自己一直在用「蠻力」解決一個其實有工具解法的問題。**Forklift** 是一個 K8s-native 的 VM 遷移工具，專為把 VMware（以及其他 hypervisor）的 VM 遷移到 KubeVirt 而設計。它可以：
- 直接連進 vSphere，列出所有的 VM 和資源
- 分析 VM 的相容性，提前告訴你哪些設備在 KubeVirt 上需要調整
- 自動把 VMDK 轉換格式、建立對應的 DataVolume、建立 KubeVirt VM
- 支援熱遷移（不停機直接把 VMware VM 搬過來）

阿明看著 Forklift 的 UI，心裡五味雜陳。「如果我三個月前就知道這個工具，應該可以省下很多時間。」

他花了一天設定好 Forklift，把最後五台 VM 用圖形化介面直接遷移過來——整個過程幾乎是自動的，每台只需要幾個小時。

「好吧，」他苦笑，「至少我用手動方式學到了很多底層細節。現在用工具，我知道工具在做什麼，遇到問題也知道從哪裡查。」

他在公司 wiki 的 KubeVirt 頁面最頂端加了一條：**「如果你是從 VMware 遷移的，請先閱讀 VMware to KubeVirt 遷移指南，以及 Forklift 工具說明。」**

---

> ### 📚 去這裡深入了解
> 如果你的遷移來源是 VMware，這裡有專門的路線：
>
> - [VMware 到 KubeVirt 遷移指南](/kubevirt/guides/vmware-to-kubevirt) — VMware 和 KubeVirt 概念的對照表、VMDK 格式轉換的方法、常見的相容性問題與解法、Forklift 工具的使用流程
>
> 讀完後，你應該能規劃一個系統性的 VMware to KubeVirt 遷移計畫，而不是一台一台用手動方式硬搬。

<QuizQuestion
  question="阿明手動遷移 VMware VM 的流程是：匯出 VMDK → 轉 QCOW2 → DataVolume HTTP import → 建 VM。Forklift 比這個流程多了什麼能力？"
  :options='[
    "直接連接 vSphere API、自動分析相容性、支援不停機熱遷移（warm migration）",
    "Forklift 比手動快 10 倍，但流程本質上相同，都需要先關機",
    "Forklift 只能遷移 VMware，手動方法可以支援更多來源 hypervisor",
    "Forklift 自動安裝 virtio-win 驅動，手動方法需要事後補裝",
  ]'
  :answer="0"
  explanation="Forklift 直接連進 vSphere 的 API，可以列出所有 VM、分析設備相容性（告訴你哪些設備需要調整）、自動轉換格式、並支援 warm migration（熱遷移，不需要先停機）。手動方法只能做冷遷移，且每個步驟都要自己處理。"
/>

---

## 第二十一章：「我想看看 KubeVirt 的原始碼」

遷移計畫正式結束後的某個下午，阿明發現了一個奇怪的問題。

在特定情況下，VMI 的狀態有時候會卡在 `Scheduling` 超過預期的時間，但最後還是能起來。這不是 bug，但他覺得哪裡怪怪的，文件上沒有解釋清楚。

他決定去看原始碼。

他以前覺得 Go 語言的大型專案很難看懂，但上手之後發現 KubeVirt 的程式碼結構其實很清晰：

```
pkg/
  virt-api/      → API 和 Webhook 的實作
  virt-controller/ → 各種 Reconcile loop
  virt-handler/  → 節點層邏輯
  virt-launcher/ → QEMU 管理邏輯
  virtctl/       → CLI 工具
```

他找到了 `virt-controller/watch/` 目錄，裡面有針對每種資源的 controller，`virtualmachine.go` 就是 VM reconcile loop 的入口。他一行一行讀，找到了那個 `Scheduling` 狀態的邏輯——原來是當 virt-handler 還沒有在目標 Node 準備好（`virt-handler` 的 annotation 還沒更新），controller 就會暫停，等待一個 backoff 重試。那個「卡住」其實是正常的等待機制，只是 timeout 設得比他預期的長。

謎題解開了。但更重要的是，他發現自己**看得懂 KubeVirt 的程式碼了**。

他開了一個 KubeVirt 的 GitHub issue，描述了那個 timeout 設定可能讓人困惑的問題，建議加一個更清楚的 event message。maintainer 回覆了：「好建議，歡迎送 PR。」

阿明盯著那行字。*歡迎送 PR。*

他從沒想過自己有一天會對一個 CNCF 專案送 PR。但他現在的理解程度——從概念到實作，從 API 到原始碼——已經足夠讓他做這件事了。

他打開 VS Code，clone 了 KubeVirt 的 repo，開始設定開發環境。

---

> ### 📚 去這裡深入了解
> 如果你想更深入地理解 KubeVirt，甚至參與貢獻，這裡是起點：
>
> - [程式碼架構導覽](/kubevirt/dev-guide/code-structure) — 整個 repo 的目錄結構解說、各個套件的職責分工、如何快速定位某個功能的實作位置
> - [開發環境設置](/kubevirt/dev-guide/getting-started) — 如何在本機跑 KubeVirt 開發環境、測試的方法、如何準備你的第一個 PR
>
> 讀完後，你應該能在 KubeVirt 的原始碼裡找到你想找的功能，甚至開始貢獻。

<QuizQuestion
  question="阿明想找 VirtualMachine 的 reconcile 邏輯在哪裡。根據 KubeVirt 的程式碼結構，他應該去哪個目錄找？"
  :options='[
    "pkg/virt-controller/watch/（各種資源的 controller 和 reconcile loop 在這裡）",
    "pkg/virt-api/（VM 的 Webhook 驗證邏輯和 CRUD 操作入口）",
    "pkg/virt-handler/（每個 Node 上的 VMI 生命週期管理）",
    "pkg/virtctl/（CLI 指令的實作，包括 start、stop、migrate）",
  ]'
  :answer="0"
  explanation="KubeVirt 的 repo 按照各個 binary 分目錄：virt-controller 負責 VM/VMI 的 reconcile loop（調和控制器），virt-api 是 Webhook 入口，virt-handler 是 Node 層的代理，virtctl 是 CLI 工具。要找 VM 的 reconcile 邏輯，就去 pkg/virt-controller/watch/ 找 virtualmachine.go。"
/>

---

## 尾聲：阿明的一年後

一年後，阿明的評估報告早已通過，所有 VM 都已在生產環境的 KubeVirt 上穩定運行——包括那台最難搞的 Windows Server、那幾台掛著 SR-IOV 網卡的 DPDK 應用、ML 團隊的 GPU 訓練工作站、以及 QA 用 VM Pool 拉起來的壓測叢集。

他坐在同一張椅子上，喝著同一個位置倒的咖啡，但已經是另一個人了。

那封改變他命運的信，現在讀起來感覺很輕。「把 VMware VM 搬進 K8s」——他當時覺得這是一個謎，現在它只是他日常工作的一部分。

一年來他真正學到的，不只是 KubeVirt 的 API 和指令，而是一種**把陌生系統拆開來看的方法**：先找到概念模型，再追蹤資料流，然後一個一個解決具體的問題。這個方法論不只適用於 KubeVirt，也適用於下一個他從沒用過的技術。

現在的他能做到的事：

**基礎管理**
- 用 `kubectl` 和 `virtctl` 管理幾十台 VM，lifecycle 管理已接進公司現有的 GitOps pipeline
- 用 Instancetype 和 Preference 定義公司標準規格，讓使用者三行 YAML 就能開 VM
- 用 VM Pool 讓 QA 在幾分鐘內拉起 20-50 台相同規格的測試 VM

**網路與效能**
- 為不同需求的 VM 設計網路策略：普通服務走 masquerade，需要直接存取走 bridge + Multus，極致效能的 DPDK 應用走 SR-IOV
- 針對計算密集的 VM 開 CPU Pinning、NUMA Topology Policy，把效能問題在上線前就解決
- 替 ML 團隊的訓練 VM 配置 GPU Passthrough，讓 A100 直通給 QEMU，成本降到雲端的零頭

**儲存與備份**
- 規劃儲存方案：需要 live migration 的 VM 用 RWX StorageClass，測試 VM 走 containerDisk，緊急擴容用 Hotplug
- 定期對關鍵 VM 做 VirtualMachineSnapshot，可以隨時把資料庫 VM clone 成 staging 環境

**可觀測性與維運**
- 有 Prometheus + Grafana 全覆蓋的 VM 監控，凌晨 2 點的故障幾分鐘內就知道
- 有一份按問題類型整理的 runbook，每個曾踩過的坑都有對應的排查步驟
- 在 KubeVirt 升版時，靠 WorkloadUpdateController 讓 VM 靜靜地 live migrate，業務無感

**安全與合規**
- 能用技術語言跟資安團隊解釋 virt-launcher 的 capability 需求和 seccomp 緩解措施
- 知道 KubeVirt 的安全邊界在哪裡，能評估什麼需要額外加固

**進階功能**
- 透過 Hook Sidecar 替 VM 注入自訂的生命週期邏輯
- 用 Forklift 系統性地處理 VMware 遷移，而不是一台一台手動搬
- 看得懂 KubeVirt 的原始碼，能在 issue tracker 上提出有意義的改善建議

他最近把公司一個新進的工程師交給他帶。那個工程師問：「KubeVirt 要從哪裡開始學？」

阿明想了一秒，說：「先讀我整理的這份文件。你會遇到阿明——他跟你一樣，第一次面對 KubeVirt，什麼都不懂，然後一個問題、一個問題地把它搞懂了。」

他沒說那個阿明就是他自己。

站在終點回頭看起點，他覺得學習的路其實沒有那麼長——只是一開始不知道地圖在哪裡。

他打開 Slack，給那位一年前寄信給他的 VP Engineering 回了一封短信：「遷移計畫一年前完成。目前 KubeVirt 平台已支援 Linux / Windows / GPU / DPDK 工作負載，下季準備開放給更多業務部門使用。附件是這一年的回顧報告。」

他按下送出，端起那杯終於不再涼掉的咖啡，喝了一口。

在角落，他的 GitHub notifications 頁面有一條新訊息——KubeVirt maintainer 剛剛 review 了他的 PR。

他微笑了。

---

> ### 📚 想繼續往更深處走？
>
> 阿明的故事到這裡告一段落，但 KubeVirt 還有很多值得探索的角落。
> 以下是按主題整理的深入閱讀清單——阿明在六個月裡逐漸把這些都翻過了一遍：
>
> **架構與原始碼**
> - [VM 生命週期深度剖析](/kubevirt/architecture/lifecycle) — 狀態機每個 transition 背後發生了什麼
> - [virt-api](/kubevirt/components/virt-api) / [virt-controller](/kubevirt/components/virt-controller) / [virt-handler](/kubevirt/components/virt-handler) / [virt-launcher](/kubevirt/components/virt-launcher) — 四大元件的原始碼層級分析
>
> **網路進階**
> - [SR-IOV 與進階網路](/kubevirt/networking/sriov) — 需要近裸機網路效能時的選項
>
> **儲存進階**
> - [DataVolume 與 CDI 整合](/kubevirt/storage/pvc-datavolume) — 大規模 image 匯入的自動化方案
> - [熱插拔磁碟](/kubevirt/storage/hotplug) — 不停機新增/移除磁碟
>
> **安全**
> - [安全架構](/kubevirt/deep-dive/security) — virt-launcher 的權限模型、SELinux、seccomp profile
>
> ---
>
> 阿明從「K8s 不是跑 Container 的嗎？」到「讓我來規劃一下 migration 策略」，走了六個月。
> 你可以走得更快——因為你現在有地圖了。

---

::: info 其他學習路徑
這是故事驅動式的學習路徑，適合喜歡在情境中學習的人。
如果你偏好系統性的概念先行，可以從 [KubeVirt 學習路徑入口](/kubevirt/learning-path/) 選擇其他方式進入。
:::
