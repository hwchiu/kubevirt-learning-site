# Snapshot、Clone 與 Export — 資料保護與搬移

## 概述

KubeVirt 提供完整的 VM 資料保護與搬移生態系：

| 資源 | 功能 | API Group |
|------|------|-----------|
| VirtualMachineSnapshot | 為執行中或停止的 VM 建立快照 | snapshot.kubevirt.io |
| VirtualMachineSnapshotContent | 快照的實際儲存物件 | snapshot.kubevirt.io |
| VirtualMachineRestore | 從快照還原 VM | snapshot.kubevirt.io |
| VirtualMachineClone | 從 VM 或快照克隆新 VM | clone.kubevirt.io |
| VirtualMachineExport | 匯出 VM 磁碟供外部存取 | export.kubevirt.io |
| VirtualMachineBackup | 完整備份（含增量） | backup.kubevirt.io |

---

## VirtualMachineSnapshot

### Spec 欄位

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: my-vm-snapshot
  namespace: default
spec:
  # 快照來源（目前只支援 VM）
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm

  # 刪除快照時的策略（預設 Delete）
  # Delete: 刪除快照時同時刪除 VolumeSnapshot
  # Retain: 保留 VolumeSnapshot
  deletionPolicy: Delete

  # 快照操作的超時時間（秒）
  failureDeadline: "5m0s"
```

### Status 欄位

```yaml
status:
  # 快照是否可用於還原
  readyToUse: true

  # 建立時間
  creationTime: "2024-01-15T10:00:00Z"

  # 發生錯誤時的訊息
  error: null

  # 快照狀態
  phase: Succeeded  # Pending, InProgress, Succeeded, Failed

  # 快照指示（說明快照時的 VM 狀態）
  indications:
  - Online        # VM 在線上時拍攝（記憶體不一致）
  - GuestAgent    # 有 guest agent，可進行 Quiescing
  - NoGuestAgent  # 沒有 guest agent（與 GuestAgent 互斥）

  # 對應的 VirtualMachineSnapshotContent 名稱
  virtualMachineSnapshotContentName: vmsnapshot-content-xxx

  # 包含的 Volume 快照列表
  snapshotVolumes:
    includedVolumes:
    - rootdisk
    excludedVolumes:
    - ephemeral-disk  # 暫態磁碟不納入快照
```

### Snapshot Indications 說明

| Indication | 意義 |
|------------|------|
| `Online` | VM 處於執行中狀態時拍攝，記憶體狀態未凍結 |
| `GuestAgent` | Guest agent 在線，可進行檔案系統凍結 |
| `NoGuestAgent` | Guest agent 不在線，無法凍結檔案系統 |
| `Paused` | VM 被暫停後拍攝（應用程式一致性快照） |
| `QuiesceTimeout` | 凍結操作超時，降級為 crash-consistent 快照 |

---

## VirtualMachineSnapshotContent

這是實際儲存快照資料的物件，由系統自動建立，**不需要手動管理**：

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshotContent
metadata:
  name: vmsnapshot-content-abc123
spec:
  # 對應的 VirtualMachineSnapshot
  virtualMachineSnapshotName: my-vm-snapshot

  # VM 在快照時的完整規格副本
  source:
    virtualMachine:
      # ... 完整的 VM spec

  # CSI VolumeSnapshot 參考列表
  volumeBackups:
  - volumeName: rootdisk
    persistentVolumeClaim:
      name: my-vm-rootdisk-pvc
    volumeSnapshotName: vmsnapshot-vol-rootdisk-abc
```

---

## VirtualMachineRestore

### Spec 欄位

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineRestore
metadata:
  name: restore-my-vm
spec:
  # 還原目標（必須與快照的來源相同）
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm

  # 使用哪個快照來還原
  virtualMachineSnapshotName: my-vm-snapshot

  # 是否包含設定（false = 只還原磁碟不還原 VM spec）
  # 省略或 true = 連同 VM spec 一起還原
