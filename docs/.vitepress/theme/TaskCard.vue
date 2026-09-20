<script setup lang="ts">
import { parse } from 'yaml';

const props = defineProps<{ source: string }>();
const card = parse(props.source).task;
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
      <div><strong>前置</strong><span>{{ card.trigger.requires }}</span></div>
    </section>

    <ol class="task-card__stages">
      <li v-for="stage in card.stages" :key="stage.id" class="task-card__stage">
        <div class="task-card__stage-marker">{{ stage.id }}</div>
        <div class="task-card__stage-body">
          <div class="task-card__location">{{ stage.place }}</div>
          <p class="task-card__reveal">{{ stage.reveal }}</p>
          <dl>
            <div><dt>对白目的</dt><dd>{{ stage.dialogue.purpose }}</dd></div>
            <div><dt>必须传达</dt><dd>{{ stage.dialogue.facts.join('、') }}</dd></div>
            <div><dt>禁止透露</dt><dd>{{ stage.dialogue.forbid === 'none' ? '无' : stage.dialogue.forbid.join('、') }}</dd></div>
            <div><dt>玩家动作</dt><dd>{{ stage.action }}</dd></div>
            <div><dt>成功条件</dt><dd>{{ stage.success }}</dd></div>
            <div><dt>成功效果</dt><dd>{{ stage.effect }}</dd></div>
          </dl>
        </div>
      </li>
    </ol>

    <footer class="task-card__result">
      <strong>完成结果</strong>
      <span>{{ card.result.success }}</span>
    </footer>
  </article>
</template>
