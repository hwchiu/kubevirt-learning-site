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

W, H = 1200, 700
dwg = svgwrite.Drawing("/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/netbox/netbox-arch-1.svg", size=(W, H))

# Background
dwg.add(dwg.rect((0, 0), (W, H), fill=BG))

def container(x, y, w, h, label):
    g = dwg.g()
    g.add(dwg.rect((x, y), (w, h), rx=8, ry=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    g.add(dwg.text(label, insert=(x+10, y+18), font_family=FONT, font_size=11, font_weight="600",
                   fill=TEXT_SECONDARY))
    return g

def box(x, y, w, h, lines, stroke=BOX_STROKE):
    g = dwg.g()
    g.add(dwg.rect((x, y), (w, h), rx=6, ry=6, fill=BOX_FILL, stroke=stroke, stroke_width=1.5))
    cy = y + h/2 - (len(lines)-1)*8
    for i, line in enumerate(lines):
        g.add(dwg.text(line, insert=(x+w/2, cy+i*16), text_anchor="middle", font_family=FONT,
                       font_size=11, fill=TEXT_PRIMARY))
    return g

def arrow(x1, y1, x2, y2, label=""):
    g = dwg.g()
    g.add(dwg.line((x1, y1), (x2, y2), stroke=ARROW, stroke_width=1.5,
                   marker_end="url(#arrow)"))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2 - 6
        g.add(dwg.text(label, insert=(mx, my), text_anchor="middle", font_family=FONT,
                       font_size=10, fill=TEXT_SECONDARY))
    return g

# Arrow marker
marker = dwg.marker(id="arrow", markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient="auto")
marker.add(dwg.polygon([(0,0),(10,3.5),(0,7)], fill=ARROW))
dwg.defs.add(marker)

# Title
dwg.add(dwg.text("NetBox 系統部署架構", insert=(W/2, 35), text_anchor="middle",
                  font_family=FONT, font_size=18, font_weight="700", fill=TEXT_PRIMARY))

# Client
cg = container(50, 60, 200, 80, "使用者端")
dwg.add(cg)
b_browser = box(70, 80, 160, 45, ["瀏覽器 / API Client"])
dwg.add(b_browser)

# Reverse Proxy
rg = container(300, 60, 240, 80, "反向代理層")
dwg.add(rg)
b_nginx = box(320, 80, 200, 45, ["Nginx", ":443 SSL / 靜態檔案"])
dwg.add(b_nginx)

# App Server
ag = container(590, 60, 240, 110, "應用伺服器層")
dwg.add(ag)
b_gunicorn = box(610, 80, 200, 40, ["Gunicorn WSGI", "127.0.0.1:8001"])
dwg.add(b_gunicorn)
b_django = box(610, 128, 200, 30, ["Django 5.2.12"])
dwg.add(b_django)

# API Layer
alg = container(880, 60, 200, 110, "API 層")
dwg.add(alg)
b_rest = box(900, 80, 160, 35, ["REST API (DRF)"])
dwg.add(b_rest)
b_gql = box(900, 123, 160, 35, ["GraphQL (Strawberry)"])
dwg.add(b_gql)

# Data Store
dg = container(300, 250, 240, 110, "資料儲存層")
dwg.add(dg)
b_pg = box(320, 270, 200, 40, ["PostgreSQL", "主要資料庫"])
dwg.add(b_pg)
b_redis = box(320, 318, 200, 35, ["Redis", "Cache + Queue"])
dwg.add(b_redis)

# Background Worker
wg = container(590, 250, 240, 80, "背景工作層")
dwg.add(wg)
b_rq = box(610, 270, 200, 45, ["RQ Worker", "high / default / low"])
dwg.add(b_rq)

# Arrows
# Browser -> Nginx
dwg.add(arrow(230, 102, 320, 102, "HTTPS :443"))
# Nginx -> Gunicorn
dwg.add(arrow(520, 102, 610, 102, "proxy_pass"))
# Gunicorn -> Django
dwg.add(dwg.line((710, 120), (710, 128), stroke=ARROW, stroke_width=1.5))
# Django -> REST
dwg.add(arrow(810, 100, 900, 97))
# Django -> GraphQL
dwg.add(arrow(810, 135, 900, 140))
# Django -> PostgreSQL
dwg.add(arrow(710, 175, 520, 288, "ORM"))
# Django -> Redis
dwg.add(arrow(710, 175, 520, 335, "Cache"))
# RQ -> Redis
dwg.add(arrow(610, 292, 520, 335, "Dequeue"))
# RQ -> PostgreSQL
dwg.add(arrow(610, 292, 520, 287))
# Django -> Redis (enqueue)
dwg.add(arrow(710, 175, 610, 280, "Enqueue"))

dwg.save()
print("Saved arch-1.svg")
