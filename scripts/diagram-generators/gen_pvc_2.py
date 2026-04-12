#!/usr/bin/env python3
# pvc-datavolume.md - Block 2: DataVolume Phase state machine

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 940, 340

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

def arrow(x1, y1, x2, y2, label="", color=ARROW):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arr{color.replace("#","")})"/>'
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2
        dx = 0 if abs(x2-x1) > abs(y2-y1) else 30
        dy = -9 if abs(x2-x1) > abs(y2-y1) else 0
        s += f'<text x="{mx+dx}" y="{my+dy}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return s

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr{ARROW.replace("#","")}" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
  <marker id="arref4444" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#ef4444"/>
  </marker>
  <marker id="arr16a34a" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#16a34a"/>
  </marker>
  <marker id="arrf59e0b" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#f59e0b"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Start dot
svg += '<circle cx="30" cy="80" r="8" fill="#111827"/>'

# States - horizontal main flow
states_main = [
    (80, "Pending", BOX_FILL, BOX_STROKE, 120),
    (270, "WaitForFirstConsumer", CONTAINER_FILL, CONTAINER_STROKE, 200),
    (520, "ImportScheduled", BOX_FILL, BOX_STROKE, 150),
    (720, "ImportInProgress", "#fef3c7", "#fcd34d", 150),
]
for x, label, cf, cs, w in states_main:
    svg += box(x-w//2, 60, w, 40, cf, cs)
    svg += text(x, 80, label, 12, TEXT_PRIMARY, True)

# Paused state (below ImportInProgress)
svg += box(660, 180, 150, 40, "#f3e8ff", "#d8b4fe")
svg += text(735, 200, "Paused", 12, "#581c87", True)

# Succeeded / Failed states
svg += box(840, 50, 130, 40, "#dcfce7", "#86efac")
svg += text(905, 70, "Succeeded ✅", 12, "#166534", True)
svg += box(840, 120, 130, 40, "#fee2e2", "#fca5a5")
svg += text(905, 140, "Failed ❌", 12, "#dc2626", True)

# Arrows
svg += arrow(38, 80, 80-60, 80, "建立 DataVolume")
svg += arrow(80+60, 80, 270-100, 80, "標準 StorageClass")
svg += arrow(270+100, 80, 520-75, 80, "PVC binding 完成")
svg += arrow(520+75, 80, 720-75, 80, "Importer Pod 執行")
svg += arrow(720+75, 65, 840, 60, "匯入成功", "#16a34a")
svg += arrow(720+75, 95, 840, 130, "匯入失敗", "#ef4444")
# Paused
svg += arrow(720, 100, 735, 180, "暫停", "#f59e0b")
svg += arrow(715, 180, 695, 100, "恢復", "#f59e0b")
# WFC note
svg += text(270, 250, "WaitForFirstConsumer: Local Storage 場景\n(local-path, TopoLVM) 需等 VM 決定節點", 10, TEXT_SECONDARY)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-pvc-2.svg", "w") as f:
    f.write(svg)
print("Done")
