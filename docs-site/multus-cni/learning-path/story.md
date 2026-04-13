---
layout: doc
title: Multus CNI — 學習路徑：阿明的多網路之旅
---

# 阿明的多網路之旅

*一個 Platform Engineer 在 KubeVirt 叢集中解決 VM 多網卡問題的真實歷程。*

---

## 第一章：「一張網卡，兩個世界的距離」

週一早上，阿明的 Slack 跳出一則訊息，來自業務部門的 DevOps 負責人老陳：

> 「阿明，我們的 VM 裡跑的那個舊系統需要同時連到 K8s 的微服務，也要連到公司 VLAN 10.88.0.0/16 那段。現在只有一張網卡，兩個需求沒辦法同時滿足，你能幫我們搞定嗎？」

阿明看了看叢集裡的 VM 配置——是用 KubeVirt 跑的，VM 被包在 Pod 裡，靠 Flannel 提供了一個 `eth0`，IP 是 `10.244.x.x`。Pod 網路沒問題，但 VLAN 10.88 根本連不到。

*所以問題是：一個 VM 只有一張網卡，但需要活在兩個不同的網段裡。*

阿明試了幾個方向：

- **多 IP？** Pod 可以有多個 IP，但兩段網路的閘道不同，路由會打架。
- **改 Flannel 設定？** 改 CNI 的影響面太大，整個叢集都會動。
- **Host Network？** 直接用宿主機網路，但安全隔離就沒了，而且會搶 port。

每一條路都是死路。

阿明打開 Kubernetes 官方文件，搜尋 "multiple network interfaces pod"。第一個結果：**Multus CNI**。

---

> ### 📚 去這裡深入了解
> - [Multus CNI 專案簡介](/multus-cni/) — Multus 的定位、使用場景，以及與 KubeVirt 的關係
>
> 讀完後，你應該能理解為什麼 Kubernetes 預設只有一張網卡，以及 Multus 如何解決這個限制。

---

## 第二章：「Meta-Plugin 是什麼意思？」

阿明讀完文件第一頁，看到一個詞：**CNI Meta-Plugin**。

*Meta-Plugin？這跟一般的 CNI 外掛有什麼不一樣？*

他打開架構圖，試著理解流程：

正常情況下，kubelet 建立 Pod 時會呼叫 CNI 外掛，外掛負責建立網路介面、設定 IP、加路由。一個 Pod，一次呼叫，一張網卡。

Multus 的做法不同。它把自己插在 kubelet 和其他 CNI 之間：

1. kubelet 以為只有 Multus 一個 CNI，呼叫它。
2. Multus 讀取 Pod Annotation，找出這個 Pod 需要哪些網路。
3. Multus **依序呼叫（Delegate）** 每一個下游 CNI 外掛——先讓 Flannel 建 `eth0`，再讓 bridge 建 `net1`。
4. Pod 最終擁有多張網路介面。

*所以 Meta-Plugin 的「Meta」是指它不自己做真正的網路設定，而是統籌協調其他 CNI 去做。這讓 Multus 可以跟任何 CNI 搭配，而不需要改動 Flannel 或 Calico 的邏輯。*

阿明想起老陳的需求：

- `eth0`（Flannel，維持 K8s Pod 網路，讓阿明還能用 `kubectl exec` 進去）
- `net1`（橋接到公司 VLAN，給業務系統直接存取）

這正是 Multus 設計要解決的場景。他開始看 Multus 的 DaemonSet 是怎麼部署到每個 Node 上的——它需要把自己的二進位放到 `/opt/cni/bin/`，並把設定寫到 `/etc/cni/net.d/`，讓 kubelet 把它認為是「第一個 CNI」。

---

> ### 📚 去這裡深入了解
> - [系統架構](/multus-cni/architecture) — CNI Meta-Plugin 原理、Delegate 機制詳解、DaemonSet 部署流程
>
> 讀完後，你應該能畫出 Multus 在 kubelet → CNI 呼叫鏈中的位置，並理解 Delegate 呼叫順序。

---

## 第三章：「NetworkAttachmentDefinition：替第二張網卡命名」

Multus 裝好了。但阿明很快發現：裝好 Multus，不等於網路就多了。

他需要告訴 Multus：「第二張網卡長什麼樣子？」

這就是 `NetworkAttachmentDefinition`（NAD）的用途——一個 Kubernetes CRD，用來描述附加網路的設定。

阿明寫了他的第一個 NAD：

```yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: vlan88-bridge
  namespace: vm-workloads
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "vlan88-bridge",
      "type": "bridge",
      "bridge": "br-vlan88",
      "vlan": 88,
      "ipam": {
        "type": "static",
        "addresses": [
          { "address": "10.88.10.50/16", "gateway": "10.88.0.1" }
        ]
      }
    }
```

