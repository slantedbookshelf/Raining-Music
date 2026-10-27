<script setup lang="ts">
import { computed, toRefs } from 'vue'

/**
 * RainLayer —— 克制的雨丝粒子层
 * 通过 `active`（默认绑定播放状态 isPlaying）控制「下雨 / 雨停」。
 * 纯展示层：pointer-events: none，绝不遮挡交互。
 * 尊重 prefers-reduced-motion：动效关闭时雨停，仅保留静态湿润感。
 */
const props = withDefaults(
  defineProps<{
    /** 是否下雨（通常绑定 isPlaying，实现「播放时下雨、暂停时雨停」） */
    active?: boolean
    /** 雨滴数量 */
    count?: number
    /** 高度（px），默认铺满父容器 */
    height?: string
    /** 雨丝是否偏淡（用于全局背景层） */
    faint?: boolean
  }>(),
  {
    active: false,
    count: 24,
    height: '100%',
    faint: false,
  }
)

const { active, faint, height } = toRefs(props)

const drops = computed(() =>
  Array.from({ length: props.count }, (_, i) => ({
    left: `${(i * 47) % 100}%`,
    delay: `${(i * 0.37) % 3}s`,
    duration: `${1.6 + ((i * 0.23) % 1.6)}s`,
    opacity: 0.25 + ((i * 0.13) % 0.4),
    scale: 0.7 + ((i * 0.17) % 0.6),
  }))
)
</script>

<template>
  <div
    class="rain-layer"
    :class="{ 'is-raining': active, 'is-faint': faint }"
    :style="{ height: height || '100%' }"
    aria-hidden="true"
  >
    <span
      v-for="(d, i) in drops"
      :key="i"
      class="rain-drop"
      :style="{
        left: d.left,
        animationDelay: d.delay,
        animationDuration: d.duration,
        opacity: d.opacity,
        transform: `scaleX(${d.scale})`,
      }"
    ></span>
  </div>
</template>

<style scoped>
.rain-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  /* 默认雨停（雨滴悬停在顶部，静止透明） */
  opacity: 0;
  transition: opacity 0.9s ease;
}

.rain-layer.is-raining {
  opacity: 1;
}

.rain-drop {
  position: absolute;
  top: -20px;
  width: 1.5px;
  height: 22px;
  border-radius: 999px;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0),
    rgba(52, 211, 153, 0.55)
  );
  /* 静止时悬停在顶部，不下落 */
  animation: rain-fall 2.2s linear infinite;
  animation-play-state: paused;
}

.rain-layer.is-raining .rain-drop {
  animation-play-state: running;
}

/* 淡色变体：用于全局背景，雨丝更隐、偏冷 */
.rain-layer.is-faint .rain-drop {
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0),
    rgba(120, 200, 175, 0.3)
  );
}

@keyframes rain-fall {
  0% {
    transform: translateY(0);
    opacity: 0;
  }
  12% {
    opacity: 1;
  }
  100% {
    transform: translateY(calc(100% + 40px));
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .rain-layer {
    opacity: 0;
  }
  .rain-drop {
    animation: none;
  }
}
</style>
