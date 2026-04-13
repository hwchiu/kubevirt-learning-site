---
layout: doc
title: Forklift — 學習路徑：阿明的大遷徙
---

# 📖 阿明的大遷徙

> 跟著阿明，從接到「一個月內把 50 台 VMware VM 搬進 KubeVirt」這個任務開始，一步步理解 Forklift 的世界。
> 每個章節都是阿明真實遭遇的問題——你會看到他怎麼查文件、怎麼犯錯、怎麼一點一點把拼圖拼起來。

---

## 序章：一個月，五十台，只有阿明一個人

KubeVirt 已經跑起來了。阿明花了兩個月把 KubeVirt 部署好，讓幾台測試用的 Linux VM 在 K8s 上跑得好好的。他以為最難的部分已經結束了。

週五下午四點半，主管傳來一則訊息：「阿明，下週開始有個任務——公司 VMware 的合約下個月到期，不續約了。vSphere 裡面還有 53 台 VM 需要在四週內遷移到 KubeVirt。你負責。」

阿明看著螢幕，計算了一下：53 台 ÷ 4 週 ÷ 5 個工作天 = 每天要搬 2-3 台 VM。

*聽起來不多，但……怎麼搬？*

他之前有試過「手動搬」一台測試 VM——把 VMDK 匯出成 OVA、上傳到物件儲存、再用 CDI 的 DataVolume 匯入 PVC、然後手動寫 KubeVirt 的 VM YAML，調整網路和儲存設定。整個過程花了他一個下午，還遇到格式不相容的問題。

53 台 × 一個下午 = 53 個下午。這根本不可能。

阿明打開搜尋引擎，輸入「bulk migrate VMware to KubeVirt」，找到了一個名字：**Forklift**。

---

## 第一章：「手動搬 VM，到底哪裡痛？」

在開始研究 Forklift 之前，阿明決定先把「手動搬 VM」的痛點整理清楚。他打開一個空白文件，開始列清單。

第一個痛點：**格式轉換**。VMware 的磁碟是 VMDK 格式，有時候還是 sparse 的；KubeVirt 的 DataVolume 接受 QCOW2 或 RAW。轉換工具（`qemu-img`）可以做到，但 VMDK 有好幾種變體，有時候轉出來的映像無法開機——他上次就踩到了這個坑，花了兩個小時才搞清楚是 `vmdk-stream` 格式的問題。

第二個痛點：**網路設定差異**。VMware 裡 VM 連接的是 Distributed Virtual Switch 上的 Port Group，名字可能叫「VLAN-100-Production」。KubeVirt 裡面的網路資源叫做 `NetworkAttachmentDefinition`，可能用 OVN-Kubernetes 或 Multus 管理。從 Port Group 對應到 NAD，沒有現成的機制，全靠人工確認再寫 YAML。

第三個痛點：**儲存對應**。VMware 的 Datastore 有快有慢，遷移過來要選對 StorageClass——SSD 等級的 VM 不能遷移到 HDD 的 StorageClass 上。但兩邊的命名完全不同，需要人工建立一張「對應表」，再逐台 VM 手動設定。

第四個痛點：**進度追蹤**。手動搬的話，50 台 VM 的狀態完全靠人工記錄——Excel 試算表、Slack 訊息、口頭確認。很容易出現「這台遷移了嗎？」「那台失敗了但我忘記重試」的情況。

阿明把這四個痛點圈起來，在旁邊寫：*Forklift 應該能解決這些。*

他去找了 Forklift 的 GitHub repo 和文件，開始看架構圖。Forklift 是一個 Kubernetes Operator——它用自己的 CRD 描述遷移任務，有 Controller 負責執行。它支援的來源包括：vSphere、oVirt/RHV、OpenStack、Hyper-V、OVA 文件。目標是 KubeVirt。

阿明對 Operator 架構不陌生，但他的目光停在一個詞上：**Provider**。

*Provider 是什麼？是「vSphere 這個遷移來源」的描述嗎？*

---

