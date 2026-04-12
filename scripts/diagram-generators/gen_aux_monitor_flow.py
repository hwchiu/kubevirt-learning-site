#!/usr/bin/env python3
# auxiliary-binaries.md Block 3: virt-launcher-monitor - graph LR

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
MONITOR_FILL = "#fef3c7"
MONITOR_STROKE = "#f59e0b"

OUT = "docs-site/public/diagrams/kubevirt/kubevirt-aux-launcher-monitor-flow.svg"

W, H = 1100, 400

def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
</defs>'''

def box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = label.split('\n')
    svg = f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    if len(lines) == 1:
        svg += f'<text x="{x}" y="{y+5}" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    else:
        base_y = y - (len(lines)-1)*6
        for i, line in enumerate(lines):
            svg += f'<text x="{x}" y="{base_y+i*15}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{arrow_marker()}
<rect width="{W}" height="{H}" fill="{BG}"/>

<text x="550" y="40" font-family="{FONT}" font-size="16" font-weight="bold" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-launcher-monitor 監控架構</text>
'''

# Nodes
nodes = [
    (150, 200, 180, 60, "virt-launcher-monitor", MONITOR_FILL, MONITOR_STROKE),
    (450, 120, 160, 50, "virt-launcher", BOX_FILL, BOX_STROKE),
    (450, 200, 160, 50, "Passt daemon", BOX_FILL, BOX_STROKE),
    (450, 280, 160, 50, "Envoy proxy", BOX_FILL, BOX_STROKE),
    (750, 200, 160, 50, "virt-handler", "#f0fdf4", "#86efac"),
]

for x, y, w, h, label, fill, stroke in nodes:
    svg += box(x, y, w, h, label, fill, stroke) + '\n'

# Arrows
arrows = [
    (230, 180, 370, 130, "程序健康檢查"),
    (230, 200, 370, 200, "daemon 狀態檢查"),
    (230, 220, 370, 270, "連線檢查"),
    (670, 200, 670, 200, "回報狀態"),
]

for x1, y1, x2, y2, label in arrows:
    svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
    mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
    svg += f'<text x="{mid_x}" y="{mid_y-8}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>\n'

svg += '</svg>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f'Written: {OUT}')
