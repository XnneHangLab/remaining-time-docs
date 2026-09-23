<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { withBase } from 'vitepress';
import snapshot from './generated/rooms.json';
import { visualPlacement, type Visual } from './generated/assets';

type Layer = {
  visual: Visual; position: number[]; depth: number; npc: boolean;
  image: string; crop: number[] | null;
};
type Room = {
  id: string; name: string; width: number; height: number;
  original: string | null; variants: { plain: string | null; box: string | null };
  active: string; background: string; layoutSource: string; mapSource: string; sceneSource: string;
  issues: string[]; layers: Layer[]; npcCount: number; objectCount: number;
};
const data = snapshot as {
  commit: string; contentVersion: string; rooms: Room[];
  images: Record<string, { url: string; width: number; height: number; sha256: string }>;
};
const selected = ref(data.rooms[0].id);
const room = computed(() => data.rooms.find((r) => r.id === selected.value)!);
const showNpcs = ref(false);
const zoom = ref(100);
const canvas = ref<HTMLCanvasElement>();
const status = ref('');
const failure = ref('');
let generation = 0;
const activeLabel = (value: string) => value === 'box' ? '黑框版' : value === 'plain' ? '普通版' : '其他背景';
const boxCount = data.rooms.filter((r) => r.active === 'box').length;
const originalCount = data.rooms.filter((r) => r.original).length;
const objectRoomCount = data.rooms.filter((r) => r.objectCount > 0).length;
const objectCount = data.rooms.reduce((total, r) => total + r.objectCount, 0);
const progressRows = computed(() => data.rooms.map((item) => ({
  ...item,
  furniture: item.objectCount > 0 ? '已接入' : '待接入',
})));
const panels = computed(() => [
  { title: '原始完整布局', image: room.value.original, active: false, missing: '此提交未找到原始完整 PNG。' },
  { title: '拆分后空背景 · 普通版', image: room.value.variants.plain, active: room.value.active === 'plain', missing: '此提交未收录普通空背景。' },
  { title: '拆分后空背景 · 黑框版', image: room.value.variants.box, active: room.value.active === 'box', missing: '此提交未收录黑框布局与背景，不能视为已改造。' },
]);
const imageUrl = (path: string) => withBase(data.images[path].url);

async function draw() {
  const target = canvas.value;
  if (!target) return;
  const ticket = ++generation;
  const current = room.value;
  const layers = current.layers.filter((layer) => showNpcs.value || !layer.npc)
    .slice().sort((a, b) => a.depth - b.depth);
  target.width = current.width;
  target.height = current.height;
  failure.value = '';
  status.value = '正在载入本房间的图层…';
  try {
    const entries = await Promise.all([...new Set(layers.map((l) => l.image))].map(async (path) => {
      const image = new Image();
      image.src = imageUrl(path);
      try { await image.decode(); }
      catch { throw new Error(`图片加载失败：${path}`); }
      return [path, image] as const;
    }));
    if (ticket !== generation) return;
    const images = new Map(entries);
    const context = target.getContext('2d');
    if (!context) throw new Error('浏览器不支持 Canvas 2D。');
    context.imageSmoothingEnabled = false;
    context.fillStyle = '#000';
    context.fillRect(0, 0, target.width, target.height);
    for (const layer of layers) {
      const image = images.get(layer.image)!;
      const [sx, sy, sw, sh] = layer.crop ?? [0, 0, image.naturalWidth, image.naturalHeight];
      const placement = visualPlacement(layer.visual, layer.position, layer.depth);
      const width = placement.width ?? sw;
      const height = placement.height ?? sh;
      context.drawImage(image, sx, sy, sw, sh,
        placement.x - placement.anchor.x * width,
        placement.y - placement.anchor.y * height, width, height);
    }
    status.value = `已绘制 ${layers.length} 个图层（含背景与门），${current.width} × ${current.height} 像素。`;
  } catch (error) {
    if (ticket !== generation) return;
    status.value = '';
    failure.value = error instanceof Error ? error.message : String(error);
  }
}
watch([selected, showNpcs], () => {
  if (typeof window !== 'undefined') {
    const url = new URL(window.location.href);
    url.searchParams.set('room', selected.value);
    window.history.replaceState(window.history.state, '', url);
  }
  void draw();
}, { flush: 'post' });
onMounted(() => {
  const requested = new URLSearchParams(window.location.search).get('room');
  if (requested && data.rooms.some((r) => r.id === requested)) selected.value = requested;
  void draw();
});
onUnmounted(() => { generation++; });
</script>

