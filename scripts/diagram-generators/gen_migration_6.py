#!/usr/bin/env python3
"""Migration internals diagram 6: Abort/cleanup flow"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
DIAMOND_FILL = "#ede9fe"
DIAMOND_STROKE = "#7c3aed"
SUCCESS_FILL = "#d1fae5"
SUCCESS_STROKE = "#10b981"
FAIL_FILL = "#fee2e2"
FAIL_STROKE = "#ef4444"

W, H = 860, 540

def marker():
    return f'<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto"><polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/></marker></defs>'

def box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE, fs=13):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="{fs}" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>'''

def diamond(x, y, w, h, label):
    hw, hh = w//2, h//2
    pts = f"{x},{y-hh} {x+hw},{y} {x},{y+hh} {x-hw},{y}"
    return f'''<polygon points="{pts}" fill="{DIAMOND_FILL}" stroke="{DIAMOND_STROKE}" stroke-width="1.5"/>
<text x="{x}" y="{y+5}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="600" fill="#4c1d95">{label}</text>'''

def arr(x1, y1, x2, y2, label="", lx=None, ly=None):
    line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
    if label:
        lx = lx or (x1+x2)//2+4
        ly = ly or (y1+y2)//2-4
        lbl = f'<text x="{lx}" y="{ly}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{label}</text>'
        return line+'\n'+lbl
    return line

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    marker(),
    f'<text x="{W//2}" y="30" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">Migration Abort &amp; Cleanup Flow</text>',
]

# Top: Abort request
svg.append(box(330, 50, 200, 44, "Abort 請求"))

# Diamond: migration phase?
svg.append(diamond(430, 150, 200, 60, "遷移階段?"))
svg.append(arr(430, 94, 430, 120))  # box → diamond

# Branch: Pre-Running (left)
svg.append(box(80, 230, 160, 44, "刪除 Target Pod", BOX_FILL, BOX_STROKE, 12))
svg.append(arr(350, 150, 240, 230, "Pre-Running", lx=240, ly=188))

# Branch: Running (right → down)
svg.append(box(600, 230, 160, 44, "dom.AbortJob", BOX_FILL, BOX_STROKE, 12))
svg.append(arr(510, 150, 640, 230, "Running", lx=560, ly=188))

# Diamond: Abort success?
svg.append(diamond(680, 345, 180, 60, "Abort 成功?"))
svg.append(arr(680, 274, 680, 315))

# Branch: 是 (success)
svg.append(box(550, 420, 160, 44, "AbortStatus = Succeeded", SUCCESS_FILL, SUCCESS_STROKE, 11))
svg.append(arr(600, 345, 610, 420, "是", lx=584, ly=381))

# Branch: 否 (fail)
svg.append(box(740, 420, 160, 44, "AbortStatus = Failed", FAIL_FILL, FAIL_STROKE, 11))
svg.append(arr(760, 345, 820, 420, "否", lx=786, ly=381))

# Cleanup Target Pod
svg.append(box(550, 490, 160, 40, "清理 Target Pod", BOX_FILL, BOX_STROKE, 11))
svg.append(arr(630, 464, 630, 490))

# Retry or fail
svg.append(box(740, 490, 160, 40, "重試或標記失敗", FAIL_FILL, FAIL_STROKE, 11))
svg.append(arr(820, 464, 820, 490))

# VMI continues
svg.append(box(100, 340, 200, 44, "VMI 繼續在源端運行", SUCCESS_FILL, SUCCESS_STROKE, 12))
svg.append(arr(160, 274, 200, 340))  # from delete target pod → VMI continues
# Also from cleanup
svg.append(arr(630, 530, 200, 362, "", lx=350, ly=545))

svg.append('</svg>')
out = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-6.svg'
with open(out, 'w') as f:
    f.write('\n'.join(svg))
print(f"Written: {out}")
