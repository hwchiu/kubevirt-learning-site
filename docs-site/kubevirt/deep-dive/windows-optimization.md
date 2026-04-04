# Windows VM 最佳化 — 從 KubeVirt 程式碼看效能調校

本文從 KubeVirt 原始碼的角度，深入解析如何在 KubeVirt 上執行高效能 Windows 虛擬機。涵蓋 HyperV Enlightenments、時鐘配置、EFI/TPM、VirtIO 驅動、CPU 拓撲最佳化等完整知識。

## 為什麼 Windows VM 需要特殊處理

### Windows 核心與 Linux 的差異

Windows 和 Linux 在虛擬化環境下的行為有本質差異：

| 面向 | Linux | Windows |
|---|---|---|
| 時鐘處理 | 使用 kvmclock 半虛擬化時鐘 | 依賴 HPET/RTC，需要 HyperV Timer |
| 中斷處理 | 原生支援 virtio 驅動 | 需安裝額外 VirtIO 驅動 |
| Spinlock | 核心層最佳化 | 過度自旋導致 CPU 浪費 |
| Watchdog | 較寬容的超時設定 | 嚴格的 watchdog → BSOD |
| 驅動模型 | 核心內建 virtio 驅動 | 需要 Red Hat VirtIO 簽名驅動 |

### 效能差距的主因

未經最佳化的 Windows VM 效能損失可達 **30-50%**，主因：

1. **無半虛擬化驅動**：使用模擬的 IDE/e1000 而非 virtio，每次 I/O 都需要完整的硬體模擬
2. **時鐘處理不當**：HPET 計時器在虛擬環境中效能極差
3. **過多 VM-Exit**：無 HyperV Enlightenments 導致頻繁的 VM-Exit（每次約 1-5μs）
4. **Spinlock 風暴**：多核心 Windows VM 的 spinlock 在虛擬環境中導致 CPU 空轉

### KubeVirt 程式碼中的 Windows 預設配置

```go
// 檔案：tests/libvmifact/factory.go
func NewWindows(opts ...libvmi.Option) *kvirtv1.VirtualMachineInstance {
    const cpuCount = 2
    const featureSpinlocks = 8191
    
    windowsOpts := []libvmi.Option{
        libvmi.WithTerminationGracePeriod(0),
        libvmi.WithCPUCount(cpuCount, cpuCount, cpuCount),
        libvmi.WithMemoryRequest("2048Mi"),
        libvmi.WithEphemeralPersistentVolumeClaim(windowsDiskName, WindowsPVCName),
    }
    windowsOpts = append(windowsOpts, opts...)
    vmi := libvmi.New(windowsOpts...)

    // ═══ HyperV Enlightenments ═══
    vmi.Spec.Domain.Features = &kvirtv1.Features{
        ACPI: kvirtv1.FeatureState{},
        APIC: &kvirtv1.FeatureAPIC{},
        Hyperv: &kvirtv1.FeatureHyperv{
            Relaxed:    &kvirtv1.FeatureState{},           // 停用 watchdog timeout
            SyNICTimer: &kvirtv1.SyNICTimer{               // 合成中斷計時器
                Direct: &kvirtv1.FeatureState{},
            },
            VAPIC:      &kvirtv1.FeatureState{},           // 半虛擬化 APIC
            Spinlocks:  &kvirtv1.FeatureSpinlocks{         // 自旋鎖最佳化
                Retries: pointer.P(uint32(featureSpinlocks)),
            },
        },
    }

    // ═══ 時鐘配置 ═══
    vmi.Spec.Domain.Clock = &kvirtv1.Clock{
        ClockOffset: kvirtv1.ClockOffset{UTC: &kvirtv1.ClockOffsetUTC{}},
        Timer: &kvirtv1.Timer{
            HPET:   &kvirtv1.HPETTimer{Enabled: pointer.P(false)},     // 停用 HPET
            PIT:    &kvirtv1.PITTimer{TickPolicy: kvirtv1.PITTickPolicyDelay},
            RTC:    &kvirtv1.RTCTimer{TickPolicy: kvirtv1.RTCTickPolicyCatchup},
            Hyperv: &kvirtv1.HypervTimer{},                             // 啟用 HyperV 時鐘
        },
    }
    
    vmi.Spec.Domain.Firmware = &kvirtv1.Firmware{UUID: WindowsFirmware}
    return vmi
}
```

::: warning 最低需求
KubeVirt 的 Windows 工廠函式設定了最低 2 vCPU + 2048Mi 記憶體。實際使用中，Windows 10/11 建議至少 **4 vCPU + 4096Mi**，Windows Server 建議 **4 vCPU + 8192Mi**。
:::

## HyperV Enlightenments 完整指南

### 什麼是 HyperV Enlightenments

HyperV Enlightenments 是 Microsoft 定義的一組半虛擬化介面規範。當 QEMU/KVM 向 Guest OS 公開這些介面時，Windows 會自動偵測並使用最佳化路徑，大幅減少效能損失。

Windows 核心透過 CPUID 指令偵測 hypervisor 功能，當發現 HyperV 相容介面時，自動啟用半虛擬化驅動程式。

### FeatureHyperv 完整結構定義

