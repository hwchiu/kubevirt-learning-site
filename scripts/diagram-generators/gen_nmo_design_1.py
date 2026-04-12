#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO lease coordination sequence diagram"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 900">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
    <marker id="arrow-back" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto">
      <polygon points="8.5 0.5, 0 3.5, 8.5 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1400" height="900" fill="{BG}"/>
  
  <!-- Title -->
  <text x="700" y="40" font-family="{FONT}" font-size="18" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Lease 協調機制 - 防止多節點同時維護</text>
  
  <!-- Participants (headers) -->
  <!-- NM1 -->
  <rect x="80" y="80" width="160" height="80" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="160" y="115" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">NodeMaintenance</text>
  <text x="160" y="140" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">node01</text>
  
  <!-- NM2 -->
  <rect x="300" y="80" width="160" height="80" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="380" y="115" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">NodeMaintenance</text>
  <text x="380" y="140" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">node02</text>
  
  <!-- Lease -->
  <rect x="540" y="80" width="160" height="80" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="620" y="115" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Lease</text>
  <text x="620" y="140" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">(etcd)</text>
  
  <!-- Node 1 -->
  <rect x="780" y="80" width="160" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="860" y="125" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">node01</text>
  
  <!-- Node 2 -->
  <rect x="1000" y="80" width="160" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="1080" y="125" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">node02</text>
  
  <!-- Lifelines -->
  <line x1="160" y1="160" x2="160" y2="850" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="380" y1="160" x2="380" y2="850" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="620" y1="160" x2="620" y2="850" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="860" y1="160" x2="860" y2="850" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="1080" y1="160" x2="1080" y2="850" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  
  <!-- Message 1: NM1 -> Lease (request) -->
  <path d="M 160 220 L 620 220" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="390" y="210" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">嘗試取得 lease</text>
  
  <!-- Message 2: NM2 -> Lease (request) -->
  <path d="M 380 270 L 620 270" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="500" y="260" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">嘗試取得 lease</text>
  
  <!-- Message 3: Lease -> NM1 (success) -->
  <path d="M 620 320 L 160 320" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow-back)" stroke-dasharray="5,3"/>
  <text x="330" y="310" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{ARROW}">✅ 取得成功</text>
  
  <!-- Message 4: Lease -> NM2 (wait) -->
  <path d="M 620 370 L 380 370" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow-back)" stroke-dasharray="5,3"/>
  <text x="500" y="360" font-family="{FONT}" font-size="14" text-anchor="middle" fill="#dc2626">❌ 等待（lease 已被佔用）</text>
  
  <!-- Message 5: NM1 -> N1 (cordon + drain) -->
  <path d="M 160 450 L 860 450" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="510" y="440" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">cordon + drain</text>
  
  <!-- Activation box for N1 draining -->
  <rect x="850" y="460" width="20" height="120" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1"/>
  
  <!-- Message 6: N1 -> NM1 (complete) -->
  <path d="M 860 580 L 160 580" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow-back)" stroke-dasharray="5,3"/>
  <text x="510" y="570" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{ARROW}">排空完成</text>
  
  <!-- Message 7: NM1 -> Lease (release) -->
  <path d="M 160 630 L 620 630" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="390" y="620" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">釋放 lease</text>
  
  <!-- Message 8: Lease -> NM2 (success) -->
  <path d="M 620 680 L 380 680" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow-back)" stroke-dasharray="5,3"/>
  <text x="500" y="670" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{ARROW}">✅ 取得成功</text>
  
  <!-- Message 9: NM2 -> N2 (cordon + drain) -->
  <path d="M 380 750 L 1080 750" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="730" y="740" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">cordon + drain</text>
  
  <!-- Activation box for N2 draining -->
  <rect x="1070" y="760" width="20" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1"/>
  
  <!-- Note box -->
  <rect x="50" y="860" width="1300" height="20" rx="4" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="700" y="873" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">Lease 持有時間：3600 秒（1 小時） | 確保同一時間只有一個節點在進行排空操作</text>
  
</svg>'''

with open('nmo-design-1.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-design-1.svg")
