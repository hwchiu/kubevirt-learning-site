# 從 VMware 到 KubeVirt — 轉換指南

::: info 適用對象
本指南專為有 VMware vSphere 經驗的系統管理員和架構師撰寫，協助您將既有的 VMware 知識對應到 KubeVirt 的世界觀中。無論您是正在評估遷移方案，或是已經開始使用 KubeVirt，本文都能幫助您快速上手。
:::

## 為什麼從 VMware 遷移到 KubeVirt

### 授權成本與 Broadcom 收購的影響

自 Broadcom 完成對 VMware 的收購後，許多企業面臨了嚴峻的授權成本挑戰：

- **訂閱制轉換**：從永久授權轉為訂閱制，年度成本大幅上升
- **產品捆綁銷售**：取消單獨產品購買，強制購買套件組合
- **合作夥伴生態縮減**：大量 VMware 合作夥伴被終止合約
- **免費版本取消**：ESXi 免費版（Hypervisor）已被下架
- **支援成本上升**：技術支援與服務合約價格調漲

::: danger 成本衝擊
根據多家企業的報告，Broadcom 收購後的 VMware 授權費用上漲幅度從 **200% 到 1200%** 不等。對於中大型企業而言，這可能意味著每年數百萬美元的額外支出。
:::

### 雲原生統一管理的優勢

KubeVirt 建立在 Kubernetes 之上，帶來了雲原生生態的所有好處：

- **統一管理平面**：使用相同的 kubectl、RBAC、Namespace 管理容器與虛擬機
- **GitOps 工作流程**：VM 定義即程式碼，可透過 Git 版本控制
- **豐富的生態系統**：Prometheus 監控、Istio 服務網格、ArgoCD 持續部署
- **開源社群**：活躍的 CNCF 社群，無供應商鎖定風險
- **自動化能力**：Kubernetes Operator 模式，自動化生命週期管理

### Container + VM 混合工作負載