```go
// 檔案：staging/src/kubevirt.io/api/core/v1/schema.go
type FeatureHyperv struct {
    // 停用 watchdog timeout → 避免 BSOD
    Relaxed *FeatureState `json:"relaxed,omitempty"`
    
    // 半虛擬化 APIC → 減少 VM-Exit
    VAPIC *FeatureState `json:"vapic,omitempty"`
    
    // 自旋鎖最佳化 → 減少 hypercall
    Spinlocks *FeatureSpinlocks `json:"spinlocks,omitempty"`
    
    // 虛擬處理器索引
    VPIndex *FeatureState `json:"vpindex,omitempty"`
    
    // 時間記帳改進
    Runtime *FeatureState `json:"runtime,omitempty"`
    
    // 合成中斷控制器
    SyNIC *FeatureState `json:"synic,omitempty"`
    
    // 合成中斷計時器（支援 Direct mode）
    SyNICTimer *SyNICTimer `json:"synictimer,omitempty"`
    
    // Hyperv 重啟支援（需要 SyNIC）
    Reset *FeatureState `json:"reset,omitempty"`
    
    // 自定義 hypervisor 識別（繞過 NVIDIA 偵測）
    VendorID *FeatureVendorID `json:"vendorid,omitempty"`
    
    // TSC 時鐘源處理
    Frequencies *FeatureState `json:"frequencies,omitempty"`
    
    // TSC 頻率變更通知（Live Migration 關鍵）
    Reenlightenment *FeatureState `json:"reenlightenment,omitempty"`
    
    // TLB 刷新最佳化（支援 Direct + Extended）
    TLBFlush *TLBFlush `json:"tlbflush,omitempty"`
    
    // 處理器間中斷最佳化
    IPI *FeatureState `json:"ipi,omitempty"`
    
    // 擴展 VMX 控制（需要 VAPIC）
    EVMCS *FeatureState `json:"evmcs,omitempty"`
}
```

### 各功能詳細說明

#### Relaxed — 停用 Watchdog Timeout

```yaml
features:
  hyperv:
    relaxed: {}  # Enabled: true (預設)
```

**問題**：Windows 核心有一個嚴格的 watchdog timer，在虛擬化環境中 CPU 排程延遲可能觸發 watchdog timeout，導致 **BSOD (藍屏)**。

**解法**：`Relaxed` 告知 Windows 核心放寬 watchdog timeout 限制。

::: danger 必須啟用
不啟用 Relaxed 是 Windows VM BSOD 最常見的原因之一。強烈建議所有 Windows VM 都啟用此功能。
:::

#### VAPIC — 半虛擬化 APIC

```yaml
features:
  hyperv:
    vapic: {}
```

**效果**：將 APIC（Advanced Programmable Interrupt Controller）的操作改為半虛擬化路徑。傳統 APIC 操作（如 EOI — End of Interrupt）需要 VM-Exit，VAPIC 透過共享記憶體頁面避免大部分 VM-Exit。

**效能提升**：中斷密集型工作負載可提升 **10-20%** 效能。

#### Spinlocks — 自旋鎖最佳化

```go
type FeatureSpinlocks struct {
    FeatureState `json:",inline"`
    Retries *uint32 `json:"spinlocks,omitempty"` // 預設 4096，推薦 8191
}
```

```yaml
features:
  hyperv:
    spinlocks:
      spinlocks: 8191
```

**問題**：Windows 核心大量使用 spinlock。在虛擬環境中，持有 lock 的 vCPU 可能被 host 調度出去，而等待的 vCPU 持續空轉（spin），浪費 CPU 時間。

**解法**：超過 `Retries` 次自旋後，改用 hypercall 通知 hypervisor，讓出 CPU。KubeVirt 預設值 **8191** 是微軟推薦的最佳值。

#### VendorID — 自定義 Hypervisor 識別

```go
type FeatureVendorID struct {
    FeatureState `json:",inline"`
    VendorID string `json:"vendorid,omitempty"` // 最多 12 字元
}
```

```yaml
features:
  hyperv:
    vendorid:
      vendorid: "1234567890ab"
```

::: tip 繞過 NVIDIA 驅動偵測
NVIDIA 消費級 GPU 驅動（GeForce 系列）會偵測虛擬化環境並拒絕啟動。設定自定義 VendorID 可繞過此偵測。搭配 `kvm.hidden: true` 一起使用效果最佳：

```yaml
features:
  kvm:
    hidden: true
  hyperv:
    vendorid:
      vendorid: "randomstring"
```
:::

#### Reenlightenment — TSC 頻率變更通知

```yaml
features:
  hyperv:
    reenlightenment: {}
    frequencies: {}
```

**重要性**：Live Migration 時，目標主機的 TSC 頻率可能不同。`Reenlightenment` 通知 Windows 核心 TSC 頻率已變更，避免時鐘漂移。`Frequencies` 搭配使用，讓 Guest 可以查詢正確的 TSC 頻率。

#### TLBFlush — TLB 刷新最佳化

```go
type TLBFlush struct {
    FeatureState `json:",inline"`
    Direct   *FeatureState `json:"direct,omitempty"`
    Extended *FeatureState `json:"extended,omitempty"`
}
```