<template>
  <section class="room-preview" aria-label="房间布局对照">
    <p class="snapshot">固定快照 <code>{{ data.commit.slice(0, 12) }}</code> · {{ data.contentVersion }}<br>
      {{ data.rooms.length }} 个房间：{{ boxCount }} 个使用黑框版，{{ data.rooms.filter(r => r.active === 'plain').length }} 个使用普通版。
      这是该提交的实际运行配置，不随游戏远端自动变化。
    </p>
    <section class="quick-progress" aria-label="全部房间进度速览">
      <div class="progress-heading">
        <div>
          <h2>总进度速览</h2>
          <p class="metadata">先看这一栏即可掌握全部房间；点击房间名进入下面的四图对照。</p>
        </div>
        <span class="progress-total">{{ data.rooms.length }} 间房</span>
      </div>
      <div class="progress-cards">
        <div><strong>{{ originalCount }}/{{ data.rooms.length }}</strong><span>原始 PNG</span></div>
        <div><strong>{{ boxCount }}/{{ data.rooms.length }}</strong><span>当前使用黑框版</span></div>
        <div><strong>{{ data.rooms.length - boxCount }}/{{ data.rooms.length }}</strong><span>当前使用普通版</span></div>
        <div><strong>{{ objectRoomCount }}/{{ data.rooms.length }}</strong><span>已接入独立物件</span></div>
        <div><strong>{{ objectCount }}</strong><span>独立物件总数</span></div>
      </div>
      <div class="progress-table-wrap">
        <table class="progress-table">
          <thead><tr><th>房间</th><th>当前背景</th><th>普通 / 黑框</th><th>独立物件</th><th>拼装状态</th></tr></thead>
          <tbody><tr v-for="item in progressRows" :key="item.id">
            <td><button type="button" @click="selected = item.id">{{ item.name }}</button></td>
            <td><span :class="['status-pill', item.active]">{{ activeLabel(item.active) }}</span></td>
            <td>{{ item.variants.plain ? '✓' : '—' }} / {{ item.variants.box ? '✓' : '—' }}</td>
            <td>{{ item.objectCount }}</td>
            <td><span :class="['status-pill', item.furniture === '已接入' ? 'done' : 'pending']">{{ item.furniture }}</span></td>
          </tr></tbody>
        </table>
      </div>
      <p class="metadata">“已接入独立物件”只表示当前运行配置已有可单独摆放的家具或物件，不等同于布局已验收完成；只有背景与门的房间仍明确显示为待接入。</p>
    </section>
    <label class="room-picker">选择房间
      <select v-model="selected">
        <option v-for="item in data.rooms" :key="item.id" :value="item.id">
          {{ item.name }} · {{ activeLabel(item.active) }} · {{ item.objectCount }} 件独立物件
        </option>
      </select>
    </label>
    <h2>{{ room.name }} <small>{{ room.id }}</small></h2>
    <p>运行中使用 <strong>{{ activeLabel(room.active) }}</strong> · {{ room.objectCount }} 件独立物件 · {{ room.npcCount }} 个 NPC。</p>
    <p v-if="!room.objectCount" class="notice">当前只接入背景、门和可能存在的 NPC，尚未拼回独立家具；背景上仍保留的固定结构不计作独立物件。</p>
    <ul v-if="room.issues.length" class="notice" aria-label="数据差异">
      <li v-for="issue in room.issues" :key="issue">{{ issue }}</li>
    </ul>
    <div class="comparison">
      <figure v-for="panel in panels" :key="panel.title">
        <figcaption>{{ panel.title }} <strong v-if="panel.active" class="badge">当前使用</strong></figcaption>
        <template v-if="panel.image">
          <a :href="imageUrl(panel.image)" target="_blank" rel="noopener" :aria-label="`${panel.title}，打开原尺寸图片`">
            <img :src="imageUrl(panel.image)" :alt="`${room.name}：${panel.title}`"
              :width="data.images[panel.image].width" :height="data.images[panel.image].height" loading="lazy">
          </a>
          <p class="metadata">{{ data.images[panel.image].width }} × {{ data.images[panel.image].height }} · 点击查看原尺寸</p>
          <code class="source-path">{{ panel.image }}</code>
        </template>
        <p v-else class="missing">{{ panel.missing }}</p>
      </figure>
      <figure>
        <figcaption>当前拼装布局 <strong class="badge">浏览器实时绘制</strong></figcaption>
        <div class="controls">
          <label><input v-model="showNpcs" type="checkbox"> 显示 NPC 初始站姿</label>
          <label>缩放 <select v-model.number="zoom">
            <option :value="100">适应宽度</option><option :value="150">150%</option><option :value="200">200%</option><option :value="300">300%</option>
          </select></label>
        </div>
        <div class="canvas-scroll">
          <canvas ref="canvas" :style="{ width: `${zoom}%` }" role="img" :aria-label="`${room.name}：按游戏配置拼装的初始布局`">
            当前浏览器需要支持 Canvas 才能查看拼装布局。
          </canvas>
        </div>
        <p role="status" class="metadata">{{ status }}</p>
        <p v-if="failure" role="alert" class="notice">{{ failure }}</p>
        <p class="metadata">包含背景、独立物件、可交互家具与门。NPC 可选显示；不含玩家、存档变化、移动与高亮。</p>
      </figure>
    </div>
    <details>
      <summary>本房间的数据来源与一致性边界</summary>
      <ul>
        <li>运行背景：<code>{{ room.background }}</code></li>
        <li>源配方选择：<code>{{ room.layoutSource }}</code></li>
        <li>运行地图：<code>{{ room.mapSource }}</code></li>
        <li>场景实体：<code>{{ room.sceneSource }}</code></li>
      </ul>
      <p>图片和布局均从同一个提交导出，图片 URL 也包含提交号，避免不同版本缓存混用。定位直接复用该提交的 visualPlacement，按游戏的 depth 稳定排序，使用最近邻采样、原尺寸和脚点；NPC 固定为初始朝向的第一个待机帧。此处使用 Canvas 2D，游戏使用 PixiJS，缩放采样与边缘混合不承诺逐像素相同。</p>
    </details>
    <details>
      <summary>全部房间的版本与拼装进度</summary>
      <div class="table-scroll"><table>
        <thead><tr><th>房间</th><th>普通空背景</th><th>黑框空背景</th><th>运行中使用</th><th>独立物件</th></tr></thead>
        <tbody><tr v-for="item in data.rooms" :key="item.id">
          <td><button type="button" @click="selected = item.id">{{ item.name }}</button></td>
          <td>{{ item.variants.plain ? '已收录' : '未收录' }}</td>
          <td>{{ item.variants.box ? '已收录' : '未收录' }}</td>
          <td>{{ activeLabel(item.active) }}</td><td>{{ item.objectCount }}</td>
        </tr></tbody>
      </table></div>
    </details>
  </section>
