#!/usr/bin/env python3
"""Generate Notion Clean SVG for Offline Snapshot Sequence"""

def generate_svg():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
    </marker>
    <marker id="arrow-dashed" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#6b7280"/>
    </marker>
    <style>
      text { 
        font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
        fill: #111827;
      }
      .participant-label { font-size: 14px; font-weight: 600; fill: #111827; text-anchor: middle; }
      .msg-label { font-size: 12px; fill: #111827; }
      .note-text { font-size: 12px; fill: #6b7280; }
    </style>
  </defs>

  <!-- Background -->
  <rect width="1200" height="900" fill="#ffffff"/>

  <!-- Participants -->
  <!-- 使用者 -->
  <rect x="100" y="50" width="150" height="60" rx="6" fill="#eff6ff" stroke="#bfdbfe" stroke-width="2"/>
  <text x="175" y="85" class="participant-label">使用者</text>
  <line x1="175" y1="110" x2="175" y2="850" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- KubeVirt Controller -->
  <rect x="400" y="50" width="220" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="510" y="85" class="participant-label">KubeVirt Controller</text>
  <line x1="510" y1="110" x2="510" y2="850" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- CSI Driver -->
  <rect x="770" y="50" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="860" y="85" class="participant-label">CSI Driver</text>
  <line x1="860" y1="110" x2="860" y2="850" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- Message 1: 停止 VM -->
  <line x1="175" y1="160" x2="500" y2="160" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="185" y="150" class="msg-label">停止 VM（或自動偵測到</text>
  <text x="185" y="165" class="msg-label">VM 已停止）</text>

  <!-- Message 2: 建立 VirtualMachineSnapshot CR -->
  <line x1="175" y1="220" x2="500" y2="220" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="185" y="210" class="msg-label">建立 VirtualMachineSnapshot CR</text>

  <!-- Note: VM 已停止，無需 freeze -->
  <rect x="370" y="260" width="280" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="510" y="290" class="note-text" text-anchor="middle">VM 已停止，無需 freeze</text>

  <!-- Message 3: 直接建立 VolumeSnapshot -->
  <line x1="510" y1="350" x2="850" y2="350" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="570" y="340" class="msg-label">直接建立 VolumeSnapshot</text>

  <!-- Message 4: 建立 PVC 快照 -->
  <rect x="750" y="390" width="220" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="860" y="420" class="note-text" text-anchor="middle">建立 PVC 快照</text>

  <!-- Message 5: VolumeSnapshot 就緒 (dashed) -->
  <line x1="860" y1="480" x2="520" y2="480" stroke="#6b7280" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrow-dashed)"/>
  <text x="620" y="470" class="msg-label">VolumeSnapshot 就緒</text>

  <!-- Message 6: VirtualMachineSnapshot ready (dashed) -->
  <line x1="510" y1="530" x2="185" y2="530" stroke="#6b7280" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrow-dashed)"/>
  <text x="220" y="520" class="msg-label">VirtualMachineSnapshot.status</text>
  <text x="220" y="535" class="msg-label">.readyToUse = true</text>

</svg>'''
    return svg

if __name__ == '__main__':
    with open('kubevirt-snapshot-offline-notion.svg', 'w') as f:
        f.write(generate_svg())
    print('Generated: kubevirt-snapshot-offline-notion.svg')