> ### 📚 去這裡深入了解
> - [系統架構](/forklift/architecture) — 了解 Forklift 的 9 個 Controller 和 9 個 CRD 的整體架構，以及 virt-v2v 在磁碟轉換中的角色
>
> 讀完後，你應該能說明：Forklift 的架構如何解決上面列出的四個手動遷移痛點？

---

## 第二章：「Provider——怎麼告訴 Forklift 我的 vSphere 在哪？」

阿明花了半個小時讀完 Forklift 的快速入門。他發現，使用 Forklift 的第一步是建立一個 **`Provider`** CRD。

`Provider` 是 Forklift 對「遷移來源或目標的連線設定」的描述。你需要告訴 Forklift：

- 這是什麼類型的平台（`vsphere`、`ovirt`、`openstack`、`openshift`）
- 連線的 endpoint 在哪（vCenter 的 URL）
- 認證資訊在哪（K8s Secret）

阿明照著文件寫出了第一個 Provider YAML：

```yaml
apiVersion: forklift.konveyor.io/v1beta1
kind: Provider
metadata:
  name: vmware-prod
  namespace: konveyor-forklift
spec:
  type: vsphere
  url: https://vcenter.example.com/sdk
  secret:
    name: vmware-credentials
    namespace: konveyor-forklift
```

他同時建立了對應的 Secret：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: vmware-credentials
  namespace: konveyor-forklift
type: Opaque
stringData:
  user: administrator@vsphere.local
  password: "my-vcenter-password"
  thumbprint: "AA:BB:CC:..."
```

`kubectl apply` 之後，他興奮地去看 Provider 的狀態：

```
kubectl get provider vmware-prod -n konveyor-forklift
NAME           READY   CONNECTED   INVENTORY   TYPE      AGE
vmware-prod    False   False       False       vsphere   10s
```

*三個 False。哪裡出問題了？*

他用 `kubectl describe` 看 Events，發現錯誤訊息：「certificate verify failed」。原來他的測試 vCenter 用的是自簽憑證，但他填的 `thumbprint` 是複製貼上時多了一個空格。修正後重新 apply，幾秒鐘內狀態變成：

```
NAME           READY   CONNECTED   INVENTORY   TYPE      AGE
vmware-prod    True    True        True        vsphere   2m
```

阿明鬆了一口氣，*果然第一次都不會成功。*

他注意到 `INVENTORY` 欄位也變成了 `True`。他還不確定這代表什麼，但直覺告訴他這跟「Forklift 是否已經把 vSphere 的 VM 清單拉回來」有關。

除了來源 Provider，阿明還建立了一個目標 Provider，指向當前的 KubeVirt（OpenShift Virtualization）叢集。這個比較簡單——Forklift 有一個預設的 `host` Provider 代表本地叢集，通常不需要額外建立。

---

> ### 📚 去這裡深入了解
> - [核心功能](/forklift/core-features) — Provider 抽象層的設計：為什麼各種異質平台都能用同一個 CRD 描述
> - [控制器與 API](/forklift/controllers-api) — ProviderController 的 Reconcile 邏輯：READY/CONNECTED/INVENTORY 三個狀態的意義
>
> 讀完後，你應該能說明：Provider 的三個狀態欄位各代表什麼？為什麼要分開？

---

## 第三章：「Inventory——Forklift 怎麼知道 vSphere 裡有什麼？」

Provider 建好了，`INVENTORY: True`。阿明想知道 Forklift 到底拉到了哪些資料。

他找到了 Forklift 提供的 REST API，試著查詢 Inventory：

```bash
kubectl port-forward svc/forklift-inventory -n konveyor-forklift 8080:8080 &

curl http://localhost:8080/providers/vsphere/vmware-prod/vms | jq '.[].name'
```

輸出讓他驚喜——整個 vSphere 環境裡的 53 台 VM 全部列出來了，連同每台 VM 的 CPU 數量、記憶體大小、磁碟清單、所在的 Host 和 Cluster 都有。

*Forklift 不只是「連上 vSphere」，它把整個環境的 inventory 都快取下來了。*

他繼續查：

```bash
# 列出所有 Network（Port Group）
curl http://localhost:8080/providers/vsphere/vmware-prod/networks | jq '.[].name'

