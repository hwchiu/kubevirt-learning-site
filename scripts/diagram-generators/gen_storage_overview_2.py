#!/usr/bin/env python3
# overview.md - Block 2: Volume -> Disk Type mapping (LR)

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 680, 220

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=13, fill=TEXT_PRIMARY, bold=False):
    weight = "600" if bold else "400"
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="middle" dominant-baseline="middle">{txt}</text>'

def arrow(x1, y1, x2, y2, label=""):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2 - 8
        s += f'<text x="{mx}" y="{my}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return s

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# VOL box
svg += box(30, 90, 130, 44, CONTAINER_FILL, CONTAINER_STROKE)
svg += text(95, 112, "Volume（資料來源）", 12, TEXT_PRIMARY, True)

# Disk type box
svg += box(230, 90, 130, 44, CONTAINER_FILL, CONTAINER_STROKE)
svg += text(295, 112, "Disk 型別", 13, TEXT_PRIMARY, True)

# Arrow with label
svg += arrow(160, 112, 230, 112, "掛載為")

# Three disk types
disk_types = [("disk（一般磁碟）", 450, 60), ("lun（SCSI LUN）", 450, 112), ("cdrom（光碟機）", 450, 164)]
for label, lx, ly in disk_types:
    svg += box(lx-75, ly-18, 160, 36, BOX_FILL, BOX_STROKE)
    svg += text(lx+5, ly, label, 12, TEXT_SECONDARY)
    svg += arrow(360, 112, lx-75, ly)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-2.svg", "w") as f:
    f.write(svg)
print("Done")
