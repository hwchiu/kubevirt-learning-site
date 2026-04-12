---
layout: doc
title: KubeVirt — VM 初始化深入分析
---

# VM 初始化深入分析

::: info 本章導讀
本章深入剖析 KubeVirt 虛擬機（VM）從建立到啟動的完整初始化流程。涵蓋：VMI Spec 到 libvirt Domain XML 的轉換管線、ContainerDisk / PVC / CloudInit / Sysprep 四種磁碟初始化方式、韌體設定（BIOS/EFI）、`preStartHook` 的執行邏輯，以及 Boot Order 配置。本章以原始碼為主要依據，並輔以時序圖與設定範例，幫助讀者建立對 KubeVirt 啟動流程的完整心智模型。
:::

::: info 相關章節
- [virt-controller 元件分析](/kubevirt/components/virt-controller)
- [virt-handler 元件分析](/kubevirt/components/virt-handler)
- [virt-launcher 元件分析](/kubevirt/components/virt-launcher)
- [ContainerDisk 儲存](/kubevirt/storage/container-disk)
- [PVC 與 DataVolume](/kubevirt/storage/pvc-datavolume)
- [QEMU/KVM 虛擬化核心](/kubevirt/deep-dive/qemu-kvm)
:::

---

## 1. 初始化流程總覽

KubeVirt 的 VM 啟動涉及多個元件的協作。整體可分為三個階段：**控制平面建立資源**、**排程與 Pod 啟動**、**virt-launcher 內部初始化**。

![VM 初始化完整流程](/diagrams/kubevirt/kubevirt-vm-init-1.png)

### 關鍵原始碼位置

| 功能 | 原始碼路徑 |
|------|-----------|
| VM → VMI 建立 | `pkg/virt-controller/watch/vm/vm.go` |
| VMI → Pod 建立 | `pkg/virt-controller/watch/vmi/vmi.go` |
| virt-handler SyncVMI | `pkg/virt-handler/vm.go` |
| virt-launcher 主迴圈 | `pkg/virt-launcher/virtwrap/manager.go` |
| VMI → Domain 轉換 | `pkg/virt-launcher/virtwrap/converter/converter.go` |
| preStartHook | `pkg/virt-launcher/virtwrap/manager.go` (約 754 行) |

---

## 2. VMI Spec 到 QEMU Domain 的轉換

### 2.1 轉換管線架構

當 virt-launcher 收到 `SyncVMI` 指令後，核心工作是將 Kubernetes 原生的 `VirtualMachineInstance` Spec 轉換為 libvirt 能讀懂的 Domain XML。這個過程由 `converter.go` 中的兩個主要函式驅動：

```
pkg/virt-launcher/virtwrap/converter/converter.go
```

![VMI Spec 轉換流程](/diagrams/kubevirt/kubevirt-vm-init-2.png)

### 2.2 generateConverterContext() 詳解

`generateConverterContext()` 的職責是蒐集所有 **執行時期** 才能得知的資訊，並封裝進 `ConverterContext` 結構體：

```go
// pkg/virt-launcher/virtwrap/converter/converter.go
type ConverterContext struct {
    Architecture          string
    AllowEmulation        bool
    Secrets               map[string]*k8sv1.Secret
    VirtualMachine        *v1.VirtualMachineInstance
    CPUSet                []int              // 綁定的 CPU 核心
    IsBlockPVC            map[string]bool    // PVC 是否為 block 模式
    IsBlockDV             map[string]bool    // DataVolume 是否為 block 模式
    DiskReadyByName       map[string]bool
    SMBios                *cmdv1.SMBios
    SRIOVDevices          []api.HostDevice   // SR-IOV 直通設備
    GpuDevices            []api.HostDevice   // GPU 直通設備
    GenericHostDevices    []api.HostDevice
    USBHostDevices        []api.HostDevice
    EFIConfiguration      *EFIConfiguration  // EFI/OVMF 設定
    OVMFPath              string
    UseVirtioTransitional bool               // 相容舊版 virtio
    NodeTopology          *v1.Topology       // NUMA 拓撲
    MemBalloonStatsPeriod uint
    SerialConsoleLog      bool
    DomainAttachmentByInterfaceName map[string]string
}
```

關鍵的 `IsBlockPVC` / `IsBlockDV` 欄位決定了磁碟是否以 **block device** 模式直接掛載（效能較高），而非透過檔案系統掛載。這個資訊只有在 Pod 啟動後、實際掛載 PVC 後才能確認。

