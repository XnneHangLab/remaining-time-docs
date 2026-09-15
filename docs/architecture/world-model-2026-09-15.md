---
title: 世界数据模型 · 2026-09-15
description: 余时遗物本地酒馆运行时的架构快照，说明世界定义、运行状态，以及记录、持久化与恢复的职责和数据流。
---

# 世界数据模型 · 2026-09-15

这是 **2026 年 9 月 15 日的架构快照**，依据游戏仓库 `NevaMind-AI/remaining-time` 的提交
`dba56a4c6cb074e40a7984664b542bfac0465c1b`
整理。本文描述该提交的实现，后续代码可能变化；日期不代表存档格式版本，也不代表一份持续跟随最新代码的接口承诺。

适用范围是以 `npm run play:local` 启动的
**memory 模式酒馆**。本文的源码路径供有游戏仓库访问权限的读者定位，不要求公共站点读者能够打开私有源码。

## 三种职责，而非三个数据库 {#overview}

用 **World Config → World State → Storage**
理解当前系统是合理的。更准确的名称是：**世界定义、运行状态、记录与持久化恢复**。它们区分数据的用途和修改责任，不意味着三套数据库，也不是只能从上往下调用的三层服务。

| 职责                         | 回答的问题                           | 当前实现                                                 |
| ---------------------------- | ------------------------------------ | -------------------------------------------------------- |
| World Config · 世界定义      | 这个世界有哪些场景、规则和初始安排？ | JSON 内容包，经加载和校验后形成 `Content`                |
| World State · 运行状态       | 这局世界现在进行到哪里？             | `MemoryWorld` 持有的 `State`                             |
| Storage · 记录、持久化与恢复 | 如何保留历史、恢复进度或重新播放？   | 引擎事件记录、快照与回放，以及浏览器 OPFS 文件和存档索引 |

其中 `MemoryWorld`
同时负责运行状态和内存中的记录；浏览器文件模块负责把记录保存下来。因此“第三层”横跨引擎与存储适配，不是一个独立的 Storage 类。

```text
作者的内容包 ──加载、校验──→ 本局固定的 Content
                                  │
                                  ▼
                         MemoryWorld 初始化 State
                                  │
玩家命令 / 模拟推进 ──→ 校验并计算下一状态
                                  │
                       先记录，再提交 State 与请求缓存
                                  │
                                  ▼
                  当前段录制：内容 + 事件 + 恢复信息
                                  │
                       写 JSON → 发布存档索引
                                  │
                       成功后释放已保存的内存前缀
                                  │
                  ┌───────────────┴────────────────┐
                  ▼                                ▼
           直接恢复档末快照                 从起点逐事件执行并校验
                  │                                │
                  ▼                                ▼
                续玩                         观看 / 定位 / 续玩
```

界面是这些职责的使用者：发送命令、展示状态、调用存档功能。菜单是否展开、按键是否按住、画面插值到哪一帧，并不都属于游戏世界的持久状态。

## 第一层：World Config，定义世界 {#config}

### 字段阅读约定

下面用 TypeScript 形状描述该版本实际接收或保存的数据，便于查看必填、可选和嵌套关系；它不是新增的 JSON 格式。`?`
表示字段可省略，`| null` 表示字段存在但当前没有动作，`Record<string, T>`
表示以 ID 为键的字典。JSON 文件不包含类型别名或注释。

`XY` 表示 `[x, y]` 数组，`Position` 表示 `{ x, y }`
对象；两种形式在当前实现中同时存在，不可任意替换。场景／人物坐标以格为单位，图层
`position`、`size`、`offset` 与显示深度以像素为单位，`anchor`
是 0–1 的归一化锚点。朝向使用角度：右 0、下 90、左 180、上 270。

### 内容清单、文件和加载结果

```ts
type XY = [number, number];
type NumberRange = [number, number];
type Position = { x: number; y: number };
type Start = { scene: string; anchor: string };

type ContentManifest = {
  schema_version: '1.0';
  content_version: string;
  start: Start;
  scenes: string[]; // 场景文件的相对路径
  stories: string[]; // 剧本文件的相对路径
};

type StoryFile = StoryBody & {
  schema_version: '1.0';
  content_version: string;
  id: string; // 内容包内唯一；单个剧本文件不填写 start
};

type Story = StoryBody & {
  schema_version: '1.0';
  content_version: string;
  start: Start; // 合并时取自 manifest
};

type Content = {
  scenes: Scene[];
  story: Story; // 多份 StoryFile 合并后的定义
};
```

内容清单的 `scenes`／`stories` 是路径；加载结果 `Content.scenes`／`Content.story`
才是对象。录制保存加载结果，不保存一份待联网解析的文件清单。

