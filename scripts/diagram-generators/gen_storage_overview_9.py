#!/usr/bin/env python3
# overview.md - Block 9: Storage architecture decision flowchart

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 860, 540

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def diamond(x, y, w, h, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE):
    hw, hh = w//2, h//2
    pts = f"{x},{y-hh} {x+hw},{y} {x},{y+hh} {x-hw},{y}"
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=12, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    lines = txt.split('\n')
    if len(lines) == 1:
        return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'
    span_h = size * 1.4
    offset = -(len(lines)-1) * span_h / 2
    out = f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
    for i, l in enumerate(lines):
        out += f'<tspan x="{x}" dy="{offset if i==0 else span_h}">{l}</tspan>'
    return out + '</text>'

def arrow(x1, y1, x2, y2, label="", color=ARROW):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arr)"/>'
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2
        s += f'<text x="{mx+4}" y="{my}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return s

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Start
svg += box(340, 10, 160, 36, "#1e40af", "#1e40af")
svg += text(420, 28, "需要儲存？", 13, "#fff", True)

# Decision: 持久化?
svg += diamond(420, 110, 160, 50)
svg += text(420, 110, "需要持久化？", 12, TEXT_PRIMARY, True)
svg += arrow(420, 46, 420, 85)

# Yes branch - 匯入映像?
svg += diamond(420, 210, 160, 50)
svg += text(420, 210, "需要匯入映像？", 12, TEXT_PRIMARY, True)
svg += arrow(420, 135, 420, 185, "是")

# Yes -> DataVolume
svg += box(310, 280, 180, 40, "#dcfce7", "#86efac")
svg += text(400, 300, "使用 DataVolume\n（CDI 自動匯入）", 12, "#166534", True)
svg += arrow(420, 235, 400, 280, "是")

# No -> PVC
svg += box(560, 280, 160, 40, "#dcfce7", "#86efac")
svg += text(640, 300, "使用 PVC\n（直接使用）", 12, "#166534", True)
svg += arrow(500, 210, 560, 300, "否")

# No branch - 用途?
svg += diamond(640, 110, 160, 50)
svg += text(640, 110, "用途？", 12, TEXT_PRIMARY, True)
svg += arrow(500, 110, 555, 110, "否")

# Ephemeral branches
ephemeral_branches = [
    (540, 400, "ContainerDisk\n（快速，暫態）", "#fef9c3", "#fde047", "#713f12", "OS 映像測試"),
    (700, 400, "EmptyDisk\n（指定大小）", "#fef9c3", "#fde047", "#713f12", "臨時空間"),
]
for bx, by, label, cf, cs, tc, reason in ephemeral_branches:
    svg += box(bx-80, by-20, 160, 40, cf, cs)
    svg += text(bx, by, label, 11, tc, True)

svg += arrow(610, 135, 560, 380, "OS 映像測試")
svg += arrow(660, 135, 700, 380, "臨時空間")

# Config branches
svg += diamond(780, 210, 140, 50)
svg += text(780, 210, "資料類型？", 12, TEXT_PRIMARY, True)
svg += arrow(720, 110, 780, 185, "設定資料")

configs = [
    (660, 320, "CloudInit"),
    (760, 320, "ConfigMap"),
    (860, 320, "Secret"),
    (760, 390, "DownwardAPI"),
]
for cx2, cy2, label in configs:
    svg += box(cx2-50, cy2-16, 100, 32, "#dbeafe", "#93c5fd")
    svg += text(cx2, cy2, label, 11, "#1d4ed8", True)
    svg += arrow(780, 235, cx2, cy2-16)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-9.svg", "w") as f:
    f.write(svg)
print("Done")
