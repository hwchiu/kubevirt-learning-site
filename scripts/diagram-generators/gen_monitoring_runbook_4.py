#!/usr/bin/env python3
"""monitoring-runbook-sync-4: runbook-sync-downstream architecture"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
DIAMOND_FILL = "#fef3c7"
DIAMOND_STROKE = "#fbbf24"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
CONTAINER2_FILL = "#fff0f0"
CONTAINER2_STROKE = "#fca5a5"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1080, 820

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def rnode(cx, cy, w, h, label, sub=None):
    x, y = cx - w//2, cy - h//2
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>']
    if sub:
        parts.append(f'<text x="{cx}" y="{cy-8}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" font-weight="600">{esc(label)}</text>')
        parts.append(f'<text x="{cx}" y="{cy+9}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{esc(sub)}</text>')
    else:
        parts.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" font-weight="600">{esc(label)}</text>')
    return "\n".join(parts)

def dnode(cx, cy, w, h, label, sub=None):
    hw, hh = w//2, h//2
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    parts = [f'<polygon points="{pts}" fill="{DIAMOND_FILL}" stroke="{DIAMOND_STROKE}" stroke-width="1.5"/>']
    if sub:
        parts.append(f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" font-weight="600">{esc(label)}</text>')
        parts.append(f'<text x="{cx}" y="{cy+9}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{esc(sub)}</text>')
    else:
        parts.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" font-weight="600">{esc(label)}</text>')
    return "\n".join(parts)

def cont(x, y, w, h, label, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
<text x="{x+12}" y="{y+16}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" font-weight="700" font-style="italic">{esc(label)}</text>'''

def av(x, y1, y2, label="", side="right"):
    parts = [f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>']
    if label:
        lx = x + 6 if side == "right" else x - 6
        anchor = "start" if side == "right" else "end"
        parts.append(f'<text x="{lx}" y="{(y1+y2)//2+4}" text-anchor="{anchor}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>')
    return "\n".join(parts)

def ah(x1, x2, y, label="", valign="above"):
    parts = [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>']
    if label:
        ly = y - 6 if valign == "above" else y + 14
        parts.append(f'<text x="{(x1+x2)//2}" y="{ly}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>')
    return "\n".join(parts)

def apath(d, label="", lx=None, ly=None):
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

# Main flow center x
MX = 200
# A: 開始
A_Y = 50
svg.append(rnode(MX, A_Y, 120, 40, "開始"))
# B: setup
B_Y = 120
svg.append(rnode(MX, B_Y, 240, 40, "setup: 克隆 upstream 與 downstream"))
# C
C_Y = 190
svg.append(rnode(MX, C_Y, 220, 40, "listRunbooksThatNeedUpdate"))
# D: diamond
D_Y = 265
svg.append(dnode(MX, D_Y, 220, 60, "比對 commit 日期"))
# E: runbooksToUpdate
E_X, E_Y = MX, 360
svg.append(rnode(E_X, E_Y, 180, 40, "runbooksToUpdate"))
# F: runbooksToDeprecate
F_X, F_Y = 540, 265
svg.append(rnode(F_X, F_Y, 180, 40, "runbooksToDeprecate"))
# G: skip
G_X, G_Y = 430, 360
svg.append(rnode(G_X, G_Y, 100, 40, "跳過"))
# H: updateRunbook entry
H_Y = 450
svg.append(rnode(E_X, H_Y, 180, 40, "updateRunbook 流程"))

# Container: updateRunbook
svg.append(cont(30, 470, 340, 290, "updateRunbook"))
H1_Y = 515
svg.append(rnode(E_X, H1_Y, 200, 40, "檢查 PR 是否已存在"))
H1_D_Y = 580
svg.append(dnode(E_X, H1_D_Y, 200, 55, "已存在?"))
H2_X, H2_Y = 320, 580
svg.append(rnode(H2_X, H2_Y, 100, 40, "跳過"))
H3_Y = 650
svg.append(rnode(E_X, H3_Y, 140, 40, "建立新分支"))
H4_Y = 710
svg.append(rnode(E_X, H4_Y, 180, 40, "copyRunbook + transform"))
H5_Y = 730
# stack them side by side to save space: H4, H5, H6, H7 linearly
H5_Y = H4_Y + 50  # commit & push but let's chain

# Simplify: chain in a vertical column inside the container
# Let's keep H5, H6, H7 visible - container grows

# Actually let me redo: scale down the container area
# Updated plan: two sub-flows side by side

# Let me restart the layout more carefully with two columns:
# Left col: main flow (A→B→C→D→E/F/G) + updateRunbook container
# Right col: deprecateRunbook container

# Let's go with a wider canvas, two subgraphs side by side
svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>''']

# Main flow: center at x=200, top-down
MX = 230
# Nodes
nodes = {}

def add_rnode(key, cx, cy, w, h, label, sub=None):
    nodes[key] = (cx, cy, w, h)
    return rnode(cx, cy, w, h, label, sub)

def add_dnode(key, cx, cy, w, h, label, sub=None):
    nodes[key] = (cx, cy, w, h)
    return dnode(cx, cy, w, h, label, sub)

def edge_bot(key): # bottom center of node
    cx, cy, w, h = nodes[key]
    return cx, cy + h//2

def edge_top(key):
    cx, cy, w, h = nodes[key]
    return cx, cy - h//2

def edge_left(key):
    cx, cy, w, h = nodes[key]
    return cx - w//2, cy

def edge_right(key):
    cx, cy, w, h = nodes[key]
    return cx + w//2, cy

svg.append(add_rnode("A", MX, 40, 120, 38, "開始"))
svg.append(add_rnode("B", MX, 100, 260, 38, "setup: 克隆 upstream 與 downstream"))
svg.append(add_rnode("C", MX, 160, 230, 38, "listRunbooksThatNeedUpdate"))
svg.append(add_dnode("D", MX, 240, 230, 62, "比對 commit 日期"))

# Branches from D
E_X, E_Y = MX, 340
svg.append(add_rnode("E", E_X, E_Y, 180, 38, "runbooksToUpdate"))
G_X, G_Y = MX+260, 240
svg.append(add_rnode("G", G_X, G_Y, 100, 38, "跳過"))
F_X, F_Y = MX+250, 340
svg.append(add_rnode("F", F_X, F_Y, 190, 38, "runbooksToDeprecate"))

# Main flow arrows
ax, ay = edge_bot("A"); bx, by = edge_top("B")
svg.append(av(MX, ay, by))
ax, ay = edge_bot("B"); bx, by = edge_top("C")
svg.append(av(MX, ay, by))
ax, ay = edge_bot("C"); bx, by = edge_top("D")
svg.append(av(MX, ay, by))
# D → E (upstream 較新, down)
svg.append(av(MX, edge_bot("D")[1], edge_top("E")[1], "upstream 較新"))
# D → G (已是最新, right)
svg.append(apath(f"M{edge_right('D')[0]},{G_Y} L{edge_left('G')[0]},{G_Y}", "已是最新", (edge_right('D')[0]+edge_left('G')[0])//2, G_Y-7))
# D → F (upstream 不存在, right+down)
dx_right = edge_right("D")[0]
svg.append(apath(f"M{dx_right},{240} L{F_X},{240} L{F_X},{edge_top('F')[1]}", "upstream 不存在", F_X+20, 225))

# updateRunbook subgraph (left column, starting at y=400)
UPD_X = 160  # center
svg.append(cont(30, 395, 280, 380, "updateRunbook"))
svg.append(add_rnode("H", UPD_X, 440, 200, 38, "updateRunbook 流程"))
svg.append(add_dnode("H1d", UPD_X, 510, 200, 55, "PR 是否已存在?"))
svg.append(add_rnode("H2", UPD_X+140, 510, 90, 38, "跳過"))
svg.append(add_rnode("H3", UPD_X, 585, 140, 38, "建立新分支"))
svg.append(add_rnode("H4", UPD_X, 640, 190, 38, "copyRunbook + transform"))
svg.append(add_rnode("H5", UPD_X, 695, 130, 38, "commit & push"))
svg.append(add_rnode("H6", UPD_X, 750, 100, 38, "建立 PR"))
svg.append(add_rnode("H7", UPD_X, 755+50, 120, 38, "關閉過時 PR"))

# E → H
svg.append(av(E_X, edge_bot("E")[1], edge_top("H")[1]))
# H → H1d
svg.append(av(UPD_X, edge_bot("H")[1], edge_top("H1d")[1]))
# H1d → H2 (已存在)
svg.append(ah(edge_right("H1d")[0], edge_left("H2")[0], 510, "已存在"))
# H1d → H3 (不存在)
svg.append(av(UPD_X, edge_bot("H1d")[1], edge_top("H3")[1], "不存在"))
# H3→H4→H5→H6→H7
for a, b in [("H3","H4"),("H4","H5"),("H5","H6"),("H6","H7")]:
    svg.append(av(UPD_X, edge_bot(a)[1], edge_top(b)[1]))

# deprecateRunbook subgraph (right column)
DEP_X = 700
svg.append(cont(580, 395, 270, 320, "deprecateRunbook", fill=CONTAINER2_FILL, stroke=CONTAINER2_STROKE))
svg.append(add_rnode("I", DEP_X, 440, 190, 38, "deprecateRunbook 流程"))
svg.append(add_dnode("I1d", DEP_X, 510, 190, 55, "PR 是否已存在?"))
svg.append(add_rnode("I2", DEP_X+140, 510, 90, 38, "跳過"))
svg.append(add_rnode("I3", DEP_X, 585, 140, 38, "建立新分支"))
svg.append(add_rnode("I4", DEP_X, 640, 160, 38, "套用棄用模板"))
svg.append(add_rnode("I5", DEP_X, 695, 130, 38, "commit & push"))
svg.append(add_rnode("I6", DEP_X, 750, 100, 38, "建立 PR"))

# F → I
svg.append(av(F_X, edge_bot("F")[1], edge_top("I")[1]))
# I → I1d
svg.append(av(DEP_X, edge_bot("I")[1], edge_top("I1d")[1]))
# I1d → I2 (已存在)
svg.append(ah(edge_right("I1d")[0], edge_left("I2")[0], 510, "已存在"))
# I1d → I3 (不存在)
svg.append(av(DEP_X, edge_bot("I1d")[1], edge_top("I3")[1], "不存在"))
for a, b in [("I3","I4"),("I4","I5"),("I5","I6")]:
    svg.append(av(DEP_X, edge_bot(a)[1], edge_top(b)[1]))

svg.append('</svg>')
out = "docs-site/public/diagrams/monitoring/monitoring-runbook-sync-4.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print(f"Written: {out}")
