#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO node drainage sequence"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1100">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
    <marker id="arrow-back" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto">
      <polygon points="8.5 0.5, 0 3.5, 8.5 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1400" height="1100" fill="{BG}"/>
  
  <!-- Title -->
  <text x="700" y="40" font-family="{FONT}" font-size="18" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">節點排空流程 - drain.RunNodeDrain 執行過程</text>
  
  <!-- Participants (headers) -->
  <!-- Controller -->
  <rect x="100" y="80" width="160" height="70" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="180" y="120" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Controller</text>
  
  <!-- Node -->
  <rect x="350" y="80" width="160" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="430" y="120" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Node</text>
  
  <!-- drain.RunNodeDrain -->
  <rect x="600" y="80" width="220" height="70" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="710" y="110" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">drain.</text>
  <text x="710" y="135" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">RunNodeDrain</text>
  
  <!-- Pod (Eviction API) -->
  <rect x="900" y="80" width="200" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="1000" y="110" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Pod</text>
  <text x="1000" y="135" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">(Eviction API)</text>
  
  <!-- Lifelines -->
  <line x1="180" y1="150" x2="180" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="430" y1="150" x2="430" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="710" y1="150" x2="710" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="1000" y1="150" x2="1000" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  
  <!-- Message 1: Controller -> Node (Add Taint) -->
  <path d="M 180 200 L 430 200" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="305" y="188" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">加入 Taint</text>
  <text x="305" y="205" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">(NoSchedule / NoExecute)</text>
  
  <!-- Message 2: Controller -> Node (Cordon) -->
  <path d="M 180 250 L 430 250" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="305" y="238" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">Cordon</text>
  <text x="305" y="255" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">(設 spec.unschedulable=true)</text>
  
  <!-- Message 3: Controller -> drain.RunNodeDrain -->
  <path d="M 180 300 L 710 300" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="445" y="288" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">呼叫 drain.RunNodeDrain</text>
  <text x="445" y="305" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">(drainer, nodeName)</text>
  
  <!-- Activation box for drain process -->
  <rect x="700" y="310" width="20" height="480" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1"/>
  
  <!-- Loop box: Evicting pods -->
  <rect x="650" y="350" width="450" height="390" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2" stroke-dasharray="8,4"/>
  <text x="665" y="375" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">loop</text>
  <text x="705" y="375" font-family="{FONT}" font-size="13" text-anchor="start" fill="{TEXT_SECONDARY}">對每個需驅逐的 Pod</text>
  
  <!-- Message 4: drain -> Pod (POST eviction) -->
  <path d="M 710 420 L 1000 420" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="855" y="408" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">POST</text>
  <text x="855" y="425" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">/pods/&#123;name&#125;/eviction</text>
  
  <!-- Activation box for Pod -->
  <rect x="990" y="430" width="20" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>
  
  <!-- Message 5: Pod -> drain (response) -->
  <path d="M 1000 510 L 710 510" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow-back)" stroke-dasharray="5,3"/>
  <text x="855" y="495" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{ARROW}">202 Accepted 或</text>
  <text x="855" y="511" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{ARROW}">429 Too Many Requests</text>
  <text x="855" y="527" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{ARROW}">(PDB 阻擋)</text>
  
  <!-- Message 6: drain -> drain (wait) -->
  <path d="M 710 570 L 760 570 L 760 630 L 710 630" fill="none" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="850" y="595" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">等待 Pod 消失</text>
  <text x="850" y="613" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">(最多 Timeout)</text>
  
  <!-- End loop marker -->
  <line x1="660" y1="730" x2="1090" y2="730" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  
  <!-- Message 7: drain -> Controller (return) -->
  <path d="M 710 800 L 180 800" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow-back)" stroke-dasharray="5,3"/>
  <text x="445" y="788" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{ARROW}">回傳錯誤</text>
  <text x="445" y="805" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{ARROW}">(若超時或部分失敗)</text>
  
  <!-- Activation box for Controller status update -->
  <rect x="170" y="830" width="20" height="120" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1"/>
  
  <!-- Message 8: Controller -> Controller (update status) -->
  <path d="M 180 870 L 230 870 L 230 930 L 180 930" fill="none" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="320" y="890" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">更新 NodeMaintenance</text>
  <text x="320" y="908" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">status (drainProgress,</text>
  <text x="320" y="926" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">conditions)</text>
  
  <!-- Note box -->
  <rect x="50" y="1000" width="1300" height="60" rx="6" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="700" y="1025" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">關鍵設定：Force=true (驅逐無 controller 的 Pod), DeleteEmptyDirData=true (VM emptyDir),</text>
  <text x="700" y="1048" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">IgnoreAllDaemonSets=true (跳過 virt-handler), Timeout=30s (等待所有 Pod 終止)</text>
  
</svg>'''

with open('nmo-drain-1.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-drain-1.svg")
