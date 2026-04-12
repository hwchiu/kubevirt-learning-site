#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO reconcile flowchart"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 2400">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="2400" fill="{BG}"/>
  
  <!-- Start -->
  <ellipse cx="600" cy="50" rx="90" ry="35" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="600" y="58" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">開始 Reconcile</text>
  
  <!-- Fetch NM CR -->
  <path d="M 600 85 L 600 130" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 500 150 L 700 150 L 680 180 L 520 180 Z" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="600" y="170" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Fetch NM CR</text>
  
  <!-- Decision: exists? -->
  <path d="M 600 180 L 600 215" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 520 215 L 600 240 L 680 215 L 600 190 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="220" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">存在?</text>
  
  <!-- No -> End -->
  <path d="M 680 215 L 900 215 L 900 2340 L 690 2340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="790" y="210" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">不存在</text>
  
  <!-- Yes -> Create drainer -->
  <path d="M 600 240 L 600 280" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="480" y="280" width="240" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="600" y="310" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">建立 drain.Helper</text>
  
  <!-- Finalizer check -->
  <path d="M 600 330 L 600 380" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 500 380 L 600 420 L 700 380 L 600 340 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="387" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">Finalizer</text>
  <text x="600" y="407" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">檢查</text>
  
  <!-- No finalizer branch -->
  <path d="M 500 380 L 300 380 L 300 500" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="400" y="375" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">無 finalizer</text>
  <rect x="200" y="500" width="200" height="70" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="300" y="525" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">新增 finalizer</text>
  <text x="300" y="545" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">觸發</text>
  <text x="300" y="562" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">BeginMaintenance</text>
  
  <!-- DeletionTimestamp set branch -->
  <path d="M 700 380 L 900 380 L 900 500" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="780" y="375" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">DeletionTimestamp</text>
  <rect x="800" y="500" width="200" height="90" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="900" y="525" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">stopMaintenance</text>
  <text x="900" y="545" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">移除 finalizer</text>
  <text x="900" y="562" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">觸發</text>
  <text x="900" y="579" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">RemovedMaintenance</text>
  
  <!-- DeletionTimestamp -> End -->
  <path d="M 900 590 L 900 2340 L 690 2340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Add finalizer -> phase check -->
  <path d="M 300 570 L 300 660 L 500 660" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Phase check -->
  <path d="M 500 640 L 600 680 L 700 640 L 600 600 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="655" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">phase == &#39;&#39;</text>
  
  <!-- Yes -> Init status -->
  <path d="M 500 640 L 300 640 L 300 740" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="400" y="635" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">是</text>
  <rect x="200" y="740" width="200" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="300" y="765" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">設 Running</text>
  <text x="300" y="785" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">統計 TotalPods /</text>
  <text x="300" y="802" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">EvictionPods</text>
  
  <!-- No -> Get Node -->
  <path d="M 600 680 L 600 870" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="700" y="655" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">否</text>
  
  <!-- Init -> Get Node -->
  <path d="M 300 810 L 300 900 L 480 900" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Get Node -->
  <rect x="480" y="870" width="240" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="600" y="900" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">取得 Node</text>
  
  <!-- Node exists? -->
  <path d="M 600 920 L 600 975" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 520 975 L 600 1015 L 680 975 L 600 935 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="982" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">Node</text>
  <text x="600" y="1002" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">存在?</text>
  
  <!-- Not exists -> Failed -->
  <path d="M 680 975 L 900 975 L 900 1070" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="750" y="970" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">不存在</text>
  <rect x="800" y="1070" width="200" height="70" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="900" y="1095" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">觸發</text>
  <text x="900" y="1115" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">FailedMaintenance</text>
  <text x="900" y="1132" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">設 Failed</text>
  
  <!-- Failed -> End -->
  <path d="M 900 1140 L 900 2340 L 690 2340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Exists -> Lease check -->
  <path d="M 600 1015 L 600 1090" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="700" y="990" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">存在</text>
  
  <!-- ErrorOnLeaseCount check -->
  <path d="M 470 1090 L 600 1140 L 730 1090 L 600 1040 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="1085" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_PRIMARY}">ErrorOnLeaseCount</text>
  <text x="600" y="1105" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_PRIMARY}">&gt; 3?</text>
  <text x="600" y="1125" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_PRIMARY}"></text>
  
  <!-- Yes -> Uncordon + Failed -->
  <path d="M 730 1090 L 900 1090 L 900 1210" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="815" y="1085" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">是</text>
  <rect x="800" y="1210" width="200" height="60" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="900" y="1235" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Uncordon</text>
  <text x="900" y="1255" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">設 Failed</text>
  
  <!-- Uncordon -> End -->
  <path d="M 900 1270 L 900 2340 L 690 2340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- No -> RequestLease -->
  <path d="M 600 1140 L 600 1300" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="470" y="1125" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">否</text>
  <rect x="480" y="1300" width="240" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="600" y="1330" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">RequestLease 3600s</text>
  
  <!-- Patch label -->
  <path d="M 600 1360 L 600 1420" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="430" y="1420" width="340" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="600" y="1445" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Patch 標籤</text>
  <text x="600" y="1470" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">exclude-from-remediation=true</text>
  
  <!-- Add Taint -->
  <path d="M 600 1490 L 600 1560" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="430" y="1560" width="340" height="90" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="600" y="1590" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">新增 Taint</text>
  <text x="600" y="1615" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">medik8s.io/drain</text>
  <text x="600" y="1635" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">node.kubernetes.io/unschedulable</text>
  
  <!-- Cordon -->
  <path d="M 600 1650 L 600 1720" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="450" y="1720" width="300" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="600" y="1750" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Cordon 節點</text>
  <text x="600" y="1775" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">Unschedulable=true</text>
  
  <!-- RunNodeDrain -->
  <path d="M 600 1790 L 600 1860" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="450" y="1860" width="300" height="60" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="1895" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">drain.RunNodeDrain</text>
  
  <!-- Drain result -->
  <path d="M 600 1920 L 600 1985" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 520 1985 L 600 2025 L 680 1985 L 600 1945 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="1995" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">結果</text>
  
  <!-- Error -> Requeue -->
  <path d="M 520 1985 L 300 1985 L 300 2100" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="410" y="1980" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">error</text>
  <rect x="200" y="2100" width="200" height="50" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="300" y="2130" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Requeue 5s</text>
  
  <!-- Success -> Succeeded -->
  <path d="M 680 1985 L 900 1985 L 900 2100" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="790" y="1980" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">success</text>
  <rect x="800" y="2100" width="200" height="70" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="900" y="2125" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">設 Succeeded</text>
  <text x="900" y="2148" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">DrainProgress=100</text>
  
  <!-- Requeue -> End -->
  <path d="M 300 2150 L 300 2340 L 510 2340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Succeeded -> End -->
  <path d="M 900 2170 L 900 2340 L 690 2340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- End -->
  <ellipse cx="600" cy="2340" rx="90" ry="35" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="600" y="2348" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">結束</text>
  
</svg>'''

with open('nmo-arch-2.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-arch-2.svg")
