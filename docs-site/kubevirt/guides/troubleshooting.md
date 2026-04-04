# 疑難排解指南 — 常見問題診斷與解決

::: danger 重要提醒
在進行任何疑難排解之前，請先確認 KubeVirt 元件的版本一致性。版本不匹配是許多奇怪問題的根源。使用 `kubectl get kubevirt -n kubevirt -o yaml` 確認版本狀態。
:::

## VM 無法啟動

### ImagePullBackOff（ContainerDisk 問題）

**症狀：** VM 停在 `Scheduling` 或 `Pending` 狀態，virt-launcher Pod 顯示 `ImagePullBackOff`。

**診斷步驟：**

```bash
# 1. 檢查 VMI 狀態
kubectl get vmi my-vm -o yaml | grep -A 20 conditions

# 2. 檢查 virt-launcher Pod 事件
kubectl describe pod virt-launcher-my-vm-xxxxx

# 3. 檢查映像是否可以拉取
kubectl run test-pull --image=quay.io/containerdisks/ubuntu:22.04 \
  --restart=Never --command -- sleep 10
```

**常見原因與解決方案：**

| 原因 | 解決方案 |
|---|---|
| 映像名稱拼寫錯誤 | 確認 `containerDisk.image` 欄位 |
| 私有 Registry 未設定認證 | 建立 `imagePullSecret` 並在 ServiceAccount 中引用 |
| Registry 不可達 | 確認網路連線和 DNS 解析 |
| 映像不存在或 tag 錯誤 | 使用 `skopeo inspect` 或 `crane` 確認映像 |
| 節點無法存取外部網路 | 設定 HTTP Proxy 或使用內部 Mirror Registry |

```yaml
# 修正：添加 imagePullSecret
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-vm
spec:
  template:
    spec:
      volumes:
        - name: rootdisk
          containerDisk:
            image: registry.internal.com/vm-images/ubuntu:22.04
            imagePullSecret: my-registry-secret  # ← 添加認證
```

### Insufficient Resources（資源不足）

**症狀：** VM 停在 `Scheduling` 狀態，virt-launcher Pod 處於 `Pending`。

**診斷步驟：**

```bash
# 1. 檢查 Pod 事件
kubectl describe pod virt-launcher-my-vm-xxxxx | grep -A 10 Events

# 2. 檢查節點可用資源
kubectl describe nodes | grep -A 5 "Allocated resources"

# 3. 檢查是否有 ResourceQuota 限制
kubectl get resourcequota -n <namespace>
kubectl describe resourcequota -n <namespace>

# 4. 若使用 CPU Pinning，檢查可分配 CPU
kubectl get node <node> -o json | \
  jq '.status.allocatable["cpu"]'
```

**解決方案：**

```bash
# 減少 VM 資源需求
# 或者增加叢集節點
# 或者調整 ResourceQuota
kubectl edit resourcequota -n <namespace>

# 若使用 HugePages，確認節點有足夠的 HugePages
kubectl get node <node> -o json | \
  jq '.status.allocatable["hugepages-1Gi"]'
```

### PVC Not Bound（儲存未綁定）

**症狀：** VM 停在 `Scheduling` 狀態，DataVolume 顯示 `WaitForFirstConsumer` 或 PVC 處於 `Pending`。

**診斷步驟：**

```bash
# 1. 檢查 DataVolume 狀態
kubectl get dv -n <namespace>
kubectl describe dv my-vm-rootdisk

# 2. 檢查 PVC 狀態
kubectl get pvc -n <namespace>
kubectl describe pvc my-vm-rootdisk

# 3. 檢查 StorageClass
kubectl get sc
kubectl describe sc <storage-class-name>

# 4. 檢查 CDI 匯入進度（若使用 DataVolume）
kubectl get dv my-vm-rootdisk -o jsonpath='{.status.progress}'
```

**常見原因與解決方案：**

