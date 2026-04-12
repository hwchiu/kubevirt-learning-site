import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 600, 750
dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-arch-4.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="arrow", markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient="auto")
marker.add(dwg.polygon([(0,0),(10,3.5),(0,7)], fill=ARROW))
dwg.defs.add(marker)

dwg.add(dwg.text("upgrade.sh 升級流程", insert=(W/2, 30), text_anchor="middle",
                  font_family=FONT, font_size=16, font_weight="700", fill=TEXT_PRIMARY))

bw, bh = 340, 36
steps_main = [
    "1. 檢查 Python ≥ 3.12",
    "2. 建立 / 重建 virtualenv",
    "3. 升級 pip",
    "4. 安裝 wheel",
    "5. 安裝 requirements.txt",
    "6. 安裝 local_requirements.txt（若存在）",
]
steps_after = [
    "8. Trace 遺漏的 Cable Paths",
    "9. 建構 MkDocs 文件",
    "10. collectstatic 收集靜態檔案",
    "11. 移除過期 Content Types",
    "12. 重建搜尋索引（lazy）",
    "13. 清除過期 Sessions",
    "14. 完成，提示重啟服務",
]

cx = W/2
y = 55
gap = 10

# Main steps
for step in steps_main:
    x = cx - bw/2
    dwg.add(dwg.rect((x, y), (bw, bh), rx=5, ry=5, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    dwg.add(dwg.text(step, insert=(cx, y+bh/2+4), text_anchor="middle", font_family=FONT, font_size=11, fill=TEXT_PRIMARY))
    y += bh + gap
    if step != steps_main[-1]:
        dwg.add(dwg.line((cx, y-gap), (cx, y-2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))

# Decision diamond
dy = y + gap
dw, ddh = 200, 40
# Diamond
pts = [(cx, dy), (cx+dw/2, dy+ddh/2), (cx, dy+ddh), (cx-dw/2, dy+ddh/2)]
dwg.add(dwg.polygon(pts, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
dwg.add(dwg.text("--readonly?", insert=(cx, dy+ddh/2+4), text_anchor="middle",
                  font_family=FONT, font_size=11, fill=TEXT_PRIMARY))
dwg.add(dwg.line((cx, y+gap-2), (cx, dy-2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))

# No branch - migrations
ny = dy + ddh + 10
bw2, bh2 = 180, 36
nx = cx - 60
dwg.add(dwg.line((cx, dy+ddh), (nx+bw2/2, ny-2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))
dwg.add(dwg.rect((nx, ny), (bw2, bh2), rx=5, ry=5, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
dwg.add(dwg.text("7. 執行 Database", insert=(nx+bw2/2, ny+14), text_anchor="middle", font_family=FONT, font_size=10, fill=TEXT_PRIMARY))
dwg.add(dwg.text("Migrations", insert=(nx+bw2/2, ny+28), text_anchor="middle", font_family=FONT, font_size=10, fill=TEXT_PRIMARY))
dwg.add(dwg.text("No", insert=(cx-30, dy+ddh+20), font_family=FONT, font_size=10, fill=TEXT_SECONDARY))

# Yes branch - skip
sy = dy + ddh + 10
bw3, bh3 = 120, 36
sx = cx + 80
dwg.add(dwg.line((cx+dw/2, dy+ddh/2), (sx+bw3/2, sy-2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))
dwg.add(dwg.rect((sx, sy), (bw3, bh3), rx=5, ry=5, fill=BOX_FILL, stroke="#fbbf24", stroke_width=1.5))
dwg.add(dwg.text("跳過", insert=(sx+bw3/2, sy+14), text_anchor="middle", font_family=FONT, font_size=10, fill=TEXT_PRIMARY))
dwg.add(dwg.text("資料庫變更", insert=(sx+bw3/2, sy+28), text_anchor="middle", font_family=FONT, font_size=10, fill=TEXT_PRIMARY))
dwg.add(dwg.text("Yes", insert=(cx+dw/2+8, dy+ddh/2), font_family=FONT, font_size=10, fill=TEXT_SECONDARY))

# Converge
conv_y = ny + bh2 + 15
dwg.add(dwg.line((nx+bw2/2, ny+bh2), (cx, conv_y-2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))
dwg.add(dwg.line((sx+bw3/2, sy+bh3), (cx, conv_y-2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))

y = conv_y
for step in steps_after:
    x = cx - bw/2
    dwg.add(dwg.rect((x, y), (bw, bh), rx=5, ry=5,
                     fill=CONTAINER_FILL if step == steps_after[-1] else BOX_FILL,
                     stroke=CONTAINER_STROKE if step == steps_after[-1] else BOX_STROKE,
                     stroke_width=1.5))
    dwg.add(dwg.text(step, insert=(cx, y+bh/2+4), text_anchor="middle", font_family=FONT, font_size=11, fill=TEXT_PRIMARY))
    y += bh + gap
    if step != steps_after[-1]:
        dwg.add(dwg.line((cx, y-gap), (cx, y-2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))

dwg.save()
print("saved arch-4.svg")
