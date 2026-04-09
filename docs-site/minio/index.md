---
layout: doc
title: MinIO — 專案簡介
---

# MinIO — 專案簡介

MinIO 是一套以 Go 語言開發的高效能、S3 相容的物件儲存系統，適用於私有雲與混合雲環境。

## 文件導覽

| 章節 | 說明 |
|------|------|
| [系統架構](./architecture) | 系統架構圖、核心元件、ObjectLayer 介面、部署模式與初始化流程 |
| [Erasure Coding 與資料分片](./erasure-coding) | Reed-Solomon 演算法、Encode/Decode 流程、Shard Size 計算、Erasure Set、Quorum 機制 |
| [底層硬碟讀寫機制](./disk-io) | xlStorage 結構、On-Disk 目錄佈局、xl.meta 格式、O_DIRECT、Inline Data、RenameData 原子操作 |
