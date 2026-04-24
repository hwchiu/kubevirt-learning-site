---
layout: doc
title: Cluster API Provider Metal3 — 故事驅動式學習
---

# Cluster API Provider Metal3 — 故事驅動式學習

透過一個完整的「裸金屬 Kubernetes 叢集部署」場景，帶你理解 CAPM3 各元件的角色與互動流程。

## 場景背景

> 小明是一家科技公司的 SRE，公司有 20 台閒置的實體伺服器。老闆說：「我們要在這些裸機上建立一個生產級 Kubernetes 叢集，而且要能像管理雲端資源一樣，用 YAML 宣告式管理。」
>
> 小明選擇了 Metal3 + CAPM3 方案。

## 第一幕：環境準備

小明先確認 Metal3 技術棧已就緒：

**已安裝的元件：**
- Management Cluster（一個小型 Kubernetes 叢集）
- Cluster API core、bootstrap、control-plane providers
- Baremetal Operator（BMO）與 Ironic
- ip-address-manager（IPAM）
- CAPM3 controller manager

```bash
# 檔案: README.md（參考指令）
# 安裝 CAPI providers
clusterctl init --core cluster-api:v1.12.0 \
    --bootstrap kubeadm:v1.12.0 \
    --control-plane kubeadm:v1.12.0

# 安裝 Metal3 infrastructure provider
clusterctl init --infrastructure metal3:v1.12.0
```

**BMO 已登記的 BareMetalHost：**

```yaml
# 檔案: examples/baremetalhost-sample.yaml（示意）
apiVersion: metal3.io/v1alpha1
kind: BareMetalHost
metadata:
  name: server-01
  namespace: metal3
  labels:
    environment: production
    role: worker
spec:
  online: false
  bootMACAddress: "aa:bb:cc:dd:ee:01"
  bmc:
    address: ipmi://192.168.1.101
    credentialsName: server-01-bmc-secret
```

> 此時 BMH 狀態為 `available`——代表這台伺服器已被 Ironic 檢測完畢，等待被分配使用。

## 第二幕：宣告目標叢集

小明撰寫叢集宣告：

```yaml
# 檔案: examples/cluster-sample.yaml（示意）
# 1. 先建立 Metal3Cluster（描述基礎設施端點）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: Metal3Cluster
metadata:
  name: production-cluster
  namespace: metal3
spec:
  controlPlaneEndpoint:
    host: 192.168.0.200   # VIP 位址
    port: 6443
  cloudProviderEnabled: false
---
# 2. 再建立 CAPI Cluster（引用 Metal3Cluster）
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: production-cluster
  namespace: metal3
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["192.168.0.0/18"]
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
    kind: Metal3Cluster
    name: production-cluster
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta2
    kind: KubeadmControlPlane
    name: production-cluster-kcp
```

**CAPM3 的反應（Metal3ClusterReconciler）：**

```go
// 檔案: baremetal/metal3cluster_manager.go
func (s *ClusterManager) Create(_ context.Context) error {
    // 驗證 ControlPlaneEndpoint 設定
    // 確認 Host 與 Port 不為空
}

func (s *ClusterManager) UpdateClusterStatus() error {
    // 設定 Metal3Cluster 的 Ready condition
    // 通知 CAPI 叢集基礎設施已就緒
}
```

1. `Metal3ClusterReconciler` 收到事件，取得 `Metal3Cluster`
2. 呼叫 `ClusterManager.Create()` 驗證設定
3. 呼叫 `UpdateClusterStatus()` 設定 Ready = true
4. CAPI Cluster 收到通知，開始建立 control plane 節點

## 第三幕：第一台 Control Plane 節點

CAPI 開始建立 control plane，建立了 `Metal3Machine`：

```yaml
# 檔案: examples/metal3machine-sample.yaml（示意）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: Metal3Machine
metadata:
  name: production-cluster-cp-0
  namespace: metal3
spec:
  image:
    url: "http://192.168.0.1/images/ubuntu-22.04-server.qcow2"
    checksum: "sha256:abc123..."
    checksumType: "sha256"
    diskFormat: "qcow2"
  hostSelector:
    matchLabels:
      environment: production
      role: control-plane
  dataTemplate:
    name: control-plane-data-template
    namespace: metal3
```

**`Metal3MachineReconciler` 的 reconcileNormal 開始執行：**

```
步驟 1：等待 bootstrap data 就緒（kubeadm 設定）
步驟 2：呼叫 machineMgr.Associate(ctx)
步驟 3：chooseHost() 找到 server-01（符合 control-plane label）
步驟 4：setHostSpec() 設定映像、user data
步驟 5：設定 BMH.spec.consumerRef = production-cluster-cp-0
步驟 6：設定 BMH.spec.online = true → 觸發 Ironic provisioning
```

> 小明看著 BMH 狀態從 `available` → `provisioning` → `provisioned`
> 幾分鐘後，第一台 control plane 伺服器上線！

## 第四幕：資料模板魔法

