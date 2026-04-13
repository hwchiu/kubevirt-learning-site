---
layout: doc
title: CDI — 學習路徑：阿明的故事
---

# 📖 CDI 學習之旅：阿明的故事

> 跟著阿明，從接到「把公司 VMware VM 磁碟搬進 K8s」這個任務開始，一步步理解 CDI 的世界。
> 每個章節都是阿明真實遭遇的問題——你會看到他怎麼查文件、怎麼犯錯、怎麼一點一點把拼圖拼起來。

---

## 序章：VM 磁碟要放哪裡？

KubeVirt 裝好了。阿明花了整整一週，把公司的測試叢集改裝成一個能跑 VM 的 K8s 環境。他給 VP 的週報上寫著：「KubeVirt 安裝完成，基本驗證 OK，下週開始進行 Pilot 遷移。」

然後他打開了第一台要遷移的 VM 的資料：一台跑著 Ubuntu 22.04 的資料庫 VM，磁碟大小 80GB，目前是 VMware 的 VMDK 格式。

*好，現在要怎麼把這個磁碟放進 K8s？*

他看著 KubeVirt 的 VirtualMachine YAML，裡面有一個 `volumes` 欄位，可以掛載 `persistentVolumeClaim`。所以理論上流程是：
1. 把 VMDK 轉換成 QCOW2 或 RAW 格式
2. 把映像檔「放進」某個 PVC
3. 讓 VM 掛這個 PVC 開機

步驟一他知道怎麼做（`qemu-img convert`）。但步驟二呢？

*「把映像放進 PVC」……PVC 就是一塊空的磁碟，我要怎麼把一個檔案複製進去？*

他試了各種方法：
- 掛一個 PVC 到 Pod 裡，然後 `kubectl cp` 把映像傳進去——但 80GB 的檔案要怎麼傳？而且 PVC 的 filesystem 是空的，直接 `dd` 進去嗎？
- 用 `hostPath` volume 先在 Node 上準備好資料？但這樣就綁死在特定 Node 了，不對。

他在 Slack 上問了其他同事，得到的回覆是：「你可以試試 CDI。」

*CDI？Containerized Data Importer？這又是什麼？*

---

> ### 📚 去這裡深入了解
> 阿明的困惑——「為什麼光有 PVC 還不夠？CDI 解決的是什麼問題？」——在這裡有答案：
>
> - [CDI 專案簡介](/containerized-data-importer/) — 了解 CDI 的設計動機與核心功能概覽
>
> 讀完後，你應該能清楚說明：CDI 在 K8s 的儲存體系裡，填補了哪個環節的空白？

---

## 第一章：「聰明的 PVC」——DataVolume 的登場

阿明開始研究 CDI。

第一個看到的概念是 **DataVolume**。文件說它是一種 CRD，用來「自動化地把資料匯入 PVC 的過程」。阿明剛開始看得一頭霧水，因為文件的措辭很技術性。於是他換個角度，直接看一個範例 YAML：

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: ubuntu-disk
spec:
  source:
    http:
      url: "https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img"
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 10Gi
```

他盯著這個 YAML 看了兩分鐘。

*等等……我只需要告訴它「來源 URL」和「我想要多大的 PVC」，它就會自動幫我下載、然後把資料放進 PVC？*

他決定直接試試看：

```bash
kubectl apply -f ubuntu-dv.yaml
kubectl get datavolume ubuntu-disk -w
```

輸出開始滾動：

```
NAME          PHASE       PROGRESS   RESTARTS   AGE
ubuntu-disk   Pending                           2s
ubuntu-disk   ImportScheduled                   4s
ubuntu-disk   ImportInProgress   0.00%          8s
ubuntu-disk   ImportInProgress   12.34%         30s
ubuntu-disk   ImportInProgress   67.89%         2m
ubuntu-disk   Succeeded          100.0%         4m
```

成功了。阿明興奮地跑去看 PVC：

```bash
kubectl get pvc ubuntu-disk
```

```
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES
ubuntu-disk   Bound    pvc-3a1c8f2e-...                          10Gi       RWO
```

PVC 自動建立了，而且已經有資料在裡面。他快速建了一個 VM，掛上這個 PVC，VM 真的開機了。

*DataVolume 就是一個「帶有下載功能的 PVC」*，他在筆記本上寫下這句話，然後在旁邊加上：*更精確的說法：DataVolume 是一個對 PVC 的生命週期管理器——它負責建 PVC、填資料、追蹤進度。*

普通 PVC 只是一塊空的磁碟。DataVolume 是一塊**帶有資料來源**的磁碟。這一個差別，解決了阿明一整週的困惑。

---

> ### 📚 去這裡深入了解
> DataVolume 的完整設計，包括它的狀態機（從 Pending 到 Succeeded 的每個 Phase）：
>
> - [系統架構](/containerized-data-importer/architecture) — DataVolume CRD 定義與狀態機詳解
> - [核心功能](/containerized-data-importer/core-features) — DataVolume 的各種資料來源類型
>
> 讀完後，你應該能解釋：DataVolume 的 Phase 有哪些？每個 Phase 代表什麼意思？

---

## 第二章：從 HTTP URL 匯入映像的細節

阿明的第一個真實任務：從公司的內部映像伺服器匯入一個 Ubuntu cloud image。

他的 HTTP 伺服器已經準備好了，URL 是 `http://images.internal.company.com/ubuntu-22.04.qcow2`，檔案是 QCOW2 格式，大小 3.5GB（壓縮後）。

