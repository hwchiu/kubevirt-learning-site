# Instancetype & Preference — VM 規格模板系統

KubeVirt 的 **Instancetype** 與 **Preference** 系統提供了一套標準化的 VM 規格模板機制，讓平台管理員可以預先定義好 VM 的資源規格與硬體偏好，使用者只需引用對應模板即可快速建立符合需求的虛擬機器。

## 為什麼需要 Instancetype / Preference

在沒有 Instancetype 系統之前，每次建立 VM 都必須在 `VirtualMachine` 的 spec 中重複指定 CPU 數量、記憶體大小、磁碟介面類型、網路介面型號等詳細設定，這造成了以下問題：

- **設定重複**：每個 VM YAML 都包含大量相同的資源設定
- **難以維護**：若要調整規格（例如全面升級 memory），需逐一修改所有 VM 定義
- **缺乏標準化**：不同團隊或使用者可能使用不一致的設定，造成效能不均
- **學習門檻高**：使用者必須了解所有底層硬體選項才能建立 VM

:::tip 類比公有雲 Instance Size
Instancetype 的設計概念直接借鑑自公有雲的 Instance Type 系統：

| 公有雲 | KubeVirt |
|--------|---------|
| t3.micro (1 vCPU, 1 GiB) | instancetype: small |
| t3.medium (2 vCPU, 4 GiB) | instancetype: medium |
| m5.xlarge (4 vCPU, 16 GiB) | instancetype: large |
| 設定 OS 偏好選項 | preference: ubuntu / windows |

使用者只需指定 `instancetype: cx1.large`，不需要知道底層的 CPU 拓撲設定細節。
:::

### Instancetype 與 Preference 的職責分工

這兩個資源有明確的職責劃分：

- **Instancetype**：負責**資源規格**（Resource），定義 VM 能使用多少 CPU、Memory、GPU 等計算資源。這些值是**強制性**的，VM spec 中不能覆蓋。
- **Preference**：負責**硬體偏好**（Preference），定義 VM 偏好使用哪種磁碟介面、網卡型號、韌體設定等。這些值是**建議性**的，VM spec 中明確指定的值優先。

```
Instancetype    →  CPU 數量、Memory 大小、GPU、I/O 策略  (強制)
Preference      →  磁碟 bus、網卡 model、BIOS/EFI、機器類型  (建議)
```

---

## VirtualMachineInstancetype vs VirtualMachineClusterInstancetype

KubeVirt 提供兩種作用域的 Instancetype 資源：

### 對比說明

| 屬性 | VirtualMachineInstancetype | VirtualMachineClusterInstancetype |
|------|---------------------------|----------------------------------|
| **作用域** | Namespace-scoped | Cluster-scoped |
| **縮寫** | `vmit` | `vmcit` |
| **誰可以建立** | 具備 namespace 寫入權限的使用者 | 叢集管理員 |
| **可見範圍** | 僅限同一 Namespace | 所有 Namespace |
| **使用場景** | 專案專屬規格（例如開發/測試環境） | 全叢集共用標準規格 |
| **Kind 引用** | `VirtualMachineInstancetype` | `VirtualMachineClusterInstancetype` |

### 使用場景選擇

:::info Namespace-scoped（VirtualMachineInstancetype）
適用於：
- 不同團隊需要不同的客製規格
- 測試用的特殊規格（例如加大 memory 的 debug instancetype）
- 租戶自行管理的資源規格
:::

:::info Cluster-scoped（VirtualMachineClusterInstancetype）
適用於：
- 平台提供給所有使用者的標準規格（如 small/medium/large/xlarge）
- 需確保全叢集規格一致性的企業環境
- KubeVirt 社群提供的預設 instancetype（如 `u1.micro`, `cx1.medium`）
:::

---

## VirtualMachinePreference vs VirtualMachineClusterPreference

| 屬性 | VirtualMachinePreference | VirtualMachineClusterPreference |
|------|-------------------------|--------------------------------|
| **作用域** | Namespace-scoped | Cluster-scoped |
| **縮寫** | `vmpref` | `vmcpref` |
| **誰可以建立** | 具備 namespace 寫入權限的使用者 | 叢集管理員 |
| **可見範圍** | 僅限同一 Namespace | 所有 Namespace |
| **使用場景** | 特定 OS 或應用的偏好設定 | 全叢集共用 OS 偏好（如 windows/ubuntu） |

---

## Instancetype Spec 完整欄位

