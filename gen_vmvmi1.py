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

W, H = 880, 380
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

def arr_h(x1, y, x2, label=""):
    ET.SubElement(svg, "line", x1=str(x1), y1=str(y), x2=str(x2), y2=str(y),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        mx = (x1+x2)//2
        txt(mx, y-14, label, size=11, fill=TEXT_SECONDARY)

def arr_v(x, y1, y2, label=""):
    ET.SubElement(svg, "line", x1=str(x), y1=str(y1), x2=str(x), y2=str(y2),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        txt(x+55, (y1+y2)//2, label, size=11, fill=TEXT_SECONDARY)

def arr_diag(x1, y1, x2, y2, label=""):
    ET.SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2
        txt(mx, my-14, label, size=11, fill=TEXT_SECONDARY)

def box(x, y, w, h, lines, fill=BOX_FILL, stroke=BOX_STROKE):
    rr(x, y, w, h, fill, stroke)
    for i, l in enumerate(lines):
        txt(x+w//2, y+h//2 - (len(lines)-1)*9 + i*18, l, size=12, fill=TEXT_PRIMARY)

# Title
txt(W//2, 28, "VM / VMI 資源關係圖", size=18, fill=TEXT_PRIMARY, weight="bold")

# Layout: VM (left), VMI (center-left), Pod (center-right), QEMU (right), DV (bottom-left)
VM_X, VM_Y = 60, 130
VMI_X, VMI_Y = 270, 130
POD_X, POD_Y = 490, 130
QEMU_X, QEMU_Y = 700, 130
DV_X, DV_Y = 60, 280

BOX_W, BOX_H = 160, 70

box(VM_X, VM_Y, BOX_W, BOX_H, ["VirtualMachine (VM)", "宣告式資源"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)
box(VMI_X, VMI_Y, BOX_W, BOX_H, ["VirtualMachineInstance", "(VMI) 執行實體"])
box(POD_X, POD_Y, BOX_W, BOX_H, ["virt-launcher Pod", "(per VMI)"])
box(QEMU_X, QEMU_Y, BOX_W, BOX_H, ["QEMU/KVM", "Process"])
box(DV_X, DV_Y, BOX_W, BOX_H, ["DataVolume / PVC", "儲存資源"], fill="#fefce8", stroke="#fde68a")

# Arrows
arr_h(VM_X+BOX_W, VM_Y+BOX_H//2, VMI_X, "creates/deletes")
arr_h(VMI_X+BOX_W, VMI_Y+BOX_H//2, POD_X, "schedules on")
arr_h(POD_X+BOX_W, POD_Y+BOX_H//2, QEMU_X, "spawns")
arr_v(VM_X+BOX_W//2, VM_Y+BOX_H, DV_Y, "references")
arr_diag(DV_X+BOX_W, DV_Y+BOX_H//2, VMI_X+BOX_W//2, VMI_Y+BOX_H, "provides disk")

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-vmvmi-1.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