```yaml
features:
  hyperv:
    tlbflush:
      direct: {}
      extended: {}
```

**效果**：
- 基本 TLBFlush：允許 Guest 發送 TLB 刷新請求
- **Direct**：直接發送 TLB flush 到 hypervisor（巢狀虛擬化最佳化，如 Windows VBS）
- **Extended**：允許部分 TLB 刷新（不刷新全部 TLB 條目）

#### SyNIC + SyNICTimer — 合成中斷控制器

```go
type SyNICTimer struct {
    FeatureState `json:",inline"`
    Direct *FeatureState `json:"direct,omitempty"`
}
```

```yaml
features:
  hyperv:
    synic: {}
    synictimer:
      direct: {}
```

SyNIC（Synthetic Interrupt Controller）提供低延遲的中斷處理路徑。SyNICTimer 的 **Direct** 模式進一步最佳化，讓計時器中斷直接注入 vCPU，不經過完整的中斷模擬路徑。

### HyperV Passthrough 模式

```yaml
features:
  hyperv:
    # 空的 hyperv 欄位 + passthrough annotation
    # 啟用所有 host 支援的 HyperV 功能
```

::: warning Passthrough 限制
HyperV Passthrough 啟用主機支援的所有 HyperV 功能，但這使得 VM 與特定主機綁定，**無法 Live Migration**。僅建議在不需要遷移的場景使用。
:::

### 轉換器程式碼分析

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/hypervisor_features.go

func convertHypervFeature(hyperv *v1.FeatureHyperv) *api.FeatureHyperv {
    result := &api.FeatureHyperv{}
    
    if hyperv.Relaxed != nil {
        result.Relaxed = &api.FeatureState{
            State: boolToOnOff(hyperv.Relaxed.Enabled, true),
        }
    }
    if hyperv.VAPIC != nil {
        result.VAPIC = &api.FeatureState{
            State: boolToOnOff(hyperv.VAPIC.Enabled, true),
        }
    }
    if hyperv.Spinlocks != nil {
        result.Spinlocks = &api.FeatureSpinlocks{
            State:   boolToOnOff(hyperv.Spinlocks.Enabled, true),
            Retries: hyperv.Spinlocks.Retries,
        }
    }
    // ... 對每個 HyperV 功能做類似轉換
    
    if hyperv.TLBFlush != nil {
        result.TLBFlush = convertTLBFlushFeature(hyperv.TLBFlush)
    }
    return result
}

func convertTLBFlushFeature(tlbFlush *v1.TLBFlush) *api.TLBFlush {
    result := &api.TLBFlush{
        State: boolToOnOff(tlbFlush.Enabled, true),
    }
    if tlbFlush.Direct != nil {
        result.Direct = &api.FeatureState{
            State: boolToOnOff(tlbFlush.Direct.Enabled, true),
        }
    }
    if tlbFlush.Extended != nil {
        result.Extended = &api.FeatureState{
            State: boolToOnOff(tlbFlush.Extended.Enabled, true),
        }
    }
    return result
}
```

產生的 Domain XML：

```xml
<features>
  <acpi/>
  <apic/>
  <hyperv>
    <relaxed state="on"/>
    <vapic state="on"/>
    <spinlocks state="on" retries="8191"/>
    <vpindex state="on"/>
    <runtime state="on"/>
    <synic state="on"/>
    <stimer state="on">
      <direct state="on"/>
    </stimer>
    <reset state="on"/>
    <vendor_id state="on" value="1234567890ab"/>
    <frequencies state="on"/>
    <reenlightenment state="on"/>
    <tlbflush state="on">
      <direct state="on"/>
      <extended state="on"/>
    </tlbflush>
    <ipi state="on"/>
    <evmcs state="on"/>
  </hyperv>
