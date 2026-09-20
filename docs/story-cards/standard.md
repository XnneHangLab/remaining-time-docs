---
title: Agent 任务卡
description: 面向编剧 Agent 的高度压缩剧情任务交付格式。
---

# Agent 任务卡

这不是面向玩家或普通读者的剧情说明，而是交给编剧 Agent 继续加工的**最小任务规格**。一张卡只描述一个任务；所有字段都必须填写，确实不存在时写 `none`，未知内容写 `TODO`，禁止留空或让 Agent 猜测。

<script setup>
import TaskCard from '../.vitepress/theme/TaskCard.vue'
import taskCardYaml from '../story/task-card-example.yaml?raw'
</script>

## Card 预览

下面的卡片由 `docs/story/task-card-example.yaml` 在构建时解析生成；YAML 是 Agent 的输入，卡片是编剧成员的阅览形式。

<TaskCard :source="taskCardYaml" />

## 标准格式

```yaml
task:
  id: stable-task-id
  title: 玩家看到的任务名
  status: proposal | reviewed | ready
  package: 内容包 / 章节
  background: 任务起因和世界事实；写事实摘要，不要求成稿

  trigger:
    time: 触发时间或时间条件，例如 18:00、第一天 18:00 后、首演结束后；无时间触发写 none
    place: 场景、anchor、实体或区域；无固定地点写 none
    requires: [必须先满足的变量、任务步骤或事实；无则 none]

  actors:
    - id: 实体或人物 ID；未知写 TODO
      role: 本任务中的职责
  objects:
    - id: 物件 ID；无则 none
      state: 初始持有者、位置或用途

  stages:
    - id: s1
      place: 本阶段实际发生地点、交互实体或目标；必须可定位
      reveal: 玩家进入本阶段时已经知道的信息
      writer:
        background: 编剧阅读的阶段背景；只使用已确认事实
        script:
          - speaker: narrator | 已定义人物 ID | player
            text: 旁白或角色台词
            choice: 可选的内部选项 ID
      coder:
        dialogue:
          purpose: 本阶段对白要完成的沟通目的
          facts: [必须传达的事实；无则 none]
          forbid: [不能提前说或不能承诺的内容；无则 none]
          tone: 语气或情绪；无特殊要求写 neutral
        action: 玩家必须做的可观察动作
        success: 推进本阶段的唯一成功条件
        effects: [成功后的变量、物品、关系或开放入口]
        next: 下一阶段 ID；结束写 done

  result:
    success: 任务完成时玩家实际得到或改变的结果；无则 none
    cancel: 取消、离开或中断后的状态
    reject: 玩家拒绝后的状态与回来方式
    repeat: 已完成后再次操作的行为
    unresolved: 尚未决定、禁止 Agent 自行补全的问题；无则 none
```

## 强制规则

- `trigger.time` 是任务级触发条件；需要按时刻触发时写具体值，例如 `18:00`、`第一天 18:00 后` 或 `首演结束后`。没有时间触发写 `none`。
- 时间暂不作为阶段时间轴。不要给每个阶段标注分钟、小时或动作耗时；阶段先后用 `requires`、`next` 和 `success` 表达。只有未来明确需要阶段独立限时或失效条件时，才扩展字段。
- `trigger.place` 和每个阶段的 `place` 都必须出现；没有固定地点写 `none`，但阶段通常应给出可定位的场景、实体或区域。
- `requires` 写必要条件，不把叙事顺序误写成前置；多个条件注明 `all` 或 `any`。
- `background`、`reveal`、`writer.background`、`coder.dialogue.facts` 和 `coder.dialogue.forbid` 是事实边界，不是让 Agent 自由补写世界设定的提示。
- `writer.script` 只组织可读的旁白、角色台词和玩家选项；角色使用稳定 ID，显示名由人物配置提供。
- Agent 可以把已确认的事实改写成自然背景和台词，可以发挥句式、节奏和情绪；不能新增人物经历、关系、奖励、承诺或玩家未知信息。
- `coder.dialogue.purpose` 约束这段对白要让玩家知道或决定什么；`facts` 必须出现，`forbid` 不得出现。没有特殊要求写 `none`。
- `coder.action` 写玩家实际操作，`coder.success` 写系统可以判定的成功结果；“理解”“感动”“答应”不能单独作为完成条件。
- `coder.effects` 只写确认过的变化。物品去向、变量名、入口和后续任务不确定时写 `TODO`，不让 Agent 猜。
- `reveal` 只包含该阶段可知的信息，不能提前泄露后续人物关系、奖励或结局。
- 独立目标拆成不同任务；有明确前后依赖的阶段才放在同一任务中。
- 对白、素材、Story JSON 和工程验收不写进最小卡；审核通过后再由 Agent 拆成具体交付物。

## 压缩示例

```yaml
task:
  id: tavern-help
  title: 老板娘的招呼
  status: ready
  package: tavern
  background: 客人离席后留下未清理的餐桌，绯月需要帮手。
  trigger:
    time: dining active
    place: tavern / dirty table exists
    requires: none
  actors:
    - id: tavern.hostess
      name: 绯月
      role: requester
  objects:
    - id: dirty-table
      state: dining / tavern
  stages:
    - id: accept
      place: tavern.hostess / counter
      reveal: 绯月需要帮手清理离席餐桌
      writer:
        background: 客人已经离席，桌上还留着餐具。
        script:
          - speaker: tavern.hostess
            text: 能麻烦你帮忙收拾一张桌子吗？
          - speaker: player
            choice: accept_help
            text: 好，我来帮忙。
      coder:
        dialogue:
          purpose: 请求玩家确认是否帮忙
          facts: [玩家需要清理一张离席餐桌]
          forbid: [提前承诺具体谢礼]
          tone: warm
        action: choice.accept_help
        success: choice.confirmed(tavern.hostess, accept_help)
        effects: [help_accepted=true]
        next: clean
  result:
    success: 接受帮工并开放清理阶段
    cancel: 保留已完成阶段
    reject: 不开放清桌，可再次交谈
    repeat: 不重复设置接受变量
    unresolved: none
```

这张卡只定义内容事实和玩家行为，不定义运行时语法。实现能力、具体 ID 和可执行对白由后续拆解确认；任何未确认事项都必须留在 `unresolved`，不能由 Agent 补设定。