# 列出所有 Datastore
curl http://localhost:8080/providers/vsphere/vmware-prod/datastores | jq '.[].name'
```

vSphere 的網路：`VM Network`、`VLAN-100-Prod`、`VLAN-200-Dev`
vSphere 的 Datastore：`SSD-Datastore-01`、`HDD-Datastore-01`、`NFS-Datastore-Archive`

阿明把這些名稱記下來。他意識到，接下來要做的事就是把這些 vSphere 的資源「對應」到 KubeVirt 這邊的資源——NetworkAttachmentDefinition 和 StorageClass。

這個 Inventory 機制很重要：它讓 Forklift 不需要在每次建立 Plan 的時候都即時查詢 vSphere（那樣太慢了）。Forklift 的 `inventory` 容器會定期同步，把 vSphere 的狀態快取在本地的資料庫裡，讓 UI 和 API 查詢都能快速回應。

阿明測試了一件事：他在 vSphere 裡建了一台新 VM，然後等了大約兩分鐘，再次查詢——新的 VM 出現了。Forklift 的 Inventory 有週期性同步機制，不是即時的，但頻率夠高。

*好，我知道 vSphere 裡有什麼了。接下來要告訴 Forklift 網路要怎麼對應。*

---

> ### 📚 去這裡深入了解
> - [系統架構](/forklift/architecture) — Inventory Controller 的架構：Provider Adapter 如何翻譯各平台的 API
> - [外部整合](/forklift/integration) — vSphere 整合細節：Forklift 怎麼透過 vSphere API 收集 VM、Network、Datastore 資訊
>
> 讀完後，你應該能說明：Forklift 的 Inventory 是如何保持與來源平台同步的？

---

## 第四章：「NetworkMap——兩邊的網路要怎麼接在一起？」

阿明面對著兩份清單：

**vSphere 的網路**（來源）：
- `VM Network`（管理用）
- `VLAN-100-Prod`（生產環境）
- `VLAN-200-Dev`（開發環境）

**KubeVirt 這邊的 NetworkAttachmentDefinition**（目標）：
- `default/pod-network`（Pod 網路，NAT）
- `kubevirt/prod-nad`（透過 Multus 接到生產 VLAN）
- `kubevirt/dev-nad`（透過 Multus 接到開發 VLAN）

他的工作是建立一個 **`NetworkMap`** CRD，告訴 Forklift 這兩邊怎麼對應。

```yaml
apiVersion: forklift.konveyor.io/v1beta1
kind: NetworkMap
metadata:
  name: vmware-network-map
  namespace: konveyor-forklift
spec:
  provider:
    source:
      name: vmware-prod
      namespace: konveyor-forklift
    destination:
      name: host
      namespace: konveyor-forklift
  map:
    - source:
        name: VM Network
      destination:
        type: pod
    - source:
        name: VLAN-100-Prod
      destination:
        type: multus
        name: kubevirt/prod-nad
    - source:
        name: VLAN-200-Dev
      destination:
        type: multus
        name: kubevirt/dev-nad
