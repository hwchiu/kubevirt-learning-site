# VitePress Project Setup Guide

How to set up a new documentation site project from scratch using this skill's workflow.

## Prerequisites

- Node.js >= 18
- npm
- git

## Initial Setup

### 1. Initialize Project

```bash
mkdir my-analysis-site && cd my-analysis-site
git init
npm init -y
npm install -D vitepress vitepress-plugin-mermaid mermaid
```

### 2. Create package.json Scripts

```json
{
  "name": "my-analysis-site",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vitepress dev docs-site",
    "build": "vitepress build docs-site",
    "preview": "vitepress preview docs-site"
  },
  "devDependencies": {
    "mermaid": "^11.0.0",
    "vitepress": "^1.6.4",
    "vitepress-plugin-mermaid": "^2.0.0"
  }
}
```

### 3. Create Makefile

```makefile
.PHONY: dev build preview install clean setup check-deps init-submodules

# ============================================================
# 首次設置
# ============================================================

check-deps:
	@echo "🔍 檢查必要工具..."
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js 未安裝。請執行: brew install node"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm 未安裝。請先安裝 Node.js"; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "❌ git 未安裝。請執行: brew install git"; exit 1; }
	@echo "✅ 所有必要工具已安裝"

init-submodules:
	@echo "📦 初始化 git submodules..."
	git submodule update --init --recursive
	@echo "✅ Submodules 已初始化"

setup: check-deps init-submodules install
	@echo ""
	@echo "🎉 專案設置完成！"
	@echo "   執行 make dev 啟動開發伺服器"
	@echo "   執行 make build 建置靜態網站"

# ============================================================
# 日常開發
# ============================================================

install:
	npm install

dev:
	npm run dev

build:
	npm run build

preview: build
	npm run preview

clean:
	rm -rf docs-site/.vitepress/dist docs-site/.vitepress/cache node_modules
```

### 4. Create VitePress Config

```javascript
// docs-site/.vitepress/config.js
import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

// Define sidebar arrays per project
const project1Sidebar = [
  {
    text: '📖 Project 1 總覽',
    items: [
      { text: '專案簡介', link: '/project-1/' },
      { text: '系統架構', link: '/project-1/architecture' },
      { text: '核心功能分析', link: '/project-1/core-features' },
      { text: '控制器與 API', link: '/project-1/controllers-api' },
      { text: '外部整合', link: '/project-1/integration' },
    ]
  },
]

export default withMermaid(defineConfig({
  base: '/my-analysis-site/',
  title: '原始碼分析',
  description: '開源專案原始碼深度分析',
  lang: 'zh-TW',
  themeConfig: {
    nav: [
      { text: '🏠 首頁', link: '/' },
      {
        text: '📦 專案',
        items: [
          { text: 'Project 1', link: '/project-1/' },
        ]
      },
    ],
    sidebar: {
      '/project-1/': project1Sidebar,
    },
    search: { provider: 'local' },
    outline: { label: '本頁目錄', level: [2, 3] },
    docFooter: { prev: '上一頁', next: '下一頁' },
    lastUpdated: { text: '最後更新' }
  },
  mermaid: {
    theme: 'default'
  }
}))
```

### 5. Create Homepage

```markdown
<!-- docs-site/index.md -->
---
layout: home

hero:
  name: "專案名稱"
  text: "原始碼深度分析"
  tagline: 深入剖析各專案的架構設計、核心元件與實作細節
  actions:
    - theme: brand
      text: 📘 開始閱讀
      link: /project-1/

features:
  - icon: 📦
    title: Project 1
    details: 專案描述
    link: /project-1/
    linkText: 開始閱讀
---
```

### 6. Create .gitignore

```
node_modules/
docs-site/.vitepress/dist/
docs-site/.vitepress/cache/
```

### 7. Setup Local LLM Chat (Dev Mode)

建立三個檔案，讓 `npm run dev` 時自動啟用 AI 即時分析：

#### 7a. Vite Plugin

