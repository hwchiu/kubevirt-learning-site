---
layout: doc
title: NetBox — 學習路徑：終結 Excel 的 Source of Truth 之旅
---

<script setup>
</script>

# 終結 Excel 的 Source of Truth 之旅

> 一個 Network Engineer 的真實掙扎，與他如何用 NetBox 重建秩序的故事。

---

## 第 1 章：「Excel 的末日」

那是一個普通的週四下午，阿明正在處理一張網路變更單，需要確認 `192.168.50.0/24` 這個段還有沒有可用的 IP。

他打開了 `IP_Management_v3_FINAL_真的是最新版.xlsx`。

滑到 Sheet 3，找到大約第 180 行，眼睛開始模糊。有幾個 IP 被標成黃色（代表「保留」），幾個標成紅色（代表「已使用」），但沒有人記得這是什麼時候標的。旁邊備註欄寫著「問 Jason」——但 Jason 三個月前已經離職了。

*這張表有問題，但我不知道哪些資料是錯的。*

阿明在 Slack 上問同事：「有人知道 `192.168.50.100` 現在是誰在用嗎？」

等了 40 分鐘，來了三個不同的答案。

---

這家公司有 30 個機架、超過 400 台實體設備，還有幾百台虛擬機器。IP 清冊是 8 年前的 Excel，設備清冊由維運、開發、安全三個部門各自維護。沒有人知道哪份資料是對的，也沒有人敢把舊表刪掉，因為萬一刪錯了怎麼辦。

更糟的是每次有人問「我們有多少台 Linux 伺服器？」或「`10.0.0.0/8` 裡有多少個 /24 Prefix 已經分配出去了？」——這些問題都沒有一個可信的快速答案。

那天下午的部門會議，老闆問了那個問題。

「我們有多少台設備？用了多少 IP？」

全場沉默。

*我需要解決這個問題，而且不能靠 Excel。*

---

> ### 📚 去這裡深入了解
> - [NetBox 專案總覽](/netbox/) — 了解 NetBox 是什麼、解決什麼問題
> - [核心功能](/netbox/core-features) — IPAM 和 DCIM 的完整功能介紹
>
> 讀完後，你應該能說明為什麼 NetBox 被定位為 Source of Truth，而不只是另一個 CMDB。

---

## 第 2 章：「第一次進 NetBox：建立 Site 和機架」

阿明花了一個晚上安裝好 NetBox（Docker Compose 部署，比想像中簡單），開著瀏覽器盯著那個乾淨的介面。

*從哪裡開始？*

NetBox 的資料模型有一個清楚的層次邏輯：**地理位置 → 設施 → 設備**。最頂層是 **Region**（地區），往下是 **Site**（機房/資料中心），再下面是 **Location**（樓層/機房區域），最後是 **Rack**（機架）。

阿明先建立了公司的第一個 Site：

```
Name: Taipei-DC1
Slug: taipei-dc1
Status: Active
Physical Address: 台北市...
```

然後建了 30 個機架，每個機架有編號（`A01` 到 `F05`），有 42U 或 48U 的容量，放在對應的機房區域裡。

這個過程讓阿明第一次意識到：**光是「建立 Site 和機架」這件事，就已經讓公司的物理拓墣變得可查詢了。**

他點開 Rack A01 的頁面，看到那個空白的 U 位示意圖，心裡有點興奮。

*接下來要把設備填進去。但在那之前，我需要先整理 IP。*

他也注意到 NetBox 的 **Tenant** 功能——可以把 Site、Device、IP 等資源指定給某個租用方（部門、客戶）。阿明建了三個 Tenant：維運部、開發部、安全部，對應公司內三個各自維護自己清冊的團隊。

*這樣以後查詢的時候就能按部門過濾了。*

---

> ### 📚 去這裡深入了解
> - [系統架構](/netbox/architecture) — NetBox 的 Django 架構、資料模型層次
> - [資料模型](/netbox/data-models) — DCIM 相關模型（Site、Rack、Location）的詳細欄位
>
> 讀完後，你應該能描述 NetBox 的 DCIM 層次結構，並說明 Region、Site、Location、Rack 之間的關係。

---

## 第 3 章：「IP 位址管理：從 Prefix 到 IPAddress」

