#!/usr/bin/env python3
"""Block 3: bridge-masquerade.md - Masquerade mode architecture"""
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

W, H = 900, 480
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-bridge-3.svg",
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

def arrow_h(x1, x2, y, lbl=""):
    dwg.add(dwg.line((x1,y),(x2,y), stroke=ARROW, stroke_width=1.5))
    if x2 > x1:
        dwg.add(dwg.polygon([(x2,y),(x2-9,y-4),(x2-9,y+4)], fill=ARROW))
        dwg.add(dwg.polygon([(x1,y),(x1+9,y-4),(x1+9,y+4)], fill=ARROW))
    else:
        dwg.add(dwg.polygon([(x2,y),(x2+9,y-4),(x2+9,y+4)], fill=ARROW))
        dwg.add(dwg.polygon([(x1,y),(x1-9,y-4),(x1-9,y+4)], fill=ARROW))
    if lbl:
        mid = (x1+x2)/2
        dwg.add(dwg.text(lbl, insert=(mid, y-7), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

# Title
label("Masquerade 模式網路架構", W//2, 36, size=18, weight="600")

# 節點 Host 大框
box(30, 55, 560, 310, fill="#fafbff", stroke=CONTAINER_STROKE, rx=12)
label("節點 Host", 80, 78, size=12, color=TEXT_SECONDARY, anchor="start")

# Pod Network Namespace
box(60, 90, 490, 250, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, rx=10)
label("Pod Network Namespace", 310, 114, size=12, color=TEXT_SECONDARY)

# nftables
box(90, 130, 170, 60, fill="#fee2e2", stroke="#ef4444", rx=8)
multiline(["nftables", "MASQUERADE / DNAT"], 175, 160, size=12, color="#991b1b")

# eth0
box(290, 130, 160, 60, fill=BOX_FILL, stroke=BOX_STROKE, rx=8)
multiline(["eth0", "Pod IP: 10.244.1.5/24"], 370, 160, size=12)

# tap0 + gateway
box(90, 230, 170, 60, fill="#fef3c7", stroke="#f59e0b", rx=8)
multiline(["tap0", "Gateway: 10.0.2.1"], 175, 260, size=12, color="#92400e")

# DHCP server
box(290, 230, 160, 60, fill="#dbeafe", stroke="#3b82f6", rx=8)
multiline(["內建 DHCP Server", "分配 10.0.2.2 給 VM"], 370, 260, size=12, color="#1d4ed8")

# connections inside namespace
dwg.add(dwg.line((260, 160), (290, 160), stroke=BOX_STROKE, stroke_width=1.5))
dwg.add(dwg.line((260, 260), (290, 260), stroke=BOX_STROKE, stroke_width=1.5))
dwg.add(dwg.line((175, 190), (175, 230), stroke=BOX_STROKE, stroke_width=1.5))

# VM Guest
box(630, 130, 230, 120, fill="#f0fdf4", stroke="#86efac", rx=10)
label("VM Guest", 745, 153, size=12, color=TEXT_SECONDARY)
box(650, 165, 190, 70, fill="#dcfce7", stroke="#22c55e", rx=8)
multiline(["eth0", "VM IP: 10.0.2.2/24", "GW: 10.0.2.1 / DNS: 10.0.2.3"], 745, 200, size=11, color="#166534")

# tap0 <-> VM arrow
arrow_h(260, 650, 260)
label("virtio tap", (260+650)/2, 252, size=10, color=TEXT_SECONDARY)

# Internet cluster network
box(630, 295, 230, 55, fill="#f1f5f9", stroke="#94a3b8", rx=8)
multiline(["叢集網路", "10.244.0.0/16"], 745, 323, size=12, color="#475569")

# NAT arrow eth0 <-> cluster
dwg.add(dwg.line((450, 160), (745, 160), stroke=ARROW, stroke_width=1))
dwg.add(dwg.line((745, 160), (745, 295), stroke=ARROW, stroke_width=1))
dwg.add(dwg.polygon([(745,295),(741,286),(749,286)], fill=ARROW))
label("NAT", 600, 148, size=10, color=TEXT_SECONDARY)

# Legend
lx, ly = 640, 370
label("圖例", lx, ly, size=12, weight="600", color=TEXT_SECONDARY, anchor="start")
items = [
    ("#fee2e2","#ef4444","nftables NAT 規則"),
    ("#fef3c7","#f59e0b","TAP 介面（Gateway）"),
    ("#dbeafe","#3b82f6","內建 DHCP Server"),
    ("#dcfce7","#22c55e","VM 網路介面"),
]
for i, (fill, stroke, lbl) in enumerate(items):
    ry = ly + 18 + i * 26
    dwg.add(dwg.rect((lx, ry),(16,16), rx=3, fill=fill, stroke=stroke, stroke_width=1.5))
    label(lbl, lx+24, ry+12, size=11, color=TEXT_PRIMARY, anchor="start")

dwg.save()
print("Saved kubevirt-net-bridge-3.svg")
