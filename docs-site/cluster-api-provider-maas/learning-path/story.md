---
layout: doc
title: Cluster API Provider MAAS — 故事驅動式學習
---

# Cluster API Provider MAAS — 故事驅動式學習

## 情境：一間新創公司的裸金屬 Kubernetes 叢集

小明是一間新創公司的基礎設施工程師。公司決定在自有機房的裸金屬伺服器上搭建 Kubernetes 叢集，並要求能像雲端一樣「宣告式管理」。他選擇了 Canonical MAAS 管理裸金屬機器，並導入 Cluster API（CAPI）搭配 CAPMAAS 實現自動化。

---

## 第一章：環境準備

小明首先在 MAAS 中完成機器的 Commission（硬體探索與測試），確保每台機器都進入 `Ready` 狀態。接著，他上傳包含 Kubernetes 1.26.4 的 Custom Image：

```
映像檔名稱：custom/u-2204-0-k-1264-0
```

然後在管理叢集（management cluster）中設定 `~/.cluster-api/clusterctl.yaml`：

```yaml
# 檔案: README.md（clusterctl 設定範例）
MAAS_API_KEY: abc123:def456:ghi789
MAAS_ENDPOINT: http://10.11.130.11:5240/MAAS
MAAS_DNS_DOMAIN: k8s.maas

KUBERNETES_VERSION: v1.26.4
CONTROL_PLANE_MACHINE_IMAGE: custom/u-2204-0-k-1264-0
CONTROL_PLANE_MACHINE_MINCPU: 4
CONTROL_PLANE_MACHINE_MINMEMORY: 8192
CONTROL_PLANE_MACHINE_RESOURCEPOOL: cp-pool
CONTROL_PLANE_MACHINE_TAG: control-plane

WORKER_MACHINE_IMAGE: custom/u-2204-0-k-1264-0
WORKER_MACHINE_MINCPU: 4
WORKER_MACHINE_MINMEMORY: 8192
WORKER_MACHINE_RESOURCEPOOL: worker-pool
WORKER_MACHINE_TAG: worker
```

初始化 CAPMAAS Infrastructure Provider：

```bash
clusterctl init --infrastructure maas:v0.7.0
```

::: tip 初始化做了什麼？
`clusterctl init` 會在管理叢集中安裝 CAPMAAS 的 CRD（MaasCluster、MaasMachine、MaasMachineTemplate）以及 CAPMAAS Controller Deployment，並從 `clusterctl.yaml` 讀取環境變數設定 Secret。
:::

---

## 第二章：建立叢集宣告

小明用 clusterctl 產生叢集 Manifest，並 apply 到管理叢集：

```bash
clusterctl generate cluster prod-cluster \
  --infrastructure=maas:v0.7.0 \
  --kubernetes-version v1.26.4 \
  --control-plane-machine-count=3 \
  --worker-machine-count=5 | kubectl apply -f -
```

這會建立以下 Kubernetes 物件：

```
Cluster (CAPI)
MaasCluster (CAPMAAS)
KubeadmControlPlane (CABPK)
MaasMachineTemplate (CAPMAAS) x2
MachineDeployment (CAPI)
KubeadmConfigTemplate (CABPK)
```

---

## 第三章：MaasClusterReconciler 的第一次協調

CAPMAAS 的 `MaasClusterReconciler` 感知到新的 `MaasCluster` 物件，開始第一次協調：

**步驟 1：加入 Finalizer**

```go
// 檔案: controllers/maascluster_controller.go

if !controllerutil.ContainsFinalizer(maasCluster, infrav1beta1.ClusterFinalizer) {
    controllerutil.AddFinalizer(maasCluster, infrav1beta1.ClusterFinalizer)
    return ctrl.Result{}, nil
}
```

**步驟 2：建立 DNS Resource**

Controller 呼叫 `dns.Service.ReconcileDNS()`，在 MAAS 中建立 DNS 記錄：
- 名稱自動生成：`prod-cluster-a1b2c3.k8s.maas`（`DnsSuffixLength = 6`）
- TTL：10 秒（低 TTL 讓 DNS 更新快速生效）

小明觀察 MaasCluster 狀態：

```bash
kubectl get maascluster prod-cluster -o yaml
```

看到 `status.network.dnsName: prod-cluster-a1b2c3.k8s.maas` 已填入，Condition `LoadBalancerReady` 變為 `True`。

---

## 第四章：機器佈建的漫長等待

接著，CAPI Machine Controller 為每個 `Machine` 建立對應的 `MaasMachine`。`MaasMachineReconciler` 開始為 Control Plane 機器進行協調：

**階段一：等待 Bootstrap Data**

```
MachineDeployed = False (WaitingForBootstrapData)
```

`KubeadmControlPlane` Controller 正在生成初始化腳本，還沒好。小明等了約 30 秒……

**階段二：Allocate 裸金屬機器**

Bootstrap Secret 就緒後，Controller 呼叫 MAAS Allocate API：

```
Allocating with constraints:
  minCPU: 4
  minMemory: 8192
  resourcePool: cp-pool
  tags: [control-plane]
  zone: (from FailureDomain)
```

MAAS 回傳機器 `systemID: xyz789`，Controller 立刻設定：

```
ProviderID: maas:///zone-a/xyz789
SystemID: xyz789
```

**階段三：Deploy 映像檔**

Controller 停用 Swap，然後呼叫 Deploy：

