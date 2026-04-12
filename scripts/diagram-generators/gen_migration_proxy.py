#!/usr/bin/env python3
# Block 3: kubevirt-migration-proxy.svg (graph LR)

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

W, H = 1400, 400

defs = f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>'''

NW, NH = 180, 52
cy = H // 2

# Source node container: x=40..560
SN_X, SN_Y, SN_W, SN_H = 40, cy-120, 560, 240
# Target node container: x=800..1360
TN_X, TN_Y, TN_W, TN_H = 800, cy-120, 560, 240

# Source: LIBVIRT_S at x=80, SP at x=320
LIBS_X = 80
SP_X = 320

# Between: SP right edge (320+200=520) to TP left edge (800)
TP_X = 840
LIBT_X = 1100

def container(x, y, w, h, label):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
<text x="{x+16}" y="{y+22}" font-family="{FONT}" font-size="13" font-weight="700" fill="{TEXT_SECONDARY}">{label}</text>'''

def box(x, y, w, h, label, sublabel=None, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>']
    if sublabel:
        lines.append(f'<text x="{x+w//2}" y="{y+h//2-7}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
        lines.append(f'<text x="{x+w//2}" y="{y+h//2+12}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{sublabel}</text>')
    else:
        lines.append(f'<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(lines)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{defs}
<rect width="{W}" height="{H}" fill="{BG}"/>

<!-- Containers -->
{container(SN_X, SN_Y, SN_W, SN_H, "Source Node")}
{container(TN_X, TN_Y, TN_W, TN_H, "Target Node")}

<!-- Source nodes -->
{box(LIBS_X, cy-NH//2, NW, NH, "libvirtd", "Source")}
{box(SP_X, cy-NH//2-5, 200, NH+10, "Source Proxy", "Unix Socket → TCP", ACCENT_FILL, ACCENT_STROKE)}

<!-- Target nodes -->
{box(TP_X, cy-NH//2-5, 200, NH+10, "Target Proxy", "TCP → Unix Socket", ACCENT_FILL, ACCENT_STROKE)}
{box(LIBT_X, cy-NH//2, NW, NH, "libvirtd", "Target")}

<!-- Arrow: LIBVIRT_S -> SP -->
<line x1="{LIBS_X+NW}" y1="{cy}" x2="{SP_X}" y2="{cy}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="{LIBS_X+NW+10}" y="{cy-10}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">Unix Socket</text>

<!-- Arrow: SP -> TP (cross container) -->
<line x1="{SP_X+200}" y1="{cy}" x2="{TP_X}" y2="{cy}" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
<text x="{(SP_X+200+TP_X)//2}" y="{cy-14}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="600" fill="{ARROW}">TCP/TLS :隨機 Port</text>

<!-- Arrow: TP -> LIBVIRT_T -->
<line x1="{TP_X+200}" y1="{cy}" x2="{LIBT_X}" y2="{cy}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="{TP_X+210}" y="{cy-10}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">Unix Socket</text>

<!-- Title -->
<text x="{W//2}" y="{H-20}" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">Migration Proxy TCP/Unix Socket 橋接架構</text>
</svg>'''

out = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-proxy.svg"
with open(out, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f"Written: {out}")
