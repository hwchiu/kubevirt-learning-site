/**
 * config.js — VitePress 組裝層
 *
 * ⚠️  請勿在此處新增專案相關設定。
 *
 * - 站台設定（title / base / nav）→ 修改 site.config.js
 * - 新增專案 sidebar            → 在 sidebars/{project}.js 新增檔案
 *                                  並在 sidebar 對應表加一行
 */
import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { localLlmChatPlugin } from './plugins/localLlmChat.js'
import { siteConfig } from './site.config.js'

// ── Sidebar imports（新增專案時在這裡加 import + 對應表各一行）──
import kubevirt from './sidebars/kubevirt.js'
import cdi from './sidebars/containerized-data-importer.js'
import monitoring from './sidebars/monitoring.js'
import instancetypes from './sidebars/common-instancetypes.js'
import nmo from './sidebars/node-maintenance-operator.js'
import forklift from './sidebars/forklift.js'
import netbox from './sidebars/netbox.js'
import multus from './sidebars/multus-cni.js'
import minio from './sidebars/minio.js'
import tidb from './sidebars/tidb.js'
import kafka from './sidebars/kafka.js'
import kubernetes from './sidebars/kubernetes.js'

export default withMermaid(defineConfig({
  base: siteConfig.base,
  title: siteConfig.title,
  description: siteConfig.description,
  lang: 'zh-TW',
  vite: {
    plugins: [
      localLlmChatPlugin({
        projectRoot: process.cwd(),
        cliCommand: siteConfig.cliCommand,
      }),
    ],
  },
  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
    ['meta', { name: 'keywords', content: siteConfig.keywords }],
  ],
  themeConfig: {
    logo: siteConfig.logo,
    siteTitle: siteConfig.siteTitle,
    nav: [
      { text: '🏠 首頁', link: '/' },
      { text: '📦 專案', items: siteConfig.projectNav },
    ],
    sidebar: {
      '/kubevirt/': kubevirt,
      '/containerized-data-importer/': cdi,
      '/monitoring/': monitoring,
      '/common-instancetypes/': instancetypes,
      '/node-maintenance-operator/': nmo,
      '/forklift/': forklift,
      '/netbox/': netbox,
      '/multus-cni/': multus,
      '/minio/': minio,
      '/tidb/': tidb,
      '/kafka/': kafka,
      '/kubernetes/': kubernetes,
    },
    socialLinks: [
      { icon: 'github', link: siteConfig.githubLink }
    ],
    footer: {
      message: siteConfig.footerMessage,
      copyright: siteConfig.footerCopyright,
    },
    search: { provider: 'local' },
    outline: { label: '本頁目錄', level: [2, 3] },
    docFooter: { prev: '上一頁', next: '下一頁' },
    lastUpdated: { text: '最後更新' },
  },
  mermaid: { theme: 'default' },
}))