### StoryBody：变量、对白、选项与任务 {#story-body}

`StoryBody` 是本文为剧本文件与合并后的 `Story` 提取的共同字段形状。源码直接定义
`Story`，JSON 中不需要增加 `StoryBody` 包装层。

```ts
type StoryBody = {
  vars: Record<string, boolean>;
  interactions: Record<
    string,
    DialogueText & {
      firstText?: string;
      topics?: Record<string, DialogueText>;
      choices: Choice[];
    }
  >;
  tasks?: Task[];
  items?: Item[];
  shops?: Record<string, Shop>; // 商人实体 ID → 商店
  clues?: { id: string; slot: number; text: string; source: string }[];
  clock?: ClockSettings;
  dining?: DiningSettings;
  schedules?: Record<string, NpcSchedule>;
  performance?: PerformanceSettings;
  practice?: PracticeSettings;
};

type Condition =
  | { var: string; equals: boolean }
  | { task: string; step: string }
  | { diningOpen: boolean }
  | { diningPendingAtLeast: number };

type DialogueText = {
  text: string;
  variants?: string[];
  replies?: { when: Condition; text: string; variants?: string[] }[];
};

type Choice = {
  id: string;
  text: string;
  topic?: string;
  opens?: string;
  when?: Condition;
  effects: Effect[];
};

type Effect =
  | { op: 'set'; var: string; value: boolean }
  | { op: 'pay_time'; seconds: number }
  | { op: 'grant_clue'; clue: string }
  | { op: 'give_item'; item: string; quantity: number }
  | { op: 'travel' }
  | { op: 'move_entity'; entity: string; path: XY[]; via?: string; arrival?: string }
  | { op: 'sleep'; selectHours: true }
  | { op: 'sleep'; seconds: number }
  | { op: 'sleep'; nextDayAt: number };

type Task = {
  id: string;
  title: string;
  background?: string;
  description: string;
  trigger?:
    | { var: string; equals: boolean }
    | { diningPendingAtLeast: number }
    | { diningDirtyAtLeast: number };
  completion?: { background: string; description: string };
  steps: {
    id: string;
    text: string;
    background?: string;
    description?: string;
    condition: {
      event:
        | 'movement.completed'
        | 'interaction.started'
        | 'choice.confirmed'
        | 'dining.cleaned'
        | 'scene.entered'
        | 'practice.completed';
      where?: Record<string, string>;
      collect?: string;
      count: number;
      items?: { value: string; label: string }[];
    };
  }[];
};
```

`interactions` 以实体 ID 为键，`topics` 以话题名为键。`opens` 切换话题，`effects`
才执行业务效果。任务的 `steps` 顺序推进，不同任务可以同时推进；`collect`
按不同值计数，否则按匹配事实次数计数。

任务事实可用字段分别是：移动的 `direction`，交互的 `entityId`，选项的
`entityId`／`choiceId`，清理与入场的 `sceneId`，练习的 `entityId`／`lessonId`。`where`、`collect`
引用这些字段，而不是任意 State 路径。

### 商品、时钟、客流与作息配置

```ts
type Item = {
  id: string;
  name: string;
  image: string;
  category: string;
  quality: string;
  description: string;
  kind?: 'relic';
  initiallyOwned?: boolean;
  slot?: number;
  effectDescription?: string;
};

type Shop = {
  name: string;
  offers: { item: string; buySeconds: number; sellSeconds: number; stock: number }[];
  restock?: { intervalSeconds: number };
};

type ClockSettings = {
  initialBalanceSeconds?: number;
  startTimeSeconds?: number;
} & (
  | { realSecondsPerTick: number; gameSecondsPerTick: number; idlePauseSeconds: number }
  | { rate: number } // 旧的连续倍率格式，与分段格式二选一
);

type DiningSettings = {
  scene: string;
  seed: number;
  maxTables: number;
  arrivalIntervalMs: NumberRange; // [最小值, 最大值]
  arrivalChance: number;
  partySize: NumberRange; // 人数范围
  eatMs: NumberRange; // 用餐时长范围
  orderMs: number;
  prepareMs: number;
  cleanMs: number;
  rewardSeconds: number;
  hours?: { open: number; close: number }; // 一天内的剧情秒
  help?: { acceptedVar: string; completedVar: string; paidVar: string };
  waiter: { id: string; name: string; character: string; image: string };
  guests: { character: string; left: string; right: string }[];
  menu: string[]; // 商品 ID
  residue: string;
};

type NpcSchedule = {
  scene: string;
  sleepAt: number; // 一天内的剧情秒
  wakeAt: number;
  entrance: XY;
  home: XY;
};
```

