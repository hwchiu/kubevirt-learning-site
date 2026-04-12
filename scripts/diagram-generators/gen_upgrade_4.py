#!/usr/bin/env python3
"""
Generate WorkloadUpdateController Migration Sequence
Notion Clean Style 4
"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 800">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>

<rect width="1100" height="800" fill="{BG}"/>

<!-- Participants -->
<rect x="50" y="30" width="180" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="140" y="60" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">WorkloadUpdateController</text>

<rect x="280" y="30" width="150" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="355" y="60" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Kubernetes API</text>

<rect x="480" y="30" width="140" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="550" y="60" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-controller</text>

<rect x="670" y="30" width="150" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="745" y="60" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">舊版 virt-launcher</text>

<rect x="870" y="30" width="150" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="945" y="60" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">新版 virt-launcher</text>

<!-- Lifelines -->
<line x1="140" y1="80" x2="140" y2="750" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<line x1="355" y1="80" x2="355" y2="750" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<line x1="550" y1="80" x2="550" y2="750" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<line x1="745" y1="80" x2="745" y2="750" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<line x1="945" y1="80" x2="945" y2="750" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>

<!-- Message 1 -->
<line x1="140" y1="120" x2="355" y2="120" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="245" y="110" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">掃描所有 VMI</text>

<!-- Self-call -->
<rect x="140" y="150" width="20" height="40" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<line x1="140" y1="160" x2="190" y2="160" stroke="{ARROW}" stroke-width="2"/>
<line x1="190" y1="160" x2="190" y2="180" stroke="{ARROW}" stroke-width="2"/>
<line x1="190" y1="180" x2="160" y2="180" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="210" y="165" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">識別使用舊版映像的 VMI</text>

<!-- Message 2 -->
<line x1="140" y1="220" x2="355" y2="220" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="245" y="210" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">建立 VirtualMachineInstanceMigration CR</text>

<!-- Message 3 -->
<line x1="355" y1="270" x2="550" y2="270" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="450" y="260" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">通知 Migration CR 建立</text>

<!-- Message 4 -->
<line x1="550" y1="310" x2="355" y2="310" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="450" y="300" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">建立新版 virt-launcher Pod（目標節點）</text>

<!-- Message 5: activate NewVL -->
<line x1="355" y1="350" x2="945" y2="350" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>

<!-- NewVL Self-call -->
<rect x="945" y="380" width="20" height="40" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<line x1="945" y1="390" x2="995" y2="390" stroke="{ARROW}" stroke-width="2"/>
<line x1="995" y1="390" x2="995" y2="410" stroke="{ARROW}" stroke-width="2"/>
<line x1="995" y1="410" x2="965" y2="410" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="1015" y="395" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">準備接受遷移</text>

<!-- Message 6 -->
<line x1="550" y1="460" x2="745" y2="460" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="645" y="450" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">觸發 libvirt 熱遷移</text>

<!-- Message 7 -->
<line x1="745" y1="510" x2="945" y2="510" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="845" y="500" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">傳輸記憶體狀態</text>

<!-- NewVL Self-call -->
<rect x="945" y="540" width="20" height="40" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<line x1="945" y1="550" x2="995" y2="550" stroke="{ARROW}" stroke-width="2"/>
<line x1="995" y1="550" x2="995" y2="570" stroke="{ARROW}" stroke-width="2"/>
<line x1="995" y1="570" x2="965" y2="570" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="1015" y="555" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">接管 VM 執行</text>

<!-- Message 8 -->
<line x1="550" y1="620" x2="355" y2="620" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="450" y="610" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">刪除舊版 virt-launcher Pod</text>

<!-- Message 9: destroy OldVL -->
<line x1="355" y1="660" x2="745" y2="660" stroke="{ARROW}" stroke-width="2"/>
<line x1="730" y1="660" x2="745" y2="675" stroke="{ARROW}" stroke-width="2"/>
<line x1="745" y1="675" x2="760" y2="660" stroke="{ARROW}" stroke-width="2"/>

<!-- WUC Self-call -->
<rect x="140" y="690" width="20" height="40" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<line x1="140" y1="700" x2="190" y2="700" stroke="{ARROW}" stroke-width="2"/>
<line x1="190" y1="700" x2="190" y2="720" stroke="{ARROW}" stroke-width="2"/>
<line x1="190" y1="720" x2="160" y2="720" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="210" y="705" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">outdatedVMI 計數器 -1</text>

</svg>'''

with open('kubevirt-upgrade-4.svg', 'w') as f:
    f.write(svg)

print("Generated: kubevirt-upgrade-4.svg")
