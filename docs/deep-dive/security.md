# 安全架構 — KubeVirt 的安全機制

::: info 本章導讀
安全性是虛擬化平台的核心關注點。KubeVirt 繼承了 Kubernetes 的安全模型，並在此基礎上增加了虛擬化特有的安全機制。本章將深入探討 KubeVirt 的安全架構，從憑證管理到機密運算，提供完整的安全指南。
:::

## 安全架構總覽

### 架構設計原則

KubeVirt 的安全架構遵循以下核心原則：

```
┌──────────────────────────────────────────────────────────┐
│                    Kubernetes API Server                  │
│                   （RBAC + Admission Control）            │
│                          ↕ mTLS                          │
├──────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌───────────────┐    ┌──────────────┐  │
│  │ virt-api │←──→│virt-controller│←──→│ virt-handler  │  │
│  │          │    │               │    │  (DaemonSet)  │  │
│  │ (無狀態) │    │  (無狀態)     │    │  (每節點一個) │  │
│  └──────────┘    └───────────────┘    └──────┬───────┘  │
│                          mTLS ↕              ↕ mTLS     │
│                                      ┌──────────────┐   │
│                                      │virt-launcher  │   │
│                                      │ (每 VM 一個)  │   │
│                                      │ ┌──────────┐  │   │
│                                      │ │  libvirt │  │   │
│                                      │ │  QEMU    │  │   │
│                                      │ └──────────┘  │   │
│                                      └──────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 最小權限原則

**virt-launcher Pod 的安全設計：**

KubeVirt 的一個關鍵安全設計是 virt-launcher Pod **不以特權模式運行**。這與許多傳統虛擬化方案不同：

```yaml
# virt-launcher Pod 的安全上下文（KubeVirt 自動設定）
securityContext:
  runAsNonRoot: true
  runAsUser: 107       # qemu 使用者
  runAsGroup: 107
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE  # 僅添加最小必要的 capability
  seccompProfile:
    type: RuntimeDefault
```

::: tip 為什麼非特權很重要？
如果 VM 被攻破（Guest Escape），攻擊者也只能獲得 virt-launcher 的非特權存取，無法影響節點或其他 VM。這是深度防禦策略的關鍵層。
:::

### 兩階段網路設定的安全意義

KubeVirt 使用兩階段網路設定來限制網路操作的權限需求：

1. **第一階段（virt-handler，特權 DaemonSet）**：在節點層級建立網路橋接和 TAP 裝置
2. **第二階段（virt-launcher，非特權 Pod）**：將已建立的 TAP 裝置連接到 VM

```
階段 1 (virt-handler, 特權)          階段 2 (virt-launcher, 非特權)
┌─────────────────────────┐        ┌─────────────────────────┐
│ 建立 bridge             │        │ 連接 TAP → QEMU        │
│ 建立 TAP device         │───────→│ 啟動 VM                 │
│ 設定 iptables 規則      │        │ 不需要網路管理權限      │
│ 需要 CAP_NET_ADMIN      │        │                         │
└─────────────────────────┘        └─────────────────────────┘
```

這種設計確保了 virt-launcher 不需要任何網路管理權限，大幅降低了攻擊面。

### mTLS 通訊

所有 KubeVirt 元件之間的通訊都使用 mutual TLS（雙向 TLS）加密：

- **virt-api ↔ Kubernetes API Server**：透過 Kubernetes 內建的 TLS
- **virt-controller ↔ virt-handler**：自簽 mTLS 憑證
- **virt-handler ↔ virt-launcher**：自簽 mTLS 憑證
- **Console/VNC Proxy**：透過 mTLS 加密的 WebSocket 連線

## 憑證管理

### TLS 憑證自動輪換

KubeVirt 使用自行管理的 Certificate Authority（CA）來簽發內部 TLS 憑證，並自動處理憑證的輪換：

```bash
# 查看目前的 CA 和憑證
kubectl get secrets -n kubevirt | grep cert

# 典型的憑證 Secret 列表：
# kubevirt-ca                    — CA 憑證
# kubevirt-virt-api-certs        — virt-api 的伺服器憑證
# kubevirt-virt-controller-certs — virt-controller 的客戶端憑證
# kubevirt-virt-handler-certs    — virt-handler 的客戶端/伺服器憑證
# kubevirt-export-proxy-certs    — export-proxy 的伺服器憑證
```

```bash
# 檢查憑證到期時間
kubectl get secret kubevirt-virt-api-certs -n kubevirt -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -noout -dates

