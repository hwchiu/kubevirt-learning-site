#!/usr/bin/env python3
"""Generate CDI Core Features - Host-Assisted Clone Flow diagram"""

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

WIDTH = 1300
HEIGHT = 950

d = draw.Drawing(WIDTH, HEIGHT, origin=(0, 0))
d.append(draw.Rectangle(0, 0, WIDTH, HEIGHT, fill=BG))

# Arrow marker
arrow = draw.Marker(-0.5, -0.5, 9, 7, scale=1, orient='auto')
arrow.append(draw.Lines(0, 0.5, 8.5, 3.5, 0, 6.5, fill=ARROW, close=True))
d.append(arrow)

# Arrow back marker
arrow_back = draw.Marker(-0.5, -0.5, 9, 7, scale=1, orient='auto')
arrow_back.append(draw.Lines(8.5, 0.5, 0, 3.5, 8.5, 6.5, fill=ARROW, close=True))
d.append(arrow_back)

def draw_actor(x, y, label):
    # Box
    lines = label.split('\n')
    height = 50 + (len(lines) - 1) * 18
    d.append(draw.Rectangle(x - 80, y, 160, height, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=2, rx=8))
    for i, line in enumerate(lines):
        d.append(draw.Text(line, 12, x, y + height/2 + (i - len(lines)/2 + 0.5) * 17,
                           text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))
    # Lifeline
    d.append(draw.Line(x, y + height, x, HEIGHT - 50, stroke=BOX_STROKE, stroke_width=2, stroke_dasharray='8,4'))
    return height

def draw_message(x1, y, x2, label, is_return=False):
    if is_return:
        d.append(draw.Line(x1, y, x2, y, stroke=ARROW, stroke_width=2, stroke_dasharray='6,3', marker_start=arrow_back))
    else:
        d.append(draw.Line(x1, y, x2, y, stroke=ARROW, stroke_width=2, marker_end=arrow))
    
    # Label
    mid_x = (x1 + x2) / 2
    bbox_w = max(len(label) * 7, 100)
    d.append(draw.Rectangle(mid_x - bbox_w/2, y - 20, bbox_w, 18, fill=BG, stroke='none'))
    d.append(draw.Text(label, 11, mid_x, y - 10, text_anchor='middle',
                       font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

def draw_activation(x, y, label):
    d.append(draw.Rectangle(x - 8, y - 10, 16, 40, fill='#ffffff', stroke=ARROW, stroke_width=1.5))
    d.append(draw.Text(label, 11, x + 100, y + 5,
                       font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI Host-Assisted 克隆流程', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Actors
src_x = 200
server_x = 650
pvc_x = 1100

actor_y = 80

h1 = draw_actor(src_x, actor_y, '來源 Pod\n(cdi-cloner)')
draw_actor(server_x, actor_y, 'Upload Server')
draw_actor(pvc_x, actor_y, '目標 PVC')

# Messages
y = actor_y + h1 + 60

draw_activation(src_x, y, '讀取來源 PVC')

y += 80
# Alt box for filesystem vs block mode
alt_y = y
alt_h = 180
d.append(draw.Rectangle(120, alt_y - 20, 450, alt_h, fill='none', stroke=CONTAINER_STROKE, stroke_width=1.5, rx=6))
d.append(draw.Text('[檔案系統模式]', 12, 150, alt_y, font_family=FONT, fill=TEXT_SECONDARY, font_weight='500'))

draw_activation(src_x, y, 'tar cv -S（稀疏感知）')

y += 70
# Else part
d.append(draw.Line(120, y, 570, y, stroke=CONTAINER_STROKE, stroke_width=1.5, stroke_dasharray='6,3'))
d.append(draw.Text('[區塊裝置模式]', 12, 150, y + 15, font_family=FONT, fill=TEXT_SECONDARY, font_weight='500'))

y += 45
draw_activation(src_x, y, '直接讀取 block device')

y += 80
draw_activation(src_x, y, 'Snappy 壓縮')

y += 70
draw_message(src_x, y, server_x, 'mTLS POST (x-cdi-content-type header)')

y += 70
draw_activation(server_x, y, 'Snappy 解壓')

y += 70
draw_activation(server_x, y, 'TAR 解包（如適用）')

y += 70
draw_message(server_x, y, pvc_x, '串流寫入')

y += 70
draw_message(server_x, y, src_x, '200 OK', is_return=True)

d.save_svg('cdi-core-6.svg')
print("Generated: cdi-core-6.svg")
