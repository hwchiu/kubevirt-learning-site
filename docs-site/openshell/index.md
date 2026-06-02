---
layout: doc
---

# NVIDIA OpenShell — 專案總覽

::: tip 分析版本
本文件基於 commit [`d9908222`](https://github.com/NVIDIA/OpenShell/commit/d9908222f2b18adeb00227f8fbefcaabd7ebd7f0) 進行分析。
:::

## 專案資訊

| 項目 | 說明 |
|------|------|
| **專案名稱** | NVIDIA OpenShell |
| **Repository** | [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell) |
| **語言／框架** | Rust（核心）、Python（CLI / PyPI 套件） |
| **PyPI 套件** | [`openshell`](https://pypi.org/project/openshell/) |
| **Helm Chart** | `oci://ghcr.io/nvidia/openshell/helm-chart` |
| **授權** | Apache License 2.0 |
| **官方文件** | [docs.nvidia.com/openshell](https://docs.nvidia.com/openshell/latest/index.html) |
| **專案狀態** | Alpha（積極開發中） |
| **專案類型** | AI Agent 安全沙箱執行環境 |

## 專案簡介

**NVIDIA OpenShell** 是針對自主 AI Agent 設計的**安全、私密執行環境（Runtime）**，提供以容器為基礎的隔離沙箱（Sandbox），透過宣告式 YAML 策略保護資料、憑證與基礎設施，防止未授權的檔案存取、資料外洩及不受控制的網路活動。

OpenShell 採用「Agent 優先」的設計理念——專案本身內建豐富的 Agent Skills，涵蓋從閘道除錯到策略生成等工作流程。支援的 AI Agent 包括 Claude Code、OpenCode、Codex、GitHub Copilot CLI、OpenClaw 等。

### 核心價值主張

- **沙箱隔離**：每個沙箱運行於獨立容器，具備策略強制的對外路由
- **宣告式策略**：YAML 策略檔控制檔案系統、網路、程序與推理（Inference）四個維度
- **熱重載策略**：網路與推理策略可在不重啟沙箱的情況下即時更新
- **憑證管理（Provider）**：以具名憑證套件（Provider）管理 API Key，運行時以環境變數注入，不落地至沙箱檔案系統
- **多計算後端**：支援 Docker、Podman、MicroVM 與 Kubernetes

## 文件目錄

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | Gateway、Supervisor、Policy Engine、Compute Runtime 架構設計 |
| [核心功能分析](./core-features) | 沙箱管理、策略系統、Provider 機制、GPU 支援、Terminal UI |
| [Kubernetes 整合](./k8s-integration) | Helm Chart 部署、CRD 需求、OpenShift 支援、K8s 特有配置 |

## 系統架構概覽

OpenShell 由三個核心執行元件構成：

| 元件 | 角色 | 說明 |
|------|------|------|
| **Gateway** | 控制平面 API 伺服器 | 管理沙箱生命週期、驗證身份、分發策略與憑證、協調 Relay |
| **Supervisor** | 沙箱本地安全邊界 | 以受限子程序啟動 Agent，在程序、檔案系統、網路層強制策略 |
| **Policy Engine（OPA）** | 策略評估引擎 | 攔截所有出站流量，根據策略決定允許、路由或拒絕 |

### 計算後端

| 後端 | 適用場景 | 沙箱隔離邊界 |
|------|---------|------------|
| Docker | 本機開發（Docker 可用） | 容器 + 沙箱命名空間 |
| Podman | 無 Root 或單機部署 | 容器 + 沙箱命名空間 |
| Kubernetes | 透過 Helm 佈署至叢集 | Pod + 沙箱命名空間 |
| VM（MicroVM） | 最高隔離需求（實驗性） | 每個沙箱一個 libkrun VM |

## 防護層次

OpenShell 在四個策略維度實施縱深防禦：

| 層級 | 保護對象 | 適用時機 |
|------|---------|---------|
| **Filesystem** | 防止在允許路徑以外讀寫 | 沙箱建立時鎖定 |
| **Network** | 阻擋未授權的對外連線 | 執行時熱重載 |
| **Process** | 阻擋提權與危險 Syscall | 沙箱建立時鎖定 |
| **Inference** | 將模型 API 呼叫路由至受控後端 | 執行時熱重載 |

## 主要指令

```bash
# 建立沙箱並啟動 Agent
openshell sandbox create -- claude

# 連線至執行中的沙箱
openshell sandbox connect [name]

# 列出所有沙箱
openshell sandbox list

# 套用或更新策略
openshell policy set <name> --policy file.yaml

# 查看目前策略
openshell policy get <name>

# 建立憑證 Provider
openshell provider create --type [type] --from-existing

# 啟動 Terminal UI（即時監控儀表板）
openshell term
```

## 建置系統

OpenShell 核心以 Rust 編寫，並提供 Python CLI 套件：

```bash
# 從二進位安裝（推薦）
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh

# 從 PyPI 安裝（需要 uv）
uv tool install -U openshell

# 從 Helm Chart 部署至 Kubernetes
helm install openshell oci://ghcr.io/nvidia/openshell/helm-chart
```

## 支援的 AI Agent

| Agent | 說明 |
|-------|------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | 原生支援，使用 `ANTHROPIC_API_KEY` |
| [OpenCode](https://opencode.ai/) | 原生支援，使用 `OPENAI_API_KEY` 或 `OPENROUTER_API_KEY` |
| [Codex](https://developers.openai.com/codex) | 原生支援，使用 `OPENAI_API_KEY` |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli) | 原生支援，使用 `GITHUB_TOKEN` |
| [OpenClaw](https://openclaw.ai/) | 搭配 [NemoClaw](https://github.com/NVIDIA/NemoClaw) 在 OpenShell 中安全執行 |
| [Ollama](https://ollama.com/) | 使用 `openshell sandbox create --from ollama` |

::: info 相關章節
本文件為 NVIDIA OpenShell 分析系列的總覽入口。詳細技術內容請參閱：
- [系統架構](./architecture) — Gateway、Supervisor、Policy Engine 內部設計
- [核心功能分析](./core-features) — 沙箱生命週期、策略系統、Provider、GPU 支援
- [Kubernetes 整合](./k8s-integration) — Helm Chart、CRD、OpenShift、K8s 進階配置
:::