| 原因 | 解決方案 |
|---|---|
| StorageClass 不存在 | 確認 `storageClassName` 欄位拼寫正確 |
| 儲存後端空間不足 | 擴充儲存池或清理不用的 PV |
| WaitForFirstConsumer | 正常行為，PVC 會在 Pod 調度時自動綁定 |
| CSI Driver 未安裝 | 安裝對應的 CSI Driver |
| DataVolume 匯入失敗 | 檢查來源 URL 是否可達 |

### Feature Gate Not Enabled（功能門未啟用）

**症狀：** `kubectl apply` 被拒絕，錯誤訊息包含 `feature gate` 相關字樣。

**診斷步驟：**

```bash
# 檢查目前啟用的 Feature Gates
kubectl get kubevirt -n kubevirt -o jsonpath='{.items[0].spec.configuration.developerConfiguration.featureGates}'
```

**解決方案：**

```yaml
# 啟用所需的 Feature Gate
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  configuration:
    developerConfiguration:
      featureGates:
        - LiveMigration
        - HotplugVolumes
        - HotplugNICs
        - VMLiveUpdateFeatures
        - Snapshot
        - VMExport
```

```bash
kubectl edit kubevirt kubevirt -n kubevirt
```

### Admission Webhook Rejection（准入控制拒絕）

**症狀：** `kubectl apply` 被 webhook 拒絕，顯示 validation error。

**診斷步驟：**

```bash
# 1. 仔細閱讀錯誤訊息
kubectl apply -f vm.yaml 2>&1

# 2. 檢查 virt-api Pod 日誌
kubectl logs -n kubevirt -l kubevirt.io=virt-api --tail=50

# 3. 使用 --dry-run=server 測試
kubectl apply -f vm.yaml --dry-run=server
```

**常見拒絕原因：**

```bash
# 無效的 disk bus + volume 組合
# 例如：containerDisk 不能使用 scsi bus
# 修正：使用 virtio 或 sata

# 無效的網路配置
# 例如：masquerade 模式不支援設定 MAC 地址
# 修正：改用 bridge 模式

# CPU 拓撲無效
# 例如：dedicatedCPUPlacement 要求 CPU 為整數
# 修正：確保 cores * sockets * threads 為正整數
```

## VM 啟動但無法連線

### 網路未初始化

**症狀：** VM 已啟動（`Running`），但無法透過 SSH 或任何方式連線。

**診斷步驟：**

```bash
# 1. 透過 console 直接存取
virtctl console my-vm

# 2. 檢查 VM 內部網路
# 在 console 中執行：
ip addr show
ip route show

# 3. 檢查 VMI 的網路資訊
kubectl get vmi my-vm -o jsonpath='{.status.interfaces}' | jq .

# 4. 檢查 cloud-init 是否正確執行
# 在 VM console 中：
cat /var/log/cloud-init.log
cat /var/log/cloud-init-output.log
```

**常見原因與解決方案：**

| 原因 | 解決方案 |
|---|---|
| cloud-init 配置錯誤 | 驗證 YAML 格式，確認 `userData` 內容正確 |
| DHCP 未回應 | 確認 CNI 插件正常運行 |
| VirtIO 驅動缺失 | Windows VM 需要安裝 VirtIO 網路驅動 |
| DNS 設定問題 | 檢查 Pod DNS Policy 和 CoreDNS 狀態 |

### Guest Agent 未安裝

**症狀：** `kubectl get vmi` 看不到 IP 地址或 Guest OS 資訊。

```bash
# 檢查 Guest Agent 狀態
kubectl get vmi my-vm -o jsonpath='{.status.conditions}' | jq .

# 安裝 Guest Agent
virtctl console my-vm

# Ubuntu/Debian
sudo apt update && sudo apt install -y qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# CentOS/RHEL/Fedora
sudo dnf install -y qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# Windows（在 VirtIO 驅動光碟中）
# 執行 D:\guest-agent\qemu-ga-x86_64.msi
```

### 防火牆規則問題

**症狀：** VM 有 IP 但某些埠口無法存取。

