#!/usr/bin/env python3
"""Diagram 1: VM 初始化完整流程 - flowchart TD with nested subgraphs."""
import os

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

OUT_DIR = "docs-site/public/diagrams/kubevirt"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1800, 1580

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def box(x,y,w,h,fill=BOX_FILL,stroke=BOX_STROKE,rx=8,sw=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def cont(x,y,w,h,label="",fill=CONTAINER_FILL,stroke=CONTAINER_STROKE):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="6,3"/>'
    if label:
        s += f'\n<text x="{x+12}" y="{y+22}" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_SECONDARY}">{esc(label)}</text>'
    return s

def oval(cx,cy,rw,rh,fill=ACCENT_FILL,stroke=ACCENT_STROKE):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rw}" ry="{rh}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def txt(x,y,s,fill=TEXT_PRIMARY,size=13,weight="normal",anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(s)}</text>'

def mtxt(x,cy,lines,fill=TEXT_PRIMARY,size=12,anchor="middle",lh=18):
    n=len(lines)
    sy=cy-(n*lh)/2+lh*0.75
    return '\n'.join(txt(x,sy+i*lh,ln,fill=fill,size=size,anchor=anchor) for i,ln in enumerate(lines))

def arrow(x1,y1,x2,y2,label="",dashed=False,color=ARROW):
    ds=' stroke-dasharray="5,3"' if dashed else ''
    s=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5"{ds} marker-end="url(#arrow)"/>'
    if label:
        mx=(x1+x2)//2; my=(y1+y2)//2-8
        s+=f'\n<text x="{mx}" y="{my}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_SECONDARY}">{esc(label)}</text>'
    return s

def path(d,label="",dashed=False,color=ARROW):
    ds=' stroke-dasharray="5,3"' if dashed else ''
    return f'<path d="{d}" stroke="{color}" stroke-width="1.5" fill="none"{ds} marker-end="url(#arrow)"/>'

items = []

# Arrow marker
defs = f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
</defs>'''

# Layout constants
CX = 900  # center x
BW = 200  # box width
BH = 56   # box height

# --- U (user oval) ---
items.append(oval(CX, 70, 90, 32, ACCENT_FILL, ACCENT_STROKE))
items.append(txt(CX, 74, "使用者", size=13, weight="600"))

# U → API
items.append(arrow(CX, 102, CX, 148, "kubectl apply VM YAML"))

# --- API box ---
items.append(box(CX-130, 150, 260, 52))
items.append(mtxt(CX, 176, ["Kubernetes API Server"], size=13, weight="600"))

# === Control Plane Container ===
items.append(cont(280, 230, 1240, 270, "控制平面 (Control Plane)"))

# API → VC (arrow going into container, left side)
items.append(arrow(700, 202, 700, 278, "VM 建立事件"))

# VC box
items.append(box(560, 280, 280, 56))
items.append(mtxt(700, 308, ["virt-controller", "VM Controller"], size=12, weight="600"))

# VC → API (back arrow, right side offset)
items.append(path(f"M 840 308 L 1000 308 L 1000 176 L 1030 176", label="", color=ARROW))
items.append(arrow(1030, 176, 1032, 176, color=ARROW))
items.append(txt(940, 300, "建立 VMI 物件", size=11, fill=TEXT_SECONDARY))

# API → VC2
items.append(arrow(1100, 202, 1100, 278, "VMI 建立事件"))

# VC2 box
items.append(box(960, 280, 280, 56))
items.append(mtxt(1100, 308, ["virt-controller", "VMI Controller"], size=12, weight="600"))

# VC2 → API back
items.append(path(f"M 1100 336 L 1100 380 L 1200 380 L 1200 176 L 1160 176", color=ARROW))
items.append(txt(1160, 370, "建立 virt-launcher Pod", size=11, fill=TEXT_SECONDARY))

# === Node Container ===
items.append(cont(240, 530, 1320, 940, "節點 (Node)"))

# API → VH
items.append(arrow(CX, 202, CX, 578, "Pod 排程完成"))
# Draw a long vertical arrow - let's make it go from API to VH
# Actually the arrow from API goes down past the control plane container
# Let's draw it on the right side
items.append(path(f"M 1180 176 L 1400 176 L 1400 560 L 1050 560", color=ARROW))
items.append(arrow(1050, 560, 1010, 578, color=ARROW))
items.append(txt(1380, 360, "Pod 排程完成", size=11, fill=TEXT_SECONDARY, anchor="end"))

# VH box
items.append(box(CX-130, 580, 260, 52))
items.append(mtxt(CX, 606, ["virt-handler"], size=13, weight="600"))

# VH → VL
items.append(arrow(CX, 632, CX, 678, "透過 gRPC SyncVMI 呼叫 virt-launcher"))

# VL box
items.append(box(CX-130, 680, 260, 52))
items.append(mtxt(CX, 706, ["virt-launcher"], size=13, weight="600"))

# VL → GCC
items.append(arrow(CX, 732, CX, 778))

# === Inner subgraph: virt-launcher init ===
items.append(cont(420, 760, 960, 660, "virt-launcher 初始化序列", fill="#fafbff", stroke="#a5b4fc"))

seq_nodes = [
    (800, ["generateConverterContext", "蒐集節點拓撲、設備資訊"]),
    (880, ["Convert", "VMI Spec → Domain XML"]),
    (960, ["preStartHook", "執行啟動前準備"]),
    (1040, ["生成 CloudInit ISO", "or Sysprep 磁碟"]),
    (1120, ["呼叫 Hook Sidecars"]),
    (1200, ["展開磁碟映像"]),
    (1280, ["libvirt.DomainDefine", "定義 Domain"]),
    (1360, ["libvirt.DomainCreate", "啟動 QEMU 行程"]),
]

for i,(y,lines) in enumerate(seq_nodes):
    items.append(box(CX-170, y-30, 340, 52))
    items.append(mtxt(CX, y-4, lines, size=12, weight="600" if i==0 else "normal"))
    if i < len(seq_nodes)-1:
        items.append(arrow(CX, y+22, CX, seq_nodes[i+1][0]-30))

# START → API (back arrow, curved)
items.append(path(f"M 1070 1356 L 1450 1356 L 1450 176 L 1032 176", color=ARROW))
items.append(txt(1460, 760, "VMI status: Running", size=11, fill=TEXT_SECONDARY, anchor="start"))


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{defs}
<rect width="{W}" height="{H}" fill="{BG}"/>
''' + '\n'.join(items) + '\n</svg>'

out = f"{OUT_DIR}/kubevirt-vm-init-overview.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
