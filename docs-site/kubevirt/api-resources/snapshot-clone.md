# Snapshot、Clone 與 Export — 資料保護與搬移

KubeVirt 提供了完整的 VM 資料保護與搬移解決方案，包含快照（Snapshot）、克隆（Clone）與匯出（Export）三大功能，讓工程師可以在不中斷服務的情況下保護 VM 狀態、複製環境或將 VM 磁碟遷移到其他平台。

:::info 前提條件
本章節所有功能都需要：
1. 叢集安裝了支援 **VolumeSnapshot** 的 CSI 驅動（如 Ceph RBD CSI、vSphere CSI、AWS EBS CSI）
2. 叢集中存在 **VolumeSnapshotClass** 資源
3. KubeVirt >= v0.35.0（Snapshot/Restore），>= v0.57.0（Clone），>= v0.58.0（Export）
:::

---

## VirtualMachineSnapshot 完整說明

### 用途

`VirtualMachineSnapshot` 用於建立 VM 在特定時間點的完整狀態快照，常見使用場景：

- **測試前保護**：升級應用程式或核心前先建立快照，升級失敗可快速還原
- **週期性備份**：排程建立快照作為備份策略的一部分
- **環境複製基礎**：以快照為來源，Clone 出多個相同環境的 VM
- **問題排查**：保留問題發生時的磁碟狀態，供事後分析

### Spec 欄位

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: ubuntu-snapshot-20240115
  namespace: production
spec:
  # source：指向要快照的 VirtualMachine
  source:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-web-server

  # deletionPolicy：當 Snapshot 被刪除時，對應的底層 VolumeSnapshot 如何處理
  # OnVMDelete（預設）: 當 VM 被刪除時，快照自動刪除
  # Retain: 即使 VM 被刪除，快照仍然保留
  deletionPolicy: Retain

  # failureDeadline：快照建立的超時時間
  # 若超過此時間仍未完成，快照標記為失敗
  # 格式：Go duration 字串（如 "5m", "1h30m"）
  failureDeadline: "5m"
```

### Status 欄位詳解

```yaml
status:
  # 快照建立時間
  creationTime: "2024-01-15T10:30:00Z"

  # 快照是否已就緒可用於還原
  readyToUse: true

  # 快照當前階段
  # InProgress: 正在建立中
  # Succeeded:  建立成功
  # Failed:     建立失敗
  phase: Succeeded

  # 錯誤資訊（建立失敗時填寫）
  error:
    message: ""
    time: ""

  # 快照包含的 Volume 清單
  snapshotVolumes:
    includedVolumes:
      - rootdisk
      - datadisk
    excludedVolumes:
      - ephemeral-disk  # 不支援快照的 volume 會被排除

  # 對應的 VirtualMachineSnapshotContent 名稱
  virtualMachineSnapshotContentName: "vmsnapshot-content-abc123"

  # 快照指示標記（Indications）
  indications:
    - Online          # VM 在線時建立的快照
    - GuestAgent      # 有 guest agent，執行了 quiesce（檔案系統凍結）
```

### Snapshot Indications 完整說明

| Indication | 說明 | 資料一致性 |
|-----------|------|-----------|
| `Online` | VM 正在運行時建立快照 | Crash-consistent（類似拔電） |
| `GuestAgent` | 有 guest agent，成功執行 quiesce | Application-consistent（最佳） |
| `NoGuestAgent` | 沒有 guest agent，無法 quiesce | Crash-consistent |
| `QuiesceTimeout` | 有 guest agent 但 quiesce 超時 | Crash-consistent（quiesce 失敗） |
| `Paused` | VM 被暫停後建立的快照 | Crash-consistent（較安全） |

:::tip 提升快照一致性
若要取得 Application-consistent 快照（確保資料庫等應用的完整性），需要在 VM 內安裝 **QEMU Guest Agent**：

```bash
# Ubuntu/Debian
sudo apt-get install qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# CentOS/RHEL
sudo yum install qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent
```

安裝後，KubeVirt 建立快照時會自動要求 guest agent 執行 `fsfreeze`，確保檔案系統一致性。
:::

---

## VirtualMachineSnapshotContent

`VirtualMachineSnapshotContent` 是實際儲存快照資料的底層物件，通常由 KubeVirt 自動建立和管理，工程師一般不需要手動操作。

### 結構說明

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshotContent
metadata:
  name: vmsnapshot-content-abc123
  namespace: production
spec:
  # 關聯的 VirtualMachineSnapshot 名稱
  virtualMachineSnapshotName: ubuntu-snapshot-20240115

  # 快照時的 VM 完整規格（用於還原時重建 VM）
  source:
    virtualMachine:
      # ... 快照時完整的 VM spec

  # 每個 Volume 對應的備份資訊
  volumeBackups:
    - volumeName: rootdisk
      persistentVolumeClaim:
        name: ubuntu-web-server-rootdisk
      volumeSnapshotName: vmsnapshot-rootdisk-xyz789

    - volumeName: datadisk
      persistentVolumeClaim:
        name: ubuntu-web-server-datadisk
      volumeSnapshotName: vmsnapshot-datadisk-xyz790
```

