---
title: remaining-time · 新版主线任务卡
description: 余时遗物 31 条可并行遗物主线任务卡，含共享证据、404 重建与三权登记。
---

# remaining-time · 新版主线

S01 之前是从404开始的入门序章；S01 是序章结束后的第一项遗物调查。以下 S01–S31 是其后的正式主线任务。31 条任务可在同一周目并行推进，章节只开放材料节点，不构成强制任务链。

每张卡按 `standard.md` 的最小任务格式编写，并补充 `tier`、案件簇、材料、兜底、合成和三权登记字段。卡片中的 `TODO` 是工程评审项，不是允许 Agent 自行补写的剧情事实。

## 运行约束

- 三类材料分别记录为独立 flag，可按任意顺序取得；取得方式必须区分取走、扫描和获授权暂借。
- 共享证据使用稳定 `evidence_id` 和只读引用，原物只能有一位当前持有人。
- `RECONSTRUCTED` 只证明材料对应关系；实物保管、缓存访问、故事公开范围在 `RIGHTS_REGISTERED` 分开确认。
- NPC 总状态与 `npc_task_flags` 分离；拒绝、归零或离开时只能使用已有签名、公共见证或物件回声作为证据替代。
- `seed_XX_a/b/c` 仍是独立行为机会；合成、交材料和三权登记不写入 `seed_signals`。

<script setup>
import TaskCard from '../.vitepress/theme/TaskCard.vue'
import remaining_time_s01 from './remaining-time/remaining-time-s01.yaml?raw'
import remaining_time_s01_expanded from './remaining-time/remaining-time-s01-expanded.yaml?raw'
import remaining_time_prologue from './remaining-time/remaining-time-prologue.yaml?raw'
import remaining_time_s02 from './remaining-time/remaining-time-s02.yaml?raw'
import remaining_time_s03 from './remaining-time/remaining-time-s03.yaml?raw'
import remaining_time_s04 from './remaining-time/remaining-time-s04.yaml?raw'
import remaining_time_s05 from './remaining-time/remaining-time-s05.yaml?raw'
import remaining_time_s06 from './remaining-time/remaining-time-s06.yaml?raw'
import remaining_time_s07 from './remaining-time/remaining-time-s07.yaml?raw'
import remaining_time_s08 from './remaining-time/remaining-time-s08.yaml?raw'
import remaining_time_s09 from './remaining-time/remaining-time-s09.yaml?raw'
import remaining_time_s10 from './remaining-time/remaining-time-s10.yaml?raw'
import remaining_time_s11 from './remaining-time/remaining-time-s11.yaml?raw'
import remaining_time_s12 from './remaining-time/remaining-time-s12.yaml?raw'
import remaining_time_s13 from './remaining-time/remaining-time-s13.yaml?raw'
import remaining_time_s14 from './remaining-time/remaining-time-s14.yaml?raw'
import remaining_time_s15 from './remaining-time/remaining-time-s15.yaml?raw'
import remaining_time_s16 from './remaining-time/remaining-time-s16.yaml?raw'
import remaining_time_s17 from './remaining-time/remaining-time-s17.yaml?raw'
import remaining_time_s18 from './remaining-time/remaining-time-s18.yaml?raw'
import remaining_time_s19 from './remaining-time/remaining-time-s19.yaml?raw'
import remaining_time_s20 from './remaining-time/remaining-time-s20.yaml?raw'
import remaining_time_s21 from './remaining-time/remaining-time-s21.yaml?raw'
import remaining_time_s22 from './remaining-time/remaining-time-s22.yaml?raw'
import remaining_time_s23 from './remaining-time/remaining-time-s23.yaml?raw'
import remaining_time_s24 from './remaining-time/remaining-time-s24.yaml?raw'
import remaining_time_s25 from './remaining-time/remaining-time-s25.yaml?raw'
import remaining_time_s26 from './remaining-time/remaining-time-s26.yaml?raw'
import remaining_time_s27 from './remaining-time/remaining-time-s27.yaml?raw'
import remaining_time_s28 from './remaining-time/remaining-time-s28.yaml?raw'
import remaining_time_s29 from './remaining-time/remaining-time-s29.yaml?raw'
import remaining_time_s30 from './remaining-time/remaining-time-s30.yaml?raw'
import remaining_time_s31 from './remaining-time/remaining-time-s31.yaml?raw'
</script>

## 任务卡

### 序章 · 404号舱的第一晚
<TaskCard :source="remaining_time_prologue" />

### S01 · 消磁门牌
<TaskCard :source="remaining_time_s01" />

### S01 · 消磁门牌（扩展版）
<TaskCard :source="remaining_time_s01_expanded" />

### S02 · 折叠餐垫
<TaskCard :source="remaining_time_s02" />

### S03 · 失效指挥信标
<TaskCard :source="remaining_time_s03" />

### S04 · 三环任务腕带
<TaskCard :source="remaining_time_s04" />

### S05 · 黑边访问钥匙
<TaskCard :source="remaining_time_s05" />

### S06 · 模拟笑声带
<TaskCard :source="remaining_time_s06" />

### S07 · 七遍审计板
<TaskCard :source="remaining_time_s07" />

### S08 · 缺口热玻璃杯
<TaskCard :source="remaining_time_s08" />

### S09 · 反相肖像膜
<TaskCard :source="remaining_time_s09" />

### S10 · 裂纹演示面罩
<TaskCard :source="remaining_time_s10" />

### S11 · 快乐胶囊
<TaskCard :source="remaining_time_s11" />

### S12 · 故障静音节拍器
<TaskCard :source="remaining_time_s12" />

### S13 · 未完成天顶图
<TaskCard :source="remaining_time_s13" />

### S14 · 单日种子膜
<TaskCard :source="remaining_time_s14" />

### S15 · 热感织物
<TaskCard :source="remaining_time_s15" />

### S16 · 一次性陌生路径钥匙
<TaskCard :source="remaining_time_s16" />

### S17 · 莫比乌斯身份币
<TaskCard :source="remaining_time_s17" />

### S18 · 旧协议徽章
<TaskCard :source="remaining_time_s18" />

### S19 · 加密寄存签
<TaskCard :source="remaining_time_s19" />

### S20 · 空白转时凭证
<TaskCard :source="remaining_time_s20" />

### S21 · 协作餐勺
<TaskCard :source="remaining_time_s21" />

### S22 · 双面停战币
<TaskCard :source="remaining_time_s22" />

### S23 · 镜面荣誉章
<TaskCard :source="remaining_time_s23" />

### S24 · 医疗仿生雨燕
<TaskCard :source="remaining_time_s24" />

### S25 · 自适应工具柄
<TaskCard :source="remaining_time_s25" />

### S26 · 模块化证物盒
<TaskCard :source="remaining_time_s26" />

### S27 · 借用秒表
<TaskCard :source="remaining_time_s27" />

### S28 · 未完成导航鸟
<TaskCard :source="remaining_time_s28" />

### S29 · 六节点计划条
<TaskCard :source="remaining_time_s29" />

### S30 · 透明合同盘
<TaskCard :source="remaining_time_s30" />

### S31 · 未发送声纹日志
<TaskCard :source="remaining_time_s31" />


## 待工程评审

`rights_claimants`、共享场景 ID、运行时变量名、材料取得交互和各任务的具体 NPC ID 需要结合现有引擎字段确认；这些卡片已经给出剧情事实和成功边界，但不替工程决定 Story JSON 语法。
