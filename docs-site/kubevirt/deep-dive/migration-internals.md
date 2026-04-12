# Live Migration 實作深入剖析 — 從程式碼看遷移流程

## 概述

Live Migration（即時遷移）是 KubeVirt 中最為複雜的功能之一。它允許在不中斷虛擬機服務的前提下，將正在運行的 VMI（VirtualMachineInstance）從一個節點搬遷至另一個節點。整個流程橫跨 **四個核心元件** 的協作：

| 元件 | 角色 | 說明 |
|------|------|------|
| **virt-controller** | 遷移調度器 | 建立目標 Pod、管理遷移狀態機、協調整體流程 |
| **virt-handler (Source)** | 源端代理 | 啟動 migration proxy、監控遷移進度 |
| **virt-handler (Target)** | 目標端代理 | 準備目標環境、啟動 migration proxy |
| **virt-launcher (Source/Target)** | libvirt 執行器 | 實際呼叫 libvirt API 執行記憶體與磁碟資料傳輸 |

::: info 核心設計理念
KubeVirt 的遷移設計遵循 Kubernetes 原生模式——透過建立新的 Pod 作為遷移目標，而非直接操作節點。這使得遷移流程能夠充分利用 Kubernetes 的排程能力（affinity、resource requests、topology constraints）。
:::

### 完整架構圖

![KubeVirt Live Migration Architecture](/diagrams/kubevirt/kubevirt-migration-1.png)

---

## Migration Controller（virt-controller）

### 檔案位置

```
pkg/virt-controller/watch/migration/migration.go  （約 2695 行）
```

Migration Controller 是整個遷移流程的「大腦」。它負責接收 `VirtualMachineInstanceMigration` 資源的建立事件，驅動狀態機轉換，並協調源端與目標端的所有動作。

### 工作佇列優先級系統

Controller 使用一個 **優先級佇列**（Priority Queue）來處理遷移任務。不同狀態的遷移具有不同的處理優先級，確保正在運行中的遷移不會被新建立的遷移阻塞：

```go
const (
    QueuePriorityRunning           = 1000  // 正在運行中的遷移，最高優先
    QueuePrioritySystemCritical    = 100   // 系統關鍵遷移
    QueuePriorityUserTriggered     = 50    // 使用者手動觸發
    QueuePrioritySystemMaintenance = 20    // 系統維護觸發
    QueuePriorityDefault           = 0     // 預設優先級
    QueuePriorityPending           = -100  // 等待中的遷移，最低優先
)
```

::: tip 優先級設計意義
這套優先級系統確保了「已經在傳輸資料的遷移」優先獲得處理時間。例如，當一個遷移正在 `Running` 階段時（優先級 1000），新建立的 `Pending` 遷移（優先級 -100）不會搶佔 controller 的處理能力。
:::

### 主要函式

```go
// Execute 從優先級佇列取出一個遷移任務並執行
func (c *Controller) Execute() bool

// sync 是核心同步邏輯，處理單次遷移的狀態協調
func (c *Controller) sync(key string, migration *virtv1.VirtualMachineInstanceMigration,
    vmi *virtv1.VirtualMachineInstance, pods []*k8sv1.Pod) error

// updateStatus 根據當前 Pod 狀態與 VMI 狀態更新遷移物件的 Status
func (c *Controller) updateStatus(migration *virtv1.VirtualMachineInstanceMigration,
    vmi *virtv1.VirtualMachineInstance, pods []*k8sv1.Pod, syncError error) error

// processMigrationPhase 核心狀態機處理，根據當前 Phase 執行對應邏輯
func (c *Controller) processMigrationPhase(
    migration, migrationCopy *virtv1.VirtualMachineInstanceMigration,
    pod, attachmentPod *k8sv1.Pod,
    vmi *virtv1.VirtualMachineInstance,
    syncError error,
) error
```

---

## 完整狀態機

### Mermaid 狀態機圖

![Migration Phase State Machine](/diagrams/kubevirt/kubevirt-migration-2.png)

### 各 Phase 詳細說明

#### Phase 1: MigrationPhaseUnset（初始狀態）

當使用者建立 `VirtualMachineInstanceMigration` 資源後，Migration Controller 首先驗證 VMI 是否符合遷移條件：

- VMI 必須處於 `Running` 狀態
- VMI 不能已有進行中的遷移
- VMI 的 `LiveMigratable` condition 必須為 True
- 目前叢集的並行遷移數不能超過上限（預設 `ParallelMigrationsPerCluster = 5`）
- 單一節點的對外遷移數不能超過上限（預設 `ParallelOutboundMigrationsPerNode = 2`）

若通過所有檢查，Phase 轉為 `MigrationPending`。

#### Phase 2: MigrationPending（等待建立目標 Pod）

Controller 呼叫 `createTargetPod()` 建立目標端的 virt-launcher Pod。此階段也處理 backup volumes 與 utility volumes 的準備。

