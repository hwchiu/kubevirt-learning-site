---
layout: doc
title: etcd — Learner Mode
---

# etcd — Learner Mode

## Learner 是什麼

Learner 是 **Raft non-voting member**。從型別定義看，etcd 直接把它當成 member 的一個 raft 屬性：

```go
// 檔案: etcd/server/etcdserver/api/membership/member.go
type RaftAttributes struct {
    PeerURLs []string `json:"peerURLs"`
    IsLearner bool `json:"isLearner,omitempty"`
}
```

新增 learner 時，不是先建一般 member 再切換旗標，而是直接走 `NewMemberAsLearner`：

```go
// 檔案: etcd/server/etcdserver/api/membership/member.go
func NewMemberAsLearner(...) *Member {
    return newMember(name, peerURLs, memberID, true)
}
```

## 為什麼需要 Learner

Learner 的核心價值是：**先同步資料，再加入投票**。這樣做可以避免新節點剛加入時就立刻改變 quorum 結構，降低擴容或替換節點時的風險。

CLI 也把這件事做成正式操作：

```go
// 檔案: etcd/etcdctl/ctlv3/command/member_command.go
cc.Flags().BoolVar(&isLearner, "learner", false, "indicates if the new member is raft learner")
```

![Learner Mode 的 quorum 與 standby member 架構](/diagrams/etcd/etcd-learner-1.png)

## 架構視角：為什麼 primary/standby 需要 learner

如果從架構角度看，不要先把 learner 想成「功能旗標」，而要把它想成 **membership 變更時的緩衝層**。

在一個標準 3-member etcd primary cluster 中，正常狀態大致如下：

```text
                +---------------------+
                |   Leader (voter)    |
                +---------------------+
                   /               \
                  / raft log        \ raft log
                 / replication       \
                v                     v
      +------------------+   +------------------+
      | Follower (voter) |   | Follower (voter) |
      +------------------+   +------------------+

Quorum = 2 / 3
```

這個架構的核心特性是：

- leader 負責接收寫入並複寫 raft log
- voting members 共同構成 quorum
- 任何 membership 變動都會影響 quorum 計算與容錯邊界

### 問題出在「新節點還沒追上資料，卻已經算進 quorum」

如果沒有 learner，直接把新節點當成 voting member 加入，架構上會立刻變成：

```text
                +---------------------+
                |   Leader (voter)    |
                +---------------------+
                 /        |          \
                /         |           \
               v          v            v
      +------------------+   +------------------+   +----------------------+
      | Follower (voter) |   | Follower (voter) |   | New Member (voter)   |
      +------------------+   +------------------+   +----------------------+
                                                       data still catching up

Quorum = 3 / 4
```

這時候風險不在於「新節點不存在」，而在於：

- quorum 已經從 `2/3` 變成 `3/4`
- 但新節點可能還在吃 snapshot、補 raft log、做磁碟初始化
- 也就是說，**容錯門檻先提高了，資料同步卻還沒完成**

這正是 learner 要解決的架構問題。

### learner 的作用：先同步，不先改變投票面

加入 learner 後，架構會更接近下面這種狀態：

```text
                +---------------------+
                |   Leader (voter)    |
                +---------------------+
                 /        |          \
                /         |           \
               v          v            v
      +------------------+   +------------------+   +----------------------+
      | Follower (voter) |   | Follower (voter) |   | Learner (non-voter)  |
      +------------------+   +------------------+   +----------------------+
                                                       sync snapshot/log

Quorum = still 2 / 3
```

這時 learner 的架構價值就很清楚：

- 它能先接收 leader 的 snapshot 與 raft log
- 它不會立刻參與投票
- 它不會立刻把 quorum 從 `2/3` 改成 `3/4`
- 等它真正追上後，才進入 promote 流程

所以 learner 的核心不是「多一台複本」，而是**把資料同步階段與投票成員變更階段拆開**。

## 為什麼這對 primary/standby 思維特別重要

很多人談 primary/standby etcd 時，直覺會用資料庫的主備模型理解：