整理 IP 清冊的工作，比阿明預期的還要複雜。

NetBox 的 IPAM 有一個精妙的設計：**階層式 Prefix 樹**。你不只是把 IP 填進去，你是在描述 IP 的分配結構。

最頂層是 **Aggregate**（聚合），代表你擁有或分配到的最大 IP 範圍，通常對應 RIR（Regional Internet Registry）的分配記錄，例如你公司向 APNIC 申請到的 /24 公網段。

往下是 **Prefix**，代表你把 Aggregate 切割出來的子網段。一個 /8 可以切成很多個 /24，每個 /24 可以再切成 /29 給小型服務使用。

最底層是 **IPAddress**，每一個實際分配給介面的 IP 位址。

阿明照著這個邏輯重建了公司的 IP 架構：

```
Aggregate: 10.0.0.0/8  (RFC 1918 私網)
  └─ Prefix: 10.10.0.0/16  (台北 DC)
       ├─ Prefix: 10.10.1.0/24  (Server VLAN)
       │    ├─ IPAddress: 10.10.1.10/24  (web-01 eth0)
       │    └─ IPAddress: 10.10.1.11/24  (web-02 eth0)
       └─ Prefix: 10.10.2.0/24  (Management VLAN)
```

當他第一次看到 Prefix 的使用率儀表板時，立刻發現了問題：`10.10.5.0/24` 的使用率顯示 95%，但那個段他根本不知道是什麼服務在用。

*這就是 Excel 做不到的——它沒辦法計算使用率。*

NetBox 也支援 **VRF**（Virtual Routing and Forwarding），可以在同一個 NetBox 實例裡管理多個互相隔離的路由域。阿明的公司有兩個 VRF：`PROD` 和 `DEV`，兩個環境都有 `10.0.0.0/8`，但彼此隔離。

他把兩個 VRF 都建好，重新將所有 Prefix 指定到對應的 VRF 下，這樣查詢 `10.10.1.10` 就會明確知道是 PROD 環境的 web-01，不會和 DEV 環境的同一個 IP 混淆。

---

> ### 📚 去這裡深入了解
> - [核心功能](/netbox/core-features) — IPAM 功能詳解：Prefix、IPAddress、VRF、RIR
> - [資料模型](/netbox/data-models) — IPAM 相關模型（Prefix、IPAddress、VRF、Aggregate）
>
> 讀完後，你應該能解釋 Aggregate、Prefix、IPAddress 三者的層次關係，以及 VRF 的用途。

---

## 第 4 章：「VLAN 和 VRF：複雜的 L2/L3 分段」

阿明的公司網路架構有點複雜——既有實體 VLAN 分段，也有 VRF 做 L3 隔離，還有一些 VLAN 跨多個 Site 延伸。

在 Excel 時代，VLAN 清冊是另一張獨立的 sheet，和 IP 清冊沒有直接關聯。某個 VLAN ID 對應什麼 Prefix，要靠人腦記憶。

NetBox 的設計讓這件事變得清晰。

**VLAN Group** 是 VLAN 的容器，可以綁定到特定 Site 或 Location。一個 VLAN 在 NetBox 裡有 ID、Name、Status、Tenant，還可以直接關聯到 Prefix，讓 L2 和 L3 的對應關係一目了然：

```
VLAN Group: Taipei-DC1-VLANs
  ├─ VLAN 100 (Server)  →  Prefix 10.10.1.0/24 (VRF: PROD)
  ├─ VLAN 200 (Mgmt)    →  Prefix 10.10.2.0/24 (VRF: PROD)
  └─ VLAN 300 (Dev)     →  Prefix 10.10.3.0/24 (VRF: DEV)
```

阿明在建 VLAN 的過程中發現了一個問題：公司有兩個地方都用了 `VLAN 100`，但一個是 Server VLAN，另一個是 Storage VLAN，在不同的 VLAN Group 下用同樣的 ID。這在 NetBox 裡是被允許的（因為它們在不同的 Group 裡），但這件事讓他意識到：

*我們的 VLAN 命名規範完全沒有標準化。*

他把這個問題記錄下來，當成後續的清理工作項目。光是「把資料放進 NetBox」這個動作，就已經幫他發現了三個原本被藏在 Excel 裡看不見的命名衝突。

---

