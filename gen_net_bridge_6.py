#!/usr/bin/env python3
"""Block 6: bridge-masquerade.md - DHCP server sequence diagram"""
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

W, H = 920, 520
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-bridge-6.svg",
                       size=(W, H), profile='full')
dwg.add(dwg.rect((0,0),(W,H),fill=BG))

# Title
dwg.add(dwg.text("Masquerade 模式 — 內建 DHCP Server 流程", insert=(W//2, 36),
                 text_anchor="middle", font_family=FONT, font_size=18,
                 font_weight="600", fill=TEXT_PRIMARY))

participants = [
    ("VM", "VM Guest"),
    ("TAP", "tap0 介面"),
    ("DHCP", "內建 DHCP Server"),
    ("DNS", "Cluster DNS\n(CoreDNS)"),
]

xs = [100, 300, 550, 780]
top_y = 60
box_w, box_h = 150, 52
lifeline_end = H - 36

for i, (_, label) in enumerate(participants):
    bx = xs[i] - box_w//2
    dwg.add(dwg.rect((bx, top_y), (box_w, box_h), rx=6, ry=6,
                     fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    lines = label.split("\n")
    if len(lines) == 1:
        dwg.add(dwg.text(lines[0], insert=(xs[i], top_y + box_h//2 + 5),
                         text_anchor="middle", font_family=FONT, font_size=13,
                         font_weight="600", fill=TEXT_PRIMARY))
    else:
        dwg.add(dwg.text(lines[0], insert=(xs[i], top_y + box_h//2 - 4),
                         text_anchor="middle", font_family=FONT, font_size=13,
                         font_weight="600", fill=TEXT_PRIMARY))
        dwg.add(dwg.text(lines[1], insert=(xs[i], top_y + box_h//2 + 13),
                         text_anchor="middle", font_family=FONT, font_size=11,
                         fill=TEXT_SECONDARY))

for x in xs:
    dwg.add(dwg.line((x, top_y + box_h), (x, lifeline_end),
                     stroke=BOX_STROKE, stroke_width=1.5, stroke_dasharray="6,4"))

def seq_arrow(x1, x2, y, msg, sub="", dashed=False):
    da = "5,4"
    kw = {"stroke": ARROW, "stroke_width": 1.5}
    if dashed:
        kw["stroke_dasharray"] = da
    dwg.add(dwg.line((x1, y), (x2, y), **kw))
    if x2 > x1:
        dwg.add(dwg.polygon([(x2,y),(x2-9,y-4),(x2-9,y+4)], fill=ARROW))
    else:
        dwg.add(dwg.polygon([(x2,y),(x2+9,y-4),(x2+9,y+4)], fill=ARROW))
    mid = (x1 + x2) / 2
    dwg.add(dwg.text(msg, insert=(mid, y - 7), text_anchor="middle",
                     font_family=FONT, font_size=12, fill=TEXT_PRIMARY))
    if sub:
        dwg.add(dwg.text(sub, insert=(mid, y + 16), text_anchor="middle",
                         font_family=FONT, font_size=10, fill=TEXT_SECONDARY))

def self_note(x, y, lines):
    # box to right
    bw = 200
    dwg.add(dwg.rect((x+10, y-8), (bw, len(lines)*16+10), rx=4,
                     fill="#fffbeb", stroke="#fbbf24", stroke_width=1))
    for i, line in enumerate(lines):
        dwg.add(dwg.text(line, insert=(x+18, y + i*16 + 4),
                         font_family=FONT, font_size=11, fill="#92400e"))
    return len(lines)*16 + 20

y = top_y + box_h + 26
step = 52

seq_arrow(xs[0], xs[1], y, "DHCP Discover（廣播）")
y += step

seq_arrow(xs[1], xs[2], y, "轉發請求")
y += step

# self note on DHCP
dwg.add(dwg.text("查詢 Pod DNS 設定", insert=(xs[2]+10, y + 4),
                 font_family=FONT, font_size=11, fill="#92400e"))
dwg.add(dwg.rect((xs[2]+8, y-8), (210, 22), rx=4,
                 fill="#fffbeb", stroke="#fbbf24", stroke_width=1))
dwg.add(dwg.text("查詢 Pod DNS (/etc/resolv.conf)", insert=(xs[2]+14, y+7),
                 font_family=FONT, font_size=11, fill="#92400e"))
y += 40

seq_arrow(xs[2], xs[1], y, "DHCP Offer", sub="IP:10.0.2.2/24  GW:10.0.2.1  DNS:10.0.2.3")
y += step + 8

seq_arrow(xs[1], xs[0], y, "回應")
y += step

seq_arrow(xs[0], xs[1], y, "DHCP Request")
y += step

seq_arrow(xs[2], xs[1], y, "DHCP ACK")
y += step

seq_arrow(xs[1], xs[0], y, "設定網路介面完成")
y += step

seq_arrow(xs[0], xs[3], y, "DNS 查詢（透過 NAT 轉發到 CoreDNS）")

# Bottom lifeline caps
for x in xs:
    bx = x - 75
    by = lifeline_end - 36
    dwg.add(dwg.rect((bx, by), (150, 36), rx=6, ry=6,
                     fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))

dwg.save()
print("Saved kubevirt-net-bridge-6.svg")