::: warning 注意事項
目標 Pod 的建立是一個關鍵步驟——它必須精確複製源端 Pod 的配置（記憶體、CPU、網路、儲存掛載），同時加入額外的 anti-affinity 規則確保不會排程到相同節點。
:::

#### Phase 3: MigrationScheduling（等待 Pod 排程）

Kubernetes Scheduler 接管排程，根據以下約束將 Pod 放置到適當節點：

- 資源需求（CPU、記憶體）
- CPU model/vendor label 匹配
- NUMA topology 約束
- Anti-affinity 排除源端節點
- PVC 可存取性
- SELinux level 匹配

#### Phase 4: MigrationScheduled（Pod 已排程）

目標 Pod 已經運行在目標節點上，等待目標端 virt-handler 偵測到 Pod 並開始準備。此階段 virt-handler（Target）會：

1. 偵測到新的 migration target Pod
2. 更新 VMI 狀態為 `PreparingTarget`

#### Phase 5: MigrationPreparingTarget（目標端準備中）

目標端最為繁忙的階段，virt-handler（Target）執行以下操作：

1. **建立目標 Domain** — 在目標節點的 libvirtd 中定義 VM Domain
2. **建立 Unix Socket** — 為 libvirt 遷移通道建立本地 socket
3. **啟動 Migration Proxy** — 設定 TCP → Unix Socket 的反向代理
4. **準備磁碟與網路** — 掛載必要的 Volume、設定網路介面
5. **回報 Ready** — 將分配到的 TCP port 寫入 VMI 狀態

#### Phase 6: MigrationTargetReady（目標端就緒）

目標端已完全準備好接收遷移資料。Controller 觸發源端開始實際的遷移操作。源端 virt-handler：

1. 啟動 Migration Proxy（Unix Socket → TCP）
2. 通知 virt-launcher 開始遷移

#### Phase 7: MigrationRunning（遷移進行中）

記憶體頁面開始從源端傳輸到目標端。此階段持續時間取決於：

- VM 記憶體大小
- 記憶體 dirty rate（寫入頻率）
- 網路頻寬
- 是否啟用 multifd 並行傳輸

#### Phase 8: MigrationSucceeded / MigrationFailed（完成或失敗）

- **成功**：VM 在目標端恢復執行，源端 Domain 被清除，源端 Pod 被刪除
- **失敗**：目標端 Pod 被清除，VM 繼續在源端執行，遷移物件標記失敗原因

---

## Target Pod 建立

### createTargetPod() 函式

```
pkg/virt-controller/watch/migration/migration.go → createTargetPod()
```

```go
func (c *Controller) createTargetPod(
    migration *virtv1.VirtualMachineInstanceMigration,
    vmi *virtv1.VirtualMachineInstance,
    sourcePod *k8sv1.Pod,
) error
```

此函式負責建立遷移目標端的 virt-launcher Pod。它必須精確匹配源端的環境，同時加入遷移專屬的配置。

### Source Pod 與 Target Pod 的差異

| 面向 | Source Pod | Target Pod |
|------|-----------|------------|
| **建立者** | VM Controller | Migration Controller |
| **Annotation** | 無遷移標記 | `kubevirt.io/migrationTargetFor: <vmi-uid>` |
| **Anti-affinity** | 無（或使用者定義） | 強制排除源端節點 |
| **CPU Model Labels** | 依據節點能力 | 匹配源端 CPU model/vendor |
| **SELinux Level** | 自動分配 | 匹配源端 level（確保共享儲存可存取） |
| **Node Selector** | 使用者定義 | 加入 CPU feature labels |
| **Resources** | 依據 VMI spec | 複製源端（含 memory overhead） |

### CPU Model / Vendor Label 匹配

當 VM 使用 `host-model` CPU 模式時，Target Pod 的 nodeSelector 會加入源端節點的 CPU 特性 label，確保目標節點具有相容的 CPU：

```yaml
nodeSelector:
  cpu-model.node.kubevirt.io/Skylake-Server: "true"
  cpu-vendor.node.kubevirt.io/Intel: "true"
  cpu-feature.node.kubevirt.io/vmx: "true"
```

### Anti-affinity 規則

Target Pod 使用 `requiredDuringSchedulingIgnoredDuringExecution` 強制排除源端節點：

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: kubevirt.io/created-by
          operator: In
          values:
          - "<vmi-uid>"
      topologyKey: kubernetes.io/hostname
