#!/usr/bin/env python3
"""Generate LogManager Architecture diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="600" fill="{BG}"/>
  
  <!-- LogManager -->
  <rect x="50" y="50" width="200" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="150" y="95" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">LogManager</text>
  
  <!-- UnifiedLog instances -->
  <rect x="400" y="30" width="220" height="100" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="510" y="65" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">UnifiedLog</text>
  <text x="510" y="85" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">(topic-0)</text>
  
  <rect x="400" y="150" width="220" height="100" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="510" y="185" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">UnifiedLog</text>
  <text x="510" y="205" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">(topic-1)</text>
  
  <rect x="400" y="270" width="220" height="100" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="510" y="305" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">UnifiedLog</text>
  <text x="510" y="325" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">(topic-N)</text>
  
  <!-- LogSegments for first UnifiedLog -->
  <rect x="720" y="20" width="180" height="60" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="810" y="45" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">LogSegment 1</text>
  <text x="810" y="62" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">(.log + .index)</text>
  
  <rect x="720" y="90" width="180" height="60" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="810" y="115" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">LogSegment 2</text>
  <text x="810" y="132" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">(.log + .index)</text>
  
  <rect x="720" y="160" width="180" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="810" y="185" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">LogSegment N</text>
  <text x="810" y="202" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">（Active）</text>
  <text x="810" y="218" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">（寫入中）</text>
  
  <!-- Background tasks -->
  <rect x="50" y="420" width="200" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="150" y="450" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">LogCleaner</text>
  <text x="150" y="470" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（Compaction 後台）</text>
  
  <rect x="300" y="420" width="200" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="400" y="450" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">LogRetention</text>
  <text x="400" y="470" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（過期刪除後台）</text>
  
  <!-- Arrows: LogManager to UnifiedLogs -->
  <path d="M 250 70 L 400 70" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="315" y="65" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">管理 N 個</text>
  
  <path d="M 250 90 L 400 200" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="315" y="145" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">管理 N 個</text>
  
  <path d="M 250 110 L 400 320" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="315" y="225" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">管理 N 個</text>
  
  <!-- Arrows: UnifiedLog to LogSegments -->
  <path d="M 620 55 L 720 50" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 620 75 L 720 120" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 620 95 L 720 195" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  
  <!-- Arrows: LogManager to background tasks -->
  <path d="M 150 130 L 150 420" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 170 130 L 390 420" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("kafka-modules-logmanager-1.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated kafka-modules-logmanager-1.svg")