```bash
# 1. 檢查 Kubernetes Service
kubectl get svc -l app=my-vm

# 2. 檢查 NetworkPolicy
kubectl get networkpolicy -n <namespace>

# 3. 在 VM 內部確認服務監聽
virtctl console my-vm
# ss -tlnp
# iptables -L -n

# 4. 從另一個 Pod 測試連線
kubectl run debug --image=busybox --rm -it -- \
  wget -qO- http://<vm-ip>:80 --timeout=5
```

::: tip 建立 Service 暴露 VM
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-vm-ssh
spec:
  selector:
    kubevirt.io/domain: my-vm
  ports:
    - port: 22
      targetPort: 22
  type: ClusterIP
```

或使用 virtctl 快速暴露：
```bash
virtctl expose vmi my-vm --port=22 --name=my-vm-ssh --type=NodePort
```
:::

## Live Migration 失敗

### Target Pod Scheduling Failure（目標 Pod 調度失敗）

**症狀：** 遷移停在 `Scheduling` 階段，最終超時失敗。

```bash
# 1. 檢查遷移狀態
kubectl get vmim -o yaml

# 2. 檢查目標 Pod 事件
kubectl get pods -l kubevirt.io/migrationJobFor=my-vm
kubectl describe pod <target-launcher-pod>

# 3. 檢查所有節點的可用資源
kubectl top nodes
kubectl describe nodes | grep -A 10 "Allocated resources"
```

**解決方案：**

```bash
# 確保至少有一個其他節點有足夠資源
# 確認 node affinity / anti-affinity 不會阻止調度
# 確認 taints 和 tolerations 允許目標節點
```

### Non-Migratable VM（不可遷移的 VM）

**症狀：** 遷移被拒絕，提示 VM 不可遷移。

**常見原因：**

```bash
# 檢查 VMI 的 migration method
kubectl get vmi my-vm -o jsonpath='{.status.migrationMethod}'

# 檢查 VMI 的 conditions 中是否有 LiveMigratable
kubectl get vmi my-vm -o jsonpath='{.status.conditions}' | jq '.[] | select(.type=="LiveMigratable")'
```

| 不可遷移的原因 | 解決方案 |
|---|---|
| 使用 SR-IOV 介面 | 遷移前移除 SR-IOV，遷移後重新附加 |
| 使用 HostDisk | 改用共享儲存的 PVC |
| 使用 GPU Passthrough | 目前無法遷移，需要停機 |
| PVC 為 RWO | 改用 RWX AccessMode |
| 使用 virtiofs | 目前不支援遷移 |

::: warning RWX 儲存是 Live Migration 的必要條件
Live Migration 需要源端和目標端同時存取相同的儲存。因此，PVC 必須使用 `ReadWriteMany (RWX)` 存取模式。常見的 RWX 儲存方案包括 Ceph RBD（搭配 `rbd-nbd`）、CephFS、NFS。
:::

### Timeout / Progress Stall（超時 / 進度停滯）

**症狀：** 遷移已開始，但資料傳輸速度極慢或停滯。

```bash
# 1. 監控遷移進度
kubectl get vmim -w

# 2. 檢查遷移詳細狀態
kubectl get vmim <migration-name> -o yaml | grep -A 20 status

# 3. 調整遷移設定
kubectl edit kubevirt kubevirt -n kubevirt
```

```yaml
# 調整遷移參數
spec:
  configuration:
    migrations:
      bandwidthPerMigration: "64Mi"         # 每次遷移頻寬限制
      completionTimeoutPerGiB: 800          # 每 GiB 的完成超時（秒）
      parallelMigrationsPerCluster: 5       # 叢集同時遷移數量上限
      parallelOutboundMigrationsPerNode: 2  # 每節點同時遷出數量
      progressTimeout: 150                  # 進度超時（秒）
      allowPostCopy: true                   # 允許 post-copy 遷移
