---
title: KubeVirt 快速入門
description: 從零開始，在 Kubernetes 上建立你的第一台虛擬機器
outline: [2, 3]
---

# KubeVirt 快速入門

本指南帶你從安裝到建立第一台 VM，涵蓋 Linux / Windows VM、網路、儲存與日常操作。
如果你是從 VMware vSphere 轉換過來的工程師，每個章節都附有對照提示，幫助你快速上手。

::: tip 💡 VMware 工程師提示
把 KubeVirt 想像成「在 Kubernetes 裡的 ESXi」——你用 YAML 取代 vSphere Client，用 `virtctl` 取代 `govc` / PowerCLI。
:::

---

## 前置需求

在開始之前，確認你已具備以下環境：

| 項目 | 最低要求 | 說明 |
|------|----------|------|
| Kubernetes 叢集 | v1.25+ | minikube、kind、或任何生產叢集皆可 |
| kubectl | 與叢集版本匹配 | 已設定好 kubeconfig |
| 硬體虛擬化 | 支援 Intel VT-x / AMD-V | 節點需啟用巢狀虛擬化或裸機 |
| 儲存 | 至少一個 StorageClass | Windows VM 或資料磁碟需要 PVC |

::: warning 巢狀虛擬化檢查
在節點上執行以下指令確認硬體虛擬化是否啟用：
```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
# 輸出 > 0 表示支援
```
如果你使用雲端虛擬機器作為節點，需確認該 VM 類型支援巢狀虛擬化（例如 GCE `n1-standard` 系列需額外啟用）。
:::

---

## 安裝 KubeVirt

### 取得最新版本號

```bash
export KUBEVIRT_VERSION=$(curl -s https://api.github.com/repos/kubevirt/kubevirt/releases/latest | grep tag_name | cut -d '"' -f 4)
echo "安裝版本: ${KUBEVIRT_VERSION}"
```

### 部署 KubeVirt Operator 與 CR

```bash
# 1. 部署 Operator
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_VERSION}/kubevirt-operator.yaml"

# 2. 部署 KubeVirt Custom Resource
kubectl apply -f "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_VERSION}/kubevirt-cr.yaml"
```

### 等待安裝完成

```bash
kubectl -n kubevirt wait kv kubevirt --for condition=Available --timeout=300s
```

驗證所有元件是否正常運作：

```bash
kubectl get pods -n kubevirt
```

預期輸出應顯示 `virt-operator`、`virt-api`、`virt-controller`、`virt-handler` 皆為 `Running` 狀態。

::: tip 💡 VMware 工程師提示
這個步驟相當於在 ESXi 主機上安裝 Hypervisor——KubeVirt Operator 就是你的「vCenter 安裝程式」，而 `kubevirt` CR 則是啟動整個虛擬化平台的開關。
:::

::: info 如果節點不支援硬體虛擬化
你可以啟用軟體模擬模式（僅供開發測試用途）：
```bash
kubectl -n kubevirt patch kubevirt kubevirt --type=merge --patch \
  '{"spec":{"configuration":{"developerConfiguration":{"useEmulation":true}}}}'
```
:::

---

## 安裝 virtctl

`virtctl` 是 KubeVirt 的專屬 CLI 工具，用於管理 VM 的生命週期與連線。

### 方法一：直接下載

```bash
export KUBEVIRT_VERSION=$(curl -s https://api.github.com/repos/kubevirt/kubevirt/releases/latest | grep tag_name | cut -d '"' -f 4)

# Linux (amd64)
curl -L -o virtctl "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_VERSION}/virtctl-${KUBEVIRT_VERSION}-linux-amd64"

# macOS (arm64 / Apple Silicon)
curl -L -o virtctl "https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_VERSION}/virtctl-${KUBEVIRT_VERSION}-darwin-arm64"

chmod +x virtctl
sudo mv virtctl /usr/local/bin/
```

### 方法二：使用 krew 安裝

```bash
kubectl krew install virt
# 之後使用 kubectl virt <command> 即可
```

### 驗證安裝

```bash
virtctl version
```

---

## 建立第一台 Linux VM

### 使用 ContainerDisk 建立 Cirros VM

ContainerDisk 將磁碟映像檔打包在容器映像中，無需設定 PVC 即可快速啟動 VM。

```yaml
# linux-vm.yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-first-linux-vm
  labels:
    app: linux-vm
spec:
  running: true
  template:
    metadata:
      labels:
        app: linux-vm
    spec:
      domain:
        resources:
          requests:
            memory: "512Mi"
            cpu: "1"
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
        machine:
          type: q35
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          containerDisk:
            image: quay.io/kubevirt/cirros-container-disk-demo:latest
        - name: cloudinitdisk
          cloudInitNoCloud:
            userData: |
              #cloud-config
              password: cirros
              chpasswd:
                expire: false
              ssh_authorized_keys:
                - ssh-rsa YOUR_PUBLIC_KEY_HERE
```

