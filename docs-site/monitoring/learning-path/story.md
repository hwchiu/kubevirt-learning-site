---
layout: doc
title: Monitoring — 學習路徑：讓 VM 不再默默消失
---

<script setup>
</script>

# 讓 VM 不再默默消失

> 一個 SRE 在凌晨兩點被叫醒之後，決定把 KubeVirt 監控做對的故事。

---

## 第 1 章：「凌晨兩點的慘案」

手機在黑暗中震動。阿明瞇著眼看螢幕——03:47。

是 on-call 輪值號碼。

「阿明，客戶說他們的 VM 全部沒辦法連線，已經兩個小時了。」電話那頭，值班主管的聲音沒有任何感情。

*兩個小時。*

阿明坐起來，打開筆電。Prometheus Alertmanager 的 Slack channel——空的。Grafana——他隱約記得有一個 Kubernetes Node 的 Dashboard，打開來看，節點全都健康。但 KubeVirt 的 VM？根本沒有任何圖表。

他登入叢集：

```bash
kubectl get vmi -A
```

輸出讓他胃下沉：

```
NAMESPACE   NAME          PHASE     AGE
prod        web-vm-01     Failed    2h14m
prod        web-vm-02     Failed    2h14m
prod        web-vm-03     Failed    2h14m
```

`Failed`。兩個多小時了。沒有任何人知道。

*我以為我有設監控的。*

天亮之後，他坐在辦公室裡寫事後報告。問題很清楚：KubeVirt 的 VMI 狀態根本沒有被納入任何告警範圍。他對 Prometheus 設定了 Node Exporter、kube-state-metrics，但 KubeVirt 有自己的指標端點——而他從來沒有設定 Prometheus 去抓它。

老闆問：「為什麼沒有告警？」

阿明沉默了兩秒，然後說：「因為我從來沒認真搞清楚 KubeVirt 暴露了什麼指標，以及怎麼讓 Prometheus 抓到它們。」

這句話讓他難受了整整一天。但也讓他決定把這件事做對。

---

> ### 📚 去這裡深入了解
> - [KubeVirt Monitoring 專案簡介](/monitoring/) — 了解這個集中式監控專案的全貌與目標
>
> 讀完後，你應該能說清楚 KubeVirt Monitoring 專案解決了什麼問題，以及它和一般的 kube-state-metrics 有何不同。

---

## 第 2 章：「探索 KubeVirt Metrics：virt-api 和 virt-handler 暴露了什麼」

阿明從頭開始。他想先搞清楚 KubeVirt 的指標從哪裡來。

```bash
kubectl get pods -n kubevirt
```

```
NAME                               READY   STATUS    RESTARTS
virt-api-7d9f8b6c4-xk2nt           1/1     Running   0
virt-controller-5c8d9f7b8-p4mn     1/1     Running   0
virt-handler-4vhqp                 1/1     Running   0  (每個 Node 一個)
virt-handler-9krtf                 1/1     Running   0
virt-operator-6b7c9d8f5-j2lp       1/1     Running   0
```

*這些 Pod 各自暴露了什麼？*

他用 `kubectl port-forward` 連到 `virt-api` 的 metrics 端點，看到了一長串輸出——

```
# HELP kubevirt_vmi_phase_count VMI phase
kubevirt_vmi_phase_count{phase="Running"} 0
kubevirt_vmi_phase_count{phase="Scheduling"} 0
kubevirt_vmi_phase_count{phase="Failed"} 3
```

*這就是了。*昨晚如果 Prometheus 有在抓這個指標，一個簡單的告警就能在 VMI 進入 `Failed` 狀態的那一刻通知他。

他繼續翻，發現指標分類相當豐富：

