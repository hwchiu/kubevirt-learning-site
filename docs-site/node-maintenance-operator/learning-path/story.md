---
layout: doc
title: NMO — 學習路徑：阿明的節點維護日記
---

# 📖 阿明的節點維護日記

> 跟著阿明，從接到「20 個節點要做硬體升級」這個任務開始，一步步理解 Node Maintenance Operator 的世界。
> 每個章節都是阿明真實遭遇的問題——你會看到他怎麼查文件、怎麼犯錯、怎麼一點一點把拼圖拼起來。

---

## 序章：那通改變阿明星期五下午的電話

星期五下午四點半，阿明正在收拾桌面，打算準時下班。

Slack 突然跳出一則訊息，是公司的 Infrastructure Manager：「阿明，下週開始機房要換這批 node 的記憶體，每台都要斷電重啟。你那邊的 cluster 要怎麼配合？」

阿明盯著螢幕，心裡算了一下：他管的生產 cluster 有 22 個 worker node，上面跑著十幾個 KubeVirt VM，每台都是客戶的業務系統——訂單處理、金流對帳，全部 24/7 不能停。

*這……要怎麼維護？*

他知道 Kubernetes 有 `kubectl drain` 這個工具，可以把節點上的 Pod 全部驅逐出去，讓節點安全下線。但他從沒在生產環境用過，心裡沒底。週末就到了，他決定先在測試環境跑一遍，摸清楚整個流程再說。

---

## 第一章：「手動 drain，原來這麼麻煩」

週末，阿明在測試環境試著手動維護一個節點。他的計畫很簡單：

```bash
kubectl cordon node-worker-01
kubectl drain node-worker-01 --ignore-daemonsets --delete-emptydir-data
```

第一個命令順利。`cordon` 把節點標記為 `SchedulingDisabled`，讓 K8s 不再把新 Pod 調度上去。

第二個命令開始執行，輸出一大串 Pod 名稱……然後卡住了。

```
evicting pod kubevirt-system/virt-launcher-vm-database-01-xxxxx
error when evicting pods/"virt-launcher-vm-database-01-xxxxx":
  Cannot evict pod as it would violate the pod's disruption budget.
```

*什麼？什麼叫 disruption budget？*

阿明搜尋了一下，發現 PodDisruptionBudget（PDB）是 K8s 的一種保護機制——如果你要驅逐某個 Pod，但驅逐後 PDB 限制的「最低可用副本數」會被打破，K8s 就會拒絕驅逐。他的 VM 對應的 `virt-launcher` Pod 剛好被 KubeVirt 設了 PDB，只允許同時最多一個不可用。

他等了幾分鐘，drain 還是卡著。他不確定要不要強制跳過 PDB——萬一在生產環境這樣做，VM 直接死掉怎麼辦？

除了 PDB，他還發現另一個問題：`kubectl drain` 是一次性命令，沒有狀態保存。如果 drain 到一半他的終端機斷線，或者他需要知道「現在有哪幾個節點在維護中」，他完全沒有辦法一眼查看。他要 SSH 進去看 taint，要用 `kubectl get pods -o wide` 看哪些 Pod 還沒被驅逐——整個過程分散在好幾個命令和好幾個終端機視窗裡。

*這要是在生產環境做 22 個節點，我會瘋掉。*

到了晚上，他把遭遇的問題記下來：
1. PDB 讓 drain 卡住，不知道要不要強制跳過
2. 沒有集中的「維護狀態」可以追蹤
3. drain 完之後如果要取消維護（uncordon），要記得自己手動做
4. 如果有多個人同時在維護不同節點，完全不知道對方的進度

他關掉電腦，心想：*應該有更好的做法吧。*

---

> ### 📚 去這裡深入了解
> 阿明遭遇的這些痛點，正是 NMO 設計出來要解決的問題：
>
> - [專案總覽](/node-maintenance-operator/) — 了解 NMO 的設計目標，以及它如何把「節點維護」變成一個可追蹤的 Kubernetes 資源
>
> 讀完後，你應該能回答：NMO 幫你自動化了哪些手動步驟？

