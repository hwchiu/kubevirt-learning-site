---
layout: doc
---

# NetBox — 專案總覽

## 專案資訊

| 項目 | 說明 |
|------|------|
| **專案名稱** | NetBox |
| **Repository** | [netbox-community/netbox](https://github.com/netbox-community/netbox) |
| **語言/框架** | Python 3.12+ / Django 5.2.12 |
| **API 框架** | Django REST Framework 3.16.1 + Strawberry GraphQL |
| **資料庫** | PostgreSQL (必要) |
| **快取/佇列** | Redis (必要) — django-redis + RQ |
| **版本** | v4.5.7 |
| **授權** | Apache License 2.0 |
| **專案類型** | Web 應用平台 |

## 簡介

NetBox 是由 DigitalOcean 開源的網路基礎設施管理平台，提供 **IPAM**（IP Address Management）與 **DCIM**（Data Center Infrastructure Management）等核心功能。它是網路工程師與資料中心維運團隊的 Source of Truth，管理 IP 位址、機櫃、設備、線路、虛擬機等所有網路基礎設施資訊。

### 核心能力

- **115 個資料模型** 橫跨 12 個 Django 應用模組
- **131 個 REST API Endpoints** + GraphQL API
- **完整 Plugin 系統** 支援第三方擴充
- **Object-Level RBAC** 細粒度權限控制
- **Webhook + Event Rules** 事件驅動整合
- **多認證後端** LDAP / OAuth2 / SAML / SSO

## 文件目錄

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | Django 應用結構、部署架構、Plugin 系統、Middleware Pipeline |
| [核心功能分析](./core-features) | IPAM、DCIM、Custom Fields、Change Logging、Search、Cable Path 演算法 |
| [資料模型分析](./data-models) | 115 個 Model 總覽、ERD 關係圖、核心模型深度分析、Mixin 模式 |
| [API 參考與分析](./api-reference) | REST API 131 Endpoints、Serializer 模式、Filter 系統、GraphQL |
| [外部整合與擴充](./integration) | 認證後端、Webhooks、Event Rules、RQ 背景任務、Plugin API |

## 與現有 KubeVirt 生態系專案的比較

| 特性 | KubeVirt 生態系 | NetBox |
|------|----------------|--------|
| 語言 | Go | Python |
| 框架 | controller-runtime / operator-sdk | Django / DRF |
| 資料儲存 | Kubernetes etcd (CRD) | PostgreSQL (ORM) |
| API 風格 | Kubernetes API (declarative) | REST + GraphQL (CRUD) |
| 擴充機制 | CRD + Operator | Plugin System (AppConfig) |
| 部署方式 | Pod in K8s | Gunicorn + Nginx + Systemd |
| 背景任務 | Controller reconcile loop | RQ (Redis Queue) |
