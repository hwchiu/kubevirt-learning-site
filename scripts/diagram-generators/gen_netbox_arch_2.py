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

W, H = 1400, 200
dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-arch-2.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="arrow", markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient="auto")
marker.add(dwg.polygon([(0,0),(10,3.5),(0,7)], fill=ARROW))
dwg.defs.add(marker)

dwg.add(dwg.text("NetBox Middleware Pipeline（請求處理順序）", insert=(W/2, 28),
                  text_anchor="middle", font_family=FONT, font_size=15, font_weight="700", fill=TEXT_PRIMARY))

steps = [
    "HTTP\nRequest", "Cors", "Session", "Locale", "Common",
    "CSRF", "Auth", "Message", "XFrame", "Security",
    "HTMX", "RemoteUser", "Core", "Maint.", "View"
]

bw, bh = 78, 48
gap = 14
start_x = 18
y = 95

for i, label in enumerate(steps):
    x = start_x + i*(bw+gap)
    lines = label.split('\n')
    if i == 0 or i == len(steps)-1:
        fill = CONTAINER_FILL
        stroke = CONTAINER_STROKE
    else:
        fill = BOX_FILL
        stroke = BOX_STROKE
    dwg.add(dwg.rect((x, y), (bw, bh), rx=5, ry=5, fill=fill, stroke=stroke, stroke_width=1.5))
    cy = y + bh/2 - (len(lines)-1)*7
    for j, line in enumerate(lines):
        dwg.add(dwg.text(line, insert=(x+bw/2, cy+j*14), text_anchor="middle",
                         font_family=FONT, font_size=10, fill=TEXT_PRIMARY))
    if i < len(steps)-1:
        ax = x+bw
        ay = y+bh/2
        dwg.add(dwg.line((ax, ay),(ax+gap-2, ay), stroke=ARROW, stroke_width=1.5,
                          marker_end="url(#arrow)"))

dwg.save()
print("saved arch-2.svg")
