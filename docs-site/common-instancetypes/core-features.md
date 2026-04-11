---
layout: doc
---

# Common Instancetypes — 核心功能分析

本章深入分析 `kubevirt/common-instancetypes` 專案的核心設計：7 大 Instancetype 系列、Size 規格體系、OS Preference 組合機制、可組合元件架構，以及標準化的 Label 系統。

::: info 相關章節
- 專案整體架構與 Kustomize 建置請參閱 [系統架構](./architecture)
- 測試框架與驗證工具請參閱 [資源類型目錄](./resource-catalog)
- 與 KubeVirt 和 CDI 的整合請參閱 [外部整合](./integration)
:::

## Instancetype 系列總覽

Common Instancetypes 定義了 7 個系列，每個系列針對不同工作負載場景，透過 CPU 配置策略、記憶體比例與進階特性的組合來區分。

### U 系列 — General Purpose（通用型）

U（Universal）系列是最基礎的通用型，VM 以時間切片方式共享物理 CPU 核心，不設定任何進階 CPU 或記憶體特性。

```yaml
# instancetypes/u/1/u1.yaml
kind: VirtualMachineClusterInstancetype
metadata:
  name: "u"
  annotations:
    instancetype.kubevirt.io/description: |-
      The U Series is quite neutral and provides resources for
      general purpose applications.

      *U* is the abbreviation for "Universal", hinting at the universal
      attitude towards workloads.

      VMs of instance types will share physical CPU cores on a
      time-slice basis with other VMs.
    instancetype.kubevirt.io/displayName: "General Purpose"
  labels:
    instancetype.kubevirt.io/class: "general.purpose"
    instancetype.kubevirt.io/icon-pf: "pficon-server-group"
    instancetype.kubevirt.io/version: "1"
    instancetype.kubevirt.io/vendor: "kubevirt.io"
```

::: info 特徵
`spec` 區塊為空，表示 U 系列不啟用任何特殊 CPU 或記憶體配置。CPU:Memory 比例為 **1:4**（例如 1 vCPU / 4Gi）。
:::

### D 系列 — Dedicated vCPU（專用 CPU 型）

D（Dedicated）系列啟用 `dedicatedCPUPlacement` 與 `isolateEmulatorThread`，VM 獲得獨佔的物理 CPU 核心，避免 CPU 時間切片競爭。

```yaml
# instancetypes/d/1/d1.yaml
kind: VirtualMachineClusterInstancetype
metadata:
  name: "d"
  annotations:
    instancetype.kubevirt.io/description: |-
      The D Series is designed for consistent and predictable performance,
      providing resources for general purpose applications.

      *D* is the abbreviation for "Dedicated", reflecting the use of
      dedicated CPU placement for workloads.

      VMs of this instance type are assigned exclusive physical CPU cores,
      avoiding CPU sharing and time-slice contention with other VMs.
    instancetype.kubevirt.io/displayName: "Dedicated vCPU"
  labels:
    instancetype.kubevirt.io/class: "dedicated.vcpu"
    instancetype.kubevirt.io/dedicatedCPUPlacement: "true"
    instancetype.kubevirt.io/isolateEmulatorThread: "true"
spec:
  cpu:
    dedicatedCPUPlacement: true
    isolateEmulatorThread: true
  ioThreadsPolicy: "auto"
```

::: tip D 系列 vs U 系列
D 系列在 U 系列的基礎上增加了 `dedicatedCPUPlacement` 和 `isolateEmulatorThread`，以及 `ioThreadsPolicy: auto`，但**不要求** hugepages 或 vNUMA。CPU:Memory 比例同為 **1:4**。
:::

### CX 系列 — Compute Exclusive（計算密集型）

CX（Compute Exclusive）系列提供最完整的效能隔離配置：專用 CPU、隔離模擬器線程、vNUMA 拓撲透傳，以及 hugepages。