```

::: tip Post-copy 遷移
對於大記憶體且寫入密集的 VM（如資料庫），pre-copy 可能永遠無法收斂。啟用 `allowPostCopy` 後，當 pre-copy 進度停滯時，會自動切換到 post-copy 模式：先遷移 vCPU，再按需傳輸記憶體分頁。

**注意：** Post-copy 模式下，如果遷移中斷，VM 可能無法恢復。
:::

## 儲存問題

### DataVolume Import 失敗

**症狀：** DataVolume 停在 `ImportInProgress` 或進入 `Failed` 狀態。

```bash
# 1. 檢查 DataVolume 狀態
kubectl get dv my-dv -o yaml

# 2. 檢查 CDI Importer Pod
kubectl get pods -n <namespace> | grep importer
kubectl logs importer-my-dv-xxxxx

# 3. 檢查 CDI 控制器日誌
kubectl logs -n cdi -l app=cdi-deployment --tail=100

# 4. 常見錯誤診斷
# 來源 URL 不可達
curl -I https://source-url.com/image.qcow2

# TLS 憑證問題
kubectl describe dv my-dv | grep -i error
```

**解決方案：**

```yaml
# 若來源使用自簽憑證
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: my-dv
spec:
  source:
    http:
      url: "https://self-signed.example.com/image.qcow2"
      certConfigMap: "tls-certs"  # 包含 CA 憑證的 ConfigMap
  storage:
    resources:
      requests:
        storage: 30Gi
---
# 建立包含 CA 憑證的 ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: tls-certs
data:
  ca.pem: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
```

### Hotplug Volume 失敗

**症狀：** `virtctl addvolume` 執行後，磁碟未出現在 VM 中。

```bash
# 1. 檢查 VolumeStatus
kubectl get vmi my-vm -o jsonpath='{.status.volumeStatus}' | jq .

# 2. 檢查 HotplugVolumes Feature Gate
kubectl get kubevirt -n kubevirt -o jsonpath='{.items[0].spec.configuration.developerConfiguration.featureGates}'

# 3. 確認 PVC 存在且已 bound
kubectl get pvc <pvc-name>

# 4. 檢查 virt-handler 日誌
kubectl logs -n kubevirt -l kubevirt.io=virt-handler --tail=50
```

### Snapshot 失敗

**症狀：** VirtualMachineSnapshot 進入 `Failed` 狀態。

```bash
# 1. 檢查 Snapshot 狀態
kubectl get vmsnapshot my-snapshot -o yaml

# 2. 檢查 VolumeSnapshotClass 是否存在
kubectl get volumesnapshotclass

# 3. 確認 CSI Driver 支援 Snapshot
kubectl get csidrivers -o yaml | grep -A 5 "volumeSnapshotClasses"
```

::: danger 前提條件
VirtualMachineSnapshot 需要：
1. 安裝 **CSI Snapshot Controller**（`snapshot-controller`）
2. 建立對應的 **VolumeSnapshotClass**
3. CSI Driver 必須支援 VolumeSnapshot 功能
4. 如果 VM 正在運行，需要安裝 **QEMU Guest Agent** 以確保 filesystem 一致性（freeze/thaw）
:::

## 效能問題

### CPU Throttling

**症狀：** VM 內部感覺緩慢，但 CPU 使用率似乎不高。

```bash
# 1. 檢查 cgroup throttle 數據
kubectl exec -n kubevirt virt-launcher-my-vm-xxxxx -- \
  cat /sys/fs/cgroup/cpu/cpu.stat

# 2. 檢查 CPU requests vs limits
kubectl get vmi my-vm -o yaml | grep -A 10 resources

# 3. 檢查 Prometheus 指標
# CPU throttle 時間
container_cpu_cfs_throttled_seconds_total{pod=~"virt-launcher-my-vm.*"}
```

**解決方案：**

```yaml
# 使用 dedicatedCPUPlacement 避免 CFS throttling
spec:
  domain:
    cpu:
      cores: 4
      dedicatedCPUPlacement: true  # CPU 不受 CFS 限制
```

### IO Latency 高

**症狀：** VM 內磁碟操作緩慢。

```bash
# 1. 在 VM 內測試磁碟效能
fio --name=test --ioengine=libaio --direct=1 \
    --bs=4k --size=256M --rw=randread --runtime=10

