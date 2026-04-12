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

W, H = 1400, 560

def box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, rx=8, font_size=13):
    lines = text.split('\n')
    n = len(lines)
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    total_h = n * (font_size + 4)
    start_y = y + h/2 - total_h/2 + font_size
    for i, line in enumerate(lines):
        svg += f'<text x="{x+w/2}" y="{start_y + i*(font_size+4)}" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

def arrow(x1, y1, x2, y2, label=""):
    svg = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        svg += f'<text x="{mx+5}" y="{my-5}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{label}</text>'
    return svg

def arrow_v(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>''')

svg.append(f'<text x="{W//2}" y="38" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">Convert() 函式結構</text>')

# Top: Convert function
conv_x, conv_y = 500, 65
svg.append(box(conv_x, conv_y, 400, 50, 'Convert(vmi, c *ConverterContext)\n磁碟、介面、CPU、記憶體轉換入口', fill="#dbeafe", stroke=ARROW, font_size=13))

# Five children
children = [
    ('Convert_v1_Disk_To_api_Disk()\n處理每一顆磁碟\n決定 bus / target / driver', 60, 185),
    ('Convert_v1_Interface_To_api_Interface()\n網路介面 Model 轉換', 320, 185),
    ('Convert_v1_CPU_To_api_CPU()\nvCPU 數量 + Topology\nCPU Pinning', 560, 185),
    ('Convert_v1_Memory_To_api_Memory()\nHugepages / NUMA', 820, 185),
    ('convertDisksToStorages()\n將磁碟對應到實際儲存後端', 1060, 185),
]

for text, cx, cy in children:
    svg.append(box(cx, cy, 240, 65, text))
    # Arrow from conv center bottom to child top center
    svg.append(arrow(conv_x+200, conv_y+50, cx+120, cy))

# Sub-children for Disk (D1)
bus_x, bus_y = 60, 310
svg.append(box(bus_x, bus_y, 240, 75, '根據 bus 類型設定 target:\nvirtio → vdX\nsata → sdX\nscsi → sdX\nusb → sdX', font_size=11))
svg.append(arrow_v(180, 250, 310))

boot_x, boot_y = 60, 420
svg.append(box(boot_x, boot_y, 240, 52, 'BootOrder 對應\ndisk.bootOrder → domain bootOrder', font_size=12))
svg.append(arrow_v(180, 385, 420))

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-3.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