```
┌─────────────────────────────────────────────────┐
│                 Kubernetes Cluster                │
│  ┌───────────┐  ┌───────────┐  ┌──────────────┐ │
│  │ Container │  │ Container │  │  KubeVirt VM │ │
│  │  (nginx)  │  │  (redis)  │  │  (Windows)   │ │
│  └───────────┘  └───────────┘  └──────────────┘ │
│  ┌───────────┐  ┌──────────────────────────────┐ │
│  │ Container │  │       KubeVirt VM            │ │
│  │  (app)    │  │   (Legacy Database)          │ │
│  └───────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## 核心概念對照表

::: tip 閱讀提示
以下對照表列出了 VMware 與 KubeVirt 之間最關鍵的概念映射。建議收藏此表，在日常工作中隨時參考。
:::

| VMware 概念 | KubeVirt 對應 | 說明 |
|---|---|---|
| **vCenter Server** | Kubernetes API Server | 集中管理控制平面，所有操作透過 API 進行 |
| **ESXi Host** | Kubernetes Node + virt-handler | 運算節點，virt-handler 負責節點層級的 VM 管理 |
| **VMDK** | PVC / DataVolume | 虛擬磁碟，PVC 提供持久化儲存，DataVolume 簡化匯入流程 |
| **VM Template** | Instancetype + Preference | VM 規格模板，Instancetype 定義資源，Preference 定義偏好設定 |
| **vSwitch / dvSwitch** | CNI（Calico / OVN）+ Multus | 虛擬網路交換器，Multus 允許多網路介面 |
| **Port Group** | NetworkAttachmentDefinition（NAD） | 網路分組定義，透過 NAD 定義額外網路介面 |
| **vMotion** | Live Migration | 不中斷服務的 VM 即時遷移 |
| **Storage vMotion** | Volume Migration | 儲存層級的遷移，在不同 StorageClass 間移動磁碟 |
| **DRS（Distributed Resource Scheduler）** | Descheduler | 自動負載均衡，重新分配工作負載到適合的節點 |
| **HA（High Availability）** | Pod Rescheduling + EvictionStrategy | 節點故障時自動重新調度 VM |
| **Resource Pool** | Namespace + ResourceQuota | 資源分配與隔離，限制 CPU / 記憶體使用量 |
| **Datastore** | StorageClass + PersistentVolume | 儲存池定義，支援多種後端（Ceph、NFS、iSCSI 等） |
| **Snapshot** | VirtualMachineSnapshot | VM 快照，依賴 CSI VolumeSnapshot 支援 |
| **Clone** | VirtualMachineClone | VM 克隆，支援完整克隆操作 |
| **OVF / OVA** | ContainerDisk / DataVolume import | VM 映像匯入匯出格式 |
| **VMware Tools** | QEMU Guest Agent（qemu-ga） | Guest OS 內的代理程式，提供資訊回報與操作 |
| **VMXNET3** | virtio-net | 半虛擬化網路介面卡，最佳網路效能 |
| **PVSCSI** | virtio-blk / virtio-scsi | 半虛擬化儲存控制器 |
| **vGPU** | GPU Passthrough / vGPU（NVIDIA） | GPU 虛擬化，支援直通與 vGPU 共享模式 |
| **NSX** | OVN-Kubernetes / Cilium | 軟體定義網路解決方案 |
| **Content Library** | Container Registry（Harbor 等） | 映像集中管理與分發 |
| **vSphere Client** | kubectl + virtctl + Dashboard | 管理介面，CLI 為主，Dashboard 為輔 |
| **vSphere Alarm** | Prometheus AlertManager | 告警與通知管理 |
| **vRealize / Aria** | Prometheus + Grafana | 監控與報表平台 |
| **Fault Tolerance（FT）** | ❌ 無直接對應 | KubeVirt 不支援同步複製模式 |

## 常見工作流程對照

### 1. 建立虛擬機

**VMware 操作：**
透過 vSphere Client → New Virtual Machine 精靈，點選介面逐步選擇 CPU、記憶體、磁碟、網路。

**KubeVirt 操作：**

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-vm
  namespace: production
spec:
  running: true
  template:
    metadata:
      labels:
        app: my-vm
    spec:
      domain:
        cpu:
          cores: 4
        memory:
          guest: 8Gi
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
          dataVolume:
            name: my-vm-rootdisk
        - name: cloudinitdisk
          cloudInitNoCloud:
            userData: |
              #cloud-config
              hostname: my-vm
              user: admin
              password: changeme
              chpasswd:
                expire: false
  dataVolumeTemplates:
    - metadata:
        name: my-vm-rootdisk
      spec:
        source:
          http:
            url: "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
        storage:
          accessModes:
            - ReadWriteMany
          resources:
            requests:
              storage: 30Gi
          storageClassName: ceph-block
```

```bash
# 建立 VM
kubectl apply -f my-vm.yaml

# 確認 VM 狀態
kubectl get vm my-vm -n production
kubectl get vmi my-vm -n production
```

### 2. 安裝作業系統

**VMware 操作：** 掛載 ISO → 從 CD-ROM 開機 → 手動安裝精靈

**KubeVirt 操作：**

```yaml
# 使用 cloud-init 自動初始化（Linux）
volumes:
  - name: cloudinitdisk
    cloudInitNoCloud:
      userData: |
        #cloud-config
        hostname: webserver
        users:
          - name: admin
            sudo: ALL=(ALL) NOPASSWD:ALL
            ssh_authorized_keys:
              - ssh-rsa AAAA...
        packages:
          - nginx
          - vim
        runcmd:
          - systemctl enable nginx
          - systemctl start nginx

# 使用 sysprep 自動初始化（Windows）
volumes:
  - name: sysprep
    sysprep:
      configMap:
        name: windows-unattend
```

::: tip 自動化差異
VMware 環境中通常需要額外的工具（如 Packer）來自動化 OS 安裝。KubeVirt 原生支援 cloud-init 和 sysprep，讓自動化更加直接。
:::

### 3. 設定網路

