#!/usr/bin/env bash
# check-updates.sh — 比對 versions.json 中的分析版本與 submodule 最新 commit
# 用法: ./scripts/check-updates.sh [project-name]
# 不帶參數時檢查所有專案

set -euo pipefail

VERSIONS_FILE="versions.json"
RESET="\033[0m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
CYAN="\033[36m"
BOLD="\033[1m"

if [ ! -f "$VERSIONS_FILE" ]; then
  echo -e "${RED}❌ 找不到 $VERSIONS_FILE${RESET}"
  exit 1
fi

# 取得所有專案名稱或使用指定的專案
if [ $# -gt 0 ]; then
  PROJECTS="$1"
else
  PROJECTS=$(python3 -c "
import json
with open('$VERSIONS_FILE') as f:
    data = json.load(f)
for p in data['projects']:
    print(p)
")
fi

HAS_UPDATES=false

echo -e "${BOLD}📋 文件更新檢查報告${RESET}"
echo "========================================"
echo ""

for PROJECT in $PROJECTS; do
  # 讀取分析時的 commit
  ANALYZED_COMMIT=$(python3 -c "
import json
with open('$VERSIONS_FILE') as f:
    data = json.load(f)
print(data['projects']['$PROJECT']['analyzed_commit'])
")

  # 取得 submodule 目前的 HEAD commit
  if [ ! -d "$PROJECT/.git" ] && [ ! -f "$PROJECT/.git" ]; then
    echo -e "${RED}⚠️  $PROJECT: submodule 未初始化${RESET}"
    continue
  fi

  CURRENT_COMMIT=$(git -C "$PROJECT" rev-parse HEAD)

  if [ "$ANALYZED_COMMIT" = "$CURRENT_COMMIT" ]; then
    echo -e "${GREEN}✅ $PROJECT: 無變更（版本一致）${RESET}"
    continue
  fi

  HAS_UPDATES=true
  SHORT_OLD="${ANALYZED_COMMIT:0:8}"
  SHORT_NEW="${CURRENT_COMMIT:0:8}"

  # 計算 commit 數量
  COMMIT_COUNT=$(git -C "$PROJECT" rev-list --count "$ANALYZED_COMMIT".."$CURRENT_COMMIT" 2>/dev/null || echo "?")

  echo -e "${YELLOW}🔄 $PROJECT: 有 ${COMMIT_COUNT} 個新 commit${RESET}"
  echo -e "   分析版本: ${SHORT_OLD}  →  最新版本: ${SHORT_NEW}"
  echo ""

  # 顯示 commit 摘要（最多 15 條）
  echo -e "   ${CYAN}最近 commit:${RESET}"
  git -C "$PROJECT" log --oneline "$ANALYZED_COMMIT".."$CURRENT_COMMIT" | head -15 | while read -r line; do
    echo "     $line"
  done

  TOTAL_COMMITS=$(git -C "$PROJECT" rev-list --count "$ANALYZED_COMMIT".."$CURRENT_COMMIT" 2>/dev/null || echo "0")
  if [ "$TOTAL_COMMITS" -gt 15 ] 2>/dev/null; then
    echo "     ... 還有 $((TOTAL_COMMITS - 15)) 個 commit"
  fi
  echo ""

  # 取得變更檔案統計
  echo -e "   ${CYAN}變更檔案統計:${RESET}"
  git -C "$PROJECT" diff --stat "$ANALYZED_COMMIT".."$CURRENT_COMMIT" | tail -1 | sed 's/^/     /'
  echo ""

  # 路徑映射分析 — 判斷哪些文件頁面受影響
  echo -e "   ${CYAN}受影響的文件頁面:${RESET}"

  CHANGED_FILES=$(git -C "$PROJECT" diff --name-only "$ANALYZED_COMMIT".."$CURRENT_COMMIT" 2>/dev/null)

  # 讀取頁面路徑映射並比對
  python3 -c "
import json

with open('$VERSIONS_FILE') as f:
    data = json.load(f)

pages = data['projects']['$PROJECT'].get('pages', {})
changed_files = '''$CHANGED_FILES'''.strip().split('\n')

affected = {}
for page_name, page_info in pages.items():
    source_paths = page_info.get('source_paths', [])
    matched_files = []
    for f in changed_files:
        for sp in source_paths:
            if f.startswith(sp):
                matched_files.append(f)
                break
    if matched_files:
        doc_files = ', '.join(page_info.get('doc_files', []))
        affected[page_name] = {
            'doc': doc_files,
            'count': len(matched_files),
            'files': matched_files[:5]
        }

if affected:
    for page, info in affected.items():
        print(f\"     📝 {page} ({info['count']} 個檔案變更)\")
        print(f\"        文件: {info['doc']}\")
        for f in info['files']:
            print(f\"        - {f}\")
        if info['count'] > 5:
            print(f\"        ... 還有 {info['count'] - 5} 個\")
else:
    print('     ℹ️  無法對應到特定頁面（可能是 CI/測試/文件變更）')
"
  echo ""
  echo "  ----------------------------------------"
  echo ""
done

if [ "$HAS_UPDATES" = false ]; then
  echo ""
  echo -e "${GREEN}🎉 所有專案文件皆為最新版本！${RESET}"
fi
