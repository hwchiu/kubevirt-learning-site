# virt-handler

virt-handler 是 KubeVirt 的**節點代理 (Node Agent)**，以 DaemonSet 形式在每個 Kubernetes 節點上運行。它是 VMI 規格與實際 QEMU 虛擬機器之間的橋梁。

## 職責概述

```
virt-handler (每個節點一個)
├── 監控本節點上的 VMI 狀態
├── 呼叫 virt-launcher 啟動/停止/修改 VM
├── 設定 VM 網路 (Phase 1 - Privileged)
├── 管理 Live Migration (Source & Target)
├── 設備管理 (GPU, SR-IOV, vDPA)
├── 熱插拔 (CPU, Memory, Disk, NIC)
├── 容器磁碟掛載 (ContainerDisk)
└── 節點能力標籤管理
```

## 部署資訊

| 項目 | 值 |
|------|-----|
| 部署型態 | DaemonSet |
| 副本 | 每個 Linux 節點一個 |
| Metrics Port | 8185 |
| Namespace | `kubevirt` |
| 特殊權限 | `hostPID: true`, `hostNetwork: true` |
| 掛載 | hostPath: `/proc`, `/var/run/kubevirt`, `/var/lib/kubelet` |

## 核心資料結構

```go
// pkg/virt-handler/controller.go
type BaseController struct {
    host        string   // 本節點主機名稱
    clientset   kubecli.KubevirtClient

    // Work Queue
    queue workqueue.TypedRateLimitingInterface[string]

    // 快取
    vmiStore    cache.Store      // 本節點 VMI 列表
    domainStore cache.Store      // libvirt domain 狀態快取

    clusterConfig *virtconfig.ClusterConfig

    // 隔離偵測：找到 virt-launcher 的 PID 與 namespace
    podIsolationDetector isolation.PodIsolationDetector

    // Launcher 連線管理
    launcherClients launcherclients.LauncherClientsManager

    // Migration Proxy 管理
    migrationProxy migrationproxy.ProxyManager

    // 節點虛擬化能力資訊
    hypervisorNodeInfo hypervisor.HypervisorNodeInformation
    hypervisorRuntime  hypervisor.VirtRuntime
}
```

## 與 virt-launcher 的通訊

virt-handler 透過 **Unix Domain Socket** 與 virt-launcher 通訊（gRPC）：

```
Socket 路徑：/var/run/kubevirt-private/{VMI-UID}/cmd-server.sock

通訊協定：gRPC (Protocol Buffers)

主要呼叫：
├── SyncVMI          → 同步 VMI 規格 (建立/更新 libvirt domain)
├── KillVMI          → 強制終止 VM
├── SignalShutdownVMI → 發送 ACPI 關機訊號
├── PauseVMI         → 暫停 VM
├── UnpauseVMI       → 恢復 VM
├── MigrateVMI       → 開始 Live Migration
├── HotplugHostDevices → 熱插拔設備
├── Exec             → 在 Guest 執行命令
└── GuestPing        → 檢查 Guest Agent 存活
```

## VMI 協調流程

```go
// pkg/virt-handler/controller.go
func (d *VirtualMachineController) execute(key string) error {

    vmi := d.getLocalVMI(key)       // 從快取取得 VMI
    domain := d.getLocalDomain(key) // 從 libvirt 取得 domain 狀態

    // 決定動作
    switch {
    case vmi != nil && domain == nil:
        // VMI 存在但 domain 不存在 → 需要啟動 VM
        d.defaultExecute(vmi, domain)

    case vmi != nil && domain != nil:
        // 兩者都存在 → 同步狀態
        d.defaultExecute(vmi, domain)

    case vmi == nil && domain != nil:
        // VMI 已刪除但 domain 還在 → 需要清理
        d.deleteOrphanedDomain(domain)
    }
}
```

## 網路設定：兩階段架構

virt-handler 負責 **Phase 1 (Privileged)** 網路設定：

```go
// pkg/network/setup/netpod/
func (n *NetPod) Setup() error {

    // 在 virt-launcher Pod 的 network namespace 中執行

    for _, iface := range n.vmi.Spec.Interfaces {
        binding := n.getBinding(iface)

        // Phase 1 Steps:
        // 1. 收集 CNI 提供的資訊
        iface := n.discoverPodNetworkInterface(binding)
        //    → IP: 10.244.1.5/24
        //    → MAC: 52:54:00:xx:xx:xx
        //    → Gateway: 10.244.1.1
        //    → MTU: 1500

        // 2. 建立網路基礎設施
        n.preparePodNetworkInterfaces(binding)
        //    → 建立 bridge: br0
        //    → 建立 veth pair: veth0 ↔ eth0-nic
        //    → 移除 eth0 的 IP (稍後給 VM 用)

        // 3. 快取配置
        n.setCachedInterface(binding)
        //    → 存到 /proc/{pid}/root/var/run/kubevirt-private/vif-cache-eth0.json
    }
}
```

