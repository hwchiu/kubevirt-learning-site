---
layout: doc
title: Monitoring — 學習路徑入口
---

# 🗺️ KubeVirt Monitoring 學習路徑

## 你適合這條路徑嗎？

這條路徑為 **SRE / DevOps / 平台工程師** 設計，假設你：

- ✅ 熟悉 Prometheus 基本概念（scrape、PromQL、AlertManager）
- ✅ 用過 Grafana 建立過儀表板
- ✅ 有可以操作的 KubeVirt 環境（或理解 KubeVirt 基本架構）
- ✅ 知道什麼是 ServiceMonitor（Prometheus Operator CRD）

如果你對 KubeVirt 本身還不熟悉，建議先閱讀 [KubeVirt 系統架構](/kubevirt/architecture/overview) 後再回來。

---

## 前置條件

| 知識 | 建議資源 |
|------|---------|
| Prometheus Operator | [官方文件](https://prometheus-operator.dev/docs/getting-started/introduction/) |
| KubeVirt 基本架構 | [KubeVirt 架構分析](/kubevirt/architecture/overview) |
| Kubernetes RBAC | 任何 K8s 入門教材 |

---

## 故事簡介

**阿明**是一名 SRE，半夜兩點被叫醒——公司 KubeVirt 生產環境的虛擬機器群集掛了，客戶打電話進來，但 Slack 毫無告警。

他從這場慘案出發，一步步建立起完整的 KubeVirt 可觀測性體系：
從理解 KubeVirt 暴露了哪些指標，到設定 ServiceMonitor 讓 Prometheus 能抓到它們；
從寫出第一條 VMI Failed 告警，到認識 75 個 Runbook 背後的處理邏輯；
從建立 Grafana Dashboard 一覽 VM 狀態，到用 monitoringlinter 確保告警規則的品質；
最後，他理解了 KubeVirt Monitoring 這個集中式專案，如何讓整個生態系的告警保持一致。

---

## 開始閱讀

👉 **[故事：讓 VM 不再默默消失](./story)**

---

## 相關技術文件

完整閱讀故事後，可以回到以下技術文件深入查閱細節：

| 文件 | 說明 |
|------|------|
| [專案簡介](/monitoring/) | KubeVirt Monitoring 專案概覽 |
| [系統架構](/monitoring/architecture) | 4 個核心工具、CI/CD 流程、目錄結構 |
| [核心功能分析](/monitoring/core-features) | 75 個 Runbook、100+ 指標、Grafana 儀表板、Linter 工具 |
| [指標與告警規則](/monitoring/metrics-alerts) | monitoringlinter 分析器、指標解析器、metricsdocs 生成器 |
| [外部整合](/monitoring/integration) | Prometheus/Grafana/OpenShift 整合、跨 Operator 指標收集 |
