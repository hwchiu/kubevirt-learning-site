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
  {text(540, 36, "Role of etcd in Kubernetes", 24, "700")}
  {text(540, 62, "All API server state eventually lands in etcd and is protected by Raft replication", 13, "400", SUBT)}

  {rect(80, 110, 210, 90, BLUE_FILL, BLUE_STROKE)}
  {text(185, 145, "kube-apiserver", 18, "700")}
  {text(185, 168, "CRUD / Watch / Lease / Event", 12, "400", SUBT)}
  {text(185, 186, "Primary write path", 12, "400", SUBT)}

  {rect(360, 95, 610, 355, GRAY_FILL, GRAY_STROKE, 20)}
  {text(665, 128, "Primary etcd Raft Cluster", 20, "700")}
  {text(665, 150, "All members share one cluster membership and one quorum boundary", 12, "400", SUBT)}

  {rect(405, 190, 190, 92, AMBER_FILL, AMBER_STROKE)}
  {text(500, 223, "Leader", 18, "700")}
  {text(500, 246, "Accepts writes", 12, "400", SUBT)}
  {text(500, 264, "Replicates Raft log", 12, "400", SUBT)}

  {rect(575, 320, 180, 90, GREEN_FILL, GREEN_STROKE)}
  {text(665, 352, "Follower", 17, "700")}
  {text(665, 375, "voter", 12, "400", SUBT)}
  {text(665, 393, "Participates in quorum", 12, "400", SUBT)}

  {rect(770, 320, 160, 90, GREEN_FILL, GREEN_STROKE)}
  {text(850, 352, "Follower", 17, "700")}
  {text(850, 375, "voter", 12, "400", SUBT)}
  {text(850, 393, "Participates in quorum", 12, "400", SUBT)}

  {line(290, 155, 405, 225)}
  {text(348, 140, "gRPC / MVCC", 11, "400", SUBT)}
  {line(515, 282, 620, 320)}
  {line(545, 282, 810, 320)}
  {text(615, 297, "raft log", 11, "400", SUBT)}
  {text(760, 297, "raft log", 11, "400", SUBT)}

  {rect(110, 295, 180, 120, PURPLE_FILL, PURPLE_STROKE)}
  {text(200, 328, "Watchers / Controllers", 16, "700")}
  {text(200, 350, "kube-controller-manager", 11, "400", SUBT)}
  {text(200, 367, "scheduler / operators", 11, "400", SUBT)}
  {text(200, 390, "Observe state via API server", 11, "400", SUBT)}

  {line(200, 295, 200, 200, "arrow-green", "#059669")}
  {text(225, 248, "Watch / List", 11, "400", SUBT, "start")}

  {rect(120, 510, 860, 160, GRAY_FILL, GRAY_STROKE, 20)}
  {text(550, 545, "Chapter Focus", 18, "700")}

  {rect(160, 575, 235, 68, BLUE_FILL, BLUE_STROKE)}
  {text(278, 603, "Defrag / Compact", 16, "700")}
  {text(278, 624, "MVCC space reclamation and disk size", 11, "400", SUBT)}

  {rect(425, 575, 235, 68, BLUE_FILL, BLUE_STROKE)}
  {text(543, 603, "Kubernetes Operations", 16, "700")}
  {text(543, 624, "One-member-at-a-time defrag and control-plane impact", 11, "400", SUBT)}

  {rect(690, 575, 250, 68, BLUE_FILL, BLUE_STROKE)}
  {text(815, 603, "Learner Mode", 16, "700")}
  {text(815, 624, "Sync data first, change the voting set later", 11, "400", SUBT)}
'''
    save_svg("etcd-overview-1", wrap_svg(body, "0 0 1080 700", ("arrow", "arrow-green")))


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


def gen_k8s_defrag() -> None:
    body = f'''
  {text(620, 36, "Operational Flow of etcd Defrag in Kubernetes", 24, "700")}
  {text(620, 62, "Run one member at a time to avoid amplifying control-plane latency and quorum risk", 13, "400", SUBT)}

  {rect(60, 120, 220, 100, BLUE_FILL, BLUE_STROKE)}
  {text(170, 154, "kube-apiserver", 18, "700")}
  {text(170, 178, "Continuously reads and writes etcd", 12, "400", SUBT)}
  {text(170, 196, "CRUD / Watch / Lease", 12, "400", SUBT)}

  {rect(340, 100, 840, 180, GRAY_FILL, GRAY_STROKE, 20)}
  {text(760, 132, "etcd Cluster", 20, "700")}

  {rect(400, 165, 180, 80, AMBER_FILL, AMBER_STROKE)}
  {text(490, 196, "Member A", 17, "700")}
  {text(490, 218, "currently being defragged", 12, "400", SUBT)}

  {rect(660, 165, 180, 80, GREEN_FILL, GREEN_STROKE)}
  {text(750, 196, "Member B", 17, "700")}
  {text(750, 218, "still able to serve traffic", 12, "400", SUBT)}

  {rect(920, 165, 180, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1010, 196, "Member C", 17, "700")}
  {text(1010, 218, "still able to serve traffic", 12, "400", SUBT)}

  {line(280, 170, 400, 200)}
  {line(280, 170, 660, 200, "arrow-green", "#059669", True)}
  {line(280, 170, 920, 200, "arrow-green", "#059669", True)}
  {text(350, 154, "Requests can feel A's stall", 11, "400", SUBT)}

  {rect(80, 345, 1090, 220, PURPLE_FILL, PURPLE_STROKE, 20)}
  {text(625, 380, "Recommended Operational Sequence", 19, "700")}

  {rect(120, 420, 220, 95, BLUE_FILL, BLUE_STROKE)}
  {text(230, 450, "1. Check Metrics First", 16, "700")}
  {text(230, 474, "Compare in-use vs db size", 11, "400", SUBT)}
  {text(230, 492, "Verify that defrag is worth it", 11, "400", SUBT)}

  {rect(385, 420, 220, 95, AMBER_FILL, AMBER_STROKE)}
  {text(495, 450, "2. Defrag One Member", 16, "700")}
  {text(495, 474, "Run etcdctl defrag against one member", 11, "400", SUBT)}
  {text(495, 492, "Do not hit all members at once", 11, "400", SUBT)}

  {rect(650, 420, 220, 95, GREEN_FILL, GREEN_STROKE)}
  {text(760, 450, "3. Observe Recovery", 16, "700")}
  {text(760, 474, "Wait for defrag_inflight to return to 0", 11, "400", SUBT)}
  {text(760, 492, "Confirm db_total_size decreases", 11, "400", SUBT)}

  {rect(915, 420, 220, 95, RED_FILL, RED_STROKE)}
  {text(1025, 450, "4. Move to the Next Member", 16, "700")}
  {text(1025, 474, "Avoid control-plane peak periods", 11, "400", SUBT)}
  {text(1025, 492, "Preserve quorum margin", 11, "400", SUBT)}

  {line(340, 468, 385, 468)}
  {line(605, 468, 650, 468)}
  {line(870, 468, 915, 468)}