**VMware 操作：** 編輯 VM Settings → Network Adapter → 選擇 Port Group

**KubeVirt 操作：**

```yaml
# 基本 Pod 網路（類似預設 vSwitch）
spec:
  domain:
    devices:
      interfaces:
        - name: default
          masquerade: {}
  networks:
    - name: default
      pod: {}

# 額外的 VLAN 網路（類似 dvSwitch Port Group）
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: vlan100
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "ovs",
      "bridge": "br-data",
      "vlan": 100
    }
---
# VM 中使用多網路
spec:
  domain:
    devices:
      interfaces:
        - name: default
          masquerade: {}
        - name: data-net
          bridge: {}
  networks:
    - name: default
      pod: {}
    - name: data-net
      multus:
        networkName: vlan100
```

### 4. 掛載額外磁碟

**VMware 操作：** 編輯 VM Settings → Add Hard Disk → 選擇 Datastore

**KubeVirt 操作：**

```bash
# 使用 Hotplug 動態掛載磁碟（VM 運行中）
virtctl addvolume my-vm \
  --volume-name=extra-disk \
  --persist
```

```yaml
# 或在 VM 定義中靜態宣告
spec:
  domain:
    devices:
      disks:
        - name: extra-disk
          disk:
            bus: virtio
  volumes:
    - name: extra-disk
      persistentVolumeClaim:
        claimName: extra-pvc
```

### 5. 建立快照

**VMware 操作：** 右鍵 VM → Snapshot → Take Snapshot

**KubeVirt 操作：**

```yaml
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: my-vm-snapshot-20240101
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm
```

```bash
kubectl apply -f snapshot.yaml
# 檢查快照狀態
kubectl get vmsnapshot my-vm-snapshot-20240101
```

### 6. 複製 VM

**VMware 操作：** 右鍵 VM → Clone → Clone to Virtual Machine

**KubeVirt 操作：**

```yaml
apiVersion: clone.kubevirt.io/v1alpha1
kind: VirtualMachineClone
metadata:
  name: clone-my-vm
spec:
  source:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm
  target:
    apiGroup: kubevirt.io
    kind: VirtualMachine
    name: my-vm-clone
```

### 7. 遷移 VM 到另一台主機

**VMware 操作：** 右鍵 VM → Migrate → 選擇目標 Host

**KubeVirt 操作：**

```bash
# 觸發即時遷移
virtctl migrate my-vm

# 監控遷移狀態
kubectl get vmim -w
```

```yaml
# 或使用 YAML
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstanceMigration
metadata:
  name: migration-my-vm
spec:
  vmiName: my-vm
```

::: warning 遷移前提條件
Live Migration 需要：
- 使用 RWX（ReadWriteMany）存取模式的 PVC
- VM 使用 Masquerade 或 Bridge 模式的網路
- 未直接掛載 HostDisk 或 SR-IOV 裝置
- 目標節點有足夠的可用資源
:::

### 8. 監控 VM 效能

**VMware 操作：** vSphere Client → Performance Tab → 即時圖表

**KubeVirt 操作：**

```bash
# 查看 VM 基本資訊
virtctl guestosinfo my-vm

# 查看 VM 的 Prometheus 指標
kubectl port-forward svc/prometheus-k8s 9090:9090 -n monitoring

# 常用 PromQL 查詢
# CPU 使用率
kubevirt_vmi_cpu_usage_seconds_total{name="my-vm"}

# 記憶體使用量
kubevirt_vmi_memory_used_bytes{name="my-vm"}

# 網路流量
kubevirt_vmi_network_receive_bytes_total{name="my-vm"}
```

### 9. 調整 CPU / 記憶體（Hot Plug）

**VMware 操作：** 編輯 VM Settings → 修改 CPU / RAM（需先啟用 Hot Add）

**KubeVirt 操作：**

