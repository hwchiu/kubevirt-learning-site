#!/usr/bin/env python3
"""Generate static diagrams for the etcd chapter."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs-site" / "public" / "diagrams" / "etcd"
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"

BG = "#ffffff"
TEXT = "#111827"
SUBT = "#6b7280"
BLUE = "#2563eb"
BLUE_FILL = "#eff6ff"
BLUE_STROKE = "#93c5fd"
GREEN_FILL = "#ecfdf5"
GREEN_STROKE = "#86efac"
AMBER_FILL = "#fffbeb"
AMBER_STROKE = "#fcd34d"
RED_FILL = "#fef2f2"
RED_STROKE = "#fca5a5"
GRAY_FILL = "#f8fafc"
GRAY_STROKE = "#cbd5e1"
PURPLE_FILL = "#f5f3ff"
PURPLE_STROKE = "#c4b5fd"


def wrap_svg(body: str, viewbox: str, marker_ids: tuple[str, ...] = ("arrow",)) -> str:
    markers = []
    for marker_id in marker_ids:
        color = BLUE
        if marker_id == "arrow-green":
            color = "#059669"
        elif marker_id == "arrow-amber":
            color = "#d97706"
        markers.append(
            f'''
    <marker id="{marker_id}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0.5, 9 3.5, 0 6.5" fill="{color}"/>
    </marker>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">
  <defs>{"".join(markers)}
  </defs>
  <rect width="100%" height="100%" fill="{BG}"/>
  {body}
</svg>
'''


def text(x: int, y: int, value: str, size: int = 13, weight: str = "400", fill: str = TEXT, anchor: str = "middle") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{value}</text>'
    )


def rect(x: int, y: int, w: int, h: int, fill: str, stroke: str, rx: int = 12, sw: float = 2) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def line(x1: int, y1: int, x2: int, y2: int, marker: str = "arrow", color: str = BLUE, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="8 6"' if dashed else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3"'
        f'{dash} marker-end="url(#{marker})"/>'
    )


def save_svg(name: str, svg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    svg_path = OUT / f"{name}.svg"
    png_path = OUT / f"{name}.png"
    svg_path.write_text(svg, encoding="utf-8")
    subprocess.run(
        ["rsvg-convert", "-o", str(png_path), str(svg_path)],
        check=True,
        cwd=ROOT,
    )


def gen_overview() -> None:
    body = f'''
  {text(660, 36, "Role of etcd in Kubernetes", 24, "700")}
  {text(660, 62, "All API server state eventually lands in etcd and is protected by Raft replication", 13, "400", SUBT)}

  {rect(80, 110, 210, 90, BLUE_FILL, BLUE_STROKE)}
  {text(185, 145, "kube-apiserver", 18, "700")}
  {text(185, 168, "CRUD / Watch / Lease / Event", 12, "400", SUBT)}
  {text(185, 186, "Primary write path", 12, "400", SUBT)}

  {rect(360, 95, 850, 355, GRAY_FILL, GRAY_STROKE, 20)}
  {text(785, 128, "Primary etcd Raft Cluster", 20, "700")}
  {text(785, 150, "Five-member production example: one leader, four voters, quorum 3/5", 12, "400", SUBT)}

  {rect(405, 190, 190, 92, AMBER_FILL, AMBER_STROKE)}
  {text(500, 223, "Leader", 18, "700")}
  {text(500, 246, "Accepts writes", 12, "400", SUBT)}
  {text(500, 264, "Replicates Raft log", 12, "400", SUBT)}

  {rect(580, 320, 140, 90, GREEN_FILL, GREEN_STROKE)}
  {text(650, 352, "Follower", 17, "700")}
  {text(650, 375, "voter", 12, "400", SUBT)}
  {text(650, 393, "Quorum path", 12, "400", SUBT)}

  {rect(740, 320, 140, 90, GREEN_FILL, GREEN_STROKE)}
  {text(810, 352, "Follower", 17, "700")}
  {text(810, 375, "voter", 12, "400", SUBT)}
  {text(810, 393, "Quorum path", 12, "400", SUBT)}

  {rect(900, 320, 140, 90, GREEN_FILL, GREEN_STROKE)}
  {text(970, 352, "Follower", 17, "700")}
  {text(970, 375, "voter", 12, "400", SUBT)}
  {text(970, 393, "Quorum path", 12, "400", SUBT)}

  {rect(1060, 320, 120, 90, GREEN_FILL, GREEN_STROKE)}
  {text(1120, 352, "Follower", 17, "700")}
  {text(1120, 375, "voter", 12, "400", SUBT)}
  {text(1120, 393, "Quorum path", 12, "400", SUBT)}

  {line(290, 155, 405, 225)}
  {text(348, 140, "gRPC / MVCC", 11, "400", SUBT)}
  {line(500, 282, 635, 320)}
  {line(520, 282, 795, 320)}
  {line(545, 282, 955, 320)}
  {line(565, 282, 1115, 320)}
  {text(618, 297, "raft log", 11, "400", SUBT)}
  {text(760, 297, "raft log", 11, "400", SUBT)}
  {text(920, 297, "raft log", 11, "400", SUBT)}
  {text(1080, 297, "raft log", 11, "400", SUBT)}

  {rect(110, 295, 180, 120, PURPLE_FILL, PURPLE_STROKE)}
  {text(200, 328, "Watchers / Controllers", 16, "700")}
  {text(200, 350, "kube-controller-manager", 11, "400", SUBT)}
  {text(200, 367, "scheduler / operators", 11, "400", SUBT)}
  {text(200, 390, "Observe state via API server", 11, "400", SUBT)}

  {line(200, 295, 200, 200, "arrow-green", "#059669")}
  {text(225, 248, "Watch / List", 11, "400", SUBT, "start")}

  {rect(120, 510, 1080, 160, GRAY_FILL, GRAY_STROKE, 20)}
  {text(660, 545, "Chapter Focus", 18, "700")}

  {rect(160, 575, 235, 68, BLUE_FILL, BLUE_STROKE)}
  {text(278, 603, "Defrag / Compact", 16, "700")}
  {text(278, 624, "MVCC space reclamation and disk size", 11, "400", SUBT)}

  {rect(425, 575, 235, 68, BLUE_FILL, BLUE_STROKE)}
  {text(543, 603, "Kubernetes Operations", 16, "700")}
  {text(543, 624, "One-member-at-a-time defrag and control-plane impact", 11, "400", SUBT)}

  {rect(690, 575, 250, 68, BLUE_FILL, BLUE_STROKE)}
  {text(815, 603, "Learner Mode", 16, "700")}
  {text(815, 624, "Sync data first, change the voting set later", 11, "400", SUBT)}

  {rect(965, 575, 200, 68, BLUE_FILL, BLUE_STROKE)}
  {text(1065, 603, "Production Shape", 16, "700")}
  {text(1065, 624, "Five voters as the default mental model", 11, "400", SUBT)}
'''
    save_svg("etcd-overview-1", wrap_svg(body, "0 0 1280 700", ("arrow", "arrow-green")))


def gen_defrag() -> None:
    body = f'''
  {text(600, 36, "Compaction vs Defrag: Space Semantics", 24, "700")}
  {text(600, 62, "in-use drops after compaction; physical db size drops after defrag", 13, "400", SUBT)}

  {rect(70, 110, 300, 250, GRAY_FILL, GRAY_STROKE, 18)}
  {text(220, 142, "Phase 1: Writes and historical revision buildup", 18, "700")}
  {rect(120, 180, 200, 120, AMBER_FILL, AMBER_STROKE)}
  {text(220, 212, "bbolt DB file", 16, "700")}
  {text(220, 236, "Used pages + old revisions", 12, "400", SUBT)}
  {text(220, 255, "db_total_size grows", 12, "400", SUBT)}
  {text(220, 274, "db_total_size_in_use also grows", 12, "400", SUBT)}

  {rect(430, 110, 330, 250, GRAY_FILL, GRAY_STROKE, 18)}
  {text(595, 142, "Phase 2: Compact", 18, "700")}
  {rect(485, 180, 220, 120, BLUE_FILL, BLUE_STROKE)}
  {text(595, 212, "Old revisions are removed", 16, "700")}
  {text(595, 236, "Pages become reusable free pages", 12, "400", SUBT)}
  {text(595, 255, "db_total_size_in_use drops", 12, "400", SUBT)}
  {text(595, 274, "db_total_size barely changes", 12, "400", SUBT)}

  {rect(820, 110, 310, 250, GRAY_FILL, GRAY_STROKE, 18)}
  {text(975, 142, "Phase 3: Defrag", 18, "700")}
  {rect(875, 180, 200, 120, GREEN_FILL, GREEN_STROKE)}
  {text(975, 212, "Rewrite into a new DB file", 16, "700")}
  {text(975, 236, "Keep only live data", 12, "400", SUBT)}
  {text(975, 255, "db_total_size drops", 12, "400", SUBT)}
  {text(975, 274, "Free pages finally return to the filesystem", 12, "400", SUBT)}

  {line(320, 240, 485, 240)}
  {line(705, 240, 875, 240)}

  {rect(120, 420, 1010, 180, PURPLE_FILL, PURPLE_STROKE, 18)}
  {text(625, 455, "Two Metrics Commonly Watched in Kubernetes", 18, "700")}

  {rect(170, 490, 420, 75, BLUE_FILL, BLUE_STROKE)}
  {text(380, 520, "etcd_mvcc_db_total_size_in_use_in_bytes", 15, "700")}
  {text(380, 544, "Logical size still used by live data", 12, "400", SUBT)}

  {rect(660, 490, 420, 75, GREEN_FILL, GREEN_STROKE)}
  {text(870, 520, "etcd_mvcc_db_total_size_in_bytes", 15, "700")}
  {text(870, 544, "Physical disk size of the DB file", 12, "400", SUBT)}

  {text(380, 590, "Compaction mainly affects this value", 12, "700", "#1d4ed8")}
  {text(870, 590, "Defrag mainly affects this value", 12, "700", "#047857")}
'''
    save_svg("etcd-defrag-1", wrap_svg(body, "0 0 1200 640"))


def gen_defrag_pages() -> None:
    body = f'''
  {text(640, 36, "What Happens Inside the bbolt File", 24, "700")}
  {text(640, 62, "Compaction frees logical space inside the file; defrag rebuilds the file and shrinks it", 13, "400", SUBT)}

  {rect(40, 105, 380, 400, GRAY_FILL, GRAY_STROKE, 20)}
  {text(230, 138, "Stage 1: Before Compaction", 19, "700")}
  {rect(100, 180, 260, 250, "#fff7ed", "#fdba74", 10)}
  {rect(120, 205, 220, 36, "#fca5a5", "#ef4444", 8)}
  {text(230, 228, "Live pages", 14, "700")}
  {rect(120, 252, 220, 36, "#fde68a", "#f59e0b", 8)}
  {text(230, 275, "Old revisions", 14, "700")}
  {rect(120, 299, 220, 36, "#fde68a", "#f59e0b", 8)}
  {text(230, 322, "Old revisions", 14, "700")}
  {rect(120, 346, 220, 36, "#fca5a5", "#ef4444", 8)}
  {text(230, 369, "Live pages", 14, "700")}
  {text(230, 458, "The file is large because it holds both current data and historical versions", 12, "400", SUBT)}

  {rect(450, 105, 380, 400, GRAY_FILL, GRAY_STROKE, 20)}
  {text(640, 138, "Stage 2: After Compaction", 19, "700")}
  {rect(510, 180, 260, 250, "#eff6ff", "#93c5fd", 10)}
  {rect(530, 205, 220, 36, "#fca5a5", "#ef4444", 8)}
  {text(640, 228, "Live pages", 14, "700")}
  {rect(530, 252, 220, 36, "#dcfce7", "#22c55e", 8)}
  {text(640, 275, "Free reusable pages", 14, "700")}
  {rect(530, 299, 220, 36, "#dcfce7", "#22c55e", 8)}
  {text(640, 322, "Free reusable pages", 14, "700")}
  {rect(530, 346, 220, 36, "#fca5a5", "#ef4444", 8)}
  {text(640, 369, "Live pages", 14, "700")}
  {text(640, 458, "Compaction removes old revisions, but the file keeps the same outer size", 12, "400", SUBT)}

  {rect(860, 105, 380, 400, GRAY_FILL, GRAY_STROKE, 20)}
  {text(1050, 138, "Stage 3: After Defrag", 19, "700")}
  {rect(940, 205, 220, 130, "#ecfdf5", "#86efac", 10)}
  {rect(960, 228, 180, 36, "#fca5a5", "#ef4444", 8)}
  {text(1050, 251, "Live pages", 14, "700")}
  {rect(960, 275, 180, 36, "#fca5a5", "#ef4444", 8)}
  {text(1050, 298, "Live pages", 14, "700")}
  {text(1050, 370, "Defrag copies only live pages into a new file", 12, "400", SUBT)}
  {text(1050, 392, "The free holes disappear and the file becomes smaller", 12, "400", SUBT)}

  {line(360, 307, 530, 307)}
  {line(750, 307, 940, 270)}
'''
    save_svg("etcd-defrag-2", wrap_svg(body, "0 0 1280 540"))


def gen_defrag_metrics() -> None:
    body = f'''
  {text(640, 36, "How the Metrics Move", 24, "700")}
  {text(640, 62, "Compaction and defrag change different metrics, so the curves do not move together", 13, "400", SUBT)}

  {rect(70, 110, 1150, 450, GRAY_FILL, GRAY_STROKE, 20)}
  <line x1="150" y1="490" x2="1150" y2="490" stroke="{TEXT}" stroke-width="2"/>
  <line x1="150" y1="490" x2="150" y2="150" stroke="{TEXT}" stroke-width="2"/>
  {text(650, 525, "time", 14, "700")}
  {text(105, 320, "size", 14, "700")}

  <polyline fill="none" stroke="#2563eb" stroke-width="5"
    points="180,260 300,250 430,245 570,335 750,330 930,220 1110,215"/>
  <polyline fill="none" stroke="#059669" stroke-width="5"
    points="180,220 300,210 430,205 570,205 750,200 930,335 1110,330"/>

  <line x1="560" y1="170" x2="560" y2="490" stroke="#94a3b8" stroke-width="2" stroke-dasharray="8 6"/>
  <line x1="920" y1="170" x2="920" y2="490" stroke="#94a3b8" stroke-width="2" stroke-dasharray="8 6"/>
  {text(560, 155, "Compaction", 14, "700")}
  {text(920, 155, "Defrag", 14, "700")}

  {rect(760, 185, 300, 90, BLUE_FILL, BLUE_STROKE)}
  {text(910, 215, "Blue: db_total_size_in_use", 15, "700")}
  {text(910, 238, "Drops when old revisions are removed", 12, "400", SUBT)}
  {text(910, 260, "Compaction changes logical usage first", 12, "400", SUBT)}

  {rect(760, 310, 300, 90, GREEN_FILL, GREEN_STROKE)}
  {text(910, 340, "Green: db_total_size", 15, "700")}
  {text(910, 363, "Drops only after the file is rewritten", 12, "400", SUBT)}
  {text(910, 385, "Defrag changes physical disk usage", 12, "400", SUBT)}

  {text(300, 190, "Both metrics grow while writes accumulate", 12, "400", SUBT)}
  {text(630, 360, "Gap widens after compaction", 12, "700", "#1d4ed8")}
  {text(995, 355, "Gap narrows after defrag", 12, "700", "#047857")}
'''
    save_svg("etcd-defrag-3", wrap_svg(body, "0 0 1280 590"))


def gen_k8s_defrag() -> None:
    body = f'''
  {text(700, 36, "Operational Flow of etcd Defrag in Kubernetes", 24, "700")}
  {text(700, 62, "Five-member production example: one member stalls, four members preserve service and quorum margin", 13, "400", SUBT)}

  {rect(60, 120, 220, 100, BLUE_FILL, BLUE_STROKE)}
  {text(170, 154, "kube-apiserver", 18, "700")}
  {text(170, 178, "Continuously reads and writes etcd", 12, "400", SUBT)}
  {text(170, 196, "CRUD / Watch / Lease", 12, "400", SUBT)}

  {rect(340, 100, 1060, 220, GRAY_FILL, GRAY_STROKE, 20)}
  {text(870, 132, "Five-Member etcd Cluster", 20, "700")}
  {text(870, 154, "Production-style maintenance view: quorum stays 3/5 while one member is being defragged", 12, "400", SUBT)}

  {rect(390, 205, 165, 80, AMBER_FILL, AMBER_STROKE)}
  {text(472, 236, "Member A", 17, "700")}
  {text(472, 258, "defrag in progress", 12, "400", SUBT)}

  {rect(580, 205, 165, 80, GREEN_FILL, GREEN_STROKE)}
  {text(662, 236, "Member B", 17, "700")}
  {text(662, 258, "serving traffic", 12, "400", SUBT)}

  {rect(770, 205, 165, 80, GREEN_FILL, GREEN_STROKE)}
  {text(852, 236, "Member C", 17, "700")}
  {text(852, 258, "serving traffic", 12, "400", SUBT)}

  {rect(960, 205, 165, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1042, 236, "Member D", 17, "700")}
  {text(1042, 258, "serving traffic", 12, "400", SUBT)}

  {rect(1150, 205, 165, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1232, 236, "Member E", 17, "700")}
  {text(1232, 258, "serving traffic", 12, "400", SUBT)}

  {line(280, 170, 390, 225)}
  {line(280, 170, 580, 225, "arrow-green", "#059669", True)}
  {line(280, 170, 770, 225, "arrow-green", "#059669", True)}
  {line(280, 170, 960, 225, "arrow-green", "#059669", True)}
  {line(280, 170, 1150, 225, "arrow-green", "#059669", True)}
  {text(350, 154, "Requests can feel A's stall, but the remaining four members keep the cluster available", 11, "400", SUBT, "start")}

  {rect(80, 385, 1240, 220, PURPLE_FILL, PURPLE_STROKE, 20)}
  {text(700, 420, "Recommended Operational Sequence", 19, "700")}

  {rect(110, 460, 250, 95, BLUE_FILL, BLUE_STROKE)}
  {text(235, 490, "1. Check Metrics First", 16, "700")}
  {text(235, 514, "Compare in-use vs db size", 11, "400", SUBT)}
  {text(235, 532, "Verify that defrag is worth it", 11, "400", SUBT)}

  {rect(395, 460, 250, 95, AMBER_FILL, AMBER_STROKE)}
  {text(520, 490, "2. Defrag One Member", 16, "700")}
  {text(520, 514, "Run etcdctl defrag against one member", 11, "400", SUBT)}
  {text(520, 532, "Keep the other four stable", 11, "400", SUBT)}

  {rect(680, 460, 250, 95, GREEN_FILL, GREEN_STROKE)}
  {text(805, 490, "3. Observe Recovery", 16, "700")}
  {text(805, 514, "Wait for defrag_inflight to return to 0", 11, "400", SUBT)}
  {text(805, 532, "Confirm db_total_size decreases", 11, "400", SUBT)}

  {rect(965, 460, 250, 95, RED_FILL, RED_STROKE)}
  {text(1090, 490, "4. Move to the Next Member", 16, "700")}
  {text(1090, 514, "Avoid control-plane peak periods", 11, "400", SUBT)}
  {text(1090, 532, "Preserve quorum and latency margin", 11, "400", SUBT)}

  {line(360, 508, 395, 508)}
  {line(645, 508, 680, 508)}
  {line(930, 508, 965, 508)}
'''
    save_svg("etcd-kubernetes-defrag-1", wrap_svg(body, "0 0 1420 640", ("arrow", "arrow-green")))


def gen_learner() -> None:
    body = f'''
  {text(760, 36, "Learner Mode: Sync First, Change Quorum Later", 24, "700")}
  {text(760, 62, "Five-member production example: keep quorum 3/5 while the new node catches up", 13, "400", SUBT)}

  {rect(60, 110, 690, 290, GRAY_FILL, GRAY_STROKE, 20)}
  {text(405, 142, "Directly Adding a Voting Member", 19, "700")}
  {rect(95, 205, 110, 80, AMBER_FILL, AMBER_STROKE)}
  {text(150, 236, "Leader", 16, "700")}
  {text(150, 257, "voter", 11, "400", SUBT)}
  {rect(225, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(280, 236, "Follower", 16, "700")}
  {text(280, 257, "voter", 11, "400", SUBT)}
  {rect(355, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(410, 236, "Follower", 16, "700")}
  {text(410, 257, "voter", 11, "400", SUBT)}
  {rect(485, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(540, 236, "Follower", 16, "700")}
  {text(540, 257, "voter", 11, "400", SUBT)}
  {rect(615, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(670, 236, "Follower", 16, "700")}
  {text(670, 257, "voter", 11, "400", SUBT)}
  {rect(305, 305, 160, 80, RED_FILL, RED_STROKE)}
  {text(385, 336, "New Node", 16, "700")}
  {text(385, 357, "already in voting set", 11, "400", SUBT)}
  {text(255, 335, "Quorum 3/5 -> 4/6", 12, "700", "#b91c1c", "start")}
  {text(255, 357, "before data catch-up finishes", 11, "400", SUBT, "start")}

  {rect(790, 110, 690, 290, GRAY_FILL, GRAY_STROKE, 20)}
  {text(1135, 142, "Adding a Learner First", 19, "700")}
  {rect(825, 205, 110, 80, AMBER_FILL, AMBER_STROKE)}
  {text(880, 236, "Leader", 16, "700")}
  {text(880, 257, "voter", 11, "400", SUBT)}
  {rect(955, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1010, 236, "Follower", 16, "700")}
  {text(1010, 257, "voter", 11, "400", SUBT)}
  {rect(1085, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1140, 236, "Follower", 16, "700")}
  {text(1140, 257, "voter", 11, "400", SUBT)}
  {rect(1215, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1270, 236, "Follower", 16, "700")}
  {text(1270, 257, "voter", 11, "400", SUBT)}
  {rect(1345, 205, 110, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1400, 236, "Follower", 16, "700")}
  {text(1400, 257, "voter", 11, "400", SUBT)}
  {rect(1090, 305, 160, 80, PURPLE_FILL, PURPLE_STROKE)}
  {text(1170, 336, "Learner", 16, "700")}
  {text(1170, 357, "non-voter", 11, "400", SUBT)}
  {text(1005, 335, "Quorum stays 3/5", 12, "700", "#6d28d9", "start")}
  {text(1005, 357, "sync snapshot / log first", 11, "400", SUBT, "start")}

  {line(880, 285, 1160, 305, "arrow-green")}
  {text(1010, 300, "sync", 11, "400", SUBT)}

  {rect(210, 450, 1120, 160, BLUE_FILL, BLUE_STROKE, 20)}
  {text(770, 485, "The Correct Primary / Standby Mental Model", 18, "700")}
  {text(770, 515, "A learner is a warm standby member inside the same five-member cluster, not a separate standby cluster", 13, "400", SUBT)}

  {rect(270, 545, 340, 40, GREEN_FILL, GREEN_STROKE)}
  {text(440, 570, "Five-voter primary cluster + learner spare", 14, "700")}
  {rect(930, 545, 340, 40, RED_FILL, RED_STROKE)}
  {text(1100, 570, "Five-voter primary + separate standby cluster", 14, "700")}
  {text(770, 568, "!=", 24, "700")}
'''
    save_svg("etcd-learner-1", wrap_svg(body, "0 0 1540 640", ("arrow", "arrow-green")))


def main() -> None:
    gen_overview()
    gen_defrag()
    gen_defrag_pages()
    gen_defrag_metrics()
    gen_k8s_defrag()
    gen_learner()
    print(f"Generated etcd diagrams in {OUT}")


if __name__ == "__main__":
    main()
