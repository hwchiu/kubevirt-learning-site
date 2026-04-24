---
layout: doc
title: Cluster API Provider MAAS — 外部整合
---

# Cluster API Provider MAAS — 外部整合

## MAAS API 整合

### 認證方式

CAPMAAS 透過環境變數讀取 MAAS 連線設定，在啟動時建立認證客戶端：

```go
// 檔案: pkg/maas/scope/client.go

func NewMaasClient(_ *ClusterScope) maasclient.ClientSetInterface {
    maasEndpoint := os.Getenv("MAAS_ENDPOINT")
    if maasEndpoint == "" {
        panic("missing env MAAS_ENDPOINT; e.g: MAAS_ENDPOINT=http://10.11.130.11:5240/MAAS")
    }

    maasAPIKey := os.Getenv("MAAS_API_KEY")
    if maasAPIKey == "" {
        panic("missing env MAAS_API_KEY; e.g: MAAS_API_KEY=x:y:z>")
    }

    maasClient := maasclient.NewAuthenticatedClientSet(maasEndpoint, maasAPIKey)
    return maasClient
}
```

| 環境變數 | 格式 | 範例 |
|---------|------|------|
| `MAAS_ENDPOINT` | `http://<host>:<port>/MAAS` | `http://10.11.130.11:5240/MAAS` |
| `MAAS_API_KEY` | `<consumer_key>:<token_key>:<token_secret>` | `abc123:def456:ghi789` |

::: warning 環境變數為必要項目
若未設定 `MAAS_ENDPOINT` 或 `MAAS_API_KEY`，程式會直接 `panic`。這兩個環境變數必須在部署 CAPMAAS 的 Pod 中正確設定。
:::

### 設定方式

在 `~/.cluster-api/clusterctl.yaml` 中設定認證與叢集參數：

```yaml
# 檔案: README.md（clusterctl 設定範例）
# MAAS 連線設定
MAAS_API_KEY: <maas-api-key>
MAAS_ENDPOINT: http://<maas-endpoint>/MAAS
MAAS_DNS_DOMAIN: maas.domain

# Kubernetes 版本
KUBERNETES_VERSION: v1.26.4

# Control Plane 機器設定
CONTROL_PLANE_MACHINE_IMAGE: custom/u-2204-0-k-1264-0
CONTROL_PLANE_MACHINE_MINCPU: 4
CONTROL_PLANE_MACHINE_MINMEMORY: 8192
CONTROL_PLANE_MACHINE_RESOURCEPOOL: resourcepool-controller
CONTROL_PLANE_MACHINE_TAG: hello-world

# Worker 機器設定
WORKER_MACHINE_IMAGE: custom/u-2204-0-k-1264-0
WORKER_MACHINE_MINCPU: 4
WORKER_MACHINE_MINMEMORY: 8192
WORKER_MACHINE_RESOURCEPOOL: resourcepool-worker
WORKER_MACHINE_TAG: hello-world
```

## 與 Cluster API 的整合點

### ClusterCacheTracker

CAPMAAS 使用 CAPI 提供的 `ClusterCacheTracker` 連接 Workload 叢集，用於：
1. 確認 API Server 是否上線（`IsAPIServerOnline()`）
2. 在 Workload 叢集 Node 物件上設定 `ProviderID`

```go
// 檔案: main.go

tracker, err := remote.NewClusterCacheTracker(
    mgr,
    remote.ClusterCacheTrackerOptions{
        Log:     &log,
        Indexes: []remote.Index{remote.NodeProviderIDIndex},
    },
)
```

### Controller 監聽關係

`MaasMachineReconciler` 監聽以下事件觸發 Reconcile：

| Watch 對象 | 觸發原因 |
|-----------|---------|
| `MaasMachine` | 主要對象變更 |
| `Machine`（CAPI）| Owner Machine 變更（例如 BootstrapData 就緒）|
| `MaasCluster` | 叢集基礎設施狀態變更（例如 Ready = true）|
| `Cluster`（CAPI）| 叢集狀態變更（例如 InfrastructureReady）|

`MaasClusterReconciler` 監聽：

| Watch 對象 | 觸發原因 |
|-----------|---------|
| `MaasCluster` | 主要對象變更 |
| `MaasMachine` | Control Plane 機器狀態變更（需更新 DNS）|
| `Cluster`（CAPI）| 叢集狀態變更 |
| `GenericEventChannel` | API Server 上線事件（非同步通知）|

## 使用 clusterctl 部署

### 初始化 Infrastructure Provider

```bash
clusterctl init --infrastructure maas:v0.7.0
```

這會將 CAPMAAS 的 CRD 和 Controller 部署到管理叢集。

### 產生叢集 Manifest

```bash
clusterctl generate cluster t-cluster \
  --infrastructure=maas:v0.7.0 \
  --kubernetes-version v1.26.4 \
  --control-plane-machine-count=1 \
  --worker-machine-count=3 | kubectl apply -f -
```