### CPU 設定

```yaml
spec:
  cpu:
    # vCPU 數量（必填）
    guest: 4

    # 專屬 CPU 隔離：將 vCPU 綁定到實體 CPU，避免被其他 Pod 搶佔
    # 需要 Node 有 CPU Manager Policy = static
    dedicatedCpuPlacement: true

    # 隔離 emulator thread 到獨立的實體 CPU
    # 需搭配 dedicatedCpuPlacement: true 使用
    isolateEmulatorThread: true

    # 即時應用（Real-time）設定
    realtime:
      # CPU affinity mask，指定哪些 vCPU 用於 real-time
      mask: "0-3"

    # 熱插拔 vCPU 的上限（最多可以動態增加到幾個 socket）
    maxSockets: 8

    # NUMA 感知 CPU 拓撲
    numa:
      guestMappingPassthrough: {}
```

:::warning dedicatedCpuPlacement 前提條件
使用 `dedicatedCpuPlacement: true` 需要：
1. Kubernetes Node 啟用 **CPU Manager** (`--cpu-manager-policy=static`)
2. Pod 的 QoS 等級必須是 **Guaranteed**（request == limit）
3. Node 有足夠的可分配專屬 CPU

若條件不符合，VM 將無法調度。
:::

### Memory 設定

```yaml
spec:
  memory:
    # 分配給 VM Guest 的記憶體大小（必填）
    guest: 8Gi

    # 使用 HugePages 提升記憶體存取效能
    hugepages:
      # 支援 2Mi（2MB）或 1Gi（1GB）
      pageSize: "1Gi"

    # 記憶體熱插拔上限
    # VM 啟動後可以動態增加記憶體到此上限
    maxGuest: 32Gi

    # 記憶體超訂百分比（% of guest memory）
    # 例如 150 代表分配 8Gi 但只保留 8Gi * 100/150 ≈ 5.3Gi 物理記憶體
    overcommitPercent: 0
```

:::tip HugePages 效能
`hugepages.pageSize: "1Gi"` 特別適合資料庫、記憶體密集型應用（如 Redis、Oracle DB），可顯著減少 TLB miss，提升 5-20% 效能。需確保 Node 有預先分配的 HugePages。
:::

### GPU 設定

```yaml
spec:
  gpus:
    - name: gpu1
      deviceName: "nvidia.com/GA102GL_A10"
      # 虛擬 GPU 選項
      virtualGPUOptions:
        display:
          # 啟用 GPU 顯示輸出
          enabled: true
          ramFB:
            enabled: true
```

### 主機設備直通

```yaml
spec:
  hostDevices:
    - name: fpga0
      deviceName: "xilinx.com/fpga-xilinx-u250"
```

### I/O 與安全設定

```yaml
spec:
  # I/O Thread 策略
  # auto: KubeVirt 自動決定
  # shared: 共享 I/O thread
  ioThreadsPolicy: "auto"

  # 啟動安全設定（AMD SEV）
  launchSecurity:
    sev: {}
```

---

## Preference Spec 完整欄位

### CPU 拓撲偏好

```yaml
spec:
  cpu:
    # 偏好的 CPU 拓撲呈現方式
    # Cores:   所有 vCPU 以 core 方式呈現（1 socket, N cores, 1 thread）
    # Sockets: 所有 vCPU 以 socket 方式呈現（N sockets, 1 core, 1 thread）
    # Threads: 所有 vCPU 以 thread 方式呈現（1 socket, 1 core, N threads）
    # Spread:  平均分散到 sockets/cores/threads（最接近物理機行為）
    # Any:     不指定，由 KubeVirt 自動決定
    preferredCPUTopology: Cores
```

### Memory 偏好

```yaml
spec:
  memory:
    preferredHugePageSize: "2Mi"
    hugePages: {}
```

### 設備偏好（最豐富的設定區段）