```

---

## Migration Proxy（TCP 代理）

### 檔案位置

```
pkg/virt-handler/migration-proxy/migration-proxy.go  （約 543 行）
```

### Port 配置

```go
const (
    LibvirtDirectMigrationPort = 49152  // libvirt 直接遷移通道（記憶體傳輸）
    LibvirtBlockMigrationPort  = 49153  // Block migration 通道（磁碟資料傳輸）
)
```

### ProxyManager 介面

```go
type ProxyManager interface {
    // 目標端：監聽 TCP port，轉發到本地 Unix Socket
    StartTargetListener(key string, targetUnixFiles []string) error
    GetTargetListenerPorts(key string) map[string]int
    StopTargetListener(key string)

    // 源端：監聽 Unix Socket，轉發到目標端 TCP port
    StartSourceListener(key string, targetAddress string,
        destSrcPortMap map[string]int, baseDir string) error
    GetSourceListenerFiles(key string) []string
    StopSourceListener(key string)

    OpenListenerCount() int
    InitiateGracefulShutdown()
}
```

### Unix Socket ↔ TCP Proxy 架構

![Migration Proxy Data Flow](/diagrams/kubevirt/kubevirt-migration-3.png)

遷移資料流的完整路徑：

1. **源端 libvirtd** 將遷移資料寫入本地 **Unix Socket**
2. **Source Proxy** 讀取 Unix Socket 資料，透過 **TCP（可選 TLS）** 傳送到目標端
3. **Target Proxy** 接收 TCP 資料，寫入目標端的 **Unix Socket**
4. **目標端 libvirtd** 從 Unix Socket 讀取並重建 VM 狀態

### TLS 加密

::: danger 安全考量
遷移資料流包含 VM 的完整記憶體內容（可能含有密碼、金鑰等敏感資料）。KubeVirt 支援透過 TLS 加密遷移通道。啟用後，Source Proxy 與 Target Proxy 之間的 TCP 連線將使用 mutual TLS 進行加密與認證。
:::

Migration Proxy 內建 TLS 支援，使用 `serverTLSConfig`、`clientTLSConfig` 與 `migrationTLSConfig` 三組配置：

```go
type migrationProxyManager struct {
    sourceProxies      map[string][]*migrationProxy
    targetProxies      map[string][]*migrationProxy
    serverTLSConfig    *tls.Config  // 目標端 TLS（作為 server）
    clientTLSConfig    *tls.Config  // 源端 TLS（作為 client）
    migrationTLSConfig *tls.Config  // 遷移專用 TLS
    managerLock        sync.Mutex
    isShuttingDown     bool
}
```

---

## libvirt Migration API 呼叫

### 檔案位置

```
pkg/virt-launcher/virtwrap/live-migration-source.go  （約 1156 行）
```

這是整個遷移流程中最核心的檔案——它直接呼叫 libvirt C API 來執行實際的記憶體與磁碟資料傳輸。

### 核心函式：migrateHelper()

```go
func (l *LibvirtDomainManager) migrateHelper(
    vmi *v1.VirtualMachineInstance,
    options *cmdclient.MigrationOptions,
) error
```

此函式的工作流程：

1. 根據 VMI 名稱查詢 libvirt Domain
2. 檢查 Domain 是否處於 paused 狀態
3. 呼叫 `generateMigrationFlags()` 產生遷移旗標
4. 呼叫 `generateMigrationParams()` 產生遷移參數
5. 啟動 `migrationMonitor` 進行進度監控
6. **呼叫 `dom.MigrateToURI3(dstURI, params, migrateFlags)`**
7. 記錄遷移結果

### generateMigrationParams() 完整參數

```go
func generateMigrationParams(
    dom cli.VirDomain,
    vmi *v1.VirtualMachineInstance,
    options *cmdclient.MigrationOptions,
    virtShareDir string,
    domSpec *api.DomainSpec,
) (*libvirt.DomainMigrateParameters, error)
```

| 參數 | 型別 | 說明 |
|------|------|------|
| `URI` | `string` | 目標端 Unix Socket 路徑，如 `unix:///var/run/kubevirt/migrationproxy/<vmi-uid>_direct` |
| `Bandwidth` | `uint64` | 遷移頻寬限制（MiB/s），0 表示無限制 |
| `DestXML` | `string` | 目標端 Domain XML（透過 `MigratableXML()` 產生後修改） |
| `PersistXML` | `string` | 持久化 Domain XML |
| `DestName` | `string` | 目標端 Domain 名稱 |
| `ParallelConnections` | `int` | Multifd 並行連線數（預設 0 = 不啟用） |
| `MigrateDisks` | `[]string` | 需要遷移的磁碟 target 列表（Storage migration 使用） |
| `DisksURI` | `string` | Block migration 專用 Unix Socket 路徑 |

### generateMigrationFlags() 完整旗標

```go
func generateMigrationFlags(
    isBlockMigration, migratePaused bool,
    options *cmdclient.MigrationOptions,
) libvirt.DomainMigrateFlags
```

| Flag | 條件 | 說明 |
|------|------|------|
| `MIGRATE_LIVE` | 始終啟用 | 即時遷移，VM 持續運行 |
| `MIGRATE_PEER2PEER` | 始終啟用 | 源端 libvirtd 直接連線目標端 |
| `MIGRATE_PERSIST_DEST` | 始終啟用 | 在目標端持久化 Domain 定義 |
| `MIGRATE_NON_SHARED_INC` | Block migration | 增量複製非共享磁碟 |
| `MIGRATE_UNSAFE` | 使用者配置 | 跳過安全檢查（如 cache=none） |
| `MIGRATE_AUTO_CONVERGE` | 使用者配置 | 透過 vCPU 節流確保收斂 |
| `MIGRATE_POSTCOPY` | 使用者配置 | 啟用 Post-copy 模式 |
| `MIGRATE_PAUSED` | VM 已暫停 | 遷移後保持暫停狀態 |
| `MIGRATE_PARALLEL` | Multifd 啟用 | 使用多通道並行傳輸 |