</features>
```

## 時鐘與計時器配置

### Windows 的時鐘問題

Windows 對時鐘精確度要求極高。在虛擬環境中：

- **HPET**（High Precision Event Timer）：在虛擬化環境中模擬成本極高，每次讀取需要 VM-Exit
- **PIT**（Programmable Interval Timer）：老舊的 8254 計時器，精度低但穩定
- **RTC**（Real-Time Clock）：保持系統時間，需要合理的 tick policy

### 時鐘轉換器程式碼

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/clock.go
type ClockDomainConfigurator struct{}

func (c ClockDomainConfigurator) Configure(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) error {
    if vmi.Spec.Domain.Clock != nil {
        clock := vmi.Spec.Domain.Clock
        newClock := &api.Clock{}
        err := convert_v1_Clock_To_api_Clock(clock, newClock)
        if err != nil {
            return err
        }
        domain.Spec.Clock = newClock
    }
    
    // TSC 頻率拓撲提示（遷移相關）
    if topology.IsManualTSCFrequencyRequired(vmi) {
        freq := *vmi.Status.TopologyHints.TSCFrequency
        clock := domain.Spec.Clock
        if clock == nil {
            clock = &api.Clock{}
        }
        clock.Timer = append(clock.Timer, api.Timer{
            Name:      "tsc",
            Frequency: strconv.FormatInt(freq, 10),
        })
        domain.Spec.Clock = clock
    }
    return nil
}

func convert_v1_Clock_To_api_Clock(source *v1.Clock, clock *api.Clock) error {
    // 時鐘偏移
    if source.UTC != nil {
        clock.Offset = "utc"
        if source.UTC.OffsetSeconds != nil {
            clock.Adjustment = strconv.Itoa(*source.UTC.OffsetSeconds)
        } else {
            clock.Adjustment = "reset"
        }
    } else if source.Timezone != nil {
        clock.Offset = "timezone"
        clock.Timezone = string(*source.Timezone)
    }

    // 計時器配置
    if source.Timer != nil {
        if source.Timer.RTC != nil {
            newTimer := api.Timer{Name: "rtc"}
            newTimer.TickPolicy = string(source.Timer.RTC.TickPolicy)
            newTimer.Present = boolToYesNo(source.Timer.RTC.Enabled, true)
            clock.Timer = append(clock.Timer, newTimer)
        }
        if source.Timer.PIT != nil {
            newTimer := api.Timer{Name: "pit"}
            newTimer.Present = boolToYesNo(source.Timer.PIT.Enabled, true)
            newTimer.TickPolicy = string(source.Timer.PIT.TickPolicy)
            clock.Timer = append(clock.Timer, newTimer)
        }
        if source.Timer.HPET != nil {
            newTimer := api.Timer{Name: "hpet"}
            newTimer.Present = boolToYesNo(source.Timer.HPET.Enabled, true)
            clock.Timer = append(clock.Timer, newTimer)
        }
        if source.Timer.Hyperv != nil {
            newTimer := api.Timer{Name: "hypervclock"}
            newTimer.Present = boolToYesNo(source.Timer.Hyperv.Enabled, true)
            clock.Timer = append(clock.Timer, newTimer)
        }
    }
    return nil
}
```

### Windows 推薦時鐘配置

| 計時器 | 設定 | 原因 |
|---|---|---|
| **HPET** | `Enabled: false` | 模擬成本極高，每次讀取需 VM-Exit |
| **PIT** | `TickPolicy: delay` | 延遲錯過的 tick，不做補償 |
| **RTC** | `TickPolicy: catchup` | 追趕錯過的 tick，避免時間漂移 |
| **Hyperv Timer** | `Enabled: true` | Windows 專用半虛擬化時鐘，效能最佳 |
| **Clock Offset** | `UTC` | 統一時間基準 |

```yaml
spec:
  domain:
    clock:
      utc: {}
      timer:
        hpet:
          enabled: false
        pit:
          tickPolicy: delay
        rtc:
          tickPolicy: catchup
        hyperv: {}
```

產生的 Domain XML：

```xml
<clock offset="utc" adjustment="reset">
  <timer name="rtc" tickpolicy="catchup" present="yes"/>
  <timer name="pit" tickpolicy="delay" present="yes"/>
  <timer name="hpet" present="no"/>
  <timer name="hypervclock" present="yes"/>
</clock>
```

::: info Tick Policy 解釋
- **delay**：延遲注入錯過的 tick，不做補償（適合 PIT，避免突發大量中斷）
- **catchup**：追趕錯過的 tick，在可用時快速補發（適合 RTC，保持時間準確）
- **discard**：直接丟棄錯過的 tick
- **merge**：合併多個錯過的 tick 為一個
:::

## EFI / Secure Boot / TPM 2.0

### Windows 11 的硬體需求

Windows 11 強制要求：
- ✅ TPM 2.0
- ✅ Secure Boot
- ✅ UEFI 韌體
- ✅ 4GB+ RAM
- ✅ 2+ vCPU

### OVMF 韌體配置

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/os.go
type EFIConfiguration struct {
    EFICode      string // OVMF 韌體路徑
    EFIVars      string // NVRAM 變數模板路徑
    SecureLoader bool   // 是否啟用 Secure Boot
}

func (o OSDomainConfigurator) configureEFI(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) {
    if !vmi.IsBootloaderEFI() || o.efiConfiguration == nil {
        return
    }
    
    domain.Spec.OS.BootLoader = &api.Loader{
        Path:     o.efiConfiguration.EFICode,
        ReadOnly: "yes",
        Secure:   boolToYesNo(&o.efiConfiguration.SecureLoader, false),
    }
    
    if util.IsSEVSNPVMI(vmi) || util.IsTDXVMI(vmi) {
        // SEV-SNP / TDX 使用無狀態韌體
        domain.Spec.OS.BootLoader.Type = "rom"
        domain.Spec.OS.NVRam = nil
    } else {
        // 一般 EFI：使用 pflash + NVRam
        domain.Spec.OS.BootLoader.Type = "pflash"
        domain.Spec.OS.NVRam = &api.NVRam{
            Template: o.efiConfiguration.EFIVars,
            NVRam:    filepath.Join(util.PathForNVram(vmi),
                vmi.Name+"_VARS.fd"),
        }
    }
}
```

產生的 Domain XML：

```xml
<os>
  <type arch="x86_64" machine="q35">hvm</type>
  <loader readonly="yes" secure="yes" type="pflash">/usr/share/OVMF/OVMF_CODE.secboot.fd</loader>
  <nvram template="/usr/share/OVMF/OVMF_VARS.secboot.fd">/path/to/my-vm_VARS.fd</nvram>
  <smbios mode="sysinfo"/>
