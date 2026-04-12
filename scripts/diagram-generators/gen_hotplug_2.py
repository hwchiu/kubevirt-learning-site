#!/usr/bin/env python3
"""Generate MemoryDump phase state diagram in Notion Clean style."""

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

OUT = Path("docs-site/public/diagrams/kubevirt/kubevirt-hotplug-memorydump-phase.svg")


def state(cx: int, cy: int, w: int, h: int, label: str, fill: str, stroke: str) -> str:
    x = cx - w // 2
    y = cy - h // 2
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<text x="{cx}" y="{cy+5}" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">{label}</text>'
    )


def arrow(x1: int, y1: int, x2: int, y2: int, label: str = "", lx: int | None = None, ly: int | None = None, color: str = ARROW) -> str:
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#arrow)"/>']
    if label:
        out.append(
            f'<text x="{lx if lx is not None else (x1+x2)//2}" y="{ly if ly is not None else (y1+y2)//2 - 8}" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
        )
    return "\n".join(out)


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="920" height="280" viewBox="0 0 920 280">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5,8.5 3.5,0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  <rect width="920" height="280" fill="{BG}"/>
  <text x="460" y="32" font-family="{FONT}" font-size="18" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">MemoryDump Phase 狀態轉換</text>

  <circle cx="60" cy="140" r="10" fill="{TEXT_PRIMARY}"/>

  {state(210, 140, 170, 44, "Dissociating", ACCENT_FILL, ACCENT_STROKE)}
  {state(430, 140, 170, 44, "InProgress", BOX_FILL, BOX_STROKE)}
  {state(680, 90, 170, 44, "Completed", SUCCESS_FILL, SUCCESS_STROKE)}
  {state(680, 190, 170, 44, "Failed", WARN_FILL, WARN_STROKE)}

  {arrow(70, 140, 125, 140, "virtctl memorydump get", 100, 128)}
  {arrow(295, 140, 345, 140, "PVC hot-attach 完成", 320, 128)}
  {arrow(515, 128, 595, 102, "傾印完成", 555, 104)}
  {arrow(515, 152, 595, 178, "傾印失敗", 555, 196)}
  {arrow(765, 90, 850, 90, "PVC 自動 hot-detach", 808, 78)}

  <circle cx="880" cy="90" r="13" fill="{BG}" stroke="{TEXT_PRIMARY}" stroke-width="2.5"/>
  <circle cx="880" cy="90" r="8" fill="{TEXT_PRIMARY}"/>

  <rect x="300" y="220" width="300" height="28" rx="4" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>
  <text x="450" y="238" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}" text-anchor="middle">InProgress 期間 VM 仍持續運行，MemoryDump 完成後會自動 hot-detach。</text>
</svg>
"""

OUT.write_text(svg, encoding="utf-8")
print(f"Generated: {OUT}")