- **VMI 生命週期**：`kubevirt_vmi_phase_count`，標籤有 `phase`（Running、Scheduling、Failed、Pending…）
- **Live Migration**：`kubevirt_vmi_migration_phase_transition_time_from_to_seconds`，記錄遷移各階段耗時
- **vCPU 使用率**：`kubevirt_vmi_vcpu_seconds_total`，可以算出 CPU 使用率
- **記憶體 balloon**：`kubevirt_vmi_memory_used_bytes`、`kubevirt_vmi_memory_available_bytes`
- **virt-launcher OOMKill**：`kubevirt_vmi_launcher_memory_overhead_bytes`

阿明打開筆記本，開始整理：

> `virt-handler` 在每台 Node 上跑，它直接和 libvirt 溝通，所以 **VMI 層級的詳細指標**（vCPU、記憶體、網路、磁碟 I/O）主要從這裡來。
>
> `virt-api` 暴露的是 **API 層指標**，例如 REST API 的 latency 和請求數。
>
> `virt-controller` 則負責 **VMI 生命週期狀態**的彙總指標。

*KubeVirt 暴露的指標遠比我想像的豐富。問題從來不是「沒有指標」，而是「我沒有讓 Prometheus 去抓」。*

---

> ### 📚 去這裡深入了解
> - [核心功能分析](/monitoring/core-features) — 了解 100+ 個 KubeVirt 指標的分類與用途，以及 Grafana Dashboard 的設計
>
> 讀完後，你應該能列出 KubeVirt 監控中最關鍵的 5 種指標類型，並說明各自對應的監控目的。

---

## 第 3 章：「設定 ServiceMonitor：讓 Prometheus 抓到 KubeVirt 指標」

知道指標在哪裡之後，下一步是讓 Prometheus 找到它。

阿明的叢集用的是 Prometheus Operator，所以他需要建立 `ServiceMonitor`。他先確認 KubeVirt 的 Service 有沒有正確暴露 metrics port：

```bash
kubectl get svc -n kubevirt -o wide
```

```
NAME                    TYPE        CLUSTER-IP     PORT(S)
kubevirt-prometheus-metrics   ClusterIP   10.96.45.12   443/TCP
virt-api                ClusterIP   10.96.12.34   443/TCP, 8443/TCP
```

`kubevirt-prometheus-metrics` 這個 Service 是 KubeVirt 專門為 Prometheus 準備的。阿明打開它的定義，確認 port 名稱是 `metrics`，然後建立 ServiceMonitor：

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kubevirt-servicemonitor
  namespace: kubevirt
  labels:
    prometheus.io/scrapeable: "true"
spec:
  selector:
    matchLabels:
      prometheus.kubevirt.io: ""
  endpoints:
    - port: metrics
      scheme: https
      tlsConfig:
        insecureSkipVerify: true
      honorLabels: true
```

`kubectl apply` 之後，他等了兩分鐘，然後去 Prometheus UI 搜尋：

```
kubevirt_vmi_phase_count
```

結果出現了。標籤有 `phase`、`namespace`、`name`。

*這就是我昨晚應該做的事。*

他深吸一口氣。這不是什麼高深技術，就是一個 ServiceMonitor YAML。但這個 YAML 缺席了兩年，導致昨晚那場慘案。

阿明在筆記裡寫下：

> 可觀測性的第一步不是寫告警，而是確保 **指標可以被收集**。沒有抓到指標，後面所有事情都是空中樓閣。

---

> ### 📚 去這裡深入了解
> - [外部整合](/monitoring/integration) — ServiceMonitor 設定、Prometheus Operator 整合、跨 Operator 指標收集的完整說明
>
> 讀完後，你應該能獨立設定 ServiceMonitor 讓 Prometheus 抓取 KubeVirt 指標，並理解 `tlsConfig` 為何必要。

---

## 第 4 章：「建立第一條告警規則：VMI Failed 立刻通知我」

指標有了。現在要讓它們「說話」。

阿明的目標很明確：**只要有任何 VMI 進入 `Failed` 狀態，五分鐘內要收到 Slack 通知**。

他開始寫 PrometheusRule：

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: kubevirt-vmi-alerts
  namespace: kubevirt
  labels:
    prometheus.io/rule: "true"
spec:
  groups:
    - name: kubevirt.vmi.rules
      rules:
        - alert: KubeVirtVMIFailed
          expr: |
            kubevirt_vmi_phase_count{phase="Failed"} > 0
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "VMI in Failed state detected"
            description: "&#123;&#123; $value &#125;&#125; VMI(s) in namespace &#123;&#123; $labels.namespace &#125;&#125; are in Failed state."
            runbook_url: "https://runbooks.prometheus-operator.dev/runbooks/kubevirt/kubevirtVMIFailed"
```

