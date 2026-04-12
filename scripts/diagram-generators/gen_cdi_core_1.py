#!/usr/bin/env python3
"""Generate CDI Core Features - Data Import State Machine diagram"""

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
HEIGHT = 700

d = draw.Drawing(WIDTH, HEIGHT, origin=(0, 0))
d.append(draw.Rectangle(0, 0, WIDTH, HEIGHT, fill=BG))

# Arrow marker
arrow = draw.Marker(-0.5, -0.5, 9, 7, scale=1, orient='auto')
arrow.append(draw.Lines(0, 0.5, 8.5, 3.5, 0, 6.5, fill=ARROW, close=True))
d.append(arrow)

def draw_box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE):
    d.append(draw.Rectangle(x, y, w, h, fill=fill, stroke=stroke, stroke_width=2, rx=8))
    d.append(draw.Text(text, 14, x + w/2, y + h/2, text_anchor='middle', dominant_baseline='middle',
                       font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_diamond(cx, cy, w, h, text, fill=ACCENT_FILL, stroke=ACCENT_STROKE):
    points = [(cx, cy - h/2), (cx + w/2, cy), (cx, cy + h/2), (cx - w/2, cy)]
    d.append(draw.Lines(*[coord for p in points for coord in p], fill=fill, stroke=stroke, stroke_width=2, close=True))
    lines = text.split('\n')
    for i, line in enumerate(lines):
        d.append(draw.Text(line, 13, cx, cy + (i - len(lines)/2 + 0.5) * 16, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_arrow(x1, y1, x2, y2, label='', curve=0):
    if curve:
        path = draw.Path(stroke=ARROW, stroke_width=2, fill='none', marker_end=arrow)
        path.M(x1, y1).Q(x1 + curve, (y1+y2)/2, x2, y2)
        d.append(path)
    else:
        d.append(draw.Line(x1, y1, x2, y2, stroke=ARROW, stroke_width=2, marker_end=arrow))
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        d.append(draw.Rectangle(mid_x - 65, mid_y - 12, 130, 24, fill=BG, stroke='none'))
        d.append(draw.Text(label, 12, mid_x, mid_y, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI 資料匯入狀態機', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Layout
info_x, info_y = 100, 120
info_w, info_h = 100, 60

decision_x, decision_y = 400, 150

scratch_x, scratch_y = 200, 280
scratch_w, scratch_h = 160, 60

transfer_dir_x, transfer_dir_y = 400, 280
transfer_dir_w, transfer_dir_h = 160, 60

transfer_file_x, transfer_file_y = 600, 280
transfer_file_w, transfer_file_h = 160, 60

convert_x, convert_y = 800, 280
convert_w, convert_h = 100, 60

transfer_scratch_x, transfer_scratch_y = 200, 400
transfer_scratch_w, transfer_scratch_h = 160, 60

resize_x, resize_y = 700, 520
resize_w, resize_h = 100, 60

complete_x, complete_y = 500, 610
complete_w, complete_h = 100, 60

# Nodes
draw_box(info_x, info_y, info_w, info_h, 'Info', ACCENT_FILL, ACCENT_STROKE)
draw_diamond(decision_x, decision_y, 140, 80, '來源類型')
draw_box(scratch_x, scratch_y, scratch_w, scratch_h, 'ValidatePreScratch')
draw_box(transfer_dir_x, transfer_dir_y, transfer_dir_w, transfer_dir_h, 'TransferDataDir')
draw_box(transfer_file_x, transfer_file_y, transfer_file_w, transfer_file_h, 'TransferDataFile')
draw_box(convert_x, convert_y, convert_w, convert_h, 'Convert')
draw_box(transfer_scratch_x, transfer_scratch_y, transfer_scratch_w, transfer_scratch_h, 'TransferScratch')
draw_box(resize_x, resize_y, resize_w, resize_h, 'Resize')
draw_box(complete_x, complete_y, complete_w, complete_h, 'Complete', CONTAINER_FILL, CONTAINER_STROKE)

# Arrows
draw_arrow(info_x + info_w, info_y + info_h/2, decision_x - 70, decision_y, '')
draw_arrow(decision_x - 40, decision_y + 40, scratch_x + scratch_w/2, scratch_y, '需要暫存空間')
draw_arrow(decision_x, decision_y + 40, transfer_dir_x + transfer_dir_w/2, transfer_dir_y, '直接寫入目錄')
draw_arrow(decision_x + 40, decision_y + 40, transfer_file_x + transfer_file_w/2, transfer_file_y, '直接寫入檔案')
draw_arrow(decision_x + 70, decision_y, convert_x, convert_y + convert_h/2, '使用 nbdkit')
draw_arrow(scratch_x + scratch_w/2, scratch_y + scratch_h, transfer_scratch_x + transfer_scratch_w/2, transfer_scratch_y, '')
draw_arrow(transfer_scratch_x + transfer_scratch_w/2, transfer_scratch_y + transfer_scratch_h, convert_x + convert_w/2, convert_y + convert_h, '')
draw_arrow(transfer_dir_x + transfer_dir_w/2, transfer_dir_y + transfer_dir_h, complete_x + complete_w/2, complete_y, '')
draw_arrow(transfer_file_x + transfer_file_w/2, transfer_file_y + transfer_file_h, resize_x, resize_y + resize_h/2, '')
draw_arrow(convert_x + convert_w/2, convert_y + convert_h, resize_x + resize_w/2, resize_y, '')
draw_arrow(resize_x + resize_w/2, resize_y + resize_h, complete_x + complete_w/2, complete_y, '')

d.save_svg('cdi-core-1.svg')
print("Generated: cdi-core-1.svg")
