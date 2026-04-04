# QEMU/KVM 深入剖析 — KubeVirt 如何管理虛擬機

本文深入解析 KubeVirt 如何透過 libvirt 操作 QEMU/KVM，從 VMI 規格轉換到 Domain XML 產生，再到虛擬機的完整生命週期管理。

## 架構概述

### 三層架構

KubeVirt 採用三層架構來管理虛擬機：

```
┌─────────────────────────────────────────────────┐
│                 Kubernetes API                    │
│       VirtualMachineInstance (VMI) Spec           │
└──────────────────┬──────────────────────────────┘
                   │ Convert_v1_VirtualMachineInstance_To_api_Domain()
                   ▼
┌─────────────────────────────────────────────────┐
│           Converter (Configurator 模式)           │
│   CPU / Memory / Network / Disk / HyperV / ...    │
└──────────────────┬──────────────────────────────┘
                   │ DomainDefineXML()
                   ▼
┌─────────────────────────────────────────────────┐
│         libvirt Domain XML → QEMU/KVM             │
│    libvirtd 解析 XML 並啟動 qemu-system-x86_64    │
└─────────────────────────────────────────────────┘
```

### virt-launcher Pod 內部結構

每個 VMI 都在獨立的 Pod 中運行，Pod 內部有三個關鍵程序：

```
┌──────────────────── virt-launcher Pod ────────────────────┐
│                                                            │
│  ┌──────────────┐    gRPC     ┌─────────────────────┐     │
│  │ virt-handler │◄──────────►│ virt-launcher (Go)    │     │
│  │  (DaemonSet) │            │  - CMD Server         │     │
│  └──────────────┘            │  - Domain Notifier    │     │
│                              │  - Agent Poller       │     │
│                              └──────┬────────────────┘     │
│                                     │ libvirt API          │
│                              ┌──────▼────────────────┐     │
│                              │ libvirtd / virtqemud   │     │
│                              │  - Domain XML 管理     │     │
│                              │  - 事件處理            │     │
│                              └──────┬────────────────┘     │
│                                     │ fork + exec          │
│                              ┌──────▼────────────────┐     │
│                              │ qemu-system-x86_64     │     │
│                              │  - 虛擬機實際執行      │     │
│                              │  - Guest Agent 通訊    │     │
│                              └────────────────────────┘     │
└────────────────────────────────────────────────────────────┘
```

::: info 為什麼選用 libvirt？
KubeVirt 選用 libvirt 而非直接操作 QEMU 的原因：
1. **穩定的 API**：libvirt 提供版本穩定的 C/Go binding，避免直接依賴 QEMU 命令列參數的變化
2. **安全性**：libvirt 以 daemon 方式運行，提供權限隔離與 SELinux/AppArmor 整合
3. **事件系統**：內建完整的生命週期事件回調機制
4. **設備熱插拔**：提供標準化的 `AttachDevice` / `DetachDevice` API
5. **遷移支援**：libvirt 原生支援 Live Migration 協議
:::

## VMI → Domain XML 轉換

### Configurator 模式化設計

KubeVirt 的轉換架構基於 **Configurator 模式**，每個元件實作統一的介面：

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/types/builder.go
type Configurator interface {
    Configure(vmi *v1.VirtualMachineInstance, domain *api.Domain) error
}
```

### 主要轉換函式

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/converter.go
func Convert_v1_VirtualMachineInstance_To_api_Domain(
    vmi *v1.VirtualMachineInstance,
    domain *api.Domain,
    c *ConverterContext,
) error {
    // 建立 DomainBuilder，註冊所有 Configurator
    builder := convertertypes.NewDomainBuilder()
    
    // 註冊 27+ 個 Configurator
    builder.Add(compute.NewCPUDomainConfigurator(...))
    builder.Add(compute.MemoryConfigurator{})
    builder.Add(compute.NewOSDomainConfigurator(...))
    builder.Add(compute.ClockDomainConfigurator{})
    builder.Add(compute.NewBalloonDomainConfigurator(...))
    builder.Add(compute.ChannelsDomainConfigurator{})
    builder.Add(compute.NewQemuCmdDomainConfigurator(...))
    builder.Add(compute.TPMDomainConfigurator{})
    builder.Add(compute.KvmDomainConfigurator{})
    builder.Add(network.NewDomainConfigurator(...))
    builder.Add(compute.NewSysInfoDomainConfigurator(...))
    // ... 更多 Configurator
    
    // 依序執行所有 Configurator
    return builder.Build(vmi, domain)
}
```

### 每個 Configurator 的職責

