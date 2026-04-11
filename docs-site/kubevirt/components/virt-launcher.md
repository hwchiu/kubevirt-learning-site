# virt-launcher

virt-launcher 是 KubeVirt 中**每個 VM 專屬的執行容器**，在 virt-launcher Pod 內運行，負責管理 libvirtd 程序和 QEMU 虛擬機器的實際執行。

## 職責概述

![virt-launcher Pod 結構](/diagrams/kubevirt/kubevirt-virt-launcher-pod.png)

## 部署資訊

| 項目 | 值 |
|------|-----|
| 部署型態 | Pod (由 virt-controller 建立) |
| 數量 | 每個執行中的 VMI 一個 |
| 通訊 | 僅 Unix Socket (無對外 Port) |
| 特殊權限 | Privileged (需要管理 libvirt/QEMU) |
| 網路 | 繼承 VMI 的 CNI 網路設定 |

## 核心介面：DomainManager

```go
// pkg/virt-launcher/virtwrap/manager.go
type DomainManager interface {
    // VM 生命週期
    SyncVMI(*v1.VirtualMachineInstance, bool, *opts) (*api.DomainSpec, error)
    KillVMI(*v1.VirtualMachineInstance) error
    DeleteVMI(*v1.VirtualMachineInstance) error
    SignalShutdownVMI(*v1.VirtualMachineInstance) error
    ResetVMI(*v1.VirtualMachineInstance) error
    SoftRebootVMI(*v1.VirtualMachineInstance) error

    // 暫停/恢復
    PauseVMI(*v1.VirtualMachineInstance) error
    UnpauseVMI(*v1.VirtualMachineInstance) error

    // 快照/備份
    FreezeVMI(*v1.VirtualMachineInstance, int32) error
    UnfreezeVMI(*v1.VirtualMachineInstance) error

    // Live Migration
    MigrateVMI(*v1.VirtualMachineInstance, *MigrationOptions) error
    PrepareMigrationTarget(*v1.VirtualMachineInstance, bool, *opts) error
    CancelVMIMigration(*v1.VirtualMachineInstance) error

    // 熱插拔
    HotplugHostDevices(vmi *v1.VirtualMachineInstance) error

    // 資訊查詢
    ListAllDomains() ([]*api.Domain, error)
    GetDomainStats() (*stats.DomainStats, error)
    GetGuestInfo() v1.VirtualMachineInstanceGuestAgentInfo
    InterfacesStatus() []api.InterfaceStatus

    // Guest Agent
    Exec(string, string, []string, int32) (string, error)
    GuestPing(string) error

    // 記憶體 Dump
    MemoryDump(vmi *v1.VirtualMachineInstance, dumpPath string) error

    // 備份
    BackupVirtualMachine(*v1.VirtualMachineInstance, *backupv1.BackupOptions) error
}
```

## VMI Spec → libvirt XML 轉換

這是 virt-launcher 最重要的功能之一：將 Kubernetes 宣告式的 VMI spec 轉換為 libvirt 的 XML 格式。

```go
// pkg/virt-launcher/virtwrap/converter/
//
// 主要轉換函數
func Convert_v1_VirtualMachineInstance_To_api_Domain(
    vmi *v1.VirtualMachineInstance,
    c *ConverterContext,
) (*api.Domain, error) {

    // CPU 轉換
    // VMI: {cores: 2, sockets: 1, threads: 1}
    // XML: <vcpu placement='static'>2</vcpu>
    //      <cpu mode='host-passthrough'>
    //        <topology sockets='1' cores='2' threads='1'/>
    //      </cpu>

    // Memory 轉換
    // VMI: {guest: "4Gi"}
    // XML: <memory unit='KiB'>4194304</memory>

    // Disk 轉換
    // VMI: {name: "rootdisk", disk: {bus: virtio}}
    //      Volume: {containerDisk: {image: "fedora:latest"}}
    // XML: <disk type='file' device='disk'>
    //        <driver name='qemu' type='qcow2' cache='none'/>
    //        <source file='/var/run/kubevirt/container-disks/disk_0.img'/>
    //        <target dev='vda' bus='virtio'/>
    //      </disk>

    // Network 轉換 (Masquerade)
    // VMI: {masquerade: {}}
    // XML: <interface type='ethernet'>
    //        <model type='virtio'/>
    //        <alias name='ua-default'/>
    //      </interface>
}
```

### 支援的架構

```go
// 架構判斷
switch vmi.Spec.Architecture {
case "amd64", "":
    // x86_64 — 預設 machine: q35
case "arm64":
    // ARM64 — machine: virt
case "ppc64le":
    // PowerPC — machine: pseries
case "s390x":
    // IBM Z — machine: s390-ccw-virtio
}
```

## 啟動流程

