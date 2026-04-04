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
npm install -D vitepress
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
    "vitepress": "^1.6.4"
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

export default defineConfig({
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
  }
})
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

### 7. Add Submodules

```bash
git submodule add https://github.com/org/project-1.git project-1
```

## Adding a New Project

Follow the skill's core workflow:

```bash
# 1. Add submodule
git submodule add https://github.com/org/new-project.git new-project

# 2. Create docs directory
mkdir -p docs-site/new-project

# 3. Run the 5-phase analysis workflow (see SKILL.md)

# 4. Build and verify
make build
make preview
```
