#!/usr/bin/env python3
# overview.md - Block 8: Disk expansion sequence diagram

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 900, 380

participants = [
    ("管理員", 80),
    ("Kubernetes", 230),
    ("CSI Driver", 380),
    ("KubeVirt", 530),
    ("VM Guest", 700),
]

steps = [
    (0, 1, "修改 PVC 大小"),
    (1, 2, "請求擴展 Volume"),
    (2, 2, "擴展底層儲存"),
    (2, 1, "回報新大小"),
    (1, 3, "VMI 感知 PVC 大小變化"),
    (3, 4, "透過 virsh blockresize 通知 VM"),
    (4, 4, "Guest OS 感知磁碟新大小"),
    (0, 4, "在 VM 內執行 growpart/resize2fs"),
]

def svg_sequence(participants, steps, W, H):
    LIFELINE_Y = 70
    STEP_H = 36
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''
    # Participant boxes
    for name, x in participants:
        svg += f'<rect x="{x-50}" y="10" width="100" height="36" rx="6" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>'
        svg += f'<text x="{x}" y="28" font-family="{FONT}" font-size="11" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle" dominant-baseline="middle">{name}</text>'
        # lifeline
        svg += f'<line x1="{x}" y1="46" x2="{x}" y2="{H-20}" stroke="{BOX_STROKE}" stroke-width="1" stroke-dasharray="4 3"/>'
    
    y = LIFELINE_Y
    for src_i, dst_i, label in steps:
        sx = participants[src_i][1]
        dx = participants[dst_i][1]
        if src_i == dst_i:
            # self-arrow
            svg += f'<path d="M{sx} {y} Q{sx+40} {y} {sx+40} {y+14} Q{sx+40} {y+28} {sx} {y+28}" fill="none" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
            svg += f'<text x="{sx+46}" y="{y+14}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" dominant-baseline="middle">{label}</text>'
            y += STEP_H
        else:
            direction = 1 if dx > sx else -1
            svg += f'<line x1="{sx}" y1="{y}" x2="{dx}" y2="{y}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
            mx = (sx + dx) // 2
            svg += f'<text x="{mx}" y="{y-8}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
            y += STEP_H
    return svg + '</svg>'

svg_out = svg_sequence(participants, steps, W, H)
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-overview-8.svg", "w") as f:
    f.write(svg_out)
print("Done")