```yaml
# 在 VM spec 中設定 maxSockets 以支援 CPU Hot Plug
spec:
  template:
    spec:
      domain:
        cpu:
          sockets: 2
          cores: 1
          threads: 1
          maxSockets: 8  # 允許最多 hot plug 到 8 sockets
        memory:
          guest: 4Gi
          maxGuest: 16Gi  # 允許最多 hot plug 到 16Gi
```

```bash
# Hot plug CPU
kubectl patch vm my-vm --type merge -p \
  '{"spec":{"template":{"spec":{"domain":{"cpu":{"sockets":4}}}}}}'

# Hot plug Memory
kubectl patch vm my-vm --type merge -p \
  '{"spec":{"template":{"spec":{"domain":{"memory":{"guest":"8Gi"}}}}}}'
```

### 10. 設定高可用（HA）

**VMware 操作：** vSphere HA → 啟用 → 設定故障回應

**KubeVirt 操作：**

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: ha-vm
spec:
  running: true
  template:
    spec:
      evictionStrategy: LiveMigrate  # 節點維護時自動遷移
      terminationGracePeriodSeconds: 180
      domain:
        cpu:
          cores: 2
        memory:
          guest: 4Gi
```

::: info HA 機制差異
VMware HA 透過 vCenter 監控 ESXi 心跳來偵測故障。KubeVirt 依賴 Kubernetes 的節點健康檢查機制，當節點被標記為 NotReady 時，根據 `evictionStrategy` 決定 VM 的處置方式。配合 `MachineHealthCheck`（Cluster API）可實現更完善的自動修復。
:::

## VMware 功能對應實現程度

| VMware 功能 | KubeVirt 狀態 | 說明 |
|---|---|---|
| VM 建立與管理 | ✅ 完整支援 | CRD 原生支援 |
| 即時遷移 | ✅ 完整支援 | Live Migration |
| 快照與還原 | ✅ 完整支援 | VirtualMachineSnapshot |
| VM 克隆 | ✅ 完整支援 | VirtualMachineClone |
| CPU Hot Plug | ✅ 完整支援 | maxSockets 機制 |
| Memory Hot Plug | ✅ 完整支援 | maxGuest 機制 |
| Disk Hot Plug | ✅ 完整支援 | virtctl addvolume |
| GPU Passthrough | ✅ 完整支援 | 支援 NVIDIA vGPU 與直通 |
| SR-IOV | ✅ 完整支援 | 透過 SR-IOV CNI |
| VNC / 遠端控制台 | ✅ 完整支援 | virtctl vnc / virtctl console |
| USB Passthrough | ⚠️ 部分支援 | 有限的 USB 裝置支援 |
| Nested Virtualization | ⚠️ 部分支援 | 需要節點啟用 nested virt |
| Storage vMotion | ⚠️ 部分支援 | Volume Migration 開發中 |
| DRS 自動均衡 | 🔄 替代方案 | 使用 Descheduler |
| Fault Tolerance | ❌ 不支援 | 無同步複製機制 |
| vSAN | 🔄 替代方案 | 使用 Rook-Ceph / Longhorn |
| NSX 微分段 | 🔄 替代方案 | 使用 NetworkPolicy + Cilium |
| vRealize Automation | 🔄 替代方案 | 使用 Terraform / ArgoCD |

## 實際遷移步驟

### 步驟一：匯出 VMware VM 磁碟

```bash
# 方法 1：使用 govc（VMware CLI 工具）匯出
govc export.ovf -vm /DC/vm/my-vm ./export/

# 方法 2：使用 ovftool
ovftool vi://user:pass@vcenter/DC/vm/my-vm ./my-vm.ova

# 方法 3：從 VMDK 轉換為 qcow2
qemu-img convert -f vmdk -O qcow2 my-vm-disk1.vmdk my-vm-disk1.qcow2
```

### 步驟二：使用 CDI 匯入磁碟

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: imported-vm-disk
spec:
  source:
    # 方法 1：從 HTTP 匯入
    http:
      url: "https://storage.example.com/my-vm-disk1.qcow2"

    # 方法 2：從 S3 匯入
    # s3:
    #   url: "s3://bucket/my-vm-disk1.qcow2"
    #   secretRef: "s3-credentials"

    # 方法 3：從 Registry 匯入
    # registry:
    #   url: "docker://registry.example.com/vm-images/my-vm:v1"
  storage:
    accessModes:
      - ReadWriteMany
    resources:
      requests:
        storage: 50Gi
    storageClassName: ceph-block
```

