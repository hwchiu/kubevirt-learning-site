---
layout: doc
---

# NVIDIA OpenShell — 核心功能分析

::: tip 分析版本
本文件基於 commit [`d9908222`](https://github.com/NVIDIA/OpenShell/commit/d9908222f2b18adeb00227f8fbefcaabd7ebd7f0) 進行分析。
:::

::: info 相關章節
- 專案簡介請參閱 [專案總覽](./index)
- 架構設計請參閱 [系統架構](./architecture)
- K8s 叢集部署請參閱 [Kubernetes 整合](./k8s-integration)
:::

## 沙箱生命週期管理

### 建立沙箱

```bash
# 基本建立：預設 base sandbox image，啟動 claude
openshell sandbox create -- claude

# 指定 Community Catalog 映像
openshell sandbox create --from ollama

# 使用本機 Dockerfile 目錄
openshell sandbox create --from ./my-sandbox-dir

# 使用容器映像
openshell sandbox create --from registry.io/img:v1

# 開啟 GPU 支援（實驗性）
openshell sandbox create --gpu --from gpu-enabled-sandbox -- claude
```

### 沙箱狀態管理

| 指令 | 說明 |
|------|------|
| `openshell sandbox create` | 建立沙箱並啟動 Agent |
| `openshell sandbox connect [name]` | SSH 連入執行中的沙箱 |
| `openshell sandbox list` | 列出所有沙箱及狀態 |
| `openshell logs [name] --tail` | 串流沙箱日誌 |

### 預設沙箱工具集

Base sandbox image 內建以下工具：

| 類別 | 工具 |
|------|------|
| Agent | `claude`, `opencode`, `codex`, `copilot` |
| 語言 | `python` (3.14), `node` (22) |
| 開發 | `gh`, `git`, `vim`, `nano` |
| 網路 | `ping`, `dig`, `nslookup`, `nc`, `traceroute`, `netstat` |

## 策略系統

### 策略結構

OpenShell 策略以宣告式 YAML 定義，分為靜態與動態兩類：

```yaml
# 範例：沙箱策略檔
version: "1"
network:
  egress:
    - name: allow-github-api-read
      destination: api.github.com
      methods: [GET, HEAD]
      paths:
        - /repos/**
        - /zen
    - name: allow-pypi
      destination: pypi.org
      methods: [GET]
inference:
  local:
    provider: openai
    model: gpt-4o
filesystem:
  # 靜態，沙箱建立時鎖定
  allow:
    - path: /workspace
      access: [read, write]
    - path: /home/user/.config
      access: [read]
process:
  # 靜態，沙箱建立時鎖定
  disallow_privilege_escalation: true
```

### 策略即時操作

```bash
# 套用或更新策略（網路/推理策略可熱重載，無需重啟沙箱）
openshell policy set demo --policy examples/policy.yaml --wait

# 查看目前啟用的策略
openshell policy get demo
```

### 策略評估流程示範

```bash
# 1. 建立沙箱（預設最小出站存取）
openshell sandbox create

# 2. 在沙箱內——被阻斷
sandbox$ curl -sS https://api.github.com/zen
# curl: (56) Received HTTP code 403 from proxy after CONNECT

# 3. 在 Host 上套用 GitHub API 唯讀策略
openshell policy set demo --policy policy.yaml --wait

# 4. 重新連線——GET 允許，POST 被策略拒絕
sandbox$ curl -sS https://api.github.com/zen
# Anything added dilutes everything else.

sandbox$ curl -sS -X POST https://api.github.com/repos/octocat/hello-world/issues
# {"error":"policy_denied","detail":"POST /repos/... not permitted by policy"}
```

## Provider（憑證管理）機制

Agent 需要 API Key、Token 與 Service Account 等憑證。OpenShell 以 **Provider** 管理：

- **Provider** 是具名的憑證套件（Named Credential Bundle）
- CLI 自動從 Shell 環境變數探索已知 Agent 的憑證（Claude、Codex、OpenCode、Copilot）
- 可手動建立自訂 Provider
- **憑證絕不進入沙箱檔案系統**；以環境變數形式在執行時注入

```bash
# 從現有環境變數建立 Provider
openshell provider create --type anthropic --from-existing

# 指定 Provider 建立沙箱
openshell sandbox create --provider my-provider -- claude
```

| Agent | Provider 環境變數 |
|-------|----------------|
| Claude Code | `ANTHROPIC_API_KEY` |
| OpenCode | `OPENAI_API_KEY` 或 `OPENROUTER_API_KEY` |
| Codex | `OPENAI_API_KEY` |
| GitHub Copilot CLI | `GITHUB_TOKEN` 或 `COPILOT_GITHUB_TOKEN` |

## 推理路由（Inference Routing）

OpenShell 的 Inference Router 提供 **Privacy-Aware LLM 路由**：

- 沙箱內對 `https://inference.local` 的所有呼叫都透過 Inference Router 轉發
- Router 剝除 Caller 憑證，注入後端憑證，轉發至受管的推理後端
- 敏感上下文保留在沙箱計算資源上，不外洩

```bash
# 配置 Inference 端點
openshell inference set --provider openai --model gpt-4o

# 沙箱內呼叫（自動路由至已配置後端）
sandbox$ curl https://inference.local/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}]}'
```

## GPU 支援（實驗性）

OpenShell 支援將 Host GPU 直通至沙箱，適用於本地推理、微調等 GPU 工作負載：

```bash
# 啟用 GPU 沙箱
openshell sandbox create --gpu --from gpu-enabled-sandbox -- claude
```

### GPU 需求

- NVIDIA 驅動已安裝於 Host
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) 已安裝
- 沙箱映像需包含適合工作負載的 GPU 驅動與函式庫（預設 base 映像不含）

