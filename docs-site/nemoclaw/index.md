---
layout: doc
---

# NVIDIA NemoClaw — 專案總覽

::: tip 分析版本
本文件基於 commit [`798d5a38`](https://github.com/NVIDIA/NemoClaw/commit/798d5a386a92a34e00f16eccb6fcb2eaa5007643) 進行分析。
:::

## 專案資訊

| 項目 | 說明 |
|------|------|
| **專案名稱** | NVIDIA NemoClaw |
| **Repository** | [NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw) |
| **授權** | Apache License 2.0 |
| **官方文件** | [docs.nvidia.com/nemoclaw](https://docs.nvidia.com/nemoclaw/latest/) |
| **社群** | [Discord](https://discord.gg/XFpfPv9Uvx)、[GitHub Discussions](https://github.com/NVIDIA/NemoClaw/discussions) |
| **專案類型** | AI Agent 安全執行參考堆疊（Reference Stack） |
| **依賴** | [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell) |

## 專案簡介

**NVIDIA NemoClaw** 是在 [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell) 沙箱內執行**常駐 AI Agent（Always-on AI Agents）**的開源參考堆疊（Reference Stack）。NemoClaw 提供引導式初始設定（Guided Onboarding）、強化藍圖（Hardened Blueprint）、路由推理（Routed Inference）、網路策略（Network Policy）與生命週期管理，透過單一 CLI 統一操作。

### NemoClaw 在生態系中的定位

```
OpenClaw / Hermes（AI Agent）
         │
         ▼
    NemoClaw（參考堆疊）
         │  強化藍圖、路由推理、網路策略、生命週期管理
         ▼
  NVIDIA OpenShell（沙箱執行環境）
         │  沙箱隔離、策略強制、憑證管理
         ▼
  Docker / Podman / Kubernetes（計算後端）
```

### 何時使用 NemoClaw vs 單獨使用 OpenShell

| 場景 | 建議 |
|------|------|
| 執行 OpenClaw 或 Hermes，需要最佳安全配置 | 使用 NemoClaw |
| 執行其他 Agent（Claude、Codex 等），無需特殊強化 | 直接使用 OpenShell |
| 需要引導式初始設定 | 使用 NemoClaw |
| 需要進階推理路由與預設網路策略 | 使用 NemoClaw |

## 支援的 AI Agent

| Agent | 快速入門指南 |
|-------|------------|
| [OpenClaw](https://openclaw.ai)（預設） | [使用 OpenClaw 快速入門](https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html) |
| [Hermes](https://get-hermes.ai/) | [使用 Hermes 快速入門](https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart-hermes.html) |

## 文件目錄

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | Plugin 結構、藍圖生命週期、沙箱環境、Host 端狀態 |
| [核心功能分析](./core-features) | 引導式初始設定、推理選項、網路策略、沙箱強化、CLI 指令 |
| [Kubernetes 整合](./k8s-integration) | 在 K8s 環境中安裝與使用 NemoClaw |

## 快速開始

### 前置需求

詳見 [Prerequisites 文件](https://docs.nvidia.com/nemoclaw/latest/get-started/prerequisites.html)。

### 安裝 NemoClaw（OpenClaw）

```bash
# 安裝 NemoClaw（預設使用 OpenClaw）
curl -LsSf https://install.nemoclaw.nvidia.com | sh

# 或使用 nemohermes alias 安裝 Hermes
NEMOCLAW_AGENT=hermes curl -LsSf https://install.nemoclaw.nvidia.com | sh
```

### 基本使用流程

```bash
# 1. 初始設定（引導式）
nemoclaw setup

# 2. 啟動 Agent 沙箱
nemoclaw start

# 3. 查看沙箱狀態
nemoclaw status

# 4. 停止沙箱
nemoclaw stop
```

## 系統架構概覽

NemoClaw 的核心是一個**插件（Plugin）**，整合至 OpenShell 的沙箱生命週期中：

| 元件 | 角色 | 說明 |
|------|------|------|
| **Plugin** | NemoClaw 核心 | 掛接至 OpenShell 生命週期，提供藍圖、策略、推理配置 |
| **Blueprint** | 強化沙箱配置 | 針對 OpenClaw / Hermes 最佳化的沙箱映像與安全設定 |
| **Inference Router** | 路由推理 | 透過 OpenShell 的 Inference Router 管理模型 API 路由 |
| **Network Policy** | 網路管控 | 預設基準規則 + Operator 審核流程的出站管控 |
| **Lifecycle Manager** | 生命週期 | 常駐 Agent 的啟動、停止、監控 |

## 與現有生態系比較

| 特性 | NemoClaw | OpenShell（裸機） |
|------|---------|-----------------|
| **目標 Agent** | OpenClaw、Hermes | 任意 Agent |
| **初始設定** | 引導式 Onboarding | 手動配置 |
| **沙箱藍圖** | 預設強化藍圖 | 使用者自定義 |
| **推理路由** | 內建預設配置 | 手動配置 |
| **網路策略** | 預設基準規則 + 審核流程 | 完全手動 |
| **常駐模式** | 原生支援 | 手動管理 |
| **複雜度** | 低（引導式） | 中（需了解 OpenShell 概念） |

::: info 相關章節
本文件為 NVIDIA NemoClaw 分析系列的總覽入口。詳細技術內容請參閱：
- [系統架構](./architecture) — Plugin 結構、藍圖生命週期、沙箱環境
- [核心功能分析](./core-features) — 初始設定、推理、網路策略、沙箱強化、CLI
- [Kubernetes 整合](./k8s-integration) — 在 K8s 環境中部署與使用 NemoClaw
:::