他複製了上一章的 DataVolume YAML，改了 URL 和 storage 大小：

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: ubuntu-2204
spec:
  source:
    http:
      url: "http://images.internal.company.com/ubuntu-22.04.qcow2"
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 20Gi
```

Apply 之後，他開始等。進度條到了 34% 就卡住了。等了十分鐘還是 34%。

*壞了？*

他去看 CDI 建立的 importer Pod：

```bash
kubectl get pods | grep importer
# importer-ubuntu-2204-xxxxx   0/1   CrashLoopBackOff
```

看 log：

```bash
kubectl logs importer-ubuntu-2204-xxxxx
# ...
# E] Failed to read image header: qemu-img: Could not open 'disk.img':
#    Could not read file header
# I] total size is: 20Gi
```

*映像壞掉了嗎？*

他用 `curl` 下載映像到本機測試：

```bash
curl -O http://images.internal.company.com/ubuntu-22.04.qcow2
qemu-img info ubuntu-22.04.qcow2
```

本機下載完全正常。他重新看了 log，發現一個關鍵字：**Scratch Space**。

```
W] scratch space is required for QCOW2 conversion but no scratch space PVC found
```

*Scratch Space 是什麼？*

原來 CDI 在匯入 QCOW2 格式的映像時，需要一個**臨時的工作空間**——它會先把原始映像下載到 Scratch PVC，在那裡做格式轉換（QCOW2 → RAW），再把轉換好的資料寫進目標 PVC。

問題是，Scratch Space 需要額外的儲存空間，而阿明的測試叢集的 StorageClass 沒有設定為 CDI 的 Scratch 使用。他去查了 CDIConfig：

```bash
kubectl get cdiconfig -o yaml | grep -A5 scratchSpaceStorageClass
```

輸出顯示 `scratchSpaceStorageClass: ""` — 沒有設定。

他設定了預設的 Scratch StorageClass：

```bash
kubectl patch cdiconfig config --type merge \
  -p '{"spec":{"scratchSpaceStorageClass":"standard"}}'
```

然後刪除舊的 DataVolume，重新建立。這次，進度條順暢地跑完了。

---

> ### 📚 去這裡深入了解
> HTTP 匯入的完整流程，以及 Scratch Space 的設計原因：
>
> - [核心功能](/containerized-data-importer/core-features) — ImportFromURL 流程、Scratch Space 機制、格式轉換
> - [系統架構](/containerized-data-importer/architecture) — Importer Binary 的工作原理
>
> 讀完後，你應該能解釋：什麼情況下 CDI 需要 Scratch Space？Scratch Space 的資料流是什麼？

---

## 第三章：上傳本地映像（Upload）

公司的 IT 部門把那台 VMware VM 的磁碟匯出來了——一個 4.2GB 的 VMDK 檔案，放在阿明的筆電上。問題是，這個檔案在本地，沒有 HTTP 伺服器可以存取。

*那……我要怎麼把本機的檔案傳進 K8s？*

他查了 CDI 的文件，找到了 **Upload** 功能。CDI 提供了一個 `cdi-uploadproxy` 服務，可以讓你直接把本機的映像上傳到 PVC，而不需要先架設 HTTP 伺服器。

CDI 還提供了一個 CLI 工具：`virtctl image-upload`（來自 KubeVirt 的 virtctl）。

阿明先建立一個 DataVolume，指定來源為 Upload：

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: vmware-disk
spec:
  source:
    upload: {}
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 50Gi
```

