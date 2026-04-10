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
    ]
  },
  {
    text: '🔐 安全與政策',
    items: [
      { text: '網路政策 (NetworkPolicy)', link: '/cilium/policy' },
    ]
  },
  {
    text: '🔭 可觀測性',
    items: [
      { text: 'Hubble 可觀測性平台', link: '/cilium/hubble' },
    ]
  },
]
