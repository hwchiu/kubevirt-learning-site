---
layout: doc
---

# NVIDIA NemoClaw — Kubernetes 整合

::: tip 分析版本
本文件基於 commit [`798d5a38`](https://github.com/NVIDIA/NemoClaw/commit/798d5a386a92a34e00f16eccb6fcb2eaa5007643) 進行分析。
:::

::: info 相關章節
- 專案簡介請參閱 [專案總覽](./index)
- 架構設計請參閱 [系統架構](./architecture)
- 核心功能請參閱 [核心功能分析](./core-features)
- OpenShell K8s 部署詳見 [OpenShell Kubernetes 整合](../openshell/k8s-integration)
:::

## 概覽

NemoClaw 在 Kubernetes 環境中以 **OpenShell Kubernetes Driver** 為基礎，將每個 AI Agent 沙箱作為 Kubernetes **Pod** 執行。NemoClaw 在 OpenShell 的 K8s 部署之上，提供針對 OpenClaw / Hermes 優化的 Blueprint、推理路由與網路策略管理。

### K8s 部署架構

```
kubectl / Helm
     │
     ▼
┌────────────────────────────────────────────┐
│         openshell Namespace               │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │         OpenShell Gateway Pod        │  │
│  │  (含 NemoClaw Plugin 配置)            │  │
│  └──────────────────┬───────────────────┘  │
│                     │ 建立沙箱 Pod          │
│  ┌──────────────────▼───────────────────┐  │
│  │         NemoClaw Agent Pod           │  │
│  │  ┌──────────────────────────────┐    │  │
│  │  │     OpenShell Supervisor     │    │  │
│  │  │  ┌────────────────────────┐  │    │  │
│  │  │  │   OpenClaw / Hermes    │  │    │  │
│  │  │  │   (restricted process) │  │    │  │
│  │  │  └────────────────────────┘  │    │  │
│  │  │  Policy Proxy (OPA)          │    │  │
│  │  │  Inference Router            │    │  │
│  │  └──────────────────────────────┘    │  │
│  │  PVC (workspace)                     │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

## 前置需求

在 Kubernetes 上使用 NemoClaw 前，需要先完成以下準備：

### 1. 安裝 Kubernetes Agent Sandbox CRD

```bash
kubectl apply -f https://github.com/kubernetes-sigs/agent-sandbox/releases/latest/download/manifest.yaml
```

### 2. 部署 OpenShell Gateway（Helm）

```bash
# 建立 Namespace
kubectl create namespace openshell

# 安裝 OpenShell Helm Chart
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart \
  --version <version> \
  -n openshell
```

詳細的 OpenShell K8s 部署配置請參閱 [OpenShell Kubernetes 整合](../openshell/k8s-integration)。

### 3. 安裝 NemoClaw CLI

```bash
# 安裝 NemoClaw（OpenClaw 預設）
curl -LsSf https://install.nemoclaw.nvidia.com | sh

# 驗證安裝
nemoclaw --version
```

## 連接至 K8s 上的 OpenShell Gateway

```bash
# 轉發 Gateway Service（開發 / 測試環境）
kubectl port-forward svc/openshell 8080:8080 -n openshell

# 設定 NemoClaw 使用 K8s Gateway
nemoclaw gateway set k8s --endpoint https://localhost:8080

# 驗證連線
nemoclaw gateway status
```

生產環境建議透過 Ingress 或 Gateway API 暴露 OpenShell Gateway，避免使用 port-forward。

## 初始設定（K8s 環境）

```bash
# K8s 環境下的引導式設定
nemoclaw setup --runtime kubernetes

# 互動式設定流程：
# 1. 確認 K8s Gateway 連線
# 2. 選擇 AI Agent（OpenClaw / Hermes）
# 3. 配置推理 Provider（NVIDIA NIM 推薦）
# 4. 建立 K8s Secret（API Key）
# 5. 套用強化 Blueprint
# 6. 生成基準網路策略
```

## 啟動 Agent 沙箱（K8s Pod）

```bash
# 啟動 OpenClaw 沙箱（以 K8s Pod 執行）
nemoclaw start

# 確認 Pod 已建立
kubectl get pods -n openshell
# NAME                           READY   STATUS    RESTARTS   AGE
# openshell-gateway-xxxxx        1/1     Running   0          10m
# nemoclaw-openclaw-xxxxxxxx     1/1     Running   0          30s

# 查看沙箱狀態
nemoclaw status
# ✓ Runtime: kubernetes
# ✓ Sandbox: running (Pod: nemoclaw-openclaw-xxxxxxxx)
# ✓ Agent: OpenClaw v1.2.3 (active)
# ✓ Inference: NVIDIA NIM (llama-3.1-70b-instruct)
# ✓ Network Policy: standard (12 rules)
```

## 推理配置（K8s 環境）

在 K8s 環境中，推理後端連線通常使用 NVIDIA NIM 或內部部署的推理服務：

### 使用 NVIDIA NIM（外部服務）

```bash
# 設定 NVIDIA NIM 推理後端
nemoclaw inference set --provider nvidia_nim \
  --model llama-3.1-70b-instruct \
  --endpoint https://integrate.api.nvidia.com/v1
```

### 使用叢集內推理服務（In-Cluster Inference）

```bash
# 使用叢集內部的 NIM 或 Ollama 服務
nemoclaw inference set \
  --provider openai_compatible \
  --endpoint http://nim-service.inference.svc.cluster.local:8000/v1 \
  --model llama-3.1-70b-instruct
```

### K8s Secret 管理推理憑證

NemoClaw 透過 OpenShell Provider 機制管理憑證，在 K8s 模式下使用 Kubernetes Secret：

```bash
# OpenShell 自動建立或引用 K8s Secret
kubectl get secrets -n openshell
# NAME                          TYPE     DATA   AGE
# openshell-provider-nvidia-nim Opaque   1      5m
```

## 網路策略（K8s 環境）

在 Kubernetes 上，NemoClaw 的網路策略分為兩個層次：

### Layer 1：OpenShell Policy Proxy（L7 應用層）

由 OpenShell 的 Supervisor 內建 Policy Proxy 強制執行，控制 AI Agent 的所有對外 HTTP/HTTPS 流量：

```yaml
# NemoClaw 基準網路策略（OpenShell YAML 格式）
network:
  egress:
    # 允許 NVIDIA NIM 推理服務
    - name: nvidia-nim
      destination: integrate.api.nvidia.com
      methods: [POST]
      paths: ["/v1/chat/completions", "/v1/completions"]

    # 允許 OpenClaw 所需的套件更新
    - name: npm-registry
      destination: registry.npmjs.org
      methods: [GET]

    # 禁止其他出站流量（隱式 Deny All）
```

### Layer 2：Kubernetes NetworkPolicy（L3/L4 網路層）

OpenShell Helm Chart 自動建立 K8s NetworkPolicy，限制沙箱 Pod 的 SSH 入站：

```yaml
# 自動建立的 NetworkPolicy（由 OpenShell Helm Chart 管理）
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: openshell-sandbox-ssh-policy
  namespace: openshell
spec:
  podSelector:
    matchLabels:
      openshell.io/sandbox: "true"
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: openshell  # 僅允許來自 Gateway Pod
      ports:
        - port: 22
          protocol: TCP
  policyTypes:
    - Ingress
```

## 使用 ConfigMap 管理網路策略

在 K8s 環境中，可以使用 ConfigMap 管理 NemoClaw 的網路策略版本：

```yaml
# nemoclaw-policy.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nemoclaw-network-policy
  namespace: openshell
data:
  policy.yaml: |
    version: "1"
    network:
      egress:
        - name: allow-nvidia-nim
          destination: integrate.api.nvidia.com
          methods: [POST]
        - name: allow-github-read
          destination: api.github.com
          methods: [GET, HEAD]
```

```bash
kubectl apply -f nemoclaw-policy.yaml

# 從 ConfigMap 套用策略
nemoclaw policy set --from-configmap nemoclaw-network-policy
```

## GPU 支援（K8s 環境）

在 K8s 叢集中使用 GPU 加速沙箱：

### 前置需求

- 叢集節點已安裝 NVIDIA 驅動
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html) 或 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) 已部署至叢集

```bash
# 安裝 NVIDIA GPU Operator（若尚未安裝）
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
helm install gpu-operator nvidia/gpu-operator -n gpu-operator --create-namespace
```

### 啟用 GPU 沙箱

```bash
# 啟動含 GPU 的 NemoClaw 沙箱
nemoclaw start --gpu

# 確認 GPU 資源分配
kubectl describe pod nemoclaw-openclaw-xxxxxxxx -n openshell | grep -A5 "Limits:"
# Limits:
#   nvidia.com/gpu: 1
```

## 持久化 Workspace

NemoClaw 沙箱的工作區以 PersistentVolumeClaim（PVC）持久化，重啟後資料不遺失：

```bash
# 查看沙箱 PVC
kubectl get pvc -n openshell
# NAME                           STATUS   VOLUME        CAPACITY   ...
# workspace-openclaw-xxxxxxxx    Bound    pvc-xxxxxxx   2Gi        ...

# 自訂 Workspace 大小（透過 OpenShell Helm values 設定）
# server.workspaceDefaultStorageSize: "10Gi"
```

## 在 CI/CD Pipeline 中使用 NemoClaw

NemoClaw 適合整合至 Kubernetes-based CI/CD Pipeline，以安全沙箱執行 Agent 任務：

### GitHub Actions 範例

```yaml
# .github/workflows/agent-task.yml
name: AI Agent Task
on: [push]

jobs:
  agent-task:
    runs-on: self-hosted   # K8s 上的 Self-hosted Runner
    steps:
      - name: Setup NemoClaw
        run: |
          curl -LsSf https://install.nemoclaw.nvidia.com | sh
          nemoclaw gateway set ci --endpoint ${{ secrets.OPENSHELL_ENDPOINT }}

      - name: Run Agent Task
        env:
          NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
        run: |
          nemoclaw start --daemon
          # 執行 Agent 任務...
          nemoclaw exec -- openclaw "分析此 PR 的程式碼變更"
          nemoclaw stop
```

### ArgoCD Workflow 範例

```yaml
# argo-workflow-agent.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: nemoclaw-agent-task
spec:
  entrypoint: run-agent
  templates:
    - name: run-agent
      container:
        image: nemoclaw-cli:latest
        command: [sh, -c]
        args:
          - |
            nemoclaw setup --non-interactive \
              --gateway $OPENSHELL_ENDPOINT \
              --provider nvidia_nim \
              --model llama-3.1-70b-instruct
            nemoclaw start --daemon
            nemoclaw exec -- openclaw "執行指定任務"
            nemoclaw stop
        env:
          - name: NVIDIA_API_KEY
            valueFrom:
              secretKeyRef:
                name: nvidia-credentials
                key: api-key
```

## OpenShift 上的 NemoClaw

```bash
# 1. 先完成 OpenShell 的 OpenShift 安裝（見 OpenShell K8s 整合文件）

# 2. 設定 NemoClaw 連接 OpenShift 上的 Gateway
nemoclaw gateway set openshift \
  --endpoint https://openshell-route.apps.cluster.example.com

# 3. 初始設定
nemoclaw setup --runtime kubernetes

# 注意：OpenShift SCC 已由 OpenShell Helm Chart 配置
# openshell-sandbox Service Account 已有 privileged SCC
```

## 常見 K8s 問題排查

| 症狀 | 可能原因 | 解決方式 |
|------|---------|---------|
| Agent Pod 無法建立 | OpenShell Gateway 未連線 | 確認 Gateway Pod 狀態與 port-forward |
| 推理呼叫 403 | API Key Secret 不存在或過期 | `kubectl get secrets -n openshell` 確認 |
| 網路被阻斷 | NetworkPolicy 限制 | 確認 K8s NetworkPolicy 與 OpenShell 策略設定 |
| GPU 未分配 | GPU Operator 未安裝 | 安裝 NVIDIA GPU Operator |
| PVC Pending | 無可用 StorageClass | 確認叢集 StorageClass 與容量 |
| Blueprint 映像拉取失敗 | Image Pull Secret 未配置 | 設定 `server.sandboxImagePullSecrets` |
| Supervisor 啟動失敗（K8s < 1.33） | `image-volume` 不支援 | 確認 `supervisor.sideloadMethod: init-container` |
