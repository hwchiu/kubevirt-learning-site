#!/usr/bin/env python3
"""Generate all 18 Forklift SVG diagrams in Notion Clean Style 4."""

import os, math

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
NOTE_FILL = "#fffbeb"
NOTE_STROKE = "#fbbf24"
NOTE_TEXT = "#92400e"

OUT = "docs-site/public/diagrams/forklift"
os.makedirs(OUT, exist_ok=True)


def xe(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


DEFS = f"""<defs>
  <marker id="arr" markerWidth="10" markerHeight="8" refX="8.5" refY="3.5" orient="auto">
    <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/>
  </marker>
  <marker id="arrd" markerWidth="10" markerHeight="8" refX="8.5" refY="3.5" orient="auto">
    <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{TEXT_SECONDARY}"/>
  </marker>
  <marker id="arro" markerWidth="10" markerHeight="8" refX="8.5" refY="3.5" orient="auto">
    <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{NOTE_TEXT}"/>
  </marker>
</defs>"""


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'style="font-family:{FONT};background:{BG}">\n{DEFS}\n{body}\n</svg>')


def save(name, content):
    with open(f"{OUT}/{name}.svg", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {name}")


# ── primitives ────────────────────────────────────────────────────────────────

def box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE, rx=6, fs=12):
    lines = str(label).split("\n")
    lh = fs + 4
    sy = y + (h - len(lines) * lh) / 2 + fs
    r = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" rx="{rx}"/>'
    t = "".join(
        f'<text x="{x+w/2}" y="{sy+i*lh}" text-anchor="middle" font-family="{FONT}" font-size="{fs}" fill="{TEXT_PRIMARY}">{xe(ln)}</text>'
        for i, ln in enumerate(lines)
    )
    return r + t


def diam(cx, cy, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE, fs=11):
    hw, hh = w / 2, h / 2
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    p = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    lines = str(label).split("\n")
    lh = fs + 3
    tot = (len(lines) - 1) * lh
    t = "".join(
        f'<text x="{cx}" y="{cy - tot/2 + i*lh + 4}" text-anchor="middle" font-family="{FONT}" font-size="{fs}" fill="{TEXT_PRIMARY}">{xe(ln)}</text>'
        for i, ln in enumerate(lines)
    )
    return p + t


def cont(x, y, w, h, title, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE):
    r = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" rx="10"/>'
    t = f'<text x="{x+12}" y="{y+18}" font-family="{FONT}" font-size="12" font-weight="bold" fill="{TEXT_PRIMARY}">{xe(title)}</text>'
    return r + t