```yaml
# instancetypes/cx/1/cx1.yaml
kind: VirtualMachineClusterInstancetype
metadata:
  name: "cx"
  annotations:
    instancetype.kubevirt.io/description: |-
      The CX Series provides exclusive compute resources for compute
      intensive applications.

      *CX* is the abbreviation of "Compute Exclusive".

      The exclusive resources are given to the compute threads of the
      VM. In order to ensure this, some additional cores (depending
      on the number of disks and NICs) will be requested to offload
      the IO threading from cores dedicated to the workload.
      In addition, in this series, the NUMA topology of the used
      cores is provided to the VM.
    instancetype.kubevirt.io/displayName: "Compute Exclusive"
  labels:
    instancetype.kubevirt.io/class: "compute.exclusive"
    instancetype.kubevirt.io/dedicatedCPUPlacement: "true"
    instancetype.kubevirt.io/isolateEmulatorThread: "true"
    instancetype.kubevirt.io/numa: "true"
spec:
  cpu:
    dedicatedCPUPlacement: true
    isolateEmulatorThread: true
    numa:
      guestMappingPassthrough: {}
  ioThreadsPolicy: "auto"
```

::: warning CX 系列前置需求
- 節點必須啟用 **CPU Manager**
- 節點必須配置 **Hugepages**（sizes.yaml 中指定 2Mi 或 1Gi）
- `maxSockets` 設定為與 guest CPU 數相同，避免 KubeVirt 預設熱插拔行為超出節點可用 CPU
:::

### M 系列 — Memory Intensive（記憶體密集型）

M（Memory）系列專為記憶體密集型應用設計，CPU:Memory 比例為 **1:8**，並預設使用 hugepages。

```yaml
# instancetypes/m/1/m1.yaml
kind: VirtualMachineClusterInstancetype
metadata:
  name: "m1"
  annotations:
    instancetype.kubevirt.io/description: |-
      The M Series provides resources for memory intensive
      applications.

      *M* is the abbreviation of "Memory".
    instancetype.kubevirt.io/displayName: "Memory Intensive"
  labels:
    instancetype.kubevirt.io/class: "memory.intensive"
    instancetype.kubevirt.io/icon-pf: "fa-memory"
    instancetype.kubevirt.io/version: "1"
    instancetype.kubevirt.io/vendor: "kubevirt.io"
spec: {}
```

::: info M 系列特性
`m1.yaml` 自身的 `spec` 為空，但 `sizes.yaml` 中每個 size 都明確配置了 `hugepages.pageSize: "2Mi"`（或 `"1Gi"` 變體），CPU:Memory 為 **1:8**（例如 2 vCPU / 16Gi）。
:::

### N 系列 — Network / DPDK（網路密集型）

N（Network）系列針對 DPDK 等網路密集型工作負載，配備 1Gi hugepages、專用 CPU，並透過 CRI-O annotations 停用 CPU 負載平衡與 IRQ 負載平衡。

```yaml
# instancetypes/n/1/n1.yaml
kind: VirtualMachineClusterInstancetype
metadata:
  name: "n"
  annotations:
    instancetype.kubevirt.io/description: |-
      The N Series provides resources for network intensive DPDK
      applications, like VNFs.

      *N* is the abbreviation for "Network".

      This series of instancetypes requires nodes capable
      of running DPDK workloads and being marked with the respective
      node-role.kubevirt.io/worker-dpdk label as such.
    instancetype.kubevirt.io/displayName: "Network"
  labels:
    instancetype.kubevirt.io/class: "network"
    instancetype.kubevirt.io/dedicatedCPUPlacement: "true"
    instancetype.kubevirt.io/isolateEmulatorThread: "true"
    instancetype.kubevirt.io/hugepages: "1Gi"
spec:
  annotations:
    cpu-load-balancing.crio.io: "disable"
    cpu-quota.crio.io: "disable"
    irq-load-balancing.crio.io: "disable"
  cpu:
    dedicatedCPUPlacement: true
    isolateEmulatorThread: true
  memory:
    hugepages:
      pageSize: "1Gi"
```

::: warning N 系列前置需求
節點必須標記 `node-role.kubevirt.io/worker-dpdk` label，且支援 DPDK 工作負載。CPU:Memory 比例為 **1:2**（例如 4 vCPU / 8Gi）。
:::

### O 系列 — Overcommitted（超額配置型）

O（Overcommitted）系列基於 U 系列，唯一差異是記憶體設定 50% 的 overcommit，使 VM 宣告的記憶體僅需一半的實際記憶體。

