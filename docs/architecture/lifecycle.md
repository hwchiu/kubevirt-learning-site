# VM 生命週期流程

本頁詳細說明 VirtualMachine (VM) 與 VirtualMachineInstance (VMI) 的完整生命週期，包含建立、執行、遷移、停止的每個步驟。

## VM 與 VMI 的關係

```
VirtualMachine (VM)
├── 持久存在，即使 VM 停止，此物件仍在
├── 包含 RunStrategy 控制 VM 的執行策略
├── 包含 DataVolumeTemplates 管理磁碟
└── 當 running=true 或 RunStrategy=Always 時
    └── 建立 VirtualMachineInstance (VMI)
            ├── 暫態物件，代表「正在執行的 VM」
            ├── 包含 spec.nodeName（被調度到哪個節點）
            └── 關機後被刪除（VM 物件仍保留）
```

### RunStrategy 策略

| 策略 | 說明 |
|------|------|
| `Always` | 如果 VMI 停止就自動重啟 |
| `Halted` | 不自動啟動，等待手動操作 |
| `Manual` | 由使用者手動控制 start/stop |
| `RerunOnFailure` | 僅在 VMI 失敗時重啟，正常關機後不重啟 |
| `Once` | 只啟動一次，停止後不再重啟 |
| `WaitAsReceiver` | 等待作為 Migration 目標接收方 |

## VMI 狀態轉換圖

```
                   kubectl apply VM
                        │
                        ▼
                   ┌─────────┐
                   │ Pending  │  ← virt-controller 建立 Pod，等待調度
                   └────┬────┘
                        │ Pod 被調度到節點
                        ▼
                 ┌────────────┐
                 │ Scheduling  │  ← virt-handler 開始處理
                 └─────┬──────┘
                       │ 節點準備完成
                       ▼
                 ┌───────────┐
                 │ Scheduled  │  ← libvirt domain 定義完成
                 └─────┬─────┘
                       │ QEMU 啟動
                       ▼
                 ┌─────────┐
                 │ Running  │  ← VM 正常執行
                 └────┬────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌──────────┐ ┌─────────┐ ┌──────────┐
    │ Migrating│ │ Paused  │ │Succeeded │
    └────┬─────┘ └────┬────┘ └──────────┘
         │            │
         ▼            ▼
      Running      Running
   (新節點上)    (unpause 後)
                             ┌──────────┐
                             │  Failed  │
                             └──────────┘
```

## VM 可列印狀態 (PrintableStatus)

使用者可透過 `kubectl get vm` 看到以下狀態：

| 狀態 | 說明 |
|------|------|
| `Stopped` | VM 已停止，VMI 不存在 |
| `Provisioning` | 等待 DataVolume 準備完成 |
| `Starting` | VM 正在啟動中 |
| `Running` | VM 正在執行 |
| `Paused` | VM 已暫停 |
| `Stopping` | VM 正在停止中 |
| `Terminating` | VM 正在終止 |
| `CrashLoopBackOff` | VM 持續崩潰，進入回退等待 |
| `Migrating` | VM 正在 Live Migration |
| `WaitingForVolumeBinding` | 等待 PVC 綁定 |
| `DataVolumeError` | DataVolume 發生錯誤 |
| `ErrorUnschedulable` | 找不到合適的節點 |
| `ErrImagePull` / `ImagePullBackOff` | 映像檔拉取失敗 |

## 詳細建立流程

### 步驟 1：使用者提交 VM 定義

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-vm
  namespace: default
spec:
  runStrategy: Always
  template:
    spec:
      domain:
        cpu:
          cores: 2
        memory:
          guest: 4Gi
        devices:
          disks:
          - name: rootdisk
            disk:
              bus: virtio
          interfaces:
          - name: default
            masquerade: {}
      networks:
      - name: default
        pod: {}
      volumes:
      - name: rootdisk
        containerDisk:
          image: quay.io/kubevirt/fedora-cloud-container-disk-demo:latest
```

### 步驟 2：virt-api 處理

```
POST /apis/kubevirt.io/v1/namespaces/default/virtualmachines
        │
        ▼
Mutating Webhook (virt-api)
  ● 補齊預設值 (terminationGracePeriodSeconds: 180)
  ● 設定預設網路介面模型
  ● 加入必要的 annotations

        │
        ▼
Validating Webhook (virt-api)
  ● 驗證 CPU/Memory 設定
  ● 驗證磁碟與 Volume 對應
  ● 驗證網路設定
  ● 檢查 Instancetype 衝突

        │
        ▼
