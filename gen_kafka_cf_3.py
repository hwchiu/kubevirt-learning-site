import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
BOX_FILL, BOX_STROKE = "#f0f4ff", "#c7d2fe"
NOTE_FILL = "#fefce8"; NOTE_STROKE = "#fde68a"

W, H = 1200, 420
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-core-features-3.svg",
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

PARTS = [("Consumer", 230), ("Broker\n(Group Coordinator)", 730)]
bw, bh = 200, 55

for name, cx in PARTS:
    x = cx - bw//2
    dwg.add(dwg.rect((x,30),(bw,bh), rx=8, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    lines = name.split("\n")
    if len(lines)==2:
        dwg.add(dwg.text(lines[0], insert=(cx,51), text_anchor="middle",
                         font_family=FONT, font_size=13, font_weight="600", fill=TEXT_PRIMARY))
        dwg.add(dwg.text(lines[1], insert=(cx,70), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))
    else:
        dwg.add(dwg.text(name, insert=(cx,57), text_anchor="middle",
                         dominant_baseline="middle", font_family=FONT, font_size=13,
                         font_weight="600", fill=TEXT_PRIMARY))
    dwg.add(dwg.line((cx,85),(cx,390), stroke="#d1d5db", stroke_width=1.5, stroke_dasharray="6,4"))

def msg(x1,x2,y,label,dashed=False):
    da="8,4" if dashed else None
    attrs={"stroke":ARROW,"stroke_width":1.5,"marker_end":"url(#arr)"}
    if da: attrs["stroke_dasharray"]=da
    dwg.add(dwg.line((x1,y),(x2,y),**attrs))
    mx=(x1+x2)/2
    tw=len(label)*6.8+16
    dwg.add(dwg.rect((mx-tw/2,y-13),(tw,16),rx=3,fill="#ffffff",opacity=0.92))
    dwg.add(dwg.text(label,insert=(mx,y-2),text_anchor="middle",
                     font_family=FONT,font_size=10,fill=TEXT_SECONDARY))

def note_box(cx, y, text):
    tw=len(text)*7.5+24
    dwg.add(dwg.rect((cx-tw/2,y-13),(tw,22),rx=4,fill=NOTE_FILL,stroke=NOTE_STROKE,stroke_width=1))
    dwg.add(dwg.text(text,insert=(cx,y+3),text_anchor="middle",font_family=FONT,font_size=11,fill="#92400e"))

cx,bx=230,730
y=130; msg(cx,bx,y,"FetchRequest（從 lastCommittedOffset 開始消費）")
y=175; msg(bx,cx,y,"FetchResponse（批次訊息）",True)
note_box(cx, 218, "處理訊息")
y=255; msg(cx,bx,y,"OffsetCommitRequest（提交 currentOffset + 1）")
y=300; msg(bx,cx,y,"OffsetCommitResponse",True)

dwg.save()
print("Done")
