#!/usr/bin/env python3
"""Generate Notion Clean SVG for NMO events lifecycle sequence diagram"""

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
  <text x="700" y="40" font-family="{FONT}" font-size="18" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">事件生命週期 - 完整維護週期中各事件的觸發順序</text>
  
  <!-- Participants (headers) -->
  <!-- User -->
  <rect x="100" y="80" width="160" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="180" y="120" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">User</text>
  
  <!-- Controller -->
  <rect x="350" y="80" width="160" height="70" rx="8" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2"/>
  <text x="430" y="120" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Controller</text>
  
  <!-- Node -->
  <rect x="600" y="80" width="160" height="70" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
  <text x="680" y="120" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Node</text>
  
  <!-- K8s Events -->
  <rect x="850" y="80" width="200" height="70" rx="8" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
  <text x="950" y="110" font-family="{FONT}" font-size="16" font-weight="600" text-anchor="middle" fill="{TEXT_PRIMARY}">Kubernetes</text>
  <text x="950" y="135" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">Events</text>
  
  <!-- Lifelines -->
  <line x1="180" y1="150" x2="180" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="430" y1="150" x2="430" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="680" y1="150" x2="680" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="950" y1="150" x2="950" y2="1050" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  
  <!-- Message 1: User -> Controller (apply CR) -->
  <path d="M 180 200 L 430 200" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="305" y="188" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">kubectl apply</text>
  <text x="305" y="205" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">NodeMaintenance CR</text>
  
  <!-- Message 2: Controller -> K8s (BeginMaintenance) -->
  <path d="M 430 250 L 950 250" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="690" y="240" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">🟢 Normal:</text>
  <text x="690" y="258" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">BeginMaintenance</text>
  
  <!-- Note: Cordon + begin draining -->
  <rect x="350" y="280" width="380" height="50" rx="6" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="540" y="300" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">Cordon node +</text>
  <text x="540" y="318" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">begin draining pods</text>
  
  <!-- Message 3: Controller -> Node (Drain) -->
  <path d="M 430 370 L 680 370" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="555" y="360" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">Drain (evict pods)</text>
  
  <!-- Activation box for Node draining -->
  <rect x="670" y="380" width="20" height="120" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="1"/>
  
  <!-- Note: No events during drain -->
  <rect x="380" y="420" width="220" height="40" rx="6" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="490" y="435" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">排空過程中</text>
  <text x="490" y="453" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">不發送事件</text>
  
  <!-- Message 4: Node -> Controller (complete) -->
  <path d="M 680 500 L 430 500" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow-back)" stroke-dasharray="5,3"/>
  <text x="555" y="490" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{ARROW}">Drain complete</text>
  
  <!-- Message 5: Controller -> K8s (SucceedMaintenance) -->
  <path d="M 430 550 L 950 550" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="690" y="540" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">🟢 Normal:</text>
  <text x="690" y="558" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">SucceedMaintenance</text>
  
  <!-- Note: Phase = Succeeded -->
  <rect x="350" y="570" width="160" height="30" rx="6" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="430" y="590" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">Phase = Succeeded</text>
  
  <!-- Separator (gap for readability) -->
  <line x1="50" y1="640" x2="1350" y2="640" stroke="{BOX_STROKE}" stroke-width="1" stroke-dasharray="8,4"/>
  
  <!-- Message 6: User -> Controller (delete CR) -->
  <path d="M 180 690 L 430 690" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="305" y="678" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">kubectl delete</text>
  <text x="305" y="695" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">NodeMaintenance CR</text>
  
  <!-- Message 7: Controller -> Node (Uncordon) -->
  <path d="M 430 740 L 680 740" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="555" y="730" font-family="{FONT}" font-size="14" text-anchor="middle" fill="{TEXT_SECONDARY}">Uncordon node</text>
  
  <!-- Message 8: Controller -> K8s (UncordonNode) -->
  <path d="M 430 790 L 950 790" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="690" y="780" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">🟢 Normal:</text>
  <text x="690" y="798" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">UncordonNode</text>
  
  <!-- Message 9: Controller -> K8s (RemovedMaintenance) -->
  <path d="M 430 840 L 950 840" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="690" y="830" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">🟢 Normal:</text>
  <text x="690" y="848" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#10b981">RemovedMaintenance</text>
  
  <!-- Note: Finalizer removed -->
  <rect x="350" y="860" width="200" height="40" rx="6" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1"/>
  <text x="450" y="875" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">Finalizer removed,</text>
  <text x="450" y="893" font-family="{FONT}" font-size="13" text-anchor="middle" fill="{TEXT_SECONDARY}">CR deleted</text>
  
  <!-- Error path (alt frame) -->
  <rect x="350" y="930" width="650" height="100" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="365" y="955" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="start" fill="#991b1b">錯誤路徑</text>
  <text x="365" y="973" font-family="{FONT}" font-size="12" text-anchor="start" fill="#7f1d1d">(節點不存在 / Lease 超限 / 嚴重錯誤)</text>
  
  <!-- Error message: Controller -> K8s (FailedMaintenance) -->
  <path d="M 430 990 L 950 990" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="690" y="980" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#dc2626">🔴 Warning:</text>
  <text x="690" y="998" font-family="{FONT}" font-size="14" font-weight="600" text-anchor="middle" fill="#dc2626">FailedMaintenance</text>
  
</svg>'''

with open('nmo-events-1.svg', 'w') as f:
    f.write(svg)

print("✓ Generated nmo-events-1.svg")
