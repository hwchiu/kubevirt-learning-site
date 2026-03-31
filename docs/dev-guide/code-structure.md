# 程式碼架構導覽

本文深入介紹 KubeVirt 程式碼庫的目錄結構、各元件的職責，以及開發者在新增功能或修復問題時需要了解的核心設計模式。

:::info 閱讀建議
建議先完成 [開發環境設置](./getting-started.md) 後再閱讀本文。在閱讀時，可以同步打開程式碼庫對照，加深理解。
:::

---

## 頂層目錄結構

```
kubevirt/
├── cmd/              # 各個 binary 的程式入口點（main 函式）
├── pkg/              # 核心業務邏輯套件（最主要的程式碼區域）
├── staging/          # API 型別定義與 Go 客戶端（類似 k8s staging）
├── tests/            # e2e 功能測試
├── tools/            # 建置輔助工具
├── vendor/           # Go 依賴套件（vendored dependencies）
├── images/           # 各元件的 Dockerfile
├── manifests/        # Kubernetes 資源清單範本（Jinja2 格式）
├── cluster-up/       # kubevirtci 開發叢集工具
├── hack/             # 建置腳本、CI 腳本
├── docs/             # 設計文件、API 文件
├── examples/         # KubeVirt 資源範例 YAML
└── bazel/            # Bazel 建置設定
```

:::tip 最重要的目錄
對於大多數功能開發，你會主要在這幾個目錄工作：
- `staging/src/kubevirt.io/api/` — 修改 API 型別時
- `pkg/` — 實作業務邏輯時
- `tests/` — 撰寫 e2e 測試時

`cmd/` 下的程式入口通常很精簡，主要邏輯都在 `pkg/` 中。
:::

---

## cmd/ 目錄 — Binary 入口點

`cmd/` 目錄下的每個子目錄對應一個獨立的 binary，各自有 `main.go` 作為程式入口。

```
cmd/
├── virt-api/              # Webhook + REST API server
├── virt-controller/       # 主控制器（VM/VMI 生命週期管理）
├── virt-handler/          # 節點代理（每個節點一個）
├── virt-launcher/         # VMI Pod 內的程序（每個 VM 一個）
├── virt-operator/         # KubeVirt 安裝/更新管理器
├── virtctl/               # 客戶端命令列工具
├── example-hook-sidecar/  # Hook sidecar 機制的範例實作
├── cniplugins/            # CNI 網路插件（passt, tap 等）
└── pr-creator/            # 自動化 PR 建立工具（CI 用）
```

### virt-api

**職責：** KubeVirt 的 API 前端，處理兩類請求：

1. **Kubernetes Admission Webhooks**：驗證（ValidatingAdmissionWebhook）和修改（MutatingAdmissionWebhook）KubeVirt 資源
2. **Subresource API**：實作 VM 的虛擬控制台、VNC 連線、串流介面等（透過 `virtctl` 使用）

```
cmd/virt-api/
└── virt-api.go    # 初始化 HTTP server，注冊 webhook 和 subresource handler
```

**相關 pkg：** `pkg/virt-api/`

### virt-controller

**職責：** KubeVirt 的核心控制平面，運行在 Kubernetes control plane 上，實作多個控制器（controller）：

- **VM Controller**：管理 `VirtualMachine` CR 的生命週期（啟動/停止/重啟）
- **VMI Controller**：管理 `VirtualMachineInstance` 的 Pod 建立和狀態追蹤
- **Migration Controller**：管理 `VirtualMachineInstanceMigration` 流程
- **DataVolume Controller**：監控 CDI DataVolume 狀態

```
cmd/virt-controller/
└── virt-controller.go    # 初始化並啟動各個 controller
```

**相關 pkg：** `pkg/virt-controller/`

### virt-handler

**職責：** 以 DaemonSet 形式運行在每個 Kubernetes 節點上，是 KubeVirt 在節點層面的代理。負責：

- 監聽分配到本節點的 VMI（VirtualMachineInstance）
- 呼叫 `virt-launcher` 啟動/停止 VM
- 管理節點層面的網路設定（Phase 2）
- 執行 VM 的 Live Migration 操作
- 回報節點的 VM 狀態

```
cmd/virt-handler/
└── virt-handler.go    # 初始化節點代理，啟動 VMI 監聽器
```

**相關 pkg：** `pkg/virt-handler/`

### virt-launcher

**職責：** 每個 VMI 都會有一個獨立的 `virt-launcher` Pod。它是 QEMU/KVM 虛擬機的包裝器：

- 管理 `libvirtd` 程序
- 透過 `libvirt` API 操作 QEMU/KVM
- 提供 gRPC 介面給 `virt-handler` 呼叫
- 監控 VM 狀態並回報

:::info 重要設計決策
每個 VMI 使用獨立的 Pod 和 `libvirtd`，是 KubeVirt 的核心設計。這樣的隔離確保單一 VM 的 crash 不會影響其他 VM，也使 Kubernetes 能正常管理 VM 的資源配額和生命週期。
:::

```
cmd/virt-launcher/
└── virt-launcher.go    # 初始化 libvirtd，啟動 gRPC server
```

**相關 pkg：** `pkg/virt-launcher/`

