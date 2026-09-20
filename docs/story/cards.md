---
title: 剧本任务卡
description: 按内容包和主线整理的 Writer / Coder 剧本任务卡。
---

# 剧本任务卡

这里的 YAML 是 Agent 和工程使用的结构化输入，卡片是编剧成员的阅读界面。每张卡保留事实边界、玩家动作、成功条件和后续效果；尚未决定的内容明确标为 `TBD`。

## 内容包与主线

### `tavern`

旧版[剧本时间线](/story/timeline)中的酒馆任务已转换为任务卡。首演仍属于演出系统流程，暂不伪装成任务卡；演出结束后才进入“酒馆里的老朋友”。

### `remaining-time`

[S01 · 消磁门牌：入门调查](#remaining-time-s01)是当前 `remaining-time` 内容包的主线卡，覆盖从404观察门牌到暂存原件的六步流程。完整 S01 的后续剧情，以及所有未确认的所有权、许可和保管决定，继续保持 `TBD`。

## tavern · 酒馆任务卡

### 熟悉移动

<script setup>
import TaskCard from '../.vitepress/theme/TaskCard.vue'
import movement from './cards/tavern-movement.yaml?raw'
import help from './cards/tavern-help.yaml?raw'
import lodging from './cards/tavern-lodging.yaml?raw'
import meetBard from './cards/tavern-meet-bard.yaml?raw'
import practice from './cards/tavern-guitar-practice.yaml?raw'
import relicLocation from './cards/tavern-relic-location.yaml?raw'
import relicWager from './cards/tavern-relic-wager.yaml?raw'
import s01 from './cards/remaining-time-s01-door-tag.yaml?raw'
</script>

<TaskCard :source="movement" />

### 老板娘的招呼

<TaskCard :source="help" />

### 一个落脚点

<TaskCard :source="lodging" />

### 酒馆里的老朋友

<TaskCard :source="meetBard" />

### 弦上的第一步

<TaskCard :source="practice" />

### 打听遗物所在地

<TaskCard :source="relicLocation" />

### 打听遗物交换条件

<TaskCard :source="relicWager" />

## remaining-time · 主线

### S01 · 消磁门牌：入门调查 {#remaining-time-s01}

<TaskCard :source="s01" />

## 后续待敲定

以下内容暂不制作成可执行任务卡，直到事实、人物关系、奖励和玩家可知信息完成确认：

- `remaining-time` 的完整 S01 后续章节；
- Eden 的所有权决定、公开使用许可和门牌最终保管决定；
- `tavern` 的山歌、海边故事和乐器传承；
- 赌坊、老鬼、下注规则和遗物取得方式；
- 首演后的其他支线。