| Configurator | 檔案位置 | 職責 |
|---|---|---|
| `CPUDomainConfigurator` | `converter/compute/cpu.go` | CPU 模式、拓撲、Feature、熱插拔 |
| `MemoryConfigurator` | `converter/compute/memory.go` | 記憶體大小、MaxGuest、熱插拔 |
| `OSDomainConfigurator` | `converter/compute/os.go` | Machine type、EFI/BIOS、Boot 順序 |
| `ClockDomainConfigurator` | `converter/compute/clock.go` | 時鐘偏移、計時器（RTC/PIT/HPET/KVM/HyperV） |
| `BalloonDomainConfigurator` | `converter/compute/balloon.go` | Memory balloon、Free page reporting |
| `ChannelsDomainConfigurator` | `converter/compute/channels.go` | Guest Agent virtio-serial channel |
| `QemuCmdDomainConfigurator` | `converter/compute/qemu_cmd.go` | 自定義 QEMU 參數（Ignition、debug log） |
| `TPMDomainConfigurator` | `converter/compute/tpm.go` | TPM 2.0 模擬（tpm-tis / tpm-crb） |
| `KvmDomainConfigurator` | `converter/compute/kvm.go` | KVM 特定功能（hidden state） |
| `NetworkConfigurator` | `converter/network/` | 網路介面（bridge/masquerade/passt） |
| `SysInfoDomainConfigurator` | `converter/compute/sysinfo.go` | SMBIOS 資訊（UUID、Serial、Chassis） |
| `LaunchSecurityDomainConfigurator` | `converter/compute/launch_security.go` | SEV / SEV-SNP / TDX 加密 |
| `ControllersDomainConfigurator` | `converter/compute/controllers.go` | USB / SCSI 控制器 |
| `HypervFeaturesDomainConfigurator` | `converter/compute/hypervisor_features.go` | HyperV Enlightenments |

## DomainManager 介面

### 完整介面定義

```go
// 檔案：pkg/virt-launcher/virtwrap/manager.go
type DomainManager interface {
    // 核心生命週期
    SyncVMI(*v1.VirtualMachineInstance, bool, *cmdv1.VirtualMachineOptions) (*api.DomainSpec, error)
    PauseVMI(*v1.VirtualMachineInstance) error
    UnpauseVMI(*v1.VirtualMachineInstance) error
    FreezeVMI(*v1.VirtualMachineInstance, int32) error
    UnfreezeVMI(*v1.VirtualMachineInstance) error
    ResetVMI(*v1.VirtualMachineInstance) error
    SoftRebootVMI(*v1.VirtualMachineInstance) error
    KillVMI(*v1.VirtualMachineInstance) error
    DeleteVMI(*v1.VirtualMachineInstance) error
    SignalShutdownVMI(*v1.VirtualMachineInstance) error
    MarkGracefulShutdownVMI()
    
    // 遷移
    MigrateVMI(*v1.VirtualMachineInstance, *cmdclient.MigrationOptions) error
    PrepareMigrationTarget(*v1.VirtualMachineInstance, bool, *cmdv1.VirtualMachineOptions) error
    CancelVMIMigration(*v1.VirtualMachineInstance) error
    FinalizeVirtualMachineMigration(*v1.VirtualMachineInstance, *cmdv1.VirtualMachineOptions) error
    
    // 查詢
    ListAllDomains() ([]*api.Domain, error)
    GetDomainStats() (*stats.DomainStats, error)
    GetGuestInfo() v1.VirtualMachineInstanceGuestAgentInfo
    GetUsers() []v1.VirtualMachineInstanceGuestOSUser
    GetFilesystems() []v1.VirtualMachineInstanceFileSystem
    InterfacesStatus() []api.InterfaceStatus
    GetGuestOSInfo() *api.GuestOSInfo
    GetQemuVersion() (string, error)
    
    // 設備熱插拔
    HotplugHostDevices(vmi *v1.VirtualMachineInstance) error
    UpdateVCPUs(vmi *v1.VirtualMachineInstance, options *cmdv1.VirtualMachineOptions) error
    UpdateGuestMemory(vmi *v1.VirtualMachineInstance) error
    
    // Guest Agent 操作
    Exec(string, string, []string, int32) (string, error)
    GuestPing(string) error
    
    // 備份 / 安全 / 其他
    MemoryDump(vmi *v1.VirtualMachineInstance, dumpPath string) error
    BackupVirtualMachine(*v1.VirtualMachineInstance, *backupv1.BackupOptions) error
    RedefineCheckpoint(*v1.VirtualMachineInstance, *backupv1.BackupCheckpoint) (bool, error)
    GetSEVInfo() (*v1.SEVPlatformInfo, error)
    GetLaunchMeasurement(*v1.VirtualMachineInstance) (*v1.SEVMeasurementInfo, error)
    InjectLaunchSecret(*v1.VirtualMachineInstance, *v1.SEVSecretOptions) error
    GetDomainDirtyRateStats(time.Duration) (*stats.DomainStatsDirtyRate, error)
    GetScreenshot(*v1.VirtualMachineInstance) (*cmdv1.ScreenshotResponse, error)
}
```

