#!/usr/bin/env python3
"""Generate CDI Controllers API - Upload Token Generation Flow diagram"""

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
HEIGHT = 700

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
    height = 50 + max(0, (len(lines) - 1) * 18)
    d.append(draw.Rectangle(x - 90, y, 180, height, fill=BOX_FILL, stroke=BOX_STROKE, stroke_width=2, rx=8))
    for i, line in enumerate(lines):
        d.append(draw.Text(line, 13, x, y + height/2 + (i - len(lines)/2 + 0.5) * 18,
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
    bbox_w = max(len(label) * 6 + 10, 120)
    d.append(draw.Rectangle(mid_x - bbox_w/2, y - 20, bbox_w, 18, fill=BG, stroke='none'))
    d.append(draw.Text(label, 10, mid_x, y - 10, text_anchor='middle',
                       font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI Upload Token 產生流程', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Actors
client_x = 200
api_x = 500
auth_x = 850
token_x = 1200

actor_y = 100

h1 = draw_actor(client_x, actor_y, 'kubectl/virtctl')
draw_actor(api_x, actor_y, 'CDI API Server')
draw_actor(auth_x, actor_y, 'CdiAPIAuthorizer')
draw_actor(token_x, actor_y, 'TokenGenerator')

# Messages
y = actor_y + h1 + 80

draw_message(client_x, y, api_x, 'POST /namespaces/{ns}/uploadtokenrequests')

y += 80
draw_message(api_x, y, auth_x, 'Authorize(request) - SubjectAccessReview')

y += 80
draw_message(auth_x, y, api_x, 'allowed=true', is_return=True)

y += 90
draw_message(api_x, y, token_x, 'Generate(Payload{Operation: Upload, Resource: PVC})')

y += 80
draw_message(token_x, y, api_x, 'JWT Token (5 分鐘有效)', is_return=True)

y += 90
draw_message(api_x, y, client_x, 'UploadTokenRequest{Status: Token}', is_return=True)

d.save_svg('cdi-controllers-api-1.svg')
print("Generated: cdi-controllers-api-1.svg")
