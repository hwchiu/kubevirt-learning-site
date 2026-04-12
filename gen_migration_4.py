#!/usr/bin/env python3
"""Migration internals diagram 4: Pre-copy sequence diagram"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
NOTE_FILL = "#fef9c3"
NOTE_STROKE = "#fde68a"

W, H = 700, 480

# Participant positions
S_X = 150
T_X = 550
TOP_Y = 70
BOT_Y = 450

def lifeline(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>'

def participant(x, label, sub=None):
    bw, bh = 130, 44
    lines = [
        f'<rect x="{x-bw//2}" y="30" width="{bw}" height="{bh}" rx="6" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>',
    ]
    if sub:
        lines.append(f'<text x="{x}" y="47" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
        lines.append(f'<text x="{x}" y="63" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{sub}</text>')
    else:
        lines.append(f'<text x="{x}" y="57" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(lines)

def msg_arrow(x1, y, x2, label=""):
    line = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
    mx = (x1+x2)//2
    if label:
        lbl = f'<text x="{mx}" y="{y-6}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">{label}</text>'
        return line + '\n' + lbl
    return line

def note(y, label):
    return f'''<rect x="80" y="{y}" width="{W-160}" height="26" rx="4" fill="{NOTE_FILL}" stroke="{NOTE_STROKE}" stroke-width="1"/>
<text x="{W//2}" y="{y+17}" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="600" fill="#92400e">{label}</text>'''

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    f'<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto"><polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/></marker></defs>',
    f'<text x="{W//2}" y="20" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">Pre-copy Migration</text>',
    participant(S_X, "Source"),
    participant(T_X, "Target"),
    lifeline(S_X, 74, BOT_Y),
    lifeline(T_X, 74, BOT_Y),
]

# Round 1
svg.append(note(100, "第 1 輪：複製所有記憶體頁面"))
svg.append(msg_arrow(S_X, 140, T_X, "傳送完整記憶體（例如 8 GiB）"))

# Round 2
svg.append(note(175, "第 2 輪：複製第 1 輪期間被修改的頁面"))
svg.append(msg_arrow(S_X, 215, T_X, "傳送 dirty pages（例如 2 GiB）"))

# Round 3
svg.append(note(250, "第 3 輪：dirty pages 更少"))
svg.append(msg_arrow(S_X, 290, T_X, "傳送 dirty pages（例如 200 MiB）"))

# Round N
svg.append(note(325, "第 N 輪：dirty pages 足夠少"))
svg.append(msg_arrow(S_X, 365, T_X, "最後一批 + 切換執行"))

# Target note
svg.append(f'<rect x="{T_X-80}" y="383" width="160" height="36" rx="6" fill="{BOX_FILL}" stroke="{ARROW}" stroke-width="1.5"/>')
svg.append(f'<text x="{T_X}" y="405" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">VM 在目標端恢復運行</text>')

svg.append('</svg>')
out = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-4.svg'
with open(out, 'w') as f:
    f.write('\n'.join(svg))
print(f"Written: {out}")
