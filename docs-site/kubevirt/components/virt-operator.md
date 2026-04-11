# virt-operator

virt-operator 是 KubeVirt 的**安裝與生命週期管理元件**，負責在 Kubernetes 叢集中部署、設定、升級所有其他 KubeVirt 元件。

## 職責概述

![virt-operator 元件概觀](/diagrams/kubevirt/kubevirt-virt-operator-overview.png)

## 部署資訊

| 項目 | 值 |
|------|-----|
| 部署型態 | Kubernetes Deployment |
| 副本數 | ≥ 2 (Leader Election) |
| 監聽 Port | 8186 (Metrics & Leader Election) |
| Namespace | `kubevirt` |
| Leader Election | 使用 Kubernetes Lease (duration: 15s) |

## 啟動方式

KubeVirt 的安裝分兩步：

```bash
# 步驟 1：部署 virt-operator (唯一需要手動部署的元件)
kubectl apply -f https://github.com/kubevirt/kubevirt/releases/latest/download/kubevirt-operator.yaml

# 步驟 2：建立 KubeVirt CR (觸發 virt-operator 部署其他元件)
kubectl apply -f https://github.com/kubevirt/kubevirt/releases/latest/download/kubevirt-cr.yaml
```

## KubeVirt CR 詳解

```yaml
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  # 映像檔設定
  imageTag: "v1.x.x"
  imageRegistry: "quay.io/kubevirt"
  imagePullPolicy: IfNotPresent

  # 元件資源配置
  infra:
    replicas: 2           # virt-api, virt-controller 副本數
    nodePlacement:
      affinity: {}        # 節點親和性規則

  workloads:
    nodePlacement:
      tolerations: []     # virt-handler 的 toleration

  # VM 更新策略
  workloadUpdateStrategy:
    workloadUpdateMethods:
    - LiveMigrate         # 更新時用 Live Migration
    # - Evict             # 或者驅逐 VM

  # Feature Gates (功能開關)
  configuration:
    developerConfiguration:
      featureGates:
      - HotplugVolumes         # 開啟 volume 熱插拔
      - LiveMigration          # 開啟 live migration
      - Snapshot               # 開啟快照功能
      - CPUManager             # 開啟 CPU 固定
      - NUMA                   # 開啟 NUMA 拓撲
      - HypervStrictCheck      # Hyper-V 嚴格檢查

    # 網路設定
    network:
      defaultNetworkInterface: "masquerade"
      permitSlirpInterface: false

    # 儲存設定
    permittedHostDevices:
      pciHostDevices:
      - pciVendorSelector: "10DE:1DB6"  # NVIDIA GPU
        resourceName: "nvidia.com/GP100GL"

  # 憑證輪換
  certificateRotateStrategy:
    selfSigned:
      caRotateInterval: "168h"
      certRotateInterval: "24h"

  # OpenShift 監控整合
  monitorNamespace: "openshift-monitoring"
  monitorAccount: "prometheus-k8s"
```

## virt-operator 產生的資源

### Deployments & DaemonSets

```go
// pkg/virt-operator/resource/generate/components/deployments.go
NewApiServerDeployment()       // virt-api
NewControllerDeployment()      // virt-controller
NewOperatorDeployment()        // virt-operator 自身
NewExportProxyDeployment()     // virt-exportproxy
NewSynchronizationControllerDeployment() // 同步控制器
```

```go
// pkg/virt-operator/resource/generate/components/daemonsets.go
NewHandlerDaemonSet()          // virt-handler
```

### RBAC 資源

```
rbac/
├── apiserver.go    → ServiceAccount, ClusterRole for virt-api
├── controller.go   → ServiceAccount, ClusterRole for virt-controller
├── handler.go      → ServiceAccount, ClusterRole for virt-handler
├── operator.go     → ClusterRole for virt-operator
└── exportproxy.go  → ServiceAccount, ClusterRole for export proxy
```

### Webhook 設定

virt-operator 動態建立並維護以下 webhooks：

**Mutating Webhooks（自動補齊預設值）：**
- `virtualmachines-mutate` — VM spec 補齊
- `virtualmachineinstances-mutate` — VMI spec 補齊

**Validating Webhooks（驗證正確性）：**
- `virtualmachines-validate` — VM spec 驗證
- `virtualmachineinstances-validate` — VMI spec 驗證
- `virtualmachinepresets-validate` — Preset 驗證
- `migration-validate` — Migration 請求驗證
- 以及 Snapshot、Clone、Instancetype 等的 webhook

## Rate Limiting 設定

```go
// pkg/virt-operator/application.go
const (
    defaultPort = 8186
    defaultHost = "0.0.0.0"
    // 可透過環境變數調整
    EnvVirtOperatorClientQPS   = "VIRT_OPERATOR_CLIENT_QPS"
    EnvVirtOperatorClientBurst = "VIRT_OPERATOR_CLIENT_BURST"
)

// 預設值
DefaultVirtOperatorQPS   = 50
DefaultVirtOperatorBurst = 100
```

## KubeVirt CR 狀態追蹤

```yaml
status:
  phase: Deployed          # Deploying | Deployed | Deleting | Deleted
  observedKubeVirtVersion: "v1.x.x"
  targetKubeVirtVersion: "v1.x.x"
  observedDeploymentID: "xxxx"
  conditions:
  - type: Available
    status: "True"
    reason: AllComponentsReady
  - type: Progressing
    status: "False"
  - type: Degraded
    status: "False"
```

## 升級流程

當使用者更新 KubeVirt CR 的 `imageTag` 時：

![virt-operator 升級流程](/diagrams/kubevirt/kubevirt-virt-operator-upgrade.png)

## 重要原始碼位置

| 功能 | 路徑 |
|------|------|
| 主程式入口 | `cmd/virt-operator/main.go` |
| Application 結構 | `pkg/virt-operator/application.go` |
| KubeVirt 控制器 | `pkg/virt-operator/kubevirt.go` |
| 資源產生器 | `pkg/virt-operator/resource/generate/components/` |
| RBAC 產生器 | `pkg/virt-operator/resource/generate/rbac/` |
| Install Strategy | `pkg/virt-operator/resource/apply/` |
