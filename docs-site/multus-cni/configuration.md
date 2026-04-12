---
layout: doc
---

# Multus CNI — 設定參考

本文提供 Multus CNI 所有設定參數的完整說明，所有內容皆引用真實原始碼路徑。

::: info 原始碼位置
設定型別定義位於 `pkg/types/types.go`、`pkg/types/conf.go`、`pkg/server/types.go`。
:::

::: info 相關章節
- 設定參數在 CNI 流程中的運作請參閱 [核心功能分析](./core-features)
- Thick Plugin 專屬設定請參閱 [Thick Plugin 深入剖析](./thick-plugin)
- 系統架構總覽請參閱 [系統架構](./architecture)
:::

## CNI 設定（NetConf）

`NetConf`（`pkg/types/types.go`）是 Multus 的主設定結構，以 JSON 格式寫入 CNI 設定目錄（`/etc/cni/net.d/`）。

### 完整設定範例

```json
{
  "name": "multus-cni-network",
  "type": "multus",
  "cniVersion": "0.3.1",
  "confDir": "/etc/cni/multus/net.d",
  "cniDir": "/var/lib/cni/multus",
  "binDir": "/opt/cni/bin",
  "kubeconfig": "/etc/cni/net.d/multus.d/multus.kubeconfig",
  "logFile": "/var/log/multus.log",
  "logLevel": "verbose",
  "logToStderr": false,
  "readinessindicatorfile": "/run/flannel/subnet.env",
  "namespaceIsolation": false,
  "globalNamespaces": "kube-system,default",
  "systemNamespaces": ["kube-system"],
  "multusNamespace": "kube-system",
  "retryDeleteOnError": false,
  "clusterNetwork": "flannel-conf",
  "defaultNetworks": []
}
```

### NetConf 欄位說明

#### 路徑設定

| 欄位 | JSON 鍵 | 預設值 | 說明 |
|------|---------|--------|------|
| `ConfDir` | `confDir` | `/etc/cni/multus/net.d` | CNI 設定檔目錄（從這裡讀取 `.conf`/`.conflist`） |
| `CNIDir` | `cniDir` | `/var/lib/cni/multus` | Scratch 快取目錄（儲存 ADD 時的委派設定） |
| `BinDir` | `binDir` | `/opt/cni/bin` | 委派 CNI Binary 搜尋目錄 |
| `Kubeconfig` | `kubeconfig` | `""` | kubeconfig 路徑（用於 Thin Plugin 向 API Server 認證） |

#### 日誌設定

| 欄位 | JSON 鍵 | 預設值 | 說明 |
|------|---------|--------|------|
| `LogFile` | `logFile` | `""` | 日誌輸出檔案路徑（空白表示不輸出至檔案） |
| `LogLevel` | `logLevel` | `"panic"` | 日誌等級：`panic`、`error`、`verbose`、`debug` |
| `LogToStderr` | `logToStderr` | `false` | 是否同時輸出日誌至標準錯誤輸出 |
| `LogOptions` | `logOptions` | `null` | 進階日誌選項（lumberjack 日誌輪替設定） |

#### 網路來源設定

| 欄位 | JSON 鍵 | 說明 |
|------|---------|------|
| `RawDelegates` | `delegates` | 直接在設定中嵌入委派 CNI 設定的 JSON 陣列（與 `clusterNetwork` 互斥） |
| `ClusterNetwork` | `clusterNetwork` | 預設網路的 NAD 名稱或 CNI 設定檔名（從 CRD、目錄或檔案讀取） |
| `DefaultNetworks` | `defaultNetworks` | 所有 Pod 都會自動附加的網路清單（NAD 名稱陣列） |

::: warning 互斥設定
`delegates` 與 `clusterNetwork`+`defaultNetworks` 不能同時設定。
- 使用 `delegates` 時，直接在設定中指定委派設定，不查詢 Kubernetes API
- 使用 `clusterNetwork` 時，從 Kubernetes CRD 或設定目錄讀取
:::

#### 命名空間設定

| 欄位 | JSON 鍵 | 預設值 | 說明 |
|------|---------|--------|------|
| `NamespaceIsolation` | `namespaceIsolation` | `false` | 啟用命名空間隔離，限制 Pod 只能使用相同命名空間的 NAD |
| `RawNonIsolatedNamespaces` | `globalNamespaces` | `""` | 逗號分隔的命名空間清單，這些命名空間的 NAD 可被任意 Pod 引用 |
| `SystemNamespaces` | `systemNamespaces` | `["kube-system"]` | 系統命名空間清單，這些命名空間的 Pod 不套用 `defaultNetworks` |
| `MultusNamespace` | `multusNamespace` | `"kube-system"` | Multus 自身使用的命名空間（用於讀取 `clusterNetwork`/`defaultNetworks`） |