# 2. 檢查 Host 端儲存狀態
kubectl exec -n kubevirt virt-launcher-my-vm-xxxxx -- \
  iostat -x 1 5

# 3. 確認最佳化配置
# - 是否使用 virtio bus？
# - 是否啟用 IO Threads？
# - Cache 模式是否為 none？
# - 是否使用 Block mode PVC？
```

### Network 效能低

**症狀：** 網路吞吐量遠低於預期。

```bash
# 1. 在 VM 內測試網路
iperf3 -c <target-ip> -t 30

# 2. 確認是否啟用多佇列
kubectl get vmi my-vm -o jsonpath='{.spec.domain.devices.networkInterfaceMultiqueue}'

# 3. 檢查 MTU 設定
# 在 VM 內：
ip link show | grep mtu

# 4. 考慮升級到 SR-IOV
# 或啟用 networkInterfaceMultiqueue
```

## 日誌收集指南

### 各元件日誌位置

```bash
# === virt-api（API 准入控制和驗證）===
kubectl logs -n kubevirt -l kubevirt.io=virt-api --tail=200

# === virt-controller（VM 生命週期管理）===
kubectl logs -n kubevirt -l kubevirt.io=virt-controller --tail=200

# === virt-handler（節點層級 VM 管理）===
# 查看特定節點的 virt-handler
kubectl logs -n kubevirt -l kubevirt.io=virt-handler \
  --field-selector spec.nodeName=worker-01 --tail=200

# === virt-launcher（VM 進程管理，包含 QEMU/libvirt）===
# 每個 VM 有一個 virt-launcher Pod
kubectl logs virt-launcher-my-vm-xxxxx -n <namespace> --tail=200

# 查看 QEMU 日誌（在 virt-launcher 中）
kubectl exec virt-launcher-my-vm-xxxxx -- \
  cat /var/log/libvirt/qemu/default_my-vm.log

# === Guest OS 日誌 ===
# 透過 serial console 查看
virtctl console my-vm

# 透過 Guest Agent（如果支援）
kubectl get vmi my-vm -o jsonpath='{.status.guestOSInfo}' | jq .
```

### 調整日誌等級

```bash
# 使用 virtctl 調整日誌等級（v1.1+）
# 增加所有元件的日誌詳細度
virtctl adm log-verbosity --set 5

# 僅增加特定元件
virtctl adm log-verbosity --set 5 --component virt-handler
virtctl adm log-verbosity --set 5 --component virt-controller

# 僅增加特定 VM 的日誌
virtctl adm log-verbosity --set 5 --vmi my-vm

# 查看目前日誌等級
virtctl adm log-verbosity

# 或透過 KubeVirt CR 設定
kubectl edit kubevirt kubevirt -n kubevirt
```

```yaml
spec:
  configuration:
    developerConfiguration:
      logVerbosity:
        virtAPI: 5
        virtController: 5
        virtHandler: 5
        virtLauncher: 5
        virtOperator: 5
        nodeVerbosity:
          worker-01: 8  # 特定節點更高的日誌等級
```

::: warning 日誌等級注意事項
高日誌等級（5 以上）會產生大量日誌輸出，可能影響效能。建議僅在疑難排解時暫時提高，完成後恢復預設等級。
:::

## 常用診斷指令

### kubectl 診斷指令集

```bash
# === VM 狀態總覽 ===
kubectl get vm -A                           # 所有 VM
kubectl get vmi -A                          # 所有運行中的 VMI
kubectl get vmim -A                         # 所有遷移任務

# === 詳細狀態檢查 ===
kubectl get vm my-vm -o yaml                # VM 完整定義
kubectl get vmi my-vm -o yaml               # VMI 運行時狀態
kubectl describe vmi my-vm                  # VMI 詳細描述（含事件）

# === Pod 層級診斷 ===
kubectl get pods -l kubevirt.io=virt-launcher  # 所有 launcher Pod
kubectl describe pod virt-launcher-my-vm-xxxxx # Pod 詳細資訊
kubectl top pod virt-launcher-my-vm-xxxxx      # Pod 資源使用

