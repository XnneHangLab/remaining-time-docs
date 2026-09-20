<script setup lang="ts">
import { computed, ref } from 'vue';
import { parse } from 'yaml';

type View = 'writer' | 'coder';

const props = defineProps<{ source: string }>();
const card = parse(props.source).task;
const view = ref<View>('writer');
const stageIndex = ref(0);
const currentStage = computed(() => card.stages[stageIndex.value]);
const speakerNames = new Map<string, string>([
  ['narrator', '旁白'],
  ['player', '玩家'],
  ...card.actors.map((actor: { id: string; name?: string }) =>
    [actor.id, actor.name || '未命名角色'] as [string, string]),
]);

function list(value: unknown) {
  if (Array.isArray(value)) return value.join('、');
  return value === undefined || value === null || value === '' ? 'none' : String(value);
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

    <section class="task-card__trigger">
      <div><strong>触发时间</strong><span>{{ card.trigger.time }}</span></div>
      <div><strong>触发地点</strong><span>{{ card.trigger.place }}</span></div>
      <div><strong>前置</strong><span>{{ list(card.trigger.requires) }}</span></div>
    </section>

    <nav class="task-card__navigation" aria-label="任务阶段">
      <button
        v-for="(stage, index) in card.stages"
        :key="stage.id"
        :class="{ active: index === stageIndex }"
        type="button"
        @click="stageIndex = index"
      >
        {{ index + 1 }} · {{ stage.id }}
      </button>
    </nav>

    <section class="task-card__viewbar" aria-label="卡片视图">
      <span>阶段 {{ stageIndex + 1 }} / {{ card.stages.length }}</span>
      <div role="group" aria-label="切换视图">
        <button :class="{ active: view === 'writer' }" type="button" @click="view = 'writer'">Writer view</button>
        <button :class="{ active: view === 'coder' }" type="button" @click="view = 'coder'">Coder view</button>
      </div>
    </section>

    <section v-if="view === 'writer'" class="task-card__stage task-card__writer">
      <div class="task-card__stage-marker">{{ currentStage.id }}</div>
      <div class="task-card__stage-body">
        <div class="task-card__location">{{ currentStage.place }}</div>
        <p class="task-card__reveal">{{ currentStage.reveal }}</p>
        <p class="task-card__background">{{ currentStage.writer.background }}</p>
        <div class="task-card__script">
          <div v-for="(line, index) in currentStage.writer.script" :key="index" class="task-card__line">
            <strong>{{ speakerNames.get(line.speaker) || '未定义角色' }}</strong>
            <span v-if="line.choice" class="task-card__choice">玩家选项</span>
            <p>{{ line.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <section v-else class="task-card__stage task-card__coder">
      <div class="task-card__stage-marker">{{ currentStage.id }}</div>
      <div class="task-card__stage-body">
        <div class="task-card__location">{{ currentStage.place }}</div>
        <dl>
          <div><dt>对白目的</dt><dd>{{ currentStage.coder.dialogue.purpose }}</dd></div>
          <div><dt>必须传达</dt><dd>{{ list(currentStage.coder.dialogue.facts) }}</dd></div>
          <div><dt>禁止透露</dt><dd>{{ list(currentStage.coder.dialogue.forbid) }}</dd></div>
          <div><dt>语气</dt><dd>{{ currentStage.coder.dialogue.tone }}</dd></div>
          <div><dt>玩家动作</dt><dd>{{ currentStage.coder.action }}</dd></div>
          <div><dt>成功条件</dt><dd>{{ currentStage.coder.success }}</dd></div>
          <div><dt>效果</dt><dd>{{ list(currentStage.coder.effects) }}</dd></div>
          <div><dt>下一阶段</dt><dd>{{ currentStage.coder.next }}</dd></div>
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
    </footer>
  </article>
</template>
