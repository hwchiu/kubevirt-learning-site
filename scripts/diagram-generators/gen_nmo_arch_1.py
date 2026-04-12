#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO architecture overview - simple flow"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 250">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1000" height="250" fill="{BG}"/>
  
  <!-- User -->
  <rect x="50" y="80" width="180" height="90" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="140" y="120" font-family="{FONT}" font-size="32" text-anchor="middle" fill="{TEXT_PRIMARY}">👤</text>
  <text x="140" y="150" font-family="{FONT}" font-size="16" text-anchor="middle" fill="{TEXT_PRIMARY}">使用者</text>
  
  <!-- Arrow 1: kubectl apply -->
  <line x1="230" y1="125" x2="330" y2="125" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="280" y="115" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">kubectl apply</text>
  
  <!-- NodeMaintenance CR -->
  <rect x="350" y="80" width="180" height="90" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="440" y="120" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">NodeMaintenance</text>
  <text x="440" y="145" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">CR</text>
  
  <!-- Arrow 2: watch -->
  <line x1="530" y1="125" x2="630" y2="125" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="580" y="115" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">watch</text>
  
  <!-- Controller -->
  <rect x="650" y="60" width="180" height="130" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="740" y="110" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">NodeMaintenance</text>
  <text x="740" y="135" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Reconciler</text>
  <text x="740" y="165" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">taint / cordon / drain</text>
  
  <!-- Arrow 3: to Node -->
  <path d="M 740 190 L 740 220 L 240 220 L 240 170" fill="none" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="480" y="235" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">操作節點</text>
  
  <!-- Node (reusing User position for circular flow) -->
  <circle cx="240" cy="125" r="8" fill="none" stroke="{ARROW}" stroke-width="2"/>
  <text x="280" y="175" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">☸ Node</text>
  
</svg>'''

with open('nmo-arch-1.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-arch-1.svg")