```yaml
spec:
  devices:
    # 磁碟匯流排類型
    # virtio: 最佳效能，需要 virtio 驅動（Linux 原生支援）
    # sata:   相容性最好，適合 Windows
    # scsi:   支援 SCSI 指令集
    preferredDiskBus: virtio

    # 網路介面卡型號
    # virtio:  最佳效能，需要 virtio-net 驅動
    # e1000:   Intel e1000 模擬，Windows 原生支援
    # e1000e:  Intel e1000e 模擬（更新版本）
    preferredInterfaceModel: virtio

    # 輸入設備（滑鼠/鍵盤）偏好
    # bus: usb / virtio / ps2
    # type: tablet / mouse / keyboard
    preferredInputBus: usb
    preferredInputType: tablet

    # 磁碟區塊大小偏好（最佳化 I/O 對齊）
    preferredDiskBlockSize:
      logical: 512
      physical: 4096

    # CD-ROM 匯流排類型
    preferredCdromBus: sata

    # LUN 設備匯流排
    preferredLunBus: scsi

    # 自動附加圖形設備（VGA/QXL）
    preferredAutoattachGraphicsDevice: true

    # 自動附加 TPM 2.0 晶片（Windows 11 需要）
    preferredTPM:
      persistent: true

    # 虛擬 GPU 顯示選項
    preferredVirtualGPUOptions:
      display:
        enabled: true
```

### 功能特性偏好

```yaml
spec:
  features:
    preferredAcpi: {}
    preferredApic:
      enabled: true
    preferredHyperv:
      relaxed:
        enabled: true
      vapic:
        enabled: true
      spinlocks:
        enabled: true
        retries: 8191
    preferredKvmFeatures:
      kvmclock:
        enabled: true
```

### 韌體偏好

```yaml
spec:
  firmware:
    # 使用傳統 BIOS
    preferredUseBios: false
    preferredUseBiosSerial: false

    # 使用 UEFI（EFI）
    preferredUseEfi: true

    # 啟用 Secure Boot（需要 EFI）
    preferredUseSecureBoot: true
```

:::warning Windows 11 韌體需求
Windows 11 需要同時啟用：
- `preferredUseEfi: true`
- `preferredUseSecureBoot: true`
- `preferredTPM.persistent: true`

否則安裝程式會拒絕安裝。
:::

### 機器類型偏好

```yaml
spec:
  machine:
    # q35: 現代 PCIe 架構，支援更多虛擬設備（推薦）
    # pc:  傳統 ISA 架構，相容性最好
    preferredMachineType: "q35"
```

### 時鐘偏好

```yaml
spec:
  clock:
    preferredClockOffset:
      # utc: 使用 UTC 時間（Linux 推薦）
      # timezone: 使用指定時區
      utc: {}
    preferredTimer:
      hpet:
        present: false
      pit:
        tickPolicy: delay
      rtc:
        tickPolicy: catchup
      hyperv: {}
      kvm: {}
      kvmclock:
        present: true
```

### 儲存與其他偏好

```yaml
spec:
  volumes:
    # 建立 DataVolume 時的預設 StorageClass
    preferredStorageClassName: "premium-ssd"

  # 偏好的子網域（影響 DNS 解析）
  subdomain: "vm-cluster"

  # 預設優雅終止時間（秒）
  preferredTerminationGracePeriodSeconds: 180
```

---

## Requirements（最低規格需求）

Preference 可以定義 VM 必須滿足的最低規格需求：

```yaml
spec:
  requirements:
    cpu:
      # VM 必須具備這些 CPU 功能才能使用此 Preference
      minimumCPUFeatures:
        - name: "avx2"
        - name: "aes"
    memory:
      guest: 2Gi
```

:::info Requirements 的作用
`requirements` 欄位確保 VM 在使用此 Preference 時，其 Instancetype 必須滿足最低規格。例如定義 `windows-11` preference 時，可要求最少 4 vCPU 和 4 GiB 記憶體，避免使用者用 `micro` instancetype 建立 Windows 11 VM 而導致效能極差。
:::

---

## 如何在 VM 中引用

### 直接指定名稱

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-vm
  namespace: production