### 實際 API 呼叫

```go
err = dom.MigrateToURI3(dstURI, params, migrateFlags)
if err != nil {
    l.setMigrationResult(true, err.Error(), "")
    log.Log.Object(vmi).Errorf("migration failed with error: %v", err)
    return fmt.Errorf(
        "error encountered during MigrateToURI3 libvirt api call: %v", err)
}
```

::: info MigrateToURI3 是什麼？
`MigrateToURI3` 是 libvirt 提供的第三代遷移 API。相較於 `MigrateToURI` 和 `MigrateToURI2`，它支援透過 `DomainMigrateParameters` 結構傳遞更豐富的參數，包括並行連線數、磁碟遷移列表等進階功能。
:::

---

## Pre-copy vs Post-copy Migration

### Pre-copy 遷移（預設模式）

Pre-copy 是 KubeVirt 的預設遷移策略。其運作原理為 **迭代式記憶體複製**：

![Pre-copy Migration](/diagrams/kubevirt/kubevirt-migration-4.png)

**優點**：切換瞬間的 downtime 極短（毫秒級）  
**缺點**：若 dirty rate 高於傳輸速度，可能永遠無法收斂

### Post-copy 遷移

Post-copy 採用相反的策略——**先切換執行，再按需取回頁面**：

![Post-copy Migration](/diagrams/kubevirt/kubevirt-migration-5.png)

**優點**：保證收斂（已傳送的頁面不會再變 dirty）  
**缺點**：切換後存在效能影響，源端 crash 會導致 VM 遺失資料

### KubeVirt 的自動切換邏輯

KubeVirt 不會一開始就使用 Post-copy。而是在 Pre-copy 超過可接受時間後，**自動切換**到 Post-copy：

```go
func (m *migrationMonitor) shouldAssistMigrationToComplete(elapsed int64) bool {
    return m.options.AllowWorkloadDisruption && m.shouldTriggerTimeout(elapsed)
}
```

切換的完整決策樹：

```go
case m.shouldAssistMigrationToComplete(elapsed):
    if m.options.AllowPostCopy && !m.vmi有VFIO設備() {
        // 切換到 Post-copy
        dom.MigrateStartPostCopy(0)
        // 設定模式為 MigrationPostCopy
    } else if m.vmi有VFIO設備() {
        // VFIO 設備：設定大 downtime，觸發 QEMU switchover
        downtime := min(acceptableCompletionTime*2*1000, 2_000_000)
        // 設定模式為 MigrationPaused
    } else {
        // Fallback：暫停 VM 以完成遷移
        dom.Suspend()
        m.acceptableCompletionTime *= 2  // 雙倍超時
        // 設定模式為 MigrationPaused
    }
```

::: danger Post-copy 限制
Post-copy **不支援** VFIO（GPU passthrough）設備。因為 VFIO 設備狀態無法透過 page-fault 機制按需取回。對於使用 GPU passthrough 的 VM，KubeVirt 會改用暫停 VM + 設定大 downtime 的方式完成遷移。
:::

---

## Multifd 並行傳輸

### 原理

傳統遷移使用 **單一 TCP 連線** 傳送所有記憶體資料。Multifd（Multiple File Descriptor）允許開啟多個並行通道，將記憶體頁面分散到多個 TCP 連線上同時傳輸：

```
傳統模式：
  [全部記憶體資料] ───單一通道──→ [目標端]

Multifd 模式：
  [記憶體資料 1/4] ───通道 1──→ [目標端]
  [記憶體資料 2/4] ───通道 2──→ ──合併──→
  [記憶體資料 3/4] ───通道 3──→
  [記憶體資料 4/4] ───通道 4──→
```

### 配置方式

透過 `MigrationConfiguration` 或 `MigrationPolicy` 設定 `ParallelMigrationThreads`：

```yaml
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
spec:
  configuration:
    migrationConfiguration:
      parallelMigrationThreads: 4
```

在程式碼中，此設定對應到以下參數與旗標：

```go
// generateMigrationParams 中
params.ParallelConnections = options.ParallelMigrationThreads

// generateMigrationFlags 中
if options.ParallelMigrationThreads > 0 {
    migrateFlags |= libvirt.MIGRATE_PARALLEL
}
```

::: tip 效能提升
在 10 Gbps 網路環境下，啟用 4 個並行通道可以將遷移速度提升 2-3 倍。單一 TCP 連線受限於 Linux 核心 TCP 視窗大小與 CPU 加密效能，多通道能有效利用高頻寬網路。
:::

