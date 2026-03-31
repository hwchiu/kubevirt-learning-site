# 程式碼架構導覽

## 整體目錄結構

```
kubevirt/
├── cmd/                    # 各 binary 的入口 (main package)
├── pkg/                    # 核心業務邏輯套件
├── staging/                # 稍後會發布為獨立模組的 API 定義
│   └── src/kubevirt.io/
│       ├── api/            # 所有 CRD 的 Go 型別定義
│       ├── client-go/      # KubeVirt Kubernetes client
│       └── ...
├── tests/                  # e2e 整合測試
├── tools/                  # 建置輔助工具
├── vendor/                 # Go 依賴模組（vendored）
├── hack/                   # 建置、測試腳本
├── docs/                   # 使用者文件
├── manifests/              # Kubernetes YAML manifests
└── images/                 # Container image 建置定義
```

---

## cmd/ — Binary 入口

每個子目錄對應一個可執行檔：

```
cmd/
├── virt-api/               # REST API 伺服器 + Admission Webhooks
│   └── virt-api.go
├── virt-controller/        # VM/VMI 控制器集合
│   └── virt-controller.go
├── virt-handler/           # 節點代理（DaemonSet）
│   └── virt-handler.go
├── virt-launcher/          # VM 執行容器（每 VMI 一個 Pod）
│   └── virt-launcher.go
├── virt-operator/          # KubeVirt 安裝/升級操作器
│   └── virt-operator.go
├── virtctl/                # CLI 工具
│   └── virtctl.go
├── cniplugins/             # CNI 插件（網路設定）
│   └── ...
├── container-disk-v2alpha/ # ContainerDisk init container
│   └── ...
├── sidecars/               # 網路綁定插件 sidecar
│   └── ...
└── synchronizer/           # 設定同步工具
    └── ...
```

### virt-api 入口流程

```go
// cmd/virt-api/virt-api.go
func main() {
    app := rest.NewVirtAPIApp()
    app.AddFlags()
    app.Run()  // 啟動 HTTP server + webhooks
}
```

---

## pkg/ — 核心套件

`pkg/` 包含 48+ 個套件，按功能分類：

### API 與通訊層

```
pkg/
├── apimachinery/           # API 輔助工具（patch, util）
├── controller/             # 控制器基礎設施（work queue, leader election）
├── rest/                   # virt-api REST handler 實作
│   ├── endpoints.go        # 所有 API endpoint 定義
│   ├── subresources.go     # VNC/Console/SSH 等 subresource handler
│   └── websocket.go        # WebSocket 代理
└── monitoring/             # Prometheus metrics 定義與收集
    ├── metrics/
    └── rules/              # Prometheus alerting rules
```

### VM 生命週期管理

```
pkg/
├── virt-controller/        # 各 Reconciler 實作
│   ├── vm.go               # VM controller（管理 VM CRD）
│   ├── vmi.go              # VMI controller（管理 VMI 生命週期）
│   ├── migration.go        # Migration controller
│   ├── node.go             # Node controller（偵測節點狀態）
│   ├── replicaset.go       # VMIReplicaSet controller
│   ├── pool.go             # VirtualMachinePool controller
│   ├── clone/              # VM Clone controller
│   └── export/             # VM Export controller
├── virt-handler/           # 節點代理業務邏輯
│   ├── vm.go               # VMI 在節點上的管理
│   ├── migration-proxy/    # Migration 代理
│   └── cgroup/             # cgroup 資源管理
└── virt-launcher/          # VM 執行邏輯
    ├── virtwrap/           # libvirt/QEMU 包裝層
    │   ├── api/            # Domain XML 型別
    │   ├── converter/      # VMI → libvirt Domain XML 轉換
    │   └── manager.go      # DomainManager 介面實作
    └── ...
```

### 網路子系統

```
pkg/
├── network/                # 網路管理核心
│   ├── setup/              # 兩階段網路設定
│   │   ├── netpod/         # Phase 1（virt-handler 執行）
│   │   └── netns/          # 網路命名空間管理
│   ├── infraconfigurators/ # 具體綁定機制實作
│   │   ├── bridge.go       # Bridge 模式
│   │   ├── masquerade.go   # Masquerade/NAT 模式
│   │   └── ...
│   ├── dhcp/               # DHCP server 實作
│   ├── multus/             # Multus 整合
│   └── namescheme/         # 網路介面命名規則
└── networkutils/           # 網路工具函式
```

