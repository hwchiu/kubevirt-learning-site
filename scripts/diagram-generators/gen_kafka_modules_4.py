#!/usr/bin/env python3
"""Generate Raft State Machine diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 900">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1400" height="900" fill="{BG}"/>
  
  <!-- Initial state -->
  <circle cx="100" cy="100" r="12" fill="{TEXT_PRIMARY}"/>
  <circle cx="100" cy="100" r="18" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="2"/>
  
  <!-- Unattached -->
  <rect x="200" y="50" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2" rx="8"/>
  <text x="300" y="95" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Unattached</text>
  
  <!-- Candidate -->
  <rect x="600" y="50" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2" rx="8"/>
  <text x="700" y="95" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Candidate</text>
  
  <!-- Leader -->
  <rect x="600" y="300" width="200" height="80" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2" rx="8"/>
  <text x="700" y="345" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Leader</text>
  
  <!-- Follower -->
  <rect x="200" y="300" width="200" height="80" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2" rx="8"/>
  <text x="300" y="345" font-family="{FONT}" font-size="16" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Follower</text>
  
  <!-- Initial -> Unattached -->
  <path d="M 118 100 L 200 90" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="145" y="85" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">啟動</text>
  
  <!-- Unattached -> Candidate -->
  <path d="M 400 90 L 600 90" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="480" y="80" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Election</text>
  <text x="480" y="95" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Timeout</text>
  
  <!-- Candidate -> Leader -->
  <path d="M 700 130 L 700 300" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="720" y="205" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">獲得多數票</text>
  <text x="720" y="220" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">（Quorum）</text>
  
  <!-- Candidate -> Follower -->
  <path d="M 600 110 L 400 320" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="450" y="195" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">收到更高 Term 的</text>
  <text x="450" y="210" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">選票或 Heartbeat</text>
  
  <!-- Candidate -> Candidate (self loop) -->
  <path d="M 700 50 Q 850 -30 800 90" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="820" y="30" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">選舉超時</text>
  <text x="820" y="45" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">重試</text>
  
  <!-- Leader -> Follower -->
  <path d="M 600 340 L 400 340" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="460" y="330" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">發現更高 Term</text>
  
  <!-- Follower -> Candidate -->
  <path d="M 300 300 L 650 130" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="420" y="200" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Election Timeout</text>
  <text x="420" y="215" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">（未收到 Heartbeat）</text>
  
  <!-- Leader -> Leader (self loop) -->
  <path d="M 800 340 Q 950 420 700 380" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="850" y="385" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">持續發送</text>
  <text x="850" y="400" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Heartbeat</text>
  
  <!-- Follower -> Follower (self loop) -->
  <path d="M 200 340 Q 50 420 300 380" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="80" y="380" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">接收 Leader</text>
  <text x="80" y="395" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Heartbeat /</text>
  <text x="80" y="410" font-family="{FONT}" font-size="13" fill="{TEXT_SECONDARY}">Log 複製</text>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("kafka-modules-raft-4.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated kafka-modules-raft-4.svg")
