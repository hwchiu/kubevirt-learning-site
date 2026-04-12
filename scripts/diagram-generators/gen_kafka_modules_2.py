#!/usr/bin/env python3
"""Generate Kafka Streams Core Classes Hierarchy diagram (Notion Clean Style 4)"""

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
  
  <!-- KafkaStreams -->
  <rect x="50" y="50" width="240" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="170" y="85" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">KafkaStreams</text>
  <text x="170" y="105" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（串流應用主程序）</text>
  
  <!-- StreamThread[] -->
  <rect x="400" y="50" width="240" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="520" y="85" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">StreamThread[]</text>
  <text x="520" y="105" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（N 個執行緒）</text>
  
  <!-- TaskManager -->
  <rect x="750" y="50" width="240" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="870" y="75" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">TaskManager</text>
  <text x="870" y="95" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（管理 Active/Standby</text>
  <text x="870" y="113" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">Task）</text>
  
  <!-- StreamTask -->
  <rect x="700" y="200" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="800" y="230" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">StreamTask</text>
  <text x="800" y="250" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（Active：處理並</text>
  <text x="800" y="267" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">生產）</text>
  
  <!-- StandbyTask -->
  <rect x="950" y="200" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="1050" y="230" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">StandbyTask</text>
  <text x="1050" y="250" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（備援：維護狀態</text>
  <text x="1050" y="267" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">副本）</text>
  
  <!-- ProcessorChain -->
  <rect x="500" y="350" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="600" y="380" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">ProcessorChain</text>
  <text x="600" y="400" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（ProcessorNode</text>
  <text x="600" y="417" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">鏈）</text>
  
  <!-- StateStore -->
  <rect x="300" y="500" width="200" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="400" y="530" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">StateStore</text>
  <text x="400" y="550" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（RocksDB / InMemory）</text>
  
  <!-- RecordCollector -->
  <rect x="750" y="350" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="850" y="380" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">RecordCollector</text>
  <text x="850" y="400" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">（輸出至 Kafka）</text>
  
  <!-- Arrows -->
  <path d="M 290 90 L 400 90" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 640 90 L 750 90" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 840 130 L 800 200" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 900 130 L 1050 200" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 750 280 L 600 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 600 430 L 450 500" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 800 280 L 850 350" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("kafka-modules-streams-2.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated kafka-modules-streams-2.svg")
