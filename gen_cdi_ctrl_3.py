#!/usr/bin/env python3
"""CDI DataVolume Mutating Webhook flow - Notion Clean Style"""
import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"

OUT = "docs-site/public/diagrams/containerized-data-importer"
os.makedirs(OUT, exist_ok=True)

W, H = 820, 720

def box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, fs=11):
    lines = text.split('\n')
    r = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
         f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n')
    lh = 16
    sy = y + (h - len(lines)*lh)/2 + lh - 2
    for i, ln in enumerate(lines):
        fw = "600" if i == 0 else "400"
        r += (f'  <text x="{x+w/2:.0f}" y="{sy+i*lh:.0f}" font-family="{FONT}" '
              f'font-size="{fs}" font-weight="{fw}" text-anchor="middle" fill="{TEXT_PRIMARY}">{ln}</text>\n')
    return r

def diamond(cx, cy, w, h, text, fs=10):
    pts = f"{cx},{cy-h//2} {cx+w//2},{cy} {cx},{cy+h//2} {cx-w//2},{cy}"
    r = (f'  <polygon points="{pts}" fill="#fef3c7" stroke="#fcd34d" stroke-width="1.5"/>\n'
         f'  <text x="{cx}" y="{cy+4}" font-family="{FONT}" font-size="{fs}" '
         f'font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">{text}</text>\n')
    return r

def arr(x1, y1, x2, y2, lbl="", color=ARROW):
    r = (f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
         f'stroke="{color}" stroke-width="1.5" marker-end="url(#arr)"/>\n')
    if lbl:
        mx, my = (x1+x2)/2, (y1+y2)/2
        lw = len(lbl)*5.5+14
        r += (f'  <rect x="{mx-lw/2:.1f}" y="{my-13:.1f}" width="{lw:.1f}" height="13" '
              f'rx="3" fill="{BG}" opacity="0.9"/>\n'
              f'  <text x="{mx:.1f}" y="{my-2:.1f}" font-family="{FONT}" font-size="9.5" '
              f'text-anchor="middle" fill="{TEXT_SECONDARY}">{lbl}</text>\n')
    return r

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
'''

CX = 410
BW, BH = 340, 42

svg += box(CX-BW//2, 30, BW, BH, "收到 DataVolume Admission Request", "#dbeafe", "#93c5fd")
svg += arr(CX, 30+BH, CX, 100)
svg += diamond(CX, 120, 160, 55, "Delete 操作?")

# Yes: skip
svg += box(620, 100, 120, 42, "跳過，允許", "#d1fae5", "#6ee7b7")
svg += arr(CX+80, 120, 620, 121, "是")

# No: SubjectAccessReview
svg += box(CX-BW//2, 175, BW, BH, "SubjectAccessReview 授權檢查", BOX_FILL)
svg += arr(CX, 147, CX, 175, "否")

svg += arr(CX, 175+BH, CX, 260)
svg += diamond(CX, 280, 160, 55, "Create 操作?")

# No: Allow
svg += box(620, 260, 120, 42, "允許", "#d1fae5", "#6ee7b7")
svg += arr(CX+80, 280, 620, 281, "否")

# Yes
svg += arr(CX, 307, CX, 375)
svg += diamond(CX, 395, 220, 55, "來源是 PVC/Snapshot clone?", 9)

# No: Allow
svg += arr(CX+110, 395, 620, 330)
svg += arr(620, 330, 620, 281)

# Yes: generate token
svg += box(CX-BW//2, 460, BW, BH, "產生 Clone Token", "#fef9c3", "#fde68a")
svg += arr(CX, 422, CX, 460, "是")

svg += box(CX-BW//2, 535, BW, BH, "設定 annotation: AnnCloneToken", BOX_FILL)
svg += arr(CX, 460+BH, CX, 535)

# Allow final
svg += box(CX-BW//2, 615, BW, BH, "允許", "#d1fae5", "#6ee7b7")
svg += arr(CX, 535+BH, CX, 615)
# connect from right allow to final
svg += f'  <line x1="620" y1="281" x2="680" y2="281" stroke="{ARROW}" stroke-width="1.5"/>\n'
svg += f'  <line x1="680" y1="281" x2="680" y2="634" stroke="{ARROW}" stroke-width="1.5"/>\n'
svg += arr(680, 634, CX+BW//2, 634)

svg += (f'  <text x="{W/2:.0f}" y="{H-12}" font-family="{FONT}" font-size="12" '
        f'font-weight="600" text-anchor="middle" fill="{TEXT_SECONDARY}">DataVolume Mutating Webhook 流程</text>\n')

svg += '</svg>'

out = f"{OUT}/cdi-controllers-api-3.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
