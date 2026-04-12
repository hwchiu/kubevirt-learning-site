#!/usr/bin/env python3
"""Generate Connect Submodules Architecture diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="800" fill="{BG}"/>
  
  <!-- ConnectAPI (top center) -->
  <rect x="450" y="50" width="300" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="600" y="80" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/api</text>
  <text x="600" y="100" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（Connector/Task/Transform</text>
  <text x="600" y="115" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">介面）</text>
  
  <!-- ConnectRuntime -->
  <rect x="450" y="200" width="300" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="600" y="230" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/runtime</text>
  <text x="600" y="250" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（Worker 執行環境）</text>
  
  <!-- ConnectTransforms -->
  <rect x="50" y="350" width="240" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="170" y="380" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/transforms</text>
  <text x="170" y="400" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（內建 SMT）</text>
  
  <!-- ConnectJson -->
  <rect x="320" y="350" width="240" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="440" y="380" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/json</text>
  <text x="440" y="400" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（JSON Converter）</text>
  
  <!-- ConnectFile -->
  <rect x="590" y="350" width="240" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="710" y="380" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/file</text>
  <text x="710" y="400" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（FileStream Connector）</text>
  
  <!-- ConnectMirror -->
  <rect x="860" y="350" width="240" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="980" y="380" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/mirror</text>
  <text x="980" y="400" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（MirrorMaker 2）</text>
  
  <!-- ConnectMirrorClient -->
  <rect x="320" y="500" width="240" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="440" y="525" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/mirror-client</text>
  <text x="440" y="545" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（MirrorMaker 2</text>
  <text x="440" y="562" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">用戶端）</text>
  
  <!-- ConnectBasicAuth -->
  <rect x="590" y="500" width="260" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="720" y="525" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">connect/basic-auth-</text>
  <text x="720" y="542" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">extension</text>
  <text x="720" y="562" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（HTTP Basic Auth）</text>
  
  <!-- Arrows: ConnectAPI to all modules -->
  <path d="M 600 130 L 600 200" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  
  <path d="M 550 130 L 170 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 570 130 L 440 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 630 130 L 710 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 650 130 L 980 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("kafka-modules-connect-3.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated kafka-modules-connect-3.svg")
