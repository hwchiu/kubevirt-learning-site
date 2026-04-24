---
layout: doc
title: Cluster API Provider MAAS — 核心功能
---

# Cluster API Provider MAAS — 核心功能

## 機器佈建流程（Machine Provisioning）

CAPMAAS 的機器佈建分為兩個階段：**Allocate（申請）** 與 **Deploy（部署）**，完全透過 MAAS REST API 驅動。

### 階段一：Allocate（資源申請）

Allocator 依照 `MaasMachineSpec` 的條件向 MAAS 請求符合資源需求的機器：

```go
// 檔案: pkg/maas/machine/machine.go

allocator := s.maasClient.
    Machines().
    Allocator().
    WithCPUCount(*mm.Spec.MinCPU).
    WithMemory(*mm.Spec.MinMemoryInMB)

if failureDomain != nil {
    allocator.WithZone(*failureDomain)
}

if mm.Spec.ResourcePool != nil {
    allocator.WithResourcePool(*mm.Spec.ResourcePool)
}

if len(mm.Spec.Tags) > 0 {
    allocator.WithTags(mm.Spec.Tags)
}

m, err = allocator.Allocate(ctx)
```

Allocate 成功後，CAPMAAS 立刻設定 ProviderID 並 Patch 回 Kubernetes，格式為：

```
maas:///<availabilityZone>/<systemID>
```

例如：`maas:///default/abc123`

### 階段二：Deploy（部署）

取得機器後，Controller 從 `Machine.Spec.Bootstrap.DataSecretName` 讀取 Bootstrap Secret，Base64 編碼後作為 user-data 注入部署請求：

```go
// 檔案: pkg/maas/machine/machine.go

noSwap := 0
if _, err := m.Modifier().SetSwapSize(noSwap).Update(ctx); err != nil {
    return nil, errors.Wrapf(err, "Unable to disable swap")
}

deployingM, err := m.Deployer().
    SetUserData(userDataB64).
    SetOSSystem("custom").
    SetEphemeralDeploy(mm.Spec.DeployInMemory).
    SetDistroSeries(mm.Spec.Image).Deploy(ctx)
```

::: tip 為何在部署前停用 Swap？
Kubernetes 節點預設要求停用 Swap。CAPMAAS 透過 MAAS API 在部署前主動呼叫 `SetSwapSize(0)` 修改機器設定，確保節點啟動後不需手動介入。
:::

### 機器狀態狀態機

```
New ──commissioned──► Ready
                         │
                         ▼ Allocate
                      Allocated
                         │
                         ▼ Deploy
                      Deploying
                         │
                         ▼ 完成
                      Deployed ◄────── CAPMAAS 標記 Ready
                         │
                         ▼ 刪除時
                    Disk erasing
                         │
                         ▼
                      Releasing
                         │
                         ▼
                       Ready（重新進入可用池）
```

| 狀態 | CAPMAAS 行為 |
|------|-------------|
| `Allocated` | 設定 NotReady，等待 Deploy 完成 |
| `Deploying` | 設定 NotReady，持續等待 |
| `Deployed` | 設定 Ready，開始 DNS/ProviderID 配置 |
| `Ready` | 非預期狀態（已回收），設定 FailureReason |
| `Disk erasing` | 非預期狀態，設定 FailureReason |
| `New` | 非預期狀態，設定 FailureReason |

## DNS 管理（作為 API Server 負載平衡）

CAPMAAS 不使用外部負載平衡器（如 AWS ELB），而是利用 **MAAS DNS Resource** 實作 API Server 的 DNS 輪詢式負載平衡。

### DNS 協調流程

```go
// 檔案: pkg/maas/dns/dns.go

func (s *Service) ReconcileDNS() error {
    s.scope.V(2).Info("Reconciling DNS")
    ctx := context.TODO()

    dnsResource, err := s.GetDNSResource()
    if err != nil && !errors.Is(err, ErrNotFound) {
        return err
    }

    dnsName := s.scope.GetDNSName()

    if dnsResource == nil {
        if _, err = s.maasClient.DNSResources().
            Builder().
            WithFQDN(s.scope.GetDNSName()).
            WithAddressTTL("10").
            WithIPAddresses(nil).
            Create(ctx); err != nil {
            return errors.Wrapf(err, "Unable to create DNS Resources")
        }
    }

    s.scope.SetDNSName(dnsName)
    return nil
}
```

### DNS 名稱自動生成

若使用者未指定 `ControlPlaneEndpoint`，CAPMAAS 會自動生成一個 DNS 名稱：

```go
// 檔案: pkg/maas/scope/cluster.go

func (s *ClusterScope) GetDNSName() string {
    if !s.Cluster.Spec.ControlPlaneEndpoint.IsZero() {
        return s.Cluster.Spec.ControlPlaneEndpoint.Host
    }

    if s.MaasCluster.Status.Network.DNSName != "" {
        return s.MaasCluster.Status.Network.DNSName
    }

    uid := uuid.New().String()
    dnsName := fmt.Sprintf("%s-%s.%s", s.Cluster.Name, uid[len(uid)-DnsSuffixLength:], s.MaasCluster.Spec.DNSDomain)

    s.SetDNSName(dnsName)
    return dnsName
}
```