### virt-operator

**職責：** 管理 KubeVirt 自身的安裝、升級和設定。它監控 `KubeVirt` CR，並確保所有 KubeVirt 元件（virt-api、virt-controller、virt-handler）都以正確的版本運行。

```
cmd/virt-operator/
└── virt-operator.go    # 初始化 operator，監控 KubeVirt CR
```

**相關 pkg：** `pkg/virt-operator/`

### virtctl

**職責：** 使用者面向的命令列工具，擴展了 `kubectl` 的功能，提供 VM 相關操作：

```bash
# 常用 virtctl 指令範例
virtctl start myvm          # 啟動 VM
virtctl stop myvm           # 停止 VM
virtctl migrate myvm        # 觸發 Live Migration
virtctl console myvm        # 存取序列控制台
virtctl vnc myvm            # 開啟 VNC 連線
virtctl ssh myvm            # SSH 進入 VM
virtctl scp file.txt myvm:/ # 複製檔案到 VM
```

```
cmd/virtctl/
└── virtctl.go    # cobra root command，子命令在 pkg/virtctl/ 中
```

**相關 pkg：** `pkg/virtctl/`

### cniplugins

**職責：** 實作 KubeVirt 使用的 CNI（Container Network Interface）插件：

- **passt**：使用者空間的 TCP/IP stack，實作 passt 網路綁定
- **tap**：建立 TAP 裝置，用於 VM 網路介面

```
cmd/cniplugins/
├── passt-binding/     # passt CNI 插件
└── tap-device-maker/  # tap 裝置建立工具
```

---

## pkg/ 目錄 — 核心套件分類

`pkg/` 是 KubeVirt 最主要的業務邏輯所在，以下依功能分類詳細說明。

### API 伺服器邏輯：pkg/virt-api/

```
pkg/virt-api/
├── api/
│   └── v1/              # API handler 實作
├── webhooks/
│   ├── validating-webhook/    # 驗證型 webhook（拒絕不合法的資源）
│   └── mutating-webhook/      # 修改型 webhook（注入預設值）
└── rest/                      # Subresource REST API handler
    ├── console.go             # 序列控制台 handler
    ├── vnc.go                 # VNC handler
    └── streamer/              # 通用串流處理
```

**Webhook 範例：**
```go
// pkg/virt-api/webhooks/validating-webhook/admitters/vmi-admitter.go
// 驗證 VMI 資源是否合法
func (admitter *VMIAdmitter) Admit(ar *admissionv1.AdmissionReview) *admissionv1.AdmissionResponse {
    // 驗證 CPU topology、記憶體設定、磁碟設定等
    causes := admitter.validateVMISpec(...)
    if len(causes) > 0 {
        return webhookutils.ToAdmissionResponseWithMessage(
            http.StatusUnprocessableEntity, causes)
    }
    return &admissionv1.AdmissionResponse{Allowed: true}
}
```

### 控制器邏輯：pkg/virt-controller/

```
pkg/virt-controller/
├── services/
│   ├── rendervm.go         # 根據 VM spec 生成 VMI 定義
│   ├── rendertemplate.go   # 生成 virt-launcher Pod spec
│   └── config.go           # 設定相關服務
└── watch/
    ├── vm.go               # VirtualMachine 控制器（Reconcile loop）
    ├── vmi.go              # VMI 控制器（Reconcile loop）
    ├── migration.go        # Migration 控制器
    ├── node.go             # 節點控制器
    ├── snapshot/           # VM Snapshot 控制器
    ├── clone/              # VM Clone 控制器
    ├── export/             # VM Export 控制器
    └── instancetype/       # Instancetype 控制器
```

**Controller Reconcile Loop 範例：**
```go
// pkg/virt-controller/watch/vm.go（簡化版）
func (c *VMController) execute(key string) error {
    // 1. 從 cache 取得 VM 物件
    vm, err := c.vmLister.VirtualMachines(ns).Get(name)

    // 2. 取得相關的 VMI（若存在）
    vmi, err := c.vmiLister.VirtualMachineInstances(ns).Get(vm.Name)

    // 3. 根據 VM.spec.running 決定要建立還是刪除 VMI
    if shouldRun(vm) && !vmiExists {
        return c.startVM(vm)  // 建立 VMI
    }
    if !shouldRun(vm) && vmiExists {
        return c.stopVM(vm, vmi)  // 刪除 VMI
    }

    // 4. 同步 VM status
    return c.updateStatus(vm, vmi)
}
```

### 節點代理：pkg/virt-handler/

```
pkg/virt-handler/
├── vm.go              # VMI 生命週期核心邏輯（最重要的檔案）
├── migration.go       # Migration 相關邏輯
├── node-labeller/     # 節點能力偵測和標籤（CPU 功能、KVM 支援）
├── cgroup/            # cgroup 管理
└── isolation/         # VMI 隔離管理（uid, selinux 等）
```