---

## Auto-converge

### 問題場景

當 VM 的記憶體 dirty rate（每秒修改的記憶體量）持續超過網路傳輸速度時，Pre-copy 遷移永遠無法收斂——每一輪傳送的 dirty pages 都比上一輪多。

### 解決方案

Auto-converge 透過 **逐步降低 vCPU 執行速度** 來減少 dirty rate：

1. 第一次偵測到不收斂：降低 vCPU 速度 20%
2. 仍不收斂：繼續降低，每次增加 10%
3. 最高降至 99% 的 CPU 節流

```go
// 在 generateMigrationFlags 中
if options.AllowAutoConverge {
    migrateFlags |= libvirt.MIGRATE_AUTO_CONVERGE
}
```

::: warning 效能影響
Auto-converge 會顯著降低 VM 內部工作負載的效能。對於延遲敏感的應用程式，應考慮使用 Post-copy 替代。兩者可以同時啟用——KubeVirt 會先嘗試 Auto-converge，若仍超時，再切換到 Post-copy（如果 `AllowWorkloadDisruption` 為 true）。
:::

---

## Migration 進度監控

### migrationMonitor 結構

```go
type migrationMonitor struct {
    l       *LibvirtDomainManager
    vmi     *v1.VirtualMachineInstance
    options *cmdclient.MigrationOptions
    migrationErr chan error

    start              int64   // 遷移開始的 Unix 時間戳（奈秒）
    lastProgressUpdate int64   // 上次進度更新時間
    progressWatermark  uint64  // 已傳送資料量的高水位線
    remainingData      uint64  // 剩餘待傳資料量

    progressTimeout          int64  // 無進度超時（秒）
    acceptableCompletionTime int64  // 可接受完成時間（秒）
    migrationFailedWithError error
}
```

### dom.GetJobStats() 監控欄位

virt-launcher 透過 `dom.GetJobStats(0)` 定期查詢 libvirt，取得遷移進度資訊：

| 欄位 | 說明 |
|------|------|
| `DataRemaining` | 剩餘待傳資料量（bytes） |
| `DataProcessed` | 已處理資料量（bytes） |
| `MemRemaining` | 剩餘待傳記憶體（bytes） |
| `MemProcessed` | 已處理記憶體（bytes） |
| `MemBps` | 記憶體傳輸速度（bytes/sec） |
| `MemDirtyRate` | 記憶體髒頁產生速率（pages/sec） |
| `MemIteration` | Pre-copy 迭代次數 |
| `MemPostcopyReqs` | Post-copy 模式下的 page fault 請求數 |
| `TimeElapsed` | 已經過時間（毫秒） |

```go
jobStats, err = dom.GetJobStats(0)
if err != nil {
    logger.Reason(err).Warning("failed to get domain job info, will retry")
    continue
}
```

### 超時計算

```go
monitor := &migrationMonitor{
    progressTimeout:          options.ProgressTimeout,
    // 完成超時 = 每 GiB 秒數 × VM 遷移資料大小（GiB）
    acceptableCompletionTime: options.CompletionTimeoutPerGiB *
                              getVMIMigrationDataSize(vmi, l.ephemeralDiskDir),
}
```

預設值（來自 `pkg/virt-config/virt-config.go`）：

```go
const (
    MigrationProgressTimeout         int64 = 150  // 150 秒無進度則判定卡住
    MigrationCompletionTimeoutPerGiB int64 = 150  // 每 GiB 允許 150 秒
)
```

::: info 超時計算範例
一個 16 GiB 記憶體的 VM：
- **ProgressTimeout** = 150 秒（與記憶體大小無關）
- **CompletionTimeout** = 150 × 16 = 2400 秒（40 分鐘）

如果在 2400 秒後遷移仍未完成，且 `AllowWorkloadDisruption = true`，則觸發 Post-copy 或暫停。否則取消遷移。
:::

### 何時觸發 Abort

```go
// 情況 1：遷移完全卡住（無任何進度）
case !m.isMigrationProgressing():
    err := dom.AbortJob()
    // "Live migration stuck for %d seconds and has been aborted"

// 情況 2：超過可接受完成時間，且未啟用 workload disruption
case m.shouldTriggerTimeout(elapsed):
    err := dom.AbortJob()
    // "Live migration is not completed after %d seconds and has been aborted"
```

---

## Migration Network

### 專用遷移網路介面

KubeVirt 支援設定專用的遷移網路，將遷移流量與一般 Pod 網路流量分離。專用介面名稱為 `migration0`：

```go
// staging/src/kubevirt.io/api/core/v1/types.go
MigrationInterfaceName string = "migration0"
```

### FindMigrationIP() 函式

