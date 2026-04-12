#!/usr/bin/env python3
# overview.md - Block 1: KubeVirt Storage Types tree

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 900, 520

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=13, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    lines = txt.split('\n')
    if len(lines) == 1:
        return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'
    out = f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
    dy = size * 1.4
    offset = -(len(lines)-1) * dy / 2
    for i, l in enumerate(lines):
        out += f'<tspan x="{x}" dy="{offset if i==0 else dy}">{l}</tspan>'
    out += '</text>'
    return out

def arrow(x1, y1, x2, y2, color=ARROW):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arr)"/>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Root node
svg += box(350, 20, 200, 44, CONTAINER_FILL, CONTAINER_STROKE)
svg += text(450, 42, "KubeVirt 儲存類型", 14, TEXT_PRIMARY, True)

# Three category nodes
cats = [
    (120, 140, "#dcfce7", "#86efac", "持久儲存\n（Persistent）"),
    (370, 140, "#fef9c3", "#fde047", "暫態儲存\n（Ephemeral）"),
    (650, 140, "#dbeafe", "#93c5fd", "設定資料\n（Configuration）"),
]
for cx, cy, cf, cs, label in cats:
    svg += box(cx, cy, 160, 50, cf, cs)
    svg += text(cx+80, cy+25, label, 13, TEXT_PRIMARY, True)
    svg += arrow(450, 64, cx+80, cy)

# Persistent children
per_children = [("PersistentVolumeClaim\n（一般 K8s PVC）", 60, 240), ("DataVolume\n（CDI 管理）", 200, 240)]
for label, lx, ly in per_children:
    svg += box(lx, ly, 155, 46, BOX_FILL, BOX_STROKE)
    svg += text(lx+77, ly+23, label, 11, TEXT_SECONDARY)
    svg += arrow(200, 190, lx+77, ly)

# Ephemeral children
eph_children = [
    ("ContainerDisk\n（容器映像）", 330, 240),
    ("EmptyDisk\n（空白磁碟）", 450, 240),
    ("Ephemeral PVC\n（PVC 的暫態包裝）", 330, 310),
]
for label, lx, ly in eph_children:
    svg += box(lx, ly, 160, 46, BOX_FILL, BOX_STROKE)
    svg += text(lx+80, ly+23, label, 11, TEXT_SECONDARY)
    svg += arrow(450, 190, lx+80, ly)

# Config children
cfg_children = [
    ("CloudInitNoCloud", 590, 230),
    ("CloudInitConfigDrive", 590, 280),
    ("ConfigMap / Secret", 590, 330),
    ("ServiceAccount", 590, 380),
    ("DownwardAPI / DownwardMetrics", 590, 430),
]
for label, lx, ly in cfg_children:
    svg += box(lx, ly, 220, 36, BOX_FILL, BOX_STROKE)
    svg += text(lx+110, ly+18, label, 11, TEXT_SECONDARY)
    svg += arrow(730, 190, lx, ly+18)

svg += '</svg>'

with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-1.svg", "w") as f:
    f.write(svg)
print("Done: kubevirt-storage-overview-1.svg")
