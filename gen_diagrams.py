#!/usr/bin/env python3
"""Generate SVG diagrams for common-instancetypes docs (Notion Clean Style 4)."""
import os

FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
BG   = "#ffffff"
BF   = "#f9fafb"
BS   = "#e5e7eb"
CF   = "#f0f4ff"
CS   = "#c7d2fe"
AC   = "#3b82f6"
TP   = "#111827"
TS   = "#6b7280"

OUT = "docs-site/public/diagrams/common-instancetypes"
os.makedirs(OUT, exist_ok=True)

DEFS = (
    '  <defs>\n'
    '    <marker id="a" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">\n'
    f'      <polygon points="0 0.5, 8.5 3.5, 0 6.5" fill="{AC}"/>\n'
    '    </marker>\n'
    '  </defs>\n'
)


def wrap(w, h, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'  <rect width="{w}" height="{h}" fill="{BG}"/>\n'
        f'{DEFS}{body}</svg>'
    )


def cont(x, y, w, h, title):
    return (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
        f'fill="{CF}" stroke="{CS}" stroke-width="1.5"/>\n'
        f'  <text x="{x+14}" y="{y+22}" font-family="{FONT}" font-size="12" '
        f'font-weight="700" fill="{TS}">{title}</text>\n'
    )


def box(x, y, w, h, lines, fill=BF, stroke=BS):
    r = (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
    )
    n = len(lines)
    lh = 18
    sy = y + (h - n * lh) / 2 + lh - 1
    for i, ln in enumerate(lines):
        fw = "600" if i == 0 else "400"
        r += (
            f'  <text x="{x+w/2:.0f}" y="{sy+i*lh:.0f}" '
            f'font-family="{FONT}" font-size="12" font-weight="{fw}" '
            f'text-anchor="middle" fill="{TP}">{ln}</text>\n'
        )
    return r


def ar(x1, y1, x2, y2, lbl=""):
    r = (
        f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{AC}" stroke-width="1.5" marker-end="url(#a)"/>\n'
    )
    if lbl:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        lw = len(lbl) * 6.5 + 12
        r += (
            f'  <rect x="{mx-lw/2:.1f}" y="{my-15:.1f}" width="{lw:.1f}" height="14" '
            f'rx="3" fill="{BG}" opacity="0.9"/>\n'
            f'  <text x="{mx:.1f}" y="{my-4:.1f}" font-family="{FONT}" font-size="10" '
            f'text-anchor="middle" fill="{TS}">{lbl}</text>\n'
        )
    return r


def lk(ax, ay, aw, ah, bx, by, bw, bh, lbl=""):
    """Auto-route arrow from box A to box B."""
    acx, acy = ax + aw / 2, ay + ah / 2
    bcx, bcy = bx + bw / 2, by + bh / 2
    dx, dy = bcx - acx, bcy - acy
    if abs(dx) >= abs(dy):
        x1 = ax + aw if dx > 0 else ax
        y1 = acy
        x2 = bx if dx > 0 else bx + bw
        y2 = bcy
    else:
        x1 = acx
        y1 = ay + ah if dy > 0 else ay
        x2 = bcx
        y2 = by if dy > 0 else by + bh
    return ar(x1, y1, x2, y2, lbl)


def lk_bottom_top(ax, ay, aw, ah, bx, by, bw, bh, lbl=""):
    """Force bottom-of-A to top-of-B arrow."""
    x1 = ax + aw / 2
    y1 = ay + ah
    x2 = bx + bw / 2
    y2 = by
    return ar(x1, y1, x2, y2, lbl)


def save(name, svg):
    p = os.path.join(OUT, name)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"  ✓ {name}")