小明注意到每台 worker 節點需要獨立的 IP 位址。`Metal3DataTemplate` 幫助他自動化這個過程：

```yaml
# 檔案: examples/metal3datatemplate-sample.yaml（示意）
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: Metal3DataTemplate
metadata:
  name: worker-data-template
  namespace: metal3
spec:
  metaData:
    strings:
    - key: node-type
      value: "worker"
    indexes:
    - key: node-index
      prefix: "worker-"
      offset: 0
      step: 1
  networkData:
    networks:
      ipv4:
      - id: "baremetal"
        fromPoolRef:
          name: "worker-ip-pool"
```

**資料流程：**

```go
// 檔案: baremetal/metal3data_manager.go
func (m *DataManager) Reconcile(ctx context.Context) error {
    // 渲染模板：
    // worker-0 → IP: 192.168.1.10, hostname: "worker-0"
    // worker-1 → IP: 192.168.1.11, hostname: "worker-1"
    // 建立 Kubernetes Secret，注入到 BMH
}

func (m *DataManager) getAddressesFromPool(ctx context.Context, ...) {
    // 向 IPAM 申請 IP 位址（建立 IPClaim）
    // IPAM 從 IPPool 分配位址，回傳 AddressFromPool
}
```

> 每台 worker 節點自動獲得唯一的 IP 位址，無需手動設定！

## 第五幕：突發危機——節點宕機

週一早上，監控告警：`worker-3` 的 kubelet 超過 5 分鐘沒有回應。

CAPI 的 `MachineHealthCheck` 偵測到異常，建立了 `Metal3Remediation`：

```yaml
# 示意：CAPI MachineHealthCheck 自動建立
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: Metal3Remediation
metadata:
  name: production-cluster-worker-3
  namespace: metal3
spec:
  strategy:
    type: Reboot
    retryLimit: 2
    timeoutSeconds: 300
```

**`Metal3RemediationReconciler` 開始工作：**

```go
// 檔案: controllers/metal3remediation_controller.go
// Phase: Running
// 1. 備份 Node label
// 2. 刪除 Kubernetes Node 物件
// 3. 設定 BMH power off annotation → Ironic 執行 IPMI power off

// Phase: Waiting
// 4. 移除 power off annotation → Ironic 執行 IPMI power on
// 5. 等待 BMH.status.poweredOn = true
// 6. 等待 Kubernetes Node 重新出現
// 7. 還原備份的 Node label
```

```go
// 檔案: baremetal/metal3remediation_manager.go
func (r *RemediationManager) SetPowerOffAnnotation(ctx context.Context) error {
    // 對 BMH 設定 power off annotation
    // BMO 偵測到 annotation，呼叫 Ironic 執行 IPMI/Redfish power off
}

func (r *RemediationManager) TimeToRemediate(timeoutSeconds int32) (bool, time.Duration) {
    // 計算是否到了可以再次嘗試修復的時間
}
```

> 15 分鐘後，`worker-3` 自動重啟並重新加入叢集。小明收到告警解除通知，甚至不需要手動介入！

## 第六幕：叢集升級（Node Reuse）

半年後，Ubuntu 24.04 LTS 發布了。小明想升級 worker 節點的作業系統。

CAPM3 的 Node Reuse 功能讓升級可以重用同一台物理機器：

```go
// 檔案: baremetal/metal3machine_manager.go
const (
    nodeReuseLabelName = "infrastructure.cluster.x-k8s.io/node-reuse"
)

// 舊 Metal3Machine 刪除時，在 BMH 上設定 node-reuse label
// 指向對應的 MachineDeployment 名稱

// 新 Metal3Machine 建立時，chooseHost() 優先選取有對應
// node-reuse label 的 BMH，直接重新 provision
```

> 升級過程中，每台伺服器依序重新 provision 新映像，整個過程自動化完成！

## 回顧：關鍵元件職責

| 元件 | 場景中的角色 |
|------|------------|
| `Metal3ClusterReconciler` | 驗證叢集設定，設定 API endpoint |
| `Metal3MachineReconciler` | 選取 BMH，觸發 provisioning |
| `Metal3DataReconciler` | 渲染 hostname、IP 等節點特定設定 |
| `Metal3RemediationReconciler` | 自動重啟不健康的節點 |
| `BareMetalHost`（BMO）| 橋接 CAPM3 與 Ironic |
| `Ironic` | 實際執行 PXE boot、映像寫入、電源控制 |

::: tip 小結
CAPM3 的核心設計哲學是「宣告式裸金屬管理」——你只需要描述**期望的狀態**（我需要 3 台 control plane + 5 台 worker），系統自動選取實體機器、provision 映像、管理 IP 位址、處理故障修復。
:::

::: info 相關章節
- [學習路徑入口](/cluster-api-provider-metal3/learning-path/)
- [專案簡介](/cluster-api-provider-metal3/)
- [核心功能](/cluster-api-provider-metal3/core-features)
- [節點修復](/cluster-api-provider-metal3/remediation)
:::
