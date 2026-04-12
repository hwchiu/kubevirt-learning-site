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

W, H = 900, 560
svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(W), height=str(H), viewBox=f"0 0 {W} {H}")
ET.SubElement(svg, "rect", width=str(W), height=str(H), fill=BG)

defs = ET.SubElement(svg, "defs")
marker = ET.SubElement(defs, "marker", id="arr", markerWidth="8", markerHeight="8",
                        refX="6", refY="3", orient="auto")
ET.SubElement(marker, "path", d="M0,0 L0,6 L8,3 z", fill=ARROW)

def rr(x, y, w, h, fill, stroke, rx="10"):
    ET.SubElement(svg, "rect", x=str(x), y=str(y), width=str(w), height=str(h),
                  fill=fill, stroke=stroke, **{"stroke-width": "1.5", "rx": rx})

def txt(x, y, content, size=13, fill=TEXT_PRIMARY, anchor="middle", weight="normal"):
    t = ET.SubElement(svg, "text", x=str(x), y=str(y),
                      **{"font-family": FONT, "font-size": str(size), "fill": fill,
                         "text-anchor": anchor, "dominant-baseline": "middle", "font-weight": weight})
    t.text = content

def arr_line(x1, y1, x2, y2, label="", label_offset_x=0, label_offset_y=-14):
    ET.SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        mx, my = (x1+x2)//2 + label_offset_x, (y1+y2)//2 + label_offset_y
        txt(mx, my, label, size=11, fill=TEXT_SECONDARY)

def state_box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    rr(x, y, w, h, fill, stroke)
    txt(x+w//2, y+h//2, label, size=13, fill=TEXT_PRIMARY, weight="bold")

def start_end(x, y, r, is_end=False):
    ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r),
                  fill=TEXT_PRIMARY if not is_end else "#ffffff",
                  stroke=TEXT_PRIMARY, **{"stroke-width": "2"})
    if is_end:
        ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r-4), fill=TEXT_PRIMARY)

# Title
txt(W//2, 28, "VMI Phase 狀態機", size=18, fill=TEXT_PRIMARY, weight="bold")

# States layout
BW, BH = 140, 44

# Row 1: start → Pending → Scheduling → Scheduled → Running
start_end(60, 90, 14)
state_box(100, 68, BW, BH, "Pending")
state_box(270, 68, BW, BH, "Scheduling")
state_box(440, 68, BW, BH, "Scheduled")
state_box(620, 68, BW, BH, "Running", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Row 2: terminal states
state_box(550, 200, BW, BH, "Succeeded", fill="#dcfce7", stroke="#86efac")
state_box(700, 200, BW, BH, "Failed", fill="#fef2f2", stroke="#fca5a5")
state_box(400, 200, BW, BH, "Unknown", fill="#fefce8", stroke="#fde68a")

# Live Migration state
state_box(620, 330, BW, BH, "Live Migration", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# End states
start_end(620, 440, 14, is_end=True)
start_end(760, 440, 14, is_end=True)
start_end(480, 440, 14, is_end=True)
start_end(480, 320, 14, is_end=True)

# Arrows
arr_line(74, 90, 100, 90, "")
arr_line(240, 90, 270, 90, "建立 VMI")
arr_line(410, 90, 440, 90, "尋找可用節點")
arr_line(580, 90, 620, 90, "節點已選定")

# Running → Succeeded
arr_line(620+BW//2, 68+BH, 620, 200, "Guest 正常關機", label_offset_x=-20)

# Running → Failed
arr_line(620+BW, 68+BH//2, 700+BW//2, 200, "異常終止")

# Running → Unknown
arr_line(620, 68+BH//2, 400+BW//2, 200, "節點失聯", label_offset_y=-18)

# Running → Live Migration
arr_line(620+BW//2, 68+BH, 620+BW//2, 330, "Live Migration 中", label_offset_x=55, label_offset_y=0)

# Live Migration → Running (loop back)
ET.SubElement(svg, "path", d="M 760,352 C 820,352 820,90 760,90", stroke=ARROW,
              fill="none", **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
txt(850, 220, "遷移完成", size=11, fill=TEXT_SECONDARY)

# Succeeded, Failed, Unknown → end
arr_line(620, 200+BH, 620, 440-14, "")
arr_line(770, 200+BH, 760, 440-14, "")
arr_line(470, 200+BH, 480, 320-14, "")

# Node failure end
txt(480, 360, "節點失聯", size=11, fill=TEXT_SECONDARY)

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-vmvmi-2.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
