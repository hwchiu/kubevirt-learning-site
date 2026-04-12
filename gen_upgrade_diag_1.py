#!/usr/bin/env python3
"""Diagram 1: kubevirt-upgrade-flow.svg — KubeVirt 升級流程三階段 (Flowchart TD)"""
import os

OUT_DIR = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/"
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BOX_FILL = "#f9fafb"; BOX_STROKE = "#e5e7eb"
CONT_FILL = "#f0f4ff"; CONT_STROKE = "#c7d2fe"
ARROW = "#3b82f6"; TP = "#111827"; TS = "#6b7280"
W, H = 1800, 1800

ARROW_DEFS = '''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#3b82f6"/>
  </marker>
</defs>'''

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def mtext(cx, cy, text, color=None, size=14, anchor="middle", dy=0):
    c = color or TP
    lines = text.split('\n')
    lh = size + 4
    total = len(lines) * lh
    sy = cy - total/2 + lh/2 + dy
    out = ''
    for i, ln in enumerate(lines):
        out += f'<text x="{cx}" y="{sy+i*lh}" text-anchor="{anchor}" dominant-baseline="middle" fill="{c}" font-size="{size}" font-family="{FONT}">{esc(ln)}</text>\n'
    return out

def rect_node(cx, cy, w, h, text, fill=BOX_FILL, stroke=BOX_STROKE, tc=None, rx=8):
    x, y = cx-w/2, cy-h/2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
            + mtext(cx, cy, text, tc))

def oval_node(cx, cy, w, h, text, fill="#4A90D9", tc="#fff"):
    x, y = cx-w/2, cy-h/2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="30" fill="{fill}" stroke="{fill}" stroke-width="1.5"/>\n'
            + mtext(cx, cy, text, tc, size=15))

def diamond(cx, cy, w, h, text):
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    return (f'<polygon points="{pts}" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>\n'
            + mtext(cx, cy, text, size=13))

def container(x, y, w, h, label):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{CONT_FILL}" stroke="{CONT_STROKE}" stroke-width="2"/>\n'
            f'<text x="{x+16}" y="{y+22}" fill="#4338ca" font-size="13" font-weight="600" font-family="{FONT}">{esc(label)}</text>\n')

