#!/usr/bin/env python3
"""Generate Notion Clean SVG for Migration Architecture"""

def generate_svg():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 900">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
    </marker>
    <style>
      text { 
        font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
        fill: #111827;
      }
      .section-title { font-size: 16px; font-weight: 600; fill: #111827; }
      .box-title { font-size: 14px; font-weight: 500; fill: #111827; }
      .box-label { font-size: 13px; fill: #6b7280; }
      .edge-label { font-size: 12px; fill: #6b7280; }
    </style>
  </defs>

  <!-- Background -->
  <rect width="1400" height="900" fill="#ffffff"/>

  <!-- Source Node Container -->
  <rect x="50" y="50" width="400" height="300" rx="8" fill="#f0f4ff" stroke="#c7d2fe" stroke-width="2"/>
  <text x="250" y="85" text-anchor="middle" class="section-title">Source Node</text>

  <!-- virt-handler (Source) -->
  <rect x="80" y="110" width="160" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1.5"/>
  <text x="160" y="145" text-anchor="middle" class="box-title">virt-handler</text>

  <!-- virt-launcher Source -->
  <rect x="80" y="190" width="160" height="70" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1.5"/>
  <text x="160" y="220" text-anchor="middle" class="box-title">virt-launcher</text>
  <text x="160" y="240" text-anchor="middle" class="box-label">Source</text>

  <!-- QEMU/KVM Source -->
  <rect x="270" y="190" width="160" height="70" rx="6" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>
  <text x="350" y="215" text-anchor="middle" class="box-title">QEMU/KVM</text>
  <text x="350" y="235" text-anchor="middle" class="box-label">VM Running</text>

  <!-- virt-launcher to QEMU arrow -->
  <line x1="240" y1="225" x2="270" y2="225" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Target Node Container -->
  <rect x="550" y="50" width="400" height="300" rx="8" fill="#f0f4ff" stroke="#c7d2fe" stroke-width="2"/>
  <text x="750" y="85" text-anchor="middle" class="section-title">Target Node</text>

  <!-- virt-handler (Target) -->
  <rect x="580" y="110" width="160" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1.5"/>
  <text x="660" y="145" text-anchor="middle" class="box-title">virt-handler</text>

  <!-- virt-launcher Target -->
  <rect x="580" y="190" width="160" height="70" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1.5"/>
  <text x="660" y="220" text-anchor="middle" class="box-title">virt-launcher</text>
  <text x="660" y="240" text-anchor="middle" class="box-label">Target</text>

  <!-- QEMU/KVM Target -->
  <rect x="770" y="190" width="160" height="70" rx="6" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>
  <text x="850" y="215" text-anchor="middle" class="box-title">QEMU/KVM</text>
  <text x="850" y="235" text-anchor="middle" class="box-label">VM Receiving</text>

  <!-- virt-launcher to QEMU arrow (Target) -->
  <line x1="740" y1="225" x2="770" y2="225" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Control Plane Container -->
  <rect x="350" y="420" width="700" height="280" rx="8" fill="#f0f4ff" stroke="#c7d2fe" stroke-width="2"/>
  <text x="700" y="455" text-anchor="middle" class="section-title">Control Plane</text>

  <!-- virt-controller -->
  <rect x="400" y="480" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1.5"/>
  <text x="490" y="515" text-anchor="middle" class="box-title">virt-controller</text>

  <!-- kube-apiserver -->
  <rect x="620" y="480" width="180" height="60" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1.5"/>
  <text x="710" y="515" text-anchor="middle" class="box-title">kube-apiserver</text>

  <!-- VirtualMachineInstanceMigration CR -->
  <rect x="840" y="480" width="180" height="80" rx="6" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1.5"/>
  <text x="930" y="505" text-anchor="middle" class="box-title">VirtualMachineInstance</text>
  <text x="930" y="525" text-anchor="middle" class="box-title">Migration CR</text>

  <!-- VC to virt-launcher Target (建立目標 pod) -->
  <path d="M 490 480 Q 490 400 660 290" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="520" y="380" class="edge-label">建立目標 pod</text>

  <!-- VC to VMIM (更新 migration 狀態) -->
  <line x1="580" y1="510" x2="840" y2="510" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="670" y="502" class="edge-label">更新 migration 狀態</text>

  <!-- virt-handler Source to QEMU Source (監控來源 VMI) -->
  <path d="M 160 170 Q 160 180 240 210" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="120" y="185" class="edge-label">監控來源 VMI</text>

  <!-- virt-handler Target to QEMU Target (監控目標 VMI) -->
  <path d="M 660 170 Q 660 180 740 210" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="680" y="185" class="edge-label">監控目標 VMI</text>

  <!-- virt-handler Source to QEMU Source (通知開始 migration) -->
  <path d="M 160 170 Q 200 190 350 190" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="200" y="175" class="edge-label">通知開始 migration</text>

  <!-- QEMU Source to QEMU Target (Pre-copy 記憶體傳輸) -->
  <path d="M 430 220 Q 500 220 770 220" stroke="#3b82f6" stroke-width="3" fill="none" marker-end="url(#arrow)" stroke-dasharray="8,4"/>
  <text x="500" y="210" text-anchor="middle" class="edge-label">Pre-copy 記憶體傳輸</text>
  <text x="500" y="225" text-anchor="middle" class="edge-label">Migration Network</text>

  <!-- virt-handler Source to API (回報狀態) -->
  <path d="M 240 140 Q 300 350 620 480" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="340" y="300" class="edge-label">回報狀態</text>

  <!-- virt-handler Target to API (回報狀態) -->
  <path d="M 660 170 Q 680 350 710 480" stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
  <text x="720" y="300" class="edge-label">回報狀態</text>

</svg>'''
    return svg

if __name__ == '__main__':
    with open('kubevirt-migration-arch-notion.svg', 'w') as f:
        f.write(generate_svg())
    print('Generated: kubevirt-migration-arch-notion.svg')
