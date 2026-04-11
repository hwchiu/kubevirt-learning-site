# VM 存取操作詳解

本文深入說明 KubeVirt 中存取虛擬機器的各種方式，包含 Console、VNC、SSH、Port-Forward 及 SCP 等操作的原理、設定步驟與實用範例。

:::info 前置需求
- 已安裝並設定 `virtctl`（參閱 [virtctl 完整指令參考](./guide.md)）
- 有效的 `kubeconfig` 且具備對目標 namespace 的存取權限
- 目標 VM 已啟動（狀態為 `Running`）
:::

---

## 1. Console 存取詳細說明

### 使用場景

Serial console 是 VM 的「緊急出口」，在以下情況非常關鍵：

- **VM 網路不通**：VM IP 設定錯誤、網路介面 down、防火牆阻擋時
- **OS 除錯**：系統進入 emergency mode 或 single user mode
- **查看啟動訊息**：觀察 kernel boot 過程、systemd 服務啟動狀態
- **密碼重置**：需要透過 console 執行 `passwd` 命令
- **GRUB 操作**：修改 boot 參數

### Console 存取原理

```
virtctl console → kube-apiserver (WebSocket) → virt-api → VMI WebSocket → libvirt → QEMU PTY
```

`virtctl console` 透過 Kubernetes API Server 建立 WebSocket 連線，經由 `virt-api` 轉發到 `virt-launcher` Pod 中的 libvirt，最終連接到 QEMU 模擬的 serial console（`/dev/ttyS0`）。

### Serial Console vs VNC Console

| 特性 | Serial Console | VNC Console |
|------|---------------|------------|
| 命令 | `virtctl console` | `virtctl vnc` |
| 介面類型 | 文字介面 | 圖形介面 |
| 啟動所需資源 | 極少 | 需要 VGA/GPU 虛擬化 |
| 適用 OS | Linux（需設定）、串列支援的 OS | 所有支援圖形介面的 OS |
| 網路需求 | 無（透過 K8s API） | 無（透過 K8s API） |
| Guest Agent | 不需要 | 不需要 |
| 退出方式 | `CTRL + ]` | 關閉 VNC viewer |

### 確保 Linux VM 有 Serial Console

大多數 Cloud Image 預設已啟用 serial console，但若你使用自訂映像，需手動設定：

```bash
# 在 VM guest 內執行
# 方法 1：編輯 /etc/default/grub
sudo vi /etc/default/grub

# 修改以下行（新增 console=ttyS0 參數）
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200n8"

# 重新生成 grub 設定
# RHEL/CentOS/Fedora：
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
# 或（UEFI 系統）：
sudo grub2-mkconfig -o /boot/efi/EFI/redhat/grub.cfg

# Ubuntu/Debian：
sudo update-grub
```

```bash
# 方法 2：確保 getty 服務在 ttyS0 運行
sudo systemctl enable --now serial-getty@ttyS0.service
sudo systemctl status serial-getty@ttyS0.service
```

:::warning Windows VM Console 注意事項
Windows VM 預設不啟用 serial console。若需要 console 存取 Windows VM，需要：
1. 啟用 EMS（Emergency Management Services）
2. 設定 Special Administration Console（SAC）

大多數情況下，Windows VM 建議使用 VNC 進行圖形介面存取。
:::

### Console 常見問題排查

**問題 1：連線後無任何輸出**

```bash
# 確認 VMI 正在運行
kubectl get vmi my-vm

# 確認 VM spec 中未停用 serial console
kubectl get vmi my-vm -o jsonpath='{.spec.domain.devices}'

# 查看 virt-launcher pod 日誌
kubectl logs -l vm.kubevirt.io/name=my-vm -c compute --tail=50
```

**問題 2：Console 輸入無回應（TTY 問題）**

```bash
# 連線後若輸入無回應，嘗試以下步驟：
# 1. 按幾次 Enter
# 2. 輸入 reset 並按 Enter
# 3. 若是 Linux，嘗試 Ctrl+L 清除畫面
```

**問題 3：Console 連線超時**

```bash
# 調整超時時間（單位：秒）
virtctl console my-vm --timeout=600
```

---

## 2. VNC 存取詳細說明

### 圖形介面連線方式

VNC（Virtual Network Computing）提供 VM 的圖形介面存取，適合 GUI 型 OS（Windows、有桌面環境的 Linux）。

```bash
# 最簡單的 VNC 存取方式
virtctl vnc my-vm
```

### virtctl vnc 工作原理

![virtctl vnc 工作流程](/diagrams/kubevirt/kubevirt-virtctl-vnc-flow.png)