### 部署並確認狀態

```bash
# 建立 VM
kubectl apply -f linux-vm.yaml

# 觀察 VM 狀態
kubectl get vm my-first-linux-vm

# 觀察 VMI（VirtualMachineInstance，實際執行的實例）
kubectl get vmi my-first-linux-vm
```

::: tip 💡 VMware 工程師提示
`VirtualMachine`（VM）相當於 vSphere 中「已註冊的虛擬機器」，而 `VirtualMachineInstance`（VMI）相當於「正在運行的虛擬機器」。VM 是宣告式定義，VMI 是實際運行的實例。
:::

### 使用 Fedora 映像（更完整的 Linux 體驗）

```yaml
# fedora-vm.yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: fedora-vm
spec:
  running: true
  template:
    metadata:
      labels:
        app: fedora-vm
    spec:
      domain:
        resources:
          requests:
            memory: "2Gi"
            cpu: "2"
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
        machine:
          type: q35
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          containerDisk:
            image: quay.io/containerdisks/fedora:latest
        - name: cloudinitdisk
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: fedora-vm
              user: fedora
              password: fedora
              chpasswd:
                expire: false
```

---

## 建立第一台 Windows VM

Windows VM 需要較多資源，並且建議啟用 Hyper-V enlightenments 以獲得最佳效能。

::: warning 準備工作
Windows VM 需要：
1. **Windows 安裝 ISO 或已預裝的磁碟映像**（透過 PVC 或 DataVolume 提供）
2. **VirtIO 驅動程式 ISO**（Windows 不內建 VirtIO 驅動）
3. **足夠的記憶體**（建議至少 4Gi）
:::

```yaml
# windows-vm.yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: windows-vm
spec:
  running: true
  template:
    metadata:
      labels:
        app: windows-vm
    spec:
      domain:
        clock:
          timer:
            hpet:
              present: false
            pit:
              tickPolicy: delay
            rtc:
              tickPolicy: catchup
            hyperv: {}
          utc: {}
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
        features:
          acpi: {}
          apic: {}
          hyperv:
            relaxed: {}
            vapic: {}
            vpindex: {}
            spinlocks:
              spinlocks: 8191
            synic: {}
            synictimer:
              direct: {}
            tlbflush: {}
            frequencies: {}
            reenlightenment: {}
            ipi: {}
            runtime: {}
            reset: {}
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: sata
            - name: virtio-drivers
              cdrom:
                bus: sata
          interfaces:
            - name: default
              masquerade: {}
          tpm: {}
        machine:
          type: q35
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          persistentVolumeClaim:
            claimName: windows-disk-pvc
        - name: virtio-drivers
          containerDisk:
            image: quay.io/kubevirt/virtio-container-disk:latest
```

::: info Hyper-V Enlightenments 說明
上面 YAML 中的 `features.hyperv` 區塊啟用了 Windows 專屬的半虛擬化功能，讓 Windows Guest OS 知道自己運行在虛擬化環境中，從而使用更高效的程式碼路徑。這些設定對 Windows 效能有顯著提升。
:::

::: tip 💡 VMware 工程師提示
Hyper-V enlightenments 類似 VMware Tools 的角色——它讓 Guest OS 與 Hypervisor 之間的溝通更有效率。`virtio-container-disk` 則相當於 VMware Tools ISO，提供磁碟與網路的半虛擬化驅動。
:::

---

## 連線到 VM

KubeVirt 提供多種方式連線到 VM：

![VM 連線方式](/diagrams/kubevirt/kubevirt-quickstart-connect-methods.png)

### 序列控制台（Serial Console）

```bash
# 連線到 VM 的序列控制台
virtctl console my-first-linux-vm

# 退出控制台：按 Ctrl+]
```

### VNC 圖形桌面

```bash
# 開啟 VNC 連線（會自動啟動 VNC 客戶端）
virtctl vnc my-first-linux-vm

# 如果只需要 proxy（不自動開啟客戶端）
virtctl vnc --proxy-only my-first-linux-vm
```

### SSH 連線

```bash
# 使用 virtctl 內建的 SSH tunnel
virtctl ssh fedora@fedora-vm

# 使用本地 SSH 金鑰
virtctl ssh -i ~/.ssh/id_rsa fedora@fedora-vm
```

### Port Forwarding

```bash
# 將 VM 的 port 8080 轉發到本地 port 8080
virtctl port-forward my-first-linux-vm 8080:8080
```

::: tip 💡 VMware 工程師提示
`virtctl console` = vSphere 的「Open Console」序列模式；`virtctl vnc` = 「Open Console」圖形模式；`virtctl ssh` = 直接 SSH，不需要知道 VM 的 IP 位址。
:::

