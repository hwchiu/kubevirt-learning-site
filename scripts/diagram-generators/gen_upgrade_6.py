#!/usr/bin/env python3
"""
Generate Upgrade Troubleshooting Flowchart
Notion Clean Style 4
"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
ACCENT_FILL = "#eff6ff"
ACCENT_STROKE = "#bfdbfe"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 950">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>

<rect width="1100" height="950" fill="{BG}"/>

<!-- Start -->
<rect x="400" y="20" width="180" height="50" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="490" y="50" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" text-anchor="middle">升級似乎卡住</text>

<!-- Decision 1 -->
<line x1="490" y1="70" x2="490" y2="110" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<path d="M 490 110 L 610 160 L 490 210 L 370 160 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="490" y="155" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">檢查 KubeVirt CR</text>
<text x="490" y="170" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">Progressing condition</text>

<!-- Left: True > 30min -->
<line x1="370" y1="160" x2="250" y2="160" stroke="{ARROW}" stroke-width="2"/>
<line x1="250" y1="160" x2="250" y2="230" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="300" y="150" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">True 超過 30 分鐘</text>

<path d="M 250 230 L 350 280 L 250 330 L 150 280 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="250" y="275" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">检查 InstallStrategy</text>
<text x="250" y="290" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">Job 狀態</text>

<!-- Job Failed -->
<line x1="150" y1="280" x2="80" y2="280" stroke="{ARROW}" stroke-width="2"/>
<line x1="80" y1="280" x2="80" y2="360" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="90" y="270" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">Job 失敗</text>
<rect x="20" y="360" width="120" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="80" y="380" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">查看 Job logs</text>
<text x="80" y="400" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">修復映像拉取問題</text>

<!-- Job Success -->
<line x1="350" y1="280" x2="420" y2="280" stroke="{ARROW}" stroke-width="2"/>
<line x1="420" y1="280" x2="420" y2="350" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="365" y="270" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">Job 成功</text>
<path d="M 420 350 L 520 400 L 420 450 L 320 400 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="420" y="405" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">檢查元件 Pod</text>

<!-- CrashLoop -->
<line x1="320" y1="400" x2="230" y2="400" stroke="{ARROW}" stroke-width="2"/>
<line x1="230" y1="400" x2="230" y2="500" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="260" y="390" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">有 CrashLoop</text>
<rect x="160" y="500" width="140" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="230" y="520" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">查看 Pod logs</text>
<text x="230" y="540" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">診斷元件問題</text>

<!-- All Running -->
<line x1="520" y1="400" x2="610" y2="400" stroke="{ARROW}" stroke-width="2"/>
<line x1="610" y1="400" x2="610" y2="470" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="545" y="390" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">全部 Running</text>

<path d="M 610 470 L 710 520 L 610 570 L 510 520 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="610" y="525" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">检查 VMIM 狀態</text>

<!-- Failed migration -->
<line x1="510" y1="520" x2="420" y2="520" stroke="{ARROW}" stroke-width="2"/>
<line x1="420" y1="520" x2="420" y2="620" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="450" y="510" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">有失敗遷移</text>
<rect x="350" y="620" width="140" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="420" y="640" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">清理失敗 VMIM</text>
<text x="420" y="660" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">等待重試</text>

<!-- No failed migration -->
<line x1="710" y1="520" x2="800" y2="520" stroke="{ARROW}" stroke-width="2"/>
<line x1="800" y1="520" x2="800" y2="740" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="730" y="510" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">無失敗遷移</text>
<rect x="700" y="740" width="200" height="80" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="800" y="765" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">檢查 virt-controller logs</text>
<text x="800" y="785" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">尋找 workload-updater</text>
<text x="800" y="805" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">日誌</text>

<!-- Right: False -->
<line x1="610" y1="160" x2="730" y2="160" stroke="{ARROW}" stroke-width="2"/>
<line x1="730" y1="160" x2="730" y2="230" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="655" y="150" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">False</text>

<path d="M 730 230 L 830 280 L 730 330 L 630 280 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="730" y="275" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">outdatedVMI</text>
<text x="730" y="290" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">計數器是否遞減？</text>

<!-- Yes: in progress -->
<line x1="830" y1="280" x2="930" y2="280" stroke="{ARROW}" stroke-width="2"/>
<line x1="930" y1="280" x2="930" y2="360" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="855" y="270" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">是</text>
<rect x="860" y="360" width="140" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="930" y="380" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">升級進行中</text>
<text x="930" y="400" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">繼續等待</text>

<!-- No -->
<line x1="730" y1="330" x2="730" y2="400" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="745" y="365" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">否</text>

<path d="M 730 400 L 830 450 L 730 500 L 630 450 Z" fill="{ACCENT_FILL}" stroke="{ACCENT_STROKE}" stroke-width="2"/>
<text x="730" y="445" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">workloadUpdateMethods</text>
<text x="730" y="460" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">是否為空？</text>

<!-- Empty: manual -->
<line x1="830" y1="450" x2="920" y2="450" stroke="{ARROW}" stroke-width="2"/>
<line x1="920" y1="450" x2="920" y2="620" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>
<text x="855" y="440" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">是</text>
<rect x="840" y="620" width="160" height="60" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="2"/>
<text x="920" y="640" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}" text-anchor="middle">手動觸發 VMI 遷移</text>

<!-- Not empty: check logs -->
<line x1="730" y1="500" x2="730" y2="740" stroke="{ARROW}" stroke-width="2"/>
<line x1="730" y1="740" x2="700" y2="740" stroke="{ARROW}" stroke-width="2"/>
<text x="745" y="620" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">否</text>

</svg>'''

with open('kubevirt-upgrade-6.svg', 'w') as f:
    f.write(svg)

print("Generated: kubevirt-upgrade-6.svg")