`slot`
是固定收藏格位，范围为 1–31；价格和奖励以生命秒计。时钟配置描述初始流速，运行中调速后的值保存在 State。客流参数描述规则，已入店客人和正在处理的订单属于
`State.dining`。

### 演出与练习配置

```ts
type PerformanceSettings = {
  scene: string;
  entrance: XY;
  position: XY;
  at: number; // 首次演出的剧情秒门槛
  performer: { id: string; name: string; character: string; image?: string };
  listeningTiles?: XY[];
  reactions?: { during: string; after: string; tipSeconds: number; lingerMs: number }[];
  audio: string;
  durationMs: number;
  completedVar: string;
  fallbackEntity: string;
  cues: {
    atMs: number;
    speaker: 'performer' | 'guest';
    text: string;
    fallbackText?: string;
    tipSeconds?: number;
  }[];
};

type MusicVoice = {
  midi: number;
  durationMs: number;
  volume: number;
  offsetMs?: number;
};

type PracticeSettings = {
  teacher: string;
  unlockedVar: string;
  label: string;
  dailyNewLessons: number;
  leadInMs: number;
  hitWindowMs: number;
  samplePath: string;
  notes: { key: string; label: string; midi: number }[]; // 按键与音区映射
  lessons: {
    id: string;
    title: string;
    guidance: string;
    durationMs: number;
    requiredHits: number;
    notes: { atMs: number; key: string; sounds: MusicVoice[] }[];
    accompaniment: (MusicVoice & { atMs: number })[];
  }[];
};
```

`cues.atMs` 相对演出时间轴，课程音符的 `atMs` 相对本轮练习起点；`offsetMs`
相对一个短句触发点。`completedVar`、`unlockedVar`
引用剧情布尔变量。多个剧本可贡献不同任务和交互，但同一内容包只有一份
`clock`、`dining`、`performance`、`practice` 配置。

### Scene：地图、实体和服务布局

```ts
type Visual = {
  image: string;
  size?: XY;
  anchor?: XY;
  offset?: XY;
};

type Scene = {
  schema_version: '1.0';
  content_version: string;
  id: string;
  name: string;
  map: {
    width: number;
    height: number;
    floorTile: number;
    wallTile: number;
    tileset?: 'tavern';
    playerScale?: number;
    collision?: string[];
    blockedEdges?: [number, number, number, number][]; // ax, ay, bx, by
    art?: (Visual & { position: XY; depth: number })[];
  };
  anchors: Record<string, XY>;
  entities: Entity[];
  dining?: {
    entrance: XY;
    counter: XY;
    counterTiles?: XY[];
    home: XY;
    tables: {
      id: string;
      service: XY;
      interactionTiles: XY[];
      position: XY;
      depth: number;
    }[];
  };
};

type Entity = {
  id: string;
  name: string;
  position: XY;
  character: string;
  sprite?: Visual;
  seatedOn?: string; // 初始绑定的座位 ID
  seat?: {
    table?: string;
    orientation: number;
    depth: number;
    playerSprite: Visual;
  };
  interactionOffsets?: XY[]; // 相对实体格的交互站位
  movable?: boolean;
  portal?: { scene: string; anchor: string };
};
```

`map.collision` 控制格子可通行性，`blockedEdges` 控制相邻格之间的边；`map.art`
只负责显示，不会自动生成可交互实体。`Scene.dining` 的入口、服务站位和 `home` 是格坐标；餐桌
`position` 与 `depth` 用于像素显示。实体 ID 跨场景引用，移动后的坐标写入 State。

### 作者交付什么

正式内容入口是
`public/content/demo/manifest.json`。清单列出场景和剧本文件，并指定起始场景、入口和内容版本。

- **场景文件**定义地图、通行限制、图层与实体外观、锚点、初始摆放、座位和场景连接。
- **剧本文件**定义初始变量、对白、选项效果和任务，以及物品、商店、时钟、客流、作息、演出与练习等可选规则。
- **素材文件**提供图像和音频，内容定义通过路径引用它们。

`loadPackage` 读取清单，把多个剧本合成一份 story；重复定义的标识或配置会被拒绝。随后 `loadContent`
校验内容并复制数据，得到
`Content = { scenes, story }`。同一个世界只能加载一次内容；更换内容应创建新的运行。

这里的“静态”指运行过程不把变化写回作者源文件，也不表示加载器把所有对象都递归冻结。边界主要由复制、受控加载与引擎对状态的独立维护建立。

### 定义与进度分开

