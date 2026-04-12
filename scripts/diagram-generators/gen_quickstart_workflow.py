#!/usr/bin/env python3
# quickstart.md Block 3: Complete Workflow - graph TD

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
DIAMOND_FILL = "#eff6ff"
DIAMOND_STROKE = "#bfdbfe"

OUT = "docs-site/public/diagrams/kubevirt/kubevirt-quickstart-complete-workflow.svg"

W, H = 1200, 1400
NODE_W, NODE_H = 160, 40
DIAMOND_SIZE = 80
GAP_X, GAP_Y = 200, 80

def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
</defs>'''

def box(x, y, w, h, label):
    lines = label.split('\n')
    svg = f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="4" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>'
    if len(lines) == 1:
        svg += f'<text x="{x}" y="{y+5}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    else:
        for i, line in enumerate(lines):
            svg += f'<text x="{x}" y="{y-10+i*14}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

def diamond(x, y, size, label):
    points = f"{x},{y-size} {x+size},{y} {x},{y+size} {x-size},{y}"
    svg = f'<polygon points="{points}" fill="{DIAMOND_FILL}" stroke="{DIAMOND_STROKE}" stroke-width="2"/>'
    svg += f'<text x="{x}" y="{y+4}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    return svg

def arrow(x1, y1, x2, y2, label=""):
    svg = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
        svg += f'<text x="{mid_x+10}" y="{mid_y-5}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{label}</text>'
    return svg

# Node positions
cx = W / 2
nodes = [
    (cx, 50, "安裝 KubeVirt Operator"),
    (cx, 130, "部署 kubevirt CR"),
    (cx, 210, "安裝 virtctl CLI"),
    (cx, 310, "D", "選擇 VM 類型"),  # Diamond
    (cx-150, 410, "建立 Linux VM YAML"),
    (cx+150, 410, "建立 Windows VM YAML"),
    (cx, 510, "kubectl apply"),
    (cx, 590, "等待 VM Running"),
    (cx, 690, "I", "連線方式"),  # Diamond
    (cx-250, 790, "virtctl console"),
    (cx, 790, "virtctl vnc"),
    (cx+250, 790, "virtctl ssh"),
    (cx+150, 910, "日常操作"),
    (cx+150, 1010, "start / stop / restart"),
    (cx+150, 1110, "migrate / snapshot / clone"),
    (cx+150, 1210, "添加磁碟 / 設定網路"),
]

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{arrow_marker()}
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Draw nodes
for item in nodes:
    if len(item) == 4:  # Diamond
        x, y, node_id, label = item
        svg += diamond(x, y, 70, label) + '\n'
    else:
        x, y, label = item
        svg += box(x, y, NODE_W, NODE_H, label) + '\n'

# Draw arrows
arrows = [
    (cx, 70, cx, 110),
    (cx, 150, cx, 190),
    (cx, 230, cx, 250),  # to diamond D
    (cx-60, 310, cx-150, 390, "Linux"),  # D to E
    (cx+60, 310, cx+150, 390, "Windows"),  # D to F
    (cx-150, 430, cx, 490),  # E to G
    (cx+150, 430, cx, 490),  # F to G
    (cx, 530, cx, 570),  # G to H
    (cx, 610, cx, 630),  # H to I diamond
    (cx-80, 690, cx-250, 770, "文字"),  # I to J
    (cx, 710, cx, 770, "圖形"),  # I to K
    (cx+80, 690, cx+250, 770, "SSH"),  # I to L
    (cx, 610, cx+150, 890),  # H to M
    (cx+150, 930, cx+150, 990),  # M to N
    (cx+150, 1030, cx+150, 1090),  # N to O
    (cx+150, 1130, cx+150, 1190),  # O to P
]

for a in arrows:
    svg += arrow(*a) + '\n'

svg += '</svg>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f'Written: {OUT}')
