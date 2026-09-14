import { defineConfig } from 'vitepress';
export default defineConfig({
  lang: 'zh-CN',
  title: '余时遗物',
  description: '余时遗物的每日更新与玩法指南。在酒馆中遇见人物、寻找遗物，决定时间的去向。',
  base: '/',
  head: [['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }]],
  themeConfig: {
    logo: { src: '/favicon.svg', alt: '余时遗物沙漏标志' },
    nav: [
      { text: '如何开始', link: '/guide/getting-started' },
      { text: '每日更新', link: '/daily-build/' },
      { text: '剧本时间线', link: '/story/timeline' },
      { text: '主要系统', link: '/systems/' },
    ],
    sidebar: [
      { text: '酒馆手记', items: [
        { text: 'Daily Build 更新', link: '/daily-build/' },
        { text: '剧本时间线', link: '/story/timeline' },
        { text: '如何开始', link: '/guide/getting-started' },
      ] },
      { text: '主要系统', items: [
        { text: '货币 · 时间有价', link: '/systems/#currency' },
        { text: '时间 · 世界继续', link: '/systems/#time' },
        { text: '收藏 · 拾起线索', link: '/systems/#collection' },
        { text: '任务 · 回应相遇', link: '/systems/#quests' },
        { text: '存档 · 重返那一刻', link: '/systems/#saves' },
      ] },
    ],
    footer: { message: '余时遗物 · 在余晖里，留下一点故事。' },
    socialLinks: [{ icon: 'github', link: 'https://github.com/XnneHangLab/remaining-time-docs' }],
    editLink: { pattern: 'https://github.com/XnneHangLab/remaining-time-docs/edit/dev/docs/:path', text: '编辑本页' },
    search: { provider: 'local' },
    outline: { label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
  },
});
