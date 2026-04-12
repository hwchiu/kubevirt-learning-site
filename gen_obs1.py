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

W, H = 960, 560

svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(W), height=str(H), viewBox=f"0 0 {W} {H}")

# Background
ET.SubElement(svg, "rect", width=str(W), height=str(H), fill=BG)

def rect(parent, x, y, w, h, fill, stroke, rx="8"):
    ET.SubElement(parent, "rect", x=str(x), y=str(y), width=str(w), height=str(h),
                  fill=fill, stroke=stroke, **{"stroke-width": "1.5", "rx": rx})

def text(parent, x, y, content, size=13, fill=TEXT_PRIMARY, anchor="middle", weight="normal"):
    t = ET.SubElement(parent, "text", x=str(x), y=str(y),
                      **{"font-family": FONT, "font-size": str(size), "fill": fill,
                         "text-anchor": anchor, "dominant-baseline": "middle", "font-weight": weight})
    t.text = content

def arrow(parent, x1, y1, x2, y2, label=""):
    ET.SubElement(parent, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2
        text(parent, mx, my-10, label, size=11, fill=TEXT_SECONDARY)

# Arrowhead
defs = ET.SubElement(svg, "defs")
marker = ET.SubElement(defs, "marker", id="arr", markerWidth="8", markerHeight="8",
                        refX="6", refY="3", orient="auto")
ET.SubElement(marker, "path", d="M0,0 L0,6 L8,3 z", fill=ARROW)

# Title
text(svg, W//2, 30, "KubeVirt 日誌架構", size=18, fill=TEXT_PRIMARY, weight="bold")

# kubevirt namespace container
rect(svg, 30, 60, 340, 160, CONTAINER_FILL, CONTAINER_STROKE, rx="10")
text(svg, 200, 80, "kubevirt namespace", size=12, fill=TEXT_SECONDARY)

# Nodes in kubevirt ns
def component_box(parent, x, y, lines):
    rect(parent, x, y, 140, 50, BOX_FILL, BOX_STROKE)
    for i, l in enumerate(lines):
        text(parent, x+70, y+15+i*18, l, size=11, fill=TEXT_PRIMARY)

component_box(svg, 50, 95, ["virt-api", "Deployment"])
component_box(svg, 210, 95, ["virt-controller", "Deployment"])
component_box(svg, 50, 165, ["virt-operator", "Deployment"])

# Worker node container
rect(svg, 390, 60, 260, 160, CONTAINER_FILL, CONTAINER_STROKE, rx="10")
text(svg, 520, 80, "每個 Worker Node", size=12, fill=TEXT_SECONDARY)

component_box(svg, 410, 95, ["virt-handler", "DaemonSet"])
component_box(svg, 410, 165, ["virt-launcher Pod", "(per VM)"])

# virt-launcher internals container
rect(svg, 670, 60, 260, 160, CONTAINER_FILL, CONTAINER_STROKE, rx="10")
text(svg, 800, 80, "virt-launcher Pod 內部", size=12, fill=TEXT_SECONDARY)

component_box(svg, 690, 95, ["libvirtd", "/var/log/libvirt/"])
component_box(svg, 690, 165, ["qemu process", "/var/log/libvirt/qemu/"])

# Log stores
LOG_Y = 360
log_positions = [120, 300, 480, 660, 820]
log_labels = ["virt-api\nlogs", "virt-controller\nlogs", "virt-handler\nlogs", "virt-launcher\nlogs", ""]

def log_box(parent, x, y, lines):
    rect(parent, x-65, y-20, 130, 55, "#eff6ff", "#bfdbfe", rx="6")
    for i, l in enumerate(lines):
        text(parent, x, y-5+i*18, l, size=11, fill=TEXT_SECONDARY)

log_box(svg, 120, 380, ["virt-api logs"])
log_box(svg, 310, 380, ["virt-controller", "logs"])
log_box(svg, 500, 380, ["virt-handler logs"])
log_box(svg, 700, 380, ["virt-launcher logs"])

# Arrows from components to logs
arrow(svg, 120, 145, 120, 360, "API 驗證失敗")
arrow(svg, 280, 120, 310, 360, "VMI 建立控制")
arrow(svg, 480, 120, 500, 360, "節點層級操作")
arrow(svg, 560, 145, 700, 360, "VM 運行狀態")
arrow(svg, 760, 145, 700, 360, "詳細 VM 日誌")

# launcher component label
text(svg, 800, 230, "launcher process", size=11, fill=TEXT_SECONDARY)
rect(svg, 700, 220, 140, 30, BOX_FILL, BOX_STROKE, rx="4")

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-observability-1.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
