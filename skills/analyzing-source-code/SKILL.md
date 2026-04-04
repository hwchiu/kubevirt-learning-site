---
name: analyzing-source-code
description: Use when adding a new open-source project to a documentation site for deep source code analysis, or when generating structured zh-TW documentation covering architecture, features, controllers, APIs, and integrations from a real codebase
---

# Analyzing Source Code

## Overview

A systematic, parallelized workflow for analyzing open-source project source code and generating comprehensive VitePress documentation in zh-TW. Every piece of documentation must reference real source files — **zero fabrication tolerance**.

**Core principle:** Read the code first, write the docs second. Every code block needs a file path. Every claim needs a source.

## When to Use

- Adding a new open-source project (git submodule) to the documentation site
- Performing deep source code analysis for any Kubernetes operator, Go project, or YAML-based project
- Generating structured, consistent documentation from a codebase
- Expanding an existing multi-project VitePress documentation site
- **「請根據最新版本分析」** — 觸發 Phase 6 增量更新流程（差異分析 → 局部更新受影響頁面）

**When NOT to use:**
- Quick README-level summaries (just read the README)
- Projects you don't have source access to
- Non-technical documentation

## Core Workflow

```dot
digraph workflow {
  rankdir=TB;
  node [shape=box, style=rounded];

  setup [label="Phase 1: Setup\n(submodule + dirs)"];
  explore [label="Phase 2: Explore\n(5 parallel agents)"];
  write [label="Phase 3: Write\n(4 parallel agents)"];
  integrate [label="Phase 4: Integrate\n(config + build)"];
  verify [label="Phase 5: Verify\n(build + preview)"];
  update [label="Phase 6: Update\n(version bump + re-analyze)"];

  setup -> explore -> write -> integrate -> verify;
  verify -> update [label="未來更新時", style=dashed];
}
```

### Phase 1: Setup (Sequential)

1. Add the project as a git submodule at the repo root
   - 確認目標 repo 的預設分支（可能是 `main`、`master`、`develop` 等）
   - 在 `.gitmodules` 中設定 `branch`，若使用者未指定則預設為 `main`
   ```bash
   git submodule add {repo-url} {project-name}
   # 確認預設分支
   git -C {project-name} remote show origin | grep 'HEAD branch'
   # 設定追蹤分支（使用實際的預設分支，非硬編碼 main）
   git config -f .gitmodules submodule.{project-name}.branch {actual-default-branch}
   ```
2. Create documentation directory: `docs-site/{project-name}/`
3. Create `index.md` with project overview and doc navigation table
4. Update `docs-site/.vitepress/config.js`:
   - Add sidebar array for the new project
   - Add to nav dropdown under "📦 專案"
   - Add sidebar route mapping

### Phase 2: Exploration (5 Parallel Agents)

Launch 5 `explore` agents simultaneously. Each agent must read **actual source files**, not just list directories.

See [exploration-prompts.md](./exploration-prompts.md) for the complete prompt templates.