</os>
```

### TPM 2.0 模擬

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/compute/tpm.go
func (t TPMDomainConfigurator) Configure(
    vmi *v1.VirtualMachineInstance, domain *api.Domain,
) error {
    newTPMDevice := api.TPM{
        Model: "tpm-tis",       // 預設：TIS 介面
        Backend: api.TPMBackend{
            Type:    "emulator", // 使用 swtpm
            Version: "2.0",
        },
    }
    
    // 持久化 TPM → 改用 CRB 模型
    if tpm.HasPersistentDevice(&vmi.Spec) {
        newTPMDevice.Backend.PersistentState = "yes"
        newTPMDevice.Model = "tpm-crb"
    }
    
    domain.Spec.Devices.TPMs = append(domain.Spec.Devices.TPMs, newTPMDevice)
    return nil
}
```

VMI YAML：

```yaml
spec:
  domain:
    firmware:
      bootloader:
        efi:
          secureBoot: true
    devices:
      tpm:
        persistent: true  # 跨重啟保留 TPM 狀態
```

::: tip Windows 11 完整配置
Windows 11 安裝需要同時啟用 EFI + Secure Boot + TPM 2.0。使用 `persistent: true` 確保 TPM 狀態在 VM 重啟後保留，這對 BitLocker 加密至關重要。
:::

## SMBIOS 配置

### Windows 授權與 SMBIOS 的關係

Windows OEM 授權通常依賴主機板 SMBIOS 中的 SLIC/MSDM 表格。在虛擬環境中，可以透過自訂 SMBIOS 資訊來配置 Windows 授權識別。

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

### 自定義 UUID / Serial 配置

```yaml
spec:
  domain:
    firmware:
      uuid: "12345678-1234-1234-1234-123456789012"
      serial: "CUSTOM-SERIAL-001"
    chassis:
      manufacturer: "Dell Inc."
      version: "1.0"
      serial: "CHASSIS-SERIAL"
      asset: "ASSET-TAG"
      sku: "SKU-001"
```

產生的 Domain XML：

```xml
<sysinfo type="smbios">
  <system>
    <entry name="uuid">12345678-1234-1234-1234-123456789012</entry>
    <entry name="serial">CUSTOM-SERIAL-001</entry>
    <entry name="manufacturer">KubeVirt</entry>
    <entry name="family">KubeVirt</entry>
  </system>
  <chassis>
    <entry name="manufacturer">Dell Inc.</entry>
    <entry name="version">1.0</entry>
    <entry name="serial">CHASSIS-SERIAL</entry>
    <entry name="asset">ASSET-TAG</entry>
    <entry name="sku">SKU-001</entry>
  </chassis>
</sysinfo>
```

## VirtIO 驅動程式

### 為什麼需要 VirtIO 驅動

| 裝置類型 | 模擬裝置 | VirtIO 裝置 | 效能差距 |
|---|---|---|---|
| 磁碟 | IDE / SATA | virtio-blk / virtio-scsi | **3-10x** IOPS 提升 |
| 網路 | e1000 / e1000e | virtio-net | **2-5x** 頻寬提升 |
| 記憶體管理 | 無 | virtio-balloon | 動態記憶體回收 |
| 隨機數 | 無 | virtio-rng | 加速密碼學運算 |

### Windows VirtIO 驅動安裝方法

**方法一：安裝時掛載驅動 ISO**

```yaml
spec:
  domain:
    devices:
      disks:
      - disk:
          bus: virtio      # 系統碟使用 virtio
        name: rootdisk
      - cdrom:
          bus: sata        # 驅動 ISO 使用 SATA（不需要驅動）
        name: virtio-drivers
  volumes:
  - name: rootdisk
    persistentVolumeClaim:
      claimName: windows-pvc
  - name: virtio-drivers
    containerDisk:
      image: registry.example.com/virtio-win:latest
```

**方法二：不安裝 VirtIO 的替代方案**

```yaml
spec:
  domain:
    devices:
      disks:
      - disk:
          bus: sata        # 使用 SATA（Windows 原生支援）
        name: rootdisk
      interfaces:
      - name: default
        model: e1000e      # 使用 e1000e（Windows 原生支援）
        masquerade: {}
```

::: warning 效能代價
使用 SATA + e1000e 雖然不需要額外驅動，但效能損失顯著。建議僅在安裝階段臨時使用，安裝完成後切換到 virtio。
:::

### VirtIO 過渡模式

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/virtio/transitional-model.go
func InterpretTransitionalModelType(
    useVirtioTransitional *bool, archString string,
) string {
    vtenabled := useVirtioTransitional != nil && *useVirtioTransitional
    return arch.NewConverter(archString).TransitionalModelType(vtenabled)
}
```

| 模式 | XML Model | PCI 類型 | 相容性 |
|---|---|---|---|
| **Non-transitional** | `virtio-non-transitional` | 純 PCIe | 現代 OS |
| **Transitional** | `virtio-transitional` | PCIe + Legacy PCI | 舊版 OS（Win XP/2003） |

```yaml
spec:
  domain:
    devices:
      useVirtioTransitional: true  # 啟用過渡模式
