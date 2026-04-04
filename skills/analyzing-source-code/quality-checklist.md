# Quality Checklist

Use this checklist to verify documentation quality before committing.

## Per-Page Checks

### architecture.md
- [ ] Project overview with accurate Go/language version from go.mod
- [ ] Mermaid system architecture diagram
- [ ] Binary/tool table with paths and descriptions
- [ ] Directory structure with 2-level depth for key dirs
- [ ] Build system documentation (Makefile targets + CI/CD)
- [ ] CRD summary table (if applicable)
- [ ] State machine diagram (if applicable)

### core-features.md
- [ ] At least 3 major features documented
- [ ] Every feature has real code snippets with file paths
- [ ] Processing flow diagrams (Mermaid sequence/flowchart)
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
- [ ] 至少包含 2 張 Mermaid ERD（如 DCIM、IPAM 等主要領域）
- [ ] 核心模型分析包含 field 數量、relationship 數量、自訂 clean/save 邏輯
- [ ] Mixin 模式分析包含程式碼片段與使用範例
- [ ] Migration 慣例與命名規則有說明
- [ ] 所有程式碼區塊包含 `# 檔案:` 路徑註解

### api-reference.md (Web 應用平台 only)
- [ ] REST API 端點總覽表按 App 分類列出
- [ ] ViewSet 繼承架構有 Mermaid 類別圖
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
- [ ] Integration architecture diagram (Mermaid)
- [ ] **IF 有自定義 Metrics**: Metric 名稱、類型、Labels、PromQL 範例

## Cross-Page Checks

- [ ] All pages use consistent title format: `{Project} — {Topic}`
- [ ] All pages have `layout: doc` frontmatter
- [ ] All pages have `::: info 相關章節` cross-reference box linking to sibling pages
- [ ] No broken internal links
- [ ] No `{{ }}` Go/GitHub Actions template syntax outside code fences (Vue will fail)
- [ ] VitePress sidebar entries match actual page files (條件頁面名稱依專案類型而異)
- [ ] Nav dropdown includes the project
- [ ] Homepage features card and table row updated
- [ ] `npm run build` succeeds with no errors

## Zero-Fabrication Verification

For a random sample of 5 code blocks across all pages:
- [ ] Verify file path exists in the submodule
- [ ] Verify function/type name matches source
- [ ] Verify code logic is accurate (not paraphrased incorrectly)

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