| Agent | Focus | Key Files to Read |
|-------|-------|-------------------|
| **structure** | Project layout, binaries, packages, CRDs, build system | README.md, go.mod, Makefile, cmd/*, PROJECT |
| **controllers** | All controllers, registration order, reconcile loops | controllers/*, cmd/*/main.go, pkg/controller/* |
| **api-types** | CRD definitions, spec/status fields, all types | api/*, pkg/apis/*, staging/*/types.go |
| **features** | Key functionality, algorithms, data flows | pkg/*, internal/*, core business logic |
| **integrations** | External project references, auth, webhooks, RBAC | go.mod imports, config/rbac/*, *_webhook.go |

### Phase 2.5: Project Type Classification

**在探索結果回來後、撰寫文件前，必須先判定專案類型。** 類型決定 Phase 3 產生哪些頁面。

#### 判定流程

```dot
digraph classify {
  rankdir=TB;
  node [shape=diamond];
  has_ctrl [label="有 Reconcile()\n控制器？"];
  is_large [label="元件 ≥ 5 個\n或 CRD ≥ 10？"];
  has_metrics [label="核心產出是\nMetrics/Alerts？"];
  has_yaml [label="核心產出是\nYAML 資源定義？"];

  node [shape=box, style=rounded];
  type_large [label="大型平台"];
  type_operator [label="Controller Operator"];
  type_monitoring [label="監控型"];
  type_resource [label="資源定義型"];
  type_library [label="工具/函式庫"];

  has_ctrl -> is_large [label="Yes"];
  has_ctrl -> has_metrics [label="No"];
  is_large -> type_large [label="Yes"];
  is_large -> type_operator [label="No"];
  has_metrics -> type_monitoring [label="Yes"];
  has_metrics -> has_yaml [label="No"];
  has_yaml -> type_resource [label="Yes"];
  has_yaml -> has_webapp [label="No"];

  has_webapp [label="有 Django/Flask/Rails\nORM + REST API？"];
  node [shape=box, style=rounded];
  type_webapp [label="Web 應用平台"];

  has_webapp -> type_webapp [label="Yes"];
  has_webapp -> type_library [label="No"];
}
```

#### 類型與頁面對照表

| 專案類型 | 必要頁面 | 條件頁面 | 範例專案 |
|----------|----------|----------|----------|
| **Controller Operator** | architecture, core-features, integration | `controllers-api.md` | CDI, NMO |
| **大型平台** | architecture, core-features, integration | `controllers-api.md` + 可加 `lifecycle.md`, `api-reference.md` | Forklift, KubeVirt |
| **監控型** | architecture, core-features, integration | `metrics-alerts.md`（取代 controllers-api） | Monitoring |
| **資源定義型** | architecture, core-features, integration | `resource-catalog.md`（取代 controllers-api） | Common Instancetypes |
| **工具/函式庫** | architecture, core-features, integration | `cli-reference.md` 或 `api-reference.md` | kubectl 插件、SDK |
| **Web 應用平台** | architecture, core-features, integration | `data-models.md` + `api-reference.md` | NetBox |

#### 判定依據

| 信號 | 類型 |
|------|------|
| 有 `controllers/`、`Reconcile()` 函式、operator-sdk 結構 | Controller Operator |
| 元件 ≥ 5、CRD ≥ 10、多個 controller + REST API | 大型平台 |
| 核心產出為 PrometheusRule、AlertRule、Dashboard JSON、無 controller | 監控型 |
| 核心產出為 YAML/JSON 資源定義、Kustomize overlay、無 controller | 資源定義型 |
| 提供 CLI、SDK 或 library package、無 CRD | 工具/函式庫 |
| `apps.py` 橫跨多個 Django apps、`models.py` 含 50+ models、`serializers/`、`views/viewsets/`、REST framework、`urls.py` API routing、`templates/`、GraphQL schema | Web 應用平台 |

::: warning 根據專案類型選擇頁面模板
分類後請使用對應的頁面模板。條件頁面名稱與內容結構差異如下：
- **Controller Operator / 大型平台** → `controllers-api.md`：控制器、CRD 定義、Webhook、RBAC
- **監控型** → `metrics-alerts.md`：工具實作、指標目錄、告警規則、Dashboard
- **資源定義型** → `resource-catalog.md`：YAML 資源定義、分類目錄、Label 規範、驗證測試
- **工具/函式庫** → `cli-reference.md`：指令清單、參數、使用範例、Public API
- **Web 應用平台** → `data-models.md`：ORM 資料模型深度分析（ERD、Mixin 模式、Migration）；`api-reference.md`：REST API 與 GraphQL 端點完整參考
:::

### Conditional Analysis Dimensions

根據專案特性，探索與撰寫階段需額外涵蓋以下內容：

| 條件 | 額外分析內容 | 文件歸屬 |
|------|-------------|----------|
| 含有特殊演算法（排程、選擇策略、狀態機轉換） | 獨立區塊說明演算法邏輯、時間/空間複雜度、決策流程圖 | core-features.md |
| 提供 HTTP/gRPC API 供外部呼叫 | API endpoint 清單、Request/Response 結構、HTTP status codes、認證方式 | controllers-api.md |
| 含有 Webhook（Validating/Mutating） | Webhook 路徑、觸發資源、驗證規則、拒絕情境與錯誤訊息 | controllers-api.md |
| 使用狀態機（Phase/State transitions） | 完整狀態流轉圖（Mermaid stateDiagram）、觸發條件、錯誤狀態處理 | architecture.md |
| 含有 CLI 工具或子命令 | 指令清單、參數說明、使用範例 | core-features.md |
| 含有自定義 Metrics | Metric 名稱、類型、Labels、PromQL 範例 | integration.md |

#### 演算法分析格式

```markdown
## {演算法名稱}

### 問題定義

{這個演算法要解決什麼問題}

### 核心邏輯

\```go
// 檔案: pkg/path/to/algorithm.go
// 實際演算法程式碼
\```

### 決策流程

\```mermaid
flowchart TD
    A[輸入] --> B{條件判斷}
    B -->|情境 A| C[策略 A]
    B -->|情境 B| D[策略 B]
\```

### 複雜度與限制

| 面向 | 說明 |
|------|------|
| 時間複雜度 | O(n) / O(n log n) 等 |
| 限制條件 | {具體限制} |
| Fallback 策略 | {降級方案} |
```

#### API 分析格式

```markdown
## API Endpoints

### {HTTP Method} {Path}

**功能**: {說明}

**Request:**
\```json
{
  "field": "value"
}
\```

**Response:**

| HTTP Status | 說明 |
|-------------|------|
| 200 | 成功 |
| 400 | 請求格式錯誤 |
| 401 | 未認證（Token 過期或無效） |
| 403 | 權限不足 |
| 404 | 資源不存在 |
| 409 | 資源衝突 |
| 500 | 內部錯誤 |

**認證方式**: Bearer Token / ServiceAccount / mTLS

\```go
// 檔案: pkg/apiserver/handler.go
// 實際 handler 程式碼
\```
```

### Phase 3: Documentation Writing (3+1 Parallel Agents)

Launch agents to write markdown pages based on exploration findings. **第四頁依專案類型不同。**

See [doc-templates.md](./doc-templates.md) for the complete page templates.

#### 必要頁面（所有專案）

| Page | Content |
|------|---------|
| **architecture.md** | Project overview, system architecture (Mermaid), binary/tool table, directory structure, build system, state machines |
| **core-features.md** | Key features with real code snippets, processing pipelines, algorithms, configurations |
| **integration.md** | External integrations, auth mechanisms, RBAC, CI/CD, ecosystem connections |

#### 條件頁面（依專案類型選擇一個）

| 專案類型 | 條件頁面 | Content |
|----------|----------|---------|
| Controller Operator / 大型平台 | **controllers-api.md** | Controllers, CRD type definitions, webhooks, validation, REST API, HTTP status codes |
| 監控型 | **metrics-alerts.md** | Tool implementations, metrics catalog, alert rules, dashboard inventory, PromQL examples |
| 資源定義型 | **resource-catalog.md** | YAML resource definitions, type catalog, classification, label conventions, validation tests |
| 工具/函式庫 | **cli-reference.md** | Command list, parameters, usage examples, public API surface |
| Web 應用平台 | **data-models.md** | ORM 資料模型深度分析（ERD、Mixin 模式、Migration） |
| Web 應用平台 | **api-reference.md** | REST API 與 GraphQL 端點完整參考 |

### Phase 4: Site Integration (Sequential)

1. Update sidebar in `config.js` with all 5 entries (index + 4 pages)
2. Update `index.md` to link to all pages (remove any 🚧 placeholders)
3. Update homepage `docs-site/index.md` with new project card and table row

### Phase 5: Verification

1. Run `npm run build` — must succeed with zero errors
2. Run `npm run dev` — visually verify navigation and content
3. Git commit with descriptive message

## Documentation Standards

### Language
- All documentation in **zh-TW** (Traditional Chinese)
- Technical terms keep English originals (e.g., Controller, CRD, Webhook)
- Code comments remain in English

### Code References (Zero Fabrication Rule)
```markdown
// ✅ CORRECT — includes real file path
\```go
// 檔案: pkg/controller/clone/planner.go
func (p *Planner) ChooseStrategy(ctx context.Context) (*cdiv1.CDICloneStrategy, error) {
    // actual code from the file
}
\```

// ❌ WRONG — no file path, possibly fabricated
\```go
func handleClone() {
    // looks plausible but might not exist
}
\```
```

**Rules:**
- Every code block MUST include the source file path as a comment
- Use actual variable/function/type names from the source
- When showing partial code, indicate with `// ...` what's omitted
- Never invent functions, types, or behaviors

### VitePress Features
- **Mermaid diagrams** for architecture and state machines — **必須安裝 `vitepress-plugin-mermaid`**
  ```bash
  npm install vitepress-plugin-mermaid mermaid --save-dev
  ```
  ```js
  // config.js
  import { withMermaid } from 'vitepress-plugin-mermaid'
  export default withMermaid(defineConfig({ /* ... */ }))
  ```
- **`::: tip` / `::: info` / `::: warning`** containers for callouts
- **Tables** for structured data (binaries, CRDs, metrics, permissions)
- **Code blocks** with language syntax highlighting (go, yaml, bash, json)
- **⚠️ 注意**: `{{ }}` Go/GitHub Actions template syntax 在 code fence 外會被 Vue 解析而報錯，需改寫或使用 inline code

### Page Structure Template
```markdown
---
layout: doc
---

