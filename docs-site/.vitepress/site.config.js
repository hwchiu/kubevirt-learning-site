/**
 * site.config.js — 站台層級設定
 *
 * 當你把這個專案複製到公司內部分析不同的專案時，
 * 只需要修改這個檔案，其他所有 config 不用動。
 */

export const siteConfig = {
  /** GitHub Pages base path（本機開發設 '/'，GitHub Pages 設 '/repo-name/'） */
  base: '/kubevirt-learning-site/',

  /** 網站標題（顯示在瀏覽器分頁） */
  title: 'KubeVirt 生態系原始碼分析',

  /** 網站描述（SEO） */
  description: '深入分析 KubeVirt 生態系各專案原始碼 — 架構、元件、API 與實作細節',

  /** 側邊欄 Logo 文字 */
  siteTitle: 'KubeVirt 生態系分析',

  /** Logo emoji（或圖片路徑） */
  logo: '🖥️',

  /** SEO keywords */
  keywords: 'KubeVirt, CDI, Kubernetes, VM, 原始碼分析',

  /** 頂部導覽「專案」下拉選單 — 新增專案時在這裡加一行 */
  projectNav: [
    { text: 'KubeVirt',                        link: '/kubevirt/architecture/overview' },
    { text: 'Containerized Data Importer (CDI)', link: '/containerized-data-importer/' },
    { text: 'Monitoring',                        link: '/monitoring/' },
    { text: 'Common Instancetypes',              link: '/common-instancetypes/' },
    { text: 'Node Maintenance Operator',         link: '/node-maintenance-operator/' },
    { text: 'Forklift',                          link: '/forklift/' },
    { text: 'NetBox',                            link: '/netbox/' },
    { text: 'Multus CNI',                        link: '/multus-cni/' },
    { text: 'TiDB',                              link: '/tidb/' },
    { text: 'Apache Kafka',                      link: '/kafka/' },
    { text: 'Kubernetes PV/PVC',                 link: '/kubernetes/' },
  ],

  /** 頁腳文字 */
  footerMessage: '基於 Apache 2.0 授權',
  footerCopyright: 'KubeVirt 生態系原始碼分析 — 為工程師而生',

  /** GitHub 連結 */
  githubLink: 'https://github.com/kubevirt/kubevirt',

  /** 呼叫 local LLM 的 CLI 指令（支援 claude / claude-router 等） */
  cliCommand: 'claude',
}