```

## CPU 拓撲最佳化

### Windows 授權模型

Windows Server 授權按照 **physical core** 計算（每 2 core 一組）。在虛擬環境中，socket 數量可能影響授權需求。

### 建議拓撲配置

```yaml
# 8 vCPU — 使用 preferCores 最佳化授權
spec:
  domain:
    cpu:
      cores: 8
      sockets: 1
      threads: 1
      dedicatedCpuPlacement: false
```

或使用 Instancetype 的拓撲策略：

```yaml
# preferCores 策略：盡量增加 core 數量，減少 socket
# 8 vCPU → 1 socket × 8 cores × 1 thread
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineInstancetype
metadata:
  name: windows-8vcpu
spec:
  cpu:
    guest: 8
  memory:
    guest: "16Gi"
```

::: tip Windows 授權最佳化
使用 `preferCores` 策略將所有 vCPU 放在同一個 socket 中，可以減少 Windows Server 的授權成本。例如 8 vCPU 配置為 1 socket × 8 cores，只需要 1 個 socket 的授權。
:::

## 網路效能

### 網路模型對比

| 模型 | 類型 | 頻寬 | CPU 開銷 | Windows 驅動 |
|---|---|---|---|---|
| `e1000` | 完全模擬 | ~1 Gbps | 高 | 原生內建 |
| `e1000e` | 完全模擬 | ~1 Gbps | 中 | 原生內建 |
| `virtio` | 半虛擬化 | ~10+ Gbps | 低 | 需安裝驅動 |

### 多佇列網路（NetworkInterfaceMultiQueue）

```go
// 檔案：pkg/virt-launcher/virtwrap/converter/network/virtio-queues.go
const MultiQueueMaxQueues = uint32(256)

func NetworkQueuesCapacity(vmi *v1.VirtualMachineInstance) uint32 {
    if !isTrue(vmi.Spec.Domain.Devices.NetworkInterfaceMultiQueue) {
        return 0
    }
    // 佇列數量 = vCPU 數量（上限 256）
    cpuTopology := vcpu.GetCPUTopology(vmi)
    queueNumber := vcpu.CalculateRequestedVCPUs(cpuTopology)
    if queueNumber > MultiQueueMaxQueues {
        queueNumber = MultiQueueMaxQueues
    }
    return queueNumber
}
```

```yaml
spec:
  domain:
    devices:
      networkInterfaceMultiqueue: true
      interfaces:
      - name: default
        model: virtio
        masquerade: {}
```

產生的 Domain XML：

```xml
<interface type="ethernet">
  <model type="virtio-non-transitional"/>
  <driver name="vhost" queues="8"/>  <!-- 8 vCPU → 8 佇列 -->
</interface>
```

::: info RSS 支援
Windows VirtIO 網路驅動支援 RSS（Receive Side Scaling），搭配多佇列使用可將網路封包處理分散到多個 CPU 核心，大幅提升網路吞吐量。
:::

## 磁碟效能

### 磁碟匯流排對比

| 匯流排 | 效能 | 佇列深度 | 多佇列 | Windows 驅動 |
|---|---|---|---|---|
| `virtio` (virtio-blk) | 最高 | 高 | ✅ | 需安裝 |
| `scsi` (virtio-scsi) | 高 | 高 | ✅ | 需安裝 |
| `sata` | 中 | 低 | ❌ | 原生 |

### Cache 模式選擇

```go
// 磁碟配置轉換
disk.Driver = &api.DiskDriver{
    Name:  "qemu",
    Cache: string(diskDevice.Cache), // "none", "writethrough", "writeback"
    IO:    diskDevice.IO,             // "native", "threads"
}
```

| Cache 模式 | 安全性 | 效能 | 適用場景 |
|---|---|---|---|
| `none` | ✅ 最安全 | 高（Direct I/O） | 推薦預設，需要 O_DIRECT 支援 |
| `writethrough` | ✅ 安全 | 中 | 不支援 Direct I/O 時的安全選擇 |
| `writeback` | ❌ 掉電風險 | 最高 | 測試環境或有 UPS 保護 |

### IO Threads 配置

```yaml
spec:
  domain:
    ioThreadsPolicy: auto  # 自動配置 IO 線程數
    devices:
      disks:
      - disk:
          bus: virtio
        name: rootdisk
        io: native
        cache: none