# === DataVolume 與儲存 ===
kubectl get dv -A                           # 所有 DataVolume
kubectl get pvc -A | grep my-vm             # VM 相關的 PVC

# === 事件（關鍵疑難排解工具）===
kubectl get events --sort-by=.lastTimestamp -n <namespace> | tail -30
kubectl get events --field-selector involvedObject.name=my-vm

# === 節點資訊 ===
kubectl get nodes -o wide
kubectl describe node <node-name> | grep -A 20 "Conditions"
kubectl describe node <node-name> | grep -A 20 "Allocated resources"
```

### virtctl 診斷指令

```bash
# === VM 互動 ===
virtctl console my-vm              # 串列主控台
virtctl vnc my-vm                  # VNC 圖形主控台
virtctl ssh user@my-vm             # SSH 連線（需要 Guest Agent）

# === VM 操作 ===
virtctl start my-vm                # 啟動 VM
virtctl stop my-vm                 # 停止 VM
virtctl restart my-vm              # 重啟 VM
virtctl pause vmi my-vm            # 暫停 VM
virtctl unpause vmi my-vm          # 恢復 VM

# === 遷移操作 ===
virtctl migrate my-vm              # 觸發遷移
virtctl migrate-cancel my-vm       # 取消遷移

# === 磁碟管理 ===
virtctl addvolume my-vm --volume-name=new-disk    # Hotplug 磁碟
virtctl removevolume my-vm --volume-name=new-disk  # 移除磁碟

# === Guest OS 資訊 ===
virtctl guestosinfo my-vm          # Guest OS 詳細資訊
virtctl userlist my-vm             # 已登入使用者
virtctl fslist my-vm               # Filesystem 列表
```

### 節點層級診斷

```bash
# === 在節點上檢查 KVM 支援 ===
# SSH 到節點後：
lsmod | grep kvm
ls -la /dev/kvm

# === 檢查 QEMU 進程 ===
ps aux | grep qemu

# === 檢查 libvirt 域 ===
virsh list --all

# === 檢查 virt-handler 狀態 ===
systemctl status kubelet
journalctl -u kubelet | grep virt-handler

# === 網路診斷 ===
ip link show
brctl show
ovs-vsctl show  # 若使用 OVS

# === 儲存診斷 ===
lsblk
df -h
mount | grep kubelet
```

## 緊急處理

### VM Stuck in Migration（VM 遷移卡住）

::: danger 緊急操作
以下操作可能導致資料遺失。僅在確認遷移已完全停滯且無法恢復時才執行。
:::

```bash
# 1. 嘗試正常取消遷移
virtctl migrate-cancel my-vm

# 2. 如果取消無效，刪除遷移物件
kubectl delete vmim <migration-name>

# 3. 如果仍然卡住，強制刪除目標 virt-launcher Pod
kubectl delete pod <target-launcher-pod> --force --grace-period=0

# 4. 確認 VM 回到正常運行狀態
kubectl get vmi my-vm -o jsonpath='{.status.migrationState}'
```

### VM Stuck in Scheduling（VM 調度卡住）

```bash
# 1. 檢查 VMI 狀態和條件
kubectl get vmi my-vm -o yaml | grep -A 30 conditions

# 2. 檢查 virt-controller 日誌
kubectl logs -n kubevirt -l kubevirt.io=virt-controller | grep my-vm

# 3. 如果需要強制清理
# 停止 VM
kubectl patch vm my-vm --type merge -p '{"spec":{"running":false}}'

# 等待 VMI 被清理
kubectl get vmi my-vm -w

# 如果 VMI 未被清理，檢查 finalizers
kubectl get vmi my-vm -o jsonpath='{.metadata.finalizers}'

