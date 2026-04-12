#!/usr/bin/env python3
# pvc-datavolume.md - Block 1: PVC Access Mode flowchart

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 820, 320

def box(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, txt, size=12, fill=TEXT_PRIMARY, bold=False, anchor="middle"):
    weight = "600" if bold else "400"
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle">{txt}</text>'

def line(x1, y1, x2, y2, color=ARROW):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arr)"/>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{ARROW}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
'''

# Root
svg += box(310, 10, 200, 36, CONTAINER_FILL, CONTAINER_STROKE)
svg += text(410, 28, "PVC Access Mode", 13, TEXT_PRIMARY, True)

# Three modes
modes = [
    (110, 100, "RWO\nReadWriteOnce", "#dbeafe", "#93c5fd"),
    (410, 100, "RWX\nReadWriteMany", "#dcfce7", "#86efac"),
    (700, 100, "ROX\nReadOnlyMany", "#fef9c3", "#fde047"),
]
for mx, my, label, cf, cs in modes:
    svg += box(mx-75, my-20, 150, 40, cf, cs)
    parts = label.split('\n')
    svg += text(mx, my-7, parts[0], 13, TEXT_PRIMARY, True)
    svg += text(mx, my+9, parts[1], 10, TEXT_SECONDARY)
    svg += line(410, 46, mx, my-20)

# Features per mode
rwo_feats = ["✅ VM 正常啟動", "❌ Live Migration 不支援", "✅ 適合大多數單節點場景"]
rwx_feats = ["✅ VM 正常啟動", "✅ Live Migration 完整支援", "⚠️ 需要 CSI 驅動支援 RWX", "💡 NFS/Ceph/Longhorn 支援"]
rox_feats = ["✅ VM 啟動（Ephemeral 模式）", "❌ 無法直接作為讀寫磁碟", "✅ 配合 Ephemeral 做 overlay"]

for feats, bx_offset in [(rwo_feats, 110), (rwx_feats, 410), (rox_feats, 700)]:
    for i, feat in enumerate(feats):
        fy = 160 + i * 30
        color = "#166534" if "✅" in feat else "#dc2626" if "❌" in feat else TEXT_SECONDARY
        svg += text(bx_offset, fy, feat, 11, color)

svg += '</svg>'
with open("docs-site/public/diagrams/kubevirt/kubevirt-storage-pvc-1.svg", "w") as f:
    f.write(svg)
print("Done")
