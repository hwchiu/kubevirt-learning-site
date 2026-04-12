import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
BOX_FILL, BOX_STROKE = "#f0f4ff", "#c7d2fe"
NOTE_FILL = "#fefce8"; NOTE_STROKE = "#fde68a"

W, H = 1600, 620
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-architecture-4.svg",
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

PARTICIPANTS = [
    ("Producer", 200),
    ("Partition Leader\n(Broker 1)", 520),
    ("Follower\n(Broker 2)", 840),
    ("Follower\n(Broker 3)", 1160),
]

bw, bh = 200, 55
line_y_start = 130
line_y_end = 580

for name, cx in PARTICIPANTS:
    x = cx - bw//2
    dwg.add(dwg.rect((x,30),(bw,bh), rx=8, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    lines = name.split("\n")
    if len(lines)==2:
        dwg.add(dwg.text(lines[0], insert=(cx,52), text_anchor="middle",
                         font_family=FONT, font_size=13, font_weight="600", fill=TEXT_PRIMARY))
        dwg.add(dwg.text(lines[1], insert=(cx,70), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))
    else:
        dwg.add(dwg.text(name, insert=(cx,58), text_anchor="middle",
                         dominant_baseline="middle", font_family=FONT, font_size=13,
                         font_weight="600", fill=TEXT_PRIMARY))
    # Lifeline
    dwg.add(dwg.line((cx,85),(cx,line_y_end), stroke="#d1d5db", stroke_width=1.5,
                     stroke_dasharray="6,4"))

def msg(x1,x2,y,label,dashed=False):
    dash = "8,4" if dashed else None
    attrs = {"stroke":ARROW,"stroke_width":1.5,"marker_end":"url(#arr)"}
    if dash: attrs["stroke_dasharray"]=dash
    dwg.add(dwg.line((x1,y),(x2,y),**attrs))
    mx=(x1+x2)/2
    tw=len(label)*7+16
    dwg.add(dwg.rect((mx-tw/2,y-13),(tw,16),rx=3,fill="#ffffff",opacity=0.92))
    dwg.add(dwg.text(label,insert=(mx,y-2),text_anchor="middle",
                     font_family=FONT,font_size=10,fill=TEXT_SECONDARY))

def self_msg(cx, y, label):
    # Self arrow
    dwg.add(dwg.path(f"M{cx} {y} C{cx+60} {y},{cx+60} {y+25},{cx} {y+25}",
                     stroke=ARROW, stroke_width=1.5, fill="none", marker_end="url(#arr)"))
    dwg.add(dwg.text(label, insert=(cx+65, y+14), font_family=FONT, font_size=10, fill=TEXT_SECONDARY))

def note(cx, y, text):
    tw = len(text)*7+30
    nx = cx-tw/2
    dwg.add(dwg.rect((nx,y-14),(tw,22), rx=4, fill=NOTE_FILL, stroke=NOTE_STROKE, stroke_width=1))
    dwg.add(dwg.text(text, insert=(cx,y+2), text_anchor="middle", font_family=FONT,
                     font_size=11, fill="#92400e"))

pCx,lCx,f1Cx,f2Cx = 200,520,840,1160

y=150; msg(pCx,lCx,y,"ProduceRequest (acks=-1)")
y=185; self_msg(lCx,y,"寫入本地 Log")
y=230; msg(f1Cx,lCx,y,"FetchRequest (Follower 複製)")
y=260; msg(lCx,f1Cx,y,"FetchResponse (新訊息)",True)
y=290; self_msg(f1Cx,y,"寫入本地 Log")
y=330; msg(f2Cx,lCx,y,"FetchRequest")
y=360; msg(lCx,f2Cx,y,"FetchResponse",True)
y=390; self_msg(f2Cx,y,"寫入本地 Log")
y=440
dwg.add(dwg.rect((lCx-160,y-16),(320,26), rx=4, fill=NOTE_FILL, stroke=NOTE_STROKE, stroke_width=1))
dwg.add(dwg.text("所有 ISR 成員確認後 — 更新 High Watermark", insert=(lCx,y+4),
                  text_anchor="middle", font_family=FONT, font_size=11, fill="#92400e"))
y=490; msg(lCx,pCx,y,"ProduceResponse (offset)",True)

dwg.save()
print("Done")
