#!/usr/bin/env python3
"""CDI ImportReconciler flowchart - Notion Clean Style"""
import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
SUCCESS = "#d1fae5"
SUCCESS_S = "#6ee7b7"

OUT = "docs-site/public/diagrams/containerized-data-importer"
os.makedirs(OUT, exist_ok=True)

W, H = 900, 900

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

def diamond(x, y, w, h, text, fs=10):
    cx, cy = x + w/2, y + h/2
    pts = f"{cx},{y} {x+w},{cy} {cx},{y+h} {x},{cy}"
    r = (f'  <polygon points="{pts}" fill="#fef3c7" stroke="#fcd34d" stroke-width="1.5"/>\n'
         f'  <text x="{cx:.0f}" y="{cy+4:.0f}" font-family="{FONT}" font-size="{fs}" '
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

CX = 450
BW, BH = 320, 42

# Nodes top to bottom
nodes = [
    (CX-BW//2, 40,  BW, BH, "Reconcile(ctx, req)", "#dbeafe", "#93c5fd"),
    (CX-BW//2, 120, BW, BH, "reconcile(ctx, req, r)", BOX_FILL, BOX_STROKE),
    (CX-BW//2, 200, BW, BH, "sync(log, req)", BOX_FILL, BOX_STROKE),
    (CX-BW//2, 280, BW, BH, "syncImport(log, req)", BOX_FILL, BOX_STROKE),
    (CX-BW//2, 360, BW, BH, "syncCommon(log, req, cleanup, nil)", BOX_FILL, BOX_STROKE),
]
for x,y,w,h,t,f,s in nodes:
    svg += box(x,y,w,h,t,f,s)

# Arrows between linear nodes
ys = [40, 120, 200, 280, 360]
for i in range(len(ys)-1):
    svg += arr(CX, ys[i]+BH, CX, ys[i+1])

# Diamond: error or result?
svg += diamond(CX-70, 440, 140, 55, "error/result?")
svg += arr(CX, 360+BH, CX, 440)

# Return (error path)
svg += box(680, 450, 150, 42, "返回", "#fee2e2", "#fca5a5")
svg += arr(CX+70, 467, 680, 471, "是")

# Diamond: usePopulator?
svg += diamond(CX-70, 540, 140, 55, "usePopulator?")
svg += arr(CX, 495, CX, 540, "否")

# Yes path: reconcileVolumeImportSourceCR
svg += box(680, 545, 225, 42, "reconcileVolumeImportSourceCR()", BOX_FILL)
svg += box(680, 610, 225, 42, "pvcModifier =\nupdatePVCForPopulation", BOX_FILL)
svg += arr(CX+70, 567, 680, 566, "是")
svg += arr(792, 587, 792, 610)

# No path: updateAnnotations
svg += box(80, 545, 225, 42, "pvcModifier =\nupdateAnnotations", BOX_FILL)
svg += arr(CX-70, 567, 305, 566, "否")

# handlePvcCreation
svg += box(CX-BW//2, 680, BW, BH, "handlePvcCreation(log, syncState, pvcModifier)", BOX_FILL)
svg += arr(192, 587, 192, 700)
svg += arr(192, 700, CX-BW//2, 700)
svg += arr(792, 652, 792, 700)
svg += arr(792, 700, CX+BW//2, 700)
svg += arr(CX, 595, CX, 680, "")

# Diamond: pvc != nil and not populator?
svg += diamond(CX-80, 760, 160, 55, "pvc!=nil\n且非populator?", 9)
svg += arr(CX, 680+BH, CX, 760)

# Yes: setVddkAnnotations -> MaybeSetPvc
svg += box(680, 760, 220, 42, "setVddkAnnotations()", BOX_FILL)
svg += box(680, 822, 220, 42, "MaybeSetPvcMultiStage\nAnnotation()", BOX_FILL, BOX_STROKE, 10)
svg += arr(CX+80, 787, 680, 781, "是")
svg += arr(790, 802, 790, 822)

# No: syncUpdate
svg += box(80, 850, 225, 42, "syncUpdate(log, syncState)", SUCCESS, SUCCESS_S)
svg += arr(CX-80, 787, 192, 852, "否")
svg += arr(790, 864, 680, 871)
svg += arr(305, 871, 305, 871)
svg += arr(790, 864, 450, 870)
# arrows to syncUpdate
svg += arr(450, 870, 305, 871)
svg += arr(305, 871, 305, 850+BH/2)

svg += (f'  <text x="{W/2:.0f}" y="{H-14}" font-family="{FONT}" font-size="12" '
        f'font-weight="600" text-anchor="middle" fill="{TEXT_SECONDARY}">ImportReconciler 調和流程</text>\n')

svg += '</svg>'

out = f"{OUT}/cdi-controllers-api-2.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