```

::: tip 磁碟效能最佳實踐
Windows VM 磁碟最佳配置：
1. 使用 `virtio` 匯流排（安裝 VirtIO 驅動後）
2. Cache 設為 `none`（Direct I/O）
3. IO 設為 `native`
4. 啟用 `ioThreadsPolicy: auto`
5. 若使用多磁碟，考慮每磁碟獨立 IO Thread
:::

## 完整 Windows VM YAML 範例

### Windows 10/11 基礎範例

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: windows11
spec:
  running: true
  template:
    metadata:
      labels:
        kubevirt.io/domain: windows11
    spec:
      domain:
        cpu:
          cores: 4
          sockets: 1
          threads: 1
        memory:
          guest: "8Gi"
        machine:
          type: q35
        firmware:
          bootloader:
            efi:
              secureBoot: true
        clock:
          utc: {}
          timer:
            hpet:
              enabled: false
            pit:
              tickPolicy: delay
            rtc:
              tickPolicy: catchup
            hyperv: {}
        features:
          acpi: {}
          apic: {}
          hyperv:
            relaxed: {}
            vapic: {}
            spinlocks:
              spinlocks: 8191
            vpindex: {}
            runtime: {}
            synic: {}
            synictimer:
              direct: {}
            frequencies: {}
            reenlightenment: {}
            tlbflush: {}
            ipi: {}
            reset: {}
        devices:
          tpm:
            persistent: true
          disks:
          - disk:
              bus: virtio
            name: rootdisk
          - cdrom:
              bus: sata
            name: virtio-drivers
          interfaces:
          - name: default
            model: virtio
            masquerade: {}
          inputs:
          - type: tablet
            bus: usb
            name: tablet
        resources:
          requests:
            memory: "8Gi"
      networks:
      - name: default
        pod: {}
      volumes:
      - name: rootdisk
        persistentVolumeClaim:
          claimName: windows11-pvc
      - name: virtio-drivers
        containerDisk:
          image: registry.example.com/virtio-win:latest
```

### Windows Server 高效能範例

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: windows-server-2022
spec:
  running: true
  template:
    metadata:
      labels:
        kubevirt.io/domain: windows-server-2022
    spec:
      domain:
        cpu:
          cores: 8
          sockets: 1
          threads: 2
          model: host-passthrough
          dedicatedCpuPlacement: true
        memory:
          guest: "32Gi"
          hugepages:
            pageSize: "2Mi"
        machine:
          type: q35
        firmware:
          bootloader:
            efi:
              secureBoot: true
        clock:
          utc: {}
          timer:
            hpet:
              enabled: false
            pit:
              tickPolicy: delay
            rtc:
              tickPolicy: catchup
            hyperv: {}
        features:
          acpi: {}
          apic: {}
          hyperv:
            relaxed: {}
            vapic: {}
            spinlocks:
              spinlocks: 8191
            vpindex: {}
            runtime: {}
            synic: {}
            synictimer:
              direct: {}
            frequencies: {}
            reenlightenment: {}
            tlbflush:
              direct: {}
              extended: {}
            ipi: {}
            evmcs: {}
            reset: {}
        ioThreadsPolicy: auto
        devices:
          tpm:
            persistent: true
          networkInterfaceMultiqueue: true
          blockMultiQueue: true
          disks:
          - disk:
              bus: virtio
            name: rootdisk
            cache: none
            io: native
          - disk:
              bus: virtio
            name: datadisk
            cache: none
            io: native
          interfaces:
          - name: default
            model: virtio
            masquerade: {}
          inputs:
          - type: tablet
            bus: usb
            name: tablet
        resources:
          requests:
            memory: "32Gi"
            cpu: "16"
          limits:
            memory: "32Gi"
            cpu: "16"
      networks:
      - name: default
        pod: {}
      volumes:
      - name: rootdisk
        persistentVolumeClaim:
          claimName: ws2022-os-pvc
      - name: datadisk
        persistentVolumeClaim:
          claimName: ws2022-data-pvc
```

::: tip 高效能配置要點
上述高效能範例包含：
- **CPU Pinning**（`dedicatedCpuPlacement: true`）
- **HugePages**（`pageSize: "2Mi"`）
- **host-passthrough** CPU 模式
- **所有 HyperV Enlightenments**
- **多佇列網路 + 磁碟**
- **IO Threads**
- **Direct I/O**（`cache: none` + `io: native`）
:::

### 使用 Instancetype + Preference 的簡化範例

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: windows11-simple
spec:
  instancetype:
    name: u1.large      # 4 vCPU, 8Gi
    kind: VirtualMachineClusterInstancetype
  preference:
    name: windows.11     # Windows 11 最佳化預設
    kind: VirtualMachineClusterPreference
  running: true
  template:
    spec:
      domain:
        devices:
          disks:
          - disk:
              bus: virtio
            name: rootdisk
          interfaces:
          - name: default
            masquerade: {}
      networks:
      - name: default
        pod: {}
      volumes:
      - name: rootdisk
        persistentVolumeClaim:
          claimName: windows11-pvc
```

## Windows VM Preference 推薦設定

```yaml
apiVersion: instancetype.kubevirt.io/v1beta1
kind: VirtualMachineClusterPreference
metadata:
  name: windows.11
  labels:
    instancetype.kubevirt.io/os-type: windows
spec:
  # ═══ CPU 拓撲 ═══
  cpu:
    preferredCPUTopology: preferCores
  
  # ═══ 裝置偏好 ═══
  devices:
    preferredDiskBus: virtio
    preferredInterfaceModel: virtio
    preferredInputBus: usb
    preferredInputType: tablet
    preferredTPM:
      persistent: true
    preferredNetworkInterfaceMultiQueue: true
  
  # ═══ 時鐘配置 ═══
  clock:
    preferredClockOffset:
      utc: {}
    preferredTimer:
      hpet:
        enabled: false
      pit:
        tickPolicy: delay
      rtc:
        tickPolicy: catchup
      hyperv: {}
  
  # ═══ HyperV Features ═══
  features:
    preferredAcpi: {}
    preferredApic: {}
    preferredHyperv:
      relaxed: {}
      vapic: {}
      spinlocks:
        spinlocks: 8191
      vpindex: {}
      runtime: {}
      synic: {}
      synictimer:
        direct: {}
      frequencies: {}
      reenlightenment: {}
      tlbflush: {}
      ipi: {}
      reset: {}
  
  # ═══ 韌體 ═══
  firmware:
    preferredUseBios: false
    preferredUseEfi: true
    preferredUseSecureBoot: true
  
  # ═══ Machine Type ═══
  machine:
    preferredMachineType: q35
```

