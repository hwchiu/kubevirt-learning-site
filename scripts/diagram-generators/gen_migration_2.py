#!/usr/bin/env python3
"""Migration internals diagram 2: Migration state machine"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
SUCCESS_FILL = "#d1fae5"
SUCCESS_STROKE = "#10b981"
FAIL_FILL = "#fee2e2"
FAIL_STROKE = "#ef4444"

W, H = 900, 680

def arrow_marker():
    return f'''<defs>
  <marker id="arr" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}" />
  </marker>
</defs>'''

def state_box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>'''

def circle(x, y, r, fill=ARROW):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'

def arr(x1, y1, x2, y2, label="", color=ARROW, lx=None, ly=None):
    dx = x2 - x1; dy = y2 - y1
    length = (dx*dx + dy*dy) ** 0.5
    if length == 0:
        return ""
    ux = dx/length; uy = dy/length
    mx = (x1+x2)//2; my = (y1+y2)//2
    line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arr)"/>'
    if label:
        lx = lx or mx+5
        ly = ly or my-6
        lbl = f'<text x="{lx}" y="{ly}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{label}</text>'
        return line + '\n' + lbl
    return line

svg_parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    arrow_marker(),
    f'<text x="{W//2}" y="36" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="{TEXT_PRIMARY}">Migration Phase State Machine</text>',
]

# Layout: vertical chain center=450
cx = 450
bw, bh = 220, 44
# States top to bottom
states = [
    (cx - bw//2, 60,  "MigrationPhaseUnset"),
    (cx - bw//2, 140, "MigrationPending"),
    (cx - bw//2, 220, "MigrationScheduling"),
    (cx - bw//2, 300, "MigrationScheduled"),
    (cx - bw//2, 380, "MigrationPreparingTarget"),
    (cx - bw//2, 460, "MigrationTargetReady"),
    (cx - bw//2, 540, "MigrationRunning"),
]
for sx, sy, label in states:
    svg_parts.append(state_box(sx, sy, bw, bh, label))

# Success / Failed terminal states
svg_parts.append(state_box(680, 540, 160, 44, "Succeeded", SUCCESS_FILL, SUCCESS_STROKE))
svg_parts.append(state_box(680, 340, 160, 44, "Failed", FAIL_FILL, FAIL_STROKE))

# Start circle
svg_parts.append(circle(cx, 50, 8))

# Arrows: start → Unset
svg_parts.append(arr(cx, 58, cx, 60))

# Main chain
for i in range(len(states)-1):
    sx1, sy1, _ = states[i]
    sx2, sy2, _ = states[i+1]
    svg_parts.append(arr(cx, sy1+bh, cx, sy2))

# Transitions to Failed (right side)
fail_x = 680
svg_parts.append(arr(cx+bw//2, 60+bh//2, fail_x, 362, "VMI 不可遷移", lx=540, ly=185))
svg_parts.append(arr(cx+bw//2, 220+bh//2, fail_x, 362, "排程失敗", lx=590, ly=248))
svg_parts.append(arr(cx+bw//2, 300+bh//2, fail_x, 362, "超時/錯誤", lx=590, ly=325))
svg_parts.append(arr(cx+bw//2, 380+bh//2, fail_x, 362, "準備失敗", lx=590, ly=403))
svg_parts.append(arr(cx+bw//2, 460+bh//2, fail_x, 362, "啟動失敗", lx=590, ly=455))
svg_parts.append(arr(cx+bw//2, 540+bh//2, fail_x, 384, "逾時/錯誤", lx=590, ly=542))

# Running → Succeeded
svg_parts.append(arr(cx+bw//2, 562, fail_x, 562, "傳輸完成", lx=570, ly=555))

# Failed / Succeeded → terminal
end_y = 640
svg_parts.append(f'<circle cx="{760}" cy="{end_y-10}" r="10" fill="{TEXT_PRIMARY}"/>')
svg_parts.append(f'<circle cx="{760}" cy="{end_y-10}" r="6" fill="{BG}"/>')
svg_parts.append(arr(760, 384, 760, end_y-20, ""))
svg_parts.append(arr(760, 584, 760, end_y-20, ""))

svg_parts.append('</svg>')

out = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-2.svg'
with open(out, 'w') as f:
    f.write('\n'.join(svg_parts))
print(f"Written: {out}")