`kubectl apply` 下去，CRD 資源建立了。但阿明盯著這個 YAML 看了很久。

*`type: bridge` 是說用 Linux bridge，`bridge: br-vlan88` 是說掛到哪個 bridge，但這個 bridge 要先在 Node 上存在才行——如果 Node 沒有 `br-vlan88`，這個 NAD 套下去就會失敗。*

他先 SSH 進一台 Node，用 `ip link add br-vlan88 type bridge` 建了橋接介面，再把對應的實體網卡加入 bridge。這步驟讓他意識到：Multus 只管「描述和呼叫」，真正的網路底層還是要 Node 上的設定先就位。

另一個讓他卡住的地方是 `namespace`：NAD 是 namespace-scoped 的資源。VM 在 `vm-workloads` namespace，NAD 也要在同一個 namespace，不然 Multus 找不到它。

---

> ### 📚 去這裡深入了解
> - [核心功能](/multus-cni/core-features) — NetworkAttachmentDefinition 結構、IPAM 選項、Annotation 設定方式
>
> 讀完後，你應該能獨立撰寫 NAD，並理解 `ipam` 欄位的不同選項對 IP 分配行為的影響。

---

## 第四章：「Annotation：告訴 Pod 要幾張網卡」

NAD 建好了，接下來是讓 Pod 用它。

Multus 使用 Pod Annotation 來決定哪個 Pod 需要哪些附加網路。阿明找到格式：

```yaml
metadata:
  annotations:
    k8s.v1.cni.cncf.io/networks: vlan88-bridge
```

如果要指定 namespace，或是給介面取特定名字：

```yaml
k8s.v1.cni.cncf.io/networks: vm-workloads/vlan88-bridge@eth1
```

`@eth1` 的意思是把這張附加網卡命名為 `eth1` 而非預設的 `net1`。阿明本來沒注意到這個細節，結果業務系統設定裡寫死了介面名稱，改成指定名字後才對。

他先用一個普通 Pod 測試，不急著動 VM：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-multus
  namespace: vm-workloads
  annotations:
    k8s.v1.cni.cncf.io/networks: vlan88-bridge
spec:
  containers:
  - name: net-test
    image: nicolaka/netshoot
    command: ["sleep", "infinity"]
```

Pod 起來後，`kubectl exec -it test-multus -- ip addr` 看到兩張網卡：

```
2: eth0@...  inet 10.244.1.23/24
3: net1@...  inet 10.88.10.50/16
```

*成了！* 阿明忍不住在 Slack 上打了一個 🎉 然後馬上刪掉，因為還沒確認 VM 的部分。

他用 `ping 10.88.0.1` 從容器裡打到 VLAN 閘道——通了。

Multus 的 Annotation 機制有一個微妙之處：如果 Annotation 格式寫錯，Pod 會卡在 `ContainerCreating` 狀態，而且錯誤訊息藏在 `kubectl describe pod` 的 Events 裡，不是很直觀。阿明犯了一次拼字錯誤，排查了十分鐘才找到。

---

> ### 📚 去這裡深入了解
> - [核心功能](/multus-cni/core-features) — Annotation 格式、多網路指定、介面命名規則
>
> 讀完後，你應該能正確撰寫多網路 Annotation，並知道如何從 Pod Events 中找到 Multus 的錯誤訊息。

---

## 第五章：「KubeVirt VM 加第二張網卡」

測試 Pod 成功了，現在是真正的挑戰：把多網卡設定套到 KubeVirt 的 VM 上。

KubeVirt 的 `VirtualMachine` 資源有自己的網路設定區塊，不是直接在 Pod Annotation 上加 NAD。它的架構是這樣：

- VM 被包在一個叫 `virt-launcher` 的 Pod 裡運行
- KubeVirt 的 `virt-controller` 負責把 VM spec 轉換成 Pod spec
- 多網路的設定要在 VM 的 `spec.networks` 和 `spec.domain.devices.interfaces` 裡定義

阿明的 VM YAML 改成這樣：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: business-vm
  namespace: vm-workloads
spec:
  template:
    spec:
      networks:
      - name: default
        pod: {}
      - name: vlan-network
        multus:
          networkName: vlan88-bridge
      domain:
        devices:
          interfaces:
          - name: default
            masquerade: {}
          - name: vlan-network
            bridge: {}
```

`spec.networks` 裡的 `pod: {}` 指定第一張網卡用 Pod 網路（即 Flannel），`multus.networkName` 指定第二張用哪個 NAD。

