export default [
  {
    text: '📖 MinIO 總覽',
    items: [
      { text: '專案簡介', link: '/minio/' },
      { text: '系統架構', link: '/minio/architecture' },
    ]
  },
  {
    text: '儲存引擎',
    collapsed: false,
    items: [
      { text: 'Erasure Coding 與資料分片', link: '/minio/erasure-coding' },
      { text: '底層硬碟讀寫機制', link: '/minio/disk-io' },
      { text: '物件讀寫完整流程', link: '/minio/object-lifecycle' },
    ]
  },
  {
    text: '資料保護與複製',
    collapsed: false,
    items: [
      { text: '資料複製與同步', link: '/minio/data-replication' },
      { text: '資料修復與自癒機制', link: '/minio/healing' },
    ]
  },
  {
    text: 'API 與整合',
    collapsed: true,
    items: [
      { text: 'S3 API 與監控整合', link: '/minio/integration' },
    ]
  },
]
