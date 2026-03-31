# 開發環境設置

本指南將帶領你從零開始建立 KubeVirt 的完整開發環境，包含工具安裝、程式碼克隆、本地叢集建立、建置流程，以及測試執行。

:::info 適用對象
本文適合想要貢獻 KubeVirt 程式碼的開發者，或需要在本地環境驗證功能的工程師。建議先熟悉 Kubernetes 基礎概念以及 Go 語言開發。
:::

---

## 前置需求

### 硬體需求

KubeVirt 的開發環境需要較充裕的硬體資源，因為本地叢集會啟動多個虛擬機節點。

| 資源 | 最低需求 | 建議配置 |
|------|----------|----------|
| CPU  | 4 核心（需支援虛擬化） | 8 核心以上 |
| RAM  | 16 GB | 32 GB |
| 磁碟空間 | 50 GB 可用空間 | 100 GB 以上（SSD 為佳） |
| 網路 | 基本網路連線 | 穩定寬頻（需拉取 container images） |

:::warning 虛擬化支援
你的 CPU 必須支援硬體虛擬化（Intel VT-x 或 AMD-V），且必須在 BIOS/UEFI 中啟用。可用以下指令驗證：

```bash
# Linux
egrep -c '(vmx|svm)' /proc/cpuinfo
# 輸出大於 0 表示支援

# 也可直接檢查 KVM 裝置
ls -la /dev/kvm
```
:::

---

### 必要軟體

#### Go 1.24+

KubeVirt 使用 Go 語言開發，需要 1.24 或以上版本。

```bash
# Linux / macOS — 使用官方安裝包
wget https://go.dev/dl/go1.24.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.24.0.linux-amd64.tar.gz

# 加入環境變數（~/.bashrc 或 ~/.zshrc）
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

# 驗證
go version
# go version go1.24.0 linux/amd64
```

```bash
# macOS — 使用 Homebrew
brew install go

# 驗證
go version
```

#### Docker 或 Podman

:::tip 建議版本
- **Docker**: 24.x 或以上（含 Docker Engine 或 Docker Desktop）
- **Podman**: 4.x 或以上（Linux 原生，效能較佳）

大多數貢獻者在 Linux 上使用 Docker Engine（不含 Desktop），macOS 上使用 Docker Desktop 或 Lima。
:::

```bash
# Linux — 安裝 Docker Engine（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 將目前使用者加入 docker 群組（免 sudo）
sudo usermod -aG docker $USER
newgrp docker

# 驗證
docker version
```

```bash
# Linux — 安裝 Podman（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y podman

# 驗證
podman version
```

#### kubectl

kubectl 版本需與目標叢集版本相符（允許 ±1 個 minor 版本差距）。

```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s \
  https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS
brew install kubectl

# 驗證
kubectl version --client
```

#### git

```bash
# Linux（Ubuntu/Debian）
sudo apt-get install -y git

# macOS
brew install git

# 設定基本 git 資訊（必要）
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

#### bazel（可選）

bazel 用於部分遺留的建置工作流程，目前主要建置已遷移至 `make`，但某些工具仍依賴 bazel。建議使用 `bazelisk` 管理版本。

```bash
# 使用 bazelisk（自動管理 bazel 版本，強烈建議）
go install github.com/bazelbuild/bazelisk@latest
sudo ln -s $GOPATH/bin/bazelisk /usr/local/bin/bazel

# 驗證
bazel version
```

---

### 各作業系統特別說明

#### Linux（推薦開發平台）

Linux 是 KubeVirt 開發的首選平台，/dev/kvm 可直接使用，無需額外配置。

```bash
# 確認 KVM 模組已載入
lsmod | grep kvm
# 應看到 kvm_intel 或 kvm_amd