```bash
kubectl apply -f vmware-upload-dv.yaml
```

這時 DataVolume 的 Phase 會變成 `UploadReady`，等待上傳。接著他用 `virtctl` 做上傳：

```bash
virtctl image-upload \
  --image-path=./vmware-disk.vmdk \
  --pvc-name=vmware-disk \
  --pvc-size=50Gi \
  --uploadproxy-url=https://cdi-uploadproxy.cdi.svc \
  --insecure \
  --wait-secs=240
```

畫面上出現進度條：

```
Uploading data to https://cdi-uploadproxy.cdi.svc
 4.20 GiB / 4.20 GiB [===================] 100.00% 45s
Uploading data completed successfully, waiting for processing to complete,
you can hit ctrl-c without interrupting the progress
Processing completed successfully
```

*這也太方便了。*

但阿明注意到，`virtctl image-upload` 執行的時候有個 `--insecure` 旗標。他去查了 `cdi-uploadproxy` 的 Service，發現它預設是用自簽憑證，在生產環境需要設定真正的 TLS 憑證。他在待辦清單上寫下：「生產環境前要處理 uploadproxy TLS」。

另外，他發現上傳流程其實也做了格式轉換——VMDK 被自動轉成了 RAW 格式。這讓他意識到，CDI 的「上傳」不只是搬資料，還包含了格式處理的邏輯。

---

> ### 📚 去這裡深入了解
> Upload 的完整流程，以及 uploadproxy 的架構：
>
> - [核心功能](/containerized-data-importer/core-features) — Upload 功能的運作方式
> - [控制器與 API](/containerized-data-importer/controllers-api) — Upload Server 與 UploadProxy 的 API 設計
>
> 讀完後，你應該能解釋：Upload 的資料流是什麼？本機映像是直接傳給哪個元件的？

---

## 第四章：PVC Clone——複製磁碟

第一批 VM 遷移完成了。阿明接到了下一個任務：「我們需要同樣的 Ubuntu 基底映像，建立 20 台 VM，每台都要有獨立的磁碟。」

*20 台……難道要匯入 20 次？*

他查了一下，發現 CDI 有 **Clone** 功能。DataVolume 的 `source` 可以指定為 `pvc`，從一個現有的 PVC 複製資料：

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: ubuntu-vm-01
spec:
  source:
    pvc:
      namespace: default
      name: ubuntu-base-image
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 20Gi
```

他建立了第一個 Clone，很快就完成了。接著他寫了一個簡單的 shell script，迴圈建立 20 個 DataVolume：

```bash
for i in $(seq -w 1 20); do
  cat <<EOF | kubectl apply -f -
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: ubuntu-vm-${i}
spec:
  source:
    pvc:
      namespace: default
      name: ubuntu-base-image
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 20Gi
EOF
done
```

他興奮地看著 20 個 DataVolume 同時開始建立——但有些很快完成，有些卡很久。他去查看慢的那幾個：

```bash
kubectl get datavolume | grep -v Succeeded
# ubuntu-vm-15   CloneScheduled   ...
# ubuntu-vm-16   CloneScheduled   ...
```

去看 events：

```
Warning  CloneNotReady  datavolume/ubuntu-vm-15
  clone not feasible: source PVC is not ReadWriteMany,
  cannot do smart clone, falling back to host-assisted clone
