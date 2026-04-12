#!/usr/bin/env python3
"""Migration internals diagram 3: Migration Proxy data flow"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
PROXY_FILL = "#fef3c7"
PROXY_STROKE = "#f59e0b"

W, H = 900, 280

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    f'<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto"><polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/></marker></defs>',
    f'<text x="{W//2}" y="30" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">Migration Proxy Data Flow</text>',
]

def box(x, y, w, h, label, sub=None, fill=BOX_FILL, stroke=BOX_STROKE):
    r = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>']
    if sub:
        r.append(f'<text x="{x+w//2}" y="{y+h//2-7}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
        r.append(f'<text x="{x+w//2}" y="{y+h//2+9}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{sub}</text>')
    else:
        r.append(f'<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(r)

def container(x, y, w, h, label):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/><text x="{x+12}" y="{y+18}" font-family="{FONT}" font-size="11" font-weight="700" fill="{ARROW}">{label}</text>'

def arrow_h(x1, y, x2, label=""):
    line = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
    if label:
        mx = (x1+x2)//2
        lbl = f'<text x="{mx}" y="{y-7}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{label}</text>'
        return line + '\n' + lbl
    return line

# Source container
svg.append(container(30, 50, 250, 190, "Source Node"))
svg.append(box(50, 80, 130, 44, "libvirtd Source"))
svg.append(box(50, 165, 200, 44, "Source Proxy", None, PROXY_FILL, PROXY_STROKE))

# Target container
svg.append(container(620, 50, 250, 190, "Target Node"))
svg.append(box(640, 80, 130, 44, "libvirtd Target"))
svg.append(box(640, 165, 200, 44, "Target Proxy", None, PROXY_FILL, PROXY_STROKE))

# Middle TCP label
svg.append(f'<rect x="350" y="155" width="200" height="64" rx="6" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>') 
svg.append(f'<text x="450" y="182" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="600" fill="{TEXT_PRIMARY}">TCP / TLS</text>')
svg.append(f'<text x="450" y="200" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">隨機 Port</text>')

# Arrows
# libvirtd-S → Source Proxy
svg.append(f'<line x1="115" y1="124" x2="115" y2="165" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>')
svg.append(f'<text x="118" y="148" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">Unix Socket</text>')

# Source Proxy → TCP box
svg.append(arrow_h(250, 187, 350, "TCP/TLS"))

# TCP box → Target Proxy
svg.append(arrow_h(550, 187, 640, ""))

# Target Proxy → libvirtd-T
svg.append(f'<line x1="725" y1="165" x2="725" y2="124" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>')
svg.append(f'<text x="728" y="148" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">Unix Socket</text>')

svg.append('</svg>')
out = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-3.svg'
with open(out, 'w') as f:
    f.write('\n'.join(svg))
print(f"Written: {out}")
