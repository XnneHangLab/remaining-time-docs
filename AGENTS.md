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
- 正式域名为 `https://afterglow.xnnehang.top/`，VitePress base 使用 `/`。Pages Source 为 GitHub Actions，通过官方 artifact 部署；自定义域名在仓库 Pages 设置中维护，DNS CNAME 指向 `xnnehanglab.github.io`。
- 文档 PR 合入后，游戏仓库按需更新 submodule 指针。游戏仓库只记录已推送且已合入文档 `dev` 的确切提交；squash 合并后必须重新获取合并后的 SHA。
- 纯文档修改不强制另开游戏 PR；需要更新游戏工作区文档版本时，可将指针更新并入相关游戏 PR。

## 网站内容范围

website 当前只发布以下内容：

| 栏目 | 编写方式 |
| --- | --- |
| 如何开始 | 依据游戏仓库实际命令介绍 just / make / npm 本地运行、构建与部署；区分游戏和文档工作目录，明确源码访问条件 |
| daily build 更新 | 按日期或实际构建版本记录已发生的变化；有真实构建链接时再附上，不编造版本、日期或发布状态 |
| 剧本时间线 | 按时间或事件阶段，以人可读的场景、人物、对白概要、前后条件和分支结果叙述 |
| 编剧 Agent 能力表与 Skill | 说明可支持的编剧行为、能力边界、工作流程和 Skill 使用方法，示例使用自然语言 |
| 架构快照 | 标注日期、游戏代码提交号和适用模式；解释世界定义、运行状态、记录与持久化恢复的实际职责、数据流和边界 |
| 主要系统 | 介绍货币、时间流逝、收藏、任务与存档系统的设计目的、玩家可见规则与体验；存档强调可回放、从任意已记录时刻继续，以及继续会清除后续记录 |

- 允许发布经代码核对的架构快照，明确其适用版本与可能过时的范围。只展开理解职责和数据流所需的类型、字段与源码入口，不批量复制原始技术合同或接口清单。
- 编剧 Skill 按面向编剧的说明组织；涉及内部路径、JSON 字段或源码实现的部分不直接搬运到网站。未实现的能力不能写成已支持。
- 项目处于高速迭代期，不为每次代码改动自动新增实现文档。架构快照保留版本依据；修正事实错误可修改原文，职责或存储方式发生实质变化时另写新日期快照并相互链接。
- 游戏仓库顶层 `docs/` 暂停新增与扩写；被架构快照覆盖的旧说明可清理并修复引用，仍有独立价值的视觉说明、设计参考及测试依赖保留。本仓库 `docs/` 是 website 的页面目录，按上述范围编写。

## 内容边界与本地开发

- 网站页面、VitePress 配置与站点构建依赖由本仓库维护；游戏运行代码和原始素材由游戏仓库维护。
- 公共内容逐篇整理，不批量复制私有仓库的文档、工作日志、环境配置、存档或未授权素材。不要维护两份需要手工同步的同一篇正文。
- 使用 npm，提交 package-lock.json；运行 `npm ci` 安装，`npm run dev` 本地编辑，`npm run build` 构建，`npm run preview` 预览产物。
- 延续快速迭代：默认不额外跑本地测试、构建或浏览器验收；用户要求或解决当前实际问题时再做最小检查。未验证时如实说明。
- 不提交 node_modules、缓存或构建产物，不在私有游戏仓库添加站点构建 CI。

## 提交与 PR

- 标题使用 `<gitmoji> <type>: <subject>`，PR 按 `.github/pull_request_template.md` 填写。
- 每个 Agent 协助完成的提交在实际消息末尾保留署名。Codex 使用 `Co-authored-by: Codex <codex@openai.com>`；从 PI_MODEL 确认模型后另写 `AI-Model: <模型 ID>`，不猜测。
- trailer 段落前留真实空行，优先使用 UTF-8 消息文件与 `git commit -F`。提交后、推送前读取实际消息及 `git interpret-trailers --parse` 结果；squash 合并也保留署名。