```javascript
// docs-site/.vitepress/plugins/localLlmChat.js
import { spawn } from 'child_process'
import { resolve } from 'path'

export function localLlmChatPlugin(options = {}) {
  const projectRoot = options.projectRoot || process.cwd()
  const cliCommand = options.cliCommand || 'claude'
  const defaultModel = options.model || 'sonnet'

  return {
    name: 'local-llm-chat',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/api/chat', async (req, res) => {
        if (req.method !== 'POST') {
          res.writeHead(405, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ error: 'Method not allowed' }))
          return
        }

        let body = ''
        for await (const chunk of req) body += chunk
        const { project, question } = JSON.parse(body)

        const systemPrompt = [
          '你是一個專業的原始碼分析助手。',
          '請用 zh-TW（繁體中文）回答，技術術語保持英文。',
          '回答時請引用具體的檔案路徑與程式碼片段。',
          '如果不確定，請誠實說明而非猜測。',
        ].join('\n')

        const contextHint = project
          ? `請基於 ./${project}/ 目錄下的原始碼以及 ./docs-site/${project}/ 的分析文件來回答。`
          : '請基於整個專案來回答。'

        const args = [
          '-p', `${contextHint}\n\n使用者問題：${question}`,
          '--append-system-prompt', systemPrompt,
          '--output-format', 'json',
          '--model', defaultModel,
        ]

        if (project) {
          args.push('--add-dir', resolve(projectRoot, project))
          args.push('--add-dir', resolve(projectRoot, 'docs-site', project))
        }

        // SSE response
        res.writeHead(200, {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        })

        const heartbeat = setInterval(() => res.write('event: ping\ndata: {}\n\n'), 5000)
        res.write(`event: status\ndata: ${JSON.stringify({ status: 'thinking', message: '正在分析原始碼...' })}\n\n`)

        try {
          const result = await new Promise((resolve, reject) => {
            const child = spawn(cliCommand, args, { cwd: projectRoot, stdio: ['ignore', 'pipe', 'pipe'], timeout: 300000 })
            let stdout = ''
            child.stdout.on('data', d => stdout += d)
            child.on('close', code => {
              if (code !== 0) return reject(new Error(`Exit code ${code}`))
              try { resolve(JSON.parse(stdout).result || stdout) } catch { resolve(stdout.trim()) }
            })
            child.on('error', reject)
          })
          res.write(`event: result\ndata: ${JSON.stringify({ result })}\n\n`)
        } catch (err) {
          res.write(`event: error\ndata: ${JSON.stringify({ error: err.message })}\n\n`)
        } finally {
          clearInterval(heartbeat)
          res.write('event: done\ndata: {}\n\n')
          res.end()
        }
      })
    },
  }
}
```

#### 7b. Theme Extension

```javascript
// docs-site/.vitepress/theme/index.js
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

#### 7c. Chat Component

建立 `docs-site/.vitepress/theme/components/LocalChat.vue`：

- 使用 `import.meta.env.DEV` 條件渲染（production build 不含）
- 自動從 `route.path` 偵測當前專案
- 支援 drag-to-resize（左上角拖曳把手）和 expand 按鈕
- SSE 串流解析，顯示 thinking → result
- 預設寬度 520px，可拖曳至 360px–viewport

> 完整程式碼較長（~500 行），建議直接從參考專案複製 `LocalChat.vue` 作為起點。

#### 7d. Register Plugin in Config

```javascript
// docs-site/.vitepress/config.js
import { localLlmChatPlugin } from './plugins/localLlmChat.js'

export default withMermaid(defineConfig({
  // ...existing config...
  vite: {
    plugins: [
      localLlmChatPlugin({
        projectRoot: process.cwd(),
        cliCommand: 'claude',   // 支援 claude code router
        model: 'sonnet',
      }),
    ],
  },
  // ...
}))
```

### 8. Add Submodules

```bash
git submodule add https://github.com/org/project-1.git project-1

# 確認 repo 的預設分支（不一定是 main，可能是 master、develop 等）
git -C project-1 remote show origin | grep 'HEAD branch'

# 設定追蹤分支（使用實際的預設分支）
# 若使用者未指定特定 branch，預設使用 main
git config -f .gitmodules submodule.project-1.branch main
```

> **注意：** 每個 repo 的預設分支可能不同（main / master / develop），加入 submodule 時務必確認並正確設定 `.gitmodules` 中的 `branch` 欄位。

## Adding a New Project

Follow the skill's core workflow:

```bash
# 1. Add submodule
git submodule add https://github.com/org/new-project.git new-project

# 2. 確認預設分支並設定追蹤
DEFAULT_BRANCH=$(git -C new-project remote show origin | grep 'HEAD branch' | awk '{print $NF}')
git config -f .gitmodules submodule.new-project.branch "$DEFAULT_BRANCH"
echo "追蹤分支: $DEFAULT_BRANCH"

# 3. Create docs directory
mkdir -p docs-site/new-project

# 4. Run the 5-phase analysis workflow (see SKILL.md)

# 5. Build and verify
make build
make preview
```
