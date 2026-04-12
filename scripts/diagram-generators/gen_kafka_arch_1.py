import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
ACTIVE_FILL = "#eff6ff"
ACTIVE_STROKE = "#3b82f6"

W, H = 1600, 620
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-architecture-1.svg", 
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

marker2 = dwg.marker(insert=(0,5), size=(10,10), orient="auto-start-reverse", id="arr2")
marker2.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker2)

def container(x, y, w, h, title, style="normal"):
    fill = CONTAINER_FILL if style=="blue" else "#f9fafb"
    stroke = CONTAINER_STROKE if style=="blue" else "#e5e7eb"
    dwg.add(dwg.rect((x,y),(w,h), rx=12, fill=fill, stroke=stroke, stroke_width=1.5))
    dwg.add(dwg.text(title, insert=(x+14, y+22), font_family=FONT, font_size=13,
                     font_weight="600", fill=TEXT_SECONDARY))

def box(x, y, w, h, label, sub=None, style="normal"):
    fill = ACTIVE_FILL if style=="active" else BOX_FILL
    stroke = ACTIVE_STROKE if style=="active" else BOX_STROKE
    dwg.add(dwg.rect((x,y),(w,h), rx=8, fill=fill, stroke=stroke, stroke_width=1.5))
    cy = y + h/2 + (-8 if sub else 0)
    dwg.add(dwg.text(label, insert=(x+w/2, cy), text_anchor="middle",
                     dominant_baseline="middle", font_family=FONT, font_size=13,
                     font_weight="600", fill=TEXT_PRIMARY))
    if sub:
        dwg.add(dwg.text(sub, insert=(x+w/2, cy+20), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

def arrow(x1,y1,x2,y2,label=None,bidir=False):
    attrs = {"stroke": ARROW, "stroke_width": 1.5,
             "marker_end": "url(#arr)"}
    if bidir:
        attrs["marker_start"] = "url(#arr2)"
    dwg.add(dwg.line((x1,y1),(x2,y2), **attrs))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        tw = len(label)*6+12
        dwg.add(dwg.rect((mx-tw/2, my-10),(tw, 18), rx=3, fill="#ffffff", opacity=0.92))
        dwg.add(dwg.text(label, insert=(mx, my+1), text_anchor="middle",
                         dominant_baseline="middle", font_family=FONT,
                         font_size=10, fill=TEXT_SECONDARY))

# Containers
container(55, 50, 490, 480, "Controller Quorum（Raft）", "blue")
container(630, 50, 370, 480, "Broker 叢集")
container(1090, 50, 460, 480, "用戶端")

# Controller nodes (C1 top center, C2 bottom-left, C3 bottom-right)
box(110, 95, 220, 70, "Controller 1", "Active Leader", "active")
c1x, c1y = 220, 165
box(85, 330, 180, 55, "Controller 2", "Voter")
c2x, c2y = 175, 357
box(335, 330, 180, 55, "Controller 3", "Voter")
c3x, c3y = 425, 357

# Broker nodes
box(675, 130, 180, 55, "Broker 1")
b1x, b1y = 765, 157
box(675, 235, 180, 55, "Broker 2")
b2x, b2y = 765, 262
box(675, 340, 180, 55, "Broker 3")
b3x, b3y = 765, 367

# Client nodes
box(1140, 130, 180, 55, "Producer")
px, py = 1230, 157
box(1140, 235, 180, 55, "Consumer")
cox, coy = 1230, 262
box(1140, 340, 200, 55, "AdminClient")
ax, ay = 1240, 367

# Bidirectional arrows (Controllers)
arrow(c1x-20, c1y, c2x+5, c2y-10, "Raft 選舉 / Log 複製", True)
arrow(c1x+20, c1y, c3x-5, c3y-10, "Raft 選舉 / Log 複製", True)
arrow(c2x+10, c2y+8, c3x-10, c3y+8, "Raft 選舉 / Log 複製", True)

# C1 → Brokers
arrow(545, 130, b1x-90, b1y, "MetadataUpdate (Fetch)")
arrow(545, 165, b2x-90, b2y)
arrow(545, 200, b3x-90, b3y, "MetadataUpdate (Fetch)")

# Producer → B1
arrow(px-90, py, b1x+90, b1y, "Produce")
# Consumer → B2
arrow(cox-90, coy, b2x+90, b2y, "Fetch")
# AdminClient → C1 (Admin API)
arrow(ax-90, ay-10, 545, 350, "Admin API")
# AdminClient → B1 (Admin API)
arrow(ax-90, ay+10, b1x+90, b1y+10, "Admin API")

dwg.save()
print("Done")