# ─── D1: instancetypes-build-pipeline ────────────────────────────────────────
def d1():
    W, H = 1060, 850

    # Node positions (x, y, w, h)
    IT   = (50,  72, 215, 80)
    PR   = (320, 72, 215, 80)
    CO   = (660, 72, 350, 80)

    ROOT = (50,  280, 285, 90)
    VMCI = (410, 280, 265, 90)
    VMI  = (740, 280, 270, 90)

    ALL  = (50,  480, 260, 50)
    CIB  = (50,  550, 260, 50)
    IB   = (50,  620, 260, 50)
    CPB  = (365, 480, 290, 50)
    PB   = (365, 550, 290, 50)
    CHK  = (680, 510, 200, 60)

    K8S  = (700, 710, 300, 70)

    bd = ""
    # Containers
    bd += cont(20, 25,  1020, 175, "原始碼定義 (Sources)")
    bd += cont(20, 240, 1020, 165, "Kustomize 建置層")
    bd += cont(20, 440, 1020, 290, "建置產出 (_build/)")
    bd += cont(20, 770, 1020, 60,  "部署目標")

    # Boxes
    bd += box(*IT,   ["instancetypes/", "7 個系列 × 多種尺寸"])
    bd += box(*PR,   ["preferences/", "16 個 OS 類別"])
    bd += box(*CO,   ["preferences/components/", "26 個可重用元件"])
    bd += box(*ROOT, ["根 kustomization.yaml", "resources: instancetypes + preferences"])
    bd += box(*VMCI, ["VirtualMachineCluster*/", "僅保留 Cluster 範圍資源"])
    bd += box(*VMI,  ["VirtualMachine*/", "僅保留 Namespace 範圍資源"])
    bd += box(*ALL,  ["common-instancetypes-all-bundle.yaml"])
    bd += box(*CIB,  ["common-clusterinstancetypes-bundle.yaml"])
    bd += box(*IB,   ["common-instancetypes-bundle.yaml"])
    bd += box(*CPB,  ["common-clusterpreferences-bundle.yaml"])
    bd += box(*PB,   ["common-preferences-bundle.yaml"])
    bd += box(*CHK,  ["CHECKSUMS.sha256"], fill="#e0f2fe", stroke="#7dd3fc")
    bd += box(*K8S,  ["KubeVirt 叢集"])

    # CO → PR (horizontal, left)
    bd += ar(CO[0], CO[1]+CO[3]//2, PR[0]+PR[2], PR[1]+PR[3]//2, "組合")

    # Sources → Kustomize
    # IT → ROOT (mostly down)
    bd += lk(*IT, *ROOT)
    # PR → ROOT (diagonal left-down)
    bd += ar(PR[0], PR[1]+PR[3]//2, ROOT[0]+ROOT[2], ROOT[1]+ROOT[3]//2)
    # IT → VMCI (diagonal right-down)
    bd += ar(IT[0]+IT[2], IT[1]+IT[3]//2, VMCI[0], VMCI[1]+VMCI[3]//2)
    # IT → VMI (long diagonal right-down)
    bd += ar(IT[0]+IT[2], IT[1]+IT[3]//2, VMI[0], VMI[1]+VMI[3]//2)
    # PR → VMCI (mostly down)
    bd += lk(*PR, *VMCI)
    # PR → VMI (diagonal right)
    bd += ar(PR[0]+PR[2], PR[1]+PR[3]//2, VMI[0], VMI[1]+VMI[3]//2)

    # Kustomize → Build
    # ROOT → ALL (mostly down)
    bd += lk(*ROOT, *ALL)
    # VMCI → CIB
    bd += ar(VMCI[0]+VMCI[2]//2 - 60, VMCI[1]+VMCI[3],
             CIB[0]+CIB[2]//2,         CIB[1])
    # VMCI → CPB
    bd += ar(VMCI[0]+VMCI[2]//2 + 40, VMCI[1]+VMCI[3],
             CPB[0]+CPB[2]//2,         CPB[1])
    # VMI → IB (long diagonal left)
    bd += ar(VMI[0], VMI[1]+VMI[3]//2,
             IB[0]+IB[2],  IB[1]+IB[3]//2)
    # VMI → PB
    bd += ar(VMI[0], VMI[1]+VMI[3]//2,
             PB[0]+PB[2],  PB[1]+PB[3]//2)

    # Build items → CHK
    bd += ar(ALL[0]+ALL[2], ALL[1]+ALL[3]//2, CHK[0], CHK[1]+CHK[3]//2)
    bd += ar(CIB[0]+CIB[2], CIB[1]+CIB[3]//2, CHK[0], CHK[1]+CHK[3]//4)
    bd += ar(IB[0]+IB[2],   IB[1]+IB[3]//2,   CHK[0], CHK[1]+CHK[3]*3//4)
    bd += ar(CPB[0]+CPB[2], CPB[1]+CPB[3]//2, CHK[0]+CHK[2], CHK[1]+CHK[3]//4)
    bd += ar(PB[0]+PB[2],   PB[1]+PB[3]//2,   CHK[0]+CHK[2], CHK[1]+CHK[3]*3//4)

    # CHK → K8S
    bd += lk(*CHK, *K8S, "kubectl apply / kustomize build")

    save("instancetypes-build-pipeline.svg", wrap(W, H, bd))


# ─── D2: instancetypes-kustomize-composition ─────────────────────────────────
def d2():
    W, H = 960, 420

    SZ      = (40,  75, 240, 70)
    BASE_IT = (40, 165, 240, 70)
    KIT     = (40, 270, 240, 70)

    BASE_PR = (360, 75, 240, 70)
    LINUX   = (360, 165, 240, 70)
    ALPINE  = (360, 270, 240, 70)

    EFI     = (660, 75,  240, 70)
    HV      = (660, 175, 240, 70)
    TOPO    = (660, 275, 240, 70)

    bd = ""
    bd += cont(20, 20, 280, 360, "Instance Type 組合")
    bd += cont(340, 20, 280, 360, "Preference 繼承鏈")
    bd += cont(640, 20, 280, 360, "可重用元件 (Component)")

    bd += box(*SZ,      ["sizes.yaml", "定義各尺寸 CPU/Memory"])
    bd += box(*BASE_IT, ["cx1.yaml", "系列基礎設定 (patch)"])
    bd += box(*KIT,     ["kustomization.yaml", "resources + patches"])
    bd += box(*BASE_PR, ["base/", "空白模板"])
    bd += box(*LINUX,   ["linux/", "+ virtio-blk, virtio-net, rng"])
    bd += box(*ALPINE,  ["alpine/", "+ metadata, requirements"])
    bd += box(*EFI,     ["efi/"])
    bd += box(*HV,      ["hyperv/"])
    bd += box(*TOPO,    ["cpu-topology-sockets/"])

    bd += lk(*SZ,      *KIT)
    bd += lk(*BASE_IT, *KIT)
    bd += lk(*BASE_PR, *LINUX)
    bd += lk(*LINUX,   *ALPINE)

    # Components → Preference (right-to-left, horizontal)
    mid_y = H // 2
    bd += ar(EFI[0], mid_y, LINUX[0]+LINUX[2], mid_y, "components 引用")

    save("instancetypes-kustomize-composition.svg", wrap(W, H, bd))


# ─── D3: instancetypes-preference-inheritance ────────────────────────────────
def d3():
    W, H = 700, 520

    BASE    = (250, 30,  200, 70)
    LINUX   = (250, 160, 200, 70)
    ALPINE  = (30,  300, 185, 80)
    UBUNTU  = (220, 300, 185, 80)
    FEDORA  = (415, 300, 185, 80)
    WINDOWS = (465, 155, 210, 80)

    bd = ""
    bd += box(*BASE,    ["base/", "空白 VirtualMachineClusterPreference", "+ vendor label"])
    bd += box(*LINUX,   ["linux/", "+ diskbus-virtio-blk", "+ interfacemodel-virtio-net, rng"])
    bd += box(*ALPINE,  ["alpine/", "+ metadata (icon, name)", "+ requirements (1 CPU, 512Mi)"])
    bd += box(*UBUNTU,  ["ubuntu/", "+ metadata + requirements"])
    bd += box(*FEDORA,  ["fedora/", "+ metadata + requirements"])
    bd += box(*WINDOWS, ["windows/ (獨立繼承鏈)", "+ hyperv + efi + tablet-usb"])

    bd += lk_bottom_top(*BASE, *LINUX)
    bd += lk(*BASE, *WINDOWS)
    bd += lk(*LINUX, *ALPINE)
    bd += lk_bottom_top(*LINUX, *UBUNTU)
    bd += lk(*LINUX, *FEDORA)

    save("instancetypes-preference-inheritance.svg", wrap(W, H, bd))


# ─── D4: instancetypes-release-flow ──────────────────────────────────────────
def d4():
    W, H = 1060, 170

    A = (20,  50, 160, 70)
    B = (215, 50, 170, 70)
    C = (420, 50, 140, 70)
    D = (595, 50, 160, 70)
    E = (790, 50, 160, 70)
    F = (985, 50, 55,  70)

    bd = ""
    bd += box(*A, ["kubevirt/kubevirt", "beta.0 release"])
    bd += box(*B, ["建立 release-1.Y 分支"])
    bd += box(*C, ["Tag v1.Y.0"])
    bd += box(*D, ["GitHub Actions", "建置 bundles"])
    bd += box(*E, ["同步至", "kubevirt/kubevirt main"])
    bd += box(*F, ["建立", "v1.Y+1.0", "milestone"])

    for src, dst in [(A, B), (B, C), (C, D), (D, E), (E, F)]:
        bd += ar(src[0]+src[2], src[1]+src[3]//2,
                 dst[0],        dst[1]+dst[3]//2)

    save("instancetypes-release-flow.svg", wrap(W, H, bd))


# ─── D5: instancetypes-vm-cdi-reference ──────────────────────────────────────
def d5():
    W, H = 920, 360

    IT  = (40,  70,  250, 90)
    PR  = (40,  190, 250, 90)
    VM  = (350, 125, 200, 100)
    DV  = (620, 70,  250, 90)
    PVC = (620, 190, 250, 90)

    bd = ""
    bd += cont(20, 20, 290, 320, "common-instancetypes")
    bd += cont(600, 20, 290, 320, "CDI")

    bd += box(*IT,  ["VirtualMachineClusterInstancetype", "例: u1.medium"])
    bd += box(*PR,  ["VirtualMachineClusterPreference", "例: fedora"])
    bd += box(*VM,  ["VirtualMachine"])
    bd += box(*DV,  ["DataVolume", "匯入 OS 映像"])
    bd += box(*PVC, ["PersistentVolumeClaim"])

    VMcx = VM[0] + VM[2] / 2
    VMcy = VM[1] + VM[3] / 2

    # VM → IT  (spec.instancetype, offset slightly up)
    bd += ar(VM[0], VMcy - 12, IT[0]+IT[2], IT[1]+IT[3]//2 - 10, "spec.instancetype")
    # IT → VM  (定義 CPU/Memory, offset slightly down)
    bd += ar(IT[0]+IT[2], IT[1]+IT[3]//2 + 12, VM[0], VMcy + 8, "定義 CPU/Memory")

    # VM → PR  (spec.preference, offset slightly up)
    bd += ar(VM[0], VMcy + 12, PR[0]+PR[2], PR[1]+PR[3]//2 - 10, "spec.preference")
    # PR → VM  (定義裝置偏好, offset slightly down)
    bd += ar(PR[0]+PR[2], PR[1]+PR[3]//2 + 12, VM[0], VMcy + 28, "定義裝置偏好")

    # VM → DV  (dataVolumeTemplates)
    bd += ar(VM[0]+VM[2], VMcy, DV[0], DV[1]+DV[3]//2, "dataVolumeTemplates")

    # DV → PVC
    bd += lk(*DV, *PVC, "自動建立")

    save("instancetypes-vm-cdi-reference.svg", wrap(W, H, bd))


# ─── D6: instancetypes-kubevirtci-lifecycle ───────────────────────────────────
def d6():
    W, H = 800, 860

    # Main vertical chain
    A = (300, 20,  200, 55)
    B = (300, 105, 200, 55)
    C = (300, 190, 200, 55)
    D = (300, 275, 200, 55)
    E = (300, 360, 200, 55)
    F = (300, 445, 200, 60)
    G = (300, 535, 200, 55)  # 叢集就緒 - highlight

    # Left branch (sync)
    H_ = (60,  640, 200, 55)
    I  = (60,  725, 200, 55)
    J  = (60,  810, 200, 55)

    # Right branch (sync-containerdisks)
    K  = (540, 640, 220, 55)
    L  = (540, 725, 220, 55)
    M  = (540, 810, 220, 55)

    bd = ""
    bd += box(*A, ["kubevirtci.sh up"])
    bd += box(*B, ["clone kubevirtci repo"])
    bd += box(*C, ["make cluster-up"])
    bd += box(*D, ["安裝 KubeVirt operator + CR"])
    bd += box(*E, ["等待 KubeVirt Available"])
    bd += box(*F, ["停用內建 common-instancetypes 部署"])
    bd += box(*G, ["叢集就緒"], fill="#dcfce7", stroke="#86efac")

    bd += box(*H_, ["kubevirtci.sh sync"])
    bd += box(*I,  ["sync.sh: 刪除舊資源"])
    bd += box(*J,  ["重新 apply Kustomize 資源"])

    bd += box(*K,  ["kubevirtci.sh sync-containerdisks"])
    bd += box(*L,  ["podman pull 測試映像"])
    bd += box(*M,  ["push 到叢集內部 registry"])

    # Main chain
    for src, dst in [(A,B),(B,C),(C,D),(D,E),(E,F),(F,G)]:
        bd += lk_bottom_top(*src, *dst)

    # G → left branch
    bd += ar(G[0]+G[2]//2 - 40, G[1]+G[3],
             H_[0]+H_[2]//2,    H_[1])
    # G → right branch
    bd += ar(G[0]+G[2]//2 + 40, G[1]+G[3],
             K[0]+K[2]//2,      K[1])

    # Left chain
    for src, dst in [(H_,I),(I,J)]:
        bd += lk_bottom_top(*src, *dst)

    # Right chain
    for src, dst in [(K,L),(L,M)]:
        bd += lk_bottom_top(*src, *dst)

    save("instancetypes-kubevirtci-lifecycle.svg", wrap(W, H, bd))


# ─── D7: instancetypes-qa-pipeline ───────────────────────────────────────────
def d7():
    W, H = 820, 830

    A = (310, 20,  200, 50)
    B = (310, 100, 200, 50)

    # Fan-out from B
    C = (20,  200, 140, 50)   # lint
    D = (175, 200, 145, 50)   # validate
    E = (335, 200, 145, 50)   # readme
    F = (495, 200, 120, 50)   # test
    G = (630, 200, 150, 50)   # test-lint

    H_ = (305, 300, 210, 60)  # check-tree-clean (decision)

    I  = (305, 400, 210, 50)
    J  = (305, 480, 210, 50)
    K  = (305, 560, 210, 50)
    L  = (305, 640, 210, 50)
    M  = (305, 720, 210, 50)
    N  = (305, 800, 210, 50)  # off-canvas - adjust H

    bd = ""
    bd += box(*A, ["程式碼變更"])
    bd += box(*B, ["make all"])
    bd += box(*C, ["lint: 程式碼檢查"])
    bd += box(*D, ["validate: schema 驗證"])
    bd += box(*E, ["readme: 自動產生文件"])
    bd += box(*F, ["test: 單元測試"])
    bd += box(*G, ["test-lint: Go 檢查"])
    bd += box(*H_, ["check-tree-clean"], fill="#fef9c3", stroke="#fde047")
    bd += box(*I,  ["make cluster-up"])
    bd += box(*J,  ["make cluster-sync"])
    bd += box(*K,  ["make cluster-functest"])
    bd += box(*L,  ["git tag vX.Y.Z"])
    bd += box(*M,  ["GitHub Actions Release"])

    # A → B
    bd += lk_bottom_top(*A, *B)

    # B → fan-out
    Bcx = B[0] + B[2] // 2
    Bbot = B[1] + B[3]
    for node in [C, D, E, F, G]:
        ncx = node[0] + node[2] // 2
        bd += ar(Bcx, Bbot, ncx, node[1])

    # Fan-in → H_
    Htop = H_[1]
    Hcx  = H_[0] + H_[2] // 2
    for node in [C, D, E, F, G]:
        ncx = node[0] + node[2] // 2
        bd += ar(ncx, node[1]+node[3], Hcx, Htop)

    # Vertical chain
    bd += lk_bottom_top(*H_, *I, "通過")
    for src, dst in [(I,J),(J,K),(K,L),(L,M)]:
        bd += lk_bottom_top(*src, *dst)

    save("instancetypes-qa-pipeline.svg", wrap(W, H, bd))


if __name__ == "__main__":
    print("Generating diagrams...")
    d1()
    d2()
    d3()
    d4()
    d5()
    d6()
    d7()
    print("Done.")
