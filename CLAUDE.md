# CLAUDE.md — Kubernetes Learning Site

## 什麼是這個專案

這是一個 **多專案 Kubernetes 技術文件網站**，使用 VitePress 建置，內容以繁體中文（zh-TW）撰寫，專注於從原始碼深度分析各種 Kubernetes 周邊專案，並附帶互動式測驗讓工程師自我評測。

**目前涵蓋專案：**
KubeVirt、CDI（Containerized Data Importer）、Forklift、Node Maintenance Operator、Multus CNI、NetBox、Monitoring（Prometheus/Alertmanager）

## 技能模組（Skills）

本專案所有工作流程皆封裝為 skills，位於 `skills/` 目錄：

| Skill | 用途 |
|-------|------|
| `skills/analyzing-source-code/` | 加入新專案的完整分析流程（含 Structure Planner）|
| `skills/quiz-generation/` | 從現有文件產生互動式測驗題目 |
| `skills/fireworks-tech-graph/` | 產生文件用靜態 SVG/PNG 技術圖表 |

**遇到任何任務，先閱讀對應 skill 的 `SKILL.md`，再開始執行。**

## 關鍵技術慣例

### VitePress 建置
```bash
npm run build        # 建置（= vitepress build docs-site）
npm run dev          # 開發伺服器
```
- 建置失敗時先檢查 dead link 和 Vue template 語法錯誤
- 所有 `.md` 中的 `{{ }}` 必須寫成 `&#123;&#123;` / `&#125;&#125;`（VitePress 會把 `{{ }}` 當成 Vue template）

### 文件格式規範
每個 `.md` 頁面：
```yaml
---
layout: doc
title: {專案} — {主題}
---
```
- 使用 `::: info 相關章節` 區塊放置跨頁連結
- 所有文件內容使用**繁體中文**
- **不要新增 Mermaid**
- 所有圖表預設改用 `skills/fireworks-tech-graph/` 產生 **靜態 SVG/PNG**
- 圖檔放在 `docs-site/public/diagrams/{project}/`
- 文件內以 `![圖說](/diagrams/{project}/{name}.png)` 引用
- 若需要產圖腳本，統一放在 `scripts/diagram-generators/`，不要再放 repo root

### Vue 元件 — QuizQuestion
```vue
<QuizQuestion
  question="1. 題目文字"
  :options='[
    "選項 A",
    "選項 B",
    "選項 C",
    "選項 D",
  ]'
  :answer="0"
  explanation="解釋文字..."
/>
```

**嚴格限制（違反會導致 build 失敗）：**
- `:options='[...]'` 外層用單引號、內層字串用雙引號
- `:options` 內**禁止** HTML entities（`&quot;`、`&apos;` 等）— 內層要表示雙引號用 `\\"` 
- `question=` 和 `explanation=` 內的雙引號用 `&quot;`
- `:answer` 是 **0-indexed**（第一個選項為 0）
- `/>` 必須獨立成一行

### Sidebar 設定
新增頁面後，必須更新 `docs-site/.vitepress/config.js` 的對應 sidebar array。

### Vue 元件匯入（quiz 頁面 header）
```vue
<script setup>
import QuizQuestion from '../.vitepress/theme/components/QuizQuestion.vue'
</script>
```

## 目錄結構

```
kubevirt-learning-site/
├── CLAUDE.md              ← 你在這裡
├── docs-site/
│   ├── .vitepress/
│   │   ├── config.js      ← Sidebar + VitePress 設定
│   │   └── theme/
│   │       └── components/
│   │           └── QuizQuestion.vue
│   ├── {project}/
│   │   ├── index.md       ← 專案首頁 + 文件導覽表
│   │   ├── quiz.md        ← 互動式測驗（QuizQuestion 元件）
│   │   └── {topic}/       ← 各主題子目錄
│   │       └── *.md
│   └── index.md           ← 網站首頁
├── {project}/             ← git submodule（原始碼）
├── scripts/               ← 版本追蹤、差異分析、圖表產生腳本
│   └── diagram-generators/← 靜態圖表 generator（Python）
├── skills/                ← Claude Code workflow skills
├── versions.json          ← 各專案已分析的 commit 版本記錄
└── Makefile               ← 常用指令（submodule 更新、版本比對等）
```

## 常用操作

### 加入新專案
→ 使用 `skills/analyzing-source-code/SKILL.md` 的完整流程

### 產生團隊測驗
→ 使用 `skills/quiz-generation/SKILL.md` 的流程

### 重繪或新增圖表
→ 使用 `skills/fireworks-tech-graph/SKILL.md`，輸出靜態 SVG/PNG，不使用 Mermaid

### 更新現有專案文件
```bash
make check-updates           # 查看哪些專案有新版本
make check-update-project PROJECT=kubevirt  # 單一專案差異分析
```

### 建置驗證
```bash
npm run build
# 如果失敗，看錯誤行號，去 quiz.md 或相關 .md 找語法問題
```

## Git 提交規範

```
docs({project}): {description}

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```
