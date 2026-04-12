import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
REMOVED_FILL = "#fef2f2"; REMOVED_STROKE = "#fca5a5"
KEPT_FILL = "#f0fdf4"; KEPT_STROKE = "#86efac"

W, H = 1600, 380
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-architecture-3.svg",
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

def label(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, style="normal"):
    dwg.add(dwg.rect((x,y),(w,h), rx=8, fill=fill, stroke=stroke, stroke_width=1.5))
    dwg.add(dwg.text(text, insert=(x+w/2, y+h/2), text_anchor="middle",
                     dominant_baseline="middle", font_family=FONT, font_size=13,
                     font_weight="600", fill=TEXT_PRIMARY))

def container(x,y,w,h,title,style="normal"):
    fill = CONTAINER_FILL if style=="blue" else "#f9fafb"
    stroke = CONTAINER_STROKE if style=="blue" else "#e5e7eb"
    dwg.add(dwg.rect((x,y),(w,h), rx=12, fill=fill, stroke=stroke, stroke_width=1.5))
    dwg.add(dwg.text(title, insert=(x+14, y+22), font_family=FONT, font_size=13,
                     font_weight="600", fill=TEXT_SECONDARY))

# Containers
container(50, 50, 680, 170, "Compaction 前")
container(50, 250, 480, 110, "Compaction 後")

bw, bh = 110, 55
gap = 18
# Before: 5 items
before = [("k=A, v=1","removed"), ("k=B, v=2","removed"), ("k=A, v=3","kept"), 
          ("k=C, v=4","kept"), ("k=B, v=5","kept")]
bx = 80
by = 110
for i,(txt,state) in enumerate(before):
    f = REMOVED_FILL if state=="removed" else KEPT_FILL
    s = REMOVED_STROKE if state=="removed" else KEPT_STROKE
    label(bx + i*(bw+gap), by, bw, bh, txt, f, s)
    if i < len(before)-1:
        x2 = bx + (i+1)*(bw+gap)
        dwg.add(dwg.line((bx+i*(bw+gap)+bw, by+bh/2),(x2, by+bh/2),
                         stroke=ARROW, stroke_width=1.5, marker_end="url(#arr)"))

# After: 3 items
after = ["k=A, v=3", "k=C, v=4", "k=B, v=5"]
ax = 80; ay = 285
for i,txt in enumerate(after):
    label(ax + i*(bw+gap), ay, bw, bh, txt, KEPT_FILL, KEPT_STROKE)
    if i < len(after)-1:
        x2 = ax + (i+1)*(bw+gap)
        dwg.add(dwg.line((ax+i*(bw+gap)+bw, ay+bh/2),(x2,ay+bh/2),
                         stroke=ARROW, stroke_width=1.5, marker_end="url(#arr)"))

# Arrow from Before→After container
arr_x = 760
dwg.add(dwg.line((760, 135), (900, 305), stroke=ARROW, stroke_width=2, marker_end="url(#arr)"))
dwg.add(dwg.text("Log Compaction", insert=(890, 210), font_family=FONT, font_size=13,
                 font_weight="600", fill=ARROW, transform="rotate(-25,890,210)"))

# Legend
lx, ly = 980, 100
dwg.add(dwg.rect((lx, ly),(280,150), rx=8, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1))
dwg.add(dwg.text("圖例", insert=(lx+14, ly+22), font_family=FONT, font_size=13,
                 font_weight="600", fill=TEXT_SECONDARY))
dwg.add(dwg.rect((lx+20,ly+40),(40,24), rx=4, fill=REMOVED_FILL, stroke=REMOVED_STROKE, stroke_width=1.5))
dwg.add(dwg.text("已被 Compact 移除", insert=(lx+72, ly+56), font_family=FONT, font_size=12, fill=TEXT_PRIMARY))
dwg.add(dwg.rect((lx+20,ly+80),(40,24), rx=4, fill=KEPT_FILL, stroke=KEPT_STROKE, stroke_width=1.5))
dwg.add(dwg.text("保留（最新版本）", insert=(lx+72, ly+96), font_family=FONT, font_size=12, fill=TEXT_PRIMARY))

dwg.save()
print("Done")
