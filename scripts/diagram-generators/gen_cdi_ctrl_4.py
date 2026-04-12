#!/usr/bin/env python3
"""CDI Upload Token sequence diagram - Notion Clean Style"""
import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG, BOX_FILL, BOX_STROKE = "#ffffff", "#f9fafb", "#e5e7eb"
CONTAINER_FILL, CONTAINER_STROKE = "#f0f4ff", "#c7d2fe"
ARROW, TEXT_PRIMARY, TEXT_SECONDARY = "#3b82f6", "#111827", "#6b7280"
RESP = "#6b7280"

OUT = "docs-site/public/diagrams/containerized-data-importer"
os.makedirs(OUT, exist_ok=True)

W, H = 1100, 560

parts = [
    ("kubectl/virtctl", "(Client)", 120),
    ("CDI API Server", "(API)", 380),
    ("CdiAPIAuthorizer", "(Auth)", 640),
    ("TokenGenerator", "(Token)", 900),
]

BW, BH = 180, 55
LIFELINE_TOP = 100
LIFELINE_BOT = 490

msgs = [
    (0, 1, False, "POST /namespaces/{ns}/uploadtokenrequests", 170),
    (1, 2, False, "Authorize(request) - SubjectAccessReview", 240),
    (2, 1, True,  "allowed=true", 310),
    (1, 3, False, "Generate(Payload{Operation:Upload, Resource:PVC})", 380),
    (3, 1, True,  "JWT Token (5 分鐘有效)", 450),
    (1, 0, True,  "UploadTokenRequest{Status: Token}", 510),
]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/>
    </marker>
    <marker id="rarr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{RESP}"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Draw participant boxes
for name, sub, cx in parts:
    x = cx - BW//2
    svg += (f'  <rect x="{x}" y="30" width="{BW}" height="{BH}" rx="8" '
            f'fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>\n'
            f'  <text x="{cx}" y="54" font-family="{FONT}" font-size="12" '
            f'font-weight="700" text-anchor="middle" fill="{TEXT_PRIMARY}">{name}</text>\n'
            f'  <text x="{cx}" y="74" font-family="{FONT}" font-size="10" '
            f'text-anchor="middle" fill="{TEXT_SECONDARY}">{sub}</text>\n')
    # Lifeline
    svg += (f'  <line x1="{cx}" y1="{LIFELINE_TOP}" x2="{cx}" y2="{LIFELINE_BOT}" '
            f'stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>\n')

# Messages
for frm, to, resp, lbl, y in msgs:
    x1 = parts[frm][2]
    x2 = parts[to][2]
    color = RESP if resp else ARROW
    marker = "rarr" if resp else "arr"
    dash = ' stroke-dasharray="6,4"' if resp else ""
    svg += (f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
            f'stroke="{color}" stroke-width="1.5"{dash} marker-end="url(#{marker})"/>\n')
    mx = (x1+x2)/2
    lw = len(lbl)*5.8+16
    svg += (f'  <rect x="{mx-lw/2:.1f}" y="{y-16:.1f}" width="{lw:.1f}" height="14" '
            f'rx="3" fill="{BG}" opacity="0.9"/>\n'
            f'  <text x="{mx:.1f}" y="{y-4:.1f}" font-family="{FONT}" font-size="10" '
            f'text-anchor="middle" fill="{color}">{lbl}</text>\n')

svg += (f'  <text x="{W/2:.0f}" y="{H-12}" font-family="{FONT}" font-size="12" '
        f'font-weight="600" text-anchor="middle" fill="{TEXT_SECONDARY}">Upload Token 產生時序圖</text>\n')

svg += '</svg>'

out = f"{OUT}/cdi-controllers-api-4.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