| 世界定义中的内容               | 运行后变化的数据                               |
| ------------------------------ | ---------------------------------------------- |
| NPC 的初始场景和位置           | NPC 当前场景、位置、路线与过门进度             |
| 绯月的对白和任务条件           | 是否已经见面、当前话题、任务已完成哪些步骤     |
| 商品目录、价格和初始店存       | 玩家物品数量、商店剩余库存和下次补货时刻       |
| 诗人的到场安排、曲谱与判定规则 | 演出进度、学会的课程和本轮命中结果             |
| 阁楼楼梯与床边的睡眠选项       | 是否获得房间许可、玩家在哪里、睡醒后到什么时间 |

上楼不会重新创建楼下酒馆，也不会把莉奈或库存恢复成初始值。渲染场景时，引擎结合固定定义与当前状态，查询此刻实际在场的实体。

### 同名的 config 不一定是世界定义

本文的 **World Config** 对应内容定义 `Content`。录制文件里另有一个名为 `config`
的小对象，用来保存模拟步长与早期 NPC 初始参数；它并不是场景与剧本的总集合。

完整恢复依赖 **内容定义 + 初始化参数 + 规则版本 + 恢复状态**。仅保存其中名为 `config`
的字段是不够的。

## 第二层：World State，保存此刻的事实 {#state}

### State 顶层与实体状态

```ts
type State = {
  sceneId: string;
  player: Position;
  orientation: number;
  moving: null | { target: Position; arrivesAt: number; durationMs?: number };
  seated?: { entity: string; returnPosition: Position };
  entities: Record<
    string,
    {
      sceneId: string;
      position: XY;
      path: XY[];
      transit: null | { via: string; arrival: string };
      moving: null | { target: Position; arrivesAt: number };
      orientation: number;
      seatedOn?: string;
    }
  >;
  vars: Record<string, boolean>;
  activeEntity: string | null;
  interactionRevision: number;
  dialogue: boolean;
  dialogueTopic?: string;
  greetedEntities?: string[];
  dialogueSeed?: number;
  npc: {
    id: string;
    position: Position;
    interactions: number;
    reply: string | null;
  };
  tasks: Record<
    string,
    {
      activated?: true;
      completed: string[]; // 已完成步骤 ID
      steps: Record<string, { count: number; values: string[] }>;
    }
  >;
  time: number; // 模拟毫秒
  storyTime: number; // 已结算剧情秒
  balance: number; // 剩余生命秒
  clock?: { realSecondsPerTick: number; elapsedMs: number };
  clues?: string[]; // 已获得线索 ID
  commerce?: {
    inventory: Record<string, number>; // 商品 ID → 玩家数量
    stock: Record<string, Record<string, number>>; // 商人 ID → 商品 ID → 店存
    nextRestock?: Record<string, number>; // 商人 ID → 下次补货的绝对剧情秒
  };
  schedules?: Record<string, 'active' | 'leaving' | 'away' | 'returning'>;
  dining?: DiningState;
  performance?: PerformanceState;
  practice?: PracticeState;
};
```

`moving.arrivesAt` 是绝对模拟毫秒；`transit.via` 是门实体 ID，`arrival`
是目标入口锚点名。离场的具名 NPC 可能仍保留实体状态，但 `sceneId` 变成空字符串、作息为
`away`，不再出现在场景中。`interactionRevision` 用于拒绝已过期的选项与交易确认。

没有配置的可选系统一般不创建对应状态字段；例如没有商品定义就没有 `commerce`。`tasks.steps`
中累计的值和 `completed` 中完成的步骤是两种信息；`activated` 用于带触发条件的任务。

### DiningState：服务员、来客与清理

```ts
type DiningActor = {
  position: XY;
  path: XY[];
  orientation: number;
  moving: null | { target: XY; arrivesAt: number; durationMs?: number };
  seatedOn?: string;
};

type DiningGuest = DiningActor & {
  entered?: boolean;
  startsAt: number;
  look: number; // 外观配置索引
  seat: string;
  approach: XY;
  exited: boolean;
  audience?: {
    preference: number; // 反应配置索引
    delayMs: number;
    heardAt?: number;
    reacted?: boolean;
    applauded?: boolean;
    spot?: XY;
    leaveAt?: number;
    settled?: boolean;
    speech?: { text: string; until: number };
  };
};

type DiningGroup = {
  id: number;
  table: string;
  phase: 'arriving' | 'waiting' | 'ordering' | 'ordered' | 'eating' | 'dirty';
  guests: DiningGuest[];
  order?: string;
  due?: number;
  cleaned: boolean;
};

type DiningState = {
  seed: number;
  nextArrival: number;
  serial: number;
  groups: DiningGroup[];
  waiter: DiningActor;
  idleUntil: number;
  job: null | {
    group: number;
    phase: 'order' | 'pickup' | 'prepare' | 'deliver' | 'clean';
    due?: number;
  };
  cleaning: null | { group: number; started: number; due: number; position: XY };
  cleanedCount: number;
  rewards: number;
};
```

