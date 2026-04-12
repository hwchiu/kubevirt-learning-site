# KubeVirt 網路架構總覽

KubeVirt 的網路設計目標是讓虛擬機器（VM）能夠無縫地融入 Kubernetes 的網路體系，同時保持 VM 特有的網路特性（如二層網路連通性、固定 MAC 地址、多網卡等）。

---

## 網路設計理念

### VM 執行在 Pod 內

KubeVirt 的每一個 VM 實際上執行在一個 Kubernetes Pod 內（稱為 **virt-launcher pod**）。這意味著：

- VM 的網路存取**必須經過** Pod 的網路介面
- Kubernetes 的所有網路策略（NetworkPolicy）對 virt-launcher pod 同樣有效
- 叢集的 CNI 插件（Calico、Cilium、Flannel 等）繼續負責 Pod 層級的網路

![VM 網路架構](/diagrams/kubevirt/kubevirt-network-stack.png)


### 使用 Kubernetes CNI 基礎架構

KubeVirt 完全依賴 Kubernetes CNI 基礎架構，不替換或繞過現有的 CNI 設定。這帶來的好處：

- **一致性**：所有 Pod 和 VM 使用相同的 CNI 插件
- **可觀測性**：現有的網路監控工具對 VM 同樣適用
- **NetworkPolicy**：可以用 Kubernetes NetworkPolicy 控制 VM 的網路存取

### 目標：VM 網路行為與 Pod 網路一致

KubeVirt 的設計目標是讓 VM 的網路行為盡可能與 Kubernetes Pod 一致，讓平台工程師不需要維護兩套不同的網路模型。

---

## VM 網路 vs Pod 網路差別

### Pod 網路的工作方式

![Pod 網路工作方式](/diagrams/kubevirt/kubevirt-network-pod.png)

### VM 網路的工作方式

VM 的網路需要**額外一層橋接或 NAT**，將 Pod 的網路介面連接到 QEMU 模擬的虛擬網卡：

![VM 網路工作方式](/diagrams/kubevirt/kubevirt-network-vm.png)

### virt-launcher 的角色

`virt-launcher` 是 KubeVirt 為每個 VM 啟動的特殊 Pod，它承擔了：

1. **QEMU 進程管理**：啟動和監控 QEMU/KVM 虛擬機器進程
2. **網路設定橋接**：在 Pod 的 network namespace 內建立橋接或 NAT 規則
3. **生命週期管理**：VM 終止後清理 Pod 資源

---

## 兩階段網路設定架構

KubeVirt 採用**兩階段（Two-Phase）網路設定架構**，解決了「容器無特權」與「網路設定需要特權」之間的矛盾。

![KubeVirt 網路設定兩階段流程](/diagrams/kubevirt/kubevirt-net-overview-1.png)

### Phase 1：特權網路設定

在具有 `NET_ADMIN` 特權的 init container 或 `virt-handler`（Node 上的 DaemonSet）中執行：

| 操作 | 說明 | 適用模式 |
|------|------|---------|
| 建立 Linux Bridge | 將 Pod eth0 連接到橋接器 | Bridge 模式 |
| 設定 iptables MASQUERADE | 設定 NAT 規則，VM IP 偽裝成 Pod IP | Masquerade 模式 |
| 配置 SR-IOV VF | 設定物理 VF 的 VLAN/MAC | SR-IOV 模式 |
| 建立 TAP 設備 | 供 QEMU 直接讀寫 L2 幀 | Bridge/SR-IOV 模式 |
| 設定 nftables 規則 | 管理進出 VM 的流量 | Masquerade 模式 |

:::info 為何分兩階段？
**容器安全性**要求容器盡量以無特權方式運行。但 Linux 網路設定（建立 bridge、設定 iptables）需要 `CAP_NET_ADMIN` 特權。

兩階段設計將特權操作**集中在最小化的初始化階段**，主要的 QEMU 進程以無特權方式運行，符合最小權限原則。
:::

### Phase 2：無特權 QEMU 設定

在無特權的 `virt-launcher` 容器主進程中執行：