> ### 📚 去這裡深入了解
> - [核心功能](/netbox/core-features) — VLAN、VRF 功能詳解
> - [資料模型](/netbox/data-models) — VLAN、VRF 模型欄位與關聯
>
> 讀完後，你應該能說明 VLAN Group 的作用，以及如何在 NetBox 裡建立 VLAN 與 Prefix 的關聯。

---

## 第 5 章：「設備清冊：Device、Interface、連線」

建好 IP 和 VLAN 架構後，阿明開始填設備清冊。這是整個過程裡工作量最大的一步。

NetBox 的 **Device** 不只是一筆名稱記錄，它包含：
- **Device Type**：型號（Dell R750、Cisco Catalyst 9300），定義設備有哪些 interface
- **Device Role**：角色（Server、Switch、Router、Firewall）
- **Rack 位置**：在哪個機架的哪幾個 U
- **Platform**：作業系統（CentOS 8、Ubuntu 22.04）
- **Status**：Active / Staged / Decommissioning

阿明先建立 Device Type 的模板庫，定義每種型號有哪些介面（`eth0`、`eth1`、`MGMT`、`iDRAC`），這樣每次新增一台設備，介面就會自動從模板建立，不需要手動一個個填。

然後是 **Cable**（線路）。NetBox 可以記錄每條物理線路的兩端介面，完整描述機房的佈線狀況。阿明試著記錄了幾條線路後，發現他需要一份實體佈線圖，但公司根本沒有這個文件。

*又是一個從來沒有被認真管理的東西。*

阿明決定先把設備基本資訊建完，佈線的部分等到實地盤點後再補。

他花了兩週時間把 400 台設備建進 NetBox。最後，他第一次打開「設備清冊」頁面，用 Site + Rack 篩選，看到整排機架上每一台設備的型號、IP、狀態一目了然。

*這就是 Source of Truth 應該有的樣子。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/netbox/core-features) — DCIM 功能：Device、Interface、Cable
> - [資料模型](/netbox/data-models) — Device 相關模型（Device、DeviceType、Interface）
>
> 讀完後，你應該能說明 Device Type 的作用，以及如何透過 Rack 視圖查看機架的設備分布。

---

## 第 6 章：「虛擬機器管理：Cluster 和 VM Interface」

實體設備建好之後，阿明轉向虛擬化環境。公司跑著兩個 VMware vSphere Cluster 和一個 KVM Cluster，加起來大約 300 台虛擬機器。

NetBox 的虛擬化模型有三個核心物件：

**Cluster Type** → **Cluster** → **Virtual Machine**

Cluster Type 定義虛擬化平台種類（VMware vSphere、KVM、OpenStack），Cluster 是實際的叢集實例，Virtual Machine 是運行在 Cluster 上的虛擬機器。

每台 Virtual Machine 也可以有自己的 **VMInterface**，並且指定 IP 位址——這樣一來，虛擬機器的 IP 管理和實體設備的 IP 管理在同一套系統裡，不需要兩張表交叉比對。

阿明在建虛擬機器清冊的時候，發現了一個很有趣的情況：有些 VM 的 IP 已經在 IPAM 裡記錄為 `In Use`，但找不到對應的 Virtual Machine 記錄——這表示有人直接在 IP 清冊裡登記了 IP，但忘記建 VM 記錄，或者那台 VM 已經被刪掉但 IP 沒有釋放。

*NetBox 讓這種「孤立 IP」的問題變得可見了。*

他花了幾天時間把孤立 IP 一一調查清楚，有些確認可以釋放，有些發現其實是被遺忘的服務還在跑著。

---

> ### 📚 去這裡深入了解
> - [核心功能](/netbox/core-features) — 虛擬化管理：Cluster、VirtualMachine、VMInterface
> - [資料模型](/netbox/data-models) — 虛擬化相關模型（Cluster、VirtualMachine、VMInterface）
>
> 讀完後，你應該能說明 NetBox 如何統一管理實體設備和虛擬機器的 IP 位址。

---

## 第 7 章：「REST API 自動化：用 Python pynetbox 批量匯入」

建了幾百台設備之後，阿明手已經快廢了。

更麻煩的是，公司每個月都會新增幾十台設備，如果每次都要手動建，這件事就不可能持續下去。

