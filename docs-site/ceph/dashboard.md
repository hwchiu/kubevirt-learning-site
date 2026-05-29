---
layout: doc
title: Ceph — Dashboard
---

# Ceph — Dashboard

Ceph Dashboard 不是單純的 Web UI；從原始碼看，它其實是 **建在 `ceph-mgr` 之上的一個完整管理模組**，負責把叢集健康度、Prometheus 指標、Grafana 儀表板、Alertmanager silence 與多種 REST API 聚合成同一個入口。

## Dashboard 的三層結構

<pre>
Browser (Angular frontend)
          |
          v
Dashboard REST controllers
(CherryPy + Router / APIRouter / RESTController)
          |
          v
ceph-mgr dashboard module
          |
          +--> Ceph cluster state / mgr APIs
          +--> Prometheus module / PromQL
          +--> Grafana API
          +--> Alertmanager API
</pre>

## 後端入口：`module.py`

Dashboard 的後端入口在 `src/pybind/mgr/dashboard/module.py`。這個檔案負責 CherryPy、SSL、認證工具與模組初始化。

可以把它理解為：

- 對外：暴露 Web 與 REST API
- 對內：調用 `ceph-mgr` 能取得的叢集資料與外部監控服務

### Controller abstraction 很明確

`src/pybind/mgr/dashboard/controllers/__init__.py` 匯出了多個核心抽象：

- `Router`
- `APIRouter`
- `UIRouter`
- `RESTController`

這代表 Dashboard API 並不是臨時拼湊，而是有明確 controller / route framework 的模組化後端。

## 前端是 Angular，不是單純模板頁

`src/pybind/mgr/dashboard/frontend/package.json` 顯示 Dashboard frontend 使用 Angular 19，並搭配 chart 套件來呈現趨勢圖與容量圖。

因此 Dashboard 的心智模型比較接近：

- 後端：`ceph-mgr` 內建管理 API
- 前端：Angular SPA
- 外部資料源：Prometheus / Alertmanager / Grafana

## Overview 頁面到底看了哪些資料？

從 `src/pybind/mgr/dashboard/frontend/src/app/ceph/overview/overview.component.ts`、`health-card` 與 `storage-card` 可以看到，首頁總覽至少聚合了以下資訊：

- cluster health summary
- `mon` / `mgr` / `osd` / host 狀態
- 已用 / 總容量
- 容量成長趨勢
- nearfull / full threshold
- 硬體摘要與升級資訊
- alert 與 telemetry 狀態

### Health API 入口

`health.service.ts` 直接揭露了前端常用的 API：

```ts
// 檔案: src/pybind/mgr/dashboard/frontend/src/app/shared/api/health.service.ts
const BASE_URL = 'api/health'

getFullHealth() {
  return this.http.get(`${BASE_URL}/full`)
}

getMinimalHealth() {
  return this.http.get(`${BASE_URL}/minimal`)
}

getHealthSnapshot(): Observable<HealthSnapshotMap> {
  return this.http.get<HealthSnapshotMap>(`${BASE_URL}/snapshot`)
}
```

這表示 Dashboard 前端不是自己拼接 cluster state，而是透過後端整理好的 health API 取得不同粒度的健康資訊。

## Prometheus 整合：Dashboard 的觀測核心

從 `src/pybind/mgr/dashboard/controllers/prometheus.py` 與 frontend 的 `prometheus.service.ts` 可以看出，Dashboard 會把 Prometheus / Alertmanager 包成自己的 REST 入口。

```ts
// 檔案: src/pybind/mgr/dashboard/frontend/src/app/shared/api/prometheus.service.ts
private baseURL = 'api/prometheus'

getPrometheusData(params: any): any {
  return this.http.get<any>(`${this.baseURL}/data`, { params })
}

getPrometheusQueryData(params: { params: string }) {
  return this.http.get<any>(`${this.baseURL}/prometheus_query_data`, { params })
}

getRules() {
  return this.http.get(`${this.baseURL}/rules`)
}
```

前端常見功能包括：

- 查詢即時 gauge / range data
- 讀取 alert groups
- 管理 silences
- 取得 recording / alerting rules
- 檢查 Prometheus 與 Alertmanager 是否已設定

### Overview 真的用哪些 PromQL？

`dashboard-promqls.enum.ts` 和 `storage-overview.service.ts` 把很多首頁卡片的公式直接寫出來了。