### 儲存子系統

```
pkg/
├── storage/                # 儲存管理
│   ├── types/              # Volume 型別定義
│   ├── snapshot/           # Snapshot controller
│   ├── hotplug/            # 熱插拔管理
│   └── datavolume/         # DataVolume 整合
└── virtio-fs/              # VirtioFS 支援（容器磁碟掛載到 VM）
```

### 安全與憑證

```
pkg/
├── certificates/           # TLS 憑證管理（cert rotation）
├── secrets/                # Secret 處理
├── auth/                   # 認證與授權
└── tls/                    # TLS 配置
```

### 設備管理

```
pkg/
├── virt-handler/
│   └── device-manager/     # GPU, SR-IOV, USB 等設備管理
│       ├── gpu.go
│       ├── vfio.go
│       └── pci.go
└── util/
    └── hardware/           # 硬體資訊收集
```

---

## staging/src/kubevirt.io/ — API 定義

這裡是所有 CRD 的 Go 型別定義，遵循 Kubernetes API conventions：

```
staging/src/kubevirt.io/
├── api/                    # 主要 API 模組
│   ├── core/v1/
│   │   ├── types.go        # VM, VMI, KubeVirt 等核心型別
│   │   ├── types_*.go      # 各子系統型別（network, storage, etc.）
│   │   ├── schema.go       # JSON schema 定義
│   │   └── zz_generated.deepcopy.go  # 自動生成的 DeepCopy 方法
│   ├── instancetype/v1beta1/
│   │   └── types.go        # Instancetype, Preference 型別
│   ├── snapshot/v1beta1/
│   │   └── types.go        # Snapshot, Restore 型別
│   ├── clone/v1alpha1/
│   │   └── types.go        # Clone 型別
│   ├── export/v1alpha1/
│   │   └── types.go        # Export 型別
│   ├── backup/v1alpha1/
│   │   └── types.go        # Backup 型別
│   └── pool/v1alpha1/
│       └── types.go        # VirtualMachinePool 型別
├── client-go/              # Kubernetes client 擴展
│   ├── kubecli/            # KubeVirt 專用 client interface
│   │   └── kubecli.go      # KubevirtClient interface 定義
│   └── generated/          # 自動生成的 informer/lister/client
└── ...
```

---

## tests/ — 測試架構

```
tests/
├── framework/              # 測試框架與輔助函式
│   ├── kubevirt.go         # 測試叢集初始化
│   ├── matcher/            # 自定義 Gomega matchers
│   └── util/               # 測試輔助函式
├── libvmi/                 # VMI 建立輔助函式
│   ├── base.go
│   ├── network.go
│   ├── storage.go
│   └── ...
├── testsuite/              # 測試設定與環境準備
│   ├── setup.go
│   └── namespace.go
├── migration_test.go       # Live Migration e2e 測試
├── vm_test.go              # VM 生命週期 e2e 測試
├── network/                # 網路相關 e2e 測試
├── storage/                # 儲存相關 e2e 測試
└── ...                     # 各功能領域的測試
```

### 測試框架（Ginkgo/Gomega）

```go
// tests/vm_test.go 範例
var _ = Describe("[sig-compute]VirtualMachine", func() {

    BeforeEach(func() {
        // 準備測試環境
    })

    It("[test_id:1539]should start VM", func() {
        vm := libvmi.NewCirros()

        vm, err = virtClient.VirtualMachine(util.NamespaceTestDefault).Create(vm)
        Expect(err).ToNot(HaveOccurred())

        Eventually(func() bool {
            vmi, err := virtClient.VirtualMachineInstance(vm.Namespace).Get(vm.Name, &metav1.GetOptions{})
            return err == nil && vmi.Status.Phase == v1.Running
        }, 300*time.Second, time.Second).Should(BeTrue())
    })
})
```

---

## 如何新增功能（Feature Gate）

KubeVirt 使用 Feature Gate 控制新功能的開關：

### 1. 定義 Feature Gate

```go
// staging/src/kubevirt.io/api/core/v1/featuregate.go
const (
    // 現有的 feature gates
    LiveMigrationGate FeatureGateName = "LiveMigration"
    SRIOVLiveMigrationGate FeatureGateName = "SRIOVLiveMigration"

    // 新增你的 feature gate
    MyNewFeatureGate FeatureGateName = "MyNewFeature"
)
```