- primary 負責服務
- standby 持續追資料
- primary 掛掉後 standby 接手

但 etcd 不是傳統單主資料庫複寫模型，而是 **Raft membership 模型**。在這個模型下，真正重要的是：

- 哪些節點算進 quorum
- 哪些節點只做同步、不影響投票
- 何時可以安全地把同步節點升格成 voting member

因此在 etcd 裡，比較精確的說法不是「primary cluster + standby cluster」，而是：

- **primary cluster**
- **cluster 內的 standby member（learner）**

也就是說，learner 解決的是 **cluster membership transition** 問題，不是 **cross-cluster disaster recovery replication** 問題。

## 從架構上看，learner 解決了哪三個風險

### 1. Quorum 先變大，資料還沒追平

這是最直接的風險。沒有 learner，新增節點會先改變 voting topology；有 learner，則先保持原 quorum，直到新節點 ready。

### 2. 替換故障節點時，把不穩定節點直接放進投票面

在 Kubernetes control plane 替換節點時，新節點通常同時要面對：

- 磁碟初始化
- 網路與憑證設定
- snapshot 載入
- raft log catch-up

learner 讓這一段初始化成本先發生在 non-voting 狀態，而不是直接污染 voting path。

### 3. 把「同步完成」和「升格為投票成員」綁成同一步

這是架構設計上很常見的反模式。learner 模式把流程拆成兩步：

1. 資料同步
2. membership promote

拆開後，系統可以在 promote 前明確檢查：

- learner 是否真的 in sync with leader
- promote 後 quorum 是否仍安全

這也正對應 `IsReadyToPromoteMember` 與相關 error path 的存在理由。

## 什麼時候才能 Promote

etcd 不允許任意提升 learner。最重要的限制在錯誤定義與測試：

- `server/etcdserver/errors/errors.go`：`can only promote a learner member which is in sync with leader`
- `tests/integration/clientv3/cluster_test.go`：未啟動或未追上 leader 的 learner，`MemberPromote` 應失敗

此外，`RaftCluster.IsReadyToPromoteMember` 還會檢查 promote 之後的 quorum 是否安全：

```go
// 檔案: etcd/server/etcdserver/api/membership/cluster.go
nmembers := 1 // We count the learner to be promoted for the future quorum
nstarted := 1 // and we also count it as started.
nquorum := nmembers/2 + 1
if nstarted < nquorum {
    return false
}
```

這段邏輯的意思是：**就算 learner 已經同步完成，也不能讓 promote 把叢集推進不安全的 quorum 狀態**。

## Learner 有哪些限制

### 1. 不能在初始 bootstrap 時直接帶入

整合測試明確寫出：

```go
// 檔案: etcd/tests/integration/clientv3/kv_test.go
// bootstrapping a cluster with learner member is not supported.
```

所以 learner 是**既有叢集的擴容/替換機制**，不是初始建群配置。

### 2. 只接受 serializable read

`TestKVForLearner` 驗證 learner：

- `OpGet(..., WithSerializable())` 成功
- 一般 `Get` 失敗
- `Put` / `Delete` / `Txn` 都失敗

這代表 learner 不是 read-write member，也不是完整讀節點；它只提供有限的、非線性一致性讀取能力。

### 3. 不能成為 leader transfer 目標

`tests/integration/v3_leadership_test.go` 驗證把 leadership 轉給 learner 應該失敗。這與 non-voting 身份一致，因為 learner 不應承擔投票領導者角色。

### 4. 叢集可容納的 learner 數量可配置，但有限制

`server/embed/config.go` 定義了：

```go
// 檔案: etcd/server/embed/config.go
fs.IntVar(&cfg.MaxLearners, "max-learners", membership.DefaultMaxLearners, ...)
```

對應錯誤則在 `server/etcdserver/api/membership/errors.go`：

- `ErrTooManyLearners`

也就是說，learner 不是可以無限制堆疊的「觀察節點」。

## Kubernetes 場景下，Learner 最實用在哪裡

