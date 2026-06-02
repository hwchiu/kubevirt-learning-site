---
layout: doc
---

# NVIDIA OpenShell — 系統架構

::: tip 分析版本
本文件基於 commit [`d9908222`](https://github.com/NVIDIA/OpenShell/commit/d9908222f2b18adeb00227f8fbefcaabd7ebd7f0) 進行分析。
:::

::: info 相關章節
- 專案簡介與總覽請參閱 [專案總覽](./index)
- 沙箱管理、策略系統與 Provider 請參閱 [核心功能分析](./core-features)
- Kubernetes 叢集部署請參閱 [Kubernetes 整合](./k8s-integration)
:::

## 整體架構

OpenShell 的架構圍繞三個穩定的執行時元件：**CLI**、**Gateway** 與 **Supervisor**，搭配底層計算驅動（Compute Driver）支援多種執行環境。

```
┌─────────────────────────────────────────────┐
│              使用者介面層                      │
│   CLI ─── SDK ─── TUI（Terminal UI）         │
└───────────────────┬─────────────────────────┘
                    │ gRPC / HTTP
┌───────────────────▼─────────────────────────┐
│                控制平面（Gateway）              │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │  Compute  │ │Credentials│ │   Identity  │  │
│  │ Subsystem │ │ Subsystem │ │  Subsystem  │  │
│  └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
│       │ Compute    │ Creds         │ OIDC     │
│       │ Driver     │ Driver        │ / mTLS   │
└───────┼────────────┼───────────────┼──────────┘
        ▼            ▼               ▼
   Docker/Podman  Keychain/       mTLS/OIDC/
   K8s / VM       Vault/K8s       Local
                  Secrets
        │
        ▼ 佈建工作負載
┌───────────────────────────────────────────┐
│              沙箱資料平面                    │
│  ┌──────────────────────────────────────┐ │
│  │              Supervisor              │ │
│  │  ┌────────────┐  ┌────────────────┐  │ │
│  │  │Policy Proxy│  │Inference Router│  │ │
│  │  │  (Egress)  │  │  (inference.   │  │ │
│  │  │            │  │   local)       │  │ │
│  │  └─────┬──────┘  └───────┬────────┘  │ │
│  │        │ OPA Engine       │           │ │
│  │  ┌─────▼──────────────────▼────────┐  │ │
│  │  │       受限 Agent 程序             │  │ │
│  │  └────────────────────────────────┘  │ │
│  └──────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

## 核心元件詳解

### Gateway（控制平面）

Gateway 是 OpenShell 的認證控制平面，擁有：

| 職責 | 說明 |
|------|------|
| **API 伺服器** | gRPC / HTTP 端點，供 CLI、SDK 與 Supervisor 呼叫 |
| **沙箱生命週期** | 建立、刪除、監視、協調沙箱狀態轉換 |
| **持久化狀態** | 沙箱記錄、策略版本、Provider、推理配置（SQLite 或 PostgreSQL） |
| **策略分發** | 將策略、設定與憑證交付給各沙箱的 Supervisor |
| **Relay 協調** | 管理沙箱 SSH 連線的 Relay 中繼通道 |
| **身份驗證** | 支援 mTLS 與 OIDC（Keycloak、Entra ID、Okta 等） |

### Supervisor（沙箱安全邊界）

Supervisor 執行於每個沙箱工作負載內，是本地安全邊界的核心：

| 職責 | 說明 |
|------|------|
| **程序隔離** | 以受限子程序啟動 Agent，降低程序權限 |
| **Policy Proxy** | 攔截所有 Agent 對外流量，透過 OPA 策略引擎評估 |
| **Inference Router** | 將 `https://inference.local` 路由至已配置的模型後端 |
| **憑證注入** | 以環境變數形式注入 Provider 憑證，不寫入沙箱檔案系統 |
| **控制通道** | 與 Gateway 保持持久連線，接收策略更新與 Relay 請求 |
| **日誌推送** | 即時將日誌推送至 Gateway |

### Policy Engine（OPA）

Policy Engine 是 Supervisor 中的 Policy Proxy 所依賴的策略評估核心：

```
Agent 出站請求
      │
      ▼
 Policy Proxy
      │
      ├─ 目的地與方法評估 (OPA)
      │     ├─ Allow → 轉發至外部服務
      │     ├─ Route → 剝除 API Key，注入後端憑證，轉發至推理後端
      │     └─ Deny  → 阻斷並記錄
      │
      └─ inference.local → Inference Router → 模型後端
```

策略決策邏輯：
- **允許（Allow）**：目的地與 HTTP 方法符合策略 Block
- **推理路由（Route for Inference）**：剝除 Caller 憑證、注入後端憑證、轉發至受管模型
- **拒絕（Deny）**：阻斷請求並記錄

## 計算驅動架構

每個 Compute Driver 接收來自 Gateway 的沙箱規格，負責：

1. **選取沙箱映像**
2. **注入沙箱身份與 Gateway 回呼設定**
3. **提供 TLS 或 Secret 素材**
4. **提供 Supervisor 二進位或映像**
5. **回報生命週期與平台事件**
6. **清理執行時資源**

### Driver 比較

| Driver | 適用場景 | 沙箱邊界 | 特點 |
|--------|---------|---------|------|
| **Docker** | 本機開發 | 容器 + 沙箱命名空間 | 使用 Host 網路，Loopback Gateway 端點可用 |
| **Podman** | Rootless / 單機 | 容器 + 沙箱命名空間 | Podman REST API、OCI Image Volume、CDI GPU |
| **Kubernetes** | 叢集佈署（Helm） | Pod + 沙箱命名空間 | K8s API、Service Account、PVC、GPU 資源 |
| **VM（MicroVM）** | 最高隔離（實驗性） | libkrun VM | 每沙箱一個 VM，`rootfs.ext4` + `overlay.ext4` |

## Supervisor 二進位交付方式

Supervisor 必須存在於每個沙箱工作負載內，不同 Driver 有不同的交付方式：

| Driver | 交付方式 |
|--------|---------|
| Docker | 本機 Supervisor 二進位 Bind Mount |
| Podman | 唯讀 OCI Image Volume（含 Supervisor 二進位） |
| Kubernetes | 沙箱 Pod 映像 或 Init Container 複製 |
| VM | 嵌入於 Guest Rootfs Bundle |

在 Kubernetes 環境下，Supervisor 的交付方式由叢集版本決定：
- **K8s ≥ 1.35**：使用 `image-volume`（ImageVolume GA 於 1.36）
- **K8s < 1.35**：使用 `init-container`（複製至 emptyDir）

## 安全模型

### Gateway ↔ Supervisor 關係

兩者的關係由 **Supervisor 主動發起**：
- Supervisor 向已知的 Gateway 端點主動發出連線
- 以沙箱工作負載身份驗證（mTLS）
- 保持持久 Session 用於控制流量與 Relay
- 如 Session 中斷，沙箱可繼續執行，但即時操作失敗直到 Supervisor 重新連線

此設計避免 Compute Driver 必須解決 Gateway → Sandbox 的可達性問題（Pod IP、Port Forwarding、NAT 穿透等）。

### 策略更新機制

| 策略類型 | 更新時機 | 方式 |
|---------|---------|------|
| Filesystem 策略 | 沙箱建立時鎖定 | 不可熱重載 |
| Process 策略 | 沙箱建立時鎖定 | 不可熱重載 |
| Network 策略 | 執行時 | `openshell policy set` 熱重載 |
| Inference 策略 | 執行時 | `openshell policy set` 熱重載 |

## 目錄結構

```
OpenShell/
├── architecture/          # 架構文件（Gateway、Sandbox、Security Policy、Compute Runtime）
├── crates/                # Rust crates（核心）
│   ├── openshell-gateway/ # Gateway 核心實作
│   ├── openshell-supervisor/ # Supervisor 實作
│   ├── openshell-driver-docker/    # Docker Driver
│   ├── openshell-driver-podman/    # Podman Driver
│   ├── openshell-driver-kubernetes/ # Kubernetes Driver
│   └── openshell-driver-vm/        # VM Driver
├── deploy/
│   └── helm/openshell/    # Helm Chart（Kubernetes 部署）
├── examples/              # 使用範例（sandbox-policy-quickstart 等）
├── .agents/skills/        # Agent Skills（Agent 驅動的開發工作流程）
└── install.sh             # 二進位安裝腳本
```

## Kubernetes Driver 底層實作流程

以下是一次 `openshell sandbox create` 在 Kubernetes 上的控制流程（偏實作視角）：

```
CLI
 │ 1. create sandbox request
 ▼
Gateway API
 │ 2. 寫入 DB（sandbox record, policy ref, provider ref）
 │ 3. 指派 sandbox identity / cert material
 ▼
Kubernetes Driver
 │ 4. 組裝 PodSpec（image、securityContext、volumes、resources）
 │ 5. 決定 supervisor 交付模式（image-volume / init-container）
 │ 6. 建立 PVC（若 workspace persistence 啟用）
 ▼
K8s API Server
 │ 7. 建立 Pod / Secret / Config
 ▼
Sandbox Pod
 │ 8. Supervisor 啟動，主動回連 Gateway
 │ 9. 接收策略快照，開始 Policy Proxy / Inference Router
 ▼
Sandbox Ready
```

### 建立路徑中的關鍵狀態

| 狀態 | 觸發條件 | 常見失敗點 |
|------|---------|-----------|
| `Requested` | Gateway 收到建立請求 | API 驗證參數不完整 |
| `Provisioning` | Driver 開始建立 K8s 資源 | Secret / PVC / RBAC 權限不足 |
| `Bootstrapping` | Pod 已啟動、Supervisor 初始化 | Supervisor sidecar 交付失敗 |
| `Connected` | Supervisor 成功回連 Gateway | mTLS 憑證錯誤或 CA 不一致 |
| `Running` | 策略與推理路由載入完成 | OPA policy syntax / provider credentials 錯誤 |

## 控制平面與資料平面的請求路徑

```
                (控制流)
CLI ──gRPC/HTTP──▶ Gateway ──session sync──▶ Supervisor
                                      ▲
                                      │ policy update / relay / lifecycle
                                      │
Agent Process ──localhost proxy──▶ Policy Proxy ──egress──▶ External Service
        │
        └──https://inference.local──▶ Inference Router ──▶ LLM Provider
                         (資料流)
```

上圖可拆成兩條獨立路徑：
- **控制流**：CLI ↔ Gateway ↔ Supervisor（生命週期、策略、Relay）
- **資料流**：Agent ↔ Policy Proxy/Inference Router ↔ 外部 API（執行期網路請求）

## 維運痛點與實務對策（OpenShell on K8s）

| 維運痛點 | 底層原因 | 建議對策 |
|---------|---------|---------|
| Gateway 擴容後狀態不一致 | 多副本下若使用 SQLite，狀態無法共享 | 生產環境改用外部 PostgreSQL；啟用備援與連線池監控 |
| 沙箱大量建立時 Pending | PVC / Image Pull / Node 資源三方競爭 | 預先容量規劃、分離 sandbox node pool、設定 ResourceQuota |
| policy 更新延遲 | Supervisor 控制通道抖動或重連頻繁 | 監控 supervisor reconnect rate，設定告警並檢查網路抖動 |
| inference.local 成功率下降 | 上游 LLM provider 限流、憑證過期、DNS 問題 | 導入 provider 健康檢查、API Key 輪替排程、失敗率 SLO |
| 憑證輪替造成短暫中斷 | mTLS 憑證與 Supervisor session 更新不同步 | 採雙憑證重疊期（overlap）與分批滾動更新 |
| Debug 困難（Pod 秒退） | 啟動期錯誤在容器早期發生，日誌不完整 | 啟用集中式日誌，保留 init-container 與 supervisor 啟動日誌 |