### 2.3 Convert() 子轉換器

`Convert()` 函式本身約 1000 行，它呼叫一系列子轉換函式，每個子轉換器負責一個設備類型：

![Convert() 函式結構](/diagrams/kubevirt/kubevirt-vm-init-3.png)

### 2.4 磁碟 Bus 類型與裝置命名

VMI Spec 中的 `disk.disk.bus` 直接影響 QEMU 內部的磁碟命名規則與效能特性：

| Bus 類型 | QEMU 裝置類型 | Linux 裝置名稱 | 特點 |
|---------|-------------|--------------|------|
| `virtio` | virtio-blk / virtio-scsi | `/dev/vdX` | 最佳效能，推薦用於 Linux |
| `sata` | ahci (SATA) | `/dev/sdX` | 相容性佳，適合 Windows |
| `scsi` | virtio-scsi | `/dev/sdX` | 支援熱插拔 |
| `usb` | usb-storage | `/dev/sdX` | 低效能，用於 Live CD |

### 2.5 BootOrder 對應

VMI Spec 中每個磁碟或網路介面都可以設定 `bootOrder`，這個值會直接被轉換成 libvirt Domain XML 中對應 `<boot order="N"/>` 元素：

```yaml
# VMI Spec
spec:
  domain:
    devices:
      disks:
        - name: rootdisk
          bootOrder: 1          # ← 第一優先開機
          disk:
            bus: virtio
        - name: cdrom
          bootOrder: 2          # ← 第二優先
          cdrom:
            bus: sata
      interfaces:
        - name: default
          bootOrder: 3          # ← 網路 PXE 第三優先
```

對應產生的 Domain XML 片段：

```xml
<disk type="file" device="disk">
  <driver name="qemu" type="qcow2"/>
  <source file="/var/run/kubevirt-private/vmi-disks/rootdisk/disk.img"/>
  <target dev="vda" bus="virtio"/>
  <boot order="1"/>             <!-- ← BootOrder 轉換結果 -->
</disk>
```

---

## 3. VM 初始化方式 — 磁碟與映像來源

KubeVirt 支援四種主要的磁碟初始化方式，適用於不同場景：

![VM 磁碟來源分類](/diagrams/kubevirt/kubevirt-vm-init-4.png)

### 3.1 ContainerDisk

ContainerDisk 讓 VM 磁碟映像以 **OCI 容器映像** 形式分發，結合 Kubernetes 的映像拉取機制。

#### 運作原理

![ContainerDisk 初始化序列](/diagrams/kubevirt/kubevirt-vm-init-5.png)

#### 支援的映像格式

| 格式 | 副檔名 | 說明 |
|------|--------|------|
| QCOW2 | `.qcow2` | 支援快照、壓縮、寫時複製 |
| RAW | `.img`, `.raw` | 效能最佳，無額外負擔 |

#### VMI 設定範例

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
metadata:
  name: fedora-vm
spec:
  domain:
    devices:
      disks:
        - name: containerdisk
          bootOrder: 1
          disk:
            bus: virtio
  volumes:
    - name: containerdisk
      containerDisk:
        image: quay.io/kubevirt/fedora-cloud-container-disk-demo:latest
        imagePullPolicy: IfNotPresent
```

#### 適用場景

- **無狀態 VM**：每次重啟都從乾淨映像開始
- **快速測試環境**：利用 OCI Registry 的 CDN 加速分發
- **CI/CD 流水線**：測試後銷毀，不需要儲存資源

::: warning 注意
ContainerDisk 是 **唯讀** 的底層映像。VM 寫入的資料存在 QEMU 的 copy-on-write 層，重啟後會遺失。若需持久化，請搭配 DataVolume。
:::

---

### 3.2 PVC / DataVolume

PersistentVolumeClaim (PVC) 提供持久化的磁碟儲存，DataVolume 則在此基礎上增加了映像匯入的自動化能力。

#### PVC 直接掛載

最簡單的方式是直接引用已存在的 PVC：

```yaml
volumes:
  - name: rootdisk
    persistentVolumeClaim:
      claimName: my-vm-disk     # 已存在的 PVC
```

#### DataVolume 自動匯入

DataVolume 是 CDI（Containerized Data Importer）提供的 CRD，能從多種來源自動下載並匯入磁碟映像：

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: fedora-dv
spec:
  source:
    http:
      url: "https://download.fedoraproject.org/pub/fedora/linux/releases/39/Cloud/x86_64/images/Fedora-Cloud-Base-39-1.5.x86_64.qcow2"
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 10Gi
    storageClassName: standard
```

