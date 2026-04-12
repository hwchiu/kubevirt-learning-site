#!/usr/bin/env python3
"""Migration internals diagram 7: Full migration sequence diagram"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
NOTE_FILL = "#fef9c3"
NOTE_STROKE = "#fde68a"
ALT_FILL = "#f0fdf4"
ALT_STROKE = "#86efac"
ALT_FAIL = "#fef2f2"

W, H = 1100, 1020

# Participants: User, API, MC, SH, TH, SL, TL
PARTS = [
    (80,  "User", "使用者"),
    (210, "API", "K8s API"),
    (340, "MC", "Migration\nController"),
    (470, "SH", "virt-handler\n(Source)"),
    (600, "TH", "virt-handler\n(Target)"),
    (730, "SL", "virt-launcher\n(Source)"),
    (870, "TL", "virt-launcher\n(Target)"),
]

def marker():
    return f'<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="8" refY="3.5" orient="auto"><polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{ARROW}"/></marker></defs>'

def participant(x, short, label):
    bw, bh = 100, 50
    lines_text = label.split('\n')
    result = [f'<rect x="{x-bw//2}" y="30" width="{bw}" height="{bh}" rx="6" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>']
    if len(lines_text) == 2:
        result.append(f'<text x="{x}" y="51" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="700" fill="{TEXT_PRIMARY}">{lines_text[0]}</text>')
        result.append(f'<text x="{x}" y="67" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{lines_text[1]}</text>')
    else:
        result.append(f'<text x="{x}" y="59" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(result)

def lifeline(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>'

def msg(x1, y, x2, label="", num=None):
    line = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{ARROW}" stroke-width="1.5" marker-end="url(#arr)"/>'
    parts = [line]
    mx = (x1+x2)//2
    if num:
        parts.append(f'<text x="{min(x1,x2)+5}" y="{y-5}" font-family="{FONT}" font-size="9" font-weight="700" fill="{ARROW}">{num}.</text>')
    if label:
        parts.append(f'<text x="{mx}" y="{y-6}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">{label}</text>')
    return '\n'.join(parts)

def note_phase(y, label):
    return f'''<rect x="40" y="{y}" width="{W-80}" height="22" rx="4" fill="{NOTE_FILL}" stroke="{NOTE_STROKE}" stroke-width="1"/>
<text x="{W//2}" y="{y+15}" text-anchor="middle" font-family="{FONT}" font-size="10" font-weight="600" fill="#92400e">{label}</text>'''

def loop_box(y1, y2, label):
    return f'''<rect x="40" y="{y1}" width="{W-80}" height="{y2-y1}" rx="4" fill="none" stroke="{ARROW}" stroke-width="1" stroke-dasharray="4,3"/>
<rect x="40" y="{y1}" width="80" height="18" rx="3" fill="{ARROW}"/>
<text x="50" y="{y1+13}" font-family="{FONT}" font-size="10" font-weight="700" fill="white">{label}</text>'''

def alt_box(y1, y2, label, fill=ALT_FILL):
    return f'''<rect x="40" y="{y1}" width="{W-80}" height="{y2-y1}" rx="4" fill="{fill}" stroke="#86efac" stroke-width="1"/>
<rect x="40" y="{y1}" width="50" height="16" rx="3" fill="#22c55e"/>
<text x="46" y="{y1+12}" font-family="{FONT}" font-size="9" font-weight="700" fill="white">{label}</text>'''

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    marker(),
    f'<text x="{W//2}" y="20" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="{TEXT_PRIMARY}">Complete Migration Sequence</text>',
]

for x, short, label in PARTS:
    svg.append(participant(x, short, label))
    svg.append(lifeline(x, 80, H-30))

# Message sequence
px = {p[1]: p[0] for p in PARTS}
y = 105

# 1. User → API
svg.append(msg(px["User"], y, px["API"], "建立 VirtualMachineInstanceMigration", num=1)); y += 30
# 2. API → MC (watch)
svg.append(msg(px["API"], y, px["MC"], "Watch 事件", num=2)); y += 30

svg.append(note_phase(y, "Phase: Unset → Pending")); y += 30
# 3. MC → MC (validate)
svg.append(f'<path d="M{px["MC"]},{y} C{px["MC"]+60},{y} {px["MC"]+60},{y+22} {px["MC"]},{y+22}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
svg.append(f'<text x="{px["MC"]+64}" y="{y+15}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">3. 驗證 VMI 可遷移性</text>'); y += 38
# 4. MC → API
svg.append(msg(px["MC"], y, px["API"], "4. 建立 Target Pod")); y += 30

svg.append(note_phase(y, "Phase: Pending → Scheduling")); y += 28
# 5. API → TH
svg.append(msg(px["API"], y, px["TH"], "5. Target Pod 排程到目標節點")); y += 28
# TH self
svg.append(f'<path d="M{px["TH"]},{y} C{px["TH"]+60},{y} {px["TH"]+60},{y+20} {px["TH"]},{y+20}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
svg.append(f'<text x="{px["TH"]+64}" y="{y+14}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">偵測到 Migration Target Pod</text>'); y += 32

svg.append(note_phase(y, "Phase: Scheduling → Scheduled")); y += 28
# 6. TH → API
svg.append(msg(px["TH"], y, px["API"], "6. 更新 VMI: PreparingTarget")); y += 28

svg.append(note_phase(y, "Phase: Scheduled → PreparingTarget")); y += 28
# 7. TH → TL
svg.append(msg(px["TH"], y, px["TL"], "7. 啟動 Target virt-launcher")); y += 28
# TL self
svg.append(f'<path d="M{px["TL"]},{y} C{px["TL"]+60},{y} {px["TL"]+60},{y+20} {px["TL"]},{y+20}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
svg.append(f'<text x="{px["TL"]+64}" y="{y+14}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">定義 Domain + Unix Socket</text>'); y += 32
# TH setup proxy
svg.append(f'<path d="M{px["TH"]},{y} C{px["TH"]+50},{y} {px["TH"]+50},{y+18} {px["TH"]},{y+18}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
svg.append(f'<text x="{px["TH"]+54}" y="{y+13}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">啟動 Target Migration Proxy</text>'); y += 28
# TH → API
svg.append(msg(px["TH"], y, px["API"], "回報 TCP Ports")); y += 28

svg.append(note_phase(y, "Phase: PreparingTarget → TargetReady")); y += 28
# API → SH
svg.append(msg(px["API"], y, px["SH"], "VMI 狀態更新：TargetReady")); y += 28
# SH setup proxy
svg.append(f'<path d="M{px["SH"]},{y} C{px["SH"]+50},{y} {px["SH"]+50},{y+18} {px["SH"]},{y+18}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
svg.append(f'<text x="{px["SH"]+54}" y="{y+13}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">啟動 Source Migration Proxy</text>'); y += 28
# SH → SL
svg.append(msg(px["SH"], y, px["SL"], "通知開始遷移")); y += 28

svg.append(note_phase(y, "Phase: TargetReady → Running")); y += 28
# SL self ops
for op in ["generateMigrationFlags()", "generateMigrationParams()", "dom.MigrateToURI3()"]:
    svg.append(f'<path d="M{px["SL"]},{y} C{px["SL"]+55},{y} {px["SL"]+55},{y+18} {px["SL"]},{y+18}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
    svg.append(f'<text x="{px["SL"]+58}" y="{y+13}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">{op}</text>')
    y += 26

# Loop pre-copy
loop_y1 = y
svg.append(msg(px["SL"], y, px["TL"], "記憶體頁面傳輸（經由 Proxy）", num=None)); y += 26
svg.append(f'<path d="M{px["SL"]},{y} C{px["SL"]+55},{y} {px["SL"]+55},{y+18} {px["SL"]},{y+18}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
svg.append(f'<text x="{px["SL"]+58}" y="{y+13}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">dom.GetJobStats() 監控進度</text>'); y += 26
loop_y2 = y
svg.append(loop_box(loop_y1 - 4, loop_y2, "loop Pre-copy")); y += 10

# Alt: success
alt1_y1 = y
svg.append(msg(px["SL"], y+8, px["API"], "MigrationState.Completed = true")); y += 26
svg.append(note_phase(y, "Phase: Running → Succeeded")); y += 22
svg.append(msg(px["MC"], y, px["API"], "刪除 Source Pod")); y += 26
alt1_y2 = y

# Alt: post-copy
svg.append(msg(px["SL"], y+8, px["SL"]+55, "")); 
svg.append(f'<path d="M{px["SL"]},{y+8} C{px["SL"]+55},{y+8} {px["SL"]+55},{y+26} {px["SL"]},{y+26}" stroke="{ARROW}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>')
svg.append(f'<text x="{px["SL"]+58}" y="{y+20}" font-family="{FONT}" font-size="10" fill="{TEXT_PRIMARY}">dom.MigrateStartPostCopy(0)</text>'); y += 30
svg.append(msg(px["SL"], y, px["TL"], "Post-copy: 按需傳送頁面")); y += 26
svg.append(msg(px["SL"], y, px["API"], "MigrationState.Completed = true")); y += 26
alt2_y2 = y

# Alt: fail
svg.append(msg(px["SL"], y+4, px["API"], "MigrationState.Failed = true")); y += 26
svg.append(note_phase(y, "Phase: Running → Failed")); y += 22
svg.append(msg(px["MC"], y, px["API"], "刪除 Target Pod")); y += 26
alt3_y2 = y

# Draw alt boxes (underneath the messages)
svg.insert(-30, alt_box(alt1_y1, alt1_y2, "alt 成功", ALT_FILL))
svg.insert(-20, alt_box(alt1_y2, alt2_y2, "alt 超時+PostCopy", "#fefce8"))
svg.insert(-10, alt_box(alt2_y2, alt3_y2, "alt 失敗", ALT_FAIL))

svg.append('</svg>')
out = '/Users/hwchiu/hwchiu/code/kubevirt-learning-site/docs-site/public/diagrams/kubevirt/kubevirt-migration-7.svg'
with open(out, 'w') as f:
    f.write('\n'.join(svg))
print(f"Written: {out}")