此处 `moving.target` 使用数组，和顶层玩家／通用实体的对象形式不同。`groups[].id` 被
`job.group`、`cleaning.group` 引用；`seed`
保存当前客流随机序列。到达、订单、清理、发言与离开期限使用模拟毫秒，`delayMs` 是持续时间，`rewards`
是累计发放的生命秒数。

### PerformanceState 与 PracticeState

```ts
type PerformanceState = {
  phase: 'scheduled' | 'arriving' | 'waiting' | 'playing' | 'done';
  elapsedMs: number;
  cue: number; // 下一条演出提示索引
  tips: number; // 诗人得到的生命秒数
  audienceNextAt?: number;
  applause?: number;
  bubble?: { text: string; name: string; position: XY; untilMs: number };
};

type PracticeState = {
  active: boolean;
  learned: number; // 已学会课程数量
  lesson: number; // 当前课程索引，从 0 开始
  note: number; // 下一短句索引
  played: number;
  newLessonsToday: number;
  finished: boolean;
  hits: number;
  results: ('hit' | 'wrong' | 'miss')[];
  startedAt?: number;
  lastSounds?: MusicVoice[];
  lastKey?: string;
  lastPlayedAt?: number;
  wrong?: boolean;
  lastLessonDay?: number;
};
```

演出 `elapsedMs`、`bubble.untilMs`、`audienceNextAt` 和听众 `audience.heardAt`
使用演出自己的毫秒时间轴。练习 `startedAt`、`lastPlayedAt` 使用绝对模拟毫秒，`lastLessonDay`
是剧情秒折算的日编号。`played` 统计拨弦操作，`hits` 统计正确接上的短句，不能互换。

`State`
是整局世界的业务状态，不只是实体列表。其主要区域如下；这是职责分组，不是可直接提交给加载器的 JSON 模板。

| 状态区域       | 记录的事实                                                                     |
| -------------- | ------------------------------------------------------------------------------ |
| 玩家与当前交互 | 场景、位置、朝向、正在走向哪里、座位及起身格、当前交互对象、对白与交互版本     |
| 场景实体       | 当前场景和位置、路线、正在进行的一格移动、过门安排、固定坐姿                   |
| 剧情与任务     | 变量、已激活任务、已完成步骤、累计事实、已获得线索、首次见面记录和对白随机序列 |
| 时间与交易     | 模拟时间、剧情时间、生命余时、时钟段进度、物品数量、店存与补货期限             |
| 日常与演出     | 餐桌、客人、莉奈的服务状态、人物作息阶段、首演阶段和听众回应                   |
| 练习           | 已学习进度、每日新课计数、当前课程、短句判定与最近拨弦反馈                     |

当前玩家仍保存在独立字段里；通用实体、客流中的服务员和来客也不全在同一个集合中。`State` 还保留早期
`npc` 回复等字段，不能把它理解为已经完全统一的实体组件模型。

### 状态如何变化

玩家操作通过 `execute` 提交，模拟推进通过 `advance(ms)`
提交。引擎从当前状态复制草稿，执行校验、计算相关系统的变化，再记录结果；记录成功后才替换正式状态。

例如领取首次帮工谢礼，会一起更新背包、剧情变量、客房许可和任务进度。购买商品则需要一起更新余时、物品数量、店存与交互版本。这些不是几个互不关联的界面更新。

失败通常保留原业务状态，并记录失败结果。有一个明确例外：当前 `memory-world-2`
规则下，站立玩家尝试向受阻方向移动，虽然位置不变，朝向仍会更新。解析失败、重复请求和录制容量拒绝发生在不同边界，不会为每次输入尝试都追加事件。

### State 不是完整恢复上下文

`inspect()` 返回 State 的副本，但 `MemoryWorld` 还持有：

- 本局固定内容与执行规则；
- 请求去重缓存：同一个请求重试时返回原结果，避免重复扣款或发奖；
- 当前内存段的事件、全局起始序号与载荷计数。

因此，把 `inspect()`
的返回值单独写进文件，再赋回去，不等于完整读档。去重信息虽然不在 State 内，也会影响之后的执行结果。

### 三种时间不要混用

