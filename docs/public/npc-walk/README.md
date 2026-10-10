# Player 与 NPC 行走预览快照

站点入口：`/npc-walk/locomotion/index.html`，共 30 个角色，主角排在首位。

## 素材来源

- NPC 与原预览页面：`NevaMind-AI/remaining-time` PR #147，固定提交 `bd9c0cb728eb26286cbf867700e5325458d16c8a`。来源为 `public/assets/room-npcs/locomotion/{index.html,manifest.json}` 及原清单中 29 个 NPC 的 `public/assets/room-npcs/{id}.{png,json}`。
- 29 个 NPC 的上游动画素材来源：`MrMaii/project-myrmidon-map-prototype@6ac2b9a2735ca4fa142421593fe47765081ac4cd`。
- Player：游戏 `dev` 固定提交 `c987409a79f17e1f359f91cb324b34444620884d`，将 `public/assets/room-player/player.png` 与 `data/spritesheets/room-player.json` 原样复制为本站 `player.png/json`。已沿 `App → LocalGame → RoomPlayer` 核对：`remaining-time` 内容包使用这套运行时素材，版本为 `player-workwear-generated-v2.1`，帧尺寸 40×48，walk 每帧 90ms。不是 `room-npcs/player-preview` 的独立自制候选。

## 网站适配

按用户要求发布此预览及所需图集。PNG、角色 JSON 原样复制；清单首位加入运行时 Player。绘制直接读取 Player 的 `animations[direction].walk` 或 NPC 的 `walk-front/left/right/back`，保留原始帧序、时长与逐帧脚点。帧按原始宽高比将长边缩放为 128px，脚点对齐同一演示轨道。

HTML 增加返回站点入口与快照说明。卡片进入视口及上下 200px 范围时独立加载，完成立即绘制，不等待其他角色；提供逐卡片状态与失败重试。暂停、逐帧、速度选择与下载功能沿用来源页面。

这是独立动画演示，不包含游戏后端、自主移动或实时游戏状态；位移速度与展示缩放未与游戏场景校准。构建及访问不请求私有仓库。后续更新从选定提交复制页面、清单及所需图集与元数据，保留运行时 Player 条目、两种动画索引、站点文案、按需加载与等比绘制逻辑，并更新来源提交号。
