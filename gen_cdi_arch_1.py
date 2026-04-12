#!/usr/bin/env python3
"""CDI System Architecture - Notion Clean Style"""
import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"

OUT = "docs-site/public/diagrams/containerized-data-importer"
os.makedirs(OUT, exist_ok=True)

W, H = 1400, 920

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/>
    </marker>
    <marker id="arr2" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{BOX_STROKE}"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
'''

def cont(x, y, w, h, title):
    return (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
            f'fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>\n'
            f'  <text x="{x+14}" y="{y+20}" font-family="{FONT}" font-size="11" '
            f'font-weight="700" fill="{TEXT_SECONDARY}">{title}</text>\n')

def box(x, y, w, h, text, color=BOX_FILL, stroke=BOX_STROKE):
    lines = text.split('\n')
    r = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
         f'fill="{color}" stroke="{stroke}" stroke-width="1.5"/>\n')
    lh = 16
    sy = y + (h - len(lines)*lh)/2 + lh - 2
    for i, ln in enumerate(lines):
        fw = "600" if i == 0 else "400"
        r += (f'  <text x="{x+w/2:.0f}" y="{sy+i*lh:.0f}" font-family="{FONT}" '
              f'font-size="11" font-weight="{fw}" text-anchor="middle" fill="{TEXT_PRIMARY}">{ln}</text>\n')
    return r

def arrow(x1, y1, x2, y2, lbl="", color=ARROW):
    mid = "arr"
    r = (f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
         f'stroke="{color}" stroke-width="1.5" marker-end="url(#arr)"/>\n')
    if lbl:
        mx, my = (x1+x2)/2, (y1+y2)/2
        lw = len(lbl)*6+14
        r += (f'  <rect x="{mx-lw/2:.1f}" y="{my-14:.1f}" width="{lw:.1f}" height="13" '
              f'rx="3" fill="{BG}" opacity="0.9"/>\n'
              f'  <text x="{mx:.1f}" y="{my-3:.1f}" font-family="{FONT}" font-size="10" '
              f'text-anchor="middle" fill="{TEXT_SECONDARY}">{lbl}</text>\n')
    return r

def line(x1, y1, x2, y2, color=BOX_STROKE):
    return (f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="1.5" stroke-dasharray="4,3"/>\n')

# === Layout ===
# Row 1: Control Plane (left), Proxy Layer (right)
# Row 2: Data Plane - Worker Pods (left), Volume Populators (middle)
# Row 3: Kubernetes Resources (left), External Sources (right)

# Control Plane container
svg += cont(30, 40, 480, 150, "Control Plane")
svg += box(50, 70, 130, 40, "cdi-operator", "#dbeafe", "#93c5fd")
svg += box(200, 70, 130, 40, "cdi-controller", "#dbeafe", "#93c5fd")
svg += box(350, 70, 130, 40, "cdi-apiserver", "#dbeafe", "#93c5fd")

# Proxy Layer container  
svg += cont(540, 40, 220, 150, "Proxy Layer")
svg += box(590, 80, 160, 40, "cdi-uploadproxy", "#fef3c7", "#fcd34d")

# Data Plane container
svg += cont(30, 230, 480, 150, "Data Plane — Worker Pods")
svg += box(50, 265, 130, 40, "cdi-importer Pod", "#d1fae5", "#6ee7b7")
svg += box(200, 265, 130, 40, "cdi-cloner Pod", "#d1fae5", "#6ee7b7")
svg += box(350, 265, 140, 40, "cdi-uploadserver Pod", "#d1fae5", "#6ee7b7")

# Volume Populators container
svg += cont(540, 230, 220, 150, "Volume Populators")
svg += box(560, 265, 175, 35, "ovirt-populator", BOX_FILL)
svg += box(560, 310, 175, 35, "openstack-populator", BOX_FILL)

# Kubernetes Resources container
svg += cont(30, 430, 360, 160, "Kubernetes Resources")
svg += box(50, 460, 130, 40, "Kubernetes API", BOX_FILL)
svg += box(200, 460, 80, 40, "PVC", BOX_FILL)
svg += box(295, 460, 80, 40, "VolumeSnap", BOX_FILL)
svg += box(50, 515, 130, 40, "StorageClass", BOX_FILL)

# External Sources container
svg += cont(420, 430, 360, 220, "External Sources")
svg += box(440, 465, 130, 35, "HTTP / S3 / GCS", BOX_FILL)
svg += box(590, 465, 165, 35, "Container Registry", BOX_FILL)
svg += box(440, 510, 130, 35, "oVirt ImageIO", BOX_FILL)
svg += box(590, 510, 165, 35, "VMware VDDK", BOX_FILL)
svg += box(440, 555, 130, 35, "Upload Client", "#fef3c7", "#fcd34d")

# === Arrows ===
# Operator -> Controller, API, Proxy
svg += arrow(180, 90, 200, 90, "部署與管理")
svg += arrow(280, 70, 280, 60)  # shared
# Let's do simpler direct connections:
svg += arrow(115, 90, 200, 90, "管理")
svg += arrow(330, 90, 350, 90, "管理")
svg += arrow(420, 65, 590, 80, "管理")

# Controller -> worker pods
svg += arrow(200, 305, 115, 305, "建立Pod")
svg += arrow(265, 305, 265, 305)
svg += arrow(265, 265, 265, 280)
svg += arrow(265, 285, 355, 285, "建立Pod")
svg += arrow(265, 285, 175, 285, "建立Pod")
# Simpler:
svg += arrow(265, 110, 115, 265, "建立Worker")
svg += arrow(265, 110, 265, 265, "建立Worker")
svg += arrow(265, 110, 420, 265, "建立Worker")

# Controller -> K8S (monitor)
svg += arrow(210, 150, 180, 460, "監控")
# API -> K8S
svg += arrow(415, 150, 245, 460, "Webhook驗證")
# API -> Proxy (token)
svg += arrow(415, 90, 590, 90, "簽發Token")

# Workers -> PVC
svg += arrow(115, 305, 237, 460, "寫入")
svg += arrow(265, 305, 237, 460, "讀寫")
svg += arrow(420, 305, 280, 460, "寫入")
# Cloner -> Snapshot
svg += arrow(265, 305, 338, 460, "建立")
# Populators -> PVC
svg += arrow(648, 282, 237, 460, "寫入")

# Proxy -> Upload Server
svg += arrow(670, 120, 490, 285, "轉發請求")
# Client -> Proxy
svg += arrow(505, 573, 700, 130, "上傳")

# Importer --- external sources (dashed)
svg += line(115, 285, 440, 483)
svg += line(115, 285, 590, 483)
svg += line(115, 285, 440, 528)
svg += line(115, 285, 590, 528)

# Controller -> StorageClass
svg += arrow(210, 150, 115, 515, "讀取")

svg += '</svg>'

out = f"{OUT}/cdi-architecture-1.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