| 时间                           | 单位与用途                                                                   |
| ------------------------------ | ---------------------------------------------------------------------------- |
| `State.time`                   | 模拟毫秒，驱动移动、服务、演奏与练习等过程                                   |
| `State.storyTime` 与时钟段进度 | 剧情秒与尚未结算的段进度，表达酒馆的一天、营业与作息；当前流速也保存在状态中 |
| `recordedAt`                   | 记录时的墙钟时间戳，属于元数据，不用它推动重放模拟                           |

当前 Demo 每累计三十秒有效模拟时间，结算十分钟剧情时间与生命消耗。等待和睡眠走引擎的时间结算流程；普通交谈期间世界继续活动。后台与闲置暂停后不会补算离线经过的时间。

界面通常按约一百毫秒合并提交模拟推进，人物到达、操作或暂停边界可以提前提交。画面插值不会每帧产生一个存档事件；重放保留原先的
`advance` 分段，不能任意合并成一次大推进。

## 第三层：记录、持久化与恢复 {#storage}

### Recording：每个 UUID 文件的结构

```ts
type Result = { ok: true } | { ok: false; error: string };

type Recording = {
  format: 'remaining-time-run-1';
  rules: 'memory-world-1' | 'memory-world-2';
  content: Content;
  config: { stepMs: number; npc: Position };
  startSequence?: number; // 省略时从 0 开始
  eventCount: number;
  events: {
    sequence: number;
    recordedAt: number;
    cause: Command | { type: 'advance'; ms: number };
    result: Result;
    state: State;
  }[];
  finalState: State;
  snapshot?: {
    format: 'memory-world-snapshot-1';
    sequence: number;
    requests: [
      string,
      {
        fingerprint: string;
        result: Result;
        sequence: number;
      },
    ][];
  };
};

type RecordingBundle = {
  format: 'remaining-time-saves-1';
  chunks: Recording[];
};
```

`eventCount` 必须等于事件数组长度；首条事件序号为 `startSequence + 1`，末尾为
`startSequence + eventCount`。`snapshot.sequence` 与末尾相同；`finalState` 应与最后一条事件的
`state` 一致。当前写出的文件包含 `snapshot`，可选标记用于兼容旧档。

`requests` 是 `[requestId, 缓存项]` 的数组，不是 JSON 对象字典。`fingerprint`
是规范化命令的 JSON 字符串；缓存同时记录成功与失败结果以及原事件序号。保存一个前缀时，仅包含该结束位置之前的请求。

`RecordingBundle` 是引擎支持的多段输入形式，不是 OPFS 存档索引。浏览器的每个 UUID 文件保存一段
`Recording`。

### Command：事件原因中的命令结构

```ts
type Command = { requestId: string } & (
  | { type: 'move'; dx: number; dy: number; sprint?: boolean }
  | { type: 'interact'; target: string }
  | { type: 'choose'; choice: string; revision: number; hours?: number }
  | { type: 'buy' | 'sell'; target: string; item: string; quantity: number; revision: number }
  | { type: 'clean'; target: string }
  | { type: 'waitUntil'; time: number }
  | { type: 'advanceStoryTime'; seconds: number }
  | { type: 'setClockSpeed'; seconds: number }
  | { type: 'practice'; lesson: number; revision: number }
  | { type: 'startPractice'; revision: number }
  | { type: 'playNote'; key: string; revision: number }
  | { type: 'cancel' | 'closeDialogue' | 'skipPerformance' | 'trade' | 'nextScene' | 'stand' }
);
```

`target` 一般是交互对象 ID，清理时是餐桌 ID；`revision` 对应当前
`interactionRevision`。`waitUntil.time` 是目标绝对剧情秒，`advanceStoryTime.seconds`
是剧情秒增量，`setClockSpeed.seconds` 是每个结算段需要的模拟秒。`choose.hours`
用于一至二十四小时的睡眠选择；`practice.lesson` 是从零开始的课程索引。

`advance(ms)` 事件没有 `requestId`，由模拟调度直接调用；它与 `advanceStoryTime`
命令不同，后者只推进剧情时钟及相关补货，不等同于普通等待或睡眠。

### Catalogue：存档 manifest.json 的结构

```ts
type SaveHead = {
  revision: string;
  slot: number;
  sequence: number;
};

type SaveSlot = {
  id: number;
  file: string;
  savedAt: number;
  start: number;
  end: number;
  scene: string;
  time: number;
  balance: number;
  bytes?: number;
  tasks?: { active: string[]; completed: string[] };
};

type Catalogue = {
  head: SaveHead;
  slots: SaveSlot[];
};
```

