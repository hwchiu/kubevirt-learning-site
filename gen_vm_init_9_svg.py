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

W, H = 1400, 680

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

svg.append(f'<text x="{W//2}" y="36" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">preStartHook() 執行流程</text>')

# Top level: SyncVMI -> GCC -> CONV -> PSH (horizontal)
sync_x, sync_y = 60, 65
gcc_x = 330
conv_x = 600
psh_y = 65

svg.append(box(sync_x, sync_y, 240, 44, 'SyncVMI 呼叫', fill="#dbeafe", stroke=ARROW))
svg.append(box(gcc_x, sync_y, 240, 44, 'generateConverterContext'))
svg.append(box(conv_x, sync_y, 240, 44, 'Convert VMI → Domain'))

svg.append(arrow_h(sync_x+240, sync_y+22, gcc_x))
svg.append(arrow_h(gcc_x+240, sync_y+22, conv_x))

# Down arrow from CONV to PSH container
psh_cont_y = 135
svg.append(arrow_v(conv_x+120, sync_y+44, psh_cont_y))

# preStartHook container
svg.append(container(80, psh_cont_y, 860, 420, 'preStartHook() 執行序列'))

steps = [
    ('1. 確認 cloudinit 資料就緒', 165),
    ('2. generateCloudInitISO\n生成 NoCloud ISO or ConfigDrive', 225),
    ('3. 執行 Hook Sidecars\n透過 gRPC\n讓外部插件修改 Domain XML', 310),
    ('4. expandDiskImagesOffline\n展開磁碟至最終大小\n避免稀疏檔造成空間問題', 410),
    ('5. setupGracefulShutdown\n設定 ACPI 關機信號', 500),
    ('6. 回傳修改後的 Domain', 565),
]

prev_y = None
for text, y in steps:
    h = 44 if '\n' not in text else (52 if text.count('\n') == 1 else 64)
    svg.append(box(120, y, 780, h, text))
    if prev_y is not None:
        svg.append(arrow_v(510, prev_y, y))
    prev_y = y + h

# After PSH: Define + Create
define_x, define_y = 1000, 330
start_x, start_y = 1000, 430

svg.append(arrow_h(900, 580, define_x, ''))
svg.append(f'<text x="940" y="570" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">完成</text>')

svg.append(box(define_x, define_y, 280, 64, 'libvirt DomainDefine\n寫入 Domain XML', fill="#dcfce7", stroke="#22c55e"))
svg.append(box(start_x, start_y, 280, 64, 'DomainCreate\n啟動 QEMU', fill="#dcfce7", stroke="#22c55e"))
svg.append(arrow_v(define_x+140, define_y+64, start_y))

# Connect from done to define
svg.append(f'<path d="M900,580 L{define_x+140},580 L{define_x+140},{define_y}" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-9.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
