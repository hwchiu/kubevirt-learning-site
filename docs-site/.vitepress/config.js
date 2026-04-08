import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { localLlmChatPlugin } from './plugins/localLlmChat.js'

const kubevirtSidebar = [
  {
    text: '🏗️ 架構總覽',
    items: [
      { text: '系統架構概述', link: '/kubevirt/architecture/overview' },
      { text: 'VM 生命週期流程', link: '/kubevirt/architecture/lifecycle' },
      { text: '架構深入剖析', link: '/kubevirt/architecture/deep-dive' },
    ]
  },
  {
    text: '⚙️ 核心元件',
    items: [
      { text: 'virt-operator', link: '/kubevirt/components/virt-operator' },
      { text: 'virt-api', link: '/kubevirt/components/virt-api' },
      { text: 'virt-controller', link: '/kubevirt/components/virt-controller' },
      { text: 'virt-handler', link: '/kubevirt/components/virt-handler' },
      { text: 'virt-launcher', link: '/kubevirt/components/virt-launcher' },
    ]
  },
  {
    text: '🔧 輔助元件',
    items: [
      { text: '輔助元件與工具程式', link: '/kubevirt/components/auxiliary-binaries' },
      { text: 'Hook Sidecar 機制', link: '/kubevirt/components/hook-sidecars' },
    ]
  },
  {
    text: '📦 API 資源 (CRD)',
    items: [
      { text: 'VM 與 VMI', link: '/kubevirt/api-resources/vm-vmi' },
      { text: 'ReplicaSet 與 Pool', link: '/kubevirt/api-resources/replica-pool' },
      { text: 'Migration', link: '/kubevirt/api-resources/migration' },
      { text: 'Instancetype & Preference', link: '/kubevirt/api-resources/instancetype' },
      { text: 'Snapshot, Clone & Export', link: '/kubevirt/api-resources/snapshot-clone' },
    ]
  },
  {
    text: '🌐 網路',
    items: [
      { text: '網路架構總覽', link: '/kubevirt/networking/overview' },
      { text: 'Bridge 與 Masquerade', link: '/kubevirt/networking/bridge-masquerade' },
      { text: 'SR-IOV 與進階網路', link: '/kubevirt/networking/sriov' },
    ]
  },
  {
    text: '💾 儲存',
    items: [
      { text: '儲存架構總覽', link: '/kubevirt/storage/overview' },
      { text: 'ContainerDisk', link: '/kubevirt/storage/container-disk' },
      { text: 'PVC 與 DataVolume', link: '/kubevirt/storage/pvc-datavolume' },
      { text: '熱插拔 (Hotplug)', link: '/kubevirt/storage/hotplug' },
    ]
  },
  {
    text: '🛠️ virtctl 操作指南',
    items: [
      { text: '完整指令參考', link: '/kubevirt/virtctl/guide' },
      { text: 'VM 存取操作', link: '/kubevirt/virtctl/access' },
    ]
  },
  {
    text: '🚀 進階功能',
    items: [
      { text: 'Live Migration', link: '/kubevirt/advanced/live-migration' },
      { text: 'Snapshot & Restore', link: '/kubevirt/advanced/snapshots' },
      { text: 'Observability & 監控', link: '/kubevirt/advanced/observability' },
    ]
  },
  {
    text: '🔬 深入剖析',
    items: [
      { text: 'QEMU/KVM 虛擬化核心', link: '/kubevirt/deep-dive/qemu-kvm' },
      { text: 'Windows VM 最佳化', link: '/kubevirt/deep-dive/windows-optimization' },
      { text: 'Live Migration 實作', link: '/kubevirt/deep-dive/migration-internals' },
      { text: '效能調校指南', link: '/kubevirt/deep-dive/performance-tuning' },
      { text: '安全架構', link: '/kubevirt/deep-dive/security' },
      { text: 'GPU/vGPU 直通', link: '/kubevirt/deep-dive/gpu-passthrough' },
    ]
  },
  {
    text: '📖 實用指南',
    items: [
      { text: '🚀 快速開始', link: '/kubevirt/guides/quickstart' },
      { text: 'VMware 到 KubeVirt', link: '/kubevirt/guides/vmware-to-kubevirt' },
      { text: '高可用 & 災難恢復', link: '/kubevirt/guides/ha-dr' },
      { text: '故障排除手冊', link: '/kubevirt/guides/troubleshooting' },
    ]
  },
  {
    text: '👨‍💻 開發指南',
    items: [
      { text: '開發環境設置', link: '/kubevirt/dev-guide/getting-started' },
      { text: '程式碼架構導覽', link: '/kubevirt/dev-guide/code-structure' },
    ]
  },
]

const cdiSidebar = [
  {
    text: '📖 CDI 總覽',
    items: [
      { text: '專案簡介', link: '/containerized-data-importer/' },
      { text: '系統架構', link: '/containerized-data-importer/architecture' },
      { text: '核心功能分析', link: '/containerized-data-importer/core-features' },
      { text: '控制器與 API', link: '/containerized-data-importer/controllers-api' },
      { text: '外部整合', link: '/containerized-data-importer/integration' },
    ]
  },
]

const monitoringSidebar = [
  {
    text: '📖 Monitoring 總覽',
    items: [
      { text: '專案簡介', link: '/monitoring/' },
      { text: '系統架構', link: '/monitoring/architecture' },
      { text: '核心功能分析', link: '/monitoring/core-features' },
      { text: '指標與告警規則', link: '/monitoring/metrics-alerts' },
      { text: '外部整合', link: '/monitoring/integration' },
    ]
  },
]

