---
layout: doc
title: Ceph — RBD 塊存儲
---

# Ceph — RBD 塊存儲

::: tip 核心概念
RBD（RADOS Block Device）不是把磁碟直接存進單一檔案，而是把 image 切成大量 objects，散佈在同一個 RADOS pool 內。這也是它能同時取得擴充性、快照、clone 與鏡像能力的原因。
:::

## RBD 架構：image 其實是很多 objects

RBD 的核心想法是把「看起來像一顆 block device 的 image」映射為：

```text
// 檔案: docs-site/ceph/rbd.md
RBD image
├── metadata/header objects
├── data objects (striped by order / stripe_unit / stripe_count)
└── optional journal / object-map / snapshot metadata
```

因此：

- image 的容量擴充不需要傳統 LVM 那種集中式 metadata 鎖
- snapshot / clone 可以建立在 object 層級的 copy-on-write
- mirror / journal 也能以 object 變更為基礎複製

## `librbd` API 與 `ImageCtx`

RBD 對外 API 定義在 `src/include/rbd/librbd.hpp`，而內部最重要的狀態容器之一是 `src/librbd/ImageCtx.h` 的 `struct ImageCtx`。

```cpp
// 檔案: ceph/src/librbd/ImageCtx.h
struct ImageCtx {
  librados::IoCtx data_ctx;
  librados::IoCtx md_ctx;
  ImageWatcher<ImageCtx> *image_watcher;
  Journal<ImageCtx> *journal;
  Operations<ImageCtx> *operations;
  uint64_t size;
  uint64_t features;
  std::string object_prefix;
  uint64_t stripe_unit, stripe_count;
  std::unique_ptr<crypto::EncryptionFormat<ImageCtx>> encryption_format;
};
```

從這個結構可以直接看出 RBD 的幾個事實：

- 它同時管理 **data** 與 **metadata** 的 `IoCtx`
- snapshot、watch、journal、operations 都掛在同一個 image context 上
- image feature（例如 object-map、exclusive-lock、journaling）會影響整個 I/O 路徑

## `librbd.hpp`：建立、快照、clone 與 mirror

`librbd` 對外暴露的 API 很完整，從建立 image 到快照、clone、鏡像都有對應介面。

```cpp
// 檔案: ceph/src/include/rbd/librbd.hpp
int create(IoCtx& io_ctx, const char *name, uint64_t size, int *order);
int clone(IoCtx& p_ioctx, const char *p_name, const char *p_snapname,
          IoCtx& c_ioctx, const char *c_name, uint64_t features,
          int *c_order);

int encryption_format(encryption_format_t format, encryption_options_t opts,
                      size_t opts_size);
int snap_create(const char *snapname);
int snap_remove(const char *snapname);
int snap_protect(const char *snap_name);
int mirror_image_enable2(mirror_image_mode_t mode);
int mirror_image_promote(bool force);
```

## RBD 的重要功能

### 1. Snapshot 與 Cloning

RBD 典型工作流是：

1. 先建立 image
2. 建立 snapshot
3. 將 snapshot protect
4. 由 snapshot clone 出子 image

這種模型非常適合 VM 黃金映像（golden image）與大量快速佈建。

### 2. Encryption

`ImageCtx` 內含 `encryption_format`，而 `librbd.hpp` 提供 `encryption_format()` / `encryption_load()`，表示加密不是額外外掛，而是 image feature 與開啟流程的一部分。

### 3. Mirroring

`librbd.hpp` 同時有 pool-level 與 image-level mirroring API，例如 `mirror_mode_set()`、`mirror_peer_site_add()`、`mirror_image_enable2()` 與 `mirror_image_promote()`。

::: info 災難復原觀點
RBD mirroring 的目標不是單純備份，而是跨叢集保留可接手的 image 狀態。promotion / demotion API 反映了 primary / secondary 角色切換的需求。
:::

### 4. Journaling

`ImageCtx` 直接持有 `Journal<ImageCtx>*`，而 `src/librbd/Operations.h` 中多個操作都帶有 `journal_op_tid` 參數，代表 journal 並不是附屬功能，而是寫入流程中的核心序列化點之一。

```cpp
// 檔案: ceph/src/librbd/Operations.h
class Operations {
public:
  void execute_resize(uint64_t size, bool allow_shrink, ProgressContext &prog_ctx,
                      Context *on_finish, uint64_t journal_op_tid);
  void execute_snap_create(const cls::rbd::SnapshotNamespace &snap_namespace,
                           const std::string &snap_name, Context *on_finish,
                           uint64_t journal_op_tid, uint64_t flags,
                           ProgressContext &prog_ctx);
};
```

搭配 `doc/rbd/rbd-mirroring.rst` 的說明可知，**journal-based mirroring** 會先把每次寫入記錄到 journal，再由遠端叢集重播，提供 point-in-time、crash-consistent 複寫基礎。

## I/O 路徑：`src/librbd/io/`

`src/librbd/io/` 目錄展示 RBD 的 I/O 已拆成多層 dispatcher / request / completion 結構，例如：

- `IoOperations.*`
- `ImageRequest.*`
- `ObjectRequest.*`
- `AioCompletion.*`
- `ImageDispatcher.*`
- `ObjectDispatcher.*`

這個分層讓 RBD 能把 cache、QoS、refresh、copyup、object dispatch 等行為插入同一條 I/O pipeline，而不是全部塞進單一 read/write 函式。

## Kubernetes：透過 CSI 暴露為 PV

Ceph 官方文件 `doc/rbd/rbd-kubernetes.rst` 說明，Kubernetes 會透過 `ceph-csi` 動態建立與掛載 RBD image。換句話說：

- Ceph 端負責提供 RBD image 與 pool
- CSI 端負責 provisioning、attach / map、Secret 與 StorageClass 串接
- Pod 最終看到的是 block device 或格式化後的檔案系統

這也是雲原生環境裡最常見的 Ceph block storage 消費模式。

## QEMU / KVM：虛擬機最常見的上層整合

`doc/rbd/qemu-rbd.rst` 直接指出，QEMU 可透過 `librbd` 直接掛載 RBD image，避免先在 host 映射成本地 block device。這使得：

- VM 磁碟可直接放在 Ceph
- snapshot / clone 非常適合 golden image 派生
- 常見虛擬裝置型態會落在 `virtio-blk` 或 `virtio-scsi` 路徑上，由 hypervisor 對 guest 暴露塊裝置

::: warning 實作邊界
`virtio-blk` / `virtio-scsi` 是 QEMU/KVM 對 guest 暴露裝置的方式，不是 Ceph 原始碼本身的類別；Ceph 這一側主要提供的是 `librbd` 與 image lifecycle。
:::

## 關鍵原始碼參考

- `ceph/src/librbd/ImageCtx.h`
- `ceph/src/include/rbd/librbd.hpp`
- `ceph/src/librbd/Operations.h`
- `ceph/src/librbd/io/`
- `ceph/doc/rbd/rbd-mirroring.rst`
- `ceph/doc/rbd/rbd-kubernetes.rst`
- `ceph/doc/rbd/qemu-rbd.rst`

::: info 相關章節
- 想先了解 object store 基礎，請參閱 [RADOS 物件存儲 & librados](./rados)
- 想看 CephFS 如何把 metadata 與 data 分流，請參閱 [CephFS 分散式文件系統](./cephfs)
- 想看 object API 對外如何變成 S3 / Swift，請參閱 [RADOS Gateway](./rgw)
:::