#### DataVolumeTemplates — VM 內嵌自動建立

在 `VM` 資源（非 VMI）中，可透過 `dataVolumeTemplates` 讓 virt-controller 自動建立並管理 DataVolume 的生命週期：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: fedora-persistent
spec:
  dataVolumeTemplates:
    - metadata:
        name: fedora-dv
      spec:
        source:
          http:
            url: "https://example.com/fedora.qcow2"
        pvc:
          accessModes: [ReadWriteOnce]
          resources:
            requests:
              storage: 15Gi
  template:
    spec:
      volumes:
        - name: rootdisk
          dataVolume:
            name: fedora-dv    # 引用上面的 DataVolume
      domain:
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
```

#### Block 模式 vs Filesystem 模式

PVC 的存取模式直接影響 virt-launcher 的磁碟掛載方式：

| 模式 | PVC volumeMode | QEMU 驅動 | 優點 |
|------|----------------|-----------|------|
| **Filesystem** | `Filesystem` | `file` driver | 相容性高，支援動態調整大小 |
| **Block** | `Block` | `block` driver | 效能較高，減少 I/O 層次 |

virt-launcher 在 `generateConverterContext()` 中透過偵測 `/dev/` 路徑來判斷是否為 block 模式，並設定 `IsBlockPVC[diskName] = true`。

---

### 3.3 CloudInit

CloudInit 是 Linux 虛擬機 **首次開機自動化配置** 的業界標準。KubeVirt 支援兩種 CloudInit 模式。

#### 兩種模式比較

| 模式 | 說明 | 適用情境 |
|------|------|---------|
| `cloudInitNoCloud` | 合成一個小型 ISO，磁碟標籤為 `CDROM` | 大多數 Cloud Image（Fedora, Ubuntu, Debian）|
| `cloudInitConfigDrive` | 遵循 OpenStack ConfigDrive v2 格式 | 需要 OpenStack 相容的 Guest Agent |

#### ISO 生成流程

virt-launcher 在 `preStartHook()` 中呼叫 `generateCloudInitISO()`，動態產生 CloudInit 資料磁碟：

```
pkg/virt-launcher/virtwrap/manager.go
```

![CloudInit ISO 生成流程](/diagrams/kubevirt/kubevirt-vm-init-6.png)

#### CloudInit 設定範例

```yaml
volumes:
  - name: cloudinit
    cloudInitNoCloud:
      userData: |
        #cloud-config
        hostname: my-vm
        users:
          - name: fedora
            sudo: ALL=(ALL) NOPASSWD:ALL
            ssh_authorized_keys:
              - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB...
        packages:
          - nginx
        runcmd:
          - systemctl enable --now nginx
      networkData: |
        version: 2
        ethernets:
          eth0:
            dhcp4: true
```

#### 使用 Secret 存放敏感資料

```yaml
# 先建立 Secret
apiVersion: v1
kind: Secret
metadata:
  name: my-vm-cloudinit
type: Opaque
stringData:
  userdata: |
    #cloud-config
    password: supersecret
    chpasswd: { expire: False }

# VMI 引用 Secret
volumes:
  - name: cloudinit
    cloudInitNoCloud:
      userDataSecretRef:
        name: my-vm-cloudinit
```

::: info CloudInit 磁碟在 Domain XML 中的樣子
CloudInit ISO 被掛載為一個 CDROM 裝置：
```xml
<disk type="file" device="cdrom">
  <driver name="qemu" type="raw"/>
  <source file="/var/run/kubevirt-private/vmi-disks/cloudinit/noCloud.iso"/>
  <target dev="sda" bus="sata"/>
  <readonly/>
