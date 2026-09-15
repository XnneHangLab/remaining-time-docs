---
title: 世界数据模型 · 2026-09-15 · NPC 实体统一版
description:
  NPC 实体统一实现预览，说明实体身份、生命周期、外观、运行状态，以及新旧录制格式的恢复边界。
---

# 世界数据模型 · 2026-09-15 · NPC 实体统一版

::: warning 实现预览本文依据游戏仓库 `NevaMind-AI/remaining-time` 的提交
`c3ca054071bbbf48ec767473fd7b4e7003e90abf` 整理，对应代码 PR #59；撰写时尚未合入
`dev`，不代表已发布版本。适用于本地 memory 酒馆模式。合入后需核对最终实现并更新版本依据。:::

这是同日的另一份架构快照，聚焦 NPC 实体统一后的结构。原先基于 `dba56a4` 的
[世界数据模型 · 2026-09-15](/architecture/world-model-2026-09-15)保留原版本字段，可用于理解旧录制。日期、代码提交号和录制规则版本各有用途；本文不承诺随每次代码修改持续更新。

## 职责总览 {#overview}

仍以 **World Config → World State → Storage**
区分世界定义、运行状态和记录／持久化恢复。变化集中在 NPC 的运行身份，以及录制边界上的状态转换。

```text
场景、剧本与人物配置
        │ 加载、校验并创建实体
        ▼
State.entities[id] ← 移动、作息、服务、演出等系统
        │
        ├─ getEntity(id)：按身份查询，与是否在场无关
        ├─ scene(id).entities：筛选该场景中在场的实体
        └─ 录制：按本局规则选择 State 或 LegacyState 布局
                         │
                         ▼
                 OPFS 记录段与存档索引
```

所有内容驱动 NPC 的基础运行状态进入同一个实体表。玩法系统继续解释各自规则，餐饮分组通过 ID 引用人物。

## World Config：作者仍填写什么 {#config}

