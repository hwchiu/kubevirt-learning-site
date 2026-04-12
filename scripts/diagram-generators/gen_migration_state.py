#!/usr/bin/env python3
# Block 2: kubevirt-migration-state-machine.svg (stateDiagram-v2)

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
FAIL_FILL = "#fff7ed"
FAIL_STROKE = "#fed7aa"
SUCCESS_FILL = "#f0fdf4"
SUCCESS_STROKE = "#bbf7d0"

W, H = 1400, 1100

defs = f'''<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/>
  </marker>
  <marker id="arrow-fail" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="#f97316"/>
  </marker>
</defs>'''

def state_box(x, y, w, h, label, fill=BOX_FILL, stroke=BOX_STROKE):
    lines = []
    lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    lines.append(f'<text x="{x+w//2}" y="{y+h//2+5}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(lines)

def start_circle(x, y):
    return f'<circle cx="{x}" cy="{y}" r="14" fill="{TEXT_PRIMARY}"/>'

def end_circle(x, y):
    return f'''<circle cx="{x}" cy="{y}" r="16" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="2"/>
<circle cx="{x}" cy="{y}" r="10" fill="{TEXT_PRIMARY}"/>'''

def v_arrow(x1, y1, x2, y2, label="", label_side="right", fail=False):
    color = "#f97316" if fail else ARROW
    marker = "url(#arrow-fail)" if fail else "url(#arrow)"
    lx = x1 + 10 if label_side == "right" else x1 - 10
    la = "start" if label_side == "right" else "end"
    ly = (y1 + y2) // 2
    lbl = f'<text x="{lx}" y="{ly+4}" text-anchor="{la}" font-family="{FONT}" font-size="11" fill="{color}">{label}</text>' if label else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" marker-end="{marker}"/>\n{lbl}'

def h_arrow(x1, y1, x2, y2, label="", fail=False):
    color = "#f97316" if fail else ARROW
    marker = "url(#arrow-fail)" if fail else "url(#arrow)"
    mx = (x1 + x2) // 2
    my = min(y1, y2) - 10
    lbl = f'<text x="{mx}" y="{my}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{color}">{label}</text>' if label else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" marker-end="{marker}"/>\n{lbl}'

def path_arrow(d, label="", fail=False, lx=0, ly=0, la="start"):
    color = "#f97316" if fail else ARROW
    marker = "url(#arrow-fail)" if fail else "url(#arrow)"
    lbl = f'<text x="{lx}" y="{ly}" text-anchor="{la}" font-family="{FONT}" font-size="11" fill="{color}">{label}</text>' if label else ''
    return f'<path d="{d}" stroke="{color}" stroke-width="2" fill="none" marker-end="{marker}"/>\n{lbl}'

# Layout: main happy path down the center, fail branches to the right
SW, SH_box = 260, 44
cx = 380  # center x of main path
fail_x = 900  # fail state x

# Y positions for each state
START_Y = 60
UNSET_Y = 120
PEND_Y = 220
SCHED_ING_Y = 320
SCHED_ED_Y = 420
PREP_Y = 520
READY_Y = 620
RUN_Y = 720
SUCC_Y = 860
FAIL_Y = 550
END_FAIL_Y = 980
END_SUCC_Y = 980

cx_box = cx - SW // 2

fail_w = 280
fail_cx = 980
fail_box_x = fail_cx - fail_w // 2

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{defs}
<rect width="{W}" height="{H}" fill="{BG}"/>

<!-- Main states -->
{start_circle(cx, START_Y)}
{state_box(cx_box, UNSET_Y, SW, SH_box, "MigrationPhaseUnset")}
{state_box(cx_box, PEND_Y, SW, SH_box, "MigrationPending")}
{state_box(cx_box, SCHED_ING_Y, SW, SH_box, "MigrationScheduling")}
{state_box(cx_box, SCHED_ED_Y, SW, SH_box, "MigrationScheduled")}
{state_box(cx_box, PREP_Y, SW, SH_box, "MigrationPreparingTarget")}
{state_box(cx_box, READY_Y, SW, SH_box, "MigrationTargetReady")}
{state_box(cx_box, RUN_Y, SW, SH_box, "MigrationRunning")}
{state_box(cx_box, SUCC_Y, SW, SH_box, "MigrationSucceeded", SUCCESS_FILL, SUCCESS_STROKE)}

<!-- Failed state (right side) -->
{state_box(fail_box_x, FAIL_Y, fail_w, SH_box, "MigrationFailed", FAIL_FILL, FAIL_STROKE)}

<!-- End circles -->
{end_circle(cx, END_SUCC_Y)}
{end_circle(fail_cx, END_FAIL_Y)}

<!-- Main path arrows -->
{v_arrow(cx, START_Y+14, cx, UNSET_Y, "建立 Migration CR")}
{v_arrow(cx, UNSET_Y+SH_box, cx, PEND_Y, "VMI 可遷移")}
{v_arrow(cx, PEND_Y+SH_box, cx, SCHED_ING_Y, "Target Pod 已建立")}
{v_arrow(cx, SCHED_ING_Y+SH_box, cx, SCHED_ED_Y, "Target Pod Ready")}
{v_arrow(cx, SCHED_ED_Y+SH_box, cx, PREP_Y, "VMI 進入 PreparingTarget")}
{v_arrow(cx, PREP_Y+SH_box, cx, READY_Y, "目標 Domain 準備完成")}
{v_arrow(cx, READY_Y+SH_box, cx, RUN_Y, "遷移開始執行")}
{v_arrow(cx, RUN_Y+SH_box, cx, SUCC_Y, "資料傳輸完成")}
{v_arrow(cx, SUCC_Y+SH_box, cx, END_SUCC_Y-16, "")}

<!-- Fail arrows from each state -->
<!-- Unset -> Failed: VMI 不可遷移 -->
<path d="M {cx_box+SW} {UNSET_Y+SH_box//2} L {fail_box_x} {FAIL_Y+SH_box//2}" stroke="#f97316" stroke-width="2" fill="none" marker-end="url(#arrow-fail)"/>
<text x="{(cx_box+SW+fail_box_x)//2}" y="{UNSET_Y+SH_box//2-8}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#f97316">VMI 不可遷移</text>

<!-- Scheduling -> Failed: Pod 排程失敗 -->
<path d="M {cx_box+SW} {SCHED_ING_Y+SH_box//2} C {fail_cx} {SCHED_ING_Y+SH_box//2}, {fail_cx} {SCHED_ING_Y+SH_box//2+40}, {fail_cx} {FAIL_Y}" stroke="#f97316" stroke-width="2" fill="none" marker-end="url(#arrow-fail)"/>
<text x="{cx_box+SW+60}" y="{SCHED_ING_Y+SH_box//2-8}" text-anchor="start" font-family="{FONT}" font-size="11" fill="#f97316">Pod 排程失敗</text>

<!-- Scheduled -> Failed: 超時或錯誤 -->
<path d="M {cx_box+SW} {SCHED_ED_Y+SH_box//2} C {fail_cx} {SCHED_ED_Y+SH_box//2}, {fail_cx} {SCHED_ED_Y+SH_box//2+40}, {fail_cx} {FAIL_Y}" stroke="#f97316" stroke-width="2" fill="none" marker-end="url(#arrow-fail)"/>
<text x="{cx_box+SW+60}" y="{SCHED_ED_Y+SH_box//2-8}" text-anchor="start" font-family="{FONT}" font-size="11" fill="#f97316">超時或錯誤</text>

<!-- PreparingTarget -> Failed -->
<path d="M {cx_box+SW} {PREP_Y+SH_box//2} L {fail_box_x} {FAIL_Y+SH_box}" stroke="#f97316" stroke-width="2" fill="none" marker-end="url(#arrow-fail)"/>
<text x="{cx_box+SW+60}" y="{PREP_Y+SH_box//2-8}" text-anchor="start" font-family="{FONT}" font-size="11" fill="#f97316">準備失敗</text>

<!-- TargetReady -> Failed -->
<path d="M {cx_box+SW} {READY_Y+SH_box//2} C {fail_cx+60} {READY_Y+SH_box//2}, {fail_cx+60} {FAIL_Y+SH_box+30}, {fail_cx+fail_w//2} {FAIL_Y+SH_box}" stroke="#f97316" stroke-width="2" fill="none" marker-end="url(#arrow-fail)"/>
<text x="{cx_box+SW+60}" y="{READY_Y+SH_box//2-8}" text-anchor="start" font-family="{FONT}" font-size="11" fill="#f97316">啟動失敗</text>

<!-- Running -> Failed -->
<path d="M {cx_box+SW} {RUN_Y+SH_box//2} C {fail_cx+100} {RUN_Y+SH_box//2}, {fail_cx+100} {FAIL_Y+SH_box+60}, {fail_cx+fail_w//2} {FAIL_Y+SH_box}" stroke="#f97316" stroke-width="2" fill="none" marker-end="url(#arrow-fail)"/>
<text x="{cx_box+SW+60}" y="{RUN_Y+SH_box//2-8}" text-anchor="start" font-family="{FONT}" font-size="11" fill="#f97316">遷移逾時/錯誤</text>

<!-- Failed -> end -->
{v_arrow(fail_cx, FAIL_Y+SH_box, fail_cx, END_FAIL_Y-16, "", fail=True)}

<!-- Title -->
<text x="{W//2}" y="{H-20}" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">VirtualMachineInstanceMigration 狀態機</text>
</svg>'''

out = "/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-state-machine.svg"
with open(out, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f"Written: {out}")
