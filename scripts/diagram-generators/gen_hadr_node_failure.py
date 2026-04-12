#!/usr/bin/env python3
# ha-dr.md Block 1: Node Failure Flow - graph TD

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
SUCCESS_FILL = "#f0fdf4"
SUCCESS_STROKE = "#86efac"
DIAMOND_FILL = "#eff6ff"
DIAMOND_STROKE = "#bfdbfe"

OUT = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-hadr-node-failure-flow.svg"

W, H = 1400, 720
NODE_W, NODE_H = 200, 48
GAP_Y = 60

def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
</defs>'''

def box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE, font_size=13):
    lines = label.split('\n')
    cy = y + h // 2
    if len(lines) == 1:
        text = f'<text x="{x + w//2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}">{lines[0]}</text>'
    else:
        tspans = ''.join(f'<tspan x="{x + w//2}" dy="{0 if i==0 else 16}">{l}</tspan>' for i, l in enumerate(lines))
        text = f'<text x="{x + w//2}" y="{cy - 8*(len(lines)-1)}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}">{tspans}</text>'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n{text}'

def diamond(cx, cy, label):
    hw, hh = 90, 36
    pts = f"{cx},{cy-hh} {cx+hw*1.4},{cy} {cx},{cy+hh} {cx-hw*1.4},{cy}"
    poly = f'<polygon points="{pts}" fill="{DIAMOND_FILL}" stroke="{DIAMOND_STROKE}" stroke-width="1.5"/>'
    text = f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}">{label}</text>'
    return poly + "\n" + text

def arrow_v(x1, y1, x2, y2, label="", label_side="right"):
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arrow)"/>'
    lbl = ""
    if label:
        lx = mid_x + (10 if label_side=="right" else -10)
        anchor = "start" if label_side=="right" else "end"
        lbl = f'<text x="{lx}" y="{mid_y}" text-anchor="{anchor}" dominant-baseline="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{label}</text>'
    return line + "\n" + lbl

def arrow_h(x1, y1, x2, y2, label=""):
    mid_x = (x1 + x2) / 2
    mid_y = min(y1, y2) - 12
    line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arrow)"/>'
    lbl = ""
    if label:
        lbl = f'<text x="{mid_x}" y="{mid_y}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{label}</text>'
    return line + "\n" + lbl

svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg_parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg_parts.append(arrow_marker())

# Layout: center column for main flow, branches at diamond F
CX = W // 2
NW = NODE_W + 60  # wider nodes

# Positions (top-down)
# A at top, then B,C,D,E (linear), F (diamond), then 4 branches G,H,I,J
y_A = 30
y_B = y_A + NODE_H + GAP_Y
y_C = y_B + NODE_H + GAP_Y
y_D = y_C + NODE_H + GAP_Y
y_E = y_D + NODE_H + GAP_Y
y_F = y_E + NODE_H + GAP_Y + 10  # diamond
DIAMOND_HH = 36
y_branches = y_F + DIAMOND_HH + GAP_Y + 10

# Branch columns (4 branches)
branch_xs = [150, 450, 850, 1150]
branch_labels = ["在其他節點重建 VMI", "在其他節點重建 VMI", "不自動重建", "不自動重建"]
branch_fills = [SUCCESS_FILL, SUCCESS_FILL, BOX_FILL, BOX_FILL]
branch_strokes = [SUCCESS_STROKE, SUCCESS_STROKE, BOX_STROKE, BOX_STROKE]
branch_edge_labels = ["Always", "RerunOnFailure", "Manual / Halted", "Once"]

# Main flow
main_nodes = [
    (CX - NW//2, y_A, NW, NODE_H, "virt-handler heartbeat 停止", BOX_FILL, BOX_STROKE),
    (CX - NW//2, y_B, NW, NODE_H, "isNodeUnresponsive 返回 true", BOX_FILL, BOX_STROKE),
    (CX - NW//2, y_C, NW, NODE_H, "節點標記 NodeUnresponsiveReason", BOX_FILL, BOX_STROKE),
    (CX - NW//2, y_D, NW, NODE_H, "節點上的 VMI 標記為 Failed", BOX_FILL, BOX_STROKE),
    (CX - NW//2, y_E, NW, NODE_H, "checkNodeForOrphanedAndErroredVMIs 清理 VMI", BOX_FILL, BOX_STROKE),
]

# Vertical arrows for main flow
arrow_data = [
    (CX, y_A + NODE_H, CX, y_B, "超過 5 分鐘"),
    (CX, y_B + NODE_H, CX, y_C, ""),
    (CX, y_C + NODE_H, CX, y_D, ""),
    (CX, y_D + NODE_H, CX, y_E, ""),
    (CX, y_E + NODE_H, CX, y_F - DIAMOND_HH, ""),
]
for x1,y1,x2,y2,lbl in arrow_data:
    svg_parts.append(arrow_v(x1, y1, x2, y2, lbl))

# Draw main nodes
for (x, y, w, h, lbl, fill, stroke) in main_nodes:
    svg_parts.append(box(x, y, w, h, lbl, fill, stroke, font_size=13))

# Diamond F
svg_parts.append(diamond(CX, y_F, "VM RunStrategy?"))

# Branch arrows from diamond to branch nodes
for i, (bx_center, blabel, bfill, bstroke, belbl) in enumerate(zip(branch_xs, branch_labels, branch_fills, branch_strokes, branch_edge_labels)):
    bx = bx_center - NODE_W//2
    # Arrow from diamond to branch: go down from diamond bottom, then elbow to branch
    # If branch is to the left/right, draw L-shaped path
    diamond_bottom_x = CX
    diamond_bottom_y = y_F + DIAMOND_HH
    branch_top_x = bx_center
    branch_top_y = y_branches
    
    mid_y = diamond_bottom_y + (branch_top_y - diamond_bottom_y) // 2
    path = f'<path d="M {diamond_bottom_x} {diamond_bottom_y} L {diamond_bottom_x} {mid_y} L {branch_top_x} {mid_y} L {branch_top_x} {branch_top_y}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>'
    svg_parts.append(path)
    # Label
    lx = (diamond_bottom_x + branch_top_x) / 2
    svg_parts.append(f'<text x="{lx}" y="{mid_y - 8}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{belbl}</text>')
    # Branch box
    svg_parts.append(box(bx, y_branches, NODE_W, NODE_H, blabel, bfill, bstroke))

svg_parts.append('</svg>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg_parts))

print(f"Written: {OUT}")
