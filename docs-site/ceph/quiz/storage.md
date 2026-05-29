---
layout: doc
title: Ceph — 儲存介面測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# Ceph — 儲存介面測驗

<QuizQuestion
  question="1. librados API 在 Ceph 生態中最核心的定位是什麼？"
  :options='[
    "直接提供存取 RADOS 物件層的原生程式介面",
    "只提供瀏覽器中的 Dashboard 視覺化功能",
    "專門用來掛載 CephFS 到 Linux 核心",
    "只給 RGW 內部使用，其他應用不能使用",
  ]'
  :answer="0"
  explanation="librados 是直接對 RADOS 物件層操作的原生 API，應用程式可以透過它讀寫物件、使用 pool 等功能。它是更底層的介面，而不是圖形化管理工具或僅供 RGW 使用的私有元件。"
/>

<QuizQuestion
  question="2. 下列哪一項是 RBD 常見的能力？"
  :options='[
    "提供區塊裝置映像，並支援快照與複製等功能",
    "只支援物件 API，不提供區塊語意",
    "專門處理 CephFS metadata journal",
    "只能在單機模式下建立磁碟映像",
  ]'
  :answer="0"
  explanation="RBD 是 Ceph 的區塊儲存介面，常見功能包括映像、快照、clone、thin provisioning 等。它提供的是 block device 語意，不是物件 API 或檔案系統 metadata 管理。"
/>

<QuizQuestion
  question="3. CephFS 最適合以下哪種存取模型？"
  :options='[
    "提供 POSIX 風格的共享檔案系統介面",
    "只允許透過 S3 API 存取資料",
    "只能以 raw block device 形式使用",
    "完全不需要 metadata 服務即可運作",
  ]'
  :answer="0"
  explanation="CephFS 提供類似 POSIX 的共享檔案系統語意，適合需要目錄、檔名、權限與檔案操作的情境。它和 RBD、RGW 分別代表不同層次的儲存介面。"
/>

<QuizQuestion
  question="4. 關於 RGW 與 S3 相容性，下列哪個說法最正確？"
  :options='[
    "RGW 目標是提供與 S3 相容的物件 API，但不代表所有細節都必然百分之百一致",
    "RGW 與 S3 完全無關，只支援 POSIX 掛載",
    "RGW 只能在沒有 OSD 的環境獨立運作",
    "RGW 是用來提供區塊裝置映射給虛擬機使用",
  ]'
  :answer="0"
  explanation="RGW 的重要價值是提供與 S3 相容的物件儲存 API，讓應用程式較容易整合。不過相容通常代表大方向與常用介面一致，不一定保證每個雲端廠商特性都完全等同。"
/>

<QuizQuestion
  question="5. Erasure Coding 在 Ceph 中主要想達成什麼目標？"
  :options='[
    "用較低的儲存開銷提供容錯能力",
    "把所有副本都集中到同一台主機以降低延遲",
    "完全取代 cluster maps 的版本管理",
    "讓 CephFS 不再需要 MDS",
  ]'
  :answer="0"
  explanation="Erasure Coding 透過資料分片與編碼分片，提供比多副本更省容量的容錯方式。它通常能降低儲存成本，但在寫入路徑與恢復複雜度上也常比 replication 更高。"
/>

<QuizQuestion
  question="6. 與 erasure coding 相比，replication 的典型特性是什麼？"
  :options='[
    "概念較直觀，讀寫與恢復邏輯通常較容易理解",
    "完全不具備容錯能力",
    "只適用於 RGW，不能用於 RBD 或 CephFS",
    "一定比任何 erasure coding 組態更節省容量",
  ]'
  :answer="0"
  explanation="Replication 透過直接保存多份副本提供容錯，設計與運維通常較直觀，也常用於需要較簡單恢復流程的情境。相對地，它的容量開銷通常高於 erasure coding。"
/>

<QuizQuestion
  question="7. 如果應用程式需要最底層、最直接的物件操作能力，優先考慮哪個介面較合理？"
  :options='[
    "librados",
    "Ceph Dashboard",
    "RBD kernel map 指令",
    "MDS standby 模式",
  ]'
  :answer="0"
  explanation="當需求是直接與物件層互動時，librados 是最底層也最直接的選擇。RBD 與 CephFS 則分別提供區塊與檔案語意，不是原生物件 API。"
/>

<QuizQuestion
  question="8. 為什麼同一個 Ceph 叢集能同時提供 RBD、CephFS 與 RGW？"
  :options='[
    "因為它們共享底層 RADOS 核心，只是在上層暴露不同存取語意",
    "因為每一種介面都必須有完全獨立的一套 OSD 叢集",
    "因為 MON 會把所有資料自動轉成 SQL 表格",
    "因為 CRUSH 只服務於 CephFS，不影響其他介面",
  ]'
  :answer="0"
  explanation="Ceph 的一大特色就是多種儲存介面共享同一個底層 RADOS 核心。RBD 提供 block、CephFS 提供 file、RGW 提供 object，但底層仍依賴相同的分散式儲存能力。"
/>

<QuizQuestion
  question="9. 在規劃 pool 時，哪個說法較符合 replicated pool 與 erasure-coded pool 的差異？"
  :options='[
    "replicated pool 側重多副本保護，erasure-coded pool 側重容量效率",
    "兩者在容錯方式與容量特性上完全沒有差異",
    "erasure-coded pool 不能與任何 Ceph 介面搭配使用",
    "replicated pool 不允許設定副本數量",
  ]'
  :answer="0"
  explanation="replicated pool 透過多份完整副本提供保護，設計較直觀；erasure-coded pool 則透過資料分片與編碼提升容量效率。兩者在效能、容量與恢復行為上都有不同取捨，因此規劃時需要依工作負載選擇。"
/>