| 操作 | 說明 | 適用模式 |
|------|------|---------|
| 配置 QEMU 網路 `-netdev` | 指定 QEMU 使用 TAP 或 passt | Bridge/Passt |
| 設定虛擬 NIC 型號 | virtio-net, e1000, rtl8139 等 | 所有模式 |
| 設定 MAC address | 固定 VM 的 MAC 地址 | 所有模式 |
| 連接 TAP 到 QEMU | 讓 QEMU 直接讀寫網路幀 | Bridge 模式 |

---

## 支援的網路綁定機制完整對比

KubeVirt 支援多種網路綁定機制，各有不同的特性與適用場景：

| 綁定機制 | 需要特權 | Live Migration | 效能 | 狀態 | 主要使用場景 |
|---------|---------|---------------|------|------|------------|
| **Masquerade** | Phase 1 | ✅ 支援 | ★★★☆ | 推薦預設 | 一般用途，與 Pod 網路整合 |
| **Bridge** | Phase 1 | ⚠️ 有條件 | ★★★★ | 穩定 | 二層網路連通，需要固定 IP |
| **SR-IOV** | Phase 1 | ❌ 不支援 | ★★★★★ | 穩定 | 極高效能需求，HPC/NFV |
| **Passt** | ❌ 不需要 | ✅ 支援 | ★★★☆ | 穩定（v1.1.0+） | 安全沙箱、受限環境 |
| **Slirp** | ❌ 不需要 | ❌ 不支援 | ★★☆☆ | **已棄用** | 舊版相容 |
| **Macvtap** | Phase 1 | ❌ 不支援 | ★★★★ | **已棄用** | 舊版相容 |

### Masquerade（推薦預設模式）

Masquerade 是最推薦的預設模式，VM 獲得一個獨立的私有 IP（預設 `10.0.2.2/24`），所有進出流量透過 iptables MASQUERADE 規則使用 Pod IP 進行 NAT。

```
VM Guest (10.0.2.2)
    ↓ MASQUERADE (iptables)
Pod (10.244.1.5)
    ↓
叢集網路
```

**特點：**
- Pod IP 就是 VM 對外的 IP，符合 Kubernetes 網路模型
- 支援 Live Migration（Pod IP 不跟著 VM 移動）
- 可以設定 Port Forwarding 讓外部存取 VM 特定 port

### Bridge（二層橋接）

Bridge 模式將 Pod 的 eth0 介面連接到一個 Linux Bridge，VM 的虛擬網卡也連接到同一個 Bridge，共享 Pod 的 MAC address 和 IP。

**特點：**
- VM 直接共享 Pod IP（二層透明）
- 適合需要 VM 直接暴露在叢集 Pod CIDR 的場景
- Live Migration 時需要特殊處理

### SR-IOV（物理 VF 直通）

SR-IOV 將物理網卡的 Virtual Function（VF）直接分配給 VM，繞過 Linux 網路堆疊，效能最高。

**特點：**
- 接近物理機網路效能（幾乎零額外開銷）
- 需要 SR-IOV 支援的物理網卡和驅動
- **不支援 Live Migration**
- 適合 HPC、NFV、高效能資料庫等場景

### Passt（使用者態網路堆疊）

Passt（Plug A Simple Socket Transport）是較新的網路模式，使用使用者態網路堆疊實現，不需要任何特權操作。

**特點：**
- 完全無特權，適合高安全性環境
- v1.1.0 後正式穩定
- 支援 Live Migration
- 效能略低於 Masquerade（使用者態轉換開銷）

---

## Multus 多網卡支援

### 為何需要 Multus

標準的 Kubernetes 每個 Pod 只有一個網路介面（除了 loopback）。對於許多 VM 使用場景（NFV、多租戶隔離、管理網路分離），需要給 VM 配置**多個網路介面**。

**Multus CNI** 是一個 meta-CNI 插件，允許 Pod 同時連接到多個網路，每個網路使用不同的 CNI 插件設定。