```

*Smart Clone？Host-assisted Clone？又有兩種？*

阿明查了文件，才理解 CDI 的 Clone 有三種路徑，效能差異很大：

1. **Network Clone（Host-Assisted Clone）**：資料要透過網路傳輸——Importer Pod 把來源 PVC 的資料讀出來，透過網路傳給目標 PVC。最慢，但永遠能用。
2. **Smart Clone（Snapshot-based Clone）**：如果 StorageClass 支援 VolumeSnapshot，CDI 會先對來源 PVC 建立 Snapshot，再從 Snapshot 建立新的 PVC。速度非常快，幾乎是瞬間完成。
3. **CSI Clone**：如果 CSI driver 支援 `VolumeCloneSource`，CDI 直接呼叫 CSI 的 Clone API，在儲存層完成複製，完全不需要搬資料。

他的慢速叢集 StorageClass 不支援 Snapshot，所以只能用最慢的 Host-Assisted Clone。他在待辦清單上又加了一條：「評估支援 VolumeSnapshot 的 StorageClass」。

---

> ### 📚 去這裡深入了解
> Clone 的三種路徑及其選擇條件：
>
> - [核心功能](/containerized-data-importer/core-features) — PVC Clone 的三種模式與效能比較
> - [外部整合](/containerized-data-importer/integration) — CSI 整合與 VolumeSnapshot 支援
>
> 讀完後，你應該能解釋：CDI 如何決定使用哪種 Clone 路徑？什麼條件會觸發 Smart Clone？

---

## 第五章：Scratch Space 的秘密

阿明在第二章已經遇過 Scratch Space 的問題了。但那時只是「改個設定讓它消失」，他從來沒有真正理解為什麼需要它。

今天他遇到了一個新問題：一個大型的 QCOW2 映像（壓縮後 8GB，解壓後 40GB）匯入時失敗了，錯誤訊息是：

```
E] scratch space PVC ubuntu-large-scratch is full
   available: 8Gi, required: 40Gi
```

*Scratch Space 的大小是怎麼決定的？*

阿明開始深入研究 Scratch Space 的機制。他找到了答案：

CDI 在匯入 QCOW2 格式的映像時，需要做兩件事：
1. **下載原始映像**（3.5GB 壓縮的 QCOW2）到 Scratch PVC
2. **格式轉換**：用 `qemu-img convert` 把 QCOW2 轉成 RAW

問題是，格式轉換的目標大小不是「壓縮後的大小」，而是「虛擬磁碟的實際大小」。一個 8GB 壓縮的 QCOW2，如果它代表一個 40GB 的虛擬磁碟，轉換後的 RAW 檔案就會是 40GB。Scratch PVC 需要夠大才能容納轉換結果。

CDI 預設的 Scratch Space 大小等於目標 PVC 的大小——如果目標 PVC 是 20Gi，Scratch PVC 也是 20Gi。但如果目標 PVC 設得太小，就會發生 Scratch Space 不足的問題。

阿明修正了他的 DataVolume，把 storage 從 8Gi 改成了 45Gi（留了一些餘量），問題解決了。

他在筆記本上畫了一張圖：

```
QCOW2 映像（8GB 壓縮）
        │
        │ 下載
        ▼
  Scratch PVC（暫存：放下載的原始 QCOW2）
        │
        │ qemu-img convert（解壓縮 + 格式轉換）
        ▼
  目標 PVC（RAW 格式，40GB 解壓後大小）
```

*所以我的目標 PVC 需要足夠大，不是根據壓縮後的大小，而是根據實際的虛擬磁碟大小。*

他意識到這個知識可以防止未來的很多坑——特別是當你從很「壓縮友好」的 cloud image（例如只有 300MB 的 Alpine Linux cloud image）匯入時，虛擬磁碟大小可能還是 8GB 或更大。

---

> ### 📚 去這裡深入了解
> Scratch Space 的設計、大小計算規則，以及 CDI 如何處理不同格式的轉換：
>
> - [核心功能](/containerized-data-importer/core-features) — Scratch Space 機制與格式轉換細節
> - [系統架構](/containerized-data-importer/architecture) — Importer 的資料流設計
>
> 讀完後，你應該能解釋：什麼格式需要 Scratch Space？什麼格式不需要？

---

## 第六章：格式轉換的幕後（QCOW2 → RAW）

阿明越來越好奇 CDI 到底是怎麼做格式轉換的。他決定去看 importer Pod 的詳細 log，了解幕後的細節。

他故意匯入一個 QCOW2 映像，然後從頭到尾追蹤 log：

```bash
kubectl logs -f importer-test-qcow2-xxxxx
```

```
I] Validating image: disk.img
I] Validating image is valid
I] Image format: qcow2
I] Starting QCOW2 to RAW conversion
I] Executing: qemu-img convert -p -O raw /scratch/disk.img /data/disk.img
    (100.00/100%)
