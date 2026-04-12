#!/usr/bin/env python3
# ha-dr.md Block 2: PDB Protection Flow - graph LR

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
SUCCESS_FILL = "#f0fdf4"
SUCCESS_STROKE = "#86efac"
ERROR_FILL = "#fef2f2"
ERROR_STROKE = "#fca5a5"

OUT = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-hadr-pdb-flow.svg"

W, H = 1500, 380
NODE_W, NODE_H = 170, 48
GAP_X = 55

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
        offset = -(len(lines)-1)*8
        tspans = ''.join(f'<tspan x="{x + w//2}" dy="{offset + i*16}">{l}</tspan>' for i, l in enumerate(lines))
        text = f'<text x="{x + w//2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}">{tspans}</text>'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n{text}'

def arrow_line(x1, y1, x2, y2, label=""):
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2 - 12
    line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arrow)"/>'
    lbl = ""
    if label:
        lbl = f'<text x="{mid_x}" y="{mid_y}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{label}</text>'
    return line + "\n" + lbl

svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg_parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg_parts.append(arrow_marker())

# Layout:
# Source A (left center)
# Upper path: A -> B -> C (no PDB path)
# Lower path: A -> D -> E -> F -> G (PDB path)

# Two rows
ROW_TOP_Y = 60
ROW_BOT_Y = 220
A_X = 40
A_Y = (ROW_TOP_Y + ROW_BOT_Y) // 2 - NODE_H // 2

# Source A
svg_parts.append(box(A_X, A_Y, NODE_W, NODE_H, "kubectl drain node-1"))

# Upper path (no PDB): B=Pod立即被刪除, C=VM強制關機❌
B_X = A_X + NODE_W + GAP_X
B_Y = ROW_TOP_Y
svg_parts.append(box(B_X, B_Y, NODE_W, NODE_H, "Pod 立即被刪除", BOX_FILL, BOX_STROKE))
C_X = B_X + NODE_W + GAP_X
C_Y = ROW_TOP_Y
svg_parts.append(box(C_X, C_Y, NODE_W, NODE_H, "VM 強制關機 ❌", ERROR_FILL, ERROR_STROKE))

# Lower path (PDB): D=Pod驅逐被阻擋, E=Live Migration啟動, F=遷移完成後釋放PDB, G=原Pod安全刪除✅
D_X = A_X + NODE_W + GAP_X
D_Y = ROW_BOT_Y
svg_parts.append(box(D_X, D_Y, NODE_W, NODE_H, "Pod 驅逐被阻擋", BOX_FILL, BOX_STROKE))
E_X = D_X + NODE_W + GAP_X
E_Y = ROW_BOT_Y
svg_parts.append(box(E_X, E_Y, NODE_W + 20, NODE_H, "Live Migration 啟動", BOX_FILL, BOX_STROKE))
F_X = E_X + NODE_W + 20 + GAP_X
F_Y = ROW_BOT_Y
svg_parts.append(box(F_X, F_Y, NODE_W + 30, NODE_H, "遷移完成後釋放 PDB", BOX_FILL, BOX_STROKE))
G_X = F_X + NODE_W + 30 + GAP_X
G_Y = ROW_BOT_Y
svg_parts.append(box(G_X, G_Y, NODE_W + 30, NODE_H, "原 Pod 安全刪除 ✅", SUCCESS_FILL, SUCCESS_STROKE))

# Draw arrows
# A -> B (elbow up)
AX_right = A_X + NODE_W
AY_mid = A_Y + NODE_H // 2
BX_left = B_X
BY_mid = B_Y + NODE_H // 2
# Elbow: right from A, then up to B row, then right to B
svg_parts.append(f'<path d="M {AX_right} {AY_mid} L {B_X - 10} {AY_mid} L {B_X - 10} {BY_mid} L {BX_left} {BY_mid}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>')
svg_parts.append(f'<text x="{(AX_right + B_X - 10)//2}" y="{AY_mid - 8}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">無 PDB</text>')

# B -> C
svg_parts.append(arrow_line(B_X + NODE_W, BY_mid, C_X, BY_mid))

# A -> D (elbow down)
DY_mid = D_Y + NODE_H // 2
svg_parts.append(f'<path d="M {AX_right} {AY_mid} L {D_X - 10} {AY_mid} L {D_X - 10} {DY_mid} L {D_X} {DY_mid}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>')
svg_parts.append(f'<text x="{(AX_right + D_X - 10)//2}" y="{DY_mid + 14}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">有 PDB</text>')

# D -> E
EY_mid = E_Y + NODE_H // 2
svg_parts.append(arrow_line(D_X + NODE_W, DY_mid, E_X, EY_mid))

# E -> F
FY_mid = F_Y + NODE_H // 2
svg_parts.append(arrow_line(E_X + NODE_W + 20, EY_mid, F_X, FY_mid))

# F -> G
GY_mid = G_Y + NODE_H // 2
svg_parts.append(arrow_line(F_X + NODE_W + 30, FY_mid, G_X, GY_mid))

# Add path labels
svg_parts.append(f'<text x="40" y="{ROW_TOP_Y - 10}" font-family="{FONT}" font-size="13" fill="#ef4444" font-weight="600">⚠ 無 PDB 路徑</text>')
svg_parts.append(f'<text x="40" y="{ROW_BOT_Y - 10}" font-family="{FONT}" font-size="13" fill="#16a34a" font-weight="600">✓ 有 PDB 路徑</text>')

svg_parts.append('</svg>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg_parts))

print(f"Written: {OUT}")
