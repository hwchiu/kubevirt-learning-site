---
layout: doc
title: NMO — 學習路徑
---

# 📖 Node Maintenance Operator 故事驅動學習路徑

> 這是一條為「需要對 K8s 節點做維護、但不想中斷 VM workload」的 Platform Engineer 設計的學習路徑。透過真實的情境故事，你將跟著主角阿明從手動 `kubectl drain` 的痛苦，逐步理解 NMO 的核心機制與實作細節。

---

## 你適合這條路徑嗎？

這條路徑假設你：

- ✅ 熟悉 Kubernetes 基本概念（Pod、Node、DaemonSet、CRD）
- ✅ 了解節點維護的基本需求（硬體升級、OS 更新、Kernel patch）
- ✅ 有管理生產環境 cluster 的經驗（或學習意願）
- ❌ 不需要有任何 Node Maintenance Operator 使用經驗

---

## 📖 [故事驅動式學習路徑](./story)

**風格**：跟著一位 SRE 工程師「阿明」，從接到「對 20+ 節點 cluster 做硬體升級」的任務開始，歷經手動維護的混亂、認識 NMO、踩到 PDB 陷阱、搞懂 Lease 協調機制，一章章把 NMO 的全貌拼起來。

**主角設定**：阿明是一位 SRE/Platform Engineer，負責一個跑著 24/7 KubeVirt VM workload 的生產 cluster，有 20 幾個節點。他收到通知：這批節點要做硬體升級，必須一台一台下線。

**你將學到**：
- `NodeMaintenance` CR 的建立與刪除如何觸發自動排空流程
- Cordon、Taint、Pod 驅逐的執行順序與原理
- PodDisruptionBudget 如何讓 drain 卡住，該怎麼應對
- Lease 機制如何防止多節點同時進入維護
- OpenShift etcd quorum 保護的作用
- Admission Webhook 的驗證邏輯
- Events 與可觀測性工具

**[→ 開始閱讀故事](./story)**

---

::: info 📚 相關技術文件
讀完故事後，可深入閱讀各主題的技術文件：

- [專案總覽](/node-maintenance-operator/) — NMO 的設計目標與核心概念
- [系統架構](/node-maintenance-operator/architecture) — Reconcile 流程與狀態機
- [NodeMaintenance CRD 規格](/node-maintenance-operator/crd-specification) — CR 欄位詳解
- [節點排空工作流程](/node-maintenance-operator/node-drainage-process) — 排空的完整執行邏輯
- [Taint 管理與 Cordoning](/node-maintenance-operator/taints-and-cordoning) — 節點隔離機制
- [Lease 分散式協調](/node-maintenance-operator/lease-based-coordination) — 多 operator 協調
- [Admission Validation](/node-maintenance-operator/validation-webhooks) — Webhook 驗證
- [事件與可觀測性](/node-maintenance-operator/event-recording-and-observability) — 觀測維護過程
:::
