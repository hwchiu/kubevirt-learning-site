#!/usr/bin/env python3
# auxiliary-binaries.md Block 2: Container Disk Sequence - sequenceDiagram

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
LIFELINE = "#e5e7eb"
ARROW = "#3b82f6"
ARROW_DASH = "#9ca3af"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
ACTOR_FILL = "#eff6ff"
ACTOR_STROKE = "#bfdbfe"

OUT = "docs-site/public/diagrams/kubevirt/kubevirt-aux-container-disk-sequence.svg"

W, H = 1000, 800
ACTOR_W = 140
ACTOR_H = 50
TOP_Y = 80
LIFELINE_START = TOP_Y + ACTOR_H + 20

def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
  <marker id="arrow-dash" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#9ca3af"/>
  </marker>
</defs>'''

def actor(x, y, label):
    svg = f'<rect x="{x-ACTOR_W/2}" y="{y}" width="{ACTOR_W}" height="{ACTOR_H}" rx="4" fill="{ACTOR_FILL}" stroke="{ACTOR_STROKE}" stroke-width="2"/>'
    lines = label.split('\n')
    if len(lines) == 1:
        svg += f'<text x="{x}" y="{y+ACTOR_H/2+5}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    else:
        for i, line in enumerate(lines):
            svg += f'<text x="{x}" y="{y+20+i*14}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{arrow_marker()}
<rect width="{W}" height="{H}" fill="{BG}"/>

<!-- Title -->
<text x="500" y="40" font-family="{FONT}" font-size="16" font-weight="bold" fill="{TEXT_PRIMARY}" text-anchor="middle">Container Disk 啟動流程</text>
'''

# Actors
actors = [
    "virt-handler",
    "container-disk-\nv2alpha",
    "QEMU",
]

positions = {}
for i, label in enumerate(actors):
    x = 150 + i * 300
    svg += actor(x, TOP_Y, label) + '\n'
    positions[label.replace('\n', '')] = x
    # Lifeline
    svg += f'<line x1="{x}" y1="{LIFELINE_START}" x2="{x}" y2="{H-40}" stroke="{LIFELINE}" stroke-width="2" stroke-dasharray="5,5"/>\n'

# Messages
y = LIFELINE_START + 30
messages = [
    (150, 400, y, "啟動 Init Container", False),
    (400, 400, y+60, "建立 Unix domain socket\n/var/run/kubevirt/container-disks/disk_0.sock", True),
    (400, 400, y+140, "啟動心跳機制 (檢查 socket 存在)", True),
    (150, 750, y+220, "啟動 QEMU 程序", False),
    (750, 400, y+280, "透過 socket 連接", False),
    (400, 750, y+340, "串流磁碟映像資料", True),
]

for x1, x2, ypos, label, is_self in messages:
    if is_self:
        # Self-call arrow
        svg += f'<line x1="{x1}" y1="{ypos}" x2="{x1+50}" y2="{ypos}" stroke="{ARROW}" stroke-width="2"/>\n'
        svg += f'<line x1="{x1+50}" y1="{ypos}" x2="{x1+50}" y2="{ypos+40}" stroke="{ARROW}" stroke-width="2"/>\n'
        svg += f'<line x1="{x1+50}" y1="{ypos+40}" x2="{x1}" y2="{ypos+40}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
        lines = label.split('\n')
        for i, line in enumerate(lines):
            svg += f'<text x="{x1+60}" y="{ypos+15+i*13}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{line}</text>\n'
    else:
        direction = 1 if x2 > x1 else -1
        svg += f'<line x1="{x1}" y1="{ypos}" x2="{x2}" y2="{ypos}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
        mid_x = (x1 + x2) / 2
        lines = label.split('\n')
        for i, line in enumerate(lines):
            svg += f'<text x="{mid_x}" y="{ypos-8-len(lines)*7+i*13}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{line}</text>\n'

# Note box
note_y = y + 400
svg += f'''
<rect x="320" y="{note_y}" width="280" height="60" rx="4" fill="#fffbeb" stroke="#fbbf24" stroke-width="2"/>
<text x="460" y="{note_y+20}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">Socket 持續監聽中...</text>
<text x="460" y="{note_y+40}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">定期檢查 socket 檔案是否存在</text>
'''

# Loop indication
loop_y = y + 480
svg += f'''
<rect x="50" y="{loop_y}" width="900" height="80" rx="4" fill="none" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<text x="70" y="{loop_y+25}" font-family="{FONT}" font-size="11" font-weight="bold" fill="{TEXT_SECONDARY}">心跳檢查 loop</text>
<text x="400" y="{loop_y+50}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">定期檢查 socket 檔案是否存在 — 若 socket 消失則停止服務</text>
'''

svg += '</svg>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f'Written: {OUT}')
