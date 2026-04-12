#!/usr/bin/env python3
import xml.etree.ElementTree as ET

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG = "#ffffff"
BOX_FILL = "#f9fafb"
BOX_STROKE = "#e5e7eb"
CONTAINER_FILL = "#f0f4ff"
CONTAINER_STROKE = "#c7d2fe"
ARROW = "#3b82f6"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"

W, H = 1040, 820
svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(W), height=str(H), viewBox=f"0 0 {W} {H}")
ET.SubElement(svg, "rect", width=str(W), height=str(H), fill=BG)

defs = ET.SubElement(svg, "defs")
marker = ET.SubElement(defs, "marker", id="arr", markerWidth="8", markerHeight="8",
                        refX="6", refY="3", orient="auto")
ET.SubElement(marker, "path", d="M0,0 L0,6 L8,3 z", fill=ARROW)
marker2 = ET.SubElement(defs, "marker", id="arr2", markerWidth="8", markerHeight="8",
                         refX="2", refY="3", orient="auto")
ET.SubElement(marker2, "path", d="M8,0 L8,6 L0,3 z", fill=ARROW)

def txt(x, y, content, size=12, fill=TEXT_PRIMARY, anchor="middle", weight="normal"):
    t = ET.SubElement(svg, "text", x=str(x), y=str(y),
                      **{"font-family": FONT, "font-size": str(size), "fill": fill,
                         "text-anchor": anchor, "dominant-baseline": "middle", "font-weight": weight})
    t.text = content

def arr_msg(x1, y, x2, label, dashed=False, ret=False):
    style = "5,5" if dashed else "none"
    if ret:
        # return arrow (right to left)
        ET.SubElement(svg, "line", x1=str(x1), y1=str(y), x2=str(x2), y2=str(y),
                      stroke=ARROW, **{"stroke-width": "1.5", "stroke-dasharray": style,
                                        "marker-end": "url(#arr2)" if ret else "url(#arr)"})
    else:
        ET.SubElement(svg, "line", x1=str(x1), y1=str(y), x2=str(x2), y2=str(y),
                      stroke=ARROW, **{"stroke-width": "1.5", "stroke-dasharray": style,
                                        "marker-end": "url(#arr)"})
    mid_x = (x1+x2)//2
    txt(mid_x, y-10, label, size=11, fill=TEXT_SECONDARY)

def note_box(x, y, w, h, label, fill="#fefce8", stroke="#fde68a"):
    ET.SubElement(svg, "rect", x=str(x), y=str(y), width=str(w), height=str(h),
                  fill=fill, stroke=stroke, **{"stroke-width": "1", "rx": "4"})
    txt(x+w//2, y+h//2, label, size=11, fill=TEXT_SECONDARY)

# Title
txt(W//2, 25, "Snapshot / Restore / Clone 操作流程", size=17, fill=TEXT_PRIMARY, weight="bold")

# Participants
participants = ["使用者", "Kubernetes API", "KubeVirt", "CSI Driver", "虛擬機器"]
P_Y = 65
P_W = 120
spacing = (W - 80) // len(participants)
p_x = [60 + i*spacing + spacing//2 for i in range(len(participants))]

LIFELINE_END = 800

for i, (px, name) in enumerate(zip(p_x, participants)):
    ET.SubElement(svg, "rect", x=str(px-P_W//2), y=str(P_Y-18), width=str(P_W), height="36",
                  fill=CONTAINER_FILL, stroke=CONTAINER_STROKE, **{"rx": "6", "stroke-width": "1.5"})
    txt(px, P_Y, name, size=12, fill=TEXT_PRIMARY, weight="bold")
    ET.SubElement(svg, "line", x1=str(px), y1=str(P_Y+18), x2=str(px), y2=str(LIFELINE_END),
                  stroke=BOX_STROKE, **{"stroke-width": "1", "stroke-dasharray": "4,4"})

U, KS, KV, CSI, VM = p_x

# Section: Snapshot
note_box(30, 100, W-60, 22, "建立快照流程", fill="#f0f4ff", stroke="#c7d2fe")
y = 138
arr_msg(U, y, KS, "建立 VirtualMachineSnapshot"); y+=28
arr_msg(KS, y, KV, "觸發 snapshot controller"); y+=28
arr_msg(KV, y, VM, "通知 guest agent 執行 fsfreeze"); y+=28
arr_msg(VM, y, KV, "fsfreeze 完成", dashed=True); y+=28
arr_msg(KV, y, CSI, "建立 VolumeSnapshot（每個磁碟）"); y+=28
arr_msg(CSI, y, KV, "VolumeSnapshot 就緒", dashed=True); y+=28
arr_msg(KV, y, VM, "通知 guest agent 執行 fsthaw"); y+=28
arr_msg(VM, y, KV, "fsthaw 完成", dashed=True); y+=28
arr_msg(KV, y, KS, "更新 VirtualMachineSnapshotContent"); y+=28
arr_msg(KS, y, U, "status.readyToUse = true", dashed=True); y+=28

# Section: Restore
note_box(30, y+5, W-60, 22, "原地還原流程", fill="#f0fff4", stroke="#86efac"); y+=38
arr_msg(U, y, KS, "停止 VM (runStrategy: Halted)"); y+=28
arr_msg(U, y, KS, "建立 VirtualMachineRestore"); y+=28
arr_msg(KS, y, KV, "觸發 restore controller"); y+=28
arr_msg(KV, y, CSI, "從 VolumeSnapshot 建立新 PVC"); y+=28
arr_msg(CSI, y, KV, "PVC 建立完成", dashed=True); y+=28
arr_msg(KV, y, KS, "更新 VM 使用新 PVC"); y+=28
arr_msg(KS, y, U, "status.complete = true", dashed=True); y+=28
arr_msg(U, y, KS, "啟動 VM"); y+=28

# Section: Clone
note_box(30, y+5, W-60, 22, "Clone 流程", fill="#fff7ed", stroke="#fed7aa"); y+=38
arr_msg(U, y, KS, "建立 VirtualMachineClone"); y+=28
arr_msg(KS, y, KV, "觸發 clone controller"); y+=28
arr_msg(KV, y, KS, "建立臨時 VirtualMachineSnapshot"); y+=28
arr_msg(KS, y, KV, "快照就緒", dashed=True); y+=28
arr_msg(KV, y, KS, "建立目標 VM 框架"); y+=28
arr_msg(KV, y, CSI, "從快照建立新 PVC（新 VM 使用）"); y+=28
arr_msg(CSI, y, KV, "新 PVC 就緒", dashed=True); y+=28
arr_msg(KV, y, KS, "更新 Clone status = Succeeded"); y+=28
arr_msg(KS, y, U, "新 VM 可以啟動", dashed=True)

tree = ET.ElementTree(svg)
ET.indent(tree, space="  ")
with open("docs-site/public/diagrams/kubevirt/kubevirt-snapshot-clone-2.svg", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)
print("Done")
