---
layout: doc
title: Multus CNI — 學習路徑
---

# Multus CNI 學習路徑

**阿明的多網路之旅**——一個 Platform Engineer 在 KubeVirt 叢集中解決 VM 多網卡需求的故事。

---

## 你適合這條路徑嗎？

**適合你，如果你：**

- 已熟悉 Kubernetes 基礎（Pod、Namespace、CRD）
- 有 Kubernetes 網路基礎概念（CNI、Pod 網路、CIDR）
- 正在運行 KubeVirt，或需要讓 Pod/VM 連接多個網段
- 想理解 Multus 的設計思路，而不只是複製 YAML

**可能需要先補充的前置知識：**

- Linux 網路基礎：bridge、VLAN、路由
- Kubernetes CNI 概念：什麼是 CNI、kubelet 如何呼叫 CNI

---

## 前置條件

| 項目 | 說明 |
|------|------|
| Kubernetes 叢集 | 已安裝 Flannel / Calico 等基礎 CNI |
| 節點存取 | 能 SSH 到 Node（排查問題需要）|
| kubectl | 已設定好 kubeconfig |
| KubeVirt（選用）| 如果要跟著第五章實作 |

---

## 故事簡介

阿明是一位 Platform Engineer，負責維運一個運行 KubeVirt 的叢集。
某天，業務部門要求 VM 同時連接 **K8s 內部服務網路** 和 **公司 VLAN**——但 VM 只有一張網卡。

跟著阿明一起，你會學到：

1. 為什麼 Kubernetes Pod 預設只有一張網卡，Multus 如何解決這個問題
2. CNI Meta-Plugin 的設計哲學：Delegate 機制如何讓 Multus 與任何 CNI 搭配
3. `NetworkAttachmentDefinition`：定義附加網路的 CRD
4. Pod Annotation：指定哪個 Pod 要幾張網卡
5. KubeVirt VM 的多網卡設定：`masquerade` vs `bridge` 介面模式
6. IPAM 選項：`static`、`dhcp`、`whereabouts` 的選擇時機
7. Thick Plugin：server 架構帶來的安全隔離優勢
8. 多網路不通的系統性排查方法

---

## 開始閱讀

<div style="margin: 2rem 0;">
  <a href="/multus-cni/learning-path/story" style="display: inline-block; padding: 0.75rem 2rem; background: var(--vp-c-brand); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; font-size: 1.05rem;">
    📖 開始閱讀故事 →
  </a>
</div>

---

## 相關技術文件

故事裡的每一章都連結到對應的深度技術文件，你可以先讀故事建立整體感，再回頭看技術文件補細節：

| 文件 | 內容 |
|------|------|
| [專案簡介](/multus-cni/) | Multus 定位、使用場景、KubeVirt 整合 |
| [系統架構](/multus-cni/architecture) | Meta-Plugin 原理、Delegate 機制、DaemonSet 部署 |
| [核心功能](/multus-cni/core-features) | NetworkAttachmentDefinition、Annotation、IPAM |
| [Thick Plugin](/multus-cni/thick-plugin) | Thin vs Thick、server 架構、Unix Domain Socket |
| [設定參考](/multus-cni/configuration) | 完整設定參數與常見錯誤 |
