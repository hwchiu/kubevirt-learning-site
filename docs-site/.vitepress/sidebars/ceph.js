export default [
  {
    text: '🗺️ 學習路徑',
    items: [
      { text: '學習路徑入口', link: '/ceph/learning-path/' },
      { text: '故事驅動式', link: '/ceph/learning-path/story' },
    ]
  },
  {
    text: '🏗️ 系統架構',
    collapsed: false,
    items: [
      { text: '專案總覽', link: '/ceph/' },
      { text: '整體架構概述', link: '/ceph/architecture' },
      { text: '部署架構與 cephadm', link: '/ceph/deployment' },
    ]
  },
  {
    text: '⚙️ 核心元件',
    collapsed: false,
    items: [
      { text: 'Monitor (MON) 詳解', link: '/ceph/monitor' },
      { text: 'OSD 詳解', link: '/ceph/osd' },
      { text: 'Manager (MGR) 與模組系統', link: '/ceph/manager' },
      { text: 'Metadata Server (MDS) 詳解', link: '/ceph/mds' },
    ]
  },
  {
    text: '💾 儲存介面',
    collapsed: false,
    items: [
      { text: 'RADOS 物件存儲 & librados', link: '/ceph/rados' },
      { text: 'RBD 塊存儲', link: '/ceph/rbd' },
      { text: 'CephFS 分散式文件系統', link: '/ceph/cephfs' },
      { text: 'RADOS Gateway (S3/Swift)', link: '/ceph/rgw' },
    ]
  },
  {
    text: '🔬 核心演算法',
    collapsed: true,
    items: [
      { text: 'CRUSH 演算法深度分析', link: '/ceph/crush' },
      { text: 'PG 機制與複製策略', link: '/ceph/pg-replication' },
    ]
  },
  {
    text: '🛠️ 維運管理',
    collapsed: true,
    items: [
      { text: 'cephadm 部署工具', link: '/ceph/cephadm' },
      { text: 'Ceph Dashboard 與 REST API', link: '/ceph/dashboard' },
      { text: '日常維運操作', link: '/ceph/operations' },
    ]
  },
  {
    text: '📝 學習測驗',
    items: [
      { text: '🏗️ 架構測驗', link: '/ceph/quiz/architecture' },
      { text: '⚙️ 元件測驗', link: '/ceph/quiz/components' },
      { text: '💾 儲存介面測驗', link: '/ceph/quiz/storage' },
    ]
  },
]
