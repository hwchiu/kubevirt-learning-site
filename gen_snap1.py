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

W, H = 900, 480
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

def arr_line(x1, y1, x2, y2, label="", lox=0, loy=-14):
    ET.SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        mx, my = (x1+x2)//2 + lox, (y1+y2)//2 + loy
        txt(mx, my, label, size=11, fill=TEXT_SECONDARY)

def state(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    rr(x, y, w, h, fill, stroke)
    txt(x+w//2, y+h//2, label, size=13, fill=TEXT_PRIMARY, weight="bold")

def start_end(x, y, r, is_end=False):
    ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r), fill=TEXT_PRIMARY,
                  stroke=TEXT_PRIMARY, **{"stroke-width": "2"})
    if is_end:
        ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r-4), fill="#ffffff")
        ET.SubElement(svg, "circle", cx=str(x), cy=str(y), r=str(r-8), fill=TEXT_PRIMARY)

# Title
txt(W//2, 28, "VirtualMachineClone Phase 狀態機", size=18, fill=TEXT_PRIMARY, weight="bold")

BW, BH = 165, 44

# States
# Row 1: start → Pending
start_end(60, 100, 14)
state(95, 78, BW, BH, "Pending")

# Fork: VM source → SnapshotInProgress, Snapshot source → CreatingTargetVM
state(340, 40, 180, BH, "SnapshotInProgress", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)
state(340, 140, 180, BH, "CreatingTargetVM", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# RestoreInProgress
state(590, 140, 180, BH, "RestoreInProgress", fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Succeeded
state(590, 280, BW, BH, "Succeeded", fill="#dcfce7", stroke="#86efac")

# Failed
state(780, 160, BW, BH, "Failed", fill="#fef2f2", stroke="#fca5a5")

# End nodes
start_end(668, 400, 14, is_end=True)
start_end(863, 280, 14, is_end=True)

# Arrows
arr_line(74, 100, 95, 100, "建立 Clone")
# Pending → SnapshotInProgress (if VM source)
arr_line(260, 90, 340, 62, "來源是 VM", lox=-30, loy=-14)
# Pending → CreatingTargetVM (if Snapshot source)
arr_line(260, 110, 340, 162, "來源是 Snapshot", lox=-15, loy=14)
# SnapshotInProgress → CreatingTargetVM
arr_line(340+180//2, 84, 340+180//2, 140, "快照完成")
# CreatingTargetVM → RestoreInProgress
arr_line(520, 162, 590, 162, "VM 建立完成")
# RestoreInProgress → Succeeded
arr_line(680, 184, 668, 280, "所有磁碟還原完成", lox=30)
# SnapshotInProgress → Failed
arr_line(520, 50, 780+BW//2, 160, "快照失敗", loy=-16)
# CreatingTargetVM → Failed
arr_line(520, 162, 780, 180, "VM 建立失敗")
# RestoreInProgress → Failed
arr_line(770, 162, 780, 178, "磁碟還原失敗", lox=15, loy=-12)
# Succeeded → end
arr_line(668, 324, 668, 386, "")
# Failed → end
arr_line(863, 204, 863, 266, "")

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-snapshot-clone-1.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