'''
    save_svg("etcd-kubernetes-defrag-1", wrap_svg(body, "0 0 1240 600", ("arrow", "arrow-green")))


def gen_learner() -> None:
    body = f'''
  {text(650, 36, "Learner Mode: Sync First, Change Quorum Later", 24, "700")}
  {text(650, 62, "Learner mode separates data catch-up from voting-topology change", 13, "400", SUBT)}

  {rect(60, 110, 560, 260, GRAY_FILL, GRAY_STROKE, 20)}
  {text(340, 142, "Directly Adding a Voting Member", 19, "700")}
  {rect(110, 205, 120, 80, AMBER_FILL, AMBER_STROKE)}
  {text(170, 236, "Leader", 16, "700")}
  {text(170, 257, "voter", 11, "400", SUBT)}
  {rect(260, 205, 120, 80, GREEN_FILL, GREEN_STROKE)}
  {text(320, 236, "Follower", 16, "700")}
  {text(320, 257, "voter", 11, "400", SUBT)}
  {rect(410, 205, 120, 80, GREEN_FILL, GREEN_STROKE)}
  {text(470, 236, "Follower", 16, "700")}
  {text(470, 257, "voter", 11, "400", SUBT)}
  {rect(260, 300, 120, 80, RED_FILL, RED_STROKE)}
  {text(320, 331, "New Node", 16, "700")}
  {text(320, 352, "already counted in quorum", 11, "400", SUBT)}
  {text(340, 338, "Quorum 2/3 -> 3/4", 12, "700", "#b91c1c", "start")}
  {text(340, 360, "while data is still catching up", 11, "400", SUBT, "start")}

  {rect(680, 110, 560, 260, GRAY_FILL, GRAY_STROKE, 20)}
  {text(960, 142, "Adding a Learner First", 19, "700")}
  {rect(730, 205, 120, 80, AMBER_FILL, AMBER_STROKE)}
  {text(790, 236, "Leader", 16, "700")}
  {text(790, 257, "voter", 11, "400", SUBT)}
  {rect(880, 205, 120, 80, GREEN_FILL, GREEN_STROKE)}
  {text(940, 236, "Follower", 16, "700")}
  {text(940, 257, "voter", 11, "400", SUBT)}
  {rect(1030, 205, 120, 80, GREEN_FILL, GREEN_STROKE)}
  {text(1090, 236, "Follower", 16, "700")}
  {text(1090, 257, "voter", 11, "400", SUBT)}
  {rect(880, 300, 120, 80, PURPLE_FILL, PURPLE_STROKE)}
  {text(940, 331, "Learner", 16, "700")}
  {text(940, 352, "non-voter", 11, "400", SUBT)}
  {text(962, 338, "Quorum stays 2/3", 12, "700", "#6d28d9", "start")}
  {text(962, 360, "sync snapshot / log first", 11, "400", SUBT, "start")}

  {line(790, 285, 930, 300, "arrow-green")}
  {text(855, 305, "sync", 11, "400", SUBT)}

  {rect(140, 430, 980, 160, BLUE_FILL, BLUE_STROKE, 20)}
  {text(630, 465, "The Correct Primary / Standby Mental Model", 18, "700")}
  {text(630, 495, "A learner is a warm standby member inside the same cluster, not a separate standby cluster", 13, "400", SUBT)}

  {rect(190, 525, 290, 40, GREEN_FILL, GREEN_STROKE)}
  {text(335, 550, "Primary cluster + learner standby member", 14, "700")}
  {rect(780, 525, 290, 40, RED_FILL, RED_STROKE)}
  {text(925, 550, "Primary cluster + separate standby cluster", 14, "700")}
  {text(630, 548, "!=", 24, "700")}
'''
    save_svg("etcd-learner-1", wrap_svg(body, "0 0 1300 620", ("arrow", "arrow-green")))


def main() -> None:
    gen_overview()
    gen_defrag()
    gen_k8s_defrag()
    gen_learner()
    print(f"Generated etcd diagrams in {OUT}")


if __name__ == "__main__":
    main()
