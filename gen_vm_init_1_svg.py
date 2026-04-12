#!/usr/bin/env python3
import math

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1600, 900

def box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, rx=8, font_size=13):
    lines = text.split('\n')
    n = len(lines)
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    total_h = n * (font_size + 4)
    start_y = y + h/2 - total_h/2 + font_size
    for i, line in enumerate(lines):
        svg += f'<text x="{x+w/2}" y="{start_y + i*(font_size+4)}" font-family="{FONT}" font-size="{font_size}" fill="{TEXT_PRIMARY}" text-anchor="middle">{line}</text>'
    return svg

def rounded_box(x, y, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, font_size=13):
    return box(x, y, w, h, text, fill, stroke, rx=h//2, font_size=font_size)

def arrow(x1, y1, x2, y2, label=""):
    mid_x = (x1+x2)/2
    mid_y = (y1+y2)/2
    svg = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        svg += f'<text x="{mid_x+5}" y="{mid_y-5}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{label}</text>'
    return svg

def arrow_h(x1, y, x2, label="", label_above=True):
    svg = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        ly = y - 8 if label_above else y + 14
        svg += f'<text x="{(x1+x2)/2}" y="{ly}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">{label}</text>'
    return svg

def arrow_v(x, y1, y2, label="", label_right=True):
    svg = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ARROW}" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        lx = x + 6 if label_right else x - 6
        anchor = "start" if label_right else "end"
        svg += f'<text x="{lx}" y="{(y1+y2)/2+4}" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="{anchor}">{label}</text>'
    return svg

def container(x, y, w, h, title, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE):
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="6,3"/>'
    svg += f'<text x="{x+12}" y="{y+18}" font-family="{FONT}" font-size="12" fill="{TEXT_SECONDARY}" font-weight="600">{title}</text>'
    return svg

