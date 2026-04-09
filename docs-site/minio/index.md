---
layout: doc
title: MinIO — 專案簡介
---

# MinIO — 專案簡介

MinIO 是一套以 Go 語言開發的高效能、S3 相容的物件儲存系統，適用於私有雲與混合雲環境。

## 文件導覽

### 系統架構

| 章節 | 說明 |
|------|------|
| [系統架構](./architecture) | 系統架構圖、核心元件、ObjectLayer 介面、部署模式與初始化流程 |

### 儲存引擎

| 章節 | 說明 |
|------|------|
| [Erasure Coding 與資料分片](./erasure-coding) | Reed-Solomon 演算法、Encode/Decode 流程、Shard Size 計算、Erasure Set、Quorum 機制 |
| [底層硬碟讀寫機制](./disk-io) | xlStorage 結構、On-Disk 目錄佈局、xl.meta 格式、O_DIRECT、Inline Data、RenameData 原子操作 |
| [物件讀寫完整流程](./object-lifecycle) | PutObject/GetObject 完整呼叫鏈、Multipart Upload、DeleteObject、Versioning |

### 資料保護與複製

| 章節 | 說明 |
|------|------|
| [資料複製與同步](./data-replication) | Bucket Replication、Site Replication、MRF 重試、一致性模型 |
| [資料修復與自癒機制](./healing) | Healing Pipeline、Bitrot 偵測、背景掃描、修復流程 |

### API 與整合

| 章節 | 說明 |
|------|------|
| [S3 API 與監控整合](./integration) | S3 API Router、Prometheus Metrics、Event Notification、IAM |