---

## 第二章：「發現 NMO：一個 CR 搞定一切」

週一早上，阿明跟同事 Jason 提起週末的嘗試。Jason 眼睛一亮：「你沒用 NMO 嗎？Node Maintenance Operator？」

「什麼 Operator？」

Jason 把文件連結丟過來。阿明打開看，發現 Node Maintenance Operator 的概念非常直觀——你建立一個 `NodeMaintenance` 這個 Custom Resource，指定要維護的節點名稱，NMO 就會自動幫你：

1. **Cordon** 節點（禁止新 Pod 調度上去）
2. 套用 **Taint**（讓節點有個明確的「正在維護」標記）
3. **驅逐**所有 Pod（等同 `kubectl drain`，但有 retry、有進度追蹤）
4. 持續更新 CR 的 **status**（你可以用 `kubectl get nodemaintenance` 看到當前狀態）

當你做完維護，刪掉這個 CR，NMO 就自動 uncordon 節點、移除 taint。

阿明試著建立他的第一個 `NodeMaintenance`：

```yaml
apiVersion: nodemaintenance.medik8s.io/v1beta1
kind: NodeMaintenance
metadata:
  name: maintenance-worker-01
spec:
  nodeName: node-worker-01
  reason: "Hardware memory upgrade - scheduled maintenance window"
```

```bash
kubectl apply -f maintenance-worker-01.yaml
```

他接著用 `kubectl get nodemaintenance maintenance-worker-01 -o yaml` 觀察 status：

```yaml
status:
  phase: Running
  totalPods: 8
  evictionPods: 6
  drainProgress: 25
  pendingPods:
    - virt-launcher-vm-database-01-xxxxx
    - virt-launcher-vm-webserver-02-xxxxx
```

*這個比 `kubectl drain` 強太多了。* 他可以清楚看到：總共有 8 個 Pod 要驅逐、目前處理了 6 個、進度 25%、還有哪兩個 Pod 卡住了。這些資訊全部都持久化在 etcd 裡，不會因為他關掉終端機就消失。

他還注意到 `phase` 欄位——它從 `Pending` 開始，進入 `Running`，完成後會變成 `Succeeded`。這是一個清楚的**狀態機**，每個狀態都有明確的語義。

*這才是在生產環境維護節點的正確方式。*

---

> ### 📚 去這裡深入了解
> 阿明看到的 `NodeMaintenance` CR 欄位，這裡有完整的規格說明：
>
> - [NodeMaintenance CRD 規格](/node-maintenance-operator/crd-specification) — `spec` 和 `status` 的每個欄位詳解，包括 `phase`、`drainProgress`、`pendingPods` 的意義
> - [系統架構](/node-maintenance-operator/architecture) — Reconcile 流程與狀態機的完整視圖
>
> 讀完後，你應該能解釋：`phase: Running` 和 `phase: Succeeded` 分別代表什麼狀態？

---

## 第三章：「觀察排空過程：progress 的每一格都有故事」

建立 CR 之後，阿明沒有立刻走開。他在終端機開了一個 watch：

```bash
kubectl get nodemaintenance maintenance-worker-01 -w
```

然後另一個終端機跑：

```bash
kubectl get pods -A --field-selector spec.nodeName=node-worker-01 -w
```

他想親眼看到驅逐的過程。

NMO 的 Reconcile loop 每隔幾秒就會更新一次 status。阿明觀察到幾個有趣的現象：

**DaemonSet 的 Pod 不會被驅逐**。他的 cluster 上有 `node-exporter`、`fluentd`、`calico-node` 這些 DaemonSet，它們的 Pod 在 drain 過程中完全沒有被動到。*這跟 `kubectl drain --ignore-daemonsets` 的行為一樣，NMO 預設就這樣處理。*

**emptyDir 的 Pod 也被驅逐了**。他有一個使用 `emptyDir` 的 log aggregator Pod，他本來以為這個 Pod 裡的資料會讓它無法被驅逐，但 NMO 還是把它驅逐了（`emptyDir` 的資料會丟失，NMO 預設允許這樣做）。他在文件裡確認這是正常行為。

