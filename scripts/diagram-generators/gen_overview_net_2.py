#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt networking overview diagram 2 - architecture"""

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
    dwg = svgwrite.Drawing('kubevirt-net-overview-2.svg', size=('1400px', '900px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("KubeVirt 網路架構總覽", insert=(700, 40),
                     text_anchor="middle", font_size=22, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Kubernetes Cluster container
    k8s_g = dwg.g()
    k8s_g.add(dwg.rect(insert=(50, 70), size=(1300, 680), rx=10, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2.5, opacity=0.3))
    k8s_g.add(dwg.text("Kubernetes Cluster", insert=(700, 100),
                      text_anchor="middle", font_size=18, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # Node 1
    node1_g = dwg.g()
    node1_g.add(dwg.rect(insert=(80, 130), size=(550, 300), rx=8, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    node1_g.add(dwg.text("Node 1", insert=(355, 160),
                        text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # virt-launcher Pod
    pod_g = dwg.g()
    pod_g.add(dwg.rect(insert=(110, 180), size=(480, 200), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    pod_g.add(dwg.text("virt-launcher Pod", insert=(350, 205),
                      text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # VM
    pod_g.add(dwg.rect(insert=(130, 220), size=(140, 80), rx=6, fill="#ffffff", stroke=BOX_STROKE, stroke_width=1.5))
    pod_g.add(dwg.text("🖥️ Virtual Machine", insert=(200, 245),
                      text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    pod_g.add(dwg.text("(QEMU/KVM)", insert=(200, 265),
                      text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    
    # TAP Device
    pod_g.add(dwg.rect(insert=(290, 220), size=(100, 80), rx=6, fill="#ffffff", stroke=BOX_STROKE, stroke_width=1.5))
    pod_g.add(dwg.text("TAP Device", insert=(340, 250),
                      text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    pod_g.add(dwg.text("(tap0)", insert=(340, 270),
                      text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Linux Bridge
    pod_g.add(dwg.rect(insert=(410, 220), size=(100, 80), rx=6, fill="#ffffff", stroke=BOX_STROKE, stroke_width=1.5))
    pod_g.add(dwg.text("Linux Bridge", insert=(460, 250),
                      text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    pod_g.add(dwg.text("(br0)", insert=(460, 270),
                      text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Pod eth0
    pod_g.add(dwg.rect(insert=(130, 320), size=(380, 40), rx=6, fill="#ffffff", stroke=BOX_STROKE, stroke_width=1.5))
    pod_g.add(dwg.text("Pod eth0 (10.244.1.5)", insert=(320, 345),
                      text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Arrows within pod
    pod_g.add(dwg.line(start=(270, 260), end=(290, 260), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    pod_g.add(dwg.text("virtio-net", insert=(280, 250),
                      text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    pod_g.add(dwg.line(start=(390, 260), end=(410, 260), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    pod_g.add(dwg.line(start=(460, 300), end=(460, 320), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    node1_g.add(pod_g)
    
    # Init Container
    node1_g.add(dwg.rect(insert=(110, 400), size=(200, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    node1_g.add(dwg.text("Init Container", insert=(210, 425),
                        text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    node1_g.add(dwg.text("(Privileged Phase 1)", insert=(210, 443),
                        text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    node1_g.add(dwg.text("建立 bridge/iptables", insert=(210, 460),
                        text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Arrow from init to bridge
    node1_g.add(dwg.line(start=(310, 435), end=(390, 290), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)', stroke_dasharray="4,4"))
    node1_g.add(dwg.text("初始化網路", insert=(360, 360),
                        font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    k8s_g.add(node1_g)
    
    # Node 2
    node2_g = dwg.g()
    node2_g.add(dwg.rect(insert=(680, 130), size=(450, 300), rx=8, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    node2_g.add(dwg.text("Node 2", insert=(905, 160),
                        text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # virt-launcher Pod 2
    pod2_g = dwg.g()
    pod2_g.add(dwg.rect(insert=(710, 180), size=(390, 200), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    pod2_g.add(dwg.text("virt-launcher Pod 2", insert=(905, 205),
                       text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # VM 2
    pod2_g.add(dwg.rect(insert=(740, 230), size=(150, 80), rx=6, fill="#ffffff", stroke=BOX_STROKE, stroke_width=1.5))
    pod2_g.add(dwg.text("🖥️ VM 2", insert=(815, 255),
                       text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    pod2_g.add(dwg.text("(SR-IOV)", insert=(815, 275),
                       text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    
    # SR-IOV VF
    pod2_g.add(dwg.rect(insert=(920, 230), size=(150, 80), rx=6, fill="#ffffff", stroke=BOX_STROKE, stroke_width=1.5))
    pod2_g.add(dwg.text("SR-IOV VF", insert=(995, 260),
                       text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    pod2_g.add(dwg.text("直通", insert=(995, 280),
                       text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Arrow VM2 to VF
    pod2_g.add(dwg.line(start=(890, 270), end=(920, 270), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    pod2_g.add(dwg.text("PCIe pass-through", insert=(905, 255),
                       text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    
    node2_g.add(pod2_g)
    k8s_g.add(node2_g)
    
    # CNI Plugin
    k8s_g.add(dwg.rect(insert=(80, 480), size=(200, 80), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    k8s_g.add(dwg.text("CNI Plugin", insert=(180, 510),
                      text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    k8s_g.add(dwg.text("(Calico/Cilium/Flannel)", insert=(180, 530),
                      text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Multus CNI
    k8s_g.add(dwg.rect(insert=(330, 480), size=(200, 80), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    k8s_g.add(dwg.text("Multus CNI", insert=(430, 510),
                      text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    k8s_g.add(dwg.text("多網卡協調器", insert=(430, 530),
                      text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # NAD
    k8s_g.add(dwg.rect(insert=(580, 480), size=(200, 80), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    k8s_g.add(dwg.text("NetworkAttachment", insert=(680, 510),
                      text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    k8s_g.add(dwg.text("Definition", insert=(680, 525),
                      text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    k8s_g.add(dwg.text("附加網路設定", insert=(680, 545),
                      text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.add(k8s_g)
    
    # Physical Network
    phy_g = dwg.g()
    phy_g.add(dwg.rect(insert=(50, 780), size=(1300, 100), rx=10, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2.5, opacity=0.3))
    phy_g.add(dwg.text("Physical Network", insert=(700, 810),
                      text_anchor="middle", font_size=18, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # Physical NIC
    phy_g.add(dwg.rect(insert=(500, 830), size=(180, 40), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    phy_g.add(dwg.text("物理 NIC (SR-IOV PF)", insert=(590, 855),
                      text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Switch
    phy_g.add(dwg.rect(insert=(740, 830), size=(180, 40), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    phy_g.add(dwg.text("Top-of-Rack Switch", insert=(830, 855),
                      text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    
    dwg.add(phy_g)
    
    # Connecting arrows
    # Pod eth0 to CNI
    dwg.add(dwg.line(start=(320, 360), end=(180, 480), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("Pod CIDR", insert=(240, 410),
                    font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # CNI to Switch
    dwg.add(dwg.line(start=(180, 560), end=(780, 830), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    # Multus to NAD
    dwg.add(dwg.line(start=(530, 520), end=(580, 520), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("管理", insert=(555, 510),
                    text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    
    # NAD to Bridge (Node 1)
    dwg.add(dwg.line(start=(680, 480), end=(460, 300), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)', stroke_dasharray="4,4"))
    dwg.add(dwg.text("設定", insert=(570, 380),
                    font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    
    # VF to Physical NIC
    dwg.add(dwg.line(start=(995, 380), end=(590, 830), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("PF VF", insert=(780, 600),
                    font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Physical NIC to Switch
    dwg.add(dwg.line(start=(680, 850), end=(740, 850), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    dwg.save()
    print("Generated: kubevirt-net-overview-2.svg")

if __name__ == '__main__':
    create_diagram()