```

第一個對應（`VM Network` → `pod`）代表：連在 `VM Network` 上的網路卡，遷移後接到 K8s 的 Pod 網路，透過 Masquerade 做 NAT。這適合只需要對外連線、不需要固定 IP 的 VM。

阿明一開始把 `VM Network` 對應到 `kubevirt/mgmt-nad`，但後來發現那個 NAD 是他之前測試用的，設定不對。幸好 NetworkMap 只是一個描述，不會立刻產生任何效果，修改很容易。

他又遇到了一個問題：有幾台 VM 在 vSphere 裡連接到了多個 Port Group（雙網卡 VM）。他查了 Forklift 的文件，確認 NetworkMap 是基於「來源 VM 有這張 NIC 連接到這個 Port Group」來做對應的——只要在 `map` 裡把所有可能出現的 Port Group 都列出來，Forklift 就知道每張 NIC 要接到哪個目標網路。

*這比我原本想的簡單一些。不需要逐台 VM 設定，只要定義好「規則」，所有 VM 都自動套用。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/forklift/core-features) — NetworkMap 的設計：Provider 抽象層如何統一描述異質網路環境
> - [控制器與 API](/forklift/controllers-api) — NetworkMapController 的 CRD 型別定義與 Validation Webhook
>
> 讀完後，你應該能說明：NetworkMap 的 `destination.type` 有哪些值？各適合什麼場景？

---

## 第五章：「StorageMap——VMDK 要轉換成哪種 StorageClass？」

網路對應解決了，接下來是儲存對應。阿明再次拿出兩份清單：

**vSphere 的 Datastore**（來源）：
- `SSD-Datastore-01`（快速，跑 DB 的 VM）
- `HDD-Datastore-01`（一般用途）
- `NFS-Datastore-Archive`（歸檔，很少存取）

**KubeVirt 這邊的 StorageClass**（目標）：
- `ceph-block-ssd`（Ceph RBD，SSD 等級）
- `ceph-block-hdd`（Ceph RBD，HDD 等級）
- `nfs-slow`（NFS，適合歸檔）

對應關係很直覺，他建立了 **`StorageMap`**：

```yaml
apiVersion: forklift.konveyor.io/v1beta1
kind: StorageMap
metadata:
  name: vmware-storage-map
  namespace: konveyor-forklift
spec:
  provider:
    source:
      name: vmware-prod
      namespace: konveyor-forklift
    destination:
      name: host
      namespace: konveyor-forklift
  map:
    - source:
        name: SSD-Datastore-01
      destination:
        storageClass: ceph-block-ssd
    - source:
        name: HDD-Datastore-01
      destination:
        storageClass: ceph-block-hdd
    - source:
        name: NFS-Datastore-Archive
      destination:
        storageClass: nfs-slow
```

阿明在這裡停下來想了一個問題：*如果一台 VM 有多個磁碟，分別在不同的 Datastore，會怎樣？*

他找到答案了：StorageMap 的對應是基於「磁碟所在的 Datastore」，所以同一台 VM 的不同磁碟可以被對應到不同的 StorageClass。Forklift 會在遷移時為每個磁碟建立獨立的 PVC，並根據 StorageMap 選擇對應的 StorageClass。

*這比手動搬的時候靈活多了。手動搬的時候，我每次都得看這台 VM 的磁碟在哪個 Datastore，然後手動決定 PVC 要用哪個 StorageClass。現在只要定義好規則，Forklift 自動套用。*

還有一件事：磁碟格式的轉換。VMware 的 VMDK 需要轉換成 KubeVirt 能用的格式。這個工作是由 **virt-v2v** 完成的——在遷移過程中，Forklift 會啟動一個 virt-v2v Job，負責把 VMDK 讀進來、轉換成 RAW 或 QCOW2，然後寫進 PVC。StorageMap 裡的 StorageClass 就是 virt-v2v 寫入目標的 PVC 所使用的 StorageClass。

---

> ### 📚 去這裡深入了解
> - [核心功能](/forklift/core-features) — StorageMap 與磁碟轉換：virt-v2v 如何將 VMDK 轉換為 KubeVirt 格式
> - [系統架構](/forklift/architecture) — virt-v2v 在遷移流程中的角色
>
> 讀完後，你應該能說明：StorageMap 如何處理同一台 VM 多個磁碟跨越不同 Datastore 的情況？

---

## 第六章：「Plan——把所有設定組合成一個遷移計畫」

Provider、NetworkMap、StorageMap 都準備好了。阿明終於可以建立 **`Plan`**——把這些設定組合起來，定義「要遷移哪些 VM」。

他決定先做一個小規模的測試 Plan，只遷移三台 VM，確認整個流程沒問題後再批量處理。

```yaml
apiVersion: forklift.konveyor.io/v1beta1
kind: Plan
metadata:
  name: vmware-migration-test
  namespace: konveyor-forklift
