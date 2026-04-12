#!/usr/bin/env python3
"""Generate 17 SVG diagrams for NetBox documentation."""

import os

OUT = "docs-site/public/diagrams/netbox"
os.makedirs(OUT, exist_ok=True)

# Style constants
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

ARROW_MARKER = '''<marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
</marker>'''

ARROW_REV_MARKER = '''<marker id="arrow-rev" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto">
  <polygon points="8.5 0.5, 0 3.5, 8.5 6.5" fill="#3b82f6"/>
</marker>'''

def svg_header(w, h, title=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">
<defs>
{ARROW_MARKER}
{ARROW_REV_MARKER}
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/>
'''

def svg_footer():
    return '</svg>\n'

def box(x, y, w, h, label, sublabel=None, fill=BOX_FILL, stroke=BOX_STROKE, rx=6, fontsize=13):
    cx = x + w // 2
    cy = y + h // 2
    txt = f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" fill="{TEXT_PRIMARY}" font-size="{fontsize}" font-family="{FONT}">{label}</text>'
    if sublabel:
        txt = f'<text x="{cx}" y="{y + h//2 - 8}" text-anchor="middle" dominant-baseline="central" fill="{TEXT_PRIMARY}" font-size="{fontsize}" font-family="{FONT}">{label}</text>'
        txt += f'<text x="{cx}" y="{y + h//2 + 10}" text-anchor="middle" dominant-baseline="central" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{sublabel}</text>'
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            + txt)

def diamond(cx, cy, hw, hh, label, fontsize=13):
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    return (f'<polygon points="{pts}" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>'
            + f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" fill="{TEXT_PRIMARY}" font-size="{fontsize}" font-family="{FONT}">{label}</text>')

def arrow(x1, y1, x2, y2, label="", label_pos=0.5, dashed=False, color=ARROW):
    dash = ' stroke-dasharray="6,3"' if dashed else ''
    mx = x1 + (x2-x1)*label_pos
    my = y1 + (y2-y1)*label_pos - 8
    lbl = f'<text x="{mx}" y="{my}" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{label}</text>' if label else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5"{dash} marker-end="url(#arrow)"/>'
            + lbl)

def curved_arrow(x1, y1, x2, y2, label="", dx=40, color=ARROW):
    mx = (x1 + x2) // 2
    my = (y1 + y2) // 2
    d = f"M {x1} {y1} C {x1+dx} {y1}, {x2+dx} {y2}, {x2} {y2}"
    lbl = f'<text x="{mx + dx//2 + 5}" y="{my}" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{label}</text>' if label else ''
    return f'<path d="{d}" stroke="{color}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>' + lbl

def path_arrow(d, label="", lx=0, ly=0, dashed=False, color=ARROW):
    dash = ' stroke-dasharray="6,3"' if dashed else ''
    lbl = f'<text x="{lx}" y="{ly}" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{label}</text>' if label else ''
    return f'<path d="{d}" stroke="{color}" stroke-width="1.5" fill="none"{dash} marker-end="url(#arrow)"/>' + lbl

def container(x, y, w, h, label, fontsize=12):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5" stroke-dasharray="6,3"/>'
            + f'<text x="{x+10}" y="{y+18}" fill="{TEXT_SECONDARY}" font-size="{fontsize}" font-family="{FONT}" font-weight="600">{label}</text>')

def subtitle(text, x=20, y=30):
    return f'<text x="{x}" y="{y}" fill="{TEXT_SECONDARY}" font-size="12" font-family="{FONT}">{text}</text>'

def cylinder(x, y, w, h, label, fontsize=13):
    rx = w // 2
    ry = 12
    cx = x + w // 2
    cy = y + h // 2
    return (f'<rect x="{x}" y="{y+ry}" width="{w}" height="{h-ry}" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>'
            + f'<ellipse cx="{cx}" cy="{y+ry}" rx="{rx}" ry="{ry}" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>'
            + f'<ellipse cx="{cx}" cy="{y+h}" rx="{rx}" ry="{ry}" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>'
            + f'<text x="{cx}" y="{cy+ry//2}" text-anchor="middle" dominant-baseline="central" fill="{TEXT_PRIMARY}" font-size="{fontsize}" font-family="{FONT}">{label}</text>')

# ─── 1. netbox-prefix-hierarchy-update.svg ──────────────────────────────────
def gen_1():
    w, h = 1200, 750
    s = svg_header(w, h)
    s += subtitle("netbox-prefix-hierarchy-update — Prefix 層級更新流程")

    # Nodes
    # A: Prefix save/delete  cx=600 y=60 w=220 h=40
    s += box(490, 55, 220, 40, "Prefix save / delete")
    # B: diamond at cx=600, y=160
    s += diamond(600, 170, 130, 40, "是否為新建或變更?")
    # C: update_parents_children  cx=180 y=300
    s += box(50, 305, 220, 40, "update_parents_children")
    # D: update_children_depth  cx=550 y=300
    s += box(450, 305, 220, 40, "update_children_depth")
    # I: skip  cx=950 y=300
    s += box(870, 305, 160, 40, "跳過更新")
    # J: old prefix update  cx=560 y=430
    s += box(400, 430, 320, 40, "對舊 prefix 也執行更新")
    # E: cx=120 y=450
    s += box(10, 480, 310, 40, "查詢所有 parent prefixes annotate_hierarchy")
    # F: cx=120 y=560
    s += box(50, 570, 220, 40, "bulk_update _children 欄位")
    # G: cx=550 y=530
    s += box(430, 530, 310, 40, "查詢所有 child prefixes annotate_hierarchy")
    # H: cx=550 y=630
    s += box(470, 630, 220, 40, "bulk_update _depth 欄位")

    # Arrows
    # A → B
    s += arrow(600, 95, 600, 130)
    # B --是--> C (left)
    s += path_arrow(f"M 470 170 L 160 170 L 160 305", "是", lx=310, ly=160)
    # B --是--> D (down)
    s += path_arrow(f"M 560 195 L 560 305", "是", lx=540, ly=255)
    # B --否--> I (right)
    s += path_arrow(f"M 730 170 L 950 170 L 950 305", "否", lx=850, ly=160)
    # B --修改且 prefix 改變--> J
    s += path_arrow(f"M 640 205 L 640 360 L 560 360 L 560 430", "修改且 prefix 改變", lx=700, ly=395)
    # C → E
    s += arrow(160, 345, 160, 480)
    # E → F
    s += arrow(165, 520, 165, 570)
    # D → G
    s += arrow(560, 345, 560, 530)
    # G → H
    s += arrow(580, 570, 580, 630)
    # J → C (left)
    s += path_arrow(f"M 400 450 L 160 450 L 160 345", "", lx=280, ly=440)
    # J → D (down)
    s += path_arrow(f"M 590 470 L 590 490 L 560 490 L 560 530", "", lx=575, ly=490)

    s += svg_footer()
    return s

# ─── 2. netbox-ipam-erd.svg ──────────────────────────────────────────────────
def gen_2():
    w, h = 900, 450
    s = svg_header(w, h)
    s += subtitle("netbox-ipam-erd — IPAM 核心模型關聯")

    # Entity boxes (w=140, h=40)
    bw, bh = 140, 40
    # Row 1
    s += box(50, 80, bw, bh, "VRF")
    s += box(260, 80, bw, bh, "RouteTarget")
    s += box(500, 80, bw, bh, "IPAddress")
    # Row 2
    s += box(50, 220, bw, bh, "Aggregate")
    s += box(300, 220, bw, bh, "Prefix")
    s += box(550, 220, bw, bh, "IPRange")
    # Row 3
    s += box(50, 360, bw, bh, "RIR")

    # Relationships
    # VRF → Prefix
    s += path_arrow(f"M 190 120 L 190 200 L 300 200 L 300 220", "contains", lx=240, ly=185)
    # VRF → IPAddress
    s += path_arrow(f"M 190 80 L 500 80", "contains", lx=340, ly=70)
    # VRF ←→ RouteTarget
    s += path_arrow(f"M 260 95 L 190 95", "import/export_targets", lx=225, ly=83)
    # Prefix → IPAddress
    s += path_arrow(f"M 440 230 L 500 230", "child IPs", lx=465, ly=218)
    # Prefix → IPRange
    s += path_arrow(f"M 440 250 L 530 250 L 530 260 L 550 260", "child ranges", lx=490, ly=248)
    # Aggregate → Prefix (contains)
    s += path_arrow(f"M 190 235 L 300 235", "contains", lx=245, ly=225)
    # RIR → Aggregate
    s += arrow(120, 360, 120, 260)
    # Label on RIR→Aggregate
    s += f'<text x="135" y="315" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">belongs to</text>'

    s += svg_footer()
    return s

# ─── 3. netbox-dcim-class-hierarchy.svg ─────────────────────────────────────
def gen_3():
    w, h = 1100, 430
    s = svg_header(w, h)
    s += subtitle("netbox-dcim-class-hierarchy — 設備類別層次結構")

    # Manufacturer box
    s += box(30, 150, 200, 40, "Manufacturer")
    s += f'<text x="130" y="200" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">name: str</text>'

    # DeviceType box (tall)
    s += box(310, 80, 230, 160, "DeviceType", fontsize=14)
    lines = ["manufacturer: FK", "model: str", "u_height: Decimal", "is_full_depth: bool", "subdevice_role: str"]
    for i, l in enumerate(lines):
        s += f'<text x="425" y="{115 + i*22}" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{l}</text>'

    # Device box (tall)
    s += box(630, 60, 230, 200, "Device", fontsize=14)
    dlines = ["device_type: FK", "role: FK", "site: FK", "rack: FK", "position: Decimal", "face: str", "status: str"]
    for i, l in enumerate(dlines):
        s += f'<text x="745" y="{95 + i*22}" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{l}</text>'

    # Rack box
    s += box(940, 150, 130, 40, "Rack")

    # Arrows (inheritance / FK style)
    # Manufacturer →1..*→ DeviceType
    s += arrow(230, 170, 310, 170)
    s += f'<text x="260" y="163" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">1..*</text>'
    # DeviceType →1..*→ Device
    s += arrow(540, 160, 630, 160)
    s += f'<text x="580" y="153" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">1..*</text>'
    # Device →*..0..1→ Rack
    s += arrow(860, 170, 940, 170)
    s += f'<text x="900" y="163" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">*..0..1</text>'

    s += svg_footer()
    return s

# ─── 4. netbox-cable-path.svg ────────────────────────────────────────────────
def gen_4():
    w, h = 1400, 380
    s = svg_header(w, h)
    s += subtitle("netbox-cable-path — Cable 穿越 Patch Panel 的路徑")

    # Container: Device A
    s += container(30, 80, 200, 180, "Device A")
    s += box(60, 170, 140, 40, "Interface 1")

    # Container: Patch Panel 1
    s += container(310, 80, 240, 220, "Patch Panel 1")
    s += box(340, 140, 160, 40, "Front Port 1")
    s += box(340, 240, 160, 40, "Rear Port 1")
    # dashed mapping line
    s += f'<line x1="420" y1="180" x2="420" y2="240" stroke="{CONTAINER_STROKE}" stroke-width="1.5" stroke-dasharray="4,3"/>'
    s += f'<text x="435" y="215" fill="{TEXT_SECONDARY}" font-size="10" font-family="{FONT}">PortMapping</text>'

    # Container: Patch Panel 2
    s += container(640, 80, 240, 220, "Patch Panel 2")
    s += box(670, 140, 160, 40, "Rear Port 2")
    s += box(670, 240, 160, 40, "Front Port 3")
    s += f'<line x1="750" y1="180" x2="750" y2="240" stroke="{CONTAINER_STROKE}" stroke-width="1.5" stroke-dasharray="4,3"/>'
    s += f'<text x="765" y="215" fill="{TEXT_SECONDARY}" font-size="10" font-family="{FONT}">PortMapping</text>'

    # Container: Device B
    s += container(980, 80, 200, 180, "Device B")
    s += box(1010, 170, 140, 40, "Interface 2")

    # Arrows between containers
    # IF1 → FP1
    s += path_arrow(f"M 200 190 L 340 160", "Cable A", lx=265, ly=163)
    # RP1 → RP2
    s += path_arrow(f"M 500 260 L 670 155", "Cable B", lx=585, ly=195)
    # FP3 → IF2
    s += path_arrow(f"M 830 260 L 1010 190", "Cable C", lx=925, ly=210)

    s += svg_footer()
    return s

# ─── 5. netbox-custom-fields-cache.svg ──────────────────────────────────────
def gen_5():
    w, h = 1500, 280
    s = svg_header(w, h)
    s += subtitle("netbox-custom-fields-cache — Custom Field 快取存取流程")

    bw, bh = 200, 40
    # Nodes LR
    s += box(30, 120, bw, bh, "Model Instance")
    s += box(270, 120, bw, bh, "CustomFieldsMixin.cf")
    s += box(510, 120, 230, bh, "CustomFieldManager.get_for_model")
    s += diamond(870, 140, 110, 40, "Request Cache 命中?")
    s += box(1060, 80, 160, 40, "回傳快取結果")
    s += box(1060, 170, 160, 40, "查詢 DB")
    s += box(1260, 170, 180, 40, "寫入 Request Cache")
    # Final box
    s += box(1260, 80, 180, 40, "逐一 deserialize")

    # Arrows
    s += arrow(230, 140, 270, 140)
    s += arrow(470, 140, 510, 140)
    s += arrow(740, 140, 760, 140)
    # D --是--> E
    s += path_arrow(f"M 870 100 L 870 80 L 1060 80", "是", lx=970, ly=70)
    # D --否--> F
    s += path_arrow(f"M 870 180 L 1060 180 L 1060 185", "否", lx=960, ly=173)
    # F → G
    s += arrow(1220, 190, 1260, 190)
    # G → E (up)
    s += path_arrow(f"M 1350 170 L 1350 100 L 1220 100", "", lx=1290, ly=90)
    # E → deserialize
    s += arrow(1240, 100, 1260, 100)
    # deserialize → final result (show as text)
    s += f'<text x="1480" y="100" text-anchor="middle" fill="{TEXT_PRIMARY}" font-size="12" font-family="{FONT}">&#123;&#39;field&#39;: v&#125;</text>'

    s += svg_footer()
    return s

# ─── 6. netbox-change-log-flow.svg ──────────────────────────────────────────
def gen_6():
    w, h = 1600, 720
    s = svg_header(w, h)
    s += subtitle("netbox-change-log-flow — 變更日誌記錄流程（Sequence）")

    participants = [
        ("Client", 130),
        ("CoreMiddleware", 330),
        ("event_tracking", 530),
        ("View", 730),
        ("Model", 930),
        ("ObjectChange", 1130),
    ]

    # Participant boxes
    for name, cx in participants:
        s += box(cx - 80, 50, 160, 44, name, fontsize=12)
        # Lifeline
        s += f'<line x1="{cx}" y1="94" x2="{cx}" y2="{h-60}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="5,3"/>'

    def seq_arrow(from_cx, to_cx, y, label, dashed=False):
        return path_arrow(f"M {from_cx} {y} L {to_cx} {y}", label, lx=(from_cx+to_cx)//2, ly=y-8, dashed=dashed)

    def self_arrow(cx, y, label):
        return (f'<path d="M {cx} {y} C {cx+60} {y}, {cx+60} {y+35}, {cx} {y+35}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>'
                + f'<text x="{cx+65}" y="{y+20}" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{label}</text>')

    steps = [
        ("arrow", 130, 330, 140, "HTTP Request"),
        ("arrow", 330, 530, 175, "enter context"),
        ("self", 530, 210, "set request_id, init queue"),
        ("arrow", 330, 730, 265, "process request"),
        ("arrow", 730, 930, 305, "snapshot() — 拍攝 prechange"),
        ("arrow", 730, 930, 345, "save()"),
        ("arrow", 930, 1130, 380, "to_objectchange(UPDATE)"),
        ("self", 1130, 415, "儲存 pre/post data"),
        ("arrow_dash", 730, 330, 465, "response"),
        ("self", 530, 505, "flush_events() — 發送 webhook"),
        ("arrow_dash", 330, 130, 565, "HTTP Response + X-Request-ID"),
    ]

    for step in steps:
        kind = step[0]
        if kind == "arrow":
            _, fc, tc, y, lbl = step
            s += seq_arrow(fc, tc, y, lbl)
        elif kind == "arrow_dash":
            _, fc, tc, y, lbl = step
            s += seq_arrow(fc, tc, y, lbl, dashed=True)
        elif kind == "self":
            _, cx, y, lbl = step
            s += self_arrow(cx, y, lbl)

    s += svg_footer()
    return s

# ─── 7. netbox-script-execution.svg ─────────────────────────────────────────
def gen_7():
    w, h = 1000, 680
    s = svg_header(w, h)
    s += subtitle("netbox-script-execution — Script 執行流程")

    bw = 300
    cx = 500

    s += box(cx - bw//2, 60, bw, 40, "ScriptModule (ManagedFile proxy)")
    s += arrow(cx, 100, cx, 140)
    s += box(cx - bw//2, 140, bw, 40, "module_scripts dict")
    s += arrow(cx, 180, cx, 220)
    s += box(cx - bw//2, 220, bw, 40, "Script model")
    s += arrow(cx, 260, cx, 300)
    s += box(cx - bw//2, 300, bw, 40, "BaseScript subclass")
    s += arrow(cx, 340, cx, 380)
    s += box(cx - bw//2, 380, bw, 40, "執行自訂邏輯")

    # Branches from 執行自訂邏輯
    # → messages list (via log_*)
    s += box(200, 480, 200, 40, "messages list")
    s += path_arrow(f"M 350 420 L 300 420 L 300 480", "log_*", lx=290, ly=450)
    # → DB Transaction (via commit=True)
    s += box(580, 480, 220, 40, "DB Transaction")
    s += path_arrow(f"M 650 420 L 700 420 L 700 480", "commit=True", lx=700, ly=450)

    # Both → Job 記錄完成狀態
    s += box(cx - bw//2, 590, bw, 40, "Job 記錄完成狀態")
    s += path_arrow(f"M 300 520 L 300 610 L 350 610", "", lx=325, ly=600)
    s += path_arrow(f"M 690 520 L 690 610 L 650 610", "", lx=680, ly=600)

    s += svg_footer()
    return s

# ─── 8. netbox-search-index.svg ─────────────────────────────────────────────
def gen_8():
    w, h = 1600, 560
    s = svg_header(w, h)
    s += subtitle("netbox-search-index — 搜尋索引快取機制")

    # Top flow (index update)
    s += box(40, 80, 180, 40, "物件 save/delete")
    s += arrow(220, 100, 260, 100)
    s += box(260, 80, 180, 40, "caching_handler")
    s += arrow(440, 100, 480, 100)
    s += diamond(580, 100, 90, 35, "remove_existing?")
    s += path_arrow(f"M 580 65 L 580 40 L 700 40 L 700 80", "否", lx=640, ly=30)
    s += path_arrow(f"M 670 100 L 700 100 L 700 80", "是", lx=685, ly=90)
    s += box(670, 40, 180, 40, "刪除舊 CachedValue")
    s += box(900, 60, 180, 40, "indexer.to_cache")
    s += path_arrow(f"M 850 60 L 900 80", "", lx=875, ly=65)
    s += arrow(1080, 80, 1120, 80)
    s += box(1120, 60, 200, 40, "產生 CachedValue 記錄")
    s += arrow(1320, 80, 1360, 80)
    s += box(1360, 60, 180, 40, "bulk_create buffer")
    s += path_arrow(f"M 1450 100 L 1450 130 L 1380 130 L 1380 160", "buffer ≥ 2000", lx=1490, ly=145)
    s += box(1310, 160, 160, 40, "flush to DB")

    # Bottom flow (search)
    s += box(40, 340, 180, 40, "搜尋請求")
    s += arrow(220, 360, 260, 360)
    s += box(260, 340, 230, 40, "CachedValueSearchBackend.search")
    s += arrow(490, 360, 530, 360)
    s += box(530, 340, 180, 40, "建構 Q filter")
    s += arrow(710, 360, 750, 360)
    s += diamond(840, 360, 80, 35, "值像 IP?")
    s += path_arrow(f"M 840 325 L 840 280 L 990 280 L 990 320", "是", lx=920, ly=270)
    s += box(940, 320, 200, 40, "加入 INET/CIDR 條件")
    s += path_arrow(f"M 920 380 L 960 380 L 960 420 L 1050 420 L 1050 400", "否", lx=1010, ly=395)
    s += box(1000, 360, 160, 40, "標準文字搜尋")
    s += box(1210, 360, 200, 40, "Window RowNumber 去重")
    s += path_arrow(f"M 1060 360 L 1210 370", "", lx=1135, ly=355)
    s += path_arrow(f"M 1140 340 L 1210 355", "", lx=1175, ly=340)
    s += arrow(1410, 370, 1450, 370)
    s += box(1450, 350, 130, 40, "回傳最低 weight")

    s += svg_footer()
    return s

# ─── 9. netbox-notification-flow.svg ────────────────────────────────────────
def gen_9():
    w, h = 900, 620
    s = svg_header(w, h)
    s += subtitle("netbox-notification-flow — 通知機制流程")

    cx = 450
    bw = 240

    s += box(cx - bw//2, 60, bw, 40, "物件變更事件")
    s += arrow(cx, 100, cx, 140)
    s += diamond(cx, 160, 110, 35, "Subscription 存在?")
    # 是 → C
    s += path_arrow(f"M 340 160 L 200 160 L 200 300", "是", lx=260, ly=150)
    s += box(100, 300, 200, 40, "建立 Notification")
    # 否 → D
    s += path_arrow(f"M 560 160 L 700 160 L 700 300", "否", lx=635, ly=150)
    s += box(600, 300, 200, 40, "檢查 EventRule")
    # D --匹配--> E
    s += path_arrow(f"M 700 340 L 700 380", "匹配", lx=720, ly=362)
    s += box(600, 380, 200, 40, "NotificationGroup.notify")
    # E → F
    s += arrow(700, 420, 700, 460)
    s += box(580, 460, 240, 40, "為每位 member 建立 Notification")
    # C → G
    s += path_arrow(f"M 200 340 L 200 520 L 330 520", "", lx=265, ly=510)
    # F → G
    s += path_arrow(f"M 700 500 L 700 520 L 570 520", "", lx=635, ly=510)
    s += box(330, 500, 240, 40, "使用者 Dashboard")
    # G → H
    s += arrow(450, 540, 450, 570)
    s += box(330, 570, 240, 40, "標記已讀 / 未讀")

    s += svg_footer()
    return s

# ─── 10. netbox-dcim-erd.svg ─────────────────────────────────────────────────
def gen_10():
    w, h = 1920, 900
    s = svg_header(w, h)
    s += subtitle("netbox-dcim-erd — DCIM 資料模型關聯圖")

    bw, bh = 160, 36
    col_x = [80, 280, 480, 680, 880, 1080, 1280, 1480]
    row_y = [80, 180, 280, 380, 480, 580, 680]

    entities = {
        "Region":        (0, 0),
        "SiteGroup":     (1, 0),
        "Site":          (2, 0),
        "Location":      (3, 0),
        "Rack":          (0, 1),
        "Device":        (1, 1),
        "Manufacturer":  (2, 1),
        "DeviceType":    (3, 1),
        "DeviceRole":    (0, 2),
        "Platform":      (1, 2),
        "Tenant":        (2, 2),
        "Cluster":       (3, 2),
        "VirtualChassis":(0, 3),
        "Interface":     (1, 3),
        "ConsolePort":   (2, 3),
        "PowerPort":     (3, 3),
        "DeviceBay":     (0, 4),
        "ModuleBay":     (1, 4),
        "Cable":         (2, 4),
    }

    def ecx(name):
        c, r = entities[name]
        return col_x[c] + bw // 2

    def ecy(name):
        c, r = entities[name]
        return row_y[r] + bh // 2

    def ex(name): c, r = entities[name]; return col_x[c]
    def ey(name): c, r = entities[name]; return row_y[r]

    for name, (c, r) in entities.items():
        s += box(col_x[c], row_y[r], bw, bh, name, fontsize=12)

    def rel(a, b, label, offset_a=(0,0), offset_b=(0,0)):
        x1 = ecx(a) + offset_a[0]
        y1 = ecy(a) + offset_a[1]
        x2 = ecx(b) + offset_b[0]
        y2 = ecy(b) + offset_b[1]
        lx = (x1+x2)//2
        ly = (y1+y2)//2 - 8
        return path_arrow(f"M {x1} {y1} L {x2} {y2}", label, lx=lx, ly=ly)

    rels = [
        ("Region", "SiteGroup", "contains"),
        ("Region", "Site", "region"),
        ("SiteGroup", "Site", "group"),
        ("Site", "Location", "site"),
        ("Site", "Rack", "site"),
        ("Location", "Rack", "location"),
        ("Rack", "Device", "rack"),
        ("Site", "Device", "site"),
        ("Manufacturer", "DeviceType", "manufacturer"),
        ("DeviceType", "Device", "device_type"),
        ("DeviceRole", "Device", "role"),
        ("Platform", "Device", "platform"),
        ("Tenant", "Device", "tenant"),
        ("Cluster", "Device", "cluster"),
        ("VirtualChassis", "Device", "virtual_chassis"),
        ("Device", "Interface", "device"),
        ("Device", "ConsolePort", "device"),
        ("Device", "PowerPort", "device"),
        ("Device", "DeviceBay", "device"),
        ("Device", "ModuleBay", "device"),
    ]

    for a, b, lbl in rels:
        x1, y1 = ecx(a), ecy(a)
        x2, y2 = ecx(b), ecy(b)
        lx = (x1+x2)//2
        ly = (y1+y2)//2 - 8
        s += path_arrow(f"M {x1} {y1} L {x2} {y2}", lbl, lx=lx, ly=ly)

    # Cable connections (curved to avoid overlap)
    s += path_arrow(f"M {ecx('Interface')+80} {ecy('Interface')} L {ecx('Cable')} {ecy('Cable')-5}", "termination_a", lx=ecx('Interface')+130, ly=ecy('Interface')-15)
    s += path_arrow(f"M {ecx('Cable')} {ecy('Cable')+5} L {ecx('Interface')+80} {ecy('Interface')+10}", "termination_b", lx=ecx('Cable')-50, ly=ecy('Cable')+20)

    s += svg_footer()
    return s

# ─── 11. netbox-ipam-erd-full.svg ────────────────────────────────────────────
def gen_11():
    w, h = 1400, 620
    s = svg_header(w, h)
    s += subtitle("netbox-ipam-erd-full — IPAM 完整模型關聯圖")

    bw, bh = 140, 36

    positions = {
        "RIR":        (50, 80),
        "Aggregate":  (260, 80),
        "VRF":        (50, 230),
        "Prefix":     (500, 230),
        "IPAddress":  (750, 80),
        "IPRange":    (750, 380),
        "VLAN":       (1000, 230),
        "VLANGroup":  (1000, 80),
        "Role":       (1200, 80),
        "Tenant":     (1200, 230),
    }

    for name, (x, y) in positions.items():
        s += box(x, y, bw, bh, name)

    def cx(n): return positions[n][0] + bw // 2
    def cy(n): return positions[n][1] + bh // 2

    rels = [
        ("RIR", "Aggregate", "rir"),
        ("Aggregate", "Prefix", "contains"),
        ("VRF", "Prefix", "vrf"),
        ("VRF", "IPAddress", "vrf"),
        ("Prefix", "IPAddress", "parent"),
        ("Prefix", "IPRange", "parent"),
        ("VLAN", "Prefix", "vlan"),
        ("VLANGroup", "VLAN", "group"),
        ("Role", "Prefix", "role"),
        ("Role", "VLAN", "role"),
        ("Tenant", "Prefix", "tenant"),
    ]

    for a, b, lbl in rels:
        x1, y1 = cx(a), cy(a)
        x2, y2 = cx(b), cy(b)
        lx = (x1+x2)//2
        ly = (y1+y2)//2 - 10
        s += path_arrow(f"M {x1} {y1} L {x2} {y2}", lbl, lx=lx, ly=ly)

    # Prefix → Prefix (self-loop)
    px, py = cx("Prefix"), cy("Prefix")
    s += f'<path d="M {px} {py-18} C {px} {py-60}, {px+80} {py-60}, {px+80} {py-18}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>'
    s += f'<text x="{px+85}" y="{py-40}" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">parent/child</text>'

    s += svg_footer()
    return s

# ─── 12. netbox-auth-flow.svg ────────────────────────────────────────────────
def gen_12():
    w, h = 1400, 780
    s = svg_header(w, h)
    s += subtitle("netbox-auth-flow — 認證與授權流程")

    s += box(590, 50, 220, 40, "使用者請求")
    s += arrow(700, 90, 700, 130)
    s += diamond(700, 165, 150, 45, "認證方式")

    backends = [
        ("Local", "Django ModelBackend", 120),
        ("LDAP", "NBLDAPBackend", 310),
        ("SSO/Proxy", "RemoteUserBackend", 500),
        ("OAuth2/SAML", "Social Auth Backend", 700),
        ("API Token", "TokenAuthentication", 1000),
    ]

    bw = 200
    for label, name, bx in backends:
        # Arrow from diamond
        s += path_arrow(f"M {700} {210 if abs(bx+bw//2-700)<300 else 165} L {bx+bw//2} {165} L {bx+bw//2} {310}", label, lx=(700+bx+bw//2)//2, ly=155)
        s += box(bx, 310, bw, 40, name, fontsize=11)

    # Special: RemoteUserBackend → diamond
    s += diamond(500, 430, 130, 40, "GROUP_SYNC?")
    s += arrow(600, 350, 600, 390)
    # Yes → configure_groups
    s += path_arrow(f"M 370 430 L 250 430 L 250 530", "Yes", lx=300, ly=420)
    s += box(170, 530, 190, 40, "configure_groups")
    # No → configure_user
    s += path_arrow(f"M 630 430 L 760 430 L 760 530", "No", lx=700, ly=420)
    s += box(660, 530, 220, 40, "configure_user 預設群組")

    # Social Auth Backend → user_default_groups_handler
    s += path_arrow(f"M 800 350 L 800 460 L 920 460 L 920 530", "", lx=860, ly=455)
    s += box(840, 530, 240, 40, "user_default_groups_handler")

    # All → ObjectPermissionMixin
    s += box(540, 640, 260, 40, "ObjectPermissionMixin")

    paths = [(220, 570, 670, 640), (265, 570, 670, 640), (880, 490, 670, 640), (960, 570, 800, 640), (1100, 350, 1100, 460), ]
    for x1, y1, x2, y2 in paths:
        s += path_arrow(f"M {x1} {y1} L {x1} {max(y1, y2)} L {x2} {max(y1, y2)} L {x2} {y2}", "", lx=(x1+x2)//2, ly=(y1+y2)//2)

    # API Token → ObjectPermissionMixin directly
    s += path_arrow(f"M 1100 350 L 1100 660 L 800 660", "", lx=980, ly=650)

    # Django + LDAP → ObjectPermissionMixin
    s += path_arrow(f"M 220 350 L 220 600 L 540 660", "", lx=380, ly=590)
    s += path_arrow(f"M 410 350 L 410 600 L 540 660", "", lx=475, ly=590)

    s += box(540, 700, 260, 40, "ObjectPermission 物件級權限")
    s += arrow(670, 680, 670, 700)
    s += box(540, 740, 260, 40, "允許 / 拒絕存取")
    s += arrow(670, 740, 670, 760)

    s += svg_footer()
    return s

# ─── 13. netbox-webhook-flow.svg ────────────────────────────────────────────
def gen_13():
    w, h = 1600, 820
    s = svg_header(w, h)
    s += subtitle("netbox-webhook-flow — Webhook / EventRule 執行流程（Sequence）")

    participants = [
        ("使用者/API", 110),
        ("EventTracking\nMiddleware", 310),
        ("enqueue_event()", 510),
        ("process_event\n_queue()", 710),
        ("process_event\n_rules()", 910),
        ("Redis Queue", 1110),
        ("send_webhook()", 1310),
        ("外部系統", 1490),
    ]

    for i, (name, cx) in enumerate(participants):
        lines = name.split('\n')
        if len(lines) == 1:
            s += box(cx - 75, 50, 150, 44, name, fontsize=11)
        else:
            s += box(cx - 75, 50, 150, 54, lines[0], sublabel=lines[1], fontsize=11)
        s += f'<line x1="{cx}" y1="104" x2="{cx}" y2="{h-60}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="5,3"/>'

    def sa(fc, tc, y, lbl, dashed=False):
        x1, x2 = participants[fc][1], participants[tc][1]
        d = 1 if x2 > x1 else -1
        mk = 'marker-end="url(#arrow)"'
        dash = ' stroke-dasharray="6,3"' if dashed else ''
        lx = (x1+x2)//2
        ly = y - 8
        lbl_txt = f'<text x="{lx}" y="{ly}" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{lbl}</text>' if lbl else ''
        return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.5"{dash} {mk}/>' + lbl_txt

    def self_a(idx, y, lbl):
        cx = participants[idx][1]
        return (f'<path d="M {cx} {y} C {cx+50} {y}, {cx+50} {y+30}, {cx} {y+30}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>'
                + f'<text x="{cx+55}" y="{y+18}" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">{lbl}</text>')

    y = 160
    s += sa(0, 1, y, "HTTP Request（CRUD 操作）"); y += 50
    s += sa(1, 2, y, "物件變更偵測"); y += 50
    s += self_a(2, y, "合併同一 Request 中的重複事件"); y += 60
    s += sa(1, 3, y, "Request 完成後 flush_events()"); y += 50
    s += sa(3, 4, y, "逐事件比對 EventRule"); y += 50
    s += self_a(4, y, "eval_conditions(data)"); y += 60

    # Alt block
    alt_y = y
    s += f'<rect x="200" y="{alt_y - 10}" width="1350" height="230" rx="6" fill="none" stroke="{CONTAINER_STROKE}" stroke-width="1.5" stroke-dasharray="6,3"/>'
    s += f'<text x="210" y="{alt_y + 8}" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">action_type</text>'

    s += sa(4, 5, alt_y + 30, "enqueue send_webhook"); y = alt_y + 30
    s += sa(5, 6, y + 45, "Worker 執行"); y += 45
    s += sa(6, 7, y + 45, "HTTP POST + HMAC-SHA512"); y += 45
    # divider
    s += f'<line x1="200" y1="{alt_y + 160}" x2="1550" y2="{alt_y + 160}" stroke="{CONTAINER_STROKE}" stroke-width="1" stroke-dasharray="4,2"/>'
    s += f'<text x="210" y="{alt_y + 178}" fill="{TEXT_SECONDARY}" font-size="11" font-family="{FONT}">action_type=script/notification</text>'
    s += sa(4, 5, alt_y + 195, "enqueue ScriptJob / NotificationGroup.notify")

    s += svg_footer()
    return s

# ─── 14. netbox-plugin-loading.svg ──────────────────────────────────────────
def gen_14():
    w, h = 1200, 720
    s = svg_header(w, h)
    s += subtitle("netbox-plugin-loading — Plugin 載入與初始化流程")

    # Subgraph 1: Plugin 載入
    s += container(20, 60, 560, 270, "Plugin 載入")
    s += box(60, 110, 240, 40, "settings.py 遍歷 PLUGINS")
    s += arrow(180, 150, 180, 190)
    s += box(60, 190, 240, 40, "importlib.import_module")
    s += arrow(180, 230, 180, 270)
    s += box(60, 270, 240, 40, "取得 plugin.config")
    s += arrow(180, 310, 180, 350)

    # Branches to 4 registries
    s += box(380, 100, 160, 36, "INSTALLED_APPS")
    s += box(380, 150, 160, 36, "MIDDLEWARE")
    s += box(380, 200, 160, 36, "RQ_QUEUES")
    s += box(380, 250, 160, 36, "EVENTS_PIPELINE")

    s += path_arrow(f"M 300 330 L 460 130 L 460 118", "", lx=380, ly=230)
    s += path_arrow(f"M 300 330 L 460 168", "", lx=380, ly=250)
    s += path_arrow(f"M 300 330 L 460 218", "", lx=380, ly=275)
    s += path_arrow(f"M 300 330 L 460 268", "", lx=380, ly=300)

    # Actually let's draw validate box first
    s += box(60, 350, 240, 40, "validate 版本+設定")
    s += arrow(180, 350, 180, 350)
    s += box(60, 270, 240, 40, "取得 plugin.config")
    s += arrow(180, 310, 180, 350)
    s += box(60, 350, 240, 40, "validate 版本+設定")
    s += arrow(180, 390, 180, 430)
    s += box(60, 430, 240, 40, "registry 註冊")

    s += path_arrow(f"M 300 450 L 380 136", "→INSTALLED_APPS", lx=360, ly=300)
    s += path_arrow(f"M 300 450 L 380 168", "→MIDDLEWARE", lx=360, ly=310)
    s += path_arrow(f"M 300 450 L 380 218", "→RQ_QUEUES", lx=360, ly=330)
    s += path_arrow(f"M 300 450 L 380 268", "→EVENTS_PIPELINE", lx=360, ly=360)

    # Subgraph 2: Plugin ready
    s += container(20, 400, 1160, 290, "Plugin ready()")
    s += box(60, 450, 220, 40, "PluginConfig.ready()")

    ready_items = [
        "register_models",
        "register_search",
        "register_data_backend",
        "register_template_extensions",
        "register_menu_items",
        "register_graphql_schema",
        "register_user_preferences",
    ]
    for i, item in enumerate(ready_items):
        xi = 350 + (i % 4) * 195
        yi = 450 + (i // 4) * 80
        s += box(xi, yi, 185, 40, item, fontsize=11)
        s += path_arrow(f"M 280 470 L {xi} {yi + 20}", "", lx=(280+xi)//2, ly=465)

    s += svg_footer()
    return s

# ─── 15. netbox-datasource-sync.svg ─────────────────────────────────────────
def gen_15():
    w, h = 1100, 220
    s = svg_header(w, h)
    s += subtitle("netbox-datasource-sync — DataSource 同步流程")

    nodes = [
        ("外部 Git/S3", 30),
        ("DataSource", 270),
        ("DataFile", 470),
        ("AutoSyncRecord", 670),
        ("ConfigContext/\nExportTemplate", 870),
    ]

    for label, x in nodes:
        lines = label.split('\n')
        if len(lines) == 1:
            s += box(x, 90, 190, 40, label)
        else:
            s += box(x, 90, 190, 50, lines[0], sublabel=lines[1])

    labels = ["sync", "", "", ""]
    for i in range(len(nodes) - 1):
        x1 = nodes[i][1] + 190
        x2 = nodes[i+1][1]
        y = 115
        lbl = labels[i]
        s += arrow(x1, y, x2, y, lbl)

    s += svg_footer()
    return s

# ─── 16. netbox-notification-group.svg ──────────────────────────────────────
def gen_16():
    w, h = 900, 580
    s = svg_header(w, h)
    s += subtitle("netbox-notification-group — 通知群組觸發機制")

    cx = 450
    bw = 280

    s += box(cx - bw//2, 60, bw, 40, "EventRule action_type=notification")
    s += arrow(cx, 100, cx, 140)
    s += box(cx - bw//2, 140, bw, 40, "NotificationGroup")
    s += arrow(cx, 180, cx, 220)
    s += box(cx - bw//2, 220, bw, 40, "members 計算 users ∪ group.users")
    s += arrow(cx, 260, cx, 300)
    s += box(cx - bw//2, 300, bw, 40, "Notification.update_or_create per user")

    # Side flow for subscription
    s += box(80, 220, 220, 40, "使用者訂閱")
    s += arrow(80 + 220//2, 260, 80 + 220//2, 300)
    s += box(80, 300, 220, 40, "Subscription Model")
    s += arrow(80 + 220//2, 340, 80 + 220//2, 380)
    s += box(30, 380, 260, 40, "物件變更時觸發個人通知")
    s += path_arrow(f"M 160 420 L 160 460 L 310 460 L 310 440", "", lx=235, ly=450)

    # All notifications → Dashboard
    s += box(cx - bw//2, 440, bw, 40, "使用者 Notification Dashboard")
    s += path_arrow(f"M {cx} 340 L {cx} 440", "", lx=cx+10, ly=390)
    s += path_arrow(f"M 160 420 L 160 460 L 310 460", "", lx=235, ly=450)

    s += svg_footer()
    return s

# ─── 17. netbox-production-deployment.svg ───────────────────────────────────
def gen_17():
    w, h = 1400, 920
    s = svg_header(w, h)
    s += subtitle("netbox-production-deployment — 生產環境部署架構")

    # Subgraph 前端
    s += container(20, 60, 400, 160, "前端")
    s += box(60, 110, 140, 40, "Load Balancer/CDN")
    s += arrow(200, 150, 260, 150)
    s += box(260, 110, 140, 40, "Nginx/Apache")

    # Subgraph 應用層
    s += container(20, 270, 400, 160, "應用層")
    s += box(60, 320, 160, 40, "Gunicorn netbox.service")
    s += box(260, 320, 140, 40, "RQ Worker netbox-rq.service")

    # Subgraph 資料層
    s += container(20, 490, 560, 200, "資料層")
    s += cylinder(50, 540, 150, 80, "PostgreSQL")
    s += cylinder(230, 540, 160, 80, "Redis tasks DB 0")
    s += cylinder(420, 540, 160, 80, "Redis caching DB 1")

    # Subgraph 外部整合
    s += container(650, 60, 720, 600, "外部整合")
    ext_items = [
        ("Webhook 接收端", 700, 120),
        ("LDAP/AD", 700, 200),
        ("OAuth2/SAML IdP", 700, 280),
        ("Git/S3 DataSource", 700, 360),
        ("Prometheus", 700, 440),
    ]
    for name, x, y in ext_items:
        s += box(x, y, 200, 40, name)

    # Connections
    # Nginx → Gunicorn
    s += path_arrow(f"M 330 155 L 330 230 L 140 230 L 140 320", "proxy_pass :8001", lx=230, ly=220)
    # Gunicorn → PG
    s += path_arrow(f"M 140 360 L 140 450 L 125 450 L 125 540", "", lx=130, ly=445)
    # Gunicorn → Redis caching
    s += path_arrow(f"M 140 380 L 140 470 L 500 470 L 500 540", "caching", lx=330, ly=460)
    # Gunicorn → Redis tasks (enqueue)
    s += path_arrow(f"M 180 360 L 310 360 L 310 430 L 310 540", "enqueue", lx=320, ly=435)
    # RQ Worker → Redis tasks (dequeue)
    s += path_arrow(f"M 330 360 L 310 360", "dequeue", lx=340, ly=348)
    # RQ Worker → PG
    s += path_arrow(f"M 330 380 L 330 450 L 125 450 L 125 560", "", lx=230, ly=445)

    # App → external
    s += path_arrow(f"M 220 320 L 620 140", "send_webhook", lx=420, ly=220)
    s += path_arrow(f"M 220 335 L 620 220", "auth", lx=420, ly=270)
    s += path_arrow(f"M 220 345 L 620 300", "auth", lx=420, ly=315)
    s += path_arrow(f"M 220 355 L 620 380", "sync", lx=420, ly=360)
    s += path_arrow(f"M 220 365 L 620 460", "/metrics", lx=420, ly=410)

    s += svg_footer()
    return s

generators = [
    ("netbox-prefix-hierarchy-update", gen_1),
    ("netbox-ipam-erd", gen_2),
    ("netbox-dcim-class-hierarchy", gen_3),
    ("netbox-cable-path", gen_4),
    ("netbox-custom-fields-cache", gen_5),
    ("netbox-change-log-flow", gen_6),
    ("netbox-script-execution", gen_7),
    ("netbox-search-index", gen_8),
    ("netbox-notification-flow", gen_9),
    ("netbox-dcim-erd", gen_10),
    ("netbox-ipam-erd-full", gen_11),
    ("netbox-auth-flow", gen_12),
    ("netbox-webhook-flow", gen_13),
    ("netbox-plugin-loading", gen_14),
    ("netbox-datasource-sync", gen_15),
    ("netbox-notification-group", gen_16),
    ("netbox-production-deployment", gen_17),
]

for name, fn in generators:
    path = os.path.join(OUT, f"{name}.svg")
    content = fn()
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

print(f"\nAll {len(generators)} SVGs generated in {OUT}/")
