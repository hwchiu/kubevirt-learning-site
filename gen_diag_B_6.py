#!/usr/bin/env python3
"""Generate cdi-upload-token-seq.svg - Upload Token generation sequence diagram"""
import os

out_path = "docs-site/public/diagrams/containerized-data-importer/cdi-upload-token-seq.svg"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1500, 660
BW, BH = 180, 55

# Participants: (line1, line2, cx)
parts = [
    ("kubectl/virtctl", "(Client)", 175),
    ("CDI API Server", "(API)", 515),
    ("CdiAPIAuthorizer", "(Auth)", 855),
    ("TokenGenerator", "(Token)", 1195),
]

LIFELINE_TOP = 100
LIFELINE_BOT = 610

# Messages: (from_idx, to_idx, style, label)
msgs = [
    (0, 1, "solid",  "POST /namespaces/{ns}/uploadtokenrequests"),
    (1, 2, "solid",  "Authorize(request) - SubjectAccessReview"),
    (2, 1, "dashed", "allowed=true"),
    (1, 3, "solid",  "Generate(Payload{Operation: Upload, Resource: PVC})"),
    (3, 1, "dashed", "JWT Token (5 分鐘有效)"),
    (1, 0, "dashed", "UploadTokenRequest{Status: Token}"),
]

MSG_Y_START = 160
MSG_Y_GAP   = 82

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
svg.append(f'  <rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append('  <defs>')
svg.append('    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
svg.append('      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>')
svg.append('    </marker>')
svg.append('  </defs>')

# Title
svg.append(f'  <text x="{W//2}" y="28" text-anchor="middle" font-size="18" font-weight="600" fill="{TEXT_PRIMARY}">Upload Token 生成流程</text>')

# Participant boxes (top)
for (l1, l2, cx) in parts:
    x = cx - BW // 2
    svg.append(f'  <rect x="{x}" y="40" width="{BW}" height="{BH}" rx="6" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>')
    svg.append(f'  <text x="{cx}" y="63" text-anchor="middle" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{l1}</text>')
    svg.append(f'  <text x="{cx}" y="82" text-anchor="middle" font-size="11" fill="{TEXT_SECONDARY}">{l2}</text>')

# Lifelines
for (_, _, cx) in parts:
    svg.append(f'  <line x1="{cx}" y1="{LIFELINE_TOP}" x2="{cx}" y2="{LIFELINE_BOT}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="5,4"/>')

# Messages
for i, (fi, ti, style, label) in enumerate(msgs):
    y = MSG_Y_START + i * MSG_Y_GAP
    fx = parts[fi][2]
    tx = parts[ti][2]

    if fx < tx:
        x1, x2 = fx + 4, tx - 9
    else:
        x1, x2 = fx - 4, tx + 9

    dash = "6,3" if style == "dashed" else "none"
    svg.append(f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.8" stroke-dasharray="{dash}" marker-end="url(#arrow)"/>')
    mid_x = (fx + tx) // 2
    svg.append(f'  <text x="{mid_x}" y="{y - 7}" text-anchor="middle" font-size="12" fill="{TEXT_SECONDARY}">{label}</text>')

# Activation boxes (thin rect on lifeline during active period)
for j, (fi, ti, _, _) in enumerate(msgs):
    for idx in [fi, ti]:
        cx = parts[idx][2]
        y_top = MSG_Y_START + j * MSG_Y_GAP - 4
        y_bot = MSG_Y_START + j * MSG_Y_GAP + 4
        svg.append(f'  <rect x="{cx-5}" y="{y_top}" width="10" height="{y_bot - y_top + 20}" rx="2" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>')

# Participant boxes (bottom echo)
for (l1, l2, cx) in parts:
    x = cx - BW // 2
    y = LIFELINE_BOT - 5
    svg.append(f'  <rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="6" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>')
    svg.append(f'  <text x="{cx}" y="{y + 22}" text-anchor="middle" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{l1}</text>')
    svg.append(f'  <text x="{cx}" y="{y + 40}" text-anchor="middle" font-size="11" fill="{TEXT_SECONDARY}">{l2}</text>')

svg.append('</svg>')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg))
print(f"Generated: {out_path}")
