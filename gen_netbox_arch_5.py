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

W, H = 800, 200
dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-arch-5.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="arrow", markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient="auto")
marker.add(dwg.polygon([(0,0),(10,3.5),(0,7)], fill=ARROW))
dwg.defs.add(marker)

dwg.add(dwg.text("動態設定管理架構", insert=(W/2, 28), text_anchor="middle",
                  font_family=FONT, font_size=15, font_weight="700", fill=TEXT_PRIMARY))

# Three boxes
bw, bh = 200, 80
y = 60

# Static config
x1 = 50
dwg.add(dwg.rect((x1, y), (bw, bh), rx=6, ry=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
dwg.add(dwg.text("configuration.py", insert=(x1+bw/2, y+22), text_anchor="middle", font_family=FONT, font_size=12, font_weight="600", fill=TEXT_PRIMARY))
dwg.add(dwg.text("（靜態設定）", insert=(x1+bw/2, y+38), text_anchor="middle", font_family=FONT, font_size=10, fill=TEXT_SECONDARY))
dwg.add(dwg.text("SECRET_KEY, DATABASE, REDIS", insert=(x1+bw/2, y+56), text_anchor="middle", font_family=FONT, font_size=9, fill=TEXT_SECONDARY))

# Dynamic config
x2 = 50
y2 = y + bh + 30
dwg.add(dwg.rect((x2, y2), (bw, bh), rx=6, ry=6, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
dwg.add(dwg.text("ConfigRevision (DB)", insert=(x2+bw/2, y2+22), text_anchor="middle", font_family=FONT, font_size=12, font_weight="600", fill=TEXT_PRIMARY))
dwg.add(dwg.text("（動態設定）", insert=(x2+bw/2, y2+38), text_anchor="middle", font_family=FONT, font_size=10, fill=TEXT_SECONDARY))
dwg.add(dwg.text("UI 可修改的參數", insert=(x2+bw/2, y2+56), text_anchor="middle", font_family=FONT, font_size=9, fill=TEXT_SECONDARY))

# Merged settings
x3 = 490
ym = (y + bh + y2 + bh)/2 - bh/2
dwg.add(dwg.rect((x3, ym), (bw, bh), rx=6, ry=6, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
dwg.add(dwg.text("Django settings.py", insert=(x3+bw/2, ym+22), text_anchor="middle", font_family=FONT, font_size=12, font_weight="600", fill=TEXT_PRIMARY))
dwg.add(dwg.text("合併載入", insert=(x3+bw/2, ym+42), text_anchor="middle", font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

# Arrows from both sources to merged
mid_x = 310
cy1 = y + bh/2
cy2 = y2 + bh/2
cm = ym + bh/2
dwg.add(dwg.line((x1+bw, cy1), (mid_x, cy1), stroke=ARROW, stroke_width=1.5))
dwg.add(dwg.line((x2+bw, cy2), (mid_x, cy2), stroke=ARROW, stroke_width=1.5))
dwg.add(dwg.line((mid_x, cy1), (mid_x, cy2), stroke=ARROW, stroke_width=1.5))
dwg.add(dwg.line((mid_x, cm), (x3-2, cm), stroke=ARROW, stroke_width=1.5, marker_end="url(#arrow)"))

dwg.save()
print("saved arch-5.svg")