他開始研究 NetBox 的 **REST API**。

NetBox 的 REST API 是完整的 CRUD，每個資源（Device、IPAddress、Prefix、Interface...）都有對應的 endpoint。認證使用 API Token，簡單清楚。

他安裝了 `pynetbox`，一個 Python 的 NetBox API client：

```python
import pynetbox

nb = pynetbox.api(
    'http://netbox.example.com',
    token='your-api-token'
)

# 批量建立 IP 位址
ips_to_create = [
    {'address': '10.10.1.20/24', 'status': 'active', 'description': 'app-01 eth0'},
    {'address': '10.10.1.21/24', 'status': 'active', 'description': 'app-02 eth0'},
]

result = nb.ipam.ip_addresses.create(ips_to_create)
print(f"建立了 {len(result)} 個 IP 位址")
```

阿明把公司現有的 Excel 清冊用 Python 讀取，轉換成 NetBox API 的格式，批量匯入。那份執行了 20 分鐘的腳本，把剩下 200 台設備的基本資料全部建進去了。

當他看到終端機印出 `建立了 200 個設備` 的那一刻，有種說不出的成就感。

*我再也不需要每次都坐在瀏覽器前面一筆一筆填了。*

他也建立了一個 CI/CD pipeline 的 hook：每次新設備上線，自動呼叫 NetBox API 建立記錄、分配 IP，並且在設備下線時自動更新狀態。

---

> ### 📚 去這裡深入了解
> - [API 參考](/netbox/api-reference) — REST API 完整說明：認證、端點、過濾、分頁
>
> 讀完後，你應該能用 pynetbox 寫一段腳本，批量建立或更新 NetBox 裡的資源。

---

## 第 8 章：「GraphQL 查詢：複雜關聯查詢」

有一天，主管問了一個複雜的問題：「台北機房所有 Active 狀態的設備，它們的 Management Interface IP 是什麼？」

如果用 REST API，這個問題需要幾個步驟：
1. 查詢 Site = `taipei-dc1` 的所有 Device
2. 對每台 Device 查詢它的 Interface
3. 找到 role = `management` 的 Interface
4. 查詢那個 Interface 的 IPAddress

四個 API call，加上在 Python 裡做 join，很麻煩。

阿明這時候想起 NetBox 還有 **GraphQL** 端點。

他開啟 `/graphql/` 的 Playground，寫了這樣一個查詢：

```graphql
{
  device_list(site: "taipei-dc1", status: "active") {
    name
    device_type {
      model
    }
    interfaces(mgmt_only: true) {
      name
      ip_addresses {
        address
      }
    }
  }
}
```

一個查詢，直接拿到所有關聯資料。Response 是 JSON，可以直接餵給 Ansible inventory。

*這才是真正的 Source of Truth——不只是儲存資料，而是可以高效查詢關聯。*

阿明開始用 GraphQL 產生動態的 Ansible inventory，不再需要維護靜態的 `hosts` 檔案。每次跑 Ansible playbook，都會先呼叫 NetBox GraphQL 拿到最新的設備清單，確保 inventory 永遠是最新的。

---

> ### 📚 去這裡深入了解
> - [API 參考](/netbox/api-reference) — GraphQL 端點說明、查詢語法、Playground 使用
>
> 讀完後，你應該能用 GraphQL 查詢跨模型的關聯資料，並說明 GraphQL 相較於 REST API 的優勢場景。

---

## 第 9 章：「Webhook 整合：資料變更觸發 Ansible/Terraform」

把 NetBox 建成 Source of Truth 只是第一步。阿明真正想做的，是讓 NetBox 成為自動化的**觸發點**。

NetBox 有兩個相關的功能：**Webhook** 和 **Event Rules**。

**Event Rule** 定義當某個物件（如 IPAddress、Device）發生特定事件（建立、修改、刪除）時，要觸發什麼動作。**Webhook** 是其中一種動作——向指定的 URL 發送 HTTP POST，帶著變更的詳細資料。

阿明設定了幾個 Event Rule：

1. **新增 IPAddress** → 呼叫 Terraform webhook，更新 DNS 記錄
2. **Device 狀態變更為 Decommissioning** → 呼叫 Ansible，執行設備下線腳本（清除設定、移出監控）
3. **新增 Device** → 呼叫 Ansible，把設備加入 Prometheus 監控