**vm.go 的核心職責：**
```go
// pkg/virt-handler/vm.go（概念示意）
// VMI state machine 的主要入口
func (d *VirtualMachineController) Execute() bool {
    key, quit, err := d.Queue.Get()

    vmi, err := d.vmiLister.Get(key)

    switch {
    case vmiShouldBeRunning(vmi):
        d.defaultExecute(vmi)   // 確保 VM 在運行
    case vmiShouldBeMigrating(vmi):
        d.migrationExecute(vmi) // 執行 migration
    case vmiShouldBeDeleted(vmi):
        d.deleteExecute(vmi)    // 清理 VM
    }
    return true
}
```

### Launcher 邏輯：pkg/virt-launcher/

```
pkg/virt-launcher/
├── notify/            # 向 virt-handler 回報狀態的 gRPC 客戶端
└── virtwrap/          # libvirt 的包裝層（最核心的部分）
    ├── api/
    │   └── schema.go  # libvirt XML 對應的 Go 結構定義
    ├── converter/
    │   ├── converter.go      # VMI spec → libvirt XML 的主要轉換邏輯
    │   ├── network.go        # 網路介面轉換
    │   ├── storage.go        # 磁碟/儲存轉換
    │   └── cpu.go            # CPU 設定轉換
    ├── manager.go     # libvirt 操作的高階管理介面
    └── domain.go      # libvirt domain 的操作（建立、刪除、遷移）
```

:::info VMI Spec 到 libvirt XML 的轉換
`converter/converter.go` 是理解 KubeVirt 如何將 Kubernetes 的 VMI 定義轉換為實際 QEMU/KVM 虛擬機的關鍵入口。若你要新增虛擬硬體支援，通常需要修改這個檔案。

```go
// pkg/virt-launcher/virtwrap/converter/converter.go
func Convert_v1_VirtualMachineInstance_To_api_Domain(
    vmi *v1.VirtualMachineInstance,
    domain *api.Domain,
    c *ConverterContext) error {

    // 轉換 CPU 設定
    convertCPUTopology(vmi.Spec.Domain.CPU, &domain.Spec.CPU)

    // 轉換記憶體
    convertMemory(vmi.Spec.Domain.Memory, &domain.Spec.Memory)

    // 轉換磁碟
    for _, disk := range vmi.Spec.Domain.Devices.Disks {
        convertDisk(disk, &domain.Spec.Devices)
    }

    // 轉換網路介面
    for _, iface := range vmi.Spec.Domain.Devices.Interfaces {
        convertInterface(iface, &domain.Spec.Devices)
    }

    return nil
}
```
:::

### 網路：pkg/network/

```
pkg/network/
├── setup/
│   ├── network.go           # Phase 1/2 網路設定的主入口
│   ├── netpod/              # Network Pod 設定（Phase 1，在 infra container 中執行）
│   └── network_test.go
├── driver/
│   ├── bridge.go            # Bridge 網路綁定實作
│   ├── masquerade.go        # Masquerade (NAT) 網路綁定
│   ├── sriov.go             # SR-IOV 直通網路
│   ├── passt.go             # Passt 使用者空間網路
│   └── macvtap.go           # Macvtap 網路
├── namescheme/              # 網路介面命名邏輯
└── vmispec/                 # VMI spec 中網路相關的輔助函式
```

**Phase 1/2 網路設定的分離：**

```go
// Phase 1：在 virt-handler 的 infra 容器中執行
// 設定宿主機側的網路（TAP 裝置、bridge、iptables 等）
// pkg/network/setup/netpod/setup.go

// Phase 2：在 virt-launcher 容器中執行
// 設定 VM 側的網路（libvirt 網路介面定義）
// pkg/virt-launcher/virtwrap/converter/network.go
```

### 儲存：pkg/storage/

```
pkg/storage/
├── snapshot/          # VM Snapshot 和 Restore 邏輯
│   ├── snapshot.go    # Snapshot 建立流程
│   └── restore.go     # Restore 流程
├── clone/             # VM Clone 功能
│   └── clone.go
├── export/            # VM Export 功能
│   └── export.go
└── backend-storage/   # 後端儲存輔助函式
```

### Monitoring：pkg/monitoring/

```
pkg/monitoring/
├── metrics/
│   ├── virt-api/          # virt-api 的 Prometheus metrics
│   ├── virt-controller/   # virt-controller 的 metrics
│   ├── virt-handler/      # virt-handler 的 metrics（VM 效能指標）
│   └── virt-operator/     # virt-operator 的 metrics
└── rules/
    └── alerts/            # Prometheus AlertManager 規則定義
```

**新增 metric 的範例：**
```go
// pkg/monitoring/metrics/virt-handler/domainstats/domain_stats_collector.go
var (
    vmiMemoryResident = prometheus.NewDesc(
        "kubevirt_vmi_memory_resident_bytes",
        "Resident set size of the process running the domain.",
        []string{"node", "namespace", "name"},
        nil,
    )
)
```

### Instancetype：pkg/instancetype/

```
pkg/instancetype/
├── apply/           # 將 instancetype/preference 套用到 VMI spec
├── find/            # 尋找對應的 instancetype/preference 資源
├── expand/          # 展開 instancetype 到完整 spec
├── revision/        # Instancetype revision 管理（確保 VM 建立後不受 instancetype 更新影響）
└── compatibility/   # 向後相容性處理
```

### Feature Gates：pkg/util/

