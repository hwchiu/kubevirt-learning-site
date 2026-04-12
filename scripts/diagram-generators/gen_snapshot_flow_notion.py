#!/usr/bin/env python3
"""Generate Notion Clean SVG for Snapshot Creation Flow"""

def generate_svg():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1300">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
    </marker>
    <style>
      text { 
        font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
        fill: #111827;
      }
      .box-title { font-size: 13px; font-weight: 500; fill: #111827; text-anchor: middle; }
      .box-subtitle { font-size: 12px; fill: #6b7280; text-anchor: middle; }
      .decision-title { font-size: 13px; font-weight: 500; fill: #111827; text-anchor: middle; }
      .edge-label { font-size: 12px; fill: #3b82f6; font-weight: 500; }
    </style>
  </defs>

  <!-- Background -->
  <rect width="1600" height="1300" fill="#ffffff"/>

  <!-- A: 使用者建立 VirtualMachineSnapshot -->
  <rect x="600" y="60" width="400" height="90" rx="35" fill="#4a9eff" stroke="#3b82f6" stroke-width="2"/>
  <text x="800" y="95" class="box-title" fill="#fff">使用者建立</text>
  <text x="800" y="115" class="box-title" fill="#fff">VirtualMachineSnapshot</text>

  <!-- B: VM 狀態? Decision -->
  <path d="M 800 260 L 950 360 L 800 460 L 650 360 Z" fill="#fff7ed" stroke="#fdba74" stroke-width="2"/>
  <text x="800" y="360" class="decision-title">VM 狀態?</text>

  <!-- C: 嘗試通知 guest agent fs-freeze -->
  <rect x="1000" y="320" width="300" height="80" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="1150" y="350" class="box-title">嘗試通知 guest agent</text>
  <text x="1150" y="370" class="box-title">fs-freeze</text>

  <!-- F: 直接進行快照 -->
  <rect x="200" y="320" width="250" height="80" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="325" y="365" class="box-title">直接進行快照</text>

  <!-- D: 所有 I/O 暫停 -->
  <rect x="1000" y="520" width="300" height="70" rx="35" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="1150" y="560" class="box-title">所有 I/O 暫停</text>

  <!-- E: 繼續但標記 -->
  <rect x="1350" y="500" width="230" height="110" rx="6" fill="#fef3c7" stroke="#fcd34d" stroke-width="2"/>
  <text x="1465" y="540" class="box-title">繼續但標記</text>
  <text x="1465" y="560" class="box-subtitle">NoGuestAgent/</text>
  <text x="1465" y="580" class="box-subtitle">QuiesceTimeout</text>

  <!-- G: 建立 VirtualMachineSnapshotContent -->
  <rect x="550" y="710" width="500" height="90" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="800" y="750" class="box-title">建立 VirtualMachineSnapshotContent</text>

  <!-- H: 逐一建立各 PVC 的 VolumeSnapshot -->
  <rect x="550" y="860" width="500" height="90" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="800" y="890" class="box-title">逐一建立各 PVC 的</text>
  <text x="800" y="910" class="box-title">VolumeSnapshot</text>

  <!-- I: 所有 VolumeSnapshot 建立成功? Decision -->
  <path d="M 800 1030 L 980 1130 L 800 1230 L 620 1130 Z" fill="#fff7ed" stroke="#fdba74" stroke-width="2"/>
  <text x="800" y="1120" class="decision-title">所有 VolumeSnapshot</text>
  <text x="800" y="1140" class="decision-title">建立成功?</text>

  <!-- J: 通知 guest agent fs-thaw 解凍 -->
  <rect x="1100" y="1080" width="300" height="100" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="1250" y="1115" class="box-title">通知 guest agent</text>
  <text x="1250" y="1135" class="box-title">fs-thaw 解凍</text>

  <!-- K: 標記快照失敗 -->
  <rect x="200" y="1070" width="300" height="120" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="2"/>
  <text x="350" y="1115" class="box-title">標記快照失敗</text>
  <text x="350" y="1140" class="box-title">清理已建立的快照</text>

  <!-- L: 更新 VirtualMachineSnapshot status -->
  <rect x="1100" y="1000" width="300" height="100" rx="6" fill="#27ae60" stroke="#10b981" stroke-width="2"/>
  <text x="1250" y="1035" class="box-title" fill="#fff">更新 VirtualMachineSnapshot</text>
  <text x="1250" y="1055" class="box-title" fill="#fff">status.readyToUse = true</text>

  <!-- M: 快照失敗 -->
  <rect x="200" y="990" width="300" height="100" rx="6" fill="#e74c3c" stroke="#dc2626" stroke-width="2"/>
  <text x="350" y="1030" class="box-title" fill="#fff">快照失敗</text>
  <text x="350" y="1050" class="box-title" fill="#fff">保留錯誤資訊</text>

  <!-- Arrows -->
  <!-- A to B -->
  <line x1="800" y1="150" x2="800" y2="260" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- B to C (Running) -->
  <line x1="950" y1="360" x2="1000" y2="360" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="970" y="350" class="edge-label">Running</text>

  <!-- B to F (Stopped) -->
  <line x1="650" y1="360" x2="450" y2="360" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="540" y="350" class="edge-label">Stopped</text>

  <!-- C to D (成功 freeze) -->
  <line x1="1150" y1="400" x2="1150" y2="520" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="1170" y="465" class="edge-label">成功 freeze</text>

  <!-- C to E (無 guest agent 或 timeout) -->
  <line x1="1300" y1="360" x2="1350" y2="555" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="1310" y="440" class="edge-label">無 guest agent</text>
  <text x="1310" y="455" class="edge-label">或 timeout</text>

  <!-- D to G -->
  <path d="M 1100 590 Q 1000 650 900 710" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>

  <!-- E to G -->
  <path d="M 1350 610 Q 1150 660 900 710" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>

  <!-- F to G -->
  <path d="M 400 400 Q 500 550 650 710" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>

  <!-- G to H -->
  <line x1="800" y1="800" x2="800" y2="860" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- H to I -->
  <line x1="800" y1="950" x2="800" y2="1030" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- I to J (是) -->
  <line x1="980" y1="1130" x2="1100" y2="1130" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="1030" y="1120" class="edge-label">是</text>

  <!-- I to K (否) -->
  <line x1="620" y1="1130" x2="500" y2="1130" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="550" y="1120" class="edge-label">否</text>

  <!-- J to L (moving J down from original design) -->
  <path d="M 1250 1080 Q 1250 1050 1250 1050" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>

  <!-- K to M -->
  <path d="M 350 1070 Q 350 1040 350 1040" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>

</svg>'''
    return svg

if __name__ == '__main__':
    with open('kubevirt-snapshot-flow-notion.svg', 'w') as f:
        f.write(generate_svg())
    print('Generated: kubevirt-snapshot-flow-notion.svg')
