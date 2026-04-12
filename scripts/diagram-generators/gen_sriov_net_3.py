#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt SR-IOV diagram 3 - decision tree"""

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
SUCCESS = "#10b981"
ERROR = "#ef4444"

def create_diagram():
    dwg = svgwrite.Drawing('kubevirt-net-sriov-5.svg', size=('1000px', '650px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("SR-IOV 使用決策樹", insert=(500, 40),
                     text_anchor="middle", font_size=20, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Question 1: Need Live Migration?
    dwg.add(dwg.path(d="M 400,80 L 500,120 L 600,80 L 500,40 Z", 
                     fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    dwg.add(dwg.text("需要 Live Migration？", insert=(500, 105),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # Yes branch - cannot use SR-IOV
    dwg.add(dwg.line(start=(400, 100), end=(200, 170), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("是", insert=(290, 130),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.add(dwg.rect(insert=(50, 170), size=(300, 80), rx=6, fill=ERROR, stroke=BOX_STROKE, stroke_width=1.5, opacity=0.9))
    dwg.add(dwg.text("❌ 不能使用 SR-IOV", insert=(200, 200),
                     text_anchor="middle", font_size=14, font_family=FONT, fill="#ffffff", font_weight="600"))
    dwg.add(dwg.text("改用 Bridge 或 Masquerade", insert=(200, 225),
                     text_anchor="middle", font_size=12, font_family=FONT, fill="#ffffff"))
    
    # No branch - check hardware
    dwg.add(dwg.line(start=(600, 100), end=(750, 200), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("否", insert=(680, 145),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Question 2: Hardware support?
    dwg.add(dwg.path(d="M 650,200 L 750,240 L 850,200 L 750,160 Z", 
                     fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    dwg.add(dwg.text("硬體支援 SR-IOV？", insert=(750, 205),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # No hardware support
    dwg.add(dwg.line(start=(850, 220), end=(920, 300), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("否", insert=(890, 255),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.add(dwg.rect(insert=(800, 300), size=(240, 80), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("考慮 DPDK + vhost-user", insert=(920, 330),
                     text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    dwg.add(dwg.text("或 Passt", insert=(920, 355),
                     text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Yes hardware - check IOMMU
    dwg.add(dwg.line(start=(750, 240), end=(750, 320), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("是", insert=(760, 275),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Question 3: IOMMU enabled?
    dwg.add(dwg.path(d="M 650,320 L 750,360 L 850,320 L 750,280 Z", 
                     fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    dwg.add(dwg.text("IOMMU 已啟用？", insert=(750, 325),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # IOMMU not enabled
    dwg.add(dwg.line(start=(650, 340), end=(500, 430), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("否", insert=(570, 380),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.add(dwg.rect(insert=(350, 430), size=(300, 80), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("先啟用 IOMMU 再評估", insert=(500, 475),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # IOMMU enabled - can use SR-IOV!
    dwg.add(dwg.line(start=(750, 360), end=(750, 480), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("是", insert=(760, 415),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.add(dwg.rect(insert=(600, 480), size=(300, 80), rx=6, fill=SUCCESS, stroke=BOX_STROKE, stroke_width=1.5, opacity=0.9))
    dwg.add(dwg.text("✅ 可以使用 SR-IOV", insert=(750, 525),
                     text_anchor="middle", font_size=15, font_family=FONT, fill="#ffffff", font_weight="600"))
    
    dwg.save()
    print("Generated: kubevirt-net-sriov-5.svg")

if __name__ == '__main__':
    create_diagram()