**`drainProgress` 的計算方式**：他發現 `drainProgress` 是百分比，計算方式是「已成功驅逐的 Pod 數 / 總 Pod 數」。這讓他可以大概估計還要多久。

大約五分鐘後，他看到 `phase` 變成了 `Succeeded`：

```yaml
status:
  phase: Succeeded
  drainProgress: 100
  totalPods: 8
  evictionPods: 8
```

他去確認節點狀態：

```bash
kubectl get node node-worker-01
```

```
NAME             STATUS                     ROLES    AGE   VERSION
node-worker-01   Ready,SchedulingDisabled   <none>   45d   v1.27.3
```

節點還活著（`Ready`），但已經被 cordon（`SchedulingDisabled`），上面沒有任何非 DaemonSet 的 Pod 了。這個節點現在可以安全地做硬體維護。

*終於。* 阿明覺得這個流程比手動 drain 優雅太多。

---

> ### 📚 去這裡深入了解
> 阿明觀察到的排空過程細節，這裡有完整的技術解析：
>
> - [節點排空工作流程](/node-maintenance-operator/node-drainage-process) — 驅逐的執行邏輯、retry 機制、DaemonSet 和 emptyDir 的處理方式
>
> 讀完後，你應該能解釋：NMO 如何決定哪些 Pod 需要被驅逐、哪些可以忽略？

---

## 第四章：「PodDisruptionBudget 又來了——這次 NMO 怎麼處理？」

維護 `node-worker-01` 成功了。阿明信心大增，立刻建立 `node-worker-02` 的 `NodeMaintenance`。

這次，`phase` 停在 `Running` 超過十分鐘沒動。`pendingPods` 裡有一個 Pod 一直在那裡：

```yaml
pendingPods:
  - virt-launcher-vm-order-processing-xxxxx
```

他用 `kubectl describe pod` 查看，沒有明顯錯誤。他去查 Events：

```bash
kubectl get events --field-selector involvedObject.name=maintenance-worker-02
```

他看到反覆出現的事件：

```
Warning  DrainError  Cannot evict pod as it would violate the pod's disruption budget.
```

又是 PDB。這次是 `vm-order-processing` 這個 VM——客戶設了 PDB，要求隨時至少要有一個 replica 在跑（即使只有一個 replica）。

阿明翻了 NMO 的文件，發現 NMO 遇到 PDB 阻擋時會持續 retry，**不會強制跳過**。這個設計是刻意的——PDB 是應用程式擁有者聲明的可用性需求，NMO 尊重這個聲明，不會在沒有明確授權的情況下繞過它。

*那怎麼辦？*

他找到幾個選項：

**選項 A**：等 VM 自己遷移完成。如果這個 VM 是 KubeVirt `VirtualMachine`（不是裸 VMI），它應該有辦法做 Live Migration 到其他節點。但他確認了一下，這個 VM 沒有設定 `evictionStrategy: LiveMigrate`，所以無法自動遷移。

**選項 B**：手動觸發 Live Migration。他可以建立一個 `VirtualMachineInstanceMigration` CR，讓 KubeVirt 把這個 VM 遷移到其他節點，然後 NMO 就能繼續驅逐了。

**選項 C**：跟應用程式負責人溝通，在維護視窗期間暫時刪除或放寬 PDB。

阿明選了選項 B——手動觸發 Migration。

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstanceMigration
metadata:
  name: migrate-vm-order-processing
  namespace: kubevirt-system
spec:
  vmiName: vm-order-processing-xxxxx