</disk>
```
:::

---

### 3.4 Sysprep (Windows)

Sysprep 是 Windows 的系統準備工具，用於 **無人值守安裝與初始化配置**。KubeVirt 透過 ConfigMap 或 Secret 提供 Sysprep 回應檔案。

#### 運作原理

![Sysprep 自動化安裝序列](/diagrams/kubevirt/kubevirt-vm-init-7.png)

#### Sysprep 設定範例

```yaml
# 建立包含 unattend.xml 的 ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: windows-sysprep
data:
  Autounattend.xml: |
    <?xml version="1.0" encoding="utf-8"?>
    <unattend xmlns="urn:schemas-microsoft-com:unattend">
      <settings pass="windowsPE">
        <component name="Microsoft-Windows-Setup" ...>
          <UserData>
            <ProductKey>
              <WillShowUI>Never</WillShowUI>
            </ProductKey>
            <AcceptEula>true</AcceptEula>
          </UserData>
        </component>
      </settings>
      <settings pass="specialize">
        <component name="Microsoft-Windows-Shell-Setup" ...>
          <ComputerName>MyWindowsVM</ComputerName>
          <TimeZone>Taipei Standard Time</TimeZone>
        </component>
      </settings>
    </unattend>
---
# VMI 引用 Sysprep
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
metadata:
  name: windows-vm
spec:
  domain:
    devices:
      disks:
        - name: sysprep
          cdrom:
            bus: sata
  volumes:
    - name: sysprep
      sysprep:
        configMap:
          name: windows-sysprep
```

#### 原始碼轉換函式

在 `converter.go` 中，`Convert_v1_SysprepSource_To_api_Disk()` 負責將 Sysprep 來源轉換為磁碟定義：

```go
// 簡化示意
func Convert_v1_SysprepSource_To_api_Disk(name string, disk *api.Disk) {
    disk.Type = "file"
    disk.Device = "cdrom"
    disk.Driver = &api.DiskDriver{Name: "qemu", Type: "raw"}
    disk.Source = api.DiskSource{
        File: fmt.Sprintf("/var/run/kubevirt-private/sysprep/%s/Autounattend.xml", name),
    }
    disk.ReadOnly = &api.ReadOnly{}
}
```

---

## 4. 韌體初始化 (BIOS vs EFI)

### 4.1 預設 BIOS (SeaBIOS)

若 VMI Spec 未特別設定，KubeVirt 使用 **SeaBIOS** 作為預設韌體。SeaBIOS 是一個開源的 x86 BIOS 實作，相容於幾乎所有 x86 作業系統。

```xml
<!-- 預設 Domain XML 韌體設定 -->
<os>
  <type arch="x86_64" machine="q35">hvm</type>
  <boot dev="hd"/>
</os>
```

### 4.2 UEFI/EFI (OVMF)

啟用 UEFI 需要 OVMF（Open Virtual Machine Firmware）韌體，透過 `spec.domain.firmware.bootloader.efi` 設定：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
metadata:
  name: uefi-vm
spec:
  domain:
    firmware:
      bootloader:
        efi:
          secureBoot: false     # 是否啟用 Secure Boot
    features:
      acpi: {}
      smm:
        enabled: true           # Secure Boot 需要啟用 SMM
    devices:
      disks:
        - name: rootdisk
          disk:
            bus: virtio
  volumes:
    - name: rootdisk
      containerDisk:
        image: quay.io/kubevirt/fedora-cloud-container-disk-demo:latest
```

對應的 Domain XML：

```xml
<os firmware="efi">
  <type arch="x86_64" machine="q35">hvm</type>
  <loader readonly="yes" secure="no" type="pflash">
    /usr/share/OVMF/OVMF_CODE.fd
  </loader>
  <nvram template="/usr/share/OVMF/OVMF_VARS.fd">
    /var/run/kubevirt-private/libvirt/qemu/nvram/fedora-vm_VARS.fd
  </nvram>
</os>
```

### 4.3 Secure Boot

Secure Boot 防止未簽名的開機程式被執行，需要啟用 `smm`（System Management Mode）：

```yaml
spec:
  domain:
    firmware:
      bootloader:
        efi:
          secureBoot: true      # 啟用 Secure Boot
    features:
      acpi: {}
      smm:
        enabled: true           # 必須啟用
```

::: warning 相容性注意事項
Secure Boot 啟用後，只有具備有效簽名的 OS（如 RHEL、Windows）才能開機。若使用自訂核心或未簽名的映像，需停用 Secure Boot。
:::

### 4.4 vTPM 整合

KubeVirt 支援 vTPM（Virtual Trusted Platform Module），可與 EFI 搭配使用：

```yaml
spec:
  domain:
    firmware:
      bootloader:
        efi:
          secureBoot: true
    devices:
      tpm:
        persistent: true        # 重啟後保留 TPM 狀態
```

vTPM 的狀態資料存放在 PVC 中以實現持久化。

### 4.5 EFI 變數持久化