```
pkg/util/
├── featuregate/
│   └── feature_gate.go    # Feature gate 檢查函式
├── hardware/
│   ├── cpu.go             # CPU 功能偵測
│   └── memory.go          # 記憶體相關工具
├── pdbs/                  # PodDisruptionBudget 輔助函式
├── query/                 # Kubernetes list/watch query 輔助
└── types/                 # 通用型別工具
```

### Virtctl 子命令：pkg/virtctl/

```
pkg/virtctl/
├── vm/                # vm 子命令（start/stop/restart/migrate）
├── console/           # console 子命令
├── vnc/               # vnc 子命令
├── ssh/               # ssh 子命令
├── scp/               # scp 子命令
├── portforward/       # port-forward 子命令
├── memorydump/        # memory-dump 子命令
├── imageupload/       # image-upload 子命令
└── create/            # create 子命令（建立 VM/VMI/Instancetype）
    ├── vm/
    ├── instancetype/
    └── preference/
```

---

## staging/src/kubevirt.io/ — API 型別定義

KubeVirt 採用類似 Kubernetes 的 staging 目錄結構，將 API 定義和客戶端分離為可獨立發布的套件。

```
staging/src/kubevirt.io/
├── api/               # CRD 型別定義（最重要）
├── client-go/         # Go 語言客戶端
└── containerized-data-importer-api/  # CDI API 型別（vendored）
```

### API 型別：staging/src/kubevirt.io/api/

```
staging/src/kubevirt.io/api/
├── core/
│   └── v1/
│       ├── schema.go              # 所有核心型別的欄位定義（最重要）
│       ├── types.go               # VirtualMachine, VMI, Migration 等結構體
│       ├── schema_utils.go        # 型別的輔助方法
│       ├── defaults.go            # 預設值定義
│       └── zz_generated_deepcopy.go  # 自動生成的 DeepCopy 方法
├── instancetype/
│   └── v1beta1/
│       └── types.go               # VirtualMachineInstancetype, VirtualMachinePreference
├── snapshot/
│   └── v1beta1/
│       └── types.go               # VirtualMachineSnapshot, VirtualMachineRestore
├── clone/
│   └── v1beta1/
│       └── types.go               # VirtualMachineClone
├── export/
│   └── v1beta1/
│       └── types.go               # VirtualMachineExport
└── pool/
    └── v1alpha1/
        └── types.go               # VirtualMachinePool
```

**核心型別結構範例：**
```go
// staging/src/kubevirt.io/api/core/v1/types.go（簡化）

// VirtualMachine 代表一個持久性的虛擬機定義
type VirtualMachine struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   VirtualMachineSpec   `json:"spec,omitempty"`
    Status VirtualMachineStatus `json:"status,omitempty"`
}

// VirtualMachineSpec 定義 VM 的期望狀態
type VirtualMachineSpec struct {
    // Running 控制 VM 是否應該運行
    Running *bool `json:"running,omitempty"`

    // RunStrategy 是更靈活的 VM 運行策略
    RunStrategy *VirtualMachineRunStrategy `json:"runStrategy,omitempty"`

    // Template 是 VMI 的範本定義
    Template *VirtualMachineInstanceTemplateSpec `json:"template"`

    // DataVolumeTemplates 是 VM 的磁碟範本
    DataVolumeTemplates []DataVolumeTemplateSpec `json:"dataVolumeTemplates,omitempty"`
}
```

### Go 客戶端：staging/src/kubevirt.io/client-go/

```
staging/src/kubevirt.io/client-go/
├── kubecli/
│   ├── kubecli.go          # KubeVirt 客戶端主介面定義
│   ├── vm.go               # VirtualMachine 客戶端方法
│   ├── vmi.go              # VMI 客戶端方法
│   ├── migration.go        # Migration 客戶端方法
│   └── ...
└── generated/              # 自動生成的 typed 客戶端
    └── clientset/
```

**客戶端使用範例：**
```go
// 在程式碼中使用 KubeVirt 客戶端
import "kubevirt.io/client-go/kubecli"

func example() {
    // 取得客戶端
    virtClient, err := kubecli.GetKubevirtClient()
    if err != nil {
        panic(err)
    }

    // 列出所有 VM
    vmList, err := virtClient.VirtualMachine("default").List(
        context.Background(),
        &metav1.ListOptions{},
    )

    // 啟動一個 VM
    err = virtClient.VirtualMachine("default").Start(
        context.Background(),
        "my-vm",
        &v1.StartOptions{},
    )

    // 取得 VMI 的控制台連線
    stream, err := virtClient.VirtualMachineInstance("default").
        SerialConsole("my-vmi", &kubecli.SerialConsoleOptions{})
}
```

---

## tests/ 目錄 — e2e 測試

