#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt SR-IOV diagram 1 - performance comparison"""

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
    dwg = svgwrite.Drawing('kubevirt-net-sriov-3.svg', size=('1200px', '400px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("網路模式效能比較", insert=(600, 40),
                     text_anchor="middle", font_size=20, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Software network (left)
    sw_g = dwg.g()
    sw_g.add(dwg.rect(insert=(50, 100), size=(500, 250), rx=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
    sw_g.add(dwg.text("軟體網路（Bridge/Masquerade）", insert=(300, 135),
                     text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # VM box
    sw_g.add(dwg.rect(insert=(90, 170), size=(100, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    sw_g.add(dwg.text("VM", insert=(140, 210),
                     text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # Kernel stack
    sw_g.add(dwg.rect(insert=(250, 170), size=(140, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    sw_g.add(dwg.text("Linux 核心", insert=(320, 195),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    sw_g.add(dwg.text("網路棧", insert=(320, 215),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Physical NIC
    sw_g.add(dwg.rect(insert=(440, 170), size=(90, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    sw_g.add(dwg.text("實體", insert=(485, 200),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    sw_g.add(dwg.text("網卡", insert=(485, 220),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Arrows
    sw_g.add(dwg.line(start=(190, 205), end=(250, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    sw_g.add(dwg.text("virtio", insert=(220, 195),
                     text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    sw_g.add(dwg.line(start=(390, 205), end=(440, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    # Performance note
    sw_g.add(dwg.text("延遲: ~50-100μs", insert=(300, 280),
                     text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    sw_g.add(dwg.text("吞吐量: ~10-20 Gbps", insert=(300, 300),
                     text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.add(sw_g)
    
    # SR-IOV (right)
    sriov_g = dwg.g()
    sriov_g.add(dwg.rect(insert=(650, 100), size=(500, 250), rx=8, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    sriov_g.add(dwg.text("SR-IOV 硬體直通", insert=(900, 135),
                        text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # VM box
    sriov_g.add(dwg.rect(insert=(690, 170), size=(100, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    sriov_g.add(dwg.text("VM", insert=(740, 210),
                        text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # VF hardware
    sriov_g.add(dwg.rect(insert=(850, 170), size=(100, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    sriov_g.add(dwg.text("VF 硬體", insert=(900, 210),
                        text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Physical NIC
    sriov_g.add(dwg.rect(insert=(1010, 170), size=(90, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    sriov_g.add(dwg.text("實體", insert=(1055, 200),
                        text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    sriov_g.add(dwg.text("網卡", insert=(1055, 220),
                        text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Arrows
    sriov_g.add(dwg.line(start=(790, 205), end=(850, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    sriov_g.add(dwg.text("VFIO 直通", insert=(820, 195),
                        text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    sriov_g.add(dwg.line(start=(950, 205), end=(1010, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    
    # Performance note
    sriov_g.add(dwg.text("延遲: ~5-15μs ⚡", insert=(900, 280),
                        text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY, font_weight="600"))
    sriov_g.add(dwg.text("吞吐量: 25-100 Gbps ⚡", insert=(900, 300),
                        text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY, font_weight="600"))
    
    dwg.add(sriov_g)
    
    dwg.save()
    print("Generated: kubevirt-net-sriov-3.svg")

if __name__ == '__main__':
    create_diagram()