```ts
// 檔案: src/pybind/mgr/dashboard/frontend/src/app/shared/enum/dashboard-promqls.enum.ts
export enum UtilizationCardQueries {
  USEDCAPACITY = 'ceph_cluster_total_used_bytes',
  WRITEIOPS = 'sum(rate(ceph_pool_wr[1m]))',
  READIOPS = 'sum(rate(ceph_pool_rd[1m]))',
  READLATENCY = 'avg_over_time(ceph_osd_apply_latency_ms[1m])',
  WRITELATENCY = 'avg_over_time(ceph_osd_commit_latency_ms[1m])',
  READCLIENTTHROUGHPUT = 'sum(rate(ceph_pool_rd_bytes[1m]))',
  WRITECLIENTTHROUGHPUT = 'sum(rate(ceph_pool_wr_bytes[1m]))'
}
```

而 `storage-overview.service.ts` 又補上容量趨勢與風險指標：

- `sum(rate(ceph_osd_stat_bytes_used[7d])) * 86400`：平均每日容量成長
- `(sum(ceph_osd_stat_bytes)) / (sum(rate(ceph_osd_stat_bytes_used[7d])) * 86400)`：推估距離容量耗盡的時間
- `ceph_osd_nearfull_ratio` / `ceph_osd_full_ratio`：容量警戒門檻

這些細節很重要，因為它說明 Dashboard 的圖表不是「看起來像監控」，而是直接建在 Ceph exporter metrics 之上。

## Prometheus module 本身做了什麼？

`src/pybind/mgr/prometheus/module.py` 是另一個關鍵檔案。它負責從 `ceph-mgr` 匯出 Ceph metrics，涵蓋 health、OSD、pool、daemon metadata 等面向。

因此觀測鏈路大致是：

1. `prometheus` mgr module 匯出 metrics
2. Prometheus 抓取 metrics 並執行 rules / recording
3. Dashboard 經由自己的 controller 代理查詢與展示

## Grafana 整合不是只有超連結

`src/pybind/mgr/dashboard/controllers/grafana.py` 與 `src/pybind/mgr/dashboard/grafana.py` 顯示，Dashboard 對 Grafana 的整合至少包含：

- 取得 Grafana URL
- 驗證 dashboard 是否可用
- 將本地 dashboard JSON 推送到 Grafana

特別是 `load_local_dashboards()` / `push_local_dashboards()` 這兩個實作，說明 Dashboard 會從本地檔案路徑載入 Ceph 預設儀表板，再透過 Grafana REST API 推送。

這代表 Dashboard 與 Grafana 的關係不是單純跳轉，而是有一層「Ceph 官方預設 dashboard distribution」的管理邏輯。

## Alertmanager：不只看警報，也能管理 silence

從 `prometheus.service.ts` 可以看到前端直接支援：

- `getAlerts()`
- `getGroupedAlerts()`
- `getSilences()`
- `setSilence()`
- `expireSilence()`
- `getNotifications()`

也就是說，Dashboard 已經把「看告警」與「抑制告警」都納入管理介面，而不是只負責 read-only 呈現。

## 實務上怎麼解讀 Dashboard？

### 1. 它是 `ceph-mgr` 的延伸，不是獨立 control plane

Dashboard 能看到什麼、能做什麼，很大程度取決於 `ceph-mgr` module 狀態與 Prometheus / Grafana 設定是否完整。

### 2. 看到圖表異常時，先分辨是哪一層出問題

- Dashboard API 壞掉？
- Prometheus 沒資料？
- PromQL 查詢本身回傳空值？
- `prometheus` mgr module 沒正常匯出？
- Grafana / Alertmanager endpoint 未設定？

先分層，比直接重整畫面有效得多。

### 3. Overview 其實很適合當維運首頁

因為它把 health、容量、趨勢、告警、升級資訊集中在一起，非常適合做 day-2 operations 的第一個觀察點。

::: tip 建議搭配方式
日常巡檢可先看 Dashboard overview，再用 CLI 補充 `ceph status`、`ceph health detail`、`ceph osd df`、`ceph orch ps` 等細節。
:::

## 適合從這頁延伸的主題

- 如果你想理解控制面如何部署服務：看 [cephadm 深入分析](/ceph/cephadm)
- 如果你想把 UI 觀察轉成 CLI 操作：看 [日常維運](/ceph/operations)
- 如果你想用故事方式串起整個系統：看 [故事驅動式學習路徑](/ceph/learning-path/story)

::: info 相關章節
- [Ceph — cephadm 深入分析](/ceph/cephadm)
- [Ceph — 日常維運](/ceph/operations)
- [Ceph — 整體架構概述](/ceph/architecture)
- [Ceph — 故事驅動式學習路徑](/ceph/learning-path/story)
:::
