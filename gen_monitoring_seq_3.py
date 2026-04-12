#!/usr/bin/env python3
"""monitoring-metricsdocs-flow-3: metricsdocs sequence diagram"""

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
LOOP_FILL = "#fef9f0"
LOOP_STROKE = "#fcd34d"
ARROW = "#3b82f6"
ARROW_RETURN = "#94a3b8"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 960, 680

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# Participants x positions
parts = {
    "Main": 120,
    "Git": 280,
    "Parser": 440,
    "Template": 600,
    "GH": 760,
}
part_labels = {
    "Main": "main()",
    "Git": "git.go",
    "Parser": "parseMetrics",
    "Template": "metrics.tmpl",
    "GH": "GitHub API",
}

svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="{ARROW}"/>
  </marker>
  <marker id="arr_ret" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="{ARROW_RETURN}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>''']

# Draw participant boxes
for name, px in parts.items():
    lbl = part_labels[name]
    svg.append(f'<rect x="{px-60}" y="20" width="120" height="44" rx="8" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.5"/>')
    svg.append(f'<text x="{px}" y="47" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{TEXT_PRIMARY}" font-weight="600">{esc(lbl)}</text>')

# Lifelines (dashed vertical lines)
for name, px in parts.items():
    svg.append(f'<line x1="{px}" y1="64" x2="{px}" y2="{H-30}" stroke="{BOX_STROKE}" stroke-width="1" stroke-dasharray="4,4"/>')

def msg(from_p, to_p, y, label, line2=None, ret=False, self_msg=False):
    x1 = parts[from_p]
    x2 = parts[to_p]
    color = ARROW_RETURN if ret else ARROW
    marker = "url(#arr_ret)" if ret else "url(#arr)"
    dash = 'stroke-dasharray="6,3"' if ret else ""
    lines = []
    if self_msg or from_p == to_p:
        # self-arrow
        lines.append(f'<path d="M{x1},{y} L{x1+40},{y} L{x1+40},{y+28} L{x1+2},{y+28}" stroke="{color}" stroke-width="1.5" fill="none" {dash} marker-end="{marker}"/>')
        lines.append(f'<text x="{x1+46}" y="{y+14}" text-anchor="start" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">{esc(label)}</text>')
        if line2:
            lines.append(f'<text x="{x1+46}" y="{y+28}" text-anchor="start" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(line2)}</text>')
    else:
        lines.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1.5" {dash} marker-end="{marker}"/>')
        mx = (x1+x2)//2
        lines.append(f'<text x="{mx}" y="{y-5}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT_PRIMARY}">{esc(label)}</text>')
        if line2:
            lines.append(f'<text x="{mx}" y="{y+11}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(line2)}</text>')
    return "\n".join(lines)

def loop_box(x1, x2, y1, y2, label):
    return f'''<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="6" fill="{LOOP_FILL}" stroke="{LOOP_STROKE}" stroke-width="1" stroke-dasharray="5,3"/>
<rect x="{x1}" y="{y1}" width="48" height="18" rx="4" fill="{LOOP_STROKE}"/>
<text x="{x1+24}" y="{y1+13}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="white" font-weight="600">loop</text>
<text x="{x1+58}" y="{y1+13}" text-anchor="start" font-family="{FONT}" font-size="10" fill="{TEXT_SECONDARY}">{esc(label)}</text>'''

# Sequence events
y = 90
# Main parseArguments (self)
svg.append(msg("Main", "Main", y, "parseArguments()", "讀取 --config-file, --cache-dir", self_msg=True))
y += 50
# Main → Git: checkoutProjects()
svg.append(msg("Main", "Git", y, "checkoutProjects()"))
y += 20
# Loop: 每個專案
loop1_y1 = y + 10
y += 30
svg.append(msg("Git", "Git", y, "gitCheckoutUpstream()", "clone 或 pull", self_msg=True))
y += 50
svg.append(msg("Git", "Git", y, "gitSwitchToBranch(version)", self_msg=True))
y += 45
loop1_y2 = y
svg.append(loop_box(parts["Git"]-80, parts["Git"]+80, loop1_y1, loop1_y2, "每個專案"))
y += 20
# Main → Parser
svg.append(msg("Main", "Parser", y, "parseMetrics()"))
y += 20
# Loop: 每個專案
loop2_y1 = y + 10
y += 30
svg.append(msg("Parser", "Parser", y, "readLines(metricsDocPath)", self_msg=True))
y += 50
svg.append(msg("Parser", "Parser", y, "parseMetricsDoc(content)", "解析 markdown 表格", self_msg=True))
y += 50
loop2_y2 = y
svg.append(loop_box(parts["Parser"]-80, parts["Parser"]+80, loop2_y1, loop2_y2, "每個專案"))
y += 20
# Main writeMetrics (self)
svg.append(msg("Main", "Main", y, "writeMetrics(metrics)", self_msg=True))
y += 50
svg.append(msg("Main", "Main", y, "sortMetrics()", "kubevirt 排首位", self_msg=True))
y += 50
# Loop: 每個 operator
loop3_y1 = y + 10
y += 30
svg.append(msg("Main", "GH", y, "HTTP GET release info / 建立連結"))
y += 30
loop3_y2 = y + 10
svg.append(loop_box(parts["Main"]-80, parts["GH"]+80, loop3_y1, loop3_y2, "每個 operator"))
y += 30
# Main → Template
svg.append(msg("Main", "Template", y, "Execute(templateData)"))
y += 30
# Template -->> Main
svg.append(msg("Template", "Main", y, "寫入 docs/metrics.md", ret=True))

svg.append('</svg>')
out = "docs-site/public/diagrams/monitoring/monitoring-metricsdocs-flow-3.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print(f"Written: {out}")
