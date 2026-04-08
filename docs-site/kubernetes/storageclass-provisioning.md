---
layout: doc
---

# Kubernetes — StorageClass 與動態佈建

::: info 相關章節
- 架構基礎請參閱 [PV/PVC 架構總覽](./pv-pvc-architecture)
- 生命週期請參閱 [PV/PVC 生命週期與綁定機制](./pv-pvc-lifecycle)
- CSI 整合架構請參閱 [CSI 整合架構](./csi-integration)
- 故障排除請參閱 [常見問題與排錯指南](./troubleshooting)
:::

## StorageClass 欄位詳解

API 型別定義：`staging/src/k8s.io/api/storage/v1/types.go`

```go
type StorageClass struct {
    metav1.TypeMeta
    metav1.ObjectMeta

    // 佈建器名稱（e.g. "kubernetes.io/aws-ebs" 或 CSI driver name）
    Provisioner string

    // 傳遞給佈建器的參數（鍵值對）
    Parameters map[string]string

    // 回收策略：Delete（預設）或 Retain
    ReclaimPolicy *v1.PersistentVolumeReclaimPolicy

    // 掛載選項（傳遞給 mount 指令）
    MountOptions []string

    // 是否允許 Volume 擴容（需佈建器支援）
    AllowVolumeExpansion *bool

    // 綁定模式：Immediate 或 WaitForFirstConsumer
    VolumeBindingMode *VolumeBindingMode

    // 允許的拓撲約束（配合 WaitForFirstConsumer 使用）
    AllowedTopologies []v1.TopologySelectorTerm
}
```

### 常見 StorageClass 範例

```yaml
# CSI 驅動（AWS EBS）
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3-encrypted
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

---
# NFS（in-tree）
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-client
provisioner: cluster.local/nfs-subdir-external-provisioner
parameters:
  server: nfs-server.example.com
  path: /exported/path
  archiveOnDelete: "false"
reclaimPolicy: Delete
```

---

## 動態佈建流程

```mermaid
flowchart TD
    A["使用者建立 PVC\n（指定 storageClassName）"] --> B{volumeBindingMode?}
    B -->|Immediate| C["PV Controller 偵測到 PVC"]
    B -->|WaitForFirstConsumer| D["等待 Pod 排程\n（Scheduler 選定節點）"]
    D --> C
    C --> E["查詢 StorageClass\n取得 provisioner 名稱"]
    E --> F["PV Controller 加入 Annotation\nvolume.beta.kubernetes.io/storage-provisioner"]
    F --> G["外部佈建器（CSI external-provisioner）\n監聽到 PVC"]
    G --> H["佈建器呼叫 CSI CreateVolume\n（帶 parameters 與拓撲資訊）"]
    H --> I["CSI Driver 在後端建立儲存卷"]
    I --> J["佈建器建立 PV\n（設定 claimRef 指向 PVC）"]
    J --> K["PV Controller 偵測到 PV 建立"]
    K --> L["PV Controller 綁定 PV ↔ PVC"]
    L --> M["PVC 狀態: Bound ✅"]
```

### 關鍵原始碼位置

| 功能 | 原始碼路徑 |
|------|-----------|
| 動態佈建觸發 | `pkg/controller/volume/persistentvolume/controller.go` → `provisionClaimOperation()` |
| Annotation 設定 | `pkg/controller/volume/persistentvolume/controller.go` → `setClaimProvisioner()` |
| WaitForFirstConsumer | `pkg/controller/volume/persistentvolume/scheduler_binder.go` |
| StorageClass 查詢 | `pkg/controller/volume/persistentvolume/util/` |
| 儲存 Admission | `plugin/pkg/admission/storage/` |

---

## 預設 StorageClass

叢集可以設定一個預設 StorageClass，當 PVC 未指定 `storageClassName` 時自動使用：

```yaml
metadata:
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
```

**注意事項**：
- 叢集中最多只能有一個預設 StorageClass（否則 Admission Controller 會拒絕）
- 相關 Admission Controller：`plugin/pkg/admission/storage/persistentvolume/admission.go`
- 若 PVC 明確設定 `storageClassName: ""`（空字串），表示**不使用動態佈建**，只匹配靜態 PV

---

## 拓撲感知動態佈建

配合 `volumeBindingMode: WaitForFirstConsumer` 與 `allowedTopologies`，實現跨可用區的拓撲感知佈建：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: topology-aware
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
allowedTopologies:
  - matchLabelExpressions:
      - key: topology.kubernetes.io/zone
        values:
          - ap-northeast-1a
          - ap-northeast-1c
```

```mermaid
sequenceDiagram
    participant Scheduler
    participant API as API Server
    participant PVCtrl as PV Controller
    participant Provisioner as CSI Provisioner

    Scheduler->>API: Pod 排程到 ap-northeast-1a 區的節點
    Scheduler->>API: 設定 PVC Annotation\nselected-node=node-az-1a
    PVCtrl->>Provisioner: 觸發佈建，帶拓撲資訊\n{ zone: ap-northeast-1a }
    Provisioner->>Provisioner: 在 ap-northeast-1a 建立 EBS
    Provisioner->>API: 建立 PV（NodeAffinity 指定 zone）
    PVCtrl->>API: 綁定完成
```

---

## Volume 擴容（Volume Expansion）

### 啟用條件

1. StorageClass 設定 `allowVolumeExpansion: true`
2. CSI 驅動支援 `EXPAND_VOLUME` capability
3. Kubernetes 版本 >= 1.11（Beta）

### 擴容流程

```mermaid
flowchart LR
    A["使用者修改 PVC\nspec.resources.requests.storage"] -->|增大容量| B["PVC Controller\n偵測到 resize 請求"]
    B --> C["Volume Expand Controller\npkg/controller/volume/expand/"]
    C --> D["呼叫 CSI ControllerExpandVolume\n（在控制平面執行）"]
    D --> E{是否需要\nFilesystem Resize?}
    E -->|是（Filesystem 模式）| F["等待 Pod 使用 Volume\nKubelet 執行 NodeExpandVolume"]
    E -->|否（Block 模式）| G["擴容完成 ✅"]
    F --> G
```

### 原始碼位置

- 控制器主邏輯：`pkg/controller/volume/expand/expand_controller.go`
- Kubelet 端擴容：`pkg/kubelet/volumemanager/reconciler/`
- CSI 介面：`pkg/volume/csi/expander.go`

### 注意事項

- **只能擴大，不能縮小**：Kubernetes 不支援 Volume 縮容（會被 Admission 拒絕）
- **線上擴容（online resize）**：Kubernetes 1.16+ 支援 Pod 仍在運行時擴容
- **離線擴容（offline resize）**：需要停止 Pod 才能擴容（部分 CSI 驅動限制）

---

## StorageClass 參數常見設定

| 佈建器 | 常用 parameters | 說明 |
|--------|----------------|------|
| `ebs.csi.aws.com` | `type: gp3`, `iops`, `throughput` | AWS EBS 卷類型與效能設定 |
| `disk.csi.azure.com` | `skuName: Premium_LRS` | Azure Disk 儲存類型 |
| `pd.csi.storage.gke.io` | `type: pd-ssd` | GCP Persistent Disk 類型 |
| `nfs.csi.k8s.io` | `server`, `share` | NFS CSI 連線資訊 |
| `rook-ceph.rbd.csi.ceph.com` | `pool`, `imageFeatures` | Ceph RBD 設定 |