```
DeployMachine:
  image: custom/u-2204-0-k-1264-0
  OSSystem: custom
  userData: (base64 of cloud-init script)
  ephemeral: false
```

機器狀態變為 `Deploying`，Condition：

```
MachineDeployed = False (MachineDeploying)
```

這個過程需要 5-15 分鐘（PXE 啟動 + OS 安裝 + kubeadm init）。

::: warning 常見踩坑：映像檔名稱錯誤
如果 `image` 欄位填錯（例如漏了 `custom/` 前綴），MAAS Deploy API 會回傳錯誤，Condition 變為 `MachineDeployFailed`。記得檢查映像檔在 MAAS 的完整名稱。
:::

---

## 第五章：DNS 附加與 API Server 上線

第一台 Control Plane 機器 Deploy 完成後，狀態變為 `Deployed`，IP 地址設定到 `status.addresses`。

`MaasClusterReconciler` 再次協調，呼叫 `reconcileDNSAttachments()`，將這台機器的 ExternalIP 加入 DNS 記錄：

```
DNS: prod-cluster-a1b2c3.k8s.maas → [10.0.1.10]
```

同時，`ReconcileMaasClusterWhenAPIServerIsOnline()` 啟動一個 goroutine 輪詢 API Server：

```go
// 檔案: pkg/maas/scope/cluster.go

_ = wait.PollImmediateInfinite(time.Second*1, func() (bool, error) {
    return s.IsAPIServerOnline()
})
```

等待 kubeadm 完成初始化後，API Server 上線，goroutine 透過 `GenericEventChannel` 發送事件，觸發最後一次 Cluster 協調，設定：

```
APIServerAvailable = True
```

---

## 第六章：Worker 機器加入叢集

所有 Worker 機器遵循相同的佈建流程，但有一個不同點：

**Worker 機器不需要 DNS 附加**

```go
// 檔案: controllers/maasmachine_controller.go

func (r *MaasMachineReconciler) reconcileDNSAttachment(
    machineScope *scope.MachineScope,
    clusterScope *scope.ClusterScope,
    m *infrav1beta1.Machine,
) error {
    if !machineScope.IsControlPlane() {
        return nil  // Worker 直接跳過
    }
    // ...
}
```

Worker 機器佈建完成後，kubelet 啟動並透過 kubeadm join 指令加入叢集。Controller 最後呼叫 `SetNodeProviderID()` 在 Node 物件上設定 ProviderID：

```go
// 檔案: pkg/maas/scope/machine.go

node.Spec.ProviderID = providerID  // "maas:///zone-a/xyz789"
```

---

## 第七章：叢集縮容與機器回收

三個月後，公司決定縮減 Worker 數量。小明修改 `MachineDeployment` 的 replicas：

```bash
kubectl scale machinedeployment prod-cluster-md-0 --replicas=2
```

CAPI 會刪除多餘的 `Machine` 和 `MaasMachine`。`MaasMachineReconciler` 進行刪除協調：

1. 確認機器不是 CP（跳過 DNS 移除）
2. 呼叫 MAAS Release API
3. 移除 `MaasMachine` 的 Finalizer

機器回到 `Ready` 狀態，重新進入 MAAS 的可用資源池。

---

## 知識測驗

以下問題幫助你確認是否理解核心概念：

**Q1：如果 MAAS 中沒有符合 `resourcePool` 和 `tags` 條件的機器，會發生什麼事？**

::: details 答案
MAAS Allocate API 會回傳錯誤（無可用機器）。`deployMachine()` 函數回傳 error，Controller 設定 Condition `MachineDeployedCondition = False (MachineDeployFailed)`。Controller 會在下次 Reconcile 時重試（但不自動觸發，需等待 `syncPeriod` 到期或手動觸發）。
:::

**Q2：Control Plane 機器意外關機（IPMI 斷電），CAPMAAS 會如何處理？**

::: details 答案
`MaasMachineReconciler` 偵測到 `MachinePowered = false` 且 `MachineState = Deployed`，會呼叫 `machineSvc.PowerOnMachine()`，然後設定 `RequeueAfter: 1 * time.Minute` 等待電源恢復後再次確認。
:::

**Q3：`MaasCluster` 刪除時，CAPMAAS 如何確保資源被完整清理？**

::: details 答案
`MaasClusterReconciler.reconcileDelete()` 會先列出所有 `MaasMachine`，如果還有機器存在，就設定 `RequeueAfter: 10 * time.Second` 等待。直到所有 `MaasMachine` 都被刪除並釋放 Finalizer 後，才移除 `MaasCluster` 的 Finalizer，讓叢集物件被 Kubernetes GC 刪除。
:::

---

## 學習總結

| 階段 | 關鍵物件 | 關鍵操作 |
|------|---------|---------|
| 環境準備 | clusterctl.yaml | MAAS_ENDPOINT、MAAS_API_KEY 設定 |
| 建立叢集 | MaasCluster | DNS Resource 建立 |
| 機器佈建 | MaasMachine | MAAS Allocate + Deploy |
| DNS 附加 | MaasCluster | Control Plane IP → DNS Record |
| API Server 上線 | ClusterScope | 非同步輪詢 + GenericEvent |
| ProviderID 設定 | MachineScope | Workload 叢集 Node 物件 |
| 機器回收 | MaasMachine | MAAS Release |

::: info 相關章節
- [學習路徑入口](./index) — 查看完整學習路線建議
- [核心功能](../core-features) — 功能說明與程式碼解析
- [控制器與 API](../controllers-api) — CRD 欄位完整參考
:::
