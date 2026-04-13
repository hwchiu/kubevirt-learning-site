---
layout: doc
title: Common Instancetypes — 學習路徑：VM 規格的標準化之路
---

# VM 規格的標準化之路

> 一個 Platform Engineer 的故事：從 copy-paste 地獄，到建立公司自己的 VM 規格目錄。

---

## 第一章：「老闆，我又要幫你建 VM 了」

阿明盯著螢幕，Slack 上又有一則訊息：

> 「阿明，幫我開一台 4 核 8G 的 VM，跑 Ubuntu，用來測試新服務。」

*好，這個我會。* 他開啟上週幫行銷部開 VM 的 YAML 檔，開始複製。

改 `name`、改 `cpu.cores`、改 `memory`……

五分鐘後，VM 開起來了。

---

下午，資料工程師傳來訊息：

> 「阿明，我需要一台 16 核 32G 的 VM，跑 Fedora，給 Spark job 用。」

*又來了。* 他再次打開上一份 YAML，開始複製、修改……

---

到了晚上，他整理了一下這個月的工作記錄。光是建立 VM，他就重複做了二十幾次幾乎一樣的事。不同的只是：CPU 核數、記憶體大小、OS 種類。

*每次都要手動設定 `machine.type`、disk bus 是 `virtio` 還是 `sata`、網卡是 `virtio` 還是 `e1000`……我真的要一直這樣下去嗎？*

他在便利貼上寫下一個問題貼在螢幕旁邊：

> **「能不能讓大家直接說：我要一台 u1.medium 的 Ubuntu VM？」**

---

> ### 📚 去這裡深入了解
> - [專案總覽](/common-instancetypes/) — 了解 Common Instancetypes 解決了什麼問題，以及如何安裝
>
> 讀完後，你應該能說出 Common Instancetypes 是什麼，以及它和 AWS EC2 Instance Types 的概念有什麼相似之處。

---

## 第二章：「原來 KubeVirt 有 Instancetype」

第二天早上，阿明開始查資料。

他搜尋了「KubeVirt VM size standard」，找到了 KubeVirt 的文件，看到了一個詞：**VirtualMachineInstancetype**。

*等等，這不就是 AWS EC2 的 Instance Type 概念嗎？*

他繼續讀下去，慢慢理解了核心思路：

**把「硬體規格」從「VM 定義」中分離出來。**

以前，VM 的 YAML 長這樣——規格直接寫死在裡面：

```yaml
spec:
  domain:
    cpu:
      cores: 4
    memory:
      guest: 8Gi
    devices:
      disks:
        - name: disk0
          disk:
            bus: virtio
```

有了 Instancetype 之後，VM 的 YAML 變成這樣：

```yaml
spec:
  instancetype:
    name: u1.medium
  preference:
    name: ubuntu
```

*就這樣？就兩行？*

規格的細節被封裝在 `u1.medium` 這個 Instancetype 物件裡了。VM 本身只需要說「我要用哪個型號」，不用知道型號裡面有幾顆 CPU、多少記憶體。

這正是他一直想要的：讓使用者選「型號」，而不是手動填規格。

---

> ### 📚 去這裡深入了解
> - [外部整合](/common-instancetypes/integration) — VirtualMachineInstancetype 的引用語法、Instancetype 如何與 VM 結合
>
> 讀完後，你應該能寫出一個使用 instancetype 和 preference 引用的 VirtualMachine YAML。

---

## 第三章：「七大系列，各有用途」

阿明找到了 common-instancetypes 這個專案——KubeVirt 社群維護的一套標準規格庫，直接提供 43 種 Instancetype 可以用。

他打開規格列表，看到七個系列：

| 系列 | 名稱 | 適用場景 |
|------|------|---------|
| `u1.*` | 通用型 | 一般 Web 服務、開發環境 |
| `o1.*` | 超效能型 | 需要超高效能的工作負載 |
| `cx1.*` | 計算最佳化 | CPU 密集型任務（編碼、模擬） |
| `m1.*` | 記憶體最佳化 | 大型資料庫、記憶體快取 |
| `n1.*` | 網路最佳化 | 高吞吐量網路應用 |
| `gn1.*` | GPU 加速型 | AI/ML 推論、圖形渲染 |
| `highperformance.*` | 高效能型 | 延遲敏感的生產環境 |

*這不就是 AWS 的 T 系列、C 系列、R 系列、P 系列……*

阿明感覺豁然開朗。公有雲廠商用了多年的設計模式，現在終於可以在自建的 KubeVirt 叢集上套用了。

每個系列還有多個「尺寸」：

```
u1.micro    →  1 vCPU,  512 MiB
u1.small    →  1 vCPU,  2 GiB
u1.medium   →  1 vCPU,  4 GiB
u1.large    →  2 vCPU,  8 GiB
u1.xlarge   →  4 vCPU,  16 GiB
u1.2xlarge  →  8 vCPU,  32 GiB
```

