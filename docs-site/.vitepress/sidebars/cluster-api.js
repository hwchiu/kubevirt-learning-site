export default [
  {
    text: '📖 Cluster API 總覽',
    items: [
      { text: '專案簡介', link: '/cluster-api/' },
      { text: '系統架構', link: '/cluster-api/architecture' },
      { text: '核心功能', link: '/cluster-api/core-features' },
    ]
  },
  {
    text: '⚙️ API 與控制器',
    items: [
      { text: '控制器與 CRD API', link: '/cluster-api/controllers-api' },
      { text: 'Provider 模型', link: '/cluster-api/providers' },
      { text: 'ClusterClass 與 Topology', link: '/cluster-api/clusterclass' },
    ]
  },
  {
    text: '🔄 操作指南',
    items: [
      { text: '叢集生命週期', link: '/cluster-api/lifecycle' },
      { text: '外部整合（clusterctl / Tilt）', link: '/cluster-api/integration' },
    ]
  },
  {
    text: '🗺️ 學習路徑',
    items: [
      { text: '學習路徑入口', link: '/cluster-api/learning-path/' },
      { text: '故事驅動式學習', link: '/cluster-api/learning-path/story' },
    ]
  },
]