Webhook 的 payload 是標準的 JSON 格式，包含物件的完整資料和變更前後的 diff。阿明在 Ansible 的 webhook receiver 端：

```python
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook/device-decommission', methods=['POST'])
def device_decommission():
    data = request.json
    device_name = data['data']['name']
    # 觸發 Ansible playbook
    subprocess.run([
        'ansible-playbook', 'decommission.yml',
        '-e', f'target_host={device_name}'
    ])
    return 'OK', 200
```

有了這個機制，「在 NetBox 更新設備狀態」這個動作，會自動觸發一系列的自動化流程。NetBox 不再只是一個記錄系統，而是整個基礎設施自動化的**事件中心**。

*Source of Truth + Event-Driven Automation——這才是真正的 NetOps。*

---

> ### 📚 去這裡深入了解
> - [外部整合](/netbox/integration) — Webhook、Event Rules 的設定方式與 payload 格式
>
> 讀完後，你應該能設計一個 Event Rule，讓 NetBox 在 Device 狀態變更時自動通知外部系統。

---

## 第 10 章：「維護 Source of Truth 的挑戰：讓資料保持最新」

三個月後，阿明坐在辦公室裡，看著 NetBox 的 Dashboard。

設備清冊裡有 412 台實體設備，287 台虛擬機器，2,847 個 IP 位址，VLAN 和 Prefix 架構清楚呈現了整個公司的 L2/L3 拓墣。

但他很清楚，最大的挑戰不是「建立」，而是「維護」。

---

阿明發現了幾個讓資料保持最新的核心問題：

**問題一：工程師不習慣先更新 NetBox**

有幾次，阿明查 NetBox 發現一個 IP 是空閒的，結果 ping 一下發現有回應。原來有人直接在設備上設定了 IP，根本沒有更新 NetBox。

解法：把「更新 NetBox 是操作的一部分」這件事制度化，在 Runbook 裡明確要求，並且在 Code Review 裡加上 checklist。

**問題二：存量資料的準確性**

那 400 台設備裡，有多少資料是從 Excel 匯入時就是錯的？有幾台設備的 IP 和 interface 對應關係是阿明猜的。

解法：定期「實地驗證」——拿 NetBox 的資料和 Ansible 抓到的實際配置比對，找出差異。

**問題三：設備下線沒人通知**

有一台測試機在 NetBox 裡還是 Active 狀態，但實際上六個月前就已經被拆掉了。

解法：建立定期掃描機制，對所有 Active 設備發送 ICMP probe，把沒有回應的設備標記為 `Offline`（待人工確認）。

---

阿明在公司內部分享了這個經驗，說了一句讓大家印象深刻的話：

> 「NetBox 不會自己保持準確。準確的 Source of Truth 是一種文化，不是一個工具。」

但即使如此，現在如果有人問「我們有多少台設備」，阿明可以在三秒內給出答案。

那已經比三個月前好了太多。

---

> ### 📚 去這裡深入了解
> - [外部整合](/netbox/integration) — 如何用 Webhook + Event Rules 建立自動更新機制
> - [核心功能](/netbox/core-features) — Custom Fields、Tags 用於標記資料品質狀態
>
> 讀完後，你應該能設計一套讓 NetBox 資料保持準確的維護機制，包含自動化驗證和人工審查流程。

---

## 故事結語

阿明花了三個月，把公司的網路資產管理從「一堆 Excel」變成了「一個可信的 Source of Truth」。

這個過程不輕鬆，但回報是清晰的：

- **任何人**都能在三秒內查到 IP 是誰在用
- **新設備上線**自動觸發監控和 DNS 設定
- **設備清冊**和實際狀況的差異從「完全不知道」變成「每週自動比對」

NetBox 本身只是一個工具。真正讓它有價值的，是把它放在自動化流程的核心，並且讓整個團隊把「更新 NetBox」當成操作的一部分。

---

::: info 繼續深入
- [← 回到學習路徑首頁](./index)
- [NetBox 系統架構](/netbox/architecture) — 深入了解 Django/PostgreSQL/Redis 架構
- [NetBox 資料模型](/netbox/data-models) — 115 個模型的完整技術細節
:::
