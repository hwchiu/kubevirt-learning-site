#!/usr/bin/env python3
"""CDI DataVolume Lifecycle State Machine - Notion Clean Style"""
import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"

OUT = "docs-site/public/diagrams/containerized-data-importer"
os.makedirs(OUT, exist_ok=True)

W, H = 1400, 1000

def box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, fs=11):
    lines = text.split('\n')
    r = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
         f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n')
    lh = 16
    sy = y + (h - len(lines)*lh)/2 + lh - 2
    for i, ln in enumerate(lines):
        fw = "600" if i == 0 else "400"
        r += (f'  <text x="{x+w/2:.0f}" y="{sy+i*lh:.0f}" font-family="{FONT}" '
              f'font-size="{fs}" font-weight="{fw}" text-anchor="middle" fill="{TEXT_PRIMARY}">{ln}</text>\n')
    return r

def cont(x, y, w, h, title):
    return (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
            f'fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>\n'
            f'  <text x="{x+12}" y="{y+19}" font-family="{FONT}" font-size="11" '
            f'font-weight="700" fill="{TEXT_SECONDARY}">{title}</text>\n')

def arr(x1, y1, x2, y2, lbl="", dashed=False, color=ARROW):
    dash = ' stroke-dasharray="5,3"' if dashed else ""
    r = (f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
         f'stroke="{color}" stroke-width="1.5"{dash} marker-end="url(#arr)"/>\n')
    if lbl:
        mx, my = (x1+x2)/2, (y1+y2)/2
        lw = len(lbl)*5.8+12
        r += (f'  <rect x="{mx-lw/2:.1f}" y="{my-13:.1f}" width="{lw:.1f}" height="12" '
              f'rx="3" fill="{BG}" opacity="0.9"/>\n'
              f'  <text x="{mx:.1f}" y="{my-2:.1f}" font-family="{FONT}" font-size="9.5" '
              f'text-anchor="middle" fill="{TEXT_SECONDARY}">{lbl}</text>\n')
    return r

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Start state
svg += f'  <circle cx="700" cy="50" r="14" fill="{ARROW}"/>\n'
svg += f'  <circle cx="700" cy="50" r="8" fill="{BG}"/>\n'

# Pending
svg += box(640, 85, 120, 38, "Pending", "#fef3c7", "#fcd34d")
svg += arr(700, 64, 700, 85, "建立DV")

# PVCBound
svg += box(640, 175, 120, 38, "PVCBound", "#dbeafe", "#93c5fd")
svg += box(460, 155, 135, 38, "WaitForFirst\nConsumer", BOX_FILL, BOX_STROKE, 10)
svg += arr(700, 123, 700, 175, "PVC已綁定")
svg += arr(700, 123, 528, 155, "延遲綁定")
svg += arr(528, 193, 640, 193, "Consumer排程")

# Import path
svg += cont(80, 250, 400, 180, "Import 路徑")
svg += box(100, 280, 155, 38, "ImportScheduled", "#d1fae5", "#6ee7b7", 10)
svg += box(280, 280, 165, 38, "ImportInProgress", "#d1fae5", "#6ee7b7", 10)
svg += box(280, 355, 165, 38, "Succeeded", "#d1fae5", "#6ee7b7")
svg += arr(255, 299, 280, 299, "Worker啟動")
svg += arr(362, 318, 362, 355, "匯入完成")
svg += arr(700, 213, 178, 280, "排程匯入")

# Clone path
svg += cont(80, 460, 700, 280, "Clone 路徑")
svg += box(100, 495, 145, 38, "CloneScheduled", "#d1fae5", "#6ee7b7", 10)
svg += box(100, 555, 145, 38, "CloneInProgress", "#d1fae5", "#6ee7b7", 10)
svg += box(280, 495, 155, 38, "CSICloneInProgress", "#d1fae5", "#6ee7b7", 9)
svg += box(460, 495, 175, 38, "SnapshotForSmart\nCloneInProgress", "#d1fae5", "#6ee7b7", 9)
svg += box(460, 555, 175, 38, "CloneFromSnapshot\nSourceInProgress", "#d1fae5", "#6ee7b7", 9)
svg += box(460, 620, 175, 38, "SmartClonePVC\nInProgress", "#d1fae5", "#6ee7b7", 9)
svg += box(640, 555, 100, 38, "Succeeded", "#d1fae5", "#6ee7b7", 10)
svg += arr(245, 514, 280, 514, "CSI")
svg += arr(245, 514, 460, 514, "Snapshot")
svg += arr(172, 533, 172, 555, "Host-Assisted")
svg += arr(172, 593, 172, 620)
svg += box(100, 620, 145, 38, "Succeeded", "#d1fae5", "#6ee7b7", 10)
svg += arr(460, 514, 740, 574)
svg += arr(548, 593, 548, 620, "")
svg += arr(548, 658, 690, 574)
svg += arr(280, 514, 690, 574)
svg += arr(700, 213, 172, 495, "排程複製")

# Upload path
svg += cont(820, 250, 380, 180, "Upload 路徑")
svg += box(840, 280, 155, 38, "UploadScheduled", "#d1fae5", "#6ee7b7", 10)
svg += box(1010, 280, 155, 38, "UploadReady", "#d1fae5", "#6ee7b7")
svg += box(1010, 355, 155, 38, "Succeeded", "#d1fae5", "#6ee7b7")
svg += arr(995, 299, 1010, 299, "Server就緒")
svg += arr(1088, 318, 1088, 355, "上傳完成")
svg += arr(700, 213, 917, 280, "排程上傳")

# Other paths
svg += cont(820, 460, 380, 160, "其他路徑")
svg += box(840, 490, 155, 38, "ExpansionInProgress", BOX_FILL, BOX_STROKE, 9)
svg += box(840, 545, 155, 38, "NamespaceTransfer\nInProgress", BOX_FILL, BOX_STROKE, 9)
svg += box(1010, 510, 155, 38, "Succeeded", "#d1fae5", "#6ee7b7")
svg += arr(995, 509, 1010, 519, "完成")
svg += arr(917, 528, 917, 545)

# Paused
svg += box(820, 145, 110, 38, "Paused", "#fef3c7", "#fcd34d")
svg += arr(700, 104, 820, 163, "暫停")
svg += arr(820, 183, 700, 192, "恢復")

# Failed
svg += box(840, 780, 120, 38, "Failed", "#fee2e2", "#fca5a5")
svg += arr(362, 393, 900, 780, "匯入失敗", color="#ef4444")
svg += arr(172, 658, 900, 780, "複製失敗", color="#ef4444")
svg += arr(1088, 393, 960, 780, "上傳失敗", color="#ef4444")
svg += arr(900, 780, 700, 123, "重試", color="#ef4444")

# PendingPopulation
svg += box(460, 280, 150, 38, "PendingPopulation", BOX_FILL, BOX_STROKE, 9)
svg += arr(700, 213, 535, 280, "Populator")
svg += arr(535, 318, 690, 374)

# Title
svg += (f'  <text x="{W/2:.0f}" y="968" font-family="{FONT}" font-size="13" '
        f'font-weight="600" text-anchor="middle" fill="{TEXT_SECONDARY}">DataVolume 生命週期狀態機</text>\n')

svg += '</svg>'

out = f"{OUT}/cdi-architecture-2.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
