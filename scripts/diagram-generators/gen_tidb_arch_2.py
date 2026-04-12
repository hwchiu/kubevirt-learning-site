#!/usr/bin/env python3
"""Generate TiDB SQL Query Execution Sequence diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 950">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
    <marker id="arrow-back" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto">
      <polygon points="8.5 0.5, 0 3.5, 8.5 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="950" fill="{BG}"/>
  
  <!-- Participants -->
  <rect x="50" y="50" width="180" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="140" y="90" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Client</text>
  
  <rect x="320" y="50" width="180" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="410" y="90" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">TiDB Server</text>
  
  <rect x="590" y="50" width="180" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="680" y="90" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">PD</text>
  
  <rect x="860" y="50" width="180" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="950" y="90" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">TiKV</text>
  
  <!-- Lifelines -->
  <line x1="140" y1="120" x2="140" y2="900" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="410" y1="120" x2="410" y2="900" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="680" y1="120" x2="680" y2="900" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="950" y1="120" x2="950" y2="900" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
  
  <!-- Message 1: Client to TiDB -->
  <path d="M 140 160 L 410 160" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="250" y="150" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">SELECT * FROM t</text>
  <text x="250" y="165" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">WHERE id=1</text>
  
  <!-- TiDB internal processing 1 -->
  <rect x="415" y="200" width="10" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>
  <text x="440" y="230" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">解析 SQL → AST</text>
  
  <!-- TiDB internal processing 2 -->
  <rect x="415" y="260" width="10" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>
  <text x="440" y="290" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">語意分析 → 邏輯計劃</text>
  
  <!-- TiDB internal processing 3 -->
  <rect x="415" y="320" width="10" height="60" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1"/>
  <text x="440" y="345" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">優化 → 物理計劃</text>
  <text x="440" y="360" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">(IndexLookup)</text>
  
  <!-- Message 2: TiDB to PD (TSO) -->
  <path d="M 410 420 L 680 420" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="520" y="410" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">獲取 TSO</text>
  <text x="520" y="425" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">(開始時間戳)</text>
  
  <!-- Response: PD to TiDB -->
  <path d="M 680 460 L 410 460" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="520" y="450" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">startTS</text>
  
  <!-- Message 3: TiDB to PD (Region route) -->
  <path d="M 410 510 L 680 510" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="480" y="500" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">查詢 Region 路由</text>
  <text x="480" y="515" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">(id=1 位於哪個 Region)</text>
  
  <!-- Response: PD to TiDB -->
  <path d="M 680 560 L 410 560" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="500" y="550" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Region Leader 位址</text>
  
  <!-- Message 4: TiDB to TiKV -->
  <path d="M 410 610 L 950 610" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="640" y="600" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">KV Get (startTS, key)</text>
  
  <!-- Response: TiKV to TiDB -->
  <path d="M 950 660 L 410 660" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="650" y="650" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">value</text>
  
  <!-- Final response: TiDB to Client -->
  <path d="M 410 710 L 140 710" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="240" y="700" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">回傳結果集</text>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("tidb-architecture-sequence-2.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated tidb-architecture-sequence-2.svg")
