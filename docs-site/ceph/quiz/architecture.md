---
layout: doc
title: Ceph — 架構測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# Ceph — 架構測驗

<QuizQuestion
  question="1. 在 Ceph 架構中，RADOS 最主要扮演什麼角色？"
  :options='[
    "提供統一的分散式物件儲存核心，並作為上層介面的基礎",
    "只負責提供 Web 管理介面與圖形化儀表板",
    "專門用來執行區塊裝置快照排程",
    "只處理 CephFS 的 metadata，不處理資料物件",
  ]'
  :answer="0"
  explanation="RADOS 是 Ceph 的核心分散式儲存層，負責物件儲存、複寫、自我修復與資料分布。RBD、CephFS 與 RGW 都建立在 RADOS 之上，而不是各自維護獨立的儲存核心。"
/>

<QuizQuestion
  question="2. Ceph MON 叢集的主要責任是什麼？"
  :options='[
    "直接儲存所有使用者資料物件",
    "維護叢集狀態與各類 cluster maps 的一致性",
    "負責執行每顆磁碟的資料校驗",
    "提供所有 S3 與 Swift API 請求入口",
  ]'
  :answer="1"
  explanation="MON 主要維護叢集的控制平面資訊，例如 monmap、osdmap、mgrmap 與 CRUSH map 的版本與一致性，並透過共識機制維持叢集狀態。使用者資料實際上儲存在 OSD，而不是 MON。"
/>

<QuizQuestion
  question="3. OSD 在 Ceph 中最核心的職責是什麼？"
  :options='[
    "只負責選舉 monitor leader",
    "負責儲存資料、處理複寫或 EC、並回應讀寫請求",
    "只處理 Ceph Dashboard 的圖形化頁面渲染",
    "專門將 RBD 映射成 Linux block device",
  ]'
  :answer="1"
  explanation="OSD 是資料平面的核心 daemon，實際負責物件儲存、資料複寫、恢復、回填與 scrub 等工作。客戶端最終也是與 OSD 互動完成資料讀寫，而不是由 MON 直接存放資料。"
/>

<QuizQuestion
  question="4. Ceph MGR 的角色最適合以下哪個描述？"
  :options='[
    "取代 MON 成為唯一的共識節點",
    "只在 CephFS 啟用時才需要存在",
    "提供額外管理與監控能力，並承載模組化功能",
    "負責直接執行 CRUSH 演算法中的資料搬移",
  ]'
  :answer="2"
  explanation="MGR 是 Ceph 的管理擴充層，提供 metrics、dashboard、orchestrator 模組等能力。它不是用來取代 MON 共識，也不是資料實際寫入節點，而是補強管理、可視化與整合功能。"
/>

<QuizQuestion
  question="5. CRUSH 演算法在 Ceph 中的主要用途是什麼？"
  :options='[
    "把所有資料集中到單一高效能 OSD",
    "根據拓樸與規則計算資料應落在哪些 OSD，而不需中心查表",
    "用來加密客戶端與 OSD 之間的傳輸內容",
    "只在 MON 發生故障時才會啟用",
  ]'
  :answer="1"
  explanation="CRUSH 會根據叢集拓樸、故障域與 placement rule 計算資料放置位置，避免依賴中央查表服務。這讓 Ceph 能在大規模環境下維持可擴展性與故障隔離能力。"
/>

<QuizQuestion
  question="6. 下列哪一項最能代表 cluster maps 在 Ceph 內的意義？"
  :options='[
    "它們是描述叢集成員、拓樸與狀態的核心中繼資料",
    "它們是儲存在每個 client 本地端的暫存檔，不影響叢集運作",
    "它們只用於 Dashboard 前端畫面顯示，與資料路徑無關",
    "它們只在部署 cephadm 時才會產生",
  ]'
  :answer="0"
  explanation="cluster maps 包含 monmap、osdmap、mgrmap 與 CRUSH map 等，是 Ceph 控制平面的核心描述資料。客戶端與 daemon 需要依賴這些 map 了解叢集狀態、拓樸與資料位置。"
/>

<QuizQuestion
  question="7. Placement Group 也就是 PG，在 Ceph 中最貼切的說法是什麼？"
  :options='[
    "每個 PG 都固定對應一顆實體磁碟，兩者一對一綁定",
    "PG 是物件與 OSD 之間的中介邏輯分組，用來簡化資料分布與恢復",
    "PG 是 MON 用來儲存金鑰的安全區域",
    "PG 只存在於 CephFS，RBD 與 RGW 不會使用",
  ]'
  :answer="1"
  explanation="PG 是 Ceph 的重要抽象層，物件會先映射到 PG，再由 PG 對應到一組 OSD。這樣能降低追蹤單一物件位置的複雜度，也讓恢復、重平衡與狀態管理更容易處理。"
/>

<QuizQuestion
  question="8. 關於 Ceph 版本命名，哪個選項是正確的理解？"
  :options='[
    "Ceph 永遠只用數字版本，不使用代號",
    "Ceph 常以字母序的代號命名主要版本，例如 Quincy、Reef、Squid",
    "Ceph 版本名稱全部來自 Linux kernel 版本號",
    "每個 Ceph 小版本都一定會更換一組全新的代號",
  ]'
  :answer="1"
  explanation="Ceph 的主要版本常使用代號命名，而且通常依字母順序演進，例如 Quincy、Reef、Squid。這些代號通常對應 major release，而不是每一個小修補版本都重新命名。"
/>

<QuizQuestion
  question="9. 為什麼 Ceph 常強調將資料路徑與控制路徑分開理解？"
  :options='[
    "因為所有資料流量都必須先經過 Dashboard 才能進入 OSD",
    "因為 client 通常向 MON 取得叢集資訊後，實際讀寫直接與 OSD 互動",
    "因為 MGR 會攔截所有寫入請求再轉交給 RGW",
    "因為 OSD 不會接收來自 client 的直接請求",
  ]'
  :answer="1"
  explanation="Ceph 的控制路徑通常由 MON 提供 map 與叢集狀態資訊，資料路徑則由 client 直接對 OSD 發送讀寫請求。這種分工能避免控制節點成為資料流量瓶頸，提升整體擴展性。"
/>
