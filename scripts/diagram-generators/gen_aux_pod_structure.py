#!/usr/bin/env python3
# auxiliary-binaries.md Block 1: VM Launcher Pod Structure - graph TB with subgraphs

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

OUT = "docs-site/public/diagrams/kubevirt/kubevirt-aux-launcher-pod-structure.svg"

W, H = 1200, 900
NODE_W, NODE_H = 180, 35

def arrow_marker():
    return '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
</defs>'''

def box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = label.split('\n')
    svg = f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    if len(lines) == 1:
        svg += f'<text x="{x}" y="{y+5}" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    else:
        base_y = y - (len(lines)-1)*6
        for i, line in enumerate(lines):
            svg += f'<text x="{x}" y="{base_y+i*13}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{arrow_marker()}
<rect width="{W}" height="{H}" fill="{BG}"/>

<!-- Main Pod Container -->
<rect x="50" y="80" width="1100" height="720" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="3"/>
<text x="600" y="110" font-family="{FONT}" font-size="16" font-weight="bold" fill="{TEXT_PRIMARY}" text-anchor="middle">🖥️ VM Launcher Pod</text>

<!-- Init Containers -->
<rect x="80" y="140" width="340" height="180" rx="6" fill="{BG}" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<text x="250" y="165" font-family="{FONT}" font-size="13" font-weight="bold" fill="{TEXT_SECONDARY}" text-anchor="middle">Init Containers</text>
'''

# Init container boxes
svg += box(160, 220, NODE_W, NODE_H, "container-disk-v2alpha\n(磁碟 0)") + '\n'
svg += box(340, 220, NODE_W, NODE_H, "container-disk-v2alpha\n(磁碟 1)") + '\n'

# Main Containers
svg += '''
<rect x="80" y="350" width="340" height="180" rx="6" fill="#ffffff" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>
<text x="250" y="375" font-family="-apple-system, 'Helvetica Neue', Arial, sans-serif" font-size="13" font-weight="bold" fill="#6b7280" text-anchor="middle">Main Containers</text>
'''

svg += box(160, 440, NODE_W, NODE_H, "virt-launcher\n(主容器)") + '\n'
svg += box(340, 440, NODE_W, NODE_H, "virt-launcher-monitor\n(監控程式)") + '\n'

# Sidecars
svg += '''
<rect x="460" y="140" width="660" height="390" rx="6" fill="#ffffff" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>
<text x="790" y="165" font-family="-apple-system, 'Helvetica Neue', Arial, sans-serif" font-size="13" font-weight="bold" fill="#6b7280" text-anchor="middle">Sidecar Containers</text>
'''

sidecars = [
    (580, 220, "virt-tail\n(guest-console-log)"),
    (790, 220, "network-passt-binding\n(Hook Sidecar)"),
    (1000, 220, "network-slirp-binding\n(Hook Sidecar)"),
    (580, 320, "cloudinit\n(Hook Sidecar)"),
    (790, 320, "disk-mutation\n(Hook Sidecar)"),
    (1000, 320, "smbios\n(Hook Sidecar)"),
]

for x, y, label in sidecars:
    svg += box(x, y, 170, NODE_H, label) + '\n'

# External components
svg += box(600, 600, 200, 40, "virt-handler\n(節點代理)", "#f0fdf4", "#86efac") + '\n'
svg += box(250, 720, 200, 40, "qemu-system-x86_64", "#fef9c3", "#fde047") + '\n'

# Arrows
svg += f'<line x1="600" y1="620" x2="600" y2="100" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
svg += f'<text x="620" y="360" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">建立 Pod</text>\n'

svg += f'<line x1="160" y1="460" x2="250" y2="700" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>\n'
svg += f'<text x="180" y="580" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">啟動 QEMU</text>\n'

svg += f'<line x1="160" y1="237" x2="200" y2="700" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5,5"/>\n'
svg += f'<text x="100" y="470" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">Unix Socket</text>\n'

svg += f'<line x1="580" y1="237" x2="300" y2="460" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5,5"/>\n'
svg += f'<text x="440" y="350" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">tail 串列日誌</text>\n'

svg += '</svg>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f'Written: {OUT}')
