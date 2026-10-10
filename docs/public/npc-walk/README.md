# NPC 行走预览快照

站点入口：`/npc-walk/locomotion/index.html`。

- 游戏来源：`NevaMind-AI/remaining-time` PR #147。
- 固定提交：`bd9c0cb728eb26286cbf867700e5325458d16c8a`。
- 来源路径：`public/assets/room-npcs/locomotion/{index.html,manifest.json}`，以及清单中 29 个角色的 `public/assets/room-npcs/{id}.{png,json}`。
- 上游动画素材来源：`MrMaii/project-myrmidon-map-prototype@6ac2b9a2735ca4fa142421593fe47765081ac4cd`。

按用户要求将此预览与所需图集发布到公共文档站。PNG、角色 JSON 与清单原样复制；HTML 增加返回文档站入口、快照与演示速度说明，并调整联网加载失败提示。卡片进入视口及上下 200px 范围时独立加载素材，加载完成立即绘制，不等待其他角色；提供逐卡片状态与失败重试。暂停、逐帧、速度选择与下载功能沿用来源页面。

这是独立动画演示，不包含游戏后端、自主移动行为或实时游戏状态；位移速度未与游戏校准。构建及访问不请求私有仓库。后续更新时，从选定游戏提交重新复制清单、页面及清单引用的全部 PNG/JSON，再保留上述站点文案、按需加载逻辑并更新提交号。