EFI NVRAM 變數（開機選項、Secure Boot 金鑰等）需要在重啟後保留。KubeVirt 透過以下方式實現：

![EFI NVRAM 管理架構](/diagrams/kubevirt/kubevirt-vm-init-8.png)

::: info EFI 磁碟架構
在 KubeVirt 中，每個 EFI VM 都有一份獨立的 NVRAM 副本。此副本在 VM 生命週期內持久存在，確保 EFI 開機設定（如 Windows BitLocker 金鑰）不會因重啟而遺失。
:::

### 4.6 韌體設定對照表

| 設定 | BIOS (SeaBIOS) | EFI (OVMF) | EFI + Secure Boot |
|------|---------------|------------|-------------------|
| 相容性 | 最廣 | 廣 | 有限（需簽名） |
| Windows 11 | ❌ | ✅ | ✅（建議） |
| TPM 支援 | ❌ | ✅ | ✅ |
| 開機速度 | 快 | 稍慢 | 稍慢 |
| SMM 要求 | 否 | 否 | **是** |

---

## 5. preStartHook 執行流程

`preStartHook()` 是 virt-launcher 在 libvirt 定義 Domain **之前** 執行的準備函式，確保所有必要資源就緒。

### 5.1 執行位置與時機

```
pkg/virt-launcher/virtwrap/manager.go (約第 754 行)
func (l *LibvirtDomainManager) preStartHook(vmi *v1.VirtualMachineInstance, ...) error
```

![preStartHook 執行位置與時機](/diagrams/kubevirt/kubevirt-vm-init-9.png)

### 5.2 各步驟詳解

#### 步驟 1–2：CloudInit ISO 生成

```go
// manager.go 簡化示意
if cloudinit.HasCloudInitVolume(vmi) {
    cloudInitData, err := cloudinit.ResolveNoCloudData(vmi)
    if err != nil { return err }
    err = cloudinit.GenerateLocalData(vmi.Name, vmi.Namespace, cloudInitData)
    // 產生 /var/run/kubevirt-private/vmi-disks/<vol>/noCloud.iso
}
```

`cloudinit.GenerateLocalData()` 內部使用 `genisoimage` 或 `mkisofs` 命令產生 ISO 9660 格式的磁碟映像，並設定磁碟 label 為 `cidata`（NoCloud 標準）。

#### 步驟 3：Hook Sidecar 呼叫

Hook Sidecar 是 KubeVirt 的插件機制，允許外部容器在 VM 啟動前攔截並修改 Domain XML：

![Hook Sidecar 呼叫序列](/diagrams/kubevirt/kubevirt-hook-sidecar-arch.png)

#### 步驟 4：磁碟映像展開

QCOW2 格式的磁碟可能以 **稀疏格式（sparse）** 存在，實際佔用空間小於宣稱大小。`expandDiskImagesOffline()` 確保磁碟在 VM 啟動前達到指定大小：

```go
// 展開磁碟至目標大小
err = qemuImg.Resize(diskPath, targetSize)
```

---

## 6. Boot Order 配置

### 6.1 多設備 Boot Order 配置

可以為磁碟、CDROM、網路介面分別設定 `bootOrder`，值越小優先級越高：

```yaml
spec:
  domain:
    devices:
      disks:
        - name: rootdisk
          bootOrder: 2          # 第二優先：硬碟
          disk:
            bus: virtio
        - name: rescue-cd
          bootOrder: 1          # 第一優先：救援 CD
          cdrom:
            bus: sata
      interfaces:
        - name: default
          bootOrder: 3          # 第三優先：PXE 網路開機
          masquerade: {}
  networks:
    - name: default
      pod: {}
  volumes:
    - name: rootdisk
      persistentVolumeClaim:
        claimName: my-disk
    - name: rescue-cd
      containerDisk:
        image: quay.io/kubevirt/fedora-cloud-container-disk-demo:latest
```

### 6.2 BIOS 與 EFI 的 Boot Order 差異

| 項目 | BIOS 模式 | EFI 模式 |
|------|----------|---------|
| Boot Order 設定方式 | libvirt `<boot order="N"/>` | EFI Boot Manager 條目 |
| PXE 支援 | ✅ | ✅（需 iPXE 韌體） |
| 動態修改 | 需重啟 VM | 可透過 efibootmgr 熱修改 |
| 設定持久化 | N/A | 存於 NVRAM（OVMF_VARS.fd）|

### 6.3 PXE 網路開機設定

