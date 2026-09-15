---
title: 世界架构 · 2026-09-15
description: 当前本地运行时的配置、状态与存储边界，以及 NPC、Story 与 ability、Scene 与 Map 的职责和编辑方式。
---

# 世界架构 · 2026-09-15

依据游戏仓库 `NevaMind-AI/remaining-time` 的实现提交
`84177e2ffc2abcd3f0143dd6783c1d96e49110f2`（[代码 PR #64](https://github.com/NevaMind-AI/remaining-time/pull/64)），内容版本 `npc-abilities-1`。本页描述该提交，集成状态见对应 PR。
适用于 `npm run play:local` 的本地 memory 模式，包括酒馆、客房与室外场景。下文区分当前实现与已确定的扩展方向；日期不等于存档格式版本。

## Config → State → Storage {#overview}

| 职责 | 保存什么 | 谁负责修改 |
| --- | --- | --- |
| **Config：世界定义** | 场景、地图、人物初始安排、剧本与能力参数，加载为 `Content` | 作者编辑 JSON；加载器组装和校验 |
| **State：本局事实** | 当前位置、活动阶段、变量、任务、物品数量与时间 | `MemoryWorld` 校验命令、推进系统并提交状态 |
| **Storage：记录与恢复** | 本局内容、输入事件、状态快照、请求去重信息与存档索引 | 引擎生成记录；浏览器存储适配负责落盘、加载和截断 |

```text
JSON 内容包 → 加载与校验 → 本局 Content → 初始化 State
                                            ↑       │
玩家命令 / 模拟推进 → 校验、计算、记录成功后提交 ──────┘
                                            │
                              内容 + 事件 + 档末状态 + 恢复信息
                                            │
                                     OPFS 文件与索引
                                            │
                              恢复续玩 / 逐事件回放与定位
```

这些是数据职责，不是三套数据库。`MemoryWorld` 同时维护运行状态和内存记录；界面发送命令、读取状态，不直接修改业务数据。
菜单开关和画面插值留在界面，人物当前位置、任务进度和活动期限进入 State。运行过程不回写作者的 JSON。

## Config：内容如何组织 {#config}

正式入口为 `public/content/demo/manifest.json`：

```text
public/content/demo/
  manifest.json          场景和剧本清单、起始 scene/anchor、版本
  scenes/*.json          场景身份、初始摆放、交互站位、场景连接
  npcs/*.json            NPC 身份及其 abilities
  stories/*.json         对白、条件、任务、商品目录与世界时钟
src/content/demo/
  maps/*.json            地图尺寸、碰撞、瓦片与美术图层
  animations/*.json      环境动画的帧与动画名
public/assets/           图片、音频等资源
```

`loadPackage()` 合并剧本，展开地图与动画帧引用，再由 `loadContent()` 校验，形成
`Content = { scenes, story, npcs? }`。`npcs` 按人物 ID 索引，旧内容可省略。重复 ID、未知字段和无效引用会被拒绝。

| 结构 | 关键字段与引用 |
| --- | --- |
| Manifest | `schema_version`、`content_version`、`scenes`、`stories`、可选 `npcs` 文件清单、`start:{scene,anchor}` |
| Scene | `id`、`name`、版本、`map`、`anchors`、`entities`；可选 `dining` 空间布局 |
| NPC 文件 | `id`、`name`、`character`、版本、`abilities`；可选 `image` |
| Story 文件 | `id`、版本、`vars`、`interactions`；可选任务、商品、线索与时钟 |
| 合并后的 Story | 多份文件的共同内容，`start` 与内容版本取自 manifest |

录制保存的是**展开后的 Content**。旧时间线不会因为作者修改了某个地图或剧本文件就改变；体验新内容需从存档 0 开启新时间线。
图片和音频仍按路径加载，资源字节没有嵌入存档。

## NPC：持续身份、能力与活动 {#entities}

**NPC 是持续存在的人物，顾客、服务员、听众是人物参与活动时的角色。** 人物保留同一个 ID、姓名、外观和位置，按需具备用餐、服务、演出等能力；普通 NPC 不需要餐饮配置。玩家状态目前仍独立保存。

新包通过 `Content.npcs` 明确人物身份与能力。普通 NPC 在 Scene 中以 `{id,position}` 摆放，姓名、角色与移动许可从 NPC 配置展开，sprite 和交互站位仍可由 Scene 提供。
代码中的 `Scene.entities` 与 `State.entities` 仍复用床、门、座椅等条目；这不要求每件装饰、商品或活动都拥有人物生命周期。

当前人物运行结构示意如下，`?` 表示可选；ID 是字典键，不在对象内重复保存：

```text
State.entities[id] = {
  name,
  appearance,          // character，以及可选 image、sprite、坐姿/演出图片
  sceneId,             // 空字符串表示场外
  position,            // [x,y]，格坐标
  orientation,         // 右0、下90、左180、上270
  path,                // 尚未走完的 [x,y] 路线
  moving,              // null 或 {target:{x,y}, arrivesAt, durationMs?}
  transit,             // null 或 {via:门ID, arrival:目标anchor}
  activity?,           // {seatedOn:座位ID}，活动结束或起身时解除
  movementSystem?      // 'dining' 表示沿用餐饮移动循环
}
```

具名人物初始化时建立身份，诗人首次到场前也可查询。顾客生成时分配稳定 ID，外观只抽取一次并保存。
离场不等于删除身份：顾客的消费分组结束后清理活动字段，保留人物基础记录；`DiningState.waiter` 和 `groups[].guests` 通过 ID 引用这些人物。
当前动态顾客仍由客流生成，离店后标记场外；尚没有室外去向或再次调度。身份保留已实现，人物后续生活安排仍待接入。

`getEntity(id)` 返回副本：未知 ID 为 `undefined`，场外人物的 `location` 为 `null`；当前所在位置读取 `location`。
`scene(id).entities` 筛选该场景内的条目，并提供当前坐标。查询副本不能用来写回世界。

## Story + ability：编排与执行 {#story-body}

**Ability 属于 NPC，描述能做什么；activity 保存此刻的活动；Story 编排对白、开放条件与任务推进。** 同一个 NPC 可具备多种能力，具备能力不代表正在执行。

例如诗人具备演出和教学能力；Story 在正式认识后开放学习入口，教学系统启动练习，达标后产生 `practice.completed` 事实推进任务。座位绑定属于活动，NPC 当前位置仍只有一份。

当前已经由 JSON 配置的内容包括：

| Story 内容 | 当前表达 |
| --- | --- |
| 初始变量 | `vars`，值为布尔值；运行值进入 `State.vars` |
| 对白与话题 | `interactions[目标ID]`，包含正文、首次对白、条件对白、话题与选项 |
| 条件 | 布尔变量、任务当前步骤、营业状态或待服务桌数 |
| 选项效果 | `set`、`pay_time`、`give_item`、`grant_clue`、`travel`、`move_entity`、`sleep` |
| 任务 | `tasks[].steps` 顺序推进；不同任务并行统计；可选触发条件和完成总结 |
| 能力衔接 | 用变量与任务条件开放现有交互入口，根据完成事实推进；能力参数在 NPC 配置中 |

任务按事实推进：移动完成、交互开始、选项确认、清桌完成、进入场景、练习完成。
`where` 过滤事实字段，`count` 统计次数，`collect` 统计不同值。每个任务只统计当前步骤，不追溯激活前的行为；选择启动 NPC 移动不代表 NPC 已抵达。

NPC 的 `abilities` 当前支持：

| 字段 | 归属与参数 |
| --- | --- |
| `movement`、`dialogue` | 可选 `true`；移动与交谈能力，对白由 Story 按人物 ID 提供 |
| `shop` | 商店名、报价、店存初值与补货 |
| `schedule` | 该人物的作息、入口与归位点 |
| `service` | 当前餐饮规则；能力所属 NPC 即服务员 |
| `performance` | 演出曲目、时间安排与提示；所属 NPC 即演出者 |
| `teaching` | 课程、判定与解锁参数；所属 NPC 即老师 |

NPC 文件由 manifest.npcs 加载，服务员／演出者／老师的 ID 不在能力内重复填写。
`abilitySettings()` 给既有系统提供参数视图，校验器也复用原规则；新包的 Story 不存放这些能力参数，录制保存完整 NPC 配置。
`getEntity().capabilities` 继续提供只读能力标记。

座位绑定已进入 `activity.seatedOn`；订单、餐饮阶段、演出与练习进度仍保存在相应共享系统状态中。
当前每个内容包各支持一份 service、performance、teaching，重复配置会被拒绝；这是现有执行系统的限制。

扩展流程保持简单：先用已有条件、效果和能力编排；确实缺少行为时，再补对应能力的配置、执行与结果，让 Story 能据真实结果推进。
物品交付／扣除，以及任务完成后自动发奖／写变量已登记为待实现需求；当前 `tasks[].completion` 只有总结文案。已有对话选项可以赠送物品和写变量。

## Scene + Map：编辑空间与画面 {#scene-map}

**Scene 放身份、站位和连接；Map 放地形、通行与显示。** 当前 Scene 使用：

```json
"map": { "source": "maps/woodland.json" }
```

路径相对逻辑内容包根目录；引用对象只写 `source`。地图 JSON 的实际源文件在 `src/content/demo/maps/`，由 Vite 发布，部署修改需要重新构建。
加载后 Scene 内的 `map` 已展开，不再是一条待解析路径。

| 想改什么 | 编辑位置 |
| --- | --- |
| NPC 身份、能力参数 | NPC 文件的 `name`、`character`、`abilities` 等字段 |
| NPC／物件初始位置、sprite、座位、隔柜台交互站位 | Scene 的 `entities`，使用 `sprite`、`seat`、`interactionOffsets` 等字段 |
| 出生点、楼梯落点、门的目的地 | Scene 的 `anchors` 与 `portal:{scene,anchor}`；Story 配开放条件及 `travel` |
| 通行格、格间阻挡 | Map 的 `collision`、可选 `blockedEdges` |
| 瓦片、环境动画、像素美术图层、玩家显示比例 | Map 的 `render`、可选 `art`、`playerScale` |
| 餐桌、柜台服务站位 | Scene 的 `dining` 布局；当前餐饮规则在服务员的 `abilities.service` |
| 台词、任务和交互结果 | Story 的 `interactions` 与 `tasks` |

### 矩阵、坐标与单位

- 地图有 `width`、`height`；新配置的 `render.matrixOrder` 为 `"yx"`。
- 碰撞是 `collision[y][x]`：`.` 可通行，`#` 阻挡。
- 瓦片是 `bgTiles[层][y][x]`、`objectTiles[层][y][x]`；每层 `height` 行、每行 `width` 个整数。一行矩阵对应一行文本，`-1` 表示不画，`0` 起是图集编号。
- **位置坐标仍是 `[x,y]`**，例如帐篷门 `[10,9]` 对应矩阵 `[9][10]`；入口、路线与交互偏移以格为单位。像素图层的位置、尺寸与偏移以像素为单位，视觉 `anchor` 是归一化锚点。
- 瓦片固定 32 像素。`showTiles` 显式控制瓦片绘制，当前室内为 `false`、室外为 `true`；瓦片编号与是否阻挡互相独立。

`render.animationSheets` 按名称关联图片与帧配置，`animatedSprites` 指定所用 sheet、动画名和像素位置／尺寸，新增动画名无需源码注册。
当前环境动画绘制在瓦片层之后，已有 `layer` 字段不提供任意层间穿插。
没有 `matrixOrder` 的旧录制仍按原列优先含义读取；转换集中在渲染适配处。

新增场景时，添加 Scene、Map 和 manifest 条目；需要通行时再配置两端 portal、落点与 Story 选项。
当前室外使用同一个本地世界与存档流程，只提供探索和通行，没有接入 Convex 模拟或室外 NPC 生成。

## Object：交互目标与活动归属 {#objects}

物件先是场景中的位置与交互目标；是否能操作，由显式配置和对应系统决定。**一张图片不会自动变成可交互对象。**

| 对象 | 配置与入口 | 活动／结果保存在哪里 |
| --- | --- | --- |
| 书、告示等可查看物件 | Scene 条目 + `interactions[ID]`；`interact` 后显示正文及选项 | 当前目标、话题和交互版本；效果写入变量、任务、线索等状态 |
| 床 | 普通物件交互 + `sleep` 选项，复用等待结算 | 玩家时间、余时及推进后的世界状态；当前睡眠没有上床姿态 |
| 座椅 | Scene 的 `seat`；`interact` 直接坐下，`stand` 起身 | 玩家 `seated:{entity,returnPosition}`；NPC 座位绑定在 `activity.seatedOn`，旧 Scene 初始 `seatedOn` 加载时转入活动 |
| 门、楼梯、帐篷入口 | Scene 的 `portal` + Story 条件与 `travel`；玩家尝试走进入口格触发 | 当前场景与玩家位置；入口不通过普通邻近交谈触发 |
| 脏餐桌 | `Scene.dining.tables` 的交互站位 + `clean` 命令 | `State.dining.groups` 与 `cleaning:{group,started,due,position}`；桌子没有独立活动日志 |
| 纯装饰和地形 | Map 的瓦片或 `art` 图层 | 只参与显示；通行另由碰撞配置决定 |

普通物件与 NPC 共用交互校验：目标在当前场景、处于可交互状态，并且玩家在相邻格或明确配置的 `interactionOffsets` 上。
选项与交易再次检查条件及 `interactionRevision`，防止提交过期操作；餐桌清理和 portal 走各自的站位／通行校验。

一次交互的持久变化进入整局 State，持续活动保存在执行它的系统中，历史统一进入世界录制。添加可阅读物件通常只改 Scene 与 Story；新增一种真实行为时才扩展对应能力。

## State：当前事实与一次提交 {#state}

| 状态区域 | 当前关键结构 |
| --- | --- |
| 玩家 | `sceneId`、`player:{x,y}`、`orientation`、`moving`；可选 `seated` |
| 身份与位置 | `entities[ID]`；服务员和顾客共享同一人物位置来源 |
| 交互 | `activeEntity`、`interactionRevision`、`dialogue`；可选话题、首次见面记录和对白随机状态；早期 `npc.reply` 字段仍承载当前正文 |
| 剧情与任务 | `vars`；`tasks[ID]` 的可选 `activated`、已完成步骤 `completed`、每步的 `{count,values}`；可选已获 `clues` |
| 交易 | 可选 `commerce`：`inventory[商品ID]`、`stock[商人ID][商品ID]`、可选补货期限 `nextRestock` |
| 时间 | `time` 为模拟毫秒；`storyTime`、`balance` 为剧情秒／生命秒；可选 `clock` 保存当前流速与段内进度 |
| 能力进度 | 可选 `schedules`、`dining`、`performance`、`practice`，保存作息、服务、演出与学习事实 |

移动截止点、清理期限使用模拟毫秒；营业与作息使用剧情时间；演出和练习有各自的相对毫秒时间轴。记录的 `recordedAt` 是墙钟时间戳，不驱动回放。

命令由 `execute()` 处理，模拟由 `advance(ms)` 推进：复制当前状态为草稿，校验并计算，记录成功后提交状态与请求缓存。
交易的扣时、增减物品和店存一起提交。失败不提交部分业务效果；新规则允许受阻移动只更新朝向。
请求 ID 用于去重，避免重试重复执行。

`inspect()` 仅返回 State 副本。完整恢复还需要本局 Content、规则、初始化参数、事件序号与请求缓存，不能仅把这个副本存下来再赋回去。

## Storage：记录、恢复与回放 {#storage}

每段 `Recording` 保存以下结构；它是输入与完整状态的记录，不是纯命令日志：

| 字段 | 用途 |
| --- | --- |
| `format`、`rules` | 当前格式 `remaining-time-run-1`；新运行规则 `memory-world-4` |
| `content` | 本局展开后的场景、地图、动画帧、NPC 能力配置与 Story |
| `config` | 模拟步长与早期 NPC 初始参数，区别于完整世界定义 Content |
| 可选 `startSequence`、`eventCount` | 全局起始游标与本段事件数；省略起点时为 0 |
| `events[]` | 每条的 `sequence`、`recordedAt`、命令或推进原因 `cause`、`result`、提交后完整 `state` |
| `finalState` | 档末状态 |
| `snapshot` | 当前写入格式为 `memory-world-snapshot-1`，补充结束序号与请求去重缓存；旧档可能缺少 |

浏览器使用同一来源的 OPFS：

```text
remaining-time-saves/
  manifest.json      head:{revision,slot,sequence} + slots:[文件及摘要]
  <uuid>.json        一段 Recording
```

存档 manifest 与内容 manifest 是两个不同文件。索引负责定位与展示，不能替代完整状态。
自动保存每秒检查，达到 1000 个事件后保存最前面的 1000 条：**先写记录文件，再发布索引，成功后释放内存前缀**。
Web Lock 与 head revision 协调同来源页面的读写；失败时保留有效索引和未保存进度。

### 四条使用路径 {#flows}

| 操作 | 当前行为 |
| --- | --- |
| 新开时间线 | 用当前 Content 初始化，确认后替换现有时间线 |
| 刷新／加载 | 使用存档嵌入的 Content，直接恢复档末状态、序号与去重缓存；加载早期槽位会清除未来 |
| 观看／定位 | 从段起点或检查点执行原命令与推进，逐事件比较结果和录制状态；观看本身不截断 |
| 从回放游标续玩 | 保留已播放前缀，清除之后的记录，再追加新事件 |

槽位是同一时间线的连续片段；当前不保留多条并行分支。存档嵌入内容，但页面启动仍需加载部署内容，媒体资源也仍依赖外部文件。

旧规则 `memory-world-1/2/3` 在录制边界转换状态布局：旧 `seatedOn` 恢复为活动绑定，规则1／2还需转换服务员与顾客的嵌套布局。
运行内部使用统一状态，保存仍沿用该时间线原规则与原 Content，不自动升级为版本4。
旧档缺少的已离场顾客身份无法补回。更早的存档可补齐快照元数据，这与更换游戏规则是两件事。

## 当前边界与源码入口 {#limits}

每条事件携带完整状态，每段也保存完整 Content；离场 NPC 的身份保留会增加体积。
内存段保护上限为 100000 个事件或 16 MiB 累计 UTF-8 事件载荷；不足 1000 条就触及预算时，当前暂停并保留进度，不自动生成更短的存档。
未成功落盘的尾部进度不保证保留，当前没有云同步。

本地可回放依赖记录的输入、受控随机状态与支持的规则。外部 Agent 的观察权限、动作发现及异步决策录制仍未接入。

### 源码入口 {#sources}

以下路径相对游戏仓库，供有源码访问权限的读者定位：

| 入口 | 职责 |
| --- | --- |
| `prototype/package.ts`、`content.ts`、`mapData.ts` | 内容加载、配置与地图校验 |
| `prototype/map.ts`、`src/components/PixiStaticMap.tsx` | 地图适配与渲染 |
| `prototype/abilities.ts` | NPC 能力定义与执行系统参数视图 |
| `prototype/entities.ts`、`world.ts` | 身份、查询、State、命令和提交 |
| `prototype/taskFacts.ts`、`dining.ts`、`schedules.ts`、`performance.ts`、`practice.ts` | 任务事实与具体能力 |
| `prototype/entityRecording.ts`、`replay.ts` | 新旧布局、恢复、回放与定位 |
| `src/lib/autosaves.ts`、`src/components/AutoSaves.tsx` | OPFS、索引与时间线操作 |
| `src/components/LocalGame.tsx` | 内容入口、玩家输入、模拟推进与界面 |

本文只描述页首代码版本；玩家可见的存档规则见[主要系统](/systems/#saves)。