```

### Status 欄位

```yaml
status:
  # 是否完成
  complete: true

  # 還原完成時間
  restoreTime: "2024-01-15T10:30:00Z"

  # 各 Volume 還原情況
  restores:
  - volumeName: rootdisk
    persistentVolumeClaimName: restore-rootdisk-abc
    volumeSnapshotName: vmsnapshot-vol-rootdisk-abc

  # 發生錯誤時的訊息
  conditions:
  - type: Ready
    status: "True"
```

---

## VirtualMachineClone

Clone 操作從現有 VM 或快照建立一個全新的 VM，並自動處理 MAC Address、SMBios Serial 等唯一識別符。

### Spec 欄位

```yaml
apiVersion: clone.kubevirt.io/v1alpha1
kind: VirtualMachineClone
metadata:
  name: clone-my-vm
spec:
  # 來源
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm
  # 或從快照克隆
  # source:
  #   apiGroup: snapshot.kubevirt.io
  #   kind: VirtualMachineSnapshot
  #   name: my-vm-snapshot

  # 目標 VM 名稱
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm-clone

  # Annotation 過濾（哪些 annotation 要保留/移除）
  annotationFilters:
  - "!kubevirt.io/*"    # 移除所有 kubevirt.io annotation（!前綴 = 排除）
  - "*"                  # 保留其他所有 annotation

  # Label 過濾（同上）
  labelFilters:
  - "!kubevirt.io/*"
  - "*"

  # 為 clone 的 VM 指定新的 MAC Address
  newMacAddresses:
    eth0: "DE:AD:BE:EF:00:02"

  # 為 clone 的 VM 指定新的 SMBios Serial
  newSMBiosSerial: "new-serial-12345"

  # 模板 annotation 過濾（VMI template 中的 annotation）
  templateAnnotationFilters:
  - "!kubectl.kubernetes.io/*"

  # 模板 label 過濾
  templateLabelFilters:
  - "*"
```

### Clone Phase 狀態機

```
                    ┌─────────┐
                    │ Pending │  等待快照操作開始
                    └────┬────┘
                         │
              ┌──────────▼──────────┐
              │ SnapshotInProgress  │  建立中間快照
              └──────────┬──────────┘
                         │
           ┌─────────────▼─────────────┐
           │ CreatingTargetVM          │  從快照建立目標 VM
           └─────────────┬─────────────┘
                         │
           ┌─────────────▼─────────────┐
           │ RestoreInProgress         │  還原磁碟資料
           └─────────────┬─────────────┘
                         │
                    ┌────▼────┐
                    │Succeeded│  或 Failed
                    └─────────┘
```

---

## VirtualMachineExport

用於匯出 VM 磁碟，讓外部工具（如 CDI）可以下載或存取 VM 的磁碟內容。

```yaml
apiVersion: export.kubevirt.io/v1alpha1
kind: VirtualMachineExport
metadata:
  name: my-vm-export
spec:
  # 來源（VM, VMSnapshot, 或 PVC）
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm

  # Token Secret（用於認證下載）
  tokenSecretRef: export-token-secret

  # 匯出連結的有效時間（預設 2 小時）
  ttlDuration: "2h"
```

```yaml
# 建立 Token Secret
apiVersion: v1
kind: Secret
metadata:
  name: export-token-secret
type: Opaque
stringData:
  token: "my-secure-token-12345"
```

### Export Status

```yaml
status:
  phase: Ready  # Pending, InProgress, Ready, Failed, Terminated

  # 下載連結
  links:
    external:
      cert: "..."  # TLS 憑證
      volumes:
      - name: rootdisk
        formats:
        - format: raw
          url: "https://..."
        - format: gzip
          url: "https://...gz"
        - format: dir
          url: "https://.../dir"  # 目錄格式
        - format: tar.gz
          url: "https://...tar.gz"
    internal:
      cert: "..."
      volumes:
      - name: rootdisk
        formats:
        - format: raw
          url: "https://virt-exportserver.default.svc.cluster.local/..."
```

---

## VirtualMachineBackup（增量備份）

```yaml
apiVersion: backup.kubevirt.io/v1alpha1
kind: VirtualMachineBackup
metadata:
  name: my-vm-backup
