---
layout: doc
---

# NVIDIA OpenShell — 底層開源生態與隔離模型

::: tip 分析版本
本文件基於 commit [`d9908222`](https://github.com/NVIDIA/OpenShell/commit/d9908222f2b18adeb00227f8fbefcaabd7ebd7f0) 進行分析。
:::

::: info 相關章節
- 系統元件概覽請參閱 [系統架構](./architecture)
- 計算後端部署請參閱 [Kubernetes 整合](./k8s-integration)
- 策略與 Provider 機制請參閱 [核心功能分析](./core-features)
:::

## 底層開源整合全景

OpenShell 並非自行從零建構所有底層能力，而是**有策略地整合多個成熟開源專案**，形成一個多層次的安全沙箱棧。整體依賴可以拆成五個平面：

![OpenShell 底層開源生態整合全景圖](/diagrams/openshell/oss-integration-map.svg)

## 開源依賴清單（按功能分類）

### 核心語言與非同步框架

OpenShell 的 Gateway 與 Supervisor 以 **Rust** 實作，主要依賴以下開源 crate：

| 開源專案 | 角色 | 整合位置 |
|---------|------|---------|
| [tokio](https://tokio.rs/) | Rust 非同步執行時期（async runtime） | Gateway + Supervisor 全部 I/O |
| [tonic](https://github.com/hyperium/tonic) | Rust gRPC 框架（HTTP/2 + Protobuf） | CLI ↔ Gateway ↔ Supervisor 通訊 |
| [axum](https://github.com/tokio-rs/axum) | Rust HTTP 伺服器框架 | Gateway REST API endpoint |
| [rustls](https://github.com/rustls/rustls) | Pure Rust TLS 實作 | mTLS 雙向驗證通道 |
| [rcgen](https://github.com/rustls/rcgen) | Rust X.509 憑證產生 | PKI Init Job 自動產生 CA / Server / Client cert |

### 策略引擎

| 開源專案 | 角色 | 整合位置 |
|---------|------|---------|
| [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) | Rego 策略評估引擎 | Supervisor 的 Policy Proxy 核心 |
| [Rego 語言](https://www.openpolicyagent.org/docs/latest/policy-language/) | 宣告式策略語言 | YAML 策略轉換為 Rego 進行 Allow/Route/Deny 決策 |
| [Linux Seccomp BPF](https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html) | 系統呼叫過濾 | Process 策略：沙箱建立時鎖定的 syscall allowlist |

::: info OPA 在沙箱內的角色
每個沙箱的 Supervisor 內部嵌入一個 OPA 評估引擎（非獨立 Pod）。每次 Agent 發出對外 HTTP 請求時，Policy Proxy 會在本地呼叫 OPA 評估 Rego 策略，決定 Allow / Route / Deny，無需跨 Pod 通訊，延遲極低。
:::

### 持久化儲存

| 開源專案 | 角色 | 整合位置 |
|---------|------|---------|
| [SQLite](https://www.sqlite.org/) + [rusqlite](https://github.com/rusqlite/rusqlite) | 嵌入式關聯式資料庫 | Gateway 預設狀態儲存（沙箱記錄、策略、Provider） |
| [PostgreSQL](https://www.postgresql.org/) + [sqlx](https://github.com/launchbadis/sqlx) | 生產級關聯式資料庫 | HA 多副本 Gateway 場景的共享狀態後端 |
| [Bitnami PostgreSQL Helm chart](https://bitnami.com/stack/postgresql/helm) | 可選 Helm subchart | 輕量化部署，可選擇內建 PostgreSQL |

### 身份驗證與 PKI

| 開源專案 | 角色 | 整合位置 |
|---------|------|---------|
| [mTLS](https://grpc.io/docs/guides/auth/) | 雙向 TLS 驗證 | Gateway ↔ Supervisor session 驗證（強制，不可關閉） |
| [OIDC / JWT](https://openid.net/connect/) | OpenID Connect 使用者驗證 | Gateway 可整合 Keycloak、Entra ID、Okta 等 IdP |
| [cert-manager](https://cert-manager.io/) | Kubernetes 憑證自動管理 | 可選整合，替代 PKI Init Job，支援自動輪替 |

### 計算驅動依賴

| 開源專案 | Driver | 角色 |
|---------|--------|------|
| [Docker Engine](https://www.docker.com/) | Docker | 容器生命週期管理（UNIX socket API） |
| [containerd](https://containerd.io/) | Docker / K8s | 容器執行時期（CRI 標準實作） |
| [runc](https://github.com/opencontainers/runc) | Docker / K8s | OCI Runtime Spec 執行器，建立 Linux Namespace + Cgroup |
| [Podman](https://podman.io/) | Podman | Rootless 容器 + REST API |
| [crun](https://github.com/containers/crun) | Podman | C 語言 OCI Runtime，Podman 預設，rootless 友善 |
| [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | Kubernetes | K8s Driver 必要的 CRD + Controller（CNCF 上游） |
| [libkrun](https://github.com/containers/libkrun) | VM | Rust library，KVM-backed MicroVM，每沙箱一個 VM |
| [KVM](https://www.linux-kvm.org/) | VM | Linux 核心虛擬化，硬體輔助隔離基礎 |

### GPU 整合

| 開源專案 | 角色 | 整合位置 |
|---------|------|---------|
| [CDI（Container Device Interface）](https://github.com/cncf-tags/container-device-interface) | OCI 標準 GPU 裝置注入介面 | Docker / Podman GPU 支援的優先路徑 |
| [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit) | GPU 容器化注入工具鏈 | CDI 不可用時的 fallback（`--gpus all`） |
| [NVIDIA GPU Operator](https://github.com/NVIDIA/gpu-operator) | K8s GPU 資源管理 | K8s Driver GPU sandbox 的先決條件 |

---

## Container Runtime 詳解

### Runtime Chain 概覽

「Container Runtime」在技術棧上有高低層之分。OpenShell 對外暴露 Driver 抽象，但底層實際的執行鏈如下：

**Docker Driver（開發環境最常用）：**

```
openshell sandbox create
  ↓ Docker Engine REST API（UNIX socket /var/run/docker.sock）
  ↓ dockerd（Docker Daemon）
  ↓ containerd（High-level runtime，管理映像、快照、生命週期）
  ↓ containerd-shim-runc-v2（保持 containerd 與 container 解耦）
  ↓ runc（Low-level OCI Runtime，實際呼叫 Linux kernel API）
  ↓ clone(2) → Namespaces 建立
  ↓ cgroups v2 → 資源限制
  ↓ Seccomp + AppArmor/SELinux → syscall/MAC 控制
```

**Podman Driver（Rootless 場景）：**

```
openshell sandbox create
  ↓ Podman REST API（~/.local/share/containers/podman.sock）
  ↓ conmon（Container Monitor，管理生命週期）
  ↓ crun（OCI Runtime，C 語言實作，rootless 優化）
  ↓ newuidmap / newgidmap → User Namespace UID/GID 重映射
  ↓ clone(2) → Namespaces（含 User Namespace，無需 root）
  ↓ cgroups v2（rootless 路徑，透過 cgroup delegation）
```

**Kubernetes Driver（叢集環境）：**

```
openshell sandbox create
  ↓ K8s API Server（建立 Pod + Secret + PVC）
  ↓ kubelet（節點守護程序）
  ↓ CRI（Container Runtime Interface）
  ↓ containerd 或 CRI-O（高層 runtime）
  ↓ runc（預設 OCI runtime）
     或 kata-containers（可替換，提供更強 VM 級隔離）
  ↓ Linux Namespace + Cgroups v2 + Seccomp
```

**VM Driver（最高隔離）：**

```
openshell sandbox create
  ↓ libkrun Rust library（直接呼叫 KVM API）
  ↓ KVM（/dev/kvm — Linux 核心虛擬化模組）
  ↓ 建立 MicroVM（Guest Kernel + rootfs.ext4 + overlay.ext4）
  ↓ virtiofs（Host 目錄共享）/ vsock（虛擬網路）
  ↓ Guest Kernel 內執行 Supervisor + Agent
```

### Supervisor 在 Runtime 鏈中的位置

Supervisor 是 OpenShell 在**容器或 VM 內部**的安全邊界，它夾在 Container Runtime 與 Agent Process 之間：

```
┌─── Container / MicroVM ───────────────────────────┐
│                                                     │
│  openshell-supervisor  ← 由 OCI entrypoint 啟動    │
│    │                                                │
│    ├── Policy Proxy (localhost HTTPS proxy)         │
│    │     └── OPA 評估每條出站請求                    │
│    ├── Inference Router (inference.local)           │
│    │     └── 攔截 LLM API 呼叫，替換憑證轉發         │
│    └── fork() → Agent Process (claude / codex ...) │
│                  └── 以降低的 Linux Capabilities 執行│
│                                                     │
└─────────────────────────────────────────────────────┘
```

Supervisor 是 OCI entrypoint，具有完整的容器內視角。即使容器在 Kubernetes 上以非 root 執行，Supervisor 仍可攔截所有 Agent 的出站請求。

---

## 隔離層次與能力分析

![OpenShell 各 Driver 的 Container Runtime 鏈與隔離層次比較](/diagrams/openshell/runtime-isolation-levels.svg)

### 各 Driver 隔離層比較

| 隔離維度 | Docker | Podman Rootless | K8s (runc) | K8s + UserNS | VM (libkrun) |
|---------|--------|----------------|------------|--------------|-------------|
| **PID 命名空間** | ✅ 獨立 | ✅ 獨立 | ✅ 獨立（Pod） | ✅ 獨立 | ✅ Guest OS 完全獨立 |
| **Net 命名空間** | ✅ 獨立 | ✅ 獨立 | ✅ 獨立（Pod） | ✅ 獨立 | ✅ Virtual NIC（vsock） |
| **Mount 命名空間** | ✅ 獨立 | ✅ 獨立 | ✅ 獨立 | ✅ 獨立 | ✅ Guest rootfs |
| **User 命名空間** | ❌ 預設不啟用 | ✅ 預設啟用 | ❌ 預設不啟用 | ✅ K8s 1.33+ | ✅ Guest 為獨立 UID 空間 |
| **Cgroups v2** | ✅ CPU/Mem/Pids | ✅ CPU/Mem/Pids | ✅ 由 kubelet 管理 | ✅ | ✅ Guest OS 獨立 cgroup |
| **Seccomp** | ✅（可配置） | ✅（可配置） | ✅（PodSecurityContext） | ✅ | ✅ Guest kernel syscall 完全獨立 |
| **Capabilities** | ✅ Drop ALL 可選 | ✅ Rootless 預設低 | ✅ Drop ALL | ✅ Drop ALL | N/A（VM 無 capability 概念） |
| **Host Kernel 共享** | ✅ 共享 | ✅ 共享 | ✅ 共享 | ✅ 共享 | ❌ Guest 有獨立 Kernel |
| **網路策略** | OpenShell 軟體層 | OpenShell 軟體層 | K8s NetworkPolicy + 軟體層 | K8s NetworkPolicy + 軟體層 | OpenShell 軟體層（Guest 內） |
| **隔離強度** | ★★☆ | ★★★ | ★★★ | ★★★★ | ★★★★★ |

### 各隔離層能阻擋什麼？

#### 軟體策略層（OpenShell Supervisor / OPA）
- 阻擋 Agent 存取未授權的外部 API（HTTP/HTTPS 出站管控）
- 阻擋使用未授權的 LLM Provider / Model
- 憑證不落地（API Key 不進入容器檔案系統）

#### 容器層（Namespace + Cgroups + Seccomp）
- 阻擋程序逃逸至 Host PID 空間
- 限制 Agent 無法任意掛載 Host 目錄
- 限制記憶體與 CPU 用量，防止 DoS
- Seccomp：阻擋危險 syscall（ptrace、mount、reboot 等）
- Capabilities Drop：阻擋取得 NET_ADMIN、SYS_ADMIN 等高權限

#### User Namespace（Podman Rootless / K8s UserNamespace）
- 即使容器內 UID=0（root），Host 視角僅為非特權 UID
- 根本性地阻擋「容器逃逸後立即成為 Host root」
- 代價：部分需要真實 root 的操作（如 bind mount /proc）會失敗

#### VM 層（libkrun / KVM）
- Agent 的任何行為都在 Guest Kernel 內，無法直接影響 Host Kernel
- Guest Kernel 崩潰不影響 Host
- 記憶體隔離：KVM 使用 EPT/NPT 硬體頁表隔離，Guest 無法讀取 Host 記憶體
- 網路必須過 virtiofs / vsock，無法直接存取 Host 網路介面
- 代價：啟動延遲高（秒級 vs 毫秒級），磁碟 footprint 較大

### 可達到的最強隔離組合

對於最高安全需求的生產場景，最強的組合為：

```
K8s + Kata Containers（OCI Runtime 替換）
     + K8s UserNamespace（K8s 1.33+）
     + K8s NetworkPolicy（硬封鎖沙箱間流量）
     + OpenShell Supervisor（OPA 軟體層出站策略）
     + PodSecurityContext（Drop ALL + seccomp=RuntimeDefault）
     + PVC 儲存隔離（每個 Agent 獨立 Volume）
```

Kata Containers 在 K8s 中提供 VM 級隔離（KVM 或 QEMU），同時保持 K8s Pod 的管理介面，結合 OpenShell 的 OPA 策略層，形成硬體隔離 + 軟體策略的雙重保護。

::: warning VM Driver 的現實限制
VM Driver（libkrun）目前仍為實驗性功能（Experimental），不建議生產環境採用。若需要 VM 級隔離，在 Kubernetes 上使用 **Kata Containers** 作為 OCI Runtime 是更成熟的路徑。
:::

---

## kubernetes-sigs/agent-sandbox CRD — K8s Driver 的關鍵上游

OpenShell Kubernetes Driver 依賴 `kubernetes-sigs/agent-sandbox` 這個 CRD，這不是 NVIDIA 自己維護的，而是由 **Kubernetes 上游 SIG（Special Interest Group）** 主導的標準化 AI Agent 沙箱 API：

| 項目 | 說明 |
|------|------|
| **Repository** | [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) |
| **定位** | K8s 生態標準化的 Agent 沙箱 CRD，非 NVIDIA 專有 |
| **作用** | 為 K8s 提供 AI Agent 沙箱的抽象 API，讓多個 Agent 框架可共用基礎設施 |
| **安裝方式** | `kubectl apply -f .../manifest.yaml`（K8s Driver 的前置需求） |

這意味著 OpenShell 的 K8s 模式並不是「自己造輪子」，而是基於上游 SIG 的標準 API，未來的 K8s 版本有望將此 CRD 進一步標準化。

---

## 維運觀點：隔離選型決策矩陣

| 場景 | 建議 Driver / 設定 | 理由 |
|------|-------------------|------|
| 本機開發、快速驗證 | Docker | 最簡單，啟動快 |
| 單機 CI、多租戶輕度隔離 | Podman Rootless | User NS 預設啟用，無需 root |
| 叢集共享、中度安全需求 | K8s（runc） + NetworkPolicy | K8s 原生管理，資源調度彈性 |
| 叢集、高安全需求 | K8s + UserNamespace（1.33+） | UID 空間隔離，防止逃逸後即為 root |
| 叢集、最強隔離（如多租戶 SaaS） | K8s + Kata Containers | VM 級隔離，共享 Pod 介面 |
| 最高安全需求（研究 / 高敏感環境） | VM Driver（libkrun）—待穩定 | 完整 Guest Kernel，最強硬體隔離 |

::: tip 隔離不等於安全
容器 / VM 隔離處理的是**計算層逃逸**問題。OpenShell 的 Supervisor + OPA 策略層處理的是**應用層資料外洩**問題（未授權 API 呼叫、憑證外洩）。兩者互補，缺一不可。
:::