格式：`<cluster-name>-<6位uuid>.<dnsDomain>`  
例如：`my-cluster-a1b2c3.maas`

### Control Plane 機器 IP 同步

每次 `MaasClusterReconciler.reconcileNormal()` 執行時，DNS Service 會比對當前所有 CP 機器的狀態：

- 正常運行中（Deployed + Powered）→ 加入 DNS 記錄
- 被刪除或不健康 → 從 DNS 記錄移除

```go
// 檔案: controllers/maascluster_controller.go

func (r *MaasClusterReconciler) reconcileDNSAttachments(
    clusterScope *scope.ClusterScope,
    dnssvc *dns.Service,
) error {
    machines, err := clusterScope.GetClusterMaasMachines()
    // ...
    if err := dnssvc.UpdateDNSAttachments(runningIpAddresses); err != nil {
        return err
    }
    return nil
}
```

## Resource Pool 與 Tag 篩選

### Resource Pool

透過 `MaasMachineSpec.ResourcePool` 欄位，CAPMAAS 在呼叫 MAAS Allocate API 時，限定只在指定的資源池中尋找可用機器：

```yaml
# 檔案: templates/cluster-template.yaml
spec:
  template:
    spec:
      minCPU: 4
      minMemory: 8192
      image: custom/u-2204-0-k-1264-0
      resourcePool: resourcepool-controller
      tags:
        - hello-world
```

### 機器篩選優先順序

| 條件 | MAAS API 參數 | 必填 |
|------|-------------|------|
| CPU 數量下限 | `WithCPUCount()` | 是（`minCPU`）|
| 記憶體下限（MB）| `WithMemory()` | 是（`minMemory`）|
| 可用區 | `WithZone()` | 否（`failureDomain`）|
| 資源池 | `WithResourcePool()` | 否（`resourcePool`）|
| 標籤 | `WithTags()` | 否（`tags`）|

## In-Memory 部署（記憶體內部署）

設定 `deployInMemory: true` 時，CAPMAAS 透過 `SetEphemeralDeploy(true)` 告知 MAAS 將作業系統載入記憶體而非寫入磁碟：

```go
// 檔案: pkg/maas/machine/machine.go

if mm.Spec.DeployInMemory {
    s.scope.Info("Machine will be deployed in memory", "system-id", m.SystemID())
}

deployingM, err := m.Deployer().
    SetUserData(userDataB64).
    SetOSSystem("custom").
    SetEphemeralDeploy(mm.Spec.DeployInMemory).
    SetDistroSeries(mm.Spec.Image).Deploy(ctx)
```

::: warning In-Memory 部署的限制
- **MAAS 版本**：需 ≥ 3.5.10、≥ 3.6.3 或 ≥ 3.7.1
- **最小 RAM**：機器需至少 **16 GB RAM**
- 機器重啟後狀態不會保留（設計如此）
:::

## 機器回收（Release）

刪除 `MaasMachine` 時，Controller 先確保 DNS 記錄已移除（CP 機器），再呼叫 MAAS Release API：

```go
// 檔案: controllers/maasmachine_controller.go

if err := machineSvc.ReleaseMachine(m.ID); err != nil {
    machineScope.Error(err, "failed to release machine")
    return ctrl.Result{}, err
}

conditions.MarkFalse(machineScope.MaasMachine, infrav1beta1.MachineDeployedCondition,
    clusterv1.DeletedReason, clusterv1.ConditionSeverityInfo, "")

controllerutil.RemoveFinalizer(maasMachine, infrav1beta1.MachineFinalizer)
```

Release 後，機器重新進入 MAAS 的 `Ready` 狀態，可被其他叢集重新 Allocate。

## 電源管理

若 Deployed 狀態的機器意外關機（`MachinePowered = false`），CAPMAAS 會自動嘗試開機：

```go
// 檔案: controllers/maasmachine_controller.go

case machineScope.MachineIsInKnownState() && !m.Powered:
    if *machineScope.GetMachineState() == infrav1beta1.MachineStateDeployed {
        machineScope.Info("Deployed machine is powered off trying power on")
        if err := machineSvc.PowerOnMachine(); err != nil {
            return ctrl.Result{}, errors.Wrap(err, "unable to power on deployed machine")
        }
        return ctrl.Result{RequeueAfter: 1 * time.Minute}, nil
    }
```

::: info 相關章節
- [系統架構](./architecture) — 了解 Controller 架構設計
- [控制器與 API](./controllers-api) — MaasMachineSpec 欄位完整說明
- [外部整合](./integration) — MAAS API 連線與設定方式
:::