# 若未載入
sudo modprobe kvm-intel   # Intel CPU
sudo modprobe kvm-amd     # AMD CPU
```

#### macOS

macOS 本身不支援 KVM，KubeVirt 的測試叢集（kubevirtci）需透過 Linux VM 運行。詳見 [macOS 特殊設定](#macos-特殊設定) 章節。

#### Windows（WSL2）

在 Windows 上強烈建議使用 WSL2（Windows Subsystem for Linux 2）並搭配 Ubuntu 發行版。

```powershell
# 在 PowerShell（管理員）中啟用 WSL2
wsl --install
wsl --set-default-version 2

# 安裝 Ubuntu
wsl --install -d Ubuntu-22.04
```

:::warning WSL2 限制
WSL2 環境中 /dev/kvm 的可用性取決於 Windows 版本和硬體。部分功能可能受限。建議在 WSL2 中使用 Podman 而非 Docker Desktop（避免 WSL2 與 Docker Desktop 整合的複雜度）。
:::

---

## 克隆程式碼庫

### 直接克隆（唯讀或內部貢獻者）

```bash
git clone https://github.com/kubevirt/kubevirt.git
cd kubevirt
```

### Fork 工作流程（推薦外部貢獻者）

KubeVirt 採用標準的 GitHub Fork + Pull Request 工作流程。

**Step 1：在 GitHub 上 Fork 專案**

前往 [https://github.com/kubevirt/kubevirt](https://github.com/kubevirt/kubevirt)，點擊右上角的 **Fork** 按鈕。

**Step 2：克隆你的 Fork**

```bash
# 將 YOUR_GITHUB_USERNAME 替換為你的帳號
git clone https://github.com/YOUR_GITHUB_USERNAME/kubevirt.git
cd kubevirt
```

**Step 3：設定 upstream remote**

```bash
# 新增官方 upstream remote
git remote add upstream https://github.com/kubevirt/kubevirt.git

# 驗證 remote 設定
git remote -v
# origin    https://github.com/YOUR_GITHUB_USERNAME/kubevirt.git (fetch)
# origin    https://github.com/YOUR_GITHUB_USERNAME/kubevirt.git (push)
# upstream  https://github.com/kubevirt/kubevirt.git (fetch)
# upstream  https://github.com/kubevirt/kubevirt.git (push)
```

**Step 4：保持 Fork 與 upstream 同步**

```bash
# 在開始新功能開發前，先同步 upstream
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

:::tip 開發分支命名建議
建議為每個 feature 或 bugfix 建立獨立分支：

```bash
# 功能開發
git checkout -b feature/add-hotplug-network-interface

# Bug 修復
git checkout -b fix/vmi-migration-panic

# 參考 GitHub issue 編號
git checkout -b issue-12345-fix-memory-leak
```
:::

---

## 建立開發叢集（kubevirtci）

### 什麼是 kubevirtci？

`kubevirtci` 是 KubeVirt 專案自帶的本地開發叢集工具，位於 `cluster-up/` 目錄。它能在本地自動建立一個完整的 Kubernetes 叢集（使用 QEMU/KVM 虛擬機），讓開發者在不需要真實雲端環境的情況下，完整測試 KubeVirt 功能。

:::info kubevirtci 的運作方式
kubevirtci 會透過 Docker/Podman 拉取預先建置好的叢集映像檔，並在容器內啟動 QEMU 虛擬機作為 Kubernetes 節點。這意味著你的主機需要支援巢狀虛擬化（nested virtualization）或直接的 KVM 存取。
:::

### 環境變數設定

在啟動叢集前，需設定以下環境變數（建議加入 `~/.bashrc` 或 `~/.zshrc`）：

```bash
# 選擇 Kubernetes provider 版本（支援的版本請見 cluster-up/cluster/）
export KUBEVIRT_PROVIDER=k8s-1.29

# 叢集節點數量（1 個 control-plane + N-1 個 worker）
export KUBEVIRT_NUM_NODES=2

# 每個節點的記憶體大小（依你的機器記憶體調整）
export KUBEVIRT_MEMORY_SIZE=12288M

# （可選）使用 Podman 而非 Docker
export KUBEVIRT_CONTAINER_RUNTIME=podman

# （可選）設定容器映像檔 registry 前綴（用於離線或鏡像環境）
# export KUBEVIRT_PROVIDER_EXTRA_ARGS="--registry-mirror https://mirror.example.com"
```

