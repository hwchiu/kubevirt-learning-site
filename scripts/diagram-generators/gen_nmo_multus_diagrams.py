#!/usr/bin/env python3
"""Generate all NMO + Multus Notion-Clean diagrams."""
import os, math, textwrap

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG          = "#ffffff"
BOX_FILL    = "#f9fafb"
BOX_STROKE  = "#e5e7eb"
C_FILL      = "#f0f4ff"   # container / subgraph
C_STROKE    = "#c7d2fe"
ARROW       = "#3b82f6"
TEXT_P      = "#111827"
TEXT_S      = "#6b7280"
DIA_FILL    = "#fef3c7"
DIA_STROKE  = "#fbbf24"
END_FILL    = "#dcfce7"
END_STROKE  = "#86efac"
START_FILL  = "#dbeafe"
START_STROKE= "#93c5fd"
WARN_FILL   = "#fee2e2"
WARN_STROKE = "#fca5a5"

OUT_NMO    = "docs-site/public/diagrams/node-maintenance-operator"
OUT_MULTUS = "docs-site/public/diagrams/multus-cni"
os.makedirs(OUT_NMO, exist_ok=True)
os.makedirs(OUT_MULTUS, exist_ok=True)

# ─── SVG helpers ───────────────────────────────────────────────────────────────

def esc(t):
    return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def wrap(text, max_chars=20):
    """Split on \n first, then wrap each line."""
    parts = []
    for raw in str(text).split("\\n"):
        parts.extend(textwrap.wrap(raw, max_chars) or [""])
    return parts

def tspan_lines(lines, cx, y0, dy, size, color, bold=False):
    spans = []
    for i, line in enumerate(lines):
        w = "bold" if bold else "normal"
        spans.append(
            f'<tspan x="{cx}" dy="{dy if i>0 else 0}"'
            f' font-weight="{w}" fill="{color}">{esc(line)}</tspan>'
        )
    return spans

