#!/usr/bin/env python3
"""
Monitoring Linter Architecture - Notion Clean Style 4
"""

def generate_svg():
    # Notion Clean Style 4
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
    
    svg = f'''<svg viewBox="0 0 1400 500" xmlns="http://www.w3.org/2000/svg">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
  <style>
    .box {{ fill: {BOX_FILL}; stroke: {BOX_STROKE}; stroke-width: 1.5; }}
    .accent {{ fill: {ACCENT_FILL}; stroke: {ACCENT_STROKE}; stroke-width: 1.5; }}
    .container {{ fill: {CONTAINER_FILL}; stroke: {CONTAINER_STROKE}; stroke-width: 1.5; }}
    .text {{ fill: {TEXT_PRIMARY}; font-family: {FONT}; font-size: 14px; }}
    .text-sm {{ fill: {TEXT_SECONDARY}; font-family: {FONT}; font-size: 12px; }}
    .arrow {{ stroke: {ARROW}; stroke-width: 2; fill: none; marker-end: url(#arrow); }}
  </style>
</defs>
<rect width="1400" height="500" fill="{BG}"/>
'''
    
    # Boxes with proper spacing
    # Row 1: Input and initial processing
    boxes = [
        # A - JSON Input
        {"x": 20, "y": 100, "w": 180, "h": 80, "label": "JSON 輸入", "sub": "metricFamilies +<br/>recordingRules", "id": "A", "class": "accent"},
        # B - parseInput
        {"x": 240, "y": 120, "w": 120, "h": 50, "label": "parseInput", "sub": "", "id": "B", "class": "box"},
        # C - promlint.NewWith...
        {"x": 400, "y": 100, "w": 180, "h": 80, "label": "promlint.NewWith-", "sub": "MetricFamilies", "id": "C", "class": "box"},
        # D - promlint.Lint
        {"x": 620, "y": 100, "w": 150, "h": 80, "label": "promlint.Lint", "sub": "標準檢查", "id": "D", "class": "box"},
        # E - CustomMetrics...
        {"x": 810, "y": 100, "w": 180, "h": 80, "label": "CustomMetrics-", "sub": "Validation<br/>自定義指標規則", "id": "E", "class": "container"},
        # F - allowlist filter
        {"x": 400, "y": 280, "w": 160, "h": 60, "label": "allowlist 過濾", "sub": "", "id": "F", "class": "box"},
        # G - CustomRecording...
        {"x": 600, "y": 260, "w": 200, "h": 80, "label": "CustomRecording-", "sub": "RuleValidation<br/>自定義 Rule 規則", "id": "G", "class": "container"},
        # H - Output
        {"x": 1100, "y": 180, "w": 120, "h": 60, "label": "排序輸出", "sub": "", "id": "H", "class": "accent"},
    ]
    
    for box in boxes:
        svg += f'<rect class="{box["class"]}" x="{box["x"]}" y="{box["y"]}" width="{box["w"]}" height="{box["h"]}" rx="8"/>\n'
        
        # Main label
        text_y = box["y"] + 28
        if box["sub"]:
            text_y = box["y"] + 22
        
        svg += f'<text class="text" x="{box["x"] + box["w"]//2}" y="{text_y}" text-anchor="middle">{box["label"]}</text>\n'
        
        # Sub text (multi-line support)
        if box["sub"]:
            lines = box["sub"].split("<br/>")
            sub_y = box["y"] + 40
            for line in lines:
                svg += f'<text class="text-sm" x="{box["x"] + box["w"]//2}" y="{sub_y}" text-anchor="middle">{line}</text>\n'
                sub_y += 16
    
    # Arrows (from the flowchart)
    # A --> B
    svg += f'<line class="arrow" x1="200" y1="140" x2="235" y2="145"/>\n'
    # B --> C
    svg += f'<line class="arrow" x1="360" y1="145" x2="395" y2="140"/>\n'
    # C --> D
    svg += f'<line class="arrow" x1="580" y1="140" x2="615" y2="140"/>\n'
    # D --> E
    svg += f'<line class="arrow" x1="770" y1="140" x2="805" y2="140"/>\n'
    # B --> F (down then right)
    svg += f'<path class="arrow" d="M 300 170 L 300 310 L 395 310"/>\n'
    # F --> G
    svg += f'<line class="arrow" x1="560" y1="310" x2="595" y2="300"/>\n'
    # E --> H (down then right)
    svg += f'<path class="arrow" d="M 900 180 L 900 210 L 1095 210"/>\n'
    # G --> H (right then up)
    svg += f'<path class="arrow" d="M 800 300 L 1050 300 L 1050 210 L 1095 210"/>\n'
    
    svg += '</svg>'
    return svg

if __name__ == '__main__':
    svg_content = generate_svg()
    with open('monitoring-linter-arch.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("Generated monitoring-linter-arch.svg")