```

Migration 完成後，那個 VM 跑到了 `node-worker-05`。幾分鐘後，NMO 成功驅逐了 Pod，`drainProgress` 恢復推進，最終 `phase` 變成了 `Succeeded`。

*原來 NMO 和 KubeVirt 要搭配使用，才能讓 VM workload 真的做到不中斷維護。*

---

> ### 📚 去這裡深入了解
> PDB 是節點維護最常遇到的障礙，這裡可以深入了解排空的完整邏輯：
>
> - [節點排空工作流程](/node-maintenance-operator/node-drainage-process) — PDB 處理邏輯、retry 機制與排空超時設定
>
> 讀完後，你應該能說明：NMO 遇到 PDB 阻擋時，會採取什麼行動？為什麼不強制跳過？

---

## 第五章：「Taint 管理：節點維護期間的隔離標記」

在處理第三個節點時，阿明注意到一件事：他 apply `NodeMaintenance` 之後，節點不只是 cordon 了——它還多了一個 taint：

```bash
kubectl describe node node-worker-03 | grep Taint
```

```
Taints: node.kubernetes.io/unschedulable:NoSchedule
        medik8s.io/drain=draining:NoSchedule
```

他看到兩個 taint：
- `node.kubernetes.io/unschedulable:NoSchedule` — 這是 cordon 時 K8s 標準加上的
- `medik8s.io/drain=draining:NoSchedule` — 這是 NMO 自己加的

*為什麼 NMO 要加自己的 taint？光是 cordon 不夠嗎？*

他查了文件，理解了設計原因：cordon（`unschedulable`）只影響 **scheduler**，阻止新 Pod 被調度上去。但有些元件不走 scheduler——比如 `DaemonSet` Controller 在某些情況下，或是直接 `kubectl apply` 帶有 `nodeName` 的 Pod——這些不會被 cordon 攔下。

Taint 則更徹底：任何 Pod，只要沒有對應的 `toleration`，就無法在這個節點上執行。NMO 的 taint `medik8s.io/drain=draining:NoSchedule` 確保：在節點整個維護過程中，不會有任何「意外的」Pod 跑上來。

更重要的是，這個 taint 是 NMO 管理的——當你刪掉 `NodeMaintenance` CR，NMO 的 Reconcile loop 會自動移除這個 taint，同時 uncordon 節點。你不需要手動清理。

阿明想到他之前手動 drain 的情況：他 drain 完之後，要記得自己 uncordon，還要注意有沒有 taint 要清理。*現在這些都由 NMO 的 CR 生命週期管理了，刪掉 CR 就等於完成維護並恢復節點，乾淨俐落。*

他試著刪掉一個已完成的 `NodeMaintenance`：

```bash
kubectl delete nodemaintenance maintenance-worker-01
```

幾秒後確認：

```bash
kubectl describe node node-worker-01 | grep Taint
# (空白)

