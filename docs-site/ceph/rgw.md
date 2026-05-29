---
layout: doc
title: Ceph — RADOS Gateway (S3/Swift)
---

# Ceph — RADOS Gateway (S3/Swift)

::: tip 核心定位
RGW（RADOS Gateway）是 Ceph 面向應用層的 HTTP gateway，對外提供 S3 / Swift 相容 API，對內則把 bucket、object、ACL、policy、multisite sync 等需求轉成對 RADOS 的操作。
:::

## RGW 的角色：從 HTTP 請求到物件操作

RGW 可以理解成 Ceph 的 object access plane：

```text
// 檔案: docs-site/ceph/rgw.md
S3 / Swift Client
        |
        v
   HTTP / REST
        |
        v
      RGWOp
        |
        v
    rgw::sal::Driver
        |
        v
     RGWRados
        |
        v
      RADOS
```

因此，RGW 並不是一個單純轉發器，而是同時處理：

- 驗證與授權
- bucket / object namespace 管理
- ACL / bucket policy / IAM policy
- notification、lifecycle、reshard
- multisite 同步與資料面操作

## `RGWOp`：請求處理骨幹

`src/rgw/rgw_op.h` 第 214 行開始定義 `class RGWOp`。這個類別是各種 REST operation 的共同基底。

```cpp
// 檔案: ceph/src/rgw/rgw_op.h
class RGWOp : public DoutPrefixProvider {
protected:
  req_state *s;
  RGWHandler *dialect_handler;
  rgw::sal::Driver* driver;
  RGWQuota quota;
  int op_ret;

public:
  virtual int verify_permission(optional_yield y) = 0;
  virtual void execute(optional_yield y) = 0;
  virtual void send_response() {}
  virtual const char* name() const = 0;
};
```

從介面設計就能看出處理管線：

1. `init_processing()`
2. `verify_requester()`
3. `verify_permission()`
4. `execute()`
5. `send_response()` / `complete()`

也就是說，RGW 把 HTTP 方言（S3 / Swift）、授權檢查與實際 object 存取拆開，再透過繼承擴充不同 operation。

## `RGWRados`：把 gateway 行為落到 RADOS

`src/rgw/driver/rados/rgw_rados.h` 第 323 行開始的 `class RGWRados`，是最核心的後端實作之一。

```cpp
// 檔案: ceph/src/rgw/driver/rados/rgw_rados.h
class RGWRados
{
  int open_root_pool_ctx(const DoutPrefixProvider *dpp);
  int open_gc_pool_ctx(const DoutPrefixProvider *dpp);
  int open_lc_pool_ctx(const DoutPrefixProvider *dpp);
  int open_pool_ctx(const DoutPrefixProvider *dpp, const rgw_pool& pool,
                    librados::IoCtx& io_ctx, bool mostly_omap, bool bulk);

  librados::IoCtx root_pool_ctx;
  RGWMetaNotifier* meta_notifier{nullptr};
  RGWDataNotifier* data_notifier{nullptr};
  RGWMetaSyncProcessorThread* meta_sync_processor_thread{nullptr};
  std::map<rgw_zone_id, RGWDataSyncProcessorThread *> data_sync_processor_threads;
};
```

這段宣告直接揭露 RGW 後端的重要能力：

- 開啟多個 pool context
- 維護 GC / lifecycle / reshard / notification 等背景元件
- 啟動 metadata 與 data sync thread
- 將 gateway 的 bucket/object 行為映射到 RADOS pool 與 object 操作

## S3 / Swift 相容性

官方文件已把 RGW 明確定位為兩種 API gateway：

- `doc/radosgw/s3.rst`：支援 Amazon S3 基本資料存取模型
- `doc/radosgw/swift.rst`：支援 OpenStack Swift 基本資料存取模型

其中 `s3.rst` 還列出 bucket policy、bucket/object ACL、multipart upload、versioning 等功能支援狀態；`swift.rst` 則說明 Swift ACL 與 container / object API 支援範圍。

::: info 相容性的正確理解
RGW 追求的是 **API compatibility**，不是複製 AWS 或 Swift 的整個內部實作。因此文件通常會明講 supported / partial / different semantics。
:::

## Bucket Policies 與 ACL

`src/rgw/rgw_common.h` 是理解權限模型的重要入口。這個檔案定義了 ACL、IAM policy 與 sync policy 相關常數與型別。

```cpp
// 檔案: ceph/src/rgw/rgw_common.h
#include "rgw_iam_policy.h"
#include "rgw_sync_policy.h"

#define RGW_ATTR_ACL                  RGW_ATTR_PREFIX "acl"
#define RGW_ATTR_IAM_POLICY           RGW_ATTR_PREFIX "iam-policy"
#define RGW_ATTR_USER_POLICY          RGW_ATTR_PREFIX "user-policy"
#define RGW_ATTR_MANAGED_POLICY       RGW_ATTR_PREFIX "managed-policy"
```

這表示 RGW 的授權模型並不是只靠 bucket metadata 上的幾個欄位，而是把：

- ACL
- bucket / object policy
- IAM-style policy
- sync policy

都納入統一的 request 驗證流程。

## Multisite replication

`doc/radosgw/multisite.rst` 描述了 realm、zonegroup、zone 的多站點架構；而 `RGWRados` 內部的 `RGWMetaSyncProcessorThread`、`RGWDataSyncProcessorThread`、`meta_notifier`、`data_notifier` 則是程式碼層面能直接看到的同步骨架。

多站點模式的價值包括：

- 跨地區災難復原
- active-active zone 寫入
- metadata 與 data 的分層同步
- 全域 bucket / user namespace 管理

::: warning 注意同步層級
RGW multisite 不是單純「把 pool 複製過去」；它有自己的 realm / zonegroup / zone 組態與 metadata sync / data sync 流程。
:::

## Driver 抽象：不只 RADOS

`src/rgw/driver/` 目錄下可看到多種 driver：

- `rados/`
- `posix/`
- `d4n/`
- 以及其他實驗或替代後端

這說明 RGW 上層 operation 與後端儲存驅動之間是有抽象邊界的；雖然 Ceph 正統部署多半仍以 `RGWRados` 為主，但架構上並非把所有邏輯硬編碼在單一 backend。

## 關鍵原始碼參考

- `ceph/src/rgw/rgw_op.h`（第 214 行：`class RGWOp`）
- `ceph/src/rgw/driver/rados/rgw_rados.h`（第 323 行：`class RGWRados`）
- `ceph/src/rgw/driver/`
- `ceph/src/rgw/rgw_common.h`
- `ceph/doc/radosgw/s3.rst`
- `ceph/doc/radosgw/swift.rst`
- `ceph/doc/radosgw/multisite.rst`

::: info 相關章節
- 想先理解 RGW 最底層依賴的 object store，請參閱 [RADOS 物件存儲 & librados](./rados)
- 想看 block storage 的另一條產品線，請參閱 [RBD 塊存儲](./rbd)
- 想看檔案系統產品線，請參閱 [CephFS 分散式文件系統](./cephfs)
:::
