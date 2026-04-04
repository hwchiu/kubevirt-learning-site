# KubeVirt 系統架構概述

KubeVirt 是一個基於 **Kubernetes 的虛擬機器管理擴充套件**，讓使用者可以在現有的 Kubernetes 叢集中，像管理容器一樣管理虛擬機器 (VM)。

## 設計理念

### 核心原則：擴展而非取代

KubeVirt 並不試圖取代 Kubernetes，而是**完全融入** Kubernetes 的生態系統。它透過以下三件事為叢集加入虛擬化能力：

1. **Custom Resource Definitions (CRD)** — 新增 VM 相關資源型別到 Kubernetes API
2. **Controllers** — 叢集級別的控制邏輯 (virt-controller)
3. **DaemonSet** — 節點級別的代理程序 (virt-handler)

### KubeVirt Razor（設計準則）

> *「如果某個功能對 Pod 也有用，我們就不應該只為 VM 實作它。」*

這個原則讓 KubeVirt 盡可能重用 Kubernetes 現有的基礎設施：
- 網路使用 CNI、Multus 而非自行實作
- 儲存使用 PVC、StorageClass 而非自行管理
- 調度使用 kube-scheduler 而非另起爐灶
- 安全模型與 Pod 保持一致

## 技術棧

```
┌─────────────────────────────────────┐
│  KubeVirt (虛擬化 API)               │  ← 本文重點
├─────────────────────────────────────┤
│  Orchestration (Kubernetes)          │  ← 調度、服務發現
├─────────────────────────────────────┤
│  Scheduling (Kubernetes Scheduler)   │  ← Pod/VM 排程
├─────────────────────────────────────┤
│  Container Runtime (containerd/CRI)  │  ← 容器執行環境
├─────────────────────────────────────┤
│  Operating System (Linux)            │  ← 宿主機 OS
├─────────────────────────────────────┤
│  Physical / Virtual Hardware         │  ← 實體或虛擬 CPU/記憶體
└─────────────────────────────────────┘
```

## 整體架構圖

```
                    ┌────────────────────────────────────────────────────┐
                    │              Kubernetes API Server                  │
                    │  (儲存所有 CRD：VM, VMI, Migration, Snapshot...)   │
                    └──────────┬───────────────────┬──────────────────────┘
                               │ Watch/Update       │ Watch/Update
                               ▼                    ▼
              ┌────────────────────┐    ┌──────────────────────┐
              │    virt-api        │    │   virt-controller     │
              │  (Deployment × N)  │    │  (Deployment × N)     │
              │  ● REST API 入口    │    │  ● VM/VMI 控制器      │
              │  ● Admission Webhook│   │  ● Migration 控制器   │
              │  ● Console/VNC 代理 │   │  ● Snapshot 控制器    │
              └────────┬───────────┘    └─────────┬────────────┘
                       │                           │ 建立 Pod
                       │                           ▼
                       │              ┌─────────────────────────────┐
                       │              │    virt-launcher Pod (×VMI)  │
                       │              │  ┌─────────────────────────┐ │
                       │              │  │  virt-launcher 程序      │ │
                       │              │  │  (接收命令、轉發指令)     │ │
                       │              │  ├─────────────────────────┤ │
                       │              │  │  libvirtd + QEMU         │ │
                       │              │  │  (實際執行 VM)            │ │
                       │              │  └─────────────────────────┘ │
                       │              └──────────────────────────────┘
                       │                           ▲
                       │                           │ Unix Socket 通訊
                       │              ┌────────────┴────────────┐
                       └─────────────→│     virt-handler         │
                                      │   (DaemonSet per Node)   │
                                      │  ● 同步 VMI 狀態          │
                                      │  ● 呼叫 virt-launcher     │
                                      │  ● 管理網路/儲存           │
                                      └─────────────────────────┘
                                           ● 每個節點一個實例
                                           ● HostPID / HostNetwork
```

## 五大核心元件

| 元件 | 部署型態 | 職責摘要 |
|------|---------|---------|
| **[virt-operator](/kubevirt/components/virt-operator)** | Deployment (≥2 副本) | 安裝與管理所有 KubeVirt 元件，監控 `KubeVirt` CR |
| **[virt-api](/kubevirt/components/virt-api)** | Deployment (≥2 副本) | HTTP/WebSocket API 入口，Admission Webhook，console/VNC 代理 |
| **[virt-controller](/kubevirt/components/virt-controller)** | Deployment (≥2 副本) | 叢集級 VM 生命週期管理，建立/刪除 virt-launcher Pod |
| **[virt-handler](/kubevirt/components/virt-handler)** | DaemonSet (每節點一個) | 節點代理，同步 VMI 與 libvirt domain，管理 migration |
| **[virt-launcher](/kubevirt/components/virt-launcher)** | Pod (每 VMI 一個) | 提供 cgroups/namespaces 隔離，執行 libvirtd + QEMU |

