---
name: quiz-generation
description: Use when generating interactive team quiz questions from existing project documentation. Produces VitePress-compatible QuizQuestion component blocks (zh-TW, 4-choice, with explanation). Supports automatic topic decomposition based on project complexity.
---

# Quiz Generation Skill

## 概述

從現有的專案文件（`docs-site/{project}/`）產生互動式測驗題目，輸出為 VitePress `QuizQuestion` 元件格式，供工程師自我評測。

**核心原則：**
- 題目必須基於文件內容，**禁止杜撰**
- **涉及函數名稱、類型名稱、欄位名稱的題目，必須在原始碼中 grep 確認名稱存在後才能出題**
- 每題必須有清楚的正確選項與錯誤誘答（distractors）
- 中文繁體（zh-TW），術語保留英文原名
- 題目難度要有層次：概念理解 → 細節掌握 → 情境應用
- 若 quiz 頁或 index 頁需要示意圖，請沿用 repo 的靜態 SVG/PNG 圖表流程，不要新增 Mermaid

## 整體流程

```
┌─────────────────────────────────────────────────────┐
│ Phase A: 主題分析（自動分解，不使用固定模板）           │
├─────────────────────────────────────────────────────┤
│ Phase B: 平行出題（每個主題一個 agent）                 │
├─────────────────────────────────────────────────────┤
│ Phase C: 組裝與 VitePress 語法驗證                     │
├─────────────────────────────────────────────────────┤
│ Phase D: build 驗證 + commit                          │
└─────────────────────────────────────────────────────┘
```

---

## Phase A: 主題分析（Topic Decomposition）

### 前置步驟：確認原始碼路徑

在開始分析之前，先確認專案的原始碼 submodule 是否可用：

```bash
# 確認 submodule 已初始化
ls {project}/

# 若目錄為空，初始化 submodule
git submodule update --init {project}
```

**記錄此路徑供 Phase B 的所有 agent 使用**，讓 agent 能在出題前驗證函數/類型名稱。

### 演算法：動態主題分解

**不使用固定分類**，而是根據專案的重要度與特性自動決定測驗分區。

#### Step 1: 讀取文件結構

```bash
ls docs-site/{project}/
cat docs-site/{project}/index.md
```

列出所有文件頁面，了解該專案文件的廣度。

#### Step 2: 計算複雜度信號

對每個主題頁面，計算以下信號：

| 信號 | 說明 | 計算方式 |
|------|------|---------|
| **頁面數量** | 文件頁面總數 | `ls docs-site/{project}/**/*.md \| wc -l` |
| **內容深度** | 每頁平均行數 | `wc -l docs-site/{project}/**/*.md` |
| **CRD/API 覆蓋率** | 是否有 CRD/API 專屬頁面 | 頁面存在 → +2 |
| **元件數量** | 核心元件個數 | 元件頁面數 |
| **整合複雜度** | 外部整合頁面數 | 整合頁面數 |

#### Step 3: 分類決策

根據信號決定「要出幾個主題分區」：

| 文件頁面數 | 建議主題數 | 說明 |
|-----------|-----------|------|
| 1–4 頁    | 2–3 個    | 輕量專案（如 NMO）|
| 5–9 頁    | 3–5 個    | 中型專案（如 CDI、Forklift）|
| 10+ 頁   | 5–8 個    | 大型專案（如 KubeVirt）|

#### Step 4: 命名主題分區

每個主題分區命名規則：
- 使用 emoji + 中文名稱，例如：`🏗️ 基礎架構`
- 每個分區對應文件中的一個**邏輯群組**，而非逐頁對應
- 確保分區間不重疊，各自有清晰的知識邊界

**大型專案（KubeVirt 等）常見分區模式：**
```
🏗️ 基礎架構      ← 架構、設計原則、部署模型
⚙️ 核心元件      ← 各 daemon/controller 的職責
🌐 API 與網路    ← CRD、API 規格、網路配置
💾 儲存與輔助元件 ← 儲存、snapshot、helper 元件
🚀 進階功能      ← migration、高可用、效能調優
🔬 深入剖析      ← monitoring、metrics、問題排查
📖 實用指南      ← 操作流程、最佳實踐
```

**中小型專案示例（NMO）：**
```
⚙️ 核心架構與元件
🔄 操作流程與 CRD
🌐 整合與觀測性
```

#### Step 5: 決定每個分區的題目數

- 基本：每個分區 **20 題**（快速測驗）
- 標準：每個分區 **30 題**（完整評測）
- 深度：每個分區 **40 題**（全面訓練）