# {Page Title}

## 概述

Brief overview connecting this to the project's purpose.

## {Major Section}

### {Subsection}

\```go
// 檔案: path/to/real/file.go
actual code from the repository
\```

::: tip 重點
Key insight derived from the code analysis
:::

## 小結

Summary of what was covered and key takeaways.
```

## Quick Reference

| Step | Action | Parallelism | Tools |
|------|--------|-------------|-------|
| Setup | Submodule + directories + index.md | Sequential | git, create |
| Explore | 5 agents analyzing source code | All parallel | explore agent |
| Write | 4 documentation pages | All parallel | general-purpose agent |
| Integrate | Config + homepage + sidebar | Sequential | edit |
| Verify | Build + preview + commit | Sequential | bash |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Fabricating code that looks plausible | Always `view` or `grep` the actual file first |
| Missing file paths on code blocks | Add `// 檔案: path/to/file.go` as first comment line |
| Shallow directory listing without reading code | Read `main.go`, reconciler, types.go — not just `ls` |
| Copy-paste from README without verification | README can be outdated; verify against actual source |
| Assuming standard operator structure | Check first — some projects are YAML-based, tools, or libraries |
| Forgetting to update all 3 config points | Sidebar array + nav dropdown + sidebar route mapping |
| Not building before committing | Always `npm run build` to catch broken links or syntax |
| Missing `layout: doc` frontmatter | Every page must start with `---\nlayout: doc\n---` |
| Inconsistent page titles | Use `{Project} — {Topic}` format consistently |
| No cross-references between pages | Add `::: info 相關章節` box with links to sibling pages |
| `{{ }}` template syntax outside code fences | Vue interprets these — rewrite or wrap in code spans |

