# remaining-time 文档

公开文档站，使用 VitePress，默认分支为 `dev`。站点由本仓库的 GitHub Actions 构建并发布到 GitHub Pages。

## 本地编辑

```sh
npm ci
npm run dev
```

页面位于 `docs/`，站点配置位于 `docs/.vitepress/config.mts`。`npm run build` 构建，`npm run preview` 预览。

## 在游戏仓库中编辑

本仓库以 `website/` submodule 挂载。进入该目录后，按 [AGENTS.md](AGENTS.md) 创建文档工作分支，提交到本仓库，使用 `xnne-bot` 开 PR，目标为 `dev`。

游戏仓库固定具体文档提交。文档 PR 合入后，若需要同步游戏工作区，再更新游戏仓库中的指针；不要引用尚未推送或尚未合入的提交。

## 发布

仓库 Settings → Pages 的 Source 使用 GitHub Actions。合入 `dev` 的站点变更触发部署，首次部署成功后地址为：

https://xnnehanglab.github.io/remaining-time-docs/