*以後開 VM，我只要問對方：需要什麼等級的效能？跑什麼工作負載？就能直接推薦型號了。*

這一刻，他腦中已經開始規劃公司的 VM 申請表格：「請選擇規格系列 ▼」。

---

> ### 📚 去這裡深入了解
> - [核心功能](/common-instancetypes/core-features) — 7 大系列完整規格、每種 Instancetype 的 CPU/Memory 配置
>
> 讀完後，你應該能為不同類型的工作負載（Web 服務、資料庫、ML 推論）推薦合適的 Instancetype 系列。

---

## 第四章：「Linux 和 Windows 為什麼需要不同設定？」

選好規格系列後，阿明注意到 VM YAML 裡還有另一個欄位：`preference`。

*Instancetype 是硬體規格，那 Preference 是什麼？*

他查了文件，看到 Preference 定義的是**「這個 OS 期望的虛擬硬體設定」**。

舉個例子：

- **Linux（Ubuntu, Fedora, RHEL）**：偏好 `virtio` disk bus，效能最佳
- **Windows**：舊版 Windows 不支援 virtio，需要 `sata` bus；網卡也需要特殊驅動

如果把 Windows VM 設成 `virtio` disk bus，VM 開不起來。但如果每次都要手動知道「這個 OS 要用哪個 bus」，又回到了手動填規格的老問題。

**Preference 就是把這些 OS 相關的「隱性知識」封裝起來。**

阿明看了一下 common-instancetypes 提供的 Preference 清單：

```
alpine         → virtio bus, virtio 網卡
centos.7       → virtio bus
fedora         → virtio bus, virtio 網卡
rhel.9         → virtio bus, TPM, SecureBoot
ubuntu         → virtio bus, virtio 網卡
windows.2k19   → sata bus, e1000e 網卡, RTC clock
windows.2k22   → sata bus, e1000e 網卡, RTC clock
```

*原來，`windows.2k22` 這個 Preference 幫我記住了：Windows Server 2022 需要 sata bus 和 e1000e 網卡。我不需要每次都去查這些細節了。*

這就是 Instancetype 和 Preference 的分工：
- **Instancetype** = 「多少資源」（CPU、記憶體）
- **Preference** = 「怎麼設定虛擬硬體」（disk bus、網卡型號、時鐘、CPU features）

---

> ### 📚 去這裡深入了解
> - [核心功能](/common-instancetypes/core-features) — OS Preference 完整列表、各 OS 的虛擬硬體偏好設定
>
> 讀完後，你應該能解釋為什麼同樣的 Instancetype 搭配不同的 Preference，VM 的虛擬硬體設定會不同。

---

## 第五章：「Namespace 還是 Cluster 範圍？」

阿明準備開始部署，但他發現有兩種 Instancetype CRD：

- `VirtualMachineInstancetype`（namespace 範圍）
- `VirtualMachineClusterInstancetype`（叢集範圍）

*什麼時候用哪個？*

他想了一下，畫了一個簡單的圖：

```
叢集範圍（Cluster）
├── 所有 namespace 都看得到
├── 由叢集管理員維護
└── common-instancetypes 提供的就是這種
    → u1.small, u1.medium, cx1.large...

Namespace 範圍
├── 只有該 namespace 看得到
├── 由該 namespace 的使用者自行管理
└── 適合各部門的客製化規格
    → db-team/high-memory-db, ml-team/gpu-inference...
```

這個設計很合理：

**叢集範圍**適合「全公司通用的標準規格」——就像 AWS 的官方 Instance Type，每個帳號都能用。Common Instancetypes 提供的 43 種規格，正是以 `VirtualMachineClusterInstancetype` 部署到叢集裡，所有 namespace 的 VM 都能引用。

**Namespace 範圍**適合「某個團隊的特殊需求」——某個部門如果需要一個 `u1.small` 以外的客製規格，可以自己在自己的 namespace 建一個，不影響其他人。

*所以阿明的職責就是：維護叢集範圍的「公司標準規格」，各部門如果有特殊需求，可以在自己的 namespace 自行新增。*

---

> ### 📚 去這裡深入了解
> - [資源類型目錄](/common-instancetypes/resource-catalog) — CRD 型別定義、namespace 範圍 vs 叢集範圍的差異
>
> 讀完後，你應該能說明什麼情境應該用 Cluster 範圍，什麼情境應該用 Namespace 範圍。

---

## 第六章：「從安裝到第一台標準化 VM」

阿明決定正式部署 common-instancetypes。

首先，確認叢集上已有 KubeVirt，然後安裝 common-instancetypes：