# 典型輸出：
# notBefore=Jan  1 00:00:00 2024 GMT
# notAfter=Jan  1 00:00:00 2025 GMT
```

**憑證輪換機制：**

```yaml
# 在 KubeVirt CR 中配置憑證輪換
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  certificateRotationStrategy:
    selfSigned:
      caRotateInterval: 48h    # CA 輪換間隔（預設 48 小時前更新）
      certRotateInterval: 24h  # 憑證輪換間隔（預設 24 小時前更新）
      caOverlapInterval: 8h    # CA 重疊期（新舊 CA 共存）
```

::: info 憑證輪換過程
1. virt-operator 監控所有憑證的到期時間
2. 在到期前（根據設定的間隔）自動生成新憑證
3. 新憑證被注入到對應的 Secret 中
4. 各元件透過 Secret 的 watch 機制自動載入新憑證
5. 在 CA 輪換期間，新舊 CA 同時有效（overlap period），確保零停機
:::

### 各元件間的 mTLS 通訊

```
┌──────────┐     mTLS      ┌───────────────┐     mTLS      ┌──────────────┐
│ virt-api │ ←────────────→ │virt-controller│ ←────────────→ │ virt-handler  │
│          │   server cert  │               │  client cert   │              │
│          │   + CA verify  │               │  + CA verify   │              │
└──────────┘                └───────────────┘                └──────┬───────┘
                                                                    │ mTLS
                                                              ┌─────▼────────┐
                                                              │virt-launcher  │
                                                              │  client cert  │
                                                              └──────────────┘
```

每個元件都同時驗證對方的憑證是否由受信任的 CA 簽發，實現雙向身份驗證。

## RBAC（Role-Based Access Control）

### KubeVirt 定義的 ClusterRole

KubeVirt 安裝時會自動建立多個 ClusterRole：

```bash
# 查看 KubeVirt 相關的 ClusterRole
kubectl get clusterrole | grep kubevirt
```

| ClusterRole | 用途 | 權限範圍 |
|---|---|---|
| `kubevirt.io:admin` | VM 完整管理 | VM CRUD + 遷移 + 快照 + Console |
| `kubevirt.io:edit` | VM 編輯 | VM CRUD + Console |
| `kubevirt.io:view` | VM 唯讀查看 | VM / VMI 讀取 |
| `kubevirt.io:default` | 最小權限 | 基本的 VMI 子資源存取 |

### VM 操作所需的最小權限

```yaml
# 開發者角色：可以管理 VM，但不能變更叢集設定
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: vm-developer
  namespace: dev-team
