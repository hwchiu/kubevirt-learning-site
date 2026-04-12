#!/usr/bin/env python3
# overview.md - Block 4: Cache modes (none / writethrough / writeback)

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 860, 280

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=12, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'

def line(x1,y1,x2,y2,color=ARROW,dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5"{d} marker-end="url(#arr)"/>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# -- none mode --
cx = 60
svg += box(cx, 10, 240, 80, CONTAINER_FILL, CONTAINER_STROKE, 10)
svg += text(cx+120, 26, "none 模式（最安全）", 12, TEXT_SECONDARY, True)
# VM -> Storage (both directions, no cache)
svg += box(cx+10, 46, 80, 30, BOX_FILL, BOX_STROKE)
svg += text(cx+50, 61, "VM 寫入", 11)
svg += box(cx+150, 46, 80, 30, BOX_FILL, BOX_STROKE)
svg += text(cx+190, 61, "底層儲存", 11)
svg += line(cx+90, 56, cx+150, 56)
svg += line(cx+150, 68, cx+90, 68, "#6b7280")

# -- writethrough mode --
cx = 330
svg += box(cx, 10, 240, 140, CONTAINER_FILL, CONTAINER_STROKE, 10)
svg += text(cx+120, 26, "writethrough 模式", 12, TEXT_SECONDARY, True)
svg += box(cx+10, 42, 80, 30, BOX_FILL, BOX_STROKE)
svg += text(cx+50, 57, "VM 寫入", 11)
svg += box(cx+150, 42, 80, 30, "#fef3c7", "#fcd34d")
svg += text(cx+190, 57, "Host 頁面快取", 10)
svg += box(cx+80, 100, 90, 30, BOX_FILL, BOX_STROKE)
svg += text(cx+125, 115, "底層儲存", 11)
svg += line(cx+90, 52, cx+150, 52)
svg += line(cx+190, 72, cx+125, 100, "#f59e0b")
svg += line(cx+125, 100, cx+50, 72, "#6b7280")

# -- writeback mode --
cx = 600
svg += box(cx, 10, 240, 160, CONTAINER_FILL, CONTAINER_STROKE, 10)
svg += text(cx+120, 26, "writeback 模式（最快）", 12, TEXT_SECONDARY, True)
svg += box(cx+10, 42, 80, 30, BOX_FILL, BOX_STROKE)
svg += text(cx+50, 57, "VM 寫入", 11)
svg += box(cx+150, 42, 80, 30, "#fef3c7", "#fcd34d")
svg += text(cx+190, 57, "Host 頁面快取", 10)
svg += box(cx+80, 110, 90, 30, BOX_FILL, BOX_STROKE)
svg += text(cx+125, 125, "底層儲存", 11)
svg += line(cx+90, 52, cx+150, 52)
svg += line(cx+190, 72, cx+125, 110, "#f59e0b", "4 2")  # dashed = async
svg += line(cx+125, 110, cx+50, 72, "#6b7280")

# Labels
svg += text(180, 210, "直接讀寫", 11, TEXT_SECONDARY)
svg += text(450, 210, "寫入同時更新快取 → 同步刷入", 11, TEXT_SECONDARY)
svg += text(720, 210, "先寫快取 → 非同步刷入（虛線）", 11, TEXT_SECONDARY)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-4.svg", "w") as f:
    f.write(svg)
print("Done")
