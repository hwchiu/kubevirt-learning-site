#!/usr/bin/env python3
"""Generate CDI Integration - Complete Clone Strategy Decision Flow diagram"""

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
SUCCESS = "#2e7d32"
WARNING = "#f9a825"
ERROR = "#c62828"

WIDTH = 2000
HEIGHT = 2400

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
        text_color = '#fff' if fill in [SUCCESS, ERROR] else TEXT_PRIMARY
        d.append(draw.Text(line, 12, x + w/2, y + h/2 + (i - len(lines)/2 + 0.5) * 15,
                           text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=text_color, font_weight='500'))

def draw_diamond(cx, cy, w, h, text, fill=ACCENT_FILL, stroke=ACCENT_STROKE):
    points = [(cx, cy - h/2), (cx + w/2, cy), (cx, cy + h/2), (cx - w/2, cy)]
    d.append(draw.Lines(*[coord for p in points for coord in p], fill=fill, stroke=stroke, stroke_width=2, close=True))
    lines = text.split('\n')
    for i, line in enumerate(lines):
        d.append(draw.Text(line, 11, cx, cy + (i - len(lines)/2 + 0.5) * 14, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_roundbox(x, y, w, h, text, fill=ACCENT_FILL, stroke=ACCENT_STROKE):
    d.append(draw.Rectangle(x, y, w, h, fill=fill, stroke=stroke, stroke_width=2, rx=25))
    d.append(draw.Text(text, 13, x + w/2, y + h/2, text_anchor='middle', dominant_baseline='middle',
                       font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

def draw_arrow(x1, y1, x2, y2, label=''):
    d.append(draw.Line(x1, y1, x2, y2, stroke=ARROW, stroke_width=2, marker_end=arrow))
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        bbox_w = len(label) * 6 + 10
        d.append(draw.Rectangle(mid_x - bbox_w/2, mid_y - 10, bbox_w, 20, fill=BG, stroke='none'))
        d.append(draw.Text(label, 10, mid_x, mid_y, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI 克隆策略完整決策流程', 20, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Start
draw_roundbox(900, 80, 200, 50, 'ChooseStrategy')

# Check source type
draw_diamond(1000, 180, 160, 70, '來源類型?')

# Three paths
draw_box(350, 280, 200, 50, 'computeStrategyForSourcePVC')
draw_box(900, 280, 200, 50, 'computeStrategyForSourceSnapshot')
draw_box(1500, 280, 200, 50, '回傳 unsupported\ndatasource 錯誤', '#fee2e2', ERROR)

draw_arrow(1000, 130, 1000, 155, '')
draw_arrow(930, 180, 450, 280, 'PVC')
draw_arrow(1000, 215, 1000, 280, 'Snapshot')
draw_arrow(1070, 180, 1600, 280, '其他')

# PVC Path
y = 380
draw_box(300, y, 300, 60, '驗證目標 StorageClass\n確認來源 PVC 存在\n驗證容量相容')
draw_arrow(450, 330, 450, y, '')

y = 490
draw_diamond(450, y, 180, 70, '全域策略覆蓋\n存在?')
draw_arrow(450, 440, 450, y - 35, '')

y = 590
draw_box(150, y, 180, 50, '使用覆蓋策略')
draw_diamond(650, y, 180, 70, 'StorageProfile\n有 CloneStrategy?')
draw_arrow(380, 490, 150 + 90, y, '是')
draw_arrow(520, 490, 650, y - 35, '否')

y = 700
draw_box(500, y, 200, 50, '使用 StorageProfile 策略')
draw_box(900, y, 180, 50, '預設:\nCloneStrategySnapshot')
draw_arrow(710, 625, 600, y, '是')
draw_arrow(720, 590 + 35, 1000 - 90, y + 25, '否')

y = 810
draw_diamond(450, y, 140, 70, '策略是\nSnapshot?')
draw_arrow(240, 640, 240, 950, '')
draw_arrow(240, 950, 450 - 70, y + 35, '')
draw_arrow(600, 750, 600, 880, '')
draw_arrow(600, 880, 450 + 70, y + 35, '')
draw_arrow(1000, 750, 1000, 880, '')
draw_arrow(1000, 880, 450 + 70, y - 35, '')

y = 950
draw_diamond(250, y, 180, 80, '相容的\nVolumeSnapshotClass\n存在?')
draw_diamond(650, y, 140, 70, '策略是\nCSI Clone?')
draw_arrow(380, 810, 250, y - 40, '是')
draw_arrow(520, 810, 650, y - 35, '否')

y = 1080
draw_box(250, y, 240, 50, 'validateAdvancedClonePVC')
draw_box(650, y, 200, 50, '回傳 HostAssisted 策略')
draw_box(50, y, 180, 50, '降級: NoVolumeSnapshotClass\n→ HostAssisted', '#fff3e0', WARNING)
draw_arrow(340, 990, 370, y + 25, '是')
draw_arrow(160, 990, 140, y + 25, '否')
draw_arrow(720, 985, 750, y + 25, '是')
draw_arrow(650, 985, 650, y, '否')

y = 1190
draw_diamond(370, y, 140, 70, 'CSI 驅動\n相容?')
draw_arrow(370, 1130, 370, y - 35, '')

y = 1300
draw_box(50, y, 200, 50, '降級: IncompatibleProvisioners\n→ HostAssisted', '#fff3e0', WARNING)
draw_diamond(540, y, 140, 70, 'VolumeMode\n相同?')
draw_arrow(300, 1190, 150, y + 25, '否')
draw_arrow(440, 1190, 540, y - 35, '是')

y = 1410
draw_box(200, y, 220, 50, '降級: IncompatibleVolumeModes\n→ HostAssisted', '#fff3e0', WARNING)
draw_diamond(600, y, 160, 80, '需要擴展且\n允許擴展?')
draw_arrow(470, 1300, 310, y + 25, '否')
draw_arrow(540 + 70, 1335, 600, y - 40, '是')

y = 1560
draw_box(350, y, 200, 50, '降級: NoVolumeExpansion\n→ HostAssisted', '#fff3e0', WARNING)
draw_box(700, y, 200, 50, '回傳選定策略 ✓', '#d1f4dd', SUCCESS)
draw_arrow(530, 1450, 450, y + 25, '不允許')
draw_arrow(670, 1450, 800, y + 25, '允許或不需要')

# Snapshot Path
y = 380
draw_box(900, y, 300, 60, '驗證目標 StorageClass\n確認來源 Snapshot 存在')
draw_arrow(1000, 330, 1050, y, '')

y = 490
draw_diamond(1050, y, 140, 70, 'Provisioner\n匹配?')
draw_arrow(1050, 440, 1050, y - 35, '')

y = 600
draw_box(850, y, 180, 50, '降級: NoProvisionerMatch\n→ HostAssisted', '#fff3e0', WARNING)
draw_diamond(1200, y, 140, 70, '容量擴展\n可行?')
draw_arrow(980, 490, 940, y + 25, '否')
draw_arrow(1120, 490, 1200, y - 35, '是')

y = 720
draw_box(1000, y, 180, 50, '降級: NoVolumeExpansion\n→ HostAssisted', '#fff3e0', WARNING)
draw_diamond(1350, y, 140, 70, 'VolumeMode\n相同?')
draw_arrow(1130, 635, 1090, y + 25, '否')
draw_arrow(1270, 635, 1350, y - 35, '是')

y = 850
draw_box(1150, y, 220, 50, '降級: IncompatibleVolumeModes\n→ HostAssisted', '#fff3e0', WARNING)
draw_box(1450, y, 240, 50, '回傳 CloneStrategySnapshot ✓', '#d1f4dd', SUCCESS)
draw_arrow(1280, 755, 1260, y + 25, '否')
draw_arrow(1420, 755, 1570, y + 25, '是')

d.save_svg('cdi-integration-1.svg')
print("Generated: cdi-integration-1.svg")