rules:
  # VM 管理
  - apiGroups: ["kubevirt.io"]
    resources: ["virtualmachines"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: ["kubevirt.io"]
    resources: ["virtualmachineinstances"]
    verbs: ["get", "list", "watch"]
  # Console 和 VNC 存取
  - apiGroups: ["subresources.kubevirt.io"]
    resources: ["virtualmachineinstances/console", "virtualmachineinstances/vnc"]
    verbs: ["get"]
  # 啟動/停止操作
  - apiGroups: ["subresources.kubevirt.io"]
    resources: ["virtualmachines/start", "virtualmachines/stop", "virtualmachines/restart"]
    verbs: ["update"]
  # DataVolume（磁碟匯入）
  - apiGroups: ["cdi.kubevirt.io"]
    resources: ["datavolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  # PVC 管理
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "create", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: vm-developer-binding
  namespace: dev-team
subjects:
  - kind: User
    name: developer@example.com
roleRef:
  kind: Role
  name: vm-developer
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# 維運角色：可以遷移 VM 和查看所有 Namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: vm-operator
rules:
  - apiGroups: ["kubevirt.io"]
    resources: ["virtualmachines", "virtualmachineinstances"]
    verbs: ["get", "list", "watch", "update", "patch"]
  - apiGroups: ["kubevirt.io"]
    resources: ["virtualmachineinstancemigrations"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: ["subresources.kubevirt.io"]
    resources: ["virtualmachines/start", "virtualmachines/stop", "virtualmachines/restart", "virtualmachines/migrate"]
    verbs: ["update"]
```

### 多租戶配置建議

```yaml
# 為每個租戶建立 Namespace 和資源配額
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-alpha
  labels:
    tenant: alpha
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: vm-quota
  namespace: tenant-alpha
spec:
  hard:
    requests.cpu: "32"
    requests.memory: 64Gi
    limits.cpu: "64"
    limits.memory: 128Gi
    persistentvolumeclaims: "20"
    requests.storage: 500Gi
    # 限制 VM 數量（透過 count quota）
    count/virtualmachines.kubevirt.io: "10"
---
# NetworkPolicy 隔離租戶間的網路流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tenant-isolation
  namespace: tenant-alpha
spec:
  podSelector: {}  # 套用到 namespace 中所有 Pod（包括 virt-launcher）
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              tenant: alpha  # 僅允許同租戶的流量
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              tenant: alpha
    - to:                      # 允許 DNS 查詢
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
```

::: warning 多租戶安全注意事項
Kubernetes 的 Namespace 隔離是「軟」隔離，不等同於完全的安全邊界。對於需要強隔離的場景，建議搭配：
1. **NetworkPolicy** 嚴格限制網路流量
2. **PodSecurityAdmission** 強制執行安全策略
3. **ResourceQuota** 防止資源耗盡攻擊
4. **Node Affinity / Taints** 實現物理層級的租戶隔離
:::

## SELinux

### virt-launcher Pod 的 SELinux Context

在啟用 SELinux 的環境中（如 RHEL、CentOS、Fedora），KubeVirt 為 virt-launcher 設定特定的 SELinux context：

```bash
# 查看 virt-launcher 的 SELinux context
kubectl exec virt-launcher-my-vm-xxxxx -- id -Z
# 典型輸出：system_u:system_r:container_t:s0:c1,c2

# 查看 QEMU 進程的 SELinux context
kubectl exec virt-launcher-my-vm-xxxxx -- ps -eZ | grep qemu
```

```yaml
# KubeVirt 自動設定的 SELinux label
# 每個 VM 獲得唯一的 MCS（Multi-Category Security）label
# 例如：s0:c1,c2
# 這確保不同 VM 的 QEMU 進程無法存取彼此的資源
```

### Live Migration 時的 SELinux Level Matching

```
源端 VM (s0:c1,c2)  ──遷移──→  目標端 VM (s0:c1,c2)
                                 ↑
                          SELinux level 必須匹配
                          否則 QEMU 無法存取磁碟
```

::: info SELinux 與遷移
Live Migration 時，KubeVirt 確保目標端的 virt-launcher 使用與源端相同的 SELinux MCS label。這是透過在遷移前將源端的 SELinux label 傳遞給目標端來實現的。如果 label 不匹配，QEMU 將無法存取共享儲存上的磁碟映像。
:::

### 自定義 SELinux Policy

```bash
# 如果需要自定義 SELinux policy（例如允許 QEMU 存取特殊裝置）

# 1. 建立自定義 policy module
cat > kubevirt-custom.te << 'EOF'
module kubevirt-custom 1.0;

require {
    type container_t;
    type device_t;
    class chr_file { open read write ioctl };
}

# 允許 container_t 存取特定裝置
allow container_t device_t:chr_file { open read write ioctl };
EOF

# 2. 編譯並安裝
checkmodule -M -m -o kubevirt-custom.mod kubevirt-custom.te
semodule_package -o kubevirt-custom.pp -m kubevirt-custom.mod
semodule -i kubevirt-custom.pp
```

## Seccomp

### 預設 Seccomp Profile

KubeVirt 使用 Kubernetes 的 RuntimeDefault Seccomp profile 來限制 virt-launcher 可以使用的系統呼叫：

```yaml
# virt-launcher 的 Seccomp 設定
securityContext:
  seccompProfile:
    type: RuntimeDefault  # 使用容器運行時的預設 profile
```

### 自定義 Seccomp Profile

對於需要更嚴格限制的場景，可以建立自定義的 Seccomp profile：

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "archMap": [
    {
      "architecture": "SCMP_ARCH_X86_64",
      "subArchitectures": ["SCMP_ARCH_X86", "SCMP_ARCH_X32"]
    }
  ],
  "syscalls": [
    {
      "names": [
        "accept4", "bind", "clone", "close", "connect",
        "dup", "dup2", "epoll_create1", "epoll_ctl",
        "epoll_wait", "eventfd2", "execve", "exit",
        "exit_group", "fcntl", "fstat", "futex",
        "getpid", "ioctl", "listen", "mmap", "mprotect",
        "munmap", "open", "openat", "pipe2", "poll",
        "read", "recvfrom", "recvmsg", "rt_sigaction",
        "rt_sigprocmask", "sendmsg", "sendto", "set_robust_list",
        "setsockopt", "socket", "stat", "write", "writev"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

```yaml
# 在 KubeVirt CR 中配置自定義 Seccomp
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  configuration:
    seccompConfiguration:
      virtualMachineInstanceProfile:
        customProfile:
          localhostProfile: "kubevirt/virt-launcher.json"
```

::: warning Seccomp 配置注意
過於嚴格的 Seccomp profile 可能導致 QEMU 無法正常運行。建議先在測試環境中驗證自定義 profile，確認所有 VM 功能正常後再部署到生產環境。使用 `strace` 工具可以幫助識別 QEMU 需要的系統呼叫。
:::

## 機密運算（Confidential Computing）

### AMD SEV（Secure Encrypted Virtualization）

**原理：** AMD SEV 使用 AES-128 硬體加密引擎對 VM 的記憶體進行即時加密。每個 VM 使用不同的加密金鑰，確保即使 Host OS 或 Hypervisor 被攻破，也無法讀取 VM 的記憶體內容。

```
┌─────────────────────────────────────────────────────┐
│                    Hardware                           │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ VM 1 記憶體   │  │ VM 2 記憶體   │                 │
│  │ Key: K1      │  │ Key: K2      │                 │
│  │ 🔒 加密      │  │ 🔒 加密      │                 │
│  └──────────────┘  └──────────────┘                 │
│           ↕ AES-128 硬體加密引擎 ↕                    │
│  ┌──────────────────────────────────────────────┐   │
│  │              物理記憶體                        │   │
│  │  [密文][密文][密文][密文][密文][密文]           │   │
│  └──────────────────────────────────────────────┘   │
│  Host OS / Hypervisor 只看到密文，無法解密           │
└─────────────────────────────────────────────────────┘
```

**配置方式：**

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: sev-vm
spec:
  template:
    spec:
      domain:
        launchSecurity:
          sev:
            policy:
              encryptedState: false  # SEV 基本模式
        firmware:
          bootloader:
            efi:
              secureBoot: false     # SEV 不支援 Secure Boot
        memory:
          guest: 4Gi
        devices:
          autoattachMemBalloon: false  # SEV 不支援 balloon
```

```bash
# 確認節點支援 SEV
kubectl get node <node> -o jsonpath='{.status.allocatable}' | grep sev

# 或在節點上直接檢查
dmesg | grep SEV
cat /sys/module/kvm_amd/parameters/sev
# 輸出 Y 表示已啟用
```

::: warning AMD SEV 的限制
- **不支援 Live Migration**（基本 SEV 模式）
- **不支援 Memory Balloon**
- **不支援 Memory Hotplug**
- **不支援 Snapshot**（記憶體部分）
- 需要 AMD EPYC 或更新的處理器
- 啟用 SEV 後效能可能降低 **2-6%**（記憶體加密開銷）
- 每個系統的 SEV 客體數量有上限（ASIDs 數量限制）
:::

### AMD SEV-SNP（SEV Secure Nested Paging）

**原理：** SEV-SNP 是 SEV 的進階版本，在記憶體加密的基礎上增加了：
- **完整性保護**：防止記憶體頁面被重放或替換
- **遠端認證（Attestation）**：允許 VM 向第三方證明其運行在可信的硬體和軟體環境上

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: sev-snp-vm
spec:
  template:
    spec:
      domain:
        launchSecurity:
          sev:
            policy:
              encryptedState: true  # SEV-ES（加密狀態）
            attestation: {}         # 啟用遠端認證
        firmware:
          bootloader:
            efi: {}
        memory:
          guest: 8Gi
        devices:
          autoattachMemBalloon: false
```

::: info SEV-SNP 的認證流程
1. VM 啟動時，AMD 安全處理器生成 Attestation Report
2. Report 包含 VM 的度量值（Measurement）、平台資訊等
3. 第三方可透過 AMD 的公鑰驗證 Report 的真實性
4. 確認 VM 運行在真正的 AMD SEV-SNP 硬體上，且啟動映像未被篡改
:::

### Intel TDX（Trust Domain Extensions）

**原理：** Intel TDX 建立一個隔離的「Trust Domain」（TD），提供：
- **記憶體加密**：使用 AES-128-XTS 全記憶體加密
- **CPU 狀態保護**：TD 內的 CPU 暫存器對 Host 不可見
- **遠端認證**：基於 Intel SGX 的認證架構

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: tdx-vm
spec:
  template:
    spec:
      domain:
        launchSecurity:
          tdx: {}
        firmware:
          bootloader:
            efi: {}
        memory:
          guest: 8Gi
        devices:
          autoattachMemBalloon: false
```

```bash
# 確認節點支援 TDX
dmesg | grep -i tdx
cat /sys/module/kvm_intel/parameters/tdx
```

::: danger TDX 支援狀態
Intel TDX 在 KubeVirt 中的支援仍處於早期階段。在生產環境中使用前，請確認：
1. KubeVirt 版本支援 TDX
2. 硬體為支援 TDX 的 Intel Xeon（4th Gen Sapphire Rapids 或更新）
3. BIOS/UEFI 已啟用 TDX
4. Host Kernel 版本支援 TDX
:::

### LaunchSecurity API 說明

KubeVirt 透過統一的 `launchSecurity` API 支援不同的機密運算技術：

```yaml
# LaunchSecurity API 結構
spec:
  domain:
    launchSecurity:
      # AMD SEV
      sev:
        policy:
          encryptedState: true/false  # SEV-ES
        attestation: {}               # 遠端認證

      # Intel TDX
      tdx: {}

      # 未來可能支援更多技術
      # ARM CCA (Confidential Compute Architecture)
      # etc.
```

## 網路安全

### NetworkPolicy 與 VM

NetworkPolicy 對 KubeVirt VM 的效果等同於對普通 Pod 的效果，因為每個 VM 都運行在一個 virt-launcher Pod 中：

```yaml
# 限制 VM 僅能被特定來源存取
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vm-access-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      kubevirt.io/domain: database-vm  # 選擇特定 VM
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: web-server      # 僅允許 web-server 存取
      ports:
        - port: 5432               # 僅允許 PostgreSQL 埠口
          protocol: TCP
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - port: 53
          protocol: UDP
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8      # 允許內部網路
```

### 加密遷移流量

Live Migration 期間，VM 的記憶體內容在網路上傳輸。為了防止竊聽，應該加密遷移流量：

```yaml
# 在 KubeVirt CR 中啟用遷移加密
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  configuration:
    migrations:
      disableTLS: false  # 確保 TLS 啟用（預設已啟用）
```

::: tip 遷移安全性
KubeVirt 預設使用 TLS 加密遷移流量。這確保了 VM 的記憶體內容在傳輸過程中不會被竊聽。在安全敏感的環境中，確認 `disableTLS` 設定為 `false`（預設值）。
:::

### Pod-to-VM 網路隔離

```yaml
# 使用 Cilium 的 L7 NetworkPolicy 進行更細粒度的控制
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: vm-l7-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      kubevirt.io/domain: web-vm
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: load-balancer
      toPorts:
        - ports:
            - port: "443"
              protocol: TCP
          rules:
            http:
              - method: "GET"
                path: "/api/.*"
```

## 映像安全

### ContainerDisk 簽名驗證

ContainerDisk 本質上是 OCI 映像，可以利用容器映像的安全機制：

```bash
# 使用 cosign 簽名 VM 映像
cosign sign --key cosign.key registry.example.com/vm-images/ubuntu:22.04

# 驗證簽名
cosign verify --key cosign.pub registry.example.com/vm-images/ubuntu:22.04
```

```yaml
# 搭配 Kyverno 或 OPA Gatekeeper 強制執行映像簽名驗證
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-vm-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-containerdisk-signature
      match:
        resources:
          kinds:
            - kubevirt.io/v1/VirtualMachine
      verifyImages:
        - imageReferences:
            - "registry.example.com/vm-images/*"
          attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      ...
                      -----END PUBLIC KEY-----
```

### DataVolume 來源驗證

```yaml
# 限制 DataVolume 只能從受信任的來源匯入
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-dv-sources
spec:
  validationFailureAction: Enforce
  rules:
    - name: restrict-http-sources
      match:
        resources:
          kinds:
            - cdi.kubevirt.io/v1beta1/DataVolume
      validate:
        message: "DataVolume 來源 URL 必須來自受信任的網域"
        pattern:
          spec:
            source:
              http:
                url: "https://trusted-storage.example.com/*"
```

### 映像掃描建議

```bash
# 使用 Trivy 掃描 ContainerDisk 映像
trivy image registry.example.com/vm-images/ubuntu:22.04

# 使用 Grype 掃描
grype registry.example.com/vm-images/ubuntu:22.04

# 整合到 CI/CD pipeline
# Jenkinsfile / GitHub Actions 中在推送映像前執行掃描
```

::: tip 映像安全最佳實踐
1. **使用私有 Registry**（如 Harbor）集中管理 VM 映像
2. **啟用映像簽名**和驗證
3. **定期掃描**映像中的漏洞
4. **固定映像版本**（使用 SHA digest 而非 tag）
5. **最小化映像**：僅包含必要的元件
:::

## 最佳實踐

### 多租戶環境安全配置

```yaml
# 完整的多租戶安全配置範例

# 1. Namespace 隔離
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-secure
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
---
# 2. 資源配額
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: tenant-secure
spec:
  hard:
    requests.cpu: "16"
    requests.memory: 32Gi
    persistentvolumeclaims: "10"
    count/virtualmachines.kubevirt.io: "5"
---
# 3. LimitRange（預設資源限制）
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-limits
  namespace: tenant-secure
spec:
  limits:
    - type: Container
      defaultRequest:
        cpu: "500m"
        memory: "512Mi"
      default:
        cpu: "2"
        memory: "4Gi"
---
# 4. NetworkPolicy（預設拒絕所有）
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: tenant-secure
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
# 5. 允許必要的通訊
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-and-internal
  namespace: tenant-secure
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
    - to:
        - podSelector: {}   # 允許 namespace 內部通訊
```

### 生產環境安全 Checklist

::: danger 生產環境部署前必須確認
以下 checklist 涵蓋 KubeVirt 生產環境的關鍵安全項目：
:::

**基礎設施層：**

- [ ] ✅ Kubernetes API Server 啟用 RBAC
- [ ] ✅ etcd 加密（encryption at rest）
- [ ] ✅ 節點作業系統已加固（CIS Benchmark）
- [ ] ✅ 節點已啟用 SELinux 或 AppArmor
- [ ] ✅ 節點的 SSH 存取受限

**KubeVirt 層：**

- [ ] ✅ KubeVirt 版本為最新的穩定版
- [ ] ✅ mTLS 憑證正常輪換（確認 `disableTLS: false`）
- [ ] ✅ 已配置適當的 RBAC（最小權限原則）
- [ ] ✅ 非必要的 Feature Gates 未啟用
- [ ] ✅ virt-launcher 的 Seccomp profile 已配置

**VM 層：**

- [ ] ✅ ContainerDisk 映像已簽名
- [ ] ✅ DataVolume 來源受限於受信任的網域
- [ ] ✅ VM 映像已通過漏洞掃描
- [ ] ✅ Guest OS 已安裝最新的安全更新
- [ ] ✅ Guest Agent 已安裝（用於安全的 freeze/thaw 操作）

**網路層：**

- [ ] ✅ NetworkPolicy 已部署（預設拒絕所有）
- [ ] ✅ 遷移流量 TLS 加密已啟用
- [ ] ✅ 管理網路與資料網路分離（若使用 Multus）
- [ ] ✅ Ingress 流量透過 WAF 或 API Gateway 過濾

**監控與稽核：**

- [ ] ✅ Kubernetes Audit Logging 已啟用
- [ ] ✅ Prometheus 監控已部署並設定告警
- [ ] ✅ 日誌集中收集（ELK / Loki）
- [ ] ✅ 定期安全掃描排程已設定

```bash
# 快速安全狀態檢查腳本
echo "=== KubeVirt 安全狀態檢查 ==="

echo "1. 檢查 mTLS 狀態..."
kubectl get kubevirt -n kubevirt -o jsonpath='{.items[0].spec.configuration.tlsConfiguration}' 2>/dev/null || echo "使用預設 TLS 配置（安全）"

echo "2. 檢查憑證到期..."
kubectl get secret kubevirt-ca -n kubevirt -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -noout -enddate

echo "3. 檢查 RBAC..."
kubectl get clusterrolebinding | grep kubevirt

echo "4. 檢查 NetworkPolicy..."
kubectl get networkpolicy -A | grep -v "^NAMESPACE"

echo "5. 檢查 Feature Gates..."
kubectl get kubevirt -n kubevirt -o jsonpath='{.items[0].spec.configuration.developerConfiguration.featureGates}'

echo ""
echo "=== 檢查完成 ==="
```
