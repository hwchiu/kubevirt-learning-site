#!/usr/bin/env python3
"""Migration internals diagram 1: Architecture overview (Source/Target/Control Plane)"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 960, 580

def arrow_marker():
    return '''<defs>
  <marker id="arr" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{}" />
  </marker>
  <marker id="arr_dash" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{}" />
  </marker>
</defs>'''.format(ARROW, ARROW)

def box(x, y, w, h, label, sublabel=None, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>']
    if sublabel:
        lines.append(f'<text x="{x+w//2}" y="{y+h//2-8}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
        lines.append(f'<text x="{x+w//2}" y="{y+h//2+10}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{sublabel}</text>')
    else:
        lines.append(f'<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(lines)

def container(x, y, w, h, label):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>
<text x="{x+14}" y="{y+20}" font-family="{FONT}" font-size="12" font-weight="700" fill="{ARROW}">{label}</text>'''

def arrow(x1, y1, x2, y2, label="", dashed=False):
    dash = 'stroke-dasharray="6,4"' if dashed else ''
    line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" {dash} marker-end="url(#arr)"/>'
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2 - 8
        lbl = f'<text x="{mx}" y="{my}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{label}</text>'
        return line + '\n' + lbl
    return line

svg_parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    arrow_marker(),
    # Title
    f'<text x="{W//2}" y="36" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="{TEXT_PRIMARY}">KubeVirt Live Migration Architecture</text>',

    # Control Plane container (top center)
    container(330, 60, 300, 110, "Control Plane"),
    box(340, 82, 130, 40, "virt-controller", "Migration Controller"),
    box(482, 82, 130, 40, "K8s API Server", None),

    # Source Node container (left)
    container(30, 220, 270, 280, "Source Node"),
    box(50, 250, 110, 40, "virt-handler", "Source"),
    box(170, 250, 110, 40, "virt-launcher", "Source"),
    box(50, 310, 110, 40, "libvirtd", "Source"),
    box(50, 380, 230, 40, "Migration Proxy", "Unix Socket → TCP"),

    # Target Node container (right)
    container(660, 220, 270, 280, "Target Node"),
    box(670, 250, 110, 40, "virt-handler", "Target"),
    box(790, 250, 110, 40, "virt-launcher", "Target"),
    box(670, 310, 110, 40, "libvirtd", "Target"),
    box(670, 380, 230, 40, "Migration Proxy", "TCP → Unix Socket"),
]

# Control plane arrows
svg_parts.append(arrow(470, 102, 482, 102, ""))  # virt-controller → API

# Numbered flow arrows
flows = [
    # 1. virt-controller → API (建立 Target Pod)
    (f'<line x1="405" y1="122" x2="405" y2="145" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'),
    # label
    (f'<text x="415" y="138" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">1. 建立 Target Pod</text>'),

    # 2. API → Target virt-handler
    (f'<line x1="612" y1="102" x2="720" y2="240" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'),
    (f'<text x="680" y="168" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">2. 排程到 Target</text>'),

    # 3. Target virt-handler → virt-launcher
    (f'<line x1="780" y1="270" x2="790" y2="270" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'),
    (f'<text x="782" y="263" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">3. 準備 Domain</text>'),

    # 4. Target virt-launcher → API
    (f'<line x1="845" y1="250" x2="612" y2="115" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'),
    (f'<text x="760" y="188" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">4. TargetReady</text>'),

    # 5. API → Source virt-handler
    (f'<line x1="330" y1="102" x2="155" y2="240" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'),
    (f'<text x="218" y="168" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">5. 觸發遷移</text>'),

    # 6. Source virt-handler → virt-launcher
    (f'<line x1="160" y1="270" x2="170" y2="270" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'),
    (f'<text x="142" y="263" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">6. 開始遷移</text>'),
]
svg_parts.extend(flows)

# Source: virt-handler → virt-launcher (internal)
svg_parts.append(f'<line x1="160" y1="270" x2="170" y2="270" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>')
# Source: virt-launcher → libvirtd (downward)
svg_parts.append(f'<line x1="105" y1="290" x2="105" y2="310" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>')
# Target: virt-handler → virt-launcher (internal)
svg_parts.append(f'<line x1="780" y1="270" x2="790" y2="270" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>')
# Target: virt-launcher → libvirtd
svg_parts.append(f'<line x1="725" y1="290" x2="725" y2="310" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>')

# Data flow: libvirtd-S → Source Proxy → TCP → Target Proxy → libvirtd-T (dashed)
svg_parts.append(f'<line x1="105" y1="350" x2="105" y2="380" stroke="{ARROW}" stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arr)"/>')
svg_parts.append(f'<line x1="280" y1="400" x2="660" y2="400" stroke="{ARROW}" stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arr)"/>')
svg_parts.append(f'<text x="470" y="393" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">記憶體資料流 TCP/TLS</text>')
svg_parts.append(f'<line x1="725" y1="380" x2="725" y2="350" stroke="{ARROW}" stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arr)"/>')

svg_parts.append('</svg>')

out = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-1.svg'
with open(out, 'w') as f:
    f.write('\n'.join(svg_parts))
print(f"Written: {out}")
