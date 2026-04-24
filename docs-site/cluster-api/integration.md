---
layout: doc
title: Cluster API — 外部整合
---

# Cluster API — 外部整合

## clusterctl — CAPI CLI 工具

`clusterctl` 是 Cluster API 的官方命令列工具，用於管理 Management Cluster 的整個生命週期。

```go
// 檔案: cmd/clusterctl/main.go
// main is the main package for clusterctl.
package main

import (
    _ "k8s.io/client-go/plugin/pkg/client/auth"
    "sigs.k8s.io/cluster-api/cmd/clusterctl/cmd"
)

func main() {
    cmd.Execute()
}
```

### 主要命令

| 命令 | 說明 |
|------|------|
| `clusterctl init` | 初始化 Management Cluster，安裝 CAPI Core + Provider |
| `clusterctl generate cluster` | 根據範本產生 Cluster YAML |
| `clusterctl get kubeconfig` | 取得 Workload Cluster 的 kubeconfig |
| `clusterctl move` | 將叢集物件從一個 Management Cluster 遷移到另一個 |
| `clusterctl upgrade plan` | 查看可用的升級版本 |
| `clusterctl upgrade apply` | 套用升級 |
| `clusterctl describe cluster` | 顯示叢集狀態（含各元件健康狀態）|
| `clusterctl delete` | 刪除 Provider 與相關資源 |

### clusterctl init 用法

```go
// 檔案: cmd/clusterctl/cmd/init.go
type initOptions struct {
    kubeconfig                string
    kubeconfigContext         string
    coreProvider              string
    bootstrapProviders        []string
    controlPlaneProviders     []string
    infrastructureProviders   []string
    ipamProviders             []string
    runtimeExtensionProviders []string
    addonProviders            []string
    targetNamespace           string
    waitProviders             bool
}
```

初始化 Management Cluster 的典型流程：

```bash
# 1. 建立 kind 叢集作為 Management Cluster
kind create cluster --name capi-management

# 2. 設定環境變數（依 Provider 不同）
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>

# 3. 初始化 Management Cluster，安裝 AWS Provider
clusterctl init --infrastructure aws

# 4. 產生 Workload Cluster 的 YAML
clusterctl generate cluster my-cluster \
  --kubernetes-version v1.31.0 \
  --control-plane-machine-count=3 \
  --worker-machine-count=3 \
  > cluster.yaml

# 5. 套用並建立叢集
kubectl apply -f cluster.yaml

# 6. 取得 kubeconfig
clusterctl get kubeconfig my-cluster > my-cluster.kubeconfig
```

### clusterctl move — 叢集遷移

`clusterctl move` 用於將叢集所有權從一個 Management Cluster 轉移到另一個：

```bash
# 將叢集從 source 遷移到 target Management Cluster
clusterctl move \
  --kubeconfig source-management.kubeconfig \
  --to-kubeconfig target-management.kubeconfig \
  --namespace default
```

::: warning 遷移前注意事項
執行 `clusterctl move` 前，必須確保 Workload Cluster 已暫停（pause），且 target Management Cluster 已安裝相同版本的 Provider。
:::

## Tilt — 本地開發環境

CAPI 提供完整的 Tilt 整合，讓開發者能快速在本地測試代碼變更：

```python
# 檔案: Tiltfile
clusterctl_cmd = "./bin/clusterctl"
kubectl_cmd = "kubectl"
kubernetes_version = "v1.35.0"

settings = {
    "enable_providers": ["docker"],
    "kind_cluster_name": os.getenv("CAPI_KIND_CLUSTER_NAME", "capi-test"),
    "debug": {},
    "build_engine": "docker",
}
```

### Tilt 開發流程

```bash
# 1. 建立設定檔
cat > tilt-settings.yaml << EOF
default_registry: "gcr.io/your-project"
enable_providers:
- docker
- kubeadm-bootstrap
- kubeadm-control-plane
EOF

# 2. 建立 kind 叢集
kind create cluster --name capi-test

# 3. 啟動 Tilt（自動 build、push、deploy）
tilt up
```

Tilt 的主要功能：

| 功能 | 說明 |
|------|------|
| 自動 Build | 監控原始碼變更，自動重新 build Controller |
| 自動 Deploy | 重新 deploy 到 kind 叢集 |
| Hot Reload | 支援 UI Button 觸發 Provider 安裝 |
| Docker Provider | 預設啟用，可在本機模擬多叢集 |

## CRD 升級管理（CRD Migrator）

CAPI 內建 `crdmigrator` 機制，在 Controller 啟動時自動將舊版 CRD 資源遷移到新版：

```go
// 檔案: controllers/crdmigrator
// CRD Migrator 確保升級 CAPI 版本後，已有的 CRD 物件能自動遷移到新版 API schema
// 通常在 main.go 中的 Manager 啟動時自動執行
```

## 監控整合

CAPI Controller 暴露標準 Prometheus Metrics：

| Metric | 說明 |
|--------|------|
| `capi_cluster_info` | 叢集基本資訊 |
| `controller_runtime_reconcile_total` | Reconcile 次數（含錯誤統計）|
| `controller_runtime_reconcile_time_seconds` | Reconcile 耗時分布 |

::: tip 生產環境建議
使用 `clusterctl describe cluster` 快速查看整個叢集的健康狀態，包含各 Provider 資源的 Ready 狀態與 Condition 詳情。
:::

::: info 相關章節
- [Provider 模型](./providers)
- [叢集生命週期](./lifecycle)
- [系統架構](./architecture)
:::
