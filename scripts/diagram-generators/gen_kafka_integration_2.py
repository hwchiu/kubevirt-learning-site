#!/usr/bin/env python3
"""Generate Schema Registry Integration diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="700" fill="{BG}"/>
  
  <!-- Producer -->
  <rect x="50" y="100" width="180" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="140" y="145" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Producer</text>
  
  <!-- Schema Registry -->
  <rect x="510" y="50" width="180" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="600" y="95" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Schema Registry</text>
  
  <!-- Kafka -->
  <rect x="510" y="250" width="180" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="600" y="295" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Kafka</text>
  
  <!-- Consumer -->
  <rect x="970" y="500" width="180" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="1060" y="545" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Consumer</text>
  
  <!-- Step 1: Producer to Schema Registry -->
  <path d="M 230 120 L 510 80" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="280" y="90" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">1. 向 Schema Registry</text>
  <text x="280" y="105" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">登記 Schema</text>
  
  <!-- Step 2: Schema Registry to Producer -->
  <path d="M 510 110 L 230 150" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="280" y="140" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">2. 回傳 Schema ID</text>
  
  <!-- Step 3: Producer to Kafka -->
  <path d="M 230 180 L 230 250 L 510 270" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="250" y="210" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">3. 發送: [Magic Byte]</text>
  <text x="250" y="225" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">[Schema ID][Avro Payload]</text>
  
  <!-- Step 4: Kafka to Consumer -->
  <path d="M 690 300 L 970 520" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="790" y="400" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">4. 消費訊息</text>
  
  <!-- Step 5: Consumer to Schema Registry -->
  <path d="M 970 520 L 690 100" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="780" y="290" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">5. 從 Schema Registry</text>
  <text x="780" y="305" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">取得 Schema</text>
  
  <!-- Step 6: Schema Registry to Consumer -->
  <path d="M 690 110 L 970 540" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="800" y="340" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">6. 回傳 Schema</text>
  
  <!-- Step 7: Consumer uses Schema (self-arrow) -->
  <path d="M 1060 580 L 1060 620 L 1100 620 L 1100 580" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="1070" y="605" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">7. 使用 Schema</text>
  <text x="1070" y="620" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">反序列化</text>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("kafka-integration-schema-2.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated kafka-integration-schema-2.svg")