## Makefile Integration

The project Makefile should include these targets for first-time setup:

```makefile
# 首次完整設置
setup: check-deps init-submodules install

# 檢查必要工具
check-deps:
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js 未安裝"; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "❌ git 未安裝"; exit 1; }

# 初始化 git submodules
init-submodules:
	git submodule update --init --recursive

# 安裝 npm 依賴
install:
	npm install
```

## Local LLM Chat Integration

### Overview

文件網站在本地開發模式（`npm run dev`）下內建 AI 即時分析功能。透過 Vite dev plugin 攔截 `/api/chat` 請求，spawn `claude -p` CLI 並以 SSE 串流回傳結果。**Production build 完全不含此功能。**

### Architecture

```dot
digraph llm_chat {
  rankdir=LR;
  node [shape=box, style=rounded];

  browser [label="瀏覽器\nLocalChat.vue"];
  vite [label="Vite Dev Plugin\n/api/chat"];
  cli [label="claude -p\n(或 claude code router)"];
  source [label="Submodule\n原始碼"];
  docs [label="docs-site/\n分析文件"];

  browser -> vite [label="POST SSE"];
  vite -> cli [label="spawn"];
  cli -> source [label="--add-dir"];
  cli -> docs [label="--add-dir"];
  cli -> vite [label="JSON stdout"];
  vite -> browser [label="SSE events"];
}
```

### Three Components