支援的 provider 版本（可在 `cluster-up/cluster/` 目錄中查看完整清單）：

| Provider | 說明 |
|----------|------|
| `k8s-1.28` | Kubernetes 1.28 |
| `k8s-1.29` | Kubernetes 1.29（推薦） |
| `k8s-1.30` | Kubernetes 1.30 |
| `okd-4.14` | OpenShift Origin 4.14 |
| `k8s-1.29-sig-network` | 含特殊網路插件的 K8s 1.29 |

### 啟動叢集

```bash
# 啟動叢集（首次執行會拉取映像檔，需要一些時間）
make cluster-up
```

:::warning 啟動時間
首次啟動需要下載容器映像檔（數 GB），請確保網路穩定，並預留 5~15 分鐘。後續啟動（映像已快取）約 2~5 分鐘。
:::

### 設定 kubeconfig 存取叢集

```bash
# 使用 kubevirtci 內建的 kubectl 包裝器（最簡單）
cluster-up/kubectl.sh get nodes

# 或者，匯出 KUBECONFIG 環境變數（讓標準 kubectl 也能使用）
export KUBECONFIG=$(cluster-up/kubeconfig.sh)

# 驗證叢集狀態
kubectl get nodes
# NAME       STATUS   ROLES           AGE   VERSION
# node01     Ready    control-plane   3m    v1.29.0
# node02     Ready    <none>          2m    v1.29.0
```

:::tip kubectl.sh vs 標準 kubectl
`cluster-up/kubectl.sh` 是 kubevirtci 提供的包裝器，會自動使用正確的 kubeconfig。匯出 `KUBECONFIG` 後，可以直接使用系統安裝的 `kubectl`，更加便利。
:::

### 停止叢集

```bash
# 停止並清理叢集（會刪除所有資料）
make cluster-down
```

### 進階叢集設定

```bash
# SSH 進入叢集節點（偵錯用）
cluster-up/ssh.sh node01

# 查看叢集 logs
cluster-up/kubectl.sh logs -n kubevirt <pod-name>

# 重新啟動叢集（不清除資料）
# 先 down 再 up
make cluster-down && make cluster-up
```

---

## 建置指令

### 建置所有 Binary

```bash
# 建置所有 KubeVirt binary（virt-api, virt-controller, virt-handler, 等）
make
# 或等同指令
make build
```

建置產物會放在 `_out/cmd/` 目錄下。

### 建置特定 Binary

```bash
# 只建置 virt-api
make build WHAT=cmd/virt-api

# 只建置 virtctl
make build WHAT=cmd/virtctl

# 只建置 virt-operator
make build WHAT=cmd/virt-operator
```

### 建置並推送 Docker Images

在部署到叢集前，需要先將修改過的 binary 打包成 container images 並推送到 registry。

```bash
# 設定你的私有 registry（必填）
export DOCKER_PREFIX=myregistry.io/myuser
# 例如：
# export DOCKER_PREFIX=quay.io/johndoe
# export DOCKER_PREFIX=docker.io/johndoe

# 設定 image tag（預設為 latest）
export DOCKER_TAG=devel

# 建置並推送所有 images
make push

# 只推送特定 image（較快）
make push-<component>
# 例如：make push-virt-handler
```

:::info 使用本地 registry
若要避免推送到遠端 registry，可使用 kubevirtci 內建的本地 registry：

```bash
# kubevirtci 通常在 localhost:5000 暴露一個本地 registry
export DOCKER_PREFIX=localhost:5000/kubevirt
export DOCKER_TAG=devel
make push
```
:::

### 生成 Kubernetes Manifests

```bash
# 根據目前的 DOCKER_PREFIX 和 DOCKER_TAG 生成安裝 manifests
make manifests

# 產出在 _out/manifests/ 目錄下
ls _out/manifests/
```

