export default [
  {
    text: '📖 Kubernetes PV/PVC 總覽',
    items: [
      { text: '專案簡介', link: '/kubernetes/' },
    ]
  },
  {
    text: '💾 PV/PVC 儲存子系統',
    items: [
      { text: 'PV/PVC 架構總覽', link: '/kubernetes/pv-pvc-architecture' },
      { text: 'PV/PVC 生命週期與綁定機制', link: '/kubernetes/pv-pvc-lifecycle' },
      { text: 'StorageClass 與動態佈建', link: '/kubernetes/storageclass-provisioning' },
      { text: 'CSI 整合架構', link: '/kubernetes/csi-integration' },
      { text: '存取模式、卷模式與回收策略', link: '/kubernetes/access-modes-reclaim' },
    ]
  },
  {
    text: '🛠️ 實務指南',
    items: [
      { text: '常見問題與排錯指南', link: '/kubernetes/troubleshooting' },
    ]
  },
]
