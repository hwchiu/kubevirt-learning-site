#!/usr/bin/env python3
"""Block 1: bridge-masquerade.md - Two-phase network setup (sequenceDiagram)"""
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
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-bridge-1.svg",
                       size=(W, H), profile='full')

# Background
dwg.add(dwg.rect((0, 0), (W, H), fill=BG))

# Title
dwg.add(dwg.text("KubeVirt 兩階段網路設定架構", insert=(W//2, 36),
                 text_anchor="middle", font_family=FONT, font_size=18,
                 font_weight="600", fill=TEXT_PRIMARY))

# Participants
participants = [
    ("K", "Kubernetes"),
    ("VH", "virt-handler\n（特權）"),
    ("VL", "virt-launcher\n（非特權）"),
    ("VM", "QEMU / VM"),
]

# Lifeline X positions
xs = [110, 290, 530, 750]
top_y = 60
box_w, box_h = 140, 52
msg_start_y = top_y + box_h + 20
lifeline_end_y = H - 40

# Draw participant boxes
for i, (_, label) in enumerate(participants):
    bx = xs[i] - box_w // 2
    by = top_y
    dwg.add(dwg.rect((bx, by), (box_w, box_h), rx=6, ry=6,
                     fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    lines = label.split("\n")
    if len(lines) == 1:
        dwg.add(dwg.text(lines[0], insert=(xs[i], top_y + box_h // 2 + 5),
                         text_anchor="middle", font_family=FONT, font_size=13,
                         font_weight="600", fill=TEXT_PRIMARY))
    else:
        dwg.add(dwg.text(lines[0], insert=(xs[i], top_y + box_h // 2 - 4),
                         text_anchor="middle", font_family=FONT, font_size=13,
                         font_weight="600", fill=TEXT_PRIMARY))
        dwg.add(dwg.text(lines[1], insert=(xs[i], top_y + box_h // 2 + 13),
                         text_anchor="middle", font_family=FONT, font_size=11,
                         fill=TEXT_SECONDARY))

# Draw lifelines
for x in xs:
    dwg.add(dwg.line((x, top_y + box_h), (x, lifeline_end_y),
                     stroke=BOX_STROKE, stroke_width=1.5, stroke_dasharray="6,4"))

# Messages
messages = [
    (0, 1, "建立 Pod，指派網路"),
    (1, 1, "Phase 1：設定 Pod netns（特權操作）"),
    (1, 2, "傳遞網路設定快取"),
    (2, 2, "Phase 2：設定 libvirt XML（非特權）"),
    (2, 3, "啟動 QEMU，掛載網路介面"),
]

y = msg_start_y + 10
step = 58

def draw_arrow(dwg, x1, x2, y, label, self_loop=False):
    if self_loop:
        # self-loop arrow
        r = 28
        dwg.add(dwg.line((x1, y), (x1 + r, y), stroke=ARROW, stroke_width=1.5))
        dwg.add(dwg.line((x1 + r, y), (x1 + r, y + 26), stroke=ARROW, stroke_width=1.5))
        dwg.add(dwg.line((x1, y + 26), (x1 + r, y + 26), stroke=ARROW, stroke_width=1.5))
        # arrowhead
        dwg.add(dwg.polygon([(x1, y+26), (x1+8, y+22), (x1+8, y+30)],
                             fill=ARROW))
        # label
        dwg.add(dwg.text(label, insert=(x1 + r + 8, y + 18),
                         font_family=FONT, font_size=12, fill=TEXT_PRIMARY))
        return y + 36
    else:
        mid_x = (x1 + x2) / 2
        dwg.add(dwg.line((x1, y), (x2, y), stroke=ARROW, stroke_width=1.5))
        # arrowhead
        if x2 > x1:
            dwg.add(dwg.polygon([(x2, y), (x2-10, y-5), (x2-10, y+5)], fill=ARROW))
        else:
            dwg.add(dwg.polygon([(x2, y), (x2+10, y-5), (x2+10, y+5)], fill=ARROW))
        dwg.add(dwg.text(label, insert=(mid_x, y - 6),
                         text_anchor="middle", font_family=FONT, font_size=12, fill=TEXT_PRIMARY))
        return y + step

for (fi, ti, label) in messages:
    if fi == ti:
        y = draw_arrow(dwg, xs[fi], xs[ti], y, label, self_loop=True)
    else:
        y = draw_arrow(dwg, xs[fi], xs[ti], y, label, self_loop=False)

# Bottom boxes (repeat)
for x in xs:
    bx = x - box_w // 2
    by = lifeline_end_y - box_h
    dwg.add(dwg.rect((bx, by), (box_w, box_h), rx=6, ry=6,
                     fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))

dwg.save()
print("Saved kubevirt-net-bridge-1.svg")