`spec.domain.devices.interfaces` 裡，第一張用 `masquerade` 模式（NAT，讓 VM 能出去 K8s 網路），第二張用 `bridge` 模式（直通，讓 VLAN 流量直接進 VM）。

VM 建立後，阿明進到 VM 裡面（用 `virtctl console business-vm`）執行 `ip addr`：

```
2: eth0  inet 10.0.2.2/24     ← masquerade，K8s 內部用
3: eth1  inet 10.88.10.51/16  ← bridge，業務 VLAN
```

*兩個網段都在，分工清楚：eth0 給 K8s 內部服務互連，eth1 給公司 VLAN 直接存取。* 正是老陳要的。

但是有個細節：`masquerade` 模式下 VM 的 IP 是 `10.0.2.2`，這是 QEMU 虛擬網路預設值，不是真正的 Pod IP。如果業務系統需要知道 VM 真實 Pod IP，要從 `virt-launcher` Pod 那層查，而不是從 VM 裡面查。

---

> ### 📚 去這裡深入了解
> - [核心功能](/multus-cni/core-features) — Multus 與 KubeVirt 搭配的網路設定方式
> - [系統架構](/multus-cni/architecture) — virt-launcher Pod 與 Multus Annotation 的關係
>
> 讀完後，你應該能設定 KubeVirt VM 的多網卡，並理解 masquerade 和 bridge 兩種介面模式的差異。

---

## 第六章：「IPAM：IP 從哪裡來？」

第五章結束後，業務跑了幾天沒問題。但老陳又來了：

> 「現在 VM 的 VLAN IP 是寫死的，如果要多開幾台 VM，IP 不就要一個個手動填？」

*靜態 IP 不能 scale。* 阿明開始研究 IPAM 選項。

Multus 本身不管 IP，它把 IPAM 交給下游 CNI 的 `ipam` 欄位。常見三種：

**1. `static`（靜態，適合少量固定 IP）**

```json
"ipam": {
  "type": "static",
  "addresses": [
    { "address": "10.88.10.50/16", "gateway": "10.88.0.1" }
  ]
}
```

優點：簡單直接。缺點：每台 VM 要改 NAD 或用不同 NAD，沒法自動分配。

**2. `dhcp`（動態，從網路上的 DHCP server 取得）**

```json
"ipam": {
  "type": "dhcp"
}
```

需要網路上真的有 DHCP server，且 DHCP client 要能在容器網路命名空間裡跑。阿明試了一下，公司 VLAN 的 DHCP 有 MAC-IP binding，每台 VM 的 MAC 會自動分配固定 IP——這對業務來說其實很好，因為 VLAN DHCP server 已經有完整的 IP 管理記錄。

**3. `whereabouts`（K8s native IP pool，推薦）**

```json
"ipam": {
  "type": "whereabouts",
  "range": "10.88.10.0/24",
  "exclude": ["10.88.10.1/32", "10.88.10.254/32"]
}
```

`whereabouts` 是專門為 Multus 設計的 IPAM 外掛，它把 IP 分配記錄存在 Kubernetes etcd 裡（用 CRD），多個 Node 上的 Pod 不會拿到重複的 IP，即使 Pod 重建也能做到一定程度的 IP 穩定性。

*阿明最後選了 DHCP，因為公司 VLAN 的 DHCP server 本來就有 MAC-IP binding 管理制度，維運人員習慣在那邊管 IP。如果公司沒有現成 DHCP，他會選 whereabouts。*

---

> ### 📚 去這裡深入了解
> - [核心功能](/multus-cni/core-features) — IPAM 選項比較：static、dhcp、whereabouts
>
> 讀完後，你應該能根據環境需求（有無 DHCP server、需不需要 IP pool 管理）選擇合適的 IPAM 方案。

---

## 第七章：「Thick Plugin：為什麼要一個 Server？」

有一天，公司的資安稽核員問阿明：

> 「Multus 的 CNI binary 直接跑在 root namespace，權限很高吧？如果被注入惡意設定，整個 Node 的網路都能被控制。有什麼辦法降低風險？」

阿明原本用的是 Multus **Thin Plugin** 模式——CNI binary 直接在 Node 上執行，kubelet 呼叫它，它馬上做完就結束，沒有持久的 process。

他查了一下 Multus 文件，找到 **Thick Plugin** 架構：

```
kubelet → thin shim (CNI binary) → gRPC → multus-daemon (DaemonSet Pod)
```