# 移除 finalizers（最後手段）
kubectl patch vmi my-vm --type json -p '[{"op":"remove","path":"/metadata/finalizers"}]'
```

::: danger 移除 Finalizers 的風險
移除 Finalizers 是最後手段，可能導致資源清理不完整（如 PVC 未正確解綁、網路配置殘留）。僅在確認其他方法無效時使用。
:::

### virt-handler 崩潰

**症狀：** 特定節點上的所有 VM 失去管理，無法啟動新 VM。

```bash
# 1. 檢查 virt-handler DaemonSet
kubectl get ds -n kubevirt virt-handler
kubectl get pods -n kubevirt -l kubevirt.io=virt-handler -o wide

# 2. 查看崩潰的 virt-handler 日誌
kubectl logs -n kubevirt virt-handler-xxxxx --previous

# 3. 檢查節點狀態
kubectl describe node <affected-node>

# 4. 嘗試重啟 virt-handler
kubectl delete pod -n kubevirt virt-handler-xxxxx

# 5. 如果問題持續，排空節點（逐步遷移 VM）
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data

# 6. 檢查節點系統日誌
journalctl -u kubelet --since "1 hour ago" | grep -i error
```

### 叢集升級失敗

**症狀：** KubeVirt 升級後元件處於異常狀態。

```bash
# 1. 檢查 KubeVirt Operator 狀態
kubectl get kubevirt -n kubevirt -o yaml | grep -A 20 status

# 2. 檢查各元件版本
kubectl get deployment -n kubevirt -o \
  jsonpath='{range .items[*]}{.metadata.name}: {.spec.template.spec.containers[0].image}{"\n"}{end}'

# 3. 檢查 Operator 日誌
kubectl logs -n kubevirt -l kubevirt.io=virt-operator --tail=200

# 4. 確認升級進度
kubectl get kubevirt -n kubevirt -o jsonpath='{.items[0].status.observedGeneration}'
kubectl get kubevirt -n kubevirt -o jsonpath='{.items[0].status.conditions}' | jq .

# 5. 若需要回滾（謹慎操作）
# 先備份當前 KubeVirt CR
kubectl get kubevirt -n kubevirt -o yaml > kubevirt-backup.yaml

# 修改版本回到之前的版本
kubectl edit kubevirt kubevirt -n kubevirt
```

::: warning 升級建議
- 升級前務必閱讀 Release Notes，特別是 Breaking Changes
- 先在測試環境驗證升級過程
- 確保所有 VM 都可以遷移（以防需要排空節點）
- 升級期間不要同時進行其他叢集變更
- 保留升級前的 KubeVirt CR 備份
:::

## 問題回報

當以上方法都無法解決問題時，建議向 KubeVirt 社群回報：

```bash
# 收集完整的診斷資訊
# 1. KubeVirt 版本和配置
kubectl get kubevirt -n kubevirt -o yaml > kubevirt-config.yaml

# 2. 問題 VM 的完整定義和狀態
kubectl get vm my-vm -o yaml > vm-definition.yaml
kubectl get vmi my-vm -o yaml > vmi-status.yaml
kubectl describe vmi my-vm > vmi-describe.txt

# 3. 相關事件
kubectl get events -n <namespace> --sort-by=.lastTimestamp > events.txt

# 4. 元件日誌
kubectl logs -n kubevirt -l kubevirt.io=virt-controller --tail=500 > virt-controller.log
kubectl logs -n kubevirt -l kubevirt.io=virt-handler --tail=500 > virt-handler.log
kubectl logs virt-launcher-my-vm-xxxxx --tail=500 > virt-launcher.log

# 5. 節點資訊
kubectl describe nodes > nodes-info.txt
```

::: info 回報管道
- **GitHub Issues**：https://github.com/kubevirt/kubevirt/issues
- **Slack**：kubernetes.slack.com #virtualization 頻道
- **郵件列表**：kubevirt-dev@googlegroups.com

回報時請附上以上收集的診斷資訊，並清楚描述：
1. 預期行為（Expected）
2. 實際行為（Actual）
3. 重現步驟（Steps to reproduce）
4. 環境資訊（Kubernetes 版本、KubeVirt 版本、CNI、CSI、硬體等）
:::
