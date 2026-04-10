---
layout: doc
title: Cilium — 專案總覽
---

# Cilium — 專案總覽

Cilium 是 CNCF 畢業的開源專案，基於 Linux 核心的 **eBPF** 技術，為 Kubernetes 叢集提供高效能的網路、安全性與可觀測性解決方案。相較於傳統 iptables 方案，Cilium 直接在核心層攔截並處理封包，大幅降低延遲並提升吞吐量。

> **版本**: v1.20.0-dev | **授權**: Apache-2.0 | **CNCF 狀態**: Graduated

## 核心特性

| 類別 | 功能 | 說明 |
|------|------|------|
| **網路** | L3/L4 網路 | 基於 eBPF 的 Pod 間通訊，支援 Overlay 與 Native Routing |
| **網路** | IPAM | 支援 Kubernetes Host Scope、AWS ENI、Azure IPAM 等多種模式 |
| **網路** | ClusterMesh | 多叢集互聯，跨叢集服務發現與負載均衡 |
| **安全性** | NetworkPolicy | 支援 CiliumNetworkPolicy (CNP) 與 CiliumClusterwideNetworkPolicy (CCNP) |
| **安全性** | mTLS 身份驗證 | 基於 SPIFFE/SPIRE 的透明雙向 TLS |
| **安全性** | 加密傳輸 | 支援 WireGuard 與 IPSec 節點間流量加密 |
| **負載均衡** | kube-proxy 替代 | eBPF-based Service 負載均衡，取代 iptables/kube-proxy |
| **負載均衡** | Maglev 哈希 | 一致性哈希實現穩定的 Backend 選擇 |
| **負載均衡** | Gateway API | 支援 Kubernetes Gateway API 及 Ingress |
| **可觀測性** | Hubble | 基於 eBPF 的網路流量可觀測性平台 |
| **可觀測性** | Prometheus Metrics | 豐富的 eBPF datapath 與控制平面指標 |
| **進階** | BGP | 整合 BGP 控制平面，支援 Pod CIDR 廣播 |
| **進階** | Egress Gateway | 為特定 Pod 提供固定的 Egress IP |

## 主要二進位

| 二進位 | 說明 |
|--------|------|
| `cilium-agent` | 每個節點上的核心 DaemonSet，負責 eBPF 程式管理與控制平面 |
| `cilium-operator` | 叢集級別控制器，管理 CRD、Identity GC、EndpointSlice 同步 |
| `cilium-operator-generic` | 通用雲平台 Operator 變體 |
| `cilium-operator-aws` | AWS 專用 Operator（含 ENI IPAM）|
| `cilium-operator-azure` | Azure 專用 Operator（含 Azure IPAM）|
| `cilium-operator-alibabacloud` | 阿里雲專用 Operator |
| `hubble` | Hubble CLI 觀測工具 |
| `hubble-relay` | Hubble 資料聚合中繼服務 |
| `cilium-health` | 節點連通性健康探針 |
| `cilium-dbg` | Cilium 除錯工具（取代舊版 cilium CLI）|
| `bugtool` | 收集除錯資訊的工具 |
| `clustermesh-apiserver` | ClusterMesh 多叢集 API 服務 |

## 文件導覽

### 系統架構

| 文件 | 說明 |
|------|------|
| [系統架構總覽](./architecture.md) | Hive 依賴注入、Agent/Operator 元件結構、啟動流程 |
| [eBPF Datapath 深度解析](./ebpf-datapath.md) | bpf_lxc.c、bpf_host.c、bpf_xdp.c 核心 eBPF 程式解析 |
| [身份識別與安全模型](./identity-security.md) | CiliumIdentity、安全標籤、IPCache、Policy 解析 |

### 網路核心

| 文件 | 說明 |
|------|------|
| [網路架構](./networking.md) | VXLAN/Geneve Overlay、Native Routing、CNI Plugin、節點間路由 |
| [負載均衡與 kube-proxy 替代](./load-balancing.md) | kube-proxy 替代、Maglev 哈希、DSR 模式、Backend 狀態機 |
| 網路策略 | CNP/CCNP 策略語法、L3/L4/L7 規則、Egress Gateway |

### 進階功能

| 文件 | 說明 |
|------|------|
| Hubble 可觀測性 | Hubble 架構、流量追蹤、Prometheus 指標整合 |
| BGP 整合 | BGP Control Plane、CiliumBGPClusterConfig CRD、路由廣播 |
| ClusterMesh 多叢集 | 跨叢集服務同步、全域身份管理、Multi-Cluster Services API |
| 加密傳輸 | WireGuard 節點加密、IPSec 設定、透明加密實作 |

### API 與整合

| 文件 | 說明 |
|------|------|
| CRD 參考 | 18+ CRD 完整說明：CNP、CiliumEndpoint、CiliumNode 等 |
| Gateway API | Kubernetes Gateway API 實作、HTTPRoute、TLSRoute |
| IPAM | IP 地址管理模式：Host Scope、AWS ENI、Azure、CRD-based |

### 維運操作

| 文件 | 說明 |
|------|------|
| 安裝與設定 | Helm 安裝、設定選項、升級流程 |
| 可觀測性實踐 | Hubble UI、Grafana Dashboard、告警規則 |
| 故障排查 | 常見問題診斷、bugtool 使用、效能分析 |

::: info 相關章節
- [系統架構總覽](./architecture.md) — 深入了解 Cilium Agent 與 Operator 的內部架構
:::
