#!/usr/bin/env python3
"""Block 5: bridge-masquerade.md - Phase 1 vs Phase 2 comparison (3 modes)"""
import svgwrite

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 960, 500
dwg = svgwrite.Drawing("docs-site/public/diagrams/kubevirt/kubevirt-net-bridge-5.svg",
                       size=(W, H), profile='full')
dwg.add(dwg.rect((0,0),(W,H),fill=BG))

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=8):
    dwg.add(dwg.rect((x,y),(w,h), rx=rx, ry=rx, fill=fill, stroke=stroke, stroke_width=1.5))

def label(text, x, y, size=13, weight="normal", color=TEXT_PRIMARY, anchor="middle"):
    dwg.add(dwg.text(text, insert=(x,y), text_anchor=anchor,
                     font_family=FONT, font_size=size, font_weight=weight, fill=color))

def multiline(lines, cx, cy, size=11, color=TEXT_PRIMARY, align="middle"):
    gap = size + 4
    total = len(lines) * gap
    sy = cy - total//2 + size
    for i, line in enumerate(lines):
        dwg.add(dwg.text(line, insert=(cx, sy + i*gap), text_anchor=align,
                         font_family=FONT, font_size=size, fill=color))

def arrow_down(x, y1, y2):
    dwg.add(dwg.line((x, y1), (x, y2), stroke=ARROW, stroke_width=2))
    dwg.add(dwg.polygon([(x,y2),(x-5,y2-10),(x+5,y2-10)], fill=ARROW))

def arrow_down_dashed(x, y1, y2):
    dwg.add(dwg.line((x, y1), (x, y2), stroke=TEXT_SECONDARY, stroke_width=1.5,
                     stroke_dasharray="6,4"))
    dwg.add(dwg.polygon([(x,y2),(x-5,y2-10),(x+5,y2-10)], fill=TEXT_SECONDARY))

# Title
label("Phase 1 vs Phase 2 — 三種模式對比", W//2, 36, size=18, weight="600")

col_w = 290
gap = 20
cols = [
    (40, "Bridge 模式", "#dbeafe", "#3b82f6"),
    (370, "Masquerade 模式", "#fef3c7", "#f59e0b"),
    (700, "Passt 模式（對比）", "#f0fdf4", "#86efac"),
]

for (cx, title, fill, stroke) in cols:
    # container
    box(cx, 60, col_w, 400, fill=fill, stroke=stroke, rx=10)
    label(title, cx + col_w//2, 84, size=13, weight="600")

    if title == "Bridge 模式":
        # Phase 1 box
        box(cx+15, 100, col_w-30, 140, fill="#fff", stroke="#3b82f6", rx=8)
        label("Phase 1（特權）", cx+col_w//2, 118, size=12, weight="600", color="#1d4ed8")
        p1_lines = ["1. 建立 bridge k6t-eth0", "2. 移除 eth0 的 Pod IP",
                    "3. 設定 bridge IP", "4. 設定 ARP proxy"]
        multiline(p1_lines, cx+25, 160, size=11, color=TEXT_PRIMARY, align="start")

        arrow_down(cx+col_w//2, 240, 270)

        box(cx+15, 270, col_w-30, 155, fill="#fff", stroke="#6b7280", rx=8)
        label("Phase 2（非特權）", cx+col_w//2, 288, size=12, weight="600", color=TEXT_SECONDARY)
        p2_lines = ["1. 設定 libvirt XML 使用 bridge", "2. 建立 tap 介面",
                    "3. 連接 tap 到 bridge", "4. 啟動 QEMU"]
        multiline(p2_lines, cx+25, 330, size=11, color=TEXT_PRIMARY, align="start")

    elif title == "Masquerade 模式":
        box(cx+15, 100, col_w-30, 120, fill="#fff", stroke="#f59e0b", rx=8)
        label("Phase 1（特權）", cx+col_w//2, 118, size=12, weight="600", color="#92400e")
        p1_lines = ["1. 設定 nftables MASQUERADE",
                    "2. 設定 nftables DNAT（ports）",
                    "3. 設定 IPv6 規則（如適用）"]
        multiline(p1_lines, cx+25, 155, size=11, color=TEXT_PRIMARY, align="start")

        arrow_down(cx+col_w//2, 220, 250)

        box(cx+15, 250, col_w-30, 175, fill="#fff", stroke="#6b7280", rx=8)
        label("Phase 2（非特權）", cx+col_w//2, 268, size=12, weight="600", color=TEXT_SECONDARY)
        p2_lines = ["1. 設定 libvirt XML 使用 tap",
                    "2. 建立 tap 介面",
                    "3. 啟動內建 DHCP server",
                    "4. 啟動 QEMU"]
        multiline(p2_lines, cx+25, 310, size=11, color=TEXT_PRIMARY, align="start")

    else:  # Passt
        box(cx+15, 100, col_w-30, 80, fill="#f1f5f9", stroke="#94a3b8", rx=8)
        label("Phase 1", cx+col_w//2, 123, size=12, weight="600", color=TEXT_SECONDARY)
        label("❌ 不需要（無特權操作）", cx+col_w//2, 148, size=12, color=TEXT_SECONDARY)

        arrow_down_dashed(cx+col_w//2, 180, 215)
        label("直接跳過", cx+col_w//2+30, 202, size=10, color=TEXT_SECONDARY, anchor="start")

        box(cx+15, 215, col_w-30, 190, fill="#fff", stroke="#6b7280", rx=8)
        label("Phase 2（非特權）", cx+col_w//2, 233, size=12, weight="600", color=TEXT_SECONDARY)
        p2_lines = ["1. 啟動 passt 程式（userspace）",
                    "2. 設定 libvirt XML 使用 passt",
                    "3. 啟動 QEMU"]
        multiline(p2_lines, cx+25, 270, size=11, color=TEXT_PRIMARY, align="start")

        box(cx+15, 370, col_w-30, 60, fill="#dcfce7", stroke="#22c55e", rx=8)
        label("✅ 完全無特權操作", cx+col_w//2, 403, size=12, color="#166534", weight="600")

dwg.save()
print("Saved kubevirt-net-bridge-5.svg")