### SyncVMI 流程

SyncVMI 是最核心的方法，負責確保虛擬機狀態與 VMI 規格一致：

```
SyncVMI() 完整流程
═══════════════════

1. 取得 domainModifyLock（互斥鎖）
         │
2. linkImageVolumeFilePaths()（若 feature gate 啟用）
         │
3. generateConverterContext()
   → 建立轉換上下文（架構、SEV、允許模擬等）
         │
4. ApplyChangedBlockTracking()（若 CBT 啟用）
         │
5. Convert_v1_VirtualMachineInstance_To_api_Domain()
   → 27+ Configurator 依序執行
   → 產生完整 Domain XML
         │
6. SetObjectDefaults_Domain()（架構預設值）
         │
7. lookupOrCreateVirDomain()
   → 若 Domain 不存在 → DomainDefineXML()
   → 若 Domain 已存在 → 取得現有 Domain
         │
8. GetState() → 檢查虛擬機狀態
   │
   ├─ Domain 已停止 + VMI 未運行 → startDomain()
   │
   └─ Domain 已暫停 + 非使用者暫停 → Resume()
         │
9. syncDisks()：同步磁碟（熱插拔/移除）
         │
10. network.Sync()：同步網路介面
         │
11. syncGracePeriod()：同步優雅關機時間
         │
12. 回傳 DomainSpec
```

### 設備熱插拔

```go
// vCPU 熱插拔
func (l *LibvirtDomainManager) UpdateVCPUs(
    vmi *v1.VirtualMachineInstance,
    options *cmdv1.VirtualMachineOptions,
) error {
    // 透過 libvirt SetVcpusFlags() 動態調整 vCPU 數量
    // 搭配 CPU hotplug 的 MaxSockets 設定
}

// 記憶體熱插拔（virtio-mem）
func (l *LibvirtDomainManager) UpdateGuestMemory(
    vmi *v1.VirtualMachineInstance,
) error {
    // 使用 virDomainUpdateDeviceFlags 更新 virtio-mem 裝置的
    // requested 大小，實現記憶體動態調整
}
```

::: tip vCPU 熱插拔注意事項
vCPU 熱插拔需要在 VMI 建立時預先配置 `MaxSockets`。KubeVirt 使用 `hotpluggable='yes'` 標記額外的 vCPU 插槽。Guest OS 需要支援 CPU hotplug（Linux 預設支援，Windows 需要 Server 版本）。
:::

## libvirt 連線管理

### Connection 介面

```go
// 檔案：pkg/virt-launcher/virtwrap/cli/libvirt.go
type Connection interface {
    // Domain 管理
    LookupDomainByName(name string) (VirDomain, error)
    DomainDefineXML(xml string) (VirDomain, error)
    ListAllDomains(flags libvirt.ConnectListAllDomainsFlags) ([]VirDomain, error)
    Close() (int, error)
    
    // 事件註冊
    DomainEventLifecycleRegister(callback libvirt.DomainEventLifecycleCallback) error
    DomainEventDeviceAddedRegister(callback libvirt.DomainEventDeviceAddedCallback) error
    DomainEventDeviceRemovedRegister(callback libvirt.DomainEventDeviceRemovedCallback) error
    DomainEventJobCompletedRegister(callback libvirt.DomainEventJobCompletedCallback) error
    AgentEventLifecycleRegister(callback libvirt.DomainEventAgentLifecycleCallback) error
    DomainEventMemoryDeviceSizeChangeRegister(callback libvirt.DomainEventMemoryDeviceSizeChangeCallback) error
    VolatileDomainEventDeviceRemovedRegister(domain VirDomain, callback libvirt.DomainEventDeviceRemovedCallback) (int, error)
    DomainEventDeregister(registrationID int) error
    
    // Guest Agent
    QemuAgentCommand(command string, domainName string) (string, error)
    
    // 統計
    GetAllDomainStats(statsTypes libvirt.DomainStatsTypes, flags libvirt.ConnectGetAllDomainStatsFlags) ([]libvirt.DomainStats, error)
    GetDomainStats(statsTypes libvirt.DomainStatsTypes, l *stats.DomainJobInfo, flags libvirt.ConnectGetAllDomainStatsFlags) ([]*stats.DomainStats, error)
    GetDomainDirtyRate(calculationDuration time.Duration, flags libvirt.DomainDirtyRateCalcFlags) ([]*stats.DomainStatsDirtyRate, error)
    
    // 版本與安全
    GetQemuVersion() (string, error)
    GetSEVInfo() (*api.SEVNodeParameters, error)
    
    // 串流與重連
    NewStream(flags libvirt.StreamFlags) (Stream, error)
    SetReconnectChan(reconnect chan bool)
}
```

### 事件處理機制