I] Conversion complete
I] Verifying converted image
I] Checksum verification: enabled
I] SHA256: a3f2c8d1...
I] Import complete
```

他看到了幾個關鍵步驟：
1. **格式驗證**：CDI 先用 `qemu-img info` 確認格式，防止不合法的映像
2. **格式轉換**：用 `qemu-img convert` 把 QCOW2 轉成 RAW
3. **Checksum 驗證**：如果 DataVolume 有設定 `checksum`，在轉換完成後驗證資料完整性

阿明特別注意到 Checksum 這個功能。他去查了 DataVolume 的 spec，發現可以這樣設定：

```yaml
spec:
  source:
    http:
      url: "https://example.com/image.qcow2"
      secretRef: "my-http-secret"
  checkpoints: []
  preallocation: false
  priorityClassName: ""
  contentType: kubevirt
```

等等，`contentType: kubevirt`——這是什麼？

他查了文件。原來 CDI 支援兩種 `contentType`：
- **`kubevirt`**（預設）：映像是 VM 磁碟（QCOW2、RAW、VMDK 等），CDI 會做格式轉換
- **`archive`**：tar.gz 壓縮檔，CDI 會解壓縮而不是做磁碟格式轉換

他還發現，CDI 支援相當多的來源格式：QCOW2、RAW、VMDK、VHD、VDI。不管輸入是什麼格式，CDI 都會把它轉換成 RAW 格式存進 PVC。這個設計的邏輯很清楚：VM hypervisor（QEMU）讀 RAW 格式最高效，而且 RAW 格式在 K8s PVC 的 block device 模式下可以直接作為磁碟掛載。

---

> ### 📚 去這裡深入了解
> CDI 支援的格式清單、轉換邏輯，以及 Checksum 驗證的設定方式：
>
> - [核心功能](/containerized-data-importer/core-features) — 格式轉換、Checksum、ContentType
>
> 讀完後，你應該能解釋：為什麼 CDI 要把所有格式都轉成 RAW？有什麼例外嗎？

---

## 第七章：幕後的協作者——CDI 控制器架構

到這個階段，阿明已經用了 CDI 好幾週了。他能讓它正常運作，但有一個問題一直在他腦袋裡：*「每次我 apply 一個 DataVolume，到底是誰在做那些事？」*

他決定去研究 CDI 的控制器架構。

他先列出 CDI 的 Pod：

```bash
kubectl get pods -n cdi
```

```
NAME                              READY   STATUS    RESTARTS   AGE
cdi-apiserver-xxx                 1/1     Running   0          7d
cdi-controller-xxx                1/1     Running   0          7d
cdi-deployment-xxx                1/1     Running   0          7d
cdi-uploadproxy-xxx               1/1     Running   0          7d
```

只有四個 Pod，但文件說 CDI 有 17 個控制器——這些控制器都打包在 `cdi-controller` 這個 Pod 裡跑。

阿明深入研究，理解了主要的分工：

**`cdi-controller`（核心大腦）**：包含大部分的 Reconcile Loop，負責：
- **DataVolume Controller**：監聽 DataVolume，決定要做什麼操作（Import/Upload/Clone）
- **Import Controller**：建立 Importer Pod，追蹤匯入進度
- **Upload Controller**：建立 Upload Server Pod，管理上傳流程
- **Clone Controller**：協調 Clone 操作（決定用哪種 Clone 路徑）
- **Smart Clone Controller**：處理 Snapshot-based Clone
- **Populators Controller**：處理 K8s Volume Populators 整合

**`cdi-apiserver`**：CDI 自己的 API Server，負責 Upload Token 的簽發（確保只有授權的客戶端才能上傳）

**`cdi-uploadproxy`**：Upload 的代理伺服器，接收來自外部的上傳請求，轉發給叢集內的 Upload Server

**`cdi-deployment`**（就是 `cdi-operator`）：管理 CDI 自身的 Lifecycle，處理安裝和升級

阿明畫了一張互動圖：

```
使用者 apply DataVolume
        │
        ▼
