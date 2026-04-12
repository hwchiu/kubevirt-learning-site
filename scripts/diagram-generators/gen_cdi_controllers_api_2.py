#!/usr/bin/env python3
"""Generate CDI ObjectTransfer state diagram in Notion Clean style."""

from pathlib import Path

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ACCENT_FILL = "#eff6ff"
ACCENT_STROKE = "#bfdbfe"
SUCCESS_FILL = "#dcfce7"
SUCCESS_STROKE = "#86efac"
WARN_FILL = "#fee2e2"
WARN_STROKE = "#fca5a5"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

OUT = Path("docs-site/public/diagrams/containerized-data-importer/cdi-object-transfer-state.svg")


def box(cx: int, cy: int, w: int, h: int, title: str, subtitle: str = "", fill: str = BOX_FILL, stroke: str = BOX_STROKE) -> str:
    x = cx - w // 2
    y = cy - h // 2
    lines = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
        f'<text x="{cx}" y="{cy - (8 if subtitle else 0)}" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">{title}</text>',
    ]
    if subtitle:
        lines.append(
            f'<text x="{cx}" y="{cy + 12}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{subtitle}</text>'
        )
    return "\n".join(lines)


def arrow(x1: int, y1: int, x2: int, y2: int, label: str = "", label_x: int | None = None, label_y: int | None = None) -> str:
    out = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arrow)"/>'
    ]
    if label:
        mx = label_x if label_x is not None else (x1 + x2) // 2
        my = label_y if label_y is not None else (y1 + y2) // 2 - 8
        out.append(
            f'<text x="{mx}" y="{my}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
        )
    return "\n".join(out)


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="980" height="320" viewBox="0 0 980 320">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  <rect width="980" height="320" fill="{BG}"/>
  <text x="490" y="32" font-family="{FONT}" font-size="18" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">ObjectTransfer 狀態機</text>

  <circle cx="60" cy="160" r="10" fill="{TEXT_PRIMARY}"/>

  {box(180, 160, 130, 44, "Empty")}
  {box(350, 160, 130, 44, "Pending", "加入 Finalizer", ACCENT_FILL, ACCENT_STROKE)}
  {box(530, 160, 150, 44, "Running", "執行 Transfer Handler")}
  {box(740, 100, 150, 44, "Complete", "轉移完成", SUCCESS_FILL, SUCCESS_STROKE)}
  {box(740, 220, 150, 44, "Error", "可重試", WARN_FILL, WARN_STROKE)}

  {arrow(70, 160, 115, 160, "建立 ObjectTransfer", 95, 148)}
  {arrow(245, 160, 285, 160, "加上 finalizer", 265, 148)}
  {arrow(415, 160, 455, 160, "ReconcilePending()", 435, 148)}
  {arrow(605, 148, 665, 112, "完成", 640, 120)}
  {arrow(605, 172, 665, 208, "錯誤", 640, 206)}
  {arrow(740, 198, 740, 124, "重試", 770, 164)}
  {arrow(815, 100, 900, 100, "reconcileCleanup()", 860, 88)}

  <circle cx="930" cy="100" r="13" fill="{BG}" stroke="{TEXT_PRIMARY}" stroke-width="2.5"/>
  <circle cx="930" cy="100" r="8" fill="{TEXT_PRIMARY}"/>
</svg>
"""

OUT.write_text(svg, encoding="utf-8")
print(f"Generated: {OUT}")
