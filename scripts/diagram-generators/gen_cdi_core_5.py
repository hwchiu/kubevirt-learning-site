#!/usr/bin/env python3
"""Generate CDI Core Features - Upload Authentication Flow diagram"""

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
HEIGHT = 900

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
    d.append(draw.Rectangle(x - 70, y, 140, 50, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=2, rx=8))
    d.append(draw.Text(label, 13, x, y + 25, text_anchor='middle', dominant_baseline='middle',
                       font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))
    # Lifeline
    d.append(draw.Line(x, y + 50, x, HEIGHT - 50, stroke=BOX_STROKE, stroke_width=2, stroke_dasharray='8,4'))

def draw_message(x1, y, x2, label, is_return=False, activation=False):
    if activation:
        # Draw activation box
        d.append(draw.Rectangle(x2 - 8, y - 10, 16, 40, fill='#ffffff', stroke=ARROW, stroke_width=1.5))
    
    if is_return:
        d.append(draw.Line(x1, y, x2, y, stroke=ARROW, stroke_width=2, stroke_dasharray='6,3', marker_start=arrow_back))
    else:
        d.append(draw.Line(x1, y, x2, y, stroke=ARROW, stroke_width=2, marker_end=arrow))
    
    # Label
    mid_x = (x1 + x2) / 2
    d.append(draw.Rectangle(mid_x - 110, y - 20, 220, 18, fill=BG, stroke='none'))
    d.append(draw.Text(label, 11, mid_x, y - 10, text_anchor='middle',
                       font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI Upload 認證流程', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Actors
client_x = 150
api_x = 400
proxy_x = 700
server_x = 1000
pvc_x = 1250

actor_y = 80

draw_actor(client_x, actor_y, '使用者/virtctl')
draw_actor(api_x, actor_y, 'API Server')
draw_actor(proxy_x, actor_y, 'Upload Proxy')
draw_actor(server_x, actor_y, 'Upload Server')
draw_actor(pvc_x, actor_y, 'PVC')

# Messages
y = 180
draw_message(client_x, y, api_x, '建立 Upload Token 請求')

y += 70
d.append(draw.Rectangle(api_x - 8, y - 10, 16, 40, fill='#ffffff', stroke=ARROW, stroke_width=1.5))
d.append(draw.Text('PS256 簽發 JWT', 12, api_x + 90, y + 5,
                   font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

y += 70
draw_message(api_x, y, client_x, '回傳 Token', is_return=True)

y += 80
draw_message(client_x, y, proxy_x, 'POST /upload (Bearer Token + 資料)')

y += 70
d.append(draw.Rectangle(proxy_x - 8, y - 10, 16, 40, fill='#ffffff', stroke=ARROW, stroke_width=1.5))
d.append(draw.Text('驗證 JWT 簽名與有效期', 11, proxy_x + 120, y - 5,
                   font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

y += 70
d.append(draw.Rectangle(proxy_x - 8, y - 10, 16, 40, fill='#ffffff', stroke=ARROW, stroke_width=1.5))
d.append(draw.Text('驗證操作類型 = Upload', 11, proxy_x + 120, y + 5,
                   font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

y += 70
draw_message(proxy_x, y, server_x, 'mTLS 反向代理')

y += 70
d.append(draw.Rectangle(server_x - 8, y - 10, 16, 40, fill='#ffffff', stroke=ARROW, stroke_width=1.5))
d.append(draw.Text('格式偵測 & 處理', 11, server_x + 100, y + 5,
                   font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

y += 70
draw_message(server_x, y, pvc_x, '寫入資料')

y += 70
draw_message(server_x, y, proxy_x, '200 OK', is_return=True)

y += 70
draw_message(proxy_x, y, client_x, '200 OK', is_return=True)

d.save_svg('cdi-core-5.svg')
print("Generated: cdi-core-5.svg")