```bash
# 方法 4：使用 virtctl 從本地上傳
virtctl image-upload dv imported-vm-disk \
  --size=50Gi \
  --image-path=./my-vm-disk1.qcow2 \
  --storage-class=ceph-block \
  --access-mode=ReadWriteMany \
  --uploadproxy-url=https://cdi-uploadproxy.cdi.svc
```

### 步驟三：建立 KubeVirt VM 定義

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: migrated-vm
  labels:
    app: migrated-vm
    origin: vmware
spec:
  running: true
  template:
    metadata:
      labels:
        app: migrated-vm
    spec:
      evictionStrategy: LiveMigrate
      domain:
        cpu:
          cores: 4
        memory:
          guest: 8Gi
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
          interfaces:
            - name: default
              masquerade: {}
          rng: {}
        features:
          acpi: {}
          smm:
            enabled: true
        firmware:
          bootloader:
            efi:
              secureBoot: true
      networks:
        - name: default
          pod: {}
      volumes:
        - name: rootdisk
          dataVolume:
            name: imported-vm-disk
```

### 步驟四：驗證與調整

```bash
# 確認 VM 啟動
kubectl get vm migrated-vm
kubectl get vmi migrated-vm

# 連線到 VM 主控台
virtctl console migrated-vm

# 安裝 QEMU Guest Agent（取代 VMware Tools）
# Ubuntu/Debian
sudo apt install qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# CentOS/RHEL
sudo yum install qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# 驗證 Guest Agent 運行
kubectl get vmi migrated-vm -o jsonpath='{.status.guestOSInfo}'
```

::: warning VirtIO 驅動程式
從 VMware 遷移的 VM 原本使用 VMXNET3 和 PVSCSI 驅動程式。遷移到 KubeVirt 後，需要改用 VirtIO 驅動程式以獲得最佳效能。

- **Linux**：大多數現代 Linux 發行版已內建 VirtIO 驅動
- **Windows**：需要額外安裝 [VirtIO 驅動程式](https://github.com/virtio-win/virtio-win-pkg-scripts)，建議在遷移前先在 VMware 環境中預先安裝
:::

## 心態轉換

### 從「GUI 操作」到「YAML 聲明式」

```
VMware 思維：                    KubeVirt 思維：
┌──────────────────┐            ┌──────────────────┐
│  打開 vSphere     │            │  撰寫 YAML       │
│  Client          │            │  （宣告期望狀態） │
│        ↓         │            │        ↓         │
│  點選選單操作      │            │  kubectl apply    │
│        ↓         │            │        ↓         │
│  等待任務完成      │            │  Controller 確保  │
│                  │            │  達到期望狀態      │
└──────────────────┘            └──────────────────┘
  命令式（Imperative）            聲明式（Declarative）
