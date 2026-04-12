#!/usr/bin/env python3
# quickstart.md Block 1: VM Connection Methods - graph LR

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
ACCENT_FILL = "#eff6ff"
ACCENT_STROKE = "#bfdbfe"

OUT = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-quickstart-connect-methods.svg"

W, H = 1000, 340
NODE_W, NODE_H = 160, 52
SRC_W, SRC_H = 100, 52

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

def src_box(x, y, w, h, label):
    # Stadium-style rounded box for source
    cy = y + h // 2
    text = f'<text x="{x + w//2}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" font-size="15" fill="{TEXT_PRIMARY}" font-weight="600">{label}</text>'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>\n{text}'

svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg_parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg_parts.append(arrow_marker())

# Source A: 使用者, placed at left center
A_X = 40
A_Y = (H - SRC_H) // 2
svg_parts.append(src_box(A_X, A_Y, SRC_W, SRC_H, "使用者"))

# 4 targets, evenly spaced vertically
targets = [
    ("virtctl console", "序列控制台\nSerial Console"),
    ("virtctl vnc", "圖形桌面\nVNC"),
    ("virtctl ssh", "SSH 連線"),
    ("kubectl port-forward", "自訂 Port\nForwarding"),
]

gap = (H - 20) / len(targets)
target_x = A_X + SRC_W + 180

for i, (label, box_label) in enumerate(targets):
    ty = 20 + int(i * gap) + (int(gap) - NODE_H) // 2
    tx = target_x
    svg_parts.append(box(tx, ty, NODE_W, NODE_H, box_label))
    # Arrow from A to target
    ax_right = A_X + SRC_W
    ay_mid = A_Y + SRC_H // 2
    ty_mid = ty + NODE_H // 2
    mid_x = (ax_right + tx) // 2
    # Elbow
    svg_parts.append(f'<path d="M {ax_right} {ay_mid} L {mid_x - 20} {ay_mid} L {mid_x - 20} {ty_mid} L {tx} {ty_mid}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>')
    # Label
    svg_parts.append(f'<text x="{mid_x}" y="{ty_mid - 8}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{label}</text>')

svg_parts.append('</svg>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg_parts))

print(f"Written: {OUT}")
