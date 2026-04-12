#!/usr/bin/env python3
# overview.md - Block 3: Bus performance/compatibility ranking

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 760, 240

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=13, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'

def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Container: 效能排序
svg += box(20, 20, 340, 90, CONTAINER_FILL, CONTAINER_STROKE, 10)
svg += text(190, 40, "效能排序（高 → 低）", 12, TEXT_SECONDARY, True)

perf = ["virtio", "scsi", "sas", "sata", "usb"]
colors = ["#3b82f6","#6366f1","#8b5cf6","#a78bfa","#c4b5fd"]
px = 40
for i, (b, c) in enumerate(zip(perf, colors)):
    svg += box(px, 60, 52, 32, c, c, 6)
    svg += text(px+26, 76, b, 11, "#fff", True)
    if i < len(perf)-1:
        svg += arrow(px+52, 76, px+62, 76)
    px += 62

# Container: 相容性排序
svg += box(400, 20, 340, 90, CONTAINER_FILL, CONTAINER_STROKE, 10)
svg += text(570, 40, "相容性排序（高 → 低）", 12, TEXT_SECONDARY, True)

compat = ["sata", "scsi", "sas", "virtio", "usb"]
colors2 = ["#10b981","#34d399","#6ee7b7","#a7f3d0","#d1fae5"]
px = 420
for i, (b, c) in enumerate(zip(compat, colors2)):
    svg += box(px, 60, 52, 32, c, c, 6)
    svg += text(px+26, 76, b, 11, "#065f46", True)
    if i < len(compat)-1:
        svg += arrow(px+52, 76, px+62, 76)
    px += 62

# Legend
svg += text(380, 150, "效能最高：virtio（需要驅動）  ·  相容性最高：sata（無需額外驅動）", 12, TEXT_SECONDARY)
svg += '</svg>'

with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-3.svg", "w") as f:
    f.write(svg)
print("Done")
