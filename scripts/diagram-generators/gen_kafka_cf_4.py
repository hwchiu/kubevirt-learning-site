import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
BOX_FILL, BOX_STROKE = "#f0f4ff", "#c7d2fe"
NOTE_FILL = "#fefce8"; NOTE_STROKE = "#fde68a"

W, H = 1600, 620
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-core-features-4.svg",
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

PARTS = [
    ("Transactional\nProducer", 220),
    ("Transaction\nCoordinator", 680),
    ("Broker\n（目標 Partition）", 1200),
]
bw,bh=200,55

for name,cx in PARTS:
    x=cx-bw//2
    dwg.add(dwg.rect((x,30),(bw,bh),rx=8,fill=BOX_FILL,stroke=BOX_STROKE,stroke_width=1.5))
    lines=name.split("\n")
    for i,line in enumerate(lines):
        cy=51+i*20 if len(lines)==2 else 57
        dwg.add(dwg.text(line,insert=(cx,cy),text_anchor="middle",
                         font_family=FONT,font_size=13,font_weight="600",fill=TEXT_PRIMARY))
    dwg.add(dwg.line((cx,85),(cx,600),stroke="#d1d5db",stroke_width=1.5,stroke_dasharray="6,4"))

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

px,tcx,bkx=220,680,1200
y=120; msg(px,tcx,y,"InitProducerId（取得 PID 與 Epoch）")
y=155; msg(tcx,px,y,"ProducerId, ProducerEpoch",True)
y=200; msg(px,tcx,y,"BeginTransaction（本地狀態變更）")
y=235; msg(px,tcx,y,"AddPartitionsToTxn（登記參與 Partition）")
y=265; msg(tcx,px,y,"OK",True)
y=305; msg(px,bkx,y,"ProduceRequest（帶 PID + Epoch + Sequence）")
y=340; msg(bkx,px,y,"ProduceResponse",True)
y=385; msg(px,tcx,y,"EndTransaction（Commit 或 Abort）")
y=420; msg(tcx,bkx,y,"WriteTxnMarkers（寫入 COMMIT/ABORT 標記）")
y=455; msg(tcx,px,y,"TransactionComplete",True)

dwg.save()
print("Done")
