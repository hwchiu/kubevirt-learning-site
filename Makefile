.PHONY: dev build preview install clean

# 安裝依賴
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
