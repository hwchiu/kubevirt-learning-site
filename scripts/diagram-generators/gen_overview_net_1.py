#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt networking overview diagram 1 - two-phase setup"""

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
    dwg = svgwrite.Drawing('kubevirt-net-overview-1.svg', size=('1000px', '600px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("KubeVirt 網路設定兩階段流程", insert=(500, 40),
                     text_anchor="middle", font_size=20, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Start node
    dwg.add(dwg.rect(insert=(420, 80), size=(160, 50), rx=8, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    dwg.add(dwg.text("virt-launcher Pod 啟動", insert=(500, 110),
                     text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # Arrow down to Phase 1
    dwg.add(dwg.line(start=(500, 130), end=(500, 170), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    # Phase 1 container
    phase1_g = dwg.g()
    phase1_g.add(dwg.rect(insert=(200, 170), size=(600, 140), rx=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
    phase1_g.add(dwg.text("Phase 1: Privileged Setup", insert=(500, 195),
                         text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # Phase 1 boxes
    tasks = [
        ("修改 Linux Network\nNamespace", 220, 220),
        ("建立 Linux Bridge\n/ TAP 設備", 380, 220),
        ("設定 iptables\n/ nftables 規則", 540, 220),
        ("設定 IP 地址\n和路由", 700, 220)
    ]
    
    for text, x, y in tasks:
        phase1_g.add(dwg.rect(insert=(x, y), size=(140, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
        lines = text.split('\n')
        for i, line in enumerate(lines):
            phase1_g.add(dwg.text(line, insert=(x + 70, y + 30 + i*18),
                                 text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    
    dwg.add(phase1_g)
    
    # Arrow down to Phase 2
    dwg.add(dwg.line(start=(500, 310), end=(500, 350), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    # Phase 2 container
    phase2_g = dwg.g()
    phase2_g.add(dwg.rect(insert=(200, 350), size=(600, 140), rx=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
    phase2_g.add(dwg.text("Phase 2: Unprivileged Setup", insert=(500, 375),
                         text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # Phase 2 boxes
    tasks2 = [
        ("設定 QEMU\n網路裝置", 260, 400),
        ("建立 virtio-net\n/ e1000 虛擬 NIC", 420, 400),
        ("連接 TAP 設備\n到 QEMU", 620, 400)
    ]
    
    for text, x, y in tasks2:
        phase2_g.add(dwg.rect(insert=(x, y), size=(140, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
        lines = text.split('\n')
        for i, line in enumerate(lines):
            phase2_g.add(dwg.text(line, insert=(x + 70, y + 30 + i*18),
                                 text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    
    dwg.add(phase2_g)
    
    # Arrow down to final state
    dwg.add(dwg.line(start=(500, 490), end=(500, 530), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    # Final state
    dwg.add(dwg.rect(insert=(400, 530), size=(200, 50), rx=8, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    dwg.add(dwg.text("VM 啟動，網路就緒", insert=(500, 560),
                     text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    dwg.save()
    print("Generated: kubevirt-net-overview-1.svg")

if __name__ == '__main__':
    create_diagram()
