# remaining-time-docs · Agent 协作约定

## 仓库与账号

- 本仓库是公开的 VitePress 文档站：`XnneHangLab/remaining-time-docs`。
- 在游戏工作区中通常位于 `website/` submodule 内；这里是独立 Git 仓库。执行 git、gh、npm 前先确认当前工作目录与 remote。
- 本仓库所有 GitHub 写操作和 PR 使用 `xnne-bot`。显式选取该账号凭据，不依赖 gh 当前默认账号；不要把令牌写入文件、remote URL、日志或工作流。
- 单独克隆时也遵守本文件；不依赖父仓库或个人目录中的 AGENTS.md。

## 分支与发布

- 默认分支为 `dev`。同步默认 fast-forward 更新 `origin/dev`，新工作分支从最新 `dev` 创建，PR 显式指定 `--repo XnneHangLab/remaining-time-docs --base dev`。
- 在 submodule 的 detached HEAD 上编辑前，先创建命名工作分支。同步遇到未提交改动时先保留工作，不执行 reset --hard 或强制覆盖。
- `dev` 的站点相关变更由公共仓库的 GitHub Actions 构建并部署到 GitHub Pages；工作流仅使用本仓库的 GITHUB_TOKEN，不需要私有游戏仓库的访问令牌。
- 文档 PR 合入后，游戏仓库按需更新 submodule 指针。游戏仓库只记录已推送且已合入文档 `dev` 的确切提交；squash 合并后必须重新获取合并后的 SHA。
- 纯文档修改不强制另开游戏 PR；需要更新游戏工作区文档版本时，可将指针更新并入相关游戏 PR。

## 内容边界与本地开发

- 页面、VitePress 配置与站点构建依赖由本仓库维护；游戏运行代码、原始素材和内部工程文档由游戏仓库维护。
- 公共内容逐篇整理，不批量复制私有仓库的文档、工作日志、环境配置、存档或未授权素材。不要维护两份需要手工同步的同一篇正文。
- 使用 npm，提交 package-lock.json；运行 `npm ci` 安装，`npm run dev` 本地编辑，`npm run build` 构建，`npm run preview` 预览产物。
- 延续快速迭代：默认不额外跑本地测试、构建或浏览器验收；用户要求或解决当前实际问题时再做最小检查。未验证时如实说明。
- 不提交 node_modules、缓存或构建产物，不在私有游戏仓库添加站点构建 CI。

## 提交与 PR

- 标题使用 `<gitmoji> <type>: <subject>`，PR 按 `.github/pull_request_template.md` 填写。
- 每个 Agent 协助完成的提交在实际消息末尾保留署名。Codex 使用 `Co-authored-by: Codex <codex@openai.com>`；从 PI_MODEL 确认模型后另写 `AI-Model: <模型 ID>`，不猜测。
- trailer 段落前留真实空行，优先使用 UTF-8 消息文件与 `git commit -F`。提交后、推送前读取实际消息及 `git interpret-trailers --parse` 结果；squash 合并也保留署名。
