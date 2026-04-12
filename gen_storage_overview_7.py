#!/usr/bin/env python3
# overview.md - Block 7: DataVolume lifecycle state machine

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 800, 240

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=12, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'

def arrow(x1, y1, x2, y2, label="", color=ARROW):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arr{color.replace("#","")})"/>'
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2 - 9
        s += text(mx, my, label, 10, TEXT_SECONDARY)
    return s

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr3b82f6" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
  <marker id="arref4444" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#ef4444"/>
  </marker>
  <marker id="arr16a34a" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#16a34a"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

states = [
    (60, 110, "Pending", BOX_FILL, BOX_STROKE),
    (220, 110, "ImportScheduled", CONTAINER_FILL, CONTAINER_STROKE),
    (420, 110, "ImportInProgress", "#fef3c7", "#fcd34d"),
    (620, 60, "Succeeded", "#dcfce7", "#86efac"),
    (620, 160, "Failed", "#fee2e2", "#fca5a5"),
]

for x, y, label, cf, cs in states:
    svg += box(x-55, y-18, 130, 36, cf, cs)
    svg += text(x+10, y, label, 12, TEXT_PRIMARY, True)

# Arrows
svg += arrow(115, 110, 165, 110, "建立 DataVolume")
svg += arrow(350, 110, 365, 110, "Importer Pod 執行")
svg += arrow(535, 100, 565, 75, "匯入成功", "#16a34a")
svg += arrow(535, 120, 565, 155, "匯入失敗", "#ef4444")

# Start dot
svg += '<circle cx="20" cy="110" r="8" fill="#111827"/>'
svg += arrow(28, 110, 5, 110)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-7.svg", "w") as f:
    f.write(svg)
print("Done")
