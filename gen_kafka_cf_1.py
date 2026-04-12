import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"

W, H = 1800, 300
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-core-features-1.svg",
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

def box(x, y, w, h, line1, line2=None):
    dwg.add(dwg.rect((x,y),(w,h), rx=8, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    cy = y+h/2+(-9 if line2 else 0)
    dwg.add(dwg.text(line1, insert=(x+w/2, cy), text_anchor="middle",
                     dominant_baseline="middle", font_family=FONT, font_size=13,
                     font_weight="600", fill=TEXT_PRIMARY))
    if line2:
        dwg.add(dwg.text(line2, insert=(x+w/2, cy+20), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

def arr(x1,y1,x2,y2,label=None,dashed=False):
    da = "8,4" if dashed else None
    attrs={"stroke":ARROW,"stroke_width":1.5,"marker_end":"url(#arr)"}
    if da: attrs["stroke_dasharray"]=da
    dwg.add(dwg.line((x1,y1),(x2,y2),**attrs))
    if label:
        mx,my=(x1+x2)/2,(y1+y2)/2
        tw=len(label)*6.5+16
        dwg.add(dwg.rect((mx-tw/2,my-11),(tw,18),rx=3,fill="#ffffff",opacity=0.9))
        dwg.add(dwg.text(label,insert=(mx,my+1),text_anchor="middle",
                         font_family=FONT,font_size=10,fill=TEXT_SECONDARY,dominant_baseline="middle"))

# LR flow: App → Interceptors → Serializer → Partitioner → RecordAccumulator → Sender ↔ Broker
# Sender → App (Callback)
bh = 70
nodes = [
    (50, 80, 180, bh, "應用程式", "producer.send(record)"),
    (280, 80, 190, bh, "ProducerInterceptors", "（前置處理）"),
    (520, 80, 190, bh, "Key/Value Serializer", "（序列化）"),
    (760, 80, 190, bh, "Partitioner", "（決定目標 Partition）"),
    (1000, 80, 190, bh, "RecordAccumulator", "（批次緩衝）"),
    (1240, 80, 190, bh, "Sender 執行緒", "（後台發送）"),
    (1480, 80, 180, bh, "Broker Leader", None),
]
for (x,y,w,h,l1,l2) in nodes:
    box(x,y,w,h,l1,l2)

# Forward arrows
for i in range(len(nodes)-1):
    x1 = nodes[i][0]+nodes[i][2]
    x2 = nodes[i+1][0]
    y = nodes[i][1]+nodes[i][3]//2
    label = None
    if i == 4:
        label = "batch.size / linger.ms"
    if i == 5:
        label = "ProduceRequest"
    arr(x1, y, x2, y, label)

# Broker → Sender (ProduceResponse) — curved back arrow
bx = nodes[6][0]+90; by = nodes[6][1]+nodes[6][3]
sx = nodes[5][0]+95; sy = nodes[5][1]+nodes[5][3]
dwg.add(dwg.path(f"M{bx} {by+5} C{bx} {by+60},{sx} {by+60},{sx} {by+5}",
                 stroke=ARROW, stroke_width=1.5, fill="none", marker_end="url(#arr)",
                 stroke_dasharray="8,4"))
dwg.add(dwg.text("ProduceResponse", insert=((bx+sx)/2, by+75), text_anchor="middle",
                 font_family=FONT, font_size=10, fill=TEXT_SECONDARY))

# Sender → App (Callback)
sx2 = nodes[5][0]+95; sy2 = nodes[5][1]+nodes[5][3]
ax = nodes[0][0]+90; ay = nodes[0][1]+nodes[0][3]
dwg.add(dwg.path(f"M{sx2} {sy2+5} C{sx2} {sy2+90},{ax} {sy2+90},{ax} {sy2+5}",
                 stroke=ARROW, stroke_width=1.5, fill="none", marker_end="url(#arr)",
                 stroke_dasharray="6,4"))
dwg.add(dwg.text("Callback", insert=((sx2+ax)//2, sy2+105), text_anchor="middle",
                 font_family=FONT, font_size=10, fill=TEXT_SECONDARY))

dwg.save()
print("Done")