或先輸出到檔案再 apply：

```bash
clusterctl generate cluster t-cluster \
  --infrastructure=maas:v0.7.0 \
  --kubernetes-version v1.26.4 \
  --control-plane-machine-count=1 \
  --worker-machine-count=3 > my_cluster.yaml
kubectl apply -f my_cluster.yaml
```

## 映像檔（MAAS Custom Image）

CAPMAAS 需要預先在 MAAS 中上傳包含 Kubernetes 元件的 Custom Image。

### Spectro Cloud 公開映像檔

| Kubernetes 版本 | 映像檔 URL |
|----------------|-----------|
| 1.25.6 | `https://maas-images-public.s3.amazonaws.com/u-2204-0-k-1256-0.tar.gz` |
| 1.26.1 | `https://maas-images-public.s3.amazonaws.com/u-2204-0-k-1261-0.tar.gz` |

### 自訂映像檔

參考 `image-generation/` 目錄自行建置映像檔：

```bash
# 進入映像檔建置目錄
cd image-generation/

# 參考 README.md 中的指引
```

映像檔在 MAAS 中的名稱格式為 `custom/<image-name>`，例如：`custom/u-2204-0-k-1264-0`。

## 程式啟動參數

CAPMAAS Manager 支援以下命令列參數：

```go
// 檔案: main.go

func initFlags(fs *pflag.FlagSet) {
    fs.StringVar(&metricsBindAddr, "metrics-bind-addr", ":8080",
        "The address the metric endpoint binds to.")
    fs.IntVar(&machineConcurrency, "machine-concurrency", 2,
        "The number of maas machines to process simultaneously")
    fs.BoolVar(&enableLeaderElection, "leader-elect", false,
        "Enable leader election for controller manager.")
    fs.DurationVar(&syncPeriod, "sync-period", 120*time.Minute,
        "The minimum interval at which watched resources are reconciled")
    fs.StringVar(&healthAddr, "health-addr", ":9440",
        "The address the health endpoint binds to.")
    fs.IntVar(&webhookPort, "webhook-port", 9443,
        "Webhook Server port")
    fs.StringVar(&watchNamespace, "namespace", "",
        "Namespace that the controller watches to reconcile cluster-api objects.")
}
```

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--metrics-bind-addr` | `:8080` | Prometheus metrics 端口 |
| `--machine-concurrency` | `2` | 同時處理的 MaasMachine 數量 |
| `--leader-elect` | `false` | 是否啟用 Leader Election |
| `--sync-period` | `120m` | 週期性 Reconcile 間隔 |
| `--health-addr` | `:9440` | 健康檢查端口 |
| `--webhook-port` | `9443` | Webhook Server 端口 |
| `--namespace` | `""` | 限定監聽的 Namespace（空值 = 全部）|

## Webhook 整合

CAPMAAS 為三個 CRD 均提供 Admission Webhook：

```go
// 檔案: main.go

if err = (&infrav1beta1.MaasCluster{}).SetupWebhookWithManager(mgr); err != nil {
    setupLog.Error(err, "unable to create webhook", "webhook", "MaasCluster")
    os.Exit(1)
}
if err = (&infrav1beta1.MaasMachine{}).SetupWebhookWithManager(mgr); err != nil {
    setupLog.Error(err, "unable to create webhook", "webhook", "MaasMachine")
    os.Exit(1)
}
if err = (&infrav1beta1.MaasMachineTemplate{}).SetupWebhookWithManager(mgr); err != nil {
    setupLog.Error(err, "unable to create webhook", "webhook", "MaasMachineTemplate")
    os.Exit(1)
}
```

Webhook 用於驗證建立/更新請求，防止非法欄位值。

## 開發模式部署

開發環境可使用 `kind` 叢集搭配本地映像檔測試：

```bash
# 建立 kind 叢集
kind create cluster --name=maas-cluster

# 建置並推送 Docker 映像檔
make docker-build && make docker-push

# 產生開發用 Manifest
make dev-manifests

# 將 _build/dev/ 內容複製到 clusterctl overrides 目錄
# ~/.cluster-api/overrides/infrastructure-maas/v0.7.0/

# 初始化
clusterctl init --infrastructure maas:v0.7.0
```

::: tip API Server 非同步探測
`ReconcileMaasClusterWhenAPIServerIsOnline()` 會啟動一個 goroutine 不斷輪詢 Workload 叢集的 API Server，一旦上線就透過 `GenericEventChannel` 推送事件觸發 `MaasClusterReconciler` 再次協調。這避免了主 Reconcile 迴圈的忙碌等待。
:::

::: info 相關章節
- [系統架構](./architecture) — Controller 架構設計
- [核心功能](./core-features) — 機器佈建流程
- [控制器與 API](./controllers-api) — CRD 欄位完整說明
:::
