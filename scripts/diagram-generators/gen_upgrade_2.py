#!/usr/bin/env python3
"""
Generate virt-operator InstallStrategy Job Sequence Diagram
Notion Clean Style 4
"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 700">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>

<rect width="900" height="700" fill="{BG}"/>

<!-- Participants -->
<rect x="80" y="30" width="120" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="140" y="60" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">virt-operator</text>

<rect x="270" y="30" width="150" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="345" y="60" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">Kubernetes API</text>

<rect x="490" y="30" width="150" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="565" y="60" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">InstallStrategy Job</text>

<rect x="710" y="30" width="120" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="770" y="60" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT_PRIMARY}" text-anchor="middle">ConfigMap</text>

<!-- Lifelines -->
<line x1="140" y1="80" x2="140" y2="650" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<line x1="345" y1="80" x2="345" y2="650" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<line x1="565" y1="80" x2="565" y2="650" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>
<line x1="770" y1="80" x2="770" y2="650" stroke="{BOX_STROKE}" stroke-width="2" stroke-dasharray="5,5"/>

<!-- Message 1: 檢查 ConfigMap 是否存在 -->
<line x1="140" y1="120" x2="345" y2="120" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="240" y="110" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">檢查 ConfigMap 是否存在</text>

<!-- Message 2: 不存在 -->
<line x1="345" y1="160" x2="140" y2="160" stroke="{ARROW}" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
<text x="240" y="150" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">不存在</text>

<!-- Message 3: 建立 InstallStrategy Job -->
<line x1="140" y1="200" x2="345" y2="200" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="240" y="190" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">建立 InstallStrategy Job</text>

<!-- Message 4: 啟動 Job Pod -->
<line x1="345" y1="240" x2="565" y2="240" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="455" y="230" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">啟動 Job Pod</text>

<!-- Self-call: 載入新版元件 manifests -->
<rect x="565" y="270" width="20" height="40" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<line x1="565" y1="280" x2="615" y2="280" stroke="{ARROW}" stroke-width="2"/>
<line x1="615" y1="280" x2="615" y2="300" stroke="{ARROW}" stroke-width="2"/>
<line x1="615" y1="300" x2="585" y2="300" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="640" y="285" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">載入新版元件 manifests</text>

<!-- Message 5: 建立 InstallStrategy ConfigMap -->
<line x1="565" y1="340" x2="770" y2="340" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="670" y="330" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">建立 InstallStrategy ConfigMap</text>

<!-- Message 6: Job 完成 -->
<line x1="565" y1="380" x2="345" y2="380" stroke="{ARROW}" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
<text x="455" y="370" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">Job 完成（Succeeded）</text>

<!-- Message 7: ConfigMap 已就緒 -->
<line x1="345" y1="420" x2="140" y2="420" stroke="{ARROW}" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow)"/>
<text x="240" y="410" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" text-anchor="middle">ConfigMap 已就緒</text>

<!-- Self-call: 開始套用新資源 -->
<rect x="140" y="450" width="20" height="40" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<line x1="140" y1="460" x2="190" y2="460" stroke="{ARROW}" stroke-width="2"/>
<line x1="190" y1="460" x2="190" y2="480" stroke="{ARROW}" stroke-width="2"/>
<line x1="190" y1="480" x2="160" y2="480" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="210" y="465" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}">開始套用新資源</text>

</svg>'''

with open('kubevirt-upgrade-2.svg', 'w') as f:
    f.write(svg)

print("Generated: kubevirt-upgrade-2.svg")
