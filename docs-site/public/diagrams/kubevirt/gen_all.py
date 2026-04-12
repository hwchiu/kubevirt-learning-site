import os
OUT = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt"

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"; BOX_FILL = "#f9fafb"; BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"; CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"; TEXT_PRIMARY = "#111827"; TEXT_SECONDARY = "#6b7280"
ACCENT_FILL = "#eff6ff"; ACCENT_STROKE = "#bfdbfe"

DEFS = '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
  <marker id="arrowg" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#9ca3af"/>
  </marker>
</defs>'''

def w(f, content):
    p = os.path.join(OUT, f)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"OK: {f}")

def svg(W, H, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n{DEFS}\n<rect width="{W}" height="{H}" fill="{BG}"/>\n{body}</svg>'

def box(cx, cy, bw, bh, label, sublabel=None, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    x, y = cx - bw//2, cy - bh//2
    s = f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
    if sublabel:
        s += f'<text x="{cx}" y="{cy-7}" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="600">{label}</text>\n'
        s += f'<text x="{cx}" y="{cy+10}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{sublabel}</text>\n'
    else:
        s += f'<text x="{cx}" y="{cy+5}" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="600">{label}</text>\n'
    return s

def multiline_box(cx, cy, bw, bh, lines, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    x, y = cx - bw//2, cy - bh//2
    s = f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
    total = len(lines)
    start_y = cy - (total-1)*9
    for i, (txt, sz, col, bold) in enumerate(lines):
        fw = "600" if bold else "normal"
        s += f'<text x="{cx}" y="{start_y + i*18}" font-family="{FONT}" font-size="{sz}" fill="{col}" text-anchor="middle" font-weight="{fw}">{txt}</text>\n'
    return s

def start_node(cx, cy, r=12):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEXT_PRIMARY}"/>\n'

def end_node(cx, cy, r=12):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BG}" stroke="{TEXT_PRIMARY}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="{r-5}" fill="{TEXT_PRIMARY}"/>\n'

def arr(x1, y1, x2, y2, dash=False, color=None):
    c = color or (ARROW if not dash else "#9ca3af")
    mk = "url(#arrowg)" if dash else "url(#arrow)"
    da = ' stroke-dasharray="6,4"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="1.5"{da} marker-end="{mk}"/>\n'

def arr_path(d, dash=False, color=None):
    c = color or (ARROW if not dash else "#9ca3af")
    mk = "url(#arrowg)" if dash else "url(#arrow)"
    da = ' stroke-dasharray="6,4"' if dash else ''
    return f'<path d="{d}" stroke="{c}" stroke-width="1.5" fill="none"{da} marker-end="{mk}"/>\n'

def label_on_arr(x, y, txt, size=11, color=None):
    c = color or TEXT_SECONDARY
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{c}" text-anchor="middle">{txt}</text>\n'

# ─────────────────────────────────────────────────────────────────────────────
# 1. kubevirt-vmim-states.svg
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmim_states():
    W, H = 1300, 780
    BW, BH = 220, 44  # state box

    # main path cx=320
    mx = 320
    sy = [130, 240, 350, 460, 620]  # Pending, PreparingTarget, TargetReady, Running, Succeeded
    labels = ["Pending","PreparingTarget","TargetReady","Running","Succeeded"]

    # error states
    fx, fy = 850, 350   # Failed
    cx2, cy2 = 1050, 530  # Cancelled

    body = ""

    # background for main path container
    body += f'<rect x="200" y="80" width="{BW+40}" height="570" rx="12" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1" opacity="0.5"/>\n'
    body += f'<text x="{mx}" y="70" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">正常路徑</text>\n'

    # start node
    body += start_node(mx, 50)

    # state boxes
    fills = [BOX_FILL, BOX_FILL, BOX_FILL, ACCENT_FILL, "#ecfdf5"]
    strokes = [BOX_STROKE, BOX_STROKE, BOX_STROKE, ACCENT_STROKE, "#6ee7b7"]
    for i, (label, yy) in enumerate(zip(labels, sy)):
        body += box(mx, yy, BW, BH, label, fill=fills[i], stroke=strokes[i], rx=20)

    # Failed box
    body += box(fx, fy, 200, 44, "Failed", fill="#fef2f2", stroke="#fca5a5", rx=20)
    # Cancelled box
    body += box(cx2, cy2, 200, 44, "Cancelled", fill="#fffbeb", stroke="#fcd34d", rx=20)

    # end nodes
    body += end_node(mx, 700)
    body += end_node(fx, 430)
    body += end_node(cx2, 610)

    # main path arrows
    body += arr(mx, 62, mx, sy[0]-22)
    body += label_on_arr(mx+120, (62+sy[0]-22)//2, "建立 VirtualMachineInstanceMigration", 10)
    
    for i in range(len(sy)-1):
        body += arr(mx, sy[i]+22, mx, sy[i+1]-22)
    
    # arrow labels on main path
    lbl_x = mx + 120
    body += label_on_arr(lbl_x, (sy[0]+22+sy[1]-22)//2, "選定目標節點，開始準備", 10)
    body += label_on_arr(lbl_x, (sy[1]+22+sy[2]-22)//2, "目標節點 virt-launcher 就緒", 10)
    body += label_on_arr(lbl_x, (sy[2]+22+sy[3]-22)//2, "開始傳輸 VM 記憶體頁面", 10)
    body += label_on_arr(lbl_x, (sy[3]+22+sy[4]-22)//2-10, "所有資料同步完成，完成 Cut-over", 10)

    # Succeeded -> end
    body += arr(mx, sy[4]+22, mx, 700-12)

    # Failed -> end
    body += arr(fx, fy+22, fx, 418)

    # Cancelled -> end
    body += arr(cx2, cy2+22, cx2, 598)

    # error transitions with curved paths
    # Pending -> Failed
    body += arr_path(f"M {mx+BW//2} {sy[0]} C {fx-60} {sy[0]}, {fx-80} {fy-40}, {fx-100} {fy}")
    body += label_on_arr(620, sy[0]-18, "無法選定目標節點", 10, "#ef4444")

    # PreparingTarget -> Failed
    body += arr_path(f"M {mx+BW//2} {sy[1]} C {fx-40} {sy[1]}, {fx-60} {fy-20}, {fx-100} {fy}")
    body += label_on_arr(640, sy[1]-18, "目標準備失敗", 10, "#ef4444")

    # TargetReady -> Cancelled
    body += arr_path(f"M {mx+BW//2} {sy[2]} C {cx2-40} {sy[2]}, {cx2-60} {cy2-40}, {cx2-100} {cy2}")
    body += label_on_arr(800, sy[2]-18, "使用者取消", 10, "#f59e0b")

    # Running -> Failed
    body += arr_path(f"M {mx+BW//2} {sy[3]} C {fx-20} {sy[3]}, {fx-60} {fy+30}, {fx-100} {fy}")
    body += label_on_arr(640, sy[3]-16, "超時或傳輸錯誤", 10, "#ef4444")

    # Running -> Cancelled
    body += arr_path(f"M {mx+BW//2} {sy[3]+10} C {cx2-20} {sy[3]+10}, {cx2-40} {cy2-40}, {cx2-100} {cy2}")
    body += label_on_arr(900, sy[3]-8, "使用者取消", 10, "#f59e0b")

    # title
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">VirtualMachineInstanceMigration 狀態轉換</text>\n'

    w("kubevirt-vmim-states.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 2. kubevirt-vmim-sequence.svg  (Pre-Copy vs Post-Copy)
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmim_sequence():
    W, H = 900, 680
    participants = [("Source", "來源節點"), ("Target", "目標節點")]
    PW, PH = 160, 50
    margin_x = 120
    spacing = 480
    xs = [margin_x + PW//2, margin_x + PW//2 + spacing]  # cx of each participant

    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">Migration 傳輸模式比較</text>\n'

    # participant boxes
    for i, (eng, chi) in enumerate(participants):
        cx = xs[i]
        x = cx - PW//2
        body += f'<rect x="{x}" y="50" width="{PW}" height="{PH}" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1.5"/>\n'
        body += f'<text x="{cx}" y="72" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">{eng}</text>\n'
        body += f'<text x="{cx}" y="90" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{chi}</text>\n'

    # lifelines
    body += f'<line x1="{xs[0]}" y1="100" x2="{xs[0]}" y2="{H-30}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>\n'
    body += f'<line x1="{xs[1]}" y1="100" x2="{xs[1]}" y2="{H-30}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>\n'

    def seq_arr(y, frm, to, label, dash=False):
        x1, x2 = xs[frm], xs[to]
        mid = (x1+x2)//2
        da = ' stroke-dasharray="5,3"' if dash else ''
        mk = 'url(#arrowg)' if dash else 'url(#arrow)'
        sc = "#9ca3af" if dash else ARROW
        b = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{sc}" stroke-width="1.5"{da} marker-end="{mk}"/>\n'
        lbl_y = y - 6
        b += f'<text x="{mid}" y="{lbl_y}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>\n'
        return b

    def note_box(y, label, h=30):
        nx = xs[0] - 80
        nw = xs[1] - xs[0] + 160
        b = f'<rect x="{nx}" y="{y}" width="{nw}" height="{h}" rx="4" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1"/>\n'
        b += f'<text x="{(nx+nx+nw)//2}" y="{y+h//2+5}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="600">{label}</text>\n'
        return b

    y = 130
    body += note_box(y, "Pre-Copy 模式（預設，較安全）")
    y += 50
    body += seq_arr(y, 0, 1, "第1輪：複製所有記憶體頁面")
    y += 45
    body += seq_arr(y, 0, 1, "第2輪：複製修改過的頁面（dirty pages）")
    y += 45
    body += seq_arr(y, 0, 1, "第N輪：持續迭代直到 dirty rate 夠低")
    y += 45
    body += seq_arr(y, 0, 1, "Cut-over：停止 Source，複製最後剩餘頁面")
    y += 45
    body += seq_arr(y, 1, 0, "VM 在 Target 繼續執行", dash=True)
    y += 60

    body += note_box(y, "Post-Copy 模式（更快完成，但風險高）")
    y += 50
    body += seq_arr(y, 0, 1, "複製 CPU 狀態和少量記憶體")
    y += 45
    body += seq_arr(y, 0, 1, "Cut-over：停止 Source，切換控制")
    y += 45
    body += seq_arr(y, 1, 0, "按需請求缺少的記憶體頁面（page fault）")
    y += 45
    body += seq_arr(y, 1, 0, "VM 在 Target 繼續執行（逐漸取得記憶體）", dash=True)

    w("kubevirt-vmim-sequence.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 3. kubevirt-vmim-requirements.svg  (graph TD)
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmim_requirements():
    W, H = 1200, 540
    body = ""

    # Title
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">VMI Live Migration 必要條件檢查</text>\n'

    # Center decision diamond
    dcx, dcy = 420, 200
    dw, dh = 180, 60

    pts = f"{dcx},{dcy-dh//2} {dcx+dw//2},{dcy} {dcx},{dcy+dh//2} {dcx-dw//2},{dcy}"
    body += f'<polygon points="{pts}" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1.5"/>\n'
    body += f'<text x="{dcx}" y="{dcy-6}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">VMI</text>\n'
    body += f'<text x="{dcx}" y="{dcy+10}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">可以 Live Migrate?</text>\n'

    # 5 condition boxes arranged in a column to the right
    conditions = [
        ("✅ 使用 Shared Storage", "(RWX PVC 或 containerDisk)"),
        ("✅ 未使用 SR-IOV 介面", None),
        ("✅ 未使用 PCI Passthrough", "(HostDevices / GPU 直通)"),
        ("✅ 未使用 HostDisk", "(非共享的 host 路徑)"),
        ("✅ 未使用 dedicatedCpuPlacement", "(或目標節點也有 CPU Manager)"),
    ]

    cond_cx = 780
    cond_y_start = 60
    cond_spacing = 90
    cond_bw, cond_bh = 340, 54

    cond_ys = []
    for i, (lbl, sub) in enumerate(conditions):
        cy_c = cond_y_start + i * cond_spacing
        cond_ys.append(cy_c)
        body += multiline_box(cond_cx, cy_c, cond_bw, cond_bh, [
            (lbl, 12, TEXT_PRIMARY, True),
            (sub, 11, TEXT_SECONDARY, False),
        ] if sub else [
            (lbl, 13, TEXT_PRIMARY, True),
        ], fill=BOX_FILL, stroke=BOX_STROKE, rx=8)

    # arrows from diamond to each condition
    for cy_c in cond_ys:
        body += arr_path(f"M {dcx+dw//2} {dcy} Q {dcx+dw//2+60} {dcy} {cond_cx-cond_bw//2} {cy_c}")
        
    # edge labels
    body += label_on_arr(dcx + dw//2 + 10, dcy - 14, "必要條件", 10)

    # Result box
    result_cx = 420
    result_cy = 440
    result_bw, result_bh = 260, 50
    body += box(result_cx, result_cy, result_bw, result_bh, "IsMigratable = True",
                fill="#ecfdf5", stroke="#6ee7b7", rx=24)

    # arrows from each condition to result
    for cy_c in cond_ys:
        end_y = cy_c + cond_bh//2 + 4
        body += arr_path(f"M {cond_cx} {end_y} Q {cond_cx-40} {result_cy-20} {result_cx+result_bw//2} {result_cy}")

    w("kubevirt-vmim-requirements.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 4. kubevirt-node-drain-sequence.svg  (sequenceDiagram)
# ─────────────────────────────────────────────────────────────────────────────
def gen_node_drain_sequence():
    parts = [
        ("Admin", "Admin"),
        ("Node", "node01"),
        ("Controller", "KubeVirt Controller"),
        ("VMI", "VMI"),
    ]
    W = 1200; H = 580
    PW, PH = 150, 52
    margin_x = 80
    spacing = (W - 2*margin_x - PW) // (len(parts)-1)
    xs = [margin_x + PW//2 + i*spacing for i in range(len(parts))]
    pi = {p[0]: i for i, p in enumerate(parts)}

    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">節點驅逐觸發 Live Migration 流程</text>\n'

    for i, (eng, chi) in enumerate(parts):
        cx = xs[i]; x = cx - PW//2
        body += f'<rect x="{x}" y="50" width="{PW}" height="{PH}" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1.5"/>\n'
        body += f'<text x="{cx}" y="72" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">{eng}</text>\n'
        body += f'<text x="{cx}" y="90" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{chi}</text>\n'
        body += f'<line x1="{cx}" y1="102" x2="{cx}" y2="{H-30}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>\n'

    def seq_arr(y, frm, to, label, dash=False, self_msg=False):
        fi, ti = pi[frm], pi[to]
        x1, x2 = xs[fi], xs[ti]
        da = ' stroke-dasharray="5,3"' if dash else ''
        mk = 'url(#arrowg)' if dash else 'url(#arrow)'
        sc = "#9ca3af" if dash else ARROW
        if self_msg:
            b = f'<path d="M {x1} {y} Q {x1+60} {y} {x1+60} {y+20} Q {x1+60} {y+40} {x1} {y+40}" stroke="{sc}" stroke-width="1.5"{da} fill="none" marker-end="{mk}"/>\n'
            b += f'<text x="{x1+70}" y="{y+22}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="start">{label}</text>\n'
            return b, y + 40
        mid = (x1+x2)//2
        b = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{sc}" stroke-width="1.5"{da} marker-end="{mk}"/>\n'
        b += f'<text x="{mid}" y="{y-6}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>\n'
        return b, y

    y = 140
    arrows = [
        ("Admin", "Node", "kubectl drain node01", False),
        ("Node", "VMI", "Eviction Request", False),
        ("VMI", "Controller", "觸發 Eviction Hook", False),
        ("Controller", "Controller", "檢查 EvictionStrategy", False, True),
        ("Controller", "Controller", "建立 VirtualMachineInstanceMigration", False, True),
        ("Controller", "VMI", "開始 Live Migration", False),
        ("VMI", "Admin", "Migration Succeeded", True),
        ("Node", "Admin", "Pod Evicted（Migration 完成後）", True),
    ]
    for a in arrows:
        frm, to, lbl = a[0], a[1], a[2]
        dash = a[3] if len(a) > 3 else False
        self_msg = a[4] if len(a) > 4 else False
        svg_s, new_y = seq_arr(y, frm, to, lbl, dash, self_msg)
        body += svg_s
        y = new_y + 52

    w("kubevirt-node-drain-sequence.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 5. kubevirt-migration-bandwidth.svg  (graph LR 3 subgraphs)
# ─────────────────────────────────────────────────────────────────────────────
def gen_migration_bandwidth():
    W, H = 1400, 560
    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">Migration 頻寬設定比較</text>\n'

    groups = [
        {
            "title": "低頻寬環境",
            "nodes": ["bandwidthPerMigration: 256Mi", "completionTimeoutPerGiB: 1600", "allowAutoConverge: true"],
            "cy": 140,
        },
        {
            "title": "高頻寬環境",
            "nodes": ["bandwidthPerMigration: 4Gi", "completionTimeoutPerGiB: 300", "parallelMigrationsPerCluster: 10"],
            "cy": 300,
        },
        {
            "title": "記憶體密集型 VM",
            "nodes": ["allowAutoConverge: true", "allowPostCopy: true（謹慎）", "completionTimeoutPerGiB: 2000"],
            "cy": 460,
        },
    ]

    node_bw, node_bh = 270, 46
    spacing_x = 330
    start_x = 200

    for g in groups:
        cy = g["cy"]
        nodes = g["nodes"]
        # container rect
        cont_x = start_x - 20
        cont_w = len(nodes) * spacing_x + 40
        body += f'<rect x="{cont_x}" y="{cy-50}" width="{cont_w}" height="100" rx="10" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>\n'
        body += f'<text x="{cont_x+12}" y="{cy-32}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" font-weight="700">{g["title"]}</text>\n'

        node_xs = [start_x + node_bw//2 + i*spacing_x for i in range(len(nodes))]
        for i, (lbl, nx) in enumerate(zip(nodes, node_xs)):
            body += box(nx, cy, node_bw, node_bh, lbl, fill=BOX_FILL, stroke=BOX_STROKE, rx=8)
            if i < len(nodes)-1:
                body += arr(nx + node_bw//2, cy, node_xs[i+1] - node_bw//2, cy)

    w("kubevirt-migration-bandwidth.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 6. kubevirt-vmpool-sequence.svg  (rolling update)
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmpool_sequence():
    parts = [
        ("Admin", "Admin"),
        ("Pool", "VirtualMachinePool Controller"),
        ("VM0", "my-pool-0"),
        ("VM1", "my-pool-1"),
        ("VM2", "my-pool-2"),
    ]
    W = 1400; H = 760
    PW, PH = 150, 52
    margin_x = 60
    spacing = (W - 2*margin_x - PW) // (len(parts)-1)
    xs = [margin_x + PW//2 + i*spacing for i in range(len(parts))]
    pi = {p[0]: i for i, p in enumerate(parts)}

    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">VirtualMachinePool 滾動更新流程</text>\n'

    for i, (eng, chi) in enumerate(parts):
        cx = xs[i]; x = cx - PW//2
        body += f'<rect x="{x}" y="50" width="{PW}" height="{PH}" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1.5"/>\n'
        body += f'<text x="{cx}" y="72" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">{eng}</text>\n'
        body += f'<text x="{cx}" y="88" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{chi}</text>\n'
        body += f'<line x1="{cx}" y1="102" x2="{cx}" y2="{H-30}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>\n'

    def seq_arr(y, frm, to, label, dash=False):
        fi, ti = pi[frm], pi[to]
        x1, x2 = xs[fi], xs[ti]
        mid = (x1+x2)//2
        da = ' stroke-dasharray="5,3"' if dash else ''
        mk = 'url(#arrowg)' if dash else 'url(#arrow)'
        sc = "#9ca3af" if dash else ARROW
        b = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{sc}" stroke-width="1.5"{da} marker-end="{mk}"/>\n'
        b += f'<text x="{mid}" y="{y-6}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>\n'
        return b

    y = 140
    arrows = [
        ("Admin", "Pool", "更新 spec.template（新 image）", False),
        ("Pool", "VM2", "停止並刪除 VM2", False),
        ("Pool", "VM2", "建立新 VM2（新 template）", False),
        ("VM2", "Pool", "VM2 Running", True),
        ("Pool", "VM1", "停止並刪除 VM1", False),
        ("Pool", "VM1", "建立新 VM1（新 template）", False),
        ("VM1", "Pool", "VM1 Running", True),
        ("Pool", "VM0", "停止並刪除 VM0", False),
        ("Pool", "VM0", "建立新 VM0（新 template）", False),
        ("VM0", "Pool", "VM0 Running", True),
        ("Pool", "Admin", "滾動更新完成", True),
    ]
    for frm, to, lbl, dash in arrows:
        body += seq_arr(y, frm, to, lbl, dash)
        y += 52

    w("kubevirt-vmpool-sequence.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 7. kubevirt-vmpool-hpa.svg  (graph LR)
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmpool_hpa():
    W, H = 1200, 440
    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">HPA 與 VirtualMachinePool 整合架構</text>\n'

    # HPA box
    hpa_cx, hpa_cy = 160, 220
    body += box(hpa_cx, hpa_cy, 160, 60, "HPA", "(HorizontalPodAutoscaler)",
                fill=ACCENT_FILL, stroke=ACCENT_STROKE, rx=10)

    # MetricsServer
    ms_cx, ms_cy = 480, 120
    body += box(ms_cx, ms_cy, 200, 60, "Metrics Server", "或 Custom Metrics API",
                fill=BOX_FILL, stroke=BOX_STROKE, rx=10)

    # VMIRS/Pool
    vm_cx, vm_cy = 480, 320
    body += box(vm_cx, vm_cy, 220, 60, "VMIRS / VirtualMachinePool",
                fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, rx=10)

    # VMI boxes
    vmi_ys = [160, 290, 420]
    vmi_cx = 850
    for i, vy in enumerate(vmi_ys):
        body += box(vmi_cx, vy, 140, 44, f"VMI-{i}", fill=BOX_FILL, stroke=BOX_STROKE, rx=8)

    # HPA -> MetricsServer
    body += arr_path(f"M {hpa_cx+80} {hpa_cy-20} Q {300} {80} {ms_cx-100} {ms_cy}")
    body += label_on_arr(310, 80, "查詢 metrics", 11)

    # HPA -> VMIRS
    body += arr_path(f"M {hpa_cx+80} {hpa_cy+20} Q {300} {360} {vm_cx-110} {vm_cy}")
    body += label_on_arr(320, 370, "調整 replicas", 11)

    # VMIRS -> VMIs
    for i, vy in enumerate(vmi_ys):
        body += arr_path(f"M {vm_cx+110} {vm_cy} Q {700} {vm_cy} {vmi_cx-70} {vy}")
        body += label_on_arr(720, vm_cy - 6 + (vy-vm_cy)//3, "管理", 10)

    # MetricsServer -> VMIs
    for i, vy in enumerate(vmi_ys):
        body += arr_path(f"M {ms_cx+100} {ms_cy} Q {750} {ms_cy} {vmi_cx+70} {vy}", dash=True, color="#9ca3af")
    body += label_on_arr(820, ms_cy+10, "收集自", 10, TEXT_SECONDARY)

    w("kubevirt-vmpool-hpa.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 8. kubevirt-vmclone-states.svg
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmclone_states():
    W, H = 1300, 780
    BW, BH = 220, 44

    # Main path states
    main_cx = 330
    states_main = [
        (main_cx, 130, "Pending", BOX_FILL, BOX_STROKE),
        (main_cx, 240, "SnapshotInProgress", ACCENT_FILL, ACCENT_STROKE),
        (main_cx, 350, "CreatingTargetVM", ACCENT_FILL, ACCENT_STROKE),
        (main_cx, 460, "RestoreInProgress", ACCENT_FILL, ACCENT_STROKE),
        (main_cx, 600, "Succeeded", "#ecfdf5", "#6ee7b7"),
    ]
    failed_cx, failed_cy = 850, 390
    
    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">VirtualMachineClone 狀態轉換</text>\n'
    body += f'<rect x="{main_cx-140}" y="80" width="{BW+60}" height="560" rx="12" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1" opacity="0.4"/>\n'
    body += f'<text x="{main_cx}" y="70" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">正常路徑</text>\n'

    body += start_node(main_cx, 60)

    for cx, cy, lbl, fill, stroke in states_main:
        body += box(cx, cy, BW, BH, lbl, fill=fill, stroke=stroke, rx=20)

    body += box(failed_cx, failed_cy, 200, 44, "Failed", fill="#fef2f2", stroke="#fca5a5", rx=20)

    body += end_node(main_cx, 680)
    body += end_node(failed_cx, 470)

    # Main arrows
    body += arr(main_cx, 72, main_cx, 108)
    body += label_on_arr(main_cx+120, 92, "建立 VirtualMachineClone", 10)
    body += arr(main_cx, 152, main_cx, 218)
    body += label_on_arr(main_cx+120, 186, "若來源是 VM，先建立臨時快照", 10)
    body += arr(main_cx, 262, main_cx, 328)
    body += label_on_arr(main_cx+130, 296, "快照完成，開始建立目標 VM", 10)
    body += arr(main_cx, 372, main_cx, 438)
    body += label_on_arr(main_cx+120, 406, "VM 框架建立完成，開始還原磁碟", 10)
    body += arr(main_cx, 482, main_cx, 578)
    body += label_on_arr(main_cx+120, 530, "所有磁碟還原完成", 10)
    body += arr(main_cx, 622, main_cx, 668)

    # Shortcut: Pending -> CreatingTargetVM (bypassing SnapshotInProgress)
    body += arr_path(f"M {main_cx-BW//2} {350} L {main_cx-BW//2-40} {350} L {main_cx-BW//2-40} {130} L {main_cx-BW//2} {130}")
    # Actually this is wrong direction - it should go Pending -> CreatingTargetVM directly
    # This is a second outgoing from Pending
    body += arr_path(f"M {main_cx-BW//2-6} {260} C {main_cx-120} {280} {main_cx-120} {330} {main_cx-BW//2} {350}")
    body += label_on_arr(main_cx-160, 305, "若來源已是 Snapshot", 10, TEXT_SECONDARY)

    # Error transitions
    body += arr_path(f"M {main_cx+BW//2} {240} C {720} {240} {720} {370} {failed_cx-100} {failed_cy}")
    body += label_on_arr(700, 240-14, "快照建立失敗", 10, "#ef4444")
    body += arr_path(f"M {main_cx+BW//2} {350} C {720} {350} {720} {375} {failed_cx-100} {failed_cy}")
    body += label_on_arr(700, 350-14, "VM 建立失敗", 10, "#ef4444")
    body += arr_path(f"M {main_cx+BW//2} {460} C {720} {460} {720} {405} {failed_cx-100} {failed_cy}")
    body += label_on_arr(700, 460-14, "磁碟還原失敗", 10, "#ef4444")

    body += arr(failed_cx, failed_cy+22, failed_cx, 458)

    w("kubevirt-vmclone-states.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 9. kubevirt-vmclone-sequence.svg  (3 sections)
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmclone_sequence():
    parts = [
        ("User", "使用者"),
        ("K8s", "Kubernetes API"),
        ("KV", "KubeVirt"),
        ("CSI", "CSI Driver"),
        ("VM", "虛擬機器"),
    ]
    W = 1400; H = 1100
    PW, PH = 140, 52
    margin_x = 60
    spacing = (W - 2*margin_x - PW) // (len(parts)-1)
    xs = [margin_x + PW//2 + i*spacing for i in range(len(parts))]
    pi = {p[0]: i for i, p in enumerate(parts)}

    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">快照 / 還原 / Clone 操作流程</text>\n'

    for i, (eng, chi) in enumerate(parts):
        cx = xs[i]; x = cx - PW//2
        body += f'<rect x="{x}" y="50" width="{PW}" height="{PH}" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1.5"/>\n'
        body += f'<text x="{cx}" y="72" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">{eng}</text>\n'
        body += f'<text x="{cx}" y="88" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{chi}</text>\n'
        body += f'<line x1="{cx}" y1="102" x2="{cx}" y2="{H-30}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>\n'

    def seq_arr(y, frm, to, label, dash=False):
        fi, ti = pi[frm], pi[to]
        x1, x2 = xs[fi], xs[ti]
        mid = (x1+x2)//2
        da = ' stroke-dasharray="5,3"' if dash else ''
        mk = 'url(#arrowg)' if dash else 'url(#arrow)'
        sc = "#9ca3af" if dash else ARROW
        b = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{sc}" stroke-width="1.5"{da} marker-end="{mk}"/>\n'
        b += f'<text x="{mid}" y="{y-6}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>\n'
        return b

    def note_box(y, label):
        nx = xs[0] - 70; nw = xs[-1] - xs[0] + 140
        b = f'<rect x="{nx}" y="{y}" width="{nw}" height="28" rx="4" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1"/>\n'
        b += f'<text x="{nx+nw//2}" y="{y+18}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="600">{label}</text>\n'
        return b

    y = 130
    body += note_box(y, "建立快照流程")
    y += 46
    body += seq_arr(y, "User", "K8s", "建立 VirtualMachineSnapshot")
    y += 44
    body += seq_arr(y, "K8s", "KV", "觸發 snapshot controller")
    y += 44
    body += seq_arr(y, "KV", "VM", "通知 guest agent 執行 fsfreeze")
    y += 44
    body += seq_arr(y, "VM", "KV", "fsfreeze 完成", dash=True)
    y += 44
    body += seq_arr(y, "KV", "CSI", "建立 VolumeSnapshot（每個磁碟）")
    y += 44
    body += seq_arr(y, "CSI", "KV", "VolumeSnapshot 就緒", dash=True)
    y += 44
    body += seq_arr(y, "KV", "VM", "通知 guest agent 執行 fsthaw")
    y += 44
    body += seq_arr(y, "VM", "KV", "fsthaw 完成", dash=True)
    y += 44
    body += seq_arr(y, "KV", "K8s", "更新 VirtualMachineSnapshotContent")
    y += 44
    body += seq_arr(y, "K8s", "User", "status.readyToUse = true", dash=True)
    y += 60

    body += note_box(y, "原地還原流程")
    y += 46
    body += seq_arr(y, "User", "K8s", "停止 VM（runStrategy: Halted）")
    y += 44
    body += seq_arr(y, "User", "K8s", "建立 VirtualMachineRestore")
    y += 44
    body += seq_arr(y, "K8s", "KV", "觸發 restore controller")
    y += 44
    body += seq_arr(y, "KV", "CSI", "從 VolumeSnapshot 建立新 PVC")
    y += 44
    body += seq_arr(y, "CSI", "KV", "PVC 建立完成", dash=True)
    y += 44
    body += seq_arr(y, "KV", "K8s", "更新 VM 使用新 PVC")
    y += 44
    body += seq_arr(y, "K8s", "User", "status.complete = true", dash=True)
    y += 44
    body += seq_arr(y, "User", "K8s", "啟動 VM")
    y += 60

    body += note_box(y, "Clone 流程")
    y += 46
    body += seq_arr(y, "User", "K8s", "建立 VirtualMachineClone")
    y += 44
    body += seq_arr(y, "K8s", "KV", "觸發 clone controller")
    y += 44
    body += seq_arr(y, "KV", "K8s", "建立臨時 VirtualMachineSnapshot")
    y += 44
    body += seq_arr(y, "K8s", "KV", "快照就緒", dash=True)
    y += 44
    body += seq_arr(y, "KV", "K8s", "建立目標 VM 框架")
    y += 44
    body += seq_arr(y, "KV", "CSI", "從快照建立新 PVC（新 VM 使用）")
    y += 44
    body += seq_arr(y, "CSI", "KV", "新 PVC 就緒", dash=True)
    y += 44
    body += seq_arr(y, "KV", "K8s", "更新 Clone status = Succeeded")
    y += 44
    body += seq_arr(y, "K8s", "User", "新 VM 可以啟動", dash=True)

    w("kubevirt-vmclone-sequence.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 10. kubevirt-vm-vmi-relationship.svg (graph TD)
# ─────────────────────────────────────────────────────────────────────────────
def gen_vm_vmi_relationship():
    W, H = 1000, 620
    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">VM / VMI 資源關係圖</text>\n'

    # Positions
    vm_cx, vm_cy = 240, 130
    vmi_cx, vmi_cy = 240, 280
    pod_cx, pod_cy = 240, 430
    qemu_cx, qemu_cy = 240, 560
    dv_cx, dv_cy = 620, 280

    # arrows
    nodes = {
        "vm": (vm_cx, vm_cy, 280, 60, "VirtualMachine (VM)", "宣告式資源", ACCENT_FILL, ACCENT_STROKE),
        "vmi": (vmi_cx, vmi_cy, 280, 60, "VirtualMachineInstance (VMI)", "執行實體", BOX_FILL, BOX_STROKE),
        "pod": (pod_cx, pod_cy, 280, 60, "virt-launcher Pod", "(per VMI)", BOX_FILL, BOX_STROKE),
        "qemu": (qemu_cx, qemu_cy, 280, 60, "QEMU/KVM Process", None, "#fef3c7", "#fcd34d"),
        "dv": (dv_cx, dv_cy, 260, 60, "DataVolume / PVC", None, CONTAINER_FILL, CONTAINER_STROKE),
    }

    for key, (cx, cy, bw, bh, lbl, sub, fill, stroke) in nodes.items():
        body += box(cx, cy, bw, bh, lbl, sub, fill=fill, stroke=stroke, rx=10)

    # VM -> VMI
    body += arr(vm_cx, vm_cy+30, vmi_cx, vmi_cy-30)
    body += label_on_arr(vm_cx+120, (vm_cy+30+vmi_cy-30)//2, "creates / deletes", 11)

    # VMI -> Pod
    body += arr(vmi_cx, vmi_cy+30, pod_cx, pod_cy-30)
    body += label_on_arr(vmi_cx+120, (vmi_cy+30+pod_cy-30)//2, "schedules on", 11)

    # Pod -> QEMU
    body += arr(pod_cx, pod_cy+30, qemu_cx, qemu_cy-30)
    body += label_on_arr(pod_cx+100, (pod_cy+30+qemu_cy-30)//2, "spawns", 11)

    # VM -> DV
    body += arr(vm_cx+140, vm_cy, dv_cx-130, dv_cy-20)
    body += label_on_arr(430, vm_cy-20, "references", 11)

    # DV -> VMI
    body += arr(dv_cx-130, dv_cy, vmi_cx+140, vmi_cy)
    body += label_on_arr(460, dv_cy-12, "provides disk", 11)

    w("kubevirt-vm-vmi-relationship.svg", svg(W, H, body))

# ─────────────────────────────────────────────────────────────────────────────
# 11. kubevirt-vmi-states.svg
# ─────────────────────────────────────────────────────────────────────────────
def gen_vmi_states():
    W, H = 1300, 760
    BW, BH = 200, 44

    main_cx = 340
    states = ["Pending", "Scheduling", "Scheduled", "Running"]
    state_ys = [130, 240, 350, 460]
    succ_cx, succ_cy = 200, 620
    fail_cx, fail_cy = 500, 620
    unk_cx, unk_cy = 860, 400

    body = ""
    body += f'<text x="{W//2}" y="30" font-family="{FONT}" font-size="16" fill="{TEXT_PRIMARY}" text-anchor="middle" font-weight="700">VirtualMachineInstance (VMI) 狀態轉換</text>\n'
    body += f'<rect x="{main_cx-120}" y="80" width="{BW+40}" height="420" rx="12" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1" opacity="0.4"/>\n'
    body += f'<text x="{main_cx}" y="70" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">生命週期</text>\n'

    body += start_node(main_cx, 60)

    fills_s = [BOX_FILL, BOX_FILL, BOX_FILL, ACCENT_FILL]
    strokes_s = [BOX_STROKE, BOX_STROKE, BOX_STROKE, ACCENT_STROKE]
    for lbl, yy, fill, stroke in zip(states, state_ys, fills_s, strokes_s):
        body += box(main_cx, yy, BW, BH, lbl, fill=fill, stroke=stroke, rx=20)

    # Running self-loop (Live Migration)
    run_y = 460
    body += f'<path d="M {main_cx+BW//2} {run_y-15} Q {main_cx+BW//2+80} {run_y-40} {main_cx+BW//2+80} {run_y} Q {main_cx+BW//2+80} {run_y+40} {main_cx+BW//2} {run_y+15}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>\n'
    body += f'<text x="{main_cx+BW//2+90}" y="{run_y+5}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="start">Live Migration 中</text>\n'

    # Succeeded box
    body += box(succ_cx, succ_cy, 180, 44, "Succeeded", fill="#ecfdf5", stroke="#6ee7b7", rx=20)
    # Failed box
    body += box(fail_cx, fail_cy, 180, 44, "Failed", fill="#fef2f2", stroke="#fca5a5", rx=20)
    # Unknown box
    body += box(unk_cx, unk_cy, 180, 44, "Unknown", fill="#fefce8", stroke="#fde047", rx=20)

    # end nodes
    body += end_node(succ_cx, 700)
    body += end_node(fail_cx, 700)
    body += end_node(unk_cx, 480)

    # Main path arrows
    body += arr(main_cx, 72, main_cx, state_ys[0]-22)
    body += label_on_arr(main_cx+120, 90, "建立 VMI", 10)
    for i in range(3):
        body += arr(main_cx, state_ys[i]+22, main_cx, state_ys[i+1]-22)

    arr_lbls = ["尋找可用節點", "節點已選定", "virt-launcher 啟動完成"]
    for i, lbl in enumerate(arr_lbls):
        mid_y = (state_ys[i]+22 + state_ys[i+1]-22)//2
        body += label_on_arr(main_cx+120, mid_y, lbl, 10)

    # Running -> Succeeded
    body += arr_path(f"M {main_cx-BW//2} {run_y} L {succ_cx+90} {succ_cy}")
    body += label_on_arr((main_cx-BW//2+succ_cx+90)//2 - 30, (run_y+succ_cy)//2 - 10, "Guest 正常關機", 10)

    # Running -> Failed
    body += arr_path(f"M {main_cx+BW//2} {run_y+15} C {600} {540} {580} {600} {fail_cx+90} {fail_cy}")
    body += label_on_arr(600, 530, "異常終止", 10, "#ef4444")

    # Succeeded -> end
    body += arr(succ_cx, succ_cy+22, succ_cx, 688)
    # Failed -> end
    body += arr(fail_cx, fail_cy+22, fail_cx, 688)
    # Unknown -> end
    body += arr(unk_cx, unk_cy+22, unk_cx, 468)
    body += label_on_arr(unk_cx+100, 468, "節點失聯", 10)

    # Unknown label
    body += f'<text x="{unk_cx}" y="{unk_cy+60}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">（節點失聯）</text>\n'

    w("kubevirt-vmi-states.svg", svg(W, H, body))

# ─── Run all ─────────────────────────────────────────────────────────────────
gen_vmim_states()
gen_vmim_sequence()
gen_vmim_requirements()
gen_node_drain_sequence()
gen_migration_bandwidth()
gen_vmpool_sequence()
gen_vmpool_hpa()
gen_vmclone_states()
gen_vmclone_sequence()
gen_vm_vmi_relationship()
gen_vmi_states()
print("All SVGs generated.")
