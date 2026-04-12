#!/usr/bin/env python3
"""Generate Notion Clean SVG for kubevirt hotplug diagram 1 - attach sequence"""

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
    dwg = svgwrite.Drawing('kubevirt-hotplug-1.svg', size=('1400px', '900px'))
    dwg.defs.add(dwg.marker(
        id='arrow', markerWidth=10, markerHeight=7, refX=9, refY=3.5, orient='auto',
        insert=(0, 0)
    ).add(dwg.polygon(points=[(0, 0.5), (8.5, 3.5), (0, 6.5)], fill=ARROW)))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG))
    
    # Title
    dwg.add(dwg.text("PVC Hotplug 掛載流程", insert=(700, 40),
                     text_anchor="middle", font_size=22, font_family=FONT,
                     fill=TEXT_PRIMARY, font_weight="600"))
    
    # Participants
    participants = [
        ("使用者", 100),
        ("Kubernetes\nAPI", 300),
        ("virt-controller", 500),
        ("Hotplug Pod\n(attacher)", 750),
        ("virt-handler\n(節點)", 1000),
        ("QEMU/libvirt\n(VM)", 1250)
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
    
    # 1. User -> API
    dwg.add(dwg.line(start=(100, y), end=(300, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("virtctl addvolume vm-name", insert=(200, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    dwg.add(dwg.text("--volume-name=my-pvc", insert=(200, y+5),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 2. API -> virt-controller
    dwg.add(dwg.line(start=(300, y), end=(500, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("VMI 狀態更新（新增 volume 請求）", insert=(400, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h + 20
    
    # 3. virt-controller -> API
    dwg.add(dwg.line(start=(500, y), end=(300, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("建立 Hotplug Pod", insert=(400, y-20),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    dwg.add(dwg.text("（掛載 PVC，等待 PVC 就緒）", insert=(400, y-5),
                    text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 4. API -> Hotplug Pod
    dwg.add(dwg.line(start=(300, y), end=(750, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("調度 Hotplug Pod 到 VM 所在節點", insert=(525, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h + 10
    
    # 5. Hotplug Pod self
    dwg.add(dwg.rect(insert=(750-10, y-10), size=(20, 40), fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("掛載 PVC 到 Hotplug Pod", insert=(900, y+10),
                    font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 6. Hotplug Pod -> API (return)
    dwg.add(dwg.line(start=(750, y), end=(300, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)', stroke_dasharray="4,4"))
    dwg.add(dwg.text("Hotplug Pod 變為 Ready", insert=(525, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h + 20
    
    # 7. virt-handler -> API
    dwg.add(dwg.line(start=(1000, y), end=(300, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("偵測到 Hotplug Pod 就緒", insert=(650, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 8. virt-handler -> QEMU
    dwg.add(dwg.line(start=(1000, y), end=(1250, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("透過 libvirt domain XML 更新", insert=(1125, y-20),
                    text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    dwg.add(dwg.text("執行 qemu device_add", insert=(1125, y-5),
                    text_anchor="middle", font_size=9, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h + 10
    
    # 9. QEMU self
    dwg.add(dwg.rect(insert=(1250-10, y-10), size=(20, 40), fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, stroke_width=1.5))
    dwg.add(dwg.text("SCSI 設備 attach 到 VM", insert=(1100, y+10),
                    text_anchor="end", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 10. QEMU -> virt-handler (return)
    dwg.add(dwg.line(start=(1250, y), end=(1000, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)', stroke_dasharray="4,4"))
    dwg.add(dwg.text("device_add 成功", insert=(1125, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h + 10
    
    # 11. virt-handler -> API
    dwg.add(dwg.line(start=(1000, y), end=(300, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)'))
    dwg.add(dwg.text("更新 VMI status.volumeStatus", insert=(650, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    y += step_h
    
    # 12. API -> User (return)
    dwg.add(dwg.line(start=(300, y), end=(100, y), stroke=ARROW, stroke_width=2, marker_end='url(#arrow)', stroke_dasharray="4,4"))
    dwg.add(dwg.text("VMI status 顯示磁碟 Ready", insert=(200, y-10),
                    text_anchor="middle", font_size=10, font_family=FONT, fill=TEXT_SECONDARY))
    
    dwg.save()
    print("Generated: kubevirt-hotplug-1.svg")

if __name__ == '__main__':
    create_diagram()