```go
// 生命週期事件 — 虛擬機狀態變更
DomainEventLifecycleRegister(func(c *libvirt.Connect, d *libvirt.Domain,
    event *libvirt.DomainEventLifecycle))
// 事件類型：Started, Suspended, Resumed, Stopped, Shutdown, Crashed

// 設備熱插拔事件
DomainEventDeviceAddedRegister(...)   // 設備成功新增
DomainEventDeviceRemovedRegister(...) // 設備成功移除

// Guest Agent 生命週期
AgentEventLifecycleRegister(...)
// 偵測 Guest Agent 連線/斷線

// 遷移任務完成
DomainEventJobCompletedRegister(...)

// 記憶體裝置大小變更（virtio-mem）
DomainEventMemoryDeviceSizeChangeRegister(...)
```

### QEMU Guest Agent 通訊

```go
// 透過 libvirt 發送 Guest Agent 命令
result, err := conn.QemuAgentCommand(
    `{"execute":"guest-network-get-interfaces"}`,
    domainName,
)
```

常用 Guest Agent 命令：

| 命令 | 用途 |
|---|---|
| `guest-ping` | 檢測 Agent 是否運行 |
| `guest-info` | 取得 Agent 版本與支援命令列表 |
| `guest-network-get-interfaces` | 取得 Guest 網路介面資訊（IP 位址） |
| `guest-fsfreeze-freeze` | 凍結檔案系統（快照前使用） |
| `guest-fsfreeze-thaw` | 解凍檔案系統 |
| `guest-get-osinfo` | 取得 Guest OS 資訊 |
| `guest-exec` | 在 Guest 中執行命令 |
| `guest-set-user-password` | 設定 Guest 使用者密碼 |

::: warning Guest Agent 依賴
Guest Agent 功能需要在 Guest OS 中安裝 `qemu-guest-agent`。Windows VM 需要安裝 VirtIO 驅動套件中包含的 QEMU Guest Agent。若 Agent 未安裝，`GetGuestInfo()`、`GetUsers()`、`GetFilesystems()` 等方法將回傳空結果。
:::

## Domain XML 型別系統

### Go struct → XML 映射

KubeVirt 在 `pkg/virt-launcher/virtwrap/api/schema.go` 中定義了完整的 libvirt Domain XML 型別系統：

```go
// 檔案：pkg/virt-launcher/virtwrap/api/schema.go

type DomainSpec struct {
    XMLName       xml.Name     `xml:"domain"`
    Type          string       `xml:"type,attr"`
    Name          string       `xml:"name"`
    UUID          string       `xml:"uuid,omitempty"`
    Memory        Memory       `xml:"memory"`
    CurrentMemory *Memory      `xml:"currentMemory,omitempty"`
    MaxMemory     *MaxMemory   `xml:"maxMemory,omitempty"`
    MemoryBacking *MemoryBacking `xml:"memoryBacking,omitempty"`
    OS            OS           `xml:"os"`
    SysInfo       *SysInfo     `xml:"sysinfo,omitempty"`
    Clock         *Clock       `xml:"clock,omitempty"`
    CPU           CPU          `xml:"cpu"`
    CPUTune       *CPUTune     `xml:"cputune,omitempty"`
    NUMATune      *NUMATune    `xml:"numatune,omitempty"`
    Features      *Features    `xml:"features,omitempty"`
    Devices       Devices      `xml:"devices"`
    IOThreads     *IOThreads   `xml:"iothreads,omitempty"`
    LaunchSecurity *LaunchSecurity `xml:"launchSecurity,omitempty"`
    QEMUCmd       *Commandline `xml:"qemu:commandline,omitempty"`
    // ...
}

type CPU struct {
    Mode     string       `xml:"mode,attr,omitempty"`
    Model    string       `xml:"model,omitempty"`
    Features []CPUFeature `xml:"feature"`
    Topology *CPUTopology `xml:"topology"`
    NUMA     *NUMA        `xml:"numa,omitempty"`
}

type CPUTopology struct {
    Sockets uint32 `xml:"sockets,attr,omitempty"`
    Cores   uint32 `xml:"cores,attr,omitempty"`
    Threads uint32 `xml:"threads,attr,omitempty"`
}

type Devices struct {
    Emulator    string       `xml:"emulator,omitempty"`
    Interfaces  []Interface  `xml:"interface"`
    Channels    []Channel    `xml:"channel"`
    Controllers []Controller `xml:"controller,omitempty"`
    Video       []Video      `xml:"video"`
    Graphics    []Graphics   `xml:"graphics"`
    Ballooning  *MemBalloon  `xml:"memballoon,omitempty"`
    Disks       []Disk       `xml:"disk"`
    Serials     []Serial     `xml:"serial"`
    Consoles    []Console    `xml:"console"`
    Watchdog    *Watchdog    `xml:"watchdog,omitempty"`
    Rng         *Rng         `xml:"rng,omitempty"`
    Inputs      []Input      `xml:"input"`
    TPMs        []TPM        `xml:"tpm,omitempty"`
    Sound       *Sound       `xml:"sound,omitempty"`
    HostDevices []HostDevice `xml:"hostdev,omitempty"`
    Memory      []MemoryDevice `xml:"memory,omitempty"`
    // ...
}
```