```go
// cmd/virt-launcher/main.go 啟動序列

func main() {
    // 1. 初始化 libvirt 事件循環
    libvirt.EventRegisterDefaultImpl()

    // 2. 連接到 libvirtd/virtqemud
    conn, err := cli.NewConnection("qemu:///system", ...)

    // 3. 初始化目錄
    initializeDirs(
        ephemeralDiskDir,    // /var/run/kubevirt-ephemeral-disks
        containerDiskDir,    // /var/run/kubevirt/container-disks
        hotplugDiskDir,      // /var/run/kubevirt/hotplug-disks
    )

    // 4. 建立 DomainManager
    manager := virtwrap.NewLibvirtDomainManager(conn, ...)

    // 5. 啟動 gRPC Command Server
    cmdServer := cmdserver.NewServer(socketPath, manager)
    cmdServer.Start()

    // 6. 標記 Ready (重新命名 socket 讓 virt-handler 知道)
    markReady(readyFile)

    // 7. 啟動 Domain 事件監控
    go manager.StartDomainEventMonitor()

    // 8. 主迴圈：等待命令與事件
    for {
        select {
        case event := <-domainEventChan:
            // 處理 domain 狀態改變
            handleDomainEvent(event)
        case <-stopChan:
            // 優雅關機
            return
        }
    }
}
```

## 重要常數

```go
const (
    defaultStartTimeout = 3 * time.Minute  // VM 啟動超時

    // 熱插拔記憶體 slot 數
    hotplugDefaultTotalPorts           = 8   // < 2GB 記憶體
    hotplugLargeMemoryDefaultTotalPorts = 16  // ≥ 2GB 記憶體

    // libvirt 連線
    LibvirtLocalConnectionTimeout = 15 * time.Second
)
```

## Network Phase 2（Unprivileged）

```go
// virt-launcher 執行 Phase 2 (不需要特殊權限)
// pkg/network/setup/

func (n *NetConf) SetupPodNetworkPhase2(domain *api.Domain) {
    for _, iface := range vmi.Spec.Interfaces {

        // 1. 讀取 Phase 1 快取的網路資訊
        cachedIface := n.loadCachedInterface(iface.Name)

        // 2. 將網路配置注入到 domain XML
        n.decorateConfig(domain, cachedIface)
        //    → 設定 MAC 地址
        //    → 設定 MTU
        //    → 指定 tap/bridge 介面

        // 3. 啟動 DHCP server (如 masquerade 模式)
        if iface.Masquerade != nil {
            n.startDHCP(cachedIface)
        }
    }
}
```

## Guest Agent 整合

virt-launcher 定期輪詢 QEMU Guest Agent 取得 VM 內部資訊：

```go
// pkg/virt-launcher/virtwrap/agent-poller/
//
// 輪詢間隔：10-30 秒
// 取得資訊：
// ├── Guest OS 資訊 (OS名稱、版本、核心)
// ├── 網路介面清單 (含 Guest 內部 IP)
// ├── 掛載的檔案系統
// ├── 登入使用者列表
// └── 系統負載

// 這些資訊更新到 VMI.Status.GuestOSInfo
// 可透過 virtctl guestosinfo 查詢
```

## 儲存管理

```go
// pkg/virt-launcher/virtwrap/storage/
//
// 支援的 Volume 掛載方式：
// ├── ContainerDisk  → /var/run/kubevirt/container-disks/
// ├── CloudInit      → ISO 格式，掛載為 cdrom
// ├── ConfigMap      → 掛載為 vFAT 磁碟
// ├── Secret         → 掛載為 vFAT 磁碟
// ├── DownwardAPI    → 掛載為 vFAT 磁碟
// ├── PVC            → 直接使用 PVC 掛載路徑
// └── EmptyDisk      → /var/run/kubevirt-private/empty-disks/
```

## 重要原始碼位置

| 功能 | 路徑 |
|------|------|
| 主程式入口 | `cmd/virt-launcher/main.go` |
| Domain Manager | `pkg/virt-launcher/virtwrap/manager.go` |
| VMI → XML 轉換 | `pkg/virt-launcher/virtwrap/converter/` |
| gRPC Command Server | `pkg/virt-launcher/virtwrap/cmd-server/` |
| Live Migration Source | `pkg/virt-launcher/virtwrap/live-migration-source.go` |
| Live Migration Target | `pkg/virt-launcher/virtwrap/live-migration-target.go` |
| Guest Agent 輪詢 | `pkg/virt-launcher/virtwrap/agent-poller/` |
| 網路設定 Phase 2 | `pkg/network/setup/` |
| 儲存管理 | `pkg/virt-launcher/virtwrap/storage/` |
| libvirt 連線封裝 | `pkg/virt-launcher/virtwrap/cli/` |
