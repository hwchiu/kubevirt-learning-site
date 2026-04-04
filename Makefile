.PHONY: dev build preview install clean setup check-deps init-submodules

# ============================================================
# 首次設置
# ============================================================

# 檢查必要工具
check-deps:
	@echo "🔍 檢查必要工具..."
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js 未安裝。請執行: brew install node"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm 未安裝。請先安裝 Node.js"; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "❌ git 未安裝。請執行: brew install git"; exit 1; }
	@echo "✅ 所有必要工具已安裝"

# 初始化 git submodules
init-submodules:
	@echo "📦 初始化 git submodules..."
	git submodule update --init --recursive
	@echo "✅ Submodules 已初始化"

# 首次完整設置（新專案 clone 後執行此目標）
setup: check-deps init-submodules install
	@echo ""
	@echo "🎉 專案設置完成！"
	@echo "   執行 make dev 啟動開發伺服器"
	@echo "   執行 make build 建置靜態網站"

# ============================================================
# 日常開發
# ============================================================

# 安裝 npm 依賴
install:
	npm install

# 本地開發伺服器（即時預覽）
dev:
	npm run dev

# 建置靜態網站
build:
	npm run build

# 預覽建置結果
preview: build
	npm run preview

# 清除建置快取
clean:
	rm -rf docs-site/.vitepress/dist docs-site/.vitepress/cache node_modules