```go
// pkg/virt-handler/migration.go
func FindMigrationIP(migrationIp string) (string, error) {
    ief, err := net.InterfaceByName(v1.MigrationInterfaceName) // "migration0"
    if err != nil {
        return migrationIp, nil  // 無專用介面，fallback 使用 Pod IP
    }

    addrs, err := ief.Addrs()
    if err != nil {
        return migrationIp, fmt.Errorf(
            "%s present but doesn't have an IP", v1.MigrationInterfaceName)
    }

    for _, addr := range addrs {
        if !addr.(*net.IPNet).IP.IsGlobalUnicast() {
            continue  // 跳過 link-local、loopback、multicast
        }
        ip := addr.(*net.IPNet).IP.To16()  // IPv6 優先
        if ip != nil {
            return ip.String(), nil
        }
    }

    return migrationIp, fmt.Errorf("no IP found on %s", v1.MigrationInterfaceName)
}
```

### IPv6 優先選擇邏輯

函式使用 `To16()` 進行轉換——它會回傳第一個 Global Unicast 位址。由於介面上 IPv6 位址通常排在 IPv4 之前，因此實際上優先選擇 IPv6：

1. 嘗試找到 `migration0` 介面
2. 過濾出 Global Unicast 位址（排除 link-local）
3. 使用 `To16()` 轉換（IPv4 會被映射為 IPv4-mapped IPv6）
4. 回傳第一個符合條件的位址

### 沒有專用網路時的 Fallback

若節點沒有 `migration0` 介面，函式直接回傳原始的 `migrationIp` 參數（通常為 Pod 的 IP 位址），遷移流量會走一般的 Pod 網路。

```yaml
# 配置專用遷移網路（使用 Multus CNI）
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: migration-network
  namespace: kubevirt
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "name": "migration-bridge",
      "type": "bridge",
      "bridge": "migration-br",
      "ipam": { "type": "whereabouts", "range": "10.10.10.0/24" }
    }
```

---

## Storage Migration（Volume Migration）

### 原理

除了記憶體之外，KubeVirt 也支援遷移 VM 的本地磁碟。這在源端與目標端不共享儲存的情況下特別有用。Block migration 使用 `MIGRATE_NON_SHARED_INC` flag，透過獨立的 TCP 通道傳輸磁碟資料。

### 相關旗標與參數

```go
// Flag
migrateFlags |= libvirt.MIGRATE_NON_SHARED_INC

// 參數
params.MigrateDisks = []string{"vda", "vdb"}  // 需要遷移的磁碟 target
params.DisksURI = "unix:///var/run/kubevirt/migrationproxy/<uid>_block"
```

### configureLocalDiskToMigrate()

```go
func configureLocalDiskToMigrate(
    dom *libvirtxml.Domain,
    vmi *v1.VirtualMachineInstance,
) error
```

此函式處理磁碟遷移時的 Domain XML 轉換，支援兩種轉換方向：

| 轉換方向 | 源端 | 目標端 | 範例場景 |
|----------|------|--------|----------|
| `fsSrcBlockDst` | Filesystem（qcow2 file） | Block device | 從本地 PVC 遷移到 iSCSI |
| `blockSrcFsDst` | Block device | Filesystem（qcow2 file） | 從 iSCSI 遷移到本地 PVC |

核心邏輯：

```go
// 計算磁碟虛擬大小
size, err := getDiskVirtualSizeFunc(diskPath)

// 設定 disk slices（讓 libvirt 知道確切的資料大小）
dom.Devices.Disks[i].Source.Slices = &libvirtxml.DomainDiskSlices{
    Slices: []libvirtxml.DomainDiskSlice{{
        Type:   "storage",
        Offset: 0,
        Size:   uint(size),
    }},
}

// Filesystem → Block 轉換
dom.Devices.Disks[i].Source.Block = &libvirtxml.DomainDiskSourceBlock{
    Dev: "/dev/" + name,
}
dom.Devices.Disks[i].Source.File = nil

// Block → Filesystem 轉換
dom.Devices.Disks[i].Source.File = &libvirtxml.DomainDiskSourceFile{
    File: hostdisk.GetMountedHostDiskDir(name) + "disk.img",
}
dom.Devices.Disks[i].Source.Block = nil
```

::: warning Storage Migration 限制
以下情況**不支援** Storage Migration：
- **Hotplug volumes** — 動態掛載的磁碟
- **Filesystem volumes** — 9p/virtiofs 共享目錄
- **Shareable disks** — 設定為 shareable 的磁碟
- **LUN disks** — 直接透傳的 LUN 設備
:::

---

## Migration Policy CRD

### MigrationPolicy Spec

```go
// staging/src/kubevirt.io/api/migrations/v1alpha1/types.go
type MigrationPolicySpec struct {
    Selectors               *Selectors         `json:"selectors"`
    AllowAutoConverge       *bool              `json:"allowAutoConverge,omitempty"`
    BandwidthPerMigration   *resource.Quantity `json:"bandwidthPerMigration,omitempty"`
    CompletionTimeoutPerGiB *int64             `json:"completionTimeoutPerGiB,omitempty"`
    AllowPostCopy           *bool              `json:"allowPostCopy,omitempty"`
    AllowWorkloadDisruption *bool              `json:"allowWorkloadDisruption,omitempty"`
}
```

