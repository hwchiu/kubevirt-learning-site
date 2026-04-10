export default [
  {
    text: '📖 Cilium 總覽',
    items: [
      { text: '專案簡介', link: '/cilium/' },
    ]
  },
  {
    text: '🏗️ 系統架構',
    items: [
      { text: '系統架構總覽', link: '/cilium/architecture' },
      { text: 'eBPF Datapath 深度解析', link: '/cilium/ebpf-datapath' },
      { text: '身份識別與安全模型', link: '/cilium/identity-security' },
    ]
  },
  {
    text: '🌐 網路核心',
    items: [
      { text: '網路架構', link: '/cilium/networking' },
      { text: '負載均衡與 kube-proxy 替代', link: '/cilium/load-balancing' },
      { text: 'BGP 控制平面', link: '/cilium/bgp' },
      { text: 'ClusterMesh 多叢集架構', link: '/cilium/clustermesh' },
    ]
  },
  {
    text: '🔐 安全與政策',
    items: [
      { text: '網路政策 (NetworkPolicy)', link: '/cilium/policy' },
      { text: '加密傳輸 (WireGuard & IPSec)', link: '/cilium/encryption' },
    ]
  },
  {
    text: '📋 參考資料',
    items: [
      { text: 'CRD 規格完整參考', link: '/cilium/crd-reference' },
    ]
  },
  {
    text: '🔭 可觀測性',
    items: [
      { text: 'Hubble 可觀測性平台', link: '/cilium/hubble' },
    ]
  },
]
