<script setup lang="ts">
import { computed, ref } from 'vue';
import { parse } from 'yaml';

type Stage = Record<string, any>;
const props = defineProps<{ source: string }>();
const card = parse(props.source).task;
const stageIndex = ref(0);
const currentStage = computed<Stage>(() => card.stages[stageIndex.value]);

function legacy(stage: Stage, key: string) {
  return key.split('.').reduce((value, part) => value?.[part], stage);
}
const currentEvent = computed(() => currentStage.value.event ?? {
  purpose: legacy(currentStage.value, 'coder.dialogue.purpose') ?? '未设定',
  must: legacy(currentStage.value, 'coder.dialogue.facts') ?? [],
  avoid: legacy(currentStage.value, 'coder.dialogue.forbid') ?? [],
  done: legacy(currentStage.value, 'coder.success') ?? '未设定',
  next: legacy(currentStage.value, 'coder.next') ?? '未设定',
});
const currentBackground = computed(() => currentStage.value.background ?? legacy(currentStage.value, 'writer.background') ?? currentStage.value.reveal ?? '');
function list(value: unknown) {
  if (Array.isArray(value)) return value.join('、');
  return value === undefined || value === null || value === '' ? '无' : String(value);
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
        <p>{{ card.background }}</p>
      </div>
      <span class="task-card__status">{{ card.status }}</span>
    </header>

    <section class="task-card__overview">
      <div><strong>触发</strong><span>{{ card.trigger?.time ?? '无' }}</span></div>
      <div><strong>地点</strong><span>{{ card.trigger?.place ?? '无' }}</span></div>
      <div><strong>前置</strong><span>{{ list(card.trigger?.requires) }}</span></div>
      <div><strong>参与者</strong><span>{{ list((card.cast ?? []).map((actor: any) => actor.name)) }}</span></div>
      <div><strong>预计规模</strong><span>{{ card.scale ?? '未设定' }}</span></div>
    </section>

    <section v-if="card.cast?.length || card.objects?.length" class="task-card__participants">
      <div v-if="card.cast?.length">
        <h4>参与 NPC</h4>
        <ul><li v-for="actor in card.cast" :key="actor.name"><strong>{{ actor.name }}</strong> · {{ actor.role }}<span v-if="actor.context"> · {{ actor.context }}</span></li></ul>
      </div>
      <div v-if="card.objects?.length">
        <h4>关键物件</h4>
        <ul><li v-for="object in card.objects" :key="object.name"><strong>{{ object.name }}</strong> · {{ object.context }}</li></ul>
      </div>
    </section>

    <nav class="task-card__navigation" aria-label="任务阶段">
      <button v-for="(stage, index) in card.stages" :key="stage.id" :class="{ active: index === stageIndex }" type="button" @click="stageIndex = index">
        {{ index + 1 }} · {{ stage.title }}
      </button>
    </nav>

    <div class="task-card__progress">统一任务卡 · 阶段 {{ stageIndex + 1 }} / {{ card.stages.length }}</div>

    <section class="task-card__stage">
      <div class="task-card__stage-marker">{{ stageIndex + 1 }}</div>
      <div class="task-card__stage-body">
        <h4 class="task-card__stage-title">{{ currentStage.title }}</h4>
        <div class="task-card__location">{{ currentStage.place }}</div>
        <p class="task-card__background">{{ currentBackground }}</p>

        <section v-if="currentStage.script?.length" class="task-card__script">
          <h4>参考演出稿</h4>
          <div v-for="(line, index) in currentStage.script" :key="index" class="task-card__line">
            <strong>{{ line.speaker ?? (line.type === 'narration' ? '旁白' : line.type === 'player' ? '玩家' : '未命名角色') }}</strong>
            <p>{{ line.text }}</p>
          </div>
        </section>

        <dl class="task-card__facts">
          <div><dt>事件意图</dt><dd>{{ currentEvent.purpose }}</dd></div>
          <div><dt>必须确认</dt><dd>{{ list(currentEvent.must) }}</dd></div>
          <div><dt>避免确认</dt><dd>{{ list(currentEvent.avoid) }}</dd></div>
          <div><dt>完成结果</dt><dd>{{ currentEvent.done }}</dd></div>
          <div><dt>下一阶段</dt><dd>{{ currentEvent.next }}</dd></div>
        </dl>
      </div>
    </section>

    <footer class="task-card__footer">
      <button type="button" :disabled="stageIndex === 0" @click="moveStage(-1)">← 上一阶段</button>
      <span>{{ currentStage.id }}</span>
      <button type="button" :disabled="stageIndex === card.stages.length - 1" @click="moveStage(1)">下一阶段 →</button>
    </footer>

    <footer class="task-card__result">
      <strong>任务完成结果</strong>
      <span>{{ card.result.success }}</span>
      <small>奖励：{{ card.result.reward }}</small>
      <small>未解决：{{ list(card.result.unresolved) }}</small>
    </footer>
  </article>
</template>
