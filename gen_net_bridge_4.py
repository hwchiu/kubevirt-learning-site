#!/usr/bin/env python3
"""Block 4: bridge-masquerade.md - nftables rules flow (graph LR)"""
import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 900, 320
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-bridge-4.svg",
                       size=(W, H), profile='full')
dwg.add(dwg.rect((0,0),(W,H),fill=BG))

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    dwg.add(dwg.rect((x,y),(w,h), rx=rx, ry=rx, fill=fill, stroke=stroke, stroke_width=1.5))

def label(text, x, y, size=13, weight="normal", color=TEXT_PRIMARY, anchor="middle"):
    dwg.add(dwg.text(text, insert=(x,y), text_anchor=anchor,
                     font_family=FONT, font_size=size, font_weight=weight, fill=color))

def multiline(lines, cx, cy, size=12, color=TEXT_PRIMARY):
    gap = size + 4
    total = len(lines) * gap
    sy = cy - total//2 + size
    for i, line in enumerate(lines):
        dwg.add(dwg.text(line, insert=(cx, sy + i*gap), text_anchor="middle",
                         font_family=FONT, font_size=size, fill=color))

def arrow_r(x1, x2, y, lbl=""):
    dwg.add(dwg.line((x1,y),(x2,y), stroke=ARROW, stroke_width=1.5))
    dwg.add(dwg.polygon([(x2,y),(x2-9,y-4),(x2-9,y+4)], fill=ARROW))
    if lbl:
        mid = (x1+x2)/2
        dwg.add(dwg.text(lbl, insert=(mid, y-8), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

# Title
label("nftables 出入站流量規則", W//2, 34, size=18, weight="600")

# ─── 出站流量 row ───
sy = 80
box(30, sy, 590, 90, fill="#fafbff", stroke=CONTAINER_STROKE, rx=10)
label("出站流量（VM → 外部）", 320, sy+20, size=12, color=TEXT_SECONDARY)

bw = 150
vm_x, rule_x, pod_x, net_x = 50, 230, 400, 560
by = sy + 35
box(vm_x, by, bw, 44, fill="#dcfce7", stroke="#22c55e", rx=8)
multiline(["VM 10.0.2.2", ":隨機port"], vm_x+bw//2, by+22, size=12, color="#166534")

box(rule_x, by, 155, 44, fill="#fee2e2", stroke="#ef4444", rx=8)
multiline(["POSTROUTING", "MASQUERADE"], rule_x+78, by+22, size=12, color="#991b1b")

box(pod_x, by, 150, 44, fill="#dbeafe", stroke="#3b82f6", rx=8)
multiline(["Pod IP", ":隨機port"], pod_x+75, by+22, size=12, color="#1d4ed8")

box(net_x, by, 110, 44, fill=BOX_FILL, stroke=BOX_STROKE, rx=8)
label("叢集網路", net_x+55, by+26, size=12)

arrow_r(vm_x+bw, rule_x, by+22)
arrow_r(rule_x+155, pod_x, by+22)
arrow_r(pod_x+150, net_x, by+22)

# ─── 入站流量 row ───
iy = 200
box(30, iy, 590, 90, fill="#fafbff", stroke=CONTAINER_STROKE, rx=10)
label("入站流量（外部 → VM）", 320, iy+20, size=12, color=TEXT_SECONDARY)

svc_x, rule2_x, vm2_x = 50, 230, 430
by2 = iy + 35

box(svc_x, by2, 165, 44, fill=BOX_FILL, stroke=BOX_STROKE, rx=8)
multiline(["Service", "/Port-forward"], svc_x+82, by2+22, size=12)

box(rule2_x, by2, 180, 44, fill="#fee2e2", stroke="#ef4444", rx=8)
multiline(["PREROUTING", "DNAT"], rule2_x+90, by2+22, size=12, color="#991b1b")

box(vm2_x, by2, 160, 44, fill="#dcfce7", stroke="#22c55e", rx=8)
multiline(["VM 10.0.2.2:80"], vm2_x+80, by2+22, size=12, color="#166534")

arrow_r(svc_x+165, rule2_x, by2+22)
arrow_r(rule2_x+180, vm2_x, by2+22)

dwg.save()
print("Saved kubevirt-net-bridge-4.svg")
