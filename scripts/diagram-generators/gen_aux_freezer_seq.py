#!/usr/bin/env python3
# auxiliary-binaries.md Block 4: virt-freezer sequence - sequenceDiagram

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
LIFELINE = "#e5e7eb"
ARROW = "#3b82f6"
ARROW_RETURN = "#9ca3af"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
ACTOR_FILL = "#eff6ff"
ACTOR_STROKE = "#bfdbfe"

OUT = "docs-site/public/diagrams/kubevirt/kubevirt-aux-freezer-sequence.svg"

W, H = 1400, 900
ACTOR_W = 140
ACTOR_H = 50
TOP_Y = 80
LIFELINE_START = TOP_Y + ACTOR_H + 20

def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
  <marker id="arrow-return" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto">
    <polygon points="8.5 0.5, 0 3.5, 8.5 6.5" fill="#9ca3af"/>
  </marker>
</defs>'''

def actor(x, y, label):
    svg = f'<rect x="{x-ACTOR_W/2}" y="{y}" width="{ACTOR_W}" height="{ACTOR_H}" rx="4" fill="{ACTOR_FILL}" stroke="{ACTOR_STROKE}" stroke-width="2"/>'
    lines = label.split('\n')
    if len(lines) == 1:
        svg += f'<text x="{x}" y="{y+ACTOR_H/2+5}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    else:
        for i, line in enumerate(lines):
            svg += f'<text x="{x}" y="{y+18+i*13}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{arrow_marker()}
<rect width="{W}" height="{H}" fill="{BG}"/>

<text x="700" y="40" font-family="{FONT}" font-size="16" font-weight="bold" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-freezer 檔案系統凍結流程</text>
'''

# Actors
actors = [
    ("Snapshot\nController", 120),
    ("virt-freezer", 320),
    ("virt-launcher\n(gRPC)", 520),
    ("QEMU Monitor\n(QMP)", 720),
    ("Guest Agent", 920),
    ("Guest\nFilesystem", 1120),
]

for label, x in actors:
    svg += actor(x, TOP_Y, label) + '\n'
    svg += f'<line x1="{x}" y1="{LIFELINE_START}" x2="{x}" y2="{H-40}" stroke="{LIFELINE}" stroke-width="2" stroke-dasharray="5,5"/>\n'

# Messages - Freeze phase
y = LIFELINE_START + 40
messages = [
    (120, 320, y, "執行 freeze 命令", False),
    (320, 520, y+60, "gRPC 連接至 virt-launcher", False),
    (520, 720, y+120, "發送 QMP 命令", False),
    (720, 920, y+180, "guest-fsfreeze-freeze", False),
    (920, 1120, y+240, "fsfreeze --freeze (Linux)\nVSS freeze (Windows)", False),
    (1120, 920, y+300, "I/O 已凍結", True),
    (920, 720, y+340, "回應成功", True),
    (720, 520, y+380, "確認凍結", True),
    (520, 320, y+420, "回傳結果", True),
]

for x1, x2, ypos, label, is_return in messages:
    direction = 1 if x2 > x1 else -1
    if is_return:
        svg += f'<line x1="{x2}" y1="{ypos}" x2="{x1}" y2="{ypos}" stroke="{ARROW_RETURN}" stroke-width="2" stroke-dasharray="5,5" marker-start="url(#arrow-return)"/>\n'
    else:
        svg += f'<line x1="{x1}" y1="{ypos}" x2="{x2}" y2="{ypos}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
    
    mid_x = (x1 + x2) / 2
    lines = label.split('\n')
    for i, line in enumerate(lines):
        svg += f'<text x="{mid_x}" y="{ypos-10-len(lines)*7+i*13}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{line}</text>\n'

# Note box
note_y = y + 480
svg += f'''
<rect x="900" y="{note_y}" width="400" height="50" rx="4" fill="#fffbeb" stroke="#fbbf24" stroke-width="2"/>
<text x="1100" y="{note_y+25}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">⏱️ 檔案系統 I/O 暫停中...</text>
'''

# Unfreeze phase
y2 = note_y + 80
unfreeze = [
    (120, 320, y2, "執行 unfreeze 命令", False),
    (320, 520, y2+60, "gRPC 連接", False),
    (520, 720, y2+120, "發送 QMP 命令", False),
    (720, 920, y2+180, "guest-fsfreeze-thaw", False),
    (920, 1120, y2+240, "fsfreeze --unfreeze / VSS thaw", False),
    (1120, 120, y2+280, "I/O 已恢復", True),
]

for x1, x2, ypos, label, is_return in unfreeze:
    if is_return:
        svg += f'<line x1="{x2}" y1="{ypos}" x2="{x1}" y2="{ypos}" stroke="{ARROW_RETURN}" stroke-width="2" stroke-dasharray="5,5" marker-start="url(#arrow-return)"/>\n'
    else:
        svg += f'<line x1="{x1}" y1="{ypos}" x2="{x2}" y2="{ypos}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
    
    mid_x = (x1 + x2) / 2
    svg += f'<text x="{mid_x}" y="{ypos-8}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>\n'

svg += '</svg>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f'Written: {OUT}')