## 重要 CRD 資源

KubeVirt 為 Kubernetes 新增了以下 CRD：

### 核心資源

| CRD | 說明 |
|-----|------|
| `VirtualMachine` (VM) | **有狀態 VM** — 停止後資料保留，可重新啟動 |
| `VirtualMachineInstance` (VMI) | **執行中的 VM 實例** — 暫態，關機後消失 |
| `VirtualMachineInstanceReplicaSet` | VM 水平擴展 (類似 ReplicaSet) |
| `VirtualMachinePool` | 高階 VM 池管理 (類似 Deployment) |
| `VirtualMachineInstanceMigration` | Live Migration 請求物件 |

### 進階資源

| CRD | 說明 |
|-----|------|
| `VirtualMachineInstancetype` | CPU/記憶體規格模板 (namespace-scoped) |
| `VirtualMachineClusterInstancetype` | CPU/記憶體規格模板 (cluster-scoped) |
| `VirtualMachinePreference` | 設備偏好配置 |
| `VirtualMachineSnapshot` | VM 快照 |
| `VirtualMachineRestore` | VM 還原請求 |
| `VirtualMachineClone` | VM 克隆請求 |
| `VirtualMachineExport` | VM 磁碟匯出 |
| `VirtualMachineBackup` | VM 備份 (含增量備份) |
| `KubeVirt` | KubeVirt 安裝與設定 CR |

## 與原生 Kubernetes 的關係

```
Kubernetes 原生工作負載
    Pod ──── 由 kubelet 直接管理

KubeVirt 虛擬機工作負載
    VM ──→ VMI ──→ virt-launcher Pod ──→ libvirtd ──→ QEMU VM
           └── 由 virt-controller 建立 Pod
                   └── 由 virt-handler 透過 socket 管理
```

**設計要點：**
- VM 對 Kubernetes 來說就是一個 Pod (virt-launcher)
- Kubernetes 負責調度、網路、儲存的基礎
- KubeVirt 在 Pod 內部管理 VM 的具體執行
- 同一 namespace 可以同時存在 Pod 和 VM，使用相同的 NetworkPolicy、RBAC

## 資料流：以建立 VM 為例

```
使用者執行：kubectl apply -f my-vm.yaml
        │
        ▼
1. [virt-api]
   ├── Mutating Webhook：補齊預設值
   ├── Validating Webhook：驗證 spec
   └── 寫入 VirtualMachine CR 到 API Server

        │ watch
        ▼
2. [virt-controller - VM 控制器]
   └── 建立 VirtualMachineInstance (VMI) CR

        │ watch
        ▼
3. [virt-controller - VMI 控制器]
   └── 建立 virt-launcher Pod (包含 libvirt)

        │ Kubernetes 調度
        ▼
4. [kube-scheduler]
   └── 選定節點，kubelet 拉起 Pod

        │ Pod Running
        ▼
5. [virt-controller]
   └── 更新 VMI.spec.nodeName = 選定節點

        │ watch (nodeName 改變)
        ▼
6. [virt-handler (在目標節點上)]
   ├── 透過 Unix socket 呼叫 virt-launcher
   ├── 將 VMI spec 轉換為 libvirt domain XML
   └── 呼叫 libvirtd 啟動 QEMU 程序

        │
        ▼
7. [QEMU VM 開始執行]
   VM 狀態更新：Pending → Scheduling → Scheduled → Running
```

## 編排 vs 協作模式

KubeVirt 使用**協作 (Choreography)** 模式，而非編排 (Orchestration) 模式：

- 每個元件**各自觀察**狀態並採取行動
- 沒有中央指揮官，而是透過 **VMI CR 作為共享狀態**
- 這讓系統更具彈性與可擴展性
- 類似於 Kubernetes 本身的 level-triggered 協調機制

::: tip 類比
這就像交通規則 (協作)，而非由交通管制員指揮每輛車 (編排)。每個元件都知道自己的規則，並根據現狀自主行動。
:::

## 原始碼位置參考

```
kubevirt/
├── cmd/                    # 各元件的 main.go 入口
│   ├── virt-api/
│   ├── virt-controller/
│   ├── virt-handler/
│   ├── virt-launcher/
│   └── virt-operator/
├── pkg/                    # 各元件的核心邏輯
│   ├── virt-api/
│   ├── virt-controller/
│   ├── virt-handler/
│   ├── virt-launcher/
│   └── virt-operator/
├── staging/src/kubevirt.io/
│   └── api/                # 所有 CRD 型別定義
│       ├── core/v1/        # VM, VMI, KubeVirt 等
│       ├── instancetype/   # Instancetype, Preference
│       ├── snapshot/       # VirtualMachineSnapshot
│       ├── clone/          # VirtualMachineClone
│       ├── export/         # VirtualMachineExport
│       └── backup/         # VirtualMachineBackup
└── docs/                   # 官方文件
```
