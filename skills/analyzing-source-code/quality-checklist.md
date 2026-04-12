# Quality Checklist

Use this checklist to verify documentation quality before committing.

## Per-Page Checks

### index.md
- [ ] 有分析版本資訊（commit SHA / 版本）
- [ ] 有專案資訊表（repo、語言、授權、專案類型）
- [ ] 有文件導覽表，列出所有主要頁面與用途
- [ ] **若頁面數量 ≥ 6 或已有多 Section**：有明確的「建議閱讀順序」
- [ ] 有 `::: info` 類型的快速跳轉，讓讀者可依目標直接進入對應頁面
- [ ] **若建立 `learning-path/`**：index.md 有入口，且說明該路徑適合哪種讀者

### architecture.md
- [ ] Project overview with accurate Go/language version from go.mod
- [ ] 至少 1 張靜態系統架構圖（SVG/PNG，使用 `/diagrams/...` 引用）
- [ ] Binary/tool table with paths and descriptions
- [ ] Directory structure with 2-level depth for key dirs
- [ ] Build system documentation (Makefile targets + CI/CD)
- [ ] CRD summary table (if applicable)
- [ ] State machine diagram (if applicable)

### core-features.md
- [ ] At least 3 major features documented
- [ ] Every feature has real code snippets with file paths
- [ ] Processing flow diagrams exist as static SVG/PNG assets
- [ ] `::: tip` containers for key insights
- [ ] No fabricated code — all snippets verified against source
- [ ] **IF 含演算法**: 獨立區塊含問題定義、核心邏輯程式碼、決策流程圖、複雜度分析
- [ ] **IF 含 CLI 工具**: 指令清單、參數說明、使用範例

### controllers-api.md (Controller Operator / 大型平台 only)
- [ ] Controller/tool registration documented
- [ ] Reconcile flow or main logic flow documented
- [ ] Full CRD type definitions (Go structs) shown
- [ ] Webhook validation rules documented
- [ ] RBAC permissions table
- [ ] Test architecture overview
- [ ] **IF 提供 HTTP/gRPC API**: Endpoint 清單、Request/Response 結構、HTTP status codes、認證方式
- [ ] **IF 有 Webhook**: 路徑、觸發資源、驗證規則、拒絕情境與錯誤訊息

### metrics-alerts.md (監控型 only)
- [ ] Tool implementations with real code
- [ ] Metrics catalog table (name, type, labels, description)
- [ ] PromQL query examples
- [ ] Alert rules with severity, condition, runbook links
- [ ] Dashboard inventory

### resource-catalog.md (資源定義型 only)
- [ ] Resource type overview table (Kind, API Group, Scope)
- [ ] Category/series classification with specs
- [ ] Real YAML resource definitions
- [ ] Label and annotation conventions
- [ ] Kustomize build structure
- [ ] Validation test architecture

### data-models.md (Web 應用平台 only)
- [ ] 模型總覽表包含所有 Django App 及其模型數量
- [ ] 至少包含 2 張靜態 ERD（如 DCIM、IPAM 等主要領域）
- [ ] 核心模型分析包含 field 數量、relationship 數量、自訂 clean/save 邏輯
- [ ] Mixin 模式分析包含程式碼片段與使用範例
- [ ] Migration 慣例與命名規則有說明
- [ ] 所有程式碼區塊包含 `# 檔案:` 路徑註解

### api-reference.md (Web 應用平台 only)
- [ ] REST API 端點總覽表按 App 分類列出
- [ ] ViewSet 繼承架構有靜態類別圖（SVG/PNG）
- [ ] Serializer 架構有程式碼範例
- [ ] 認證方式（Token、Session、LDAP 等）有完整說明
- [ ] HTTP 狀態碼對照表包含所有常見回應碼
- [ ] 若有 GraphQL 則包含 Schema 定義與查詢範例
- [ ] FilterSet 與查詢參數有範例說明
- [ ] 所有程式碼區塊包含 `# 檔案:` 路徑註解

### integration.md
- [ ] Primary ecosystem integration documented
- [ ] Auth/RBAC mechanisms explained
- [ ] CI/CD workflows documented
- [ ] Usage examples from config/samples/
- [ ] Integration architecture diagram exists as static SVG/PNG
- [ ] **IF 有自定義 Metrics**: Metric 名稱、類型、Labels、PromQL 範例

## Cross-Page Checks

- [ ] All pages use consistent title format: `{Project} — {Topic}`
- [ ] All pages have `layout: doc` frontmatter
- [ ] All pages have `::: info 相關章節` cross-reference box linking to sibling pages
- [ ] 專案總覽頁（index.md）本身就能扮演最基本的學習導覽入口
- [ ] 若有 `learning-path/`，內容是**導讀層**而非重複貼上技術文件
- [ ] quiz index（若存在）中的「建議學習路徑」需與技術文件閱讀順序一致
- [ ] 文件內不新增 Mermaid，圖表一律引用 `docs-site/public/diagrams/...` 靜態資產
- [ ] No broken internal links
- [ ] No `{{ }}` Go/GitHub Actions template syntax outside code fences (Vue will fail)
- [ ] VitePress sidebar entries match actual page files (條件頁面名稱依專案類型而異)
- [ ] Nav dropdown includes the project
- [ ] Homepage features card and table row updated
- [ ] `npm run build` succeeds with no errors

