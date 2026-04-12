#!/usr/bin/env python3
# GPU Device Plugin Lifecycle - graph LR

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

OUT = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-gpu-device-lifecycle.svg"

W, H = 1400, 220
NODE_W, NODE_H = 140, 48
GAP_X = 60
START_X = 40
START_Y = (H - NODE_H) // 2

nodes = [
    ("A", "探索 Discovery"),
    ("B", "註冊 Registration"),
    ("C", "ListAndWatch"),
    ("D", "等待分配"),
    ("E", "Allocate"),
    ("F", "Pod 啟動"),
]

edge_labels = [
    "掃描 sysfs",
    "gRPC 連線 Kubelet",
    "回報裝置清單",
    "Pod 請求資源",
    "回傳裝置資訊",
]

# Compute positions
positions = {}
for i, (nid, _) in enumerate(nodes):
    x = START_X + i * (NODE_W + GAP_X)
    positions[nid] = (x, START_Y)

# F -> D back arc
def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
</defs>'''

def box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = label.split('\n')
    cy = y + h // 2
    if len(lines) == 1:
        text = f'<text x="{x + w//2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}">{lines[0]}</text>'
    else:
        dy_start = -(len(lines)-1) * 9
        tspans = ''.join(f'<tspan x="{x + w//2}" dy="{dy_start + i*18}">{l}</tspan>' for i, l in enumerate(lines))
        text = f'<text x="{x + w//2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}">{tspans}</text>'
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

# Draw arrows first
for i in range(len(nodes) - 1):
    nid_a = nodes[i][0]
    nid_b = nodes[i+1][0]
    ax, ay = positions[nid_a]
    bx, by = positions[nid_b]
    x1 = ax + NODE_W
    y1 = ay + NODE_H // 2
    x2 = bx
    y2 = by + NODE_H // 2
    lbl = edge_labels[i] if i < len(edge_labels) else ""
    svg_parts.append(arrow_line(x1, y1, x2, y2, lbl))

# F -> D back arc (curved path below)
fx, fy = positions["F"]
dx, dy = positions["D"]
fx_mid = fx + NODE_W // 2
dx_mid = dx + NODE_W // 2
arc_y = fy + NODE_H + 40
back_path = f'<path d="M {fx_mid} {fy + NODE_H} Q {fx_mid} {arc_y} {(fx_mid+dx_mid)//2} {arc_y} Q {dx_mid} {arc_y} {dx_mid} {dy + NODE_H}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>'
back_label_x = (fx_mid + dx_mid) // 2
back_label_y = arc_y + 16
svg_parts.append(back_path)
svg_parts.append(f'<text x="{back_label_x}" y="{back_label_y}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Pod 終止</text>')

# Draw boxes
for nid, label in nodes:
    x, y = positions[nid]
    svg_parts.append(box(x, y, NODE_W, NODE_H, label))

svg_parts.append('</svg>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg_parts))

print(f"Written: {OUT}")
