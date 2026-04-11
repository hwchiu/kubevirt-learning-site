# virt-api

virt-api 是 KubeVirt 的 **HTTP/HTTPS API 入口點**，負責驗證資源定義、處理 VM 操作請求、以及代理 Console/VNC/SSH 等即時連線。

## 職責概述

![virt-api 元件概觀](/diagrams/kubevirt/kubevirt-virt-api-overview.png)

## 部署資訊

| 項目 | 值 |
|------|-----|
| 部署型態 | Kubernetes Deployment |
| 副本數 | ≥ 2 |
| Port | 443 (外部), 8443 (內部 TLS), 8186 (Metrics) |
| Namespace | `kubevirt` |
| Service | `virt-api` ClusterIP |

## 核心資料結構

```go
// pkg/virt-api/api.go
type virtAPIApp struct {
    service.ServiceListen
    virtCli                      kubecli.KubevirtClient
    aggregatorClient             *aggregatorclient.Clientset
    authorizor                   rest.VirtApiAuthorizor
    clusterConfig                *virtconfig.ClusterConfig

    tlsConfig                    *tls.Config
    certmanager                  certificate2.Manager   // TLS 憑證管理
    handlerTLSConfiguration      *tls.Config

    reloadableRateLimiter        *ratelimiter.ReloadableRateLimiter
    reloadableWebhookRateLimiter *ratelimiter.ReloadableRateLimiter

    hasCDIDataSource bool     // 是否有 CDI DataSource 支援
    reInitChan       chan string
}
```

## Admission Webhooks

### Mutating Webhook（自動補齊）

當使用者建立 VM/VMI 時，virt-api 自動補齊以下預設值：

```
VMI 補齊內容：
├── terminationGracePeriodSeconds: 180 (秒)
├── domain.machine.type: "q35" (x86) 或其他架構預設
├── 自動掛載 AutoattachPodInterface: true
├── AutoattachGraphicsDevice: true (VNC)
├── AutoattachSerialConsole: true
├── AutoattachMemBalloon: true
└── 網路介面 model: virtio (如未指定)

VM 補齊內容：
├── spec.template 繼承 VMI 補齊邏輯
└── DataVolumeTemplate 預設 AccessMode
```

### Validating Webhook（驗證）

```
驗證項目：
├── CPU 核數 > 0
├── Memory 大小合理
├── Disk 名稱與 Volume 名稱一致
├── 網路介面名稱與 Network 名稱一致
├── Instancetype 與 spec 不衝突
├── Live Migration 相容性
├── 安全性：普通用戶不能使用 hostPID/hostNetwork
└── 功能開關 (FeatureGates) 是否啟用
```

## REST Subresources

### Console 連線

```bash
# virtctl 內部使用此 API
GET /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachineinstances/{name}/console
```

```go
// pkg/virt-api/rest/console.go
func (app *SubresourceAPIApp) ConsoleRequestHandler(request *restful.Request, response *restful.Response) {
    // 1. 驗證 VMI 存在且 Running
    // 2. 建立 WebSocket 連線
    // 3. 從 virt-handler 取得目標節點資訊
    // 4. 透過 TLS 連線到目標節點的 serial console
    // 5. 雙向轉發串流
}
```

### VNC 連線

```bash
GET /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachineinstances/{name}/vnc
```

VNC 連線流程：

![VNC 連線流程](/diagrams/kubevirt/kubevirt-virt-api-vnc-flow.png)

### Port Forward

```bash
GET /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachineinstances/{name}/portforward/{port}
```

### VM 操作

```bash
# 啟動 VM
PUT /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachines/{name}/start

# 停止 VM
PUT /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachines/{name}/stop

# 重啟 VM
PUT /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachines/{name}/restart

# 暫停 VMI
PUT /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachineinstances/{name}/pause

# 觸發 Migration
PUT /apis/subresources.kubevirt.io/v1/namespaces/{ns}/virtualmachines/{name}/migrate
```

## TLS 憑證管理

virt-api 使用動態憑證輪換：

```go
// 使用 bootstrap.NewFileCertificateManager
// 憑證存放位置：
// - CA: /etc/virt-api/certificates/ca.crt
// - Server cert: /etc/virt-api/certificates/tls.crt
// - Server key:  /etc/virt-api/certificates/tls.key

// 憑證由 virt-operator 管理，定期輪換
// 預設輪換週期：24 小時
// CA 輪換週期：168 小時 (7 天)
```

## Rate Limiting

```go
// 預設值
DefaultVirtAPIQPS   = 30
DefaultVirtAPIBurst = 50

// virt-api 支援動態重新載入 rate limiter
// 透過 ClusterConfig 變更觸發
```

## 啟動流程

```go
// pkg/virt-api/api.go
func (app *virtAPIApp) Execute() {
    // 1. 建立 Kubernetes client
    // 2. 初始化 cluster config (Feature Gates)
    // 3. 設定 TLS 憑證管理員
    // 4. 等待 KubeVirt CR 準備完成
    // 5. 啟動 cert manager
    // 6. 啟動 webhook server
    // 7. 啟動 API server
    // 8. 加入 Leader Election (for webhook 管理)
}

func (app *virtAPIApp) Compose() {
    // 設定所有 REST 路由
    // 包含 subresources + webhook endpoints
}
```

## 授權機制

```go
// pkg/virt-api/rest/authorizer.go
// virt-api 使用 Kubernetes SubjectAccessReview 驗證請求者權限

// 範例：使用者需要以下 RBAC 才能執行 console
// apiGroups: [subresources.kubevirt.io]
// resources: [virtualmachineinstances/console]
// verbs: [get]
```

## 常見問題排查

```bash
# 查看 virt-api 日誌
kubectl logs -n kubevirt -l kubevirt.io=virt-api --tail=100

# 查看 webhook 設定
kubectl get mutatingwebhookconfigurations virt-operator-mutating-webhook-configuration
kubectl get validatingwebhookconfigurations virt-operator-validating-webhook-configuration

# 測試 API 可用性
kubectl get --raw /apis/subresources.kubevirt.io/v1/
```

## 重要原始碼位置

| 功能 | 路徑 |
|------|------|
| 主程式入口 | `cmd/virt-api/main.go` |
| Application 結構 | `pkg/virt-api/api.go` |
| REST Subresources | `pkg/virt-api/rest/` |
| Console 處理 | `pkg/virt-api/rest/console.go` |
| VNC 處理 | `pkg/virt-api/rest/vnc.go` |
| VM 操作 | `pkg/virt-api/rest/lifecycle.go` |
| Port Forward | `pkg/virt-api/rest/portforward.go` |
| Memory Dump | `pkg/virt-api/rest/memorydump.go` |
| Webhooks | `pkg/virt-api/webhooks/` |