```
tests/
├── framework/         # 測試框架工具和輔助函式
│   ├── framework.go   # 測試 framework 初始化
│   └── matcher/       # 自訂 Gomega matcher
├── libvmi/            # 建立 VMI 測試物件的工廠函式
│   ├── factory.go     # VMI 建立輔助（含預設值）
│   ├── compute.go     # CPU/記憶體設定的 VMI option
│   ├── storage.go     # 磁碟設定的 VMI option
│   └── network.go     # 網路設定的 VMI option
├── libnet/            # 網路測試輔助函式
├── libstorage/        # 儲存測試輔助函式
├── libnode/           # 節點操作輔助函式
├── libmigration/      # Migration 測試輔助
├── compute/           # 計算相關 e2e 測試
├── network/           # 網路相關 e2e 測試
├── storage/           # 儲存相關 e2e 測試
├── migration/         # Migration e2e 測試
├── instancetype/      # Instancetype e2e 測試
└── monitoring/        # Monitoring e2e 測試
```

**e2e 測試範例：**
```go
// tests/compute/vmi_lifecycle_test.go（簡化）
var _ = Describe("[sig-compute] VMI Lifecycle", func() {
    var virtClient kubecli.KubevirtClient

    BeforeEach(func() {
        virtClient = kubevirt.Client()
    })

    Context("when a VMI is created", func() {
        It("should reach running phase", func() {
            // 使用 libvmi 工廠建立 VMI（帶有預設值）
            vmi := libvmi.New(
                libvmi.WithCPUCount(1, 1, 1),
                libvmi.WithMemory("256Mi"),
                libvmi.WithContainerDiskImage(
                    "quay.io/kubevirt/cirros-container-disk-demo"),
            )

            // 建立 VMI
            vmi, err := virtClient.VirtualMachineInstance("default").
                Create(context.Background(), vmi)
            Expect(err).ToNot(HaveOccurred())

            // 等待 VMI 進入 Running 狀態
            Eventually(func() v1.VirtualMachineInstancePhase {
                vmi, err = virtClient.VirtualMachineInstance("default").
                    Get(context.Background(), vmi.Name, metav1.GetOptions{})
                Expect(err).ToNot(HaveOccurred())
                return vmi.Status.Phase
            }, 300*time.Second, 3*time.Second).Should(Equal(v1.Running))
        })
    })
})
```

---

## 如何新增一個新功能（以 Feature Gate 為例）

以下以新增一個假想的 `MyNewFeature` feature gate 為例，說明完整的開發流程。

### Step 1：定義 FeatureGate 常數

```go
// staging/src/kubevirt.io/api/core/v1/schema.go
// 在 FeatureGateName 常數區塊中新增
const (
    // ... 現有的 feature gates ...

    // MyNewFeature 啟用 XXX 功能
    // 狀態：Alpha（在達到 Beta/GA 前需要顯式啟用）
    MyNewFeature FeatureGateName = "MyNewFeature"
)
```

### Step 2：在邏輯中使用 Feature Gate

```go
// 在需要的 pkg/ 邏輯中引入 feature gate 檢查
import (
    "kubevirt.io/kubevirt/pkg/util/featuregate"
    v1 "kubevirt.io/api/core/v1"
)

func applyMyNewFeature(vmi *v1.VirtualMachineInstance) error {
    // 先檢查 feature gate 是否啟用
    if !featuregate.DefaultFeatureGate.Enabled(v1.MyNewFeature) {
        return nil  // Feature gate 未啟用，直接返回
    }

    // Feature gate 已啟用，執行新功能邏輯
    // ...
    return nil
}
```

### Step 3：在 Webhook 中加入驗證（若 API 有新欄位）

```go
// pkg/virt-api/webhooks/validating-webhook/admitters/vmi-admitter.go
func validateMyNewFeatureSpec(
    field *k8sfield.Path,
    spec *v1.VirtualMachineInstanceSpec,
) []metav1.StatusCause {
    if spec.MyNewFeatureSpec == nil {
        return nil  // 未使用此功能，不需驗證
    }

    // 確認 feature gate 已啟用
    if !featuregate.DefaultFeatureGate.Enabled(v1.MyNewFeature) {
        return []metav1.StatusCause{{
            Type: metav1.CauseTypeFieldValueInvalid,
            Message: fmt.Sprintf(
                "MyNewFeature feature gate must be enabled to use %s",
                field.Child("myNewFeatureSpec").String(),
            ),
            Field: field.Child("myNewFeatureSpec").String(),
        }}
    }

    // 其他欄位驗證...
    return nil
}
```

### Step 4：更新 API 文件和 schema 注釋

```go
// staging/src/kubevirt.io/api/core/v1/schema.go
// 新增欄位時加入完整的 godoc 說明
type VirtualMachineInstanceSpec struct {
    // ... 現有欄位 ...

    // MyNewFeatureSpec 設定 MyNewFeature 的相關參數。
    // 需要啟用 MyNewFeature feature gate。
    // +optional
    MyNewFeatureSpec *MyNewFeatureSpec `json:"myNewFeatureSpec,omitempty"`
}
```

### Step 5：撰寫測試