```yaml
# instancetypes/o/1/o1.yaml
kind: VirtualMachineClusterInstancetype
metadata:
  name: "o"
  annotations:
    instancetype.kubevirt.io/description: |-
      The O Series is based on the U Series, with the only difference
      being that memory is overcommitted.

      *O* is the abbreviation for "Overcommitted".
    instancetype.kubevirt.io/displayName: "Overcommitted"
  labels:
    instancetype.kubevirt.io/class: "overcommitted"
    instancetype.kubevirt.io/icon-pf: "pficon-virtual-machine"
spec:
  memory:
    overcommitPercent: 50
```

::: tip 記憶體 Overcommit
`overcommitPercent: 50` 代表 VM 實際被分配的記憶體為宣告值的 50%。例如 `o1.large` 宣告 8Gi，實際僅需要 4Gi 節點記憶體。此系列 CPU:Memory 比例與 U 系列相同為 **1:4**。
:::

### RT 系列 — Realtime（即時運算型）

RT（Realtime）系列是功能最齊全的 instancetype，結合專用 CPU、隔離模擬器線程、vNUMA、1Gi hugepages，以及 `realtime` CPU 配置。

```yaml
# instancetypes/rt/1/rt1.yaml
kind: VirtualMachineClusterInstancetype
metadata:
  name: "rt"
  annotations:
    instancetype.kubevirt.io/description: |-
      The RT Series provides resources for realtime applications, like Oslat.

      *RT* is the abbreviation for "realtime".

      This series of instance types requires nodes capable of running
      realtime applications.
    instancetype.kubevirt.io/displayName: "Realtime"
  labels:
    instancetype.kubevirt.io/class: "realtime"
    instancetype.kubevirt.io/dedicatedCPUPlacement: "true"
    instancetype.kubevirt.io/isolateEmulatorThread: "true"
    instancetype.kubevirt.io/numa: "true"
    instancetype.kubevirt.io/realtime: "true"
    instancetype.kubevirt.io/hugepages: "1Gi"
spec:
  annotations:
    cpu-load-balancing.crio.io: disable
    cpu-quota.crio.io: disable
    irq-load-balancing.crio.io: disable
  cpu:
    dedicatedCPUPlacement: true
    isolateEmulatorThread: true
    numa:
      guestMappingPassthrough: {}
    realtime: {}
  memory:
    hugepages:
      pageSize: 1Gi
```

### 系列特性比較表

| 系列 | 全名 | CPU:Mem | dedicatedCPU | isolateEmulator | vNUMA | Hugepages | Realtime | Overcommit | ioThreadsPolicy |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **U** | Universal | 1:4 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | — |
| **D** | Dedicated | 1:4 | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | auto |
| **CX** | Compute Exclusive | 1:2 | ✓ | ✓ | ✓ | 2Mi / 1Gi | ✗ | ✗ | auto |
| **M** | Memory | 1:8 | ✗ | ✗ | ✗ | 2Mi / 1Gi | ✗ | ✗ | — |
| **N** | Network (DPDK) | 1:2 | ✓ | ✓ | ✗ | 1Gi | ✗ | ✗ | — |
| **O** | Overcommitted | 1:4 | ✗ | ✗ | ✗ | ✗ | ✗ | 50% | — |
| **RT** | Realtime | 1:4 | ✓ | ✓ | ✓ | 1Gi | ✓ | ✗ | — |

::: info CRI-O 排程 Annotations
N 和 RT 系列透過 `spec.annotations` 注入 CRI-O 專用的排程提示，確保 Pod 層級的 CPU 隔離：
```yaml
annotations:
  cpu-load-balancing.crio.io: "disable"
  cpu-quota.crio.io: "disable"
  irq-load-balancing.crio.io: "disable"
```
:::

## Size 規格

每個 Instancetype 系列透過 `sizes.yaml` 定義不同的 Size 規格。Size 名稱遵循雲端慣例（nano → 8xlarge），透過 Kustomize 將系列的基礎定義（如 `u1.yaml`）與 sizes 合併產生最終資源。

### U 系列 Size 規格（CPU:Memory = 1:4）

從 `instancetypes/u/1/sizes.yaml` 擷取：