DataVolume Controller（決策者）
        │
   ┌────┴────┐──────────────┐
   ▼         ▼              ▼
Import    Upload          Clone
Controller Controller  Controller
   │         │              │
   ▼         ▼              ▼
Importer  Upload Server  Smart Clone /
Pod       Pod            Host-assisted
（下載/轉換）（等待上傳）    Clone
```

*所以 DataVolume Controller 是整個流程的入口，它根據 DataVolume 的 source 類型，分派給對應的專門控制器。*

---

> ### 📚 去這裡深入了解
> CDI 的完整控制器清單與每個控制器的職責：
>
> - [控制器與 API](/containerized-data-importer/controllers-api) — 17 個控制器的分工、CRD、Webhook、API Server
> - [系統架構](/containerized-data-importer/architecture) — 9 個 Binary 與整體架構
>
> 讀完後，你應該能解釋：當你 apply 一個 HTTP 來源的 DataVolume，會觸發哪幾個控制器的 Reconcile？

---

## 第八章：與 KubeVirt 的配合

VM 平台逐漸穩定了。但阿明發現了一個使用上的摩擦點：他需要先建 DataVolume 等匯入完成，才能建 VM。如果有人不小心先建了 VM，VM 會因為磁碟還沒準備好而啟動失敗。

他去翻了 KubeVirt 的文件，發現有一個設定叫做 `dataVolumeTemplates`——VM spec 裡可以直接定義 DataVolume，KubeVirt 會自動等 DataVolume 變成 Succeeded 才啟動 VM：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: ubuntu-vm
spec:
  running: false
  dataVolumeTemplates:
    - metadata:
        name: ubuntu-vm-disk
      spec:
        source:
          http:
            url: "http://images.internal.company.com/ubuntu-22.04.qcow2"
        pvc:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 20Gi
  template:
    spec:
      domain:
        devices:
          disks:
            - name: disk0
              disk:
                bus: virtio
      volumes:
        - name: disk0
          dataVolume:
            name: ubuntu-vm-disk
```

這個設計讓阿明眼睛一亮。他不再需要分成兩步——一個 YAML 就能定義「這台 VM 的磁碟要從哪裡來、VM 要怎麼設定」，KubeVirt 負責協調兩者的順序。

他把這個 VM apply 上去，然後觀察：

```bash
kubectl get vm ubuntu-vm -w
# ubuntu-vm   Stopped   (DataVolume not ready)
# ubuntu-vm   Stopped   (DataVolume not ready)
# ubuntu-vm   Stopped   (DataVolume ready)
```

DataVolume 完成後，他手動把 VM `running` 改成 `true`，VM 順利啟動了。

他還研究了另一個功能：`WaitForFirstConsumer`。當 PVC 的 StorageClass 設定為 `volumeBindingMode: WaitForFirstConsumer` 時，PVC 會等到 Pod 實際被調度到某個 Node 才決定在哪個可用區建立。CDI 和 KubeVirt 都支援這個模式——DataVolume 會等到 VM Pod 被調度後，才在正確的可用區建立 PVC，避免跨可用區的磁碟掛載問題。

*原來 CDI 和 KubeVirt 之間有這麼多細緻的協作設計。*

---

> ### 📚 去這裡深入了解
> CDI 與 KubeVirt 的整合細節，包括 dataVolumeTemplates 和 WaitForFirstConsumer：
>
> - [外部整合](/containerized-data-importer/integration) — KubeVirt 整合、DataVolume 與 VM 的協作
>
> 讀完後，你應該能解釋：為什麼用 `dataVolumeTemplates` 比先建 DataVolume 再建 VM 更好？

---

## 第九章：進階玩法——Snapshot 與跨 Namespace Clone

VM 平台已經上線三個月了。阿明現在接到了一個進階需求：「開發團隊需要能夠快速複製 VM（用來建立測試環境），而且要能跨 Namespace。」

他研究了 CDI 的進階功能，發現了兩個工具：

### VolumeSnapshot 整合

如果叢集的 StorageClass 支援 VolumeSnapshot，CDI 的 Smart Clone 功能會自動使用它。但阿明發現，他可以主動利用 Snapshot 做更多事。