```
┌────────────────────────────────────────────────┐
│  virt-launcher Pod（使用 Multus）              │
│  ┌──────────────────────────────────────────┐  │
│  │  VM                                      │  │
│  │  eth0 (管理網路, 10.0.2.2)   ← Pod網路   │  │
│  │  eth1 (資料網路, 192.168.x.x)← VLAN 100  │  │
│  │  eth2 (儲存網路, 10.100.x.x) ← VLAN 200  │  │
│  └──────────────────────────────────────────┘  │
│  net0: Pod network (masquerade)                │
│  net1: Multus NAD - data-network               │
│  net2: Multus NAD - storage-network            │
└────────────────────────────────────────────────┘
```

### NetworkAttachmentDefinition（NAD）

`NetworkAttachmentDefinition` 是 Multus 定義的 Kubernetes CRD，用於描述一個附加網路的 CNI 設定。

:::warning Multus 安裝確認
使用 Multus 多網卡功能前，確認叢集已安裝 Multus CNI：

```bash
# 確認 Multus DaemonSet 運行中
kubectl get daemonset -n kube-system | grep multus

# 確認 CRD 已安裝
kubectl get crd | grep network-attachment-definitions

# 確認 NAD 已建立
kubectl get network-attachment-definitions -n production
```
:::

---

## NetworkAttachmentDefinition 使用說明

### CNI 設定格式

```yaml
# bridge 類型的 NAD
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: vlan100-network
  namespace: production
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "vlan100-network",
      "type": "bridge",
      "bridge": "br-vlan100",
      "vlan": 100,
      "ipam": {
        "type": "whereabouts",
        "range": "192.168.100.0/24",
        "exclude": ["192.168.100.0/30"]
      }
    }
---
# macvlan 類型的 NAD（直接連接物理網路）
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: macvlan-storage
  namespace: production
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "macvlan-storage",
      "type": "macvlan",
      "master": "eth1",
      "mode": "bridge",
      "ipam": {
        "type": "host-local",
        "subnet": "10.100.0.0/24",
        "rangeStart": "10.100.0.10",
        "rangeEnd": "10.100.0.200",
        "gateway": "10.100.0.1"
      }
    }
---
# SR-IOV 類型的 NAD（高效能網路）
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: sriov-dpdk
  namespace: production
  annotations:
    k8s.v1.cni.cncf.io/resourceName: "intel.com/intel_sriov_netdevice"
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "sriov-dpdk",
      "type": "sriov",
      "resourceName": "intel.com/intel_sriov_netdevice",
      "ipam": {}
    }
---
# ipvlan 類型的 NAD
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: ipvlan-mgmt
  namespace: production
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "ipvlan-mgmt",
      "type": "ipvlan",
      "master": "eth0",
      "mode": "l2",
      "ipam": {
        "type": "static",
        "addresses": [
          {"address": "172.16.0.0/24"}
        ]
      }
    }
```

### 在 VMI spec 中引用 NAD

```yaml
spec:
  networks:
    - name: default
      pod: {}
    - name: vlan100
      multus:
        networkName: "production/vlan100-network"  # namespace/NAD名稱
    - name: storage
      multus:
        networkName: "macvlan-storage"             # 同 namespace 可省略 namespace
        default: false
```

---

## 網路介面 Spec 詳細說明

VM 的網路介面在 `spec.template.spec.domain.devices.interfaces` 中定義：