:::info 底層 VolumeSnapshot 對應
每個 `volumeBackup` 條目都對應一個底層的 Kubernetes `VolumeSnapshot` 資源。可以用以下指令查看：

```bash
kubectl get volumesnapshot -n production
```
:::

---

## VirtualMachineRestore 完整說明

### 用途

`VirtualMachineRestore` 用於將 VM 從快照還原到特定時間點的狀態。

:::warning 還原前注意事項
- 還原操作**不可逆**，還原後 VM 的當前狀態將被快照狀態取代
- 還原時 VM 必須處於**停止（Stopped）**狀態，否則操作會被拒絕
- 若要保留當前狀態，應先建立新快照再執行還原
:::

### Spec 欄位

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineRestore
metadata:
  name: ubuntu-restore-20240115
  namespace: production
spec:
  # target：要還原的 VM 目標
  target:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-web-server  # 還原到原始 VM（原地還原）

  # virtualMachineSnapshotName：使用哪個快照還原
  virtualMachineSnapshotName: ubuntu-snapshot-20240115

  # patches：JSON Patch，可在還原後修改 VM 設定
  patches:
    - '{"op": "replace", "path": "/spec/template/spec/hostname", "value": "restored-ubuntu"}'
    - '{"op": "remove", "path": "/metadata/annotations/last-modified"}'

  # includeVolumes：只還原指定的 Volume（留空則還原所有）
  includeVolumes:
    - rootdisk

  # excludeVolumes：排除不需要還原的 Volume
  excludeVolumes:
    - datadisk  # 資料磁碟保留現有內容，只還原系統磁碟
```

### Status 欄位

```yaml
status:
  # 還原是否完成
  complete: true

  # 還原完成時間
  restoreTime: "2024-01-15T11:00:00Z"

  # 條件清單
  conditions:
    - type: Ready
      status: "True"
      reason: "RestoreComplete"
      message: "All volumes were successfully restored"

  # 每個 Volume 的還原狀態
  restores:
    - volumeName: rootdisk
      persistentVolumeClaim: ubuntu-web-server-rootdisk
      volumeRestoreName: restore-rootdisk-abc123
      initialPopulationComplete: true
```

---

## VirtualMachineClone 完整說明

### 用途

`VirtualMachineClone` 用於從現有 VM 或快照克隆出一個新的 VM，常見場景：

- **環境複製**：從 golden image VM 快速批量建立多個測試環境
- **藍綠部署**：複製生產環境 VM 作為新版本測試環境
- **開發隔離**：為每個開發人員建立獨立的 VM 副本

### Spec 欄位

```yaml
apiVersion: clone.kubevirt.io/v1beta1
kind: VirtualMachineClone
metadata:
  name: clone-ubuntu-for-dev
  namespace: production
spec:
  # source：克隆來源，可以是 VM 或 VirtualMachineSnapshot
  source:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-web-server

  # target：克隆出的新 VM 名稱
  target:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-dev-clone

  # annotationFilters：控制哪些 annotation 要複製到新 VM
  # 支援 glob 模式，以 "!" 開頭表示排除
  annotationFilters:
    - "*"                           # 複製所有 annotation
    - "!kubevirt.io/*"              # 排除 KubeVirt 內部 annotation
    - "!kubectl.kubernetes.io/*"    # 排除 kubectl annotation

  # labelFilters：控制哪些 label 要複製到新 VM
  labelFilters:
    - "*"                          # 複製所有 label
    - "!environment"               # 排除 environment label

  # newMacAddresses：為新 VM 的網路介面指定新的 MAC address
  newMacAddresses:
    default: "02:00:00:00:00:01"

  # newSMBiosSerial：指定新 VM 的 SMBios serial number
  newSMBiosSerial: "DEV-CLONE-001"