### Matching 演算法

MigrationPolicy 使用 **label selector** 進行匹配。Controller 會遍歷所有 MigrationPolicy，找到最匹配的那一個：

```go
func (c *Controller) matchMigrationPolicy(
    vmi *virtv1.VirtualMachineInstance,
    clusterMigrationConfiguration *virtv1.MigrationConfiguration,
) error
```

匹配邏輯：
1. 取得所有 `MigrationPolicy` 物件
2. 對每個 Policy，檢查其 `Selectors.NamespaceSelector` 是否匹配 VMI 所在 Namespace 的 labels
3. 對每個 Policy，檢查其 `Selectors.VirtualMachineInstanceSelector` 是否匹配 VMI 的 labels
4. 選擇匹配分數最高的 Policy
5. 將結果寫入 `vmi.Status.MigrationState.MigrationPolicyName` 與 `MigrationConfiguration`

### YAML 範例

```yaml
apiVersion: migrations.kubevirt.io/v1alpha1
kind: MigrationPolicy
metadata:
  name: high-performance-migration
spec:
  # 可配置參數
  allowAutoConverge: true
  allowPostCopy: false
  allowWorkloadDisruption: true
  bandwidthPerMigration: "1Gi"           # 限制每次遷移使用 1 GiB/s 頻寬
  completionTimeoutPerGiB: 300           # 每 GiB 允許 300 秒

  # Label Selector
  selectors:
    namespaceSelector:
      environment: "production"          # 匹配有此 label 的 Namespace
    virtualMachineInstanceSelector:
      workload-type: "database"          # 匹配有此 label 的 VMI
```

```yaml
---
apiVersion: migrations.kubevirt.io/v1alpha1
kind: MigrationPolicy
metadata:
  name: low-priority-migration
spec:
  allowAutoConverge: false
  allowPostCopy: true
  allowWorkloadDisruption: true
  bandwidthPerMigration: "256Mi"
  completionTimeoutPerGiB: 600
  selectors:
    namespaceSelector:
      environment: "staging"
    virtualMachineInstanceSelector:
      workload-type: "batch"
```

---

## Migration 取消

### 預交接取消（Handoff 前）

當遷移尚未進入 `Running` 階段（即記憶體傳輸尚未開始），取消操作只需 **刪除 Target Pod**：

1. 使用者設定 `migration.Status.Phase = MigrationFailed` 或刪除 Migration 物件
2. Controller 偵測到取消請求
3. Controller 刪除 Target Pod
4. Target 端 virt-handler 清理相關資源
5. VMI 繼續在源端正常運行

### 後交接取消（Handoff 後）

當遷移已在 `Running` 階段，記憶體正在傳輸中，需要呼叫 libvirt API 取消：

```go
// pkg/virt-launcher/virtwrap/live-migration-source.go
if jobInfo.Type == libvirt.DOMAIN_JOB_UNBOUNDED {
    err := dom.AbortJob()
    if err != nil {
        log.Log.Object(vmi).Reason(err).Error("failed to cancel migration")
        l.setMigrationAbortStatus(v1.MigrationAbortFailed)
        return
    }
}
```

### AbortStatus

```go
type MigrationAbortStatus string

const (
    MigrationAbortSucceeded  MigrationAbortStatus = "Succeeded"   // 成功取消
    MigrationAbortInProgress MigrationAbortStatus = "Aborting"    // 取消進行中
    MigrationAbortFailed     MigrationAbortStatus = "Failed"      // 取消失敗
)
```

### 清理流程

![Migration Abort &amp; Cleanup Flow](/diagrams/kubevirt/kubevirt-migration-6.png)

---

## 完整遷移流程時序圖

![完整遷移流程時序圖](/diagrams/kubevirt/kubevirt-migration-7.png)

---

## 常用操作與監控指令

### 觸發遷移

```bash
# 建立遷移物件
cat <<EOF | kubectl apply -f -
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstanceMigration
metadata:
  name: my-migration
  namespace: default
spec:
  vmiName: my-vm
EOF

# 或使用 virtctl
virtctl migrate my-vm
```

### 監控遷移狀態

```bash
# 查看遷移物件狀態
kubectl get vmim my-migration -o yaml

# 即時監控遷移進度
kubectl get vmim -w

# 查看 VMI 的 migrationState
kubectl get vmi my-vm -o jsonpath='{.status.migrationState}' | jq .
```

### 查看遷移相關事件

```bash
# 查看與遷移相關的事件
kubectl get events --field-selector reason=Migrating
kubectl get events --field-selector reason=Migrated
kubectl get events --field-selector reason=PreparingTarget
```

### 取消遷移

```bash
# 刪除遷移物件即可取消
kubectl delete vmim my-migration

# 或使用 virtctl
virtctl migrate-cancel my-vm
```

### 查看遷移相關 Pod

