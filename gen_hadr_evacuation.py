#!/usr/bin/env python3
# ha-dr.md Block 3: Evacuation Controller Flow - graph TD

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
SUCCESS_FILL = "#f0fdf4"
SUCCESS_STROKE = "#86efac"

OUT = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-hadr-evacuation-flow.svg"

W, H = 900, 680
NODE_W, NODE_H = 340, 52
GAP_Y = 55
CX = W // 2

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

nodes = [
    ("A", "節點被標記 drain taint", BOX_FILL, BOX_STROKE),
    ("B", "EvacuationController 偵測", BOX_FILL, BOX_STROKE),
    ("C", "vmisToMigrate() 識別需遷移的 VMI", BOX_FILL, BOX_STROKE),
    ("D", "filterRunningNonMigratingVMIs() 過濾", BOX_FILL, BOX_STROKE),
    ("E", "建立 VirtualMachineInstanceMigration", BOX_FILL, BOX_STROKE),
    ("F", "Migration 執行", BOX_FILL, BOX_STROKE),
    ("G", "VMI 遷移到新節點", BOX_FILL, BOX_STROKE),
    ("H", "EvictionRequested condition 移除", SUCCESS_FILL, SUCCESS_STROKE),
]

svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg_parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg_parts.append(arrow_marker())

# Compute positions
positions = {}
y = 30
for nid, label, fill, stroke in nodes:
    x = CX - NODE_W // 2
    positions[nid] = (x, y, fill, stroke)
    y += NODE_H + GAP_Y

# Draw arrows
for i in range(len(nodes) - 1):
    nid_a = nodes[i][0]
    nid_b = nodes[i+1][0]
    xa, ya, _, _ = positions[nid_a]
    xb, yb, _, _ = positions[nid_b]
    x1 = xa + NODE_W // 2
    y1 = ya + NODE_H
    x2 = xb + NODE_W // 2
    y2 = yb
    svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arrow)"/>')

# Draw boxes
for nid, label, fill, stroke in nodes:
    x, y, _, _ = positions[nid]
    svg_parts.append(box(x, y, NODE_W, NODE_H, label, fill, stroke))

svg_parts.append('</svg>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg_parts))

print(f"Written: {OUT}")
