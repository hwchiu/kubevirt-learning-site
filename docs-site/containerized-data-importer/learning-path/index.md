---
layout: doc
title: CDI — 學習路徑
---

# 📖 CDI 故事驅動學習路徑

> 這是一條為「熟悉 Kubernetes，但初次面對 VM 磁碟管理問題」的工程師設計的學習路徑。透過一個真實的情境故事，你將跟著主角阿明逐步理解 Containerized Data Importer（CDI）的核心概念與實作細節。

---

## 你適合這條路徑嗎？

這條路徑假設你：

- ✅ 熟悉 Kubernetes 基本概念（Pod、PVC、CRD、Controller）
- ✅ 大概知道 VM 磁碟映像是什麼（QCOW2、RAW 格式）
- ✅ 已經或正在評估 KubeVirt 的使用情境（可選）
- ❌ 不需要有任何 CDI 使用經驗

---

## 📖 [故事驅動式學習路徑](./story)

**風格**：跟著 Platform Engineer「阿明」，從接到「把 VMware VM 磁碟搬進 K8s PVC」的任務開始，一章章遭遇問題、尋找答案。CDI 的每個核心概念都在解決具體問題時自然出現。

**涵蓋內容**：
- 為什麼需要 CDI？（光有 PVC 還不夠）
- DataVolume 是什麼？為什麼說它是「聰明的 PVC」
- 從 HTTP URL 匯入 QCOW2 映像
- 上傳本地映像到 K8s（Upload API）
- PVC Clone：快速複製磁碟
- Scratch Space：為什麼 CDI 需要臨時空間
- 格式轉換背後的機制（QCOW2 → RAW）
- CDI 的控制器架構：幕後的協作者們
- 與 KubeVirt 整合：DataVolume 如何成為 VM 的磁碟
- 進階用法：VolumeSnapshot 與跨 Namespace Clone

**適合**：喜歡有情境脈絡、想先理解「為什麼」再看「是什麼」的學習者。

**[→ 開始閱讀故事](./story)**

---

::: info 📚 相關技術文件
讀完故事後，可深入閱讀各主題的技術文件：

- [系統架構](/containerized-data-importer/architecture) — 9 個 Binary、10 個 CRD、DataVolume 狀態機
- [核心功能](/containerized-data-importer/core-features) — 資料匯入、多來源、格式轉換、上傳、PVC 克隆
- [控制器與 API](/containerized-data-importer/controllers-api) — 17 個控制器、CRD、Webhook、API Server
- [外部整合](/containerized-data-importer/integration) — KubeVirt、CSI、VolumeSnapshot、Forklift
:::
