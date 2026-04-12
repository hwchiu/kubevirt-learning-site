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

W, H = 900, 580
dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-arch-3.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="arrow", markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient="auto")
marker.add(dwg.polygon([(0,0),(10,3.5),(0,7)], fill=ARROW))
dwg.defs.add(marker)

dwg.add(dwg.text("Plugin 整合點一覽", insert=(W/2, 32), text_anchor="middle",
                  font_family=FONT, font_size=17, font_weight="700", fill=TEXT_PRIMARY))

# Central plugin box
cx, cy = 420, 120
pw, ph = 200, 55
dwg.add(dwg.rect((cx-pw/2, cy-ph/2), (pw, ph), rx=8, ry=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
dwg.add(dwg.text("Plugin", insert=(cx, cy-8), text_anchor="middle", font_family=FONT, font_size=14, font_weight="700", fill=TEXT_PRIMARY))
dwg.add(dwg.text("(PluginConfig)", insert=(cx, cy+10), text_anchor="middle", font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

# Integration points - arranged in two columns
left_items = [
    ("middleware", "注入 MIDDLEWARE 列表", 140, 240),
    ("queues", "建立 RQ 佇列 {plugin}.{queue}", 140, 310),
    ("events_pipeline", "事件處理管線", 140, 380),
    ("search_indexes", "全文搜尋索引", 140, 450),
    ("data_backends", "資料後端", 140, 520),
]
right_items = [
    ("graphql_schema", "擴充 GraphQL Schema", 700, 240),
    ("menu / menu_items", "導航選單", 700, 310),
    ("template_extensions", "模板擴充", 700, 380),
    ("user_preferences", "使用者偏好", 700, 450),
    ("/plugins/{name}/", "URL 路由 (Web + API)", 700, 520),
]

bw, bh = 200, 45
for name, desc, bx, by in left_items:
    dwg.add(dwg.rect((bx-bw/2, by-bh/2), (bw, bh), rx=5, ry=5, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    dwg.add(dwg.text(name, insert=(bx, by-6), text_anchor="middle", font_family=FONT, font_size=11, font_weight="600", fill=TEXT_PRIMARY))
    dwg.add(dwg.text(desc, insert=(bx, by+10), text_anchor="middle", font_family=FONT, font_size=9, fill=TEXT_SECONDARY))
    dwg.add(dwg.line((bx+bw/2, by), (cx-pw/2-2, cy), stroke=ARROW, stroke_width=1.2, marker_end="url(#arrow)"))

for name, desc, bx, by in right_items:
    dwg.add(dwg.rect((bx-bw/2, by-bh/2), (bw, bh), rx=5, ry=5, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    dwg.add(dwg.text(name, insert=(bx, by-6), text_anchor="middle", font_family=FONT, font_size=11, font_weight="600", fill=TEXT_PRIMARY))
    dwg.add(dwg.text(desc, insert=(bx, by+10), text_anchor="middle", font_family=FONT, font_size=9, fill=TEXT_SECONDARY))
    dwg.add(dwg.line((cx+pw/2, cy), (bx-bw/2-2, by), stroke=ARROW, stroke_width=1.2, marker_end="url(#arrow)"))

dwg.save()
print("saved arch-3.svg")