---

## VM 基本操作

以下是 VM 日常管理的常用指令：

### 生命週期管理

```bash
# 啟動 VM
virtctl start my-first-linux-vm

# 優雅關機（送出 ACPI shutdown 訊號）
virtctl stop my-first-linux-vm

# 強制關機
virtctl stop my-first-linux-vm --force

# 重新啟動
virtctl restart my-first-linux-vm

# 暫停 VM（凍結 vCPU，記憶體保留）
virtctl pause vm my-first-linux-vm

# 取消暫停
virtctl unpause vm my-first-linux-vm
```

### 即時遷移（Live Migration）

```bash
# 將 VM 遷移到另一個節點
virtctl migrate my-first-linux-vm

# 查看遷移狀態
kubectl get vmim
```

::: info 即時遷移前置條件
即時遷移需要：
- 叢集有多個可排程節點
- VM 使用共享儲存（如 Ceph RBD、NFS）或 ContainerDisk
- VM 未使用 `hostPath` 或 node-local 儲存
:::

### 狀態查詢

```bash
# 列出所有 VM
kubectl get vm

# 列出所有正在運行的 VMI
kubectl get vmi

# 查看 VM 詳細資訊
kubectl describe vm my-first-linux-vm

# 查看 VMI 事件與狀態
kubectl describe vmi my-first-linux-vm
```

::: tip 💡 VMware 工程師提示
| 你在 VMware 做的事 | 在 KubeVirt 怎麼做 |
|---|---|
| Power On | `virtctl start <vm>` |
| Power Off | `virtctl stop <vm>` |
| Suspend | `virtctl pause vm <vm>` |
| Resume | `virtctl unpause vm <vm>` |
| Reset | `virtctl restart <vm>` |
| vMotion | `virtctl migrate <vm>` |
:::

---

## 添加資料磁碟

### 建立 PVC 作為資料磁碟

```yaml
# data-disk-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data-disk
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

### 在 VM 中掛載資料磁碟

在 `VirtualMachine` 的 YAML 中增加磁碟與 Volume 定義：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-with-data-disk
spec:
  running: true
  template:
    spec:
      domain:
        resources:
          requests:
            memory: "1Gi"
            cpu: "1"
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
            - name: datadisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
        machine:
          type: q35
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          containerDisk:
            image: quay.io/containerdisks/fedora:latest
        - name: datadisk
          persistentVolumeClaim:
            claimName: my-data-disk
```

### 動態添加磁碟（Hotplug）

無需關機即可添加磁碟：

```bash
# 動態掛載 PVC 到正在運行的 VM
virtctl addvolume my-first-linux-vm \
  --volume-name=extra-disk \
  --claim-name=my-data-disk

# 動態卸載磁碟
virtctl removevolume my-first-linux-vm --volume-name=extra-disk
```

::: tip 💡 VMware 工程師提示
Hotplug 磁碟類似 vSphere 中「編輯設定 → 新增硬碟」而不用關機的操作。PVC 就是你的 VMDK 檔案，StorageClass 則對應到 Datastore 的角色。
:::

---

## 設定網路

### Masquerade 模式（預設推薦）

Masquerade 是最簡單的網路模式，VM 透過 NAT 存取外部網路：

![Masquerade 網路模式](/diagrams/kubevirt/kubevirt-quickstart-masquerade-net.png)

```yaml
# 在 VM spec 中設定 masquerade 網路
spec:
  template:
    spec:
      domain:
        devices:
          interfaces:
            - name: default
              masquerade: {}
              ports:
                - name: http
                  port: 80
                - name: ssh
                  port: 22
      networks:
        - name: default
          pod: {}
```

### 透過 Service 暴露 VM 埠

```yaml
# vm-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: linux-vm-ssh
spec:
  type: NodePort
  selector:
    app: linux-vm
  ports:
    - name: ssh
      protocol: TCP
      port: 22
      targetPort: 22
```

```bash
kubectl apply -f vm-service.yaml

# 查看 NodePort
kubectl get svc linux-vm-ssh
```

::: info 進階網路選項
KubeVirt 支援多種網路模式：
- **Masquerade**：NAT 模式，適合大部分場景（本指南使用）
- **Bridge**：L2 橋接，VM 直接取得 Pod 網段 IP
- **SR-IOV**：硬體直通，適合高效能需求
- **Multus**：多網卡支援，可同時接入多個網路

詳細說明請參考 [網路概覽](../networking/overview.md)。
:::

::: tip 💡 VMware 工程師提示
Masquerade 模式類似 VMware Workstation 的 NAT 模式。如果你需要類似 vSphere 中 VM 直接拿到 VLAN IP 的行為，請使用 Bridge 或 SR-IOV 搭配 Multus CNI。
:::

---

