#!/usr/bin/env python3
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1200, 560

def swimlane_header(x, y, w, h, text, fill="#dbeafe", stroke="#3b82f6"):
    lines = text.split('\n')
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    lh = 15
    sy = y + h/2 - len(lines)*lh/2 + 13
    for i, line in enumerate(lines):
        svg += f'<text x="{x+w/2}" y="{sy+i*lh}" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

def lifeline(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#d1d5db" stroke-width="1.5" stroke-dasharray="6,4"/>'

def msg(x1, y, x2, label, dashed=False):
    dash = 'stroke-dasharray="6,3"' if dashed else ''
    svg = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="2" {dash} marker-end="url(#arrow)"/>'
    mid = (x1+x2)/2
    svg += f'<text x="{mid}" y="{y-7}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return svg

def self_msg(x, y, label):
    svg = f'<path d="M{x},{y} Q{x+60},{y} {x+60},{y+20} Q{x+60},{y+40} {x},{y+40}" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>'
    svg += f'<text x="{x+70}" y="{y+22}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{label}</text>'
    return svg

def note(x, y, w, text):
    lines = text.split('\n')
    h = len(lines)*16 + 12
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#fef9c3" stroke="#fbbf24" stroke-width="1"/>'
    for i, line in enumerate(lines):
        svg += f'<text x="{x+w/2}" y="{y+14+i*16}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>''')

svg.append(f'<text x="{W//2}" y="36" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">Sysprep 自動化安裝序列</text>')

participants = [
    ('使用者', 140, "#fef3c7", "#f59e0b"),
    ('Kubernetes API', 400, "#dbeafe", "#3b82f6"),
    ('virt-launcher', 680, "#dcfce7", "#22c55e"),
    ('Windows VM', 980, "#ede9fe", "#8b5cf6"),
]

header_y, header_h = 55, 55
for name, cx, fill, stroke in participants:
    svg.append(swimlane_header(cx-100, header_y, 200, header_h, name, fill, stroke))

ll_start = header_y + header_h
ll_end = H - 30
for _, cx, _, _ in participants:
    svg.append(lifeline(cx, ll_start, ll_end))

u_x, api_x, vl_x, w_x = 140, 400, 680, 980

y = 145
svg.append(msg(u_x, y, api_x, '建立包含 unattend.xml 的 ConfigMap'))
y += 45
svg.append(msg(u_x, y, api_x, '建立 VMI 引用此 ConfigMap'))
y += 45
svg.append(msg(api_x, y, vl_x, 'SyncVMI'))
y += 45
svg.append(self_msg(vl_x, y, 'Convert_v1_SysprepSource_To_api_Disk()'))
y += 55
svg.append(note(vl_x-100, y, 260, '將 ConfigMap 內容\n掛載為 virtio-fs 或 ISO'))
y += 52
svg.append(msg(vl_x, y, w_x, '啟動 Windows VM'))
y += 45
svg.append(self_msg(w_x, y, '偵測 Sysprep 磁碟'))
y += 55
svg.append(self_msg(w_x, y, '執行 sysprep /unattend'))
y += 55
svg.append(self_msg(w_x, y, '首次開機設定完成'))

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-7.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