def lbl(x, y, s, fs=10, fill=TEXT_SECONDARY, anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{fs}" fill="{fill}">{xe(s)}</text>'


def title(x, y, s, fs=15):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" font-size="{fs}" font-weight="bold" fill="{TEXT_PRIMARY}">{xe(s)}</text>'


def arr(x1, y1, x2, y2, label="", dashed=False, color=None):
    c = color or (TEXT_SECONDARY if dashed else ARROW)
    mk = "arrd" if dashed else "arr"
    da = ' stroke-dasharray="6,3"' if dashed else ""
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist > 0:
        x2e = x2 - dx / dist * 9
        y2e = y2 - dy / dist * 9
    else:
        x2e, y2e = x2, y2
    ln = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2e:.1f}" y2="{y2e:.1f}" stroke="{c}" stroke-width="1.5"{da} marker-end="url(#{mk})"/>'
    lb = ""
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if abs(dx) >= abs(dy):
            my -= 8
        else:
            mx += 18
        lb = f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{xe(label)}</text>'
    return ln + lb


def arr_path(d, dashed=False):
    mk = "arrd" if dashed else "arr"
    c = TEXT_SECONDARY if dashed else ARROW
    da = ' stroke-dasharray="6,3"' if dashed else ""
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="1.5"{da} marker-end="url(#{mk})"/>'


def startdot(cx, cy):
    return f'<circle cx="{cx}" cy="{cy}" r="10" fill="{ARROW}"/>'


def enddot(cx, cy):
    return (f'<circle cx="{cx}" cy="{cy}" r="12" fill="{BG}" stroke="{ARROW}" stroke-width="2.5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="{ARROW}"/>')


# ── Sequence helper ────────────────────────────────────────────────────────────

class Seq:
    def __init__(self, participants, min_w=1300, p_w=120, p_h=44, msg_gap=52, pad=55):
        self.ps = participants
        self.p_w = p_w
        self.p_h = p_h
        self.msg_gap = msg_gap
        self.pad = pad
        n = len(participants)
        col_w = max(p_w + 55, (min_w - 2 * pad) / n)
        self.W = max(min_w, int(n * col_w + 2 * pad))
        self.col_w = (self.W - 2 * pad) / n
        self.cx = {pid: pad + (i + 0.5) * self.col_w for i, (pid, _) in enumerate(participants)}
        self.y0 = pad + p_h + 35
        self.cy = self.y0
        self.items = []

    def msg(self, frm, to, label="", ret=False):
        x1, x2, y = self.cx[frm], self.cx[to], self.cy
        c = TEXT_SECONDARY if ret else ARROW
        mk = "arrd" if ret else "arr"
        da = ' stroke-dasharray="5,3"' if ret else ""
        dx = x2 - x1
        x2e = x2 - (9 if dx > 0 else -9)
        self.items.append(f'<line x1="{x1:.1f}" y1="{y}" x2="{x2e:.1f}" y2="{y}" stroke="{c}" stroke-width="1.5"{da} marker-end="url(#{mk})"/>')
        if label:
            mx = (x1 + x2) / 2
            self.items.append(f'<text x="{mx:.1f}" y="{y-6}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{xe(label)}</text>')
        self.cy += self.msg_gap

    def loop_box(self, label):
        y = self.cy
        lx = self.pad - 22
        rw = self.W - 2 * self.pad + 44
        self.items.append(f'<rect x="{lx}" y="{y}" width="{rw}" height="22" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5" rx="4"/>')
        self.items.append(f'<text x="{lx+8}" y="{y+15}" font-family="{FONT}" font-size="10" font-weight="bold" fill="{TEXT_PRIMARY}">{xe(label)}</text>')
        self.cy += 30

    def note(self, label, *pids):
        xs = [self.cx[p] for p in pids] if pids else list(self.cx.values())
        lx = min(xs) - self.p_w / 2 + 5
        rx = max(xs) + self.p_w / 2 - 5
        nw = max(rx - lx, 220)
        y = self.cy
        nh = 28
        self.items.append(f'<rect x="{lx:.1f}" y="{y}" width="{nw:.1f}" height="{nh}" fill="{NOTE_FILL}" stroke="{NOTE_STROKE}" stroke-width="1.5" rx="4"/>')
        self.items.append(f'<text x="{lx+nw/2:.1f}" y="{y+17}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{NOTE_TEXT}">{xe(label)}</text>')
        self.cy += nh + 12

    def sep(self, n=20):
        self.cy += n

    def render(self):
        H = self.cy + 55
        p_boxes = "".join(box(self.cx[pid] - self.p_w / 2, self.pad, self.p_w, self.p_h, plabel) for pid, plabel in self.ps)
        lifelines = "".join(
            f'<line x1="{self.cx[pid]:.1f}" y1="{self.pad+self.p_h}" x2="{self.cx[pid]:.1f}" y2="{H-25}" stroke="#d1d5db" stroke-width="1" stroke-dasharray="4,3"/>'
            for pid, _ in self.ps
        )
        body = p_boxes + lifelines + "".join(self.items)
        return svg(self.W, H, body)


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 1: forklift-system-arch
# ═══════════════════════════════════════════════════════════════════════════════

def d01_system_arch():
    W, H = 1560, 700
    p = [title(W / 2, 30, "Forklift 系統架構")]

    # Left: Sources
    p.append(cont(30, 50, 210, 590, "來源平台"))
    src_list = ["VMware vSphere", "oVirt/RHV", "OpenStack", "Hyper-V", "OVA 檔案", "OpenShift (OCP)"]
    SW, SH = 185, 42
    SX = 42
    src_ys = [90, 170, 250, 330, 410, 490]
    for slabel, sy in zip(src_list, src_ys):
        p.append(box(SX, sy, SW, SH, slabel))

    # Middle: Controller
    p.append(cont(290, 50, 940, 590, "Forklift Controller"))
    # node layout: (label, x, y, w, h)
    NW, NH = 230, 52
    adp = (310, 105, NW, NH)
    api = (740, 105, NW, NH)
    sch = (310, 270, NW, NH)
    pop = (310, 460, NW, NH)
    v2v = (680, 460, NW, NH)

    def bc(node):
        return node[0] + node[2] / 2, node[1] + node[3] / 2

    ctrl_nodes = [
        ("Provider Adapters\n(Inventory 收集)", adp),
        ("forklift-api\n(REST+Webhooks)", api),
        ("Migration Scheduler\n(Itinerary 狀態機)", sch),
        ("Volume Populators\n(oVirt/OpenStack/vSphere)", pop),
        ("virt-v2v\n(Guest OS 轉換)", v2v),
    ]
    for clabel, nd in ctrl_nodes:
        p.append(box(*nd, clabel))

    # Right: Target
    p.append(cont(1280, 50, 245, 590, "目標環境"))
    cdi = (1295, 180, 210, 52)
    kv  = (1295, 330, 210, 52)
    tvm = (1295, 470, 210, 44)
    p.append(box(*cdi, "CDI\n(DataVolume)"))
    p.append(box(*kv,  "KubeVirt\n(VirtualMachine)"))
    p.append(box(*tvm, "目標 VM"))

    # Source → Adapters
    src_labels = ["govmomi", "go-ovirt", "gophercloud", "WinRM", "OVF解析", "K8s API"]
    adp_cx, adp_cy = bc(adp)
    for i, (sy, slbl) in enumerate(zip(src_ys, src_labels)):
        p.append(arr(SX + SW, sy + SH / 2, adp[0], adp_cy + (i - 2.5) * 6, slbl))

    # Internal controller arrows
    p.append(arr(bc(adp)[0], adp[1] + NH, bc(sch)[0], sch[1]))
    p.append(arr(bc(sch)[0], sch[1] + NH, bc(pop)[0], pop[1]))
    # scheduler → v2v: go right then down
    p.append(arr_path(f"M {sch[0]+NW},{bc(sch)[1]} L {v2v[0]+NW/2},{bc(sch)[1]} L {v2v[0]+NW/2},{v2v[1]}"))
    # API dashed → Scheduler
    p.append(arr(bc(api)[0], api[1] + NH, bc(sch)[0] + 40, sch[1], "Webhooks 驗証/變更", dashed=True))

    # Populators/V2V → CDI
    p.append(arr(pop[0] + NW, bc(pop)[1], cdi[0], bc(cdi)[1]))
    p.append(arr(v2v[0] + NW, bc(v2v)[1], cdi[0], bc(cdi)[1] + 10))
    # CDI → KubeVirt → VM
    p.append(arr(bc(cdi)[0], cdi[1] + cdi[3], bc(kv)[0], kv[1]))
    p.append(arr(bc(kv)[0], kv[1] + kv[3], bc(tvm)[0], tvm[1]))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 2: forklift-migration-pipeline (sequence)
# ═══════════════════════════════════════════════════════════════════════════════

def d02_migration_pipeline():
    s = Seq([
        ("user", "使用者"), ("api", "forklift-api"), ("ctrl", "Plan Controller"),
        ("itin", "Itinerary 狀態機"), ("pop", "Volume Populator"),
        ("v2v", "virt-v2v"), ("cdi", "CDI"), ("kv", "KubeVirt"),
    ], min_w=1400, p_w=115, msg_gap=50)

    s.msg("user", "api", "建立 Migration CR")
    s.msg("api", "ctrl", "Reconcile Plan")
    s.msg("ctrl", "itin", "選擇 Itinerary (Cold/Warm/Live)")
    s.sep(10)
    s.loop_box("loop  每個 VM")
    s.msg("itin", "ctrl", "下一步驟 (Phase)")
    s.msg("ctrl", "pop", "建立 DataVolume / 複製磁碟")
    s.msg("pop", "cdi", "寫入 PVC")
    s.msg("ctrl", "v2v", "啟動 Guest OS 轉換")
    s.msg("v2v", "ctrl", "轉換完成", ret=True)
    s.msg("ctrl", "kv", "建立 VirtualMachine")
    s.sep(5)
    s.msg("ctrl", "user", "Migration 完成", ret=True)

    return s.render()


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 3: forklift-cold-migration (state diagram)
# ═══════════════════════════════════════════════════════════════════════════════

def d03_cold_migration():
    W, H = 1200, 860
    p = [title(W / 2, 28, "Cold Migration 狀態流程")]

    BW, BH = 200, 40

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=20, fs=11)

    def bc_y(y): return y + BH / 2

    # Column centers
    C1, C2, C3 = 220, 600, 920

    # Row y positions
    rows = [60, 140, 220, 300, 380, 460, 560, 640, 720, 790]
    r = rows

    p.append(startdot(C1, r[0]))
    p.append(bx(C1, r[1], "Started"))
    p.append(bx(C1, r[2], "PreHook", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(bx(C1, r[3], "StorePowerState"))
    p.append(bx(C1, r[4], "PowerOffSource"))
    p.append(bx(C1, r[5], "WaitForPowerOff"))
    p.append(bx(C1, r[6], "CreateDataVolumes"))
    p.append(diam(C1, r[7] + 20, 220, 56, "disk_path?"))
    p.append(bx(C2, r[6], "CopyDisks\n(CDIDiskCopy)", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(bx(C3, r[6], "AllocateDisks\n(VirtV2vDiskCopy)", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(bx(C3, r[5], "CreateGuestConversionPod"))
    p.append(bx(C3, r[4], "ConvertGuest"))
    p.append(bx(C3, r[3], "CopyDisksVirtV2V"))

    p.append(bx(C2, r[4], "CreateVM"))
    p.append(bx(C2, r[3], "PostHook", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(bx(C2, r[2], "Completed"))
    p.append(enddot(C2, r[1]))

    # Arrows along C1
    p.append(arr(C1, r[0] + 10, C1, r[1]))
    p.append(arr(C1, r[1] + BH, C1, r[2], "HasPreHook"))
    p.append(arr(C1, r[2] + BH, C1, r[3], "無Hook"))
    p.append(arr(C1, r[3] + BH, C1, r[4]))
    p.append(arr(C1, r[4] + BH, C1, r[5]))
    p.append(arr(C1, r[5] + BH, C1, r[6]))
    p.append(arr(C1, r[6] + BH, C1, r[7] - 8))
    # from diamond to CopyDisks and AllocateDisks
    p.append(arr(C1 - 110, r[7] + 20, C2 - BW / 2, r[6] + BH / 2, "CDIDiskCopy"))
    p.append(arr(C1 + 110, r[7] + 20, C3 - BW / 2, r[6] + BH / 2, "VirtV2vDiskCopy"))
    # CopyDisks → CreateVM
    p.append(arr(C2, r[6], C2, r[4] + BH))
    # AllocateDisks → CreateGuestConversionPod (go up)
    p.append(arr(C3, r[6], C3, r[5] + BH))
    p.append(arr(C3, r[5], C3, r[4] + BH))
    p.append(arr(C3, r[4], C3, r[3] + BH))
    # CopyDisksVirtV2V → CreateVM
    p.append(arr(C3 - BW / 2, r[3] + BH / 2, C2 + BW / 2, r[4] + BH / 2))
    # CreateVM → PostHook
    p.append(arr(C2, r[4], C2, r[3] + BH, "HasPostHook"))
    p.append(arr(C2, r[3], C2, r[2] + BH))
    # CreateVM → Completed (no hook)
    p.append(arr(C2 + BW / 2 + 10, r[4] + BH / 2, C2 + BW / 2 + 50, r[4] + BH / 2))
    p.append(arr_path(f"M {C2+BW/2+50},{r[4]+BH/2} L {C2+BW/2+50},{r[2]+BH/2} L {C2+BW/2+10},{r[2]+BH/2}", dashed=True))
    p.append(lbl(C2 + BW / 2 + 80, r[3] + 10, "無Hook"))
    p.append(arr(C2, r[2], C2, r[1] + 5))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 4: forklift-warm-migration (state diagram)
# ═══════════════════════════════════════════════════════════════════════════════

def d04_warm_migration():
    W, H = 1300, 1000
    p = [title(W / 2, 28, "Warm Migration 狀態流程")]

    BW, BH = 195, 38

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=18, fs=11)

    C1, C2 = 280, 750
    rows = [60, 120, 190, 260, 330, 410, 490, 570, 650, 730, 810, 880, 940]
    r = rows

    # Phase labels
    p.append(cont(40, 175, W - 80, 195, "Precopy Init"))
    p.append(cont(40, 395, W - 80, 205, "Precopy Loop"))
    p.append(cont(40, 625, W - 80, 270, "Cutover"))

    p.append(startdot(C1, r[0]))
    p.append(bx(C1, r[1], "Started"))
    p.append(diam(C1, r[2] + 19, 210, 52, "HasPreHook?"))
    p.append(bx(C1, r[3], "PreHook", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(bx(C1, r[4], "CreateInitialSnapshot"))
    p.append(bx(C1, r[5], "WaitForInitialSnapshot"))
    p.append(bx(C1, r[6], "StoreInitialSnapshotDeltas\n(vSphere) / CreateDVs"))
    p.append(bx(C1, r[7], "CreateDataVolumes"))
    p.append(bx(C1, r[8], "CopyDisks"))
    p.append(bx(C1, r[9], "CopyingPaused"))
    p.append(bx(C1, r[10], "RemovePreviousSnapshot\n/ CreateSnapshot"))
    p.append(bx(C1, r[11], "AddCheckpoint"))

    # Cutover path
    p.append(bx(C2, r[8], "StorePowerState"))
    p.append(bx(C2, r[9], "PowerOffSource"))
    p.append(bx(C2, r[10], "WaitForPowerOff"))
    p.append(bx(C2, r[11], "CreateFinalSnapshot"))
    p.append(bx(C2, r[12], "AddFinalCheckpoint / Finalize"))

    p.append(bx(C1, r[12], "CreateVM / PostHook", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(enddot(C1, r[12] + BH + 20))

    # Arrows
    p.append(arr(C1, r[0] + 10, C1, r[1]))
    p.append(arr(C1, r[1] + BH, C1, r[2] - 8))
    p.append(arr(C1 - 50, r[2] + 19, C1 - 80, r[3] + BH / 2))
    p.append(arr(C1 - 80, r[3] + BH / 2, C1 - 80, r[4] + BH / 2))
    p.append(arr(C1 - 80, r[4] + BH / 2, C1 - BW / 2, r[4] + BH / 2, "HasPreHook→"))
    p.append(arr(C1 + 50, r[2] + 19, C1, r[4] + BH / 2, "無Hook"))
    p.append(arr(C1, r[4] + BH, C1, r[5]))
    p.append(arr(C1, r[5] + BH, C1, r[6]))
    p.append(arr(C1, r[6] + BH, C1, r[7]))
    p.append(arr(C1, r[7] + BH, C1, r[8]))
    p.append(arr(C1, r[8] + BH, C1, r[9]))
    p.append(arr(C1, r[9] + BH, C1, r[10]))
    p.append(arr(C1, r[10] + BH, C1, r[11]))
    # Loop back
    p.append(arr_path(f"M {C1-BW/2},{r[11]+BH/2} L {C1-BW/2-40},{r[11]+BH/2} L {C1-BW/2-40},{r[8]+BH/2} L {C1-BW/2},{r[8]+BH/2}"))
    p.append(lbl(C1 - BW / 2 - 55, r[9] + 20, "繼續"))
    # Cutover trigger
    p.append(arr(C1 + BW / 2, r[11] + BH / 2, C2 - BW / 2, r[8] + BH / 2, "觸發Cutover"))
    p.append(arr(C2, r[8] + BH, C2, r[9]))
    p.append(arr(C2, r[9] + BH, C2, r[10]))
    p.append(arr(C2, r[10] + BH, C2, r[11]))
    p.append(arr(C2, r[11] + BH, C2, r[12]))
    # Finalize → CreateVM
    p.append(arr(C2 - BW / 2, r[12] + BH / 2, C1 + BW / 2, r[12] + BH / 2))
    p.append(arr(C1, r[12] + BH, C1, r[12] + BH + 15))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 5: forklift-live-migration (state diagram)
# ═══════════════════════════════════════════════════════════════════════════════

def d05_live_migration():
    W, H = 1300, 900
    p = [title(W / 2, 28, "Live Migration 狀態流程 (OCP-to-OCP)")]

    BW, BH = 210, 38

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=18, fs=11)

    C1, C2 = 300, 820

    p.append(cont(40, 180, W - 80, 330, "準備目標階段 (prepare_target)"))
    p.append(cont(40, 540, W - 80, 195, "同步階段 (synchronization)"))

    rows = [60, 120, 190, 260, 330, 395, 460, 525, 590, 650, 710, 770, 825]
    r = rows

    p.append(startdot(C1, r[0]))
    p.append(bx(C1, r[1], "Started"))
    p.append(diam(C1, r[2] + 19, 220, 52, "FlagPreHook?"))
    p.append(bx(C1, r[3], "PreHook", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(bx(C1, r[4], "CreateSecrets"))
    p.append(bx(C1, r[5], "CreateConfigMaps"))
    p.append(bx(C1, r[6], "EnsurePreference"))
    p.append(bx(C1, r[7], "EnsureInstanceType"))
    p.append(bx(C1, r[8], "EnsureDataVolumes"))
    p.append(bx(C1, r[9], "EnsurePersistentVolumeClaims"))
    p.append(bx(C1, r[10], "CreateTarget"))
    p.append(bx(C1, r[11], "SetOwnerReferences"))
    p.append(bx(C1, r[12], "CreateServiceExports\n/ WaitForTargetVMI"))
    p.append(bx(C2, r[11], "CreateVMIMigrations"))
    p.append(bx(C2, r[12], "WaitForStateTransfer"))

    p.append(bx(C1, 845, "PostHook / Completed", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(enddot(C1, 845 + BH + 15))

    # Arrows
    p.append(arr(C1, r[0] + 10, C1, r[1]))
    p.append(arr(C1, r[1] + BH, C1, r[2] - 8))
    p.append(arr(C1 - 50, r[2] + 19, C1 - 80, r[3] + BH / 2, "HasPreHook"))
    p.append(arr(C1 - 80, r[3] + BH / 2, C1 - 80, r[4] + BH / 2))
    p.append(arr(C1 - 80, r[4] + BH / 2, C1 - BW / 2, r[4] + BH / 2))
    p.append(arr(C1 + 50, r[2] + 19, C1, r[4] + BH / 2, "無Hook"))
    for i in range(4, 12):
        p.append(arr(C1, r[i] + BH, C1, r[i + 1]))
    # Branch at r[12] (CreateServiceExports/WaitForTargetVMI)
    p.append(arr(C1 + BW / 2, r[12] + BH / 2, C2 - BW / 2, r[11] + BH / 2, "同叢集"))
    p.append(arr(C2, r[11] + BH, C2, r[12]))
    # Merge back
    p.append(arr(C2 - BW / 2, r[12] + BH / 2, C1 + BW / 2, 845 + BH / 2))
    p.append(arr(C1, r[12] + BH, C1, 845, "Submariner/同叢集"))
    p.append(arr(C1, 845 + BH, C1, 845 + BH + 10))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 6: forklift-plan-reconcile (flowchart TD)
# ═══════════════════════════════════════════════════════════════════════════════

def d06_plan_reconcile():
    W, H = 1100, 1100
    p = [title(W / 2, 28, "Plan Controller Reconcile 流程")]

    BW, BH = 220, 42
    DW, DH = 240, 60

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=6, fs=11)

    def dm(cx, y, label):
        return diam(cx, y + DH / 2, DW, DH, label)

    C1, C2 = 280, 750

    rows = [55, 120, 200, 280, 360, 440, 530, 620, 710, 800, 890, 980, 1055]
    r = rows

    p.append(startdot(C1, r[0]))
    p.append(bx(C1, r[1], "Reconcile 入口"))
    p.append(dm(C1, r[2], "Fetch Plan"))
    p.append(bx(C2, r[2] + 10, "cleanupOrphanedResources", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(dm(C1, r[3], "Archived 且已標記?"))
    p.append(bx(C2, r[3] + 10, "return 跳過", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(dm(C1, r[4], "Succeeded 且未Archived?"))
    p.append(dm(C1, r[5], "postpone 等待依賴"))
    p.append(bx(C2, r[5] + 10, "Requeue 延後重試", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(bx(C1, r[6], "Validation 驗證 Plan"))
    p.append(bx(C2, r[6] + 5, "標記 Archived→return", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(bx(C1, r[7], "setPopulatorDataSourceLabels"))
    p.append(dm(C1, r[8], "plan.Spec.Archived?"))
    p.append(bx(C2, r[8] + 10, "archive 清理\n+設定 Archived Condition", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(bx(C1, r[9], "設定 Ready Condition"))
    p.append(bx(C1, r[10], "Stage Conditions"))
    p.append(bx(C1, r[11], "execute 執行遷移"))
    p.append(bx(C1, r[12], "updatePlanStatus 持久化狀態"))

    # Main flow
    p.append(arr(C1, r[0] + 10, C1, r[1]))
    p.append(arr(C1, r[1] + BH, C1, r[2]))
    p.append(arr(C1 + DW / 2, r[2] + DH / 2, C2 - BW / 2, r[2] + BH / 2 + 10, "NotFound"))
    p.append(arr(C1, r[2] + DH, C1, r[3], "Found"))
    p.append(arr(C1 + DW / 2, r[3] + DH / 2, C2 - BW / 2, r[3] + BH / 2 + 10, "是"))
    p.append(arr(C1, r[3] + DH, C1, r[4], "否"))
    p.append(arr(C1 + DW / 2, r[4] + DH / 2, C2 - BW / 2, r[3] + BH / 2 + 10, "是"))
    p.append(arr(C1, r[4] + DH, C1, r[5], "否"))
    p.append(arr(C1 + DW / 2, r[5] + DH / 2, C2 - BW / 2, r[5] + BH / 2 + 10, "尚未就緒"))
    p.append(arr(C1, r[5] + DH, C1, r[6], "全部就緒"))
    p.append(arr(C1 + BW / 2, r[6] + BH / 2, C2 - BW / 2, r[6] + BH / 2 + 5, "dangling archived"))
    p.append(arr(C1, r[6] + BH, C1, r[7], "驗證通過"))
    p.append(arr(C1, r[7] + BH, C1, r[8]))
    p.append(arr(C1 + DW / 2, r[8] + DH / 2, C2 - BW / 2, r[8] + BH / 2 + 10, "是"))
    p.append(arr(C1, r[8] + DH, C1, r[9], "否"))
    p.append(arr(C1, r[9] + BH, C1, r[10]))
    p.append(arr(C1, r[10] + BH, C1, r[11]))
    p.append(arr(C1, r[11] + BH, C1, r[12]))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 7: forklift-webhook-rbac (sequence)
# ═══════════════════════════════════════════════════════════════════════════════

def d07_webhook_rbac():
    s = Seq([
        ("user", "使用者"), ("k8s", "Kubernetes API"),
        ("wh", "Forklift Webhook"), ("sar", "SubjectAccessReview"),
    ], min_w=900, p_w=135, msg_gap=50)

    s.msg("user", "k8s", "建立/更新 Plan")
    s.msg("k8s", "wh", "AdmissionReview (含 UserInfo)")
    s.msg("wh", "sar", "PermitUser(get, source provider)")
    s.msg("sar", "wh", "Allowed / Denied", ret=True)
    s.msg("wh", "sar", "PermitUser(get, dest provider)")
    s.msg("sar", "wh", "Allowed / Denied", ret=True)
    s.msg("wh", "sar", "PermitUser(create, VM in target ns)")
    s.msg("sar", "wh", "Allowed / Denied", ret=True)
    s.msg("wh", "k8s", "AdmissionResponse", ret=True)
    s.msg("k8s", "user", "結果", ret=True)

    return s.render()


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 8: forklift-populator-flow (flowchart TD)
# ═══════════════════════════════════════════════════════════════════════════════

def d08_populator_flow():
    W, H = 1050, 1080
    p = [title(W / 2, 28, "Volume Populator 流程")]

    BW, BH = 235, 44
    DW, DH = 260, 62

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=6, fs=11)

    def dm(cx, y, label):
        return diam(cx, y + DH / 2, DW, DH, label)

    C1, C2 = 320, 780

    rows = [55, 115, 185, 255, 330, 415, 500, 580, 660, 740, 820, 900, 980]
    r = rows

    p.append(startdot(C1, r[0]))
    p.append(bx(C1, r[1], "使用者建立PVC\ndataSourceRef 指向 Populator CR"))
    p.append(bx(C1, r[2], "Controller 偵測 PVC"))
    p.append(dm(C1, r[3], "驗證 StorageClass\n非 in-tree provisioner"))
    p.append(bx(C2, r[3] + 10, "跳過", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(bx(C1, r[4], "處理 WaitForFirstConsumer\nBinding Mode"))
    p.append(bx(C1, r[5], "建立 prime PVC\n前綴: prime-"))
    p.append(bx(C1, r[6], "建立 Populator Pod\n前綴: populate-"))
    p.append(bx(C1, r[7], "監控 Pod 進度\n每5秒擷取 HTTPS :8443 metrics"))
    p.append(dm(C1, r[8], "Pod 狀態?"))
    p.append(bx(C1, r[9], "Patch PV ClaimRef\n指向原始 PVC"))
    p.append(dm(C2, r[8], "重試次數 < 3?\nvSphere 不重試"))
    p.append(bx(C2, r[9], "標記失敗", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(bx(C1, r[10], "等待 prime PVC 進入 Lost 狀態"))
    p.append(bx(C1, r[11], "刪除 prime PVC"))
    p.append(bx(C1, r[12], "PV 重新綁定至原始 PVC\nPopulation 完成"))

    p.append(arr(C1, r[0] + 10, C1, r[1]))
    p.append(arr(C1, r[1] + BH, C1, r[2]))
    p.append(arr(C1, r[2] + BH, C1, r[3]))
    p.append(arr(C1 + DW / 2, r[3] + DH / 2, C2 - BW / 2, r[3] + BH / 2 + 10, "驗證失敗"))
    p.append(arr(C1, r[3] + DH, C1, r[4], "驗證通過"))
    p.append(arr(C1, r[4] + BH, C1, r[5]))
    p.append(arr(C1, r[5] + BH, C1, r[6]))
    p.append(arr(C1, r[6] + BH, C1, r[7]))
    p.append(arr(C1, r[7] + BH, C1, r[8]))
    # Running loop back
    p.append(arr_path(f"M {C1-BW/2},{r[8]+DH/2} L {C1-BW/2-40},{r[8]+DH/2} L {C1-BW/2-40},{r[7]+BH/2} L {C1-BW/2},{r[7]+BH/2}"))
    p.append(lbl(C1 - BW / 2 - 60, r[7] + DH / 2 + 20, "Running"))
    p.append(arr(C1, r[8] + DH, C1, r[9], "Succeeded"))
    # Failed → retry check
    p.append(arr(C1 + DW / 2, r[8] + DH / 2, C2 - DW / 2, r[8] + DH / 2, "Failed"))
    p.append(arr(C2, r[8] + DH, C2, r[9] + BH / 4, "否"))
    p.append(arr(C2 - DW / 2, r[8] - 5, C1 + BW / 2, r[6] + BH / 2, "是→重建"))
    p.append(arr(C1, r[9] + BH, C1, r[10]))
    p.append(arr(C1, r[10] + BH, C1, r[11]))
    p.append(arr(C1, r[11] + BH, C1, r[12]))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 9: forklift-provider-adapter (factory pattern graph)
# ═══════════════════════════════════════════════════════════════════════════════

def d09_provider_adapter():
    W, H = 1100, 560
    p = [title(W / 2, 28, "Provider Adapter Factory Pattern")]

    BW, BH = 190, 42
    # Top: adapter.New
    p.append(box(W / 2 - 110, 55, 220, BH, "adapter.New", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, fs=13))
    # Middle: switch
    p.append(diam(W / 2, 165, 240, 60, "Switch Provider"))

    providers = [
        ("VSphere", "vsphere.Adapter"),
        ("OVirt", "ovirt.Adapter"),
        ("OpenStack", "openstack.Adapter"),
        ("OpenShift", "ocp.Adapter"),
        ("OVA", "ova.Adapter"),
        ("EC2", "ec2adapter.New"),
        ("HyperV", "hyperv.Adapter"),
    ]
    n = len(providers)
    xs = [80 + i * (W - 100) / (n - 1) for i in range(n)]
    py = 330

    for i, (ptype, pimpl) in enumerate(providers):
        p.append(box(xs[i] - BW / 2, py, BW, BH + 4, f"{ptype}\n{pimpl}", fill=BOX_FILL, stroke=BOX_STROKE, fs=10))
        p.append(arr(xs[i], 195, xs[i], py, ptype))

    # All → Builder/Client/Validator
    p.append(box(W / 2 - 130, 455, 260, BH, "Builder / Client / Validator", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, fs=12))
    for x in xs:
        p.append(arr(x, py + BH + 4, W / 2, 455))

    # Top arrow
    p.append(arr(W / 2, 55 + BH, W / 2, 135))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 10: forklift-vsphere-scheduler (flowchart TD)
# ═══════════════════════════════════════════════════════════════════════════════

def d10_vsphere_scheduler():
    W, H = 1050, 900
    p = [title(W / 2, 28, "vSphere Migration Scheduler")]

    BW, BH = 240, 44
    DW, DH = 260, 64

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=6, fs=11)

    def dm(cx, y, label):
        return diam(cx, y + DH / 2, DW, DH, label)

    C1, C2 = 340, 800

    rows = [55, 115, 190, 270, 360, 450, 545, 635, 720, 800, 865]
    r = rows

    p.append(startdot(C1, r[0]))
    p.append(bx(C1, r[1], "Start"))
    p.append(bx(C1, r[2], "取得 Package Mutex"))
    p.append(bx(C1, r[3], "buildInFlight: 掃描所有同Provider Plan\n累加每Host正在傳輸的磁碟數"))
    p.append(bx(C1, r[4], "buildPending: 收集當前Plan\n尚未開始的VM按Host分組"))
    p.append(bx(C1, r[5], "schedulable: 逐 Host 檢查"))
    p.append(dm(C1, r[6], "Host inFlight\n< MaxInFlight?"))
    p.append(bx(C2, r[6] + 10, "跳過此 Host", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(dm(C1, r[7], "VM cost+inFlight\n<= MaxInFlight?"))
    p.append(bx(C1, r[8], "加入可排程清單", fill="#f0fdf4", stroke="#bbf7d0"))
    p.append(dm(C2, r[7], "VM cost > MaxInFlight\n且 Host 完全閒置?"))
    p.append(bx(C2, r[8] + 10, "跳過此 VM", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(bx(C1, r[9], "回傳第一個可排程 VM"))
    p.append(enddot(C1, r[10]))

    p.append(arr(C1, r[0] + 10, C1, r[1]))
    p.append(arr(C1, r[1] + BH, C1, r[2]))
    p.append(arr(C1, r[2] + BH, C1, r[3]))
    p.append(arr(C1, r[3] + BH, C1, r[4]))
    p.append(arr(C1, r[4] + BH, C1, r[5]))
    p.append(arr(C1, r[5] + BH, C1, r[6]))
    p.append(arr(C1 + DW / 2, r[6] + DH / 2, C2 - BW / 2, r[6] + BH / 2 + 10, "否"))
    p.append(arr(C1, r[6] + DH, C1, r[7], "是"))
    p.append(arr(C1, r[7] + DH, C1, r[8], "是"))
    p.append(arr(C1 + DW / 2, r[7] + DH / 2, C2 - DW / 2, r[7] + DH / 2, "否"))
    p.append(arr(C2, r[7] + DH, C2, r[8] + BH / 4, "否"))
    p.append(arr(C2 - DW / 2, r[7] + DH / 4, C1 + BW / 2, r[8] + BH / 4, "是"))
    p.append(arr(C1, r[8] + BH, C1, r[9]))
    p.append(arr(C1, r[9] + BH, C1, r[10]))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 11: forklift-warm-precopy (sequence)
# ═══════════════════════════════════════════════════════════════════════════════

def d11_warm_precopy():
    s = Seq([
        ("ctrl", "Forklift\nController"), ("client", "Provider\nClient"),
        ("src", "來源VM\n(vSphere)"), ("cdi", "CDI\nDataVolume"), ("tgt", "目標叢集"),
    ], min_w=1100, p_w=120, msg_gap=50)

    s.note("=== Precopy 迴圈 ===")
    s.loop_box("loop  每次 Precopy 直到 Cutover")
    s.msg("ctrl", "client", "CreateSnapshot(vmRef)")
    s.msg("client", "src", "建立 VM 快照")
    s.msg("src", "client", "snapshotId, taskId", ret=True)
    s.msg("ctrl", "client", "CheckSnapshotReady()")
    s.msg("client", "ctrl", "ready=true", ret=True)
    s.msg("ctrl", "client", "GetSnapshotDeltas(snapshot)")
    s.msg("client", "ctrl", "map[disk]deltaId", ret=True)
    s.msg("ctrl", "cdi", "SetCheckpoints(precopies, DVs, final=false)")
    s.msg("cdi", "src", "透過 VDDK 傳輸 delta 區塊")
    s.msg("cdi", "ctrl", "傳輸完成", ret=True)
    s.msg("ctrl", "client", "RemoveSnapshot(snapshot)")
    s.sep(5)
    s.note("記錄 Precopy, 排程 NextPrecopyAt")
    s.sep(20)
    s.note("=== Cutover 階段 ===")
    s.msg("ctrl", "client", "CreateSnapshot(vmRef)")
    s.msg("ctrl", "client", "PowerOff(vmRef)")
    s.msg("client", "src", "關閉 VM")
    s.msg("ctrl", "cdi", "SetCheckpoints(precopies, DVs, final=true)")
    s.msg("cdi", "src", "傳輸最終 delta")
    s.msg("cdi", "ctrl", "完成", ret=True)
    s.msg("ctrl", "tgt", "建立 KubeVirt VirtualMachine")
    s.msg("ctrl", "client", "Finalize() 清理快照")

    return s.render()


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 12: forklift-virt-v2v-pipeline (flowchart TD)
# ═══════════════════════════════════════════════════════════════════════════════

def d12_virt_v2v_pipeline():
    W, H = 1050, 1050
    p = [title(W / 2, 28, "virt-v2v 轉換 Pipeline")]

    BW, BH = 240, 44
    DW, DH = 260, 64

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=6, fs=11)

    def dm(cx, y, label):
        return diam(cx, y + DH / 2, DW, DH, label)

    C1, C2 = 330, 790

    rows = [55, 110, 175, 250, 330, 420, 510, 590, 670, 745, 820, 895, 975]
    r = rows

    p.append(startdot(C1, r[0]))
    p.append(bx(C1, r[1], "entrypoint.go: main"))
    p.append(bx(C1, r[2], "載入 AppConfig 環境變數"))
    p.append(bx(C1, r[3], "linkCertificates: 設定 CA 憑證"))
    p.append(bx(C1, r[4], "createV2vOutputDir: 建立工作目錄"))
    p.append(bx(C1, r[5], "NewConversion: 偵測磁碟"))
    p.append(dm(C1, r[6], "IsRemoteInspection?"))
    p.append(bx(C2, r[6] + 8, "RunRemoteV2vInspection\nvirt-v2v-inspector+VDDK"))
    p.append(dm(C1, r[7], "IsInPlace?"))
    p.append(dm(C1, r[8], "LibvirtUrl 存在?"))
    p.append(bx(C1, r[9], "GetDomainXML\n從 Libvirt 取得 Domain XML"))
    p.append(bx(C1, r[10], "RunVirtV2vInPlace\nvirt-v2v-in-place -i libvirtxml"))
    p.append(bx(C2, r[8] + 8, "RunVirtV2vInPlaceDisk\nvirt-v2v-in-place -i disk"))
    p.append(bx(C2, r[7] + 8, "RunVirtV2v\nvirt-v2v+virt-v2v-monitor"))
    p.append(bx(C1, r[11], "RunVirtV2VInspection\nvirt-v2v-inspector"))
    p.append(bx(C1, r[12], "RunCustomize\nvirt-customize: 驅動安裝/客製化"))

    p.append(arr(C1, r[0] + 10, C1, r[1]))
    for i in range(1, 6):
        p.append(arr(C1, r[i] + BH, C1, r[i + 1]))
    p.append(arr(C1 + DW / 2, r[6] + DH / 2, C2 - BW / 2, r[6] + BH / 2 + 8, "是"))
    p.append(arr(C1, r[6] + DH, C1, r[7], "否"))
    p.append(arr(C1 + DW / 2, r[7] + DH / 2, C2 - BW / 2, r[7] + BH / 2 + 8, "否→FullV2V"))
    p.append(arr(C1, r[7] + DH, C1, r[8], "是"))
    p.append(arr(C1, r[8] + DH, C1, r[9], "是"))
    p.append(arr(C1 + DW / 2, r[8] + DH / 2, C2 - BW / 2, r[8] + BH / 2 + 8, "否→InPlaceDisk"))
    p.append(arr(C1, r[9] + BH, C1, r[10]))
    # Converge to RunVirtV2VInspection
    p.append(arr(C1, r[10] + BH, C1, r[11]))
    p.append(arr(C2, r[7] + BH + 8, C2, r[10] + BH / 2))
    p.append(arr(C2, r[10] + BH / 2, C1 + BW / 2, r[11] + BH / 2))
    p.append(arr(C2, r[8] + BH + 8, C2 - 5, r[10] + BH / 2))
    p.append(arr(C1, r[11] + BH, C1, r[12]))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 13: forklift-storage-mapping (flowchart LR)
# ═══════════════════════════════════════════════════════════════════════════════

def d13_storage_mapping():
    W, H = 1300, 480
    p = [title(W / 2, 28, "Storage Mapping 流程")]

    # 3 columns: Source, StorageMap, Target
    p.append(cont(30, 55, 300, 380, "來源"))
    p.append(cont(380, 55, 400, 380, "StorageMap"))
    p.append(cont(840, 55, 430, 380, "目標 Kubernetes"))

    # Source nodes
    BW, BH = 250, 44
    p.append(box(50, 140, BW, BH, "vSphere Datastore A"))
    p.append(box(50, 270, BW, BH, "vSphere Datastore B"))

    # StorageMap nodes
    SMW = 340
    p.append(box(400, 140, SMW, BH, "StoragePair 1\n+ OffloadPlugin", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(box(400, 270, SMW, BH, "StoragePair 2"))

    # Target nodes
    TW = 370
    p.append(box(860, 140, TW, BH, "StorageClass: ontap-san\nVolumeMode: Block"))
    p.append(box(860, 270, TW, BH, "StorageClass: ceph-rbd\nVolumeMode: Filesystem"))

    # Side annotations
    p.append(box(400, 360, SMW, BH, "XCOPY Offload\n陣列內部複製", fill=NOTE_FILL, stroke=NOTE_STROKE))
    p.append(box(860, 360, TW, BH, "CDI 標準傳輸\n網路複製", fill=NOTE_FILL, stroke=NOTE_STROKE))

    # Arrows: source → map
    p.append(arr(50 + BW, 140 + BH / 2, 400, 140 + BH / 2))
    p.append(arr(50 + BW, 270 + BH / 2, 400, 270 + BH / 2))
    # map → target
    p.append(arr(400 + SMW, 140 + BH / 2, 860, 140 + BH / 2))
    p.append(arr(400 + SMW, 270 + BH / 2, 860, 270 + BH / 2))
    # dashed to annotations
    p.append(arr(400 + SMW / 2, 140 + BH, 400 + SMW / 2, 360, dashed=True))
    p.append(arr(860 + TW / 2, 270 + BH, 860 + TW / 2, 360, dashed=True))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 14: forklift-integration-overview (graph TB)
# ═══════════════════════════════════════════════════════════════════════════════

def d14_integration_overview():
    W, H = 1400, 700
    p = [title(W / 2, 28, "Forklift Integration Overview")]

    # Row 1: Forklift Controller
    p.append(cont(30, 50, 620, 130, "Forklift Controller"))
    p.append(box(60, 90, 250, 50, "Migration Controller", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(box(360, 90, 250, 50, "Plan Controller", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))

    # Row 2: Adapters
    p.append(cont(30, 210, 1340, 130, "Adapter Layer"))
    adapters = ["vSphere Adapter", "oVirt Adapter", "OpenStack Adapter", "Hyper-V Adapter", "OVA Adapter"]
    aw = 230
    for i, a in enumerate(adapters):
        ax = 50 + i * (aw + 30)
        p.append(box(ax, 250, aw, 50, a))

    # Row 3: Target
    p.append(cont(30, 370, 620, 130, "目標平台"))
    p.append(box(55, 410, 165, 50, "KubeVirt API"))
    p.append(box(240, 410, 180, 50, "CDI DataVolume"))
    p.append(box(440, 410, 185, 50, "Volume Populators"))

    # Row 4: Sources
    p.append(cont(700, 370, 670, 130, "來源平台"))
    sources = ["vCenter/ESXi", "oVirt Engine", "OpenStack", "Hyper-V Host", "OVA Files"]
    sw = 110
    for i, s in enumerate(sources):
        sx = 715 + i * (sw + 15)
        p.append(box(sx, 410, sw, 50, s, fs=10))

    # Controller arrows
    p.append(arr(185, 115, 360, 115))
    # Plan → Adapters
    adp_xs = [50 + i * (aw + 30) + aw / 2 for i in range(5)]
    for ax in adp_xs:
        p.append(arr(485, 140, ax, 250))
    # Adapters → Targets
    tgt_xs = [55 + 82, 240 + 90, 440 + 92]
    for ax in adp_xs[:2]:
        for tx in tgt_xs:
            p.append(arr(ax, 300, tx, 410, dashed=True))
    for ax in adp_xs[2:3]:
        for tx in tgt_xs[::2]:
            p.append(arr(ax, 300, tx, 410, dashed=True))
    for ax in adp_xs[3:4]:
        for tx in tgt_xs[:2]:
            p.append(arr(ax, 300, tx, 410, dashed=True))
    for ax in adp_xs[4:]:
        for tx in tgt_xs[:2]:
            p.append(arr(ax, 300, tx, 410, dashed=True))
    # Adapters → Sources
    src_xs = [715 + i * (sw + 15) + sw / 2 for i in range(5)]
    for i, ax in enumerate(adp_xs):
        p.append(arr(ax, 300, src_xs[i], 410))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 15: forklift-cdi-sources (graph LR)
# ═══════════════════════════════════════════════════════════════════════════════

def d15_cdi_sources():
    W, H = 1350, 520
    p = [title(W / 2, 28, "CDI Source Types 與 Volume Populators")]

    # Left: CDI source types
    p.append(cont(30, 55, 380, 420, "CDI Source Types"))
    src_nodes = [
        ("VDDK Source\nvSphere", 50, 100),
        ("ImageIO Source\noVirt", 50, 190),
        ("HTTP Source\nOCP-to-OCP", 50, 280),
        ("Blank Source\nHyperV/OVA", 50, 370),
    ]
    for label, x, y in src_nodes:
        p.append(box(x, y, 340, 54, label))

    # Middle: targets
    mid_nodes = [
        ("vSphere", 520, 100),
        ("oVirt", 520, 190),
        ("SourceCluster", 520, 280),
        ("LocalDisk", 520, 370),
    ]
    for label, x, y in mid_nodes:
        p.append(box(x, y, 170, 54, label, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))

    # Right: Volume Populators
    p.append(cont(770, 55, 550, 420, "Volume Populators"))
    pop_nodes = [
        ("VSphereXcopy\nVolumePopulator", 790, 100),
        ("Openstack\nVolumePopulator", 790, 210),
        ("Ovirt\nVolumePopulator", 790, 320),
    ]
    for label, x, y in pop_nodes:
        p.append(box(x, y, 230, 54, label))

    # Storage targets
    stor_nodes = [
        ("StorageArray\n(ESXi Copy Offload)", 1060, 100),
        ("OpenStack Storage\n(Cinder/Glance)", 1060, 210),
        ("oVirt Storage\n(ovirt-img)", 1060, 320),
    ]
    for label, x, y in stor_nodes:
        p.append(box(x, y, 250, 54, label, fill=BOX_FILL, stroke=BOX_STROKE, fs=10))

    # Source → mid
    src_labels = ["VDDK SDK", "ImageIO API", "HTTP Download", "virt-v2v填入"]
    for (_, sx, sy), (_, mx, my), slbl in zip(src_nodes, mid_nodes, src_labels):
        p.append(arr(sx + 340, sy + 27, mx, my + 27, slbl))
    # Populators → storage
    pop_labels = ["ESXi Copy Offload", "Cinder/Glance", "ovirt-img"]
    for (_, px, py), (_, stx, sty), plbl in zip(pop_nodes, stor_nodes, pop_labels):
        p.append(arr(px + 230, py + 27, stx, sty + 27, plbl))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 16: forklift-cdi-checkpoint (sequence)
# ═══════════════════════════════════════════════════════════════════════════════

def d16_cdi_checkpoint():
    s = Seq([
        ("fc", "Forklift\nController"), ("src", "Source\nPlatform"), ("cdi", "CDI\nDataVolume"),
    ], min_w=900, p_w=130, msg_gap=50)

    s.msg("fc", "src", "CreateSnapshot (precopy-1)")
    s.msg("src", "fc", "snapshot-id-1", ret=True)
    s.msg("fc", "cdi", "SetCheckpoints(current=snap-1, previous='')")
    s.msg("cdi", "src", "傳輸完整磁碟資料")
    s.msg("cdi", "fc", "Paused (checkpoint copied)", ret=True)
    s.sep(10)
    s.msg("fc", "src", "CreateSnapshot (precopy-2)")
    s.msg("src", "fc", "snapshot-id-2", ret=True)
    s.msg("fc", "cdi", "SetCheckpoints(current=snap-2, previous=snap-1)")
    s.msg("cdi", "src", "傳輸差異資料 (delta)")
    s.msg("cdi", "fc", "Paused (checkpoint copied)", ret=True)
    s.sep(10)
    s.msg("fc", "cdi", "SetCheckpoints(final=true)")
    s.msg("cdi", "src", "傳輸最後一批差異")
    s.msg("cdi", "fc", "Succeeded", ret=True)

    return s.render()


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 17: forklift-vsphere-client (graph TD)
# ═══════════════════════════════════════════════════════════════════════════════

def d17_vsphere_client():
    W, H = 850, 560
    p = [title(W / 2, 28, "vSphere Client 選擇邏輯")]

    BW, BH = 200, 42
    DW, DH = 240, 60

    def bx(cx, y, label, fill=BOX_FILL, stroke=BOX_STROKE):
        return box(cx - BW / 2, y, BW, BH, label, fill, stroke, rx=6, fs=12)

    def dm(cx, y, label):
        return diam(cx, y, DW, DH, label)

    C1, C2 = 280, 640
    p.append(startdot(C1, 55))
    p.append(bx(C1, 80, "getClient"))
    p.append(dm(C1, 180, "virt-v2v 啟用?"))
    p.append(bx(C2, 180, "使用 Provider SDK", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(dm(C1, 300, "SDK = ESXI?"))
    p.append(dm(C1, 420, "ESXi Host 可用?"))
    p.append(bx(C1, 490 + 20, "建立/快取 ESXi Client", fill="#f0fdf4", stroke="#bbf7d0"))

    p.append(arr(C1, 55 + 10, C1, 80))
    p.append(arr(C1, 80 + BH, C1, 180))
    p.append(arr(C1 + DW / 2, 180 + DH / 2, C2 - BW / 2, 180 + DH / 2, "是"))
    p.append(arr(C1, 180 + DH, C1, 300, "否"))
    p.append(arr(C1 + DW / 2, 300 + DH / 2, C2 - BW / 2, 200 + DH / 2, "是"))
    p.append(arr(C1, 300 + DH, C1, 420, "否"))
    p.append(arr(C1 + DW / 2, 420 + DH / 2, C2 - BW / 2, 220 + DH / 2, "否"))
    p.append(arr(C1, 420 + DH, C1, 510, "是"))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram 18: forklift-tekton-pipelines (graph LR)
# ═══════════════════════════════════════════════════════════════════════════════

def d18_tekton_pipelines():
    W, H = 1500, 620
    p = [title(W / 2, 28, "Forklift Tekton Pipelines")]

    # Left: Pipelines
    p.append(cont(30, 55, 260, 510, "Tekton Pipelines"))
    p.append(box(50, 160, 220, 64, "pull-request 管線\nPR 觸發", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    p.append(box(50, 370, 220, 64, "push 管線\nmerge 觸發", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))

    # Right: Components
    p.append(cont(360, 55, 1110, 510, "元件"))
    components = [
        ("API", 380, 100, 100, 42),
        ("forklift-controller", 510, 100, 170, 42),
        ("forklift-operator", 710, 100, 165, 42),
        ("ova-provider-server", 905, 100, 175, 42),
        ("ova-proxy", 1110, 100, 120, 42),
        ("virt-v2v", 1255, 100, 130, 42),
        ("ovirt-populator", 380, 200, 155, 42),
        ("openstack-populator", 560, 200, 185, 42),
        ("vsphere-xcopy-populator", 775, 200, 210, 42),
        ("populator-controller", 1010, 200, 185, 42),
        ("forklift-validation", 1220, 200, 175, 42),
        ("hyperv-provider-server", 380, 300, 200, 42),
        ("forklift-cli-download", 610, 300, 200, 42),
    ]
    for label, x, y, w, h in components:
        p.append(box(x, y, w, h, label, fs=10))

    # Arrows: both pipelines → all components
    PR_CX, PR_CY = 160, 192
    PUSH_CX, PUSH_CY = 160, 402

    for label, x, y, w, h in components:
        cx, cy = x + w / 2, y + h / 2
        p.append(arr(270, PR_CY, x, cy))
        p.append(arr(270, PUSH_CY, x, cy, dashed=True))

    return svg(W, H, "".join(p))


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

diagrams = [
    ("forklift-system-arch", d01_system_arch),
    ("forklift-migration-pipeline", d02_migration_pipeline),
    ("forklift-cold-migration", d03_cold_migration),
    ("forklift-warm-migration", d04_warm_migration),
    ("forklift-live-migration", d05_live_migration),
    ("forklift-plan-reconcile", d06_plan_reconcile),
    ("forklift-webhook-rbac", d07_webhook_rbac),
    ("forklift-populator-flow", d08_populator_flow),
    ("forklift-provider-adapter", d09_provider_adapter),
    ("forklift-vsphere-scheduler", d10_vsphere_scheduler),
    ("forklift-warm-precopy", d11_warm_precopy),
    ("forklift-virt-v2v-pipeline", d12_virt_v2v_pipeline),
    ("forklift-storage-mapping", d13_storage_mapping),
    ("forklift-integration-overview", d14_integration_overview),
    ("forklift-cdi-sources", d15_cdi_sources),
    ("forklift-cdi-checkpoint", d16_cdi_checkpoint),
    ("forklift-vsphere-client", d17_vsphere_client),
    ("forklift-tekton-pipelines", d18_tekton_pipelines),
]

print(f"Generating {len(diagrams)} SVG diagrams...")
for name, fn in diagrams:
    save(name, fn())
print(f"\nDone! SVGs saved to {OUT}/")
