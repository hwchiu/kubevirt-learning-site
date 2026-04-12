#!/usr/bin/env python3
# Block 1: kubevirt-migration-architecture.svg (graph TB)

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

W, H = 1600, 1000

def box(x, y, w, h, label, sublabel=None, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>']
    if sublabel:
        cy = y + h//2 - 10
        lines.append(f'<text x="{x+w//2}" y="{cy}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
        lines.append(f'<text x="{x+w//2}" y="{cy+20}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">{sublabel}</text>')
    else:
        lines.append(f'<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(lines)

def container(x, y, w, h, label):
    return f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
<text x="{x+16}" y="{y+22}" font-family="{FONT}" font-size="13" font-weight="700" fill="{TEXT_SECONDARY}">{label}</text>'''

def arrow_line(x1, y1, x2, y2, label="", dashed=False, color=ARROW):
    dash = ' stroke-dasharray="8,4"' if dashed else ''
    mid_x = (x1+x2)//2
    mid_y = (y1+y2)//2
    lbl = f'<text x="{mid_x+6}" y="{mid_y-6}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{label}</text>' if label else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{dash} marker-end="url(#arrow)"/>\n{lbl}'

def curved_arrow(x1, y1, x2, y2, cx1, cy1, cx2, cy2, label="", dashed=False, color=ARROW):
    dash = ' stroke-dasharray="8,4"' if dashed else ''
    d = f"M {x1} {y1} C {cx1} {cy1}, {cx2} {cy2}, {x2} {y2}"
    mid_x = (x1+x2)//2
    mid_y = (y1+y2)//2
    lbl = f'<text x="{mid_x+8}" y="{mid_y}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{label}</text>' if label else ''
    return f'<path d="{d}" stroke="{color}" stroke-width="2" fill="none"{dash} marker-end="url(#arrow)"/>\n{lbl}'

# Node dimensions
NW, NH = 180, 52

# Layout
# Control Plane: top center
CP_X, CP_Y, CP_W, CP_H = 450, 30, 700, 160
VC_X, VC_Y = 500, 85
API_X, API_Y = 820, 85

# Source Node: bottom left
SN_X, SN_Y, SN_W, SN_H = 40, 240, 660, 680
SH_X, SH_Y = 100, 310
SL_X, SL_Y = 100, 460
LIBS_X, LIBS_Y = 100, 610
SP_X, SP_Y = 380, 530

# Target Node: bottom right
TN_X, TN_Y, TN_W, TN_H = 900, 240, 660, 680
TH_X, TH_Y = 960, 310
TL_X, TL_Y = 960, 460
LIBT_X, LIBT_Y = 960, 610
TP_X, TP_Y = 1180, 530

defs = f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
  <marker id="arrow-dash" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#9ca3af"/>
  </marker>
</defs>'''

def label_arrow(x1, y1, x2, y2, label, num, offset_x=8, offset_y=-8, dashed=False, color=ARROW):
    dash = ' stroke-dasharray="8,4"' if dashed else ''
    lx = (x1+x2)//2 + offset_x
    ly = (y1+y2)//2 + offset_y
    return f'''<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{dash} marker-end="url(#{'arrow-dash' if dashed else 'arrow'})"/>
<text x="{lx}" y="{ly}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY if dashed else TEXT_PRIMARY}">{"" if not num else f"{num}. "}{label}</text>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{defs}
<rect width="{W}" height="{H}" fill="{BG}"/>

<!-- Containers -->
{container(CP_X, CP_Y, CP_W, CP_H, "Control Plane")}
{container(SN_X, SN_Y, SN_W, SN_H, "Source Node")}
{container(TN_X, TN_Y, TN_W, TN_H, "Target Node")}

<!-- Control Plane nodes -->
{box(VC_X, VC_Y, NW, NH, "virt-controller", "Migration Controller")}
{box(API_X, API_Y, NW+20, NH, "Kubernetes API Server")}

<!-- Source Node nodes -->
{box(SH_X, SH_Y, NW, NH, "virt-handler", "Source")}
{box(SL_X, SL_Y, NW, NH, "virt-launcher", "Source")}
{box(LIBS_X, LIBS_Y, NW, NH, "libvirtd", "Source")}
{box(SP_X, SP_Y, 200, NH+10, "Migration Proxy", "Unix Socket → TCP", ACCENT_FILL, ACCENT_STROKE)}

<!-- Target Node nodes -->
{box(TH_X, TH_Y, NW, NH, "virt-handler", "Target")}
{box(TL_X, TL_Y, NW, NH, "virt-launcher", "Target")}
{box(LIBT_X, LIBT_Y, NW, NH, "libvirtd", "Target")}
{box(TP_X, TP_Y, 200, NH+10, "Migration Proxy", "TCP → Unix Socket", ACCENT_FILL, ACCENT_STROKE)}

<!-- Internal source arrows -->
<line x1="{SH_X+NW//2}" y1="{SH_Y+NH}" x2="{SL_X+NW//2}" y2="{SL_Y}" stroke="{BOX_STROKE}" stroke-width="1.5" marker-end="url(#arrow-dash)"/>
<line x1="{SL_X+NW//2}" y1="{SL_Y+NH}" x2="{LIBS_X+NW//2}" y2="{LIBS_Y}" stroke="{BOX_STROKE}" stroke-width="1.5" marker-end="url(#arrow-dash)"/>

<!-- Internal target arrows -->
<line x1="{TH_X+NW//2}" y1="{TH_Y+NH}" x2="{TL_X+NW//2}" y2="{TL_Y}" stroke="{BOX_STROKE}" stroke-width="1.5" marker-end="url(#arrow-dash)"/>
<line x1="{TL_X+NW//2}" y1="{TL_Y+NH}" x2="{LIBT_X+NW//2}" y2="{LIBT_Y}" stroke="{BOX_STROKE}" stroke-width="1.5" marker-end="url(#arrow-dash)"/>

<!-- 1. VC -> API -->
{label_arrow(VC_X+NW, API_Y+NH//2, API_X, API_Y+NH//2, "建立 Target Pod", "1", 0, -12)}

<!-- 2. API -> TH (curves down from control plane to target node) -->
<path d="M {API_X+NW//2} {API_Y+NH} C {API_X+NW//2} {TH_Y-60}, {TH_X+NW//2} {TH_Y-60}, {TH_X+NW//2} {TH_Y}" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
<text x="{API_X+NW//2+50}" y="{(API_Y+NH+TH_Y)//2-10}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">2. 排程到 Target Node</text>

<!-- 3. TH -> TL -> already shown as internal -->
<!-- Label the internal arrow with step 3 -->
<text x="{TH_X+NW+8}" y="{(TH_Y+TL_Y+NH)//2}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">3. 準備 Domain</text>

<!-- 4. TL -> API -->
<path d="M {TL_X} {TL_Y+NH//2} C {TL_X-80} {TL_Y+NH//2}, {API_X+NW} {API_Y+NH+60}, {API_X+NW+10} {API_Y+NH}" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
<text x="{TL_X-180}" y="{TL_Y+NH//2-10}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">4. TargetReady</text>

<!-- 5. API -> SH -->
<path d="M {API_X} {API_Y+NH//2} C {API_X-80} {API_Y+NH//2}, {SH_X+NW+80} {SH_Y-60}, {SH_X+NW} {SH_Y+NH//2}" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
<text x="{SH_X+NW+10}" y="{SH_Y-20}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">5. 觸發遷移</text>

<!-- Label internal SH->SL arrow with step 6 -->
<text x="{SH_X+NW+8}" y="{(SH_Y+SL_Y+NH)//2}" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">6. 開始遷移</text>

<!-- Dashed memory flow: LIBVIRT_S -> SP -> TP -> LIBVIRT_T -->
<line x1="{LIBS_X+NW}" y1="{LIBS_Y+NH//2}" x2="{SP_X}" y2="{SP_Y+NH//2+5}" stroke="#9ca3af" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrow-dash)"/>
<text x="{LIBS_X+NW+10}" y="{LIBS_Y+NH//2-8}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">記憶體資料流</text>

<line x1="{SP_X+200}" y1="{SP_Y+NH//2+5}" x2="{TP_X}" y2="{TP_Y+NH//2+5}" stroke="#9ca3af" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrow-dash)"/>
<text x="{SP_X+210}" y="{SP_Y+NH//2-5}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">TCP/TLS</text>

<line x1="{TP_X+200}" y1="{TP_Y+NH//2+5}" x2="{LIBT_X+NW}" y2="{LIBT_Y+NH//2}" stroke="#9ca3af" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrow-dash)"/>
<text x="{TP_X+210}" y="{TP_Y+NH//2-5}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">Unix Socket</text>

<!-- Title -->
<text x="{W//2}" y="{H-30}" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">Live Migration 完整架構</text>
</svg>'''

out = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-architecture.svg"
with open(out, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f"Written: {out}")
