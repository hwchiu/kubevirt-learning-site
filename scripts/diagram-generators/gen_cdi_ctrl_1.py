#!/usr/bin/env python3
"""CDI cdi-controller overview - Notion Clean Style"""
import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"

OUT = "docs-site/public/diagrams/containerized-data-importer"
os.makedirs(OUT, exist_ok=True)

W, H = 1400, 680

def cont(x, y, w, h, title):
    return (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
            f'fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>\n'
            f'  <text x="{x+12}" y="{y+19}" font-family="{FONT}" font-size="11" '
            f'font-weight="700" fill="{TEXT_SECONDARY}">{title}</text>\n')

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Outer container: cdi-controller 程序
svg += cont(20, 20, W-40, H-60, "cdi-controller 程序")

# DataVolume Controllers
svg += cont(50, 55, 480, 230, "DataVolume Controllers")
items_dv = ["ImportReconciler","UploadController","PvcCloneController","SnapshotCloneController","PopulatorController"]
for i, name in enumerate(items_dv):
    row, col = divmod(i, 2)
    bx = 65 + col*230
    by = 82 + row*65
    svg += box(bx, by, 210, 42, name, "#dbeafe", "#93c5fd", 11)
# 5th item centered
svg += box(65+115, 212, 210, 42, "PopulatorController", "#dbeafe", "#93c5fd", 11)

# Primary Controllers
svg += cont(550, 55, 420, 230, "Primary Controllers")
items_p = ["ImportController\n(Legacy)","CloneController\n(Legacy)","UploadController\n(Legacy)","ConfigController","StorageProfileController","DataImportCronController","DataSourceController"]
positions = [(565,82),(565,130),(565,178),(785,82),(785,130),(785,178),(680,226)]
for name, (bx, by) in zip(items_p, positions):
    svg += box(bx, by, 185, 42, name, BOX_FILL, BOX_STROKE, 10)

# Populator Controllers
svg += cont(50, 310, 480, 160, "Populator Controllers")
items_pop = ["ImportPopulator","UploadPopulator","ClonePopulator","ForkliftPopulator"]
for i, name in enumerate(items_pop):
    bx = 65 + (i%2)*230
    by = 335 + (i//2)*65
    svg += box(bx, by, 210, 42, name, "#d1fae5", "#6ee7b7", 11)

# Transfer
svg += cont(550, 310, 420, 160, "Transfer")
svg += box(650, 360, 220, 50, "ObjectTransferController", BOX_FILL, BOX_STROKE, 11)

svg += (f'  <text x="{W/2:.0f}" y="{H-20}" font-family="{FONT}" font-size="12" '
        f'font-weight="600" text-anchor="middle" fill="{TEXT_SECONDARY}">cdi-controller 控制器架構概覽</text>\n')

svg += '</svg>'

out = f"{OUT}/cdi-controllers-api-1.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