spec:
  # 來源 VM
  virtualMachineName: my-vm

  # 備份類型：Full 或 Incremental
  type: Incremental

  # 增量備份的參考基準（上次備份的名稱）
  incrementalBackupContentName: last-backup-content

  # 刪除策略
  deletionPolicy: Retain
```

增量備份使用 CBT（Changed Block Tracking）技術，只備份自上次備份以來變更的磁碟區塊。

---

## 完整操作流程

### 建立並使用 Snapshot

```bash
# 1. 建立快照
kubectl apply -f - <<EOF
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: pre-upgrade-snapshot
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: production-vm
  failureDeadline: "5m0s"
EOF

# 2. 等待快照就緒
kubectl wait vmsnapshot pre-upgrade-snapshot \
  --for=jsonpath='{.status.readyToUse}'=true \
  --timeout=300s

# 3. 確認快照狀態
kubectl get vmsnapshot pre-upgrade-snapshot -o yaml

# 4. （在升級失敗後）建立還原
kubectl apply -f - <<EOF
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineRestore
metadata:
  name: restore-from-pre-upgrade
spec:
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: production-vm
  virtualMachineSnapshotName: pre-upgrade-snapshot
EOF

# 5. 等待還原完成
kubectl wait vmrestore restore-from-pre-upgrade \
  --for=condition=Ready \
  --timeout=600s

# 6. 查看還原結果
kubectl get vmrestore restore-from-pre-upgrade -o yaml
```

### 克隆 VM

```bash
# 克隆 VM
kubectl apply -f - <<EOF
apiVersion: clone.kubevirt.io/v1alpha1
kind: VirtualMachineClone
metadata:
  name: dev-clone
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: template-vm
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: dev-vm-01
  newMacAddresses:
    eth0: ""  # 自動分配新 MAC
  labelFilters:
  - "!kubevirt.io/*"
  - "*"
EOF

# 等待克隆完成
kubectl wait vmclone dev-clone \
  --for=jsonpath='{.status.phase}'=Succeeded \
  --timeout=600s
```

### 使用 virtctl 管理

```bash
# 快照操作
virtctl vmexport create my-export --vm=my-vm
virtctl vmexport download my-export --output=/tmp/disk.img --volume=rootdisk

# 查看 VM 匯出連結
virtctl vmexport get my-export

# 刪除匯出
virtctl vmexport delete my-export
```

---

## CSI Volume Snapshot 依賴

KubeVirt Snapshot 功能依賴 CSI 驅動的 VolumeSnapshot 支援：

```bash
# 確認 CSI 驅動支援 VolumeSnapshot
kubectl get volumesnapshotclasses

# 確認 VolumeSnapshot CRD 已安裝
kubectl api-resources | grep volumesnapshot

# 查看自動建立的 CSI VolumeSnapshot
kubectl get volumesnapshot
```

::: warning 儲存後端要求
- 必須使用支援 VolumeSnapshot 的 CSI 驅動（如 Rook Ceph, Dell CSI, NetApp Trident）
- HostPath / Local Path 等本地儲存**不支援** VolumeSnapshot
- DataVolume 使用的 PVC 也需要相同的 CSI 驅動支援
:::

---

## 常用操作指令

```bash
# Snapshot
kubectl get vmsnapshot                         # 列出所有快照
kubectl get vmsnapshot my-snap -o yaml         # 查看快照詳情
kubectl delete vmsnapshot old-snapshot         # 刪除快照

# Restore
kubectl get vmrestore                          # 列出所有還原操作
kubectl describe vmrestore my-restore         # 查看還原詳情

# Clone
kubectl get vmclone                            # 列出所有克隆操作
kubectl describe vmclone my-clone             # 查看克隆詳情

# Export
kubectl get vmexport                           # 列出所有匯出操作
virtctl vmexport create exp1 --vm=my-vm       # 建立匯出
virtctl vmexport download exp1 \              # 下載磁碟
  --output=/tmp/disk.raw \
  --volume=rootdisk

# 一鍵備份腳本
for VM in $(kubectl get vm -o name); do
  VM_NAME=$(echo $VM | cut -d/ -f2)
  kubectl apply -f - <<EOF
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: daily-${VM_NAME}-$(date +%Y%m%d)
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: ${VM_NAME}
EOF
done
```