若需要 PXE 開機（例如：裸機映像部署、無磁碟 VM），將網路介面設為第一開機：

```yaml
spec:
  domain:
    devices:
      interfaces:
        - name: pxe-net
          bootOrder: 1          # PXE 第一優先
          bridge: {}
  networks:
    - name: pxe-net
      multus:
        networkName: pxe-network
```

生成的 Domain XML 會在 `<interface>` 元素內加入 `<boot order="1"/>`：

```xml
<interface type="bridge">
  <source bridge="k6t-eth0"/>
  <model type="virtio"/>
  <boot order="1"/>             <!-- PXE 第一開機 -->
</interface>
```

---

## 7. 初始化時序圖

以下時序圖展示從使用者建立 `VM` 資源到 VMI 狀態轉換為 `Running` 的完整流程，含各元件的互動與 VMI 狀態機轉換：

![VM 初始化時序圖](/diagrams/kubevirt/kubevirt-vm-init-1.png)

### VMI 狀態機轉換

![VMI 狀態機轉換](/diagrams/kubevirt/kubevirt-vmi-states.png)

### 狀態轉換觸發條件

| 狀態轉換 | 觸發元件 | 觸發條件 |
|---------|---------|---------|
| `Pending` → `Scheduling` | virt-controller | virt-launcher Pod 建立後 |
| `Scheduling` → `Scheduled` | virt-controller | Pod 被 kube-scheduler 排程 |
| `Scheduled` → `Running` | virt-handler | virt-launcher 回報 QEMU 啟動成功 |
| `Running` → `Succeeded` | virt-handler | libvirt 回報 Domain shutoff（正常） |
| `Running` → `Failed` | virt-handler | libvirt 回報 Domain crashed |
| `Running` → `Migrating` | virt-controller | VirtualMachineInstanceMigration 建立 |

---

## 8. 常見問題排查

### 8.1 VM 卡在 Scheduling 狀態

排查 virt-launcher Pod 是否能被排程：

```bash
# 查看 VMI 狀態
kubectl get vmi my-vm -o yaml | grep -A 10 status

# 查看 virt-launcher Pod 事件
kubectl describe pod virt-launcher-my-vm-xxxxx

# 常見原因：
# - 節點資源不足（CPU / 記憶體）
# - nodeSelector / tolerations 不符
# - ContainerDisk 映像拉取失敗
```

### 8.2 CloudInit 未執行

```bash
# 進入 VM 查看 cloud-init 日誌
virtctl console my-vm
# 在 VM 內執行：
sudo journalctl -u cloud-init
sudo cloud-init status --long

# 確認 ISO 是否正確掛載
sudo blkid | grep cidata
```

### 8.3 EFI 開機失敗

```bash
# 確認 OVMF 韌體是否安裝在節點上
ls /usr/share/OVMF/

# 查看 virt-launcher 日誌
kubectl logs virt-launcher-my-vm-xxxxx -c compute

# 確認 SMM 是否啟用（Secure Boot 必需）
kubectl get vmi my-vm -o jsonpath='{.spec.domain.features}'
```

### 8.4 磁碟轉換失敗

```bash
# 查看 converter 相關日誌
kubectl logs virt-launcher-my-vm-xxxxx -c compute | grep -i "converter\|domain\|disk"

# 確認 PVC 狀態
kubectl get pvc my-pvc -o yaml | grep -A 5 status
```

---

## 9. 小結

KubeVirt 的 VM 初始化流程展現了 **將 VM 管理雲原生化** 的設計思想：

| 設計決策 | 效益 |
|---------|------|
| VMI Spec → Domain XML 的宣告式轉換 | 版本控制、GitOps 友善 |
| ContainerDisk 利用 OCI 生態系 | 映像分發、快取、版本管理 |
| DataVolume 自動匯入 | 降低儲存管理複雜度 |
| CloudInit 標準化 | 與現有 Linux 映像生態相容 |
| preStartHook 擴展點 | 允許自定義插件介入初始化 |
| EFI/vTPM 支援 | 滿足 Windows 11、Secure Boot 需求 |

理解這個轉換管線對於：

- **效能調校**：選擇正確的磁碟 bus 類型和 block/filesystem 模式
- **故障排查**：快速定位是控制平面、排程、還是 libvirt 層面的問題
- **自定義開發**：撰寫 Hook Sidecar 在初始化時注入自定義設備

都有重要的指導意義。