他可以先建立一個「黃金映像」DataVolume，然後對它建立 VolumeSnapshot，未來所有的 VM 都從 Snapshot Clone，而不需要重複匯入：

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: ubuntu-base-snapshot
spec:
  volumeSnapshotClassName: csi-aws-vsc
  source:
    persistentVolumeClaimName: ubuntu-base-image
```

然後新的 DataVolume 可以從 Snapshot 建立：

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: new-vm-disk
spec:
  source:
    snapshot:
      namespace: default
      name: ubuntu-base-snapshot
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 20Gi
```

### 跨 Namespace Clone

跨 Namespace Clone 有一個安全問題：如果 Namespace A 的 PVC 可以被 Namespace B 隨意 Clone，就有資料洩露的風險。CDI 用 **DataVolume Authorization** 解決了這個問題。

來源 Namespace 需要建立一個 `DataVolume` 的 ClusterRole Binding，授權目標 Namespace 可以 Clone：

實作上，CDI 透過一個 `cdi.kubevirt.io/allowClone` 的 annotation 或 RBAC 機制控制跨 Namespace 的 Clone 權限。阿明設定好權限後，跨 Namespace Clone 的 YAML 和普通 Clone 幾乎一樣，只是 source 的 namespace 不同：

```yaml
spec:
  source:
    pvc:
      namespace: golden-images   # 來源在不同的 Namespace
      name: ubuntu-base-image
```

第一次試的時候，Clone 立刻失敗了：

```
E] Source namespace golden-images is not authorized to be cloned into namespace dev
```

他去補了 RBAC 設定，才讓它正常工作。*安全預設值，挺好的。*

---

> ### 📚 去這裡深入了解
> Snapshot 整合、跨 Namespace Clone 的授權機制：
>
> - [核心功能](/containerized-data-importer/core-features) — PVC Clone 進階用法、Snapshot 支援
> - [外部整合](/containerized-data-importer/integration) — VolumeSnapshot 整合、Forklift 大規模遷移
>
> 讀完後，你應該能解釋：跨 Namespace Clone 為什麼需要額外授權？CDI 如何驗證這個授權？

---

## 尾聲：阿明的 CDI 地圖

季度結束。阿明把 CDI 的學習筆記整理成一張概念地圖，貼在工作台上：

```
資料來源                   CDI 核心機制               目標
─────────────────────────────────────────────────────────────
HTTP/HTTPS URL   ──┐
本地映像上傳      ──┤  DataVolume（帶狀態的 PVC）  ──▶  PVC（RAW 格式）
現有 PVC Clone   ──┤    │                              │
VolumeSnapshot  ──┘    ▼                              ▼
                   Importer/Upload/Clone           KubeVirt VM
                   Pod（執行實際工作）              掛載磁碟開機
                        │
                        ▼
                   格式轉換（QCOW2/VMDK → RAW）
                   Scratch Space（臨時工作區）
                   Checksum 驗證（資料完整性）
```

三個月前，阿明連「PVC 裡怎麼放資料」都想不通。現在他能完整地解釋 CDI 的每個功能——不只是「這個功能怎麼用」，還有「為什麼這樣設計」。

最讓他有感的一件事是：CDI 看起來是一個小功能（「不就是把資料放進 PVC 嗎」），但實際上它解決的是一個複雜的協調問題——不同格式的映像、不同的資料來源、不同的儲存後端、跨 Namespace 的安全邊界。DataVolume 這個抽象，把所有這些複雜性包在一個簡單的介面後面。

*這就是好的抽象的力量。*

---

> ### 📚 深入研究整個 CDI
> 完整的技術文件在這裡：
>
> - [CDI 專案簡介](/containerized-data-importer/) — 重新看一遍，你會發現比第一次讀懂得多
> - [系統架構](/containerized-data-importer/architecture) — 9 個 Binary、10 個 CRD、完整狀態機
> - [核心功能](/containerized-data-importer/core-features) — 所有匯入模式的完整技術細節
> - [控制器與 API](/containerized-data-importer/controllers-api) — 17 個控制器的原始碼層級分析
> - [外部整合](/containerized-data-importer/integration) — CDI 在更大生態系中的位置
>
> 恭喜你完成了整個學習之旅。