```bash
# 安裝最新版 common-instancetypes
export VERSION=$(curl -s https://api.github.com/repos/kubevirt/common-instancetypes/releases/latest | jq -r .tag_name)
kubectl apply -f https://github.com/kubevirt/common-instancetypes/releases/download/${VERSION}/common-instancetypes-all.yaml
```

確認安裝成功：

```bash
kubectl get virtualmachineclusterinstancetype
# 應該看到 u1.small, u1.medium, cx1.large 等 43 種規格

kubectl get virtualmachineclusterpreference
# 應該看到 ubuntu, fedora, windows.2k22 等 18+ 種 OS 偏好
```

接著，建立第一台標準化的 VM：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: web-server-01
spec:
  instancetype:
    name: u1.medium          # 1 vCPU, 4 GiB
  preference:
    name: ubuntu             # virtio bus, virtio 網卡
  running: true
  template:
    spec:
      domain:
        devices: {}
      volumes:
        - name: disk0
          persistentVolumeClaim:
            claimName: ubuntu-22-04-pvc
```

*就這樣。沒有手動填 CPU cores、沒有手動設 disk bus，只有兩個「型號名稱」。*

阿明把這份 YAML 發給各部門，告訴他們：「以後開 VM，換掉 `instancetype.name` 和 `preference.name` 就好，其他不用動。」

---

> ### 📚 去這裡深入了解
> - [外部整合](/common-instancetypes/integration) — 完整的安裝步驟、VM 引用語法、與 KubeVirt 的整合方式
> - [系統架構](/common-instancetypes/architecture) — Kustomize 建置系統、版本管理機制
>
> 讀完後，你應該能獨立完成 common-instancetypes 的安裝，並建立第一台使用標準規格的 VM。

---

## 第七章：「建立公司自己的 Instancetype」

幾週後，資料工程團隊找來了：

> 「阿明，我們需要一個 8 核 64G 記憶體的規格，專門跑 Spark，但 common-instancetypes 裡面的 `m1.xlarge` 是 4 核 16G，不夠。」

*這就是需要客製化 Instancetype 的時候了。*

阿明建立了一個叢集範圍的客製 Instancetype：

```yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: data-spark-large
  labels:
    instancetype.kubevirt.io/vendor: mycompany.internal
    instancetype.kubevirt.io/version: "1.0"
spec:
  cpu:
    guest: 8
  memory:
    guest: 64Gi
```

套用到叢集：

```bash
kubectl apply -f data-spark-large.yaml
```

驗證：

```bash
kubectl get virtualmachineclusterinstancetype data-spark-large
```

現在，資料工程師的 VM YAML 只需要：

```yaml
spec:
  instancetype:
    name: data-spark-large
  preference:
    name: ubuntu
```

---

阿明開始整理公司的 Instancetype 目錄：

```
公司標準規格（來自 common-instancetypes）
├── u1.small / u1.medium / u1.large    → 一般服務
├── cx1.medium / cx1.large             → 計算密集
└── m1.large / m1.xlarge               → 記憶體密集

公司客製規格（自行維護）
├── data-spark-large                   → 資料工程 Spark
├── ml-inference-gpu                   → ML 推論（搭配 gn1）
└── legacy-windows-app                 → 舊系統 Windows VM
```

*這不就是我一直想要的 VM 規格型錄嗎？*

---

**一個月後**，阿明收到資料工程師的訊息：

> 「阿明，我今天自己開 VM 了！選了 `data-spark-large` + `ubuntu`，五分鐘就搞定。謝啦！」

阿明看了一眼螢幕旁邊的便利貼——那個他寫下的問題：

> **「能不能讓大家直接說：我要一台 u1.medium 的 Ubuntu VM？」**

他把便利貼撕下來，揉成一團，丟進垃圾桶。

問題解決了。

---

> ### 📚 去這裡深入了解
> - [資源類型目錄](/common-instancetypes/resource-catalog) — Label 規範、自訂 Instancetype 的驗證測試
> - [核心功能](/common-instancetypes/core-features) — 元件化設計，如何組合與擴充既有規格
>
> 讀完後，你應該能建立公司自己的 VirtualMachineClusterInstancetype，並規劃一套符合組織需求的 VM 規格目錄。

---

## 學習路徑完成 🎉

恭喜你完成了 Common Instancetypes 的學習路徑！

你現在應該能夠：

- ✅ 說明 Instancetype 和 Preference 的分工與概念
- ✅ 從 7 大系列中為不同工作負載選擇合適的規格
- ✅ 安裝 common-instancetypes 並在 VM 中引用標準規格
- ✅ 建立公司自己的客製 Instancetype

**下一步建議：**
- 瀏覽完整的[資源類型目錄](/common-instancetypes/resource-catalog)，了解所有可用的 Label 和 annotation
- 查看[系統架構](/common-instancetypes/architecture)，了解 common-instancetypes 的版本管理機制，規劃升級策略