Apply 之後，他用一個測試 VMI 來驗證——故意讓它進入 Failed 狀態，然後等待。

一分鐘後，Slack 叫了。

那個聲音讓阿明愣了一秒，然後笑出來。

*如果昨晚有這條告警，我就不用在凌晨三點四十七分被電話叫醒了。*

但他很快發現一個問題：`description` 裡的 `runbook_url` 他隨手填了一個不存在的連結。告警觸發了，但值班工程師打開連結——404。

*告警觸發之後，工程師要做什麼？*

這個問題把他帶向了下一章。

---

> ### 📚 去這裡深入了解
> - [指標與告警規則](/monitoring/metrics-alerts) — PrometheusRule 結構、PromQL 表達式最佳實踐、告警標籤規範
>
> 讀完後，你應該能獨立撰寫符合 KubeVirt Monitoring 規範的 PrometheusRule，並理解 `for`、`labels.severity`、`annotations.runbook_url` 的意義。

---

## 第 5 章：「認識 Runbook：告警觸發後要做什麼」

阿明打開 KubeVirt Monitoring 的 GitHub repo，找到 `docs/runbooks/` 目錄。

裡面有 75 個 Markdown 檔案，每個對應一條告警規則。他翻開 `KubeVirtVMIFailed.md`：

```markdown
## Meaning
This alert fires when one or more VMIs are in the Failed phase...

## Impact
Virtual machines are not running and workloads are interrupted...

## Diagnosis
1. Check the VMI status:
   kubectl get vmi -A -o wide

2. Look for events:
   kubectl describe vmi <name> -n <namespace>

3. Check virt-launcher logs:
   kubectl logs <virt-launcher-pod> -n <namespace>

## Mitigation
- If the issue is a node failure, consider live migration...
- If the VMI image is corrupted, restore from snapshot...
```

*這才是告警的完整形態。*

光有 Prometheus 說「有 VMI Failed」是不夠的——值班工程師在凌晨三點收到告警，需要的是一份清單：第一步做什麼、第二步做什麼、什麼情況下升級。

阿明把他的 PrometheusRule 的 `runbook_url` 改成了真正的連結，指向 KubeVirt Monitoring repo 裡對應的 Runbook。

他也意識到 75 個 Runbook 背後有一個重要設計原則：**每一條告警都應該是可操作的（actionable）**。一條告警如果觸發之後工程師不知道要做什麼，這條告警就是噪音，而不是訊號。

他在筆記裡記下：

> 告警 = 問題的偵測 + 解決問題的路徑。
> 缺少 Runbook 的告警，就像火警警報沒有疏散路線圖。

---

> ### 📚 去這裡深入了解
> - [核心功能分析](/monitoring/core-features) — Runbook 的結構設計、75 個告警的分類、Runbook 自動化驗證流程
>
> 讀完後，你應該能理解一個好的 Runbook 包含哪些必要區段，以及 KubeVirt Monitoring 如何確保 Runbook 的品質一致性。

---

## 第 6 章：「Grafana Dashboard：建立 VM 狀態一覽」

告警解決了「出事要通知我」的問題。但阿明還想要一個地方，可以在**不出事的時候**主動觀察 VM 群的健康狀態。