```go
// pkg/virt-controller/watch/vm_test.go（單元測試）
var _ = Describe("MyNewFeature", func() {
    Context("when feature gate is enabled", func() {
        BeforeEach(func() {
            featuregate.DefaultFeatureGate.Set(
                string(v1.MyNewFeature) + "=true")
        })

        AfterEach(func() {
            featuregate.DefaultFeatureGate.Set(
                string(v1.MyNewFeature) + "=false")
        })

        It("should apply the new feature", func() {
            // 測試邏輯
        })
    })

    Context("when feature gate is disabled", func() {
        It("should skip the new feature", func() {
            // 測試 feature gate 未啟用時的行為
        })
    })
})

// tests/compute/my_new_feature_test.go（e2e 測試）
var _ = Describe("[sig-compute][Feature:MyNewFeature] My New Feature", func() {
    BeforeEach(func() {
        // 確認 feature gate 已啟用（否則 skip）
        checks.SkipTestIfNoFeatureGate(v1.MyNewFeature)
    })

    It("should work end-to-end", func() {
        // e2e 測試邏輯
    })
})
```

:::tip 測試慣例
KubeVirt 的 e2e 測試使用標籤系統：
- `[Feature:MyNewFeature]` 標籤讓測試可以被 feature gate 條件過濾
- `checks.SkipTestIfNoFeatureGate()` 確保在 feature gate 未啟用的環境中自動跳過測試
- 使用 `[Serial]` 標籤標記需要序列執行的測試
:::

---

## 程式碼生成工具

KubeVirt 大量使用 Kubernetes 的程式碼生成工具，以下是各工具的說明。

### 生成工具列表

| 工具 | 用途 | 觸發指令 |
|------|------|----------|
| `deepcopy-gen` | 為 API 型別生成 `DeepCopyObject()` 等方法 | `make generate-go` |
| `client-gen` | 為 API 型別生成 typed 客戶端 | `make generate-go` |
| `lister-gen` | 為 API 型別生成 lister（帶 cache 的讀取器） | `make generate-go` |
| `informer-gen` | 為 API 型別生成 informer（帶 event handler 的 watcher） | `make generate-go` |
| `openapi-gen` | 生成 OpenAPI schema（用於 API 文件和驗證） | `make generate-go` |
| `mockgen` | 生成 mock 介面（用於單元測試） | `make generate-go` |

### 程式碼生成的觸發標記

生成工具的行為由原始碼中的特殊注釋（`// +k8s:...`）控制：

```go
// staging/src/kubevirt.io/api/core/v1/types.go

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
// +k8s:openapi-gen=true

// VirtualMachine 代表一個持久性的 VM 設定
type VirtualMachine struct {
    // ...
}
```

### 執行生成

```bash
# 執行所有生成步驟
make generate

# 只執行 Go 程式碼生成（deepcopy, client, lister, informer, openapi）
make generate-go

# 只執行 manifests 生成（Kubernetes YAML 資源）
make generate-manifests

# 驗證生成的程式碼是最新的（CI 使用）
make verify-generate
```

:::warning 修改 API 後必須執行 generate
每次修改 `staging/src/kubevirt.io/api/` 中的型別定義後，都必須執行 `make generate`，否則：
1. `DeepCopy` 方法會不完整，導致控制器邏輯出錯
2. 客戶端程式碼會過舊，編譯失敗
3. CI 的 `verify-generate` 檢查會失敗
:::

---

## API 版本管理原則

### 目前 API 版本

| API Group | 版本 | 說明 |
|-----------|------|------|
| `kubevirt.io` | `v1` | 核心型別（VM, VMI, Migration）— 穩定 |
| `instancetype.kubevirt.io` | `v1beta1` | Instancetype/Preference — Beta |
| `snapshot.kubevirt.io` | `v1beta1` | Snapshot/Restore — Beta |
| `clone.kubevirt.io` | `v1beta1` | Clone — Beta |
| `export.kubevirt.io` | `v1beta1` | Export — Beta |
| `pool.kubevirt.io` | `v1alpha1` | VirtualMachinePool — Alpha |

### 新增 API 欄位的原則

```go
// 正確做法：新欄位必須是可選的（使用指針型別或有預設值）
type VirtualMachineInstanceSpec struct {
    // 現有欄位
    Domain DomainSpec `json:"domain"`

    // 新增欄位：必須使用 omitempty，並提供向後相容的預設行為
    // +optional
    NewFeatureConfig *NewFeatureConfig `json:"newFeatureConfig,omitempty"`
}
```

:::danger 不要破壞向後相容性
KubeVirt API 的向後相容性原則：
1. **絕對不要**刪除已有的 API 欄位
2. **絕對不要**改變已有欄位的語意
3. 新欄位必須是**可選的**（omitempty）
4. 新欄位必須有**合理的預設行為**（舊客戶端不設定此欄位時，系統行為不變）
5. 使用 Feature Gate 保護 Alpha/Beta 功能
:::

### 棄用流程

1. 在欄位/功能上加入 `// Deprecated:` godoc 注釋
2. 在下一個 minor 版本中繼續保留但標記為 deprecated
3. 在設定的廢棄期（通常 2-3 個 minor 版本）後才能移除
4. 在 release notes 中明確說明棄用和移除計畫

### CRD 版本轉換

當 API 需要從 v1alpha1 升級到 v1beta1 或 v1 時：

