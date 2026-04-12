#!/usr/bin/env python3
"""
Generate KubeVirt Upgrade State Diagram
Notion Clean Style 4
"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 900">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>

<rect width="1000" height="900" fill="{BG}"/>

<!-- Start -->
<circle cx="100" cy="50" r="15" fill="{TEXT_PRIMARY}"/>
<circle cx="100" cy="50" r="10" fill="{BG}"/>
<line x1="100" y1="65" x2="100" y2="120" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="160" y="95" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">系統穩定運行</text>

<!-- State 1: Stable -->
<rect x="50" y="120" width="300" height="140" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
<text x="60" y="145" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">Stable</text>
<text x="200" y="175" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Available = True</text>
<text x="200" y="205" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Progressing = False</text>
<text x="200" y="235" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Degraded = False</text>

<!-- Transition 1 -->
<line x1="350" y1="190" x2="450" y2="190" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="400" y="175" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">使用者更新</text>
<text x="400" y="190" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">KubeVirt CR spec</text>

<!-- State 2: UpgradeDetected -->
<rect x="450" y="120" width="300" height="140" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
<text x="460" y="145" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">UpgradeDetected</text>
<text x="600" y="175" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Progressing = True</text>
<text x="600" y="205" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Available = True (暫時)</text>
<text x="600" y="235" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">outdatedVirtualMachineInstanceWorkloads > 0</text>

<!-- Transition 2 -->
<line x1="600" y1="260" x2="600" y2="320" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="660" y="285" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">virt-operator 建立</text>
<text x="660" y="300" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">InstallStrategy Job</text>

<!-- State 3: InstallStrategyPhase -->
<rect x="450" y="320" width="300" height="120" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
<text x="460" y="345" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">InstallStrategyPhase</text>
<text x="600" y="375" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">InstallStrategy Job 執行中</text>
<text x="600" y="405" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">產生新版 ConfigMap</text>

<!-- Transition 3 -->
<line x1="600" y1="440" x2="600" y2="500" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="660" y="475" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">ConfigMap 就緒</text>

<!-- State 4: ComponentUpdate -->
<rect x="450" y="500" width="300" height="140" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
<text x="460" y="525" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">ComponentUpdate</text>
<text x="600" y="555" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-api 滾動更新</text>
<text x="600" y="585" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-controller 滾動更新</text>
<text x="600" y="615" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-handler 逐節點更新</text>

<!-- Transition 4 -->
<line x1="450" y1="570" x2="350" y2="570" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="400" y="555" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">元件更新完成</text>

<!-- State 5: WorkloadMigration -->
<rect x="50" y="500" width="300" height="140" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
<text x="60" y="525" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">WorkloadMigration</text>
<text x="200" y="555" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">WorkloadUpdateController 偵測過時 VMI</text>
<text x="200" y="585" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">LiveMigrate / Evict 執行中</text>
<text x="200" y="615" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">outdatedVMI 計數器遞減</text>

<!-- Transition 5 back to Stable -->
<line x1="200" y1="500" x2="200" y2="260" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="50" y="370" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">所有 VMI 已更新完成</text>
<text x="50" y="385" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">outdatedVMI = 0</text>

</svg>'''

with open('kubevirt-upgrade-3.svg', 'w') as f:
    f.write(svg)

print("Generated: kubevirt-upgrade-3.svg")
