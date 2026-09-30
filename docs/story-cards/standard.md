---
title: 统一任务卡标准
description: 规则驱动与 Agentic 共用的严格剧本格式。
---

# 统一任务卡标准

任务卡是编剧、审阅者和下游转换共用的一份详细剧本。源文件使用严格 YAML，docs site 将它渲染成可读的剧本卡。

Rule-based 和 Agentic 只使用这一份剧本。运行 JSON、Agent prompt、实体映射、状态字段和效果语法属于下游转换，不属于编剧输入。

## 结构

任务卡只有三层：

1. **任务概览**：说明整项任务的背景、目标、边界和规模。
2. **参与者与物件**：说明本任务需要的 NPC 和物件上下文。
3. **事件阶段**：每个阶段包含背景、参考演出稿和事件约束。

## 严格 YAML 格式

```yaml
task:
  id: stable-task-id
  title: 玩家看到的任务名
  status: proposal | reviewed | ready
  package: 内容包或章节

  background: 玩家为什么遇到这件事；开场可以知道什么
  goal: 玩家最终要完成什么
  boundary: 本任务解决什么，不解决什么
  scale: 4个事件阶段；每阶段约1至4轮交互

  trigger:
    time: 触发时间或条件；没有则写 none
    place: 场景或区域；没有固定地点则写 none
    requires: [必要前置；没有则写 none]

  cast:
    - name: Ash
      role: 本任务中的作用
      context: 与本任务相关的事实和处境

  objects:
    - name: 317号门牌
      context: 初始位置、可执行操作和成功后的变化

  stages:
    - id: ask-ash
      title: 询问 Ash
      place: 下层回廊 · Ash维修台
      background: 玩家此时已经知道的完整背景

      script:
        - type: narration | npc | player
          speaker: 可选；npc 时填写人物名
          text: 旁白、NPC 台词或玩家示例

      event:
        purpose: 本阶段必须完成的交流或行动意图
        must: [本阶段必须确认的事实]
        avoid: [本阶段不能提前确认的事实]
        done: 可以确认的阶段完成结果
        next: 下一阶段 ID；任务结束写 done

  result:
    success: 任务完成时玩家实际得到或改变的结果
    reward: 额外奖励；没有则写无
    unresolved: [任务完成后仍未解决的内容]
```

字段保持封闭。不要添加 `writer`、`coder`、`prompt`、`process`、`interruptions`、`condition` 或运行时效果字段。

## 参考演出稿

`script` 是剧本正文，也是控制剧情长度和节奏的参考。Rule-based 可以直接采用它；Agentic 可以根据玩家的实际问法改写它。

台词不是唯一合法回答，也不是任务完成条件。它只需要表达这一事件的理想演出，不需要覆盖所有玩家分支。

## 事件约束

`event` 是每个阶段最小的语义边界：

- `purpose`：这一阶段想完成什么。
- `must`：玩家最终必须确认或获得什么。
- `avoid`：这一阶段不能提前透露或承诺什么。
- `done`：什么结果算完成。
- `next`：完成后进入哪一阶段。

不再单独填写 `goal`、`reveal`、`facts`、`must_establish`、`acceptable_actions`、`success`、`outcome`、`process` 或 `interruptions`。这些内容分别合并到了任务背景、事件约束和结果字段中。

通用的离开、拒绝和重复行为由运行时规则处理。只有特殊行为需要记录时，才把它写进 `must`、`avoid` 或 `done`，不要为每个阶段重复填写通用边界。

## 转换原则

```text
事件结果与边界 > 参考演出稿中的事实 > 参考演出稿的具体措辞
```

- Rule-based 读取阶段和事件结果，可以直接使用参考演出稿。
- Agentic 读取背景、参考演出稿和事件约束，再自然回应玩家。
- Agent 可以改变句式、顺序和长度，但不能改变 `must`、`avoid` 或 `done`。
- 两种实现都不通过文本相似度判断任务完成。

## 审阅标准

1. 只看任务卡就能理解整项任务和每个事件。
2. 参考演出稿表达了预期情节、节奏和信息揭示顺序。
3. 每个事件都有明确的意图、必须确认、禁止提前确认和完成结果。
4. Agent 不需要自行补造关键事实。
5. Rule-based 可以直接采用参考演出稿。
6. 任务规模符合预期，没有依赖无限对白推进。