def box_svg(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE, rx=8, fs=12, color=TEXT_P):
    lines = wrap(label, max(12, w//8))
    lh = fs + 4
    total_text = len(lines) * lh
    cy = y + h/2 - total_text/2 + lh/2
    spans = []
    for i,l in enumerate(lines):
        spans.append(f'<tspan x="{x+w/2}" dy="{lh if i>0 else 0}" fill="{color}">{esc(l)}</tspan>')
    span_str = "".join(spans)
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
        f'<text x="{x+w/2}" y="{cy}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="{fs}" dominant-baseline="middle">{span_str}</text>\n'
    )

def stadium_svg(x, y, w, h, label, fill=START_FILL, stroke=START_STROKE, fs=12):
    r = h/2
    lines = wrap(label, max(12, w//8))
    lh = fs+4; total_text=len(lines)*lh; cy = y+h/2-total_text/2+lh/2
    spans="".join(f'<tspan x="{x+w/2}" dy="{lh if i>0 else 0}" fill="{TEXT_P}">{esc(l)}</tspan>' for i,l in enumerate(lines))
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
        f'<text x="{x+w/2}" y="{cy}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="{fs}" dominant-baseline="middle">{spans}</text>\n'
    )

def diamond_svg(cx, cy, hw, hh, label, fill=DIA_FILL, stroke=DIA_STROKE, fs=11):
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    lines = wrap(label, max(10, hw//6))
    lh=fs+3; total=len(lines)*lh; ty=cy-total/2+lh/2
    spans="".join(f'<tspan x="{cx}" dy="{lh if i>0 else 0}" fill="{TEXT_P}">{esc(l)}</tspan>' for i,l in enumerate(lines))
    return (
        f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
        f'<text x="{cx}" y="{ty}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="{fs}" dominant-baseline="middle">{spans}</text>\n'
    )

def arrow_svg(x1,y1,x2,y2, label="", color=ARROW, fs=10):
    dx,dy = x2-x1, y2-y1
    if dx==0 and dy==0: return ""
    angle = math.atan2(dy,dx)
    arrowlen=10; aw=5
    ax1 = x2 - arrowlen*math.cos(angle-0.35)
    ay1 = y2 - arrowlen*math.sin(angle-0.35)
    ax2 = x2 - arrowlen*math.cos(angle+0.35)
    ay2 = y2 - arrowlen*math.sin(angle+0.35)
    mx,my = (x1+x2)/2, (y1+y2)/2
    lbl=""
    if label:
        # offset perpendicular
        px = -math.sin(angle)*14
        py =  math.cos(angle)*14
        lbl = (f'<text x="{mx+px:.1f}" y="{my+py:.1f}" text-anchor="middle" '
               f'font-family="{FONT}" font-size="{fs}" fill="{TEXT_S}">{esc(label)}</text>\n')
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="1.5" marker-end="url(#arr_{color.replace("#","")})"/>\n'
        + lbl
    )

def arrowdef(color=ARROW):
    cid = color.replace("#","")
    return (f'<marker id="arr_{cid}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>\n')

def svg_doc(w, h, body, extra_defs=""):
    defs = arrowdef(ARROW) + arrowdef("#6b7280") + extra_defs
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">\n'
            f'<defs>{defs}</defs>\n'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>\n'
            + body + '</svg>\n')

# ─── Sequence diagram helper ────────────────────────────────────────────────────

def seq_diagram(participants, messages, title="", w=900):
    """
    participants: list of (id, label)
    messages: list of dicts:
      { "from": id, "to": id, "label": str, "type": "->"|"-->"|"note" }
    """
    N = len(participants)
    left_pad = 40
    top_pad = 60 if title else 30
    col_w = (w - left_pad*2) / N
    lifeline_start = top_pad + 40
    msg_h = 42
    h = lifeline_start + len(messages)*msg_h + 60

    body = ""
    if title:
        body += f'<text x="{w//2}" y="26" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="bold" fill="{TEXT_P}">{esc(title)}</text>\n'

    cols = {}
    for i,(pid, plabel) in enumerate(participants):
        cx = left_pad + col_w*i + col_w/2
        cols[pid] = cx
        bw = min(col_w-20, 160)
        bh = 34
        body += box_svg(cx-bw/2, top_pad, bw, bh, plabel, fill=C_FILL, stroke=C_STROKE, fs=11)

    # lifelines
    lifeline_end = h - 40
    for pid,_ in participants:
        cx = cols[pid]
        body += f'<line x1="{cx}" y1="{lifeline_start+34}" x2="{cx}" y2="{lifeline_end}" stroke="{BOX_STROKE}" stroke-width="1" stroke-dasharray="4,3"/>\n'

    y = lifeline_start + 34 + 20
    for msg in messages:
        mtype = msg.get("type","->")
        if mtype == "note":
            # centered note
            body += (f'<text x="{w//2}" y="{y}" text-anchor="middle" '
                     f'font-family="{FONT}" font-size="10" fill="{TEXT_S}" '
                     f'font-style="italic">{esc(msg["label"])}</text>\n')
            y += msg_h*0.7
            continue
        if mtype == "alt_start":
            body += (f'<rect x="20" y="{y-10}" width="{w-40}" height="{msg_h*1.5}" '
                     f'rx="4" fill="none" stroke="{C_STROKE}" stroke-width="1" stroke-dasharray="4,2"/>\n'
                     f'<text x="28" y="{y+4}" font-family="{FONT}" font-size="9" fill="{TEXT_S}">{esc(msg.get("label","alt"))}</text>\n')
            y += msg_h*0.5
            continue
        if mtype == "alt_end":
            y += msg_h*0.3
            continue

        f_id = msg["from"]
        t_id = msg["to"]
        lbl  = msg.get("label","")
        x1 = cols[f_id]; x2 = cols[t_id]
        dash = "5,3" if mtype=="-->" else "none"
        # arrow line
        body += (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
                 f'stroke="{ARROW}" stroke-width="1.5" stroke-dasharray="{dash}" '
                 f'marker-end="url(#arr_{ARROW.replace("#","")})"/>\n')
        mx = (x1+x2)/2
        body += (f'<text x="{mx}" y="{y-5}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="10" fill="{TEXT_S}">{esc(lbl)}</text>\n')
        # activation box
        if mtype != "-->":
            body += f'<rect x="{x2-4}" y="{y}" width="8" height="12" fill="{START_FILL}" stroke="{START_STROKE}" stroke-width="1"/>\n'
        y += msg_h

    return svg_doc(w, h, body)

# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def nmo_architecture_1():
    """LR graph: User→CR→Controller→Node"""
    W,H = 820, 140
    BW,BH = 170,50
    nodes = [
        (50,  "👤 使用者",     BOX_FILL, BOX_STROKE),
        (270, "NodeMaintenance CR", C_FILL, C_STROKE),
        (490, "NodeMaintenanceReconciler", BOX_FILL, BOX_STROKE),
        (710, "☸ Node",       END_FILL, END_STROKE),
    ]
    labels = ["kubectl apply", "watch", "taint / cordon / drain"]
    body=""
    xs = [n[0] for n in nodes]
    y0 = (H-BH)//2
    for x,lbl,fill,stroke in nodes:
        body += box_svg(x, y0, BW, BH, lbl, fill=fill, stroke=stroke, fs=11)
    cy = y0+BH//2
    for i,(x1,_,_,_) in enumerate(nodes[:-1]):
        x2 = nodes[i+1][0]
        body += arrow_svg(x1+BW, cy, x2, cy, labels[i], fs=10)
    return svg_doc(W,H,body)

def nmo_architecture_2():
    """Flowchart TD: full reconcile flow"""
    W = 700
    # Nodes: (id, label, type, x, y)
    # type: box|diamond|stadium|warn
    BW,BH = 200,46; DW,DH = 100,36; SW,SH=150,36
    PAD=20
    nodes = {
        "A":  ("stadium", 250, 30,  270, 36, "開始 Reconcile",     START_FILL, START_STROKE),
        "B":  ("diamond", 250, 100, 110, 32, "Fetch NM CR",        DIA_FILL, DIA_STROKE),
        "Z1": ("stadium", 490, 100, 140, 36, "結束",               END_FILL, END_STROKE),
        "C":  ("box",     150, 170, 220, 46, "建立 drain.Helper",   BOX_FILL, BOX_STROKE),
        "D":  ("diamond", 150, 250, 130, 32, "Finalizer 檢查",      DIA_FILL, DIA_STROKE),
        "E":  ("box",     -10, 330, 200, 54, "新增 finalizer\n觸發 BeginMaintenance", BOX_FILL, BOX_STROKE),
        "F":  ("box",     300, 330, 200, 54, "stopMaintenance\n移除 finalizer\n觸發 RemovedMaintenance", BOX_FILL, BOX_STROKE),
        "Z2": ("stadium", 340, 420, 120, 36, "結束",               END_FILL, END_STROKE),
        "G":  ("diamond", 150, 430, 90,  30, "phase == ''",         DIA_FILL, DIA_STROKE),
        "H":  ("box",     -20, 500, 210, 46, "設 Running\n統計 TotalPods",  BOX_FILL, BOX_STROKE),
        "I":  ("box",     150, 560, 200, 46, "取得 Node",           BOX_FILL, BOX_STROKE),
        "J":  ("box",     410, 560, 200, 54, "觸發 FailedMaintenance\n設 Failed", WARN_FILL, WARN_STROKE),
        "Z3": ("stadium", 450, 640, 120, 36, "結束",               END_FILL, END_STROKE),
        "K":  ("diamond", 150, 640, 130, 32, "ErrorOnLeaseCount > 3?", DIA_FILL, DIA_STROKE),
        "L":  ("box",     -20, 710, 190, 46, "Uncordon\n設 Failed", WARN_FILL, WARN_STROKE),
        "Z4": ("stadium", -10, 790, 120, 36, "結束",               END_FILL, END_STROKE),
        "M":  ("box",     150, 720, 200, 36, "RequestLease 3600s",  C_FILL, C_STROKE),
        "N":  ("box",     150, 780, 220, 46, "Patch 標籤\nexclude-from-remediation=true", BOX_FILL, BOX_STROKE),
        "O":  ("box",     150, 850, 220, 54, "新增 Taint\nmedik8s.io/drain\nnode.kubernetes.io/unschedulable", BOX_FILL, BOX_STROKE),
        "P":  ("box",     150, 930, 220, 46, "Cordon 節點\nUnschedulable=true", BOX_FILL, BOX_STROKE),
        "Q":  ("box",     150, 1000,220, 36, "drain.RunNodeDrain",  BOX_FILL, BOX_STROKE),
        "R":  ("box",     -20, 1060,160, 36, "Requeue 5s",          WARN_FILL, WARN_STROKE),
        "S":  ("box",     330, 1060,210, 46, "設 Succeeded\nDrainProgress=100", END_FILL, END_STROKE),
        "Z5": ("stadium", 150, 1130,130, 36, "結束",               END_FILL, END_STROKE),
    }
    H = 1200
    body=""
    # draw nodes
    def node_center(nid):
        t,x,y,w,h,_,_,_ = nodes[nid]
        if t=="diamond": return (x,y)
        return (x+w/2, y+h/2)
    def node_top(nid):
        t,x,y,w,h,_,_,_= nodes[nid]
        if t=="diamond": return (x, y-h)
        return (x+w/2, y)
    def node_bot(nid):
        t,x,y,w,h,_,_,_= nodes[nid]
        if t=="diamond": return (x, y+h)
        return (x+w/2, y+h)
    def node_right(nid):
        t,x,y,w,h,_,_,_= nodes[nid]
        if t=="diamond": return (x+w, y)
        return (x+w, y+h/2)
    def node_left(nid):
        t,x,y,w,h,_,_,_= nodes[nid]
        if t=="diamond": return (x-w, y)
        return (x, y+h/2)

    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond":
            body += diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        elif t=="stadium":
            body += stadium_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=11)
        elif t=="warn":
            body += box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=11)
        else:
            body += box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=11)

    def arr(f,t,lbl="",fx="bot",tx="top"):
        getters = {"bot":node_bot,"top":node_top,"left":node_left,"right":node_right}
        x1,y1=getters[fx](f); x2,y2=getters[tx](t)
        body2=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
        return body2

    arrows=[
        ("A","B","","bot","top"),
        ("B","Z1","不存在","right","top"),
        ("B","C","存在","bot","top"),
        ("C","D","","bot","top"),
        ("D","E","無 finalizer","left","top"),
        ("D","F","DeletionTimestamp 已設","right","top"),
        ("F","Z2","","bot","top"),
        ("E","G","","bot","top"),
        ("G","H","是","left","top"),
        ("G","I","否","bot","top"),
        ("H","I","","bot","top"),
        ("I","J","Node 不存在","right","top"),
        ("J","Z3","","bot","top"),
        ("I","K","Node 存在","bot","top"),
        ("K","L","是","left","top"),
        ("L","Z4","","bot","top"),
        ("K","M","否","bot","top"),
        ("M","N","","bot","top"),
        ("N","O","","bot","top"),
        ("O","P","","bot","top"),
        ("P","Q","","bot","top"),
        ("Q","R","error","left","top"),
        ("Q","S","success","right","top"),
        ("R","Z5","","bot","top"),
        ("S","Z5","","bot","right"),
    ]
    for a in arrows:
        f,t,lbl,fx,tx=a
        body+=arr(f,t,lbl,fx,tx)

    return svg_doc(W, H, body)

