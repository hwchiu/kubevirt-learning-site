#!/usr/bin/env python3
"""Generate monitoring diagrams as SVGs in Notion Clean Style 4."""

import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW_COLOR = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
SUCCESS_FILL = "#dcfce7"
SUCCESS_STROKE = "#86efac"
ERROR_FILL = "#fee2e2"
ERROR_STROKE = "#fca5a5"
WARN_FILL = "#fef9c3"
WARN_STROKE = "#fde047"

OUT_DIR = "docs-site/public/diagrams/monitoring"
os.makedirs(OUT_DIR, exist_ok=True)


def make_svg(w, h, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW_COLOR}"/>
    </marker>
    <marker id="arrow-gray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{TEXT_SECONDARY}"/>
    </marker>
    <marker id="arrow-dash" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW_COLOR}"/>
    </marker>
  </defs>
  <rect width="{w}" height="{h}" fill="{BG}"/>
{content}
</svg>'''


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def R(x, y, w, h, fill=BOX_FILL, stroke=BOX_STROKE, rx=6, sw=1.5):
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def DR(x, y, w, h, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, rx=8):
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="6,3"/>'


def T(x, y, s, fill=TEXT_PRIMARY, size=13, weight="normal", anchor="middle"):
    return f'  <text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" font-size="{size}" font-weight="{weight}" font-family="{FONT}">{esc(s)}</text>'


def MT(x, cy, lines, fill=TEXT_PRIMARY, size=12, anchor="middle", lh=17):
    n = len(lines)
    start_y = cy - (n * lh) / 2 + lh * 0.75
    return '\n'.join(T(x, start_y + i * lh, ln, fill=fill, size=size, anchor=anchor) for i, ln in enumerate(lines))


def L(x1, y1, x2, y2, color=ARROW_COLOR, sw=1.5, dashed=False, marker="url(#arrow)"):
    d = ' stroke-dasharray="5,3"' if dashed else ''
    m = f' marker-end="{marker}"' if marker else ''
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}{m}/>'


def P(d, color=ARROW_COLOR, sw=1.5, dashed=False, marker="url(#arrow)"):
    ds = ' stroke-dasharray="5,3"' if dashed else ''
    m = f' marker-end="{marker}"' if marker else ''
    return f'  <path d="{d}" stroke="{color}" stroke-width="{sw}" fill="none"{ds}{m}/>'


def DM(cx, cy, w, h, fill=BOX_FILL, stroke=BOX_STROKE):
    pts = f"{cx},{cy - h // 2} {cx + w // 2},{cy} {cx},{cy + h // 2} {cx - w // 2},{cy}"
    return f'  <polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'


def ALbl(x, y, s):
    return f'  <text x="{x}" y="{y}" text-anchor="middle" fill="{TEXT_SECONDARY}" font-size="10" font-family="{FONT}">{esc(s)}</text>'


def BOX(cx, cy, w, h, lines, fill=BOX_FILL, stroke=BOX_STROKE):
    parts = [R(cx - w // 2, cy - h // 2, w, h, fill=fill, stroke=stroke)]
    parts.append(MT(cx, cy, lines))
    return '\n'.join(parts)


def write_svg(name, svg_content):
    path = os.path.join(OUT_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"  Written: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. monitoring-system-arch  (architecture.md line 35)
# ─────────────────────────────────────────────────────────────────────────────
def gen_system_arch():
    W, H = 980, 680
    parts = []

    # ── Left container: KubeVirt 子專案 ──────────────────────────────────────
    parts.append(DR(20, 30, 200, 580, rx=10))
    parts.append(T(120, 52, "KubeVirt 子專案", fill=TEXT_SECONDARY, size=11, weight="600"))
    ops = ["kubevirt", "CDI", "SSP", "HCO", "CNAO", "其他子專案"]
    op_ys = [90, 170, 250, 330, 410, 490]
    for i, (nm, oy) in enumerate(zip(ops, op_ys)):
        parts.append(BOX(120, oy, 160, 38, [nm]))
    # center x = 120, right edge = 200

    # ── Middle container: kubevirt/monitoring ────────────────────────────────
    parts.append(DR(270, 30, 210, 580, rx=10))
    parts.append(T(375, 52, "kubevirt/monitoring 儲存庫", fill=TEXT_SECONDARY, size=10, weight="600"))
    tools = [
        (["monitoringlinter", "靜態分析 Linter"], 95),
        (["metricsdocs", "文件產生器"], 185),
        (["runbook-sync", "下游同步"], 275),
        (["prom-metrics-linter", "指標命名 Linter"], 365),
        (["pkg/metrics/parser", "指標解析器"], 455),
        (["dashboards/", "Grafana 儀表板"], 530),
        (["docs/runbooks/", "Runbook 文件"], 590),
    ]
    tool_ids = {}
    tool_ys = [95, 185, 275, 365, 455, 530, 590]
    for (lines, ty) in zip(
        [["monitoringlinter", "靜態分析 Linter"],
         ["metricsdocs", "文件產生器"],
         ["runbook-sync-downstream", "Runbook 同步工具"],
         ["prom-metrics-linter", "指標命名 Linter"],
         ["pkg/metrics/parser", "指標解析器"],
         ["dashboards/", "Grafana 儀表板"],
         ["docs/runbooks/", "Runbook 文件"]],
        tool_ys
    ):
        parts.append(BOX(375, ty, 190, 38, lines))

    # ── Right container: 外部系統 ────────────────────────────────────────────
    parts.append(DR(540, 30, 210, 580, rx=10))
    parts.append(T(645, 52, "外部系統", fill=TEXT_SECONDARY, size=11, weight="600"))
    ext_ys = [90, 180, 270, 360, 450]
    for nm, ey in zip(["Prometheus", "Grafana", "GitHub Actions", "quay.io Registry", "openshift/runbooks"], ext_ys):
        parts.append(BOX(645, ey, 190, 38, [nm]))

    # ── Right container: GitHub / downstream ────────────────────────────────
    parts.append(DR(800, 30, 160, 360, rx=10))
    parts.append(T(880, 52, "CI/CD 整合", fill=TEXT_SECONDARY, size=11, weight="600"))
    for nm, ey in zip(["GitHub Actions", "自動化觸發", "PR 建立", "版本發布"], [90, 160, 230, 300]):
        parts.append(BOX(880, ey, 140, 36, [nm]))

    # ── Arrows ────────────────────────────────────────────────────────────────
    # monitoringlinter → KubeVirt子專案
    parts.append(L(280, 95, 200, 90, color=ARROW_COLOR))
    parts.append(L(280, 95, 200, 170, color=ARROW_COLOR))
    # metricsdocs → KubeVirt子專案
    parts.append(L(280, 185, 200, 90))
    parts.append(L(280, 185, 200, 170))
    parts.append(L(280, 185, 200, 250))
    parts.append(L(280, 185, 200, 330))
    # prom-metrics-linter → KubeVirt子専案
    parts.append(L(280, 365, 200, 90))
    parts.append(L(280, 365, 200, 170))
    # runbook-sync → openshift/runbooks
    parts.append(L(470, 275, 540, 450))
    # dashboards → Grafana
    parts.append(L(470, 530, 540, 180))
    # prom-metrics-linter → quay.io (dashed)
    parts.append(L(470, 365, 540, 360, dashed=True))
    # GitHub Actions → metricsdocs, runbook-sync, prom-metrics-linter
    parts.append(L(540, 270, 470, 185))
    parts.append(L(540, 270, 470, 275))
    parts.append(L(540, 270, 470, 365))
    # Prometheus → runbooks
    parts.append(L(540, 90, 470, 590))

    # Title
    parts.append(T(W // 2, H - 20, "系統架構圖 — kubevirt/monitoring 與外部系統整合", fill=TEXT_SECONDARY, size=11))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 2. monitoring-cicd-workflows  (architecture.md line 235)
# ─────────────────────────────────────────────────────────────────────────────
def gen_cicd_workflows():
    W, H = 820, 360
    parts = []

    # Title
    parts.append(T(W // 2, 28, "GitHub Actions 工作流程", fill=TEXT_PRIMARY, size=15, weight="600"))

    # 4 containers in 2x2 grid
    # Top-left: Pull Request 觸發
    parts.append(DR(30, 50, 370, 130, rx=8))
    parts.append(T(215, 68, "Pull Request 觸發", fill=TEXT_SECONDARY, size=11, weight="600"))
    parts.append(BOX(130, 105, 160, 52, ["sanity.yaml", "Markdown Lint"]))
    parts.append(BOX(320, 105, 160, 52, ["runbook-preview.yaml", "Runbook 預覽"]))

    # Top-right: Push to main
    parts.append(DR(420, 50, 370, 130, rx=8))
    parts.append(T(605, 68, "Push to main", fill=TEXT_SECONDARY, size=11, weight="600"))
    parts.append(BOX(605, 105, 200, 52, ["publish.yaml", "GitHub Pages 發布"]))

    # Bottom-left: 每日排程
    parts.append(DR(30, 200, 370, 140, rx=8))
    parts.append(T(215, 218, "每日排程", fill=TEXT_SECONDARY, size=11, weight="600"))
    parts.append(BOX(130, 258, 160, 60, ["update_metrics_docs.yaml", "指標文件更新", "⏰ 05:00 UTC"]))
    parts.append(BOX(320, 258, 160, 60, ["runbook_sync_downstream.yaml", "Runbook 同步", "⏰ 04:30 UTC"]))

    # Bottom-right: Release 發布
    parts.append(DR(420, 200, 370, 140, rx=8))
    parts.append(T(605, 218, "Release 發布", fill=TEXT_SECONDARY, size=11, weight="600"))
    parts.append(BOX(605, 258, 220, 60, ["prom-metrics-linter.yaml", "Docker 映像推送", "→ quay.io"]))

    parts.append(T(W // 2, H - 8, "各工作流程依觸發類型分組", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 3. monitoring-go-modules  (architecture.md line 260)
# ─────────────────────────────────────────────────────────────────────────────
def gen_go_modules():
    W, H = 820, 340
    parts = []

    parts.append(T(W // 2, 28, "多 Go Module 架構", fill=TEXT_PRIMARY, size=15, weight="600"))

    # Root module
    parts.append(BOX(410, 80, 280, 54, ["根模組 github.com/kubevirt/monitoring", "go 1.23.6"], fill="#e0f2fe", stroke="#7dd3fc"))
    # Arrow down to monitoringlinter
    parts.append(L(410, 107, 410, 148))
    parts.append(ALbl(450, 140, "包含"))
    parts.append(BOX(410, 170, 200, 38, ["monitoringlinter/", "靜態分析器"]))

    # Four sub-modules
    xs = [100, 280, 560, 740]
    mods = [
        (["tools/metricsdocs", "go 1.16"], "#fdf4ff", "#e9d5ff"),
        (["tools/runbook-sync-downstream", "go 1.22.1"], "#fdf4ff", "#e9d5ff"),
        (["test/metrics/prom-metrics-linter", "go 1.20"], "#fdf4ff", "#e9d5ff"),
        (["pkg/metrics/parser", "go 1.20"], "#fff7ed", "#fed7aa"),
    ]

    for x, (lines, f, s) in zip(xs, mods):
        parts.append(BOX(x, 270, 175, 52, lines, fill=f, stroke=s))
        # Dashed line from root to sub-module (independent modules)
        parts.append(P(f"M {410} {107} L {x} {244}", color="#e5e7eb", dashed=True, marker=""))

    parts.append(T(W // 2, H - 12, "各工具擁有獨立 go.mod，依賴版本互不影響", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 4. monitoring-metrics-collection  (integration.md line 74)
# ─────────────────────────────────────────────────────────────────────────────
def gen_metrics_collection():
    W, H = 860, 480
    parts = []

    parts.append(T(W // 2, 26, "指標收集流程 — metricsdocs 工具", fill=TEXT_PRIMARY, size=15, weight="600"))

    # Left: 9 operators
    op_names = ["kubevirt", "CDI", "CNAO", "SSP", "NMO", "HPPO", "HPP", "HCO", "KMP"]
    op_ys = [70 + i * 44 for i in range(9)]
    for nm, oy in zip(op_names, op_ys):
        parts.append(BOX(90, oy, 130, 34, [nm]))

    # Middle: metricsdocs subgraph
    parts.append(DR(270, 45, 380, 420, rx=10))
    parts.append(T(460, 62, "metricsdocs 工具", fill=TEXT_SECONDARY, size=11, weight="600"))

    tool_ys = [100, 190, 280, 380]
    tool_labels = [
        ["config 設定檔", "讀取版本號"],
        ["git clone/pull", "各 Operator 原始碼"],
        ["解析 metrics.md", "表格格式"],
        ["metrics.tmpl", "合併輸出"],
    ]
    for ty, tl in zip(tool_ys, tool_labels):
        parts.append(BOX(460, ty, 200, 46, tl))

    # Arrows inside metricsdocs
    for a, b in zip(tool_ys[:-1], tool_ys[1:]):
        parts.append(L(460, a + 23, 460, b - 23))

    # Operator arrows to git clone box (GIT is at y=190)
    git_y = 190
    for nm, oy in zip(op_names, op_ys):
        parts.append(L(155, oy, 360, git_y))

    # Output arrow
    parts.append(L(560, 380 + 23, 700, 240))
    parts.append(BOX(780, 240, 150, 44, ["docs/metrics.md", "統一指標文件"], fill="#dcfce7", stroke="#86efac"))
    parts.append(L(710, 240, 705, 240))

    parts.append(T(W // 2, H - 12, "自動聚合 9 個 KubeVirt 子專案的指標文件", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 5. monitoring-recording-rule-validation  (integration.md line 194)
# ─────────────────────────────────────────────────────────────────────────────
def gen_recording_rule_validation():
    W, H = 680, 720
    parts = []

    parts.append(T(W // 2, 26, "Recording Rule 命名驗證流程", fill=TEXT_PRIMARY, size=15, weight="600"))

    cx = 340

    # Node positions
    A = (cx, 65)       # Recording Rule 名稱
    B = (cx, 155)      # 分割為 3 段？
    C = (190, 230)     # ❌ 格式錯誤
    D = (cx, 240)      # level:metric:operations
    E = (cx, 330)      # metric 以 operator 開頭？
    F = (190, 400)     # ❌ 前綴錯誤
    G = (cx, 415)      # 偵測 expr 中的運算
    H_node = (cx, 500) # 單一運算？
    I = (500, 560)     # operations 後綴匹配？
    J = (240, 560)     # 至少一個運算出現？
    K = (500, 640)     # ❌ 後綴不匹配
    L_node = (cx, 680) # ✅ 通過
    M = (120, 640)     # ❌ 缺少運算
    N = (340, 640)     # operations 有重複 token？
    O = (500, 700)     # ❌ 重複運算

    # Draw boxes
    parts.append(BOX(*A, 200, 36, ["Recording Rule 名稱"]))
    parts.append(DM(*B, 160, 46))
    parts.append(MT(B[0], B[1], ["分割為 3 段？"]))

    parts.append(BOX(*C, 140, 34, ["❌ 格式錯誤"], fill=ERROR_FILL, stroke=ERROR_STROKE))
    parts.append(BOX(*D, 210, 34, ["level : metric : operations"]))
    parts.append(DM(*E, 220, 46))
    parts.append(MT(E[0], E[1], ["metric 以 operator 名稱開頭？"]))

    parts.append(BOX(*F, 140, 34, ["❌ 前綴錯誤"], fill=ERROR_FILL, stroke=ERROR_STROKE))
    parts.append(BOX(*G, 200, 34, ["偵測 expr 中的運算"]))
    parts.append(DM(*H_node, 140, 44))
    parts.append(MT(H_node[0], H_node[1], ["單一運算？"]))

    parts.append(DM(*I, 170, 40))
    parts.append(MT(I[0], I[1], ["operations 後綴匹配？"]))
    parts.append(DM(*J, 200, 40))
    parts.append(MT(J[0], J[1], ["至少一個運算在 operations 中？"]))

    parts.append(BOX(*K, 150, 34, ["❌ 後綴不匹配"], fill=ERROR_FILL, stroke=ERROR_STROKE))
    parts.append(BOX(*L_node, 120, 36, ["✅ 通過"], fill=SUCCESS_FILL, stroke=SUCCESS_STROKE))
    parts.append(BOX(*M, 140, 34, ["❌ 缺少運算"], fill=ERROR_FILL, stroke=ERROR_STROKE))
    parts.append(DM(*N, 190, 40))
    parts.append(MT(N[0], N[1], ["operations 有重複 token？"]))
    parts.append(BOX(*O, 140, 34, ["❌ 重複運算"], fill=ERROR_FILL, stroke=ERROR_STROKE))

    # Arrows
    parts.append(L(A[0], A[1] + 18, B[0], B[1] - 23))
    # B → C (否)
    parts.append(L(B[0] - 80, B[1], C[0] + 70, C[1] - 17))
    parts.append(ALbl(230, B[1] - 3, "否"))
    # B → D (是)
    parts.append(L(B[0], B[1] + 23, D[0], D[1] - 17))
    parts.append(ALbl(B[0] + 18, B[1] + 10, "是"))
    # D → E
    parts.append(L(D[0], D[1] + 17, E[0], E[1] - 23))
    # E → F (否)
    parts.append(L(E[0] - 110, E[1], F[0] + 70, F[1] - 17))
    parts.append(ALbl(228, E[1] - 3, "否"))
    # E → G (是)
    parts.append(L(E[0], E[1] + 23, G[0], G[1] - 17))
    parts.append(ALbl(E[0] + 18, E[1] + 10, "是"))
    # G → H
    parts.append(L(G[0], G[1] + 17, H_node[0], H_node[1] - 22))
    # H → I (是)
    parts.append(L(H_node[0] + 70, H_node[1], I[0] - 85, I[1]))
    parts.append(ALbl(425, H_node[1] - 5, "是"))
    # H → J (否)
    parts.append(L(H_node[0] - 70, H_node[1], J[0] + 100, J[1]))
    parts.append(ALbl(268, H_node[1] - 5, "否"))
    # I → K (否)
    parts.append(L(I[0], I[1] + 20, K[0], K[1] - 17))
    parts.append(ALbl(I[0] + 18, I[1] + 8, "否"))
    # I → L (是)
    parts.append(L(I[0] - 85, I[1] + 8, L_node[0] + 60, L_node[1] - 18))
    parts.append(ALbl(430, I[1] + 20, "是"))
    # J → M (否)
    parts.append(L(J[0] - 100, J[1], M[0] + 70, M[1] - 17))
    parts.append(ALbl(155, J[1] - 5, "否"))
    # J → N (是)
    parts.append(L(J[0] + 10, J[1] + 20, N[0] - 95, N[1]))
    parts.append(ALbl(265, J[1] + 15, "是"))
    # N → O (是)
    parts.append(L(N[0] + 95, N[1], O[0] - 70, O[1]))
    parts.append(ALbl(420, N[1] - 5, "是"))
    # N → L (否)
    parts.append(L(N[0], N[1] + 20, L_node[0], L_node[1] - 18))
    parts.append(ALbl(N[0] + 18, N[1] + 10, "否"))

    parts.append(T(W // 2, H - 10, "prom-metrics-linter Recording Rule 驗證邏輯", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 6. monitoring-runbook-sync-sequence  (integration.md line 321)
# ─────────────────────────────────────────────────────────────────────────────
def gen_runbook_sync_sequence():
    W, H = 860, 520
    parts = []

    parts.append(T(W // 2, 26, "Runbook 下游同步流程 — Sequence Diagram", fill=TEXT_PRIMARY, size=15, weight="600"))

    participants = [
        ("GHA", "GitHub Actions\n(每日 04:30 UTC)", 80),
        ("SYNC", "runbook-sync-downstream", 230),
        ("UP", "kubevirt/monitoring\n(upstream)", 400),
        ("DOWN", "openshift/runbooks\n(downstream)", 580),
        ("BOT", "hco-bot Fork", 750),
    ]

    LIFE_TOP = 95
    LIFE_BOTTOM = H - 50
    BOX_H = 44

    xs = [p[2] for p in participants]

    # Participant boxes
    for pid, label, x in participants:
        lines = label.split('\n')
        parts.append(BOX(x, LIFE_TOP, 140, BOX_H, lines, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
        # Lifeline
        parts.append(L(x, LIFE_TOP + BOX_H // 2, x, LIFE_BOTTOM, color="#e5e7eb", sw=1, dashed=True, marker=""))

    # Messages
    msgs = [
        (xs[0], xs[1], "觸發同步"),
        (xs[1], xs[2], "git clone 上游"),
        (xs[1], xs[3], "git clone 下游"),
        (xs[1], xs[1], "比對 Runbook 差異"),
        (xs[1], xs[1], "套用轉換規則"),
        (xs[1], xs[4], "推送新分支"),
        (xs[4], xs[3], "建立 Pull Request"),
        (xs[1], xs[3], "關閉舊的重複 PR"),
    ]

    msg_ys = [160, 200, 240, 280, 310, 360, 400, 440]

    for (x1, x2, lbl), my in zip(msgs, msg_ys):
        if x1 == x2:
            # Self-loop
            rx = x1 + 20
            parts.append(P(f"M {x1} {my} Q {rx + 50} {my} {rx + 50} {my + 20} Q {rx + 50} {my + 40} {x1} {my + 40}"))
            parts.append(ALbl(x1 + 60, my + 15, lbl))
        else:
            parts.append(L(x1, my, x2, my))
            mx = (x1 + x2) // 2
            parts.append(ALbl(mx, my - 5, lbl))

    parts.append(T(W // 2, H - 12, "每日自動同步上游 Runbook 至 OpenShift 下游儲存庫", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 7. monitoring-cicd-overview  (integration.md line 407)
# ─────────────────────────────────────────────────────────────────────────────
def gen_cicd_overview():
    W, H = 820, 520
    parts = []

    parts.append(T(W // 2, 28, "GitHub Actions CI/CD 工作流程總覽", fill=TEXT_PRIMARY, size=15, weight="600"))

    # Left: Triggers
    parts.append(DR(30, 48, 200, 430, rx=10))
    parts.append(T(130, 66, "觸發條件", fill=TEXT_SECONDARY, size=11, weight="600"))

    triggers = ["Push to main", "Pull Request", "Release 發布", "排程觸發", "手動觸發"]
    trig_ys = [100, 170, 240, 310, 380]
    for nm, ty in zip(triggers, trig_ys):
        parts.append(BOX(130, ty, 165, 38, [nm]))

    # Right: Workflows
    parts.append(DR(340, 48, 450, 430, rx=10))
    parts.append(T(565, 66, "6 個 Workflow", fill=TEXT_SECONDARY, size=11, weight="600"))

    workflows = [
        (["sanity.yaml", "Markdown Lint"], 100),
        (["publish.yaml", "GitHub Pages 部署"], 170),
        (["prom-metrics-linter.yaml", "Docker 映像發布"], 240),
        (["update_metrics_docs.yaml", "指標文件更新"], 310),
        (["runbook_sync_downstream.yaml", "Runbook 同步"], 380),
        (["runbook-preview.yaml", "Runbook 預覽"], 450),
    ]

    for lines, wy in workflows:
        parts.append(BOX(565, wy, 250, 44, lines))

    wf_ys = [100, 170, 240, 310, 380, 450]

    # Arrows: triggers → workflows
    # Push → sanity, publish
    parts.append(L(212, trig_ys[0], 440, wf_ys[0]))
    parts.append(L(212, trig_ys[0], 440, wf_ys[1]))
    # PR → sanity, runbook-preview
    parts.append(L(212, trig_ys[1], 440, wf_ys[0]))
    parts.append(L(212, trig_ys[1], 440, wf_ys[5]))
    # Release → prom-metrics-linter
    parts.append(L(212, trig_ys[2], 440, wf_ys[2]))
    # Schedule → update_metrics_docs, runbook_sync
    parts.append(L(212, trig_ys[3], 440, wf_ys[3]))
    parts.append(L(212, trig_ys[3], 440, wf_ys[4]))
    # Manual → publish, runbook_sync
    parts.append(L(212, trig_ys[4], 440, wf_ys[1]))
    parts.append(L(212, trig_ys[4], 440, wf_ys[4]))

    parts.append(T(W // 2, H - 12, "觸發條件與工作流程的對應關係", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 8. monitoring-daily-schedule  (integration.md line 538)
# ─────────────────────────────────────────────────────────────────────────────
def gen_daily_schedule():
    W, H = 760, 220
    parts = []

    parts.append(T(W // 2, 28, "每日自動化排程時序 (UTC)", fill=TEXT_PRIMARY, size=15, weight="600"))

    # Timeline axis
    axis_y = 160
    ax0, ax1 = 80, W - 40
    parts.append(L(ax0, axis_y, ax1, axis_y, color="#e5e7eb", sw=1.5, marker=""))

    # Time marks: 04:00, 04:30, 05:00, 05:30, 06:00
    times = ["04:00", "04:30", "05:00", "05:30", "06:00"]
    time_xs = [ax0 + i * (ax1 - ax0) // 4 for i in range(5)]
    for tx, tl in zip(time_xs, times):
        parts.append(L(tx, axis_y - 5, tx, axis_y + 5, color="#6b7280", sw=1.5, marker=""))
        parts.append(T(tx, axis_y + 20, tl, fill=TEXT_SECONDARY, size=11))

    step = (ax1 - ax0) / 4  # pixels per 30 min

    # Runbook 同步 04:30 ~ 05:00
    rb_x = time_xs[1]
    parts.append(R(rb_x, axis_y - 50, int(step), 32, fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
    parts.append(T(rb_x + step // 2, axis_y - 29, "Runbook 同步", fill=TEXT_PRIMARY, size=11))

    # 指標文件更新 05:00 ~ 05:30
    md_x = time_xs[2]
    parts.append(R(md_x, axis_y - 50, int(step), 32, fill=SUCCESS_FILL, stroke=SUCCESS_STROKE))
    parts.append(T(md_x + step // 2, axis_y - 29, "指標文件更新", fill=TEXT_PRIMARY, size=11))

    # Section labels
    parts.append(T(rb_x + step // 2, axis_y - 58, "04:30 UTC", fill=TEXT_SECONDARY, size=10))
    parts.append(T(md_x + step // 2, axis_y - 58, "05:00 UTC", fill=TEXT_SECONDARY, size=10))

    parts.append(T(W // 2, H - 12, "每日自動化 CI/CD 排程", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 9. monitoring-linter-checks  (integration.md line 557)
# ─────────────────────────────────────────────────────────────────────────────
def gen_linter_checks():
    W, H = 780, 640
    parts = []

    parts.append(T(W // 2, 26, "monitoringlinter — 靜態分析規則檢查流程", fill=TEXT_PRIMARY, size=15, weight="600"))

    cx = 380

    # Container: Operator 專案
    parts.append(DR(30, 44, 200, 110, rx=8))
    parts.append(T(130, 62, "Operator 專案", fill=TEXT_SECONDARY, size=11, weight="600"))
    parts.append(BOX(130, 90, 165, 34, ["任意 .go 檔案"]))
    parts.append(BOX(130, 132, 165, 34, ["pkg/monitoring/*.go"]))

    # Container: monitoringlinter 檢查
    parts.append(DR(250, 44, 500, 500, rx=8))
    parts.append(T(500, 62, "monitoringlinter 檢查規則", fill=TEXT_SECONDARY, size=11, weight="600"))

    CHK1 = (500, 115)
    CHK2 = (500, 195)
    CHK3 = (500, 285)
    CHK4 = (500, 365)
    CHK5 = (500, 445)
    ERR1 = (680, 195)
    ERR2 = (680, 365)
    ERR3 = (680, 445)

    parts.append(DM(*CHK1, 220, 44))
    parts.append(MT(CHK1[0], CHK1[1], ["import prometheus?"]))
    parts.append(DM(*CHK2, 260, 44))
    parts.append(MT(CHK2[0], CHK2[1], ["呼叫 Register/MustRegister?"]))
    parts.append(DM(*CHK3, 240, 44))
    parts.append(MT(CHK3[0], CHK3[1], ["在 pkg/monitoring 目錄內？"]))
    parts.append(DM(*CHK4, 200, 44))
    parts.append(MT(CHK4[0], CHK4[1], ["呼叫 RegisterMetrics?"]))
    parts.append(DM(*CHK5, 260, 44))
    parts.append(MT(CHK5[0], CHK5[1], ["呼叫 RegisterAlerts", "或 RegisterRecordingRules?"]))

    parts.append(BOX(*ERR1, 180, 36, ["❌ 必須使用 operator-observability"], fill=ERROR_FILL, stroke=ERROR_STROKE))
    parts.append(BOX(*ERR2, 180, 36, ["❌ 必須在 pkg/monitoring 內"], fill=ERROR_FILL, stroke=ERROR_STROKE))
    parts.append(BOX(*ERR3, 180, 36, ["❌ 必須在 pkg/monitoring 內"], fill=ERROR_FILL, stroke=ERROR_STROKE))

    OK4 = (320, 365)
    OK5 = (320, 445)
    parts.append(BOX(*OK4, 130, 34, ["✅ 允許呼叫", "RegisterMetrics"], fill=SUCCESS_FILL, stroke=SUCCESS_STROKE))
    parts.append(BOX(*OK5, 130, 34, ["✅ 允許呼叫", "RegisterAlerts"], fill=SUCCESS_FILL, stroke=SUCCESS_STROKE))

    # Arrows
    parts.append(L(130, 90, CHK1[0] - 110, CHK1[1]))  # ANY → CHK1
    parts.append(L(CHK1[0], CHK1[1] + 22, CHK2[0], CHK2[1] - 22))
    parts.append(ALbl(CHK1[0] + 18, CHK1[1] + 12, "是"))
    parts.append(L(CHK2[0], CHK2[1] + 22, ERR1[0] - 90, ERR1[1]))
    parts.append(ALbl(CHK2[0] + 20, CHK2[1] + 10, "是"))
    parts.append(L(CHK1[0] - 110, CHK1[1], CHK3[0] - 120, CHK3[1]))
    parts.append(ALbl(CHK1[0] - 120, CHK1[1] + 10, "否"))
    parts.append(L(CHK3[0] - 120, CHK3[1], CHK4[0] - 100, CHK4[1]))
    parts.append(L(CHK3[0] - 120, CHK3[1], CHK5[0] - 130, CHK5[1]))
    parts.append(L(CHK4[0], CHK4[1] + 22, ERR2[0] - 90, ERR2[1]))
    parts.append(ALbl(CHK4[0] + 18, CHK4[1] + 10, "是"))
    parts.append(L(CHK5[0], CHK5[1] + 22, ERR3[0] - 90, ERR3[1]))
    parts.append(ALbl(CHK5[0] + 18, CHK5[1] + 10, "是"))
    # pkg/monitoring → OK
    parts.append(L(130, 132, OK4[0] - 65, OK4[1]))
    parts.append(L(130, 132, OK5[0] - 65, OK5[1]))

    parts.append(T(W // 2, H - 12, "強制 Operator 專案使用 operator-observability 套件集中管理監控元件", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 10. monitoring-tools-overview  (metrics-alerts.md line 17)
# ─────────────────────────────────────────────────────────────────────────────
def gen_tools_overview():
    W, H = 860, 420
    parts = []

    parts.append(T(W // 2, 28, "kubevirt/monitoring 核心工具總覽", fill=TEXT_PRIMARY, size=15, weight="600"))

    # Main container
    parts.append(DR(20, 44, W - 40, 320, rx=10))
    parts.append(T(W // 2, 62, "kubevirt/monitoring 核心工具", fill=TEXT_SECONDARY, size=11, weight="600"))

    # 4 sub-containers
    sub_data = [
        ("靜態分析", ["monitoringlinter", "Go AST 分析器"], 80),
        ("文件生成", ["metricsdocs", "指標文件彙整"], 290),
        ("同步工具", ["runbook-sync-downstream", "Runbook 下游同步"], 500),
        ("品質驗證", ["prom-metrics-linter", "指標命名規範"], 700),
    ]

    box_ys = [130, 195]

    for lbl, lines1, bx in sub_data:
        parts.append(DR(bx - 90, 75, 185, 260, rx=8))
        parts.append(T(bx, 92, lbl, fill=TEXT_SECONDARY, size=11, weight="600"))
        parts.append(BOX(bx, 160, 165, 44, lines1))
        if lbl == "文件生成":
            parts.append(BOX(bx, 250, 165, 44, ["metrics parser", "Prometheus 指標解析"]))

    # External targets
    OPERATOR = (120, 370)
    DOCS = (360, 370)
    OPENSHIFT = (560, 370)

    parts.append(BOX(*OPERATOR, 165, 38, ["各 KubeVirt Operator"], fill="#fff7ed", stroke="#fed7aa"))
    parts.append(BOX(*DOCS, 165, 38, ["docs/metrics.md"], fill="#f0fdf4", stroke="#bbf7d0"))
    parts.append(BOX(*OPENSHIFT, 165, 38, ["openshift/runbooks"], fill="#fdf4ff", stroke="#e9d5ff"))
    QUAY = (740, 370)
    parts.append(BOX(*QUAY, 165, 38, ["Operator 指標驗證"], fill="#fef9c3", stroke="#fde047"))

    # Arrows
    parts.append(L(170, 182, OPERATOR[0] + 82, OPERATOR[1] - 19))
    parts.append(L(380, 182, DOCS[0] + 82, DOCS[1] - 19))
    parts.append(L(590, 182, OPENSHIFT[0] + 82, OPENSHIFT[1] - 19))
    parts.append(L(800, 182, QUAY[0] + 82, QUAY[1] - 19))

    parts.append(T(W // 2, H - 12, "四個核心工具各司其職，協同維護 KubeVirt 監控品質", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 11. monitoring-analyzer-flow  (metrics-alerts.md line 88)
# ─────────────────────────────────────────────────────────────────────────────
def gen_analyzer_flow():
    W, H = 740, 660
    parts = []

    parts.append(T(W // 2, 26, "monitoringlinter 分析流程 — Flowchart", fill=TEXT_PRIMARY, size=15, weight="600"))

    cx = 370

    A = (cx, 65)
    B = (cx, 145)
    C = (190, 200)
    D = (cx, 215)
    E = (cx, 295)
    F = (190, 350)
    G = (cx, 365)
    H_node = (cx, 440)
    I = (530, 495)
    J = (cx, 495)
    K = (530, 565)
    L_node = (cx, 565)
    M = (cx, 610)

    parts.append(BOX(*A, 240, 36, ["遍歷每個 Go 檔案"]))
    parts.append(DM(*B, 260, 46))
    parts.append(MT(B[0], B[1], ["檔案是否 import 監控相關套件?"]))
    parts.append(BOX(*C, 140, 34, ["跳過此檔案"], fill=BOX_FILL, stroke=BOX_STROKE))
    parts.append(BOX(*D, 220, 34, ["AST Inspect 所有節點"]))
    parts.append(DM(*E, 160, 44))
    parts.append(MT(E[0], E[1], ["節點是 CallExpr?"]))
    parts.append(BOX(*F, 140, 34, ["繼續遍歷"]))
    parts.append(DM(*G, 200, 44))
    parts.append(MT(G[0], G[1], ["是 SelectorExpr 方法呼叫?"]))
    parts.append(DM(*H_node, 220, 44))
    parts.append(MT(H_node[0], H_node[1], ["使用 prometheus 套件?"]))
    parts.append(BOX(*I, 200, 40, ["checkPrometheusMethodCall"]))
    parts.append(DM(*J, 200, 44))
    parts.append(MT(J[0], J[1], ["檔案在 pkg/monitoring 內?"]))
    parts.append(BOX(*K, 200, 40, ["checkOperatorMetrics", "MethodCall"]))
    parts.append(DM(*L_node, 200, 44))
    parts.append(MT(L_node[0], L_node[1], ["使用 operatorrules?"]))
    parts.append(BOX(*M, 220, 36, ["checkOperatorRulesMethodCall"]))

    # Arrows
    parts.append(L(A[0], A[1] + 18, B[0], B[1] - 23))
    parts.append(L(B[0] - 130, B[1], C[0] + 70, C[1] - 17))
    parts.append(ALbl(240, B[1] - 5, "否"))
    parts.append(L(B[0], B[1] + 23, D[0], D[1] - 17))
    parts.append(ALbl(B[0] + 18, B[1] + 10, "是"))
    parts.append(L(D[0], D[1] + 17, E[0], E[1] - 22))
    parts.append(L(E[0] - 80, E[1], F[0] + 70, F[1] - 17))
    parts.append(ALbl(240, E[1] - 5, "否"))
    parts.append(L(E[0], E[1] + 22, G[0], G[1] - 22))
    parts.append(ALbl(E[0] + 18, E[1] + 10, "是"))
    parts.append(L(G[0] - 100, G[1], F[0] + 70, F[1] + 10))
    parts.append(ALbl(240, G[1] - 5, "否"))
    parts.append(L(G[0], G[1] + 22, H_node[0], H_node[1] - 22))
    parts.append(ALbl(G[0] + 18, G[1] + 10, "是"))
    parts.append(L(H_node[0] + 110, H_node[1], I[0] - 100, I[1]))
    parts.append(ALbl(467, H_node[1] - 5, "是"))
    parts.append(L(H_node[0], H_node[1] + 22, J[0], J[1] - 22))
    parts.append(ALbl(H_node[0] + 18, H_node[1] + 10, "否"))
    parts.append(L(J[0] + 18, J[1] + 5, J[0] + 100, J[1] + 20))
    parts.append(ALbl(J[0] + 60, J[1] + 5, "是→跳過"))
    parts.append(L(J[0], J[1] + 22, L_node[0], L_node[1] - 22))
    parts.append(ALbl(J[0] + 18, J[1] + 10, "否"))
    parts.append(L(J[0] - 100, J[1] + 8, K[0] - 100, K[1]))
    parts.append(ALbl(240, J[1] + 15, "使用operatormetrics?"))
    parts.append(L(L_node[0], L_node[1] + 22, M[0], M[1] - 18))
    parts.append(ALbl(L_node[0] + 18, L_node[1] + 10, "是"))

    parts.append(T(W // 2, H - 12, "基於 go/analysis 框架的 AST 靜態分析流程", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 12. monitoring-metricsdocs-sequence  (metrics-alerts.md line 258)
# ─────────────────────────────────────────────────────────────────────────────
def gen_metricsdocs_sequence():
    W, H = 920, 520
    parts = []

    parts.append(T(W // 2, 26, "metricsdocs 生成流程 — Sequence Diagram", fill=TEXT_PRIMARY, size=15, weight="600"))

    participants = [
        ("Main", "main()", 80),
        ("Git", "git.go", 240),
        ("Parser", "parseMetrics", 400),
        ("Template", "metrics.tmpl", 580),
        ("GH", "GitHub API", 760),
    ]

    LIFE_TOP = 95
    LIFE_BOTTOM = H - 50
    BOX_H = 40

    for pid, lbl, x in participants:
        parts.append(BOX(x, LIFE_TOP, 140, BOX_H, [lbl], fill=CONTAINER_FILL, stroke=CONTAINER_STROKE))
        parts.append(L(x, LIFE_TOP + BOX_H // 2, x, LIFE_BOTTOM, color="#e5e7eb", sw=1, dashed=True, marker=""))

    xs = {p[0]: p[2] for p in participants}

    msgs = [
        (xs["Main"], xs["Main"], "parseArguments()"),
        (xs["Main"], xs["Git"], "checkoutProjects()"),
        (xs["Git"], xs["Git"], "gitCheckoutUpstream() / pull"),
        (xs["Git"], xs["Git"], "gitSwitchToBranch(version)"),
        (xs["Main"], xs["Parser"], "parseMetrics()"),
        (xs["Parser"], xs["Parser"], "readLines(metricsDocPath)"),
        (xs["Parser"], xs["Parser"], "parseMetricsDoc(content)"),
        (xs["Main"], xs["Main"], "writeMetrics() / sortMetrics()"),
        (xs["Main"], xs["GH"], "GET release info → 建立連結"),
        (xs["Main"], xs["Template"], "Execute(templateData)"),
        (xs["Template"], xs["Main"], "寫入 docs/metrics.md"),
    ]

    msg_ys = [155, 185, 215, 245, 285, 315, 345, 385, 415, 445, 470]

    for (x1, x2, lbl), my in zip(msgs, msg_ys):
        if x1 == x2:
            rx = x1 + 20
            parts.append(P(f"M {x1} {my} Q {rx + 50} {my} {rx + 50} {my + 16} Q {rx + 50} {my + 30} {x1} {my + 30}"))
            parts.append(ALbl(x1 + 65, my + 8, lbl))
        else:
            # Return arrow (dashed) if from right to left with smaller x2
            if x2 < x1:
                parts.append(L(x1, my, x2, my, dashed=True))
            else:
                parts.append(L(x1, my, x2, my))
            mx = (x1 + x2) // 2
            parts.append(ALbl(mx, my - 5, lbl))

    parts.append(T(W // 2, H - 12, "metricsdocs 自動彙整 9 個子專案的指標文件", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 13. monitoring-runbook-sync-flow  (metrics-alerts.md line 405)
# ─────────────────────────────────────────────────────────────────────────────
def gen_runbook_sync_flow():
    W, H = 820, 700
    parts = []

    parts.append(T(W // 2, 26, "runbook-sync-downstream 同步架構", fill=TEXT_PRIMARY, size=15, weight="600"))

    cx = 280

    A = (cx, 65)
    B = (cx, 130)
    C = (cx, 200)
    D = (cx, 280)
    E = (500, 340)
    F = (150, 340)
    G_skip = (cx, 360)

    H_up = (500, 420)
    I_dep = (150, 420)

    # subgraph updateRunbook
    parts.append(DR(360, 390, 420, 280, rx=8))
    parts.append(T(570, 408, "updateRunbook", fill=TEXT_SECONDARY, size=11, weight="600"))

    H1 = (570, 435)
    H2 = (680, 485)
    H3 = (570, 490)
    H4 = (570, 540)
    H5 = (570, 590)
    H6 = (570, 635)
    H7 = (570, 655)

    parts.append(BOX(*A, 200, 36, ["開始"]))
    parts.append(BOX(*B, 270, 36, ["setup: 克隆 upstream 與 downstream"]))
    parts.append(BOX(*C, 230, 36, ["listRunbooksThatNeedUpdate"]))
    parts.append(DM(*D, 190, 44))
    parts.append(MT(D[0], D[1], ["比對 commit 日期"]))

    parts.append(BOX(*E, 170, 36, ["runbooksToUpdate"], fill=WARN_FILL, stroke=WARN_STROKE))
    parts.append(BOX(*F, 170, 36, ["runbooksToDeprecate"], fill="#fee2e2", stroke="#fca5a5"))
    parts.append(BOX(*G_skip, 100, 32, ["跳過"], fill=BOX_FILL, stroke=BOX_STROKE))

    # updateRunbook subgraph
    parts.append(DM(*H1, 200, 40))
    parts.append(MT(H1[0], H1[1], ["檢查 PR 是否已存在?"]))
    parts.append(BOX(*H2, 80, 32, ["跳過"]))
    parts.append(BOX(*H3, 160, 34, ["建立新分支"]))
    parts.append(BOX(*H4, 200, 34, ["copyRunbook + transform"]))
    parts.append(BOX(*H5, 160, 34, ["commit & push"]))
    parts.append(BOX(*H6, 160, 34, ["建立 PR"]))
    parts.append(BOX(*H7, 160, 34, ["關閉過時 PR"]))

    # subgraph deprecateRunbook
    parts.append(DR(20, 390, 270, 280, rx=8))
    parts.append(T(155, 408, "deprecateRunbook", fill=TEXT_SECONDARY, size=11, weight="600"))

    I1 = (155, 435)
    I2 = (50, 485)
    I3 = (155, 490)
    I4 = (155, 540)
    I5 = (155, 590)
    I6 = (155, 635)

    parts.append(DM(*I1, 200, 40))
    parts.append(MT(I1[0], I1[1], ["檢查 PR 是否已存在?"]))
    parts.append(BOX(*I2, 70, 32, ["跳過"]))
    parts.append(BOX(*I3, 150, 34, ["建立新分支"]))
    parts.append(BOX(*I4, 180, 34, ["套用棄用模板"]))
    parts.append(BOX(*I5, 150, 34, ["commit & push"]))
    parts.append(BOX(*I6, 150, 34, ["建立 PR"]))

    # Main arrows
    parts.append(L(A[0], A[1] + 18, B[0], B[1] - 18))
    parts.append(L(B[0], B[1] + 18, C[0], C[1] - 18))
    parts.append(L(C[0], C[1] + 18, D[0], D[1] - 22))
    parts.append(L(D[0] + 95, D[1], E[0] - 85, E[1]))
    parts.append(ALbl(410, D[1] - 5, "upstream 較新"))
    parts.append(L(D[0] - 95, D[1], F[0] + 85, F[1]))
    parts.append(ALbl(185, D[1] - 5, "upstream 不存在"))
    parts.append(L(D[0], D[1] + 22, G_skip[0], G_skip[1] - 16))
    parts.append(ALbl(D[0] + 25, D[1] + 12, "已是最新"))
    # To subgraphs
    parts.append(L(E[0], E[1] + 18, H1[0], H1[1] - 20))
    parts.append(L(F[0], F[1] + 18, I1[0], I1[1] - 20))

    # updateRunbook arrows
    parts.append(L(H1[0] + 100, H1[1], H2[0] - 40, H2[1]))
    parts.append(ALbl(636, H1[1] - 5, "已存在"))
    parts.append(L(H1[0], H1[1] + 20, H3[0], H3[1] - 17))
    parts.append(ALbl(H1[0] + 18, H1[1] + 10, "不存在"))
    parts.append(L(H3[0], H3[1] + 17, H4[0], H4[1] - 17))
    parts.append(L(H4[0], H4[1] + 17, H5[0], H5[1] - 17))
    parts.append(L(H5[0], H5[1] + 17, H6[0], H6[1] - 17))
    parts.append(L(H6[0], H6[1] + 17, H7[0], H7[1] - 17))

    # deprecateRunbook arrows
    parts.append(L(I1[0] - 100, I1[1], I2[0] + 35, I2[1]))
    parts.append(ALbl(90, I1[1] - 5, "已存在"))
    parts.append(L(I1[0], I1[1] + 20, I3[0], I3[1] - 17))
    parts.append(ALbl(I1[0] + 18, I1[1] + 10, "不存在"))
    parts.append(L(I3[0], I3[1] + 17, I4[0], I4[1] - 17))
    parts.append(L(I4[0], I4[1] + 17, I5[0], I5[1] - 17))
    parts.append(L(I5[0], I5[1] + 17, I6[0], I6[1] - 17))

    parts.append(T(W // 2, H - 12, "runbook-sync-downstream 同步架構與流程分支", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 14. monitoring-promlinter-arch  (metrics-alerts.md line 640)
# ─────────────────────────────────────────────────────────────────────────────
def gen_promlinter_arch():
    W, H = 860, 220
    parts = []

    parts.append(T(W // 2, 26, "prom-metrics-linter 架構 — Flowchart LR", fill=TEXT_PRIMARY, size=15, weight="600"))

    ys = H // 2 + 10

    nodes = [
        (90, ["JSON 輸入", "metricFamilies", "+ recordingRules"]),
        (230, ["parseInput"]),
        (360, ["promlint.", "NewWithMetricFamilies"]),
        (490, ["promlint.Lint", "標準檢查"]),
        (620, ["CustomMetrics", "Validation"]),
        (760, ["排序輸出"]),
    ]

    for nx, lines in nodes:
        parts.append(BOX(nx, ys, 130, 52, lines))

    # Main pipeline arrows
    for i in range(len(nodes) - 1):
        x1 = nodes[i][0] + 65
        x2 = nodes[i + 1][0] - 65
        parts.append(L(x1, ys, x2, ys))

    # allowlist branch
    parts.append(BOX(360, ys - 80, 130, 36, ["allowlist 過濾"]))
    parts.append(L(230 + 65, ys, 360, ys - 62))
    parts.append(BOX(490, ys - 80, 130, 36, ["CustomRecording", "RuleValidation"]))
    parts.append(L(360 + 65, ys - 62, 490 - 65, ys - 62))
    parts.append(L(490, ys - 62, 760, ys - 26))

    parts.append(T(W // 2, H - 10, "基於 promlint 加入 KubeVirt 自定義規則的指標命名驗證工具", fill=TEXT_SECONDARY, size=10))

    return make_svg(W, H, '\n'.join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# Generate all and write files
# ─────────────────────────────────────────────────────────────────────────────
diagrams = [
    ("monitoring-system-arch.svg", gen_system_arch),
    ("monitoring-cicd-workflows.svg", gen_cicd_workflows),
    ("monitoring-go-modules.svg", gen_go_modules),
    ("monitoring-metrics-collection.svg", gen_metrics_collection),
    ("monitoring-recording-rule-validation.svg", gen_recording_rule_validation),
    ("monitoring-runbook-sync-sequence.svg", gen_runbook_sync_sequence),
    ("monitoring-cicd-overview.svg", gen_cicd_overview),
    ("monitoring-daily-schedule.svg", gen_daily_schedule),
    ("monitoring-linter-checks.svg", gen_linter_checks),
    ("monitoring-tools-overview.svg", gen_tools_overview),
    ("monitoring-analyzer-flow.svg", gen_analyzer_flow),
    ("monitoring-metricsdocs-sequence.svg", gen_metricsdocs_sequence),
    ("monitoring-runbook-sync-flow.svg", gen_runbook_sync_flow),
    ("monitoring-promlinter-arch.svg", gen_promlinter_arch),
]

print(f"Generating {len(diagrams)} SVG diagrams...")
for fname, fn in diagrams:
    try:
        svg = fn()
        write_svg(fname, svg)
    except Exception as e:
        print(f"  ERROR generating {fname}: {e}")
        import traceback
        traceback.print_exc()

print("Done!")