| Size | 名稱 | vCPU | Memory |
|:---:|:---:|:---:|:---:|
| nano | u1.nano | 1 | 512Mi |
| micro | u1.micro | 1 | 1Gi |
| small | u1.small | 1 | 2Gi |
| medium | u1.medium | 1 | 4Gi |
| 2xmedium | u1.2xmedium | 2 | 4Gi |
| large | u1.large | 2 | 8Gi |
| xlarge | u1.xlarge | 4 | 16Gi |
| 2xlarge | u1.2xlarge | 8 | 32Gi |
| 4xlarge | u1.4xlarge | 16 | 64Gi |
| 8xlarge | u1.8xlarge | 32 | 128Gi |

```yaml
# instancetypes/u/1/sizes.yaml（部分摘錄）
---
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: "u1.nano"
  labels:
    instancetype.kubevirt.io/cpu: "1"
    instancetype.kubevirt.io/memory: "512Mi"
    instancetype.kubevirt.io/size: "nano"
spec:
  cpu:
    guest: 1
  memory:
    guest: "512Mi"
---
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: "u1.8xlarge"
  labels:
    instancetype.kubevirt.io/cpu: "32"
    instancetype.kubevirt.io/memory: "128Gi"
    instancetype.kubevirt.io/size: "8xlarge"
spec:
  cpu:
    guest: 32
  memory:
    guest: "128Gi"
```

### CX 系列 Size 規格（CPU:Memory = 1:2 + Hugepages）

CX 系列較為特殊：每個 size 同時提供 **2Mi** 和 **1Gi** 兩種 hugepage 變體，1Gi 變體以 `1gi` 後綴命名。此外，`maxSockets` 設定為與 vCPU 數相同。

從 `instancetypes/cx/1/sizes.yaml` 擷取：

| Size | 名稱 | vCPU | Memory | Hugepage |
|:---:|:---:|:---:|:---:|:---:|
| medium | cx1.medium | 1 | 2Gi | 2Mi |
| medium1gi | cx1.medium1gi | 1 | 2Gi | 1Gi |
| large | cx1.large | 2 | 4Gi | 2Mi |
| large1gi | cx1.large1gi | 2 | 4Gi | 1Gi |
| xlarge | cx1.xlarge | 4 | 8Gi | 2Mi |
| xlarge1gi | cx1.xlarge1gi | 4 | 8Gi | 1Gi |
| 2xlarge | cx1.2xlarge | 8 | 16Gi | 2Mi |
| 2xlarge1gi | cx1.2xlarge1gi | 8 | 16Gi | 1Gi |
| 4xlarge | cx1.4xlarge | 16 | 32Gi | 2Mi |
| 4xlarge1gi | cx1.4xlarge1gi | 16 | 32Gi | 1Gi |
| 8xlarge | cx1.8xlarge | 32 | 64Gi | 2Mi |
| 8xlarge1gi | cx1.8xlarge1gi | 32 | 64Gi | 1Gi |

```yaml
# instancetypes/cx/1/sizes.yaml（部分摘錄）
---
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: "cx1.xlarge"
  labels:
    instancetype.kubevirt.io/cpu: "4"
    instancetype.kubevirt.io/memory: "8Gi"
    instancetype.kubevirt.io/size: "xlarge"
    instancetype.kubevirt.io/hugepages: "2Mi"
spec:
  cpu:
    guest: 4
    maxSockets: 4
  memory:
    guest: "8Gi"
    hugepages:
      pageSize: "2Mi"
---
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: "cx1.xlarge1gi"
  labels:
    instancetype.kubevirt.io/cpu: "4"
    instancetype.kubevirt.io/memory: "8Gi"
    instancetype.kubevirt.io/size: "xlarge1gi"
    instancetype.kubevirt.io/hugepages: "1Gi"
spec:
  cpu:
    guest: 4
    maxSockets: 4
  memory:
    guest: "8Gi"
    hugepages:
      pageSize: "1Gi"
```

### N 系列 Size 規格（CPU:Memory = 1:2，最小為 medium）

N 系列從 `medium`（4 vCPU）起步，沒有 nano / micro / small 等小規格，反映 DPDK 工作負載的最低資源需求。

從 `instancetypes/n/1/sizes.yaml` 擷取：

| Size | 名稱 | vCPU | Memory |
|:---:|:---:|:---:|:---:|
| medium | n1.medium | 4 | 4Gi |
| large | n1.large | 4 | 8Gi |
| xlarge | n1.xlarge | 8 | 16Gi |
| 2xlarge | n1.2xlarge | 16 | 32Gi |
| 4xlarge | n1.4xlarge | 32 | 64Gi |
| 8xlarge | n1.8xlarge | 64 | 128Gi |

