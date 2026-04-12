#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt SR-IOV diagram 4 - Passt comparison"""

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
    dwg = svgwrite.Drawing('kubevirt-net-sriov-6.svg', size=('1200px', '400px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("Masquerade vs Passt 網路模式比較", insert=(600, 40),
                     text_anchor="middle", font_size=20, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Masquerade mode (left)
    masq_g = dwg.g()
    masq_g.add(dwg.rect(insert=(50, 100), size=(500, 250), rx=8, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=2))
    masq_g.add(dwg.text("Masquerade 模式（對比）", insert=(300, 135),
                       text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # VM box
    masq_g.add(dwg.rect(insert=(90, 170), size=(100, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    masq_g.add(dwg.text("VM", insert=(140, 210),
                       text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # kernel tap
    masq_g.add(dwg.rect(insert=(240, 170), size=(120, 70), rx=6, fill="#f0ad4e", stroke=BOX_STROKE, stroke_width=1.5))
    masq_g.add(dwg.text("kernel tap", insert=(300, 210),
                       text_anchor="middle", font_size=13, font_family=FONT, fill="#ffffff", font_weight="500"))
    
    # Pod network
    masq_g.add(dwg.rect(insert=(410, 170), size=(110, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    masq_g.add(dwg.text("Pod 網路", insert=(465, 210),
                       text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Arrows
    masq_g.add(dwg.line(start=(190, 205), end=(240, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    masq_g.add(dwg.text("tap", insert=(215, 195),
                       text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    
    masq_g.add(dwg.line(start=(360, 205), end=(410, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    masq_g.add(dwg.text("kernel netfilter/", insert=(385, 185),
                       text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    masq_g.add(dwg.text("nftables", insert=(385, 200),
                       text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Notes
    masq_g.add(dwg.text("✗ 需要特權操作", insert=(300, 280),
                       text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    masq_g.add(dwg.text("✗ Phase 1 nftables 設定", insert=(300, 300),
                       text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.add(masq_g)
    
    # Passt mode (right)
    passt_g = dwg.g()
    passt_g.add(dwg.rect(insert=(650, 100), size=(500, 250), rx=8, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
    passt_g.add(dwg.text("Passt 模式", insert=(900, 135),
                        text_anchor="middle", font_size=16, font_family=FONT, fill=TEXT_PRIMARY, font_weight="600"))
    
    # VM box
    passt_g.add(dwg.rect(insert=(690, 170), size=(100, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    passt_g.add(dwg.text("VM", insert=(740, 210),
                        text_anchor="middle", font_size=14, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
    
    # passt program
    passt_g.add(dwg.rect(insert=(840, 150), size=(150, 110), rx=6, fill="#5bc0de", stroke=BOX_STROKE, stroke_width=1.5))
    passt_g.add(dwg.text("passt 程式", insert=(915, 190),
                        text_anchor="middle", font_size=14, font_family=FONT, fill="#ffffff", font_weight="600"))
    passt_g.add(dwg.text("（使用者態 TCP/IP）", insert=(915, 210),
                        text_anchor="middle", font_size=11, font_family=FONT, fill="#ffffff"))
    
    # Pod network
    passt_g.add(dwg.rect(insert=(1040, 170), size=(80, 70), rx=6, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=1.5))
    passt_g.add(dwg.text("Pod", insert=(1080, 195),
                        text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    passt_g.add(dwg.text("網路", insert=(1080, 215),
                        text_anchor="middle", font_size=13, font_family=FONT, fill=TEXT_PRIMARY))
    
    # Arrows
    passt_g.add(dwg.line(start=(790, 205), end=(840, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    passt_g.add(dwg.text("socket", insert=(815, 195),
                        text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    
    passt_g.add(dwg.line(start=(990, 205), end=(1040, 205), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    passt_g.add(dwg.text("普通 socket", insert=(1015, 185),
                        text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    passt_g.add(dwg.text("syscall", insert=(1015, 200),
                        text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    
    # Notes
    passt_g.add(dwg.text("✓ 完全無特權操作", insert=(900, 280),
                        text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_SECONDARY, font_weight="600"))
    passt_g.add(dwg.text("✓ 不需要 Phase 1", insert=(900, 300),
                        text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_SECONDARY, font_weight="600"))
    passt_g.add(dwg.text("✓ 更高安全性", insert=(900, 320),
                        text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_SECONDARY, font_weight="600"))
    
    dwg.add(passt_g)
    
    dwg.save()
    print("Generated: kubevirt-net-sriov-6.svg")

if __name__ == '__main__':
    create_diagram()
