#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO state machine"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="800" fill="{BG}"/>
  
  <!-- Initial state -->
  <circle cx="100" cy="400" r="20" fill="{TEXT_PRIMARY}"/>
  <circle cx="100" cy="400" r="12" fill="{BG}"/>
  
  <!-- Running state -->
  <rect x="300" y="320" width="200" height="160" rx="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="3"/>
  <text x="400" y="410" font-family="{FONT}" font-size="20" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Running</text>
  
  <!-- Succeeded state -->
  <rect x="700" y="100" width="220" height="160" rx="80" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="3"/>
  <text x="810" y="190" font-family="{FONT}" font-size="20" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Succeeded</text>
  
  <!-- Failed state -->
  <rect x="700" y="540" width="220" height="160" rx="80" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="3"/>
  <text x="810" y="630" font-family="{FONT}" font-size="20" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Failed</text>
  
  <!-- End state -->
  <circle cx="1100" cy="400" r="20" fill="{TEXT_PRIMARY}"/>
  <circle cx="1100" cy="400" r="15" fill="{TEXT_PRIMARY}"/>
  <circle cx="1100" cy="400" r="8" fill="{BG}"/>
  
  <!-- Arrow: Initial -> Running -->
  <path d="M 120 400 L 300 400" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="210" y="380" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">CR 建立，</text>
  <text x="210" y="398" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">新增 finalizer</text>
  
  <!-- Arrow: Running -> Running (self loop) -->
  <path d="M 310 320 Q 280 220 400 220 Q 520 220 490 320" fill="none" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="400" y="195" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">drain 進行中，</text>
  <text x="400" y="213" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">error 時 requeue 5s</text>
  
  <!-- Arrow: Running -> Succeeded -->
  <path d="M 500 360 L 700 220" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="580" y="275" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">所有 Pod</text>
  <text x="580" y="293" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">驅逐完成</text>
  
  <!-- Arrow: Running -> Failed -->
  <path d="M 500 440 L 700 580" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="550" y="505" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">Node 不存在 OR</text>
  <text x="550" y="523" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">ErrorOnLeaseCount &gt; 3</text>
  
  <!-- Arrow: Succeeded -> End -->
  <path d="M 920 180 L 1100 180 L 1100 380" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="1010" y="165" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">CR 刪除，</text>
  <text x="1010" y="183" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">節點 uncordon</text>
  
  <!-- Arrow: Failed -> End -->
  <path d="M 920 620 L 1100 620 L 1100 420" stroke="{ARROW}" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="990" y="605" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">CR 刪除，</text>
  <text x="990" y="623" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">節點 uncordon</text>
  <text x="990" y="641" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">（若可行）</text>
  
</svg>'''

with open('nmo-arch-3.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-arch-3.svg")
