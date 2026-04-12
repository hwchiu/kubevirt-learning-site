#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO RequestLease flowchart"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1200">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1400" height="1200" fill="{BG}"/>
  
  <!-- Title -->
  <text x="700" y="40" font-family="{FONT}" font-size="18" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">RequestLease 詳細流程</text>
  
  <!-- Start -->
  <ellipse cx="700" cy="100" rx="120" ry="40" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="700" y="108" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">開始 RequestLease</text>
  
  <!-- GET Lease -->
  <path d="M 700 140 L 700 200" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 600 200 L 700 250 L 800 200 L 700 150 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="700" y="210" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">GET Lease</text>
  <text x="700" y="232" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">node-&lt;nodename&gt;</text>
  
  <!-- Branch: Not exists -->
  <path d="M 600 200 L 300 200 L 300 350" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="450" y="190" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">不存在</text>
  
  <!-- CREATE new Lease -->
  <rect x="180" y="350" width="240" height="90" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="300" y="380" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">CREATE 新 Lease</text>
  <text x="300" y="405" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">HolderIdentity=</text>
  <text x="300" y="423" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">node-maintenance</text>
  <text x="300" y="440" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">duration=3600s</text>
  
  <!-- CREATE -> Success -->
  <path d="M 300 440 L 300 1100 L 590 1100" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Branch: Exists -->
  <path d="M 700 250 L 700 330" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="800" y="232" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">存在</text>
  
  <!-- Check HolderIdentity -->
  <path d="M 570 330 L 700 400 L 830 330 L 700 260 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="700" y="345" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">HolderIdentity</text>
  <text x="700" y="365" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">==</text>
  <text x="700" y="385" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">node-maintenance?</text>
  
  <!-- Yes (same holder) -> UPDATE -->
  <path d="M 830 330 L 1000 330 L 1000 460" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="900" y="320" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">是（同一持有者）</text>
  
  <rect x="880" y="460" width="240" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="1000" y="490" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">UPDATE Lease</text>
  <text x="1000" y="515" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">更新 RenewTime</text>
  
  <!-- UPDATE -> Success -->
  <path d="M 1000 530 L 1000 1100 L 810 1100" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- No (different holder) -> Check expired -->
  <path d="M 700 400 L 700 510" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="570" y="385" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">否（不同持有者）</text>
  
  <path d="M 600 510 L 700 580 L 800 510 L 700 440 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="700" y="525" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">Lease 是否</text>
  <text x="700" y="545" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">已過期？</text>
  <text x="700" y="565" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}"></text>
  
  <!-- Not expired -> AlreadyHeldError -->
  <path d="M 600 510 L 300 510 L 300 680" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="450" y="500" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">未過期</text>
  
  <rect x="180" y="680" width="240" height="80" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="300" y="710" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="#991b1b">return</text>
  <text x="300" y="730" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="#991b1b">AlreadyHeldError</text>
  <text x="300" y="750" font-family="{FONT}" font-size="13" text-anchor="middle" fill="#7f1d1d">holderIdentity=&lt;current holder&gt;</text>
  
  <!-- AlreadyHeldError -> FAIL -->
  <path d="M 300 760 L 300 1000" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Expired -> TAKEOVER -->
  <path d="M 800 510 L 1000 510 L 1000 680" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="900" y="500" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">已過期</text>
  
  <rect x="880" y="680" width="240" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="1000" y="710" font-family="{FONT}" font-size="15" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">TAKEOVER</text>
  <text x="1000" y="735" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">更新 HolderIdentity</text>
  <text x="1000" y="752" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">LeaseTransitions++</text>
  
  <!-- TAKEOVER -> Success -->
  <path d="M 1000 760 L 1000 1100 L 810 1100" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- FAIL end -->
  <ellipse cx="300" cy="1000" rx="70" ry="35" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="300" y="1008" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="#991b1b">失敗</text>
  
  <!-- Success end -->
  <ellipse cx="700" cy="1100" rx="70" ry="35" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="700" y="1108" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">成功</text>
  
</svg>'''

with open('nmo-lease-1.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-lease-1.svg")