作者的 JSON 结构沿用[原版 Config 字段说明](/architecture/world-model-2026-09-15#config)：

| 定义                                         | 内容与本版关系                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `ContentManifest`、`Content`                 | 清单仍组装场景和剧本；录制嵌入加载后的内容                                                  |
| `Scene.entities`                             | 普通具名 NPC、床、凳子、楼梯等实体的定义和初始摆放                                          |
| `StoryBody`                                  | [共同剧本字段](/architecture/world-model-2026-09-15#story-body)：变量、交互、任务与玩法配置 |
| `story.dining.waiter`、`story.dining.guests` | 服务员定义与可选顾客外观；加载／生成时创建统一运行实体                                      |
| `story.performance.performer`                | 诗人定义；初始化时建立实体，首次到场由演出流程控制                                          |
| 商店、作息、演出、练习配置                   | 保留现有参数、素材引用和执行规则，通过人物 ID 关联                                          |

**运行身份已统一，作者配置的入口仍然分布在场景与玩法配置中。**
本版没有新增一个要求作者填写的全局 Entity JSON 文件，也没有改写 Story 的任务、商品或课程格式。

下文继续用 TypeScript 形状说明字段：`?` 表示可省略，`null`
表示明确没有当前动作或场景位置。这些类型说明不是需要额外写入 JSON 的包装层。

## Entity：身份、生命周期与外观 {#entities}

### 唯一的基础状态

```ts
type XY = [number, number];
type Position = { x: number; y: number };
type Visual = {
  image: string;
  size?: XY;
  anchor?: XY;
  offset?: XY;
};

type Appearance = {
  character: string;
  image?: string;
  performingImage?: string;
  left?: string;
  right?: string;
  sprite?: Visual;
};

type EntityState = {
  name: string;
  appearance: Appearance;
  sceneId: string;
  position: XY;
  orientation: number;
  path: XY[];
  moving: null | {
    target: Position;
    arrivesAt: number;
    durationMs?: number;
  };
  transit: null | { via: string; arrival: string };
  seatedOn?: string;
  movementSystem?: 'dining';
};
```

实体 ID 是 `State.entities` 的字典键，基础状态内部不重复保存
`id`。普通人物、莉奈、诗人和顾客共用上述结构；顾客还附加下文的消费活动字段。

- `sceneId` 是当前场景 ID；空字符串表示场外。场外的 `position`
  只保留模拟坐标，不代表一个正在模拟的场外地点。
- `position`、`path`、`moving.target` 以格为单位。当前位置／路线用数组，移动目标统一使用 `{ x, y }`
  对象；餐饮人物也采用这一形式。
- `arrivesAt` 是绝对模拟毫秒，`durationMs` 是这一格移动耗时。朝向为右 0、下 90、左 180、上 270。
- `transit.via` 引用门实体，`arrival` 引用目标入口锚点；`seatedOn` 引用座位实体。
- `movementSystem: 'dining'`
  表示由现有餐饮循环推进移动，保留原执行顺序和碰撞策略。它不代表另一份人物位置。

### 外观分配

`appearance` 保存这位实体实际选用的外观信息：`character` 是角色形象标识，`image`
是可选行走形象资源，`left`／`right` 是顾客左右坐姿图片，`sprite`
支持场景实体的自定义视觉参数，`performingImage` 是演出时的替代形象。

本版初始化会把配置中的姓名与外观复制进实体状态。动态顾客生成时，用受控随机序列选择一次外观，保存其资源引用；刷新、读档和回放不会在渲染时重新抽取。图片和音频文件本身仍是外部资源，不会随 State 嵌入存档。

`Visual.size`／`offset` 以像素为单位，`anchor`
是归一化锚点。动画当前帧与画面插值留在渲染层。本版尚未提供换装或任意修改人物外观的命令。

### getEntity(id)：查询结果 {#lookup}

`getEntity(id)` 返回副本；未知 ID 返回 `undefined`。其公共字段如下：

```ts
type EntityView = {
  id: string;
  name: string;
  character: string;
  sprite?: Visual;
  appearance: Appearance;
  location: null | { sceneId: string; position: XY };
  state: EntityState; // 顾客在此对象上另有 Guest 的活动字段
  capabilities: {
    movement?: true;
    dialogue?: true;
    shop?: true;
    schedule?: true;
    service?: true;
    customer?: true;
    performance?: true;
    teaching?: true;
  };
};
```

返回值还保留场景定义中的原有字段，例如
`portal`、`seat`、`interactionOffsets`。这些定义字段见[原版 Scene／Entity 结构](/architecture/world-model-2026-09-15#config)。直接查询时，继承自定义的顶层
`position` 可能仍是初始摆放；**当前所在位置应读取 `location`**。`scene(id).entities`
筛选在场实体，并将其顶层 `position` 替换为运行位置，供既有场景调用方使用。

| 查询结果                              | 意义                                       |
| ------------------------------------- | ------------------------------------------ |
| `undefined`                           | 本局没有这个 ID 的实体记录                 |
| 有实体，`location: null`              | 实体已存在，当前不在任何已表示的场景中     |
| 有实体，`location.sceneId` 为另一场景 | 可以查询身份；不会出现在当前场景列表里     |
| 有实体，位置在当前场景                | 会进入该场景的实体视图，但不保证此刻可交互 |

能力标记依据现有定义、实体状态及人物 ID 关联关系计算，不是 State 内新增的能力字典，也不是作者填写的通用能力协议。例如绯月具备
`shop`，莉奈具备 `service`，诗人具备 `performance` 和
`teaching`。当前标记并不穷举座位、传送门等已有交互。

查询接口是引擎内部的只读视图，尚未实现面向 Agent 的信息权限过滤或通用动作发现协议。动作仍通过现有命令入口校验距离、作息、剧情条件与交互版本；返回副本的修改不会写回世界。

### 创建、入场与离场 {#lifecycle}

具名 NPC 在世界初始化时创建，包括还没有首次登场的诗人。动态顾客生成时按餐饮分组序号和组内索引分配 ID，通常为
`guest:<group>:<index>`；若与作者定义 ID 冲突，则前置冒号避让。分组计数 `DiningState.serial`
随状态保存，顾客 ID 不因走路、入座或离场而改变。

```text
具名人物初始化 / 顾客生成
          │ 同一个 ID
          ▼
  场外等待 → 入场 → 行动、消费或工作 → 离场
                                       │
                                       ▼
                              保留身份与外观，仍可查询
```

莉奈和普通具名 NPC 的作息控制离场／返回；诗人的首次入场由演出阶段控制，后续也参与作息。顾客仍执行原有入店、入座、消费和离店循环，并未统一成具名人物的
`schedules` 配置。

顾客离场后先标记场外；当整组已清理且所有顾客均离开时，删除分组及已结束消费活动字段，保留实体基础记录。本版没有通用销毁／重新召回顾客命令。ID 的稳定性以本局保留的时间线为范围，跨分支引用还需要调用方管理时间线上下文。

## World State：其他进度与共享活动 {#state}

### 顶层 State 的变化范围

顶层仍使用 `entities: Record<string, EntityState>`；其中处于餐饮活动的顾客对象实际还包含 `Guest`
字段。其余顶层字段的结构沿用[原版 State 展开](/architecture/world-model-2026-09-15#state)，变化边界如下：

| 字段                                        | 本版归属                                                 |
| ------------------------------------------- | -------------------------------------------------------- |
| `entities`                                  | 全部配置 NPC、动态顾客及现有场景实体的基础状态           |
| `dining`                                    | 餐饮调度、分组、订单、工作与清理；通过 ID 引用人物       |
| `schedules`                                 | 具名 NPC ID → `active / leaving / away / returning`      |
| `performance`、`practice`                   | 沿用原版演出与练习状态，字段尚未整体迁入能力组件         |
| `player`、`moving`、`orientation`、`seated` | 玩家专用状态仍独立存在                                   |
| `vars`、`tasks`、`commerce`、`clues`        | 剧情、任务、库存、店存和线索保持原结构                   |
| `time`、`storyTime`、`balance`、`clock`     | 模拟时间、剧情时间、生命余时和时钟段进度保持原语义       |
| 对话字段与 `npc`                            | 当前交互、首次见面、对白随机序列及早期回复字段保持原结构 |

练习的已学课程／每日计数与本轮判定仍在 `State.practice`
中；学习者长期进度和活动状态的进一步拆分是后续工作。

### 顾客活动字段 {#guests}

```ts
type Guest = EntityState & {
  entered?: boolean;
  startsAt: number;
  look: number;
  seat: string;
  approach: XY;
  exited: boolean;
  audience?: {
    preference: number;
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
```

这些字段和基础状态位于同一个 `State.entities[guestId]` 对象上。`look`
保留外观配置索引，渲染直接读取实体的 `appearance`；`seat` 是分配的座位 ID，`approach`
是起身后使用的格坐标，`seatedOn` 表达当前实际坐姿绑定。

`startsAt`、`leaveAt`、`speech.until` 使用绝对模拟毫秒，`delayMs` 是持续毫秒；`heardAt`
使用演出自己的毫秒时间轴。`preference`
是听众反应配置索引。上述消费／听众字段会随已结束的分组清理，不把每个离场顾客的完整活动永久留在实体上。

### DiningState：人物引用与共享进度 {#dining}

```ts
type DiningGroup = {
  id: number;
  table: string;
  phase: 'arriving' | 'waiting' | 'ordering' | 'ordered' | 'eating' | 'dirty';
  guests: string[]; // 顾客实体 ID
  order?: string; // 商品 ID
  due?: number;
  cleaned: boolean;
};

type DiningState = {
  seed: number;
  nextArrival: number;
  serial: number;
  groups: DiningGroup[];
  waiter: string; // 服务员实体 ID
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

`job.group` 与 `cleaning.group` 引用餐饮分组号；它们不是实体 ID。`table`
引用场景的餐桌布局 ID。`seed` 是当前客流随机状态；`serial`
同时参与后续顾客身份分配，不能在续玩时随意重置。

到达、工作、清理与闲逛期限使用模拟毫秒，`rewards`
是累计发放的生命秒数。餐桌布局、订单和分组仍由餐饮系统维护，不能据此认为所有物件和活动都已实体化。

## Storage：运行状态与录制布局 {#storage}

### 按规则保存的状态

```ts
type Rules = 'memory-world-1' | 'memory-world-2' | 'memory-world-3';
type RecordedState = State | LegacyState;
```

这里 `State` 指本版运行状态，`LegacyState`
指[原版 State／DiningState 布局](/architecture/world-model-2026-09-15#state)。这两个名字用于解释录制边界，不表示一局游戏同时维护两套可写人物状态。

| 规则                           | 引擎内部与 `inspect()` | 事件的 `state`、录制的 `finalState` |
| ------------------------------ | ---------------------- | ----------------------------------- |
| `memory-world-3`，新运行默认   | 统一实体结构           | 本版 `State`                        |
| `memory-world-1 / 2`，旧时间线 | 统一实体结构           | 按旧布局写出的 `LegacyState`        |

原版 [Recording 字段](/architecture/world-model-2026-09-15#storage)中的 `rules`
增加版本 3，`events[].state` 和 `finalState` 按上表解释。其余字段保持原结构：`content`、初始化
`config`、`startSequence`、`eventCount`、事件原因与结果、墙钟 `recordedAt`、快照序号和请求去重缓存。

`remaining-time-run-1`、`memory-world-snapshot-1`、bundle 标识 `remaining-time-saves-1`
均未更名。命令联合、存档 `Catalogue / SaveHead / SaveSlot`
也沿用原版字段。版本 3 保留版本 2 的冲刺及碰壁转向规则。

### 编码、恢复与回放

- `encodeState`：按本局规则选择保存布局。旧布局把服务员和在组顾客嵌回餐饮状态，移动目标转回数组，并在首次登场前省略诗人的运行实体。
- `decodeState`：恢复旧状态时创建统一实体、重建服务员与顾客引用，并把餐饮移动目标转成对象。
- `recordedState()`：返回本局录制布局的副本，用于与历史事件比较；`inspect()` 返回运行布局的副本。
- 快照恢复增加对必要实体、顾客身份、分组引用、外观、坐标与移动结构的校验。校验完成后才替换当前世界及请求缓存。
- 逐事件回放仍执行同一引擎，通过录制布局比较事件结果和状态；不会把新版 `inspect()`
  直接拿去与旧版事件比较。

**旧时间线继续按原规则读写，不自动升级成版本 3，也不静默重写原始文件。**
新格式的持久身份保证适用于新规则时间线。旧文件没有记录已经被移除的顾客，恢复时无法补出这些历史身份；从旧档恢复可重建其仍保存的顾客与全部具名 NPC。

### 文件与四条使用路径

[原版的 OPFS 文件、索引发布与自动保存顺序](/architecture/world-model-2026-09-15#storage)保持适用：先写记录文件，再发布索引，成功后释放已保存内存前缀。

| 路径           | 本版行为                                                                     |
| -------------- | ---------------------------------------------------------------------------- |
| 新开时间线     | 初始化全部具名 NPC，使用版本 3，顾客随后按客流生成                           |
| 刷新／加载槽位 | 使用录制嵌入内容与规则，必要时转换旧布局，再直接恢复档末快照                 |
| 观看／定位     | 按记录的命令和模拟推进执行，按该档规则比较保存布局                           |
| 从游标续玩     | 保留当前前缀、清除未来，沿当前时间线规则继续保存；保留前缀中的身份和分组计数 |

[原版四条路径的确认与截断规则](/architecture/world-model-2026-09-15#flows)继续适用。观看本身不截断时间线；旧档升级与多分支共存均不是本版提供的操作。

## 容量与对接边界 {#limits}

- 每条事件仍保存完整状态，新运行的状态包含离场后保留的实体基础记录；实体数量随历史来客数增长。结束活动的数据会清理，身份保留仍有成本。
- 自动保存仍按最前面的 1000 个事件分段，每段保护上限仍为 100000 个事件或 16 MiB 累计 UTF-8
  JSON 事件载荷。实体增多会减少预算内能容纳的事件数。
- 如果不足 1000 个事件就触及预算，当前机制会保留进度并暂停相关操作，不会自动保存更短的段。本版没有完成长期身份归档或容量治理。
- NPC 运行身份、基础状态和外观入口已经统一；玩家专用状态、商品实例、活动实体化、完整能力配置和 Agent 观察／动作协议仍需后续对接。
- 固定循环和现有玩法逻辑继续运行；本版没有增加外部模型调用，也不新增对任意异步 Agent 决策可重放的承诺。

## 源码入口与版本维护 {#sources}

| 代码位置                                                                 | 职责                                        |
| ------------------------------------------------------------------------ | ------------------------------------------- |
| `prototype/entities.ts`                                                  | 统一实体结构、初始化、外观与顾客 ID 分配    |
| `prototype/world.ts`                                                     | `State`、实体查询、场景筛选、命令与状态提交 |
| `prototype/dining.ts`、`schedules.ts`、`performance.ts`                  | 通过统一实体执行服务、作息、演出与消费循环  |
| `prototype/entityRecording.ts`                                           | 新旧状态布局转换、实体快照校验与结构比较    |
| `prototype/replay.ts`                                                    | 按录制规则恢复、回放、定位和续玩            |
| `src/components/LocalGame.tsx`、`DiningScene.tsx`、`BardPerformance.tsx` | 输入、实体显示、作息提示与演出界面          |
| `src/lib/autosaves.ts`、`src/components/AutoSaves.tsx`                   | OPFS、索引、自动保存和时间线操作            |

源码路径供有游戏仓库访问权限的读者定位。原版快照继续描述其绑定提交；本页在代码合入前保持预览标识，合入后核对最终提交。以后职责或格式再发生实质变化时，另建有明确版本依据的快照。