kubectl get node node-worker-01
# NAME             STATUS   ROLES    AGE   VERSION
# node-worker-01   Ready    <none>   45d   v1.27.3
```

taint 消失了，`SchedulingDisabled` 也消失了——節點完全恢復正常。

---

> ### 📚 去這裡深入了解
> NMO 的 taint 管理策略與 cordon 的差異：
>
> - [Taint 管理與 Cordoning](/node-maintenance-operator/taints-and-cordoning) — NMO 加的 taint 是什麼、為什麼需要它、生命週期如何管理
>
> 讀完後，你應該能解釋：taint 和 cordon 在阻止 Pod 調度上的差異是什麼？

---

## 第六章：「Lease 機制：為什麼不能同時維護多個節點？」

進入第二週，阿明被分配了一個「效率優化」任務：機房同時要換 5 台節點的記憶體，他想看能不能同時啟動 5 個 `NodeMaintenance`，這樣維護時間可以縮短到原本的五分之一。

他建立了 5 個 CR，但很快發現奇怪的事：只有第一個 CR 的 `phase` 進到了 `Running`，其他四個全部停在 `Pending`。

他查 Events：

```bash
kubectl get events --field-selector reason=BlockedByNodeHealthCheck
```

看到訊息：

```
Waiting to acquire lease for node maintenance. Other maintenance or node health check is in progress.
```

*Lease？什麼是 Lease？*

阿明翻了文件，理解了這個設計。NMO 使用 Kubernetes 的 `Lease` 資源（`coordination.k8s.io/v1`）來實作**分散式協調鎖**。在同一時間，只有一個節點能持有這個 Lease 進行維護。

這個設計的原因是**保護 cluster 的可用性**。假設你有 3 個 master node 和 5 個 worker node，如果允許同時 drain 多個節點：
- etcd quorum 可能被打破（如果多個 control-plane 節點同時下線）
- worker 節點數量驟降，還在跑的 Pod 可能沒有足夠的節點可以調度
- 已被驅逐的 Pod 無法找到新家，workload 中斷

NMO 的 Lease 機制確保了**序列化的維護流程**：一次只維護一個節點，前一個維護完成（或被取消）後，Lease 才釋放，下一個等待中的 `NodeMaintenance` 才能開始。

更有趣的是，這個 Lease 不只是 NMO 自己用。它是 **medik8s ecosystem** 共享的協調機制——**Node Health Check（NHC）** operator 也會在修復節點時取得這個 Lease。這意味著 NMO 和 NHC 不會互相衝突：如果 NHC 正在修復某個故障節點，NMO 就知道要等一等，不會同時把另一個節點也下線。

阿明想到如果沒有這個機制會怎樣：*NHC 正在修復 node-05（因為它 NotReady 了），同時我又手動維護 node-06 和 node-07，cluster 可能瞬間少掉 3 個節點，某些 Pod 完全沒地方跑。*

他調整了計畫：不強求同時做 5 台，接受 NMO 的序列化流程，讓它一台一台來。雖然時間比較長，但安全多了。

---

> ### 📚 去這裡深入了解
> Lease 協調機制的技術細節：
>
> - [Lease 分散式協調](/node-maintenance-operator/lease-based-coordination) — Lease 資源的結構、NMO 如何與 NHC 共享協調鎖、等待與超時機制
>
> 讀完後，你應該能說明：為什麼 NMO 要用 Lease 而不是直接允許並行維護？

---

## 第七章：「OpenShift etcd 保護：control-plane 節點不能隨便下線」

阿明的 cluster 是跑在 OpenShift 上的。當他試著對一個 control-plane 節點建立 `NodeMaintenance` 時，CR 停在 `Pending` 很久，Events 出現了他看不懂的訊息：

```
etcd quorum is not maintained when node node-master-02 is remediated
```

*etcd quorum？*

他查了文件，理解了 OpenShift 版本 NMO 的特殊保護機制。OpenShift 的 control-plane 節點跑著 etcd cluster，etcd 是 K8s 所有狀態的儲存後端。etcd 使用 Raft consensus 協議，需要多數節點（quorum）才能正常運作：

- 3 個 etcd 節點：需要至少 2 個健康
- 5 個 etcd 節點：需要至少 3 個健康

如果你在一個 3 個 master 的 cluster 裡，有一個 master 已經 NotReady（比如硬體故障），這時再讓另一個 master 進入維護下線，etcd 就只剩 1 個節點——quorum 被打破，整個 cluster 的 API server 可能停擺。

NMO 的 etcd quorum 保護機制會在讓 control-plane 節點進入維護**之前**，先向 OpenShift 的 `MachineHealthCheck` API 查詢當前 etcd 的健康狀態。只有在確認 etcd quorum 仍然安全的情況下，維護才被允許繼續。

阿明看了一下他的 cluster：`node-master-01` 最近的確有些不穩定，偶爾出現 NotReady。NMO 正是因為偵測到這個狀況，才阻止他讓 `node-master-02` 進入維護。

*如果沒有這個保護，我可能真的會把 etcd 打掛，整個 cluster 就完蛋了。*

他等 `node-master-01` 恢復健康，觀察了幾分鐘確認穩定後，`NodeMaintenance` 的狀態自動從 `Pending` 進入了 `Running`——NMO 持續在 retry，等到條件滿足就自動繼續，不需要他手動重試。

---

> ### 📚 去這裡深入了解
> etcd quorum 保護的實作細節：
>
> - [系統架構](/node-maintenance-operator/architecture) — NMO 在 OpenShift 環境的特殊邏輯，包括 etcd quorum 驗證的觸發條件
>
> 讀完後，你應該能解釋：什麼情況下 NMO 會阻止 control-plane 節點進入維護？

---

## 第八章：「Webhook 驗證：試著做壞事，NMO 怎麼擋」

維護工作順利進行到第三週。某天，阿明的同事 Brian 試著做一個「快捷操作」——他想直接修改一個已存在的 `NodeMaintenance` CR，把 `spec.nodeName` 改成另一個節點：

```bash
kubectl patch nodemaintenance maintenance-worker-05 \
  --type=merge \
  -p '{"spec":{"nodeName":"node-worker-07"}}'