### 典型 Domain XML 輸出範例

以下是一個 KubeVirt 產生的典型 Domain XML：

```xml
<domain type="kvm" xmlns:qemu="http://libvirt.org/schemas/domain/qemu/1.0">
  <name>default_my-vm</name>
  <uuid>abcdef12-3456-7890-abcd-ef1234567890</uuid>
  <memory unit="bytes">2147483648</memory>

  <os>
    <type arch="x86_64" machine="q35">hvm</type>
    <smbios mode="sysinfo"/>
  </os>

  <sysinfo type="smbios">
    <system>
      <entry name="uuid">abcdef12-3456-7890-abcd-ef1234567890</entry>
      <entry name="manufacturer">KubeVirt</entry>
      <entry name="product">None</entry>
      <entry name="family">KubeVirt</entry>
    </system>
  </sysinfo>

  <cpu mode="host-model">
    <topology sockets="1" cores="2" threads="1"/>
  </cpu>

  <clock offset="utc">
    <timer name="rtc" tickpolicy="catchup" present="yes"/>
    <timer name="pit" tickpolicy="delay" present="yes"/>
    <timer name="kvmclock" present="yes"/>
  </clock>

  <features>
    <acpi/>
    <apic/>
  </features>

  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>

    <disk type="file" device="disk">
      <driver name="qemu" type="raw" cache="none" io="native"/>
      <source file="/var/run/kubevirt-private/vmi-disks/rootdisk/disk.img"/>
      <target dev="vda" bus="virtio"/>
    </disk>

    <interface type="ethernet">
      <model type="virtio-non-transitional"/>
      <source dev="tap0"/>
      <mac address="52:54:00:12:34:56"/>
      <driver name="vhost" queues="2"/>
    </interface>

    <channel type="unix">
      <source mode="bind" path="/var/run/libvirt/qemu/channel/org.qemu.guest_agent.0"/>
      <target type="virtio" name="org.qemu.guest_agent.0"/>
    </channel>

    <memballoon model="virtio-non-transitional">
      <stats period="10"/>
    </memballoon>

    <rng model="virtio-non-transitional">
      <backend model="random">/dev/urandom</backend>
    </rng>
  </devices>
</domain>
```

## QEMU 命令列參數

### QemuCmdDomainConfigurator

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/qemu_cmd.go
type QemuCmdDomainConfigurator struct {
    verboseLogEnabled bool
}

func (q QemuCmdDomainConfigurator) Configure(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) error {
    // 1. Ignition 配置注入
    ignitiondata := vmi.Annotations[v1.IgnitionAnnotation]
    if ignitiondata != "" && strings.Contains(ignitiondata, "ignition") {
        initializeQEMUCmdAndQEMUArg(domain)
        domain.Spec.QEMUCmd.QEMUArg = append(domain.Spec.QEMUCmd.QEMUArg,
            api.Arg{Value: "-fw_cfg"},
            api.Arg{Value: fmt.Sprintf("name=opt/com.coreos/config,file=%s",
                ignitionpath)},
        )
    }

    // 2. SeaBIOS debug logging（高 verbosity 時啟用）
    if q.verboseLogEnabled {
        virtLauncherLogVerbosity, err := strconv.Atoi(
            os.Getenv(util.ENV_VAR_VIRT_LAUNCHER_LOG_VERBOSITY))
        if err == nil && virtLauncherLogVerbosity > util.EXT_LOG_VERBOSITY_THRESHOLD {
            initializeQEMUCmdAndQEMUArg(domain)
            domain.Spec.QEMUCmd.QEMUArg = append(domain.Spec.QEMUCmd.QEMUArg,
                api.Arg{Value: "-chardev"},
                api.Arg{Value: fmt.Sprintf("file,id=firmwarelog,path=%s",
                    QEMUSeaBiosDebugPipe)},
                api.Arg{Value: "-device"},
                api.Arg{Value: "isa-debugcon,iobase=0x402,chardev=firmwarelog"},
            )
        }
    }
    return nil
}
```

### 自定義 QEMU 參數的 XML 格式

```xml
<domain type="kvm" xmlns:qemu="http://libvirt.org/schemas/domain/qemu/1.0">
  <!-- ... 其他配置 ... -->
  <qemu:commandline>
    <qemu:arg value="-fw_cfg"/>
    <qemu:arg value="name=opt/com.coreos/config,file=/path/to/ignition.json"/>
    <qemu:arg value="-chardev"/>
    <qemu:arg value="file,id=firmwarelog,path=/var/log/qemu-firmware.log"/>
    <qemu:arg value="-device"/>
    <qemu:arg value="isa-debugcon,iobase=0x402,chardev=firmwarelog"/>
  </qemu:commandline>
