#!/usr/bin/env python3
# overview.md - Block 5: IOThread strategies (shared vs auto)

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 680, 240

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=12, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'

def line(x1,y1,x2,y2,color=ARROW):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arr)"/>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# -- shared strategy --
svg += box(20, 10, 280, 200, CONTAINER_FILL, CONTAINER_STROKE, 10)
svg += text(160, 30, "shared 策略", 13, TEXT_SECONDARY, True)
svg += box(60, 55, 100, 36, "#dbeafe", "#93c5fd")
svg += text(110, 73, "IOThread 1", 12, "#1d4ed8", True)
for i, dy in enumerate([110, 150, 190]):
    svg += box(230, dy-18, 60, 32, BOX_FILL, BOX_STROKE)
    svg += text(260, dy, f"Disk {i+1}", 11)
    svg += line(160, 73, 230, dy)

# -- auto strategy --
svg += box(380, 10, 280, 200, CONTAINER_FILL, CONTAINER_STROKE, 10)
svg += text(520, 30, "auto 策略", 13, TEXT_SECONDARY, True)
colors = ["#dbeafe","#dcfce7","#fef9c3"]
bcolors = ["#93c5fd","#86efac","#fde047"]
tcolors = ["#1d4ed8","#166534","#713f12"]
for i, (cf, cs, tc, dy) in enumerate(zip(colors, bcolors, tcolors, [80, 120, 160])):
    svg += box(400, dy-18, 100, 32, cf, cs)
    svg += text(450, dy, f"IOThread {i+1}", 12, tc, True)
    svg += box(540, dy-14, 60, 28, BOX_FILL, BOX_STROKE)
    svg += text(570, dy, f"Disk {i+1}", 11)
    svg += line(500, dy, 540, dy)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-5.svg", "w") as f:
    f.write(svg)
print("Done")
