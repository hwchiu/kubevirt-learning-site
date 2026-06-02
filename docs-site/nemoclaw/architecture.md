---
layout: doc
---

# NVIDIA NemoClaw — 系統架構

::: tip 分析版本
本文件基於 commit [`798d5a38`](https://github.com/NVIDIA/NemoClaw/commit/798d5a386a92a34e00f16eccb6fcb2eaa5007643) 進行分析。
:::

::: info 相關章節
- 專案簡介請參閱 [專案總覽](./index)
- 初始設定、推理與網路策略請參閱 [核心功能分析](./core-features)
- Kubernetes 部署請參閱 [Kubernetes 整合](./k8s-integration)
:::

## 整體架構概覽

NemoClaw 作為 OpenShell 之上的**薄層（Thin Layer）**參考堆疊，透過 Plugin 機制整合至 OpenShell 的核心生命週期，不替換底層安全機制，而是在其基礎上提供針對 OpenClaw / Hermes 最佳化的配置與管理能力。

```
使用者
  │
  ▼ nemoclaw CLI
┌─────────────────────────────────────────┐
│            NemoClaw Plugin              │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  Blueprint  │  │ Lifecycle Manager│  │
│  │  (強化配置) │  │  (常駐 Agent)    │  │
│  └──────┬──────┘  └────────┬─────────┘  │
│         │                  │            │
│  ┌──────▼──────────────────▼─────────┐  │
│  │        OpenShell Gateway API      │  │
│  └───────────────┬───────────────────┘  │
└──────────────────┼──────────────────────┘
                   │
         ┌─────────▼──────────┐
         │   OpenShell 核心    │
         │  Sandbox │ Policy   │
         │  Engine  │ Proxy    │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │   沙箱工作負載       │
         │  Supervisor         │
         │  ├── OpenClaw       │
         │  │   (restricted)   │
         │  └── Policy Proxy   │
         └────────────────────┘
```

## Plugin 結構

NemoClaw Plugin 是 NemoClaw 的核心抽象，掛接至 OpenShell 的沙箱生命週期：

| Plugin 元件 | 職責 |
|------------|------|
| **Blueprint Loader** | 載入並驗證針對目標 Agent 的強化沙箱藍圖 |
| **Policy Composer** | 組合基準網路策略與使用者自訂規則 |
| **Inference Configurator** | 設定推理路由（provider、model、endpoint） |
| **Lifecycle Hook** | 在沙箱建立/啟動/停止/刪除事件上執行 NemoClaw 邏輯 |
| **Host-side State** | 維護本機設定、Profile 與沙箱元資料 |

## Blueprint（強化藍圖）

Blueprint 是針對特定 Agent 優化的沙箱配置集合：

```yaml
# Blueprint 包含的配置維度
blueprint:
  agent: openclaw                        # 目標 Agent
  image: nvidia/nemoclaw/openclaw:latest # 沙箱映像（含 Agent 與依賴）
  security:
    capabilities_drop: [ALL]            # 刪除所有 Linux Capabilities
    no_new_privileges: true             # 禁止取得新權限
    read_only_root: true                # Root Filesystem 唯讀
    process_limits:                     # 程序限制
      max_pids: 128
  network_policy: baseline              # 預設使用基準策略
  inference:
    provider: nvidia_nim                # 預設推理 Provider
```

### Blueprint 生命週期

```
nemoclaw setup
    │
    ├─ 互動式引導填寫設定（推理 Provider、API Key 等）
    ├─ 驗證前置需求（OpenShell 已安裝、Docker/K8s 可用）
    ├─ 載入對應 Agent 的 Blueprint
    ├─ 建立 OpenShell Provider（憑證）
    └─ 生成初始 Network Policy

nemoclaw start
    │
    ├─ 套用 Blueprint 到 OpenShell sandbox create
    ├─ 注入推理配置
    ├─ 套用網路策略
    └─ 啟動 Supervisor（常駐 Agent 程序）
```

## 沙箱環境

NemoClaw 管理的沙箱環境具有以下特性：

### 容器安全措施

| 安全措施 | 說明 |
|---------|------|
| **Capability Drop** | 刪除所有 Linux Capabilities，僅保留必要的最小集合 |
| **No New Privileges** | `no_new_privileges` Security Context 防止子程序取得額外權限 |
| **Read-only Root FS** | 根檔案系統掛載為唯讀，僅 `/workspace` 等特定目錄可寫 |
| **Process Limits** | 限制最大 PID 數，防止 Fork Bomb |
| **Seccomp Profile** | 限制可用 Syscall，阻擋危險操作 |

### 推理路由架構

```
沙箱內 Agent（OpenClaw）
         │
         ▼ 呼叫 inference.local
   Inference Router（OpenShell）
         │
         ├─ 驗證 Agent 憑證
         ├─ 剝除原始 API Key
         ├─ 注入 NemoClaw 管理的後端憑證
         └─ 轉發至目標推理後端

         ▼
┌──────────────────────────────┐
│    支援的推理後端              │
├──────────────────────────────┤
│ NVIDIA NIM（推薦）             │
│ OpenAI API                   │
│ Azure OpenAI                 │
│ Anthropic                    │
│ 其他 OpenAI 相容 API           │
└──────────────────────────────┘
```

## Network Policy 架構

NemoClaw 的網路管控採用**分層策略模型**：

```
┌──────────────────────────────────────────┐
│           Network Policy 層次             │
├──────────────────────────────────────────┤
│  Level 3：使用者自訂規則（Override）        │
│           nemoclaw policy add ...        │
├──────────────────────────────────────────┤
│  Level 2：Agent 特定規則                  │
│           OpenClaw / Hermes 所需的        │
│           最小網路存取（Blueprint 內建）    │
├──────────────────────────────────────────┤
│  Level 1：基準規則（Baseline）            │
│           推理後端存取 + 必要的系統更新    │
├──────────────────────────────────────────┤
│  Level 0：OpenShell 沙箱預設（最小存取）  │
│           完全阻斷，僅 inference.local     │
└──────────────────────────────────────────┘
```

### Operator 審核流程

當 Agent 請求新的網路存取時：

```
Agent 請求新網路存取
       │
       ▼
 OpenShell Policy Proxy 攔截
       │
       ▼
 NemoClaw 審核佇列（Pending）
       │
       ▼
 Operator 收到通知
       │
  ┌────┴────┐
  │         │
  ▼         ▼
核准      拒絕
  │         │
  ▼         ▼
動態更新    記錄並封鎖
網路策略
```

## Host 端狀態

NemoClaw 在 Host 上維護以下狀態：

```
~/.nemoclaw/
├── config.yaml          # NemoClaw 全域設定
├── profiles/            # Agent Profile（推理、策略配置）
│   └── openclaw.yaml
├── sandboxes/           # 沙箱元資料
│   └── <sandbox-id>.yaml
└── logs/                # NemoClaw 操作日誌
```

## 與 OpenShell 的邊界劃分

| 職責 | 歸屬 | 說明 |
|------|------|------|
| 沙箱建立/刪除/監視 | OpenShell | Compute Driver 管理 Pod/Container 生命週期 |
| 策略強制執行 | OpenShell | Supervisor 的 Policy Proxy + OPA |
| 憑證不落地機制 | OpenShell | Provider 以環境變數注入 |
| Blueprint 選取與套用 | NemoClaw | 依目標 Agent 選擇最佳配置 |
| 引導式 Onboarding | NemoClaw | 互動式設定流程 |
| 推理 Provider 預設配置 | NemoClaw | NVIDIA NIM 等預設後端 |
| 常駐 Agent 管理 | NemoClaw | start/stop/status 生命週期 |
| Operator 審核流程 | NemoClaw | 網路存取請求的審核機制 |

## NemoClaw 在 K8s 的底層落地流程

NemoClaw 本身不直接創建 Pod，而是把「藍圖 + 策略 + 推理配置」轉成 OpenShell 可執行的請求：

```
nemoclaw start
   │
   ├─ 1. 讀取 ~/.nemoclaw/profiles/<agent>.yaml
   ├─ 2. 合成 Blueprint（image/security/resources）
   ├─ 3. 產生 Network Policy（baseline + user override）
   ├─ 4. 檢查 Provider/Model 設定
   ▼
OpenShell API 呼叫（sandbox create + policy set + inference set）
   ▼
OpenShell Gateway / Kubernetes Driver
   ▼
K8s Pod + Supervisor + Agent（OpenClaw/Hermes）
```

### 重要實作邏輯：不是替代 OpenShell，而是「編排 OpenShell」

| 層次 | 負責元件 | 實作重點 |
|------|---------|---------|
| 編排層 | NemoClaw CLI/Plugin | 組合藍圖、策略、推理、常駐模式 |
| 控制層 | OpenShell Gateway | API、狀態儲存、策略下發、身份驗證 |
| 執行層 | OpenShell Supervisor | Policy Proxy、Inference Router、程序隔離 |
| 基礎層 | Kubernetes | Pod 調度、儲存、網路、節點資源管理 |

## 常駐 Agent 的控制/資料雙路徑

```
          (控制路徑)
nemoclaw CLI ──▶ OpenShell Gateway ──▶ Supervisor
      ▲                                   │
      │                                   ├─ policy/inference config sync
      │                                   └─ status/log stream
      │
      └────────── status / stop / restart ──────────┘

          (資料路徑)
OpenClaw/Hermes ──▶ Policy Proxy ──▶ External APIs
        │
        └──▶ inference.local ──▶ Inference Router ──▶ LLM Provider
```

若要排查「為什麼 `nemoclaw start` 成功但任務失敗」，要同時檢查兩條路徑：  
1) 控制路徑是否連通（Gateway/Supervisor session）；2) 資料路徑是否被策略或上游 provider 阻斷。

## 維運痛點與實務對策（NemoClaw）

| 維運痛點 | 底層原因 | 建議對策 |
|---------|---------|---------|
| `nemoclaw setup` 與叢集現況脫節 | 初次引導後，叢集資源/憑證會持續變動 | 導入週期性 re-validation（provider key、storage class、GPU 資源） |
| Agent 長時間執行後記憶體膨脹 | 常駐 workload 缺少明確重啟策略 | 為 Agent Pod 設定 memory limits + liveness probe + 週期性重啟 |
| 網路審核流程堆積 | pending 規則沒有 SLA 與責任人 | 建立審核隊列 SLA、owner 值班、逾時自動拒絕或升級 |
| 多環境配置漂移（dev/staging/prod） | Blueprint 與 policy 以檔案散落管理 | 版本化 profile/policy（GitOps），以 PR 審核變更 |
| 事件追蹤困難 | CLI、Gateway、Supervisor、K8s 事件分散 | 建立統一 trace-id，串接集中式日誌與告警 |
| 升級後行為改變 | NemoClaw 與 OpenShell 版本相依 | 維護版本相容矩陣，升級前先做 canary sandbox 驗證 |
