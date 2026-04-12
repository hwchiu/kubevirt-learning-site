#!/usr/bin/env python3
"""
Generate CRD Storage Version Migration Flowchart
Notion Clean Style 4
"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
ACCENT_FILL = "#eff6ff"
ACCENT_STROKE = "#bfdbfe"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 650">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>

<rect width="1100" height="650" fill="{BG}"/>

<!-- Start -->
<rect x="50" y="30" width="180" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="140" y="55" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">舊版 CRD</text>
<text x="140" y="75" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">v1alpha3 storage</text>

<!-- Arrow to upgrade -->
<line x1="230" y1="60" x2="300" y2="60" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<rect x="300" y="30" width="150" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="375" y="65" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">升級 KubeVirt</text>

<!-- Arrow to new CRD -->
<line x1="450" y1="60" x2="520" y2="60" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<rect x="520" y="30" width="180" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="610" y="55" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">新版 CRD</text>
<text x="610" y="75" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">v1 storage</text>

<!-- Decision -->
<line x1="610" y1="90" x2="610" y2="150" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<path d="M 610 150 L 740 210 L 610 270 L 480 210 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="610" y="205" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">舊版物件是否</text>
<text x="610" y="220" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">自動遷移？</text>

<!-- Yes path: auto migration -->
<line x1="740" y1="210" x2="850" y2="210" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="770" y="200" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">是（大多數情況）</text>
<rect x="850" y="170" width="200" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="950" y="200" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">KubeVirt 自動</text>
<text x="950" y="220" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">轉換 API 版本</text>

<!-- No path: manual migration -->
<line x1="480" y1="210" x2="320" y2="210" stroke="{ARROW}" stroke-width="2"/>
<line x1="320" y1="210" x2="320" y2="340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="370" y="200" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">否（重大 schema 變更）</text>

<rect x="200" y="340" width="240" height="90" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="320" y="370" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">使用</text>
<text x="320" y="390" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">kube-storage-version-migrator</text>
<text x="320" y="410" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">手動觸發遷移</text>

<!-- Verify -->
<line x1="320" y1="430" x2="320" y2="500" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<rect x="200" y="500" width="240" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="320" y="530" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">驗證所有物件</text>
<text x="320" y="550" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">使用新版 storage</text>

</svg>'''

with open('kubevirt-upgrade-8.svg', 'w') as f:
    f.write(svg)

print("Generated: kubevirt-upgrade-8.svg")