#### 其他設定

| 欄位 | JSON 鍵 | 預設值 | 說明 |
|------|---------|--------|------|
| `ReadinessIndicatorFile` | `readinessindicatorfile` | `""` | 就緒指示檔路徑，Multus 等待此檔案存在後才處理 CNI 請求 |
| `RetryDeleteOnError` | `retryDeleteOnError` | `false` | 委派 DEL 失敗時，是否繼續嘗試下一個委派外掛 |
| `AuxiliaryCNIChainName` | `auxiliaryCNIChainName` | `""` | 輔助 CNI 鏈名稱 |
| `RuntimeConfig` | `runtimeConfig` | `null` | CNI RuntimeConfig（PortMaps、Bandwidth、IPs 等） |

## RuntimeConfig

`RuntimeConfig`（`pkg/types/types.go`）在 CNI ADD 時提供執行期額外設定：

| 欄位 | JSON 鍵 | 說明 |
|------|---------|------|
| `PortMaps` | `portMappings` | 連接埠對映設定陣列 |
| `Bandwidth` | `bandwidth` | 頻寬限制設定（入/出向速率與突發值） |
| `IPs` | `ips` | 要求的 IP 位址清單 |
| `Mac` | `mac` | 要求的 MAC 位址 |
| `InfinibandGUID` | `infinibandGUID` | 要求的 InfiniBand GUID |
| `DeviceID` | `deviceID` | SR-IOV 裝置 ID |
| `CNIDeviceInfoFile` | `CNIDeviceInfoFile` | CNI 裝置資訊檔案路徑（用於傳遞裝置詳細資訊） |

### PortMapEntry

| 欄位 | JSON 鍵 | 說明 |
|------|---------|------|
| `HostPort` | `hostPort` | 宿主機連接埠（1-65535） |
| `ContainerPort` | `containerPort` | 容器連接埠（1-65535） |
| `Protocol` | `protocol` | 協定：`tcp`、`udp`（預設 `tcp`） |
| `HostIP` | `hostIP` | 宿主機繫結 IP（可選） |

### BandwidthEntry

| 欄位 | JSON 鍵 | 說明 |
|------|---------|------|
| `IngressRate` | `ingressRate` | 入向速率限制（bps） |
| `IngressBurst` | `ingressBurst` | 入向突發大小（bytes） |
| `EgressRate` | `egressRate` | 出向速率限制（bps） |
| `EgressBurst` | `egressBurst` | 出向突發大小（bytes） |

## 委派設定（DelegateNetConf）

`DelegateNetConf`（`pkg/types/types.go`）代表單一委派網路的設定，由 Multus 從 NAD 轉換而來：

| 欄位 | JSON 鍵 | 說明 |
|------|---------|------|
| `IfnameRequest` | `ifnameRequest` | 要求的介面名稱（覆蓋自動產生的 `net{N}` 名稱） |
| `MacRequest` | `macRequest` | 要求的 MAC 位址 |
| `InfinibandGUIDRequest` | `infinibandGUIDRequest` | 要求的 InfiniBand GUID |
| `IPRequest` | `ipRequest` | 要求的 IP 位址清單 |
| `GatewayRequest` | `default-route` | 預設路由閘道 IP 清單 |
| `DeviceID` | `deviceID` | SR-IOV 裝置 ID（來自 kubelet checkpoint） |
| `ResourceName` | `resourceName` | SR-IOV 資源名稱 |
| `MasterPlugin` | 內部 | 是否為主要（預設）網路外掛 |
| `ConfListPlugin` | 內部 | 是否為 conflist 格式（多外掛鏈） |

## Pod 網路選擇（NetworkSelectionElement）

`NetworkSelectionElement`（`pkg/types/types.go`）代表 Pod Annotation 中的單一網路附加描述符，符合 Kubernetes Network CRD De-facto Standard。

### JSON 格式完整範例

```json
[
  {
    "name": "sriov-net",
    "namespace": "kube-system",
    "interface": "net1",
    "ips": ["10.56.217.171/24", "2001:db8::1/64"],
    "mac": "20:04:0f:f1:88:01",
    "infiniband-guid": "c2:b0:57:49:47:f1:a0:26",
    "portMappings": [
      {"hostPort": 8080, "containerPort": 80, "protocol": "tcp"}
    ],
    "bandwidth": {
      "ingressRate": 1000000,
      "ingressBurst": 1000000,
      "egressRate": 1000000,
      "egressBurst": 1000000
    },
    "deviceID": "0000:00:1f.6",
    "cni-args": {"foo": "bar"},
    "default-route": ["10.56.217.1"]
  }
]
```

### NetworkSelectionElement 欄位說明