```

立刻收到錯誤：

```
Error from server (Forbidden): admission webhook "nodemaintenance-validation.medik8s.io" denied the request:
  nodeName is immutable and cannot be changed after creation
```

Brian 轉頭問阿明：「這個 webhook 是什麼？」

阿明翻了文件，解釋給他聽：NMO 部署了一個 **Admission Validation Webhook**——當你對 `NodeMaintenance` CR 發出建立或更新請求時，API server 會先把請求轉發給這個 webhook，由它決定是否允許。

這個 webhook 做了幾件事：

**建立時驗證**：
- `spec.nodeName` 是否對應到 cluster 裡真實存在的節點？
- 這個節點是否已經有另一個 `NodeMaintenance` 在進行中？

**更新時驗證**：
- `spec.nodeName` 不可變更（immutable）——一旦你決定要維護哪個節點，就不能改變。如果要維護不同節點，必須建立新的 CR。

Brian 想了想：「那我可以繞過 webhook 直接改 etcd 嗎？」

阿明搖搖頭：「你不應該直接改 etcd——那是 K8s 的大忌。而且即使你改了，NMO 的 Reconcile loop 也會根據 CR 的 `spec.nodeName` 去操作節點，你可能會造成狀態不一致。」

*這個 webhook 的存在，讓很多潛在的操作錯誤在進入系統之前就被擋下來了。* 阿明覺得這個設計很好——與其讓錯誤的操作進去 etcd 再想辦法回滾，不如在入口處就把關。

他還試了另一個測試：試著對一個不存在的節點名稱建立 `NodeMaintenance`：

```yaml
spec:
  nodeName: node-that-does-not-exist
```

同樣被 webhook 擋住：

```
Error from server: node "node-that-does-not-exist" not found in cluster
```

*這讓我想到如果沒有 webhook，這個 CR 會安靜地進到 etcd，然後 NMO 的 Reconcile loop 在找不到節點時一直 error、一直 retry，既不報錯又什麼都不做。Webhook 讓錯誤快速失敗（fail fast）。*

---

> ### 📚 去這裡深入了解
> Webhook 的驗證邏輯完整說明：
>
> - [Admission Validation](/node-maintenance-operator/validation-webhooks) — webhook 的驗證規則、不可變欄位清單、錯誤訊息對照
>
> 讀完後，你應該能列舉：NMO Admission Webhook 會驗證哪些規則？

---

## 第九章：「可觀測性：當維護卡住了，怎麼診斷？」

三週的節點維護工作接近尾聲，阿明回顧了整個過程，整理出一份「診斷 checklist」——當 `NodeMaintenance` 的 `phase` 停住不動時，他學到怎麼系統性地找到原因。

**第一步：看 CR 的 status**

```bash
kubectl describe nodemaintenance <name>
```

`status.pendingPods` 告訴你哪些 Pod 還沒被驅逐，`status.drainProgress` 告訴你整體進度。如果 `pendingPods` 一直有同一個 Pod，問題就在那個 Pod 上。

**第二步：看 Events**

```bash
kubectl get events --field-selector involvedObject.name=<maintenance-name> --sort-by='.lastTimestamp'
```

Events 記錄了 NMO 的每一個重要操作：開始 cordon、開始驅逐、遇到 PDB、獲得 Lease、釋放 Lease。阿明建立了一個習慣：遇到問題先看 Events，大部分情況都能在這裡找到線索。

**第三步：看 NMO controller 的 logs**

```bash
kubectl logs -n node-maintenance-operator-system \
  deployment/node-maintenance-operator-controller-manager \
  -c manager --since=10m