| Component | Path | Purpose |
|-----------|------|---------|
| **Vite Plugin** | `.vitepress/plugins/localLlmChat.js` | Dev-only middleware, spawns CLI, returns SSE |
| **Vue Component** | `.vitepress/theme/components/LocalChat.vue` | Chat UI, drag-resize, auto-detect project |
| **Theme Extension** | `.vitepress/theme/index.js` | Mounts component in `layout-bottom` slot |

### Vite Plugin (`localLlmChat.js`)

- **Apply mode**: `'serve'` only — production build ignores it
- **Endpoint**: `POST /api/chat` with `{ project, question }` body
- **CLI invocation**: `claude -p "{prompt}" --add-dir {projectDir} --add-dir {docsDir} --output-format json --append-system-prompt "{system}" --model sonnet`
- **SSE events**: `status` → `result` / `error` → `done`, with heartbeat every 5s
- **Timeout**: 5 minutes (300s)
- **Compatible with**: `claude` (native) and `claude code router` (same CLI interface)

```javascript
// Plugin factory pattern
export function localLlmChatPlugin(options = {}) {
  const projectRoot = options.projectRoot || process.cwd()
  const cliCommand = options.cliCommand || 'claude'
  const defaultModel = options.model || 'sonnet'

  return {
    name: 'local-llm-chat',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/api/chat', async (req, res) => {
        // Parse POST body → build prompt → spawn CLI → stream SSE
      })
    },
  }
}
```

### Vue Component (`LocalChat.vue`)

#### Key Design Decisions

| Feature | Implementation |
|---------|---------------|
| **Dev-only** | `v-if="import.meta.env.DEV"` — tree-shaken in build |
| **Auto-detect project** | Parses `route.path` for known project slugs |
| **Drag-to-resize** | Top-left `nw-resize` handle with mouse + touch support |
| **Expand mode** | `⊞` button toggles 75vw / 85vh fullscreen-like panel |
| **SSE parsing** | `ReadableStream` reader with line-by-line event parsing |
| **Suggestion buttons** | Quick-start questions for common analysis queries |

#### Size & Constraints

| Property | Default | Expanded | Min | Max |
|----------|---------|----------|-----|-----|
| Width | 520px | 75vw (max 900px) | 360px | viewport - 60px |
| Height | 560px | 85vh | 350px | viewport - 100px |
| Font size | 14px | 14px | — | — |
| Line height | 1.7 | 1.7 | — | — |

### Theme Extension (`theme/index.js`)

```javascript
import DefaultTheme from 'vitepress/theme'
import LocalChat from './components/LocalChat.vue'
import { h } from 'vue'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'layout-bottom': () => h(LocalChat),
    })
  },
}
```

### Config Integration

```javascript
// docs-site/.vitepress/config.js
import { localLlmChatPlugin } from './plugins/localLlmChat.js'

export default withMermaid(defineConfig({
  // ...
  vite: {
    plugins: [
      localLlmChatPlugin({
        projectRoot: process.cwd(),
        cliCommand: 'claude',   // or any compatible CLI
        model: 'sonnet',
      }),
    ],
  },
  // ...
}))
```

### System Prompt Design

CLI 收到的 system prompt 包含：
1. 角色定義：原始碼分析助手，專精 KubeVirt 生態系
2. 語言指示：zh-TW 回答，技術術語保持英文
3. 引用規範：回答須引用檔案路徑與程式碼
4. 誠實原則：不確定就說明，不猜測

Context hint 根據 `project` 參數動態指定目標目錄：
```
請基於 ./{project}/ 目錄下的原始碼以及 ./docs-site/{project}/ 的分析文件來回答。
```

---

## Phase 6: 增量更新（觸發語：「請根據最新版本分析」）

當使用者說「**請根據最新版本分析**」或類似語句時，執行以下完整流程。**不是重新全寫，而是差異驅動的增量更新。**

### 6.1 版本追蹤機制

專案根目錄的 `versions.json` 記錄每個專案的：
- `analyzed_commit` — 上次分析時的 git commit SHA
- `analyzed_date` — 分析日期
- `pages` → `source_paths` — 每個文件頁面對應的 source 目錄映射

### 6.2 增量更新流程

