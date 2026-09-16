---
title: 如何开始
description: 使用 just、make 或 npm 在本地运行余时遗物，并将酒馆版本部署到静态网站。
---

# 如何开始

先在本地走进酒馆，再把可玩的版本部署到自己的站点。

## 准备环境

- **Node.js 22 LTS 与 npm**；包含 pre-commit 的版本需 **22.22.1 或更新补丁版本**。
- **Git**，用于获取源码。
- **just 或 make**，任选一个；也可以直接使用 npm。
- 建议使用较新的 Chrome 或 Edge，存档需要浏览器支持本地文件存储。

游戏源码目前位于私有仓库，需要先获得访问权限。公开的文档仓库用于构建本网站；下面的游戏命令都在游戏仓库根目录执行。

```sh
git clone --branch dev https://github.com/NevaMind-AI/remaining-time.git
cd remaining-time
```

## 本地运行

### 使用 just

```sh
just install
just dev
```

### 使用 make

```sh
make install
make dev
```

### 直接使用 npm

```sh
npm ci
npm run play:local
```

三种方式启动的都是当前酒馆版本，无需配置后端或模型密钥。打开终端显示的地址，默认是 `http://localhost:5173/ai-town/`；端口被占用时，以终端输出为准。

### 走进酒馆之后

| 操作 | 按键 |
| --- | --- |
| 移动 | WASD / 方向键 |
| 加速移动 | 按住 Shift |
| 与附近目标交互 | E |
| 普通背包 / 遗物收藏 | 1 / 2 |
| 主动等待 / 查看任务 | R / T |
| 隐藏或显示 HUD | H |

存档入口在**设置 → 存档**。你可以回看已经记录的过程，也可以在回放中选择一个历史时刻重新接手，详见[存档系统](/systems/#saves)。

## 开发中的格式化 {#formatting}

本节适用于包含 [游戏 PR #67](https://github.com/NevaMind-AI/remaining-time/pull/67) 的版本；使用前请确认当前分支已包含该改动。所有命令都在**游戏仓库根目录**执行。

### 启用 pre-commit

安装或更新依赖时，`npm ci` 或 `npm install` 会安装 lint-staged，并通过 `prepare` 自动启用 Git hook。已经安装本版本依赖，但安装时使用了 `--ignore-scripts`，执行一次：

```sh
npm run prepare
```

确认当前仓库配置：

```sh
git config --get core.hooksPath
```

应输出 `.githooks`。该设置位于本地 Git 配置中，不会随推送传给其他开发者，每位开发者都需要在自己的克隆中启用。

如果原本设置了其他 `core.hooksPath`，先合并已有 hook：`prepare` 会将路径设为 `.githooks`，原路径中的 hook 不会继续自动执行。

### 日常提交：增量自动格式化

编辑完成后，只暂存本次要提交的内容，再正常提交。以下以 `README.md` 为例：

```sh
git add README.md
git commit
```

pre-commit 会通过 lint-staged 调用 `prettier --write --ignore-unknown`，自动格式化本次暂存文件，并将结果更新到暂存区后继续提交。普通格式差异会直接修正，无需先处理检查失败。忽略规则继续生效，不支持的格式跳过；hook 不运行 lint、类型检查或测试。

也可以提前运行 `npm run fmt:staged`、`make fmt-staged` 或 `just fmt-staged`。这些命令会改写本次暂存文件并暂存格式化结果。

### 部分暂存与执行失败

使用 `git add -p` 只提交部分修改时，lint-staged 会暂时隐藏同文件中的未暂存修改，格式化并暂存本次内容后，再恢复未暂存修改。不要自行追加 `git add .`，以免带入其他修改。

如果文件有语法错误、Prettier 无法解析，或未暂存修改恢复时发生冲突，提交会停止并显示具体原因。lint-staged 默认创建备份并在失败时恢复原状态；按终端提示处理，必要时用 `git stash list` 查找它保留的备份。保留默认的 stash 与部分暂存保护选项，不使用 `--no-stash` 或 `--no-hide-partially-staged` 关闭保护。

### 存量检查与 Make／Just 入口

提交 hook 只覆盖暂存文件。要检查所有存量文件，运行以下任意一个命令：

```sh
npm run fmt:check
# 或
make fmt-check
# 或
just fmt-check
```

全量检查读取整个工作区，包含未暂存和未跟踪的受支持文件，并遵守忽略规则；没有暂存改动时也能运行。它不改写文件或暂存状态，用于了解存量格式情况。

| 操作 | npm | Make | Just |
| --- | --- | --- | --- |
| 启用提交 hook | `npm run prepare` | `make hooks-install` | `just hooks-install` |
| 自动格式化本次暂存内容 | `npm run fmt:staged` | `make fmt-staged` | `just fmt-staged` |
| 检查所有存量文件 | `npm run fmt:check` | `make fmt-check` | `just fmt-check` |
| 全量格式化工作区 | `npm run fmt` | `make fmt` | `just fmt` |

需要一次性修正存量格式时，使用 `make fmt`、`just fmt` 或 `npm run fmt`。这些命令可能修改本次任务之外的文件，运行后先查看 diff，再选择要暂存的改动；不会自动暂存。

自动 CI 仅在目标分支为 `main` 的 PR 上运行格式检查，也保留手动入口；向 `dev` 提交 PR 或推送不会自动运行该检查。

## 构建当前酒馆版本

在游戏仓库根目录执行：

```sh
npm run build:local
```

构建产物位于 `dist/`。要在本地预览产物：

```sh
npx vite preview --host 127.0.0.1
```

打开终端给出的地址，默认是 `http://127.0.0.1:4173/ai-town/`。预览服务用于本地查看产物，正式发布时使用静态网站托管。

::: tip 选择对应的构建命令
当前 `just build` / `make build` 对应 `npm run build`，用于仓库保留的 Convex 运行入口。部署本页介绍的酒馆版本，请使用 **`npm run build:local`**。
:::

## 部署到 Vercel

有游戏仓库访问权限的部署者，可以将该仓库导入 Vercel，选择 `dev` 作为需要发布的分支，并设置：

| 设置 | 值 |
| --- | --- |
| 项目根目录 | 游戏仓库根目录 |
| Framework Preset | Vite |
| Install Command | `npm ci` |
| Build Command | `npm run build:local` |
| Output Directory | `dist` |

保留仓库现有的 `vercel.json` 路由设置。部署完成后，通过 **`https://你的游戏域名/ai-town/`** 访问酒馆。

也可以使用其他静态托管服务：将 `dist/` 的内容挂载到 `/ai-town/`，确保该路径下的页面、素材和剧情内容都能被访问。正式站点使用 **HTTPS**，以满足浏览器存档所需的安全上下文条件。

`afterglow.xnnehang.top` 是文档站；游戏部署使用自己的站点地址。

## 更新版本与保留进度

存档属于当前浏览器与当前网站地址。本地开发、构建预览、线上站点各自保存进度；更换域名或端口不会自动迁移存档，清除网站数据也会删除存档。

刷新会恢复最近成功保存的位置。已有时间线保留开始时的剧情内容；想体验新版本剧情，可在存档窗口选“存档 0”，再选择“开始新游戏”。**这会清除现有时间线**，请在确认后操作。
