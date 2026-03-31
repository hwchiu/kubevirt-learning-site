# KubeVirt 網路架構總覽

## 設計理念

KubeVirt 的網路架構目標是讓 VM 能夠無縫整合到 Kubernetes 的網路生態系中，同時提供傳統虛擬化平台所具備的進階網路功能。

```
┌─────────────────────────────────────────────────────┐
│                  Kubernetes Node                     │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │              virt-launcher Pod                │  │
│  │                                               │  │
│  │  ┌─────────────────┐    ┌─────────────────┐  │  │
│  │  │  QEMU/KVM VM    │    │  Network Setup  │  │  │
│  │  │                 │◄──►│  (Phase 2)      │  │  │
│  │  │  ┌───────────┐  │    └─────────────────┘  │  │
│  │  │  │  vNIC     │  │                          │  │
│  │  └──┴───────────┴──┘                          │  │
│  │         │                                      │  │
│  │    ┌────▼────────────────────────────────┐    │  │
│  │    │      Pod Network Namespace          │    │  │
│  │    │  eth0 / net1 / net2 ...             │    │  │
│  │    └────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────┘  │
│                      │                               │
│  ┌───────────────────▼───────────────────────────┐  │
│  │  Phase 1 (virt-handler, privileged)           │  │
│  │  - 初始化網路命名空間                           │  │
│  │  - 設定 bridge/tap/veth                        │  │
│  └───────────────────────────────────────────────┘  │
│                      │                               │
│               CNI Plugin (Calico/Flannel/OVN)        │
└─────────────────────────────────────────────────────┘
```

---

## 兩階段網路設定架構

KubeVirt 的網路初始化分為兩個階段，這是為了安全考量（最小權限原則）：

### Phase 1：特權阶段（virt-handler 執行）

- **執行者**：virt-handler（以 root 執行的 DaemonSet）
- **時機**：virt-launcher Pod 啟動後，進入 launcher 的網路命名空間
- **操作**：
  - 建立 tap 介面（tap0）連接到 Pod 的 eth0
  - 設定 bridge（br0）
  - 設定 ARP proxy
  - 準備 SR-IOV VF 並移入命名空間
  - 設定 nftables 規則（Masquerade 模式）
- **特點**：需要 CAP_NET_ADMIN 等網路相關 capabilities

### Phase 2：非特權阶段（virt-launcher 執行）

- **執行者**：virt-launcher（無特殊權限）
- **時機**：QEMU 啟動前
- **操作**：
  - 準備 QEMU 的網路參數（`-netdev tap,id=...`）
  - 設定 DHCP server（若需要）
  - 配置 virtio-net 或 e1000 等虛擬網路卡
- **特點**：無需特殊權限，安全性更高

---

## 網路綁定機制對比

| 機制 | 效能 | Live Migration | 外部可見 IP | 適用場景 |
|------|------|---------------|-------------|----------|
| **Masquerade** | ★★★☆☆ | ✅ 支援 | ❌ NAT，Pod IP | 最常見，一般用途 |
| **Bridge** | ★★★★☆ | ⚠️ 依 CNI 而定 | ✅ 直接存取 | 需要 VM 在 Pod 網路中可見 |
| **SR-IOV** | ★★★★★ | ❌ 不支援 | ✅ 直接存取 | 高效能、低延遲工作負載 |
| **Passt** | ★★★☆☆ | ✅ 支援 | ❌ 透過 user-space | 安全性高，無需特殊權限 |
| ~~Slirp~~ | ★★☆☆☆ | ✅ | ❌ | 已棄用 |
| ~~Macvtap~~ | ★★★★☆ | ⚠️ | ✅ | 已棄用 |

---

## Multus 多網卡支援

KubeVirt 透過 Multus CNI 支援為 VM 連接多個網路：

```
VM
├── eth0  →  Pod Network (Masquerade/Bridge)
├── net1  →  Multus Network 1 (SR-IOV VLAN 100)
└── net2  →  Multus Network 2 (Bridge bond0)
```

### 安裝 Multus

```bash
kubectl apply -f https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/master/deployments/multus-daemonset.yml
```

### 建立 NetworkAttachmentDefinition

```yaml
# 橋接網路 NAD
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: flatl2-net
  namespace: default
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "flatl2-net",
      "type": "bridge",
      "bridge": "br1",
      "isGateway": false,
      "ipam": {
        "type": "whereabouts",
        "range": "192.168.100.0/24",
        "exclude": ["192.168.100.0/30"]
      }
    }
---
# SR-IOV NAD
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: sriov-net
  namespace: default
  annotations:
    k8s.v1.cni.cncf.io/resourceName: intel.com/intel_sriov_netdevice
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "sriov-net",
      "type": "sriov",
      "spoofchk": "off",
      "trust": "on",
      "vlan": 200,
      "ipam": {}
    }
```

