---
title: Agent 任务卡
description: 面向编剧 Agent 的高度压缩剧情任务交付格式。
---

# Agent 任务卡

这不是面向玩家或普通读者的剧情说明，而是交给编剧 Agent 继续加工的**最小任务规格**。一张卡只描述一个任务；所有字段都必须填写，确实不存在时写 `none`，未知内容写 `TODO`，禁止留空或让 Agent 猜测。

## 标准格式

```yaml
task:
  id: stable-task-id
  title: 玩家看到的任务名
  status: proposal | reviewed | ready
  package: 内容包 / 章节

  trigger:
    time: 触发时间、时间段或事件；无固定时间写 none
    place: 场景、anchor、实体或区域；无固定地点写 none
    requires: [必须先满足的变量、任务步骤或事实；无则 none]

  actors: [实体或人物: 本任务中的职责；未知 ID 写 TODO]
  objects: [物件: 初始持有者/位置/用途；无则 none]

  stages:
    - id: s1
      time: 本阶段开放时间或时间条件；无则 none
      place: 本阶段实际发生地点、交互实体或目标；必须可定位
      reveal: 玩家进入本阶段时已经知道的信息
      action: 玩家必须做的可观察动作
      success: 推进本阶段的唯一成功条件
      effect: 成功后的变量、物品、关系、开放入口或下一阶段
      next: 下一阶段 ID；结束写 done

  result:
    success: 任务完成时玩家实际得到或改变的结果；无则 none
    cancel: 取消、离开或中断后的状态
    reject: 玩家拒绝后的状态与回来方式
    repeat: 已完成后再次操作的行为
    unresolved: 尚未决定、禁止 Agent 自行补全的问题；无则 none
```

## 强制规则

- `trigger.time`、`trigger.place` 和每个阶段的 `time`、`place` 都必须出现；没有限制也写 `none`。
- 时间只表达**开放、失效、作息、营业或截止约束**。使用能表达约束的最粗粒度：`第一天傍晚`、`首演结束后`、`营业时间内`、`午夜前`。只有运行规则确实依赖精确时刻时才写小时或分钟。
- 不要用时间记录完整剧情进度、人物每分钟做什么或玩家完成动作需要几分钟；阶段先后用 `requires`、`next` 和 `success` 表达。没有实际时间限制时写 `none`。
- `requires` 写必要条件，不把叙事顺序误写成前置；多个条件注明 `all` 或 `any`。
- `action` 写玩家实际操作，`success` 写系统可以判定的成功结果；“理解”“感动”“答应”不能单独作为完成条件。
- `effect` 只写确认过的变化。物品去向、变量名、入口和后续任务不确定时写 `TODO`，不让 Agent 猜。
- `reveal` 只包含该阶段可知的信息，不能提前泄露后续人物关系、奖励或结局。
- 独立目标拆成不同任务；有明确前后依赖的阶段才放在同一任务中。
- 对白、素材、实体 ID、Story JSON 和工程验收不写进最小卡；审核通过后再由 Agent 拆成具体交付物。

## 压缩示例

```yaml
task:
  id: tavern-help
  title: 老板娘的招呼
  status: ready
  package: tavern
  trigger:
    time: dining active
    place: tavern / dirty table exists
    requires: none
  actors: [tavern.hostess: requester, tavern.waiter: service owner]
  objects: [dirty table: dining state / tavern]
  stages:
    - id: accept
      time: after trigger
      place: tavern.hostess / counter
      reveal: 绯月需要帮手清理离席餐桌
      action: confirm help
      success: choice.accept_help confirmed
      effect: unlock clean; next clean
      next: clean
    - id: clean
      time: after accept; guest departed
      place: tavern / dirty table
      reveal: 桌上留下餐具，需要玩家处理
      action: complete one manual clean
      success: dining.cleaned(tavern) = 1
      effect: unlock reward; next reward
      next: reward
    - id: reward
      time: after clean
      place: tavern.hostess / counter
      reveal: 绯月答应提供一瓶汽水
      action: confirm reward
      success: item transfer succeeds
      effect: citrus-soda +1; room access on; done
      next: done
  result:
    success: 首桌谢礼、客房入口、后续按桌帮工
    cancel: 保留已完成阶段
    reject: 不开放清桌；可再次交谈
    repeat: 不重复发首桌谢礼；后续清桌按独立规则结算
    unresolved: none
```

这张卡只定义内容事实和玩家行为，不定义运行时语法。实现能力、具体 ID 和可执行对白由后续拆解确认；任何未确认事项都必须留在 `unresolved`，不能由 Agent 补设定。