spec:
  provider:
    source:
      name: vmware-prod
      namespace: konveyor-forklift
    destination:
      name: host
      namespace: konveyor-forklift
  targetNamespace: migrated-vms
  networkMap:
    name: vmware-network-map
    namespace: konveyor-forklift
  storageMap:
    name: vmware-storage-map
    namespace: konveyor-forklift
  vms:
    - name: web-server-01
    - name: app-server-02
    - name: db-server-03
```

`kubectl apply` 之後，阿明查看 Plan 的狀態：

```
kubectl get plan vmware-migration-test -n konveyor-forklift
NAME                     READY   EXECUTING   SUCCEEDED   FAILED   AGE
vmware-migration-test    True    False       0           0        30s
```

`READY: True` 表示 Plan 驗證通過，所有的 Provider、NetworkMap、StorageMap 都正確。但 `EXECUTING: False` 表示遷移還沒開始——這是預期的行為。**Plan 只是描述「要做什麼」，不會自動開始執行**。要觸發實際的遷移，需要建立 `Migration` 資源。

阿明發現 Plan 還有一個有趣的欄位：`warm`。這是 Warm Migration 的開關，他現在先設定為 `false`（Cold Migration）。等第一批測試 VM 遷移成功後，再研究 Warm Migration。

他還注意到 `targetNamespace: migrated-vms`——遷移後的 VM 資源會建立在這個 Namespace 裡。他先 `kubectl create namespace migrated-vms` 確保 Namespace 存在。

*計畫建好了。感覺就像是寫了一份工作規格書——把要做什麼、怎麼做都寫清楚，但還沒有人開始動工。*

---

> ### 📚 去這裡深入了解
> - [控制器與 API](/forklift/controllers-api) — PlanController 的架構：Plan CRD 的欄位定義、Validation 規則
> - [核心功能](/forklift/core-features) — 遷移流程全貌：Plan 如何協調 NetworkMap、StorageMap 與 VM 清單
>
> 讀完後，你應該能說明：為什麼 Plan 和 Migration 要分成兩個 CRD？這樣設計有什麼好處？

---

## 第七章：「Migration——觀察 virt-v2v 的轉換過程」

阿明深吸一口氣，建立了第一個 **`Migration`** 資源：

```yaml
apiVersion: forklift.konveyor.io/v1beta1
kind: Migration
metadata:
  name: test-migration-01
  namespace: konveyor-forklift
spec:
  plan:
    name: vmware-migration-test
    namespace: konveyor-forklift
