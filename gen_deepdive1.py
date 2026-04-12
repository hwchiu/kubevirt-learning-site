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

W, H = 1000, 620
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

def state(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    rr(x, y, w, h, fill, stroke)
    txt(x+w//2, y+h//2, label, size=13, fill=TEXT_PRIMARY, weight="bold")

def state2(x, y, w, h, lines, fill=BOX_FILL, stroke=BOX_STROKE):
    rr(x, y, w, h, fill, stroke)
    for i, l in enumerate(lines):
        txt(x+w//2, y+h//2 - (len(lines)-1)*9 + i*17, l, size=11, fill=TEXT_SECONDARY)

def start_end(x, y, r, is_end=False):
    ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r), fill=TEXT_PRIMARY,
                  stroke=TEXT_PRIMARY, **{"stroke-width": "2"})
    if is_end:
        ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r-4), fill="#ffffff")
        ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r-8), fill=TEXT_PRIMARY)

# Title
txt(W//2, 28, "VMI 詳細狀態轉換圖（Deep Dive）", size=18, fill=TEXT_PRIMARY, weight="bold")

BW, BH = 150, 44

# Layout column positions (horizontal flow)
# start → VmPhaseUnset → Pending → Scheduling → Scheduled → Running
col_x = [50, 100, 240, 400, 560, 730]
ROW1 = 100

start_end(col_x[0]+14, ROW1+BH//2, 14)
state(col_x[1], ROW1, BW, BH, "VmPhaseUnset")
state(col_x[2], ROW1, BW, BH, "Pending")
state(col_x[3], ROW1, BW, BH, "Scheduling")
state(col_x[4], ROW1, BW, BH, "Scheduled")
state(col_x[5], ROW1, BW, BH, "Running", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Arrows in row 1
arr_line(col_x[0]+28, ROW1+BH//2, col_x[1], ROW1+BH//2, "")
arr_line(col_x[1]+BW, ROW1+BH//2, col_x[2], ROW1+BH//2, "VMI 建立")
arr_line(col_x[2]+BW, ROW1+BH//2, col_x[3], ROW1+BH//2, "virt-controller 處理")
arr_line(col_x[3]+BW, ROW1+BH//2, col_x[4], ROW1+BH//2, "Pod 排程到節點")
arr_line(col_x[4]+BW, ROW1+BH//2, col_x[5], ROW1+BH//2, "libvirt domain 定義")

# Terminal states row 2
ROW2 = 250
state(col_x[3], ROW2, BW, BH, "Failed", fill="#fef2f2", stroke="#fca5a5")
state(col_x[4], ROW2, BW, BH, "Succeeded", fill="#dcfce7", stroke="#86efac")
state(col_x[5], ROW2, BW, BH, "Unknown", fill="#fefce8", stroke="#fde68a")

# Failed arrows
arr_line(col_x[2]+BW//2, ROW1+BH, col_x[3]+BW//2, ROW2, "Spec 不合法", lox=-40)
arr_line(col_x[3]+BW//2, ROW1+BH, col_x[3]+BW//2, ROW2, "資源不足", lox=30)
arr_line(col_x[4]+BW//2, ROW1+BH, col_x[3]+BW//2+10, ROW2, "QEMU 啟動失敗")
arr_line(col_x[5]+BW//2, ROW1+BH, col_x[3]+BW, ROW2+BH//3, "QEMU 崩潰 / OOM", loy=14)

# Running → Succeeded
arr_line(col_x[5]+BW//2, ROW1+BH, col_x[4]+BW//2, ROW2, "Guest OS 正常關機")

# Running → Unknown
arr_line(col_x[5]+BW, ROW1+BH//2, col_x[5]+BW+30, ROW2+BH//2, "", lox=0)
ET.SubElement(svg, "line", x1=str(col_x[5]+BW), y1=str(ROW1+BH//2),
              x2=str(col_x[5]+BW+30), y2=str(ROW1+BH//2),
              stroke=ARROW, **{"stroke-width": "1.5"})
ET.SubElement(svg, "line", x1=str(col_x[5]+BW+30), y1=str(ROW1+BH//2),
              x2=str(col_x[5]+BW+30), y2=str(ROW2+BH//2),
              stroke=ARROW, **{"stroke-width": "1.5"})
arr_line(col_x[5]+BW+30, ROW2+BH//2, col_x[5]+BW, ROW2+BH//2, "virt-handler 通訊中斷")

# WaitingForSync row
ROW3 = 380
state(col_x[5], ROW3, BW, BH, "WaitingForSync", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)
arr_line(col_x[5]+BW//2, ROW2+BH, col_x[5]+BW//2, ROW3, "通訊中斷")  # Unknown → WaitingForSync? No...

# Actually: Running → WaitingForSync, WaitingForSync → Running (migration)
# Fix: Running → WaitingForSync
arr_line(col_x[5]+BW//2, ROW1+BH, col_x[5]+BW//2, ROW3, "Migration 目標等待", lox=50, loy=0)
# WaitingForSync → Running (back)
ET.SubElement(svg, "path", d=f"M {col_x[5]} {ROW3+BH//2} C {col_x[5]-40} {ROW3+BH//2} {col_x[5]-40} {ROW1+BH//2} {col_x[5]} {ROW1+BH//2}",
              stroke=ARROW, fill="none", **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
txt(col_x[5]-70, (ROW1+ROW3)//2+BH//2, "遷移完成", size=11, fill=TEXT_SECONDARY)

# WaitingForSync → Failed
arr_line(col_x[5]+BW//2, ROW3+BH, col_x[3]+BW//2+30, ROW2+BH, "遷移失敗", loy=14)

# Unknown → Running (recovery)
ET.SubElement(svg, "path", d=f"M {col_x[5]+BW+50} {ROW2+BH//4} C {col_x[5]+BW+80} {ROW1+BH//4} {col_x[5]+BW+60} {ROW1+BH//4} {col_x[5]+BW} {ROW1+BH//4}",
              stroke=ARROW, fill="none", **{"stroke-width": "1.5", "stroke-dasharray": "4,4", "marker-end": "url(#arr)"})
txt(col_x[5]+BW+70, (ROW1+ROW2)//2, "通訊恢復", size=11, fill=TEXT_SECONDARY)

# End nodes
start_end(col_x[3]+BW//2, ROW2+BH+40, 14, is_end=True)
start_end(col_x[4]+BW//2, ROW2+BH+40, 14, is_end=True)
arr_line(col_x[3]+BW//2, ROW2+BH, col_x[3]+BW//2, ROW2+BH+26, "")
arr_line(col_x[4]+BW//2, ROW2+BH, col_x[4]+BW//2, ROW2+BH+26, "")

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-arch-deepdive-1.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
