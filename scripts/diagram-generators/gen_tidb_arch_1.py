#!/usr/bin/env python3
"""Generate TiDB Server Internal Architecture diagram (Notion Clean Style 4)"""

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
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1100">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
    </marker>
  </defs>
  
  <rect width="1000" height="1100" fill="{BG}"/>
  
  <!-- MySQL Client -->
  <rect x="350" y="30" width="300" height="70" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="500" y="60" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">MySQL Client</text>
  <text x="500" y="80" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">(TCP :4000)</text>
  
  <!-- pkg/server -->
  <rect x="300" y="140" width="400" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="500" y="165" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/server</text>
  <text x="500" y="185" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">連線管理 / 協定解析</text>
  
  <!-- pkg/session -->
  <rect x="300" y="250" width="400" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="500" y="275" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/session</text>
  <text x="500" y="295" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">Session 管理 / 交易協調</text>
  
  <!-- pkg/parser -->
  <rect x="250" y="360" width="500" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="500" y="385" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/parser</text>
  <text x="500" y="405" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">SQL 詞法 + 語法解析 / 生成 AST</text>
  
  <!-- pkg/planner -->
  <rect x="250" y="470" width="500" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="500" y="495" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/planner</text>
  <text x="500" y="515" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">邏輯計劃生成 / 語意分析</text>
  
  <!-- pkg/planner/core -->
  <rect x="200" y="580" width="600" height="70" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="500" y="605" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/planner/core</text>
  <text x="500" y="625" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">查詢優化器 / 邏輯 → 物理計劃</text>
  
  <!-- Query type decision -->
  <rect x="375" y="690" width="250" height="60" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2" rx="8"/>
  <text x="500" y="725" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">查詢類型</text>
  
  <!-- pkg/executor (left path) -->
  <rect x="50" y="800" width="350" height="90" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="225" y="825" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">pkg/executor</text>
  <text x="225" y="845" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">在 TiDB 本地執行</text>
  <text x="225" y="862" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">推送計算至 TiKV Coprocessor</text>
  
  <!-- MPP planner (right path) -->
  <rect x="600" y="800" width="350" height="90" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5" rx="6"/>
  <text x="775" y="825" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">MPP 計劃生成</text>
  <text x="775" y="850" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">推送至 TiFlash</text>
  
  <!-- TiKV -->
  <rect x="50" y="940" width="200" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="150" y="970" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">TiKV</text>
  <text x="150" y="990" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">行式儲存 /</text>
  <text x="150" y="1005" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">Coprocessor</text>
  
  <!-- TiFlash -->
  <rect x="750" y="940" width="200" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="850" y="970" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">TiFlash</text>
  <text x="850" y="990" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">列式儲存 / MPP</text>
  
  <!-- PD -->
  <rect x="400" y="940" width="200" height="80" fill="{CONTAINER_FILL}" stroke="{CONTAINER_STROKE}" stroke-width="2" rx="8"/>
  <text x="500" y="970" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">PD</text>
  <text x="500" y="990" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">TSO / Region 路由</text>
  
  <!-- Arrows -->
  <path d="M 500 100 L 500 140" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="520" y="125" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">MySQL 協定</text>
  
  <path d="M 500 210 L 500 250" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 500 320 L 500 360" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 500 430 L 500 470" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 500 540 L 500 580" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <path d="M 500 650 L 500 690" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  
  <!-- Branch: OLTP path -->
  <path d="M 400 720 L 225 800" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="280" y="750" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">OLTP (Point/Batch)</text>
  
  <!-- Branch: OLAP/MPP path -->
  <path d="M 600 720 L 775 800" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="650" y="750" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">OLAP / MPP</text>
  
  <!-- Executor to TiKV -->
  <path d="M 150 890 L 150 940" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="170" y="920" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">KV RPC (gRPC)</text>
  
  <!-- MPP to TiFlash -->
  <path d="M 850 890 L 850 940" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="870" y="920" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">MPP gRPC</text>
  
  <!-- TiKV to PD -->
  <path d="M 250 980 L 400 980" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  
  <!-- TiFlash to PD -->
  <path d="M 750 980 L 600 980" stroke="{ARROW}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
</svg>'''
    
    return svg

if __name__ == "__main__":
    svg_content = generate_svg()
    with open("tidb-architecture-server-1.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ Generated tidb-architecture-server-1.svg")