## Zero-Fabrication Verification

**這是強制步驟，不得略過。** 提交前必須系統性驗證所有原始碼引用。

### 步驟一：列出所有程式碼區塊的 file path

```bash
# 從所有文件中提取 // 檔案: 註解
grep -r "// 檔案:" docs-site/{project}/ --include="*.md"
```

確認每個 code block 都有對應的 `// 檔案:` 行。若有遺漏，補上路徑或移除該程式碼區塊。

### 步驟二：驗證每個引用路徑確實存在

```bash
# 對每個出現的路徑，確認檔案存在於 submodule
ls {project}/path/to/cited/file.go
```

若路徑不存在，代表程式碼區塊內容是捏造的，**必須刪除或用真實路徑替換**。

### 步驟三：驗證關鍵函數/類型名稱

針對文件中每個明確提及的函數名稱、類型名稱、常數名稱，在原始碼中確認存在：

```bash
# 確認函數名稱
grep -r "func.*FunctionName" {project}/

# 確認類型定義
grep -r "type TypeName " {project}/

# 確認常數/欄位名稱
grep -rn "ConstantName" {project}/
```

**任何 grep 無結果的名稱，必須從文件中刪除或替換為真實存在的名稱。**

### 步驟四：抽查 5 個程式碼區塊

從所有頁面中隨機選取至少 5 個程式碼區塊，完整執行：

- [ ] 確認 file path 存在於 submodule
- [ ] 確認函數/類型名稱與原始碼完全相符（大小寫、拼寫）
- [ ] 確認程式碼邏輯與原始碼語意一致（非改寫或臆測）

### 快速檢查腳本

```bash
# 找出所有沒有 // 檔案: 的 code block（潛在捏造風險）
python3 -c "
import re, sys, glob
files = glob.glob('docs-site/{project}/**/*.md', recursive=True)
issues = []
for f in files:
    content = open(f).read()
    # 找到所有 go/python/bash code block
    blocks = re.finditer(r'\`\`\`(?:go|python|bash|yaml)\n(.*?)\`\`\`', content, re.DOTALL)
    for m in blocks:
        if '// 檔案:' not in m.group(1) and '# 檔案:' not in m.group(1):
            line = content[:m.start()].count('\n') + 1
            issues.append(f'{f}:{line} — missing file path')
for i in issues:
    print(i)
print(f'Total issues: {len(issues)}')
"
```

## Common Build Issues

| Issue | Fix |
|-------|-----|
| `promql` language not loaded | Non-blocking; VitePress falls back to txt |
| Chunk size >500KB warning | Non-blocking; large pages are expected |
| Dead links in build output | Fix the link in the markdown file |
| Missing sidebar route | Add `'/{project}/': projectSidebar` to config.js |

## Local LLM Chat Checks

### Plugin (`localLlmChat.js`)
- [ ] `apply: 'serve'` — must NOT run in production build
- [ ] POST `/api/chat` endpoint accepts `{ project, question }` body
- [ ] Spawns CLI with `--add-dir` for both project source and docs directories
- [ ] SSE response with `status`, `result`/`error`, and `done` events
- [ ] Heartbeat interval (5s) to prevent connection timeout
- [ ] 5-minute process timeout to avoid hanging
- [ ] CORS headers for `OPTIONS` preflight

### Component (`LocalChat.vue`)
- [ ] `v-if="import.meta.env.DEV"` — zero chat UI in production
- [ ] Auto-detects current project from route path
- [ ] All known project slugs listed in `projects` array
- [ ] Drag-to-resize with min/max bounds (360×350 → viewport)
- [ ] Touch support for mobile resize
- [ ] Expand button (`⊞`/`⊟`) toggles large panel mode
- [ ] SSE stream parsing handles all event types
- [ ] Error state displays user-friendly message
- [ ] Suggestion buttons for common queries

### Theme Extension (`theme/index.js`)
- [ ] Extends `DefaultTheme` (not replaces)
- [ ] Mounts `LocalChat` in `layout-bottom` slot only
- [ ] No other slot overrides unless explicitly needed

### Config Integration
- [ ] `localLlmChatPlugin` imported and registered in `vite.plugins`
- [ ] `projectRoot` points to repository root (where submodules live)
- [ ] `cliCommand` matches environment (`claude` or custom path)
- [ ] `npm run build` succeeds — plugin is skipped in production
- [ ] `npm run dev` shows 🤖 button in bottom-right corner