他打開 KubeVirt Monitoring repo 的 `dashboards/` 目錄，找到現成的 Grafana Dashboard JSON：

- `kubevirt-top-consumers.json`：按資源消耗排名的 VM 清單
- `kubevirt-virt-controller.json`：virt-controller 的工作負載狀態
- `kubevirt-infrastructure-resources.json`：底層基礎設施資源概覽

阿明把這些 JSON 匯入 Grafana，打開第一個 Dashboard。

畫面上出現了他一直以來缺少的東西：一個清楚的 VM 狀態矩陣，每一個 VM 是什麼 phase、CPU 用了多少、記憶體 balloon 膨脹到哪裡，全部一目了然。

*如果昨晚這個 Dashboard 是開著的，值班工程師就算沒收到告警，也應該看得到異常。*

他開始自訂一個給自己環境用的 Dashboard，核心面板包括：

1. **VMI Phase Distribution**：用 `kubevirt_vmi_phase_count` 做成圓餅圖，一眼看出有多少 Running / Scheduling / Failed
2. **Top CPU Consumers**：用 `rate(kubevirt_vmi_vcpu_seconds_total[5m])` 排序找出消耗 vCPU 最多的 VM
3. **Live Migration Progress**：用 migration 相關指標追蹤正在進行中的 VM 遷移
4. **OOMKill 事件**：`kubevirt_vmi_launcher_memory_overhead_bytes` 超過閾值的 VM

花了兩個小時，他建立了一個讓他滿意的 Dashboard。他把它釘在監控大螢幕上。

那一刻，他感覺到了久違的踏實感。

---

> ### 📚 去這裡深入了解
> - [核心功能分析](/monitoring/core-features) — Grafana Dashboard 結構、現有 Dashboard 的設計邏輯、指標視覺化最佳實踐
>
> 讀完後，你應該能理解 KubeVirt 官方 Dashboard 的設計思路，並能根據自己環境需求擴充或客製化面板。

---

## 第 7 ��：「monitoringlinter：為什麼告警規則也需要 linter」

一週後，阿明的同事小琳也開始為她負責的 CDI（Containerized Data Importer）元件寫告警規則。她的第一版 PrometheusRule 寫完後，請阿明幫忙看看。

阿明打開 YAML，馬上發現幾個問題：

- 有一條告警沒有 `severity` 標籤
- `runbook_url` 用的是 placeholder，還沒換成真實連結
- 有一條 `expr` 算式在 label 維度上有 cardinality 爆炸風險

*每次都要用眼睛看？*

阿明想起 KubeVirt Monitoring 有一個叫 `monitoringlinter` 的工具。他拉了 repo 下來看了一下：

```bash
go run ./tools/monitoring/monitoringlinter/cmd/main.go \
  --rules-file path/to/your/rules.yaml
```

輸出是這樣的：

```
FAIL: alert KubeVirtVMIPending missing required label 'severity'
FAIL: alert KubeVirtVMIPending runbook_url is not a valid URL
WARN: alert KubeVirtHighMemoryUsage expression may cause high cardinality
```

*這就是 linter 存在的意義。*

`monitoringlinter` 會檢查：
- 必要欄位是否齊全（`severity`、`runbook_url`）
- 告警名稱是否符合命名規範
- 表達式是否有潛在的效能問題
- `for` 時間窗口是否合理（太短容易 flapping、太長反應太慢）

阿明把 monitoringlinter 加進了他們的 CI pipeline。從此，每次有人送 PR 修改告警規則，linter 都會自動跑一遍。

他告訴小琳：「告警規則就跟程式碼一樣，要 review，要 lint，要測試。不然它就只是一個假裝自己有監控的 YAML。」

小琳笑了。「那 monitoringlinter 就是告警規則的 golangci-lint？」

「差不多就是這樣。」

---