svg_parts = []
svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg_parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg_parts.append(f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>''')

# Title
svg_parts.append(f'<text x="{W//2}" y="38" font-family="{FONT}" font-size="20" font-weight="700" fill="{TEXT_PRIMARY}" text-anchor="middle">VM 初始化完整流程</text>')

# User node (rounded)
svg_parts.append(rounded_box(680, 65, 240, 40, '使用者 (kubectl apply VM YAML)', fill="#dbeafe", stroke=ARROW))
# API Server
svg_parts.append(box(680, 145, 240, 44, 'Kubernetes API Server', fill=BOX_FILL, stroke=BOX_STROKE))

svg_parts.append(arrow_v(800, 105, 145, 'kubectl apply VM YAML'))

# Control Plane container
svg_parts.append(container(80, 205, 720, 200, '控制平面 (Control Plane)'))

# virt-controller VM Controller
svg_parts.append(box(100, 235, 260, 44, 'virt-controller\nVM Controller', fill=BOX_FILL))
# virt-controller VMI Controller
svg_parts.append(box(460, 235, 260, 44, 'virt-controller\nVMI Controller', fill=BOX_FILL))

# VM create event from API to VC
svg_parts.append(arrow(800, 189, 360, 257, ''))
svg_parts.append(f'<text x="580" y="222" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">VM 建立事件</text>')

# VC creates VMI
svg_parts.append(arrow(360, 257, 800, 210, ''))
svg_parts.append(f'<text x="590" y="245" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle">建立 VMI 物件</text>')

# VMI create event
svg_parts.append(arrow(800, 220, 720, 257, ''))
svg_parts.append(f'<text x="790" y="242" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="middle"> VMI 建立事件</text>')

# VC2 creates pod
svg_parts.append(arrow(720, 257, 800, 240, ''))
svg_parts.append(f'<text x="780" y="260" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}" text-anchor="start"> 建立 virt-launcher Pod</text>')

# Inter-control-plane arrows
svg_parts.append(arrow_h(360, 257, 460, 'VMI 建立事件'))

# Node container
svg_parts.append(container(80, 425, 1420, 420, '節點 (Node)'))

# virt-handler
svg_parts.append(box(100, 460, 200, 44, 'virt-handler'))
# virt-launcher
svg_parts.append(box(380, 460, 200, 44, 'virt-launcher'))

svg_parts.append(arrow(800, 265, 200, 480, ''))
svg_parts.append(f'<text x="420" y="380" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">Pod 排程完成</text>')
svg_parts.append(arrow_h(300, 482, 380, 'gRPC SyncVMI'))

# virt-launcher init sequence container
svg_parts.append(container(620, 440, 860, 380, 'virt-launcher 初始化序列'))

bw, bh = 240, 40
bx = 680
steps = [
    ('generateConverterContext\n蒐集節點拓撲、設備資訊', 470),
    ('Convert\nVMI Spec → Domain XML', 530),
    ('preStartHook\n執行啟動前準備', 590),
    ('生成 CloudInit ISO\nor Sysprep 磁碟', 650),
    ('呼叫 Hook Sidecars', 700),
    ('展開磁碟映像', 750),
    ('libvirt.DomainDefine\n定義 Domain', 650+160),
    ('libvirt.DomainCreate\n啟動 QEMU 行程', 650+210),
]

# Draw chain boxes
step_data = [
    ('generateConverterContext\n蒐集節點拓撲、設備資訊', 680, 470),
    ('Convert\nVMI Spec → Domain XML', 980, 470),
    ('preStartHook\n執行啟動前準備', 680, 560),
    ('生成 CloudInit ISO\nor Sysprep 磁碟', 680, 630),
    ('呼叫 Hook Sidecars', 680, 690),
    ('展開磁碟映像', 680, 740),
    ('libvirt.DomainDefine\n定義 Domain', 980, 630),
    ('libvirt.DomainCreate\n啟動 QEMU 行程', 980, 700),
]

# Row 1: GCC -> CONV -> PSH
gcc_x, gcc_y = 660, 470
conv_x, conv_y = 960, 470
psh_x, psh_y = 1260, 470

svg_parts.append(box(gcc_x, gcc_y, 260, 44, 'generateConverterContext\n蒐集節點拓撲、設備資訊'))
svg_parts.append(box(conv_x, conv_y, 260, 44, 'Convert\nVMI Spec → Domain XML'))
svg_parts.append(box(psh_x, psh_y, 200, 44, 'preStartHook\n執行啟動前準備'))

svg_parts.append(arrow_h(gcc_x+260, gcc_y+22, conv_x))
svg_parts.append(arrow_h(conv_x+260, conv_y+22, psh_x))

# Row 2: CloudInit -> Hooks -> Expand
ci_x, ci_y = 660, 565
hooks_x, hooks_y = 960, 565
expand_x, expand_y = 1260, 565

svg_parts.append(box(ci_x, ci_y, 260, 44, '生成 CloudInit ISO\nor Sysprep 磁碟'))
svg_parts.append(box(hooks_x, hooks_y, 260, 44, '呼叫 Hook Sidecars'))
svg_parts.append(box(expand_x, expand_y, 200, 44, '展開磁碟映像'))

svg_parts.append(arrow_v(psh_x+100, psh_y+44, ci_y))
svg_parts.append(arrow_h(ci_x+260, ci_y+22, hooks_x))
svg_parts.append(arrow_h(hooks_x+260, hooks_y+22, expand_x))

# Row 3: Define -> Create -> API update
define_x, define_y = 760, 665
start_x, start_y = 1060, 665

svg_parts.append(box(define_x, define_y, 260, 44, 'libvirt.DomainDefine\n定義 Domain'))
svg_parts.append(box(start_x, start_y, 260, 44, 'libvirt.DomainCreate\n啟動 QEMU 行程'))

svg_parts.append(arrow_v(expand_x+100, expand_y+44, define_y))
svg_parts.append(arrow_h(define_x+260, define_y+22, start_x))

# Arrow from virt-launcher to init sequence
svg_parts.append(arrow_h(580, 482, gcc_x, 'virt-launcher 初始化'))

# Final status update
svg_parts.append(arrow(start_x+130, start_y+44, 800, H-50, ''))
svg_parts.append(box(660, H-75, 280, 40, 'VMI status: Running → API Server', fill="#dcfce7", stroke="#86efac"))

svg_parts.append('</svg>')

out_path = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-vm-init-1.svg'
with open(out_path, 'w') as f:
    f.write('\n'.join(svg_parts))
print(f'Written: {out_path}')