```

controller 的 log 是最詳細的診斷來源，會顯示每次 Reconcile 的決策邏輯。阿明用 `--since=10m` 避免輸出太多，搭配 `grep` 過濾有興趣的節點名稱。

**第四步：確認 Lease 狀態**

```bash
kubectl get lease -n node-maintenance-operator-system
```

如果 `phase` 停在 `Pending`，通常是因為 Lease 被其他操作持有。看 Lease 的 `holderIdentity` 就能知道是哪個維護在進行。

**第五步：確認節點的 taint 和狀態**

```bash
kubectl describe node <node-name> | grep -A5 Taint
kubectl get node <node-name>
```

有時候 NMO 已經完成了部分工作（cordon 和 taint 已加），但 drain 卡住了。確認節點狀態有助於判斷進行到哪個步驟。

---

阿明把這份 checklist 整理成文件，分享給整個 Platform Team。他回顧三週的維護工作：22 個節點，全部順利完成，零 VM 中斷（除了那一次 PDB 事件，但有 Live Migration 解決了）。

*一開始我以為節點維護就是跑個 kubectl drain 的事，沒想到背後涉及這麼多機制——狀態機、Taint、Lease、etcd quorum 保護、Webhook 驗證。每一層都有它存在的理由。*

他覺得，理解這些機制讓他不只是「會用 NMO」，而是在出問題時知道要去哪裡找原因、知道每個設計決策背後的考量。這才是真正的掌握一個工具。

---

> ### 📚 去這裡深入了解
> NMO 的可觀測性工具與故障排除完整指南：
>
> - [事件與可觀測性](/node-maintenance-operator/event-recording-and-observability) — Events 的種類、記錄時機與查詢方法
> - [故障排除與 Debugging](/node-maintenance-operator/troubleshooting-and-debugging) — 常見問題、診斷步驟與解法對照
>
> 讀完後，你應該能說明：`NodeMaintenance` 的 `phase` 停住時，診斷的標準步驟是什麼？

---

## 尾聲：阿明寫給下一個接手的人

三週維護結束後的下午，阿明在公司的 Wiki 開了一頁新文件，標題：「節點維護 SOP：使用 NMO」。

他寫下了整個流程，但最後加了一段話：

> 這份 SOP 告訴你**怎麼做**。但如果你想知道**為什麼這樣設計**——為什麼不能同時維護多個節點、為什麼 control-plane 節點有額外保護、為什麼 NMO 不強制跳過 PDB——我建議你讀一遍 NMO 的技術文件。
>
> 真正理解一個工具，不只是會用它，而是在它出問題的時候，你知道要看哪裡。

他關上電腦，去喝了一杯還沒涼的咖啡。

---

::: info 📚 完整技術文件
- [專案總覽](/node-maintenance-operator/) — 重新看一遍，現在你會有不同的視角
- [系統架構](/node-maintenance-operator/architecture) — Reconcile 流程完整圖解
- [部署與設定](/node-maintenance-operator/installation-and-deployment) — 如何在新 cluster 安裝 NMO
- [NodeMaintenance CRD 規格](/node-maintenance-operator/crd-specification) — 所有欄位的完整參考
- [節點排空工作流程](/node-maintenance-operator/node-drainage-process) — 排空邏輯深入解析
- [Taint 管理與 Cordoning](/node-maintenance-operator/taints-and-cordoning) — 隔離機制詳解
- [Lease 分散式協調](/node-maintenance-operator/lease-based-coordination) — 協調鎖的實作
- [Admission Validation](/node-maintenance-operator/validation-webhooks) — Webhook 驗證規則
- [RBAC 與權限](/node-maintenance-operator/rbac-and-permissions) — 誰有權限建立 NodeMaintenance
- [事件與可觀測性](/node-maintenance-operator/event-recording-and-observability) — 監控維護過程
- [故障排除與 Debugging](/node-maintenance-operator/troubleshooting-and-debugging) — 遇到問題時的參考手冊
:::