---

## 網路介面 Spec 詳細說明

```yaml
spec:
  template:
    spec:
      domain:
        devices:
          interfaces:
          - name: default           # 必須與 networks[].name 對應
            # 綁定機制（二擇一）
            masquerade: {}
            # bridge: {}
            # sriov: {}
            # passt: {}

            # 虛擬網路卡型號
            model: virtio           # virtio, e1000, e1000e, rtl8139, ne2k_pci
            # 指定 MAC Address（省略則自動分配）
            macAddress: "DE:AD:BE:EF:12:34"
            # PCI 位址（精確控制 PCI 拓撲）
            pciAddress: "0000:01:00.0"
            # DHCP 選項（僅 Masquerade/Bridge 有效）
            dhcpOptions:
              bootFileName: pxelinux.0
              tftpServerName: 192.168.1.1
              privateOptions:
              - option: 240
                value: "some-value"
            # Port 對映（Masquerade 使用）
            ports:
            - name: http
              port: 80
              protocol: TCP   # TCP, UDP
            - name: ssh
              port: 22
              protocol: TCP
            # ACPI index（硬體識別用）
            acpiIndex: 1
            # 網路綁定插件名稱（新框架）
            binding:
              name: my-custom-binding
```

---

## 網路資源 Spec

```yaml
spec:
  template:
    spec:
      networks:
      # Pod 網路（每個 VM 只能有一個）
      - name: default
        pod: {}
        # pod:
        #   vmIPv6NetworkCIDR: "fd10:0:2::/120"  # 自定義 IPv6 CIDR

      # Multus 網路
      - name: flatl2
        multus:
          # 引用 NetworkAttachmentDefinition
          networkName: flatl2-net
          # 跨 namespace 引用
          # networkName: other-namespace/sriov-net
          # 是否為預設網路（只有一個可以是 true）
          default: false
```

---

## 網路綁定插件框架（Network Binding Plugin）

KubeVirt v1.1.0 引入了插件框架，讓社群可以開發自訂網路綁定：

```yaml
# 在 KubeVirt CR 中啟用插件
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
spec:
  configuration:
    networkConfiguration:
      binding:
        my-custom-binding:
          sidecarImage: registry/my-binding:v1.0
          networkAttachmentDefinition: my-nad
```

```yaml
# 在 VMI 中使用
interfaces:
- name: net1
  binding:
    name: my-custom-binding
```

---

## 常見網路配置 YAML 範例

### 範例 1：簡單 Masquerade（預設設定）

```yaml
domain:
  devices:
    interfaces:
    - name: default
      masquerade: {}
networks:
- name: default
  pod: {}
```

### 範例 2：多網卡（主網路 Masquerade + 次要 Bridge）

```yaml
domain:
  devices:
    interfaces:
    - name: default
      masquerade: {}
      model: virtio
    - name: internal
      bridge: {}
      model: virtio
      macAddress: "02:00:00:00:00:01"
networks:
- name: default
  pod: {}
- name: internal
  multus:
    networkName: internal-bridge-net
```

### 範例 3：Port Forwarding（Masquerade 模式）

```yaml
domain:
  devices:
    interfaces:
    - name: default
      masquerade: {}
      ports:
      - name: ssh
        port: 22
        protocol: TCP
      - name: http
        port: 80
        protocol: TCP
      - name: app
        port: 8080
        protocol: TCP
networks:
- name: default
  pod: {}
```

### 範例 4：IPv4/IPv6 雙棧（Masquerade）

```yaml
domain:
  devices:
    interfaces:
    - name: default
      masquerade: {}
networks:
- name: default
  pod:
    vmIPv6NetworkCIDR: "fd10:0:2::/120"
```

---

## 常用診斷指令

```bash
# 查看 VMI 的網路資訊
kubectl get vmi my-vm -o jsonpath='{.status.interfaces}' | jq .

# 查看 Pod 網路設定
kubectl exec -it virt-launcher-xxx -- ip addr
kubectl exec -it virt-launcher-xxx -- ip route
kubectl exec -it virt-launcher-xxx -- nft list ruleset  # Masquerade 模式的 nftables 規則

# 確認 Multus 設定
kubectl get network-attachment-definitions
kubectl describe network-attachment-definition sriov-net

# 查看 SR-IOV 資源
kubectl get node <nodename> -o jsonpath='{.status.allocatable}' | jq .

# 排查網路問題
kubectl describe vmi my-vm | grep -A5 "Interfaces"
kubectl logs -n kubevirt ds/virt-handler | grep "network"
```
