#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO ErrorOnLeaseCount mechanism"""

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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="900" fill="{BG}"/>
  
  <!-- Title -->
  <text x="600" y="40" font-family="{FONT}" font-size="18" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">ErrorOnLeaseCount 機制 - 避免節點永久被 cordon</text>
  
  <!-- Start -->
  <ellipse cx="600" cy="100" rx="110" ry="40" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="600" y="108" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">RequestLease</text>
  
  <!-- Check result -->
  <path d="M 600 140 L 600 210" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 520 210 L 600 260 L 680 210 L 600 160 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="600" y="225" font-family="{FONT}" font-size="15" text-anchor="middle" fill="{TEXT_PRIMARY}">結果？</text>
  
  <!-- Branch: AlreadyHeldError or other error -->
  <path d="M 520 210 L 250 210 L 250 350" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="350" y="195" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">AlreadyHeldError</text>
  <text x="350" y="210" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">且 DrainProgress &gt; 0</text>
  
  <!-- Other error -->
  <path d="M 520 250 L 450 250 L 450 350" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="485" y="240" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">其他錯誤</text>
  
  <!-- Increment counter box (merged) -->
  <rect x="150" y="350" width="400" height="60" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="350" y="385" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="#991b1b">ErrorOnLeaseCount++</text>
  
  <!-- Success branch -->
  <path d="M 680 210 L 900 210 L 900 350" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="790" y="200" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">成功</text>
  
  <!-- Reset counter -->
  <rect x="780" y="350" width="240" height="60" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="900" y="385" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">ErrorOnLeaseCount = 0</text>
  
  <!-- Success -> End (merge later) -->
  <path d="M 900 410 L 900 800 L 710 800" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Check threshold -->
  <path d="M 350 410 L 350 490" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 240 490 L 350 560 L 460 490 L 350 420 Z" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="350" y="505" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">ErrorOnLeaseCount</text>
  <text x="350" y="525" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_PRIMARY}">&gt; 3？</text>
  
  <!-- No -> Requeue -->
  <path d="M 240 490 L 150 490 L 150 650" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="195" y="480" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">否</text>
  
  <rect x="30" y="650" width="240" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="150" y="685" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">重新排程 reconcile</text>
  
  <!-- Requeue -> End -->
  <path d="M 150 710 L 150 800 L 490 800" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- Yes -> Uncordon + Failed -->
  <path d="M 460 490 L 650 490 L 650 650" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="555" y="480" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">是</text>
  
  <rect x="530" y="650" width="240" height="80" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="650" y="680" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="#991b1b">Uncordon 節點</text>
  <text x="650" y="707" font-family="{FONT}" font-size="15" text-anchor="middle" fill="#7f1d1d">設定 Phase=Failed</text>
  
  <!-- Uncordon -> End maintenance -->
  <path d="M 650 730 L 650 800 L 710 800" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  
  <!-- End -->
  <ellipse cx="600" cy="800" rx="110" ry="40" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="600" y="808" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">結束維護</text>
  
  <!-- Note box -->
  <rect x="50" y="850" width="1100" height="30" rx="6" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="600" y="870" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{TEXT_SECONDARY}">註：ErrorOnLeaseCount 只會在已開始排水（DrainProgress &gt; 0）後的 AlreadyHeldError 才計數</text>
  
</svg>'''

with open('nmo-lease-2.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-lease-2.svg")
