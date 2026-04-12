#!/usr/bin/env python3
"""
Generate KubeVirt Upgrade Strategy Overview diagram
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
ACCENT_FILL = "#eff6ff"
ACCENT_STROKE = "#bfdbfe"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1100">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>

<rect width="900" height="1100" fill="{BG}"/>

<!-- Start Node -->
<rect x="250" y="20" width="400" height="60" rx="30" fill="#4A90D9" stroke="none"/>
<text x="450" y="45" font-family="{FONT}" font-size="14" fill="#fff" text-anchor="middle">使用者更新 KubeVirt CR</text>
<text x="450" y="65" font-family="{FONT}" font-size="14" fill="#fff" text-anchor="middle">imagePullPolicy / imageTag</text>

<!-- Arrow to Phase 1 -->
<line x1="450" y1="80" x2="450" y2="120" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>

<!-- Phase 1 Container -->
<rect x="50" y="120" width="800" height="180" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<text x="60" y="145" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">Phase 1: 準備階段</text>

<!-- Phase 1 Boxes -->
<rect x="80" y="160" width="220" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="190" y="180" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-operator 偵測 CR 變更</text>
<text x="190" y="200" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">比對 generation annotation</text>

<rect x="340" y="160" width="220" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="450" y="180" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">建立 InstallStrategy Job</text>
<text x="450" y="200" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">產生新版 ConfigMap</text>

<rect x="600" y="160" width="220" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="710" y="180" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">InstallStrategy ConfigMap</text>
<text x="710" y="200" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">寫入目標元件 manifests</text>

<!-- Phase 1 Arrows -->
<line x1="450" y1="120" x2="190" y2="160" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="300" y1="190" x2="340" y2="190" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="560" y1="190" x2="600" y2="190" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>

<!-- Phase 2 Container -->
<rect x="50" y="340" width="800" height="240" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<text x="60" y="365" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">Phase 2: 元件滾動更新</text>

<!-- virt-operator apply -->
<rect x="340" y="380" width="220" height="40" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="450" y="405" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-operator 套用新資源</text>

<!-- Phase 2 Components -->
<rect x="80" y="460" width="160" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="160" y="480" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">CRD / RBAC / Webhook</text>
<text x="160" y="500" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">直接 apply</text>

<rect x="270" y="460" width="160" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="350" y="480" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-api Deployment</text>
<text x="350" y="500" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">滾動更新</text>

<rect x="460" y="460" width="180" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="550" y="480" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-controller Deployment</text>
<text x="550" y="500" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">滾動更新</text>

<rect x="670" y="460" width="160" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="750" y="480" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-handler DaemonSet</text>
<text x="750" y="500" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">逐節點滾動更新</text>

<!-- Phase 2 Arrows -->
<line x1="710" y1="220" x2="710" y2="340" stroke="{ARROW}" stroke-width="2"/>
<line x1="710" y1="340" x2="450" y2="380" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="450" y1="420" x2="160" y2="460" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="450" y1="420" x2="350" y2="460" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="450" y1="420" x2="550" y2="460" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="450" y1="420" x2="750" y2="460" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>

<!-- Phase 3 Container -->
<rect x="50" y="620" width="800" height="380" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<text x="60" y="645" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}">Phase 3: 工作負載更新</text>

<!-- WorkloadUpdateController -->
<rect x="300" y="660" width="300" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="450" y="680" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">WorkloadUpdateController</text>
<text x="450" y="700" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">偵測過時 VMI</text>

<!-- Decision Diamond -->
<path d="M 450 750 L 550 800 L 450 850 L 350 800 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="450" y="795" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">workloadUpdateMethods</text>
<text x="450" y="810" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">設定為何？</text>

<!-- LiveMigrate Path -->
<rect x="80" y="870" width="200" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="180" y="890" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">建立 VirtualMachineInstanceMigration</text>
<text x="180" y="910" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">遷移至新版 virt-launcher</text>

<!-- Evict Path -->
<rect x="350" y="870" width="200" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="450" y="890" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">批次驅逐 VMI</text>
<text x="450" y="910" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">batchEvictionSize per batch</text>

<!-- No Action Path -->
<rect x="620" y="870" width="200" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="720" y="890" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">不自動更新</text>
<text x="720" y="910" font-family="{FONT}" font-size="12" fill="{TEXT_PRIMARY}" text-anchor="middle">手動干預</text>

<!-- Phase 3 Arrows -->
<line x1="450" y1="580" x2="450" y2="660" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="450" y1="720" x2="450" y2="750" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="350" y1="800" x2="180" y2="870" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="220" y="825" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">LiveMigrate</text>
<line x1="450" y1="850" x2="450" y2="870" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="460" y="865" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">Evict</text>
<line x1="550" y1="800" x2="720" y2="870" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="650" y="825" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">空 / 無設定</text>

<!-- Convergence to End -->
<line x1="180" y1="930" x2="450" y2="1000" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="450" y1="930" x2="450" y2="1000" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<line x1="720" y1="930" x2="450" y2="1000" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>

<!-- End Node -->
<rect x="280" y="1000" width="340" height="70" rx="35" fill="#27AE60" stroke="none"/>
<text x="450" y="1025" font-family="{FONT}" font-size="14" fill="#fff" text-anchor="middle">KubeVirt CR 狀態</text>
<text x="450" y="1045" font-family="{FONT}" font-size="14" fill="#fff" text-anchor="middle">Available=true</text>
<text x="450" y="1065" font-family="{FONT}" font-size="14" fill="#fff" text-anchor="middle">Progressing=false</text>

</svg>'''

with open('kubevirt-upgrade-1.svg', 'w') as f:
    f.write(svg)

print("Generated: kubevirt-upgrade-1.svg")
