#!/usr/bin/env python3
# auxiliary-binaries.md Block 5: Export Proxy Architecture - graph LR

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
USER_FILL = "#fef3c7"
USER_STROKE = "#f59e0b"
PROXY_FILL = "#eff6ff"
PROXY_STROKE = "#bfdbfe"
SERVER_FILL = "#f0fdf4"
SERVER_STROKE = "#86efac"
STORAGE_FILL = "#fce7f3"
STORAGE_STROKE = "#f472b6"

OUT = "docs-site/public/diagrams/kubevirt/kubevirt-aux-export-proxy-arch.svg"

W, H = 1200, 500

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
        base_y = y - (len(lines)-1)*7
        for i, line in enumerate(lines):
            svg += f'<text x="{x}" y="{base_y+i*15}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{arrow_marker()}
<rect width="{W}" height="{H}" fill="{BG}"/>

<text x="600" y="40" font-family="{FONT}" font-size="16" font-weight="bold" fill="{TEXT_PRIMARY}" text-anchor="middle">VM Export Proxy 架構</text>
'''

# Nodes
nodes = [
    (150, 250, 180, 70, "外部使用者", USER_FILL, USER_STROKE),
    (450, 250, 200, 80, "virt-exportproxy\n(kubevirt NS)", PROXY_FILL, PROXY_STROKE),
    (800, 150, 200, 70, "virt-exportserver\n(匯出 Pod 1)", SERVER_FILL, SERVER_STROKE),
    (800, 350, 200, 70, "virt-exportserver\n(匯出 Pod 2)", SERVER_FILL, SERVER_STROKE),
    (1050, 150, 120, 60, "PVC /\nSnapshot", STORAGE_FILL, STORAGE_STROKE),
    (1050, 350, 120, 60, "PVC /\nSnapshot", STORAGE_FILL, STORAGE_STROKE),
]

for x, y, w, h, label, fill, stroke in nodes:
    svg += box(x, y, w, h, label, fill, stroke) + '\n'

# Arrows
arrows = [
    (240, 250, 350, 250, "HTTPS + Token"),
    (550, 230, 700, 165, "反向代理"),
    (550, 270, 700, 335, "反向代理"),
    (900, 150, 990, 150, "讀取"),
    (900, 350, 990, 350, "讀取"),
]

for x1, y1, x2, y2, label in arrows:
    svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
    mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
    svg += f'<text x="{mid_x}" y="{mid_y-8}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>\n'

svg += '</svg>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f'Written: {OUT}')