def nmo_architecture_3():
    """State diagram: Running/Succeeded/Failed"""
    W,H = 680, 360
    body=""
    # States
    states = {
        "init":      (80,  180, "●",        "#374151", "#374151"),
        "Running":   (220, 100, "Running",   BOX_FILL,  BOX_STROKE),
        "Succeeded": (440, 100, "Succeeded", END_FILL,  END_STROKE),
        "Failed":    (440, 260, "Failed",    WARN_FILL,  WARN_STROKE),
        "end":       (600, 180, "◉",        "#374151", "#374151"),
    }
    BW,BH = 140,50
    for sid,(x,y,lbl,fill,stroke) in states.items():
        if sid in ("init","end"):
            body += f'<circle cx="{x}" cy="{y}" r="16" fill="{fill}" stroke="{stroke}" stroke-width="2"/>\n'
            body += f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" font-size="14" fill="white">{esc(lbl)}</text>\n'
        else:
            body += box_svg(x-BW//2, y-BH//2, BW, BH, lbl, fill=fill, stroke=stroke, fs=13)

    def cx(sid):
        x,y,_,_,_ = states[sid]; return x
    def cy(sid):
        x,y,_,_,_ = states[sid]; return y

    arrs = [
        ("init","Running","CR 建立，新增 finalizer"),
        ("Running","Running","drain 進行中，error 時 requeue 5s"),
        ("Running","Succeeded","所有 Pod 驅逐完成"),
        ("Running","Failed","Node 不存在 OR\nErrorOnLeaseCount > 3"),
        ("Succeeded","end","CR 刪除，節點 uncordon"),
        ("Failed","end","CR 刪除，嘗試 uncordon"),
    ]

    for f,t,lbl in arrs:
        x1=cx(f); y1=cy(f); x2=cx(t); y2=cy(t)
        if f==t:  # self-loop
            body += (f'<path d="M {x1+70},{y1-10} C {x1+110},{y1-60} {x1+110},{y1+20} {x1+70},{y1+10}" '
                     f'fill="none" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr_{ARROW.replace("#","")})"/>\n')
            body += f'<text x="{x1+120}" y="{y1-20}" font-family="{FONT}" font-size="10" fill="{TEXT_S}">{esc(lbl)}</text>\n'
        else:
            # adjust for box edges
            if x2 > x1: x1+=70
            elif x2 < x1: x1-=70
            if x2 > x1+5: x2-=70
            elif x2 < x1-5: x2+=70
            if y2 > y1+30: y1+=BH//2; y2-=BH//2
            elif y2 < y1-30: y1-=BH//2; y2+=BH//2
            body += arrow_svg(x1,y1,x2,y2,lbl,fs=10)
    return svg_doc(W,H,body)

def nmo_design_motivation_1():
    """Sequence: NM1/NM2 lease coordination"""
    parts = [
        ("NM1","NodeMaintenance\nnode01"),
        ("NM2","NodeMaintenance\nnode02"),
        ("Lease","Lease (etcd)"),
        ("N1","node01"),
        ("N2","node02"),
    ]
    msgs = [
        {"from":"NM1","to":"Lease","label":"嘗試取得 lease","type":"->"},
        {"from":"NM2","to":"Lease","label":"嘗試取得 lease","type":"->"},
        {"from":"Lease","to":"NM1","label":"✅ 取得成功","type":"-->"},
        {"from":"Lease","to":"NM2","label":"❌ 等待（lease 已被佔用）","type":"-->"},
        {"from":"NM1","to":"N1","label":"cordon + drain","type":"->"},
        {"from":"N1","to":"NM1","label":"排空完成","type":"-->"},
        {"from":"NM1","to":"Lease","label":"釋放 lease","type":"->"},
        {"from":"Lease","to":"NM2","label":"✅ 取得成功","type":"-->"},
        {"from":"NM2","to":"N2","label":"cordon + drain","type":"->"},
    ]
    return seq_diagram(parts, msgs, w=800)

def nmo_node_drainage_1():
    """Sequence: drain trigger flow"""
    parts = [
        ("C","Controller"),
        ("N","Node"),
        ("D","drain.RunNodeDrain"),
        ("P","Pod (Eviction API)"),
    ]
    msgs = [
        {"from":"C","to":"N","label":"加入 Taint（NoSchedule/NoExecute）","type":"->"},
        {"from":"C","to":"N","label":"Cordon（spec.unschedulable=true）","type":"->"},
        {"from":"C","to":"D","label":"呼叫 drain.RunNodeDrain(drainer, nodeName)","type":"->"},
        {"from":"D","to":"P","label":"POST /pods/{name}/eviction","type":"->"},
        {"from":"P","to":"D","label":"202 Accepted 或 429（PDB 阻擋）","type":"-->"},
        {"type":"note","label":"── 對每個需驅逐的 Pod 重複上兩步 ──"},
        {"from":"D","to":"C","label":"回傳錯誤（若超時或部分失敗）","type":"-->"},
        {"from":"C","to":"C","label":"更新 NodeMaintenance status","type":"->"},
    ]
    return seq_diagram(parts, msgs, w=900)

def nmo_taints_cordoning_1():
    """State diagram: node lifecycle Before/During/After"""
    W,H = 800, 500
    body=""
    states = [
        (100, 90,  380, 160, "正常狀態 (Before)",
         "Taints: []\nUnschedulable: false\nLabels: (無 medik8s 標記)"),
        (100, 230, 380, 160, "維護中 (During)",
         "Taints: node.kubernetes.io/unschedulable:NoSchedule\nmedik8s.io/drain:NoSchedule\nUnschedulable: true\nLabels: exclude-from-remediation=true"),
        (100, 370, 380, 100, "維護完成 (After)",
         "Taints: [] (已移除)\nUnschedulable: false\nLabels: (medik8s 標記已移除)"),
    ]
    fills = [BOX_FILL, C_FILL, END_FILL]
    strokes = [BOX_STROKE, C_STROKE, END_STROKE]
    for i,(x,y,w,h,title,detail) in enumerate(states):
        body += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fills[i]}" stroke="{strokes[i]}" stroke-width="1.5"/>\n'
        body += f'<text x="{x+w//2}" y="{y+18}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="bold" fill="{TEXT_P}">{esc(title)}</text>\n'
        dy=0
        for line in detail.split("\\n"):
            dy+=18
            body += f'<text x="{x+14}" y="{y+30+dy}" font-family="{FONT}" font-size="11" fill="{TEXT_S}">{esc(line)}</text>\n'

    tr_x = 115
    tr_labels = [
        "NodeMaintenance CR 建立\n① 加 Taint ② Cordon ③ 加 Label",
        "NodeMaintenance CR 刪除\n① 移除 Label ② 移除 Taint ③ Uncordon",
    ]
    for i in range(2):
        y1 = states[i][1]+states[i][3]
        y2 = states[i+1][1]
        mid = (y1+y2)//2
        body += arrow_svg(tr_x,y1,tr_x,y2,"",fs=10)
        lbl=tr_labels[i]
        dy=0
        for line in lbl.split("\\n"):
            body += f'<text x="{tr_x+14}" y="{mid-10+dy}" font-family="{FONT}" font-size="11" fill="{TEXT_S}">{esc(line)}</text>\n'
            dy+=15

    return svg_doc(W,H,body)

