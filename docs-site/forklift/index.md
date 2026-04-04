---
layout: doc
---

# Forklift — VM 遷移工具

[Forklift](https://github.com/kubev2v/forklift)（又稱 Migration Toolkit for Virtualization, MTV）是一個 Kubernetes Operator，負責將虛擬機器從 VMware vSphere、oVirt/RHV、OpenStack、Hyper-V 及 OVA 等來源遷移至 KubeVirt 環境。

## 文件導覽

| 文件 | 內容 |
|------|------|
| [系統架構](./architecture) | 專案總覽、系統架構圖、Binary 入口、目錄結構、建置系統 |
| [核心功能分析](./core-features) | 遷移流程、Provider 抽象層、磁碟轉換、網路對映、演算法分析 |
| [控制器與 API](./controllers-api) | Controller 架構、CRD 型別、Webhook、REST API、認證機制 |
| [外部整合](./integration) | KubeVirt/CDI/vSphere/oVirt/OpenStack/Hyper-V 整合、CI/CD |