寫入 VirtualMachine CR 到 etcd
```

### 步驟 3：virt-controller (VM 控制器)

```go
// pkg/virt-controller/watch/vm/vm.go
func (c *Controller) sync(vm *v1.VirtualMachine) {
    // 1. 計算期望狀態 (running=true → 需要 VMI)
    // 2. 取得目前的 VMI
    // 3. 若 VMI 不存在 → 建立 VMI
    // 4. 若 VM 停止 → 刪除 VMI
    // 5. 處理 DataVolumeTemplates
    // 6. 更新 VM status
}
```

### 步驟 4：virt-controller (VMI 控制器)

```go
// pkg/virt-controller/watch/vmi/vmi.go
func (c *Controller) sync(vmi *v1.VirtualMachineInstance) {
    // 1. 若 Pod 不存在 → 建立 virt-launcher Pod
    // 2. Pod 調度後 → 更新 VMI.spec.nodeName
    // 3. 監控 Pod 健康狀態
    // 4. 更新 VMI 狀態 (phase, conditions)
}
```

**建立的 virt-launcher Pod 包含：**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: virt-launcher-my-vm-xxxxx
  labels:
    kubevirt.io: virt-launcher
    kubevirt.io/created-by: <VMI-UID>
spec:
  containers:
  - name: compute
    image: virt-launcher:latest
    # privileged 容器，用於 libvirt/QEMU 管理
    securityContext:
      privileged: true
  volumes:
  # 掛載 PVC、ConfigMap、Secret 等
```

### 步驟 5：virt-handler (節點代理)

```go
// pkg/virt-handler/controller.go
func (d *VirtualMachineController) execute(key string) error {
    // 1. 取得 VMI (spec.nodeName == 本節點)
    // 2. 取得目前 libvirt domain 狀態
    // 3. 比較期望狀態 vs 實際狀態
    // 4. 呼叫 virt-launcher 執行同步
    //    - 設定網路 (virt-handler 在 launcher netns 執行 CNI)
    //    - 掛載儲存
    //    - 同步 domain 定義
}
```

**兩階段網路配置：**

```
Phase 1 (Privileged — virt-handler 執行):
  ● 在 virt-launcher Pod 的 network namespace 執行
  ● 收集 CNI 分配的 IP、MAC、路由資訊
  ● 建立 bridge/veth pair 基礎設施
  ● 快取網路配置到 /var/run/kubevirt-private/vif-cache-xxx.json

Phase 2 (Unprivileged — virt-launcher 執行):
  ● 讀取快取的網路配置
  ● 產生 libvirt domain XML 的網路部分
  ● 啟動 DHCP server (如需要)
```

### 步驟 6：virt-launcher

```go
// pkg/virt-launcher/virtwrap/manager.go
func (l *LibvirtDomainManager) SyncVMI(vmi *v1.VirtualMachineInstance, ...) {
    // 1. 將 VMI spec 轉換為 libvirt domain XML
    //    (pkg/virt-launcher/virtwrap/converter/)
    // 2. 透過 libvirt API 定義 domain
    // 3. 啟動 domain (libvirt virDomainCreate)
    // 4. QEMU 程序啟動，VM 開始執行
}
```

## 刪除/停止流程

```
kubectl delete vm my-vm
        │
        ▼
1. [virt-controller]
   ├── 設定 VMI 的 DeletionTimestamp
   └── 等待 VMI 終止

        │
        ▼
2. [virt-handler]
   ├── 偵測到 VMI 刪除
   ├── 呼叫 virt-launcher 發送 ACPI 關機訊號
   └── 等待 QEMU 程序退出 (grace period: 180秒)

        │
        ▼
3. [virt-launcher]
   ├── 收到關機訊號後轉發給 QEMU
   ├── 等待 VM 優雅關機
   └── 若超時 → 強制終止 QEMU

        │
        ▼
4. [Kubernetes]
   ├── 刪除 virt-launcher Pod
   └── 清理 PVC、ConfigMap 等資源

        │
        ▼
5. [virt-controller]
   └── 更新 VM status (Stopped)
       (如果 RunStrategy=Always → 自動重新建立 VMI)
```

## 狀態更新流程

```
QEMU 域事件
    │
    ▼
virt-launcher (監聽 libvirt 事件)
    │ domain 狀態改變
    ▼
virt-handler (接收 launcher 通知)
    │ 更新 VMI status
    ▼
Kubernetes API Server
    │ VMI.Status 更新
    ▼
virt-controller (watch VMI 改變)
    │ 更新 VM status
    ▼
使用者可透過 kubectl get vm 看到最新狀態
```

## 常用狀態查詢指令

```bash
# 查看 VM 狀態
kubectl get vm
kubectl describe vm my-vm

# 查看 VMI 詳細狀態
kubectl get vmi
kubectl describe vmi my-vm

# 查看 virt-launcher Pod
kubectl get pod -l kubevirt.io=virt-launcher

# 查看 VM 事件
kubectl get events --field-selector involvedObject.name=my-vm

# 查看 virt-handler 日誌 (在目標節點上)
kubectl logs -n kubevirt -l kubevirt.io=virt-handler --tail=100
```