Thick Plugin 多了一層：Node 上有一個持續運行的 `multus-daemon` Pod（以 DaemonSet 部署），CNI 呼叫不再直接執行邏輯，而是透過 Unix Domain Socket 傳給 daemon，由 daemon 處理後回傳結果。

這帶來幾個好處：

1. **安全隔離**：daemon 可以用 Kubernetes RBAC 和 Pod Security 控制其能力，不需要整個 CNI 執行環境都是 root。
2. **可觀測性**：daemon 是長駐 process，可以寫 log、expose metrics，方便排查問題。
3. **設定熱更新**：daemon 可以監聽 ConfigMap 變化，不需要重新部署就能更新設定。
4. **錯誤隔離**：如果 daemon crash，可以被 DaemonSet 重啟，不影響已建立的網路連線。

*代價是多了一個 DaemonSet，在 Node 資源緊的叢集上，每個 Node 多一個 Pod 的 overhead。*

阿明最後跟資安稽核員討論：目前叢集規模不大，選擇在下次大版本升級時改用 Thick Plugin，目前先用 Thin 但限制 Multus DaemonSet 的 Node 安全設定（AppArmor profile、syscall filter）作為緩解。

---

> ### 📚 去這裡深入了解
> - [Thick Plugin 深入剖析](/multus-cni/thick-plugin) — Thin vs Thick 比較、server 架構、Unix Domain Socket 通訊流程
>
> 讀完後，你應該能解釋 Thick Plugin 的安全優勢，並判斷你的環境是否需要從 Thin 升級。

---

## 第八章：「網路不通，從哪裡下手？」

第二個月，另一個團隊的 VM 照著阿明的設定做，但 `net1` 建起來了，卻 ping 不通 VLAN 閘道。他們找阿明幫忙。

阿明列出他的排查 checklist，這是幾個月實戰下來磨出來的：

**Step 1：確認 Multus 有成功建立介面**

```bash
kubectl describe pod <virt-launcher-pod> -n <namespace>
# 看 Events，找有沒有 Multus 的錯誤訊息
kubectl get pod <virt-launcher-pod> -n <namespace> -o jsonpath='{.metadata.annotations}'
# 看 k8s.v1.cni.cncf.io/network-status，確認介面有被建立
```

**Step 2：確認 NAD 和 namespace 對得上**

```bash
kubectl get network-attachment-definitions -n <namespace>
# NAD 要跟 Pod 在同一個 namespace
```

**Step 3：確認 Node 上的 bridge 存在**

```bash
# SSH 到 Pod 所在的 Node
ip link show br-vlan88
bridge link show
```

這次的問題就在這裡：另一個團隊的 VM 被調度到一台新加入的 Node，這台 Node 沒有執行 `br-vlan88` 的建立腳本。*Node 的基礎網路準備是 Multus 管不到的範疇。*

**Step 4：確認 bridge 有正確加入 VLAN trunk**

```bash
bridge vlan show
# 確認 VLAN 88 有在 br-vlan88 的 member port 上
```

**Step 5：抓封包確認流量方向**

```bash
# 在 VM 裡
tcpdump -i eth1 icmp
# 在 Node 上
tcpdump -i br-vlan88 icmp
```

*能在 VM 發出、Node bridge 看到，但沒到閘道 → 實體網路問題（trunk 設定、VLAN 沒開）。*
*VM 根本沒發出 → IPAM 問題（IP 沒設定，或路由不對）。*

阿明花了二十分鐘和那個團隊一起排查，問題鎖定在 Node 初始化腳本沒有跑到新 Node。他建議他們把 bridge 建立的步驟加到 Node provisioning 的 Ansible playbook 裡，讓每台新 Node 自動就位。

---

> ### 📚 去這裡深入了解
> - [設定參考](/multus-cni/configuration) — 完整設定參數與常見錯誤模式
> - [系統架構](/multus-cni/architecture) — Multus DaemonSet 在每個 Node 上做了什麼
>
> 讀完後，你應該能系統性地排查 Multus 多網路不通的問題，從 NAD → Annotation → Node 網路設定逐層確認。

---

## 後記：現在阿明的叢集

三個月後，阿明的 KubeVirt 叢集已經有十幾台 VM 跑著 Multus 多網卡：

- `eth0`：Flannel Pod 網路，給 K8s 內部服務互連
- `eth1`：公司 VLAN，給業務系統直接存取，IP 由 DHCP server 管理

Node 初始化腳本已經自動化，新 Node 加入叢集就會建好 bridge。Thick Plugin 的遷移計畫排在下季度。

老陳的 VM 每天乖乖跑著，阿明的 Slack 好幾週沒有收到網路相關的抱怨。

*這大概是 Platform Engineer 最安靜的快樂。*