::: tip 各系列 Size 範圍比較
- **U / D / O / RT**：nano → 8xlarge（10 種 sizes）
- **CX / M**：medium → 8xlarge（含 `1gi` hugepage 變體，共 12 種）
- **N**：medium → 8xlarge（6 種 sizes，最小 4 vCPU）
:::

## OS Preference 體系

VirtualMachinePreference 定義了 VM 的作業系統偏好設定（韌體、裝置、時鐘等），透過 Kustomize 元件化組合實現。

### 組合架構

所有 Preference 繼承自 `preferences/base/`，提供最基礎的資源骨架：

```yaml
# preferences/base/VirtualMachineClusterPreference.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterPreference
metadata:
  name: VirtualMachineClusterPreference
  labels:
    instancetype.kubevirt.io/vendor: "kubevirt.io"
```

### Linux Preference — 通用 Linux 客機

`linux` 是所有 Linux 發行版 Preference 的基礎，組合了 virtio 磁碟匯流排、virtio 網路介面和亂數產生器：

```yaml
# preferences/linux/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../base

components:
  - ./metadata
  - ../components/diskbus-virtio-blk
  - ../components/interfacemodel-virtio-net
  - ../components/rng

patches:
  - target:
      kind: VirtualMachinePreference
    patch: |-
      - op: replace
        path: /metadata/name
        value: linux
  - target:
      kind: VirtualMachineClusterPreference
    patch: |-
      - op: replace
        path: /metadata/name
        value: linux
```

### RHEL 9 Preference — 架構特化

RHEL 9 為每個架構（amd64、arm64、s390x）定義獨立的 Preference。以 amd64 為例，它繼承 `linux` 的基礎配置，再加上架構要求、Secure Boot 和專用 IO 線程：

```yaml
# preferences/rhel/9/amd64/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

components:
  - ./metadata
  - ./requirements
  - ../../../components/preferred-architecture/amd64
  - ../../../components/required-architecture/amd64
  - ../../../components/disk-dedicatediothread
  - ../../../components/secureboot

nameSuffix: ".9"
```

搭配 requirements 元件設定最低硬體需求：

```yaml
# preferences/rhel/9/amd64/requirements/requirements.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: requirements
  labels:
    instancetype.kubevirt.io/required-cpu: "1"
    instancetype.kubevirt.io/required-memory: "1.5Gi"
spec:
  requirements:
    cpu:
      guest: 1
    memory:
      guest: 1.5Gi
```

### Fedora Preference — 繼承 Linux + Secure Boot

Fedora 繼承自 `linux` Preference，增加架構限制和 Secure Boot：

```yaml
# preferences/fedora/amd64/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../linux

components:
  - ./metadata
  - ../requirements
  - ../../components/preferred-architecture/amd64
  - ../../components/required-architecture/amd64
  - ../../components/secureboot

patches:
  - target:
      kind: VirtualMachinePreference
    patch: |-
      - op: replace
        path: /metadata/name
        value: fedora
  - target:
      kind: VirtualMachineClusterPreference
    patch: |-
      - op: replace
        path: /metadata/name
        value: fedora
```

### Windows 2022 Preference — 完整企業級配置

Windows Server 2022 繼承 `windows/base`（包含 Hyper-V 模擬、SATA 磁碟、e1000e 網卡、USB Tablet 輸入等），再增加 EFI 永久儲存、TPM 和 Secure Boot：

```yaml
# preferences/windows/2k22/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../base

components:
  - ./metadata
  - ./requirements
  - ../../components/efi-persisted
  - ../../components/tpm
  - ../../components/secureboot

nameSuffix: .2k22
```

其中 `windows/base` 的組合層級：

```yaml
# preferences/windows/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

components:
  - ./metadata
  - ../../components/hyperv
  - ../../components/cpu-topology-sockets
  - ../../components/diskbus-sata
  - ../../components/interfacemodel-e1000e
  - ../../components/tablet-usb
  - ../../components/termination-grace-period
```

### Preference 繼承關係

![Preference 繼承關係](/diagrams/common-instancetypes/instancetypes-preference-inheritance.png)

### OS Preference 元件組合對照表