```

### Status Phase 完整說明

![VirtualMachineClone Phase 狀態機](/diagrams/kubevirt/kubevirt-snapshot-clone-1.png)

| Phase | 說明 |
|-------|------|
| `Pending` | Clone 請求已接收，等待開始執行 |
| `SnapshotInProgress` | 正在為來源 VM 建立臨時快照（當 source 是 VM 時） |
| `CreatingTargetVM` | 正在建立目標 VM 的 Kubernetes 資源 |
| `RestoreInProgress` | 正在從快照還原磁碟資料到新 VM |
| `Succeeded` | 克隆成功完成，新 VM 已就緒 |
| `Failed` | 克隆失敗，查看 `status.conditions` 了解原因 |

```yaml
status:
  phase: Succeeded
  snapshotName: tmp-snapshot-for-clone-abc123
  restoreName: clone-restore-xyz789
  conditions:
    - type: Ready
      status: "True"
      reason: "CloneSucceeded"
      message: "VM clone completed successfully"
    - type: SnapshotReady
      status: "True"
```

---

## VirtualMachineExport 完整說明

### 用途

`VirtualMachineExport` 提供一個臨時的 HTTP 服務，讓外部工具可以下載 VM 磁碟資料，常用於：

- **跨平台遷移**：將 KubeVirt VM 遷移到 VMware、Hyper-V 或其他雲端平台
- **外部備份工具**：整合 Velero 等備份工具對 VM 磁碟進行備份
- **磁碟分析**：將 VM 磁碟匯出給安全分析或取證工具使用
- **映像製作**：基於現有 VM 製作可重複使用的映像

### Spec 欄位

```yaml
apiVersion: export.kubevirt.io/v1beta1
kind: VirtualMachineExport
metadata:
  name: ubuntu-export
  namespace: production
spec:
  # source：匯出來源，支援三種類型
  source:
    # 類型 1：直接從 VM 匯出（需要 VM 停止）
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-web-server

    # 類型 2：從 VirtualMachineSnapshot 匯出（推薦）
    # apiGroup: "snapshot.kubevirt.io"
    # kind: VirtualMachineSnapshot
    # name: ubuntu-snapshot-20240115

    # 類型 3：直接從 PVC 匯出
    # apiGroup: ""
    # kind: PersistentVolumeClaim
    # name: ubuntu-rootdisk-pvc

  # tokenSecretRef：包含存取 token 的 Secret 名稱
  tokenSecretRef: ubuntu-export-token

  # ttlDuration：Export 服務的有效期限
  ttlDuration: "2h"
```

### 建立存取 Token

```bash
kubectl create secret generic ubuntu-export-token \
  --from-literal=token="$(openssl rand -base64 32)" \
  -n production
```

### Status 欄位與下載連結

```yaml
status:
  phase: Ready

  tokenSecretRef: ubuntu-export-token

  links:
    internal:
      cert: "<base64 CA certificate>"
      volumes:
        - name: rootdisk
          formats:
            - format: raw
              url: "https://virt-export-ubuntu-export.production.svc/volumes/rootdisk/disk.img"
            - format: gzip
              url: "https://virt-export-ubuntu-export.production.svc/volumes/rootdisk/disk.img.gz"
            - format: archive
              url: "https://virt-export-ubuntu-export.production.svc/volumes/rootdisk/disk.tar.gz"

    external:
      cert: "<base64 CA certificate>"
      volumes:
        - name: rootdisk
          formats:
            - format: raw
              url: "https://vm-export.example.com/volumes/rootdisk/disk.img"
            - format: vmdk
              url: "https://vm-export.example.com/volumes/rootdisk/disk.vmdk"
```

### 支援的匯出格式

| 格式 | 說明 | 適用場景 |
|------|------|---------|
| `raw` | 原始磁碟映像（.img） | 通用，可直接掛載 |
| `gzip` | gzip 壓縮的 raw 格式（.img.gz） | 節省傳輸頻寬 |
| `vmdk` | VMware 磁碟格式（.vmdk） | 遷移到 VMware vSphere |
| `archive` | tar 封存（包含所有磁碟） | 多磁碟 VM 的完整備份 |

---

## CSI Volume Snapshot 依賴關係

KubeVirt 的 Snapshot 功能依賴 Kubernetes 的 **CSI Volume Snapshot** 機制。

### 必要元件

```
Storage Provider（如 Ceph, AWS EBS）
    ↓
