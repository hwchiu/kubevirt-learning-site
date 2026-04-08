export default [
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
  {
    text: '📝 隨堂測驗',
    items: [
      { text: 'KubeVirt 架構測驗', link: '/kubevirt/quiz' },
    ]
  },
]
