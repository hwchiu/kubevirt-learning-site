#!/usr/bin/env python3
"""Generate TiDB Session Lifecycle State Machine diagram (Notion Clean Style 4)"""

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
    ACCENT_FILL = "#eff6ff"
    ACCENT_STROKE = "#bfdbfe"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="700" fill="{BG}"/>
  
  <!-- Initial state -->
  <circle cx="100" cy="150" r="12" fill="{TEXT_PRIMARY}"/>
  <circle cx="100" cy="150" r="18" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="2"/>
  
  <!-- Idle -->
  <rect x="250" y="100" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2" rx="8"/>
  <text x="350" y="145" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Idle</text>
  
  <!-- Active -->
  <rect x="650" y="100" width="200" height="80" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2" rx="8"/>
  <text x="750" y="145" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Active</text>
  
  <!-- InTransaction -->
  <rect x="450" y="350" width="250" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2" rx="8"/>
  <text x="575" y="395" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">InTransaction</text>
  
  <!-- Final state -->
  <circle cx="1000" cy="150" r="12" fill="{TEXT_PRIMARY}"/>
  <circle cx="1000" cy="150" r="18" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="2"/>
  
  <!-- Initial -> Idle -->
  <path d="M 118 150 L 250 140" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="165" y="135" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">連線建立</text>
  
  <!-- Idle -> Active -->
  <path d="M 450 130 L 650 130" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="525" y="120" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">收到 SQL</text>
  
  <!-- Active -> Idle -->
  <path d="M 650 150 L 450 150" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="490" y="170" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">SQL 執行完成</text>
  <text x="490" y="185" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">(非交易)</text>
  
  <!-- Active -> InTransaction -->
  <path d="M 700 180 L 620 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="640" y="255" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">BEGIN 或 DML</text>
  <text x="640" y="270" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">(悲觀交易)</text>
  
  <!-- InTransaction -> Active -->
  <path d="M 650 350 L 730 180" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="720" y="255" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">COMMIT /</text>
  <text x="720" y="270" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">ROLLBACK</text>
  
  <!-- InTransaction -> InTransaction (self loop) -->
  <path d="M 575 430 Q 575 520 630 450" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="520" y="500" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">繼續 DML</text>
  
  <!-- Active -> Final -->
  <path d="M 850 140 L 982 150" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="870" y="130" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">COM_QUIT /</text>
  <text x="870" y="145" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">連線斷開</text>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("tidb-controllers-session-2.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated tidb-controllers-session-2.svg")
