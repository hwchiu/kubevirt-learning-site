#!/usr/bin/env python3
"""Generate WaitForFirstConsumer resolution sequence in Notion Clean style."""

from pathlib import Path

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

OUT = Path("docs-site/public/diagrams/kubevirt/kubevirt-storage-pvc-wffc.svg")

participants = [
    ("User", "使用者", 100),
    ("CDI", "CDI 控制器", 280),
    ("VM", "VM Controller", 460),
    ("SCH", "K8s Scheduler", 640),
    ("PVC", "PVC / PV", 820),
]

msgs = [
    (0, 1, False, "建立 DataVolume (WFC StorageClass)", 130),
    (1, 4, False, "建立 PVC → WaitForFirstConsumer", 180),
    (1, 0, True, "phase = WaitForFirstConsumer", 230),
    (0, 2, False, "建立 VM 並引用該 DataVolume", 290),
    (2, 3, False, "建立 VMI Pod", 340),
    (3, 4, False, "決定節點後觸發 PVC binding", 390),
    (4, 1, True, "PVC Bound", 440),
    (1, 1, False, "啟動 Importer Pod（同節點）", 500),
    (1, 0, True, "phase = ImportInProgress → Succeeded", 560),
]

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="640" viewBox="0 0 960 640">',
    f'  <defs><marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/></marker></defs>',
    f'  <rect width="960" height="640" fill="{BG}"/>',
    f'  <text x="480" y="30" font-family="{FONT}" font-size="18" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">WaitForFirstConsumer 解決流程</text>',
]

for _, label, cx in participants:
    parts.append(
        f'  <rect x="{cx-70}" y="50" width="140" height="44" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1.5"/>'
    )
    parts.append(
        f'  <text x="{cx}" y="77" font-family="{FONT}" font-size="12" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    )
    parts.append(
        f'  <line x1="{cx}" y1="94" x2="{cx}" y2="600" stroke="{BOX_STROKE}" stroke-width="1.2" stroke-dasharray="5,4"/>'
    )

for frm, to, dashed, label, y in msgs:
    x1 = participants[frm][2]
    x2 = participants[to][2]
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    color = TEXT_SECONDARY if dashed else ARROW
    marker = "" if frm == to else ' marker-end="url(#arrow)"'
    if frm == to:
        parts.append(
            f'  <path d="M {x1} {y} h 50 v 28 h -42" fill="none" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arrow)"/>'
        )
        lx = x1 + 88
    else:
        parts.append(
            f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1.5"{dash}{marker}/>'
        )
        lx = (x1 + x2) / 2
    parts.append(
        f'  <text x="{lx}" y="{y-8}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    )

parts.append(
    f'  <rect x="60" y="600" width="840" height="24" rx="4" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>'
)
parts.append(
    f'  <text x="480" y="616" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">重點：先由 Scheduler 決定節點，再讓 PVC binding 與 Importer Pod 在同節點完成。</text>'
)
parts.append("</svg>")

OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"Generated: {OUT}")