def nmo_lease_coordination_1():
    """Flowchart TD: RequestLease flow"""
    W,H = 640, 580
    BW,BH=200,44; DW,DH=110,34

    nodes={
        "A": ("stadium",320,30,  180,36, "開始 RequestLease", START_FILL, START_STROKE),
        "B": ("diamond",320,110, 120,34, "GET Lease\nnode-<nodename>", DIA_FILL, DIA_STROKE),
        "C": ("box",    100,200, 210,44, "CREATE 新 Lease\nHolderIdentity=node-maintenance\nduration=3600s", C_FILL, C_STROKE),
        "Z1":("stadium",100,270, 120,34, "成功", END_FILL, END_STROKE),
        "D": ("diamond",430,200, 120,34, "HolderIdentity\n== node-maintenance?", DIA_FILL, DIA_STROKE),
        "E": ("box",    560,280, 180,44, "UPDATE Lease\n更新 RenewTime", BOX_FILL, BOX_STROKE),
        "Z2":("stadium",580,350, 120,34, "成功", END_FILL, END_STROKE),
        "F": ("diamond",430,330, 120,34, "Lease\n是否已過期?", DIA_FILL, DIA_STROKE),
        "G": ("box",    290,420, 220,44, "return AlreadyHeldError\nholderIdentity=<current holder>", WARN_FILL, WARN_STROKE),
        "H": ("box",    430,420, 200,44, "TAKEOVER\n更新 HolderIdentity\nLeaseTransitions++", BOX_FILL, BOX_STROKE),
        "FAIL":("stadium",290,490,120,34,"失敗", WARN_FILL, WARN_STROKE),
        "Z3": ("stadium",490,490,120,34, "成功", END_FILL, END_STROKE),
    }
    body=""
    def nc(nid):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond": return (x,y)
        return (x+w/2,y+h/2)
    def nb(nid,side="bot"):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond":
            if side=="bot": return (x,y+h)
            if side=="top": return (x,y-h)
            if side=="left": return (x-w,y)
            if side=="right": return (x+w,y)
        bmap={"bot":(x+w/2,y+h),"top":(x+w/2,y),"left":(x,y+h/2),"right":(x+w,y+h/2)}
        return bmap[side]

    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond": body+=diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        elif t=="stadium": body+=stadium_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=11)
        else: body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)

    arrs=[
        ("A","B","","bot","top"),
        ("B","C","不存在","left","top"),
        ("C","Z1","","bot","top"),
        ("B","D","存在","right","top"),
        ("D","E","是","right","top"),
        ("E","Z2","","bot","top"),
        ("D","F","否","bot","top"),
        ("F","G","未過期","left","top"),
        ("F","H","已過期","right","top"),
        ("G","FAIL","","bot","top"),
        ("H","Z3","","bot","top"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

def nmo_lease_coordination_2():
    """Flowchart TD: ErrorOnLeaseCount"""
    W,H = 580, 520
    nodes={
        "A": ("stadium",290,30, 160,36,"RequestLease",START_FILL,START_STROKE),
        "B": ("diamond",290,110,120,34,"結果?",DIA_FILL,DIA_STROKE),
        "C": ("box",    90,200, 200,44,"ErrorOnLeaseCount++",BOX_FILL,BOX_STROKE),
        "D": ("box",    370,200,180,44,"ErrorOnLeaseCount = 0",END_FILL,END_STROKE),
        "E": ("diamond",90,280, 120,34,"ErrorOnLeaseCount\n> 3?",DIA_FILL,DIA_STROKE),
        "F": ("stadium",270,360,180,36,"重新排程 reconcile",C_FILL,C_STROKE),
        "G": ("box",    -20,360,200,54,"Uncordon 節點\n設定 Phase=Failed",WARN_FILL,WARN_STROKE),
        "H": ("stadium",10, 440,160,36,"結束維護",END_FILL,END_STROKE),
    }
    body=""
    def nb(nid,side="bot"):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond":
            if side=="bot": return (x,y+h)
            if side=="top": return (x,y-h)
            if side=="left": return (x-w,y)
            if side=="right": return (x+w,y)
        bmap={"bot":(x+w/2,y+h),"top":(x+w/2,y),"left":(x,y+h/2),"right":(x+w,y+h/2)}
        return bmap[side]
    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond": body+=diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        elif t=="stadium": body+=stadium_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=11)
        else: body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
    arrs=[
        ("A","B","","bot","top"),
        ("B","C","AlreadyHeldError / 其他錯誤","left","top"),
        ("B","D","成功","right","top"),
        ("C","E","","bot","top"),
        ("E","F","否","right","top"),
        ("E","G","是","left","top"),
        ("G","H","","bot","top"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

def nmo_validation_webhooks_1():
    """Flowchart TD: ValidateCreate flow"""
    W,H = 720, 680
    nodes={
        "A": ("stadium",360,30, 190,36,"收到 CREATE 請求",START_FILL,START_STROKE),
        "B": ("box",    260,100,200,44,"validateNodeExists\nGET node by name",BOX_FILL,BOX_STROKE),
        "E1":("box",    500,100,200,44,"❌ 拒絕\n節點不存在",WARN_FILL,WARN_STROKE),
        "E2":("box",    500,170,200,44,"❌ 拒絕\nAPI 錯誤",WARN_FILL,WARN_STROKE),
        "C": ("box",    260,200,220,44,"validateNoNodeMaintenanceExists\nLIST all NodeMaintenance CRs",BOX_FILL,BOX_STROKE),
        "E3":("box",    10,200, 200,44,"❌ 拒絕\n相同 nodeName CR 已存在",WARN_FILL,WARN_STROKE),
        "E4":("box",    10,270, 200,44,"❌ 拒絕\nAPI 錯誤",WARN_FILL,WARN_STROKE),
        "D": ("diamond",360,300,110,32,"OpenShift 叢集?",DIA_FILL,DIA_STROKE),
        "OK1":("stadium",100,380,130,36,"✅ 允許建立",END_FILL,END_STROKE),
        "F": ("box",    270,380,220,44,"validateControlPlaneQuorum\n檢查 node-role label",BOX_FILL,BOX_STROKE),
        "OK2":("stadium",120,460,130,36,"✅ 允許建立",END_FILL,END_STROKE),
        "G": ("box",    280,460,220,44,"呼叫 etcd.IsEtcdDisruptionAllowed()",C_FILL,C_STROKE),
        "OK3":("stadium",200,550,130,36,"✅ 允許建立",END_FILL,END_STROKE),
        "E5":("box",    380,550,220,64,"❌ 拒絕\n違反 etcd quorum\n不允許 control-plane\n節點進入維護",WARN_FILL,WARN_STROKE),
    }
    body=""
    def nb(nid,side="bot"):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond":
            if side=="bot": return (x,y+h)
            if side=="top": return (x,y-h)
            if side=="left": return (x-w,y)
            if side=="right": return (x+w,y)
        bmap={"bot":(x+w/2,y+h),"top":(x+w/2,y),"left":(x,y+h/2),"right":(x+w,y+h/2)}
        return bmap[side]
    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond": body+=diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        elif t=="stadium": body+=stadium_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        else: body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
    arrs=[
        ("A","B","","bot","top"),
        ("B","E1","Node 不存在","right","left"),
        ("B","E2","API 錯誤","right","left"),
        ("B","C","Node 存在","bot","top"),
        ("C","E3","已存在相同 nodeName","left","right"),
        ("C","E4","API 錯誤","left","right"),
        ("C","D","無衝突","bot","top"),
        ("D","OK1","否","left","right"),
        ("D","F","是","bot","top"),
        ("F","OK2","非 control-plane","left","right"),
        ("F","G","是 control-plane","bot","top"),
        ("G","OK3","允許中斷","left","right"),
        ("G","E5","不允許中斷","right","left"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

def nmo_events_1():
    """Sequence: event lifecycle"""
    parts=[
        ("User","User"),
        ("Ctrl","Controller"),
        ("Node","Node"),
        ("K8s","Kubernetes Events"),
    ]
    msgs=[
        {"from":"User","to":"Ctrl","label":"kubectl apply NodeMaintenance CR","type":"->"},
        {"from":"Ctrl","to":"K8s","label":"🟢 Normal: BeginMaintenance","type":"->"},
        {"type":"note","label":"── Cordon node + begin draining pods ──"},
        {"from":"Ctrl","to":"Node","label":"Drain (evict pods)","type":"->"},
        {"type":"note","label":"── 排空過程中不發送事件 ──"},
        {"from":"Node","to":"Ctrl","label":"Drain complete","type":"-->"},
        {"from":"Ctrl","to":"K8s","label":"🟢 Normal: SucceedMaintenance","type":"->"},
        {"type":"note","label":"── Phase = Succeeded ──"},
        {"from":"User","to":"Ctrl","label":"kubectl delete NodeMaintenance CR","type":"->"},
        {"from":"Ctrl","to":"Node","label":"Uncordon node","type":"->"},
        {"from":"Ctrl","to":"K8s","label":"🟢 Normal: UncordonNode","type":"->"},
        {"from":"Ctrl","to":"K8s","label":"🟢 Normal: RemovedMaintenance","type":"->"},
        {"type":"note","label":"── alt: 錯誤路徑 ──"},
        {"from":"Ctrl","to":"K8s","label":"🔴 Warning: FailedMaintenance","type":"->"},
    ]
    return seq_diagram(parts, msgs, w=860)

def nmo_troubleshooting_1():
    """Flowchart TD: quick diagnosis"""
    W,H = 700, 620
    nodes={
        "A": ("box",    280,30, 200,44,"NodeMaintenance 異常",WARN_FILL,WARN_STROKE),
        "B": ("diamond",280,110,130,34,"nm.status.phase",DIA_FILL,DIA_STROKE),
        "C": ("diamond",110,200,130,34,"drainProgress 是否推進?",DIA_FILL,DIA_STROKE),
        "D": ("box",    -10,300,190,36,"正常排空中，請等待",END_FILL,END_STROKE),
        "E": ("diamond",-30,380,130,34,"pendingPods 有值?",DIA_FILL,DIA_STROKE),
        "F": ("box",    -120,460,200,44,"查看 PDB\n卡住的 Pod",BOX_FILL,BOX_STROKE),
        "G": ("box",    80,460, 180,36,"查看 errorOnLeaseCount",BOX_FILL,BOX_STROKE),
        "H": ("box",    370,200,190,44,"查看 status.lastError",WARN_FILL,WARN_STROKE),
        "H1":("box",    520,280,190,36,"node not found → 節點名稱錯誤",BOX_FILL,BOX_STROKE),
        "H2":("box",    520,330,190,36,"lease 錯誤 → Lease 衝突",BOX_FILL,BOX_STROKE),
        "H3":("box",    520,380,210,36,"lease could not be extended → Lease 失敗超限",BOX_FILL,BOX_STROKE),
        "I": ("box",    370,430,190,44,"查看 errorOnLeaseCount",BOX_FILL,BOX_STROKE),
        "J": ("box",    260,510,200,44,"確認 medik8s-leases\nnamespace",C_FILL,C_STROKE),
        "K": ("box",    480,510,170,44,"查看 Operator logs\nkubectl logs ...",BOX_FILL,BOX_STROKE),
        "L": ("box",    300,570,200,36,"查看 Kubernetes Events",BOX_FILL,BOX_STROKE),
    }
    body=""
    def nb(nid,side="bot"):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond":
            if side=="bot": return (x,y+h)
            if side=="top": return (x,y-h)
            if side=="left": return (x-w,y)
            if side=="right": return (x+w,y)
        bmap={"bot":(x+w/2,y+h),"top":(x+w/2,y),"left":(x,y+h/2),"right":(x+w,y+h/2)}
        return bmap[side]
    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond": body+=diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        elif t=="stadium": body+=stadium_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        else: body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
    arrs=[
        ("A","B","","bot","top"),
        ("B","C","Running","left","right"),
        ("B","H","Failed","right","top"),
        ("B","I","卡住/無進展","bot","top"),
        ("C","D","是","left","right"),
        ("C","E","否","bot","top"),
        ("E","F","是","left","right"),
        ("E","G","否","right","left"),
        ("H","H1","","right","left"),
        ("H","H2","","right","left"),
        ("H","H3","","right","left"),
        ("I","J","遞增","left","top"),
        ("I","K","未遞增","right","top"),
        ("K","L","","bot","right"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

# ── Multus diagrams ─────────────────────────────────────────────────────────────

def multus_architecture_1():
    """graph TB: system architecture with subgraphs"""
    W,H = 900, 600
    body=""
    # Draw 3 subgraph containers
    subs=[
        (30,  50, 380,200,"Thin Plugin 模式",       C_FILL,  C_STROKE),
        (30,  280,380,200,"Thick Plugin 模式（推薦）",C_FILL, C_STROKE),
        (440, 50, 420,200,"CNI 委派（兩種模式共用）",  C_FILL,  C_STROKE),
    ]
    for sx,sy,sw,sh,stitle,sf,ss in subs:
        body+=f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="{sf}" stroke="{ss}" stroke-width="1.5"/>\n'
        body+=f'<text x="{sx+12}" y="{sy+18}" font-family="{FONT}" font-size="12" font-weight="bold" fill="{TEXT_S}">{esc(stitle)}</text>\n'

    # Control plane
    body+=f'<rect x="30" y="510" width="380" height="70" rx="10" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>\n'
    body+=f'<text x="42" y="528" font-family="{FONT}" font-size="12" font-weight="bold" fill="{TEXT_S}">Kubernetes Control Plane</text>\n'

    # Nodes inside subgraphs
    thin_nodes=[
        (40,  80, 160,36,"kubelet / CRI",  BOX_FILL, BOX_STROKE),
        (220, 80, 190,36,"multus binary\n/opt/cni/bin/multus",BOX_FILL,BOX_STROKE),
    ]
    thick_nodes=[
        (40,  310,160,36,"kubelet / CRI",  BOX_FILL, BOX_STROKE),
        (210, 310,190,36,"multus-shim binary\n/opt/cni/bin/multus",BOX_FILL,BOX_STROKE),
        (40,  390,360,44,"multus-daemon DaemonSet Pod\n(Pod Informer + NAD Informer + 共用 k8s 客戶端)",C_FILL,C_STROKE),
    ]
    cni_nodes=[
        (450, 80, 170,36,"Multus 核心邏輯",BOX_FILL,BOX_STROKE),
        (450,150, 120,36,"CNI Plugin 1 (bridge)",END_FILL,END_STROKE),
        (590,150, 120,36,"CNI Plugin 2 (sriov)",END_FILL,END_STROKE),
        (700,150, 130,36,"CNI Plugin N (macvlan)",END_FILL,END_STROKE),
    ]
    k8s_nodes=[
        (50, 530, 160,36,"Kubernetes API Server",BOX_FILL,BOX_STROKE),
        (220,530, 190,36,"NetworkAttachmentDefinition CRD",C_FILL,C_STROKE),
    ]

    for x,y,w,h,lbl,fill,stroke in thin_nodes+thick_nodes+cni_nodes+k8s_nodes:
        body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)

    def bc(x,y,w,h): return (x+w/2,y+h/2)
    def br(x,y,w,h): return (x+w,y+h/2)
    def bt(x,y,w,h): return (x+w/2,y)
    def bb(x,y,w,h): return (x+w/2,y+h)

    # Thin: kubelet->multus
    body+=arrow_svg(*br(*thin_nodes[0][:4]),*thin_nodes[1][:2],"呼叫 CNI",fs=9)
    # Thin: multus->K8SAPI
    body+=arrow_svg(*bb(*thin_nodes[1][:4]),*bt(*k8s_nodes[0][:4]),"直接讀取 kubeconfig",fs=9)

    # Thick: kubelet->shim
    body+=arrow_svg(*br(*thick_nodes[0][:4]),*thick_nodes[1][:2],"呼叫 CNI",fs=9)
    # Thick: shim->daemon
    x1,y1=thick_nodes[1][0]+thick_nodes[1][2]/2, thick_nodes[1][1]+thick_nodes[1][3]
    x2,y2=thick_nodes[2][0]+thick_nodes[2][2]/2, thick_nodes[2][1]
    body+=arrow_svg(x1,y1,x2,y2,"HTTP over Unix Socket",fs=9)
    # Thick daemon->K8SAPI
    body+=arrow_svg(*bb(*thick_nodes[2][:4]),*bt(*k8s_nodes[0][:4]),"共用 k8s 客戶端",fs=9)

    # CNI: multus->delegates
    for dn in cni_nodes[1:]:
        body+=arrow_svg(*bb(*cni_nodes[0][:4]),*bt(*dn[:4]),"委派",fs=9)

    return svg_doc(W,H,body)

def multus_configuration_1():
    """Flowchart LR: auto config generation"""
    W,H = 780, 160
    BW,BH=170,50; DW,DH=110,36
    nodes={
        "A": ("box",    30,  55,180,50,"/etc/cni/net.d/\n掃描設定檔",BOX_FILL,BOX_STROKE),
        "B": ("diamond",260, 80,100,30,"找到 .conf\n或 .conflist?",DIA_FILL,DIA_STROKE),
        "C": ("box",    400, 55,190,50,"選取字母排序最前\n的設定作為預設網路",BOX_FILL,BOX_STROKE),
        "D": ("box",    610, 55,160,50,"產生 00-multus.conf\n（含預設網路設定）",C_FILL,C_STROKE),
        "E": ("box",    560,125,210,30,"fsnotify 監控目錄\n設定變更時重新產生",BOX_FILL,BOX_STROKE),
        "F": ("box",    400,125,130,30,"等待設定檔出現",BOX_FILL,BOX_STROKE),
    }
    body=""
    def nb(nid,side="right"):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond":
            if side=="right": return (x+w,y)
            if side=="left":  return (x-w,y)
            if side=="bot":   return (x,y+h)
            if side=="top":   return (x,y-h)
        bmap={"right":(x+w,y+h/2),"left":(x,y+h/2),"bot":(x+w/2,y+h),"top":(x+w/2,y)}
        return bmap[side]
    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond": body+=diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        else: body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
    arrs=[
        ("A","B","","right","left"),
        ("B","C","是","right","left"),
        ("C","D","","right","left"),
        ("D","E","","bot","right"),
        ("B","F","否","bot","left"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

def multus_core_features_1():
    """Sequence: CNI ADD flow"""
    parts=[
        ("CRI","kubelet / CRI"),
        ("M","Multus 核心邏輯\n(pkg/multus)"),
        ("K8S","Kubernetes API\n(pkg/k8sclient)"),
        ("D1","預設 CNI\n(Flannel)"),
        ("D2","附加 CNI 1\n(SR-IOV)"),
        ("D3","附加 CNI 2\n(macvlan)"),
    ]
    msgs=[
        {"from":"CRI","to":"M","label":"CNI ADD（CNI_ARGS 含 Pod 名稱/命名空間）","type":"->"},
        {"from":"M","to":"M","label":"解析 NetConf，取得 kubeconfig","type":"->"},
        {"from":"M","to":"K8S","label":"GetPod(namespace, name)","type":"->"},
        {"from":"K8S","to":"M","label":"Pod 物件（含 Annotations）","type":"-->"},
        {"from":"M","to":"M","label":"解析 k8s.v1.cni.cncf.io/networks Annotation","type":"->"},
        {"from":"M","to":"K8S","label":"GetNetworkAttachmentDef(namespace, name)","type":"->"},
        {"from":"K8S","to":"M","label":"NetworkAttachmentDefinition CR","type":"-->"},
        {"from":"M","to":"D1","label":"委派 ADD（預設網路，eth0）","type":"->"},
        {"from":"D1","to":"M","label":"網路結果（IP、路由等）","type":"-->"},
        {"from":"M","to":"D2","label":"委派 ADD（附加網路 1，net1）","type":"->"},
        {"from":"D2","to":"M","label":"網路結果","type":"-->"},
        {"from":"M","to":"D3","label":"委派 ADD（附加網路 2，net2）","type":"->"},
        {"from":"D3","to":"M","label":"網路結果","type":"-->"},
        {"from":"M","to":"M","label":"合併結果，儲存 delegates 至 scratch 目錄","type":"->"},
        {"from":"M","to":"CRI","label":"CNI 結果（主要 eth0 的 IP 資訊）","type":"-->"},
        {"from":"M","to":"K8S","label":"更新 Pod Annotation k8s.v1.cni.cncf.io/network-status","type":"->"},
    ]
    return seq_diagram(parts, msgs, w=1000)

def multus_core_features_2():
    """Flowchart LR: DEL scratch cache"""
    W,H = 820, 190
    nodes={
        "A": ("box",  30, 70,190,50,"CmdAdd 執行完成",BOX_FILL,BOX_STROKE),
        "B": ("box",  260,30,230,50,"/var/lib/cni/multus/{containerID}\n儲存所有 DelegateNetConf JSON",C_FILL,C_STROKE),
        "C": ("box",  30,140,190,40,"CmdDel 呼叫",WARN_FILL,WARN_STROKE),
        "D": ("diamond",280,115,100,30,"快取存在?",DIA_FILL,DIA_STROKE),
        "E": ("box",  420, 70,210,50,"consumeScratchNetConf()\n讀取快取，並刪除檔案",BOX_FILL,BOX_STROKE),
        "F": ("box",  420,140,210,40,"對每個 DelegateNetConf\n呼叫委派 DEL",BOX_FILL,BOX_STROKE),
        "G": ("box",  620,140,150,40,"記錄警告，\n嘗試從設定重建",WARN_FILL,WARN_STROKE),
    }
    body=""
    def nb(nid,side="right"):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond":
            if side=="right": return (x+w,y)
            if side=="left":  return (x-w,y)
            if side=="bot":   return (x,y+h)
            if side=="top":   return (x,y-h)
        bmap={"right":(x+w,y+h/2),"left":(x,y+h/2),"bot":(x+w/2,y+h),"top":(x+w/2,y)}
        return bmap[side]
    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond": body+=diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        else: body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
    arrs=[
        ("A","B","saveDelegates()","right","left"),
        ("C","D","","right","left"),
        ("D","E","是","top","bot"),
        ("E","F","","bot","top"),
        ("D","G","否","right","left"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

def multus_core_features_3():
    """Flowchart LR: SR-IOV device allocation"""
    W,H = 780, 160
    nodes={
        "K": ("box",30, 60,130,44,"kubelet",BOX_FILL,BOX_STROKE),
        "CP":("box",220,40,230,64,"/var/lib/kubelet/device-plugins/\nkubelet_internal_checkpoint",C_FILL,C_STROKE),
        "M": ("box",220,120,130,36,"Multus",BOX_FILL,BOX_STROKE),
        "NAD":("box",430,120,160,36,"NAD 設定\n(取得 DeviceID)",BOX_FILL,BOX_STROKE),
        "RC":("box",430,60, 160,44,"RuntimeConfig\n(設定 DeviceID)",BOX_FILL,BOX_STROKE),
        "SRIOV":("box",620,80,130,44,"SR-IOV CNI Plugin",END_FILL,END_STROKE),
    }
    body=""
    def nb(nid,side="right"):
        t,x,y,w,h,_,_,_=nodes[nid]
        bmap={"right":(x+w,y+h/2),"left":(x,y+h/2),"bot":(x+w/2,y+h),"top":(x+w/2,y)}
        return bmap[side]
    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
    arrs=[
        ("K","CP","分配 SR-IOV VF","right","left"),
        ("M","CP","讀取 checkpoint","top","bot"),
        ("M","NAD","取得 DeviceID","right","left"),
        ("NAD","RC","設定 DeviceID","top","bot"),
        ("RC","SRIOV","委派","right","left"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

def multus_thick_plugin_1():
    """Flowchart TD: multus-daemon startup"""
    W,H = 580, 700
    nodes={
        "A": ("stadium",290,30, 200,36,"啟動 multus-daemon",START_FILL,START_STROKE),
        "B": ("box",    200,95, 220,44,"讀取 daemon-config.json\ncniServerConfig()",BOX_FILL,BOX_STROKE),
        "C": ("box",    200,163,220,44,"解析 multus CNI 設定\nconfig.ParseMultusConfig()",BOX_FILL,BOX_STROKE),
        "D": ("diamond",290,240,140,34,"ReadinessIndicatorFile\n是否設定?",DIA_FILL,DIA_STROKE),
        "E": ("box",    80, 320,200,36,"等待就緒指示檔存在",BOX_FILL,BOX_STROKE),
        "F": ("diamond",290,350,130,34,"MultusConfigFile\n== auto?",DIA_FILL,DIA_STROKE),
        "G": ("box",    80, 430,220,44,"建立 config.Manager\n自動產生 multus CNI 設定",BOX_FILL,BOX_STROKE),
        "H": ("box",    330,430,210,44,"複製使用者提供的\nmultus 設定至 cniConfigDir",BOX_FILL,BOX_STROKE),
        "I": ("box",    200,505,220,36,"startMultusDaemon()",C_FILL,C_STROKE),
        "J": ("box",    200,563,240,36,"srv.FilesystemPreRequirements()\n建立 /run/multus/ 目錄",BOX_FILL,BOX_STROKE),
        "K": ("box",    200,621,240,44,"srv.NewCNIServer()\n建立 HTTP Server + Informers",BOX_FILL,BOX_STROKE),
    }
    body=""
    def nb(nid,side="bot"):
        t,x,y,w,h,_,_,_=nodes[nid]
        if t=="diamond":
            if side=="bot": return (x,y+h)
            if side=="top": return (x,y-h)
            if side=="left": return (x-w,y)
            if side=="right": return (x+w,y)
        bmap={"bot":(x+w/2,y+h),"top":(x+w/2,y),"left":(x,y+h/2),"right":(x+w,y+h/2)}
        return bmap[side]
    for nid,(t,x,y,w,h,lbl,fill,stroke) in nodes.items():
        if t=="diamond": body+=diamond_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
        elif t=="stadium": body+=stadium_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=11)
        else: body+=box_svg(x,y,w,h,lbl,fill=fill,stroke=stroke,fs=10)
    arrs=[
        ("A","B","","bot","top"),
        ("B","C","","bot","top"),
        ("C","D","","bot","top"),
        ("D","E","是","left","right"),
        ("D","F","否","bot","top"),
        ("E","F","","bot","top"),
        ("F","G","是","left","right"),
        ("F","H","否","right","top"),
        ("G","I","","bot","top"),
        ("H","I","","bot","top"),
        ("I","J","","bot","top"),
        ("J","K","","bot","top"),
    ]
    for f,t,lbl,fs,ts in arrs:
        x1,y1=nb(f,fs); x2,y2=nb(t,ts)
        body+=arrow_svg(x1,y1,x2,y2,lbl,fs=9)
    return svg_doc(W,H,body)

def multus_thick_plugin_2():
    """Sequence: shim communication flow"""
    parts=[
        ("kubelet","kubelet"),
        ("shim","multus-shim\n(CNI Binary)"),
        ("daemon","multus-daemon\n(HTTP Server)"),
    ]
    msgs=[
        {"from":"kubelet","to":"shim","label":"呼叫 CNI ADD（環境變數 + stdin）","type":"->"},
        {"from":"shim","to":"shim","label":"封裝 CNI 請求為 HTTP JSON","type":"->"},
        {"from":"shim","to":"daemon","label":"POST /cni  {Env: {...}, Config: {...}} （Unix Socket）","type":"->"},
        {"from":"daemon","to":"daemon","label":"解析請求，取得 K8sArgs","type":"->"},
        {"from":"daemon","to":"daemon","label":"從 Informer 快取查詢 Pod/NAD","type":"->"},
        {"from":"daemon","to":"daemon","label":"執行 CNI 委派（呼叫各個 CNI Binary）","type":"->"},
        {"from":"daemon","to":"shim","label":"HTTP 200 + CNI 結果 JSON","type":"-->"},
        {"from":"shim","to":"kubelet","label":"輸出 CNI 結果（stdout）","type":"-->"},
    ]
    return seq_diagram(parts, msgs, w=800)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN: generate all
# ═══════════════════════════════════════════════════════════════════════════════

diagrams = [
    (f"{OUT_NMO}/nmo-architecture-1.svg",    nmo_architecture_1),
    (f"{OUT_NMO}/nmo-architecture-2.svg",    nmo_architecture_2),
    (f"{OUT_NMO}/nmo-architecture-3.svg",    nmo_architecture_3),
    (f"{OUT_NMO}/nmo-design-motivation-1.svg",nmo_design_motivation_1),
    (f"{OUT_NMO}/nmo-node-drainage-1.svg",   nmo_node_drainage_1),
    (f"{OUT_NMO}/nmo-taints-cordoning-1.svg", nmo_taints_cordoning_1),
    (f"{OUT_NMO}/nmo-lease-coordination-1.svg",nmo_lease_coordination_1),
    (f"{OUT_NMO}/nmo-lease-coordination-2.svg",nmo_lease_coordination_2),
    (f"{OUT_NMO}/nmo-validation-webhooks-1.svg",nmo_validation_webhooks_1),
    (f"{OUT_NMO}/nmo-events-1.svg",          nmo_events_1),
    (f"{OUT_NMO}/nmo-troubleshooting-1.svg", nmo_troubleshooting_1),
    (f"{OUT_MULTUS}/multus-architecture-1.svg",multus_architecture_1),
    (f"{OUT_MULTUS}/multus-configuration-1.svg",multus_configuration_1),
    (f"{OUT_MULTUS}/multus-core-features-1.svg",multus_core_features_1),
    (f"{OUT_MULTUS}/multus-core-features-2.svg",multus_core_features_2),
    (f"{OUT_MULTUS}/multus-core-features-3.svg",multus_core_features_3),
    (f"{OUT_MULTUS}/multus-thick-plugin-1.svg",multus_thick_plugin_1),
    (f"{OUT_MULTUS}/multus-thick-plugin-2.svg",multus_thick_plugin_2),
]

for path, fn in diagrams:
    try:
        svg = fn()
        with open(path, "w") as f:
            f.write(svg)
        print(f"OK: {path}")
    except Exception as e:
        print(f"ERROR {path}: {e}")
        import traceback; traceback.print_exc()
