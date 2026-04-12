#!/usr/bin/env python3
"""Generate Notion Clean SVG for Online Snapshot Sequence"""

def generate_svg():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1100">
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
  <rect width="1400" height="1100" fill="#ffffff"/>

  <!-- Participants -->
  <!-- 使用者 -->
  <rect x="100" y="50" width="150" height="60" rx="6" fill="#eff6ff" stroke="#bfdbfe" stroke-width="2"/>
  <text x="175" y="85" class="participant-label">使用者</text>
  <line x1="175" y1="110" x2="175" y2="1000" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- KubeVirt Controller -->
  <rect x="350" y="50" width="220" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="460" y="85" class="participant-label">KubeVirt Controller</text>
  <line x1="460" y1="110" x2="460" y2="1000" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- qemu-guest-agent -->
  <rect x="670" y="50" width="220" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="780" y="85" class="participant-label">qemu-guest-agent</text>
  <line x1="780" y1="110" x2="780" y2="1000" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- CSI Driver -->
  <rect x="990" y="50" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="1080" y="85" class="participant-label">CSI Driver</text>
  <line x1="1080" y1="110" x2="1080" y2="1000" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- Message 1: 建立 VirtualMachineSnapshot CR -->
  <line x1="175" y1="160" x2="450" y2="160" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="185" y="150" class="msg-label">建立 VirtualMachineSnapshot CR</text>

  <!-- Message 2: fs-freeze -->
  <line x1="460" y1="210" x2="770" y2="210" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="470" y="200" class="msg-label">fs-freeze（凍結 filesystem I/O）</text>

  <!-- Message 3: 等待應用層 I/O 完成 -->
  <rect x="660" y="250" width="240" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="780" y="270" class="note-text" text-anchor="middle">等待應用層 I/O 完成</text>

  <!-- Note: Filesystem 進入凍結狀態 -->
  <rect x="620" y="330" width="320" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="780" y="360" class="note-text" text-anchor="middle">Filesystem 進入凍結狀態</text>

  <!-- Message 4: 建立 VolumeSnapshot -->
  <line x1="460" y1="420" x2="1070" y2="420" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="650" y="410" class="msg-label">建立 VolumeSnapshot</text>

  <!-- Message 5: 建立 PVC 快照 -->
  <rect x="970" y="460" width="220" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="1080" y="490" class="note-text" text-anchor="middle">建立 PVC 快照</text>

  <!-- Message 6: fs-thaw -->
  <line x1="460" y1="550" x2="770" y2="550" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="470" y="540" class="msg-label">fs-thaw（解凍 filesystem）</text>

  <!-- Note: Filesystem 恢復正常 I/O -->
  <rect x="620" y="590" width="320" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="780" y="620" class="note-text" text-anchor="middle">Filesystem 恢復正常 I/O</text>

  <!-- Message 7: VolumeSnapshot 就緒 (dashed) -->
  <line x1="1080" y1="680" x2="470" y2="680" stroke="#6b7280" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrow-dashed)"/>
  <text x="650" y="670" class="msg-label">VolumeSnapshot 就緒</text>

  <!-- Message 8: VirtualMachineSnapshot ready (dashed) -->
  <line x1="460" y1="730" x2="185" y2="730" stroke="#6b7280" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrow-dashed)"/>
  <text x="220" y="720" class="msg-label">VirtualMachineSnapshot.status</text>
  <text x="220" y="735" class="msg-label">.readyToUse = true</text>

</svg>'''
    return svg

if __name__ == '__main__':
    with open('kubevirt-snapshot-online-notion.svg', 'w') as f:
        f.write(generate_svg())
    print('Generated: kubevirt-snapshot-online-notion.svg')
