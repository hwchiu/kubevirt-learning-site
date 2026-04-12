#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt SR-IOV diagram 2 - architecture"""

import svgwrite

# Notion Clean Style 4
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
ACCENT_FILL = "#eff6ff"
ACCENT_STROKE = "#bfdbfe"

def create_diagram():
    dwg = svgwrite.Drawing('kubevirt-net-sriov-4.svg', size=('1200px', '800px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("KubeVirt SR-IOV 整合架構", insert=(600, 40),
                     text_anchor="middle", font_size=22, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Control Plane
    cp_g = dwg.g()
    cp_g.add(dwg.rect(insert=(50, 80), size=(1100, 180), rx=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
    cp_g.add(dwg.text("控制面 Control Plane", insert=(600, 110),
                     text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # KubeVirt Controller
    cp_g.add(dwg.rect(insert=(100, 140), size=(200, 80), rx=6, fill="#4a9eff", stroke=BOX_STROKE, stroke_width=1.5))
    cp_g.add(dwg.text("KubeVirt Controller", insert=(200, 185),
                     text_anchor="middle", font_size=14, font_family=FONT, fill="#ffffff", font_weight="500"))
    
    # SR-IOV Device Plugin
    cp_g.add(dwg.rect(insert=(400, 140), size=(220, 80), rx=6, fill="#4a9eff", stroke=BOX_STROKE, stroke_width=1.5))
    cp_g.add(dwg.text("SR-IOV Device Plugin", insert=(510, 170),
                     text_anchor="middle", font_size=14, font_family=FONT, fill="#ffffff", font_weight="500"))
    cp_g.add(dwg.text("（管理 VF 資源池）", insert=(510, 190),
                     text_anchor="middle", font_size=11, font_family=FONT, fill="#ffffff"))
    
    # Multus CNI
    cp_g.add(dwg.rect(insert=(720, 140), size=(180, 80), rx=6, fill="#f0ad4e", stroke=BOX_STROKE, stroke_width=1.5))
    cp_g.add(dwg.text("Multus CNI", insert=(810, 170),
                     text_anchor="middle", font_size=14, font_family=FONT, fill="#ffffff", font_weight="500"))
    cp_g.add(dwg.text("（多 CNI 協調器）", insert=(810, 190),
                     text_anchor="middle", font_size=11, font_family=FONT, fill="#ffffff"))
    
    dwg.add(cp_g)
    
    # Node
    node_g = dwg.g()
    node_g.add(dwg.rect(insert=(50, 300), size=(500, 420), rx=8, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    node_g.add(dwg.text("節點 Node", insert=(300, 330),
                       text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # SR-IOV CNI Plugin
    node_g.add(dwg.rect(insert=(90, 360), size=(180, 80), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    node_g.add(dwg.text("SR-IOV CNI Plugin", insert=(180, 390),
                       text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    node_g.add(dwg.text("（設定 VF 網路）", insert=(180, 410),
                       text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # VF Pool
    node_g.add(dwg.rect(insert=(90, 480), size=(180, 100), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    node_g.add(dwg.text("VF 資源池", insert=(180, 510),
                       text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    node_g.add(dwg.text("intel.com/sriov_net_A: 4", insert=(180, 530),
                       text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Physical NIC
    node_g.add(dwg.rect(insert=(90, 620), size=(180, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    node_g.add(dwg.text("實體網卡 PF", insert=(180, 645),
                       text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    node_g.add(dwg.text("（已建立 VF）", insert=(180, 665),
                       text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Arrow VF Pool to PF
    node_g.add(dwg.line(start=(180, 580), end=(180, 620), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    dwg.add(node_g)
    
    # Pod
    pod_g = dwg.g()
    pod_g.add(dwg.rect(insert=(650, 300), size=(500, 420), rx=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
    pod_g.add(dwg.text("Pod", insert=(900, 330),
                      text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # virt-launcher
    pod_g.add(dwg.rect(insert=(720, 380), size=(150, 80), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    pod_g.add(dwg.text("virt-launcher", insert=(795, 425),
                      text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # QEMU VM
    pod_g.add(dwg.rect(insert=(720, 520), size=(360, 150), rx=6, fill="#5cb85c", stroke=BOX_STROKE, stroke_width=1.5))
    pod_g.add(dwg.text("QEMU VM", insert=(900, 560),
                      text_anchor="middle", font_size=15, font_family=FONT, fill="#ffffff", font_weight="600"))
    pod_g.add(dwg.text("（持有 VF）", insert=(900, 585),
                      text_anchor="middle", font_size=12, font_family=FONT, fill="#ffffff"))
    
    # Arrow virt-launcher to QEMU
    pod_g.add(dwg.line(start=(795, 460), end=(795, 520), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    dwg.add(pod_g)
    
    # Connecting arrows
    # SR-IOV Device Plugin to KubeVirt Controller
    dwg.add(dwg.line(start=(400, 180), end=(300, 180), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("宣告 VF 資源", insert=(350, 170),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # KubeVirt Controller to virt-launcher
    dwg.add(dwg.line(start=(200, 220), end=(795, 380), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("分配 VF", insert=(450, 290),
                    font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Multus to SR-IOV CNI
    dwg.add(dwg.line(start=(720, 200), end=(270, 390), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("呼叫 SR-IOV CNI", insert=(450, 280),
                    font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # SR-IOV CNI to VF Pool
    dwg.add(dwg.line(start=(180, 440), end=(180, 480), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("設定 VF，移交給 Pod", insert=(320, 460),
                    font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # virt-launcher to QEMU
    dwg.add(dwg.text("透過 VFIO 存取", insert=(960, 500),
                    font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.save()
    print("Generated: kubevirt-net-sriov-4.svg")

if __name__ == '__main__':
    create_diagram()