```

`kubectl apply`。

幾秒鐘後，他開始看到動靜：

```bash
kubectl get migration test-migration-01 -n konveyor-forklift -w
NAME               READY   RUNNING   SUCCEEDED   FAILED   AGE
test-migration-01  True    True      0           0        15s
test-migration-01  True    True      0           0        2m
test-migration-01  True    False     1           0        8m
```

第一台 VM 在 8 分鐘後遷移成功。阿明切到另一個視窗，看看到底發生了什麼：

```bash
kubectl get pods -n konveyor-forklift -w
```

他看到 Forklift 啟動了一系列 Pod：

1. **`importer-*` Pod**（CDI 的 DataVolume importer）：先建立目標 PVC，準備接收磁碟資料
2. **`virt-v2v-*` Pod**：這才是真正的主角。這個 Pod 連接到 vSphere，把 VM 的 VMDK 讀出來，進行格式轉換，然後寫進目標 PVC

阿明對 virt-v2v 的 log 很好奇，他 `kubectl logs` 看了一下：

```
virt-v2v: Reusing disk: web-server-01-disk0
virt-v2v: Converting disk 1 of 1 (web-server-01-disk0)
virt-v2v: Checking for Windows
virt-v2v: This is a Linux guest
virt-v2v: Detected kernel: vmlinuz-5.15.0-91-generic
virt-v2v: Installing virtio drivers
virt-v2v: Disk conversion complete
```

*virt-v2v 不只是複製磁碟，它還在轉換 guest OS 的驅動程式！*

這一點讓阿明眼睛一亮。VMware 的 VM 裡通常裝了 VMware Tools 和 VMXNET3 驅動，這些在 KubeVirt（QEMU/KVM）環境裡無法使用。virt-v2v 會自動把 VMware 的驅動替換成 VirtIO 驅動，讓 VM 在新環境裡能正常開機和運作。

遷移完成後，阿明去 `migrated-vms` Namespace 看：

```bash
kubectl get vm -n migrated-vms
NAME             AGE    STATUS    READY
web-server-01    12m    Stopped   False
```

VM 資源建立了，狀態是 `Stopped`——Forklift 不會自動開機，讓工程師有機會先確認設定，手動啟動。阿明用 `virtctl start web-server-01 -n migrated-vms` 開機，過了一分鐘，VM 跑起來了，網路也通了。

*第一台遷移成功。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/forklift/core-features) — 磁碟轉換機制：virt-v2v 如何替換 VMware 驅動並安裝 VirtIO
> - [外部整合](/forklift/integration) — CDI 整合：Migration 如何透過 DataVolume 建立 PVC
> - [系統架構](/forklift/architecture) — MigrationController 的工作流程：從 Migration CR 到 VM 資源建立
>
> 讀完後，你應該能說明：virt-v2v 在遷移流程中做了哪些工作？為什麼磁碟複製和驅動替換都是必要的？

---

## 第八章：「Warm Migration——五十台 VM 不能都停機等搬遷」

第一批三台測試 VM 成功了。但接下來阿明面臨一個現實問題：有些 VM 是生產環境的服務，停機時間不能超過幾分鐘。但 Cold Migration（完整複製磁碟再開機）對一台有 200GB 磁碟的 VM 來說，可能要等幾個小時。

他開始研究 **Warm Migration**。

Warm Migration 的核心思想是：在 VM 還在運行的時候，先用 CBT（Changed Block Tracking，VMware 的增量備份機制）把大部分磁碟資料複製過去；等到真正要切換的時候，再做一次短暫的增量同步，然後關機、最終同步、開機。整個停機時間可以從幾小時縮短到幾分鐘。

要啟用 Warm Migration，首先要在 vSphere 這邊確認 CBT 已啟用。阿明查了一下，大部分 VM 預設是開啟的，只有少數老舊 VM 需要手動開啟。

然後他修改 Plan，加上 `warm: true`：

```yaml
spec:
  warm: true
  # ... 其他設定不變
```

重新建立 Migration 後，阿明觀察到行為完全不同：

```bash
kubectl get migration warm-migration-01 -n konveyor-forklift
NAME                  READY   RUNNING   PRECOPY   CUTOVER   SUCCEEDED
warm-migration-01     True    True      True      False     0
```

`PRECOPY: True` 表示 Forklift 正在進行預複製（Pre-copy）階段——把 VM 當前的磁碟資料複製到目標 PVC，同時 VM 仍然在 vSphere 上正常運行。

幾個小時後，Pre-copy 完成。現在阿明需要手動觸發 **Cutover**——這是告訴 Forklift「現在可以進行最終切換了」的動作：

```bash
kubectl patch migration warm-migration-01 \
  -n konveyor-forklift \
  --type merge \
  -p '{"spec":{"cutover":"2024-03-15T03:00:00Z"}}'
