---
layout: doc
title: KubeVirt — 學習路徑 B：故事驅動式
---

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

---

## 尾聲：阿明的六個月後

六個月後，阿明的評估報告早已通過，第一批 VM 已經在生產環境的 KubeVirt 上穩定運行。

他坐在同一張椅子上，喝著同一個位置倒的咖啡，但已經是另一個人了。

那封改變他命運的信，現在讀起來感覺很輕。「把 VMware VM 搬進 K8s」——他當時覺得這是一個謎，現在它只是他日常工作的一部分。

六個月來他真正學到的，不只是 KubeVirt 的 API 和指令，而是一種**把陌生系統拆開來看的方法**：先找到概念模型（VM vs VMI），再追蹤資料流（apply 之後發生什麼），然後一個一個解決具體的問題（網路、儲存、高可用）。這個方法論不只適用於 KubeVirt，也適用於下一個他從沒用過的技術。

現在的他能做到的事：
- 用 `kubectl` 和 `virtctl` 管理幾十台 VM，就像管理普通的 K8s workload 一樣，甚至把 VM 的 lifecycle 管理接進了公司現有的 GitOps pipeline
- 為不同需求的 VM 設計不同的網路策略：普通服務走 masquerade，需要直接存取的走 bridge + Multus
- 規劃儲存方案，讓需要 live migration 的 VM 使用 RWX StorageClass，讓測試用的 VM 走 containerDisk
- 排除各種奇怪的問題——`virt-launcher` Pod 的 log、`virsh` 的輸出、QEMU 的 error message，他都能看懂，也知道哪一層出問題要去哪裡找線索
- 在 KubeVirt 升版或 Node 維護前，把 VM 都 live migrate 到安全的 Node 上，讓維護視窗安靜地完成——不再需要打電話說「那個系統要暫停一下」

他最近開始幫新進的同事介紹 KubeVirt。他發現最難解釋的不是技術細節，而是最初的那個問題：「為什麼要把 VM 跑在 K8s 上？」

他現在的答案是：「因為你不想管兩套東西。當 VM 能用 `kubectl` 管、能用 Helm chart 部署、能接進你現有的監控和告警——那它就真的成為 K8s 生態的一部分了，而不是一個旁邊的孤島。」

站在終點回頭看起點，他覺得學習的路其實沒有那麼長——只是一開始不知道地圖在哪裡。

他打開 Slack，給那位六個月前寄信給他的 VP Engineering 回了一封短信：「Q3 目標完成。第一批 24 台 VM 已全數遷移至 KubeVirt，維運成本估計可降低 40%，詳見附件報告。」

他按下送出，端起那杯終於不再涼掉的咖啡，喝了一口。

---

> ### 📚 想繼續往更深處走？
>
> 阿明的故事到這裡告一段落，但 KubeVirt 還有很多值得探索的角落。
> 以下是按主題整理的深入閱讀清單——阿明在六個月裡逐漸把這些都翻過了一遍：
>
> **架構與原始碼**
> - [VM 生命週期深度剖析](/kubevirt/architecture/lifecycle) — 狀態機的每一個 transition 背後發生了什麼，從 Pending 到 Running 到 Migrating 的完整路徑
> - [virt-api 原始碼分析](/kubevirt/components/virt-api) — Webhook 設計、Admission Controller 實作細節
> - [virt-controller 原始碼分析](/kubevirt/components/virt-controller) — Reconcile loop 如何處理 VM、VMI、Pod 的狀態同步
> - [virt-handler 原始碼分析](/kubevirt/components/virt-handler) — 節點層的資源準備與 libvirt domain 管理
> - [virt-launcher 原始碼分析](/kubevirt/components/virt-launcher) — QEMU 進程的生命週期管理與監控機制
>
> **網路進階**
> - [網路模型完整解析](/kubevirt/networking/overview) — SR-IOV 的適用場景、Multus 多網卡設定的完整方案
> - [Bridge 與 Masquerade 深度比較](/kubevirt/networking/bridge-masquerade) — 原始碼層級的實作差異
>
> **儲存進階**
> - [DataVolume 與 CDI 整合](/kubevirt/storage/pvc-datavolume) — 如何大規模匯入現有 VM image、DataVolume 的 phase 狀態機
> - [ContainerDisk 的適用邊界](/kubevirt/storage/container-disk) — 什麼情況可以用、什麼情況一定不能用
>
> **維運進階**
> - [Live Migration 概述](/kubevirt/advanced/live-migration) — 觸發條件、前置需求、監控方法
> - [Migration 內部機制深度剖析](/kubevirt/deep-dive/migration-internals) — Pre-copy 演算法、記憶體 dirty rate 追蹤、收斂策略
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