</domain>
```

## CPU 配置深入

### CPU Model 選擇

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/cpu.go
func (c CPUDomainConfigurator) Configure(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) error {
    // host-model：使用主機 CPU 型號但允許遷移
    // host-passthrough：直接暴露主機 CPU（最佳效能，限制遷移）
    // custom：指定特定 CPU 型號
    if cpu.Model != "" {
        domain.Spec.CPU.Mode = cpu.Model
    }
}
```

| 模式 | 效能 | 遷移相容性 | 使用場景 |
|---|---|---|---|
| `host-model` | 高 | ✅ 相同 CPU 系列可遷移 | 預設推薦 |
| `host-passthrough` | 最高 | ❌ 限同型主機 | 效能敏感場景 |
| custom (如 `Skylake-Server`) | 中 | ✅ 最佳遷移相容 | 異構叢集 |

### CPU Topology

```go
type CPUTopology struct {
    Sockets uint32 `xml:"sockets,attr,omitempty"`
    Cores   uint32 `xml:"cores,attr,omitempty"`
    Threads uint32 `xml:"threads,attr,omitempty"`
}
```

::: tip 拓撲選擇策略
KubeVirt 支援 `preferCores` 和 `preferSockets` 策略：
- **preferCores**：同一 socket 內增加 core 數量（推薦用於 Windows 授權最佳化）
- **preferSockets**：增加 socket 數量（NUMA 感知應用場景）

例：8 vCPU + preferCores = 1 socket × 8 cores × 1 thread
例：8 vCPU + preferSockets = 8 sockets × 1 core × 1 thread
:::

### NUMA 拓撲配置

```go
type NUMA struct {
    Cells []NUMACell `xml:"cell"`
}

type NUMACell struct {
    ID           string `xml:"id,attr"`
    CPUs         string `xml:"cpus,attr"`
    Memory       uint64 `xml:"memory,attr,omitempty"`
    Unit         string `xml:"unit,attr,omitempty"`
    MemoryAccess string `xml:"memAccess,attr,omitempty"` // "shared" or "private"
}
```

### CPU Pinning

```go
type CPUTune struct {
    VCPUPin     []CPUTuneVCPUPin     `xml:"vcpupin"`
    IOThreadPin []CPUTuneIOThreadPin `xml:"iothreadpin,omitempty"`
    EmulatorPin *CPUEmulatorPin      `xml:"emulatorpin"`
}

type CPUTuneVCPUPin struct {
    VCPU   uint32 `xml:"vcpu,attr"`
    CPUSet string `xml:"cpuset,attr"` // 例如 "0,2,4,6"
}
```

產生的 XML：

```xml
<cputune>
  <vcpupin vcpu="0" cpuset="2"/>
  <vcpupin vcpu="1" cpuset="3"/>
  <emulatorpin cpuset="0-1"/>
  <iothreadpin iothread="1" cpuset="4"/>
</cputune>
```

::: danger CPU Pinning 前提條件
CPU Pinning 需要在 Kubernetes 層級啟用 CPU Manager（`--cpu-manager-policy=static`），並且 Pod 必須使用 Guaranteed QoS class（`requests == limits`）。否則 KubeVirt 無法取得專屬 CPU 核心。
:::

## 記憶體管理

### Memory Balloon

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/balloon.go
type BalloonDomainConfigurator struct {
    useLaunchSecuritySEV  bool
    useLaunchSecurityPV   bool
    freePageReporting     bool
    memBalloonStatsPeriod uint
    virtioModel           string  // "virtio-non-transitional" 等
}
```

Balloon 允許 hypervisor 動態回收 Guest 未使用的記憶體：

```xml
<memballoon model="virtio-non-transitional">
  <stats period="10"/>
  <driver iommu="on"/>  <!-- SEV/SNP 環境 -->
</memballoon>
```

### HugePages 配置

```go
type MemoryBacking struct {
    HugePages *HugePages `xml:"hugepages,omitempty"`
    Source    *MemoryBackingSource `xml:"source,omitempty"`
    Access   *MemoryBackingAccess `xml:"access,omitempty"`
}

type HugePages struct {
    HugePage []HugePage `xml:"page,omitempty"`
}

type HugePage struct {
    Size    string `xml:"size,attr"`    // "2048" 或 "1048576"
    Unit    string `xml:"unit,attr"`    // "KiB"
    NodeSet string `xml:"nodeset,attr"` // NUMA node
}
```

VMI YAML 範例：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
metadata:
  name: hugepages-vm
spec:
  domain:
    memory:
      hugepages:
        pageSize: "2Mi"  # 或 "1Gi"
    resources:
      requests:
        memory: "4Gi"
```

