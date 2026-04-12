#!/usr/bin/env python3
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1400, 580

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

def msg(x1, y, x2, label, color=ARROW, dashed=False):
    dash = 'stroke-dasharray="6,3"' if dashed else ''
    dx = 1 if x2 > x1 else -1
    svg = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="2" {dash} marker-end="url(#arrow)"/>'
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
  <marker id="arrow-ret" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#6b7280"/>
  </marker>
</defs>''')

svg.append(f'<text x="{W//2}" y="35" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">ContainerDisk 初始化序列</text>')

# Participants
participants = [
    ('Kubernetes', 180, "#dbeafe", "#3b82f6"),
    ('container-disk\nInit Container', 520, "#fef3c7", "#f59e0b"),
    ('virt-launcher\n主容器', 860, "#dcfce7", "#22c55e"),
    ('QEMU', 1200, "#ede9fe", "#8b5cf6"),
]

header_y = 55
header_h = 55
for name, cx, fill, stroke in participants:
    svg.append(swimlane_header(cx-100, header_y, 200, header_h, name, fill, stroke))

lifeline_y_start = header_y + header_h
lifeline_y_end = H - 30
for _, cx, _, _ in participants:
    svg.append(lifeline(cx, lifeline_y_start, lifeline_y_end))

k_x, ic_x, vl_x, q_x = 180, 520, 860, 1200

# Messages
y = 145
svg.append(msg(k_x, y, ic_x, '啟動 Init Container'))
y += 50
svg.append(note(ic_x-90, y, 240, '從 OCI Registry 拉取映像'))
y += 48
svg.append(self_msg(ic_x, y, '掛載 OCI 映像層'))
y += 55
svg.append(self_msg(ic_x, y, '找到 /disk/disk.img or /disk/disk.qcow2'))
y += 55
svg.append(self_msg(ic_x, y, '複製到 emptyDir /var/run/kubevirt/container-disks/'))
y += 55
# dashed return
svg.append(f'<line x1="{ic_x}" y1="{y}" x2="{k_x}" y2="{y}" stroke="#6b7280" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arrow-ret)"/>')
svg.append(f'<text x="{(ic_x+k_x)//2}" y="{y-7}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">Init Container 完成</text>')

y += 50
svg.append(msg(k_x, y, vl_x, '啟動 virt-launcher'))
y += 50
svg.append(self_msg(vl_x, y, '偵測 emptyDir 中的磁碟'))
y += 50
svg.append(self_msg(vl_x, y, 'Convert() 設定磁碟路徑'))
y += 50
svg.append(msg(vl_x, y, q_x, '啟動並掛載磁碟'))

svg.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-5.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg))
print(f'Written: {out_path}')
