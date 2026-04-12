#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt SR-IOV diagram 5 - Macvtap"""

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
    dwg = svgwrite.Drawing('kubevirt-net-sriov-7.svg', size=('800px', '500px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("Macvtap 架構（已棄用）", insert=(400, 40),
                     text_anchor="middle", font_size=20, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Physical interface
    dwg.add(dwg.rect(insert=(300, 100), size=(200, 80), rx=6, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    dwg.add(dwg.text("實體介面 eth0", insert=(400, 145),
                     text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # Arrow down left
    dwg.add(dwg.line(start=(350, 180), end=(200, 250), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("macvtap", insert=(260, 210),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Arrow down right
    dwg.add(dwg.line(start=(450, 180), end=(600, 250), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("macvtap", insert=(540, 210),
                     font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    # macvtap0 (VM 1)
    dwg.add(dwg.rect(insert=(100, 250), size=(200, 100), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("macvtap0", insert=(200, 285),
                     text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    dwg.add(dwg.text("（VM 1）", insert=(200, 310),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_SECONDARY))
    
    # macvtap1 (VM 2)
    dwg.add(dwg.rect(insert=(500, 250), size=(200, 100), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("macvtap1", insert=(600, 285),
                     text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    dwg.add(dwg.text("（VM 2）", insert=(600, 310),
                     text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Deprecation notice
    dwg.add(dwg.rect(insert=(150, 400), size=(500, 70), rx=6, fill="#fef3c7", stroke="#f59e0b", stroke_width=2))
    dwg.add(dwg.text("⚠️ Macvtap 已棄用", insert=(400, 425),
                     text_anchor="middle", font_size=14, font_family=FONT, fill="#92400e", font_weight="600"))
    dwg.add(dwg.text("請使用 SR-IOV 或 Bridge binding + Multus 替代", insert=(400, 450),
                     text_anchor="middle", font_size=12, font_family=FONT, fill="#92400e"))
    
    dwg.save()
    print("Generated: kubevirt-net-sriov-7.svg")

if __name__ == '__main__':
    create_diagram()
