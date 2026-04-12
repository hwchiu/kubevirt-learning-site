import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"

W, H = 1800, 500
dwg = svgwrite.Drawing("docs-site/public/diagrams/kafka/kafka-architecture-2.svg",
                        size=(W, H), profile='full', debug=False)
dwg.add(dwg.rect((0,0),(W,H), fill=BG))

marker = dwg.marker(insert=(10,5), size=(10,10), orient="auto", id="arr")
marker.add(dwg.path("M0,0 L10,5 L0,10 Z", fill=ARROW))
dwg.defs.add(marker)

def box(x, y, w, h, line1, line2=None):
    dwg.add(dwg.rect((x,y),(w,h), rx=8, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    cy = y+h/2+(-8 if line2 else 0)
    dwg.add(dwg.text(line1, insert=(x+w/2, cy), text_anchor="middle",
                     dominant_baseline="middle", font_family=FONT, font_size=13,
                     font_weight="600", fill=TEXT_PRIMARY))
    if line2:
        dwg.add(dwg.text(line2, insert=(x+w/2, cy+20), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

def arr(x1,y1,x2,y2,label=None):
    dwg.add(dwg.line((x1,y1),(x2,y2), stroke=ARROW, stroke_width=1.5, marker_end="url(#arr)"))
    if label:
        mx,my=(x1+x2)/2,(y1+y2)/2
        tw=len(label)*6.5+16
        dwg.add(dwg.rect((mx-tw/2,my-11),(tw,18),rx=3,fill="#ffffff",opacity=0.9))
        dwg.add(dwg.text(label,insert=(mx,my+1),text_anchor="middle",
                         dominant_baseline="middle",font_family=FONT,font_size=10,fill=TEXT_SECONDARY))

def varr(x,y1,y2,label=None):
    arr(x,y1,x,y2,label)

# Row 1: Network → RequestQueue → KafkaRequestHandlerPool → KafkaApis
# Row 2: KafkaApis fans out to ReplicaManager, GroupCoordinator, AdminManager
# Row 3: ReplicaManager → LogManager → Disk; ReplicaManager → OtherBroker

# Top row nodes
bw1, bh = 190, 65
y1 = 60
x_net, x_rq, x_krh, x_kapi = 60, 310, 560, 810

box(x_net, y1, 200, bh, "網路層", "(Selector / KafkaChannel)")
box(x_rq, y1, 200, bh, "RequestQueue", "(ArrayBlockingQueue)")
box(x_krh, y1, 220, bh, "KafkaRequestHandlerPool", "(N 個執行緒)")
box(x_kapi, y1, 160, bh, "KafkaApis", "(請求分派)")

# Connect top row
arr(x_net+200, y1+32, x_rq, y1+32, "請求入隊")
arr(x_rq+200, y1+32, x_krh, y1+32, "分配給 Handler")
arr(x_krh+220, y1+32, x_kapi, y1+32)

# KafkaApis fans to 3 components
y2 = 250
x_rm = 760; x_gc = 1060; x_am = 1360
box(x_rm, y2, 200, 65, "ReplicaManager")
box(x_gc, y2, 210, 65, "GroupCoordinator")
box(x_am, y2, 200, 65, "AdminManager")

kapi_cx = x_kapi + 80
kapi_by = y1 + bh
arr(kapi_cx, kapi_by, x_rm+100, y2, "ProduceRequest / FetchRequest")
arr(kapi_cx, kapi_by, x_gc+105, y2, "OffsetFetch / JoinGroup")
arr(kapi_cx, kapi_by, x_am+100, y2, "CreateTopics")

# ReplicaManager → LogManager → Disk
y3 = 420
x_lm = 760; x_disk = 1060; x_ob = 1360
box(x_lm, y3, 200, 60, "LogManager", "(本地 Log 管理)")
box(x_disk, y3, 180, 60, "磁碟", "(Log Segments)")
box(x_ob, y3, 210, 60, "其他 Broker", "(Follower)")

arr(x_rm+100, y2+65, x_lm+100, y3)
arr(x_lm+200, y3+30, x_disk, y3+30)
arr(x_rm+200, y2+30, x_ob+5, y3, "副本複製 (Fetch)")

dwg.save()
print("Done")