spec:
  # 引用 Instancetype
  instancetype:
    # kind 可以是:
    # VirtualMachineInstancetype (namespace-scoped, 預設)
    # VirtualMachineClusterInstancetype (cluster-scoped)
    kind: VirtualMachineClusterInstancetype
    name: "medium"
    # revisionName: 可指定特定版本的 ControllerRevision（可選）
    # revisionName: "medium-v2"

  # 引用 Preference
  preference:
    kind: VirtualMachineClusterPreference
    name: "ubuntu"

  runStrategy: Always
  template:
    spec:
      domain:
        # 不需要再指定 CPU/Memory，由 instancetype 決定
        devices:
          disks:
            - name: rootdisk
              disk:
                # 不需要指定 bus，由 preference 決定
                {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: ubuntu-dv
```

### 從 Volume 自動推斷（inferFromVolume）

當使用從公共映像庫下載的磁碟時，映像可能已標記對應的 instancetype 和 preference，KubeVirt 可以自動推斷：

```yaml
spec:
  instancetype:
    # 從名為 "rootdisk" 的 volume 推斷 instancetype
    inferFromVolume: rootdisk
    # 推斷失敗時的行為: Ignore（忽略）或 Reject（拒絕建立）
    inferFromVolumeFailurePolicy: Ignore

  preference:
    inferFromVolume: rootdisk
    inferFromVolumeFailurePolicy: Reject
```

推斷依賴 DataVolume 或 PVC 上的標籤：

```yaml
# 在 DataVolume 或 PVC 上標記
metadata:
  labels:
    instancetype.kubevirt.io/default-instancetype: "cx1.medium"
    instancetype.kubevirt.io/default-instancetype-kind: "VirtualMachineClusterInstancetype"
    instancetype.kubevirt.io/default-preference: "ubuntu"
    instancetype.kubevirt.io/default-preference-kind: "VirtualMachineClusterPreference"
```

### ControllerRevision 的角色

當 VM 引用 Instancetype 或 Preference 後，KubeVirt 會自動建立 **ControllerRevision** 物件，記錄當時引用的版本快照：

```bash
# 查看 VM 使用的 ControllerRevision
kubectl get controllerrevision -n production

# ControllerRevision 命名格式: <resource-name>-<hash>
# 例如: medium-12345678
```

:::tip ControllerRevision 的重要性
ControllerRevision 確保了 **VM 設定的不可變性**。即使叢集管理員後來修改了 Instancetype 定義，已存在的 VM 仍然使用建立時的版本，避免在不知情的情況下變更 VM 規格。

只有在 VM 明確更新 `revisionName` 或重新建立後，才會套用新版本的 Instancetype/Preference。
:::

---

## 衝突解決機制

### Instancetype 與 VM spec 的衝突

Instancetype 定義的是**資源規格**，屬於**強制性**設定：

```
衝突規則：Instancetype 的設定 > VM spec 的設定（Instancetype 優先）
```

例如，如果 Instancetype 定義 `cpu.guest: 4`，但 VM spec 也設定了 `domain.cpu.cores: 2`，KubeVirt 會：
1. 以 Instancetype 的值（4 vCPU）為準
2. 在 admission webhook 階段**拒絕**該 VM 建立（若兩者有明確衝突）

:::danger 常見錯誤
```yaml
# 錯誤示範：使用 instancetype 後還指定 CPU/Memory
spec:
  instancetype:
    name: medium
  template:
    spec:
      domain:
        cpu:          # ❌ 會被 admission webhook 拒絕
          cores: 2
        resources:    # ❌ 同樣會被拒絕
          requests:
            memory: 4Gi
```
:::

### Preference 與 VM spec 的衝突

Preference 定義的是**偏好設定**，屬於**建議性**設定：

```
衝突規則：VM spec 的設定 > Preference 的設定（VM spec 優先）
```

例如，Preference 建議 `preferredDiskBus: virtio`，但 VM spec 明確指定 `disk.bus: sata`，則會使用 `sata`。

```yaml
# 這是合法的：VM spec 可以覆蓋 Preference 的建議
spec:
  preference:
    name: ubuntu
  template:
    spec:
      domain:
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: sata  # ✅ 覆蓋 preference 的 virtio 建議
```

---

## 完整 YAML 範例

### 定義 VirtualMachineClusterInstancetype

```yaml
# small - 2 vCPU, 4 GiB
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: small
  annotations:
    description: "2 vCPU, 4 GiB RAM - 適合輕量應用"
spec:
  cpu:
    guest: 2
  memory:
    guest: 4Gi
---
# medium - 4 vCPU, 8 GiB
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: medium
  annotations:
    description: "4 vCPU, 8 GiB RAM - 適合一般應用"
spec:
  cpu:
    guest: 4
  memory:
    guest: 8Gi
---
# large - 8 vCPU, 16 GiB, HugePages
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: large
  annotations:
    description: "8 vCPU, 16 GiB RAM, 1Gi HugePages - 適合資料庫"
spec:
  cpu:
    guest: 8
    dedicatedCpuPlacement: true
  memory:
    guest: 16Gi
    hugepages:
      pageSize: "1Gi"
  ioThreadsPolicy: "auto"
---
# gpu-medium - 4 vCPU, 16 GiB + GPU
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterInstancetype
metadata:
  name: gpu-medium
  annotations:
    description: "4 vCPU, 16 GiB RAM + NVIDIA GPU"
spec:
  cpu:
    guest: 4
  memory:
    guest: 16Gi
  gpus:
    - name: gpu0
      deviceName: "nvidia.com/GA102GL_A10"
```

### 定義 VirtualMachineClusterPreference

```yaml
# ubuntu - Ubuntu 最佳化設定
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterPreference
metadata:
  name: ubuntu
  annotations:
    description: "Ubuntu Linux 最佳化設定（virtio 驅動）"
spec:
  cpu:
    preferredCPUTopology: Cores
  devices:
    preferredDiskBus: virtio
    preferredInterfaceModel: virtio
    preferredInputBus: usb
    preferredInputType: tablet
  features:
    preferredAcpi: {}
    preferredApic:
      enabled: true
  firmware:
    preferredUseEfi: true
    preferredUseSecureBoot: false
  machine:
    preferredMachineType: "q35"
  clock:
    preferredClockOffset:
      utc: {}
    preferredTimer:
      kvmclock:
        present: true
---
# centos - CentOS/RHEL 設定
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterPreference
metadata:
  name: centos
  annotations:
    description: "CentOS/RHEL 最佳化設定"
spec:
  cpu:
    preferredCPUTopology: Sockets
  devices:
    preferredDiskBus: virtio
    preferredInterfaceModel: virtio
    preferredInputBus: usb
    preferredInputType: tablet
  firmware:
    preferredUseEfi: true
  machine:
    preferredMachineType: "q35"
  clock:
    preferredClockOffset:
      utc: {}
---
# windows - Windows Server/Desktop 設定
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterPreference
metadata:
  name: windows
  annotations:
    description: "Windows Server 最佳化設定（含 TPM + Secure Boot）"
spec:
  cpu:
    preferredCPUTopology: Sockets
  devices:
    preferredDiskBus: sata           # Windows 原生支援 SATA
    preferredInterfaceModel: e1000e  # Windows 原生支援 e1000e
    preferredInputBus: usb
    preferredInputType: tablet
    preferredTPM:
      persistent: true               # Windows 11 需要 TPM
    preferredAutoattachGraphicsDevice: true
  features:
    preferredAcpi: {}
    preferredApic:
      enabled: true
    preferredHyperv:
      relaxed:
        enabled: true
      vapic:
        enabled: true
      spinlocks:
        enabled: true
        retries: 8191
      synic:
        enabled: true
      synictimer:
        enabled: true
  firmware:
    preferredUseEfi: true
    preferredUseSecureBoot: true     # Windows 11 需要
  machine:
    preferredMachineType: "q35"
  clock:
    preferredClockOffset:
      timezone: "Local"             # Windows 偏好本地時間
    preferredTimer:
      hyperv: {}
      pit:
        tickPolicy: delay
      rtc:
        tickPolicy: catchup
```

### VM 引用 Instancetype 和 Preference 的完整範例

```yaml
# ubuntu-vm.yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: ubuntu-web-server
  namespace: production
  labels:
    app: web-server
    os: ubuntu
spec:
  instancetype:
    kind: VirtualMachineClusterInstancetype
    name: medium
  preference:
    kind: VirtualMachineClusterPreference
    name: ubuntu
  runStrategy: Always
  template:
    metadata:
      labels:
        kubevirt.io/vm: ubuntu-web-server
    spec:
      domain:
        devices:
          disks:
            - name: rootdisk
              disk: {}       # bus 由 preference (virtio) 決定
            - name: cloudinit
              disk: {}
          interfaces:
            - name: default
              masquerade: {}  # model 由 preference (virtio) 決定
        # 不需要指定 CPU 和 Memory，由 instancetype 決定
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: ubuntu-22-04-rootdisk
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              users:
                - name: admin
                  sudo: ALL=(ALL) NOPASSWD:ALL
                  ssh_authorized_keys:
                    - ssh-ed25519 AAAA...
  dataVolumeTemplates:
    - metadata:
        name: ubuntu-22-04-rootdisk
      spec:
        source:
          registry:
            url: "docker://quay.io/containerdisks/ubuntu:22.04"
        storage:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 30Gi
---
# windows-vm.yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: windows-server-2022
  namespace: production
spec:
  instancetype:
    kind: VirtualMachineClusterInstancetype
    name: large
  preference:
    kind: VirtualMachineClusterPreference
    name: windows
  runStrategy: Always
  template:
    spec:
      domain:
        devices:
          disks:
            - name: rootdisk
              disk: {}    # bus 由 preference (sata) 決定
          interfaces:
            - name: default
              masquerade: {}
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: windows-2022-rootdisk
  dataVolumeTemplates:
    - metadata:
        name: windows-2022-rootdisk
      spec:
        source:
          http:
            url: "http://storage.example.com/windows-server-2022.iso"
        storage:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 60Gi
```

### 使用 inferFromVolume 自動推斷範例

```yaml
# 先建立帶有標籤的 DataVolume
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: ubuntu-golden-image
  namespace: production
  labels:
    instancetype.kubevirt.io/default-instancetype: "medium"
    instancetype.kubevirt.io/default-instancetype-kind: "VirtualMachineClusterInstancetype"
    instancetype.kubevirt.io/default-preference: "ubuntu"
    instancetype.kubevirt.io/default-preference-kind: "VirtualMachineClusterPreference"
spec:
  source:
    registry:
      url: "docker://quay.io/containerdisks/ubuntu:22.04"
  storage:
    resources:
      requests:
        storage: 30Gi
---
# VM 使用 inferFromVolume 自動推斷
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: auto-infer-vm
  namespace: production
spec:
  instancetype:
    inferFromVolume: rootdisk
    inferFromVolumeFailurePolicy: Reject

  preference:
    inferFromVolume: rootdisk
    inferFromVolumeFailurePolicy: Reject

  runStrategy: Always
  template:
    spec:
      domain:
        devices:
          disks:
            - name: rootdisk
              disk: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: ubuntu-golden-image
```

---

## virtctl 指令

### 建立 Instancetype

```bash
# 使用 virtctl 建立 instancetype
virtctl create instancetype \
  --name small-custom \
  --cpu 2 \
  --memory 4Gi

# 建立 cluster-scoped instancetype
virtctl create instancetype \
  --name large-dedicated \
  --cpu 8 \
  --memory 32Gi \
  --namespace-scoped=false

# 輸出 YAML 而不直接套用
virtctl create instancetype \
  --name medium-preview \
  --cpu 4 \
  --memory 8Gi \
  --dry-run

# 套用到叢集
virtctl create instancetype \
  --name production-medium \
  --cpu 4 \
  --memory 8Gi | kubectl apply -f -
```

### 建立 Preference

```bash
# 建立 preference
virtctl create preference \
  --name custom-linux \
  --volume-storage-class fast-ssd

# 建立 cluster-scoped preference
virtctl create preference \
  --name cluster-windows \
  --namespace-scoped=false
```

### 查詢已有的 Instancetype / Preference

```bash
# 列出所有 cluster instancetype
kubectl get virtualmachineclusterinstancetype

# 列出特定 namespace 的 instancetype
kubectl get virtualmachineinstancetype -n production

# 查看 instancetype 詳細資訊
kubectl describe virtualmachineclusterinstancetype medium

# 列出所有 cluster preference
kubectl get virtualmachineclusterpreference

# 查看 preference 詳細資訊
kubectl describe virtualmachineclusterpreference ubuntu

# 查看 VM 使用的 ControllerRevision（版本快照）
kubectl get controllerrevision -n production -l kubevirt.io/vm=ubuntu-web-server

# 查看 VM 目前引用的 instancetype/preference 版本
kubectl get vm ubuntu-web-server -n production \
  -o jsonpath='{.spec.instancetype}{"\n"}{.spec.preference}'
```

:::tip 查看社群預設 Instancetype
KubeVirt 社群提供了一組預設的 Instancetype 和 Preference，常見命名慣例：

```bash
kubectl get virtualmachineclusterinstancetype

# 社群 instancetype 命名慣例：
# u1.micro    - 1 vCPU, 0.5 GiB（超輕量）
# u1.small    - 1 vCPU, 2 GiB
# u1.medium   - 1 vCPU, 4 GiB
# u1.large    - 2 vCPU, 8 GiB
# cx1.small   - 1 vCPU, 2 GiB（計算最佳化）
# cx1.medium  - 2 vCPU, 4 GiB
# cx1.large   - 4 vCPU, 8 GiB
# cx1.xlarge  - 8 vCPU, 16 GiB
# cx1.2xlarge - 16 vCPU, 32 GiB
```
:::