```yaml
spec:
  template:
    spec:
      domain:
        devices:
          interfaces:
            - name: default
              # 綁定機制（擇一）
              masquerade: {}         # Masquerade NAT 模式
              # bridge: {}           # Bridge 二層模式
              # sriov: {}            # SR-IOV 直通模式
              # passt: {}            # Passt 使用者態模式
              # binding:             # Network Binding Plugin
              #   name: "my-plugin"

              # 虛擬網卡硬體型號
              # virtio:  最佳效能，Linux/Windows 需安裝 virtio 驅動
              # e1000:   Intel e1000 模擬，相容性佳
              # e1000e:  Intel e1000e（更新），Windows 原生支援
              # rtl8139: Realtek RTL8139，老舊但相容性極好
              # ne2k_pci: NE2000 PCI，非常老舊的模擬網卡
              model: virtio

              # 指定 MAC 地址（不指定則 KubeVirt 自動生成）
              macAddress: "02:00:00:00:00:01"

              # Port forwarding 設定（僅 masquerade 模式有效）
              ports:
                - name: http
                  port: 80
                  protocol: TCP
                - name: https
                  port: 443
                  protocol: TCP
                - name: dns
                  port: 53
                  protocol: UDP

              # 指定虛擬 PCIe 地址
              pciAddress: "0000:01:00.0"

              # DHCP 自訂選項（bridge 模式下影響 VM 取得的 DHCP 設定）
              dhcpOptions:
                bootFileName: "pxelinux.0"
                tftpServerName: "192.168.1.100"
                nTPServers:
                  - "192.168.1.1"
                privateOptions:
                  - option: 252
                    value: "http://wpad.example.com/proxy.pac"

              # ACPI 設備序號（影響 VM 內的網卡命名）
              acpiIndex: 1

              # VLAN tag（SR-IOV 模式下設定 VF 的 VLAN）
              tag: 100
```

:::tip Model 選擇建議
```
Linux VM:   model: virtio    （最佳效能，Linux 核心內建 virtio-net）
Windows VM: model: e1000e    （Windows 原生支援，或安裝 virtio-win 驅動後用 virtio）
舊系統相容: model: rtl8139   （幾乎所有 OS 都支援，但效能最差）
```
:::

---

## 網路資源 Spec

VM 使用的網路在 `spec.template.spec.networks` 中定義：

```yaml
spec:
  template:
    spec:
      networks:
        # Pod 網路（Kubernetes 預設網路）
        - name: default
          pod: {}

        # Multus 附加網路
        - name: vlan100
          multus:
            networkName: "production/vlan100-network"

        - name: storage-net
          multus:
            networkName: "macvlan-storage"
            default: false
```

:::info Pod 網路名稱慣例
`networks[].name` 必須與 `interfaces[].name` **完全對應**。

```yaml
networks:
  - name: primary    # 自訂名稱
    pod: {}
interfaces:
  - name: primary    # 必須與 networks 中的名稱一致
    masquerade: {}
```
:::

---

## Network Binding Plugin 框架

### 概述

KubeVirt v1.1.0 引入了 **Network Binding Plugin** 框架，允許第三方實作自定義的網路綁定機制，而不需要修改 KubeVirt 核心程式碼。

:::tip 比 Sidecar Hooks 更靈活
舊版的 sidecar hook 機制需要在每個 VM 的 spec 中指定 annotation，且難以維護。Network Binding Plugin 提供了更結構化、更易於管理的方式來擴展網路功能。
:::

### 設定方式：KubeVirt CR networkBindings

```yaml
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  configuration:
    networkConfiguration:
      networkBindings:
        # 插件名稱
        my-custom-plugin:
          domainAttachmentType: tap   # tap 或 managedTap
          sidecarImage: "registry.example.com/my-network-plugin:v1.0"
          networkAttachmentDefinitionInlining: false
          migration:
            method: link_refresh

        ovn-localnet:
          domainAttachmentType: managedTap
          sidecarImage: "quay.io/kubevirt/network-passt-binding:latest"
```

### 在 VM 中使用 Network Binding Plugin

```yaml
spec:
  template:
    spec:
      domain:
        devices:
          interfaces:
            - name: secondary
              binding:
                name: my-custom-plugin
      networks:
        - name: secondary
          multus:
            networkName: "my-nad"
```

---

## 完整 YAML 範例

### 單網卡 Masquerade 範例

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: ubuntu-single-nic
  namespace: default
spec:
  runStrategy: Always
  template:
    metadata:
      labels:
        kubevirt.io/vm: ubuntu-single-nic
    spec:
      domain:
        cpu:
          cores: 2
        memory:
          guest: 4Gi
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
              model: virtio
              ports:
                - name: ssh
                  port: 22
                  protocol: TCP
                - name: http
                  port: 8080
                  protocol: TCP
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: ubuntu-dv
  dataVolumeTemplates:
    - metadata:
        name: ubuntu-dv
      spec:
        source:
          registry:
            url: "docker://quay.io/containerdisks/ubuntu:22.04"
        storage:
          resources:
            requests:
              storage: 30Gi