</template>

<style scoped>
.room-preview { margin: 24px 0; }
.quick-progress { border: 1px solid var(--vp-c-divider); border-radius: 10px; padding: 16px; margin: 20px 0 28px; }
.progress-heading { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
.progress-heading h2 { margin: 0; }
.progress-total { font-size: 13px; color: var(--vp-c-text-2); white-space: nowrap; }
.progress-cards { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; margin: 16px 0; }
.progress-cards div { background: var(--vp-c-bg-soft); border-radius: 7px; padding: 10px; }
.progress-cards strong, .progress-cards span { display: block; }
.progress-cards strong { font-size: 20px; }
.progress-cards span { color: var(--vp-c-text-2); font-size: 12px; line-height: 1.4; }
.progress-table-wrap { overflow: auto; max-height: 560px; }
.progress-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.progress-table th, .progress-table td { padding: 7px 8px; border-bottom: 1px solid var(--vp-c-divider); text-align: left; white-space: nowrap; }
.status-pill { display: inline-block; border-radius: 999px; padding: 2px 7px; font-size: 12px; }
.status-pill.box { background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1); }
.status-pill.plain { background: var(--vp-c-bg-soft); color: var(--vp-c-text-2); }
.status-pill.done { color: var(--vp-c-green-1); background: var(--vp-c-green-soft); }
.status-pill.pending { color: var(--vp-c-warning-1); background: var(--vp-c-warning-soft); }

.snapshot, .metadata { color: var(--vp-c-text-2); font-size: 13px; line-height: 1.6; }
.room-picker, .controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
select { border: 1px solid var(--vp-c-divider); border-radius: 6px; padding: 6px 10px; background: var(--vp-c-bg); color: var(--vp-c-text-1); max-width: 100%; }
small { font-size: 14px; color: var(--vp-c-text-2); }
.comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin: 20px 0; }
figure { margin: 0; border: 1px solid var(--vp-c-divider); padding: 12px; border-radius: 8px; min-width: 0; }
figcaption { font-weight: 600; margin-bottom: 12px; }
.badge { color: var(--vp-c-brand-1); font-size: 12px; display: inline-block; margin-left: 6px; }
img { width: 100%; height: auto; max-height: 480px; object-fit: contain; background: #000; image-rendering: pixelated; }
.source-path { display: block; overflow-wrap: anywhere; font-size: 11px; }
.missing { min-height: 200px; display: grid; place-content: center; color: var(--vp-c-text-2); }
.notice { padding: 10px 16px; border-left: 3px solid var(--vp-c-warning-1); background: var(--vp-c-warning-soft); }
.controls { font-size: 13px; margin-bottom: 10px; }
.controls input { margin-right: 5px; }
.canvas-scroll { max-height: 560px; overflow: auto; background: #000; }
canvas { display: block; max-width: none; height: auto; image-rendering: pixelated; }
details { margin: 20px 0; }
summary { cursor: pointer; font-weight: 600; }
.table-scroll { overflow: auto; }
td button { text-align: left; color: var(--vp-c-brand-1); text-decoration: underline; }
@media (max-width: 800px) { .comparison { grid-template-columns: 1fr; } .progress-cards { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
