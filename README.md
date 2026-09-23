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

## 房间布局预览

`/rooms/` 提供 26 间房的原始完整图、普通空背景、黑框空背景，以及由浏览器自动绘制的初始拼装布局。运行背景以导出的地图为准；缺失版本明确标注，NPC 可切换显示。

快照更新需要本地能读取指定游戏提交，但站点部署不需要游戏仓库、令牌或正在运行的游戏：

```sh
python scripts/export-room-preview.py --repo ../remaining-time --ref <完整游戏提交号>
```

导出器通过 Git 读取固定提交，不读取游戏工作区未提交文件。它生成 `docs/public/room-preview/` 的 PNG 和 `docs/.vitepress/theme/room-preview/generated/` 的布局清单、原样复用的游戏定位函数及许可文本；重新导出会替换这两个位置的对应生成文件。不要手改生成数据。所选提交必须含有原始房间参考和运行资产；缺少必需图层、非 sprite 实体、瓦片地图或暂未适配的坐客会停止导出，避免交付不完整拼图。

游戏来源为 NevaMind-AI/remaining-time；初始快照来自已合入的 #103，提交 `92d516217f37671e3f8c3a4ed00ba639e1c179e0`。图片逐字节保留，清单记录来源路径、尺寸和 SHA-256；源素材署名和许可见该游戏提交的 LICENSE 及相应资产说明，未新增素材授权声明。`generated/assets.ts` 和 `generated/LICENSE` 同样直接来自该提交。

第四个视图采用 Canvas 2D，复用游戏 `visualPlacement`，按 `LocalGame` 的 art／实体顺序及深度稳定排序，门逐格绘制，NPC 取初始朝向 90° 的首个待机帧。更新快照时应复核 `LocalGame.tsx`、`RoomNpc.tsx` 与 `prototype/entities.ts` 的规则是否变化。此页面是初始静态布局对照，不模拟玩家、剧情、存档或 NPC 行走，也不承诺与 PixiJS 逐像素一致。

## 发布

仓库 Settings → Pages 的 Source 使用 GitHub Actions，自定义域名设置为 `afterglow.xnnehang.top`。合入 `dev` 的站点变更触发部署，网站地址为：

https://afterglow.xnnehang.top/

DNS 使用 CNAME：`afterglow` → `xnnehanglab.github.io`。VitePress 的 base 为 `/`。

工作流通过 `upload-pages-artifact` 和 `deploy-pages` 直接发布构建产物；源码保存在 `dev`。域名由 Pages 设置维护，HTTPS 需等待 DNS 生效和 GitHub 证书签发。
