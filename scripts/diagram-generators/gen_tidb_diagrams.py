#!/usr/bin/env python3
"""Generate all 9 TiDB diagrams - Notion Clean Style 4."""
import os

FONT           = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG             = "#ffffff"
BOX_FILL       = "#f9fafb"
BOX_STROKE     = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW          = "#3b82f6"
TEXT_PRIMARY   = "#111827"
TEXT_SECONDARY = "#6b7280"
NOTE_FILL      = "#fef9c3"
NOTE_STROKE    = "#fde68a"

OUT = "docs-site/public/diagrams/tidb"
os.makedirs(OUT, exist_ok=True)

# ── primitives ────────────────────────────────────────────────────────────────

def SVG(w, h, body):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
    <marker id="arrowrev" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto-start-reverse">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  <rect width="{w}" height="{h}" fill="{BG}"/>
{body}</svg>
'''

def R(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8, sw=1.5):
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>\n'

def T(x, y, s, sz=13, fill=TEXT_PRIMARY, anchor="middle", bold=False, italic=False):
    fw = "600" if bold else "normal"
    fs = "italic" if italic else "normal"
    return (f'  <text x="{x}" y="{y}" font-family="{FONT}" font-size="{sz}" fill="{fill}" '
            f'text-anchor="{anchor}" dominant-baseline="middle" font-weight="{fw}" '
            f'font-style="{fs}" xml:space="preserve">{s}</text>\n')

def BOX(x, y, w, h, lines, fill=BOX_FILL, stroke=BOX_STROKE, rx=8, sz=13, bold=False):
    o = R(x, y, w, h, fill, stroke, rx)
    cx = x + w / 2
    n = len(lines)
    lh = sz + 6
    sy = y + h / 2 - (n - 1) * lh / 2
    for i, ln in enumerate(lines):
        o += T(cx, sy + i * lh, ln, sz=sz, bold=bold)
    return o

def aLine(x1, y1, x2, y2, lbl="", dash=False, bidir=False, lox=0, loy=-12):
    da = ' stroke-dasharray="5,4"' if dash else ""
    ms = ' marker-start="url(#arrowrev)"' if bidir else ""
    o = (f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" '
         f'stroke-width="1.5" marker-end="url(#arrow)"{ms}{da}/>\n')
    if lbl:
        lx = (x1 + x2) / 2 + lox
        ly = (y1 + y2) / 2 + loy
        o += T(lx, ly, lbl, sz=11, fill=TEXT_SECONDARY)
    return o

def aPath(d, lbl="", lx=0, ly=0, dash=False, bidir=False):
    da = ' stroke-dasharray="5,4"' if dash else ""
    ms = ' marker-start="url(#arrowrev)"' if bidir else ""
    o = (f'  <path d="{d}" stroke="{ARROW}" stroke-width="1.5" fill="none" '
         f'marker-end="url(#arrow)"{ms}{da}/>\n')
    if lbl:
        o += T(lx, ly, lbl, sz=11, fill=TEXT_SECONDARY)
    return o

def DIAMOND(cx, cy, dw, dh, label, sz=13):
    hw, hh = dw / 2, dh / 2
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    o = f'  <polygon points="{pts}" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>\n'
    o += T(cx, cy, label, sz=sz)
    return o

def CIRCLE(cx, cy, r, fill=TEXT_PRIMARY):
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{BOX_STROKE}" stroke-width="1.5"/>\n'

def CIRCLE2(cx, cy, r, fill=TEXT_PRIMARY):  # end state (circle-in-circle)
    o  = f'  <circle cx="{cx}" cy="{cy}" r="{r+5}" fill="{BG}" stroke="{TEXT_PRIMARY}" stroke-width="2"/>\n'
    o += f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEXT_PRIMARY}"/>\n'
    return o

# ── Sequence diagram helpers ─────────────────────────────────────────────────

def seq_participants(names_list, p_cx, y_top, bw=160, bh=48):
    """Draw participant boxes. names_list: list of (alias, display_lines)"""
    o = ""
    for alias, lines in names_list:
        cx = p_cx[alias]
        o += BOX(cx - bw/2, y_top, bw, bh, lines, sz=13, bold=True)
    return o

def seq_lifelines(p_cx, y_start, y_end, dash=True):
    o = ""
    for cx in p_cx.values():
        da = ' stroke-dasharray="6,4"' if dash else ""
        o += f'  <line x1="{cx}" y1="{y_start}" x2="{cx}" y2="{y_end}" stroke="#d1d5db" stroke-width="1.2"{da}/>\n'
    return o

def seq_msg(p_cx, frm, to, y, lbl="", dash=False):
    x1, x2 = p_cx[frm], p_cx[to]
    loy = -12 if x2 > x1 else -12
    lox = 0
    return aLine(x1, y, x2, y, lbl=lbl, dash=dash, loy=loy, lox=lox)

def seq_self(p_cx, who, y, lbl="", bw=160):
    cx = p_cx[who]
    rx = cx + bw / 2
    o = aPath(f"M {rx},{y} H {rx+50} V {y+32} H {rx+9}",
              lbl=lbl, lx=rx+55, ly=y+16)
    return o, 32

def seq_note(p_cx, who, y, lines, nw=240):
    cx = p_cx[who]
    nh = len(lines) * 20 + 16
    nx = cx - nw / 2
    o = R(nx, y, nw, nh, fill=NOTE_FILL, stroke=NOTE_STROKE, rx=6)
    for i, ln in enumerate(lines):
        o += T(cx, y + 12 + i * 20, ln, sz=11, fill="#92400e")
    return o, nh

def seq_loop_box(p_cx_list, y_start, y_end, label="loop"):
    xs = [p_cx_list[0] - 80]
    xe = [p_cx_list[-1] + 80]
    x0 = min(xs)
    x1 = max(xe)
    o  = R(x0, y_start, x1-x0, y_end-y_start, fill="none", stroke=CONTAINER_STROKE, rx=4)
    o += R(x0, y_start, 50, 20, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, rx=4)
    o += T(x0+25, y_start+10, label, sz=11, fill=TEXT_SECONDARY)
    return o

# ══════════════════════════════════════════════════════════════════════════════
# D1 — tidb-server-arch  (flowchart TD)
# ══════════════════════════════════════════════════════════════════════════════

def gen_server_arch():
    W = 1000
    CX = 500
    CBW = 300   # center box width
    CBX = CX - CBW / 2

    def cbox(y, h, lines):
        return BOX(CBX, y, CBW, h, lines)

    y_A = 20;  h_A = 60
    y_B = y_A + h_A + 22;  h_B = 65
    y_C = y_B + h_B + 22;  h_C = 65
    y_D = y_C + h_C + 22;  h_D = 80
    y_E = y_D + h_D + 22;  h_E = 65
    y_F = y_E + h_E + 22;  h_F = 80
    # diamond G
    y_G = y_F + h_F + 35;  dw_G = 160; dh_G = 60
    # branches
    LCX = 180;  LBW = 300;  LBX = LCX - LBW/2
    RCX = 820;  RBW = 300;  RBX = RCX - RBW/2
    y_HI = y_G + dh_G/2 + 30;  h_HI = 80
    y_JK = y_HI + h_HI + 25;   h_JK = 65
    y_L  = y_JK + h_JK + 50;   h_L  = 65
    H = int(y_L + h_L + 40)

    o = ""
    o += cbox(y_A, h_A, ["MySQL Client", "(TCP :4000)"])
    o += cbox(y_B, h_B, ["pkg/server", "連線管理 / 協定解析"])
    o += cbox(y_C, h_C, ["pkg/session", "Session 管理 / 交易協調"])
    o += cbox(y_D, h_D, ["pkg/parser", "SQL 詞法 + 語法解析", "生成 AST"])
    o += cbox(y_E, h_E, ["pkg/planner", "邏輯計劃生成 / 語意分析"])
    o += cbox(y_F, h_F, ["pkg/planner/core", "查詢優化器", "邏輯 → 物理計劃"])
    o += DIAMOND(CX, y_G, dw_G, dh_G, "查詢類型")
    o += BOX(LBX, y_HI, LBW, h_HI, ["pkg/executor", "在 TiDB 本地執行", "推送計算至 TiKV Coprocessor"])
    o += BOX(RBX, y_HI, RBW, h_HI, ["MPP 計劃生成", "推送至 TiFlash"])
    o += BOX(LBX, y_JK, LBW, h_JK, ["TiKV", "行式儲存 / Coprocessor"])
    o += BOX(RBX, y_JK, RBW, h_JK, ["TiFlash", "列式儲存 / MPP"])
    o += BOX(CBX, y_L, CBW, h_L, ["PD", "TSO / Region 路由"])

    # center arrows
    o += aLine(CX, y_A+h_A, CX, y_B, "MySQL 協定")
    o += aLine(CX, y_B+h_B, CX, y_C)
    o += aLine(CX, y_C+h_C, CX, y_D)
    o += aLine(CX, y_D+h_D, CX, y_E)
    o += aLine(CX, y_E+h_E, CX, y_F)
    o += aLine(CX, y_F+h_F, CX, y_G - dh_G/2)

    # G → H  (left)
    gL = CX - dw_G/2
    gR = CX + dw_G/2
    o += aPath(f"M {gL},{y_G} H {LCX} V {y_HI}",
               lbl="OLTP (Point/Batch)", lx=(gL+LCX)/2, ly=y_G-15)
    # G → I  (right)
    o += aPath(f"M {gR},{y_G} H {RCX} V {y_HI}",
               lbl="OLAP / MPP", lx=(gR+RCX)/2, ly=y_G-15)

    # H → J, I → K
    o += aLine(LCX, y_HI+h_HI, LCX, y_JK, "KV RPC (gRPC)")
    o += aLine(RCX, y_HI+h_HI, RCX, y_JK, "MPP gRPC")

    # J,K → L
    Lcy = y_L + h_L/2
    o += aPath(f"M {LCX},{y_JK+h_JK} V {Lcy} H {CBX}")
    o += aPath(f"M {RCX},{y_JK+h_JK} V {Lcy} H {CBX+CBW}")

    return SVG(W, H, o)

# ══════════════════════════════════════════════════════════════════════════════
# D2 — tidb-sql-execution  (sequenceDiagram)
# ══════════════════════════════════════════════════════════════════════════════

def gen_sql_execution():
    W = 920
    BW = 160; BH = 50
    p_cx = {"C": 90, "T": 310, "P": 560, "K": 790}
    participants = [
        ("C", ["Client"]),
        ("T", ["TiDB Server"]),
        ("P", ["PD"]),
        ("K", ["TiKV"]),
    ]
    P_TOP = 20
    lifeline_start = P_TOP + BH
    y = lifeline_start + 30

    o = ""
    o += seq_participants(participants, p_cx, P_TOP, bw=BW, bh=BH)

    msgs = [
        ("C","T", "SELECT * FROM t WHERE id=1", False),
        ("T","T", "解析 SQL → AST",             False),
        ("T","T", "語意分析 → 邏輯計劃",          False),
        ("T","T", "優化 → 物理計劃（IndexLookup）", False),
        ("T","P", "獲取 TSO（開始時間戳）",         False),
        ("P","T", "startTS",                    True),
        ("T","P", "查詢 Region 路由（id=1 位於哪個 Region）", False),
        ("P","T", "Region Leader 位址",           True),
        ("T","K", "KV Get（startTS, key）",       False),
        ("K","T", "value",                       True),
        ("T","C", "回傳結果集",                    True),
    ]

    all_ys = []
    for frm, to, lbl, dash in msgs:
        if frm == to:
            chunk, dy = seq_self(p_cx, frm, y, lbl, bw=BW)
            o += chunk
            all_ys.append(y)
            y += dy + 30
        else:
            o += seq_msg(p_cx, frm, to, y, lbl=lbl, dash=dash)
            all_ys.append(y)
            y += 50

    lifeline_end = y + 20
    o_life = seq_lifelines(p_cx, lifeline_start, lifeline_end)
    H = lifeline_end + 20
    return SVG(W, H, o_life + o)

# ══════════════════════════════════════════════════════════════════════════════
# D3 — tidb-connection-flow  (sequenceDiagram with loop)
# ══════════════════════════════════════════════════════════════════════════════

def gen_connection_flow():
    W = 1000
    BW = 170; BH = 50
    p_cx = {"C": 90, "S": 310, "Se": 570, "E": 830}
    participants = [
        ("C",  ["Client"]),
        ("S",  ["pkg/server"]),
        ("Se", ["pkg/session"]),
        ("E",  ["pkg/executor"]),
    ]
    P_TOP = 20
    lifeline_start = P_TOP + BH
    y = lifeline_start + 30

    o = ""
    o += seq_participants(participants, p_cx, P_TOP, bw=BW, bh=BH)

    # pre-loop messages
    o += seq_msg(p_cx, "C","S", y, "TCP 連線建立（:4000）"); y += 50
    o += seq_msg(p_cx, "S","C", y, "Handshake 封包（Server Greeting）", dash=True); y += 50
    o += seq_msg(p_cx, "C","S", y, "Auth 封包（帳號/密碼）"); y += 50
    chunk, dy = seq_self(p_cx, "S", y, "驗證身分（pkg/privilege）", bw=BW)
    o += chunk; y += dy + 25
    o += seq_msg(p_cx, "S","C", y, "OK 封包", dash=True); y += 50

    # loop
    loop_y_start = y
    y += 30  # space for loop label

    o += seq_msg(p_cx, "C","S",  y, "COM_QUERY / COM_STMT_EXECUTE"); y += 50
    o += seq_msg(p_cx, "S","Se", y, "建立 Statement Context"); y += 50
    o += seq_msg(p_cx, "Se","E", y, "解析 → 優化 → 執行"); y += 50
    o += seq_msg(p_cx, "E","Se", y, "結果集 / 受影響行數", dash=True); y += 50
    o += seq_msg(p_cx, "Se","S", y, "結果", dash=True); y += 50
    o += seq_msg(p_cx, "S","C",  y, "ResultSet / OK 封包", dash=True); y += 50

    loop_y_end = y + 10
    # draw loop box behind
    loop_xs = sorted(p_cx.values())
    o_loop = seq_loop_box(loop_xs, loop_y_start, loop_y_end, "loop 每條 SQL")
    y = loop_y_end + 20

    o += seq_msg(p_cx, "C","S",  y, "COM_QUIT"); y += 50
    o += seq_msg(p_cx, "S","Se", y, "關閉 Session"); y += 50

    lifeline_end = y + 20
    o_life = seq_lifelines(p_cx, lifeline_start, lifeline_end)
    H = lifeline_end + 20
    return SVG(W, H, o_life + o_loop + o)

# ══════════════════════════════════════════════════════════════════════════════
# D4 — tidb-session-lifecycle  (stateDiagram-v2)
# ══════════════════════════════════════════════════════════════════════════════

def gen_session_lifecycle():
    W = 1060; H = 420
    SW = 200; SH = 55  # state box
    SY = 180           # center y of states

    states = {
        "Idle":          (160, SY),
        "Active":        (430, SY),
        "InTransaction": (730, SY),
    }
    start = (50,  SY)
    end   = (430, 330)

    o = ""
    # states
    for name, (cx, cy) in states.items():
        o += BOX(cx - SW/2, cy - SH/2, SW, SH, [name], rx=20)

    # start dot
    o += CIRCLE(start[0], start[1], 12)
    # end dot
    o += CIRCLE2(end[0], end[1], 10)

    # transitions
    # [*] → Idle
    o += aLine(start[0]+12, start[1], states["Idle"][0]-SW/2, states["Idle"][1],
               lbl="連線建立", loy=-14)
    # Idle → Active
    o += aLine(states["Idle"][0]+SW/2, SY, states["Active"][0]-SW/2, SY,
               lbl="收到 SQL", loy=-14)
    # Active → Idle (curved back above)
    ax1, ax2 = states["Active"][0]-SW/2, states["Idle"][0]+SW/2
    mid_above = SY - 60
    o += aPath(f"M {ax1},{SY-5} C {ax1-30},{mid_above} {ax2+30},{mid_above} {ax2},{SY-5}",
               lbl="SQL 執行完成（非交易）", lx=(ax1+ax2)/2, ly=mid_above-15)
    # Active → InTransaction
    o += aLine(states["Active"][0]+SW/2, SY, states["InTransaction"][0]-SW/2, SY,
               lbl="BEGIN 或 DML（悲觀交易）", loy=-14)
    # InTransaction → Active (curved above)
    bx1, bx2 = states["InTransaction"][0]-SW/2, states["Active"][0]+SW/2
    mid_b = SY - 60
    o += aPath(f"M {bx1},{SY-5} C {bx1-30},{mid_b} {bx2+30},{mid_b} {bx2},{SY-5}",
               lbl="COMMIT / ROLLBACK", lx=(bx1+bx2)/2, ly=mid_b-15)
    # InTransaction → InTransaction (self)
    itcx = states["InTransaction"][0]
    o += aPath(f"M {itcx+SW/2},{SY-10} H {itcx+SW/2+45} V {SY+30} H {itcx+SW/2+9}",
               lbl="繼續 DML", lx=itcx+SW/2+50, ly=SY+10)
    # Active → [*]
    o += aLine(states["Active"][0], SY+SH/2, end[0], end[1]-15,
               lbl="COM_QUIT / 連線斷開", lox=60, loy=0)

    return SVG(W, H, o)

# ══════════════════════════════════════════════════════════════════════════════
# D5 — tidb-sql-pipeline  (flowchart LR, 12 nodes)
# ══════════════════════════════════════════════════════════════════════════════

def gen_sql_pipeline():
    nodes = [
        ["SQL 文字"],
        ["詞法分析", "(Lexer)"],
        ["語法分析", "(Parser/yacc)"],
        ["AST", "（抽象語法樹）"],
        ["語意分析", "Compile"],
        ["邏輯計劃", "（LogicalPlan）"],
        ["邏輯優化", "（規則優化）"],
        ["統計資訊", "估算基數"],
        ["物理計劃", "（PhysicalPlan）"],
        ["執行計劃", "（ExecPlan）"],
        ["算子執行", "（Executor）"],
        ["結果集"],
    ]
    N = len(nodes)
    BW = 148; BH = 62; GAP = 20
    MARGIN = 30
    W = MARGIN * 2 + N * BW + (N-1) * GAP
    H = 140

    BOX_Y = (H - BH) // 2
    o = ""
    for i, lines in enumerate(nodes):
        x = MARGIN + i * (BW + GAP)
        cx = x + BW / 2
        o += BOX(x, BOX_Y, BW, BH, lines)
        if i > 0:
            px = MARGIN + (i-1) * (BW + GAP) + BW
            o += aLine(px, H/2, x, H/2)

    return SVG(W, H, o)

# ══════════════════════════════════════════════════════════════════════════════
# D6 — tidb-2pc  (sequenceDiagram with notes)
# ══════════════════════════════════════════════════════════════════════════════

def gen_2pc():
    W = 940
    BW = 160; BH = 50
    p_cx = {"C": 90, "T": 310, "P": 560, "K": 790}
    participants = [
        ("C", ["Client"]),
        ("T", ["TiDB Server"]),
        ("P", ["PD"]),
        ("K", ["TiKV"]),
    ]
    P_TOP = 20
    lifeline_start = P_TOP + BH
    y = lifeline_start + 30

    o = ""
    o += seq_participants(participants, p_cx, P_TOP, bw=BW, bh=BH)

    o += seq_msg(p_cx, "C","T", y, "BEGIN"); y += 50
    o += seq_msg(p_cx, "T","P", y, "獲取 startTS（全域唯一時間戳）"); y += 50
    o += seq_msg(p_cx, "P","T", y, "startTS", dash=True); y += 50

    # Note over TiDB
    note_lines = ["執行 DML 操作", "修改存放於本地記憶體 buffer"]
    chunk, nh = seq_note(p_cx, "T", y, note_lines, nw=280)
    o += chunk; y += nh + 20

    o += seq_msg(p_cx, "C","T", y, "COMMIT"); y += 50
    o += seq_msg(p_cx, "T","P", y, "獲取 commitTS"); y += 50
    o += seq_msg(p_cx, "P","T", y, "commitTS", dash=True); y += 50
    o += seq_msg(p_cx, "T","K", y, "Prewrite 階段：寫入 Lock 到主鍵 + 次要鍵"); y += 50
    o += seq_msg(p_cx, "K","T", y, "Prewrite OK", dash=True); y += 50
    o += seq_msg(p_cx, "T","K", y, "Commit 階段：提交主鍵（清除鎖，寫入 Write Record）"); y += 50
    o += seq_msg(p_cx, "K","T", y, "Commit OK", dash=True); y += 50

    # Note over TiDB
    note2 = ["非同步清理次要鍵鎖"]
    chunk2, nh2 = seq_note(p_cx, "T", y, note2, nw=220)
    o += chunk2; y += nh2 + 20

    o += seq_msg(p_cx, "T","C", y, "COMMIT OK", dash=True); y += 50

    lifeline_end = y + 20
    o_life = seq_lifelines(p_cx, lifeline_start, lifeline_end)
    H = lifeline_end + 20
    return SVG(W, H, o_life + o)

# ══════════════════════════════════════════════════════════════════════════════
# D7 — tidb-htap-routing  (flowchart TD)
# ══════════════════════════════════════════════════════════════════════════════

def gen_htap_routing():
    W = 860; CX = 430
    BW = 220; BW2 = 260

    y0  = 20;  h0  = 50
    y1  = 100; h1  = 50
    y2  = 195; dw2 = 220; dh2 = 65
    y3  = 315; h3  = 80
    y4  = 460; h4  = 50
    y5  = 540; h5  = 50

    LCX = 220; RCX = 640

    o = ""
    o += BOX(CX-BW/2,  y0, BW,  h0,  ["SQL 查詢"])
    o += BOX(CX-BW/2,  y1, BW,  h1,  ["查詢優化器"])
    o += DIAMOND(CX, y2+dh2/2, dw2, dh2, "TiFlash 副本？", sz=12)
    o += BOX(LCX-BW2/2, y3, BW2, h3, ["TiFlash", "MPP 列式執行"])
    o += BOX(RCX-BW2/2, y3, BW2, h3, ["TiKV", "行式執行", "Coprocessor 下推"])
    o += BOX(CX-BW/2,  y4, BW,  h4,  ["合併結果"])
    o += BOX(CX-BW/2,  y5, BW,  h5,  ["回傳用戶端"])

    o += aLine(CX, y0+h0, CX, y1)
    o += aLine(CX, y1+h1, CX, y2)

    # diamond to branches
    dL = CX - dw2/2; dR = CX + dw2/2
    dBot = y2 + dh2
    o += aPath(f"M {dL},{y2+dh2/2} H {LCX} V {y3}",
               lbl="是（OLAP）", lx=(dL+LCX)/2, ly=y2+dh2/2-14)
    o += aPath(f"M {dR},{y2+dh2/2} H {RCX} V {y3}",
               lbl="否（OLTP）", lx=(dR+RCX)/2, ly=y2+dh2/2-14)

    o += aPath(f"M {LCX},{y3+h3} V {y4+h4/2} H {CX-BW/2}")
    o += aPath(f"M {RCX},{y3+h3} V {y4+h4/2} H {CX+BW/2}")
    o += aLine(CX, y4+h4, CX, y5)

    H = y5 + h5 + 30
    return SVG(W, H, o)

# ══════════════════════════════════════════════════════════════════════════════
# D8 — tidb-ddl-states  (stateDiagram-v2, linear)
# ══════════════════════════════════════════════════════════════════════════════

def gen_ddl_states():
    states_info = [
        ("None",        ["None"]),
        ("DeleteOnly",  ["Delete", "Only"]),
        ("WriteOnly",   ["Write", "Only"]),
        ("WriteReorg",  ["Write", "Reorg"]),
        ("Public",      ["Public"]),
    ]
    N = len(states_info)
    SW = 130; SH = 65; GAP = 55
    MARGIN = 60
    W = MARGIN * 2 + N * SW + (N-1) * GAP + 80
    SY = 120

    o = ""
    sx = {}
    for i, (key, lines) in enumerate(states_info):
        cx = MARGIN + 40 + i * (SW + GAP) + SW/2
        sx[key] = cx
        o += BOX(cx - SW/2, SY - SH/2, SW, SH, lines, rx=20)

    start = (MARGIN, SY)
    end_x = sx["Public"] + SW/2 + 50
    end = (end_x, SY)

    o += CIRCLE(start[0], start[1], 12)
    o += CIRCLE2(end[0], end[1], 10)

    # [*] → None
    o += aLine(start[0]+12, SY, sx["None"]-SW/2, SY)

    # state→state arrows with labels below the line
    transitions = [
        ("None",       "DeleteOnly",  "ADD COLUMN 開始"),
        ("DeleteOnly", "WriteOnly",   "Write-Only 狀態"),
        ("WriteOnly",  "WriteReorg",  "資料重組（backfill）"),
        ("WriteReorg", "Public",      "正式生效"),
    ]
    for frm, to, lbl in transitions:
        x1 = sx[frm] + SW/2
        x2 = sx[to]  - SW/2
        o += aLine(x1, SY, x2, SY, lbl=lbl, loy=14)

    # Public → [*]
    o += aLine(sx["Public"]+SW/2, SY, end[0]-15, SY)

    H = SY + 80
    return SVG(W, H, o)

# ══════════════════════════════════════════════════════════════════════════════
# D9 — tidb-overview  (graph TB with subgraphs)
# ══════════════════════════════════════════════════════════════════════════════

def gen_overview():
    W = 1320; 
    PAD = 20

    # ── subgraph containers ─────────────────────────────────────────────
    # Client
    sg_client = (370, 20, 580, 110)   # x,y,w,h
    # TiDB Layer
    sg_tidb   = (20, 170, 1280, 110)
    # PD Layer
    sg_pd     = (660, 320, 640, 110)
    # TiKV
    sg_tikv   = (20, 470, 660, 155)
    # TiFlash
    sg_tf     = (700, 470, 600, 155)

    def sg(x, y, w, h, title):
        o  = R(x, y, w, h, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, rx=10)
        o += T(x+12, y+14, title, sz=11, fill=TEXT_SECONDARY, anchor="start", italic=True)
        return o

    # ── nodes ─────────────────────────────────────────────────────────
    NW = 200; NH = 55; NW2 = 220
    def node(cx, cy, lines, w=NW, h=NH):
        return BOX(cx - w/2, cy - h/2, w, h, lines)

    # Client nodes
    APP_cx,   APP_cy   = 480, 78
    MYSQL_cx, MYSQL_cy = 720, 78

    # TiDB nodes
    T1_cx, T1_cy = 160, 228
    T2_cx, T2_cy = 660, 228
    T3_cx, T3_cy = 1160, 228

    # PD nodes
    PD1_cx, PD1_cy = 800, 378
    PD2_cx, PD2_cy = 1100, 378

    # TiKV nodes
    KV1_cx, KV1_cy = 120, 548
    KV2_cx, KV2_cy = 340, 548
    KV3_cx, KV3_cy = 560, 548

    # TiFlash nodes
    TF1_cx, TF1_cy = 840, 548
    TF2_cx, TF2_cy = 1100, 548

    o = ""
    # containers first (background)
    o += sg(*sg_client, "用戶端")
    o += sg(*sg_tidb,   "TiDB 計算層（無狀態，可橫向擴展）")
    o += sg(*sg_pd,     "PD 叢集（中繼資料 / TSO / 排程）")
    o += sg(*sg_tikv,   "TiKV 行式儲存（Raft 多副本）")
    o += sg(*sg_tf,     "TiFlash 列式儲存（OLAP 加速）")

    # nodes
    o += node(APP_cx,   APP_cy,   ["應用程式", "(MySQL Driver)"])
    o += node(MYSQL_cx, MYSQL_cy, ["MySQL CLI /", "ORM 框架"])
    o += node(T1_cx, T1_cy, ["TiDB Server 1"], w=200)
    o += node(T2_cx, T2_cy, ["TiDB Server 2"], w=200)
    o += node(T3_cx, T3_cy, ["TiDB Server N"], w=200)
    o += node(PD1_cx, PD1_cy, ["PD Leader"],   w=220)
    o += node(PD2_cx, PD2_cy, ["PD Follower"], w=220)
    o += node(KV1_cx, KV1_cy, ["TiKV Node 1", "(Region Leader)"],   w=190, h=60)
    o += node(KV2_cx, KV2_cy, ["TiKV Node 2", "(Region Follower)"], w=190, h=60)
    o += node(KV3_cx, KV3_cy, ["TiKV Node 3", "(Region Follower)"], w=190, h=60)
    o += node(TF1_cx, TF1_cy, ["TiFlash Node 1"], w=200)
    o += node(TF2_cx, TF2_cy, ["TiFlash Node 2"], w=200)

    # ── arrows ────────────────────────────────────────────────────────
    # Client → TiDB (APP→T1, MYSQL→T2)
    o += aPath(f"M {APP_cx},{APP_cy+NH/2} L {T1_cx},{T1_cy-NH/2}",
               lbl="MySQL 協定 :4000", lx=(APP_cx+T1_cx)/2+30, ly=(APP_cy+T1_cy)/2-12)
    o += aPath(f"M {MYSQL_cx},{MYSQL_cy+NH/2} L {T2_cx},{T2_cy-NH/2}",
               lbl="MySQL 協定 :4000", lx=(MYSQL_cx+T2_cx)/2+30, ly=(MYSQL_cy+T2_cy)/2-12)

    # TiDB → PD
    o += aPath(f"M {T1_cx},{T1_cy+NH/2} L {PD1_cx},{PD1_cy-NH/2}",
               lbl="TSO / 路由資訊", lx=(T1_cx+PD1_cx)/2+30, ly=(T1_cy+PD1_cy)/2-12)
    o += aPath(f"M {T2_cx},{T2_cy+NH/2} L {PD1_cx-20},{PD1_cy-NH/2}",
               lbl="TSO / 路由資訊", lx=(T2_cx+PD1_cx)/2+30, ly=(T2_cy+PD1_cy)/2-12)

    # TiDB → TiKV
    o += aPath(f"M {T1_cx},{T1_cy+NH/2} V {KV1_cy-30} H {KV1_cx}",
               lbl="KV RPC (gRPC)", lx=T1_cx+50, ly=(T1_cy+NH/2 + KV1_cy-30)/2)
    o += aPath(f"M {T2_cx},{T2_cy+NH/2} L {KV2_cx},{KV2_cy-30}",
               lbl="KV RPC (gRPC)", lx=(T2_cx+KV2_cx)/2+35, ly=(T2_cy+KV2_cy)/2-12)

    # TiDB → TiFlash
    o += aPath(f"M {T1_cx+NW/2},{T1_cy} H {TF1_cx} V {TF1_cy-NH/2}",
               lbl="MPP 查詢 (gRPC)", lx=(T1_cx+NW/2+TF1_cx)/2, ly=T1_cy-14)

    # TiKV internal
    o += aLine(KV1_cx+95, KV1_cy, KV2_cx-95, KV2_cy, lbl="Raft 複製", loy=-14)
    o += aLine(KV2_cx+95, KV2_cy, KV3_cx-95, KV3_cy, lbl="Raft 複製", loy=-14)

    # TiKV → TiFlash (Raft Learner)
    o += aLine(KV1_cx+95, KV1_cy+15, TF1_cx-100, TF1_cy+15,
               lbl="Multi-Raft Learner", loy=16)
    o += aLine(KV2_cx+95, KV2_cy+20, TF2_cx-100, TF2_cy+20,
               lbl="Multi-Raft Learner", loy=16)

    # PD ↔ PD2
    o += aLine(PD1_cx+110, PD1_cy, PD2_cx-110, PD2_cy,
               lbl="Raft 選舉", bidir=True, loy=-14)

    H = sg_tikv[1] + sg_tikv[3] + 40
    return SVG(W, H, o)

# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

diagrams = [
    ("tidb-server-arch",     gen_server_arch),
    ("tidb-sql-execution",   gen_sql_execution),
    ("tidb-connection-flow", gen_connection_flow),
    ("tidb-session-lifecycle", gen_session_lifecycle),
    ("tidb-sql-pipeline",    gen_sql_pipeline),
    ("tidb-2pc",             gen_2pc),
    ("tidb-htap-routing",    gen_htap_routing),
    ("tidb-ddl-states",      gen_ddl_states),
    ("tidb-overview",        gen_overview),
]

for name, fn in diagrams:
    svg_path = os.path.join(OUT, f"{name}.svg")
    content = fn()
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {svg_path}")

print("Done.")