```

他設定了凌晨三點進行 Cutover——業務量最低的時候。到了那個時間點，Forklift 自動：
1. 做最後一次增量同步（只複製 Pre-copy 期間變更的 Block）
2. 關閉 vSphere 上的 VM
3. 完成磁碟的最終同步
4. 在 KubeVirt 上建立 VM 並開機

停機時間：6 分鐘。

*從幾小時到 6 分鐘。這個技術值得花時間學。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/forklift/core-features) — Warm Migration 機制：CBT 的工作原理、Pre-copy 與 Cutover 的協調
> - [外部整合](/forklift/integration) — vSphere 整合：CBT API 的使用方式
>
> 讀完後，你應該能說明：什麼情況下應該用 Warm Migration？Pre-copy 階段需要多久？如何決定 Cutover 的時機？

---

## 第九章：「遷移失敗——怎麼找出問題在哪？」

在遷移 53 台 VM 的過程中，並不是每次都這麼順利。阿明遇到了幾次失敗，每次都要花時間排查。

**失敗案例一：virt-v2v 磁碟讀取失敗**

一台 Windows Server 2012 的 VM 遷移失敗了：

```bash
kubectl get migration win2012-migration -n konveyor-forklift
NAME               READY   SUCCEEDED   FAILED
win2012-migration  True    0           1
```

阿明去找失敗的詳細資訊：

```bash
kubectl describe migration win2012-migration -n konveyor-forklift
```

在 Events 裡找到：`virt-v2v failed: unable to read disk: disk is locked`

*磁碟被鎖住了？*

他回到 vSphere 查，發現那台 VM 有一個 Snapshot 正在進行中——是 VM Backup 軟體自動觸發的。Snapshot 存在時，VMDK 處於鎖定狀態，virt-v2v 無法讀取。

解法：等 Backup 完成（或暫停 Backup 排程），刪除 Snapshot，重新觸發 Migration。

**失敗案例二：目標 StorageClass 空間不足**

一台有 500GB 磁碟的 VM 遷移到一半失敗：

```
virt-v2v: disk write failed: no space left on device
```

阿明用 `kubectl get pvc -n migrated-vms` 查看，發現 PVC 的 `CAPACITY` 只有 200Gi——StorageClass 的預設限制。他需要在 Plan 裡為這台 VM 明確指定磁碟大小：

```yaml
spec:
  vms:
    - name: big-data-vm
      hooks: []
      # 指定磁碟大小覆蓋
```

實際上 Forklift 會根據來源 VMDK 的大小自動計算目標 PVC 的大小，這個問題是因為他的 `ceph-block-hdd` StorageClass 有 `maxVolumeSize` 限制。解法是修改 StorageClass 設定或換用沒有大小限制的 StorageClass。

**失敗案例三：網路對應遺漏**

有幾台 VM 開機後網路不通，查了一下，發現這些 VM 有一張 NIC 連到了 `VLAN-300-DB`，但他的 NetworkMap 裡沒有這個 Port Group 的對應。Forklift 預設把找不到對應的 NIC 連到 Pod 網路，但那個 VLAN-300-DB 是資料庫專用的內部 VLAN，不應該走 NAT。

解法：更新 NetworkMap，加上 `VLAN-300-DB` 的對應，然後重新執行 Migration。

*每次失敗都是一次學習。但重點是失敗訊息要夠清楚，讓你知道去哪裡找問題。*

阿明總結了一份排查清單，貼在 Confluence 頁面上，供團隊參考。

---

> ### 📚 去這裡深入了解
> - [控制器與 API](/forklift/controllers-api) — Migration 的狀態機與 Condition 欄位：如何讀懂失敗原因
> - [外部整合](/forklift/integration) — vSphere 整合的已知限制：Snapshot、CBT 限制、憑證問題
>
> 讀完後，你應該能說明：遇到 Migration 失敗時，應該按什麼順序排查問題？

---

## 第十章：「規模化——五十台 VM 的批量策略」

測試成功、問題也基本排查清楚了。現在阿明需要在剩下的兩週半內遷移剩餘的 50 台 VM。

他制定了以下策略：

**1. 按風險分批**

他把 50 台 VM 分成三個批次：
- **批次一（低風險）**：開發環境、測試環境的 VM（15 台）。先做，熟悉流程，確認 NetworkMap 和 StorageMap 設定正確。
- **批次二（中風險）**：Staging 環境和非關鍵生產服務（20 台）。用 Warm Migration，在離峰時間切換。
- **批次三（高風險）**：核心資料庫和關鍵服務（15 台）。提前兩週通知相關團隊，安排維護時窗，準備回滾方案。

**2. 用多個 Plan 分類管理**

一個 Plan 可以包含多台 VM，但阿明發現把所有 VM 塞進同一個 Plan 不方便追蹤。他決定按業務系統分 Plan：

```
plan-batch1-dev          15 台 VM
plan-batch2-staging      20 台 VM
plan-batch3-prod-web     10 台 VM
plan-batch3-prod-db       5 台 VM
```

每個 Plan 有獨立的進度追蹤，某個 Plan 失敗不會影響其他 Plan。

**3. 並行遷移加速**

Forklift 支援多台 VM 並行遷移。阿明在 Plan 裡設定了 `maxInFlight` 參數，控制同時進行 virt-v2v 轉換的 VM 數量——設太高會吃滿網路頻寬和 ESXi 的 I/O，設太低則進度太慢。他測試後發現設定 5-8 個並行比較合適。

**4. Hook 做自動化後處理**

有幾台 VM 遷移完成後需要執行一些初始化指令碼（例如更換 IP 設定、更新 DNS 記錄）。Forklift 支援 `Hook` CRD，可以在 VM 遷移完成後自動執行 Ansible Playbook 或自定義腳本。

阿明建立了一個 Hook：

```yaml
apiVersion: forklift.konveyor.io/v1beta1
kind: Hook
metadata:
  name: post-migration-config
  namespace: konveyor-forklift
