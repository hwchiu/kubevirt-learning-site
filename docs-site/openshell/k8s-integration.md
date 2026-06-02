---
layout: doc
---

# NVIDIA OpenShell — Kubernetes 整合

::: tip 分析版本
本文件基於 commit [`d9908222`](https://github.com/NVIDIA/OpenShell/commit/d9908222f2b18adeb00227f8fbefcaabd7ebd7f0) 進行分析。
:::

::: warning 實驗性功能
OpenShell 的 Kubernetes 部署路徑目前為實驗性（Experimental）功能，仍在積極開發中。預期有 Breaking Changes。
:::

::: info 相關章節
- 專案簡介請參閱 [專案總覽](./index)
- 架構設計請參閱 [系統架構](./architecture)
- 沙箱管理與策略請參閱 [核心功能分析](./core-features)
:::

## 概覽

OpenShell 支援將 Gateway 部署至 Kubernetes 叢集，使 AI Agent 沙箱以 Kubernetes **Pod** 的形式執行。透過官方 Helm Chart（OCI 格式）可快速完成部署，沙箱生命週期由 Kubernetes Driver 透過標準 K8s API 管理。

### Kubernetes 模式的優勢

| 特性 | 說明 |
|------|------|
| **Pod 隔離** | 每個沙箱為獨立 Pod，享有 Kubernetes 原生的命名空間隔離 |
| **PVC Workspace** | 沙箱工作區以 PersistentVolumeClaim 持久化 |
| **GPU 資源管理** | 透過 K8s Resource Request/Limit 分配 GPU |
| **Service Account** | 沙箱 Pod 使用專屬 Service Account，實現最小權限 |
| **Network Policy** | 透過 K8s NetworkPolicy 限制沙箱間 SSH 入站僅允許 Gateway |
| **HA Gateway** | 多副本 Gateway 搭配外部 PostgreSQL 實現高可用 |
| **OIDC 整合** | 支援 Keycloak、Entra ID、Okta 等企業 Identity Provider |

## 前置需求

在部署 OpenShell 前，必須先安裝 **Kubernetes Agent Sandbox CRD 與 Controller**：

```bash
kubectl apply -f https://github.com/kubernetes-sigs/agent-sandbox/releases/latest/download/manifest.yaml
```

此 CRD 由 [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) 提供，為 OpenShell Kubernetes Driver 的基礎依賴。

## 安裝 OpenShell（Helm）

### 標準 Kubernetes 安裝

```bash
# 使用特定版本安裝（推薦）
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart --version <version>

# 安裝至指定 Namespace
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart \
  --version <version> \
  -n openshell \
  --create-namespace
```

### 在 OpenShift 上安裝

```bash
# 預先建立 Namespace（SCC 設定需要）
oc create ns openshell

# 授予沙箱 Service Account privileged SCC
oc adm policy add-scc-to-user privileged -z openshell-sandbox -n openshell

# 部署 OpenShell（含 OpenShift 安全設定覆寫）
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart \
  --version <version> \
  -n openshell \
  --set server.disableTls=true \
  --set podSecurityContext.fsGroup=null \
  --set securityContext.runAsUser=null
```

## Helm Chart 版本策略

| Tag | 來源 | 適用場景 |
|-----|------|---------|
| `<semver>`（如 `0.6.0`） | 標記的 GitHub Release | 生產環境（推薦） |
| `0.0.0-dev` | `main` 最新 Commit（浮動） | 測試最新變更 |
| `0.0.0-dev.<commit-sha>` | `main` 特定 Commit | 精確鎖定 Commit |

## 資料庫後端

Gateway 需要持久化儲存，支援 SQLite（預設）或 PostgreSQL。

### 預設（SQLite）

```yaml
server:
  dbUrl: "sqlite:/var/openshell/openshell.db"
postgres:
  enabled: false
```

### 外部 PostgreSQL

```bash
# 建立包含連線 URI 的 Secret
kubectl create secret generic my-pg-credentials -n openshell \
  --from-literal=uri="******host:5432/dbname"

# 安裝時指向外部 Secret
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart \
  --version <version> \
  -n openshell \
  --set server.externalDbSecret=my-pg-credentials
```

### 內建 PostgreSQL（Bitnami Subchart）

```bash
# 部署含內建 PostgreSQL 的 OpenShell
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart \
  --version <version> \
  --set postgres.enabled=true \
  --set postgres.auth.******
```

## PKI 初始化

Helm Chart 預設透過 pre-install/pre-upgrade Job 自動生成 Gateway 與 Client 的 mTLS Secrets：

- **Job 行為**：幂等執行；若兩個 Secret 已存在則記錄後退出；若其中一個存在則報錯提示恢復方式；都不存在時生成 CA、Server cert、Client cert
- **Job 映像**：使用 Gateway 映像本身（隔離環境友善，無需額外 openssl/alpine sidecar）

```bash
# 停用 PKI Job（自帶 cert-manager 或手動 PKI 時使用）
helm install openshell ... --set pkiInitJob.enabled=false
```

### 整合 cert-manager

```yaml
certManager:
  enabled: true
  caSecretName: "openshell-ca-tls"
  certificateDuration: "8760h"
  certificateRenewBefore: "720h"
  serverDnsNames:
    - openshell
    - openshell.openshell.svc
    - openshell.openshell.svc.cluster.local
    - localhost
```

## Kubernetes 特有配置

### 沙箱 Service Account

```yaml
sandboxServiceAccount:
  create: true                  # 自動建立沙箱 Pod 用 Service Account
  annotations: {}               # 可添加 IAM Role 等 Annotation（如 IRSA）
  name: ""                      # 使用既有 Service Account 時設定名稱
```

### NetworkPolicy

```yaml
networkPolicy:
  enabled: true   # 建立 NetworkPolicy，限制 SSH 入站僅允許來自 Gateway
```

### Supervisor 交付方式

Supervisor 二進位依叢集 K8s 版本自動選擇：

```yaml
supervisor:
  sideloadMethod: ""   # 空 = 自動偵測（K8s ≥ 1.35 用 image-volume，< 1.35 用 init-container）
  image:
    repository: ghcr.io/nvidia/openshell/supervisor
    tag: ""            # 預設與 Chart appVersion 一致
```

| K8s 版本 | 交付方式 | 說明 |
|---------|---------|------|
| ≥ 1.35 | `image-volume` | ImageVolume GA（1.36），預設啟用 |
| 1.33–1.34 | `image-volume`（手動啟用） | 需手動啟用 Feature Gate |
| < 1.33 | `init-container` | Init Container 複製至 emptyDir |

### 沙箱 Workspace 儲存

```yaml
server:
  workspaceDefaultStorageSize: "2Gi"   # 沙箱 PVC 預設大小（Kubernetes quantity 格式）
  sandboxNamespace: ""                  # 沙箱 Pod 所在 Namespace（預設為 Release Namespace）
```

### 沙箱映像設定

```yaml
server:
  sandboxImage: "ghcr.io/nvidia/openshell-community/sandboxes/base:latest"
  sandboxImagePullPolicy: ""            # 空 = K8s 預設（:latest 用 Always，否則 IfNotPresent）
  sandboxImagePullSecrets: []           # 沙箱 Pod 的 Image Pull Secret（需存在於沙箱 Namespace）
```

### Gateway Service 設定

```yaml
service:
  type: ClusterIP   # K8s Service 類型
  port: 8080        # gRPC/HTTP 主要端口
  healthPort: 8081  # 健康檢查端口
  metricsPort: 9090 # Prometheus Metrics 端口
```

### 使用者命名空間隔離（K8s 1.33+）

```yaml
server:
  enableUserNamespaces: false   # 啟用後容器 UID 0 映射至非特權 Host UID
                                 # 需要 K8s 1.33+ 且支援的 Container Runtime
```

## OIDC 整合

企業環境可整合外部 Identity Provider 進行使用者驗證：

```yaml
server:
  oidc:
    issuer: "https://keycloak.example.com/realms/openshell"
    audience: "openshell-cli"
    rolesClaim: "realm_access.roles"   # Keycloak
    # rolesClaim: "roles"              # Entra ID
    # rolesClaim: "groups"             # Okta
    adminRole: "openshell-admin"
    userRole: "openshell-user"
    jwksTtl: 3600
    # 非公開 CA（如 OpenShift Ingress）時指定 CA ConfigMap
    caConfigMapName: "oidc-ca-bundle"
```

## Gateway API（GRPCRoute）

```yaml
grpcRoute:
  enabled: true
  gateway:
    className: "eg"    # Envoy Gateway 預設 GatewayClass
    create: true
    listener:
      port: 80
      protocol: "HTTP"
  hostnames: []        # 空 = 匹配所有 Host
```

## 高可用（HA）部署

```yaml
replicaCount: 3

# 搭配外部 PostgreSQL（不能用 SQLite 做 HA）
server:
  externalDbSecret: my-pg-credentials

# affinity 避免 Gateway 副本共存同一節點
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: openshell
          topologyKey: kubernetes.io/hostname
```

## 使用 OpenShell CLI 連接 K8s Gateway

在 K8s 叢集內部署 Gateway 後，從本機 CLI 連接：

```bash
# 將 Gateway Service 轉發至本機（開發環境）
kubectl port-forward svc/openshell 8080:8080 -n openshell

# 設定 CLI 連接 Gateway
openshell gateway set k8s-gateway --endpoint https://localhost:8080

# 建立沙箱（將以 K8s Pod 形式執行）
openshell sandbox create -- claude

# 查看沙箱 Pod
kubectl get pods -n openshell
```

## 在 K8s 中建立沙箱的流程

```
openshell sandbox create -- claude
         │
         ▼ gRPC
┌────────────────┐
│  Gateway Pod   │  (openshell Namespace)
│                │
│  Kubernetes    │
│  Driver        │──── kubectl apply ────▶ Sandbox Pod
└────────────────┘                         (openshell Namespace)
                                            ├── init-container (Supervisor delivery)
                                            ├── sandbox container
                                            │     └── openshell-supervisor
                                            │           └── claude (restricted)
                                            └── PVC (workspace storage)
```

## 沙箱 Pod 安全上下文

```yaml
# Gateway Pod
podSecurityContext:
  fsGroup: 1000

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  runAsNonRoot: true
  runAsUser: 1000
```

::: tip OpenShift 注意事項
在 OpenShift 上，`fsGroup` 與 `runAsUser` 由 SCC 管理，需設為 `null` 讓 OpenShift 自動分配。
:::

## 常見 Kubernetes 部署問題排查

| 症狀 | 可能原因 | 解決方式 |
|------|---------|---------|
| Gateway Pod 啟動失敗 | CRD 未安裝 | 先執行 `kubectl apply -f agent-sandbox manifest.yaml` |
| 沙箱 Pod Pending | PVC 無法 Bound | 確認 StorageClass 存在且有容量 |
| mTLS 連線失敗 | PKI Secret 不存在或過期 | 刪除舊 Secret，重新執行 `helm upgrade` 讓 PKI Job 重新生成 |
| Supervisor 無法啟動 | K8s 版本與 `sideloadMethod` 不符 | 手動設定 `supervisor.sideloadMethod` |
| OIDC 驗證失敗 | Issuer URL 或 roles claim 設定錯誤 | 確認 `server.oidc.issuer` 與 JWT 內容一致 |
| OpenShift SCC 錯誤 | 沙箱 Service Account 缺少 privileged SCC | 執行 `oc adm policy add-scc-to-user privileged` |