```

::: tip 聲明式的優勢
聲明式管理意味著您只需描述「要什麼」，而不需要指定「怎麼做」。Kubernetes 的控制器會持續確保實際狀態符合您的宣告。即使 VM 意外停止，控制器也會自動重新啟動它。
:::

### 從「單機管理」到「叢集編排」

- **VMware**：每台 ESXi 是獨立的管理單位，vCenter 是選用的附加層
- **KubeVirt**：叢集是基本管理單位，每個 Node 是叢集的一部分

### 從「儲存中心」到「容器原生」

- **VMware**：以 Datastore 為中心，VM 檔案存放在共享儲存上
- **KubeVirt**：以 PVC 為抽象層，底層儲存透過 CSI 驅動整合

### 從「網路 VLAN」到「CNI 覆蓋網路」

- **VMware**：依賴實體交換器 VLAN 劃分和 dvSwitch
- **KubeVirt**：預設使用覆蓋網路（Overlay），透過 Multus 支援直接 VLAN 接入

## 常見問題 FAQ

### Q1：KubeVirt 的效能比 VMware 差嗎？

不一定。使用 VirtIO 驅動、CPU pinning、HugePages 等最佳化後，KubeVirt 的效能可以非常接近甚至匹敵 VMware。關鍵在於正確的效能調校。

### Q2：KubeVirt 支援 Windows VM 嗎？

✅ 完整支援。KubeVirt 可以運行 Windows Server 和 Windows Desktop，支援 VirtIO 驅動程式、sysprep 自動化、以及 Hyper-V enlightenments 加速。

### Q3：如何處理 VMware 的授權？

遷移到 KubeVirt 後，不再需要 VMware 相關授權。KubeVirt 本身是 100% 開源的 Apache 2.0 授權。但請注意 Guest OS（如 Windows）仍需要相應的授權。

### Q4：可以逐步遷移嗎？還是必須一次全部搬？

完全支援逐步遷移。您可以先遷移非關鍵的工作負載進行驗證，確認穩定後再逐步遷移生產環境的 VM。

### Q5：Live Migration 的效能和 vMotion 比起來如何？

KubeVirt 的 Live Migration 基於 QEMU/libvirt 的遷移機制，支援 pre-copy 和 post-copy 模式。在大多數場景下，遷移時間和 vMotion 相當。大記憶體 VM 建議使用 post-copy 模式以減少遷移時間。

### Q6：KubeVirt 能取代所有 VMware 功能嗎？

大部分核心功能都有對應方案，但某些進階功能（如 Fault Tolerance 同步複製）目前沒有直接對應。請參考上方的功能對應表評估是否符合您的需求。

### Q7：如何選擇底層儲存方案？

常見選擇包括：
- **Rook-Ceph**：分散式儲存，支援 RWX，最推薦的方案
- **Longhorn**：輕量級分散式儲存，適合小規模環境
- **NFS**：簡單但效能有限
- **本地儲存（Local PV）**：最高效能，但不支援 Live Migration

### Q8：需要學 Kubernetes 才能用 KubeVirt 嗎？

是的，基本的 Kubernetes 知識是必要的。建議至少了解 Pod、Service、PVC、Namespace、RBAC 等核心概念。好消息是，您的 VMware 經驗中的許多概念（如資源池、儲存、網路）都能直接對應到 Kubernetes 中。

### Q9：有圖形化管理介面嗎？

有多種選擇：
- **OpenShift Console**：如果使用 OpenShift，內建完整的 VM 管理 UI
- **Rancher**：支援 KubeVirt VM 管理
- **Kubernetes Dashboard**：基本的資源查看
- **Headlamp**：支援 KubeVirt 的 Kubernetes Dashboard

### Q10：遷移過程中 VM 會停機嗎？

匯出 VMware VM 時通常需要關機（除非使用 CBT 增量備份）。匯入到 KubeVirt 後啟動 VM。因此，遷移過程中會有一段停機時間。建議在維護窗口期間進行遷移，並事先做好充分的測試。

### Q11：如何處理 VMware 的備份方案（如 Veeam）？

KubeVirt 環境中，可以使用以下方案替代：
- **Velero + CSI Snapshots**：Kubernetes 原生備份方案
- **Kasten K10**：企業級 Kubernetes 備份
- **Trilio**：支援 KubeVirt VM 備份
- **VirtualMachineSnapshot**：KubeVirt 原生快照功能

### Q12：多租戶隔離和 VMware 的 Resource Pool 比起來如何？

Kubernetes 提供了更細粒度的隔離機制：
- **Namespace**：邏輯隔離（類似 Resource Pool）
- **ResourceQuota**：資源配額限制
- **NetworkPolicy**：網路隔離
- **RBAC**：權限控制
- **PodSecurityAdmission**：安全策略

這些機制組合起來，可以實現比 VMware Resource Pool 更強的多租戶隔離。