`virtctl vnc` 的工作流程：
1. 與 kube-apiserver 建立 WebSocket 連線
2. 在本地啟動一個 WebSocket-to-VNC proxy
3. 自動偵測並啟動系統中安裝的 VNC viewer
4. VNC viewer 連接到本地 proxy，透過 WebSocket tunnel 到達 VM

### VNC Viewer 安裝建議

**macOS：**
```bash
# 使用 Homebrew 安裝 TigerVNC
brew install tiger-vnc

# 或安裝 Remmina（需要 XQuartz）
brew install --cask remmina
```

**Linux（Debian/Ubuntu）：**
```bash
# 安裝 virt-viewer（推薦）
sudo apt install virt-viewer

# 安裝 TigerVNC
sudo apt install tigervnc-viewer

# 安裝 Remmina
sudo apt install remmina remmina-plugin-vnc
```

**Linux（RHEL/Fedora）：**
```bash
# 安裝 virt-viewer（推薦，與 KubeVirt 最相容）
sudo dnf install virt-viewer

# 安裝 TigerVNC
sudo dnf install tigervnc
```

**Windows：**
- [TightVNC](https://www.tightvnc.com/) - 免費，功能完整
- [UltraVNC](https://uvnc.com/) - 免費，支援檔案傳輸
- [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) - 免費版可用

### --proxy-only 模式：手動連接 VNC

```bash
# 終端機 1：啟動 proxy，指定固定 port
virtctl vnc my-vm --proxy-only --custom-port=5900
# 輸出：
# 2024/01/15 10:00:00 address: 127.0.0.1:5900

# 終端機 2：手動使用 VNC viewer 連線
vncviewer 127.0.0.1:5900

# 使用 virt-viewer
remote-viewer vnc://127.0.0.1:5900

# 使用 noVNC（HTML5 VNC，在瀏覽器中開啟）
virtctl vnc my-vm --vnc-type=novnc --custom-port=6080
# 然後在瀏覽器開啟 http://127.0.0.1:6080
```

:::tip 多 VM 同時 VNC 連線
若需要同時存取多個 VM，為每個 VM 指定不同的 port：
```bash
# 終端機 1
virtctl vnc vm-1 --proxy-only --custom-port=5901 &

# 終端機 2
virtctl vnc vm-2 --proxy-only --custom-port=5902 &

# 分別連線
vncviewer 127.0.0.1:5901  # vm-1
vncviewer 127.0.0.1:5902  # vm-2
```
:::

### VNC 截圖功能

```bash
# 截取 VM 當前畫面（PNG 格式）
virtctl vnc my-vm --screenshot

# 指定截圖輸出檔名
virtctl vnc my-vm --screenshot --screenshot-file=vm-snapshot-$(date +%Y%m%d%H%M%S).png
```

:::info VNC 截圖使用場景
- 自動化測試：確認 VM 的 GUI 狀態
- 問題記錄：截取錯誤畫面供分析
- 無需安裝 VNC viewer 即可確認 VM 顯示內容
:::

### VNC 效能調整建議

```bash
# 建議在高延遲網路環境下使用 noVNC（HTML5 壓縮效果較好）
virtctl vnc my-vm --vnc-type=novnc

# 若 VNC 卡頓，確認 VM 的顯示裝置設定
kubectl get vmi my-vm -o yaml | grep -A 10 video
```

---

## 3. SSH 存取詳細說明

SSH 是存取 Linux VM 最常見的方式。`virtctl ssh` 透過 KubeVirt 的 WebSocket tunnel 建立 SSH 連線，無需 VM 有對外可達的 IP。

### 設定 SSH Key 注入

在使用 SSH 前，必須先設定 VM 接受你的 SSH 公鑰。KubeVirt 提供兩種方式：

#### 方式 A：cloud-init userData 注入（建立 VM 時設定）

在 VM 的 `cloud-init` 設定中直接注入 SSH 公鑰：

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-vm
spec:
  running: true
  template:
    spec:
      domain:
        devices:
          disks:
            - name: cloudinitdisk
              disk:
                bus: virtio
        resources:
          requests:
            memory: 2Gi
      volumes:
        - name: cloudinitdisk
          cloudInitNoCloud:
            userData: |
              #cloud-config
              users:
                - name: cloud-user
                  sudo: ALL=(ALL) NOPASSWD:ALL
                  shell: /bin/bash
                  ssh_authorized_keys:
                    - ssh-rsa AAAA...（你的 SSH 公鑰）
              # 或直接在 root 用戶設定
              ssh_authorized_keys:
                - ssh-rsa AAAA...（你的 SSH 公鑰）
```

```bash
# 套用 VM 設定
kubectl apply -f my-vm.yaml

# 等待 VM 啟動
kubectl wait vmi/my-vm --for=condition=Ready --timeout=180s

# 使用 SSH 連線
virtctl ssh cloud-user@my-vm
```

#### 方式 B：AccessCredentials CRD（動態注入）

`AccessCredentials` 允許在 VM 運行時動態注入 SSH 公鑰，無需重建 VM。

```yaml
# 步驟 1：建立包含 SSH 公鑰的 Secret
apiVersion: v1
kind: Secret
metadata:
  name: my-ssh-key-secret
type: Opaque
data:
  key: <base64-encoded-ssh-public-key>
  # 使用 base64 -w0 ~/.ssh/id_rsa.pub | pbcopy 取得
```

```yaml
# 步驟 2：在 VM spec 中設定 AccessCredentials
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-vm
spec:
  template:
    spec:
      accessCredentials:
        - sshPublicKey:
            source:
              secret:
                secretName: my-ssh-key-secret
            propagationMethod:
              qemuGuestAgent:
                users:
                  - cloud-user
      domain:
        devices: {}
      volumes: []
```

:::info AccessCredentials 詳細說明
`AccessCredentials` 在[第 6 節](#6-accesscredentials-crd-說明)有完整的介紹。
:::

### virtctl ssh 完整使用範例

```bash
# 基本 SSH 連線
virtctl ssh cloud-user@my-vm

# 指定 identity file（SSH 私鑰）
virtctl ssh my-vm \
  --username=cloud-user \
  --identity-file=~/.ssh/id_rsa

# 執行單一命令後返回（非互動式）
virtctl ssh my-vm \
  --username=cloud-user \
  --command="sudo systemctl status nginx"

# 查看 VM 的 hostname 和 OS 資訊
virtctl ssh my-vm \
  --username=cloud-user \
  --command="uname -a && cat /etc/os-release"

# 使用本地 ssh 客戶端（透過 ProxyCommand 模式）
virtctl ssh my-vm \
  --username=cloud-user \
  --local-ssh

# 傳遞額外的 ssh 選項
virtctl ssh my-vm \
  --username=cloud-user \
  --ssh-option="StrictHostKeyChecking=no" \
  --ssh-option="UserKnownHostsFile=/dev/null"

# 連接特定 namespace 的 VM
virtctl ssh my-vm \
  --username=cloud-user \
  -n production
```

### 透過 Port-Forward 進行 SSH

若不想使用 `virtctl ssh`，也可以手動透過 port-forward 建立 SSH tunnel：

```bash
# 終端機 1：建立 port-forward（本地 2222 → VM 22）
virtctl port-forward vm/my-vm 2222:22 -n production
# 或保持在背景運行
virtctl port-forward vm/my-vm 2222:22 -n production &

# 終端機 2：透過 port-forward 使用 SSH
ssh -p 2222 cloud-user@127.0.0.1

# 指定 identity file
ssh -p 2222 -i ~/.ssh/id_rsa cloud-user@127.0.0.1

# 傳輸檔案
scp -P 2222 local-file.txt cloud-user@127.0.0.1:/remote/path/
```

### SSH Config 範例（透過 ProxyCommand）

將 `virtctl port-forward` 整合到 `~/.ssh/config`，實現透明化 SSH 存取：

```ssh-config
# ~/.ssh/config

# 針對 KubeVirt VM 的通用設定
Host vm-*
  User cloud-user
  IdentityFile ~/.ssh/id_rsa
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  ProxyCommand virtctl port-forward --stdio %h 22

# 特定 VM（production namespace）
Host prod-web-vm
  Hostname my-web-vm
  User cloud-user
  IdentityFile ~/.ssh/prod_key
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  ProxyCommand virtctl port-forward --stdio vm/%h 22 -n production

# 特定 VM（使用 namespace 前綴）
Host vm/my-vm
  User cloud-user
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  ProxyCommand virtctl port-forward --stdio %h 22
```

```bash
# 設定好 SSH config 後，可以直接使用 ssh 連線
ssh cloud-user@my-vm           # 需要配置好 ProxyCommand

# 若使用上面的 prod-web-vm 設定
ssh prod-web-vm
```

:::tip ProxyCommand 說明
`ProxyCommand virtctl port-forward --stdio vm/%h 22` 中：
- `--stdio` 模式：使用 stdin/stdout 而非建立 TCP socket
- `%h`：SSH 會自動替換為目標 hostname（即 VM 名稱）
- `22`：VM 內部的 SSH port

這樣可以直接用 `ssh vm-name` 連線，而不需要每次都輸入完整的 `virtctl ssh` 命令。
:::

### 解決 SSH Host Key 驗證問題

```bash
# 方法 1：使用 --known-hosts 指定 known_hosts 檔案
virtctl ssh my-vm \
  --username=cloud-user \
  --known-hosts=/path/to/known_hosts

# 方法 2：直接略過 host key 驗證（不建議在生產環境使用）
virtctl ssh my-vm \
  --username=cloud-user \
  --ssh-option="StrictHostKeyChecking=no" \
  --ssh-option="UserKnownHostsFile=/dev/null"

# 方法 3：先掃描並儲存 host key
virtctl port-forward vm/my-vm 2222:22 &
ssh-keyscan -p 2222 127.0.0.1 >> ~/.ssh/known_hosts
# 之後的 SSH 連線就不會有 host key 警告
```

---

## 4. Port Forward 詳細說明

`virtctl port-forward` 允許將本地 port 轉發到 VM 內部的 port，無需 VM 有可達的網路介面。

### 語法詳解

```
virtctl port-forward [vm|vmi]/NAME [protocol/]localPort[:targetPort] [flags]

參數說明：
  vm/NAME    : 目標 VirtualMachine 名稱
  vmi/NAME   : 目標 VirtualMachineInstance 名稱
  protocol   : tcp（預設）或 udp
  localPort  : 本地監聽的 port（1-65535）
  targetPort : VM 內部的目標 port（若省略則與 localPort 相同）

Flags：
  -n, --namespace : 指定 namespace
  --stdio         : 使用 stdin/stdout 模式（用於 SSH ProxyCommand）
```

### TCP Port-Forward 範例

```bash
# 轉發 Web 服務（本地 8080 → VM 80）
virtctl port-forward vm/my-web-vm 8080:80
# 在瀏覽器開啟 http://localhost:8080

# 轉發 HTTPS（本地 8443 → VM 443）
virtctl port-forward vm/my-web-vm 8443:443

# 轉發 SSH（本地 2222 → VM 22）
virtctl port-forward vm/my-vm 2222:22
# 然後：ssh -p 2222 user@127.0.0.1

# 轉發資料庫（本地 3306 → VM MySQL 3306）
virtctl port-forward vm/my-db-vm 3306

# 轉發 PostgreSQL
virtctl port-forward vm/my-db-vm 5432

# 在背景執行 port-forward
virtctl port-forward vm/my-vm 8080:80 &
echo "Port-forward PID: $!"
```

### UDP Port-Forward 範例

```bash
# 轉發 DNS（本地 5353 → VM 53）
virtctl port-forward vm/my-dns-vm udp/5353:53

# 轉發 DHCP（本地 6767 → VM 67）
virtctl port-forward vm/my-dhcp-vm udp/6767:67

# 測試 UDP port-forward
# 終端機 1
virtctl port-forward vm/my-dns-vm udp/5353:53 &

# 終端機 2：測試 DNS 查詢
dig @127.0.0.1 -p 5353 example.com
```

### 多 Port 同時 Forward

```bash
# 同時 forward 多個 port（逗號分隔）
virtctl port-forward vm/my-vm 8080:80,8443:443,3306:3306

# Web + SSH + DB 全部 forward
virtctl port-forward vm/my-vm 8080:80,2222:22,3306:3306

# 混合 TCP 和 UDP
virtctl port-forward vm/my-vm 8080:80,udp/5353:53
```

### stdio 模式（用於 SSH ProxyCommand）

```bash
# stdio 模式不建立 TCP socket，而是使用 stdin/stdout 傳輸
# 通常用於 SSH config 的 ProxyCommand
virtctl port-forward --stdio vm/my-vm 22

# 完整的 SSH ProxyCommand 使用方式：
ssh -o "ProxyCommand=virtctl port-forward --stdio vm/my-vm 22" \
    -o "StrictHostKeyChecking=no" \
    cloud-user@my-vm
```

### 與 kubectl port-forward 的差異

| 特性 | `virtctl port-forward` | `kubectl port-forward` |
|------|----------------------|----------------------|
| 轉發目標 | VM 內部 port | Pod 內部 port |
| 適用物件 | VirtualMachine / VMI | Pod / Service / Deployment |
| 協定支援 | TCP + UDP | TCP only |
| 多 port | 支援（逗號分隔） | 支援（空格分隔） |
| stdio 模式 | 支援 | 不支援 |

:::warning 為什麼不能用 kubectl port-forward 存取 VM？
`kubectl port-forward` 轉發的是 Pod 的 port，`virt-launcher` Pod 運行的是 QEMU 程序，其監聽的 port 是 QEMU 管理 port，而非 VM guest OS 內的 port。因此存取 VM 內的服務必須使用 `virtctl port-forward`。
:::

### 使用場景範例

```bash
# 場景 1：開發環境快速存取 VM 中的 Web 服務
virtctl port-forward vm/dev-vm 8080:80 &
curl http://localhost:8080/healthz

# 場景 2：連線 VM 中的資料庫進行管理
virtctl port-forward vm/db-vm 3306 &
mysql -h 127.0.0.1 -P 3306 -u root -p

# 場景 3：遠端 debug（將 debug port 轉發到本地）
virtctl port-forward vm/app-vm 5005:5005 &
# 然後在 IDE 中使用 remote debug 連線到 127.0.0.1:5005
```

---

## 5. SCP 詳細說明

`virtctl scp` 提供在本地主機與 VM 之間複製檔案的功能，底層透過 WebSocket tunnel 傳輸。

### virtctl scp 語法

```
virtctl scp [flags] [[user@]SOURCE] [[user@]DESTINATION]

SOURCE 和 DESTINATION 格式：
  - 本地路徑：/local/path/file.txt
  - VM 路徑：[user@][vm|vmi/]vmName:remote/path/file.txt

Flags：
  -r, --recursive              : 遞迴複製目錄
  --username                   : 指定 SSH 用戶名
  --identity-file              : 指定 SSH 私鑰路徑
  -n, --namespace              : 指定 namespace
  --ssh-option                 : 傳遞額外 SSH 選項
```

### 上傳到 VM

```bash
# 上傳單一檔案到 VM
virtctl scp /local/path/config.yaml cloud-user@my-vm:/home/cloud-user/

# 上傳到特定目錄
virtctl scp /local/scripts/deploy.sh cloud-user@my-vm:/opt/scripts/

# 指定 identity file
virtctl scp --identity-file=~/.ssh/id_rsa \
  /local/file.txt cloud-user@my-vm:/remote/path/

# 上傳到 production namespace 的 VM
virtctl scp -n production \
  /local/app.jar cloud-user@my-vm:/opt/app/

# 使用 vm/ 前綴格式
virtctl scp /local/file.txt --username=cloud-user vm/my-vm:/remote/path/
```

### 下載從 VM

```bash
# 下載 VM 中的日誌檔案
virtctl scp cloud-user@my-vm:/var/log/app/app.log ./app.log

# 下載設定檔
virtctl scp cloud-user@my-vm:/etc/nginx/nginx.conf ./nginx.conf.bak

# 下載到特定目錄
virtctl scp cloud-user@my-vm:/home/cloud-user/results.csv ./data/

# 從 production namespace VM 下載
virtctl scp -n production \
  cloud-user@my-vm:/var/log/system.log ./logs/$(date +%Y%m%d)-system.log

# 批量下載（使用 glob pattern）
virtctl scp cloud-user@my-vm:"/var/log/*.log" ./logs/
```

### 遞迴複製目錄

```bash
# 上傳整個目錄到 VM
virtctl scp -r /local/config-dir/ cloud-user@my-vm:/etc/app-config/

# 下載整個目錄從 VM
virtctl scp -r cloud-user@my-vm:/home/cloud-user/project/ ./local-backup/

# 同步設定目錄（會覆蓋已存在的檔案）
virtctl scp -r /local/configs/ \
  --ssh-option="StrictHostKeyChecking=no" \
  cloud-user@my-vm:/opt/configs/
```

:::tip SCP 與 rsync 的選擇
- `virtctl scp`：簡單的單次複製，無需在 VM 中安裝額外工具
- `rsync`（透過 port-forward）：適合需要增量同步、斷點續傳的場景

使用 rsync 透過 port-forward：
```bash
# 先建立 port-forward
virtctl port-forward vm/my-vm 2222:22 &

# 使用 rsync 同步（透過 SSH port-forward）
rsync -avz -e "ssh -p 2222" \
  /local/path/ cloud-user@127.0.0.1:/remote/path/
```
:::

---

## 6. AccessCredentials CRD 說明

### 什麼是 AccessCredentials

`AccessCredentials` 是 KubeVirt 的 CRD 機制，允許在 VM 運行時**動態注入** SSH 公鑰或用戶密碼，而不需要重建 VM。

與 cloud-init 的靜態注入不同，`AccessCredentials` 支援：
- 動態更換 SSH 公鑰（只需更新 Secret）
- 多用戶、多公鑰管理
- 與外部 Secret 管理系統整合（如 HashiCorp Vault、AWS Secrets Manager）

### SSHPublicKey Source 類型

目前支援從 **Kubernetes Secret** 讀取 SSH 公鑰：

```yaml
accessCredentials:
  - sshPublicKey:
      source:
        secret:
          secretName: my-ssh-key-secret  # K8s Secret 名稱
      propagationMethod:
        # 見下方 propagationMethod 說明
```

### propagationMethod 類型

#### 1. QemuGuestAgent（透過 QEMU Guest Agent 注入）

需要 VM 中已安裝並運行 `qemu-guest-agent`，注入會即時生效。

```yaml
propagationMethod:
  qemuGuestAgent:
    users:
      - cloud-user      # 注入到哪個用戶的 authorized_keys
      - admin
```

#### 2. ConfigDrive（透過 ConfigDrive 注入）

透過 ConfigDrive volume 注入（無需 guest agent），但需要 VM 重啟後才能生效。

```yaml
propagationMethod:
  configDrive: {}
```

### 完整 YAML 範例

**步驟 1：建立包含 SSH 公鑰的 Secret**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: developer-ssh-keys
  namespace: default
type: Opaque
data:
  # base64 編碼的 SSH 公鑰（可包含多行，每行一個公鑰）
  # 取得方式：cat ~/.ssh/id_rsa.pub | base64 -w0
  key: c3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBREFRQUJBQUFBZ1FDNi4uLg==
```

```bash
# 使用 kubectl 命令建立 Secret（推薦，避免手動 base64 編碼）
kubectl create secret generic developer-ssh-keys \
  --from-file=key=$HOME/.ssh/id_rsa.pub
```

**步驟 2：在 VM 中設定 AccessCredentials**

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-secure-vm
  namespace: default
spec:
  running: true
  template:
    metadata:
      labels:
        kubevirt.io/vm: my-secure-vm
    spec:
      # AccessCredentials 設定
      accessCredentials:
        # 使用 QemuGuestAgent 注入（即時生效）
        - sshPublicKey:
            source:
              secret:
                secretName: developer-ssh-keys
            propagationMethod:
              qemuGuestAgent:
                users:
                  - cloud-user
                  - ubuntu
        # 也可以同時設定多個 AccessCredential
        - sshPublicKey:
            source:
              secret:
                secretName: ops-team-ssh-keys
            propagationMethod:
              qemuGuestAgent:
                users:
                  - cloud-user
      domain:
        cpu:
          cores: 2
        memory:
          guest: 4Gi
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
      volumes:
        - name: rootdisk
          dataVolume:
            name: fedora-dv
        - name: cloudinitdisk
          cloudInitNoCloud:
            userData: |
              #cloud-config
              # 確保 cloud-user 存在
              users:
                - name: cloud-user
                  sudo: ALL=(ALL) NOPASSWD:ALL
                  shell: /bin/bash
```

**步驟 3：動態更新 SSH 公鑰**

```bash
# 更新 Secret 中的 SSH 公鑰（只需更新 Secret，不需重建 VM）
kubectl create secret generic developer-ssh-keys \
  --from-file=key=$HOME/.ssh/new_id_rsa.pub \
  --dry-run=client -o yaml | kubectl apply -f -

# 若使用 QemuGuestAgent，變更會在幾秒內自動生效
# 驗證
virtctl ssh my-secure-vm \
  --username=cloud-user \
  --identity-file=~/.ssh/new_id_rsa
```

:::tip 多用戶 SSH 存取管理
使用 `AccessCredentials` 可以輕鬆實現多用戶存取控制：

```yaml
# 每個用戶或團隊一個 Secret
accessCredentials:
  - sshPublicKey:
      source:
        secret:
          secretName: alice-ssh-key
      propagationMethod:
        qemuGuestAgent:
          users: [alice]
  - sshPublicKey:
      source:
        secret:
          secretName: bob-ssh-key
      propagationMethod:
        qemuGuestAgent:
          users: [bob]
  - sshPublicKey:
      source:
        secret:
          secretName: ops-team-keys
      propagationMethod:
        qemuGuestAgent:
          users: [cloud-user]  # 多個公鑰可以注入到同一用戶
```
:::

:::warning AccessCredentials 的注意事項
1. **QemuGuestAgent** 方式需要 VM 中已安裝 `qemu-guest-agent` 並正在運行
2. **ConfigDrive** 方式需要 VM 重啟才能套用新的 SSH 公鑰
3. Secret 必須與 VM 在**同一個 namespace**
4. 若 Secret 被刪除，已注入的公鑰不會自動移除（需要手動清除）
:::

---

## 7. USB Redirection

### usbredir 支援說明

KubeVirt 支援 USB Redirection，允許將客戶端的 USB 裝置重定向到 VM 中使用。

```yaml
# 在 VM spec 中啟用 USB Redirection
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-usb-vm
spec:
  template:
    spec:
      domain:
        devices:
          # 啟用 USB
          inputs:
            - type: tablet
              bus: usb
              name: tablet
          # 設定 USB redirection（需要叢集支援）
```

### 需要 Client 端支援

USB Redirection 需要支援 usbredir 協定的 VNC 客戶端：

- **virt-viewer / remote-viewer**（Linux/macOS）：完整支援 usbredir
- **SPICE client**：最佳 USB Redirection 支援

```bash
# 使用 virt-viewer（支援 USB Redirection）
# 需要先啟動 VNC proxy
virtctl vnc my-usb-vm --proxy-only --custom-port=5900 &
remote-viewer vnc://127.0.0.1:5900
```

### 使用限制

:::warning USB Redirection 限制
1. 並非所有 USB 裝置都支援重定向（需要 usbredir 協定相容）
2. 效能受網路延遲影響，高速 USB 裝置（如 USB 3.0 儲存裝置）效能可能較差
3. 加密的 USB 裝置通常無法正確重定向
4. 部分叢集設定可能限制 USB Redirection 功能
5. Windows VM 可能需要安裝額外的 usbredir 驅動程式
:::

---

## 8. 完整範例集

### 範例 1：設定 cloud-init SSH Key + virtctl ssh 存取

```bash
# 1. 取得你的 SSH 公鑰
cat ~/.ssh/id_rsa.pub
# 輸出：ssh-rsa AAAAB3NzaC1yc2E... user@hostname

# 2. 建立 VM YAML（含 cloud-init SSH key 設定）
cat << 'EOF' > my-vm.yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: demo-vm
  namespace: default
spec:
  running: true
  template:
    spec:
      domain:
        cpu:
          cores: 2
        memory:
          guest: 4Gi
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
      volumes:
        - name: rootdisk
          containerDisk:
            image: quay.io/kubevirt/fedora-cloud-container-disk-demo:latest
        - name: cloudinitdisk
          cloudInitNoCloud:
            userData: |
              #cloud-config
              users:
                - name: fedora
                  sudo: ALL=(ALL) NOPASSWD:ALL
                  shell: /bin/bash
                  ssh_authorized_keys:
                    - ssh-rsa AAAAB3NzaC1yc2E...（替換為你的公鑰）
EOF

# 3. 建立 VM
kubectl apply -f my-vm.yaml

# 4. 等待 VM 啟動
kubectl wait vmi/demo-vm --for=condition=Ready --timeout=180s

# 5. 確認 VM 狀態
kubectl get vmi demo-vm

# 6. SSH 連線
virtctl ssh demo-vm --username=fedora

# 7. 執行命令確認環境
virtctl ssh demo-vm --username=fedora --command="uname -a"
```

### 範例 2：AccessCredentials 動態 SSH Key 注入

```bash
# 1. 建立 SSH key（若還沒有）
ssh-keygen -t rsa -b 4096 -f ~/.ssh/kubevirt_key -N ""

# 2. 建立包含公鑰的 K8s Secret
kubectl create secret generic my-ssh-public-key \
  --from-file=key=$HOME/.ssh/kubevirt_key.pub

# 3. 確認 Secret 已建立
kubectl get secret my-ssh-public-key
kubectl describe secret my-ssh-public-key

# 4. 建立使用 AccessCredentials 的 VM
cat << 'EOF' | kubectl apply -f -
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: access-cred-demo
spec:
  running: true
  template:
    spec:
      accessCredentials:
        - sshPublicKey:
            source:
              secret:
                secretName: my-ssh-public-key
            propagationMethod:
              qemuGuestAgent:
                users:
                  - cloud-user
      domain:
        cpu:
          cores: 2
        memory:
          guest: 2Gi
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
      volumes:
        - name: rootdisk
          containerDisk:
            image: quay.io/kubevirt/fedora-cloud-container-disk-demo:latest
        - name: cloudinitdisk
          cloudInitNoCloud:
            userData: |
              #cloud-config
              users:
                - name: cloud-user
                  sudo: ALL=(ALL) NOPASSWD:ALL
                  shell: /bin/bash
              packages:
                - qemu-guest-agent
              runcmd:
                - systemctl enable --now qemu-guest-agent
EOF

# 5. 等待 VM 啟動並確認 guest agent 運行
kubectl wait vmi/access-cred-demo --for=condition=Ready --timeout=180s
virtctl guestosinfo access-cred-demo  # 確認 guest agent 正常

# 6. 使用指定的 key 進行 SSH 連線
virtctl ssh access-cred-demo \
  --username=cloud-user \
  --identity-file=~/.ssh/kubevirt_key

# 7. 動態更換 SSH Key（無需重啟 VM）
# 產生新的 key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/kubevirt_key_new -N ""

# 更新 Secret
kubectl create secret generic my-ssh-public-key \
  --from-file=key=$HOME/.ssh/kubevirt_key_new.pub \
  --dry-run=client -o yaml | kubectl apply -f -

# 等待幾秒後，使用新 key 連線
sleep 10
virtctl ssh access-cred-demo \
  --username=cloud-user \
  --identity-file=~/.ssh/kubevirt_key_new
```

### 範例 3：VNC 連線完整範例

```bash
# 1. 確認 VM 正在運行
kubectl get vmi my-windows-vm

# 2. 方法 A：自動啟動 VNC viewer
virtctl vnc my-windows-vm

# 3. 方法 B：手動指定 port 並連線
virtctl vnc my-windows-vm --proxy-only --custom-port=5900 &
VNC_PID=$!

# 等待 proxy 啟動
sleep 2

# macOS 使用 TigerVNC 連線
vncviewer 127.0.0.1:5900

# Linux 使用 virt-viewer 連線
remote-viewer vnc://127.0.0.1:5900

# 結束後關閉 proxy
kill $VNC_PID

# 4. 截取 VM 截圖（用於監控或問題記錄）
virtctl vnc my-windows-vm \
  --screenshot \
  --screenshot-file="screenshot-$(date +%Y%m%d-%H%M%S).png"

ls -la screenshot-*.png
```

### 範例 4：Port-Forward + SSH ProxyCommand 配置

```bash
# 1. 設定 SSH config
cat << 'EOF' >> ~/.ssh/config

# KubeVirt VMs - 使用 virtctl port-forward 作為 ProxyCommand
Host kv-*
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  IdentityFile ~/.ssh/kubevirt_key
  ProxyCommand virtctl port-forward --stdio vm/%h 22

# Production namespace 的 VM
Host prod-vm-*
  User cloud-user
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  IdentityFile ~/.ssh/prod_key
  ProxyCommand virtctl port-forward --stdio vm/%h 22 -n production
EOF

# 2. 確認 SSH config 語法正確
ssh -G kv-my-vm | head -20

# 3. 使用簡化的 SSH 命令連線（Host 規則名稱需與 VM 名稱匹配）
# 例如 VM 名稱為 my-app-vm，SSH host 設定為 kv-my-app-vm
ssh cloud-user@kv-my-vm  # 等效於 virtctl ssh my-vm --username=cloud-user

# 4. 使用 SCP（透過相同的 ProxyCommand）
scp -r /local/configs/ cloud-user@kv-my-vm:/etc/app/

# 5. 使用 rsync（增量同步）
rsync -avz --progress \
  /local/data/ \
  cloud-user@kv-my-vm:/remote/data/
```

### 範例 5：SCP 上傳/下載範例

```bash
# ====== 上傳範例 ======

# 上傳設定檔
virtctl scp \
  --identity-file=~/.ssh/id_rsa \
  ./app-config.yaml \
  cloud-user@my-vm:/etc/myapp/config.yaml

# 上傳部署腳本並執行
virtctl scp ./deploy.sh cloud-user@my-vm:/tmp/deploy.sh
virtctl ssh my-vm \
  --username=cloud-user \
  --command="chmod +x /tmp/deploy.sh && sudo /tmp/deploy.sh"

# 批量上傳（使用 rsync 透過 port-forward）
virtctl port-forward vm/my-vm 2222:22 &
rsync -avz -e "ssh -p 2222 -i ~/.ssh/id_rsa" \
  ./configs/ cloud-user@127.0.0.1:/etc/app/configs/

# ====== 下載範例 ======

# 下載日誌檔案（含時間戳記命名）
virtctl scp \
  cloud-user@my-vm:/var/log/app/error.log \
  "./logs/error-$(date +%Y%m%d).log"

# 下載整個日誌目錄
virtctl scp -r \
  cloud-user@my-vm:/var/log/app/ \
  ./app-logs-backup/

# 下載 VM 的設定備份
virtctl scp \
  cloud-user@my-vm:/etc/myapp/ \
  ./backup/configs/

# 從 production namespace 下載事件日誌
virtctl scp \
  -n production \
  --identity-file=~/.ssh/prod_key \
  cloud-user@prod-vm:/var/log/audit/audit.log \
  ./audit-$(date +%Y%m%d).log

# ====== 結合使用範例 ======

# 備份 VM 設定後更新，確認後再部署
virtctl scp cloud-user@my-vm:/etc/nginx/nginx.conf ./nginx.conf.bak
vim ./nginx.conf.bak  # 編輯
virtctl scp ./nginx.conf.bak cloud-user@my-vm:/etc/nginx/nginx.conf
virtctl ssh my-vm \
  --username=cloud-user \
  --command="sudo nginx -t && sudo systemctl reload nginx"
```

---

## 總結：存取方式選擇指南

| 情境 | 推薦方式 | 命令 |
|------|---------|------|
| VM 無網路，緊急登入 | Serial Console | `virtctl console` |
| Windows VM 或 GUI 操作 | VNC | `virtctl vnc` |
| Linux VM 日常操作 | SSH | `virtctl ssh` |
| 存取 VM 上的 Web 服務 | Port Forward | `virtctl port-forward` |
| 上傳/下載少量檔案 | SCP | `virtctl scp` |
| 大量檔案同步 | rsync via port-forward | `rsync -e ssh` |
| 自動化腳本中的 SSH | ProxyCommand | SSH config |
| 動態管理 SSH Key | AccessCredentials | CRD + Secret |
