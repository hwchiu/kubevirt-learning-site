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

W, H = 1200, 360

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
        svg += f'<text x="{(x1+x2)/2}" y="{ly}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return svg

def arrow_v(x, y1, y2, label="", label_right=True):
    svg = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        lx = x + 6 if label_right else x - 6
        anchor = "start" if label_right else "end"
        svg += f'<text x="{lx}" y="{(y1+y2)/2+4}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="{anchor}">{label}</text>'
    return svg

def container(x, y, w, h, title, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE):
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="6,3"/>'
    svg += f'<text x="{x+12}" y="{y+18}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" font-weight="600">{title}</text>'
    return svg

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>''')

svg.append(f'<text x="{W//2}" y="36" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">EFI NVRAM 管理架構</text>')

# OVMF template
ovmf_x, ovmf_y = 60, 130
svg.append(box(ovmf_x, ovmf_y, 220, 64, 'OVMF_VARS.fd\n模板檔案', fill="#fef3c7", stroke="#f59e0b"))

# virt-launcher container
svg.append(container(340, 80, 440, 170, 'virt-launcher Pod'))

# NVRAM
nvram_x, nvram_y = 360, 120
svg.append(box(nvram_x, nvram_y, 400, 80, '/var/run/kubevirt-private/\nlibvirt/qemu/nvram/\nvmi-name_VARS.fd', fill="#ede9fe", stroke="#8b5cf6", font_size=12))

svg.append(arrow_h(ovmf_x+220, ovmf_y+32, nvram_x, '首次啟動複製'))

# QEMU
qemu_x, qemu_y = 840, 130
svg.append(box(qemu_x, qemu_y, 200, 64, 'QEMU\nEFI 運行時', fill="#dcfce7", stroke="#22c55e"))
svg.append(arrow_h(nvram_x+400, nvram_y+40, qemu_x, '掛載'))

# PVC
pvc_x, pvc_y = 840, 240
svg.append(box(pvc_x, pvc_y, 200, 64, 'PVC\nor hostPath', fill="#f0fdf4", stroke="#86efac"))

# Arrow from NVRAM down to PVC
svg.append(f'<line x1="{nvram_x+200}" y1="{nvram_y+80}" x2="{pvc_x+100}" y2="{pvc_y}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>')
svg.append(f'<text x="{nvram_x+300}" y="{(nvram_y+80+pvc_y)//2}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">重啟保留</text>')

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-8.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
