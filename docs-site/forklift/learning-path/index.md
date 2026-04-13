---
layout: doc
title: Forklift — 學習路徑
---

# 📖 Forklift 故事驅動學習路徑

> 這是一條為「已部署 KubeVirt、但需要大量遷移 VM」的工程師設計的學習路徑。透過一個真實的情境故事，你將跟著主角阿明逐步理解 Forklift 的核心概念與實作細節。

---

## 你適合這條路徑嗎？

這條路徑假設你：

- ✅ 熟悉 Kubernetes 基本概念（Pod、PVC、CRD、Controller）
- ✅ 已部署或正在使用 KubeVirt 執行 VM
- ✅ 有 VMware vSphere 或其他虛擬化平台的基本使用經驗
- ❌ 不需要有任何 Forklift 使用經驗

---

## 📖 [故事驅動式學習路徑](./story)

**風格**：跟著 Platform Engineer「阿明」，從接到「把 50 台 VMware VM 遷移進 KubeVirt」的緊急任務開始，一章章遭遇問題、尋找答案。Forklift 的每個核心概念都在解決具體問題時自然出現。

**涵蓋內容**：
- 手動遷移 VM 為什麼這麼痛苦？
- Forklift 是什麼？Provider 怎麼連接 vSphere
- Inventory 收集機制：Forklift 怎麼探索來源環境
- NetworkMap：來源與目標網路怎麼映射
- StorageMap：VMDK 轉換成哪種 StorageClass
- 建立 Plan：定義要遷移哪些 VM
- 執行 Migration：觀察 virt-v2v 磁碟轉換過程
- Cold vs Warm Migration：如何做到不停機遷移
- 遷移失敗排查：常見錯誤與解法
- 規模化：批量遷移 50 台 VM 的策略

**適合**：喜歡有情境脈絡、想先理解「為什麼」再看「是什麼」的學習者。

**[→ 開始閱讀故事](./story)**

---

::: info 📚 相關技術文件
讀完故事後，可深入閱讀各主題的技術文件：

- [系統架構](/forklift/architecture) — 9 Controllers、9 CRDs、Provider Adapters、virt-v2v
- [核心功能](/forklift/core-features) — 遷移流程、Provider 抽象層、磁碟轉換、網路對映
- [控制器與 API](/forklift/controllers-api) — Controller 架構、CRD 型別、Webhook、REST API
- [外部整合](/forklift/integration) — KubeVirt、CDI、vSphere、oVirt、OpenStack、Hyper-V
:::
