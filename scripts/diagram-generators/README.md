# Diagram Generators

本目錄存放 `kubevirt-learning-site` 的靜態圖表產生腳本。

## 規則

- 所有新的圖表 generator script 都放這裡，不要再放 repo root
- 圖表輸出目標為 `docs-site/public/diagrams/{project}/`
- 文件內一律引用匯出的靜態 SVG/PNG，不新增 Mermaid
- 預設從 **repo root** 執行，例如：

```bash
python3 scripts/diagram-generators/gen_forklift_diagrams.py
python3 scripts/diagram-generators/gen_vm_init_9_svg.py
```

## 命名慣例

- `gen_{project}_*.py`：單張或一組專案圖
- `gen_*_diagrams.py`：批次產生多張圖

## 相關規範

- 文件圖表策略：`CLAUDE.md`
- 繪圖流程：`skills/fireworks-tech-graph/SKILL.md`
- 文件產生流程：`skills/analyzing-source-code/SKILL.md`
