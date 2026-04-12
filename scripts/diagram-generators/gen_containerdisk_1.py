#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt container-disk diagram - startup sequence"""

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
    dwg = svgwrite.Drawing('kubevirt-containerdisk-seq-1.svg', size=('1400px', '900px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("ContainerDisk 啟動流程", insert=(700, 40),
                     text_anchor="middle", font_size=22, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Participants
    participants = [
        ("Kubernetes API", 100),
        ("virt-controller", 300),
        ("節點", 500),
        ("init-container\n(container-disk-binary)", 700),
        ("emptyDir Volume\n(shared)", 950),
        ("virt-launcher\n(libvirt/QEMU)", 1200)
    ]
    
    y_start = 100
    for name, x in participants:
        # Box
        dwg.add(dwg.rect(insert=(x-80, y_start), size=(160, 60), rx=6, fill=ACCENT_FILL, stroke=ACCENT_STROKE, stroke_width=2))
        lines = name.split('\n')
        for i, line in enumerate(lines):
            dwg.add(dwg.text(line, insert=(x, y_start + 30 + i*15),
                           text_anchor="middle", font_size=12, font_family=FONT, fill=TEXT_PRIMARY, font_weight="500"))
        # Lifeline
        dwg.add(dwg.line(start=(x, y_start+60), end=(x, 850), stroke=BOX_STROKE, stroke_width=1.5, stroke_dasharray="4,4"))
    
    # Sequence arrows
    y = 200
    step_h = 60
    
    # 1. K8s -> virt-controller
    dwg.add(dwg.line(start=(100, y), end=(300, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("偵測到新 VMI", insert=(200, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 2. virt-controller -> Node
    dwg.add(dwg.line(start=(300, y), end=(500, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("建立 virt-launcher Pod", insert=(400, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    dwg.add(dwg.text("(含 init container)", insert=(400, y+5),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 3. Node -> init-container
    dwg.add(dwg.line(start=(500, y), end=(700, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("拉取 ContainerDisk 映像", insert=(600, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 4. init-container self (activation)
    dwg.add(dwg.rect(insert=(700-10, y-10), size=(20, 40), fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("啟動，掛載 ContainerDisk 映像", insert=(850, y+10),
                    font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 5. init-container -> emptyDir
    dwg.add(dwg.line(start=(700, y), end=(950, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("複製 /disk/disk.img", insert=(825, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    dwg.add(dwg.text("到 emptyDir 共享卷", insert=(825, y+5),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 6. init-container -> Node (return dashed)
    dwg.add(dwg.line(start=(700, y), end=(500, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)', stroke_dasharray="4,4"))
    dwg.add(dwg.text("init container 完成退出", insert=(600, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 7. Node -> virt-launcher
    dwg.add(dwg.line(start=(500, y), end=(1200, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("啟動 virt-launcher 主容器", insert=(850, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 8. virt-launcher -> emptyDir
    dwg.add(dwg.line(start=(1200, y), end=(950, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("從 emptyDir 讀取磁碟映像", insert=(1075, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 9. virt-launcher self (activation)
    dwg.add(dwg.rect(insert=(1200-10, y-10), size=(20, 50), fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("透過 libvirt 以 qcow2 overlay", insert=(1050, y+5),
                    text_anchor="end", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    dwg.add(dwg.text("方式啟動 QEMU VM", insert=(1050, y+20),
                    text_anchor="end", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h + 10
    
    # 10. virt-launcher -> K8s (return dashed)
    dwg.add(dwg.line(start=(1200, y), end=(100, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)', stroke_dasharray="4,4"))
    dwg.add(dwg.text("VMI 狀態更新為 Running", insert=(650, y-10),
                    text_anchor="middle", font_size=11, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.save()
    print("Generated: kubevirt-containerdisk-seq-1.svg")

if __name__ == '__main__':
    create_diagram()
