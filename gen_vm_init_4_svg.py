#!/usr/bin/env python3
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1400, 600

def box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, rx=8, font_size=13):
    lines = text.split('\n')
    n = len(lines)
    svg_txt = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    total_h = n * (font_size + 4)
    start_y = y + h/2 - total_h/2 + font_size
    for i, line in enumerate(lines):
        svg_txt += f'<text x="{x+w/2}" y="{start_y + i*(font_size+4)}" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg_txt

def leaf(x, y, w, h, text, fill=BOX_FILL, font_size=12):
    lines = text.split('\n')
    svg_txt = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{BOX_STROKE}" stroke-width="1"/>'
    lh = font_size + 3
    start_y = y + h/2 - len(lines)*lh/2 + font_size
    for i, line in enumerate(lines):
        svg_txt += f'<text x="{x+w/2}" y="{start_y + i*lh}" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg_txt

def conn(x1, y1, x2, y2):
    mx = (x1+x2)//2
    return f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>'

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'''<defs>
  <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0.5, 7 3, 0 5.5" fill="{ARROW}"/>
  </marker>
</defs>''')

svg.append(f'<text x="{W//2}" y="38" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">VM 磁碟來源分類</text>')

# Central root
root_w, root_h = 200, 60
root_x, root_y = W//2 - root_w//2, H//2 - root_h//2
svg.append(box(root_x, root_y, root_w, root_h, 'VM 磁碟來源', fill="#dbeafe", stroke=ARROW, rx=30, font_size=15))

# Four branches: ContainerDisk, PVC/DataVolume, CloudInit, Sysprep
branches = [
    {
        'title': 'ContainerDisk',
        'color': '#fef3c7',
        'stroke': '#f59e0b',
        'x': 100,
        'y': 120,
        'leaves': ['OCI 映像包含磁碟', 'Init Container 展開', '無狀態 / 暫存'],
    },
    {
        'title': 'PVC / DataVolume',
        'color': '#dcfce7',
        'stroke': '#22c55e',
        'x': 100,
        'y': 380,
        'leaves': ['持久化儲存', 'CDI 自動匯入', 'Block / Filesystem 模式'],
    },
    {
        'title': 'CloudInit',
        'color': '#ede9fe',
        'stroke': '#8b5cf6',
        'x': 950,
        'y': 120,
        'leaves': ['noCloud 模式', 'ConfigDrive 模式', '合成 ISO'],
    },
    {
        'title': 'Sysprep',
        'color': '#fce7f3',
        'stroke': '#ec4899',
        'x': 950,
        'y': 380,
        'leaves': ['Windows 無人值守安裝', 'ConfigMap / Secret', 'unattend.xml'],
    },
]

bw, bh = 220, 44
lw, lh = 200, 34

for b in branches:
    bx, by = b['x'], b['y']
    svg.append(box(bx, by, bw, bh, b['title'], fill=b['color'], stroke=b['stroke'], rx=10, font_size=14))
    # connect from root to branch
    if bx < root_x:
        svg.append(conn(bx+bw, by+bh//2, root_x, root_y+root_h//2))
    else:
        svg.append(conn(root_x+root_w, root_y+root_h//2, bx, by+bh//2))
    # leaves
    leaf_start_x = bx + (bw-lw)//2
    leaf_start_y = by + bh + 15
    for i, ltext in enumerate(b['leaves']):
        ly = leaf_start_y + i * (lh + 8)
        svg.append(leaf(leaf_start_x, ly, lw, lh, ltext, fill=b['color']))
        svg.append(f'<line x1="{bx+bw//2}" y1="{by+bh}" x2="{leaf_start_x+lw//2}" y2="{ly}" stroke="{b["stroke"]}" stroke-width="1" stroke-dasharray="4,3"/>')

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-4.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
