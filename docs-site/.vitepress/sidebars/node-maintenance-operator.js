export default [
  {
    text: '📖 Node Maintenance Operator',
    items: [
      { text: '專案總覽', link: '/node-maintenance-operator/' },
      { text: '設計動機與存在價值', link: '/node-maintenance-operator/design-motivation' },
    ]
  },
  {
    text: '系統架構',
    collapsed: false,
    items: [
      { text: '系統架構', link: '/node-maintenance-operator/architecture' },
      { text: '部署與設定', link: '/node-maintenance-operator/installation-and-deployment' },
    ]
  },
  {
    text: '核心功能',
    collapsed: false,
    items: [
      { text: 'NodeMaintenance CRD 規格', link: '/node-maintenance-operator/crd-specification' },
      { text: '節點排空工作流程', link: '/node-maintenance-operator/node-drainage-process' },
      { text: 'Admission Validation', link: '/node-maintenance-operator/validation-webhooks' },
      { text: 'Lease 分散式協調', link: '/node-maintenance-operator/lease-based-coordination' },
      { text: 'Taint 管理與 Cordoning', link: '/node-maintenance-operator/taints-and-cordoning' },
    ]
  },
  {
    text: '維運進階',
    collapsed: true,
    items: [
      { text: 'RBAC 與權限', link: '/node-maintenance-operator/rbac-and-permissions' },
      { text: '故障排除', link: '/node-maintenance-operator/troubleshooting-and-debugging' },
      { text: '事件與可觀測性', link: '/node-maintenance-operator/event-recording-and-observability' },
    ]
  },
]
