---
layout: doc
---

# Node Maintenance Operator — 部署與設定

**章節：** 系統架構｜**對象：** Platform engineers、Operators

---

## 部署方式比較

| 方法 | 適用情境 | Webhook 支援 |
|------|---------|-------------|
| OLM Bundle（推薦） | OpenShift / 有 OLM 的 K8s | ✅ 自動 |
| Kustomize (`make deploy`) | 開發測試 | ❌ 需另外設定 |
| 本機執行 (`make run`) | 本機開發 | ❌ |

---

## OLM Bundle 部署（推薦）

OLM Bundle 是最簡易且完整支援 Webhook 的部署方式，適合 OpenShift 或已安裝 OLM 的 Kubernetes 叢集。

```bash
# 最新版（main branch）
operator-sdk run bundle quay.io/medik8s/node-maintenance-operator-bundle:latest \
  -n openshift-workload-availability

# 確認安裝
kubectl get csv -n openshift-workload-availability
kubectl get deployment -n node-maintenance-operator-system
```

Bundle 的相關設定定義於 `bundle/manifests/node-maintenance-operator.clusterserviceversion.yaml`：

| 欄位 | 值 |
|------|----|
| Channel | `stable` |
| Min Kubernetes | `1.23.0` |
| InstallMode | `AllNamespaces`（cluster-wide） |
| Suggested Namespace | `openshift-workload-availability` |

::: tip
使用 OLM Bundle 部署時，Webhook 所需的 TLS 憑證會由 OLM 自動注入，無需額外設定 cert-manager。
:::

---

## Kustomize 部署（含 cert-manager）

若環境中沒有 OLM，但仍需 Webhook 功能，可搭配 cert-manager 進行部署。

```bash
// 檔案: Makefile（參考步驟）
# 1. 安裝 cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# 2. 解除 config/default/kustomization.yaml 中 cert-manager 相關的註解
# 取消 `- ../certmanager`
# 取消 `- webhookcainjection_patch.yaml`
# 取消 vars 區段

# 3. 部署
kustomize build config/default | kubectl apply -f -
```

::: warning Webhook 與 make deploy
使用 `make deploy` 部署時，Webhook 無法正常運作（缺少憑證 volume）。建議使用 OLM Bundle 或搭配 cert-manager 進行完整部署。
:::

---

## Deployment 規格

Operator 的資源限制與 Pod 設定定義於 `config/manager/manager.yaml`：

```yaml
// 檔案: config/manager/manager.yaml
resources:
  limits:
    cpu: 200m
    memory: 100Mi
  requests:
    cpu: 100m
    memory: 20Mi

priorityClassName: system-cluster-critical
terminationGracePeriodSeconds: 10
```

`system-cluster-critical` 的 `priorityClassName` 確保 Operator Pod 在節點資源緊張時不易被驅逐。

---

## 所有啟動參數

以下參數來源於 `main.go`，可在部署時透過 `args` 欄位覆寫：

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--metrics-bind-address` | `:8080` | Prometheus metrics 端點 |
| `--health-probe-bind-address` | `:8081` | 健康探針端點 |
| `--leader-elect` | `false` | 啟用 leader election（HA 必須） |
| `--enable-http2` | `false` | 啟用 HTTP/2（預設關閉以防範 CVE） |
| `--zap-level` | `info` | 日誌等級 |

::: tip HA 部署
在多副本或高可用部署中，請務必將 `--leader-elect` 設為 `true`，以確保同一時間只有一個 controller 處理 reconcile 迴圈。
:::

---

## 節點親和性與容忍

Operator 預設設有 Toleration，允許排程到 infra 或 control-plane 節點，避免佔用一般工作節點資源：

```yaml
// 檔案: config/manager/manager.yaml
tolerations:
  - key: node-role.kubernetes.io/master
    operator: Exists
    effect: NoSchedule
  - key: node-role.kubernetes.io/control-plane
    operator: Exists
    effect: NoSchedule
  - key: node-role.kubernetes.io/infra
    operator: Exists
    effect: NoSchedule
  - key: node-role.kubernetes.io/infra
    operator: Exists
    effect: NoExecute
```

---

## Webhook 憑證

Webhook 的 TLS 憑證支援兩種注入方式（來源：`main.go` 第 178–207 行）：

| 方式 | 憑證路徑 | 適用情境 |
|------|---------|---------|
| **OLM 自動注入**（預設） | `/apiserver.local.config/certificates/` | OLM Bundle 部署 |
| **cert-manager** | 由 cert-manager 掛載至 Pod | Kustomize 部署 |

若使用 OLM Bundle，Operator 啟動時會自動偵測 `/apiserver.local.config/certificates/` 路徑是否存在，並以此路徑的憑證啟動 Webhook Server。

---

## 環境變數

以下環境變數由 Kubernetes Downward API 或 Operator 設定自動注入：

| 變數 | 說明 | 預設 |
|------|------|------|
| `OPERATOR_NAMESPACE` | 透過 downward API 注入 Pod 所在 namespace | （自動） |
| `LEASE_NAMESPACE` | Lease 物件存放的 namespace | `medik8s-leases` |

---

## 驗證安裝

部署完成後，執行以下指令確認各元件正常運作：

```bash
# 確認 operator pod 正常運作
kubectl get pods -n node-maintenance-operator-system

# 確認 CRD 已安裝
kubectl get crd nodemaintenances.nodemaintenance.medik8s.io

# 確認 webhook 已設定
kubectl get validatingwebhookconfigurations | grep nodemaintenance

# 查看 operator 日誌
kubectl logs -n node-maintenance-operator-system \
  -l control-plane=controller-manager -f
```

::: tip 排查建議
若 Pod 無法正常啟動，請優先查看 Operator 日誌，並確認 CRD 與 Webhook 設定均已正確建立。詳見 [Troubleshooting & Debugging](./troubleshooting-and-debugging) 章節。
:::

---

::: info 相關章節
- [RBAC 與權限設定](./rbac-and-permissions) — Operator 所需的 ClusterRole、ServiceAccount 設定說明
- [Validation Webhooks](./validation-webhooks) — NodeMaintenance 資源的驗證邏輯與 Webhook 運作方式
- [Troubleshooting & Debugging](./troubleshooting-and-debugging) — 常見問題排查與日誌分析
:::
