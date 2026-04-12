#!/usr/bin/env python3
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
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

def diamond(cx, cy, hw, hh, text, font_size=12):
    pts = f'{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}'
    svg = f'<polygon points="{pts}" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>'
    lines = text.split('\n')
    lh = font_size + 3
    sy = cy - len(lines)*lh/2 + font_size - 2
    for i, line in enumerate(lines):
        svg += f'<text x="{cx}" y="{sy+i*lh}" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

def arrow_v(x, y1, y2, label="", label_right=True):
    svg = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        lx = x + 6 if label_right else x - 6
        anchor = "start" if label_right else "end"
        svg += f'<text x="{lx}" y="{(y1+y2)/2+4}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="{anchor}">{label}</text>'
    return svg

def arrow_h(x1, y, x2, label="", label_above=True):
    svg = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        ly = y - 8 if label_above else y + 14
        svg += f'<text x="{(x1+x2)/2}" y="{ly}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return svg

def arrow_custom(x1, y1, x2, y2, label="", label_offset_x=5, label_offset_y=-5):
    svg = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        mx, my = (x1+x2)//2+label_offset_x, (y1+y2)//2+label_offset_y
        svg += f'<text x="{mx}" y="{my}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{label}</text>'
    return svg

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>''')

svg.append(f'<text x="{W//2}" y="36" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">CloudInit ISO 生成流程</text>')

# Row 1: preStartHook -> generateCloudInitISO
psh_x, psh_y = 100, 65
svg.append(box(psh_x, psh_y, 240, 44, 'preStartHook 執行', fill="#dbeafe", stroke=ARROW))

gci_x, gci_y = 420, 65
svg.append(box(gci_x, gci_y, 240, 44, 'generateCloudInitISO'))
svg.append(arrow_h(psh_x+240, psh_y+22, gci_x))

# Decision diamond
d_cx, d_cy = 730, 87
svg.append(diamond(d_cx, d_cy, 100, 40, '資料來源'))
svg.append(arrow_h(gci_x+240, gci_y+22, d_cx-100))

# Four sources branching down
sources = [
    ('cloudInitNoCloud\n.userData', 150, 230, 'userData 字串\n直接寫入'),
    ('cloudInitNoCloud\n.userDataSecretRef', 420, 230, '從 Kubernetes Secret\n讀取 userData'),
    ('cloudInitNoCloud\n.userDataBase64', 690, 230, 'Base64 解碼\nuserData'),
    ('networkDataSecretRef', 960, 230, '從 Secret 讀取\nnetworkData'),
]

for label, sx, sy, box_text in sources:
    svg.append(arrow_custom(d_cx, d_cy+40, sx+100, sy, label, label_offset_y=-6))
    svg.append(box(sx, sy, 200, 52, box_text))

# All converge to mkisofs
mk_x, mk_y = 490, 340
svg.append(box(mk_x, mk_y, 300, 52, 'mkisofs / genisoimage\n產生 NoCloud ISO', fill="#dcfce7", stroke="#22c55e"))

for sx, sy, _ in [(150, 230, ''), (420, 230, ''), (690, 230, ''), (960, 230, '')]:
    svg.append(arrow_custom(sx+100, sy+52, mk_x+150, mk_y, '', 0, 0))

# ISO output
iso_x, iso_y = 410, 440
svg.append(box(iso_x, iso_y, 460, 52, '/var/run/kubevirt-private/vmi-disks/\ncloudinitnocloud/noCloud.iso', fill="#f0fdf4", stroke="#86efac", font_size=12))
svg.append(arrow_v(mk_x+150, mk_y+52, iso_y))

# Mount to VM
vm_x, vm_y = 490, 530
svg.append(box(vm_x, vm_y, 300, 40, '掛載到 VM 作為 CD-ROM', fill="#fef3c7", stroke="#f59e0b"))
svg.append(arrow_v(mk_x+150, iso_y+52, vm_y))

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-6.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
