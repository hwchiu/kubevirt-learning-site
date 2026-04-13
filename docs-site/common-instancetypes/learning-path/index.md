---
layout: doc
title: Common Instancetypes — 學習路徑總覽
---

# Common Instancetypes 學習路徑：VM 規格的標準化之路

## 你適合這條路徑嗎？

如果你符合以下描述，這條路徑就是為你設計的：

- ✅ 已經在使用 KubeVirt，能夠建立基本的 VirtualMachine
- ✅ 開始幫多個團隊或環境建立 VM，覺得每次都要寫一堆重複的 YAML
- ✅ 想要建立公司內部的 VM 規格標準，讓大家用一致的方式申請 VM
- ✅ 聽過 AWS EC2 Instance Types（t3.medium、m5.large...），想在 KubeVirt 實現同樣的概念

這個問題不是深奧的技術問題，而是**組織與標準化**的問題。Common Instancetypes 提供了一套現成的解法。

---

## 前置條件

| 知識 | 說明 |
|------|------|
| KubeVirt 基礎 | 能建立 VirtualMachine，了解 VM spec 的基本結構 |
| Kubernetes 基礎 | 了解 namespace、CRD、kubectl 操作 |
| 不需要 | 深入的 KVM/QEMU 知識 |

---

## 故事簡介

**主角：阿明**，Platform Engineer，公司剛完成 KubeVirt 部署。

起初，他幫每個部門建 VM 都是 copy-paste YAML 再改規格——直到請求越來越多，他開始思考：能不能像 AWS 那樣，讓使用者直接選「規格型號」就好？

這條路徑跟著阿明的七章故事，從「YAML 複製地獄」走到「建立公司自己的 Instancetype 目錄」。

---

## 開始學習

👉 [進入故事：VM 規格的標準化之路](./story)

---

## 相關技術文件

| 文件 | 說明 |
|------|------|
| [專案總覽](/common-instancetypes/) | Common Instancetypes 是什麼、怎麼安裝 |
| [系統架構](/common-instancetypes/architecture) | Kustomize 建置系統、版本管理 |
| [核心功能](/common-instancetypes/core-features) | 7 大系列 43 種 Instancetype、18+ OS Preference |
| [資源類型目錄](/common-instancetypes/resource-catalog) | CRD 定義、Label 規範、驗證機制 |
| [外部整合](/common-instancetypes/integration) | 在 VirtualMachine 中引用的方式 |