CSI Driver（實作 VolumeSnapshot API）
    ↓
VolumeSnapshotClass（設定快照參數）
    ↓
KubeVirt（使用 VolumeSnapshotClass 建立 VolumeSnapshot）
```

### VolumeSnapshotClass 設定範例

```yaml
# Ceph RBD CSI 的 VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: ceph-rbd-snapshotclass
  annotations:
    snapshot.storage.kubernetes.io/is-default-class: "true"
driver: rbd.csi.ceph.com
deletionPolicy: Delete
parameters:
  clusterID: "your-ceph-cluster-id"
  csi.storage.k8s.io/snapshotter-secret-name: ceph-csi-secret
  csi.storage.k8s.io/snapshotter-secret-namespace: ceph-system
---
# AWS EBS CSI 的 VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: ebs-vsc
  annotations:
    snapshot.storage.kubernetes.io/is-default-class: "true"
driver: ebs.csi.aws.com
deletionPolicy: Delete
parameters:
  tagSpecification_1: "Name={{.VolumeSnapshotNamespace}}/{{.VolumeSnapshotName}}"
```

### KubeVirt 選擇 VolumeSnapshotClass 的邏輯

1. **優先使用標記為預設的 VolumeSnapshotClass**（`is-default-class: "true"`）
2. 若無預設，使用與 PVC 相同 CSI Driver 的 VolumeSnapshotClass
3. 若有多個符合條件的，依照字母順序選擇第一個

:::warning 快照功能無法使用的常見原因
```bash
# 檢查是否有可用的 VolumeSnapshotClass
kubectl get volumesnapshotclass

# 檢查 CSI driver 是否支援 snapshot
kubectl get csidriver -o custom-columns='NAME:.metadata.name,SNAPSHOT:.spec.volumeLifecycleModes'

# 若沒有任何 VolumeSnapshotClass，快照功能將無法使用
kubectl describe vmsnapshot <name> -n <namespace>
```
:::

---

## 完整操作流程

![Snapshot / Restore / Clone 操作流程](/diagrams/kubevirt/kubevirt-snapshot-clone-2.png)

---

## 完整 YAML 範例

### VirtualMachineSnapshot 範例

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: prod-ubuntu-snapshot-daily
  namespace: production
  annotations:
    snapshot.kubevirt.io/description: "Daily backup - 2024-01-15 10:00"
spec:
  source:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-web-server
  deletionPolicy: Retain
  failureDeadline: "10m"
```

### VirtualMachineRestore 範例（原地還原）

```yaml
# 步驟 1：先停止 VM
# kubectl patch vm ubuntu-web-server -n production \
#   --type merge -p '{"spec":{"runStrategy":"Halted"}}'

# 步驟 2：建立 Restore 物件
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineRestore
metadata:
  name: ubuntu-restore-to-daily
  namespace: production
spec:
  target:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-web-server
  virtualMachineSnapshotName: prod-ubuntu-snapshot-daily
  # 只還原系統磁碟，保留資料磁碟的當前狀態
  excludeVolumes:
    - datadisk
  patches:
    - '{"op":"replace","path":"/spec/template/spec/hostname","value":"ubuntu-restored"}'
```

### VirtualMachineClone 範例（克隆為新 VM）

```yaml
# 從快照克隆新環境（推薦方式，不影響原 VM）
apiVersion: clone.kubevirt.io/v1beta1
kind: VirtualMachineClone
metadata:
  name: clone-ubuntu-to-staging
  namespace: production
spec:
  source:
    apiGroup: "snapshot.kubevirt.io"
    kind: VirtualMachineSnapshot
    name: prod-ubuntu-snapshot-daily
  target:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-staging
  annotationFilters:
    - "*"
    - "!kubevirt.io/*"
    - "!cdi.kubevirt.io/*"
  labelFilters:
    - "*"
    - "!environment"
    - "!tier"
  newMacAddresses:
    default: "02:11:22:33:44:55"
  newSMBiosSerial: "STAGING-001"
---
# 從正在運行的 VM 直接克隆
apiVersion: clone.kubevirt.io/v1beta1
kind: VirtualMachineClone
metadata:
  name: clone-ubuntu-for-dev-alice
  namespace: production
spec:
  source:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-web-server
  target:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ubuntu-dev-alice
  newMacAddresses:
    default: "02:aa:bb:cc:dd:01"
  newSMBiosSerial: "DEV-ALICE-001"
```

