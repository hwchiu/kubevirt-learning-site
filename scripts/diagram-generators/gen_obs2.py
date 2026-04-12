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

W, H = 960, 700
svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(W), height=str(H), viewBox=f"0 0 {W} {H}")
ET.SubElement(svg, "rect", width=str(W), height=str(H), fill=BG)

defs = ET.SubElement(svg, "defs")
marker = ET.SubElement(defs, "marker", id="arr", markerWidth="8", markerHeight="8",
                        refX="6", refY="3", orient="auto")
ET.SubElement(marker, "path", d="M0,0 L0,6 L8,3 z", fill=ARROW)

def rr(x, y, w, h, fill, stroke, rx="8"):
    ET.SubElement(svg, "rect", x=str(x), y=str(y), width=str(w), height=str(h),
                  fill=fill, stroke=stroke, **{"stroke-width": "1.5", "rx": rx})

def txt(x, y, content, size=13, fill=TEXT_PRIMARY, anchor="middle", weight="normal"):
    t = ET.SubElement(svg, "text", x=str(x), y=str(y),
                      **{"font-family": FONT, "font-size": str(size), "fill": fill,
                         "text-anchor": anchor, "dominant-baseline": "middle", "font-weight": weight})
    t.text = content

def arr(x1, y1, x2, y2, label=""):
    ET.SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                  stroke=ARROW, **{"stroke-width": "1.5", "marker-end": "url(#arr)"})
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2 - 10
        txt(mx, my, label, size=11, fill=TEXT_SECONDARY)

def diamond(x, y, w, h, label):
    pts = f"{x},{y-h//2} {x+w//2},{y} {x},{y+h//2} {x-w//2},{y}"
    ET.SubElement(svg, "polygon", points=pts, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE,
                  **{"stroke-width": "1.5"})
    txt(x, y, label, size=12, fill=TEXT_PRIMARY)

def oval(x, y, w, h, label):
    ET.SubElement(svg, "ellipse", cx=str(x), cy=str(y), rx=str(w//2), ry=str(h//2),
                  fill="#dcfce7", stroke="#86efac", **{"stroke-width": "1.5"})
    txt(x, y, label, size=12, fill=TEXT_PRIMARY)

def box(x, y, w, h, lines, fill=BOX_FILL, stroke=BOX_STROKE):
    rr(x, y, w, h, fill, stroke)
    for i, l in enumerate(lines):
        txt(x+w//2, y+h//2 - (len(lines)-1)*9 + i*18, l, size=11, fill=TEXT_PRIMARY)

# Title
txt(W//2, 28, "VMI 問題排查流程圖", size=18, fill=TEXT_PRIMARY, weight="bold")

# Start
oval(480, 65, 160, 36, "開始排查")
arr(480, 83, 480, 115)

# Step A
box(390, 120, 180, 50, ["kubectl get vmi -A", "確認 VMI 狀態"])
arr(480, 170, 480, 205)

# Decision
diamond(480, 230, 160, 60, "VMI Phase?")

# Branches
# Pending
arr(400, 230, 200, 280, "Pending")
box(110, 280, 180, 50, ["kubectl describe vmi", "查看 events"])
arr(200, 330, 200, 380)
box(110, 380, 180, 50, ["確認資源是否足夠", "PVC 是否就緒"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Scheduling
arr(480, 260, 480, 300, "Scheduling")
box(390, 300, 180, 50, ["kubectl get node", "確認節點狀態"])
arr(480, 350, 480, 400)
box(390, 400, 180, 50, ["確認節點 taint/label", "是否有 KVM"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Running with issues
arr(560, 230, 720, 280, "Running 但有問題")
box(640, 280, 180, 50, ["kubectl describe vmi", "查看 conditions"])
arr(730, 330, 730, 380)
box(640, 380, 180, 50, ["kubectl logs virt-launcher", "查看詳細日誌"])
arr(730, 430, 730, 470)

# Sub decision
diamond(730, 500, 160, 55, "問題類型?")

# Network
arr(730, 527, 580, 580, "網路")
box(490, 580, 170, 50, ["查看 virt-handler logs", "確認 CNI 設定"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Disk
arr(730, 527, 730, 580, "磁碟")
box(650, 580, 160, 50, ["查看 PVC 狀態", "確認 StorageClass"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# QEMU crash
arr(730, 527, 870, 580, "QEMU crash")
box(800, 580, 145, 50, ["查看 libvirt/QEMU logs", "在 launcher pod 內"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# Failed
arr(560, 255, 870, 300, "Failed")
box(800, 280, 160, 50, ["kubectl get events", "查看失敗原因"])
arr(880, 330, 880, 390)
box(800, 390, 160, 50, ["查看 virt-handler logs", "virt-controller logs"], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE)

# End
oval(480, 655, 200, 36, "解決或提交 issue")

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-observability-2.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
