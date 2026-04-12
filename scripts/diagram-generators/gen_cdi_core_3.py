#!/usr/bin/env python3
"""Generate CDI Core Features - nbdkit Processing Chain diagram"""

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

WIDTH = 1400
HEIGHT = 500

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
        d.append(draw.Text(line, 13, x + w/2, y + h/2 + (i - len(lines)/2 + 0.5) * 17,
                           text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_arrow(x1, y1, x2, y2):
    d.append(draw.Line(x1, y1, x2, y2, stroke=ARROW, stroke_width=2, marker_end=arrow))

# Title
d.append(draw.Text('nbdkit 處理鏈與資料轉換流程', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Container
container_x, container_y = 80, 120
container_w, container_h = 880, 280
d.append(draw.Rectangle(container_x, container_y, container_w, container_h,
                        fill='none', stroke=CONTAINER_STROKE, stroke_width=2, rx=12, stroke_dasharray='8,4'))
d.append(draw.Text('nbdkit 處理鏈', 15, container_x + container_w/2, container_y + 25,
                   text_anchor='middle', font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Nodes inside container
source_x, source_y = 120, 180
plugin_x, plugin_y = 120, 270
gzip_x, gzip_y = 300, 225
xz_x, xz_y = 450, 225
readahead_x, readahead_y = 600, 225
retry_x, retry_y = 750, 225
socket_x, socket_y = 840, 270

box_w, box_h = 120, 55

draw_box(source_x, source_y, box_w, box_h, '遠端來源\nHTTP/VDDK', ACCENT_FILL, ACCENT_STROKE)
draw_box(plugin_x, plugin_y, box_w, box_h, 'Plugin\ncurl/vddk', BOX_FILL, BOX_STROKE)
draw_box(gzip_x, gzip_y, 120, 55, 'Filter: gzip', BOX_FILL, BOX_STROKE)
draw_box(xz_x, xz_y, 120, 55, 'Filter: xz', BOX_FILL, BOX_STROKE)
draw_box(readahead_x, readahead_y, 120, 55, 'Filter:\nreadahead', BOX_FILL, BOX_STROKE)
draw_box(retry_x, retry_y, 120, 55, 'Filter: retry', BOX_FILL, BOX_STROKE)
draw_box(socket_x, socket_y, 100, 55, 'Unix\nSocket', BOX_FILL, BOX_STROKE)

# Outside container
qemu_x, qemu_y = 1050, 250
qemu_w, qemu_h = 140, 70
draw_box(qemu_x, qemu_y, qemu_w, qemu_h, 'qemu-img\nconvert\n-O raw')

pvc_x, pvc_y = 1250, 260
pvc_w, pvc_h = 100, 50
draw_box(pvc_x, pvc_y, pvc_w, pvc_h, 'PVC', CONTAINER_FILL, CONTAINER_STROKE)

# Arrows
draw_arrow(source_x + box_w/2, source_y + box_h, plugin_x + box_w/2, plugin_y)
draw_arrow(plugin_x + box_w, plugin_y + box_h/2, gzip_x, gzip_y + 27)
draw_arrow(gzip_x + 120, gzip_y + 27, xz_x, xz_y + 27)
draw_arrow(xz_x + 120, xz_y + 27, readahead_x, readahead_y + 27)
draw_arrow(readahead_x + 120, readahead_y + 27, retry_x, retry_y + 27)
draw_arrow(retry_x + 120, retry_y + 27, socket_x, socket_y + 27)
draw_arrow(socket_x + 100, socket_y + 27, qemu_x, qemu_y + 35)
draw_arrow(qemu_x + qemu_w, qemu_y + 35, pvc_x, pvc_y + 25)

d.save_svg('cdi-core-3.svg')
print("Generated: cdi-core-3.svg")
