---
layout: doc
title: Ceph — CephFS 分散式文件系統
---

# Ceph — CephFS 分散式文件系統

::: tip 一句話理解
CephFS = **data 放在 RADOS**，**metadata 交給 MDS**。它不是獨立儲存後端，而是建立在 Ceph 既有 object store 上的 POSIX-like 分散式檔案系統。
:::

## 架構：data 與 metadata 分治

CephFS 的資料面與 metadata 面是分開設計的：

```text
// 檔案: docs-site/ceph/cephfs.md
Application / libcephfs / kernel client
                |
                v
        +---------------+
        |      MDS      |  <--- inode / dentry / subtree / caps / quota
        +---------------+
                |
                v
        +---------------+
        |     RADOS     |  <--- file data objects in data pools
        +---------------+
```

這種拆分讓 CephFS 能同時保有：

- 檔案內容的大規模水平擴充
- metadata hot path 的獨立優化
- 多 MDS 的平行擴展空間

## POSIX 相容性定位

官方文件 `doc/cephfs/posix.rst` 說明 CephFS 盡量遵守 POSIX semantics，尤其重視多 client 間的 cache coherency；但在跨 object 邊界的同時寫入、mmap coherency、`atime` 等細節上，仍有刻意放寬或限制。

::: warning 不要把「POSIX-compliant」理解成完全等同本地檔案系統
CephFS 的目標是讓大多數應用能以接近 POSIX 的方式運作，但在極端一致性與部分 atomicity 場景，仍需理解其分散式代價。
:::

## `libcephfs` client 與 `Client` 類別

使用者空間 client 的核心實作可從 `src/client/Client.h` 切入。`class Client` 提供 mount、unmount、目錄操作、stat、readdir 與 MDS command 等能力。

```cpp
// 檔案: ceph/src/client/Client.h
class Client : public Dispatcher, public md_config_obs_t {
public:
  int mount(const std::string &mount_root, const UserPerm& perms,
            bool require_mds=false, const std::string &fs_name="");
  void unmount();
  int statfs(const char *path, struct statvfs *stbuf, const UserPerm& perms);
  int opendir(const char *name, dir_result_t **dirpp, const UserPerm& perms);
  int readdir_r(dir_result_t *dirp, struct dirent *de);
};
```

這表示 `libcephfs` 並不是薄薄一層 syscall wrapper，而是有完整 client state machine、cache、session 與 MDS 溝通邏輯的使用者空間實作。

## MDS：metadata 熱點的控制中心

`src/mds/MDSRank.h` 可看出單一 MDS rank 的生命週期與 active 狀態管理。

```cpp
// 檔案: ceph/src/mds/MDSRank.h
bool is_active() const { return state == MDSMap::STATE_ACTIVE; }
bool is_stopping() const { return state == MDSMap::STATE_STOPPING; }
void wait_for_active(MDSContext *c) {
  waiting_for_active.push_back(c);
}
```

### 多個 active MDS

`doc/cephfs/multimds.rst` 指出 CephFS 可透過 `max_mds` 啟用多個 active MDS，以分攤 metadata workload。這對大量 client、目錄層級廣、metadata request 密集的工作負載特別重要。

### Subtree pinning

同一份文件也描述了 `ceph.dir.pin` 的 subtree pinning 機制，可把特定目錄樹固定交由某個 rank 處理，以避免熱門 subtree 在 MDS 間來回漂移。

## `CDir` / `CDentry`：目錄與目錄項目管理

`CDir` 與 `CDentry` 展示 CephFS metadata cache 內部如何管理 pin、subtree 與 auth 狀態。

```cpp
// 檔案: ceph/src/mds/CDir.h
static const unsigned STATE_STICKY =     (1<<13);
static const unsigned STATE_AUXSUBTREE = (1<<19);
bool is_subtree_root() const {
  return get(PIN_SUBTREE) > 0;
}
mds_rank_t get_export_pin(bool inherit=true) const;
```

```cpp
// 檔案: ceph/src/mds/CDentry.h
static const int PIN_INODEPIN = 1;
bool can_auth_pin(int *err_ret=nullptr) const override;
void auth_pin(void *by) override;
void auth_unpin(void *by) override;
```

從這些型別可以看出：

- subtree 與 pin 不是管理命令層的小功能，而是 MDS cache / authority 模型的一部分
- dentry、inode、dir fragment 的 pin 直接影響 metadata ownership 與遷移

## Quota

`doc/cephfs/quota.rst` 說明 CephFS quota 是透過虛擬 xattr 設定：

- `ceph.quota.max_files`
- `ceph.quota.max_bytes`

它可以套在任意目錄上，因此很適合搭配 tenant 目錄、subvolume 或 home directory 管理容量與檔案數量。

## CephFS volumes 與 subvolumes

CephFS 不只是一個 mountable filesystem，`doc/cephfs/fs-volumes.rst` 也定義了管理層抽象：

- **FS volume**：CephFS filesystem 抽象
- **subvolume group**：比 subvolume 高一層的管理單位
- **subvolume**：獨立的目錄樹，可被 CSI / Manila 等上層消費

這一層通常由 `ceph-mgr` 的 `volumes` 模組負責，讓管理者可以把 CephFS 當成可供應租戶或 workload 的 export service，而不只是手動建目錄。

::: info 實務意義
當你看到 CephFS CSI、Manila 或租戶隔離場景時，常常真正被 provisioning 的不是「整個檔案系統」，而是某個 subvolume。
:::

## 關鍵原始碼參考

- `ceph/src/client/Client.h`
- `ceph/src/mds/MDSRank.h`
- `ceph/src/mds/CDir.h`
- `ceph/src/mds/CDentry.h`
- `ceph/doc/cephfs/posix.rst`
- `ceph/doc/cephfs/multimds.rst`
- `ceph/doc/cephfs/quota.rst`
- `ceph/doc/cephfs/fs-volumes.rst`

::: info 相關章節
- 想先理解底層 object store，請參閱 [RADOS 物件存儲 & librados](./rados)
- 想看 block image 如何以 object 形式儲存，請參閱 [RBD 塊存儲](./rbd)
- 想看 object gateway 如何對外提供 HTTP 介面，請參閱 [RADOS Gateway](./rgw)
:::
