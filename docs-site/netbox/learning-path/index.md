---
layout: doc
title: NetBox — 學習路徑：終結 Excel 的 Source of Truth 之旅
---

# NetBox 學習路徑

## 終結 Excel 的 Source of Truth 之旅

這條學習路徑以**故事驅動**的方式，帶你從零開始理解 NetBox 如何解決真實世界的網路資產管理問題。

---

## 你適合這條路徑嗎？

**非常適合你，如果你有以下情境：**

- 公司的 IP 位址清冊還在 Excel 試算表裡，各部門各自維護
- 設備清冊分散在不同文件，不知道哪台設備插在哪個機架
- 想建立一套 **Source of Truth**，讓所有人查詢同一份資料
- 想用 API 自動化網路設備的盤點與設定

**你不需要先具備：**

- NetBox 使用經驗
- 完整的資料庫知識

---

## 前置條件

| 條件 | 說明 |
|------|------|
| **網路基礎** | 理解 IP 位址、Subnet、VLAN 的基本概念 |
| **資料中心概念** | 知道什麼是機架（Rack）、機房（Site） |
| **Python 基礎** | 第 7、8 章會用到 Python 和 REST API |
| **Linux CLI** | 能執行基本指令 |

---

## 故事簡介

主角**阿明**是一家中型科技公司的 Network Engineer。公司有 30 個機架、幾百台設備，但 IP 清冊是 8 年前的 Excel，設備清冊由三個部門各自維護，沒有人知道哪份資料是對的。

某天，老闆在會議上問：「我們有多少台設備？用了多少 IP？」

沒有人能立刻回答。

那天下午，阿明開始研究 NetBox。

---

## 故事章節

| 章節 | 標題 | 核心概念 |
|------|------|----------|
| 第 1 章 | Excel 的末日 | 為什麼試算表管不了網路 |
| 第 2 章 | 第一次進 NetBox | Site、Rack、Tenant |
| 第 3 章 | IP 位址管理 | Prefix、IPAddress、RIR |
| 第 4 章 | VLAN 和 VRF | L2/L3 分段、路由隔離 |
| 第 5 章 | 設備清冊 | Device、Interface、Cable |
| 第 6 章 | 虛擬機器管理 | Cluster、VirtualMachine、VMInterface |
| 第 7 章 | REST API 自動化 | pynetbox、批量匯入 |
| 第 8 章 | GraphQL 查詢 | 複雜關聯查詢 |
| 第 9 章 | Webhook 整合 | Event Rules、Ansible、Terraform |
| 第 10 章 | 維護 Source of Truth | 讓資料保持最新的挑戰 |

---

## 開始閱讀

::: info 進入故事
[→ 開始閱讀故事：終結 Excel 的 Source of Truth 之旅](./story)
:::

---

## 相關技術文件

閱讀故事後，可以透過以下文件深入技術細節：

| 文件 | 說明 |
|------|------|
| [專案總覽](/netbox/) | NetBox 專案概覽、版本資訊 |
| [系統架構](/netbox/architecture) | Django/PostgreSQL/Redis 架構設計 |
| [核心功能](/netbox/core-features) | IPAM、DCIM、虛擬化管理、Plugin 系統 |
| [資料模型](/netbox/data-models) | 115 個模型、12 個 Django apps 詳解 |
| [API 參考](/netbox/api-reference) | REST API + GraphQL，131 個 Endpoints |
| [外部整合](/netbox/integration) | Webhook、Event Rules、LDAP、OAuth2 |