### 2. 在程式碼中使用

```go
// pkg/virt-controller/vm.go
import "kubevirt.io/kubevirt/pkg/util/hardware"

func (c *VMController) reconcile(vm *v1.VirtualMachine) {
    if virtconfig.MyNewFeatureEnabled() {
        // 新功能邏輯
    }
}
```

### 3. 在 KubeVirt CR 中啟用

```yaml
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  configuration:
    developerConfiguration:
      featureGates:
      - LiveMigration
      - MyNewFeature
```

---

## 程式碼生成工具

KubeVirt 使用多個 Kubernetes 標準程式碼生成工具：

### DeepCopy 生成

```bash
# 更新 API 型別後，重新生成 DeepCopy 方法
hack/update-codegen.sh
```

生成的檔案：`staging/src/kubevirt.io/api/core/v1/zz_generated.deepcopy.go`

### Client 生成

```bash
# 生成 informer, lister, typed client
hack/update-generated-client.sh
```

生成位置：`staging/src/kubevirt.io/client-go/generated/`

### CRD Manifest 生成

```bash
# 從 Go 型別生成 CRD YAML
make generate
```

生成位置：`_out/manifests/release/kubevirt.yaml`

### Swagger/OpenAPI 生成

```bash
make generate-swagger
```

---

## API 版本管理

| 版本 | 穩定度 | 說明 |
|------|--------|------|
| `v1` | GA | 核心 VM/VMI API，穩定 |
| `v1beta1` | Beta | Instancetype, Snapshot API |
| `v1alpha1` | Alpha | Clone, Export, Backup API |

**版本升級規則**：
- Alpha → Beta：需要一個發布週期的穩定使用
- Beta → GA：需要廣泛的使用者回饋，無重大問題
- 不能在不給遷移路徑的情況下移除 Beta 或 GA API

---

## 關鍵介面定義

### DomainManager（virt-launcher 核心介面）

```go
// pkg/virt-launcher/virtwrap/manager.go
type DomainManager interface {
    SyncVMI(*v1.VirtualMachineInstance, *v1.VirtualMachineInstanceMigration, *cmdv1.VirtualMachineOptions) (*api.DomainSpec, error)
    PauseVMI(*v1.VirtualMachineInstance) error
    UnpauseVMI(*v1.VirtualMachineInstance) error
    FreezeVMI(*v1.VirtualMachineInstance, int32) error
    UnfreezeVMI(*v1.VirtualMachineInstance) error
    SoftResetVMI(*v1.VirtualMachineInstance) error
    KillVMI(*v1.VirtualMachineInstance) error
    DeleteVMIDomain(*v1.VirtualMachineInstance) error
    // ... 更多方法
}
```

### KubevirtClient（API 客戶端介面）

```go
// staging/src/kubevirt.io/client-go/kubecli/kubecli.go
type KubevirtClient interface {
    kubernetes.Interface
    VirtualMachineInstance(namespace string) VirtualMachineInstanceInterface
    VirtualMachine(namespace string) VirtualMachineInterface
    VirtualMachineInstanceMigration(namespace string) VirtualMachineInstanceMigrationInterface
    VirtualMachineInstancePreset(namespace string) VirtualMachineInstancePresetInterface
    VirtualMachineInstanceReplicaSet(namespace string) ReplicaSetInterface
    KubeVirt(namespace string) KubeVirtInterface
    // ... snapshot, instancetype, etc.
}
```

---

## 常用開發指令

```bash
# 完整建置
make

# 只建置某個 binary
make cmd/virt-controller

# 生成程式碼
make generate

# 執行單元測試
make test

# 執行 e2e 測試（需要叢集）
make functest

# 格式化程式碼
make fmt

# 執行 linter
make lint

# 建置並推送映像
make push

# 生成 manifests
make manifests

# 查看 Makefile 所有目標
make help
```

::: tip 新手入門建議
1. 先讀 `staging/src/kubevirt.io/api/core/v1/types.go` 了解核心型別
2. 再讀 `pkg/virt-controller/vm.go` 了解 VM 如何被管理
3. 最後讀 `pkg/virt-launcher/virtwrap/converter/` 了解 VM spec 如何轉成 QEMU 命令
:::