```

### 多網卡（Pod + Multus）範例

```yaml
# 步驟 1：建立 NetworkAttachmentDefinition
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: data-network-vlan100
  namespace: production
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "data-network-vlan100",
      "type": "bridge",
      "bridge": "br-data",
      "vlan": 100,
      "macspoofchk": true,
      "ipam": {
        "type": "whereabouts",
        "range": "192.168.100.0/24",
        "gateway": "192.168.100.1"
      }
    }
---
# 步驟 2：建立多網卡 VM
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: multi-nic-vm
  namespace: production
spec:
  runStrategy: Always
  template:
    spec:
      domain:
        cpu:
          cores: 4
        memory:
          guest: 8Gi
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
              model: virtio
              macAddress: "02:00:00:00:00:01"
              ports:
                - name: ssh
                  port: 22
                  protocol: TCP
            - name: data
              bridge: {}
              model: virtio
              macAddress: "02:00:00:00:01:01"
      networks:
        - name: default
          pod: {}
        - name: data
          multus:
            networkName: "data-network-vlan100"
      volumes:
        - name: rootdisk
          dataVolume:
            name: multi-nic-rootdisk
  dataVolumeTemplates:
    - metadata:
        name: multi-nic-rootdisk
      spec:
        source:
          registry:
            url: "docker://quay.io/containerdisks/ubuntu:22.04"
        storage:
          resources:
            requests:
              storage: 30Gi
```

### SR-IOV 範例（簡要）

```yaml
# NetworkAttachmentDefinition for SR-IOV
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: sriov-net
  namespace: production
  annotations:
    k8s.v1.cni.cncf.io/resourceName: "intel.com/intel_sriov_netdevice"
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "sriov-net",
      "type": "sriov",
      "resourceName": "intel.com/intel_sriov_netdevice",
      "ipam": {
        "type": "whereabouts",
        "range": "10.200.0.0/24"
      }
    }
---
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: sriov-high-perf-vm
  namespace: production
spec:
  runStrategy: Always
  template:
    spec:
      domain:
        cpu:
          cores: 8
          dedicatedCpuPlacement: true
        memory:
          guest: 32Gi
          hugepages:
            pageSize: "1Gi"
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
              model: virtio
            - name: sriov-data
              sriov: {}
              model: virtio
              macAddress: "02:00:00:00:02:01"
              tag: 200
      networks:
        - name: default
          pod: {}
        - name: sriov-data
          multus:
            networkName: "sriov-net"
      volumes:
        - name: rootdisk
          dataVolume:
            name: sriov-vm-disk
  dataVolumeTemplates:
    - metadata:
        name: sriov-vm-disk
      spec:
        source:
          registry:
            url: "docker://quay.io/containerdisks/centos:8"
        storage:
          resources:
            requests:
              storage: 50Gi
```

:::danger SR-IOV 不支援 Live Migration
使用 SR-IOV 介面的 VM **無法進行 Live Migration**。若 Node 需要維護，SR-IOV VM 必須先停機再重新調度到其他節點。

建議方案：
- 需要高效能 + Live Migration → 使用 Masquerade + 高速 CNI
- 純效能需求，不需遷移 → 使用 SR-IOV
:::

---

## 架構總覽圖

![KubeVirt 網路架構總覽](/diagrams/kubevirt/kubevirt-net-overview-2.png)

:::tip 網路模式選擇決策樹
```
需要 Live Migration 嗎？
├── 是 → Masquerade 或 Passt
│         ├── 需要 L2 直連（固定 IP，ARP 廣播）→ Bridge + 特殊設定
│         ├── 需要最高安全性（無特權）→ Passt（v1.1.0+）
│         └── 一般使用場景 → Masquerade（推薦）
└── 否 → 需要極高網路效能嗎？
          ├── 是 → SR-IOV（HPC/NFV/資料庫）
          └── 否 → Masquerade 或 Bridge
```
:::