Docker 後端的 GPU 沙箱：
- 優先使用 CDI（Container Device Interface）
- CDI 不可用時退回至 Docker 的 NVIDIA GPU 路徑（`--gpus all`）

## Terminal UI（TUI）

OpenShell 提供即時的 Terminal 儀表板，靈感來自 [k9s](https://k9scli.io/)：

```bash
openshell term
```

TUI 提供：
- 即時 Gateway 狀態與沙箱狀態（每 2 秒自動刷新）
- 鍵盤驅動導覽：`Tab` 切換面板、`j`/`k` 移動清單、`Enter` 選取、`:` 指令模式
- Gateway 健康狀態、沙箱清單、Provider 清單即時查看

## Agent 驅動的開發工作流程

OpenShell 的開發本身也大量使用 Agent 自動化，`.agents/skills/` 目錄包含：

| Skill | 說明 |
|-------|------|
| `openshell-cli` | CLI 使用指南 |
| `debug-openshell-cluster` | Gateway 故障診斷 |
| `debug-inference` | 推理配置除錯 |
| `generate-sandbox-policy` | 從自然語言需求或 API 文件生成 YAML 策略 |
| `create-spike` | 問題調查工作流程 |
| `build-from-issue` | 從 Issue 實作功能 |
| `triage-issue` | Issue 分類與路由 |
| `review-security-issue` | 安全問題評估 |
| `fix-security-issue` | 安全問題修復 |

所有實作工作均經人工審核後才由 Agent 執行（Human-Gated）。

## Community Sandbox 生態系

使用 `--from` 參數可存取 [OpenShell Community](https://github.com/NVIDIA/OpenShell-Community) 的沙箱目錄：

```bash
openshell sandbox create --from gemini    # Google Gemini Agent
openshell sandbox create --from ollama    # Ollama 本地模型
openshell sandbox create --from pi        # Pi Agent
```

## 遙測（Telemetry）

OpenShell 收集匿名遙測資料，用於改善產品。收集的資料僅限於：
- 沙箱生命週期結果統計
- Provider 類型分佈（匿名）
- 策略決策計數
- 網路活動拒絕類別彙總

**不收集**：沙箱名稱、主機名稱、檔案路徑、Prompt 內容、憑證、Provider 名稱、模型名稱或使用者內容。

停用遙測：
```bash
export OPENSHELL_TELEMETRY_ENABLED=false
```
