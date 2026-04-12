#!/usr/bin/env python3
"""Generate all 15 Kafka diagrams - Notion Clean Style 4"""
import os, math

OUT = "docs-site/public/diagrams/kafka"
os.makedirs(OUT, exist_ok=True)

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"; BOX_FILL = "#f9fafb"; BOX_STROKE = "#e5e7eb"
CON_FILL = "#f0f4ff"; CON_STROKE = "#c7d2fe"
ARROW = "#3b82f6"; TP = "#111827"; TS = "#6b7280"
NOTE_FILL = "#fef9c3"; NOTE_STROKE = "#fde047"

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def svg_hdr(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">\n'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>\n'
            f'<defs>\n'
            f'<marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
            f'<polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/></marker>\n'
            f'</defs>\n')

def svg_end(): return '</svg>\n'

def R(x, y, w, h, fi=BOX_FILL, st=BOX_STROKE, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fi}" stroke="{st}" stroke-width="1.5"/>\n')

def T(x, y, t, sz=13, fi=TP, an='middle', bold=False):
    fw = 'bold' if bold else 'normal'
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{sz}" '
            f'fill="{fi}" text-anchor="{an}" font-weight="{fw}" '
            f'xml:space="preserve">{esc(t)}</text>\n')

def nd(x, y, w, h, lines, fi=BOX_FILL, st=BOX_STROKE, rx=8, fz=13):
    """Node box with centered multi-line text."""
    s = R(x, y, w, h, fi, st, rx)
    if isinstance(lines, str):
        lines = [l.strip() for l in lines.split('<br/>')]
    lh = fz + 5
    tot = len(lines) * lh - 5
    sy = y + h / 2 - tot / 2 + fz - 1
    for i, ln in enumerate(lines):
        s += T(x + w / 2, sy + i * lh, ln, fz)
    return s

def cb(x, y, w, h, title, fz=12):
    """Container box (subgraph)."""
    return R(x, y, w, h, CON_FILL, CON_STROKE, 10) + T(x + w / 2, y + 18, title, fz, TS)

def la(x1, y1, x2, y2, lbl='', ls='above', dash=False, lsz=11):
    """Line arrow."""
    dk = ' stroke-dasharray="6,4"' if dash else ''
    s = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" '
         f'stroke-width="1.5"{dk} marker-end="url(#arrow)"/>\n')
    if lbl:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        a = math.atan2(y2 - y1, x2 - x1)
        d = 14
        if ls == 'above':
            ox, oy = -math.sin(a) * d, math.cos(a) * d
        else:
            ox, oy = math.sin(a) * d, -math.cos(a) * d
        s += T(mx + ox, my + oy, lbl, lsz, TS)
    return s

def pa(d, lbl='', lx=0, ly=0, dash=False, lsz=11):
    """Path arrow."""
    dk = ' stroke-dasharray="6,4"' if dash else ''
    s = (f'<path d="{d}" stroke="{ARROW}" stroke-width="1.5" '
         f'fill="none"{dk} marker-end="url(#arrow)"/>\n')
    if lbl:
        s += T(lx, ly, lbl, lsz, TS)
    return s

def save(name, svg):
    path = f"{OUT}/{name}.svg"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"  Written: {path}")


# ── Sequence diagram helper ───────────────────────────────────────────────────

