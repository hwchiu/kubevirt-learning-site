---
layout: doc
---

# KubeVirt Monitoring 原始碼分析

## 專案簡介

**KubeVirt Monitoring** 是 KubeVirt 生態系的集中式監控基礎設施專案，彙集了 Grafana 儀表板、Prometheus 告警規則與 Runbook，以及用於確保各 Operator 一致監控實踐的工具。

- **GitHub**: [kubevirt/monitoring](https://github.com/kubevirt/monitoring)
- **License**: Apache 2.0
- **語言**: Go / Python / Shell

## 文件導覽

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | 專案結構、4 個核心工具、目錄佈局、CI/CD 流程 |
| [核心功能分析](./core-features) | 75 個 Runbook、100+ 指標、Grafana 儀表板、Linter 工具 |
| [控制器與 API](./controllers-api) | monitoringlinter 分析器、metricsdocs 生成器、指標解析器 |
| [外部整合](./integration) | Prometheus/Grafana/OpenShift 整合、跨 Operator 指標收集 |
