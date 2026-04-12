#!/usr/bin/env python3
# overview.md - Block 6: CDI sources -> DataVolume

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 760, 300

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=12, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    lines = txt.split('\n')
    if len(lines) == 1:
        return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'
    out = f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
    for i, l in enumerate(lines):
        out += f'<tspan x="{x}" dy="{0 if i==0 else size*1.4}">{l}</tspan>'
    out += '</text>'
    return out

def line(x1,y1,x2,y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Source group label
svg += text(110, 20, "資料來源", 12, TEXT_SECONDARY, True)
sources = ["HTTP/HTTPS URL", "S3 物件儲存", "容器映像倉庫", "現有 PVC", "空白磁碟"]
src_y = [50, 100, 150, 200, 250]
for s, sy in zip(sources, src_y):
    svg += box(20, sy-16, 170, 32, BOX_FILL, BOX_STROKE)
    svg += text(105, sy, s, 12)

# CDI box
svg += box(280, 120, 160, 60, "#dbeafe", "#93c5fd", 10)
svg += text(360, 145, "CDI", 14, "#1d4ed8", True)
svg += text(360, 163, "Containerized Data Importer", 10, "#3b82f6")

# DataVolume box
svg += box(550, 120, 170, 60, "#dcfce7", "#86efac", 10)
svg += text(635, 150, "DataVolume（新 PVC）", 12, "#166534", True)

# Arrows sources -> CDI
for sy in src_y:
    svg += line(190, sy, 280, 150)

# Arrow CDI -> DV
svg += line(440, 150, 550, 150)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-6.svg", "w") as f:
    f.write(svg)
print("Done")
