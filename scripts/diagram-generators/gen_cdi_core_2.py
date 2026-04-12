#!/usr/bin/env python3
"""Generate CDI Core Features - Data Source Classification diagram"""

import drawsvg as draw

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

WIDTH = 1200
HEIGHT = 800

d = draw.Drawing(WIDTH, HEIGHT, origin=(0, 0))
d.append(draw.Rectangle(0, 0, WIDTH, HEIGHT, fill=BG))

# Arrow marker
arrow = draw.Marker(-0.5, -0.5, 9, 7, scale=1, orient='auto')
arrow.append(draw.Lines(0, 0.5, 8.5, 3.5, 0, 6.5, fill=ARROW, close=True))
d.append(arrow)

def draw_box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE):
    d.append(draw.Rectangle(x, y, w, h, fill=fill, stroke=stroke, stroke_width=2, rx=8))
    lines = text.split('\n')
    for i, line in enumerate(lines):
        d.append(draw.Text(line, 14, x + w/2, y + h/2 + (i - len(lines)/2 + 0.5) * 18,
                           text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_arrow(x1, y1, x2, y2, label=''):
    d.append(draw.Line(x1, y1, x2, y2, stroke=ARROW, stroke_width=2, marker_end=arrow))
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        d.append(draw.Rectangle(mid_x - 60, mid_y - 12, 120, 24, fill=BG, stroke='none'))
        d.append(draw.Text(label, 11, mid_x, mid_y, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI 資料來源分類與處理路徑', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Container
container_x, container_y = 80, 100
container_w, container_h = 440, 450
d.append(draw.Rectangle(container_x, container_y, container_w, container_h,
                        fill='none', stroke=CONTAINER_STROKE, stroke_width=2, rx=12, stroke_dasharray='8,4'))
d.append(draw.Text('資料來源分類', 15, container_x + container_w/2, container_y + 25,
                   text_anchor='middle', font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Sources
http_x, http_y = 120, 160
s3_x, s3_y = 120, 235
gcs_x, gcs_y = 120, 310
registry_x, registry_y = 120, 385
imageio_x, imageio_y = 120, 460
vddk_x, vddk_y = 350, 460

box_w, box_h = 100, 50

draw_box(http_x, http_y, box_w, box_h, 'HTTP', ACCENT_FILL, ACCENT_STROKE)
draw_box(s3_x, s3_y, box_w, box_h, 'S3', ACCENT_FILL, ACCENT_STROKE)
draw_box(gcs_x, gcs_y, box_w, box_h, 'GCS', ACCENT_FILL, ACCENT_STROKE)
draw_box(registry_x, registry_y, box_w, box_h, 'Registry', ACCENT_FILL, ACCENT_STROKE)
draw_box(imageio_x, imageio_y, box_w, box_h, 'ImageIO', ACCENT_FILL, ACCENT_STROKE)
draw_box(vddk_x, vddk_y, box_w, box_h, 'VDDK', ACCENT_FILL, ACCENT_STROKE)

# Intermediate nodes
nbdkit_x, nbdkit_y = 620, 260
nbdkit_w, nbdkit_h = 150, 60
draw_box(nbdkit_x, nbdkit_y, nbdkit_w, nbdkit_h, 'nbdkit\nUnix Socket')

format_x, format_y = 620, 380
format_w, format_h = 150, 60
draw_box(format_x, format_y, format_w, format_h, 'FormatReaders')

# Final nodes
qemu_x, qemu_y = 880, 320
qemu_w, qemu_h = 140, 60
draw_box(qemu_x, qemu_y, qemu_w, qemu_h, 'qemu-img\nconvert')

pvc_x, pvc_y = 920, 600
pvc_w, pvc_h = 100, 60
draw_box(pvc_x, pvc_y, pvc_w, pvc_h, 'PVC', CONTAINER_FILL, CONTAINER_STROKE)

# Arrows
draw_arrow(http_x + box_w, http_y + box_h/2, nbdkit_x, nbdkit_y + nbdkit_h/2, 'nbdkit curl')
draw_arrow(vddk_x + box_w, vddk_y + box_h/2, nbdkit_x + nbdkit_w/2, nbdkit_y + nbdkit_h, 'nbdkit vddk')

draw_arrow(s3_x + box_w, s3_y + box_h/2, format_x, format_y + format_h/2 - 20, '直接串流')
draw_arrow(gcs_x + box_w, gcs_y + box_h/2, format_x, format_y + format_h/2, '直接串流')
draw_arrow(registry_x + box_w, registry_y + box_h/2, format_x, format_y + format_h/2 + 15, 'docker 拉取')
draw_arrow(imageio_x + box_w, imageio_y + box_h/2, format_x + format_w/2, format_y + format_h, 'oVirt SDK')

draw_arrow(nbdkit_x + nbdkit_w, nbdkit_y + nbdkit_h/2, qemu_x, qemu_y + qemu_h/2 - 10, '')
draw_arrow(format_x + format_w, format_y + format_h/2, qemu_x, qemu_y + qemu_h/2 + 10, '')

draw_arrow(qemu_x + qemu_w/2, qemu_y + qemu_h, pvc_x + pvc_w/2, pvc_y, '')

d.save_svg('cdi-core-2.svg')
print("Generated: cdi-core-2.svg")
