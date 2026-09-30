<script setup lang="ts">
import { computed, ref } from 'vue';
import { parse } from 'yaml';

type Stage = Record<string, any>;
const props = defineProps<{ source: string }>();
const card = parse(props.source).task;
const stageIndex = ref(0);
const currentStage = computed<Stage>(() => card.stages[stageIndex.value]);
const participants = computed(() => card.participants ?? card.actors ?? []);

function list(value: unknown) {
  if (Array.isArray(value)) return value.join('、');
  return value === undefined || value === null || value === '' ? '无' : String(value);
}
function legacy(stage: Stage, key: string) {
  return key.split('.').reduce((value, part) => value?.[part], stage);
}
function field(stage: Stage, key: string, oldKey?: string) {
  return stage[key] ?? (oldKey ? legacy(stage, oldKey) : undefined);
}
function moveStage(delta: number) {
  stageIndex.value = Math.max(0, Math.min(card.stages.length - 1, stageIndex.value + delta));
}
</script>

<template>
  <article class="task-card">
    <header class="task-card__header">
      <div>
        <p class="task-card__eyebrow">{{ card.id }} · {{ card.package }}</p>
        <h3>{{ card.title }}</h3>
        <p>{{ card.summary?.background ?? card.background }}</p>
      </div>
      <span class="task-card__status">{{ card.status }}</span>
    </header>

    <section class="task-card__overview">
      <div><strong>触发</strong><span>{{ card.trigger?.time ?? '无' }}</span></div>
      <div><strong>地点</strong><span>{{ card.trigger?.place ?? '无' }}</span></div>
      <div><strong>前置</strong><span>{{ list(card.trigger?.requires) }}</span></div>
      <div><strong>参与者</strong><span>{{ list(participants.map((actor: any) => actor.name || actor.id)) }}</span></div>
      <div><strong>预计规模</strong><span>{{ typeof (card.summary?.scale ?? card.scale) === 'object' ? `${(card.summary?.scale ?? card.scale).stage_count} 个阶段；每阶段 ${(card.summary?.scale ?? card.scale).interaction_range} 轮交互` : (card.summary?.scale ?? card.scale ?? '未设定') }}</span></div>
    </section>

    <section v-if="participants.length || card.objects?.length" class="task-card__participants">
      <div v-if="participants.length">
        <h4>参与 NPC</h4>
        <ul><li v-for="actor in participants" :key="actor.id"><strong>{{ actor.name || actor.id }}</strong> · {{ actor.role }}<span v-if="actor.context"> · {{ actor.context }}</span></li></ul>
      </div>
      <div v-if="card.objects?.length">
        <h4>关键物件</h4>
        <ul><li v-for="object in card.objects" :key="object.id"><strong>{{ object.name || object.id }}</strong> · {{ object.initial_state ?? object.state }}<span v-if="object.result"> · {{ object.result }}</span></li></ul>
      </div>
    </section>

    <nav class="task-card__navigation" aria-label="任务阶段">
      <button v-for="(stage, index) in card.stages" :key="stage.id" :class="{ active: index === stageIndex }" type="button" @click="stageIndex = index">
        {{ index + 1 }} · {{ stage.title ?? stage.id }}
      </button>
    </nav>

    <div class="task-card__progress">统一任务卡 · 阶段 {{ stageIndex + 1 }} / {{ card.stages.length }}</div>

    <section class="task-card__stage">
      <div class="task-card__stage-marker">{{ stageIndex + 1 }}</div>
      <div class="task-card__stage-body">
        <h4 class="task-card__stage-title">{{ currentStage.title ?? currentStage.id }}</h4>
        <div class="task-card__location">{{ currentStage.place }}</div>
        <p class="task-card__reveal">{{ currentStage.reveal }}</p>
        <p class="task-card__background">{{ currentStage.background ?? legacy(currentStage, 'writer.background') ?? currentStage.reveal }}</p>

        <section v-if="currentStage.script?.length" class="task-card__script">
          <h4>参考演出稿</h4>
          <div v-for="(line, index) in currentStage.script" :key="index" class="task-card__line">
            <strong>{{ line.speaker ?? (line.type === 'narration' ? '旁白' : line.type === 'player' ? '玩家' : '未命名角色') }}</strong>
            <p>{{ line.text }}</p>
          </div>
        </section>

        <dl class="task-card__facts">
          <div><dt>玩家目标</dt><dd>{{ currentStage.goal ?? field(currentStage, 'action', 'coder.action') ?? '未设定' }}</dd></div>
          <div><dt>事件意图</dt><dd>{{ currentStage.event?.intent ?? field(currentStage, 'intent', 'coder.dialogue.purpose') ?? '未设定' }}</dd></div>
          <div><dt>必须确认</dt><dd>{{ list(currentStage.event?.must_establish ?? field(currentStage, 'facts', 'coder.dialogue.facts')) }}</dd></div>
          <div><dt>不能提前确认</dt><dd>{{ list(currentStage.event?.must_not_establish ?? field(currentStage, 'forbid', 'coder.dialogue.forbid')) }}</dd></div>
          <div><dt>可行行动</dt><dd>{{ list(currentStage.event?.acceptable_actions ?? field(currentStage, 'action', 'coder.action')) }}</dd></div>
          <div><dt>成功结果</dt><dd>{{ currentStage.outcome?.success ?? field(currentStage, 'success', 'coder.success') ?? '未设定' }}</dd></div>
          <div><dt>下一阶段</dt><dd>{{ currentStage.outcome?.next_stage ?? currentStage.next ?? legacy(currentStage, 'coder.next') ?? '未设定' }}</dd></div>
        </dl>

        <div v-if="currentStage.process?.length" class="task-card__process">
          <h4>过程步骤</h4>
          <ol><li v-for="(step, index) in currentStage.process" :key="step.id || index"><strong>{{ step.id || `步骤 ${index + 1}` }}</strong><span>{{ step.action }}</span><span v-if="step.observed">结果：{{ step.observed }}</span><span v-if="step.change">变化：{{ step.change }}</span></li></ol>
        </div>

        <section v-if="currentStage.interruptions" class="task-card__interruptions">
          <h4>中断与重复</h4>
          <dl><div v-for="(text, kind) in currentStage.interruptions" :key="kind"><dt>{{ kind }}</dt><dd>{{ text }}</dd></div></dl>
        </section>
      </div>
    </section>

    <footer class="task-card__footer">
      <button type="button" :disabled="stageIndex === 0" @click="moveStage(-1)">← 上一阶段</button>
      <span>{{ currentStage.id }}</span>
      <button type="button" :disabled="stageIndex === card.stages.length - 1" @click="moveStage(1)">下一阶段 →</button>
    </footer>

    <footer class="task-card__result">
      <strong>任务完成结果</strong>
      <span>{{ card.result?.success ?? card.result ?? '未设定' }}</span>
      <small v-if="card.result?.reward">奖励：{{ card.result.reward }}</small>
      <small v-if="card.result?.boundary">边界：{{ card.result.boundary }}</small>
    </footer>
  </article>
</template>