### 執行程式碼生成

當你修改了 API 型別定義後，需要重新執行程式碼生成：

```bash
# 執行所有程式碼生成（deepcopy, client, openapi 等）
make generate

# 只執行 Go 生成（deepcopy-gen 等）
make generate-go

# 只執行 manifests 生成
make generate-manifests
```

:::warning 生成後必須提交
執行 `make generate` 後，所有生成的檔案變更都必須包含在你的 PR 中。CI 會驗證生成的程式碼是否與 API 定義一致。
:::

---

## 部署到本地叢集

### 一鍵同步（推薦）

```bash
# cluster-sync 會自動完成：build → push → deploy 的完整流程
make cluster-sync
```

### 分步驟部署

```bash
# Step 1：建置並推送 images
export DOCKER_PREFIX=localhost:5000/kubevirt
export DOCKER_TAG=devel
make push

# Step 2：部署到叢集
make deploy

# 或使用 manifests 手動部署
kubectl apply -f _out/manifests/release/kubevirt-operator.yaml
kubectl apply -f _out/manifests/release/kubevirt-cr.yaml
```

### 驗證部署狀態

```bash
# 等待 KubeVirt operator 就緒
cluster-up/kubectl.sh -n kubevirt wait kv kubevirt \
  --for condition=Available --timeout 300s

# 查看所有 KubeVirt pods 狀態
cluster-up/kubectl.sh get pods -n kubevirt
# NAME                               READY   STATUS    RESTARTS   AGE
# virt-api-7d8b9c4f6-xk9p2           1/1     Running   0          2m
# virt-controller-6c8b7d9f5-rl4m7    1/1     Running   0          2m
# virt-handler-n9x2k                 1/1     Running   0          2m
# virt-handler-p7q3s                 1/1     Running   0          2m
# virt-operator-5f6g7h8-abc12        1/1     Running   0          3m

# 查看 KubeVirt CR 狀態
cluster-up/kubectl.sh get kubevirt -n kubevirt -o yaml
```

### 快速迭代開發

在修改某個 component 後，可以只重新部署該 component：

```bash
# 只重新建置並推送 virt-handler
make build WHAT=cmd/virt-handler
make push-virt-handler

# 重啟 virt-handler DaemonSet 讓節點重新拉取
cluster-up/kubectl.sh rollout restart daemonset/virt-handler -n kubevirt
cluster-up/kubectl.sh rollout status daemonset/virt-handler -n kubevirt
```

---

## 執行測試

### 單元測試

```bash
# 執行所有單元測試
make test

# 輸出詳細測試結果
make test WHAT="./pkg/..."

# 針對特定套件執行
go test ./pkg/virt-controller/...
go test ./pkg/virt-handler/...
go test ./pkg/network/...

# 針對特定測試（使用 Ginkgo focus）
go test ./pkg/virt-controller/... -v \
  --ginkgo.focus="VirtualMachine controller"

# 執行並顯示覆蓋率報告
go test ./pkg/... -coverprofile=coverage.out
go tool cover -html=coverage.out
```