對 Kubernetes 維運最實際的用途有兩類：

1. **替換故障 control-plane 節點上的 etcd member**
2. **擴充 stacked / external etcd 叢集時，先同步再 promote**

這樣可以避免新 member 還沒追平 log，就立刻進入 voting set，降低直接改動 quorum 的風險。

## 能不能用 Learner 建立 primary 的 standby etcd cluster？

短答案：**不能直接建立獨立的 standby cluster**。Learner 模式能做的是建立 **同一個 etcd cluster 內的 warm standby member**，而不是另一套可獨立切換的 cluster。

這個結論是根據原始碼與測試行為整理出的推論：

1. `etcdctl member add --learner` 操作的是現有 cluster 的 membership，而不是建立第二個 cluster。這點可從 `etcdctl/ctlv3/command/member_command.go` 與 `server/etcdserver/api/membership/member.go` 看出來。
2. `NewMemberAsLearner` 只是把 `IsLearner=true` 寫進 member raft 屬性；它仍然屬於同一個 `RaftCluster`。
3. `tests/integration/clientv3/kv_test.go` 明確寫出 `bootstrapping a cluster with learner member is not supported`，代表 learner 不是用來初始化另一套 standby cluster。
4. `server/embed/config.go` 的 `max-learners` 與 membership error 中的 `ErrTooManyLearners`，也顯示 learner 是受控、過渡性的 cluster member，而不是長期跨站備援拓樸。

### 更精確的說法

Learner 適合的是：

- 在同一個 primary cluster 裡預先加入新節點
- 讓它先吃 snapshot / raft log
- 等追平 leader 後再 promote
- 最後替換掉舊 member 或完成安全擴容

Learner 不適合直接拿來做的是：

- 建立另一個獨立 cluster ID 的 standby etcd 叢集
- 讓另一個 cluster 持續以 learner 身份跟 primary 同步
- 在 primary 全掛時，直接把那個 cluster 無縫升格成 primary

如果硬要用架構圖來對比，可以這樣理解：

**Learner 能做的**

```text
Primary etcd cluster
  ├─ voter
  ├─ voter
  ├─ voter
  └─ learner   <- warm standby inside the same cluster
```

**Learner 不能直接做的**

```text
Primary etcd cluster          Standby etcd cluster
  ├─ voter                      ├─ voter
  ├─ voter        X             ├─ voter
  └─ voter                      └─ voter

No built-in "learner link" between two independent clusters
```

### 如果你要的是 DR standby cluster，應該怎麼理解 learner 的角色

從現有 etcd 原始碼來看，learner 比較像 **cluster 內的 warm spare**，不是 **cluster 外的 disaster recovery replica**。

所以若你的目標是跨機房或跨區域的 standby cluster，實務上通常要靠：

- 定期 snapshot / restore
- 備份同步
- 在災難時重新 bootstrap 新 cluster

這部分不是 learner membership 直接提供的能力。這是根據目前 membership API、bootstrap 限制與測試行為得到的推論。

### 可以怎麼把 learner 用在「接近 standby」的場景

對 primary cluster 來說，一個實用流程是：

1. 對現有 primary cluster 執行 `member add --learner`
2. 啟動新節點，讓它追上 leader
3. 驗證 learner 已 ready，並滿足 `MemberPromote` 條件
4. promote 成 voting member
5. 若目標是替換舊節點，再移除舊 member

這是一種**滾動替換 / 安全擴容**模型，本質上是在同一個 cluster 內預先準備 standby capacity，而不是建立另一個 standby cluster。

## 團隊應該記住的心智模型

Learner 不是「便宜版 member」，而是**加入 voting set 之前的安全緩衝區**：

- 可以先吃 snapshot / raft log
- 不參與投票
- 不接受一般寫入
- 追上 leader 後才考慮 promote

::: info 相關章節
- [為什麼需要 Defrag](./defrag)
- [Kubernetes 中的 Defrag 操作](./kubernetes-defrag)
:::
