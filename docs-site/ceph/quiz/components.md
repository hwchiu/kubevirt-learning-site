---
layout: doc
title: Ceph — 元件測驗
---

<script setup>
import QuizQuestion from '../../.vitepress/theme/components/QuizQuestion.vue'
</script>

# Ceph — 元件測驗

<QuizQuestion
  question="1. Ceph MON 使用 Paxos 類型的共識機制，主要目的是什麼？"
  :options='[
    "讓所有 OSD 同步使用同一塊本地磁碟",
    "確保叢集關鍵狀態更新在 monitor 之間維持一致",
    "提升 RGW 的 HTTP 連線吞吐量",
    "把 CephFS metadata 直接複寫到所有 client",
  ]'
  :answer="1"
  explanation="MON 需要對叢集狀態達成一致，例如 map 更新與節點狀態變更，因此使用 Paxos 類型共識來維持一致性。這是控制平面正確性的基礎，而不是資料平面吞吐量優化手段。"
/>

<QuizQuestion
  question="2. BlueStore 與較早期儲存後端相比，最明顯的特點是什麼？"
  :options='[
    "BlueStore 需要先經過本地檔案系統才能寫入資料",
    "BlueStore 直接管理原始區塊裝置，減少額外檔案系統層",
    "BlueStore 只能用於 RGW，不能用於 RBD",
    "BlueStore 只能搭配單節點 Ceph 叢集使用",
  ]'
  :answer="1"
  explanation="BlueStore 直接對原始區塊裝置進行管理，不再依賴像 FileStore 那樣先透過本地檔案系統。這通常能帶來更好的效能與更有效的空間利用。"
/>

<QuizQuestion
  question="3. 關於 CephFS 的 MDS 狀態，下列哪個描述最合理？"
  :options='[
    "所有 MDS 永遠都是 active，不能有備援角色",
    "MDS 可以有 active 與 standby 等狀態，以支援高可用",
    "MDS 只在 RGW 啟用後才會存在",
    "MDS 只負責處理 OSD 心跳，不處理檔案系統 metadata",
  ]'
  :answer="1"
  explanation="CephFS 的 MDS 會有 active、standby 等狀態，讓叢集在 metadata 服務上具備高可用與故障切換能力。MDS 的核心工作是管理 CephFS metadata，而不是 OSD 心跳。"
/>

<QuizQuestion
  question="4. cephadm 在現代 Ceph 叢集中的主要用途是什麼？"
  :options='[
    "取代 CRUSH 演算法決定資料放置位置",
    "作為叢集部署與生命週期管理工具",
    "只提供 CephFS 用戶端掛載指令",
    "專門負責將 RBD 匯出成 NFS 分享",
  ]'
  :answer="1"
  explanation="cephadm 是 Ceph 官方常用的部署與維運工具，負責 bootstrap、daemon 佈署、升級與服務管理。它屬於叢集生命週期管理層，而不是資料放置或檔案分享元件。"
/>

<QuizQuestion
  question="5. Ceph MGR modules 的設計價值是什麼？"
  :options='[
    "讓管理功能可以模組化擴充，而不必把所有能力硬寫進核心 daemon",
    "用來取代所有 MON 的選舉與共識流程",
    "只為了在 client 端快取 RADOS 物件",
    "讓每顆 OSD 都能直接提供 S3 API",
  ]'
  :answer="0"
  explanation="MGR modules 提供模組化擴充點，例如 dashboard、prometheus、orchestrator 等，都能透過 MGR 擴充。這樣能讓管理能力靈活演進，而不必讓所有功能都直接耦合進核心控制邏輯。"
/>

<QuizQuestion
  question="6. Ceph Dashboard 一般建立在哪個元件之上？"
  :options='[
    "MON 的內建 Web 伺服器，與 MGR 無關",
    "MGR 的 dashboard 模組",
    "每個 OSD 內建的圖形化頁面",
    "RGW 的 Swift 相容層",
  ]'
  :answer="1"
  explanation="Ceph Dashboard 通常是由 MGR 的 dashboard 模組提供，透過 MGR 蒐集與整合叢集資訊後輸出圖形化介面。它不是每個 OSD 各自提供的獨立 Web UI。"
/>

<QuizQuestion
  question="7. RADOS Gateway 也就是 RGW，主要提供哪一類操作介面？"
  :options='[
    "提供物件儲存 API，例如 S3 與 Swift 相容操作",
    "只提供 POSIX 檔案系統 syscall 介面",
    "只提供區塊裝置映射，不支援 HTTP",
    "專門處理 monitor quorum 選舉",
  ]'
  :answer="0"
  explanation="RGW 是 Ceph 的物件儲存閘道，通常提供 S3 與 Swift 相容 API，讓應用程式透過 HTTP 存取物件。POSIX 檔案語意主要是 CephFS，區塊裝置則由 RBD 提供。"
/>

<QuizQuestion
  question="8. 為什麼在有 MON 的情況下，Ceph 仍然需要 MGR？"
  :options='[
    "因為 MGR 主要補充監控、統計、模組與編排整合能力",
    "因為 MON 不能儲存任何叢集 map",
    "因為 MGR 是唯一能與 OSD 通訊的元件",
    "因為沒有 MGR 就無法進行任何 client I/O",
  ]'
  :answer="0"
  explanation="MON 著重於叢集狀態一致性與控制平面核心資訊，而 MGR 補足了監控、模組化擴充、dashboard 與 orchestrator 整合等能力。兩者角色不同，MGR 並不是用來取代 MON 的一致性職責。"
/>

<QuizQuestion
  question="9. 當使用者透過 RGW 上傳物件時，哪個描述最貼近真實流程？"
  :options='[
    "RGW 只把請求寫進 MON，不會接觸 RADOS",
    "RGW 作為 HTTP 閘道接收請求，後端仍將資料存入 Ceph 儲存叢集",
    "RGW 會把物件永遠保存在本機磁碟，不依賴 OSD",
    "RGW 只在 CephFS 啟用時才能運作",
  ]'
  :answer="1"
  explanation="RGW 面向應用程式提供 HTTP 物件 API，但底層儲存仍然落在 Ceph 叢集之上，通常會透過 RADOS 存放資料。它不是單純本機快取服務，也不是只依賴 MON 儲存內容。"
/>
