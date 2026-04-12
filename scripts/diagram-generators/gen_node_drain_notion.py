#!/usr/bin/env python3
"""Generate Notion Clean SVG for Node Drain Sequence"""

def generate_svg():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1300">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
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
  <rect width="1400" height="1300" fill="#ffffff"/>

  <!-- Participants -->
  <!-- 管理員 -->
  <rect x="60" y="50" width="150" height="60" rx="6" fill="#eff6ff" stroke="#bfdbfe" stroke-width="2"/>
  <text x="135" y="85" class="participant-label">管理員</text>
  <line x1="135" y1="110" x2="135" y2="1200" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- Kubernetes API -->
  <rect x="290" y="50" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="380" y="85" class="participant-label">Kubernetes API</text>
  <line x1="380" y1="110" x2="380" y2="1200" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- virt-controller -->
  <rect x="550" y="50" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="640" y="85" class="participant-label">virt-controller</text>
  <line x1="640" y1="110" x2="640" y2="1200" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- virt-handler -->
  <rect x="810" y="50" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="900" y="85" class="participant-label">virt-handler</text>
  <line x1="900" y1="110" x2="900" y2="1200" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- virt-launcher -->
  <rect x="1070" y="50" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="2"/>
  <text x="1160" y="85" class="participant-label">virt-launcher</text>
  <line x1="1160" y1="110" x2="1160" y2="1200" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- Message 1: kubectl drain -->
  <line x1="135" y1="150" x2="370" y2="150" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="145" y="140" class="msg-label">kubectl drain node-1</text>
  <text x="145" y="155" class="msg-label">--ignore-daemonsets</text>

  <!-- Message 2: 為節點加上 NoSchedule taint -->
  <rect x="270" y="180" width="220" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="380" y="200" class="note-text" text-anchor="middle">為節點加上 NoSchedule</text>
  <text x="380" y="220" class="note-text" text-anchor="middle">taint</text>

  <!-- Message 3: 驅逐節點上的 pods -->
  <rect x="270" y="250" width="220" height="50" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="380" y="270" class="note-text" text-anchor="middle">驅逐節點上的 pods</text>

  <!-- Message 4: VMI eviction 請求 -->
  <line x1="380" y1="330" x2="630" y2="330" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="390" y="320" class="msg-label">VMI eviction 請求</text>

  <!-- Message 5: 建立 VirtualMachineInstanceMigration CR -->
  <line x1="640" y1="370" x2="390" y2="370" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="420" y="360" class="msg-label">建立 VirtualMachineInstance</text>
  <text x="420" y="375" class="msg-label">Migration CR</text>

  <!-- Message 6: 在目標節點建立新的 virt-launcher pod -->
  <line x1="640" y1="420" x2="390" y2="420" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="410" y="410" class="msg-label">在目標節點建立新的</text>
  <text x="410" y="425" class="msg-label">virt-launcher pod</text>

  <!-- Message 7: 通知 virt-handler 開始 migration -->
  <line x1="380" y1="470" x2="890" y2="470" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="500" y="460" class="msg-label">通知 virt-handler 開始 migration</text>

  <!-- Message 8: 啟動 QEMU migration -->
  <line x1="900" y1="510" x2="1150" y2="510" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="910" y="500" class="msg-label">啟動 QEMU migration</text>

  <!-- Note: Pre-copy 記憶體傳輸中... -->
  <rect x="1040" y="550" width="240" height="80" rx="4" fill="#fef3c7" stroke="#fcd34d" stroke-width="1"/>
  <text x="1160" y="580" class="note-text" text-anchor="middle">Pre-copy 記憶體</text>
  <text x="1160" y="600" class="note-text" text-anchor="middle">傳輸中...</text>

  <!-- Message 9: Migration Succeeded -->
  <line x1="1160" y1="670" x2="390" y2="670" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="8,4"/>
  <text x="650" y="660" class="msg-label">Migration Succeeded</text>

  <!-- Message 10: drain 完成 -->
  <line x1="380" y1="710" x2="145" y2="710" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="220" y="700" class="msg-label">drain 完成</text>

</svg>'''
    return svg

if __name__ == '__main__':
    with open('kubevirt-node-drain-notion.svg', 'w') as f:
        f.write(generate_svg())
    print('Generated: kubevirt-node-drain-notion.svg')
