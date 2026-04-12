#!/usr/bin/env python3
import xml.etree.ElementTree as ET

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 960, 380
svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(W), height=str(H), viewBox=f"0 0 {W} {H}")
ET.SubElement(svg, "rect", width=str(W), height=str(H), fill=BG)

defs = ET.SubElement(svg, "defs")
marker = ET.SubElement(defs, "marker", id="arr", markerWidth="8", markerHeight="8",
                        refX="6", refY="3", orient="auto")
ET.SubElement(marker, "path", d="M0,0 L0,6 L8,3 z", fill=ARROW)

def rr(x, y, w, h, fill, stroke, rx="10"):
    ET.SubElement(svg, "rect", x=str(x), y=str(y), width=str(w), height=str(h),
                  fill=fill, stroke=stroke, **{"stroke-width": "1.5", "rx": rx})

def txt(x, y, content, size=12, fill=TEXT_PRIMARY, anchor="middle", weight="normal"):
    t = ET.SubElement(svg, "text", x=str(x), y=str(y),
                      **{"font-family": FONT, "font-size": str(size), "fill": fill,
                         "text-anchor": anchor, "dominant-baseline": "middle", "font-weight": weight})
    t.text = content

def arr_line(x1, y1, x2, y2, label="", lox=0, loy=-14):
    ET.SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        mx, my = (x1+x2)//2 + lox, (y1+y2)//2 + loy
        txt(mx, my, label, size=11, fill=TEXT_SECONDARY)

def box(x, y, w, h, lines, fill=BOX_FILL, stroke=BOX_STROKE):
    rr(x, y, w, h, fill, stroke)
    for i, l in enumerate(lines):
        txt(x+w//2, y+h//2 - (len(lines)-1)*9 + i*18, l, size=12, fill=TEXT_PRIMARY)

# Title
txt(W//2, 28, "HPA 與 VMIRS/VirtualMachinePool 自動擴縮架構", size=17, fill=TEXT_PRIMARY, weight="bold")

# Nodes
HPA_X, HPA_Y = 60, 150
MS_X, MS_Y = 320, 60
VMIRS_X, VMIRS_Y = 320, 250
VMI_Y = 150

box(HPA_X, HPA_Y, 180, 70, ["HPA", "(HorizontalPodAutoscaler)"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)
box(MS_X, MS_Y, 200, 60, ["Metrics Server", "或 Custom Metrics API"], fill="#fefce8", stroke="#fde68a")
box(VMIRS_X, VMIRS_Y, 200, 60, ["VMIRS / VirtualMachinePool", "副本集控制器"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# VMI instances
vmi_positions = [600, 720, 840]
vmi_labels = ["VMI-0", "VMI-1", "VMI-N"]
for i, (vx, vl) in enumerate(zip(vmi_positions, vmi_labels)):
    box(vx, VMI_Y, 90, 50, [vl])

# Arrows HPA → Metrics Server
arr_line(HPA_X+180, HPA_Y+30, MS_X, MS_Y+30, "查詢 metrics", lox=-30, loy=-14)

# HPA → VMIRS
arr_line(HPA_X+180, HPA_Y+45, VMIRS_X, VMIRS_Y+30, "調整 replicas", lox=-30, loy=14)

# VMIRS → VMIs
for vx in vmi_positions:
    arr_line(VMIRS_X+200, VMIRS_Y+30, vx, VMI_Y+50, "管理", loy=-12)

# Metrics Server → VMIs
for vx in vmi_positions:
    arr_line(MS_X+200//2, MS_Y+60, vx+45, VMI_Y, "收集自", loy=-12)

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-replica-1.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
