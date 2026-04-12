#!/usr/bin/env python3
"""Block 1: sriov.md - PF/VF SR-IOV architecture"""
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
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-sriov-1.svg",
                       size=(W, H), profile='full')
dwg.add(dwg.rect((0,0),(W,H),fill=BG))

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    dwg.add(dwg.rect((x,y),(w,h), rx=rx, ry=rx, fill=fill, stroke=stroke, stroke_width=1.5))

def label(text, x, y, size=13, weight="normal", color=TEXT_PRIMARY, anchor="middle"):
    dwg.add(dwg.text(text, insert=(x,y), text_anchor=anchor,
                     font_family=FONT, font_size=size, font_weight=weight, fill=color))

def multiline(lines, cx, cy, size=12, color=TEXT_PRIMARY, align="middle"):
    gap = size + 4
    total = len(lines) * gap
    sy = cy - total//2 + size
    for i, line in enumerate(lines):
        dwg.add(dwg.text(line, insert=(cx, sy+i*gap), text_anchor=align,
                         font_family=FONT, font_size=size, fill=color))

def arrow_r(x1, x2, y, lbl=""):
    dwg.add(dwg.line((x1,y),(x2,y), stroke=ARROW, stroke_width=1.5))
    dwg.add(dwg.polygon([(x2,y),(x2-9,y-4),(x2-9,y+4)], fill=ARROW))
    if lbl:
        mid = (x1+x2)/2
        dwg.add(dwg.text(lbl, insert=(mid, y-7), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

def arrow_down(x, y1, y2, lbl=""):
    dwg.add(dwg.line((x,y1),(x,y2), stroke=ARROW, stroke_width=1.5))
    dwg.add(dwg.polygon([(x,y2),(x-5,y2-10),(x+5,y2-10)], fill=ARROW))
    if lbl:
        dwg.add(dwg.text(lbl, insert=(x+8, (y1+y2)//2+4), text_anchor="start",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

# Title
label("SR-IOV PF / VF 架構", W//2, 36, size=18, weight="600")

# 實體主機 container
box(30, 55, 560, 390, fill="#fafbff", stroke=CONTAINER_STROKE, rx=12)
label("實體主機", 80, 78, size=12, color=TEXT_SECONDARY, anchor="start")

# PF box
box(80, 90, 180, 70, fill="#dbeafe", stroke="#3b82f6", rx=8)
multiline(["網卡 PF", "（Physical Function）", "enp1s0f0"], 170, 125, size=12, color="#1d4ed8")

# VF boxes (2 rows x 2)
vf_positions = [(80, 220), (280, 220), (80, 310), (280, 310)]
vf_labels = ["VF 0", "VF 1", "VF 2", "VF 3"]
for (vx, vy), vlbl in zip(vf_positions, vf_labels):
    box(vx, vy, 150, 60, fill="#dcfce7", stroke="#22c55e", rx=8)
    multiline([vlbl, "（Virtual Function）"], vx+75, vy+30, size=12, color="#166534")
    # arrow from PF
    arrow_down(vx+75, 160, vy, "")

# Connect PF to all VFs with lines
# PF center: (170, 160)
for (vx, vy) in vf_positions:
    dwg.add(dwg.line((170, 160), (vx+75, 220), stroke=ARROW, stroke_width=1.2))

# IOMMU
box(80, 390, 180, 50, fill="#fef3c7", stroke="#f59e0b", rx=8)
multiline(["IOMMU", "（記憶體保護）"], 170, 415, size=12, color="#92400e")

# VFIO
box(280, 390, 180, 50, fill="#fee2e2", stroke="#ef4444", rx=8)
multiline(["VFIO Driver", "（使用者態存取）"], 370, 415, size=12, color="#991b1b")

# VF0/1 -> IOMMU
dwg.add(dwg.line((155, 380), (170, 440), stroke=ARROW, stroke_width=1.2))
dwg.add(dwg.line((355, 380), (170, 440), stroke=ARROW, stroke_width=1.2))
arrow_r(260, 280, 415, "")

# Kubernetes Pods container
box(630, 120, 240, 240, fill="#f0fdf4", stroke="#86efac", rx=12)
label("Kubernetes Pods", 750, 143, size=12, color=TEXT_SECONDARY)

box(650, 155, 200, 70, fill="#dcfce7", stroke="#22c55e", rx=8)
multiline(["VM 1", "（持有 VF 0）"], 750, 190, size=13, color="#166534")

box(650, 255, 200, 70, fill="#dcfce7", stroke="#22c55e", rx=8)
multiline(["VM 2", "（持有 VF 1）"], 750, 290, size=13, color="#166534")

# VFIO -> VM1, VM2
arrow_r(460, 650, 190, "直通 VF 給 VM")
arrow_r(460, 650, 290, "直通 VF 給 VM")

dwg.save()
print("Saved kubevirt-net-sriov-1.svg")
