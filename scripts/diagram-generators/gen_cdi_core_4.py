#!/usr/bin/env python3
"""Generate CDI Core Features - Clone Strategy Selection diagram"""

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

WIDTH = 1600
HEIGHT = 1200

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

def draw_diamond(cx, cy, w, h, text, fill=ACCENT_FILL, stroke=ACCENT_STROKE):
    points = [(cx, cy - h/2), (cx + w/2, cy), (cx, cy + h/2), (cx - w/2, cy)]
    d.append(draw.Lines(*[coord for p in points for coord in p], fill=fill, stroke=stroke, stroke_width=2, close=True))
    lines = text.split('\n')
    for i, line in enumerate(lines):
        d.append(draw.Text(line, 12, cx, cy + (i - len(lines)/2 + 0.5) * 16, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_PRIMARY, font_weight='500'))

def draw_arrow(x1, y1, x2, y2, label=''):
    d.append(draw.Line(x1, y1, x2, y2, stroke=ARROW, stroke_width=2, marker_end=arrow))
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        bbox_w = len(label) * 7 + 10
        d.append(draw.Rectangle(mid_x - bbox_w/2, mid_y - 10, bbox_w, 20, fill=BG, stroke='none'))
        d.append(draw.Text(label, 11, mid_x, mid_y, text_anchor='middle', dominant_baseline='middle',
                           font_family=FONT, fill=TEXT_SECONDARY, font_weight='400'))

# Title
d.append(draw.Text('CDI 克隆策略選擇流程', 18, WIDTH/2, 40, text_anchor='middle',
                   font_family=FONT, fill=TEXT_PRIMARY, font_weight='600'))

# Nodes
choose_x, choose_y = 800, 100
draw_box(choose_x - 90, choose_y, 180, 50, 'ChooseStrategy', ACCENT_FILL, ACCENT_STROKE)

source_type_x, source_type_y = 800, 200
draw_diamond(source_type_x, source_type_y, 140, 80, '來源類型?')

pvc_compute_x, pvc_compute_y = 400, 320
draw_box(pvc_compute_x - 140, pvc_compute_y, 280, 50, 'computeStrategyForSourcePVC')

snap_compute_x, snap_compute_y = 1200, 320
draw_box(snap_compute_x - 140, snap_compute_y, 280, 50, 'computeStrategyForSourceSnapshot')

global_override_x, global_override_y = 400, 440
draw_diamond(global_override_x, global_override_y, 140, 80, '全域覆寫?')

use_global_x, use_global_y = 200, 560
draw_box(use_global_x - 80, use_global_y, 160, 50, '使用全域策略')

storage_profile_x, storage_profile_y = 600, 560
draw_diamond(storage_profile_x, storage_profile_y, 180, 80, 'StorageProfile\n有指定策略?')

use_sp_x, use_sp_y = 400, 680
draw_box(use_sp_x - 80, use_sp_y, 160, 50, '使用 SP 策略')

default_snap_x, default_snap_y = 800, 680
draw_box(default_snap_x - 80, default_snap_y, 160, 50, '預設: Snapshot')

is_snapshot_x, is_snapshot_y = 600, 800
draw_diamond(is_snapshot_x, is_snapshot_y, 160, 80, '策略 = Snapshot?')

has_vsc_x, has_vsc_y = 600, 920
draw_diamond(has_vsc_x, has_vsc_y, 180, 80, '有相容的\nVolumeSnapshotClass?')

fallback_x, fallback_y = 200, 1040
draw_box(fallback_x - 100, fallback_y, 200, 50, '回退: HostAssisted')

csi_compat_x, csi_compat_y = 800, 920
draw_diamond(csi_compat_x, csi_compat_y, 160, 80, 'CSI Driver\n相容?')

vol_mode_x, vol_mode_y = 1000, 1040
draw_diamond(vol_mode_x, vol_mode_y, 160, 80, 'Volume Mode\n一致?')

use_selected_x, use_selected_y = 1200, 1040
draw_box(use_selected_x - 90, use_selected_y, 180, 50, '使用選定策略', CONTAINER_FILL, CONTAINER_STROKE)

# Arrows
draw_arrow(choose_x, choose_y + 50, source_type_x, source_type_y - 40, '')
draw_arrow(source_type_x - 70, source_type_y, pvc_compute_x, pvc_compute_y - 25, 'PVC')
draw_arrow(source_type_x + 70, source_type_y, snap_compute_x, snap_compute_y - 25, 'Snapshot')

draw_arrow(pvc_compute_x, pvc_compute_y + 50, global_override_x, global_override_y - 40, '')

draw_arrow(global_override_x - 70, global_override_y, use_global_x, use_global_y - 25, '有')
draw_arrow(global_override_x + 70, global_override_y, storage_profile_x, storage_profile_y - 40, '無')

draw_arrow(storage_profile_x - 90, storage_profile_y, use_sp_x, use_sp_y - 25, '有')
draw_arrow(storage_profile_x + 90, storage_profile_y, default_snap_x, default_snap_y - 25, '無')

draw_arrow(use_global_x, use_global_y + 50, is_snapshot_x - 80, is_snapshot_y - 40, '')
draw_arrow(use_sp_x, use_sp_y + 50, is_snapshot_x, is_snapshot_y - 40, '')
draw_arrow(default_snap_x, default_snap_y + 50, is_snapshot_x + 80, is_snapshot_y - 40, '')

draw_arrow(is_snapshot_x, is_snapshot_y + 40, has_vsc_x, has_vsc_y - 40, '是')
draw_arrow(is_snapshot_x + 80, is_snapshot_y, csi_compat_x, csi_compat_y - 40, 'CSI Clone')

draw_arrow(has_vsc_x - 90, has_vsc_y, fallback_x + 50, fallback_y - 25, '否')
draw_arrow(has_vsc_x + 90, has_vsc_y, csi_compat_x, csi_compat_y, '是')

draw_arrow(csi_compat_x - 80, csi_compat_y, fallback_x + 100, fallback_y, '否')
draw_arrow(csi_compat_x + 80, csi_compat_y, vol_mode_x, vol_mode_y - 40, '是')

draw_arrow(vol_mode_x - 80, vol_mode_y, fallback_x + 100, fallback_y + 25, '否')
draw_arrow(vol_mode_x + 80, vol_mode_y, use_selected_x, use_selected_y + 25, '是')

d.save_svg('cdi-core-4.svg')
print("Generated: cdi-core-4.svg")
