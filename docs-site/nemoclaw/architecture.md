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
