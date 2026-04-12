#!/usr/bin/env python3
"""Generate CDI Core Features - Checksum Validation Flow diagram"""

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
SUCCESS = "#10b981"
ERROR = "#ef4444"

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
        d.append(draw.Text(line, 14, x + w/2, y + h/2 + (i - len(lines)/2 + 0.5) * 18,
                           text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_diamond(cx, cy, w, h, text, fill=ACCENT_FILL, stroke=ACCENT_STROKE):
    points = [(cx, cy - h/2), (cx + w/2, cy), (cx, cy + h/2), (cx - w/2, cy)]
    d.append(draw.Lines(*[coord for p in points for coord in p], fill=fill, stroke=stroke, stroke_width=2, close=True))
    d.append(draw.Text(text, 13, cx, cy, text_anchor='middle', dominant_baseline='middle',
                       font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_arrow(x1, y1, x2, y2, label=''):
    d.append(draw.Line(x1, y1, x2, y2, stroke=ARROW, stroke_width=2, marker_end=arrow))
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        bbox_w = len(label) * 7 + 10
        d.append(draw.Rectangle(mid_x - bbox_w/2, mid_y - 12, bbox_w, 24, fill=BG, stroke='none'))
        d.append(draw.Text(label, 11, mid_x, mid_y, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI Checksum 驗證流程', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Nodes
stream_x, stream_y = 100, 200
stream_w, stream_h = 120, 60
draw_box(stream_x, stream_y, stream_w, stream_h, '資料串流', ACCENT_FILL, ACCENT_STROKE)

tee_x, tee_y = 320, 200
tee_w, tee_h = 140, 60
draw_box(tee_x, tee_y, tee_w, tee_h, 'io.TeeReader')

write_x, write_y = 580, 120
write_w, write_h = 120, 60
draw_box(write_x, write_y, write_w, write_h, '目標寫入')

hash_x, hash_y = 580, 280
hash_w, hash_h = 140, 60
draw_box(hash_x, hash_y, hash_w, hash_h, 'hash.Hash\n計算')

compare_x, compare_y = 850, 200
draw_diamond(compare_x, compare_y, 120, 80, '比較')

success_x, success_y = 1050, 120
success_w, success_h = 150, 60
draw_box(success_x, success_y, success_w, success_h, '驗證通過 ✓', '#d1fae5', SUCCESS)

error_x, error_y = 1050, 280
error_w, error_h = 240, 60
draw_box(error_x, error_y, error_w, error_h, 'ErrChecksumMismatch ✗', '#fee2e2', ERROR)

# Arrows
draw_arrow(stream_x + stream_w, stream_y + stream_h/2, tee_x, tee_y + tee_h/2, '')
draw_arrow(tee_x + tee_w, tee_y + 15, write_x, write_y + write_h/2, '')
draw_arrow(tee_x + tee_w, tee_y + 45, hash_x, hash_y + hash_h/2, '')
draw_arrow(hash_x + hash_w, hash_y + hash_h/2, compare_x - 60, compare_y + 20, '')
draw_arrow(compare_x + 60, compare_y - 20, success_x, success_y + success_h/2, '一致')
draw_arrow(compare_x + 60, compare_y + 20, error_x, error_y + error_h/2, '不一致')

d.save_svg('cdi-core-7.svg')
print("Generated: cdi-core-7.svg")
