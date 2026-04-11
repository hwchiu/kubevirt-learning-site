---
layout: doc
---

# Node Maintenance Operator — RBAC 與權限分析

本頁面針對 Security Engineer 與 Platform Engineer，逐一解析 Node Maintenance Operator 所需的 RBAC 權限、各角色職責，以及每個維護步驟對應的具體權限依據。

---

## 1. ClusterRole: manager-role（主要權限）

來源：`config/rbac/role.yaml`

此 ClusterRole 綁定至 controller-manager ServiceAccount，涵蓋 operator 執行完整維護流程所需的所有叢集層級權限。

| API Group | 資源 | Verbs | 原因 |
|-----------|------|-------|------|
| `""` (core) | namespaces | create, get | 建立 lease holder 追蹤用的 namespace |
| `""` (core) | nodes | get, list, patch, update, watch | 取得節點狀態、套用 taint、cordon/uncordon |
| `""` (core) | pods | get, list, watch | 列出節點上的 Pod 以決定驅逐候選者 |
| `""` (core) | pods/eviction | create | 驅逐節點上的 Pod |
| `apps` | daemonsets, deployments, replicasets, statefulsets | get, list, watch | 識別 Pod 擁有者，正確處理 DaemonSet（跳過驅逐） |
| `coordination.k8s.io` | leases | create, get, list, patch, update, watch | Leader election 與多實例 lease 協調 |
| `monitoring.coreos.com` | servicemonitors | create, get | 整合 Prometheus 監控（選用） |
| `nodemaintenance.medik8s.io` | nodemaintenances | create, delete, get, list, patch, update, watch | 管理 NodeMaintenance CR |
| `nodemaintenance.medik8s.io` | nodemaintenances/finalizers | update | 管理清理 finalizer |
| `nodemaintenance.medik8s.io` | nodemaintenances/status | get, patch, update | 更新維護進度（drainProgress、phase） |
| `oauth.openshift.io` | `*` | `*` | OpenShift 特有：webhook 驗證 SCC |
| `policy` | poddisruptionbudgets | get, list, watch | 驅逐時尊重 PodDisruptionBudget |

---

## 2. ClusterRole: proxy-role（metrics 安全代理）

來源：`config/rbac/auth_proxy_role.yaml`

此 ClusterRole 供 kube-rbac-proxy sidecar 使用，保護 metrics 端點不被未授權存取。

| API Group | 資源 | Verbs | 原因 |
|-----------|------|-------|------|
| `authentication.k8s.io` | tokenreviews | create | 驗證 metrics 請求的 token |
| `authorization.k8s.io` | subjectaccessreviews | create | 確認請求者有 metrics 存取權 |

---

## 3. Role: leader-election-role（namespace 範圍）

來源：`config/rbac/leader_election_role.yaml`
命名空間：`node-maintenance-operator-system`

此 Role 限定在 operator 自身的命名空間內，用於多副本情境下的 leader election 協調。

| API Group | 資源 | Verbs |
|-----------|------|-------|
| `""` | configmaps | get, list, watch, create, update, patch, delete |
| `coordination.k8s.io` | leases | get, list, watch, create, update, patch, delete |
| `""` | events | create, patch |

---

## 4. 維護工作流程對應權限

以下流程圖說明每個維護階段實際使用哪些 RBAC 權限：

![NMO 維護工作流程對應權限](/diagrams/node-maintenance-operator/nmo-rbac-workflow.png)

步驟 7–8 會迴圈執行，直到節點上所有符合條件的 Pod 均被驅逐或逾時。DaemonSet 管理的 Pod 在步驟 7 識別擁有者後會直接跳過驅逐（需要 `apps` 群組的 `daemonsets: get` 權限）。

---

## 5. Service Account

| 項目 | 值 |
|------|----|
| 名稱（base） | `controller-manager` |
| 名稱（OLM） | `node-maintenance-operator-controller-manager` |
| 命名空間 | `node-maintenance-operator-system` |

OLM 安裝時，Operator Lifecycle Manager 會自動建立並管理此 ServiceAccount，並將上述 ClusterRole 與 Role 分別透過 ClusterRoleBinding 與 RoleBinding 綁定至此帳號。

---

## 6. oauth.openshift.io 野生萬用字元的理由

::: warning 廣泛的 OpenShift 權限
`oauth.openshift.io/*` 與 `verbs: *` 是 OpenShift 特有需求，用於 webhook 對 SecurityContextConstraints (SCC) 的驗證。此權限在 Kubernetes 原生叢集上不會生效（該 API group 根本不存在）。

如有安全疑慮，可向 [medik8s 社群](https://github.com/medik8s/node-maintenance-operator) 反映縮小範圍的需求。
:::

---

## 7. 最小化安裝（不含 OpenShift 權限）

在純 Kubernetes（vanilla）環境中，`oauth.openshift.io` 萬用字元權限並非必要。由於該 API group 在非 OpenShift 叢集上不存在，Kubernetes 不會套用此規則，但若希望明確移除以符合最小權限原則，可在部署前編輯 ClusterRole：

```yaml
// 檔案: config/rbac/role.yaml
# 移除以下區塊（僅適用於非 OpenShift 叢集）
- apiGroups:
  - oauth.openshift.io
  resources:
  - '*'
  verbs:
  - '*'
```

移除後請重新套用 ClusterRole：

```bash
// 檔案: scripts/apply-rbac.sh
kubectl apply -f config/rbac/role.yaml
```

::: info 相關章節
- [安裝與部署](./installation-and-deployment) — 了解如何透過 OLM 或 Helm 部署 Node Maintenance Operator，以及 RBAC 資源的自動建立流程。
- [疑難排解與偵錯](./troubleshooting-and-debugging) — 當 operator 因 RBAC 權限不足而無法正常運作時，查閱常見錯誤訊息與排除方式。
:::