**每個分區的來源文件對應：**
在 Phase B 中給每個 agent 明確指定要讀的文件頁面。

---

## Phase B: 平行出題

### 啟動方式

每個主題分區啟動一個獨立的 `general-purpose` agent，平行執行：

```
Topic A → Agent 1 (30 questions)
Topic B → Agent 2 (30 questions)  ← 同時執行
Topic C → Agent 3 (30 questions)
...
```

### 給每個 Agent 的 Prompt 模板

```
你是一位專業的 Kubernetes 教育工作者，請為「{分區名稱}」主題出 {N} 道選擇題。

## 來源文件（必須閱讀）
以下是你出題時必須參考的文件，請完整閱讀後再出題：
- docs-site/{project}/{page1}.md
- docs-site/{project}/{page2}.md
{其他相關頁面}

## 原始碼路徑（函數/類型名稱驗證用）
- 專案 submodule 路徑：{project}/
- **出題時若涉及具體函數名稱、類型名稱、欄位名稱，必須先 grep 原始碼確認存在**

## 出題要求

1. **題目格式**：單選，4 個選項（A/B/C/D），1 個正確答案
2. **語言**：繁體中文，技術術語保留英文原名
3. **難度分布**（每 30 題）：
   - 10 題：概念理解（What is / What does）
   - 10 題：細節掌握（How / When / Which）
   - 10 題：情境應用（Given ... what happens / which approach）
4. **禁止**：模糊選項、「以上皆是」、不看文件就能猜出的答案
5. **必須**：每題有清楚的解釋，說明「為什麼是這個答案」以及「其他選項為何錯誤」

## ⛔ 零捏造原則（Zero Fabrication Rule）

**出題時嚴格禁止以下行為：**
- ❌ 使用文件中未明確出現的函數名稱或類型名稱
- ❌ 根據命名慣例「猜測」函數名稱（如 `handleReconcile()`、`processEvent()` 等）
- ❌ 在 explanation 中引用未經驗證的實作細節

**若題目涉及函數/類型名稱，必須：**
1. 先 grep 原始碼確認存在：`grep -r "FuncName" {project}/`
2. 在 explanation 中標注來源：「此函數定義於 `{project}/path/to/file.go`」
3. 若 grep 無結果，**改出不涉及具體名稱的概念題**

## 輸出格式

每道題按以下格式輸出，**不要加任何其他說明文字**：

```
<QuizQuestion
  question="{題號}. {題目}"
  :options='[
    "{選項A}",
    "{選項B}",
    "{選項C}",
    "{選項D}",
  ]'
  :answer="{0-indexed 正確選項}"
  explanation="{解釋}"
/>
```

## 語法規則（違反會導致 build 失敗）
- `:options='[...]'` 外層單引號、內層字串雙引號
- options 內禁止 HTML entities（`&quot;`、`&apos;` 等），要表示雙引號用 `\\"` 
- `explanation=` 內的雙引號用 `&quot;`
- `:answer` 是 0-indexed（第一個選項為 0）
- `/>` 必須獨立成一行
```

---

## Phase C: 組裝與驗證

### C1: 建立 quiz.md 框架

```markdown
---
layout: doc
title: {專案} — 互動式測驗
---

# {專案} 知識測驗

::: info 測驗說明
共 {N} 題，涵蓋 {X} 個主題領域。點選選項後按「確認答案」查看結果。
:::

<script setup>
import QuizQuestion from '../.vitepress/theme/components/QuizQuestion.vue'
</script>

## {分區1 emoji 標題}

{分區1 的 30 題}

---

## {分區2 emoji 標題}

{分區2 的 30 題}

---

{... 其他分區}
```

### C2: 組裝 Agent 輸出

用 Python 腳本組裝各 agent 的輸出（避免手動複製錯誤）：

```python
sections = [
    ("## 🏗️ 基礎架構", "/tmp/quiz_arch.txt"),
    ("## ⚙️ 核心元件", "/tmp/quiz_comp.txt"),
    # ...
]

with open('docs-site/{project}/quiz.md', 'w') as out:
    out.write(header)
    for title, path in sections:
        out.write(f'\n{title}\n\n')
        content = open(path).read()
        # 清除可能的 agent completion 訊息（污染來源）
        content = re.sub(r'^Agent completed.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^Now I have.*$', '', content, flags=re.MULTILINE)
        out.write(content.strip())
        out.write('\n\n---\n')
```

**重要：** Agent 輸出可能包含「Agent completed」等 metadata 行，**必須過濾掉**，否則 VitePress build 會失敗。

### C3: 語法驗證

在執行 build 之前，先用 Node.js 驗證所有 `:options` 表達式：

```python
import subprocess, re

