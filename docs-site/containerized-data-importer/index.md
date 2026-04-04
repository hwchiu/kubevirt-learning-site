---
layout: doc
---

# Containerized Data Importer (CDI) 原始碼分析

## 專案簡介

**Containerized Data Importer (CDI)** 是 KubeVirt 生態系中負責資料管理的核心元件，提供將虛擬機器映像匯入 Kubernetes PersistentVolume 的能力。

- **GitHub**: [kubevirt/containerized-data-importer](https://github.com/kubevirt/containerized-data-importer)
- **License**: Apache 2.0
- **語言**: Go

## 文件導覽

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | 專案結構、9 個 Binary、10 個 CRD、建置系統、DataVolume 狀態機 |
| [核心功能分析](./core-features) | 資料匯入、上傳、克隆機制，格式轉換，Checksum 驗證 |
| [控制器與 API](./controllers-api) | 17 個控制器、CRD 型別定義、Webhook、API Server |
| [外部整合](./integration) | KubeVirt/CSI/VolumeSnapshot 整合、認證授權、RBAC、Forklift |
