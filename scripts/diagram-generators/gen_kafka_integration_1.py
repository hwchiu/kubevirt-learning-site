#!/usr/bin/env python3
"""Generate MirrorMaker 2 Architecture diagram (Notion Clean Style 4)"""

def generate_svg():
    # Style constants
    FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
    BG = "#ffffff"
    BOX_FILL = "#f9fafb"
    BOX_STROKE = "#e5e7eb"
    CONTAINER_FILL = "#f0f4ff"
    CONTAINER_STROKE = "#c7d2fe"
    ARROW = "#3b82f6"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6b7280"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 450">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1400" height="450" fill="{BG}"/>
  
  <!-- Source Cluster -->
  <rect x="50" y="50" width="260" height="150" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="180" y="80" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Source 叢集</text>
  <rect x="80" y="100" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="180" y="145" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Broker (Source)</text>
  
  <!-- MirrorMaker 2 Worker -->
  <rect x="390" y="50" width="620" height="350" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="700" y="80" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">MirrorMaker 2 Worker</text>
  
  <!-- MirrorSourceConnector -->
  <rect x="420" y="100" width="260" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="550" y="133" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">MirrorSourceConnector</text>
  <text x="550" y="155" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（複製 Topic 資料）</text>
  
  <!-- MirrorCheckpointConnector -->
  <rect x="420" y="200" width="260" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="550" y="233" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">MirrorCheckpointConnector</text>
  <text x="550" y="255" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（複製 Consumer 位移）</text>
  
  <!-- MirrorHeartbeatConnector -->
  <rect x="420" y="300" width="260" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="550" y="333" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">MirrorHeartbeatConnector</text>
  <text x="550" y="355" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（心跳監控）</text>
  
  <!-- Target Cluster -->
  <rect x="1090" y="50" width="260" height="150" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="1220" y="80" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Target 叢集</text>
  <rect x="1120" y="100" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="1220" y="145" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Broker (Target)</text>
  
  <!-- Arrows -->
  <!-- Source to MirrorSource -->
  <path d="M 310 140 L 420 140" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="355" y="130" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">消費</text>
  
  <!-- MirrorSource to Target -->
  <path d="M 680 140 L 1120 140" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="880" y="130" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">生產</text>
  
  <!-- Source to MirrorCheckpoint -->
  <path d="M 310 140 L 340 140 L 340 240 L 420 240" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="360" y="200" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">讀取 Offset</text>
  
  <!-- MirrorCheckpoint to Target -->
  <path d="M 680 240 L 1050 240 L 1050 140 L 1120 140" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="840" y="230" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">寫入轉換後 Offset</text>
  
  <!-- MirrorHeartbeat to Target -->
  <path d="M 680 340 L 1070 340 L 1070 140 L 1120 140" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="860" y="330" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">心跳</text>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("kafka-integration-mm2-1.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated kafka-integration-mm2-1.svg")
