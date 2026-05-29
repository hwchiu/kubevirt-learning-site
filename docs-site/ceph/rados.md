---
layout: doc
title: Ceph — RADOS 物件存儲 & librados
---

# Ceph — RADOS 物件存儲 & librados

::: tip 核心定位
RADOS（Reliable Autonomic Distributed Object Store）是 Ceph 的核心分散式物件存儲層。RBD、CephFS 與 RGW 都不是繞過 RADOS，而是建立在它提供的 pool、object、replication / erasure coding、watch/notify 與一致性機制之上。
:::

## 為什麼 RADOS 是 Ceph 的基底

Ceph 將所有資料最終都拆成 object，交由 OSD 叢集保存。從 API 角度來看，應用程式不是直接面對「磁碟」或「檔案系統」，而是透過 `librados` 對 object 執行讀寫、比對、刪除、事件通知與非同步 I/O。

```text
// 檔案: docs-site/ceph/rados.md
pool
└── namespace
    └── object
        ├── data
        ├── xattrs / omap
        └── version / watch state
```

::: info 觀察重點
- **pool** 決定資料放在哪一組 RADOS namespace / placement policy 內
- **namespace** 提供同一 pool 內的邏輯隔離
- **object** 是最小資料操作單位
:::

## `librados` C++ API：從連線到 `IoCtx`

`src/include/rados/librados.hpp` 定義了 C++ 介面。實務上最常見的進入點是 `Rados` 與 `IoCtx`：

- `Rados`：代表叢集連線與 cluster-level 操作
- `IoCtx`：代表某個 pool 的操作上下文
- `ObjectWriteOperation` / `ObjectReadOperation`：可批次組裝 object 操作
- `AioCompletion`：非同步完成通知

```cpp
// 檔案: ceph/src/include/rados/librados.hpp
class CEPH_RADOS_API Rados
{
public:
  int init(const char * const id);
  int connect();
  int ioctx_create(const char *name, IoCtx &pioctx);
};
```

這裡的連線流程很直接：

1. `Rados::init()` 設定 client 身分
2. `conf_read_file()` / `conf_parse_argv()` 等讀入設定
3. `Rados::connect()` 建立與 monitor / cluster 的連線
4. `ioctx_create()` 取得特定 pool 的 `IoCtx`

::: warning C 與 C++ API 名稱差異
在 C++ API 中通常使用 `Rados::ioctx_create()`；其對應的底層 C API 名稱是 `rados_ioctx_create()`，宣告位於 `src/include/rados/librados.h`。
:::

## 物件操作模型：讀、寫、附加、刪除、CAS

`ObjectWriteOperation` 與 `ObjectReadOperation` 的設計重點，是讓多個動作可以組成單一 object transaction-like 請求並送往 OSD。

```cpp
// 檔案: ceph/src/include/rados/librados.hpp
class CEPH_RADOS_API ObjectWriteOperation : public ObjectOperation
{
public:
  void write(uint64_t off, const bufferlist& bl);
  void write_full(const bufferlist& bl);
  void append(const bufferlist& bl);
  void remove();
};

class CEPH_RADOS_API ObjectReadOperation : public ObjectOperation
{
public:
  void stat(uint64_t *psize, time_t *pmtime, int *prval);
  void read(size_t off, uint64_t len, bufferlist *pbl, int *prval);
};
```

另外，`ObjectOperation` 本身也支援條件式保護：

- `cmpext()`：比較 object 內容區段
- `cmpxattr()`：比較 xattr
- `assert_version()` / `assert_exists()`：做版本或存在性檢查

這類操作常被拿來實作 **CAS（compare-and-set）** 風格流程：先比對版本 / metadata，再決定是否提交寫入。

## 非同步 I/O：`AioCompletion`

RADOS 在高併發環境下大量依賴 AIO。`AioCompletion` 提供 callback、等待與回傳值查詢能力。

```cpp
// 檔案: ceph/src/include/rados/librados.hpp
struct CEPH_RADOS_API AioCompletion {
  int set_complete_callback(void *cb_arg, callback_t cb);
  int wait_for_complete();
  bool is_complete();
  int get_return_value();
  void release();
};
```

搭配 `IoCtx::aio_write_full()`、`aio_append()`、`aio_remove()`、`aio_cmpext()` 等 API，可把 object I/O 與上層事件迴圈整合，避免同步等待拖慢 client。

::: tip 為什麼重要
RBD、RGW 這類高吞吐元件都會把 RADOS AIO 當成基礎能力使用；`AioCompletion` 是上層非同步工作流與回呼鏈的重要接點。
:::

## Watches 與 Notifies

RADOS 不只是儲存層，也提供事件通知能力。`WatchCtx2`、`watch2()` 與 `notify2()` 讓 client 可以訂閱 object 狀態變更。

```cpp
// 檔案: ceph/src/include/rados/librados.hpp
class CEPH_RADOS_API WatchCtx2 {
public:
  virtual void handle_notify(uint64_t notify_id,
                             uint64_t cookie,
                             uint64_t notifier_id,
                             bufferlist& bl) = 0;
  virtual void handle_error(uint64_t cookie, int err) = 0;
};
```

典型用途包含：

- cache / metadata 更新通知
- 分散式協調中的輕量事件推播
- 上層元件的 lock、state 變更追蹤

## Python 綁定：`src/pybind/rados/`

Ceph 也提供 Python 介面，實作位於 `src/pybind/rados/`。其中 `rados.pyx` 明確說明它是對 `librados` 的 thin wrapper。

```py
# 檔案: ceph/src/pybind/rados/rados.pyx
"""
This module is a thin wrapper around librados.

Error codes from librados are turned into exceptions that subclass
:class:`Error`.
"""
```

這層綁定讓管理工具、測試程式與自動化腳本能直接使用 Python 操作 pool / object，而不必自己包 C API。

## 原始碼閱讀建議

1. 先看 `Rados` 與 `IoCtx` 的生命週期
2. 再看 `ObjectWriteOperation` / `ObjectReadOperation` 如何組裝複合操作
3. 最後追 `AioCompletion` 與 watch/notify 的非同步流程

## 關鍵原始碼參考

- `ceph/src/include/rados/librados.hpp`
- `ceph/src/include/rados/librados.h`
- `ceph/src/pybind/rados/rados.pyx`
- `ceph/src/pybind/rados/`

::: info 相關章節
- 想看 block storage 如何建立在 RADOS 之上，請參閱 [RBD 塊存儲](./rbd)
- 想看檔案系統如何把 metadata 與 data 分離，請參閱 [CephFS 分散式文件系統](./cephfs)
- 想看 S3 / Swift gateway 如何把物件操作轉成 HTTP API，請參閱 [RADOS Gateway](./rgw)
:::