:::tip Ginkgo 測試框架
KubeVirt 使用 [Ginkgo](https://onsi.github.io/ginkgo/) 作為 BDD 測試框架，搭配 [Gomega](https://onsi.github.io/gomega/) 作為 matcher 函式庫。

常用的 Ginkgo 指令：
```bash
# 安裝 Ginkgo CLI
go install github.com/onsi/ginkgo/v2/ginkgo@latest

# 使用 ginkgo CLI 執行（提供更豐富的輸出）
ginkgo -v ./pkg/virt-controller/...

# 只執行特定 spec
ginkgo --focus="should create VMI" ./pkg/virt-controller/...
```
:::

### e2e 功能測試

e2e 測試需要一個正在運行的 KubeVirt 叢集（`make cluster-up` + `make cluster-sync`）。

```bash
# 執行所有 e2e 功能測試（耗時較長）
make functest

# 使用 focus 只執行特定測試
FUNC_TEST_ARGS="--ginkgo.focus=VMI" make functest

# 聚焦在網路相關測試
FUNC_TEST_ARGS="--ginkgo.focus=\[Serial\].*network" make functest

# 跳過特定測試
FUNC_TEST_ARGS="--ginkgo.skip=\[QUARANTINE\]" make functest

# 設定測試 timeout（秒）
FUNC_TEST_ARGS="--timeout=3600" make functest

# 指定 kubeconfig
KUBECONFIG=$(cluster-up/kubeconfig.sh) \
  FUNC_TEST_ARGS="--ginkgo.focus=LiveMigration" \
  make functest
```

:::warning e2e 測試時間
完整的 e2e 測試套件可能需要數小時。建議在開發時使用 `--ginkgo.focus` 縮小測試範圍，只在提交 PR 前執行完整測試套件（CI 會自動執行）。
:::

### 整合測試

部分測試介於單元測試和 e2e 測試之間，需要較少的叢集資源：

```bash
# 執行整合測試（需要 KUBECONFIG）
make integration-test

# 特定整合測試
INTEGRATION_TEST_ARGS="--ginkgo.focus=storage" make integration-test
```

### 測試標籤說明

KubeVirt 的 e2e 測試使用 Ginkgo 標籤（Labels）分類：

| 標籤 | 說明 |
|------|------|
| `[Serial]` | 必須序列執行（不能並行）的測試 |
| `[QUARANTINE]` | 不穩定的測試，暫時隔離 |
| `[sig-network]` | 網路相關測試 |
| `[sig-storage]` | 儲存相關測試 |
| `[sig-compute]` | 計算（VM）相關測試 |
| `[Slow]` | 執行時間較長的測試 |

---

## macOS 特殊設定

### Docker Desktop 問題

macOS 上的 Docker Desktop 有一些常見問題需要注意。

**Docker Hub Rate Limit 問題**

```bash
# 登入 Docker Hub 以提高 pull rate limit
docker login

# 或設定 Docker Desktop keychain（推薦）
# 在 Docker Desktop > Settings > Docker Engine 中加入：
# "credsStore": "osxkeychain"
```

### 安裝 GNU 工具

部分建置腳本依賴 GNU 版本的工具（Linux 預設），macOS 預設使用 BSD 版本，需要額外安裝：

```bash
# 安裝 GNU coreutils 和 sed
brew install coreutils gnu-sed findutils gawk

# 加入 PATH（讓 GNU 版本優先）
# 加入 ~/.zshrc 或 ~/.bashrc
export PATH="$(brew --prefix)/opt/coreutils/libexec/gnubin:$PATH"
export PATH="$(brew --prefix)/opt/gnu-sed/libexec/gnubin:$PATH"
export PATH="$(brew --prefix)/opt/findutils/libexec/gnubin:$PATH"
export PATH="$(brew --prefix)/opt/gawk/libexec/gnubin:$PATH"
```

### Lima 作為 Docker Desktop 替代方案

[Lima](https://github.com/lima-vm/lima) 是 macOS 上的 Linux 虛擬機管理工具，可作為輕量級 Docker Desktop 替代方案，並且更接近 Linux 開發環境。

```bash
# 安裝 Lima
brew install lima

# 建立 Lima VM（使用 Docker template）
limactl start template://docker

# 設定 Docker context
docker context use lima-docker

# 驗證
docker version
```

:::tip Lima + Podman
Lima 也支援 Podman，對於不需要 Docker Compose 的使用場景，Podman 是更輕量的選擇：

```bash
limactl start template://podman
# 設定 Podman socket
export DOCKER_HOST=unix://$HOME/.lima/podman/sock/podman.sock
```
:::

### Apple Silicon（M1/M2/M3）架構問題

Apple Silicon 使用 ARM64 架構，而 KubeVirt 預設建置 amd64 binary，需要特別處理：

```bash
# 建置 ARM64 binary（在 M1/M2 Mac 本地執行用）
ARCH=arm64 make build

# 建置多架構 image
DOCKER_BUILDKIT=1 docker buildx create --use
DOCKER_BUILDKIT=1 docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myregistry.io/myuser/virt-handler:devel \
  --push .
```

:::warning 架構相容性
目前 kubevirtci 的開發叢集映像主要為 amd64 架構。在 Apple Silicon Mac 上，Docker Desktop 的 Rosetta 轉譯可以執行 amd64 容器，但效能較差。建議在 Linux (amd64) 環境進行完整的 kubevirtci 測試。
:::

---

## 常見建置問題與解決方案

### 問題：Go module checksum 驗證失敗

**症狀：**
```
verifying module: checksum mismatch
```

**解決方案：**
```bash
# 方案 1：設定 GONOSUMCHECK
export GONOSUMCHECK="k8s.io/*,sigs.k8s.io/*,kubevirt.io/*"

# 方案 2：設定 GONOSUMDB
export GONOSUMDB="*"

# 方案 3：清除 module cache 重試
go clean -modcache
```

### 問題：Docker Image Pull Rate Limit

**症狀：**
```
Error response from daemon: toomanyrequests: You have reached your pull rate limit.
```

**解決方案：**
```bash
# 登入 Docker Hub
docker login

# 或使用鏡像 registry（需在 kubevirtci 設定中指定）
# 或設定 DOCKER_PREFIX 使用自己的 registry
```

### 問題：kubevirtci 啟動失敗

**症狀：**
```
Error: failed to start cluster: /dev/kvm not found
```

**解決方案：**
```bash
# 檢查 KVM 是否存在
ls -la /dev/kvm

# 若不存在，載入 KVM 模組
sudo modprobe kvm-intel   # Intel
sudo modprobe kvm-amd     # AMD

# 確認虛擬化在 BIOS 中已啟用（需重開機進 BIOS 設定）

# 若在 VM 中開發，確認巢狀虛擬化已啟用
# VMware: 在 VM 設定中啟用 "Virtualize Intel VT-x/EPT or AMD-V/RVI"
# VirtualBox: 在 VM 設定 > 系統 > 加速 > 啟用 VT-x/AMD-V
# Hyper-V: Set-VMProcessor -VMName "MyVM" -ExposeVirtualizationExtensions $true
```

### 問題：bazel 版本不相容

**症狀：**
```
ERROR: The project you're trying to build requires Bazel X.Y.Z
```

**解決方案：**
```bash
# 使用 bazelisk（自動管理版本）
go install github.com/bazelbuild/bazelisk@latest
sudo ln -sf $GOPATH/bin/bazelisk /usr/local/bin/bazel

# 驗證：bazelisk 會讀取 .bazelversion 檔案自動下載對應版本
bazel version
```

### 問題：kubevirtci 記憶體不足

**症狀：**
```
Error: VM failed to start: not enough memory
# 或 kubevirtci 節點 crash / OOMKilled
```

**解決方案：**
```bash
# 降低每個節點的記憶體
export KUBEVIRT_MEMORY_SIZE=8192M   # 從 12288M 降低

# 或減少節點數量
export KUBEVIRT_NUM_NODES=1   # 只使用 1 個節點

# 重新建立叢集
make cluster-down
make cluster-up
```

### 問題：go generate 後有 uncommitted 變更

**症狀：**
```
CI 報告 "generated files are out of date"
```

**解決方案：**
```bash
# 執行完整生成流程
make generate

# 確認所有生成的變更都已加入 commit
git add -A
git status  # 確認無遺漏
git commit -s -m "generate: update generated files"
```

:::danger 不要手動編輯生成的檔案
所有 `zz_generated_*.go`、`*_generated.go` 等生成的檔案都不應手動編輯。任何修改都應透過 `make generate` 更新。手動修改在下次執行 `make generate` 時會被覆蓋。
:::

---

## Feature Gate 開啟方式（開發時常用）

在開發新功能時，通常需要開啟對應的 Feature Gate 才能測試。

### 開啟 Feature Gate 的指令

```bash
# 開啟單個 feature gate
cluster-up/kubectl.sh patch kubevirt kubevirt \
  -n kubevirt \
  --type=merge \
  -p '{"spec":{"configuration":{"developerConfiguration":{"featureGates":["ExpandDisks"]}}}}'

# 開啟多個 feature gate（常用組合）
cluster-up/kubectl.sh patch kubevirt kubevirt \
  -n kubevirt \
  --type=merge \
  -p '{
    "spec": {
      "configuration": {
        "developerConfiguration": {
          "featureGates": [
            "ExpandDisks",
            "HotplugVolumes",
            "LiveMigration",
            "Sidecar",
            "NetworkBindingPlugins"
          ]
        }
      }
    }
  }'

# 查看目前啟用的 feature gates
cluster-up/kubectl.sh get kubevirt kubevirt \
  -n kubevirt \
  -o jsonpath='{.spec.configuration.developerConfiguration.featureGates}'
```

### 常用 Feature Gates 列表

| Feature Gate | 說明 | 狀態 |
|--------------|------|------|
| `LiveMigration` | VM 線上遷移 | GA（通常預設啟用）|
| `HotplugVolumes` | 熱插拔磁碟 | Beta |
| `ExpandDisks` | 磁碟擴容 | Beta |
| `Sidecar` | Hook sidecar 支援 | Beta |
| `NetworkBindingPlugins` | 網路綁定插件框架 | Alpha |
| `HotplugNICs` | 熱插拔網路介面 | Alpha |
| `VMLiveUpdateFeatures` | VM 線上更新功能（CPU/Memory） | Alpha |
| `GPU` | GPU passthrough 支援 | Beta |
| `HostDevices` | 主機裝置 passthrough | Beta |
| `VSOCK` | VM VSOCK 通訊 | Alpha |
| `VMExport` | VM 匯出功能 | Alpha |
| `DisableMDEVConfiguration` | 停用 MDEV 設定 | Alpha |

:::tip Feature Gate 的預設狀態
從 KubeVirt v1.0 起，部分原本需要手動開啟的 feature gate 已預設啟用（如 `LiveMigration`）。開發時若要測試 Alpha 功能，通常都需要手動開啟。
:::

### 重置 Feature Gates

```bash
# 移除所有自訂 feature gates（回到預設）
cluster-up/kubectl.sh patch kubevirt kubevirt \
  -n kubevirt \
  --type=merge \
  -p '{"spec":{"configuration":{"developerConfiguration":{"featureGates":[]}}}}'
```

---

## 快速參考

### 常用指令速查表

```bash
# 叢集操作
make cluster-up                    # 啟動開發叢集
make cluster-down                  # 停止叢集
make cluster-sync                  # 建置 + 推送 + 部署（一鍵）

# 建置
make                               # 建置所有 binary
make build WHAT=cmd/virt-handler   # 建置特定 binary
make push                          # 建置並推送所有 images
make manifests                     # 生成 K8s manifests
make generate                      # 執行程式碼生成

# 測試
make test                          # 單元測試
make functest                      # e2e 功能測試
make lint                          # 執行 linter

# 叢集存取
cluster-up/kubectl.sh get pods -n kubevirt   # 查看 pods
cluster-up/ssh.sh node01                      # SSH 進節點
export KUBECONFIG=$(cluster-up/kubeconfig.sh) # 設定 KUBECONFIG
```

:::info 下一步
完成開發環境設置後，建議繼續閱讀：
- [程式碼架構導覽](./code-structure.md) — 了解各目錄和元件的職責
- KubeVirt 官方貢獻指南：[CONTRIBUTING.md](https://github.com/kubevirt/kubevirt/blob/main/CONTRIBUTING.md)
- Ginkgo 測試框架文件：[https://onsi.github.io/ginkgo/](https://onsi.github.io/ginkgo/)
:::
