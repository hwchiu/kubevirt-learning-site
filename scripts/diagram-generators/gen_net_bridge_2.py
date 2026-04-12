#!/usr/bin/env python3
"""Block 2: bridge-masquerade.md - Bridge mode architecture"""
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

W, H = 900, 500
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-bridge-2.svg",
                       size=(W, H), profile='full')
dwg.add(dwg.rect((0,0),(W,H),fill=BG))

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    dwg.add(dwg.rect((x, y), (w, h), rx=rx, ry=rx, fill=fill, stroke=stroke, stroke_width=1.5))

def label(text, x, y, size=13, weight="normal", color=TEXT_PRIMARY, anchor="middle"):
    dwg.add(dwg.text(text, insert=(x, y), text_anchor=anchor,
                     font_family=FONT, font_size=size, font_weight=weight, fill=color))

def multiline(lines, cx, cy, size=12, color=TEXT_PRIMARY):
    gap = size + 4
    total = len(lines) * gap
    start_y = cy - total // 2 + size
    for i, line in enumerate(lines):
        dwg.add(dwg.text(line, insert=(cx, start_y + i * gap),
                         text_anchor="middle", font_family=FONT, font_size=size, fill=color))

def arrow_h(x1, x2, y, color=ARROW, label_text="", dashed=False):
    da = "6,3" if dashed else None
    kw = {"stroke": color, "stroke_width": 1.5}
    if da:
        kw["stroke_dasharray"] = da
    dwg.add(dwg.line((x1, y), (x2, y), **kw))
    if x2 > x1:
        dwg.add(dwg.polygon([(x2,y),(x2-9,y-4),(x2-9,y+4)], fill=color))
    else:
        dwg.add(dwg.polygon([(x2,y),(x2+9,y-4),(x2+9,y+4)], fill=color))
    if label_text:
        mid = (x1 + x2) / 2
        dwg.add(dwg.text(label_text, insert=(mid, y-7), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

def arrow_v(x, y1, y2, color=ARROW):
    dwg.add(dwg.line((x, y1), (x, y2), stroke=color, stroke_width=1.5))
    if y2 > y1:
        dwg.add(dwg.polygon([(x,y2),(x-4,y2-9),(x+4,y2-9)], fill=color))
    else:
        dwg.add(dwg.polygon([(x,y2),(x-4,y2+9),(x+4,y2+9)], fill=color))

def line_h(x1, x2, y, color=BOX_STROKE):
    dwg.add(dwg.line((x1,y),(x2,y),stroke=color,stroke_width=1.5))

def line_v(x, y1, y2, color=BOX_STROKE):
    dwg.add(dwg.line((x,y1),(x,y2),stroke=color,stroke_width=1.5))

# Title
label("Bridge 模式網路架構", W//2, 36, size=18, weight="600")

# ── 節點 Host 大框 ──
box(30, 55, 560, 390, fill="#fafbff", stroke=CONTAINER_STROKE, rx=12)
label("節點 Host", 80, 78, size=12, color=TEXT_SECONDARY, anchor="start")

# ── Pod Network Namespace 框 ──
box(60, 90, 480, 240, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, rx=10)
label("Pod Network Namespace", 310, 114, size=12, color=TEXT_SECONDARY)

# Linux Bridge
box(180, 130, 200, 64, fill="#dbeafe", stroke="#3b82f6", rx=8)
multiline(["Linux Bridge", "k6t-eth0", "IP: 10.244.1.5/24"], 280, 162, size=12, color="#1d4ed8")

# eth0
box(80, 230, 120, 52, fill=BOX_FILL, stroke=BOX_STROKE, rx=8)
multiline(["eth0", "（移除 IP）"], 140, 256, size=12)

# tap0
box(360, 230, 120, 52, fill="#fef3c7", stroke="#f59e0b", rx=8)
multiline(["tap0", "（連接 VM）"], 420, 256, size=12, color="#92400e")

# Bridge to eth0 and tap0 lines
line_v(280, 194, 230)  # bridge down to eth0 level
line_h(140, 280, 212)  # left to bridge bottom-mid
line_h(280, 420, 212)  # right to bridge bottom-mid
line_v(140, 212, 230)
line_v(420, 212, 230)

# veth-host in host netns
box(80, 360, 140, 52, fill=BOX_FILL, stroke=BOX_STROKE, rx=8)
multiline(["veth-host", "（host netns）"], 150, 386, size=12)

# arrow eth0 <-> veth-host
arrow_v(140, 282, 360)
label("veth pair", 175, 322, size=10, color=TEXT_SECONDARY, anchor="start")

# CNI plugin
box(80, 430, 140, 50, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, rx=8)
multiline(["CNI Plugin", "（calico/flannel）"], 150, 455, size=12)
arrow_v(150, 412, 430)

# ── VM Guest 框 ──
box(640, 90, 230, 140, fill="#f0fdf4", stroke="#86efac", rx=10)
label("VM Guest", 755, 113, size=12, color=TEXT_SECONDARY)

box(660, 125, 190, 80, fill="#dcfce7", stroke="#22c55e", rx=8)
multiline(["eth0", "IP: 10.244.1.5/24", "（同 Pod IP）"], 755, 165, size=12, color="#166534")

# arrow tap0 <-> VM
arrow_h(480, 660, 258, label_text="virtio tap")
# adjust: tap0 right edge at 480, VM box at 660
dwg.add(dwg.line((480, 258), (660, 258), stroke=ARROW, stroke_width=1.5))
dwg.add(dwg.polygon([(660,258),(651,254),(651,262)], fill=ARROW))
dwg.add(dwg.polygon([(480,258),(489,254),(489,262)], fill=ARROW))
dwg.add(dwg.text("virtio tap", insert=(570, 248), text_anchor="middle",
                 font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

# Legend
legend_items = [
    ("#dbeafe", "#3b82f6", "Linux Bridge（k6t-eth0）"),
    ("#fef3c7", "#f59e0b", "TAP 介面（tap0）"),
    ("#dcfce7", "#22c55e", "VM 虛擬網卡"),
]
lx, ly = 640, 260
label("圖例", lx, ly, size=12, weight="600", color=TEXT_SECONDARY, anchor="start")
for i, (fill, stroke, lbl) in enumerate(legend_items):
    ry = ly + 20 + i * 28
    dwg.add(dwg.rect((lx, ry), (16, 16), rx=3, fill=fill, stroke=stroke, stroke_width=1.5))
    label(lbl, lx + 24, ry + 12, size=11, color=TEXT_PRIMARY, anchor="start")

dwg.save()
print("Saved kubevirt-net-bridge-2.svg")