## VMware 工程師速查表

如果你有 VMware vSphere 的管理經驗，以下對照表幫助你快速找到 KubeVirt 中的對應操作：

### 日常操作對照

| VMware vSphere | KubeVirt | 備註 |
|----------------|----------|------|
| Power On VM | `virtctl start <vm>` | 或設定 `spec.running: true` |
| Power Off VM | `virtctl stop <vm>` | 送出 ACPI 關機訊號 |
| Open Console | `virtctl console <vm>` | 序列控制台 |
| Open VNC Console | `virtctl vnc <vm>` | 圖形桌面 |
| vMotion | `virtctl migrate <vm>` | 即時遷移到其他節點 |
| Create Snapshot | 建立 `VirtualMachineSnapshot` | 見下方 YAML |
| Clone VM | 建立 `VirtualMachineClone` | 見下方 YAML |
| VM Template | `VirtualMachineInstancetype` + `VirtualMachinePreference` | 定義硬體規格與偏好 |
| Edit VM Settings | `kubectl edit vm <vm>` | 直接編輯 YAML |
| Install VMware Tools | 使用 `virtio-container-disk` | 半虛擬化驅動 |
| Resource Pool | Kubernetes `ResourceQuota` | 命名空間層級的資源限制 |
| Datastore | `StorageClass` + `PVC` | 儲存後端抽象 |
| Port Group | Multus `NetworkAttachmentDefinition` | 網路定義 |

### 快照（Snapshot）

```yaml
# snapshot.yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: my-vm-snapshot
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-first-linux-vm
```

```bash
# 建立快照
kubectl apply -f snapshot.yaml

# 查看快照狀態
kubectl get vmsnapshot

# 從快照還原
cat <<EOF | kubectl apply -f -
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineRestore
metadata:
  name: restore-my-vm
spec:
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-first-linux-vm
  virtualMachineSnapshotName: my-vm-snapshot
EOF
```

### 複製（Clone）

```yaml
# clone.yaml
apiVersion: clone.kubevirt.io/v1alpha1
kind: VirtualMachineClone
metadata:
  name: clone-my-vm
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-first-linux-vm
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-cloned-vm
```

### 使用 Instancetype 與 Preference（類似 VM Template）

```yaml
# 使用預定義的 instancetype 與 preference 建立 VM
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-from-template
spec:
  instancetype:
    kind: VirtualMachineClusterInstancetype
    name: u1.medium
  preference:
    kind: VirtualMachineClusterPreference
    name: fedora
  running: true
  template:
    spec:
      domain:
        devices:
          interfaces:
            - name: default
              masquerade: {}
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          containerDisk:
            image: quay.io/containerdisks/fedora:latest
```

```bash
# 列出可用的 instancetype
kubectl get virtualmachineclusterinstancetype

# 列出可用的 preference
kubectl get virtualmachineclusterpreference
```

::: tip 💡 VMware 工程師提示
`VirtualMachineInstancetype` 定義了硬體規格（CPU、記憶體），類似 vSphere 中建立 Template 時選擇的硬體配置。`VirtualMachinePreference` 定義了 Guest OS 偏好設定（firmware、裝置類型等），類似選擇「Guest OS Type: Linux / Windows」時自動套用的最佳化設定。
:::

---

## 完整流程總覽

![KubeVirt 完整使用流程](/diagrams/kubevirt/kubevirt-quickstart-complete-workflow.png)

---

## 常見問題

::: danger VM 一直停在 Scheduling 狀態？
1. 確認節點資源是否足夠：`kubectl describe node | grep -A5 Allocatable`
2. 確認硬體虛擬化是否啟用：`kubectl get kubevirt kubevirt -n kubevirt -o yaml | grep useEmulation`
3. 查看 VMI 事件：`kubectl describe vmi <vm-name>`
:::

::: warning ContainerDisk VM 資料不持久
ContainerDisk 是唯讀的——VM 重啟後所有變更都會遺失。如需持久化資料，請使用 PVC 作為根磁碟或額外掛載資料磁碟。
:::

---

## 下一步

- 📖 [架構概覽](../architecture/overview.md) — 了解 KubeVirt 的內部架構
- 🔧 [virtctl 完整指南](../virtctl/guide.md) — 更多 CLI 操作
- 🌐 [網路設定](../networking/overview.md) — Bridge、SR-IOV 與 Multus
- 💾 [儲存管理](../storage/overview.md) — PVC、DataVolume 與 ContainerDisk
- 🔄 [即時遷移](../advanced/live-migration.md) — 遷移機制與最佳實踐
- 📸 [快照與複製](../api-resources/snapshot-clone.md) — 進階快照操作
- 🔀 [VMware 遷移指南](./vmware-to-kubevirt.md) — 從 vSphere 搬遷到 KubeVirt