```go
// 需要實作 Conversion Webhook
// 在 staging/src/kubevirt.io/api/<group>/<version>/conversion.go 中
// 定義 Hub 版本（轉換的中間版本）和轉換函式

// 範例：將 v1alpha1 轉換為 v1beta1
func Convert_v1alpha1_MyType_To_v1beta1_MyType(
    in *v1alpha1.MyType,
    out *v1beta1.MyType,
    scope conversion.Scope,
) error {
    // 欄位對應轉換
    out.Spec.NewField = in.Spec.OldField
    return nil
}
```

---

## 重要的設計模式

### 1. Controller 模式（Reconcile Loop）

KubeVirt 遵循標準的 Kubernetes Controller 設計模式：

```
┌─────────────────────────────────────────────────┐
│                  Informer Cache                  │
│  (本地快取 Kubernetes 資源，減少 API Server 負載)  │
└──────────────────────┬──────────────────────────┘
                       │ Event (Add/Update/Delete)
                       ▼
┌─────────────────────────────────────────────────┐
│                  Work Queue                      │
│   (去重複化的工作佇列，防止重複處理同一個物件)      │
└──────────────────────┬──────────────────────────┘
                       │ key (namespace/name)
                       ▼
┌─────────────────────────────────────────────────┐
│               Reconcile Function                 │
│  1. 從 cache 取得當前狀態                         │
│  2. 計算期望狀態                                  │
│  3. 執行必要的動作（建立/更新/刪除子資源）          │
│  4. 更新 Status                                  │
└─────────────────────────────────────────────────┘
```

```go
// 標準 Reconcile loop 結構
func (c *MyController) Run(threadiness int, stopCh <-chan struct{}) {
    for i := 0; i < threadiness; i++ {
        go wait.Until(c.runWorker, time.Second, stopCh)
    }
    <-stopCh
}

func (c *MyController) runWorker() {
    for c.processNextWorkItem() {}
}

func (c *MyController) processNextWorkItem() bool {
    key, quit := c.queue.Get()
    if quit {
        return false
    }
    defer c.queue.Done(key)

    err := c.reconcile(key.(string))
    if err != nil {
        // 重新排入佇列（指數退避）
        c.queue.AddRateLimited(key)
    }
    return true
}
```

### 2. VMI Spec 到 Libvirt XML 的轉換架構

```
VirtualMachineInstance (Kubernetes CR)
           │
           │ pkg/virt-launcher/virtwrap/converter/converter.go
           ▼
api.Domain (libvirt XML 結構體)
           │
           │ libvirt XML marshaling
           ▼
libvirt XML (傳給 libvirtd 建立 QEMU 虛擬機)
```

這個轉換架構使得 KubeVirt 可以：
- 將 Kubernetes 原生的 API（VMI spec）翻譯為 QEMU 能理解的設定
- 集中管理所有 VM 設定的轉換邏輯
- 方便測試（只需測試轉換函式，不需要真實的 QEMU）

### 3. Phase 1/2 網路設定的分離

KubeVirt 將網路設定分為兩個 Phase，在不同的容器中執行：

```
Phase 1（網路準備階段）：
  執行者：virt-handler（以特權模式運行在節點上）
  執行時機：VMI Pod 建立時，在 virt-launcher 啟動前
  工作：
  - 建立 TAP 裝置
  - 設定 bridge
  - 設定 iptables/nftables（masquerade 模式）
  - 設定 MAC 地址

Phase 2（VM 網路設定階段）：
  執行者：virt-launcher（在 VMI Pod 內）
  執行時機：libvirt domain 啟動前
  工作：
  - 生成 libvirt 網路介面 XML
  - 設定 DHCP 伺服器（masquerade 模式）
  - 連接 VM 網路介面到 Phase 1 建立的裝置
```

:::info 為什麼需要兩個 Phase？
Phase 1/2 的分離是 KubeVirt 安全模型的核心：
- **Phase 1** 需要特權操作（建立網路裝置），由 virt-handler 以特權身份執行
- **Phase 2** 只需非特權操作，在 virt-launcher 的非特權容器中執行
- 這樣最小化了 virt-launcher（直接接觸 QEMU）的特權，提高安全性
:::

### 4. Sidecar Hook 機制

Sidecar hook 允許使用者在不修改 KubeVirt 核心的情況下，在 VM 啟動前後執行自訂邏輯：

```
VMI Pod
├── virt-launcher container      # KubeVirt 核心
└── hook-sidecar container       # 使用者自訂 sidecar
    └── 監聽 gRPC socket
        ├── OnDefineDomain()     # 在 libvirt domain 定義前呼叫
        │   └── 可修改 libvirt XML
        └── PreCloudInitIso()    # 在 cloud-init ISO 生成前呼叫
            └── 可修改 cloud-init 資料
```

**使用 Sidecar hook 的 VMI 範例：**
```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
metadata:
  annotations:
    # 指定 hook sidecar 容器映像
    hooks.kubevirt.io/hookSidecars: |
      [{"args": ["--version", "v1alpha2"],
        "image": "quay.io/myuser/my-hook:latest",
        "imagePullPolicy": "IfNotPresent"}]
spec:
  domain:
    devices: {}
    resources:
      requests:
        memory: 64M
```