def seq(participants, events, width=1200):
    """
    participants: list of (id, label)  label may contain <br/>
    events: list of dicts
      {'t':'msg', 'f':id, 'to':id, 'l':label, 'dash':False}
      {'t':'note', 'over':id_or_list, 'l':label}
      {'t':'loop', 'l':label}
      {'t':'loop_end'}
    """
    n = len(participants)
    margin = 90
    spacing = (width - 2 * margin) / max(n - 1, 1) if n > 1 else 0
    px = {p[0]: int(margin + i * spacing) for i, p in enumerate(participants)}

    BW, BH = 180, 50
    # draw participants
    parts = ''
    for pid, plabel in participants:
        x = px[pid]
        lines = [l.strip() for l in plabel.split('<br/>')]
        parts += nd(x - BW // 2, 20, BW, BH, lines, fz=12)

    msgs = []
    y = 20 + BH + 20

    for ev in events:
        if ev['t'] == 'msg':
            x1, x2 = px[ev['f']], px[ev['to']]
            lbl = ev.get('l', '')
            dash = ev.get('dash', False)
            dk = ' stroke-dasharray="6,4"' if dash else ''
            if x1 != x2:
                mx = (x1 + x2) / 2
                arrow_svg = (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
                             f'stroke="{ARROW}" stroke-width="1.5"{dk} marker-end="url(#arrow)"/>\n')
                if lbl:
                    arrow_svg += T(mx, y - 6, lbl, 11, TS)
            else:
                # self-arrow
                sx = x1 + 60
                arrow_svg = (f'<path d="M {x1} {y} C {sx} {y} {sx} {y+30} {x1} {y+30}" '
                             f'stroke="{ARROW}" stroke-width="1.5"{dk} fill="none" marker-end="url(#arrow)"/>\n')
                if lbl:
                    arrow_svg += T(x1 + 80, y + 15, lbl, 11, TS, an='start')
                y += 30
            msgs.append(arrow_svg)
            y += 50

        elif ev['t'] == 'note':
            over = ev.get('over', participants[0][0])
            if isinstance(over, list):
                xs = [px[o] for o in over]
                cx = sum(xs) / len(xs)
            else:
                cx = px[over]
            lbl = ev['l']
            lines = lbl.split('\n')
            nw = max(220, max(len(l) * 9 for l in lines) + 40)
            nh = len(lines) * 20 + 16
            nx = cx - nw / 2
            note_svg = R(nx, y, nw, nh, NOTE_FILL, NOTE_STROKE, 6)
            for i, ln in enumerate(lines):
                note_svg += T(cx, y + 14 + i * 20, ln, 11, TP)
            msgs.append(note_svg)
            y += nh + 10

        elif ev['t'] == 'loop':
            lbl = ev.get('l', 'loop')
            loop_svg = (R(10, y, width - 20, 22, CON_FILL, CON_STROKE, 4) +
                        T(30, y + 15, f'loop  {lbl}', 11, TS, an='start'))
            msgs.append(loop_svg)
            y += 28

        elif ev['t'] == 'loop_end':
            loop_svg = (f'<line x1="10" y1="{y}" x2="{width-10}" y2="{y}" '
                        f'stroke="{CON_STROKE}" stroke-width="1.5"/>\n')
            msgs.append(loop_svg)
            y += 20

    height = y + 30

    # lifelines
    lifelines = ''
    for pid, _ in participants:
        x = px[pid]
        lifelines += (f'<line x1="{x}" y1="{20+BH}" x2="{x}" y2="{height}" '
                      f'stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="5,4"/>\n')

    s = svg_hdr(width, height)
    s += lifelines
    s += parts
    for m in msgs:
        s += m
    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D1: kafka-kraft-topology
# ─────────────────────────────────────────────────────────────────────────────
def kafka_kraft_topology():
    W, H = 1500, 600
    s = svg_hdr(W, H)

    # Clients (left column)
    s += cb(30, 140, 220, 310, '用戶端')
    s += nd(50, 175, 180, 55, 'Producer')
    s += nd(50, 255, 180, 55, 'Consumer')
    s += nd(50, 335, 180, 55, 'AdminClient')
    # client centers
    Pcx, Pcy = 140, 202
    Ccx, Ccy = 140, 282
    Acx, Acy = 140, 362

    # Controller Quorum (top-right)
    s += cb(320, 30, 1150, 220, 'Controller Quorum（Raft）')
    CW, CH = 220, 75
    c1x, c2x, c3x = 360, 710, 1060
    cY = 95
    s += nd(c1x, cY, CW, CH, ['Controller 1', 'Active Leader'])
    s += nd(c2x, cY, CW, CH, ['Controller 2', 'Voter'])
    s += nd(c3x, cY, CW, CH, ['Controller 3', 'Voter'])
    C1cx, C2cx, C3cx = c1x + CW/2, c2x + CW/2, c3x + CW/2
    cCY = cY + CH/2  # 132

    # C1 <-> C2 bidir
    s += la(c1x + CW, cCY - 7, c2x, cCY - 7, 'Raft 選舉 / Log 複製', 'above')
    s += la(c2x, cCY + 7, c1x + CW, cCY + 7)
    # C2 <-> C3 bidir
    s += la(c2x + CW, cCY - 7, c3x, cCY - 7)
    s += la(c3x, cCY + 7, c2x + CW, cCY + 7)
    # C1 <-> C3 arc (above)
    mid = (C1cx + C3cx) / 2
    s += pa(f'M {C1cx} {cY} Q {mid} {cY-50} {C3cx} {cY}')
    s += pa(f'M {C3cx} {cY+CH} Q {mid} {cY+CH+50} {C1cx} {cY+CH}')

    # Broker Cluster
    s += cb(320, 310, 1150, 190, 'Broker 叢集')
    BW, BH = 200, 65
    b1x, b2x, b3x = 360, 710, 1060
    bY = 360
    s += nd(b1x, bY, BW, BH, 'Broker 1')
    s += nd(b2x, bY, BW, BH, 'Broker 2')
    s += nd(b3x, bY, BW, BH, 'Broker 3')
    B1cx, B2cx, B3cx = b1x + BW/2, b2x + BW/2, b3x + BW/2
    bCY = bY + BH/2  # 392

    # C1 -> B1, B2, B3
    s += la(C1cx, cY + CH, B1cx, bY, 'MetadataUpdate (Fetch)', 'above')
    s += la(C1cx + 5, cY + CH, B2cx, bY)
    s += la(C1cx + 10, cY + CH, B3cx, bY)

    # Clients -> Brokers/Controllers
    s += la(230, Pcy, b1x, bCY, 'Produce', 'above')
    s += la(230, Ccy, B2cx, bY + BH, 'Fetch', 'above')
    s += la(230, Acy, c1x, cY + CH/2, 'Admin API', 'above')
    s += la(230, Acy + 8, b1x, bCY, 'Admin API', 'below')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D2: kafka-request-flow
# ─────────────────────────────────────────────────────────────────────────────
def kafka_request_flow():
    W, H = 1900, 560
    s = svg_hdr(W, H)

    # Main flow row
    NH, NW = 80, 195
    y0 = 220

    s += nd(30, y0, NW + 5, NH, ['網路層', 'Selector / KafkaChannel'])
    s += nd(295, y0, NW + 15, NH, ['RequestQueue', 'ArrayBlockingQueue'])
    s += nd(580, y0, NW + 30, NH, ['KafkaRequestHandlerPool', 'N 個執行緒'])
    s += nd(885, y0, 160, NH, ['KafkaApis', '請求分派'])

    # arrows main flow
    s += la(235, y0 + NH/2, 295, y0 + NH/2, '請求入隊')
    s += la(310 + NW, y0 + NH/2, 580, y0 + NH/2, '分配給 Handler')
    s += la(610 + NW, y0 + NH/2, 885, y0 + NH/2)

    # Branch targets (right side)
    RX = 1120
    s += nd(RX, 80,  200, 70, 'ReplicaManager')
    s += nd(RX, 240, 200, 70, 'GroupCoordinator')
    s += nd(RX, 390, 200, 70, 'AdminManager')

    # KApis branches
    KAcx = 885 + 80  # 965
    s += la(KAcx, y0 + 10, RX, 80 + 35, 'ProduceRequest / FetchRequest', 'above')
    s += la(KAcx, y0 + NH/2, RX, 240 + 35, 'OffsetFetch / JoinGroup', 'above')
    s += la(KAcx, y0 + 65, RX, 390 + 35, 'CreateTopics', 'below')

    # Further right
    s += nd(1395, 80,  180, 70, ['LogManager', '本地 Log 管理'])
    s += nd(1395, 220, 220, 70, ['其他 Broker', 'Follower'])
    s += nd(1650, 80,  200, 70, ['磁碟', 'Log Segments'])

    s += la(1320, 115, 1395, 115, '')
    s += la(1320, 185, 1575, 255, '副本複製 (Fetch)', 'above')
    s += la(1575, 115, 1650, 115, '')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D3: kafka-log-compaction
# ─────────────────────────────────────────────────────────────────────────────
def kafka_log_compaction():
    W, H = 1350, 280
    s = svg_hdr(W, H)

    NW, NH = 100, 55
    gap = 20

    # Before container
    bef_w = 5 * NW + 4 * gap + 60
    s += cb(30, 30, bef_w, 170, 'Compaction 前')
    bef_labels = ['k=A, v=1', 'k=B, v=2', 'k=A, v=3', 'k=C, v=4', 'k=B, v=5']
    for i, lbl in enumerate(bef_labels):
        x = 60 + i * (NW + gap)
        s += nd(x, 90, NW, NH, lbl, fz=12)
        if i > 0:
            s += la(60 + (i-1) * (NW + gap) + NW, 90 + NH/2,
                    60 + i * (NW + gap), 90 + NH/2)

    bef_right = 30 + bef_w

    # After container
    aft_start = bef_right + 80
    aft_w = 3 * NW + 2 * gap + 60
    s += cb(aft_start, 30, aft_w, 170, 'Compaction 後')
    aft_labels = ['k=A, v=3', 'k=C, v=4', 'k=B, v=5']
    for i, lbl in enumerate(aft_labels):
        x = aft_start + 30 + i * (NW + gap)
        s += nd(x, 90, NW, NH, lbl, fz=12)
        if i > 0:
            s += la(aft_start + 30 + (i-1) * (NW + gap) + NW, 90 + NH/2,
                    aft_start + 30 + i * (NW + gap), 90 + NH/2)

    # Before -> After
    s += la(bef_right, 115, aft_start, 115, 'Compaction')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D4: kafka-isr  (sequenceDiagram)
# ─────────────────────────────────────────────────────────────────────────────
def kafka_isr():
    participants = [
        ('producer', 'Producer'),
        ('leader', 'Partition Leader<br/>(Broker 1)'),
        ('f1', 'Follower<br/>(Broker 2)'),
        ('f2', 'Follower<br/>(Broker 3)'),
    ]
    events = [
        {'t':'msg','f':'producer','to':'leader','l':'ProduceRequest (acks=-1)'},
        {'t':'msg','f':'leader','to':'leader','l':'寫入本地 Log'},
        {'t':'msg','f':'f1','to':'leader','l':'FetchRequest (Follower 複製)'},
        {'t':'msg','f':'leader','to':'f1','l':'FetchResponse (新訊息)','dash':True},
        {'t':'msg','f':'f1','to':'f1','l':'寫入本地 Log'},
        {'t':'msg','f':'f2','to':'leader','l':'FetchRequest'},
        {'t':'msg','f':'leader','to':'f2','l':'FetchResponse','dash':True},
        {'t':'msg','f':'f2','to':'f2','l':'寫入本地 Log'},
        {'t':'note','over':'leader','l':'所有 ISR 成員確認後\n更新 High Watermark'},
        {'t':'msg','f':'leader','to':'producer','l':'ProduceResponse (offset)','dash':True},
    ]
    return seq(participants, events, width=1300)


# ─────────────────────────────────────────────────────────────────────────────
# D5: kafka-producer-flow
# ─────────────────────────────────────────────────────────────────────────────
def kafka_producer_flow():
    W, H = 1900, 360
    s = svg_hdr(W, H)

    NW, NH = 185, 70
    y0 = 145

    nodes = [
        (30,   ['應用程式', 'producer.send(record)']),
        (265,  ['ProducerInterceptors', '前置處理']),
        (500,  ['Key/Value Serializer', '序列化']),
        (735,  ['Partitioner', '決定目標 Partition']),
        (970,  ['RecordAccumulator', '批次緩衝']),
        (1205, ['Sender 執行緒', '後台發送']),
        (1450, ['Broker Leader']),
    ]
    for x, lines in nodes:
        s += nd(x, y0, NW, NH, lines)

    labels = [
        '', '', '',
        '',
        'batch.size 或 linger.ms',
        'ProduceRequest',
        '',
    ]
    for i in range(len(nodes) - 1):
        x1 = nodes[i][0] + NW
        x2 = nodes[i+1][0]
        lbl = labels[i+1]
        s += la(x1, y0 + NH/2, x2, y0 + NH/2, lbl, 'above')

    # Broker -> Sender (ProduceResponse)
    s += la(1450 + NW/2, y0 + NH,
            1205 + NW/2, y0 + NH,
            'ProduceResponse', 'below', dash=True)
    # Sender -> App (Callback)
    bx = 1205 + NW/2
    ax = 30 + NW/2
    s += pa(f'M {bx} {y0+NH+40} Q {(bx+ax)/2} {y0+NH+80} {ax} {y0+NH+40}',
            'Callback', (bx + ax) / 2, y0 + NH + 95)

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D6: kafka-consumer-group (sequenceDiagram)
# ─────────────────────────────────────────────────────────────────────────────
def kafka_consumer_group():
    participants = [
        ('c1', 'Consumer 1'),
        ('c2', 'Consumer 2'),
        ('gc', 'Group Coordinator<br/>(Broker)'),
    ]
    events = [
        {'t':'msg','f':'c1','to':'gc','l':'FindCoordinator（按 group.id Hash 找 Coordinator Broker）'},
        {'t':'msg','f':'gc','to':'c1','l':'Coordinator 位址','dash':True},
        {'t':'msg','f':'c1','to':'gc','l':'JoinGroup（第一個加入者成為 Leader）'},
        {'t':'msg','f':'c2','to':'gc','l':'JoinGroup'},
        {'t':'msg','f':'gc','to':'c1','l':'JoinGroupResponse（包含所有成員資訊，指定 C1 為 Leader）','dash':True},
        {'t':'msg','f':'gc','to':'c2','l':'JoinGroupResponse（等待 Leader 分配）','dash':True},
        {'t':'note','over':'c1','l':'C1 執行 Partition 分配演算法'},
        {'t':'msg','f':'c1','to':'gc','l':'SyncGroup（提交分配方案）'},
        {'t':'msg','f':'c2','to':'gc','l':'SyncGroup'},
        {'t':'msg','f':'gc','to':'c1','l':'SyncGroupResponse（C1 的 Partition 分配）','dash':True},
        {'t':'msg','f':'gc','to':'c2','l':'SyncGroupResponse（C2 的 Partition 分配）','dash':True},
        {'t':'loop','l':'Heartbeat'},
        {'t':'msg','f':'c1','to':'gc','l':'Heartbeat（session.timeout.ms 內）'},
        {'t':'msg','f':'c2','to':'gc','l':'Heartbeat'},
        {'t':'loop_end'},
    ]
    return seq(participants, events, width=1200)


# ─────────────────────────────────────────────────────────────────────────────
# D7: kafka-offset-commit (sequenceDiagram)
# ─────────────────────────────────────────────────────────────────────────────
def kafka_offset_commit():
    participants = [
        ('consumer', 'Consumer'),
        ('broker', 'Broker<br/>(Group Coordinator)'),
    ]
    events = [
        {'t':'msg','f':'consumer','to':'broker','l':'FetchRequest（從 lastCommittedOffset 開始消費）'},
        {'t':'msg','f':'broker','to':'consumer','l':'FetchResponse（批次訊息）','dash':True},
        {'t':'note','over':'consumer','l':'處理訊息'},
        {'t':'msg','f':'consumer','to':'broker','l':'OffsetCommitRequest（提交 currentOffset + 1）'},
        {'t':'msg','f':'broker','to':'consumer','l':'OffsetCommitResponse','dash':True},
    ]
    return seq(participants, events, width=900)


# ─────────────────────────────────────────────────────────────────────────────
# D8: kafka-transaction (sequenceDiagram)
# ─────────────────────────────────────────────────────────────────────────────
def kafka_transaction():
    participants = [
        ('producer', 'Transactional Producer'),
        ('tc',       'Transaction Coordinator'),
        ('broker',   'Broker（目標 Partition）'),
    ]
    events = [
        {'t':'msg','f':'producer','to':'tc','l':'InitProducerId（取得 PID 與 Epoch）'},
        {'t':'msg','f':'tc','to':'producer','l':'ProducerId, ProducerEpoch','dash':True},
        {'t':'msg','f':'producer','to':'tc','l':'BeginTransaction（本地狀態變更）'},
        {'t':'msg','f':'producer','to':'tc','l':'AddPartitionsToTxn（登記參與 Partition）'},
        {'t':'msg','f':'tc','to':'producer','l':'OK','dash':True},
        {'t':'msg','f':'producer','to':'broker','l':'ProduceRequest（帶 PID + Epoch + Sequence）'},
        {'t':'msg','f':'broker','to':'producer','l':'ProduceResponse','dash':True},
        {'t':'msg','f':'producer','to':'tc','l':'EndTransaction（Commit 或 Abort）'},
        {'t':'msg','f':'tc','to':'broker','l':'WriteTxnMarkers（寫入 COMMIT/ABORT 標記）'},
        {'t':'msg','f':'tc','to':'producer','l':'TransactionComplete','dash':True},
    ]
    return seq(participants, events, width=1200)


# ─────────────────────────────────────────────────────────────────────────────
# D9: kafka-overview
# ─────────────────────────────────────────────────────────────────────────────
def kafka_overview():
    W, H = 1600, 820
    s = svg_hdr(W, H)

    # Producers (top-left)
    s += cb(30, 30, 260, 160, '生產者應用程式')
    s += nd(60, 70, 200, 55, 'Producer App 1')
    s += nd(60, 145, 200, 55, 'Producer App 2')

    # Kafka Cluster (center)
    s += cb(340, 30, 900, 540, 'Kafka 叢集 (KRaft 模式)')

    # Controllers (inner container)
    s += cb(365, 65, 850, 170, 'Controller Quorum (Raft)')
    s += nd(390, 105, 230, 60, ['Controller 1', 'Active'])
    s += nd(680, 105, 230, 60, ['Controller 2', 'Standby'])
    s += nd(970, 105, 230, 60, ['Controller 3', 'Standby'])

    # Brokers (inner container)
    s += cb(365, 280, 850, 260, 'Broker 節點')
    s += nd(390, 320, 230, 75, ['Broker 1', 'Leader Partitions'])
    s += nd(680, 320, 230, 75, ['Broker 2', 'Follower Partitions'])
    s += nd(970, 320, 230, 75, ['Broker 3', 'Follower Partitions'])

    # Controller -> Broker metadata
    s += la(840, 235, 840, 280, 'Metadata Replication', 'above')

    # Consumers (top-right)
    s += cb(1290, 30, 280, 160, '消費者應用程式')
    s += nd(1310, 70, 240, 55, 'Consumer Group A')
    s += nd(1310, 145, 240, 55, 'Consumer Group B')

    # Connect (bottom-left)
    s += cb(30, 620, 260, 170, 'Kafka Connect')
    s += nd(55, 660, 210, 55, 'Source Connector')
    s += nd(55, 735, 210, 55, 'Sink Connector')

    # Streams (bottom-right)
    s += cb(1290, 620, 280, 170, 'Kafka Streams')
    s += nd(1310, 680, 240, 60, 'Streams Application')

    # Broker centers
    B1cx = 390 + 115  # 505
    B2cx = 680 + 115  # 795
    B3cx = 970 + 115  # 1085
    bTop = 320
    bBot = 320 + 75

    # Producers -> Brokers
    s += la(290, 97, B1cx, bTop, 'Produce', 'above')
    s += la(290, 172, B2cx, bTop, 'Produce', 'above')

    # Brokers -> Consumers
    s += la(1240, 357, 1310, 97, 'Consume', 'above')
    s += la(1240, 395, 1310, 172, 'Consume', 'above')

    # Source Connector -> Broker
    s += la(265, 687, B1cx, bBot, 'Produce', 'above')

    # Broker -> Sink Connector
    s += la(B3cx, bBot, 265, 762, 'Consume', 'above')

    # Streams <-> Brokers
    s += la(1290, 715, 1240, 395, 'Read/Write')
    s += la(1240, 357, 1290, 715, 'Produce Results', 'below')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D10: kafka-mm2
# ─────────────────────────────────────────────────────────────────────────────
def kafka_mm2():
    W, H = 1500, 420
    s = svg_hdr(W, H)

    # Source cluster
    s += cb(30, 100, 230, 180, 'Source 叢集')
    s += nd(55, 165, 180, 55, ['Broker', '(Source)'])
    SBcx, SBcy = 145, 192

    # MM2 worker
    s += cb(330, 30, 600, 360, 'MirrorMaker 2 Worker')
    MW, MH = 480, 65
    mx = 390
    s += nd(mx, 90,  MW, MH, ['MirrorSourceConnector', '複製 Topic 資料'])
    s += nd(mx, 190, MW, MH, ['MirrorCheckpointConnector', '複製 Consumer 位移'])
    s += nd(mx, 290, MW, MH, ['MirrorHeartbeatConnector', '心跳監控'])
    MS_cx = mx + MW/2  # 630
    MC_cx = MS_cx
    MH_cx = MS_cx
    MS_cy = 90 + MH/2   # 122
    MC_cy = 190 + MH/2  # 222
    MH_cy = 290 + MH/2  # 322

    # Target cluster
    s += cb(1000, 100, 230, 180, 'Target 叢集')
    s += nd(1025, 165, 180, 55, ['Broker', '(Target)'])
    TBcx, TBcy = 1115, 192

    # Arrows
    s += la(235, SBcy - 10, mx, MS_cy, '消費', 'above')
    s += la(mx + MW, MS_cy, 1025, TBcy - 15, '生產', 'above')
    s += la(235, SBcy + 10, mx, MC_cy, '讀取 Offset', 'below')
    s += la(mx + MW, MC_cy, 1025, TBcy, '寫入轉換後 Offset', 'below')
    s += la(mx + MW, MH_cy, 1025, TBcy + 15, '心跳', 'below')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D11: kafka-schema-registry
# ─────────────────────────────────────────────────────────────────────────────
def kafka_schema_registry():
    W, H = 1400, 360
    s = svg_hdr(W, H)

    NW, NH = 160, 60
    # Nodes
    s += nd(30, 150, NW, NH, 'Producer')
    s += nd(700, 30, NW + 60, NH, 'Schema Registry')
    s += nd(700, 150, NW, NH, 'Kafka')
    s += nd(1200, 150, NW, NH, 'Consumer')

    PcX, PcY = 30 + NW/2, 180
    SRcX, SRcY = 700 + (NW+60)/2, 60
    KcX, KcY = 700 + NW/2, 180
    CcX, CcY = 1200 + NW/2, 180

    # 1. Producer -> SR
    s += la(PcX, 150, SRcX, 30 + NH, '1. 向 Schema Registry 登記 Schema', 'above')
    # 2. SR -> Producer
    s += la(SRcX - 20, 30 + NH, PcX - 10, 150, '2. 回傳 Schema ID', 'above', dash=True)
    # 3. Producer -> Kafka
    s += la(30 + NW, PcY, 700, KcY, '3. 發送: [Magic Byte][Schema ID][Avro Payload]', 'above')
    # 4. Consumer -> Kafka (consume)
    s += la(1200, CcY, 700 + NW, KcY, '4. 消費訊息', 'above')
    # 5. Consumer -> SR
    s += la(CcX, 150, SRcX + 20, 30 + NH, '5. 從 Schema Registry 取得 Schema', 'above')
    # 6. SR -> Consumer
    s += la(SRcX + 40, 30 + NH, CcX + 10, 150, '6. 回傳 Schema', 'above', dash=True)
    # 7. Consumer self (deserialize)
    arrow_svg = (f'<path d="M {CcX+NW/2-10} {CcY+NH/2} C {CcX+NW/2+50} {CcY+NH/2} '
                 f'{CcX+NW/2+50} {CcY+NH/2+40} {CcX+NW/2-10} {CcY+NH/2+40}" '
                 f'stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>\n')
    s += arrow_svg
    s += T(CcX + NW/2 + 90, CcY + NH/2 + 25, '7. 使用 Schema 反序列化', 11, TS, an='start')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D12: kafka-logmanager
# ─────────────────────────────────────────────────────────────────────────────
def kafka_logmanager():
    W, H = 1300, 560
    s = svg_hdr(W, H)

    # LogManager (top center)
    LMW, LMH = 180, 60
    LMx, LMy = W//2 - LMW//2, 30
    s += nd(LMx, LMy, LMW, LMH, 'LogManager')
    LMcx = LMx + LMW/2
    LMcy = LMy + LMH

    # UnifiedLog boxes
    UW, UH = 175, 60
    ux = [80, 480, 880]
    uY = 170
    ul_labels = ['UnifiedLog<br/>(topic-0)', 'UnifiedLog<br/>(topic-1)', 'UnifiedLog<br/>(topic-N)']
    for i, (x, lbl) in enumerate(zip(ux, ul_labels)):
        s += nd(x, uY, UW, UH, lbl)
        s += la(LMcx, LMcy, x + UW/2, uY, '管理 N 個', 'above')

    # LogSegments under each UnifiedLog
    segW, segH = 155, 55
    for i, ux_i in enumerate(ux):
        ucx = ux_i + UW/2
        seg_ys = [310, 385, 460]
        seg_labels = [
            ['LogSegment 1', '.log + .index'],
            ['LogSegment 2', '.log + .index'],
            ['LogSegment N（Active）', '寫入中'],
        ]
        for j, (sy, slbl) in enumerate(zip(seg_ys, seg_labels)):
            sx = ux_i + (UW - segW) // 2
            s += nd(sx, sy, segW, segH, slbl, fz=11)
            if j == 0:
                s += la(ucx, uY + UH, ucx, sy, '')
            else:
                s += la(ucx, seg_ys[j-1] + segH, ucx, sy, '')

    # LogCleaner and LogRetention
    s += nd(100, 460, 180, 60, ['LogCleaner', 'Compaction 後台'])
    s += nd(970, 460, 200, 60, ['LogRetention', '過期刪除後台'])
    s += la(LMcx, LMcy, 190, 460, 'LogCleaner', 'above')
    s += la(LMcx, LMcy, 1070, 460, 'LogRetention', 'above')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D13: kafka-streams-arch
# ─────────────────────────────────────────────────────────────────────────────
def kafka_streams_arch():
    W, H = 1100, 580
    s = svg_hdr(W, H)

    NW, NH = 280, 60
    cx = W // 2

    def bx(w=NW): return cx - w // 2

    # KafkaStreams
    s += nd(bx(), 30, NW, NH, ['KafkaStreams', '串流應用主程序'])
    s += la(cx, 30 + NH, cx, 160, '')

    # StreamThread[]
    s += nd(bx(), 160, NW, NH, ['StreamThread[]', 'N 個執行緒'])
    s += la(cx, 160 + NH, cx, 290, '')

    # TaskManager
    s += nd(bx(), 290, NW, NH, ['TaskManager', '管理 Active/Standby Task'])

    # StreamTask and StandbyTask
    TW = 220
    s += nd(cx - TW - 30, 420, TW, NH, ['StreamTask', 'Active：處理並生產'])
    s += nd(cx + 30, 420, TW, NH, ['StandbyTask', '備援：維護狀態副本'])
    s += la(cx - 10, 290 + NH, cx - TW/2 - 30, 420, 'Active', 'above')
    s += la(cx + 10, 290 + NH, cx + 30 + TW/2, 420, 'Standby', 'above')

    # ProcessorChain and StateStore under StreamTask
    ST_cx = cx - TW/2 - 30
    s += nd(ST_cx - TW/2, 510, TW, 50, ['ProcessorChain', 'ProcessorNode 鏈'], fz=12)
    s += la(ST_cx, 420 + NH, ST_cx, 510, '')

    # RecordCollector
    s += nd(cx + 30 + TW/2 - TW/2, 510, TW, 50, ['RecordCollector', '輸出至 Kafka'], fz=12)
    s += la(cx + 30 + TW/2, 420 + NH, cx + 30 + TW/2, 510, '')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D14: kafka-connect-modules
# ─────────────────────────────────────────────────────────────────────────────
def kafka_connect_modules():
    W, H = 1300, 520
    s = svg_hdr(W, H)

    NW, NH = 280, 55
    API_cx = W // 2

    # API at top
    s += nd(API_cx - NW//2, 30, NW, NH, ['connect/api', 'Connector/Task/Transform 介面'])
    APIcy = 30 + NH

    # Children
    children = [
        'connect/runtime\n(Worker 執行環境)',
        'connect/transforms\n(內建 SMT)',
        'connect/json\n(JSON Converter)',
        'connect/file\n(FileStream Connector)',
        'connect/mirror\n(MirrorMaker 2)',
    ]
    n = len(children)
    total_w = n * NW + (n - 1) * 30
    start_x = (W - total_w) // 2
    for i, lbl in enumerate(children):
        x = start_x + i * (NW + 30)
        lines = lbl.split('\n')
        s += nd(x, 200, NW, NH + 10, lines, fz=12)
        child_cx = x + NW / 2
        s += la(API_cx, APIcy, child_cx, 200, '')

    # connect/mirror-client (below mirror)
    mirror_idx = 4
    mir_x = start_x + mirror_idx * (NW + 30)
    mir_cx = mir_x + NW / 2
    s += nd(mir_x, 360, NW, NH + 10, ['connect/mirror-client', '(MirrorMaker 2 用戶端)'], fz=12)
    s += la(mir_cx, 200 + NH + 10, mir_cx, 360, '')

    # connect/basic-auth (extra note)
    s += nd(start_x - NW - 30, 200, NW + 20, NH + 10,
            ['connect/basic-auth-extension', '(HTTP Basic Auth)'], fz=12)
    s += la(API_cx, APIcy, start_x - NW - 30 + (NW+20)/2, 200, '')

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# D15: kafka-raft-state  (stateDiagram-v2)
# ─────────────────────────────────────────────────────────────────────────────
def kafka_raft_state():
    W, H = 1400, 640
    s = svg_hdr(W, H)

    SW, SH = 180, 55  # state box size

    # Positions
    states = {
        'Unattached':  (610, 60),
        'Candidate':   (610, 210),
        'Leader':      (200, 400),
        'Follower':    (1000, 400),
    }

    # Draw state boxes (rounded)
    for name, (x, y) in states.items():
        s += nd(x, y, SW, SH, name, rx=20)

    # Start circle
    start_x, start_y = 610 + SW//2, 30
    s += f'<circle cx="{start_x}" cy="{start_y}" r="10" fill="{ARROW}"/>\n'

    # Helper centers
    def cx(n): return states[n][0] + SW/2
    def cy(n): return states[n][1] + SH/2
    def tx(n): return states[n][0]
    def ty(n): return states[n][1]
    def bx(n): return states[n][0] + SW
    def by_top(n): return states[n][1]
    def by_bot(n): return states[n][1] + SH

    # [*] -> Unattached
    s += la(start_x, start_y + 10, cx('Unattached'), ty('Unattached'), '啟動')

    # Unattached -> Candidate
    s += la(cx('Unattached'), by_bot('Unattached'),
            cx('Candidate'), ty('Candidate'),
            'Election Timeout', 'above')

    # Candidate -> Leader
    s += la(tx('Candidate'), cy('Candidate'),
            bx('Leader'), cy('Leader'),
            '獲得多數票（Quorum）', 'above')

    # Candidate -> Follower
    s += la(bx('Candidate'), cy('Candidate'),
            tx('Follower'), cy('Follower'),
            '收到更高 Term 的選票或 Heartbeat', 'above')

    # Leader -> Follower
    s += la(bx('Leader'), cy('Leader') + 8,
            tx('Follower'), cy('Follower') + 8,
            '發現更高 Term', 'below')

    # Follower -> Candidate
    s += la(tx('Follower'), cy('Follower') - 8,
            bx('Candidate'), cy('Candidate') - 8,
            'Election Timeout（未收到 Heartbeat）', 'above')

    # Candidate self-loop (上方)
    ccx = cx('Candidate')
    cty = ty('Candidate')
    s += pa(f'M {bx("Candidate")} {cty+10} C {bx("Candidate")+70} {cty-20} {bx("Candidate")+70} {cty+SH+20} {bx("Candidate")} {cty+SH-10}',
            '選舉超時重試', bx('Candidate') + 120, cty + SH//2, lsz=11)

    # Leader self-loop
    lcx = cx('Leader')
    lty = ty('Leader')
    s += pa(f'M {tx("Leader")} {lty+10} C {tx("Leader")-70} {lty-20} {tx("Leader")-70} {lty+SH+20} {tx("Leader")} {lty+SH-10}',
            '持續發送 Heartbeat', tx('Leader') - 180, lty + SH//2, lsz=11)

    # Follower self-loop
    frx = bx('Follower')
    fty = ty('Follower')
    s += pa(f'M {frx} {fty+10} C {frx+70} {fty-20} {frx+70} {fty+SH+20} {frx} {fty+SH-10}',
            '接收 Heartbeat / Log 複製', frx + 80, fty + SH//2, lsz=11)

    s += svg_end()
    return s


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
diagrams = [
    ('kafka-kraft-topology',  kafka_kraft_topology),
    ('kafka-request-flow',    kafka_request_flow),
    ('kafka-log-compaction',  kafka_log_compaction),
    ('kafka-isr',             kafka_isr),
    ('kafka-producer-flow',   kafka_producer_flow),
    ('kafka-consumer-group',  kafka_consumer_group),
    ('kafka-offset-commit',   kafka_offset_commit),
    ('kafka-transaction',     kafka_transaction),
    ('kafka-overview',        kafka_overview),
    ('kafka-mm2',             kafka_mm2),
    ('kafka-schema-registry', kafka_schema_registry),
    ('kafka-logmanager',      kafka_logmanager),
    ('kafka-streams-arch',    kafka_streams_arch),
    ('kafka-connect-modules', kafka_connect_modules),
    ('kafka-raft-state',      kafka_raft_state),
]

print("Generating SVGs...")
for name, fn in diagrams:
    save(name, fn())

print(f"\nDone! {len(diagrams)} SVGs written to {OUT}/")