**為什麼需要 Phase 1 在 virt-handler 執行？**
- 需要 `CAP_NET_ADMIN` 才能修改 Pod 的 network namespace
- virt-launcher 只有最小權限，無法自行設定橋接

## Migration Source 管理

```go
// pkg/virt-handler/migration-source.go
type MigrationSourceController struct {
    // ...
}

func (c *MigrationSourceController) migrate(vmi *v1.VirtualMachineInstance) error {

    // 1. 找到 Migration 目標節點的 IP
    targetIP := c.findMigrationIP(migration)

    // 2. 設定 Migration Proxy
    //    建立 TCP 通道：source → proxy → target
    c.migrationProxy.StartSourceListener(migration, targetIP)

    // 3. 呼叫 virt-launcher 開始遷移
    opts := &MigrationOptions{
        MigrationUID:            migration.UID,
        Parallelism:             8,     // 8 個並行 channel
        UnsafeMigration:         false,
        AllowAutoConverge:       true,
        AllowPostCopy:           false,
    }
    c.launcherClient.MigrateVMI(vmi, opts)

    // 4. 監控遷移進度
    c.monitorMigration(vmi, migration)
}
```

### Migration 網路選擇

```go
func FindMigrationIP(migrationIfaces []net.Interface) string {
    // 優先使用 migration0 介面 (專用遷移網路)
    for _, iface := range migrationIfaces {
        if iface.Name == "migration0" {
            return iface.IP
        }
    }
    // 退而求其次使用 Pod 網路
    return podIP
}
```

## 設備管理

### Device Manager

```go
// pkg/virt-handler/device-manager/
//
// 管理的設備類型：
// ├── PCI 設備 (GPU、NIC)
// ├── USB 設備
// ├── Mediated 設備 (vGPU)
// ├── VFIO 設備 (SR-IOV VF)
// └── vDPA 設備
```

### 節點標籤

virt-handler 在啟動時為節點加上能力標籤：

```yaml
# 節點標籤範例
labels:
  kubevirt.io/schedulable: "true"
  # CPU 型號
  cpu-model.node.kubevirt.io/Skylake-Client: "true"
  # CPU 功能
  cpu-feature.node.kubevirt.io/vmx: "true"
  cpu-feature.node.kubevirt.io/svm: "true"
  # 裸機或虛擬化
  hyperv.node.kubevirt.io/base: "true"
  # 設備
  devices.kubevirt.io/kvm: "1"
```

## 重要常數

```go
const (
    defaultPort            = 8185
    defaultHost            = "0.0.0.0"
    defaultWatchdogTimeout = 30 * time.Second

    // Migration 並行通道數
    parallelMultifdMigrationThreads = 8

    // 事件訊息
    VMIDefined  = "VirtualMachineInstance defined."
    VMIStarted  = "VirtualMachineInstance started."
    VMIShutdown = "The VirtualMachineInstance was shut down."
    VMICrashed  = "The VirtualMachineInstance crashed."
    VMIMigrating = "VirtualMachineInstance is migrating."
)
```

## 日誌排查

```bash
# 查看特定節點的 virt-handler 日誌
NODE=worker-1
POD=$(kubectl get pod -n kubevirt -l kubevirt.io=virt-handler \
  --field-selector spec.nodeName=$NODE -o name)
kubectl logs -n kubevirt $POD --tail=200

# 查看 VMI 相關事件
kubectl describe vmi my-vm | grep -A5 Events

# 列出節點 KubeVirt 標籤
kubectl get node worker-1 --show-labels | tr ',' '\n' | grep kubevirt
```

## 重要原始碼位置

| 功能 | 路徑 |
|------|------|
| 主程式入口 | `cmd/virt-handler/main.go` |
| 控制器 | `pkg/virt-handler/controller.go` |
| Migration Source | `pkg/virt-handler/migration-source.go` |
| Migration Target | `pkg/virt-handler/migration-target.go` (確認目標端準備) |
| Migration Proxy | `pkg/virt-handler/migration-proxy/` |
| 設備管理 | `pkg/virt-handler/device-manager/` |
| ContainerDisk 掛載 | `pkg/virt-handler/container-disk/` |
| 熱插拔磁碟 | `pkg/virt-handler/hotplug-disk/` |
| 節點標籤 | `pkg/virt-handler/node-labeller/` |
| Launcher 連線 | `pkg/virt-handler/launcher-clients/` |
| 隔離偵測 | `pkg/virt-handler/isolation/` |
