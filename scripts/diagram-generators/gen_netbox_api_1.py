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
LIFELINE = "#d1d5db"

W, H = 1100, 520

dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-api-1.svg", size=(W, H))
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(id="arrow", markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient="auto")
marker.add(dwg.polygon([(0,0),(10,3.5),(0,7)], fill=ARROW))
dwg.defs.add(marker)
marker2 = dwg.marker(id="arrow2", markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient="auto")
marker2.add(dwg.polygon([(0,0),(10,3.5),(0,7)], fill=TEXT_SECONDARY))
dwg.defs.add(marker2)

dwg.add(dwg.text("API 請求處理流程 (Sequence)", insert=(W/2, 30), text_anchor="middle",
                  font_family=FONT, font_size=15, font_weight="700", fill=TEXT_PRIMARY))

participants = ["Client", "Django\nDispatcher", "Token\nAuth", "Token\nPerm", "ViewSet", "FilterSet", "Serializer", "PostgreSQL"]
n = len(participants)
margin = 60
spacing = (W - 2*margin) / (n - 1)
bw, bh = 90, 44
top_y = 50

xs = [margin + i * spacing for i in range(n)]

# Draw participant boxes and lifelines
for i, (x, p) in enumerate(zip(xs, participants)):
    lines = p.split('\n')
    dwg.add(dwg.rect((x-bw/2, top_y), (bw, bh), rx=5, ry=5, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    cy = top_y + bh/2 - (len(lines)-1)*7
    for j, line in enumerate(lines):
        dwg.add(dwg.text(line, insert=(x, cy+j*14), text_anchor="middle", font_family=FONT, font_size=10, fill=TEXT_PRIMARY))
    # Lifeline
    dwg.add(dwg.line((x, top_y+bh), (x, H-30), stroke=LIFELINE, stroke_width=1, stroke_dasharray="4,3"))

# Messages
messages = [
    (0, 1, "GET /api/dcim/devices/?site=nyc"),
    (1, 2, "authenticate(request)"),
    (2, 2, "驗證 Token (v1/v2)"),
    (2, 1, "(user, token)  ←"),
    (1, 3, "has_permission(request, view)"),
    (3, 3, "檢查 write_enabled"),
    (3, 1, "True  ←"),
    (1, 4, "list(request)"),
    (4, 4, "queryset.restrict(user)"),
    (4, 5, "套用查詢參數"),
    (5, 7, "SQL Query"),
    (7, 5, "QuerySet  ←"),
    (5, 4, "filtered QuerySet  ←"),
    (4, 6, "序列化"),
    (6, 0, "JSON 200  ←"),
]

msg_start_y = top_y + bh + 20
step_h = (H - 30 - msg_start_y) / len(messages)
y = msg_start_y

for i, (frm, to, label) in enumerate(messages):
    x1 = xs[frm]
    x2 = xs[to]
    my = y + step_h/2
    is_return = label.endswith("←")
    color = TEXT_SECONDARY if is_return else ARROW
    marker_id = "arrow2" if is_return else "arrow"
    dash = "5,3" if is_return else None
    stroke_kwargs = dict(stroke=color, stroke_width=1.3, marker_end=f"url(#{marker_id})")
    if dash:
        stroke_kwargs["stroke_dasharray"] = dash
    if frm == to:
        # self arrow - small loop
        dwg.add(dwg.path(d=f"M {x1} {my} Q {x1+35} {my-10} {x1+35} {my+10} Q {x1+35} {my+25} {x1} {my+20}",
                         fill="none", stroke=color, stroke_width=1.3, marker_end=f"url(#{marker_id})"))
    else:
        dwg.add(dwg.line((x1, my), (x2, my), **stroke_kwargs))
    # label
    lx = (x1+x2)/2
    ly = my - 4
    if frm == to:
        lx = x1 + 40
        ly = my + 5
    anchor = "middle"
    dwg.add(dwg.text(label.replace(" ←",""), insert=(lx, ly), text_anchor=anchor,
                     font_family=FONT, font_size=9, fill=TEXT_SECONDARY))
    y += step_h

dwg.save()
print("saved api-1.svg")