| Preference | 磁碟匯流排 | 網路介面 | Secure Boot | EFI | TPM | Hyper-V | RNG | 架構 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **linux** | virtio | virtio | ✗ | ✗ | ✗ | ✗ | ✓ | — |
| **fedora** (amd64) | virtio | virtio | ✓ | ✗ | ✗ | ✗ | ✓ | amd64 |
| **rhel.9** (amd64) | virtio | virtio | ✓ | ✗ | ✗ | ✗ | ✓ | amd64 |
| **windows** (base) | sata | e1000e | ✗ | ✗ | ✗ | ✓ | ✗ | — |
| **windows.2k22** | sata | e1000e | ✓ | ✓ (persisted) | ✓ | ✓ | ✗ | — |

## 可組合元件

`preferences/components/` 目錄包含所有可重複使用的 Kustomize Component，每個元件透過 Strategic Merge Patch 將特定配置注入 VirtualMachinePreference。

### 韌體與安全元件

#### Secure Boot

啟用 UEFI Secure Boot 並開啟 SMM（System Management Mode）：

```yaml
# preferences/components/secureboot/secureboot.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: secureboot
spec:
  features:
    preferredSmm: {}
  firmware:
    preferredEfi:
      secureBoot: true
```

#### EFI（非持久化）

啟用 UEFI 韌體但不開啟 Secure Boot：

```yaml
# preferences/components/efi/efi.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: efi
spec:
  firmware:
    preferredEfi:
      secureBoot: false
```

#### EFI Persisted（持久化 EFI 變數）

啟用 UEFI 韌體並持久化 EFI 變數（如 Boot 順序），供需要儲存韌體狀態的 OS 使用：

```yaml
# preferences/components/efi-persisted/efi.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: efi
spec:
  firmware:
    preferredEfi:
      persistent: true
      secureBoot: false
```

#### TPM（可信平台模組）

啟用持久化的 vTPM 裝置，Windows 11 / Server 2022+ 等系統的必要安全元件：

```yaml
# preferences/components/tpm/tpm.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: tpm
spec:
  devices:
    preferredTPM:
      persistent: true
```

### Hyper-V 模擬元件

Windows 客機的核心元件，配置完整的 Hyper-V enlightenments 以最佳化 Windows 虛擬化效能：

```yaml
# preferences/components/hyperv/hyperv.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: hyperv
spec:
  clock:
    preferredClockOffset:
      utc: {}
    preferredTimer:
      hpet:
        present: false
      pit:
        tickPolicy: delay
      rtc:
        tickPolicy: catchup
      hyperv: {}
  features:
    preferredAcpi: {}
    preferredApic: {}
    preferredHyperv:
      relaxed: {}
      vapic: {}
      vpindex: {}
      spinlocks:
        spinlocks: 8191
      synic: {}
      synictimer:
        direct: {}
      tlbflush: {}
      frequencies: {}
      reenlightenment: {}
      ipi: {}
      runtime: {}
      reset: {}
```

::: info Hyper-V Enlightenments 詳解
此元件啟用了完整的 Hyper-V 半虛擬化特性：
- **relaxed / vapic / vpindex** — 基礎半虛擬化加速
- **spinlocks (8191)** — 自旋鎖最佳化
- **synic / synictimer (direct)** — 合成中斷控制器與計時器
- **tlbflush** — TLB 快取刷新最佳化
- **frequencies / reenlightenment** — 時鐘頻率與 re-enlightenment 通知
- **ipi / runtime / reset** — 處理器間中斷、執行時資訊、重設功能

同時停用 HPET 計時器，設定 PIT 為 `delay` 策略、RTC 為 `catchup` 策略。
:::

### 裝置元件

#### RNG（亂數產生器）

```yaml
# preferences/components/rng/rng.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: rng
spec:
  devices:
    preferredRng: {}
```

#### 磁碟匯流排（Disk Bus）

三種磁碟匯流排選項：

```yaml
# preferences/components/diskbus-virtio-blk/diskbus-virtio-blk.yaml
spec:
  devices:
    preferredDiskBus: virtio

# preferences/components/diskbus-sata/diskbus-sata.yaml
spec:
  devices:
    preferredDiskBus: sata

# preferences/components/diskbus-scsi/diskbus-scsi.yaml
spec:
  devices:
    preferredDiskBus: scsi
```

