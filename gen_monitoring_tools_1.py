#!/usr/bin/env python3
"""monitoring-tools-overview-1: kubevirt/monitoring core tools diagram"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1100, 580

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def box(x, y, w, h, label, sub=None, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>']
    if sub:
        lines.append(f'<text x="{x+w//2}" y="{y+h//2-10}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" font-weight="600">{esc(label)}</text>')
        lines.append(f'<text x="{x+w//2}" y="{y+h//2+10}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{esc(sub)}</text>')
    else:
        lines.append(f'<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" font-weight="600">{esc(label)}</text>')
    return "\n".join(lines)

def container(x, y, w, h, label):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>
<text x="{x+14}" y="{y+18}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" font-weight="600">{esc(label)}</text>'''

def subcontainer(x, y, w, h, label):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="rgba(255,255,255,0.7)" stroke="{CONTAINER_STROKE}" stroke-width="1" stroke-dasharray="4,3"/>
<text x="{x+8}" y="{y+14}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>'''

def arrow(x1, y1, x2, y2, label="", label_x=None, label_y=None):
    dx = x2 - x1
    dy = y2 - y1
    parts = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>']
    if label:
        lx = label_x if label_x else (x1+x2)//2
        ly = label_y if label_y else (y1+y2)//2 - 6
        parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>')
    return "\n".join(parts)

def curved_arrow(x1, y1, x2, y2, cx, cy, label="", label_x=None, label_y=None):
    parts = [f'<path d="M{x1},{y1} Q{cx},{cy} {x2},{y2}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>']
    if label:
        lx = label_x if label_x else cx
        ly = label_y if label_y else cy - 6
        parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>')
    return "\n".join(parts)

svg_parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>''']

# Main container: kubevirt/monitoring 核心工具
svg_parts.append(container(20, 20, 700, 460, "kubevirt/monitoring 核心工具"))

# Sub-container 1: 靜態分析 (x=40, y=45, w=150, h=100)
svg_parts.append(subcontainer(40, 45, 150, 100, "靜態分析"))
svg_parts.append(box(55, 65, 120, 60, "monitoringlinter", "Go AST 分析器"))

# Sub-container 2: 文件生成 (x=210, y=45, w=150, h=160)
svg_parts.append(subcontainer(210, 45, 150, 160, "文件生成"))
svg_parts.append(box(225, 65, 120, 55, "metricsdocs", "指標文件彙整"))
svg_parts.append(box(225, 135, 120, 55, "metrics parser", "Prometheus 指標解析"))

# Sub-container 3: 同步工具 (x=380, y=45, w=160, h=100)
svg_parts.append(subcontainer(380, 45, 160, 100, "同步工具"))
svg_parts.append(box(395, 65, 130, 60, "runbook-sync-downstream", "Runbook 下游同步"))

# Sub-container 4: 品質驗證 (x=40, y=185, w=150, h=100)
svg_parts.append(subcontainer(40, 195, 150, 100, "品質驗證"))
svg_parts.append(box(55, 215, 120, 60, "prom-metrics-linter", "指標命名規範"))

# External nodes (right side and bottom)
# OPERATOR node
svg_parts.append(box(800, 100, 160, 65, "各 KubeVirt Operator", fill=BOX_FILL))
# DOCS node
svg_parts.append(box(800, 220, 160, 65, "docs/metrics.md", fill=BOX_FILL))
# OPENSHIFT node
svg_parts.append(box(800, 340, 160, 65, "openshift/runbooks", fill=BOX_FILL))

# Arrows:
# LINTER (175, 95) → OPERATOR (800, 132): limit prometheus.Register to pkg/monitoring
svg_parts.append(curved_arrow(175, 95, 800, 132, 490, 60,
    "限制 prometheus.Register 到 pkg/monitoring", 490, 45))

# METRICSDOCS (345, 92) → DOCS (800, 252)
svg_parts.append(curved_arrow(360, 92, 800, 252, 600, 180,
    "克隆 9 個專案 / 解析指標表格", 600, 168))

# PARSER (345, 162) → PROMLINT (175, 245)
svg_parts.append(arrow(345, 162, 175, 245,
    "Metric → MetricFamily", 260, 190))

# RUNBOOK (460, 95) → OPENSHIFT (800, 372)
svg_parts.append(curved_arrow(540, 95, 800, 372, 700, 260,
    "upstream → downstream / 自動建 PR", 700, 248))

# PROMLINT (175, 275) → OPERATOR (800, 165)
svg_parts.append(curved_arrow(175, 275, 800, 165, 490, 350,
    "前綴/後綴驗證", 490, 365))

# Close SVG
svg_parts.append('</svg>')

svg_content = "\n".join(svg_parts)
out = "docs-site/public/diagrams/monitoring/monitoring-tools-overview-1.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"Written: {out}")
