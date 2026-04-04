# virtctl 完整指令參考

`virtctl` 是 KubeVirt 專屬的 CLI 工具，提供 `kubectl` 所缺乏的虛擬機操作能力，包含生命週期管理、Console 存取、儲存熱插拔等功能。

:::info 版本說明
`virtctl` 版本應與叢集中安裝的 KubeVirt 版本保持一致，以確保 API 相容性。
:::

---

## 1. 安裝與設定

### 從 GitHub Release 下載

KubeVirt 官方在每個 Release 提供對應平台的 `virtctl` 二進位檔。

```bash
# 自動偵測叢集版本與當前平台架構
VERSION=$(kubectl get kubevirt.kubevirt.io/kubevirt -n kubevirt \
  -o=jsonpath="{.status.observedKubeVirtVersion}")
ARCH=$(uname -s | tr A-Z a-z)-$(uname -m | sed 's/x86_64/amd64/') || windows-amd64.exe

echo "版本: ${VERSION}"
echo "架構: ${ARCH}"

# 下載並安裝
curl -L -o virtctl \
  https://github.com/kubevirt/kubevirt/releases/download/${VERSION}/virtctl-${VERSION}-${ARCH}
chmod +x virtctl
sudo mv virtctl /usr/local/bin
```

:::tip 手動指定版本
若不想依賴叢集查詢，可直接指定版本：
```bash
VERSION=v1.3.0
curl -L -o virtctl \
  https://github.com/kubevirt/kubevirt/releases/download/${VERSION}/virtctl-${VERSION}-linux-amd64
```
:::

### 作為 kubectl Plugin 安裝（Krew）