spec:
  image: quay.io/konveyor/hook-runner:latest
  playbook: |
    - hosts: all
      tasks:
        - name: Update network config
          # ... Ansible tasks
```

然後在 Plan 的 VM 清單裡引用這個 Hook：

```yaml
spec:
  vms:
    - name: web-server-01
      hooks:
        - hook:
            name: post-migration-config
            namespace: konveyor-forklift
          step: PostRestart
```

**最終結果**

第四週結束時，阿明盯著 Forklift 的狀態：

```bash
kubectl get migration -n konveyor-forklift
NAME                    SUCCEEDED   FAILED
batch1-migration        15          0
batch2-migration        20          0
batch3-web-migration    10          0
batch3-db-migration      5          0
```

53 台 VM，全部成功遷移。失敗數：0（那三次失敗都是在測試階段，後來全部解決了）。

阿明把 Confluence 頁面更新，把整個遷移流程的文件寫好，附上所有的 YAML 範本和排查清單。然後他關掉電腦，終於去把那杯從一個月前就沒喝完的咖啡加熱了一下。

*任務完成。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/forklift/core-features) — Plan 的進階設定：maxInFlight、Hook、Warm Migration 的組合使用
> - [控制器與 API](/forklift/controllers-api) — Hook CRD 設計與 hook-runner 執行機制
> - [系統架構](/forklift/architecture) — Forklift 的整體架構回顧：現在你應該能看懂每個元件的職責
>
> 讀完後，你應該能設計一個針對你自己環境的批量遷移策略——包括如何分批、如何設定並行度、如何處理遷移後的自動化配置。

---

## 尾聲

阿明的故事到這裡結束了，但技術的探索沒有終點。

你現在應該能夠：

- ✅ 建立 `Provider`，連接 vSphere 或其他遷移來源
- ✅ 理解 Inventory 機制，知道 Forklift 如何探索來源環境
- ✅ 建立 `NetworkMap` 和 `StorageMap`，定義資源對應關係
- ✅ 建立 `Plan`，組合所有設定並指定要遷移的 VM
- ✅ 觸發 `Migration`，觀察 virt-v2v 的轉換過程
- ✅ 使用 Warm Migration，將停機時間縮短到分鐘級別
- ✅ 排查常見的遷移失敗原因
- ✅ 設計批量遷移策略，處理大規模遷移場景

如果你想深入了解 Forklift 的內部實作，歡迎閱讀完整的技術文件：

::: info 📚 完整技術文件
- [系統架構](/forklift/architecture) — Controller 架構、CRD 設計、virt-v2v 整合
- [核心功能](/forklift/core-features) — 遷移流程、Provider 抽象層、磁碟轉換、Warm Migration
- [控制器與 API](/forklift/controllers-api) — 每個 Controller 的職責、CRD 型別、Webhook、REST API
- [外部整合](/forklift/integration) — KubeVirt、CDI、vSphere、oVirt、OpenStack、Hyper-V 的整合細節
:::