def line(x1,y1,x2,y2, dash="", label="", lx=None, ly=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ARROW}" stroke-width="1.5"{da} marker-end="url(#arrow)"/>\n'
    if label:
        mx = lx if lx is not None else (x1+x2)/2
        my = ly if ly is not None else (y1+y2)/2
        s += f'<text x="{mx+4}" y="{my-4}" fill="{TS}" font-size="12" font-family="{FONT}">{esc(label)}</text>\n'
    return s

def path(d, label="", lx=None, ly=None):
    s = f'<path d="{d}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>\n'
    if label and lx is not None:
        s += f'<text x="{lx}" y="{ly}" fill="{TS}" font-size="12" font-family="{FONT}">{esc(label)}</text>\n'
    return s

# ── Layout coordinates ──────────────────────────────────────────────
NW = 380; NH = 60   # standard node
WN = NW; WH = 68    # wide 2-line node

# A - oval
A = (900, 60)

# Phase 1: y=120..490
P1 = (430, 115, 940, 390)   # x,y,w,h
B = (900, 205); C = (900, 305); D = (900, 415)

# Phase 2: y=530..930
P2 = (70, 525, 1660, 420)
E = (900, 620)
# F G H I side-by-side (4 nodes in 1660px width)
F = (255, 800); G = (665, 800); H = (1075, 800); I = (1485, 800)

# Phase 3: y=970..1580
P3 = (70, 965, 1660, 630)
J = (900, 1060)
K = (900, 1215)   # diamond
L = (380, 1430); M = (900, 1430); N = (1420, 1430)

# O - oval
O = (900, 1710)

# ── Build SVG ──────────────────────────────────────────────────────
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">']
svg.append(ARROW_DEFS)
svg.append(f'<rect width="{W}" height="{H}" fill="white"/>')

# Containers (drawn first, behind nodes)
svg.append(container(*P1, "Phase 1: 準備階段"))
svg.append(container(*P2, "Phase 2: 元件滾動更新"))
svg.append(container(*P3, "Phase 3: 工作負載更新"))

# Nodes
svg.append(oval_node(*A, 520, 56, "使用者更新 KubeVirt CR\nimagePullPolicy / imageTag"))
svg.append(rect_node(*B, NW, NH, "virt-operator 偵測 CR 變更\n比對 generation annotation"))
svg.append(rect_node(*C, NW, NH, "建立 InstallStrategy Job\n產生新版 ConfigMap"))
svg.append(rect_node(*D, NW, NH, "InstallStrategy ConfigMap\n寫入目標元件 manifests"))
svg.append(rect_node(*E, NW, NH, "virt-operator 套用新資源"))
svg.append(rect_node(*F, 340, WH, "CRD / RBAC / Webhook\n直接 apply"))
svg.append(rect_node(*G, 340, WH, "virt-api Deployment\n滾動更新"))
svg.append(rect_node(*H, 340, WH, "virt-controller Deployment\n滾動更新"))
svg.append(rect_node(*I, 340, WH, "virt-handler DaemonSet\n逐節點滾動更新"))
svg.append(rect_node(*J, NW, WH, "WorkloadUpdateController\n偵測過時 VMI"))
svg.append(diamond(*K, 340, 100, "workloadUpdateMethods\n設定為何？"))
svg.append(rect_node(*L, 360, WH, "建立 VirtualMachineInstanceMigration\n遷移至新版 virt-launcher"))
svg.append(rect_node(*M, 360, WH, "批次驅逐 VMI\nbatchEvictionSize per batch"))
svg.append(rect_node(*N, 320, WH, "不自動更新\n手動干預"))
svg.append(oval_node(*O, 500, 66, "KubeVirt CR 狀態\nAvailable=true\nProgressing=false", fill="#27AE60"))

# ── Arrows ──────────────────────────────────────────────────────────
# Phase 1
svg.append(line(A[0], A[1]+28, B[0], B[1]-30))
svg.append(line(B[0], B[1]+30, C[0], C[1]-30))
svg.append(line(C[0], C[1]+30, D[0], D[1]-30))
# D → E (cross containers)
svg.append(line(D[0], D[1]+30, E[0], E[1]-30))
# E → F, G, H, I (fan out)
for node in [F, G, H, I]:
    svg.append(path(f"M{E[0]},{E[1]+30} L{E[0]},{E[1]+55} L{node[0]},{E[1]+55} L{node[0]},{node[1]-34}"))

# F,G,H,I → J (merge — bent paths through gap between phases)
merge_y = 958  # between Phase2 bottom (945) and Phase3 top (965)
for node in [F, G, H, I]:
    svg.append(path(f"M{node[0]},{node[1]+34} L{node[0]},{merge_y} L{J[0]},{merge_y} L{J[0]},{J[1]-34}"))

# J → K
svg.append(line(J[0], J[1]+34, K[0], K[1]-50))

# K → L (LiveMigrate, left)
svg.append(path(f"M{K[0]-170},{K[1]} L{L[0]+20},{K[1]} L{L[0]+20},{L[1]-34}", label="LiveMigrate", lx=K[0]-168, ly=K[1]-8))
# K → M (Evict, down)
svg.append(line(K[0], K[1]+50, M[0], M[1]-34, label="Evict", lx=K[0]+6, ly=(K[1]+50+M[1]-34)//2))
# K → N (右, 無設定)
svg.append(path(f"M{K[0]+170},{K[1]} L{N[0]-20},{K[1]} L{N[0]-20},{N[1]-34}", label="空/無設定", lx=K[0]+172, ly=K[1]-8))

# L,M,N → O (merge)
for node in [L, M, N]:
    svg.append(path(f"M{node[0]},{node[1]+34} L{node[0]},{O[1]-33} L{O[0]},{O[1]-33} L{O[0]},{O[1]-33}"))
svg.append(line(O[0], O[1]-33, O[0], O[1]-33))
# Override — simpler direct lines to O
svg = [s for s in svg if 'L{O[0]}' not in s]
# Redo: L,M,N → O
for node in [L, M, N]:
    svg.append(path(f"M{node[0]},{node[1]+34} L{node[0]},{1620} L{O[0]},{1620} L{O[0]},{O[1]-33}"))

svg.append('</svg>')
out = '\n'.join(svg)
os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "kubevirt-upgrade-flow.svg"), "w", encoding="utf-8") as f:
    f.write(out)
print("✓ kubevirt-upgrade-flow.svg")
