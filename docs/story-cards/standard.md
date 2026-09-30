---
title: 统一任务卡标准
description: 规则驱动与 Agentic 共用的严格剧本数据格式。
---

# 统一任务卡标准

任务卡是编剧、审阅者和下游转换共用的一份详细剧本。它用严格 YAML 保存，用 docs site 渲染成可读的剧本卡。

规则驱动和 Agentic 不维护两套剧本。二者都从同一张任务卡生成自己的运行产物。运行 JSON、Agent prompt、实体映射、状态字段和效果语法不属于编剧任务卡。

## 核心原则

每个阶段同时包含两部分：

- **参考演出稿**：旁白、NPC 台词和玩家示例，帮助人类阅读、判断节奏，也可以直接作为 rule-based 的默认演出。
- **事件边界**：事件意图、必须确认的事实、不能提前确认的事实、可行行动和成功结果，防止下游转换时自行补造剧情。

参考演出稿可以被 Agent 改写，但不能改变事件边界。事件结果和信息边界优先于台词中的具体措辞。

## 严格顶层结构

```yaml
task:
  id: stable-task-id
  title: 玩家看到的任务名
  status: proposal | reviewed | ready
  package: 内容包或章节

  summary:
    background: 玩家为什么遇到这件事；开场可以知道什么
    goal: 玩家最终要完成什么
    boundary: 本任务解决什么，不解决什么
    scale:
      stage_count: 4
      interaction_range: 1-4

  trigger:
    time: 触发时间或条件；没有则写 none
    place: 场景或区域；没有固定地点则写 none
    requires: [必要前置；没有则写 none]

  participants:
    - id: ash
      name: Ash
      role: 本任务中的作用
      context: 与本任务相关的已知事实和当前处境
      boundary: [本任务中不能提前透露的内容]

  objects:
    - id: door-tag-317
      name: 317号门牌
      initial_state: 初始地点、持有人或用途
      possible_actions: [观察, 扫描, 暂借, 交付]
      result: 成功后的去向或变化

  stages:
    - id: ask-ash
      title: 询问 Ash
      place: 下层回廊 · Ash维修台
      background: 玩家此时已经知道的完整背景
      reveal: 玩家进入阶段时已知的信息
      goal: 当前需要完成的行动

      script:
        - type: narration | npc | player
          speaker: 可选；npc 时填写人物名
          text: 旁白、NPC 台词或玩家示例

      event:
        intent: 本阶段必须完成的交流或行动意图
        must_establish: [本阶段必须确认的事实]
        must_not_establish: [本阶段不能提前确认的事实]
        acceptable_actions: [能够合理推进本阶段的玩家行为]

      outcome:
        success: 可以确认的阶段完成结果
        next_stage: 下一阶段 ID；任务结束写 done
        retained: [完成后保留的信息、物品或状态]

      interruptions:
        leave: 玩家离开时如何保留和恢复
        reject: 玩家拒绝时如何处理
        repeat: 玩家重复操作时如何处理

  result:
    success: 任务完成时玩家实际得到或改变的结果
    boundary: 任务完成后仍未解决的内容
    reward: 额外奖励；没有则写无
    cancel: 任务中断后的保留状态
    repeat: 完成后再次访问的行为
```

顶层和阶段只允许使用上述字段。不要添加 `writer`、`coder`、`prompt` 或运行时字段。

## 编剧如何填写

### `summary`

概括整项任务的起因、目标、完成边界和规模。规模用于控制剧情长度，不要求固定台词字数。

### `participants`

只写本任务所需的上下文，不写完整人物档案。`boundary` 是该 NPC 在本任务中不能提前透露的内容，不是人格或长期记忆。

### `objects`

写清楚物件的初始位置、可以执行的操作和成功后的变化。扫描、暂借、持有和交付应区分开。

### `script`

这是人类可读的参考演出稿。它可以直接用于 rule-based 的默认演出，也可以被 Agent 根据玩家问法改写。

台词不是唯一合法回应，也不是任务完成条件。不要为了覆盖所有玩家问法而写大量分支；把稳定事实和边界写进 `event`。

### `event`

这是防止下游幻觉的最小护栏：

- `intent`：本阶段需要完成什么。
- `must_establish`：玩家最终必须获得或确认什么。
- `must_not_establish`：本阶段不能提前透露或承诺什么。
- `acceptable_actions`：哪些合理的玩家行为可以推进事件。

### `outcome` 与 `interruptions`

结果必须能通过玩家行为或可观察状态确认。不能只写“玩家理解了”“NPC被感动了”。离开、拒绝和重复访问也要说明行为，避免下游自行决定是否推进。

## 转换原则

Rule-based 和 Agentic 都读取同一张任务卡：

- Rule-based 可以直接采用 `script`，并根据 `outcome` 推进。
- Agentic 读取当前阶段的背景、参考演出稿和事件边界，再自然回应玩家。
- Agentic 可以改变句式、顺序和长度，但不能改变 `must_establish`、`must_not_establish` 或 `outcome`。
- 两者都不通过文本相似度判断任务完成。

信息优先级如下：

```text
任务结果与信息边界
  > 事件意图
  > 参考演出稿中的事实
  > 参考演出稿的具体措辞
```

如果参考台词和事件边界冲突，任务卡应被视为内容错误，需要修改，不交给 Agent 自行解释。

## 审阅标准

1. 不看下游代码也能理解任务和每个阶段。
2. 参考演出稿能表达预期的情节、节奏和信息揭示顺序。
3. 每个阶段都有明确意图、必须确认和禁止提前确认的内容。
4. 玩家存在多种合理问法时，事件仍然有清晰的成功边界。
5. 失败、拒绝、离开和重复访问不会产生未声明的剧情变化。
6. Rule-based 可以直接采用参考演出稿，Agentic 不需要补造关键事实。
7. 阶段数量和交互规模符合任务预期。