| 欄位 | JSON 鍵 | 必填 | 說明 |
|------|---------|------|------|
| `Name` | `name` | ✅ | NetworkAttachmentDefinition 名稱 |
| `Namespace` | `namespace` | ❌ | NAD 所在命名空間（預設為 Pod 的命名空間） |
| `IPRequest` | `ips` | ❌ | 要求的 IP 位址清單（傳遞給委派外掛的 IPAM） |
| `MacRequest` | `mac` | ❌ | 要求的 MAC 位址 |
| `InfinibandGUIDRequest` | `infiniband-guid` | ❌ | 要求的 InfiniBand GUID |
| `InterfaceRequest` | `interface` | ❌ | 要求的介面名稱（覆蓋自動的 `net{N}`） |
| `PortMappingsRequest` | `portMappings` | ❌ | 連接埠對映設定 |
| `BandwidthRequest` | `bandwidth` | ❌ | 頻寬限制設定 |
| `DeviceID` | `deviceID` | ❌ | SR-IOV 裝置 ID |
| `CNIArgs` | `cni-args` | ❌ | 傳遞給委派外掛的額外 CNI 參數 |
| `GatewayRequest` | `default-route` | ❌ | Pod 的預設閘道 IP 清單 |

## Daemon 設定（ControllerNetConf）

`ControllerNetConf`（`pkg/server/types.go`）是 Thick Plugin 的 multus-daemon 設定結構，預設讀取自 `/etc/cni/net.d/multus.d/daemon-config.json`。

### 完整設定範例

```json
{
  "chrootDir": "/hostroot",
  "logFile": "/var/log/multus-daemon.log",
  "logLevel": "verbose",
  "logToStderr": true,
  "socketDir": "/run/multus",
  "metricsPort": 9091,
  "perNodeCertificate": {
    "enabled": true,
    "bootstrapKubeconfig": "/etc/kubernetes/bootstrap.kubeconfig",
    "certDir": "/var/lib/multus/certs",
    "certDuration": "24h"
  }
}
```

### ControllerNetConf 欄位說明

| 欄位 | JSON 鍵 | 預設值 | 說明 |
|------|---------|--------|------|
| `ChrootDir` | `chrootDir` | `""` | Chroot 目錄路徑，呼叫委派 CNI Binary 前先 chroot 至此目錄 |
| `LogFile` | `logFile` | `""` | 日誌輸出檔案路徑 |
| `LogLevel` | `logLevel` | `"panic"` | 日誌等級：`panic`、`error`、`verbose`、`debug` |
| `LogToStderr` | `logToStderr` | `false` | 是否輸出日誌至 stderr |
| `SocketDir` | `socketDir` | `"/run/multus/"` | Unix Socket 目錄路徑（`multus.sock` 建立於此） |
| `MetricsPort` | `metricsPort` | `null` | Prometheus 指標 HTTP 伺服器埠號（未設定則不啟動） |
| `PerNodeCertificate` | `perNodeCertificate` | `null` | 每節點 TLS 憑證設定 |

### PerNodeCertificate 欄位說明

| 欄位 | JSON 鍵 | 說明 |
|------|---------|------|
| `Enabled` | `enabled` | 是否啟用每節點 TLS 憑證自動管理 |
| `BootstrapKubeconfig` | `bootstrapKubeconfig` | 用於首次憑證申請的 Bootstrap kubeconfig 路徑 |
| `CertDir` | `certDir` | 憑證儲存目錄路徑 |
| `CertDuration` | `certDuration` | 憑證有效期限（預設 `"10m"`，格式為 Go duration string） |

## K8sArgs — CNI_ARGS 解析

`K8sArgs`（`pkg/types/types.go`）定義從 `CNI_ARGS` 環境變數解析出的 Kubernetes 特有資訊：

| 欄位 | CNI_ARGS 鍵 | 說明 |
|------|------------|------|
| `K8S_POD_NAME` | `K8S_POD_NAME` | Pod 名稱 |
| `K8S_POD_NAMESPACE` | `K8S_POD_NAMESPACE` | Pod 命名空間 |
| `K8S_POD_INFRA_CONTAINER_ID` | `K8S_POD_INFRA_CONTAINER_ID` | Pause 容器 ID |
| `K8S_POD_UID` | `K8S_POD_UID` | Pod UID |

## 設定自動生成模式

當 Thick Plugin 使用 `multus-config-file: auto` 選項啟動時，`config.Manager`（`pkg/server/config/`）根據以下規則自動產生 Multus CNI 設定：

![Multus 設定自動生成流程](/diagrams/multus-cni/multus-config-1.png)

自動生成的設定確保 Multus 的 CNI 設定（以 `00-` 前綴）優先於其他 CNI 設定，從而成為叢集的主 CNI 外掛。