content = open('docs-site/{project}/quiz.md').read()
lines = content.split('\n')

in_options = False
opt_lines = []
opt_start = 0
issues = []

for i, line in enumerate(lines, 1):
    if ":options='" in line:
        in_options = True
        opt_start = i
        opt_lines = [line[line.index(":options='") + len(":options='"):]]
    elif in_options:
        opt_lines.append(line)
        if line.strip().endswith("]'"):
            opts_str = '\n'.join(opt_lines).rstrip("'")
            r = subprocess.run(['node', '-e', f'var x = {opts_str}'],
                               capture_output=True, text=True)
            if r.returncode != 0:
                issues.append((opt_start, opts_str[:80], r.stderr[:100]))
            in_options = False

if issues:
    for start, preview, err in issues:
        print(f"Line {start}: {err}")
else:
    print("All :options valid ✓")
```

**常見問題與修法：**

| 問題 | 症狀 | 修法 |
|------|------|------|
| `&quot;` 在 options 內 | `Unexpected token` | 改為 `\\"` |
| `&apos;` 在 options 內 | `Unexpected token` | 改為 `\\'` |
| Agent metadata 殘留 | 解析失敗或題目缺失 | 用 regex 過濾 |
| ` ``` ` code fence 包住 section | 整段被當成 code block | 移除多餘的 ``` |
| `{{ }}` 在文字中 | Vue template 錯誤 | 改為 `&#123;&#123;` |

---

## Phase D: Build 驗證

```bash
npm run build
```

### 如果 build 失敗

**策略：binary search by section**

```python
import subprocess, shutil

content = open('docs-site/{project}/quiz.md').read()
lines = content.split('\n')
quiz_path = 'docs-site/{project}/quiz.md'

# 找到各 section 分隔符位置（--- 行）
section_ends = [i for i, l in enumerate(lines) if l.strip() == '---' and i > 10]

for end in section_ends:
    test = '\n'.join(lines[:end])
    open(quiz_path, 'w').write(test)
    r = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
    ok = 'build error' not in r.stdout + r.stderr
    print(f"Up to line {end}: {'OK' if ok else 'FAIL'}")
    if not ok:
        break

shutil.copy('/tmp/quiz_original.md', quiz_path)
```

找到失敗的 section 後，在該 section 內再 binary search 到具體問題題號。

**VitePress 錯誤位置解讀：**
- `quiz.md (1520:13): Error parsing JavaScript expression: Unexpected token (3:30)`
  - `1520:13`：quiz.md 的第 1520 行
  - `(3:30)`：`:options` 值的第 3 行、第 30 個字元
  - 去看對應行的第 3 個 option，第 30 個字元附近

---

## Sidebar 更新

在 `docs-site/.vitepress/config.js` 的對應 sidebar array 加入 quiz 連結：

```javascript
{
  text: '📝 測驗',
  items: [
    { text: '互動式知識測驗', link: '/{project}/quiz' },
  ]
}
```

---

## 快速參考：QuizQuestion 格式

```vue
<QuizQuestion
  question="1. 題目文字（數字加點）"
  :options='[
    "選項 A",
    "選項 B（正確）",
    "選項 C",
    "選項 D",
  ]'
  :answer="1"
  explanation="解釋為什麼 B 正確，以及其他選項為何錯誤。術語保留英文。"
/>
```

**必須遵守：**
- 外層 `'` 單引號，內層字串 `"` 雙引號
- options 內表示 `"` → 用 `\\"` 
- question/explanation 內表示 `"` → 用 `&quot;`
- `:answer` 是 0-indexed
- `/>` 獨立成一行，不與任何其他字元同行
- 每個 section 以 `---` 分隔
- 題號從 1 開始重新計算（每個分區獨立）

---

## 完整範例：產生 KubeVirt 測驗流程

```bash
# 1. 讀取文件結構
ls docs-site/kubevirt/

# 2. 執行 Phase A: 主題分析
# → 判斷為大型專案（12+ 頁面）
# → 建立 7 個主題分區，每區 30 題

# 3. Phase B: 平行啟動 7 個 agent
# → 各自讀取對應文件頁面，輸出到 /tmp/quiz_*.txt

# 4. Phase C: 組裝
python3 assemble_quiz.py
python3 validate_options.py

# 5. Phase D: Build
npm run build

# 6. 如果失敗，binary search 定位問題，修復後重試

# 7. Commit
git add docs-site/kubevirt/quiz.md
git commit -m "feat(kubevirt): add 210-question interactive quiz (7 sections × 30 questions)

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
