#!/usr/bin/env python3
"""Migration internals diagram 5: Post-copy sequence diagram"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
NOTE_FILL = "#fef9c3"
NOTE_STROKE = "#fde68a"

W, H = 700, 500

S_X = 150
T_X = 550

def lifeline(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>'

def participant(x, label):
    bw, bh = 130, 44
    return f'''<rect x="{x-bw//2}" y="30" width="{bw}" height="{bh}" rx="6" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>
<text x="{x}" y="57" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>'''

def arrow_lr(x1, y, x2, label=""):
    line = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
    if label:
        mx = (x1+x2)//2
        lbl = f'<text x="{mx}" y="{y-6}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">{label}</text>'
        return line+'\n'+lbl
    return line

def note(y, label, span=True):
    return f'''<rect x="80" y="{y}" width="{W-160}" height="26" rx="4" fill="{NOTE_FILL}" stroke="{NOTE_STROKE}" stroke-width="1"/>
<text x="{W//2}" y="{y+17}" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="600" fill="#92400e">{label}</text>'''

def side_note(x, y, label):
    bw = 160
    return f'''<rect x="{x-bw//2}" y="{y}" width="{bw}" height="30" rx="6" fill="{BOX_FILL}" stroke="{ARROW}" stroke-width="1.5"/>
<text x="{x}" y="{y+19}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">{label}</text>'''

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    f'<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto"><polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/></marker></defs>',
    f'<text x="{W//2}" y="20" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">Post-copy Migration</text>',
    participant(S_X, "Source"),
    participant(T_X, "Target"),
    lifeline(S_X, 74, 460),
    lifeline(T_X, 74, 460),
]

# Step 1: transfer min pages
svg.append(note(100, "第 1 輪：傳送最少量必要頁面"))
svg.append(arrow_lr(S_X, 140, T_X, "傳送 VM 狀態 + 部分記憶體"))

# Target starts running
svg.append(side_note(T_X, 160, "VM 在目標端開始執行"))

# Page faults
svg.append(note(210, "按需請求頁面（Page Fault）"))
svg.append(arrow_lr(T_X, 248, S_X, "Page Fault! 需要頁面 0x1234"))
svg.append(arrow_lr(S_X, 278, T_X, "傳送頁面 0x1234"))

svg.append(arrow_lr(T_X, 318, S_X, "Page Fault! 需要頁面 0x5678"))
svg.append(arrow_lr(S_X, 348, T_X, "傳送頁面 0x5678"))

svg.append(note(380, "持續按需傳送，直到所有頁面都到達目標端"))

svg.append('</svg>')
out = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-5.svg'
with open(out, 'w') as f:
    f.write('\n'.join(svg))
print(f"Written: {out}")