| 字段                               | 含义与约束                                                        |
| ---------------------------------- | ----------------------------------------------------------------- |
| `head.revision`                    | 并发写入版本；初始空索引为 `empty`，时间线发布后使用新 UUID       |
| `head.slot`                        | 当前最后槽位号，等于 `slots.length`，空时间线为 0                 |
| `head.sequence`                    | 已保存的末尾全局事件序号，空时间线为 0                            |
| `slots[].id`                       | 从 1 连续增长的槽位号                                             |
| `file`                             | 本目录下 `<uuid>.json` 文件名                                     |
| `savedAt`                          | 保存时的 Unix 毫秒时间戳                                          |
| `start` / `end`                    | 开始前的事件游标／结束事件序号；下一档的 `start` 等于上一档 `end` |
| `scene`                            | 档末场景的显示名称，找不到名称时使用场景 ID                       |
| `time` / `balance`                 | 档末模拟毫秒／剩余生命秒，用于存档卡片                            |
| `bytes`                            | JSON 文件字节数；旧索引可能暂缺                                   |
| `tasks.active` / `tasks.completed` | 用于列表展示的任务标题数组，不是任务 ID 或完整任务状态            |

索引只负责定位文件与展示摘要，不能用它重建 State。完整任务进度和物品数量仍从 `Recording.finalState`
恢复。旧索引缺少 `bytes` 或任务摘要时，打开详情列表会从对应文件补齐。

### 只存在于内存的恢复结构

`MemoryWorld.checkpoint()`
返回恢复闭包，捕获 State、请求 Map、当前段事件、起始序号和载荷计数；它不是上述 JSON 文件的一部分。浏览器的回放会话持有
`id`、`head`、`slots` 和 `replay` 控制器，播放倍速、游标与界面开关也不会作为独立世界字段落盘。

### 录制保存的内容

一段录制包含以下几类数据：

| 数据                               | 用途                                                 |
| ---------------------------------- | ---------------------------------------------------- |
| 格式与规则标识                     | 识别录制格式，并选择支持的执行语义                   |
| 本局内容与初始化参数               | 固定这次运行所用的场景、剧本和模拟设置               |
| 全局起始序号与事件数量             | 连接相邻记录段，发现缺失或不连续的历史               |
| 每条事件的原因、结果和提交后 State | 重现命令或时间推进，并比较执行结果                   |
| `finalState`                       | 本段最后一条事件之后的状态                           |
| `snapshot`                         | 快照版本、末尾全局序号，以及截至该位置的请求去重信息 |

当前录制标识是 `remaining-time-run-1`，快照标识是 `memory-world-snapshot-1`；新运行使用
`memory-world-2` 规则，也保留对 `memory-world-1` 的支持。这些标识与本文日期各有用途。

**快照状态实际取自 `finalState`**，`snapshot`
补充恢复所需的序号和请求缓存，并没有再独立存一份业务状态。

每条事件目前携带完整 State；文件还嵌入完整内容定义。所以它既有可重演的输入，也有用于校验与快速恢复的状态副本，不是一份只有命令的精简日志。实体也不会各自保存独立的完整历史。

### 浏览器中的文件

存档位于当前网站来源的浏览器私有文件系统 **OPFS**：

```text
remaining-time-saves/
  manifest.json       存档索引、当前 head revision、全局结束序号与槽位摘要
  <uuid>.json         一段录制及其恢复信息
```

这里的 `manifest.json` 是**存档索引**，与内容包里的同名入口清单不是同一个文件。

槽位是同一条时间线的连续片段，不是多条互相独立的角色存档。当前没有云端同步；IndexedDB 只用于读取并迁移更早的本地存档格式，日常保存使用 OPFS。

### 一次自动保存的顺序

浏览器每秒检查一次，在待保存事件达到一千条时，截取**当前段最前面的一千条**：

1. 以这一千条的最后状态作为 `finalState`，只带上该结束位置之前的请求缓存。
2. 写入新的 UUID JSON 文件，完成关闭发布。
3. 发布引用新文件的存档索引。
4. 索引发布成功后，才释放引擎中对应的事件前缀。

保存期间继续产生的事件留在内存，归入下一档。事件数量固定，不代表每档涵盖的游戏时间固定。

文件访问共用 Web Lock；写入还核对 head
revision，阻止旧页面覆盖另一页面已经更新的时间线。它是当前浏览器来源内的协调，不是跨设备同步。

写文件或发布索引失败时，上一份有效索引与内存进度保留，并提示重试。删除未来记录时先发布新的索引，再清理文件；没有被索引引用的残留文件不会重新成为可加载槽位。网页关闭前未成功发布的尾部进度不保证保存。

## 四条实际使用路径 {#flows}

### 新开时间线