#### 網路介面模型（Interface Model）

四種網路介面模型選項：

```yaml
# preferences/components/interfacemodel-virtio-net/interfacemodel-virtio-net.yaml
spec:
  devices:
    preferredInterfaceModel: virtio

# preferences/components/interfacemodel-e1000e/e1000e.yaml
spec:
  devices:
    preferredInterfaceModel: e1000e

# preferences/components/interfacemodel-e1000/e1000.yaml
spec:
  devices:
    preferredInterfaceModel: e1000

# preferences/components/interfacemodel-rtl8139/rtl8139.yaml
spec:
  devices:
    preferredInterfaceModel: rtl8139
```

::: tip 磁碟匯流排與網路介面的選擇
- **Linux 客機**：使用 `virtio`（磁碟）+ `virtio`（網路）以獲得最佳效能
- **Windows 客機**：使用 `sata`（磁碟）+ `e1000e`（網路）以確保開箱即用的驅動支援
- **舊版 OS**：可能需要 `e1000` 或 `rtl8139`
:::

### CPU 拓撲元件

#### cpu-topology-sockets（Socket 拓撲）

將 CPU 拓撲偏好設為 sockets，Windows 許可通常以 socket 計費：

```yaml
# preferences/components/cpu-topology-sockets/cpu-topology-sockets.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: cpu-topology-sockets
spec:
  cpu:
    preferredCPUTopology: sockets
```

#### cpu-topology-spread（分散拓撲）

將 vCPU 均勻分散到 sockets、cores、threads 三個維度：

```yaml
# preferences/components/cpu-topology-spread/cpu-topology-spread.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: cpu-topology-spread
spec:
  cpu:
    preferredCPUTopology: spread
    spreadOptions:
      across: SocketsCoresThreads
```

#### cpu-topology-spread-4（4:1 分散比例）

指定 `ratio: 4` 的分散拓撲，通常用於 SMT（Simultaneous Multi-Threading）場景：

```yaml
# preferences/components/cpu-topology-spread-4/cpu-topology-spread-4.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: cpu-topology-spread-4
spec:
  cpu:
    preferredCPUTopology: spread
    spreadOptions:
      across: SocketsCoresThreads
      ratio: 4
```

### 架構需求元件

#### required-architecture

以 label 和 spec 雙重方式指定所需的 CPU 架構，支援 amd64、arm64、s390x：

```yaml
# preferences/components/required-architecture/amd64/required-architecture.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: required-architecture
  labels:
    instancetype.kubevirt.io/required-architecture: "amd64"
spec:
  requirements:
    architecture: "amd64"
```

#### preferred-architecture

僅設定偏好架構（不強制），用於排程提示：

```yaml
# preferences/components/preferred-architecture/amd64/preferred-architecture.yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachinePreference
metadata:
  name: preferred-architecture
  labels:
    instancetype.kubevirt.io/preferred-architecture: "amd64"
spec:
  preferredArchitecture: "amd64"
```

### 元件總覽表

| 元件 | 分類 | 作用 |
|:---|:---:|:---|
| `secureboot` | 韌體 | 啟用 UEFI Secure Boot + SMM |
| `efi` | 韌體 | 啟用 UEFI（不含 Secure Boot） |
| `efi-persisted` | 韌體 | 啟用持久化 UEFI 變數 |
| `tpm` | 安全 | 啟用持久化 vTPM |
| `hyperv` | 特性 | 完整 Hyper-V enlightenments + 時鐘配置 |
| `rng` | 裝置 | 啟用虛擬亂數產生器 |
| `diskbus-virtio-blk` | 磁碟 | 偏好 virtio 磁碟匯流排 |
| `diskbus-sata` | 磁碟 | 偏好 SATA 磁碟匯流排 |
| `diskbus-scsi` | 磁碟 | 偏好 SCSI 磁碟匯流排 |
| `interfacemodel-virtio-net` | 網路 | 偏好 virtio 網路介面 |
| `interfacemodel-e1000e` | 網路 | 偏好 e1000e 網路介面 |
| `interfacemodel-e1000` | 網路 | 偏好 e1000 網路介面 |
| `interfacemodel-rtl8139` | 網路 | 偏好 rtl8139 網路介面 |
| `cpu-topology-sockets` | CPU | CPU 拓撲以 socket 為主 |
| `cpu-topology-spread` | CPU | CPU 拓撲均勻分散 |
| `cpu-topology-spread-4` | CPU | CPU 拓撲以 4:1 比例分散 |
| `required-architecture` | 架構 | 強制要求特定 CPU 架構 |
| `preferred-architecture` | 架構 | 偏好特定 CPU 架構（不強制） |
| `disk-dedicatediothread` | 磁碟 | 啟用專用 IO 線程 |
| `tablet-usb` | 輸入 | 啟用 USB Tablet 輸入裝置 |
| `interface-multiqueue` | 網路 | 啟用網路介面多佇列 |
| `termination-grace-period` | 生命週期 | 設定 3600 秒終止寬限期（Windows） |

