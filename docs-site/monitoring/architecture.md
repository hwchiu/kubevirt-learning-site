---
layout: doc
---

# Monitoring — 系統架構

本文件深入分析 [kubevirt/monitoring](https://github.com/kubevirt/monitoring) 專案的原始碼架構，涵蓋核心工具、建置系統與 Go Module 設計。

::: info 相關章節
- 各工具的核心功能請參閱 [核心功能分析](./core-features)
- CI/CD 與自動化工具請參閱 [控制器與 API](./controllers-api)
- 與 KubeVirt 生態系的整合請參閱 [外部整合](./integration)
:::

## 專案概述

`kubevirt/monitoring` 是 KubeVirt 生態系的監控基礎設施儲存庫，主要負責：

- 收集與管理 **Grafana 儀表板** (dashboards)
- 維護 **Prometheus Runbook** 告警處理手冊
- 提供 **指標命名規範檢查** 工具 (linter)
- 自動化 **指標文件產生** 與 **Runbook 同步**

::: info 基本資訊
- **Go 版本**：`go 1.23.6`（根模組，定義於 `go.mod`）
- **授權條款**：Apache License 2.0
- **模組路徑**：`github.com/kubevirt/monitoring`
- **根模組依賴**：`golang.org/x/tools v0.30.0`（用於 `go/analysis` 靜態分析框架）
:::

## 系統架構圖

以下展示 monitoring 專案中四個核心工具與外部系統之間的關係：

```mermaid
graph TB
    subgraph "kubevirt/monitoring 儲存庫"
        ML["monitoringlinter<br/>靜態分析 Linter"]
        MD["metricsdocs<br/>指標文件產生器"]
        RS["runbook-sync-downstream<br/>Runbook 同步工具"]
        PL["prom-metrics-linter<br/>指標命名 Linter"]
        MP["pkg/metrics/parser<br/>指標解析器"]
        DB["dashboards/<br/>Grafana 儀表板"]
        RB["docs/runbooks/<br/>Runbook 文件"]
    end

    subgraph "KubeVirt 子專案"
        KV["kubevirt/kubevirt"]
        CDI["kubevirt/containerized-data-importer"]
        SSP["kubevirt/ssp-operator"]
        HCO["kubevirt/hyperconverged-cluster-operator"]
        CNAO["kubevirt/cluster-network-addons-operator"]
        OTHER["其他子專案..."]
    end

    subgraph "外部系統"
        PROM["Prometheus"]
        GRAF["Grafana"]
        GH["GitHub Actions"]
        QUAY["quay.io Registry"]
        DS["openshift/runbooks<br/>下游儲存庫"]
    end

    ML -->|"檢查 operator 專案<br/>監控程式碼規範"| KV
    ML -->|"檢查 operator 專案<br/>監控程式碼規範"| CDI

    MD -->|"clone 並解析<br/>各專案的 metrics.md"| KV
    MD -->|"clone 並解析<br/>各專案的 metrics.md"| CDI
    MD -->|"clone 並解析<br/>各專案的 metrics.md"| SSP
    MD -->|"clone 並解析<br/>各專案的 metrics.md"| HCO
    MD -->|"clone 並解析<br/>各專案的 metrics.md"| OTHER

    PL -->|"在 CI 中驗證<br/>指標命名規範"| KV
    PL -->|"在 CI 中驗證<br/>指標命名規範"| CDI
    MP -->|"提供解析輔助"| PL

    RS -->|"同步 runbook"| RB
    RS -->|"建立 PR 同步"| DS

    DB -->|"匯入"| GRAF
    PL -.->|"Docker image 發布"| QUAY
    GH -->|"CI/CD 自動化"| MD
    GH -->|"CI/CD 自動化"| RS
    GH -->|"CI/CD 自動化"| PL
    PROM -->|"告警觸發參照"| RB
```

## 核心工具

專案包含四個主要工具，各自負責不同的監控相關任務：

| 工具名稱 | 路徑 | 功能說明 | Go 版本 |
|---------|------|---------|--------|
| **monitoringlinter** | `monitoringlinter/cmd/monitoringlinter/` | 基於 `go/analysis` 的靜態分析器，確保 Kubernetes operator 專案的監控程式碼（指標註冊、告警、recording rules）集中於 `pkg/monitoring` 目錄，並使用 `operator-observability` 套件而非直接呼叫 Prometheus 註冊方法 | `go 1.23.6` |
| **metricsdocs** | `tools/metricsdocs/` | 指標文件產生器，自動 clone 九個 KubeVirt 子專案的 Git 儲存庫，解析各專案的 `metrics.md`，並彙整產生統一的指標文件 | `go 1.16` |
| **runbook-sync-downstream** | `tools/runbook-sync-downstream/` | 自動化 Runbook 同步工具，比對上游 (`kubevirt/monitoring`) 與下游 (`openshift/runbooks`) 的 runbook 差異，透過 GitHub API 建立 PR 進行同步，支援新增更新與廢棄標記 | `go 1.22.1` |
| **prom-metrics-linter** | `test/metrics/prom-metrics-linter/` | 以容器化方式運行的 Prometheus 指標命名規範檢查器，基於 `promlint` 並加入 KubeVirt 自定義規則，驗證 operator 名稱前綴、counter 後綴，以及 recording rule 命名結構 | `go 1.20` |

### monitoringlinter

靜態分析 linter，使用 `golang.org/x/tools/go/analysis` 框架實作。透過 `singlechecker.Main()` 以獨立指令方式運行。

```go
// monitoringlinter/cmd/monitoringlinter/main.go
func main() {
	singlechecker.Main(monitoringlinter.NewAnalyzer())
}
```

**核心規則：**

1. 禁止在專案中任何位置直接呼叫 `prometheus.Register()` / `prometheus.MustRegister()`
2. `operatormetrics.RegisterMetrics()` 僅允許在 `pkg/monitoring` 目錄下使用
3. `operatorrules.RegisterAlerts()` 與 `operatorrules.RegisterRecordingRules()` 僅允許在 `pkg/monitoring` 目錄下使用

::: tip 安裝方式
```bash
go install github.com/kubevirt/monitoring/monitoringlinter/cmd/monitoringlinter@latest
monitoringlinter ./...
```
:::

### metricsdocs

指標文件產生器會從設定檔讀取九個 KubeVirt 子專案的版本資訊，逐一 clone 並解析各專案的指標文件：

```go
// tools/metricsdocs/types.go
var projectsInfo = []*projectInfo{
	{"KUBEVIRT", "kubevirt", defaultOrg, "docs/observability/metrics.md"},
	{"CDI", "containerized-data-importer", defaultOrg, "doc/metrics.md"},
	{"NETWORK_ADDONS", "cluster-network-addons-operator", defaultOrg, "docs/metrics.md"},
	{"SSP", "ssp-operator", defaultOrg, "docs/metrics.md"},
	{"NMO", "node-maintenance-operator", defaultOrg, "docs/metrics.md"},
	{"HPPO", "hostpath-provisioner-operator", defaultOrg, "docs/metrics.md"},
	{"HPP", "hostpath-provisioner", defaultOrg, "docs/metrics.md"},
	{"HCO", "hyperconverged-cluster-operator", defaultOrg, "docs/metrics.md"},
	{"KMP", "kubemacpool", "k8snetworkplumbingwg", "doc/metrics.md"},
}
```

::: info 設定檔格式
設定檔 (`tools/metricsdocs/config`) 採用 dotenv 格式，定義各子專案的版本號：
```
KUBEVIRT_VERSION="main"
CDI_VERSION="main"
SSP_VERSION="main"
...
```
:::

### runbook-sync-downstream

自動化同步工具，將 `kubevirt/monitoring` 中的 runbook 同步至 `openshift/runbooks` 下游儲存庫。主要功能：

- 比對上下游 runbook 的最後更新時間
- 自動建立包含更新內容的 PR（使用 `hco-bot` 帳號）
- 標記已在上游廢棄的 runbook
- 關閉同一 runbook 的過時 PR

```go
// tools/runbook-sync-downstream/main.go
const (
	upstreamRunbooksDir   = "docs/runbooks"
	downstreamRepositoryOwner = "openshift"
	downstreamRepositoryName  = "runbooks"
	downstreamRunbooksDir     = "alerts/openshift-virtualization-operator"
)
```

::: warning 需要環境變數
執行此工具需設定 `GITHUB_TOKEN` 環境變數，並透過 `DRY_RUN` 控制是否實際推送（預設為 `true`）。
:::

### prom-metrics-linter

基於 `promlint` 的容器化指標 linter，加入 KubeVirt 專屬的自定義驗證規則：

**指標驗證規則：**
- 指標名稱必須以 `{operatorName}_` 前綴開頭
- 若有子 operator，名稱需以 `{operatorName}_{subOperatorName}_` 開頭
- Counter 類型指標需有 `_total` 或 `_timestamp_seconds` 後綴

**Recording Rule 驗證規則：**
- 名稱必須遵循 `level:metric:operations` 三段式結構
- metric 段需符合 operator 前綴規範
- operations 段需反映 expr 中使用的聚合/時間運算
- 不可出現重複的 operations token

```bash
# 容器化執行方式
podman run -i "quay.io/kubevirt/prom-metrics-linter:<tag>" \
  --metric-families='<metrics_json>' \
  --operator-name=kubevirt \
  --sub-operator-name=<sub-operator>
```

## 目錄結構

```
kubevirt/monitoring/
├── dashboards/                         # Grafana 儀表板定義
│   ├── grafana/
│   │   └── kubevirt-control-plane.json   # Grafana 原生格式
│   └── openshift/
│       └── kubevirt-top-consumers.json   # OpenShift Console 格式
├── docs/
│   ├── runbooks/                       # 70+ Prometheus 告警 Runbook
│   │   ├── CDIDataImportCronOutdated.md
│   │   ├── KubeVirtCRModified.md
│   │   ├── VirtAPIDown.md
│   │   └── ...
│   ├── deprecated_runbooks/            # 已廢棄的 runbook
│   ├── metrics.md                      # 自動產生的指標彙整文件
│   └── ghpages.json                    # GitHub Pages 設定
├── monitoringlinter/                   # 靜態分析 Linter
│   ├── analyzer.go                       # 核心分析邏輯
│   ├── analyzer_test.go                  # 單元測試
│   ├── cmd/monitoringlinter/main.go      # CLI 進入點
│   ├── testdata/                         # 測試用的 Go 原始碼
│   └── tests/                            # E2E 測試腳本
├── pkg/
│   └── metrics/
│       └── parser/                     # 共用指標解析器
│           └── metrics_parser.go         # Metric → MetricFamily 轉換
├── tools/
│   ├── metricsdocs/                    # 指標文件產生器
│   │   ├── metricsdocs.go                # 主程式邏輯
│   │   ├── types.go                      # 專案資訊與資料結構
│   │   ├── git.go                        # Git 操作
│   │   ├── metrics.tmpl                  # Markdown 模板
│   │   └── config                        # 版本設定檔
│   ├── runbook-sync-downstream/        # Runbook 同步工具
│   │   ├── main.go                       # 主程式：同步與 PR 管理
│   │   ├── runbook.go                    # Runbook 差異比對
│   │   ├── worktree.go                   # Git worktree 操作
│   │   ├── setup.go                      # 儲存庫設定
│   │   ├── commitdate.go                 # commit 日期解析
│   │   ├── cmd/preview/main.go           # Runbook 預覽工具
│   │   └── templates/                    # 廢棄通知模板
│   └── ghpages/                        # GitHub Pages 建置腳本
│       └── main.py                       # Python 建置工具
├── test/
│   └── metrics/
│       └── prom-metrics-linter/        # 指標命名 Linter
│           ├── metric_name_linter.go     # 進入點與 JSON 解析
│           ├── custom_linter_rules.go    # 自定義驗證規則
│           ├── allowlist.json            # 允許清單
│           └── Dockerfile                # 多架構容器映像
├── .github/workflows/                  # 6 個 CI/CD 工作流程
├── go.mod                              # 根模組定義
├── Makefile                            # 建置指令
└── monitoring-guidelines.md            # 監控準則
```

## 建置系統

### Makefile 目標

專案使用 `Makefile` 管理所有建置任務，預設容器運行環境為 `podman`：

| Make 目標 | 功能說明 | 指令 |
|-----------|---------|------|
| `build-metricsdocs` | 編譯 metricsdocs 工具 | `cd ./tools/metricsdocs && go build -ldflags="-s -w" -o _out/metricsdocs .` |
| `metricsdocs` | 執行 metricsdocs（需設定 `CONFIG_FILE`） | `tools/metricsdocs/_out/metricsdocs --config-file $(CONFIG_FILE)` |
| `monitoringlinter-build` | 編譯 monitoringlinter | `go build -o bin/ ./monitoringlinter/cmd/monitoringlinter` |
| `monitoringlinter-unit-test` | 執行 monitoringlinter 單元測試 | `go test ./monitoringlinter/...` |
| `monitoringlinter-test` | 執行 monitoringlinter E2E 測試 | 先 build 再執行 `./monitoringlinter/tests/e2e.sh` |
| `promlinter-build` | 建置 prom-metrics-linter 容器映像 | `${CONTAINER_RUNTIME} build -t ${IMG} test/metrics/prom-metrics-linter` |
| `promlinter-push` | 推送 prom-metrics-linter 映像 | `${CONTAINER_RUNTIME} push ${IMG}` |
| `build-runbook-sync-downstream` | 編譯 runbook-sync-downstream 工具 | `cd tools/runbook-sync-downstream && go build -ldflags="-s -w" -o _out/runbook-sync-downstream .` |
| `runbook-sync-downstream` | 執行 runbook 同步 | 先 build 再執行同步 |
| `build-runbook-preview` | 編譯 runbook 預覽工具 | `cd tools/runbook-sync-downstream && go build -ldflags="-s -w" -o _out/runbook-preview ./cmd/preview/` |
| `lint-markdown` | 對 runbook 做 Markdown 格式檢查 | 使用 `markdownlint-cli2` 容器映像 |

### CI/CD 工作流程（GitHub Actions）

專案共有 **6 個 GitHub Actions 工作流程**：

| 工作流程檔案 | 名稱 | 觸發條件 | 功能說明 |
|-------------|------|---------|---------|
| `sanity.yaml` | Sanity Checks | push/PR to `main` | 使用 `markdownlint-cli2` 檢查 `docs/*runbooks/*.md` 的 Markdown 格式 |
| `publish.yaml` | Generate a build and push to 'ghpages' branch | push to `main` | 使用 Python 建置腳本將文件發布至 `ghpages` 分支 |
| `prom-metrics-linter.yaml` | prom-metrics-linter | Release 發布 | 建置多架構（amd64/arm64/s390x）Docker 映像並推送至 `quay.io/kubevirt/prom-metrics-linter` |
| `runbook-preview.yaml` | Runbook Downstream Preview | PR 修改 `docs/runbooks/**` | 在 PR 中預覽 runbook 轉換為下游格式的結果 |
| `runbook_sync_downstream.yaml` | Run runbook-sync-downstream | 每日排程 `04:30 UTC` | 自動將 runbook 同步至 `openshift/runbooks` 下游儲存庫 |
| `update_metrics_docs.yaml` | Auto-Update Metrics Documentation | 每日排程 `05:00 UTC` | 自動更新指標文件並建立 PR |

```mermaid
graph LR
    subgraph "Pull Request 觸發"
        A["sanity.yaml<br/>Markdown Lint"] 
        B["runbook-preview.yaml<br/>Runbook 預覽"]
    end

    subgraph "Push to main"
        C["publish.yaml<br/>GitHub Pages 發布"]
    end

    subgraph "每日排程"
        D["update_metrics_docs.yaml<br/>指標文件更新<br/>⏰ 05:00 UTC"]
        E["runbook_sync_downstream.yaml<br/>Runbook 同步<br/>⏰ 04:30 UTC"]
    end

    subgraph "Release 發布"
        F["prom-metrics-linter.yaml<br/>Docker 映像推送<br/>→ quay.io"]
    end
```

## Go Module 架構

專案採用 **多 Go Module** 設計，共有 **5 個獨立的 `go.mod`**，各工具擁有獨立的依賴管理：

```mermaid
graph TB
    ROOT["根模組<br/>github.com/kubevirt/monitoring<br/>go 1.23.6"]
    MD["tools/metricsdocs<br/>go 1.16"]
    RS["tools/runbook-sync-downstream<br/>go 1.22.1"]
    PL["test/metrics/prom-metrics-linter<br/>go 1.20"]
    MP["pkg/metrics/parser<br/>go 1.20"]

    ROOT -->|"包含"| ML["monitoringlinter/"]
    
    style ROOT fill:#e1f5fe
    style MD fill:#f3e5f5
    style RS fill:#f3e5f5
    style PL fill:#f3e5f5
    style MP fill:#fff3e0
```

| 模組路徑 | Go 版本 | 主要依賴 | 用途 |
|---------|---------|---------|------|
| `github.com/kubevirt/monitoring` | 1.23.6 | `golang.org/x/tools v0.30.0` | 根模組，包含 monitoringlinter |
| `github.com/kubevirt/monitoring/tools/metricsdocs` | 1.16 | `github.com/joho/godotenv v1.4.0` | 指標文件產生器 |
| `github.com/kubevirt/monitoring/tools/runbook-sync-downstream` | 1.22.1 | `go-git/go-git/v5`、`google/go-github/v60`、`k8s.io/klog/v2` | Runbook 同步與 GitHub PR 管理 |
| `github.com/kubevirt/monitoring/test/metrics/prom-metrics-linter` | 1.20 | `prometheus/client_golang v1.15.1`、`prometheus/client_model v0.4.0` | Prometheus 指標命名 linter |
| `github.com/kubevirt/monitoring/pkg/metrics/parser` | 1.20 | `prometheus/client_model v0.4.0` | 共用指標解析器（Metric → MetricFamily 轉換） |

::: tip 多模組設計的好處
每個工具有各自的 `go.mod`，意味著：
1. **獨立的依賴管理** — 各工具可以使用不同版本的 Go 和第三方套件
2. **最小化依賴** — 使用某工具時不需要下載其他工具的依賴
3. **獨立的 vendor 目錄** — `metricsdocs/vendor/`、`prom-metrics-linter/vendor/` 各自管理
4. **版本靈活性** — Go 版本從 1.16 到 1.23.6 跨度很大，各工具按需升級
:::

::: warning 注意事項
根模組的 `go 1.23.6` 僅適用於 `monitoringlinter`。其他工具如 `metricsdocs`（`go 1.16`）使用較舊的 Go 版本，這代表它們可能不支援較新的 Go 語言特性。
:::
