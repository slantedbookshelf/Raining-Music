<script setup lang="ts">
import Left from './components/left.vue'
import Center from './components/center.vue'
import Right from './components/right.vue'
import GrassField from '@/components/GrassField.vue'
import RainLayer from '@/components/RainLayer.vue'

// 播放状态：用于控制「播放时下雨、暂停时雨停」
const { isPlaying } = useAudioPlayer()
</script>
<template>
  <footer
    class="player-bar m-3 mt-0 rounded-2xl bg-white border border-border shadow-player flex items-center justify-between relative z-10 overflow-hidden"
  >
    <!-- 草地材质（底部） -->
    <GrassField />
    <!-- 播放时落下的雨丝 -->
    <RainLayer :active="isPlaying" :count="18" class="z-[1]" />

    <!-- 内容层，浮在草地之上 -->
    <div class="relative z-10 flex items-center justify-between w-full">
      <!-- 左边：歌曲封面和歌曲名称 -->
      <Left />
      <!-- 中间：控制区 -->
      <Center />
      <!-- 右边：历史播放和音量 -->
      <Right />
    </div>
  </footer>
</template>

<style scoped>
.player-bar {
  background: linear-gradient(
    180deg,
    #ffffff 0%,
    #f3fbf7 55%,
    #eaf7f1 100%
  );
}
</style>
