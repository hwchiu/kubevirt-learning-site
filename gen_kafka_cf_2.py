import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
BOX_FILL, BOX_STROKE = "#f0f4ff", "#c7d2fe"
NOTE_FILL = "#fefce8"; NOTE_STROKE = "#fde68a"
LOOP_FILL = "#f0fdf4"; LOOP_STROKE = "#86efac"

W, H = 1600, 680
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-core-features-2.svg",
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

PARTS = [("Consumer 1", 240), ("Consumer 2", 620), ("Group Coordinator\n(Broker)", 1050)]
bw, bh = 200, 55

for name, cx in PARTS:
    x = cx - bw//2
    dwg.add(dwg.rect((x, 30),(bw, bh), rx=8, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    lines = name.split("\n")
    if len(lines)==2:
        dwg.add(dwg.text(lines[0], insert=(cx,51), text_anchor="middle",
                         font_family=FONT, font_size=13, font_weight="600", fill=TEXT_PRIMARY))
        dwg.add(dwg.text(lines[1], insert=(cx,70), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))
    else:
        dwg.add(dwg.text(name, insert=(cx,58), text_anchor="middle",
                         dominant_baseline="middle", font_family=FONT, font_size=13,
                         font_weight="600", fill=TEXT_PRIMARY))
    dwg.add(dwg.line((cx,85),(cx,640), stroke="#d1d5db", stroke_width=1.5, stroke_dasharray="6,4"))

def msg(x1, x2, y, label, dashed=False):
    da="8,4" if dashed else None
    attrs={"stroke":ARROW,"stroke_width":1.5,"marker_end":"url(#arr)"}
    if da: attrs["stroke_dasharray"]=da
    dwg.add(dwg.line((x1,y),(x2,y),**attrs))
    mx=(x1+x2)/2
    tw=len(label)*6.5+16
    dwg.add(dwg.rect((mx-tw/2,y-13),(tw,16),rx=3,fill="#ffffff",opacity=0.92))
    dwg.add(dwg.text(label,insert=(mx,y-2),text_anchor="middle",
                     font_family=FONT,font_size=10,fill=TEXT_SECONDARY))

def note_box(cx, y, text):
    tw=len(text)*7+24
    dwg.add(dwg.rect((cx-tw/2,y-13),(tw,22),rx=4,fill=NOTE_FILL,stroke=NOTE_STROKE,stroke_width=1))
    dwg.add(dwg.text(text,insert=(cx,y+3),text_anchor="middle",font_family=FONT,font_size=11,fill="#92400e"))

c1x,c2x,gcx=240,620,1050
y=120; msg(c1x,gcx,y,"FindCoordinator（按 group.id Hash）")
y=150; msg(gcx,c1x,y,"Coordinator 位址",True)
y=190; msg(c1x,gcx,y,"JoinGroup（第一個加入者成為 Leader）")
y=220; msg(c2x,gcx,y,"JoinGroup")
y=255; msg(gcx,c1x,y,"JoinGroupResponse（包含成員資訊，指定 C1 為 Leader）",True)
y=285; msg(gcx,c2x,y,"JoinGroupResponse（等待 Leader 分配）",True)
note_box(c1x, 318, "C1 執行 Partition 分配演算法")
y=340; msg(c1x,gcx,y,"SyncGroup（提交分配方案）")
y=365; msg(c2x,gcx,y,"SyncGroup")
y=400; msg(gcx,c1x,y,"SyncGroupResponse（C1 的 Partition 分配）",True)
y=430; msg(gcx,c2x,y,"SyncGroupResponse（C2 的 Partition 分配）",True)

# Loop box
loop_y1=460; loop_y2=580
dwg.add(dwg.rect((120,loop_y1),(760,loop_y2-loop_y1), rx=6,
                 fill=LOOP_FILL, stroke=LOOP_STROKE, stroke_width=1.5, opacity=0.7))
dwg.add(dwg.text("loop  Heartbeat", insert=(130,loop_y1+18), font_family=FONT,
                 font_size=11, font_weight="600", fill="#166534"))
y=510; msg(c1x,gcx,y,"Heartbeat（session.timeout.ms 内）")
y=545; msg(c2x,gcx,y,"Heartbeat")

dwg.save()
print("Done")
