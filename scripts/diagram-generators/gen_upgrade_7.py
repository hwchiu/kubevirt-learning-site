#!/usr/bin/env python3
"""
Generate EvictionStrategy Decision Flowchart
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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>

<rect width="1200" height="900" fill="{BG}"/>

<!-- Start -->
<rect x="500" y="20" width="200" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="600" y="50" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">掃描過時 VMI</text>

<!-- Decision 1: evictionStrategy -->
<line x1="600" y1="70" x2="600" y2="110" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<path d="M 600 110 L 750 170 L 600 230 L 450 170 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="600" y="175" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">VMI.spec.evictionStrategy</text>

<!-- LiveMigrate path -->
<line x1="450" y1="170" x2="300" y2="170" stroke="{ARROW}" stroke-width="2"/>
<line x1="300" y1="170" x2="300" y2="240" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="355" y="160" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">LiveMigrate</text>
<path d="M 300 240 L 400 290 L 300 340 L 200 290 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="300" y="295" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">是否可遷移？</text>

<!-- LiveMigrate - Yes -->
<line x1="200" y1="290" x2="100" y2="290" stroke="{ARROW}" stroke-width="2"/>
<line x1="100" y1="290" x2="100" y2="550" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="135" y="280" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">是</text>
<rect x="40" y="550" width="120" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="100" y="575" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">加入</text>
<text x="100" y="595" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">migratable</text>
<text x="100" y="615" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">OutdatedVMIs</text>

<!-- LiveMigrate - No -->
<line x1="400" y1="290" x2="500" y2="290" stroke="{ARROW}" stroke-width="2"/>
<line x1="500" y1="290" x2="500" y2="410" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="430" y="280" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">否</text>
<rect x="420" y="410" width="160" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="500" y="435" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">abortChangeVMIs</text>
<text x="500" y="455" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">停止進行中的遷移</text>

<!-- LiveMigrateIfPossible path -->
<line x1="600" y1="110" x2="600" y2="90" stroke="{ARROW}" stroke-width="2"/>
<line x1="600" y1="90" x2="900" y2="90" stroke="{ARROW}" stroke-width="2"/>
<line x1="900" y1="90" x2="900" y2="240" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="730" y="80" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">LiveMigrateIfPossible</text>
<path d="M 900 240 L 1000 290 L 900 340 L 800 290 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="900" y="295" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">是否可遷移？</text>

<!-- LiveMigrateIfPossible - Yes -->
<line x1="800" y1="290" x2="100" y2="290" stroke="{ARROW}" stroke-width="2"/>
<text x="430" y="280" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">是</text>

<!-- LiveMigrateIfPossible - No -->
<line x1="1000" y1="290" x2="1100" y2="290" stroke="{ARROW}" stroke-width="2"/>
<line x1="1100" y1="290" x2="1100" y2="550" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="1030" y="280" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">否</text>
<rect x="1020" y="550" width="160" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="1100" y="575" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">加入</text>
<text x="1100" y="595" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">evictOutdatedVMIs</text>

<!-- None path -->
<line x1="750" y1="170" x2="900" y2="170" stroke="{ARROW}" stroke-width="2"/>
<line x1="900" y1="170" x2="900" y2="200" stroke="{ARROW}" stroke-width="2"/>
<line x1="900" y1="200" x2="1100" y2="200" stroke="{ARROW}" stroke-width="2"/>
<line x1="1100" y1="200" x2="1100" y2="550" stroke="{ARROW}" stroke-width="2"/>
<text x="810" y="160" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">None</text>

<!-- External path -->
<line x1="600" y1="230" x2="600" y2="310" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="615" y="270" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">External</text>
<rect x="520" y="310" width="160" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="600" y="330" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">跳過</text>
<text x="600" y="350" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">由外部控制器處理</text>

<!-- Lower flow: migratableOutdatedVMIs -->
<line x1="100" y1="630" x2="100" y2="700" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<path d="M 100 700 L 200 750 L 100 800 L 0 750 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="100" y="745" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">workloadUpdateMethods</text>
<text x="100" y="760" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">包含 LiveMigrate?</text>

<!-- Yes: Create VMIM -->
<line x1="0" y1="750" x2="0" y2="750" stroke="{ARROW}" stroke-width="2"/>
<line x1="0" y1="750" x2="100" y2="850" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="30" y="790" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">是</text>
<rect x="20" y="850" width="160" height="40" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="100" y="875" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">建立 VMIM CR</text>

<!-- No: keep outdated -->
<line x1="200" y1="750" x2="300" y2="750" stroke="{ARROW}" stroke-width="2"/>
<line x1="300" y1="750" x2="300" y2="850" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="230" y="740" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">否</text>
<rect x="220" y="850" width="160" height="40" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="300" y="875" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">保留於過時狀態</text>

<!-- Lower flow: evictOutdatedVMIs -->
<line x1="1100" y1="630" x2="1100" y2="700" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<path d="M 1100 700 L 1200 750 L 1100 800 L 1000 750 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="1100" y="745" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">workloadUpdateMethods</text>
<text x="1100" y="760" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">包含 Evict?</text>

<!-- Yes: Evict -->
<line x1="1000" y1="750" x2="900" y2="750" stroke="{ARROW}" stroke-width="2"/>
<line x1="900" y1="750" x2="900" y2="850" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="930" y="740" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">是</text>
<rect x="820" y="850" width="160" height="40" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="900" y="875" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">批次驅逐</text>

<!-- No: keep outdated -->
<line x1="1100" y1="800" x2="1100" y2="850" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="1115" y="825" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">否</text>
<rect x="1020" y="850" width="160" height="40" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="1100" y="875" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">保留於過時狀態</text>

</svg>'''

with open('kubevirt-upgrade-7.svg', 'w') as f:
    f.write(svg)

print("Generated: kubevirt-upgrade-7.svg")