const instancetypesSidebar = [
  {
    text: '📖 Common Instancetypes 總覽',
    items: [
      { text: '專案簡介', link: '/common-instancetypes/' },
      { text: '系統架構', link: '/common-instancetypes/architecture' },
      { text: '核心功能分析', link: '/common-instancetypes/core-features' },
      { text: '資源類型目錄', link: '/common-instancetypes/resource-catalog' },
      { text: '外部整合', link: '/common-instancetypes/integration' },
    ]
  },
]

const nmoSidebar = [
  {
    text: '📖 Node Maintenance Operator 總覽',
    items: [
      { text: '專案簡介', link: '/node-maintenance-operator/' },
      { text: '系統架構', link: '/node-maintenance-operator/architecture' },
      { text: '核心功能分析', link: '/node-maintenance-operator/core-features' },
      { text: '控制器與 API', link: '/node-maintenance-operator/controllers-api' },
      { text: '外部整合', link: '/node-maintenance-operator/integration' },
    ]
  },
]

const forkliftSidebar = [
  {
    text: '📖 Forklift 總覽',
    items: [
      { text: '專案簡介', link: '/forklift/' },
      { text: '系統架構', link: '/forklift/architecture' },
      { text: '核心功能分析', link: '/forklift/core-features' },
      { text: '控制器與 API', link: '/forklift/controllers-api' },
      { text: '外部整合', link: '/forklift/integration' },
    ]
  },
]

const netboxSidebar = [
  {
    text: '📖 NetBox 總覽',
    items: [
      { text: '專案簡介', link: '/netbox/' },
      { text: '系統架構', link: '/netbox/architecture' },
      { text: '核心功能分析', link: '/netbox/core-features' },
      { text: '資料模型分析', link: '/netbox/data-models' },
      { text: 'API 參考與分析', link: '/netbox/api-reference' },
      { text: '外部整合與擴充', link: '/netbox/integration' },
    ]
  },
]

const multusSidebar = [
  {
    text: '📖 Multus CNI 總覽',
    items: [
      { text: '專案簡介', link: '/multus-cni/' },
      { text: '系統架構', link: '/multus-cni/architecture' },
      { text: '核心功能分析', link: '/multus-cni/core-features' },
      { text: 'Thick Plugin 深入剖析', link: '/multus-cni/thick-plugin' },
      { text: '設定參考', link: '/multus-cni/configuration' },
    ]
  },
]

const tidbSidebar = [
  {
    text: '📖 TiDB 總覽',
    items: [
      { text: '專案簡介', link: '/tidb/' },
      { text: '系統架構', link: '/tidb/architecture' },
      { text: '核心功能分析', link: '/tidb/core-features' },
      { text: '控制器與 API', link: '/tidb/controllers-api' },
      { text: '外部整合', link: '/tidb/integration' },
    ]
  },
]

const kafkaSidebar = [
  {
    text: '📖 Apache Kafka 總覽',
    items: [
      { text: '專案簡介', link: '/kafka/' },
      { text: '系統架構', link: '/kafka/architecture' },
      { text: '核心功能分析', link: '/kafka/core-features' },
      { text: '核心模組深度解析', link: '/kafka/modules' },
      { text: '外部整合', link: '/kafka/integration' },
    ]
  },
]

const kubernetesSidebar = [
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

export default withMermaid(defineConfig({
  base: '/kubevirt-learning-site/',
  title: 'KubeVirt 生態系原始碼分析',
  description: '深入分析 KubeVirt 生態系各專案原始碼 — 架構、元件、API 與實作細節',
  lang: 'zh-TW',
  vite: {
    plugins: [
      localLlmChatPlugin({
        projectRoot: process.cwd(),
        cliCommand: 'claude',
        model: 'sonnet',
      }),
    ],
  },
  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
    ['meta', { name: 'keywords', content: 'KubeVirt, CDI, Kubernetes, VM, 原始碼分析' }],
  ],
  themeConfig: {
    logo: '🖥️',
    siteTitle: 'KubeVirt 生態系分析',
    nav: [
      { text: '🏠 首頁', link: '/' },
      {
        text: '📦 專案',
        items: [
          { text: 'KubeVirt', link: '/kubevirt/architecture/overview' },
          { text: 'Containerized Data Importer (CDI)', link: '/containerized-data-importer/' },
          { text: 'Monitoring', link: '/monitoring/' },
          { text: 'Common Instancetypes', link: '/common-instancetypes/' },
          { text: 'Node Maintenance Operator', link: '/node-maintenance-operator/' },
          { text: 'Forklift', link: '/forklift/' },
          { text: 'NetBox', link: '/netbox/' },
          { text: 'Multus CNI', link: '/multus-cni/' },
          { text: 'TiDB', link: '/tidb/' },
          { text: 'Apache Kafka', link: '/kafka/' },
          { text: 'Kubernetes PV/PVC', link: '/kubernetes/' },
        ]
      },
    ],
    sidebar: {
      '/kubevirt/': kubevirtSidebar,
      '/containerized-data-importer/': cdiSidebar,
      '/monitoring/': monitoringSidebar,
      '/common-instancetypes/': instancetypesSidebar,
      '/node-maintenance-operator/': nmoSidebar,
      '/forklift/': forkliftSidebar,
      '/netbox/': netboxSidebar,
      '/multus-cni/': multusSidebar,
      '/tidb/': tidbSidebar,
      '/kafka/': kafkaSidebar,
      '/kubernetes/': kubernetesSidebar,
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/kubevirt/kubevirt' }
    ],
    footer: {
      message: '基於 Apache 2.0 授權',
      copyright: 'KubeVirt 生態系原始碼分析 — 為工程師而生'
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
  },
  mermaid: {
    theme: 'default'
  }
}))
