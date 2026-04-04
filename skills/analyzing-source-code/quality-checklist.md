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

### controllers-api.md
- [ ] Controller/tool registration documented
- [ ] Reconcile flow or main logic flow documented
- [ ] Full CRD type definitions (Go structs) shown
- [ ] Webhook validation rules documented
- [ ] RBAC permissions table
- [ ] Test architecture overview

### integration.md
- [ ] Primary ecosystem integration documented
- [ ] Auth/RBAC mechanisms explained
- [ ] CI/CD workflows documented
- [ ] Usage examples from config/samples/
- [ ] Integration architecture diagram (Mermaid)

## Cross-Page Checks

- [ ] All pages use consistent title format: `{Project} — {Topic}`
- [ ] All pages have `layout: doc` frontmatter
- [ ] All pages have `::: info 相關章節` cross-reference box linking to sibling pages
- [ ] No broken internal links
- [ ] No `{{ }}` Go/GitHub Actions template syntax outside code fences (Vue will fail)
- [ ] VitePress sidebar has all 5 entries (index + 4 pages)
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