[Krew](https://krew.sigs.k8s.io/) 是 `kubectl` 的 plugin 管理器，可透過 `krew` 安裝 `virtctl`。

```bash
# 安裝 krew（若尚未安裝）
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)

# 安裝 virt plugin
kubectl krew install virt

# 驗證版本
kubectl virt version
```

:::info Krew 安裝後的使用方式
透過 Krew 安裝後，所有 `virtctl` 命令都改以 `kubectl virt` 方式呼叫：
```bash
kubectl virt start my-vm
kubectl virt console my-vm
```
:::

### kubeconfig 設定

`virtctl` 使用與 `kubectl` 相同的 kubeconfig 設定。

```bash
# 使用預設 kubeconfig（~/.kube/config）
virtctl version

# 指定特定 kubeconfig 檔案
virtctl version --kubeconfig=/path/to/custom/kubeconfig

# 指定 Namespace
virtctl start my-vm -n production

# 設定預設 Namespace（透過 kubectl）
kubectl config set-context --current --namespace=my-namespace
```

### 驗證安裝

```bash
# 查看 virtctl 版本及伺服器連線狀態
virtctl version

# 預期輸出範例：
# Client Version: version.Info{GitVersion:"v1.3.0", ...}
# Server Version: version.Info{GitVersion:"v1.3.0", ...}

# 列出可用命令
virtctl --help
```

:::warning 版本不符警告
若 Client 版本與 Server 版本不一致，部分功能可能無法正常運作。建議保持版本同步。
:::

---

## 2. VM 生命週期管理

### virtctl start

啟動一個已停止的 VirtualMachine。

```bash
# 基本啟動
virtctl start my-vm

# 在指定 namespace 啟動
virtctl start my-vm -n production

# 以暫停狀態啟動（VM 資源已建立，vCPU 暫停，可用於調試）
virtctl start my-vm --paused

# 啟動後等待 VM 進入 Running 狀態（使用 kubectl wait）
virtctl start my-vm && \
  kubectl wait vmi/my-vm --for=condition=Ready --timeout=120s

# 啟動並觀察 VMI 狀態變化
virtctl start my-vm
kubectl get vmi my-vm -w
```

:::tip --paused 的使用場景
`--paused` 適合需要在 VM 完全啟動前進行操作的場景，例如：
- 附加 debugger 到 vCPU
- 在 guest 開始執行前設定 memory breakpoint
啟動後使用 `virtctl unpause` 恢復執行。
:::

### virtctl stop

停止一個正在執行的 VirtualMachine。

```bash
# 正常停止（發送 ACPI shutdown 信號，等待 guest OS 優雅關機）
virtctl stop my-vm

# 強制停止（立即斷電，等同於直接拔掉電源線）
virtctl stop my-vm --force

# 設定優雅停機期限（等待最多 60 秒，超時後強制停止）
virtctl stop my-vm --grace-period=60

# 在指定 namespace 停止
virtctl stop my-vm -n staging

# 強制停止並忽略 grace period（0 秒等待）
virtctl stop my-vm --grace-period=0
```

:::warning stop vs stop --force
| 選項 | 行為 | 資料安全性 |
|------|------|-----------|
| `virtctl stop` | 發送 ACPI 關機信號，guest OS 正常關機 | 安全，OS 會完成 flush |
| `virtctl stop --force` | 立即終止 VMI，不等待 guest OS | 風險：可能造成資料不一致 |
| `virtctl stop --grace-period=N` | 等待 N 秒後若未停止則強制停止 | 折衷方案 |

建議正常情況使用 `virtctl stop`，只有在 VM 無回應時才使用 `--force`。
:::

### virtctl restart

重啟一個正在執行的 VirtualMachine。

```bash
# 正常重啟（發送 ACPI reboot 信號，等待 guest OS 正常重啟）
virtctl restart my-vm

# 強制重啟（立即重設，等同於按下 reset 按鈕）
virtctl restart my-vm --force

# 設定 grace period 後重啟
virtctl restart my-vm --grace-period=30

# 在特定 namespace 重啟
virtctl restart my-vm -n production
```

:::info restart 適用場景
- **正常重啟**：kernel 更新後、服務設定變更後需要重啟
- **強制重啟**：VM 當機無回應，需要強制恢復

`virtctl restart` 會保留 VM 設定（PVC 掛載、網路設定等），重啟後 VMI 將使用最新的 VM spec。
:::

### virtctl pause

暫停 VM 的 vCPU 執行，記憶體狀態會被保留。

```bash
# 暫停 VirtualMachine（高階物件，建議使用）
virtctl pause vm my-vm

# 暫停 VirtualMachineInstance（底層物件）
virtctl pause vmi my-vm

# 暫停特定 namespace 的 VM
virtctl pause vm my-vm -n production

# 確認暫停狀態
kubectl get vm my-vm -o jsonpath='{.status.printableStatus}'
# 輸出: Paused
```

:::info pause vs stop 的差異
| 操作 | 記憶體狀態 | 磁碟 I/O | CPU | 恢復速度 |
|------|-----------|---------|-----|---------|
| `pause` | 保留（in-memory） | 停止 | 凍結 | 毫秒級 |
| `stop` | 清除 | 關閉 | 停止 | 需要完整開機 |

`pause` 類似於「暫停遊戲」，所有記憶體內容都保留；`stop` 則是完全關機。
:::

### virtctl unpause

恢復已暫停的 VM。

```bash
# 恢復 VirtualMachine
virtctl unpause vm my-vm

# 恢復 VirtualMachineInstance
virtctl unpause vmi my-vm

# 恢復特定 namespace 的 VM
virtctl unpause vm my-vm -n production

# 確認恢復後狀態
kubectl get vm my-vm -o jsonpath='{.status.printableStatus}'
# 輸出: Running
```

### virtctl migrate

觸發 VM 的 Live Migration（熱遷移）到其他節點。

```bash
# 基本熱遷移（KubeVirt 自動選擇目標節點）
virtctl migrate my-vm

# 指定目標節點選擇器（限制遷移到具有特定 label 的節點）
virtctl migrate my-vm --addedNodeSelector kubernetes.io/hostname=node-02

# 遷移到特定 zone 的節點
virtctl migrate my-vm --addedNodeSelector topology.kubernetes.io/zone=us-east-1b

# 在特定 namespace 執行遷移
virtctl migrate my-vm -n production

# 觸發遷移後監控狀態
virtctl migrate my-vm
kubectl get vmim -w  # 監控 VirtualMachineInstanceMigration 物件

# 查看詳細遷移進度
kubectl describe vmim $(kubectl get vmim -o jsonpath='{.items[0].metadata.name}')
```

:::tip 查詢遷移狀態
```bash
# 列出所有遷移任務
kubectl get virtualmachineinstancemigration

# 查看特定 VM 的遷移歷史
kubectl get vmim -l kubevirt.io/vmi-name=my-vm

# 查看遷移詳情
kubectl describe vmim <migration-name>
```
:::

:::warning Live Migration 前提條件
Live Migration 需要：
1. 共享儲存（NFS、Ceph RBD 等），`ReadWriteMany` 存取模式
2. 目標節點有足夠的 CPU 和記憶體資源
3. 若 VM 使用 `hostDisk`，則無法進行 Live Migration
:::

### virtctl migrate-cancel

取消正在進行的 Live Migration。

```bash
# 取消特定 VM 的遷移
virtctl migrate-cancel my-vm

# 取消特定 namespace 的 VM 遷移
virtctl migrate-cancel my-vm -n production

# 確認取消狀態
kubectl get vmim -l kubevirt.io/vmi-name=my-vm
```

### virtctl reset

對 VM 執行硬重置（等同於按下實體主機的 Reset 按鈕）。

```bash
# 硬重置 VM（立即重設，不等待 guest OS）
virtctl reset my-vm

# 在特定 namespace 硬重置
virtctl reset my-vm -n production
```

:::warning reset vs restart --force
`virtctl reset` 和 `virtctl restart --force` 功能相似，都是強制重設 VM，不等待 guest OS 正常關閉。
- `reset`：直接在 QEMU 層級發送 reset 信號
- `restart --force`：終止並重建 VMI

兩者都可能造成 guest OS 內的資料遺失，請謹慎使用。
:::

### virtctl soft-reboot

透過 ACPI 或 Guest Agent 向 guest OS 發送軟重啟信號。

```bash
# 發送軟重啟信號（需要 guest agent 或 ACPI 支援）
virtctl soft-reboot my-vm

# 在特定 namespace 發送軟重啟
virtctl soft-reboot my-vm -n production
```

:::info soft-reboot 的需求
`virtctl soft-reboot` 需要以下其中一個條件：
1. **QEMU Guest Agent**：已安裝且運行中（推薦）
2. **ACPI**：VM spec 中啟用 ACPI（大多數 Linux/Windows VM 預設支援）

若兩者皆不可用，命令將會失敗。
:::

---

## 3. Console 與存取

### virtctl console

連接到 VM 的 serial console，適用於無法透過網路存取 VM 的緊急情況。

```bash
# 基本 console 連接（Serial Console）
virtctl console my-vm

# 指定連線超時（預設 5 分鐘）
virtctl console my-vm --timeout=300

# 連接特定 namespace 的 VM console
virtctl console my-vm -n production

# 連接 VMI（而非 VM）
virtctl console vmi/my-vm
```

:::tip 退出 Console
連接到 console 後，按下 **`CTRL + ]`** 即可退出 console 連線並回到 terminal。

若使用 `kubectl virt console`，退出方式相同。
:::

:::warning Console 無輸出的排查
若連接 console 後無任何輸出，請確認：

1. **Linux VM**：確保 grub 設定包含 serial console 參數：
   ```
   GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200n8"
   ```
   並執行 `grub2-mkconfig -o /boot/grub2/grub.cfg`

2. **VM Spec**：確認 VMI spec 中有設定 serial console：
   ```yaml
   spec:
     domain:
       devices:
         # serial console 預設啟用，若明確設定請確認未被停用
   ```

3. **TTY 設定**：若 console 輸入無回應，可能是 TTY 設定問題，嘗試按 Enter 或輸入幾個字元。
:::

### virtctl vnc

啟動 VNC 連線，透過圖形介面存取 VM。

```bash
# 基本 VNC 連線（自動啟動本地 VNC viewer）
virtctl vnc my-vm

# 只啟動 WebSocket proxy，不自動開啟 VNC viewer
virtctl vnc my-vm --proxy-only

# 指定自訂 proxy 埠（預設為隨機可用埠）
virtctl vnc my-vm --custom-port=5900

# 使用 noVNC（HTML5 VNC client）
virtctl vnc my-vm --vnc-type=novnc

# 連接特定 namespace 的 VM
virtctl vnc my-vm -n production

# 截取 VM 畫面截圖（輸出 PNG 檔案）
virtctl vnc my-vm --screenshot --screenshot-file=vm-screenshot.png
```

:::info --proxy-only 使用方式
使用 `--proxy-only` 時，`virtctl` 只啟動本地 WebSocket proxy，你需要手動開啟 VNC viewer 連線：

```bash
# 終端機 1：啟動 proxy
virtctl vnc my-vm --proxy-only --custom-port=5900
# 輸出：Proxy listening at 127.0.0.1:5900

# 終端機 2：使用任意 VNC viewer 連線
vncviewer 127.0.0.1:5900
# 或使用 Remmina / TigerVNC
```
:::

:::tip VNC Viewer 推薦
- **macOS**：TigerVNC (`brew install tiger-vnc`)、Remmina
- **Linux**：`virt-viewer`、TigerVNC、Remmina
- **Windows**：TightVNC、UltraVNC、RealVNC
:::

### virtctl ssh

透過 KubeVirt 建立的 WebSocket tunnel 進行 SSH 連線，無需 VM 有對外 IP。

```bash
# 基本 SSH 連線（自動建立 port-forward tunnel）
virtctl ssh cloud-user@my-vm

# 指定 SSH 用戶名（不在 host 前指定的方式）
virtctl ssh my-vm --username=cloud-user

# 指定 SSH key 檔案
virtctl ssh my-vm --username=ubuntu --identity-file=~/.ssh/id_rsa

# 指定 SSH port（若 VM 內 SSH 不是監聽 22）
virtctl ssh my-vm --username=cloud-user --port=2222

# 執行單一命令並返回（非互動式）
virtctl ssh my-vm --username=cloud-user --command="uname -a"

# 使用本地 ssh 客戶端（透過 ProxyCommand 模式）
virtctl ssh my-vm --username=cloud-user --local-ssh

# 連接特定 namespace 的 VM
virtctl ssh my-vm --username=cloud-user -n production

# 透過 jump host 使用（配合 --local-ssh 和 SSH config）
virtctl ssh my-vm --username=cloud-user --local-ssh \
  --ssh-option="StrictHostKeyChecking=no"
```

:::warning SSH Key 設定
使用 `virtctl ssh` 前，需確保 VM 已設定好 SSH 公鑰：
1. 透過 **cloud-init** 在 VM 建立時注入
2. 透過 **AccessCredentials CRD** 動態注入

詳細說明請參閱 [VM 存取操作詳解](./access.md)。
:::

### virtctl scp

在本地主機與 VM 之間複製檔案，語法與標準 `scp` 相容。

```bash
# 上傳本地檔案到 VM
virtctl scp /local/path/file.txt cloud-user@my-vm:/remote/path/

# 下載 VM 中的檔案到本地
virtctl scp cloud-user@my-vm:/remote/path/file.txt /local/path/

# 遞迴複製整個目錄到 VM
virtctl scp -r /local/directory cloud-user@my-vm:/remote/path/

# 指定 SSH identity file
virtctl scp --identity-file=~/.ssh/id_rsa \
  /local/file.txt cloud-user@my-vm:/remote/path/

# 從特定 namespace 的 VM 下載檔案
virtctl scp -n production cloud-user@my-vm:/var/log/app.log ./app.log
```

:::tip SCP 語法說明
`virtctl scp` 語法中，VM/VMI 名稱使用 `vm/NAME` 或 `vmi/NAME` 格式，或直接用 `user@NAME` 格式：

```bash
# 兩種等效語法
virtctl scp file.txt cloud-user@my-vm:/tmp/
virtctl scp file.txt --username=cloud-user vm/my-vm:/tmp/
```
:::

### virtctl port-forward

將 VM/VMI 內部 port 轉發到本地，支援 TCP 和 UDP 協定。

```bash
# 基本 TCP port-forward（本地 8080 -> VM 80）
virtctl port-forward vm/my-vm 8080:80

# 本地和遠端使用相同 port
virtctl port-forward vm/my-vm 8080

# UDP port-forward（DNS 服務）
virtctl port-forward vm/my-vm udp/5353:53

# 同時 forward 多個 port（逗號分隔）
virtctl port-forward vm/my-vm 8080:80,8443:443,3306:3306

# forward VMI 的 port
virtctl port-forward vmi/my-vm 8080:80

# 使用 stdio 模式（用於 SSH ProxyCommand，不建立 TCP socket）
virtctl port-forward --stdio vm/my-vm 22

# 在特定 namespace 使用 port-forward
virtctl port-forward vm/my-vm 8080:80 -n production
```

:::info port-forward 語法詳解
```
virtctl port-forward [vm|vmi]/NAME [protocol/]localPort[:targetPort]

protocol  : tcp（預設）或 udp
localPort : 本地監聽的 port
targetPort: VM 內部的目標 port（若省略則與 localPort 相同）
```

範例對照：
| 命令 | 效果 |
|------|------|
| `virtctl port-forward vm/my-vm 8080:80` | 本地 8080 → VM 80 (TCP) |
| `virtctl port-forward vm/my-vm 3306` | 本地 3306 → VM 3306 (TCP) |
| `virtctl port-forward vm/my-vm udp/5353:53` | 本地 5353 → VM 53 (UDP) |
:::

:::info 與 kubectl port-forward 的差異
| 工具 | 轉發目標 | 適用物件 |
|------|---------|---------|
| `kubectl port-forward` | Pod 內的 port | Kubernetes Pod |
| `virtctl port-forward` | VM 內部 port | KubeVirt VM/VMI |

`kubectl port-forward` 無法直接存取 VM 內部的 port，必須使用 `virtctl port-forward`。
:::

---

## 4. 儲存管理

### virtctl addvolume

熱插拔（Hot-plug）一個 Volume 到正在運行的 VM/VMI。

```bash
# 熱插拔 PVC 到 VM
virtctl addvolume my-vm --volume-name=my-pvc

# 熱插拔 DataVolume 到 VM
virtctl addvolume my-vm --volume-name=my-dv \
  --disk-type=disk

# 設定 serial 號（用於 udev 規則識別）
virtctl addvolume my-vm --volume-name=my-pvc \
  --serial=CUSTOM-SERIAL-001

# 指定匯流排類型（scsi 或 virtio）
virtctl addvolume my-vm --volume-name=my-pvc \
  --bus=scsi

# 設定快取模式
virtctl addvolume my-vm --volume-name=my-pvc \
  --cache=none

# 以 LUN 類型掛載（適用於 iSCSI 等區塊裝置）
virtctl addvolume my-vm --volume-name=my-pvc \
  --disk-type=lun

# 熱插拔到 VMI（直接）
virtctl addvolume vmi/my-vm --volume-name=my-pvc
```

:::warning 熱插拔 PVC 的限制
- PVC 必須在相同 namespace
- `ReadWriteOnce` PVC 只能掛載到一個 VM
- 熱插拔的 volume 在 VM 重啟後預設不會自動重新掛載（非 persistent），除非 VM spec 中也有對應設定
:::

### virtctl removevolume

移除一個已熱插拔的 Volume。

```bash
# 移除熱插拔的 volume
virtctl removevolume my-vm --volume-name=my-pvc

# 移除特定 namespace VM 的 volume
virtctl removevolume my-vm --volume-name=my-pvc -n production

# 移除 VMI 的 volume
virtctl removevolume vmi/my-vm --volume-name=my-pvc
```

### virtctl expand

通知 VM 的 guest OS 磁碟已擴展，觸發線上磁碟容量調整。

```bash
# 擴展後通知 VM（觸發 guest 端識別新容量）
virtctl expand my-vm

# 在特定 namespace 執行
virtctl expand my-vm -n production
```

:::info 線上磁碟擴展完整流程
1. 擴展 PVC（或 DataVolume）大小
2. 執行 `virtctl expand my-vm` 通知 VM
3. 在 guest OS 內調整分割區和檔案系統大小：
   ```bash
   # Linux guest 內執行
   sudo growpart /dev/vda 1
   sudo resize2fs /dev/vda1
   # 或對於 XFS
   sudo xfs_growfs /
   ```
:::

### virtctl imageupload

上傳本地磁碟映像檔（ISO、QCOW2、RAW）到叢集中的 DataVolume 或 PVC。

```bash
# 基本上傳：上傳 qcow2 映像到新建的 DataVolume
virtctl imageupload dv my-dv \
  --image-path=/path/to/fedora.qcow2 \
  --size=10Gi \
  --uploadproxy-url=https://cdi-uploadproxy.example.com

# 上傳到已存在的 PVC
virtctl imageupload pvc my-pvc \
  --image-path=/path/to/ubuntu.iso \
  --uploadproxy-url=https://cdi-uploadproxy.example.com

# 指定存取模式
virtctl imageupload dv my-dv \
  --image-path=/path/to/centos.qcow2 \
  --size=20Gi \
  --access-mode=ReadWriteOnce \
  --uploadproxy-url=https://cdi-uploadproxy.example.com

# 上傳到 block volume
virtctl imageupload dv my-block-dv \
  --image-path=/path/to/disk.raw \
  --size=50Gi \
  --volume-mode=block \
  --uploadproxy-url=https://cdi-uploadproxy.example.com

# 使用 StorageClass 指定儲存類別
virtctl imageupload dv my-dv \
  --image-path=/path/to/image.qcow2 \
  --size=10Gi \
  --storage-class=rook-ceph-block \
  --uploadproxy-url=https://cdi-uploadproxy.example.com

# 查詢 CDI Upload Proxy URL
kubectl get svc -n cdi cdi-uploadproxy \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

:::tip imageupload 流程說明
1. `virtctl imageupload` 在叢集中建立 `DataVolume`（若指定）
2. CDI 自動建立 `UploadProxy` 接收映像
3. `virtctl` 將本地映像以 HTTP multipart 方式上傳
4. CDI 將映像轉換並儲存到 PVC

需要確保：
- CDI（Containerized Data Importer）已安裝
- CDI Upload Proxy 可從本地存取（或使用 `kubectl port-forward`）
:::

:::info 繞過 TLS 驗證
若 CDI uploadproxy 使用自簽憑證：
```bash
virtctl imageupload dv my-dv \
  --image-path=/path/to/image.qcow2 \
  --size=10Gi \
  --uploadproxy-url=https://cdi-uploadproxy.example.com \
  --insecure
```
:::

### virtctl memorydump

將 VM 記憶體 dump 到 PVC，用於除錯分析。

```bash
# 將 VM 記憶體 dump 到指定 PVC
virtctl memorydump get my-vm --claim-name=my-memory-dump-pvc

# 自動建立 PVC 並 dump 記憶體
virtctl memorydump get my-vm \
  --claim-name=my-memory-dump-pvc \
  --create-claim \
  --access-mode=ReadWriteOnce

# 指定輸出格式（raw 或 gzip 壓縮）
virtctl memorydump get my-vm \
  --claim-name=my-memory-dump-pvc \
  --create-claim \
  --format=gzip

# 移除已建立的 memory dump 關聯（不刪除 PVC 本身）
virtctl memorydump remove my-vm

# 在特定 namespace 執行
virtctl memorydump get my-vm \
  --claim-name=my-memory-dump-pvc \
  -n production
```

:::info 使用 memory dump 進行分析
Memory dump 完成後，掛載 PVC 到另一個 Pod 即可分析：
```bash
# 建立分析 Pod，掛載 memory dump PVC
kubectl run analyzer --image=ubuntu \
  --overrides='{"spec":{"volumes":[{"name":"dump","persistentVolumeClaim":{"claimName":"my-memory-dump-pvc"}}],"containers":[{"name":"analyzer","image":"ubuntu","command":["sleep","infinity"],"volumeMounts":[{"name":"dump","mountPath":"/dump"}]}]}}'

# 進入 Pod 分析 dump
kubectl exec -it analyzer -- bash
ls /dump/
```
:::

---

## 5. VM 資訊查詢

### virtctl guestosinfo

查看 VM 中 guest OS 的詳細資訊（需要已安裝並運行 QEMU Guest Agent）。

```bash
# 查看 guest OS 詳細資訊
virtctl guestosinfo my-vm

# 查看特定 namespace VM 的 OS 資訊
virtctl guestosinfo my-vm -n production

# 輸出為 JSON 格式（預設即為 JSON）
virtctl guestosinfo my-vm | jq '.'

# 只查看 OS 名稱和版本
virtctl guestosinfo my-vm | jq '{name: .name, version: .version}'
```

:::info guestosinfo 輸出範例
```json
{
  "guestAgentVersion": "5.2.0",
  "hostname": "my-vm",
  "os": {
    "name": "Fedora Linux",
    "kernelRelease": "6.5.6-300.fc39.x86_64",
    "version": "39 (Cloud Edition)",
    "prettyName": "Fedora Linux 39 (Cloud Edition)",
    "versionId": "39",
    "kernelVersion": "#1 SMP PREEMPT_DYNAMIC ...",
    "machine": "x86_64",
    "id": "fedora"
  },
  "timezone": "UTC, 0"
}
```

若 guest agent 未安裝，命令將返回錯誤：`VM does not have guest agent`
:::

### virtctl userlist

列出目前已登入 VM 的用戶列表（需要 QEMU Guest Agent）。

```bash
# 列出 VM 中已登入的用戶
virtctl userlist my-vm

# 查詢特定 namespace VM
virtctl userlist my-vm -n production

# 輸出為 JSON 並解析
virtctl userlist my-vm | jq '.'
```

:::info userlist 輸出範例
```json
[
  {
    "userName": "cloud-user",
    "domain": "",
    "loginTime": 1701388800
  }
]
```
:::

### virtctl fslist

列出 VM 中掛載的檔案系統資訊（需要 QEMU Guest Agent）。

```bash
# 列出 VM 中所有檔案系統
virtctl fslist my-vm

# 查詢特定 namespace VM
virtctl fslist my-vm -n production

# 格式化輸出
virtctl fslist my-vm | jq '.[] | {mountPoint: .mountPoint, type: .type, totalBytes: .totalBytes}'
```

:::info fslist 輸出範例
```json
[
  {
    "diskName": "vda",
    "mountPoint": "/",
    "fileSystemType": "xfs",
    "usedBytes": 2147483648,
    "totalBytes": 10737418240
  },
  {
    "diskName": "vda",
    "mountPoint": "/boot",
    "fileSystemType": "xfs",
    "usedBytes": 209715200,
    "totalBytes": 1073741824
  }
]
```
:::

---

## 6. 建立資源

### virtctl create vm

使用命令列參數快速生成 VM YAML，方便 GitOps 或腳本化建立。

```bash
# 基本建立（輸出 YAML，不立即套用）
virtctl create vm --name=my-new-vm

# 指定 CPU 和記憶體
virtctl create vm --name=my-vm \
  --instancetype=u1.small

# 使用 instance type 和 preference
virtctl create vm --name=my-vm \
  --instancetype=u1.medium \
  --preference=windows.2k22

# 添加 ContainerDisk volume（使用 container image 作為磁碟）
virtctl create vm --name=my-vm \
  --volume-containerdisk=src:registry.example.com/fedora:39

# 添加現有 PVC
virtctl create vm --name=my-vm \
  --volume-pvc=my-data-pvc

# 添加 DataVolume（自動建立 PVC）
virtctl create vm --name=my-vm \
  --volume-datasource=src:fedora/fedora39

# 指定 cloud-init user data（Base64 或檔案路徑）
virtctl create vm --name=my-vm \
  --volume-containerdisk=src:registry.example.com/fedora:39 \
  --cloud-init-user-data="I2Nsb3VkLWNvbmZpZwpzc2hfYXV0aG9yaXplZF9rZXlzOgogIC0gc3NoLXJzYSBBQUFBLi4u"

# 直接套用到叢集
virtctl create vm --name=my-vm \
  --instancetype=u1.small \
  --volume-containerdisk=src:registry.example.com/fedora:39 | kubectl apply -f -

# 輸出為 YAML 供審閱
virtctl create vm --name=my-vm \
  --instancetype=u1.small \
  --volume-containerdisk=src:registry.example.com/fedora:39 \
  -o yaml
```

:::tip 常用 cloud-init 設定編碼
```bash
# 將 cloud-init 設定編碼為 Base64
cat << 'EOF' | base64 -w0
#cloud-config
users:
  - name: cloud-user
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-rsa AAAA...
EOF
```
:::

### virtctl create instancetype

建立 VirtualMachineInstancetype（可重複使用的資源規格模板）。

```bash
# 建立 namespace-scoped instancetype（VirtualMachineInstancetype）
virtctl create instancetype \
  --name=my-instancetype \
  --cpu=4 \
  --memory=8Gi

# 建立 cluster-scoped instancetype（VirtualMachineClusterInstancetype）
virtctl create instancetype \
  --name=my-cluster-instancetype \
  --cpu=8 \
  --memory=16Gi \
  --cluster-wide

# 輸出並套用
virtctl create instancetype \
  --name=custom-small \
  --cpu=2 \
  --memory=4Gi | kubectl apply -f -
```

:::info Namespace vs Cluster Scope
| 類型 | CRD 名稱 | 適用範圍 |
|------|---------|---------|
| Namespace-scoped | `VirtualMachineInstancetype` | 單一 namespace |
| Cluster-scoped | `VirtualMachineClusterInstancetype` | 整個叢集 |

建議：
- **開發/測試環境**：使用 namespace-scoped，避免影響其他團隊
- **共用基礎架構**：使用 cluster-scoped，統一管理規格
:::

### virtctl create preference

建立 VirtualMachinePreference（定義 OS 偏好設定）。

```bash
# 建立 namespace-scoped preference（Linux 偏好）
virtctl create preference \
  --name=my-linux-preference

# 建立 cluster-scoped preference
virtctl create preference \
  --name=linux-common \
  --cluster-wide

# 輸出並套用
virtctl create preference \
  --name=fedora-pref | kubectl apply -f -
```

### virtctl create clone

基於現有 VM 建立 Clone（複製 VM）。

```bash
# 從 VM 建立 clone
virtctl create clone \
  --source-name=my-source-vm \
  --name=my-cloned-vm | kubectl apply -f -

# 指定來源和目標 VM 名稱
virtctl create clone \
  --source-name=template-vm \
  --name=prod-vm-01 | kubectl apply -f -

# 跨 namespace clone（需要適當的 RBAC 權限）
virtctl create clone \
  --source-name=my-vm \
  --name=cloned-vm \
  --source-namespace=staging \
  --target-namespace=production | kubectl apply -f -
```

---

## 7. 其他操作

### virtctl expose

為 VM 或 VMI 建立 Kubernetes Service，讓外部流量可以存取 VM。

```bash
# 建立 ClusterIP Service（叢集內部存取）
virtctl expose vm my-vm \
  --port=80 \
  --name=my-vm-web

# 建立 NodePort Service（透過節點 IP 存取）
virtctl expose vm my-vm \
  --port=80 \
  --name=my-vm-web-nodeport \
  --type=NodePort

# 指定目標 port（Service port 與 VM port 不同）
virtctl expose vm my-vm \
  --port=8080 \
  --target-port=80 \
  --name=my-vm-service

# 建立 LoadBalancer Service（使用 cloud 負載均衡器）
virtctl expose vm my-vm \
  --port=443 \
  --name=my-vm-lb \
  --type=LoadBalancer

# 在特定 namespace 建立 Service
virtctl expose vm my-vm \
  --port=3306 \
  --name=my-vm-mysql \
  --type=ClusterIP \
  -n production
```

### virtctl vmexport

匯出 VM、VMI 或 PVC 的磁碟內容，支援加密下載。

```bash
# 建立 VMExport 物件（開始匯出流程）
virtctl vmexport create my-export \
  --vm=my-vm

# 下載匯出的磁碟映像
virtctl vmexport download my-export \
  --output=my-vm-disk.qcow2

# 指定格式下載
virtctl vmexport download my-export \
  --output=my-vm-disk.raw \
  --format=raw

# 完成後刪除 VMExport 物件
virtctl vmexport delete my-export

# 從 PVC 建立匯出
virtctl vmexport create my-pvc-export \
  --pvc=my-data-pvc
```

### virtctl guestfs

啟動一個帶有 `libguestfs` 工具的臨時 Pod，用於直接存取 PVC 中的磁碟映像。

```bash
# 掛載 PVC 並啟動互動式 guestfs shell
virtctl guestfs my-pvc

# 指定自訂映像（預設使用 kubevirt/libguestfs-tools）
virtctl guestfs my-pvc --image=custom/libguestfs:latest

# 指定 PVC namespace
virtctl guestfs my-pvc -n production

# 在 guestfs shell 中可執行的操作範例：
# virt-filesystems --all --long -h -a /dev/vda
# virt-df -h
# guestmount -a /dev/vda -m /dev/sda1 /mnt
# ls /mnt
```

:::tip guestfs 使用場景
- 修復損壞的 guest OS（在 VM 無法啟動時）
- 直接讀取 PVC 中的設定檔
- 調整 VM 磁碟大小後的手動 resize
- 提取 VM 中的資料（無需啟動 VM）
:::

### virtctl adm logverbosity

動態調整 KubeVirt 各元件的 log 詳細程度，適用於 debug 場景。

```bash
# 設定所有元件的 log verbosity
virtctl adm log-verbosity --all 4

# 只設定 virt-api 的 log level
virtctl adm log-verbosity --virt-api 5

# 設定 virt-controller 的 log level
virtctl adm log-verbosity --virt-controller 6

# 設定 virt-handler 的 log level（每個節點的 daemon）
virtctl adm log-verbosity --virt-handler 7

# 設定 virt-launcher 的 log level（每個 VMI 的 process）
virtctl adm log-verbosity --virt-launcher 8

# 設定最高 verbosity（通常只在深度 debug 時使用）
virtctl adm log-verbosity --all 9

# 恢復正常 log level
virtctl adm log-verbosity --all 2
```

:::warning Log Verbosity 等級說明
| 等級 | 說明 | 建議使用場景 |
|------|------|------------|
| 0 | 只顯示 Fatal 錯誤 | 生產環境（最靜音） |
| 2 | 一般資訊（預設） | 正常生產環境 |
| 4 | 詳細資訊 | 一般問題排查 |
| 6 | 更詳細（含 API 呼叫） | 深度排查 |
| 9 | 最詳細（含所有操作） | 開發 debug |

**注意**：高 verbosity 會產生大量日誌，影響效能，請在排查完畢後恢復到正常等級。
:::

### virtctl objectgraph

查看 VM 相關資源的依賴圖，了解 VM 和其他 Kubernetes 物件的關係。

```bash
# 查看 VM 的物件依賴圖
virtctl objectgraph vm my-vm

# 查看 VMI 的物件依賴圖
virtctl objectgraph vmi my-vm

# 查看特定 namespace 的物件依賴圖
virtctl objectgraph vm my-vm -n production
```

:::info objectgraph 輸出說明
`objectgraph` 會列出 VM 相關的所有資源，例如：
- VirtualMachine
- VirtualMachineInstance
- DataVolume / PVC
- Pod（virt-launcher pod）
- Service（若已建立）
- Migration 物件

適合用於了解刪除 VM 時會影響哪些資源。
:::

### virtctl version

查看 `virtctl` 客戶端和 KubeVirt 伺服器的版本資訊。

```bash
# 查看完整版本資訊（client + server）
virtctl version

# 只顯示客戶端版本
virtctl version --client

# 輸出為 JSON 格式
virtctl version -o json

# 輸出為 YAML 格式
virtctl version -o yaml
```

:::info 版本輸出範例
```
Client Version: version.Info{
  GitVersion: "v1.3.0",
  GitCommit:  "abc123...",
  BuildDate:  "2024-01-15T10:00:00Z",
  GoVersion:  "go1.21.0",
  Compiler:   "gc",
  Platform:   "linux/amd64"
}
Server Version: version.Info{
  GitVersion: "v1.3.0",
  GitCommit:  "abc123...",
  BuildDate:  "2024-01-15T10:00:00Z",
  GoVersion:  "go1.21.0",
  Compiler:   "gc",
  Platform:   "linux/amd64"
}
```
:::

---

## 快速參考表

| 命令 | 功能 | 常用選項 |
|------|------|---------|
| `virtctl start` | 啟動 VM | `--paused` |
| `virtctl stop` | 停止 VM | `--force`, `--grace-period` |
| `virtctl restart` | 重啟 VM | `--force` |
| `virtctl pause` | 暫停 VM | - |
| `virtctl unpause` | 恢復 VM | - |
| `virtctl migrate` | 熱遷移 | `--addedNodeSelector` |
| `virtctl migrate-cancel` | 取消遷移 | - |
| `virtctl reset` | 硬重置 | - |
| `virtctl soft-reboot` | 軟重啟 | - |
| `virtctl console` | Serial console | `--timeout` |
| `virtctl vnc` | VNC 連線 | `--proxy-only`, `--custom-port` |
| `virtctl ssh` | SSH 連線 | `--username`, `--identity-file` |
| `virtctl scp` | 檔案複製 | `-r` |
| `virtctl port-forward` | Port 轉發 | - |
| `virtctl addvolume` | 熱插拔 volume | `--serial`, `--bus` |
| `virtctl removevolume` | 移除 volume | - |
| `virtctl imageupload` | 上傳映像 | `--uploadproxy-url`, `--size` |
| `virtctl memorydump` | 記憶體 dump | `--claim-name`, `--create-claim` |
| `virtctl guestosinfo` | OS 資訊 | - |
| `virtctl userlist` | 已登入用戶 | - |
| `virtctl fslist` | 檔案系統列表 | - |
| `virtctl create vm` | 建立 VM | `--instancetype`, `--preference` |
| `virtctl expose` | 建立 Service | `--type`, `--port` |
| `virtctl vmexport` | 匯出磁碟 | `--output`, `--format` |
| `virtctl guestfs` | libguestfs shell | - |
| `virtctl version` | 版本資訊 | `--client` |