## 命名慣例與 Label 系統

Common Instancetypes 使用標準化的 Label 系統，讓使用者可以透過 `kubectl` label selector 快速查詢和篩選資源。

### 查詢範例

```shell
# 列出所有提供 4 個 vCPU 的 Instancetype
$ kubectl get virtualmachineclusterinstancetype \
    -l instancetype.kubevirt.io/cpu=4
NAME         AGE
cx1.xlarge   39s
m1.xlarge    39s
n1.large     39s
n1.medium    39s
o1.xlarge    39s
u1.xlarge    39s
```

### 通用 Label

適用於所有 Instancetype 和 Preference 資源：

| Label | 說明 | 範例值 |
|:---|:---|:---|
| `instancetype.kubevirt.io/common-instancetypes-version` | 產生資源的 common-instancetypes 專案版本 | `1.2.0` |
| `instancetype.kubevirt.io/vendor` | 資源供應商（上游固定為 `kubevirt.io`） | `kubevirt.io` |
| `instancetype.kubevirt.io/icon-pf` | 建議使用的 PatternFly 圖示 | `pficon-server-group` |
| `instancetype.kubevirt.io/deprecated` | 標記已棄用的資源 | `true` |

### Instancetype 專用 Label

| Label | 說明 | 範例值 |
|:---|:---|:---|
| `instancetype.kubevirt.io/version` | Instancetype class 的版本 | `1` |
| `instancetype.kubevirt.io/class` | Instancetype 的分類 | `general.purpose`、`compute.exclusive` |
| `instancetype.kubevirt.io/cpu` | 提供的 vCPU 數量 | `4` |
| `instancetype.kubevirt.io/memory` | 提供的記憶體量 | `16Gi` |
| `instancetype.kubevirt.io/size` | Size 名稱 | `xlarge` |
| `instancetype.kubevirt.io/numa` | 是否啟用 NUMA guestMappingPassthrough（選用） | `true` |
| `instancetype.kubevirt.io/dedicatedCPUPlacement` | 是否啟用專用 CPU 配置（選用） | `true` |
| `instancetype.kubevirt.io/isolateEmulatorThread` | 是否隔離模擬器線程（選用） | `true` |
| `instancetype.kubevirt.io/hugepages` | Hugepage 大小（選用） | `2Mi`、`1Gi` |
| `instancetype.kubevirt.io/realtime` | 是否為即時運算型（選用） | `true` |

### Preference 專用 Label

| Label | 說明 | 範例值 |
|:---|:---|:---|
| `instancetype.kubevirt.io/os-type` | 工作負載的作業系統類型 | `linux`、`windows`、`legacy` |
| `instancetype.kubevirt.io/arch` | 工作負載支援的 CPU 架構 | `amd64`、`arm64` |
| `instancetype.kubevirt.io/required-cpu` | 最低 CPU 需求 | `1` |
| `instancetype.kubevirt.io/required-memory` | 最低記憶體需求 | `2Gi` |
| `instancetype.kubevirt.io/required-architecture` | 強制要求的 CPU 架構 | `amd64` |
| `instancetype.kubevirt.io/preferred-architecture` | 偏好的 CPU 架構 | `amd64` |

::: tip Label 設計原則
Label 系統的核心設計原則是**資源可被查詢**。每個 instancetype 和 preference 透過 label 暴露其特性，使用者不需要閱讀 spec 內容即可透過 `kubectl get -l` 篩選出符合需求的資源。下游供應商可修改 `instancetype.kubevirt.io/vendor` 為自己的識別標記。
:::