```bash
# 查看 target pod
kubectl get pods -l kubevirt.io=virt-launcher \
  --field-selector status.phase=Running

# 查看 target pod 的詳細資訊
kubectl describe pod <target-pod-name>
```

### 查看遷移相關指標

```bash
# Prometheus 查詢（若已整合）
# 遷移成功次數
kubevirt_vmi_migration_succeeded_total

# 遷移失敗次數
kubevirt_vmi_migration_failed_total

# 遷移持續時間
kubevirt_vmi_migration_phase_transition_time_from_creation_seconds

# 遷移資料傳輸量
kubevirt_vmi_migration_data_processed_bytes
kubevirt_vmi_migration_data_remaining_bytes
kubevirt_vmi_migration_dirty_memory_rate_bytes

# 遷移記憶體傳輸速度
kubevirt_vmi_migration_disk_transfer_rate_bytes
```

### 檢查 MigrationPolicy

```bash
# 列出所有 MigrationPolicy
kubectl get migrationpolicies

# 查看特定 Policy 的詳細配置
kubectl get migrationpolicy high-performance-migration -o yaml

# 確認 VMI 匹配到的 Policy
kubectl get vmi my-vm -o jsonpath='{.status.migrationState.migrationPolicyName}'
```

---

## 與 VMware vMotion 的比較

| 面向 | KubeVirt Live Migration | VMware vMotion |
|------|------------------------|----------------|
| **架構基礎** | Kubernetes Pod + libvirt/QEMU | vSphere ESXi Hypervisor |
| **遷移單元** | VMI（對應一個 Pod） | VM（對應一個 .vmx） |
| **排程器** | Kubernetes Scheduler | vSphere DRS |
| **網路傳輸** | TCP/TLS（經 Migration Proxy） | VMkernel vMotion NIC |
| **Pre-copy** | ✅ 支援（預設） | ✅ 支援（預設） |
| **Post-copy** | ✅ 支援 | ❌ 不支援 |
| **Storage Migration** | ✅ 支援（Block Migration） | ✅ 支援（Storage vMotion） |
| **跨叢集遷移** | ❌ 不支援 | ✅ Cross-vCenter vMotion |
| **Multifd 並行傳輸** | ✅ 支援 | ✅ 多 NIC 並行 |
| **加密** | TLS（可選） | 預設加密（vSphere 6.5+） |
| **GPU Passthrough** | 有限支援（暫停遷移） | ❌ 不支援（vSphere 8 部分支援） |
| **記憶體壓縮** | QEMU 內建 XBZRLE | ESXi 內建壓縮 |
| **自動收斂** | Auto-converge（vCPU 節流） | 內建 SDPS |
| **遷移策略** | MigrationPolicy CRD | DRS 規則 + VM/Host 群組 |
| **網路要求** | 任意 CNI（Pod 網路 or 專用網路） | VMkernel 專用網路 |
| **最大記憶體限制** | 無硬性限制（視超時設定） | 無硬性限制 |

### KubeVirt Live Migration 的優勢

::: tip 相較 vMotion 的獨特優勢
1. **雲原生整合** — 遷移作為 Kubernetes 資源管理，可透過 GitOps、CI/CD 自動化
2. **Post-copy 支援** — 保證遷移收斂，即使在高 dirty rate 場景
3. **MigrationPolicy CRD** — 細粒度的遷移策略管理，支援 namespace 和 VMI 級別
4. **開源可控** — 完整原始碼可審查與客製化
5. **多 CNI 彈性** — 可使用 Multus 搭配任意網路方案作為遷移網路
:::

### KubeVirt Live Migration 的限制

::: danger 目前限制
1. **不支援跨叢集遷移** — VM 只能在同一 Kubernetes 叢集內遷移
2. **VFIO 設備遷移受限** — GPU passthrough 的 VM 遷移需要暫停，可能造成秒級中斷
3. **無內建負載均衡器** — 不像 DRS 會自動觸發遷移以平衡資源，需要搭配 Descheduler
4. **遷移頻寬管理** — 目前僅支援每次遷移的頻寬限制，無全域頻寬池管理
5. **儲存遷移限制** — 不支援 hotplug volumes、shareable disks、LUN 類型的遷移
:::

---

## 總結

KubeVirt 的 Live Migration 實作是一個精密的分散式系統協作流程。從使用者建立 `VirtualMachineInstanceMigration` 資源開始，經過 Migration Controller 的狀態機驅動、Target Pod 的排程與準備、Migration Proxy 的網路通道建立，最終由 virt-launcher 呼叫 libvirt 的 `MigrateToURI3` API 完成實際的記憶體與磁碟資料傳輸。

理解這個流程有助於：

- **故障排查**：根據遷移卡在哪個 Phase，快速定位問題元件
- **效能調優**：選擇合適的 Pre-copy / Post-copy / Multifd 策略
- **容量規劃**：根據 VM 記憶體大小與 dirty rate 估算遷移時間與頻寬需求
- **安全強化**：確保 TLS 加密與專用遷移網路的正確配置
