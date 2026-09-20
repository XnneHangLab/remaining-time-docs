---
title: tavern · 旧版任务卡
description: 从旧版酒馆剧本时间线迁移的 Agent 任务卡。
---

# tavern · 旧版

这些卡片由旧版酒馆剧本内容迁移而来，统一使用 `package: tavern`。它们保留已有事实和效果，不代表会自动迁移到 `remaining-time` 新内容包。

<script setup>
import TaskCard from '../.vitepress/theme/TaskCard.vue'
import movement from './tavern/tavern-movement.yaml?raw'
import help from './tavern/tavern-help.yaml?raw'
import lodging from './tavern/tavern-lodging.yaml?raw'
import meetBard from './tavern/tavern-meet-bard.yaml?raw'
import practice from './tavern/tavern-guitar-practice.yaml?raw'
import relicLocation from './tavern/tavern-relic-location.yaml?raw'
import relicWager from './tavern/tavern-relic-wager.yaml?raw'
</script>

## 熟悉移动

<TaskCard :source="movement" />

## 老板娘的招呼

<TaskCard :source="help" />

## 一个落脚点

<TaskCard :source="lodging" />

## 酒馆里的老朋友

<TaskCard :source="meetBard" />

## 弦上的第一步

<TaskCard :source="practice" />

## 打听遗物所在地

<TaskCard :source="relicLocation" />

## 打听遗物交换条件

<TaskCard :source="relicWager" />

首演仍属于演出系统流程，暂不伪装成任务卡；演出结束后才进入“酒馆里的老朋友”。
