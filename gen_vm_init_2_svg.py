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

W, H = 1600, 620

def box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, rx=8, font_size=13):
    lines = text.split('\n')
    n = len(lines)
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    total_h = n * (font_size + 4)
    start_y = y + h/2 - total_h/2 + font_size
    for i, line in enumerate(lines):
        svg += f'<text x="{x+w/2}" y="{start_y + i*(font_size+4)}" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

def arrow_h(x1, y, x2, label="", label_above=True):
    svg = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        ly = y - 8 if label_above else y + 14
        svg += f'<text x="{(x1+x2)/2}" y="{ly}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return svg

def arrow_v(x, y1, y2, label="", label_right=True):
    svg = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        lx = x + 6 if label_right else x - 6
        anchor = "start" if label_right else "end"
        svg += f'<text x="{lx}" y="{(y1+y2)/2+4}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="{anchor}">{label}</text>'
    return svg

def container(x, y, w, h, title, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE):
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="6,3"/>'
    svg += f'<text x="{x+14}" y="{y+20}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" font-weight="600">{title}</text>'
    return svg

def line(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" stroke-dasharray="4,3"/>'

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>''')

svg.append(f'<text x="{W//2}" y="38" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">VMI Spec → Domain XML 轉換流程</text>')

# Input: VMI Spec
svg.append(box(30, 265, 160, 50, 'VMI Spec\nkubevirt.io/v1', fill="#dbeafe", stroke=ARROW))
svg.append(arrow_h(190, 290, 260, '輸入'))

# generateConverterContext container
svg.append(container(260, 60, 380, 460, 'generateConverterContext()'))
svg.append(box(300, 95, 300, 44, 'GCC: 蒐集執行環境資訊', fill="#e0e7ff", stroke=CONTAINER_STROKE))

items_gcc = [
    ('節點拓撲\nNUMA / CPU', 155),
    ('設備設定\n/proc/cmdline\nKVM capabilities', 215),
    ('SR-IOV 設備', 310),
    ('GPU 設備', 360),
    ('網路設定\n介面對應', 410),
]
for text, y in items_gcc:
    svg.append(box(300, y, 300, 44, text))
    svg.append(arrow_v(450, 139, y, ''))

# Arrow from GCC to ConverterContext
svg.append(arrow_h(640, 290, 720, 'ConverterContext'))

# Convert() container
svg.append(container(720, 60, 820, 530, 'Convert(vmi, ctx)'))
svg.append(box(760, 95, 280, 44, '初始化 Domain 結構', fill="#e0e7ff", stroke=CONTAINER_STROKE))

conv_items = [
    'Convert CPU\nvCPU數量 / Topology\nCPU Model / Features',
    'Convert Memory\nHugepages / NUMA',
    'Convert Disks\n磁碟 + 映像來源',
    'Convert Networks\nvirtio / e1000 / SR-IOV',
    'Convert Clock\nRTC / Hypervisor Timer',
    'Convert Firmware\nBIOS / EFI / Secure Boot',
    'Convert Video\nVGA / Virtio-GPU',
    'Convert Sound\nAC97 / ICH9',
    'Convert Features\nACPI / APIC / SMM',
]

# Two columns
col1 = conv_items[:5]
col2 = conv_items[5:]

for i, text in enumerate(col1):
    by = 155 + i * 65
    svg.append(box(740, by, 240, 52, text))
    svg.append(arrow_v(900, 139, by, ''))

for i, text in enumerate(col2):
    by = 155 + i * 72
    svg.append(box(1000, by, 240, 52, text))
    svg.append(arrow_v(900, 139, by, ''))

# Arrow to libvirtd
svg.append(arrow_h(1540, 310, 1580, 'libvirt Domain XML'))

# Output: libvirtd
svg.append(box(1540, 285, 40, 50, '', fill=BG, stroke=BG))  # spacer
svg.append(arrow_h(1540, 310, 1580, ''))
svg.append(box(1555, 285, 20, 50, '', fill=BG, stroke=BG))

# Actually draw libvirtd box at far right
svg.append(box(1560, 270, 20, 50, '', fill=BG))

# Redraw better
# Output arrow and libvirtd
svg2 = f'<line x1="1540" y1="310" x2="1590" y2="310" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
svg2 += f'<text x="1545" y="303" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">libvirt Domain XML</text>'
svg.append(svg2)

svg.append(box(1590, 278, 160, 64, 'libvirtd', fill="#dcfce7", stroke="#86efac"))

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-2.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