### VirtualMachineExport 範例

```yaml
# 步驟 1：建立 token secret
# kubectl create secret generic ubuntu-export-token \
#   --from-literal=token="$(openssl rand -hex 32)" -n production

# 步驟 2：建立 Export 物件
apiVersion: export.kubevirt.io/v1beta1
kind: VirtualMachineExport
metadata:
  name: ubuntu-export-for-migration
  namespace: production
spec:
  source:
    apiGroup: "snapshot.kubevirt.io"
    kind: VirtualMachineSnapshot
    name: prod-ubuntu-snapshot-daily
  tokenSecretRef: ubuntu-export-token
  ttlDuration: "4h"
```

---

## 常用操作指令

### virtctl vmexport 相關指令

```bash
# 建立 Export 並等待就緒
virtctl vmexport create ubuntu-export \
  --vm=ubuntu-web-server \
  --namespace=production

# 下載匯出的磁碟（raw 格式）
virtctl vmexport download ubuntu-export \
  --output=ubuntu-disk.img \
  --volume=rootdisk \
  --namespace=production

# 下載匯出的磁碟（vmdk 格式，用於 VMware）
virtctl vmexport download ubuntu-export \
  --output=ubuntu-disk.vmdk \
  --volume=rootdisk \
  --format=vmdk \
  --namespace=production

# 刪除 Export
virtctl vmexport delete ubuntu-export --namespace=production
```

### kubectl 查詢快照狀態指令

```bash
# 查看所有快照
kubectl get vmsnapshot -n production

# 查看快照詳細狀態（包含 indications 和 error）
kubectl describe vmsnapshot prod-ubuntu-snapshot-daily -n production

# 監看快照建立進度
kubectl get vmsnapshot prod-ubuntu-snapshot-daily -n production \
  -o jsonpath='{.status.phase}' --watch

# 查看快照包含的 volume
kubectl get vmsnapshot prod-ubuntu-snapshot-daily -n production \
  -o jsonpath='{.status.snapshotVolumes}'

# 查看底層 VolumeSnapshot
kubectl get volumesnapshot -n production

# 查看 VirtualMachineSnapshotContent
kubectl get vmsnapshotcontent -n production

# 查看還原狀態
kubectl get vmrestore -n production
kubectl describe vmrestore ubuntu-restore-to-daily -n production

# 查看 Clone 狀態
kubectl get vmclone -n production
kubectl get vmclone clone-ubuntu-to-staging -n production \
  -o jsonpath='{.status.phase}'

# 查看 Export 狀態與下載連結
kubectl get vmexport -n production
kubectl get vmexport ubuntu-export-for-migration -n production \
  -o jsonpath='{.status.links}'

# 等待快照就緒（腳本使用）
kubectl wait vmsnapshot prod-ubuntu-snapshot-daily \
  --for=jsonpath='{.status.readyToUse}'=true \
  --timeout=300s \
  -n production

# 等待 Clone 完成
kubectl wait vmclone clone-ubuntu-to-staging \
  --for=jsonpath='{.status.phase}'=Succeeded \
  --timeout=600s \
  -n production
```

:::tip 自動化快照腳本
```bash
#!/bin/bash
VM_NAME="ubuntu-web-server"
NAMESPACE="production"
DATE=$(date +%Y%m%d-%H%M%S)
SNAPSHOT_NAME="${VM_NAME}-snapshot-${DATE}"

kubectl apply -f - <<EOF
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: ${SNAPSHOT_NAME}
  namespace: ${NAMESPACE}
spec:
  source:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: ${VM_NAME}
  deletionPolicy: Retain
  failureDeadline: "10m"
EOF

kubectl wait vmsnapshot ${SNAPSHOT_NAME} \
  --for=jsonpath='{.status.readyToUse}'=true \
  --timeout=600s \
  -n ${NAMESPACE}

echo "Snapshot ${SNAPSHOT_NAME} created successfully"

# 保留最近 7 個，刪除舊快照
kubectl get vmsnapshot -n ${NAMESPACE} \
  --sort-by=.metadata.creationTimestamp \
  -o name | head -n -7 | xargs -r kubectl delete -n ${NAMESPACE}
```
:::