> ### 📚 去這裡深入了解
> - [指標與告警規則](/monitoring/metrics-alerts) — monitoringlinter 的檢查項目、metricsdocs 生成器、告警規則的 CI 整合方式
>
> 讀完後，你應該能設定 monitoringlinter 在你的 CI pipeline 中自動檢查告警規則，並理解它具體驗證哪些項目。

---

## 第 8 章：「跨 Operator 整合：Monitoring 專案怎麼統一管理生態系告警」

一個月後，阿明被邀請加入公司的平台工程小組，負責規劃整個 KubeVirt 生態系的監控標準化。

這時候他才真正理解 **kubevirt/monitoring** 這個 repo 存在的深層原因。

KubeVirt 生態系有好幾個相關專案：
- **KubeVirt**（核心 VM 管理）
- **CDI**（VM 磁碟映像匯入）
- **Forklift**（VM 遷移工具）
- **Node Maintenance Operator**（節點維護）

每個專案都有自己的告警規則。如果各自為政，很快就會出現問題：

- A 專案的告警用 `critical`，B 專案的用 `CRITICAL`，C 專案的用數字 `1`
- 有些 Runbook 有詳細的 Diagnosis 步驟，有些只有一行「請聯繫 XXX」
- 不同專案的 Dashboard 設計風格完全不一樣，值班工程師切換時要重新適應

`kubevirt/monitoring` 解決的就是這個問題。它是一個**中央倉庫**：

- 統一的告警規則命名規範
- 統一的 Runbook 格式（每個都有 Meaning、Impact、Diagnosis、Mitigation 四個區段）
- 統一的 monitoringlinter 作為品質閘門
- 統一的 Grafana Dashboard 設計語言

各個子專案透過 Git submodule 或者直接 PR 的方式把各自的告警規則和 Runbook 貢獻到這個中央倉庫。這樣，整個生態系的監控實踐就能保持一致。

阿明在小組的提案裡寫下：

> 監控的一致性不是技術問題，而是**協作問題**。好的監控基礎設施需要：
> 1. 標準（誰決定告警規則怎麼寫）
> 2. 工具（monitoringlinter 確保標準被遵守）
> 3. 流程（PR review + CI 把關）
> 4. 文化（工程師認為監控是功能，不是事後補救）

這份提案被通過了。

阿明看著監控螢幕上的 Dashboard，想起一個月前凌晨三點四十七分的那通電話。

那通電話讓他覺得丟臉，但也讓他把整件事做對了。

---

> ### 📚 去這裡深入了解
> - [外部整合](/monitoring/integration) — 跨 Operator 指標收集架構、各子專案如何整合進 Monitoring 專案
> - [系統架構](/monitoring/architecture) — KubeVirt Monitoring 的 4 個核心工具與整體 CI/CD 流程
>
> 讀完後，你應該能解釋 kubevirt/monitoring 如何作為集中式倉庫統一管理多個子專案的告警規則，以及 monitoringlinter 在整個流程中扮演什麼角色。

---

## 故事結語

阿明的路徑從一次失敗開始，走過了以下每一步：

| 章節 | 學到了什麼 |
|------|-----------|
| 第 1 章 | 沒有監控的代價——VM 靜靜死掉兩個小時 |
| 第 2 章 | KubeVirt 暴露的指標遠比你想像的豐富 |
| 第 3 章 | ServiceMonitor 是讓 Prometheus 找到指標的第一步 |
| 第 4 章 | PrometheusRule 的正確寫法與 severity/runbook 規範 |
| 第 5 章 | Runbook 讓告警從「噪音」變成「可操作的訊號」 |
| 第 6 章 | Grafana Dashboard 讓你在不出事時主動觀察 |
| 第 7 章 | monitoringlinter 把監控品質納入 CI 流程 |
| 第 8 章 | kubevirt/monitoring 如何統一整個生態系的監控實踐 |

---

👈 [回到學習路徑入口](./index)
