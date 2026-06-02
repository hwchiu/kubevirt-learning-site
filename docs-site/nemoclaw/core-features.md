---
layout: doc
---

# NVIDIA NemoClaw — 核心功能分析

::: tip 分析版本
本文件基於 commit [`798d5a38`](https://github.com/NVIDIA/NemoClaw/commit/798d5a386a92a34e00f16eccb6fcb2eaa5007643) 進行分析。
:::

::: info 相關章節
- 專案簡介請參閱 [專案總覽](./index)
- 架構設計請參閱 [系統架構](./architecture)
- K8s 叢集部署請參閱 [Kubernetes 整合](./k8s-integration)
:::

## 引導式初始設定（Guided Onboarding）

NemoClaw 的核心優勢之一是簡化的引導式初始設定流程，即使不熟悉 OpenShell 的使用者也能快速完成配置：

```bash
# 開始引導式設定
nemoclaw setup
```

`nemoclaw setup` 會互動式地引導使用者完成：

1. **前置需求確認**：驗證 OpenShell、Docker/Podman/K8s 已正確安裝
2. **Agent 選擇**：OpenClaw（預設）或 Hermes
3. **推理 Provider 配置**：選擇並配置推理後端（NVIDIA NIM、OpenAI 等）
4. **API Key 輸入**：安全地輸入並建立 OpenShell Provider
5. **Blueprint 套用**：自動套用對應 Agent 的強化沙箱藍圖
6. **基準網路策略生成**：自動生成適合所選 Agent 的基準網路策略

### Hermes Agent 設定

```bash
# 使用 Hermes 作為目標 Agent
NEMOCLAW_AGENT=hermes nemoclaw setup

# 或使用 nemohermes alias
nemohermes setup
```

## 推理選項（Inference Options）

NemoClaw 支援多種推理後端，透過 OpenShell 的 Inference Router 提供 Privacy-Aware 路由：

### 支援的推理 Provider

| Provider | 說明 | 配置方式 |
|---------|------|---------|
| **NVIDIA NIM**（推薦） | NVIDIA 的企業級推理服務，支援 GPU 加速 | `nemoclaw inference set --provider nvidia_nim` |
| **OpenAI** | OpenAI GPT 系列模型 | `nemoclaw inference set --provider openai` |
| **Azure OpenAI** | Azure 上的 OpenAI 服務 | `nemoclaw inference set --provider azure_openai` |
| **Anthropic** | Claude 系列模型 | `nemoclaw inference set --provider anthropic` |
| **本地 Ollama** | 本機執行的開源模型 | `nemoclaw inference set --provider ollama` |

### 配置推理後端

```bash
# 設定推理 Provider 與模型
nemoclaw inference set --provider nvidia_nim --model llama-3.1-70b-instruct

# 查看目前推理配置
nemoclaw inference get

# 驗證推理連線
nemoclaw inference validate
```

### 推理路由工作方式

```bash
# 沙箱內 Agent 的 API 呼叫（自動路由）
sandbox$ curl https://inference.local/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b-instruct",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
# → 自動路由至已配置的 NVIDIA NIM 後端
# → Caller 的 API Key 被剝除，注入 NemoClaw 管理的 NIM 憑證
```

## 網路策略管理

### 基準規則（Baseline Policy）

NemoClaw 預設的基準網路策略涵蓋：

- 推理後端存取（`inference.local` → 已配置的 Provider）
- 必要的系統套件更新（OS 更新端點）
- Agent 正常運作所需的最小外部存取

```bash
# 查看目前網路策略
nemoclaw policy get

# 查看基準策略詳情
nemoclaw policy get --preset baseline
```

### 自訂網路策略

```bash
# 新增自訂出站規則
nemoclaw policy add --destination github.com --methods GET,HEAD

# 套用自訂策略檔
nemoclaw policy set --file my-policy.yaml

# 重設為基準策略
nemoclaw policy reset

# 查看可用的預設策略
nemoclaw policy presets
```

### 網路存取審核流程

當 Agent 嘗試存取未授權的目的地時，NemoClaw 會啟動審核流程：

```bash
# 查看待審核的網路存取請求
nemoclaw policy review list

# 核准特定請求
nemoclaw policy review approve <request-id>

# 拒絕特定請求
nemoclaw policy review deny <request-id>

# 核准並永久加入策略
nemoclaw policy review approve <request-id> --persist
```

## 沙箱強化（Sandbox Hardening）

NemoClaw 在 OpenShell 的基礎安全措施上，針對 OpenClaw / Hermes 進行額外強化：

### 容器安全措施

| 措施 | 實作方式 | 效果 |
|------|---------|------|
| **Capability Drop** | Blueprint 中設定 `capabilities: drop: [ALL]` | 移除所有 Linux Capabilities |
| **No New Privileges** | Security Context `allowPrivilegeEscalation: false` | 禁止子程序取得額外權限 |
| **Read-only Root FS** | `readOnlyRootFilesystem: true` | Root FS 唯讀，防止惡意寫入 |
| **Process Limits** | `pids_limit` 限制 | 防止 Fork Bomb 攻擊 |
| **Seccomp Profile** | 自訂 Seccomp Profile | 限制可用 Syscall 集合 |
| **User Namespace** | 配合 K8s 1.33+ 的 User Namespace | 容器 Root 映射至非特權 Host UID |

### 安全最佳實務建議

詳見官方文件 [Security Best Practices](https://docs.nvidia.com/nemoclaw/latest/security/best-practices.html)，NemoClaw 提供三種安全姿態（Posture Profile）：

| Profile | 說明 | 適用場景 |
|---------|------|---------|
| **Strict** | 最大限制，僅允許最小必要操作 | 生產環境、高安全需求 |
| **Standard**（預設） | 平衡安全與可用性 | 一般開發與生產 |
| **Development** | 放寬限制，便於除錯 | 本機開發、調試 |

## CLI 指令參考

完整指令參考見 [CLI Commands 文件](https://docs.nvidia.com/nemoclaw/latest/reference/commands.html)，以下為常用指令：

### 生命週期管理

| 指令 | 說明 |
|------|------|
| `nemoclaw setup` | 引導式初始設定 |
| `nemoclaw start` | 啟動 Agent 沙箱（常駐模式） |
| `nemoclaw stop` | 停止 Agent 沙箱 |
| `nemoclaw status` | 查看沙箱狀態 |
| `nemoclaw restart` | 重啟沙箱 |
| `nemoclaw logs [--tail]` | 查看沙箱日誌 |

### 推理管理

| 指令 | 說明 |
|------|------|
| `nemoclaw inference set --provider <p> --model <m>` | 設定推理後端 |
| `nemoclaw inference get` | 查看目前推理配置 |
| `nemoclaw inference validate` | 驗證推理連線 |

### 網路策略管理

| 指令 | 說明 |
|------|------|
| `nemoclaw policy get` | 查看目前策略 |
| `nemoclaw policy set --file <file>` | 套用策略檔 |
| `nemoclaw policy add --destination <host>` | 新增出站規則 |
| `nemoclaw policy reset` | 重設為基準策略 |
| `nemoclaw policy review list` | 列出待審核請求 |
| `nemoclaw policy review approve <id>` | 核准網路請求 |

### 設定管理

| 指令 | 說明 |
|------|------|
| `nemoclaw config get` | 查看目前設定 |
| `nemoclaw config set <key> <value>` | 修改設定 |

## 常駐模式（Always-on Agent）

NemoClaw 的核心使用場景之一是以**常駐模式**執行 AI Agent：

```bash
# 啟動常駐沙箱（背景執行）
nemoclaw start --daemon

# 確認 Agent 持續執行
nemoclaw status
# ✓ Sandbox: running (pid: 1234)
# ✓ Agent: OpenClaw v1.2.3 (active)
# ✓ Inference: NVIDIA NIM (llama-3.1-70b-instruct)
# ✓ Network Policy: standard (12 rules)

# 連入執行中的沙箱進行互動
nemoclaw connect

# 查看 Agent 活動日誌
nemoclaw logs --tail --follow
```

### 常駐模式的應用場景

| 場景 | 說明 |
|------|------|
| **自動化工作流程** | Agent 持續監聽任務佇列，自動執行工作 |
| **CI/CD 整合** | 在 CI Pipeline 中以安全沙箱執行 Agent 任務 |
| **開發輔助** | 在背景持續執行的程式撰寫輔助 Agent |
| **K8s 叢集管理** | 在 Kubernetes 環境中以 Pod 形式常駐執行 |

## 故障排查

常見問題詳見 [Troubleshooting 文件](https://docs.nvidia.com/nemoclaw/latest/reference/troubleshooting.html)：

| 症狀 | 可能原因 | 解決方式 |
|------|---------|---------|
| `nemoclaw start` 失敗 | OpenShell 未啟動 | 確認 `openshell gateway status` |
| 推理呼叫被拒絕 | 推理 Provider 未配置 | 執行 `nemoclaw inference set` |
| 網路存取被阻斷 | 目的地不在策略中 | 執行 `nemoclaw policy add` 或審核待審請求 |
| Agent 程序意外退出 | Seccomp / Capability 限制 | 使用 Development Profile 除錯 |
| 沙箱無法建立 | Blueprint 映像拉取失敗 | 確認 Image Pull 憑證與網路連線 |
