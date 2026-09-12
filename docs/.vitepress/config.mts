import { defineConfig } from 'vitepress';
export default defineConfig({
  lang: 'zh-CN',
  title: 'remaining-time',
  description: 'remaining-time 游戏指南与公开文档',
  base: '/',
  themeConfig: {
    nav: [{ text: '开始阅读', link: '/guide/getting-started' }],
    sidebar: [{ text: '指南', items: [{ text: '关于文档', link: '/guide/getting-started' }] }],
    socialLinks: [{ icon: 'github', link: 'https://github.com/XnneHangLab/remaining-time-docs' }],
    editLink: { pattern: 'https://github.com/XnneHangLab/remaining-time-docs/edit/dev/docs/:path', text: '编辑本页' },
    search: { provider: 'local' },
    outline: { label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
  },
});