::: info Instancetype 與 Preference
- **Instancetype**：定義硬體規格（CPU 數量、記憶體大小）— 類似 AWS EC2 instance type
- **Preference**：定義 Guest OS 偏好設定（HyperV、時鐘、裝置匯流排）— 類似 OS 配置模板

兩者分離的設計讓使用者只需選擇「規格」+「OS 類型」即可建立最佳化的 VM。
:::

## 常見問題排查

### BSOD 常見原因與解法

| 錯誤碼 | 可能原因 | 解法 |
|---|---|---|
| `CLOCK_WATCHDOG_TIMEOUT` | 未啟用 Relaxed | 啟用 `hyperv.relaxed` |
| `WHEA_UNCORRECTABLE_ERROR` | CPU 模式不相容 | 改用 `host-model` 或 `host-passthrough` |
| `INACCESSIBLE_BOOT_DEVICE` | 缺少 VirtIO 驅動 | 安裝 VirtIO 磁碟驅動或改用 SATA |
| `KERNEL_DATA_INPAGE_ERROR` | 磁碟 I/O 問題 | 檢查 PV 健康狀態、調整 cache 模式 |
| `HAL_INITIALIZATION_FAILED` | 時鐘配置錯誤 | 停用 HPET、啟用 HyperV Timer |

::: danger 排查步驟
1. 首先檢查 `virtctl console <vm-name>` 查看啟動畫面
2. 使用 `virtctl vnc <vm-name>` 連接 VNC 查看 BSOD 錯誤碼
3. 檢查 virt-launcher Pod 日誌：`kubectl logs <pod-name> -c compute`
4. 查看 libvirt 日誌：`kubectl exec <pod-name> -c compute -- cat /var/log/libvirt/qemu/*.log`
:::

### 時間同步問題

**症狀**：Windows VM 時間與主機不同步，時間快進或落後。

**解法**：

```yaml
# 確保以下配置正確
spec:
  domain:
    clock:
      utc: {}
      timer:
        hyperv: {}                   # 啟用 HyperV 時鐘
        hpet:
          enabled: false             # 停用 HPET
    features:
      hyperv:
        frequencies: {}              # TSC 頻率處理
        reenlightenment: {}          # TSC 頻率變更通知
```

並在 Windows Guest 中安裝 QEMU Guest Agent，啟用 NTP 同步。

### 網路不通問題

**症狀**：Windows VM 啟動後無網路連線。

**檢查清單**：

1. **缺少 VirtIO 網路驅動**：切換到 `model: e1000e` 測試
2. **防火牆阻擋**：Windows 防火牆可能阻擋 ICMP
3. **IP 配置問題**：使用 Guest Agent 檢查 IP
   ```bash
   virtctl guestosinfo <vm-name>
   ```
4. **masquerade 模式限制**：確認 Pod 網路正常

### 磁碟效能低問題

**症狀**：Windows VM 磁碟 IOPS 遠低於預期。

**最佳化清單**：

```yaml
# 1. 使用 virtio 匯流排
- disk:
    bus: virtio
  name: rootdisk
  
# 2. 設定 cache 和 io 模式
  cache: none
  io: native

# 3. 啟用 IO Threads
ioThreadsPolicy: auto

# 4. 啟用磁碟多佇列
devices:
  blockMultiQueue: true
```

如果使用 Ceph RBD 或其他分散式儲存：

```yaml
# 5. 使用 virtio-scsi（支援更多磁碟 + TRIM/discard）
- disk:
    bus: scsi
  name: datadisk
  cache: none
```

## 效能調校總結

| 類別 | 基礎配置 | 最佳化配置 | 效能提升 |
|---|---|---|---|
| **HyperV** | Relaxed + VAPIC + Spinlocks | 全部啟用 | 20-40% |
| **時鐘** | 預設 | HPET off + HyperV Timer | 5-15% |
| **CPU** | 預設拓撲 | preferCores + dedicatedCpu | 10-30% |
| **記憶體** | 預設 | HugePages 2Mi | 5-10% |
| **磁碟** | SATA | virtio + none cache + native IO | 300-1000% |
| **網路** | e1000 | virtio + multiqueue | 200-500% |

::: tip 最佳化優先順序
如果時間有限，按以下優先順序進行最佳化：
1. 🔴 **安裝 VirtIO 驅動**（影響最大）
2. 🟠 **啟用 HyperV Enlightenments**（避免 BSOD + 效能提升）
3. 🟡 **配置正確的時鐘**（穩定性 + 效能）
4. 🟢 **CPU Pinning + HugePages**（進一步效能提升）
5. 🔵 **多佇列 + IO Threads**（高負載場景）
:::
