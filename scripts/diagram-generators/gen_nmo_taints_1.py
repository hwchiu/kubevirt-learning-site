#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO taints and cordoning state diagram"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1600" height="900" fill="{BG}"/>
  
  <!-- Title -->
  <text x="800" y="40" font-family="{FONT}" font-size="18" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">節點維護生命週期狀態變化 - Taints、Labels 與 Unschedulable 標記</text>
  
  <!-- Initial state -->
  <circle cx="100" cy="450" r="20" fill="{TEXT_PRIMARY}"/>
  <circle cx="100" cy="450" r="12" fill="{BG}"/>
  
  <!-- Before state -->
  <rect x="250" y="300" width="350" height="300" rx="12" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="3"/>
  <text x="425" y="340" font-family="{FONT}" font-size="20" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">正常狀態 (Before)</text>
  
  <!-- Before content box -->
  <rect x="280" y="370" width="290" height="200" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="295" y="395" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Taints: []</text>
  <text x="295" y="430" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Unschedulable:</text>
  <text x="455" y="430" font-family="{FONT}" font-size="14" text-anchor="start" fill="#10b981">false</text>
  <text x="295" y="465" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Labels:</text>
  <text x="295" y="490" font-family="{FONT}" font-size="13" text-anchor="start" fill="{TEXT_SECONDARY}">(無 medik8s 標記)</text>
  
  <!-- During state -->
  <rect x="750" y="250" width="400" height="400" rx="12" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="3"/>
  <text x="950" y="290" font-family="{FONT}" font-size="20" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">維護中 (During)</text>
  
  <!-- During content box -->
  <rect x="780" y="320" width="340" height="300" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="795" y="345" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Taints:</text>
  <text x="815" y="370" font-family="{FONT}" font-size="12" text-anchor="start" fill="{TEXT_SECONDARY}">- node.kubernetes.io/</text>
  <text x="835" y="388" font-family="{FONT}" font-size="12" text-anchor="start" fill="{TEXT_SECONDARY}">unschedulable:NoSchedule</text>
  <text x="815" y="410" font-family="{FONT}" font-size="12" text-anchor="start" fill="{TEXT_SECONDARY}">- medik8s.io/drain:</text>
  <text x="835" y="428" font-family="{FONT}" font-size="12" text-anchor="start" fill="{TEXT_SECONDARY}">NoSchedule</text>
  
  <text x="795" y="465" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Unschedulable:</text>
  <text x="975" y="465" font-family="{FONT}" font-size="14" text-anchor="start" fill="#dc2626">true</text>
  
  <text x="795" y="500" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Labels:</text>
  <text x="815" y="525" font-family="{FONT}" font-size="12" text-anchor="start" fill="{TEXT_SECONDARY}">medik8s.io/exclude-from-</text>
  <text x="815" y="543" font-family="{FONT}" font-size="12" text-anchor="start" fill="{TEXT_SECONDARY}">remediation: &quot;true&quot;</text>
  
  <!-- After state -->
  <rect x="1250" y="300" width="350" height="300" rx="12" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="3"/>
  <text x="1425" y="340" font-family="{FONT}" font-size="20" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">維護完成 (After)</text>
  
  <!-- After content box -->
  <rect x="1280" y="370" width="290" height="200" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="1295" y="395" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Taints: []</text>
  <text x="1295" y="415" font-family="{FONT}" font-size="12" text-anchor="start" fill="{TEXT_SECONDARY}">(維護 Taint 已移除)</text>
  <text x="1295" y="450" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Unschedulable:</text>
  <text x="1455" y="450" font-family="{FONT}" font-size="14" text-anchor="start" fill="#10b981">false</text>
  <text x="1295" y="485" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="{TEXT_PRIMARY}">Labels:</text>
  <text x="1295" y="510" font-family="{FONT}" font-size="13" text-anchor="start" fill="{TEXT_SECONDARY}">(medik8s 標記已移除)</text>
  
  <!-- End state -->
  <circle cx="1500" cy="750" r="20" fill="{TEXT_PRIMARY}"/>
  <circle cx="1500" cy="750" r="15" fill="{TEXT_PRIMARY}"/>
  <circle cx="1500" cy="750" r="8" fill="{BG}"/>
  
  <!-- Arrow: Initial -> Before -->
  <path d="M 120 450 L 250 450" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  
  <!-- Arrow: Before -> During -->
  <path d="M 600 450 L 750 450" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="675" y="420" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">NodeMaintenance</text>
  <text x="675" y="438" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">CR 建立</text>
  <text x="675" y="470" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">①加 Taint</text>
  <text x="675" y="486" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">②Cordon</text>
  <text x="675" y="502" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">③加 Label</text>
  
  <!-- Arrow: During -> After -->
  <path d="M 1150 450 L 1250 450" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="1200" y="420" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">NodeMaintenance</text>
  <text x="1200" y="438" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">CR 刪除</text>
  <text x="1200" y="470" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">①移除 Label</text>
  <text x="1200" y="486" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">②移除 Taint</text>
  <text x="1200" y="502" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">③Uncordon</text>
  
  <!-- Arrow: After -> End -->
  <path d="M 1425 600 L 1425 750 L 1480 750" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  
</svg>'''

with open('nmo-taints-1.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-taints-1.svg")
