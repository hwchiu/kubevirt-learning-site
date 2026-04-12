#!/usr/bin/env python3
"""Block 2: sriov.md - VFIO driver architecture (graph LR)"""
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

W, H = 860, 300
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-sriov-2.svg",
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
        dwg.add(dwg.text(line, insert=(cx, sy+i*gap), text_anchor="middle",
                         font_family=FONT, font_size=size, fill=color))

def arrow_r(x1, x2, y, lbl=""):
    dwg.add(dwg.line((x1,y),(x2,y), stroke=ARROW, stroke_width=1.5))
    dwg.add(dwg.polygon([(x2,y),(x2-9,y-4),(x2-9,y+4)], fill=ARROW))
    if lbl:
        mid = (x1+x2)/2
        dwg.add(dwg.text(lbl, insert=(mid, y-7), text_anchor="middle",
                         font_family=FONT, font_size=11, fill=TEXT_SECONDARY))

# Title
label("VFIO 驅動架構", W//2, 34, size=18, weight="600")

# Kernel Space container
box(30, 60, 370, 200, fill="#fafbff", stroke=CONTAINER_STROKE, rx=10)
label("核心態 Kernel Space", 215, 82, size=12, color=TEXT_SECONDARY)

# VFIO Kernel module
box(55, 100, 190, 70, fill="#dbeafe", stroke="#3b82f6", rx=8)
multiline(["VFIO Kernel Module", "（vfio, vfio-pci）"], 150, 135, size=12, color="#1d4ed8")

# IOMMU group
box(55, 195, 190, 55, fill="#fef3c7", stroke="#f59e0b", rx=8)
multiline(["IOMMU Group", "（裝置隔離邊界）"], 150, 222, size=12, color="#92400e")

arrow_r(150, 150, 185, "")
dwg.add(dwg.line((150,170),(150,195), stroke=ARROW, stroke_width=1.5))
dwg.add(dwg.polygon([(150,195),(146,186),(154,186)], fill=ARROW))

# User Space container
box(460, 60, 370, 200, fill="#fafbff", stroke=CONTAINER_STROKE, rx=10)
label("使用者態 User Space", 645, 82, size=12, color=TEXT_SECONDARY)

# QEMU
box(485, 100, 155, 70, fill="#dcfce7", stroke="#22c55e", rx=8)
multiline(["QEMU/KVM", "（VM Hypervisor）"], 562, 135, size=12, color="#166534")

# VFIO user API
box(485, 195, 155, 55, fill="#fee2e2", stroke="#ef4444", rx=8)
multiline(["VFIO User API", "/dev/vfio/"], 562, 222, size=12, color="#991b1b")

# IOMMU group -> VFIO user API
arrow_r(245, 485, 222, "安全 DMA")

# VFIO user -> QEMU (arrow up)
dwg.add(dwg.line((562,195),(562,170), stroke=ARROW, stroke_width=1.5))
dwg.add(dwg.polygon([(562,170),(558,179),(566,179)], fill=ARROW))

dwg.save()
print("Saved kubevirt-net-sriov-2.svg")
