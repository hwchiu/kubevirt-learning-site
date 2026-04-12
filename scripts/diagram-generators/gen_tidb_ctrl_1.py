#!/usr/bin/env python3
"""Generate TiDB Connection Processing Sequence diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 1000">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1300" height="1000" fill="{BG}"/>
  
  <!-- Participants -->
  <rect x="50" y="50" width="180" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="140" y="90" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Client</text>
  
  <rect x="350" y="50" width="180" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="440" y="85" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/server</text>
  
  <rect x="650" y="50" width="180" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="740" y="85" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/session</text>
  
  <rect x="950" y="50" width="200" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="1050" y="85" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/executor</text>
  
  <!-- Lifelines -->
  <line x1="140" y1="120" x2="140" y2="950" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="440" y1="120" x2="440" y2="950" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="740" y1="120" x2="740" y2="950" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="1050" y1="120" x2="1050" y2="950" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  
  <!-- Message 1: TCP connection -->
  <path d="M 140 160 L 440 160" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="260" y="150" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">TCP 連線建立（:4000）</text>
  
  <!-- Message 2: Handshake -->
  <path d="M 440 200 L 140 200" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="220" y="190" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Handshake 封包</text>
  <text x="220" y="205" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">(Server Greeting)</text>
  
  <!-- Message 3: Auth -->
  <path d="M 140 250 L 440 250" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="250" y="240" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Auth 封包</text>
  <text x="250" y="255" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">(帳號/密碼)</text>
  
  <!-- Internal: Verify -->
  <rect x="445" y="280" width="10" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>
  <text x="470" y="310" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">驗證身分</text>
  <text x="470" y="325" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">(pkg/privilege)</text>
  
  <!-- Message 4: OK -->
  <path d="M 440 350 L 140 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="260" y="340" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">OK 封包</text>
  
  <!-- Loop box -->
  <rect x="80" y="400" width="1100" height="450" fill="none" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="8,4" rx="8"/>
  <text x="90" y="425" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_SECONDARY}">loop 每條 SQL</text>
  
  <!-- Message 5: COM_QUERY -->
  <path d="M 140 460 L 440 460" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="220" y="450" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">COM_QUERY /</text>
  <text x="220" y="465" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">COM_STMT_EXECUTE</text>
  
  <!-- Message 6: Create context -->
  <path d="M 440 510 L 740 510" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="540" y="500" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">建立 Statement</text>
  <text x="540" y="515" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Context</text>
  
  <!-- Message 7: Execute -->
  <path d="M 740 560 L 1050 560" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="840" y="550" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">解析 → 優化 →</text>
  <text x="840" y="565" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">執行</text>
  
  <!-- Response: Result -->
  <path d="M 1050 610 L 740 610" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="840" y="600" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">結果集 /</text>
  <text x="840" y="615" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">受影響行數</text>
  
  <!-- Response: To server -->
  <path d="M 740 660 L 440 660" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="560" y="650" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">結果</text>
  
  <!-- Response: To client -->
  <path d="M 440 710 L 140 710" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="230" y="700" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">ResultSet /</text>
  <text x="230" y="715" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">OK 封包</text>
  
  <!-- Message 8: COM_QUIT -->
  <path d="M 140 880 L 440 880" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="260" y="870" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">COM_QUIT</text>
  
  <!-- Message 9: Close session -->
  <path d="M 440 920 L 740 920" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="550" y="910" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">關閉 Session</text>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("tidb-controllers-conn-1.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated tidb-controllers-conn-1.svg")