```dot
digraph incremental_update {
  rankdir=TB;
  node [shape=box, style=rounded];

  pull [label="Step 1: 拉取最新 code\nmake update-submodules"];
  check [label="Step 2: 差異檢查\nscripts/check-updates.sh"];
  decide [label="Step 3: 判斷影響範圍" shape=diamond];
  skip [label="無需更新\n僅更新 submodule commit"];
  partial [label="Step 4a: 局部更新\n只重寫受影響頁面"];
  full [label="Step 4b: 完整更新\n重跑 Phase 2→5"];
  stamp [label="Step 5: 更新版本標記\nversions.json + index.md"];
  verify [label="Step 6: 驗證\nmake build"];
  commit [label="Step 7: 提交"];

  pull -> check -> decide;
  decide -> skip [label="CI/測試/文件"];
  decide -> partial [label="新功能/新 API"];
  decide -> full [label="架構重構"];
  partial -> stamp;
  full -> stamp;
  skip -> commit;
  stamp -> verify -> commit;
}
```

#### Step 1: 拉取最新 code

```bash
# 更新所有專案
make update-submodules

# 或更新單一專案
make check-update-project PROJECT=netbox
```

#### Step 2: 自動差異分析

```bash
# 自動執行 — 比對 versions.json 中的 analyzed_commit vs submodule HEAD
make check-updates
```

腳本會輸出：
- 每個專案的新 commit 數量與摘要
- 變更檔案統計
- **受影響的文件頁面**（基於 `versions.json` 中的 `source_paths` 映射）

#### Step 3: 判斷更新範圍

根據 check-updates 報告決定處理方式：

| 變更類型 | 判斷依據 | 動作 |
|---------|---------|------|
| **無需更新** | 僅 CI/CD、README、測試、文件格式變更 | 跳過，直接更新 submodule commit |
| **局部更新** | 新增 API、新增 Model、新增 Controller、功能增強 | 只對受影響頁面執行 explore + write |
| **完整更新** | 架構重構、大版本升級（如 Django 5→6）、核心元件重寫 | 完整重跑 Phase 2→5 |

#### Step 4a: 局部更新（最常見）

只針對受影響的頁面重新分析：

1. 根據報告中列出的受影響頁面，啟動對應的 explore agent
2. explore agent 重點閱讀**變更的檔案**，而非整個專案
3. 將分析結果**合併更新**到現有文件中（不是整頁重寫）
4. 新增的功能/API/Model → 新增章節
5. 修改的邏輯 → 更新對應段落
6. 刪除的功能 → 移除對應說明

**Explore agent 的差異分析提示詞模板：**
```
專案 {project} 從 {old_commit} 更新至 {new_commit}。
以下是本次變更涉及的檔案：
{changed_files_list}

請分析這些變更對 {page_name} 頁面的影響：
1. 是否有新增的功能/API/模型需要記錄？
2. 是否有修改的行為需要更新描述？
3. 是否有移除的功能需要從文件中刪除？
4. 現有文件中哪些程式碼片段需要更新？

請引用具體的檔案路徑與程式碼。
```

#### Step 4b: 完整更新

等同於新專案分析，完整執行 Phase 2→5。

#### Step 5: 更新版本標記

更新完成後，**必須同步更新**：

1. `versions.json` — 更新 `analyzed_commit` 和 `analyzed_date`
2. `docs-site/{project}/index.md` — 更新 `::: tip 分析版本` 區塊

```bash
# versions.json 範例更新
{
  "analyzed_commit": "{new-full-sha}",
  "analyzed_date": "2026-05-01"
}
```

```markdown
::: tip 分析版本
本文件基於 commit [`{new-short-sha}`]({repo-url}/commit/{new-full-sha}) 進行分析。
:::
```

#### Step 6-7: 驗證與提交

```bash
make build
git add -A && git commit -m "docs({project}): update analysis to {new-short-sha}"
```

### 6.3 Makefile 指令速查

| 指令 | 用途 |
|------|------|
| `make submodule-status` | 查看所有 submodule 目前版本 |
| `make update-submodules` | 更新所有 submodule 至最新 commit |
| `make check-updates` | 更新 + 自動差異分析報告 |
| `make check-update-project PROJECT=xxx` | 單一專案更新 + 差異分析 |