**實作 Sidecar hook 的 Go 程式碼範例：**
```go
// cmd/example-hook-sidecar/main.go（參考實作）
type ExampleHookSidecar struct{}

func (s ExampleHookSidecar) OnDefineDomain(
    ctx context.Context,
    params *hooksv1alpha2.OnDefineDomainParams,
) (*hooksv1alpha2.OnDefineDomainResult, error) {
    // 取得當前的 domain XML
    domainXML := params.GetDomainXML()

    // 解析並修改 domain 設定
    var domain api.Domain
    xml.Unmarshal(domainXML, &domain)

    // 在這裡注入自訂設定...
    domain.Spec.Metadata.KubeVirt.Sidecar = "example"

    // 序列化並返回修改後的 XML
    newDomainXML, _ := xml.Marshal(domain)
    return &hooksv1alpha2.OnDefineDomainResult{
        DomainXML: newDomainXML,
    }, nil
}
```

---

## 貢獻指引

### PR 提交前的完整檢查清單

在提交 Pull Request 前，請確認以下所有項目：

```bash
# ✅ 1. 執行 linter（程式碼風格和靜態分析）
make lint

# ✅ 2. 確保所有單元測試通過
make test

# ✅ 3. 確保程式碼生成是最新的
make generate
git diff --exit-code  # 確認沒有 uncommitted 的生成變更

# ✅ 4. 確保 manifests 是最新的
make manifests
git diff --exit-code

# ✅ 5. （如有 API 變更）驗證 OpenAPI schema
make generate-manifests

# ✅ 6. 在本地叢集執行相關的 e2e 測試
make cluster-up
make cluster-sync
FUNC_TEST_ARGS="--ginkgo.focus=YourFeature" make functest
```

### Commit Message 格式

KubeVirt 遵循特定的 commit message 格式，且**必須**包含 `Signed-off-by`（DCO）：

```
<type>(<scope>): <short description>

<detailed description>

Signed-off-by: Your Name <you@example.com>
```

**Type 分類：**

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修復 |
| `docs` | 文件變更 |
| `refactor` | 重構（不影響功能） |
| `test` | 新增或修改測試 |
| `chore` | 建置系統、工具變更 |
| `perf` | 效能改善 |

**範例：**
```
feat(network): add support for passt network binding plugin

Add initial support for the passt user-space networking binding.
This allows VMs to use passt instead of bridge or masquerade for
network connectivity, providing better isolation.

Closes #12345

Signed-off-by: Jane Developer <jane@example.com>
```

:::warning Signed-off-by 是必要的
KubeVirt 採用 [DCO（Developer Certificate of Origin）](https://developercertificate.org/) 機制，**每個 commit 都必須有 `Signed-off-by` 行**。

使用 `git commit -s` 自動加入：
```bash
git commit -s -m "feat(vmi): add support for MyNewFeature"
```

若忘記加入，可用以下指令補救：
```bash
git commit --amend -s   # 修改最後一個 commit
# 或對多個 commit
git rebase --signoff HEAD~3  # 對最近 3 個 commit 加入簽署
```
:::

### Review 流程

1. **提交 PR**：確保 PR 描述清楚說明變更的目的、範圍和測試方式
2. **CI 自動測試**：所有 CI 檢查必須通過才能 merge
3. **等待 Reviewer**：KubeVirt maintainer 或 approver 會 review 你的 PR
4. **回應 Review 意見**：根據 review 意見修改並 push 新的 commit
5. **獲得 LGTM + Approve**：需要至少一個 LGTM 和一個 Approve
6. **自動 Merge**：Tide bot 會在滿足條件後自動 merge

:::info 尋求幫助
KubeVirt 社群非常友善，歡迎新貢獻者：
- **Slack**：加入 [Kubernetes Slack](https://slack.k8s.io/)，進入 `#kubevirt-dev` 頻道
- **郵件列表**：[kubevirt-dev@googlegroups.com](mailto:kubevirt-dev@googlegroups.com)
- **每週會議**：查看 [KubeVirt 社群日曆](https://calendar.google.com/calendar/embed?src=18pc0jur01k8f2cccvn5j04j1g%40group.calendar.google.com)
- **Issue**：在 [GitHub Issues](https://github.com/kubevirt/kubevirt/issues) 提問或回報 bug
:::

---

## 快速索引

| 我想做... | 看這裡 |
|-----------|--------|
| 新增 API 欄位 | `staging/src/kubevirt.io/api/core/v1/schema.go` |
| 修改 VM 啟動/停止邏輯 | `pkg/virt-controller/watch/vm.go` |
| 修改 libvirt XML 生成 | `pkg/virt-launcher/virtwrap/converter/converter.go` |
| 新增網路綁定支援 | `pkg/network/driver/` |
| 新增 virtctl 子命令 | `pkg/virtctl/` + `cmd/virtctl/` |
| 新增 Prometheus metric | `pkg/monitoring/metrics/` |
| 修改 Webhook 驗證邏輯 | `pkg/virt-api/webhooks/` |
| 新增 Feature Gate | `staging/src/kubevirt.io/api/core/v1/schema.go` 中的 `FeatureGateName` |
| 撰寫 e2e 測試 | `tests/` + `tests/libvmi/` 工廠函式 |
| 了解節點代理行為 | `pkg/virt-handler/vm.go` |
