#!/usr/bin/env python3
"""Generate Kafka Architecture Overview diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1200" height="900" fill="{BG}"/>
  
  <!-- Producers Container -->
  <rect x="50" y="50" width="240" height="160" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="170" y="80" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">生產者應用程式</text>
  <rect x="70" y="100" width="200" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="170" y="130" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Producer App 1</text>
  <rect x="70" y="160" width="200" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="170" y="190" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Producer App 2</text>
  
  <!-- Kafka Cluster Container -->
  <rect x="350" y="50" width="500" height="520" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="600" y="80" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Kafka 叢集 (KRaft 模式)</text>
  
  <!-- Controller Quorum Container -->
  <rect x="380" y="100" width="440" height="180" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="600" y="125" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Controller Quorum (Raft)</text>
  <rect x="400" y="140" width="120" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="460" y="170" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Controller 1</text>
  <text x="460" y="185" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Active</text>
  <rect x="540" y="140" width="120" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="600" y="170" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Controller 2</text>
  <text x="600" y="185" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Standby</text>
  <rect x="680" y="140" width="120" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="740" y="170" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Controller 3</text>
  <text x="740" y="185" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Standby</text>
  
  <!-- Broker Nodes Container -->
  <rect x="380" y="300" width="440" height="250" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="600" y="325" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Broker 節點</text>
  <rect x="400" y="345" width="120" height="60" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="460" y="370" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Broker 1</text>
  <text x="460" y="388" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Leader</text>
  <text x="460" y="400" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Partitions</text>
  <rect x="540" y="345" width="120" height="60" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="600" y="370" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Broker 2</text>
  <text x="600" y="388" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Follower</text>
  <text x="600" y="400" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Partitions</text>
  <rect x="680" y="345" width="120" height="60" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="740" y="370" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">Broker 3</text>
  <text x="740" y="388" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Follower</text>
  <text x="740" y="400" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">Partitions</text>
  
  <!-- Metadata Replication Arrow -->
  <path d="M 600 280 L 600 330" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="620" y="310" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Metadata</text>
  <text x="620" y="325" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Replication</text>
  
  <!-- Consumers Container -->
  <rect x="910" y="50" width="240" height="160" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="1030" y="80" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">消費者應用程式</text>
  <rect x="930" y="100" width="200" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="1030" y="130" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Consumer Group A</text>
  <rect x="930" y="160" width="200" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="1030" y="190" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Consumer Group B</text>
  
  <!-- Connect Container -->
  <rect x="50" y="260" width="240" height="160" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="170" y="290" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Kafka Connect</text>
  <rect x="70" y="310" width="200" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="170" y="340" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Source Connector</text>
  <rect x="70" y="370" width="200" height="50" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="170" y="400" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Sink Connector</text>
  
  <!-- Streams Container -->
  <rect x="50" y="470" width="240" height="100" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="170" y="500" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Kafka Streams</text>
  <rect x="70" y="520" width="200" height="40" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="170" y="545" font-family="{FONT}" font-size="14" fill="{TEXT_PRIMARY}" text-anchor="middle">Streams Application</text>
  
  <!-- Arrows: Producers to Brokers -->
  <path d="M 290 125 L 400 360" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="335" y="240" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Produce</text>
  <path d="M 290 185 L 540 360" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="400" y="280" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Produce</text>
  
  <!-- Arrows: Source Connector to Broker -->
  <path d="M 290 335 L 400 370" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="335" y="355" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Produce</text>
  
  <!-- Arrows: Brokers to Consumers -->
  <path d="M 520 360 L 930 125" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="720" y="235" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Consume</text>
  <path d="M 660 360 L 930 185" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="780" y="280" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Consume</text>
  
  <!-- Arrows: Broker to Sink Connector -->
  <path d="M 680 380 L 680 450 L 290 395" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="500" y="425" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Consume</text>
  
  <!-- Arrows: Broker to Streams and back -->
  <path d="M 400 405 L 290 540" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="335" y="470" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Read/Write</text>
  <path d="M 170 570 L 170 640 L 600 640 L 600 405" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="380" y="660" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">Produce Results</text>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("kafka-architecture-overview-1.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated kafka-architecture-overview-1.svg")