### virtio-mem 記憶體熱插拔

```go
type MemoryDevice struct {
    XMLName xml.Name      `xml:"memory"`
    Model   string        `xml:"model,attr"`  // "virtio-mem"
    Target  *MemoryTarget `xml:"target"`
}

type MemoryTarget struct {
    Size      Memory `xml:"size"`       // 最大容量
    Requested Memory `xml:"requested"`  // 當前請求量
    Current   Memory `xml:"current"`    // 目前實際使用
    Node      string `xml:"node"`       // NUMA node
    Block     Memory `xml:"block"`      // 區塊大小
}
```

::: info virtio-mem vs balloon
- **Balloon**：Guest 主動歸還記憶體頁面，粒度為頁面大小（4KB），適合記憶體 overcommit
- **virtio-mem**：Host 端控制記憶體裝置大小，粒度為 block size（通常 2MB），適合真正的記憶體熱插拔
:::

## Machine Type

### q35 vs i440fx

| 特性 | q35 | i440fx |
|---|---|---|
| PCI 匯流排 | **PCIe**（PCI Express） | **Legacy PCI** |
| AHCI (SATA) | ✅ 原生支援 | ❌ 需模擬 |
| USB 3.0 | ✅ 支援 | ❌ USB 2.0 |
| IOMMU | ✅ Intel VT-d | ❌ |
| Secure Boot | ✅ 支援 | ❌ |
| Hotplug 能力 | 更完整 | 有限 |

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/os.go
func configureMachineType(vmi *v1.VirtualMachineInstance, domain *api.Domain) {
    if machine := vmi.Spec.Domain.Machine; machine != nil {
        domain.Spec.OS.Type.Machine = machine.Type
    }
    // 預設由 arch 模組設定：amd64 → "q35"
}
```

::: tip 為什麼 KubeVirt 預設使用 q35
KubeVirt 預設使用 q35 machine type，因為：
1. 支援 PCIe 匯流排，允許更多設備和更好的 hotplug 支援
2. 搭配 OVMF (EFI) 實現 Secure Boot
3. IOMMU 支援對 VFIO passthrough 和 SEV/TDX 加密虛擬機是必要的
4. 現代 Guest OS（尤其 Windows 10+）對 q35 有更好的支援
:::

## 安全特性

### LaunchSecurity 配置

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/launch_security.go
type LaunchSecurityDomainConfigurator struct {
    architecture string
}

func (l LaunchSecurityDomainConfigurator) Configure(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) error {
    // SEV 配置
    if util.IsSEVVMI(vmi) {
        domain.Spec.LaunchSecurity = &api.LaunchSecurity{
            Type:   "sev",
            Policy: fmt.Sprintf("0x%04x", policy),
        }
        // 可選：DHCert、Session
    }
    
    // SEV-SNP 配置
    if util.IsSEVSNPVMI(vmi) {
        domain.Spec.LaunchSecurity = &api.LaunchSecurity{
            Type:   "sev-snp",
            Policy: fmt.Sprintf("0x%x", policy),
        }
    }
    
    // TDX 配置
    if util.IsTDXVMI(vmi) {
        domain.Spec.LaunchSecurity = &api.LaunchSecurity{
            Type: "tdx",
            QuoteGenerationService: &api.QGS{
                Path: socketPath, // 從 annotation 取得
            },
        }
    }
}
```

```go
// API 型別
type LaunchSecurity struct {
    Type                   string `xml:"type,attr"`
    DHCert                 string `xml:"dhCert,omitempty"`
    Session                string `xml:"session,omitempty"`
    Cbitpos                string `xml:"cbitpos,omitempty"`
    ReducedPhysBits        string `xml:"reducedPhysBits,omitempty"`
    Policy                 string `xml:"policy,omitempty"`
    QuoteGenerationService *QGS   `xml:"quoteGenerationService,omitempty"`
}
```

### 各安全技術比較

| 技術 | 廠商 | 記憶體加密 | 完整性保護 | 遠端認證 |
|---|---|---|---|---|
| **SEV** | AMD | ✅ AES-128 | ❌ | ❌ |
| **SEV-SNP** | AMD | ✅ AES-128 | ✅ RMP | ✅ |
| **TDX** | Intel | ✅ AES-128 | ✅ | ✅ |

VMI YAML 範例（SEV）：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
spec:
  domain:
    launchSecurity:
      sev:
        policy:
          encryptedState: false
    firmware:
      bootloader:
        efi:
          secureBoot: false
    devices:
      disks:
      - disk:
          bus: virtio
        name: rootdisk
      interfaces:
      - name: default
        model: virtio
        masquerade: {}
