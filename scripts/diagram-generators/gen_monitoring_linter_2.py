#!/usr/bin/env python3
"""monitoring-linter-flow-2: monitoringlinter analysis flowchart TD"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
DIAMOND_FILL = "#fef3c7"
DIAMOND_STROKE = "#fbbf24"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 900, 800

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def rect_node(cx, cy, w, h, line1, line2=None):
    x, y = cx - w//2, cy - h//2
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>']
    if line2:
        parts.append(f'<text x="{cx}" y="{cy-8}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" font-weight="600">{esc(line1)}</text>')
        parts.append(f'<text x="{cx}" y="{cy+10}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{esc(line2)}</text>')
    else:
        parts.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" font-weight="600">{esc(line1)}</text>')
    return "\n".join(parts)

def diamond(cx, cy, w, h, line1, line2=None):
    # Diamond shape using polygon
    hw, hh = w//2, h//2
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    parts = [f'<polygon points="{pts}" fill="{DIAMOND_FILL}" stroke="{DIAMOND_STROKE}" stroke-width="1.5"/>']
    if line2:
        parts.append(f'<text x="{cx}" y="{cy-7}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" font-weight="600">{esc(line1)}</text>')
        parts.append(f'<text x="{cx}" y="{cy+9}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{esc(line2)}</text>')
    else:
        parts.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" font-weight="600">{esc(line1)}</text>')
    return "\n".join(parts)

def arrow_v(x, y1, y2, label="", side="right"):
    parts = [f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>']
    if label:
        lx = x + 8 if side == "right" else x - 8
        anchor = "start" if side == "right" else "end"
        parts.append(f'<text x="{lx}" y="{(y1+y2)//2+4}" text-anchor="{anchor}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>')
    return "\n".join(parts)

def arrow_h(x1, x2, y, label=""):
    parts = [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>']
    if label:
        parts.append(f'<text x="{(x1+x2)//2}" y="{y-6}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>')
    return "\n".join(parts)

def arrow_path(d, label="", lx=None, ly=None):
    parts = [f'<path d="{d}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>']
    if label and lx and ly:
        parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>')
    return "\n".join(parts)

svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>''']

# Nodes layout (top-down main flow at x=450)
CX = 450
# A: 遍歷每個 Go 檔案
A_Y = 50
svg.append(rect_node(CX, A_Y, 200, 44, "遍歷每個 Go 檔案"))

# B: diamond: 檔案是否 import 監控相關套件?
B_Y = 140
svg.append(diamond(CX, B_Y, 260, 70, "檔案是否 import", "監控相關套件?"))

# C: 跳過此檔案 (branch: 否, to right)
C_X, C_Y = 700, 140
svg.append(rect_node(C_X, C_Y, 140, 44, "跳過此檔案"))

# D: AST Inspect 所有節點
D_Y = 240
svg.append(rect_node(CX, D_Y, 220, 44, "AST Inspect 所有節點"))

# E: diamond: 節點是 CallExpr?
E_Y = 330
svg.append(diamond(CX, E_Y, 220, 60, "節點是", "CallExpr?"))

# F: 繼續遍歷 (branch: 否, to right)
F_X, F_Y = 700, 330
svg.append(rect_node(F_X, F_Y, 120, 44, "繼續遍歷"))

# G: diamond: 是 SelectorExpr 方法呼叫?
G_Y = 420
svg.append(diamond(CX, G_Y, 240, 60, "是 SelectorExpr", "方法呼叫?"))

# H: diamond: 使用 prometheus 套件?
H_Y = 510
svg.append(diamond(CX, H_Y, 230, 60, "使用 prometheus 套件?"))

# I: checkPrometheusMethodCall (branch: 是, to left)
I_X, I_Y = 180, 510
svg.append(rect_node(I_X, I_Y, 200, 44, "checkPrometheusMethodCall"))

# J: diamond: 檔案在 pkg/monitoring 內?
J_Y = 600
svg.append(diamond(CX, J_Y, 230, 60, "檔案在", "pkg/monitoring 內?"))

# K: diamond: 使用 operatormetrics?
K_Y = 690
svg.append(diamond(CX, K_Y, 210, 55, "使用 operatormetrics?"))

# L: checkOperatorMetricsMethodCall (branch: 是, to left)
L_X, L_Y = 170, 690
svg.append(rect_node(L_X, L_Y, 210, 44, "checkOperatorMetricsMethodCall"))

# M: diamond: 使用 operatorrules?
M_X, M_Y = 680, 690
svg.append(diamond(M_X, M_Y, 200, 55, "使用 operatorrules?"))

# N: checkOperatorRulesMethodCall (branch: 是, below M)
N_X, N_Y = 680, 760
svg.append(rect_node(N_X, N_Y, 200, 44, "checkOperatorRulesMethodCall"))

# Arrows
svg.append(arrow_v(CX, A_Y+22, B_Y-35))
# B → C (否, right)
svg.append(arrow_h(CX+130, C_X-70, B_Y, "否"))
# B → D (是, down)
svg.append(arrow_v(CX, B_Y+35, D_Y-22, "是", "right"))
svg.append(arrow_v(CX, D_Y+22, E_Y-30))
# E → F (否, right)
svg.append(arrow_h(CX+110, F_X-60, E_Y, "否"))
# E → G (是, down)
svg.append(arrow_v(CX, E_Y+30, G_Y-30, "是", "right"))
# G → F (否, right)
svg.append(arrow_h(CX+120, F_X-60, G_Y, "否"))
# G → H (是, down)
svg.append(arrow_v(CX, G_Y+30, H_Y-30, "是", "right"))
# H → I (是, left)
svg.append(arrow_h(CX-115, I_X+100, H_Y, "是"))
# H → J (否, down)
svg.append(arrow_v(CX, H_Y+30, J_Y-30, "否", "right"))
# J → F (是, right then up)
svg.append(arrow_path(f"M{CX+115},{J_Y} L{F_X},{J_Y} L{F_X},{F_Y+22}", "是", F_X+30, J_Y-6))
# J → K (否, down)
svg.append(arrow_v(CX, J_Y+30, K_Y-28, "否", "right"))
# K → L (是, left)
svg.append(arrow_h(CX-105, L_X+105, K_Y, "是"))
# K → M (否, right)
svg.append(arrow_h(CX+105, M_X-100, K_Y, "否"))
# M → N (是, down)
svg.append(arrow_v(M_X, M_Y+28, N_Y-22, "是", "right"))

svg.append('</svg>')
out = "docs-site/public/diagrams/monitoring/monitoring-linter-flow-2.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print(f"Written: {out}")
