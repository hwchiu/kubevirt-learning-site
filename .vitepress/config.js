import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/kubevirt-learning-site/',
  title: 'KubeVirt 學習指南',
  description: '深入淺出 KubeVirt — 基於 Kubernetes 的虛擬機器管理平台完整學習資源',
  lang: 'zh-TW',
  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
    ['meta', { name: 'keywords', content: 'KubeVirt, Kubernetes, VM, 虛擬機器, 學習' }],
  ],
  themeConfig: {
    logo: '🖥️',
    siteTitle: 'KubeVirt 學習指南',
    nav: [
      { text: '🏠 首頁', link: '/' },
      { text: '🏗️ 架構', link: '/architecture/overview' },
      { text: '⚙️ 元件', link: '/components/virt-operator' },
      { text: '📦 API 資源', link: '/api-resources/vm-vmi' },
      { text: '🌐 網路', link: '/networking/overview' },
      { text: '💾 儲存', link: '/storage/overview' },
      { text: '🛠️ virtctl', link: '/virtctl/guide' },
      { text: '🚀 進階功能', link: '/advanced/live-migration' },
    ],
    sidebar: {
      '/architecture/': [
        {
          text: '🏗️ 架構總覽',
          items: [
            { text: '系統架構概述', link: '/architecture/overview' },
            { text: 'VM 生命週期流程', link: '/architecture/lifecycle' },
            { text: '架構深入剖析', link: '/architecture/deep-dive' },
          ]
        }
      ],
      '/components/': [
        {
          text: '⚙️ 核心元件',
          items: [
            { text: 'virt-operator', link: '/components/virt-operator' },
            { text: 'virt-api', link: '/components/virt-api' },
            { text: 'virt-controller', link: '/components/virt-controller' },
            { text: 'virt-handler', link: '/components/virt-handler' },
            { text: 'virt-launcher', link: '/components/virt-launcher' },
          ]
        }
      ],
      '/api-resources/': [
        {
          text: '📦 API 資源 (CRD)',
          items: [
            { text: 'VM 與 VMI', link: '/api-resources/vm-vmi' },
            { text: 'ReplicaSet 與 Pool', link: '/api-resources/replica-pool' },
            { text: 'Migration', link: '/api-resources/migration' },
            { text: 'Instancetype & Preference', link: '/api-resources/instancetype' },
            { text: 'Snapshot, Clone & Export', link: '/api-resources/snapshot-clone' },
          ]
        }
      ],
      '/networking/': [
        {
          text: '🌐 網路',
          items: [
            { text: '網路架構總覽', link: '/networking/overview' },
            { text: 'Bridge 與 Masquerade', link: '/networking/bridge-masquerade' },
            { text: 'SR-IOV 與進階網路', link: '/networking/sriov' },
          ]
        }
      ],
      '/storage/': [
        {
          text: '💾 儲存',
          items: [
            { text: '儲存架構總覽', link: '/storage/overview' },
            { text: 'ContainerDisk', link: '/storage/container-disk' },
            { text: 'PVC 與 DataVolume', link: '/storage/pvc-datavolume' },
            { text: '熱插拔 (Hotplug)', link: '/storage/hotplug' },
          ]
        }
      ],
      '/virtctl/': [
        {
          text: '🛠️ virtctl 操作指南',
          items: [
            { text: '完整指令參考', link: '/virtctl/guide' },
            { text: 'VM 存取操作', link: '/virtctl/access' },
          ]
        }
      ],
      '/advanced/': [
        {
          text: '🚀 進階功能',
          items: [
            { text: 'Live Migration', link: '/advanced/live-migration' },
            { text: 'Snapshot & Restore', link: '/advanced/snapshots' },
            { text: 'Observability & 監控', link: '/advanced/observability' },
          ]
        }
      ],
      '/dev-guide/': [
        {
          text: '👨‍💻 開發指南',
          items: [
            { text: '開發環境設置', link: '/dev-guide/getting-started' },
            { text: '程式碼架構導覽', link: '/dev-guide/code-structure' },
          ]
        }
      ],
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/kubevirt/kubevirt' }
    ],
    footer: {
      message: '基於 Apache 2.0 授權',
      copyright: 'KubeVirt 學習指南 — 為工程師而生'
    },
    search: {
      provider: 'local'
    },
    outline: {
      label: '本頁目錄',
      level: [2, 3]
    },
    docFooter: {
      prev: '上一頁',
      next: '下一頁'
    },
    lastUpdated: {
      text: '最後更新'
    }
  }
})
