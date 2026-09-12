---
title: 如何开始
description: 使用 just、make 或 npm 在本地运行余时遗物，并将酒馆版本部署到静态网站。
---

# 如何开始

先在本地走进酒馆，再把可玩的版本部署到自己的站点。

## 准备环境

- **Node.js 22 LTS 与 npm**。
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

三种方式启动的都是当前酒馆版本，无需配置后端或模型密钥。打开终端显示的地址，默认是 **http://localhost:5173/ai-town/**；端口被占用时，以终端输出为准。

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

## 构建当前酒馆版本

在游戏仓库根目录执行：

```sh
npm run build:local
```

构建产物位于 `dist/`。要在本地预览产物：

```sh
npx vite preview --host 127.0.0.1
```

打开终端给出的地址，默认是 **http://127.0.0.1:4173/ai-town/**。预览服务用于本地查看产物，正式发布时使用静态网站托管。

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