页面读取当前部署的内容包，创建 `MemoryWorld`
并初始化状态。存档窗口中的“存档 0”是新游戏入口；确认开始会清除现有时间线，之后从全局事件零重新累计。

内容文件修改后，刷新通常仍会恢复已有存档绑定的旧内容。要体验新内容，需要加载新的内容包并新开时间线，现有运行没有规则热迁移。

### 刷新或加载某个槽位

启动时，页面同时获取当前内容包和本地存档信息。有存档时，实际运行优先采用恢复出的世界及其嵌入内容。当前页面仍等待内容包加载成功才进入游戏，因此“存档嵌入内容”不等于启动完全不依赖部署文件。

普通加载读取目标槽位，校验内容、规则、快照结构和结束位置，**直接恢复档末状态、序号和去重缓存，不逐事件执行之前的历史**。旧文件若没有快照元数据，会首次扫描之前的命令补齐去重信息，而不是重跑模拟。

加载较早槽位成功后，发布截断后的索引并清除后续槽位；当前尚未保存的进度也会被放弃。校验失败时保留当前世界与已有时间线。

### 观看、定位与切档

播放第一档时从本局初始状态开始；播放之后的某档时，用前一档末尾快照作为起点。通常只读取目标档和前一档，不从事件零重新计算全部前缀。

回放调用相同的 `execute` 与
`advance`，比较每一步的结果和 State，并在段末核对记录。向后定位利用内存检查点恢复后再执行；它与磁盘中的恢复快照是两种不同机制。当前每二千个事件建立一个检查点，最多保留起点和八个非起点检查点。

播放速度按记录的**模拟时长**计算，可选 1×、2×、4×、8×；命令事件不额外等待。观看和定位本身不截断时间线，退出可以返回观看前的世界及未保存事件。

### 从回放位置继续

只有确认从游标位置继续，才修改保存的时间线：

- 游标在档末：保留该档，清除后续档案，从这里追加新事件。
- 游标在档内：磁盘保留此前完整档，本档已播放部分留在内存，与之后的新事件凑满一千条再保存。

当前提供的是**保留前缀后改写未来**，不是同时保留多条可切换的分支。

## 当前边界 {#limits}

- **存储成本：** 每段最多十万个事件或 16 MiB 累计 UTF-8
  JSON 事件载荷。这是序列化载荷预算，不是浏览器实际堆内存上限。
- **容量失败：**
  如果不足一千条就触及内存保护，当前进度保留并暂停相关操作，不会自动生成一个不足阈值的小存档。请求去重表随命令数增长，存档索引随槽位数增长。
- **长期规模：**
  槽位没有应用层数量上限，但仍受浏览器配额约束。完整 bundle 回放接口会持有全部输入；当前没有紧凑增量日志或长篇运行的性能保证。
- **校验范围：**
  快照加载检查恢复结构与结束位置，回放检查实际经过的事件。二者都不代表签名认证，也不保证任意外部文件可信。
- **版本与素材：**
  内容定义会固定在录制中，图片和音频字节仍是外部资源。规则标识也不是整份引擎源码的封存；后续代码与素材变更仍可能影响旧档体验。
- **随机与 Agent：**
  当前内容驱动的行为通过受控状态推进。尚未接入任意异步 Agent 决策的录制合同，不能据此承诺外部模型调用可确定性重放。
- **浏览器范围：**
  不同来源、端口、浏览器的文件不共享；清除网站数据会删除存档。持久存储请求不是云备份，也不是断电安全保证。

## 对应代码与维护方式 {#sources}

| 代码位置                                       | 本文对应职责                                  |
| ---------------------------------------------- | --------------------------------------------- |
| `prototype/package.ts`、`prototype/content.ts` | 内容包组装、边界校验与内容定义                |
| `prototype/world.ts`                           | State、命令与时间推进、记录、检查点和快照恢复 |
| `prototype/replay.ts`                          | 录制验证、直接恢复、逐事件回放与定位          |
| `src/lib/autosaves.ts`                         | OPFS 文件、索引、旧档迁移和时间线截断         |
| `src/components/AutoSaves.tsx`                 | 自动保存触发和存档窗口操作                    |
| `src/components/LocalGame.tsx`                 | 启动、输入、模拟调度、回放与界面衔接          |

本文只对页首标明的代码版本负责。修正文档中的事实错误时保留版本依据；如果职责边界或存储方式发生实质变化，另写新日期快照并相互链接，无需为每次功能改动重写本文。

玩家可见的操作规则见[主要系统：存档](/systems/#saves)，本版本附近的玩法变化见
[Daily Build 更新](/daily-build/)。