```

::: danger SEV/TDX 限制
- SEV/SEV-SNP 僅支援 AMD EPYC 處理器
- TDX 僅支援 Intel 第 4 代 Xeon Scalable（Sapphire Rapids）及更新
- 加密 VM 的 balloon 裝置需要啟用 IOMMU driver
- SEV 不支援 Live Migration（SEV-SNP 和 TDX 有實驗性支援）
- Secure Boot 在 SEV-SNP/TDX 中使用 `rom` 型 loader（非 `pflash`）
:::

## Domain XML 中的 Features 區塊

### KVM 特定功能

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/kvm.go
type KvmDomainConfigurator struct{}

func (k KvmDomainConfigurator) Configure(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) error {
    // KVM Hidden State — 隱藏 KVM hypervisor 特徵
    // 用途：繞過某些軟體的虛擬化偵測（如 NVIDIA 驅動）
    if vmi.Spec.Domain.Features != nil &&
       vmi.Spec.Domain.Features.KVM != nil &&
       vmi.Spec.Domain.Features.KVM.Hidden {
        domain.Spec.Features.KVM = &api.FeatureKVM{
            Hidden: &api.FeatureState{State: "on"},
        }
    }
}
```

產生的 XML：

```xml
<features>
  <acpi/>
  <apic/>
  <kvm>
    <hidden state="on"/>
  </kvm>
  <hyperv>
    <relaxed state="on"/>
    <vapic state="on"/>
    <spinlocks state="on" retries="8191"/>
    <vpindex state="on"/>
    <synic state="on"/>
    <synictimer state="on">
      <direct state="on"/>
    </synictimer>
  </hyperv>
</features>
```

## TPM 配置

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/tpm.go
func (t TPMDomainConfigurator) Configure(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) error {
    newTPMDevice := api.TPM{
        Model: "tpm-tis",  // 預設模型
        Backend: api.TPMBackend{
            Type:    "emulator",  // swtpm
            Version: "2.0",
        },
    }
    
    // 持久化 TPM 使用 tpm-crb 模型
    if tpm.HasPersistentDevice(&vmi.Spec) {
        newTPMDevice.Backend.PersistentState = "yes"
        newTPMDevice.Model = "tpm-crb"
    }
    
    domain.Spec.Devices.TPMs = append(domain.Spec.Devices.TPMs, newTPMDevice)
    return nil
}
```

| 模型 | 介面 | 持久化 | 適用場景 |
|---|---|---|---|
| `tpm-tis` | TIS (LPC) | ❌ | 臨時 TPM、無狀態 VM |
| `tpm-crb` | CRB (MMIO) | ✅ | 持久 TPM、Windows 11、BitLocker |

::: info TPM 2.0 與 Windows 11
Windows 11 強制要求 TPM 2.0。KubeVirt 使用 `swtpm`（軟體 TPM 模擬器）提供 TPM 功能。搭配 `tpm-crb` 模型和持久化後端，可以跨重啟保留 TPM 狀態，支援 BitLocker 加密。
:::

## SMBIOS 配置

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/sysinfo.go
type SysInfoDomainConfigurator struct {
    smBIOS *SMBIOS
}

type SMBIOS struct {
    Manufacturer string
    Product      string
    Version      string
    SKU          string
    Family       string
}
```

產生的 XML：

```xml
<sysinfo type="smbios">
  <system>
    <entry name="uuid">12345678-1234-1234-1234-123456789012</entry>
    <entry name="serial">e4686d2c-6e8d-4335-b8fd-81bee22f4815</entry>
    <entry name="manufacturer">KubeVirt</entry>
    <entry name="product">None</entry>
    <entry name="family">KubeVirt</entry>
  </system>
  <chassis>
    <entry name="manufacturer">KubeVirt</entry>
    <entry name="serial">e4686d2c-6e8d-4335-b8fd-81bee22f4815</entry>
  </chassis>
</sysinfo>
```

VMI 中自訂 SMBIOS：

```yaml
spec:
  domain:
    firmware:
      uuid: "12345678-1234-1234-1234-123456789012"
      serial: "my-custom-serial"
    chassis:
      manufacturer: "MyCompany"
      version: "1.0"
      serial: "CHASSIS-001"
      asset: "ASSET-001"
      sku: "SKU-001"
```

## 總結

KubeVirt 的 QEMU/KVM 整合架構充分展現了良好的軟體工程設計：

1. **Configurator 模式**：將 27+ 個元件的轉換邏輯解耦，每個 Configurator 獨立負責一個功能領域
2. **型別安全的 XML 映射**：Go struct 標籤完整映射 libvirt Domain XML schema
3. **DomainManager 抽象**：35 個方法覆蓋虛擬機完整生命週期，便於測試和替換
4. **事件驅動架構**：透過 libvirt 事件回調實現非阻塞的狀態監控
5. **安全優先**：從 SEV/TDX 加密到 TPM 模擬，支援最新的機密運算技術
