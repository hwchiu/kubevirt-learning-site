#!/usr/bin/env python3
# quickstart.md Block 2: Masquerade Network - graph LR

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

OUT = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-quickstart-masquerade-net.svg"

W, H = 1100, 200
NODE_W, NODE_H = 180, 60
GAP_X = 80
START_X = 40
START_Y = (H - NODE_H) // 2

def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
</defs>'''

def box(x, y, w, h, lines_list, fill=BOX_FILL, stroke=BOX_STROKE):
    cy = y + h // 2
    if len(lines_list) == 1:
        text = f'<text x="{x + w//2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}">{lines_list[0]}</text>'
    else:
        offset = -(len(lines_list)-1)*9
        tspans = ''.join(f'<tspan x="{x + w//2}" dy="{offset + i*18}">{l}</tspan>' for i, l in enumerate(lines_list))
        text = f'<text x="{x + w//2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}">{tspans}</text>'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n{text}'

nodes = [
    (["VM", "10.0.2.2"],),
    (["Pod Network", "10.244.x.x"],),
    (["節點網路"],),
    (["外部網路"],),
]
edge_labels = ["NAT", "CNI", "路由"]

positions = []
for i, _ in enumerate(nodes):
    x = START_X + i * (NODE_W + GAP_X)
    positions.append((x, START_Y))

svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg_parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg_parts.append(arrow_marker())

# Arrows
for i in range(len(nodes) - 1):
    x1 = positions[i][0] + NODE_W
    y1 = START_Y + NODE_H // 2
    x2 = positions[i+1][0]
    y2 = START_Y + NODE_H // 2
    lbl = edge_labels[i] if i < len(edge_labels) else ""
    mid_x = (x1 + x2) / 2
    mid_y = y1 - 14
    svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arrow)"/>')
    if lbl:
        svg_parts.append(f'<text x="{mid_x}" y="{mid_y}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">{lbl}</text>')

# Boxes
for i, (lines_tuple,) in enumerate(nodes):
    x, y = positions[i]
    svg_parts.append(box(x, y, NODE_W, NODE_H, lines_tuple))

svg_parts.append('</svg>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg_parts))

print(f"Written: {OUT}")
