<script setup lang="ts">
import Header from './components/header/index.vue'
import Aside from './components/aside/index.vue'
import Main from './components/main/index.vue'
import Footer from './components/footer/index.vue'
// import BG from './components/bg/index.vue'
import AgentChat from '@/components/Agent/AgentChat.vue'
import RainLayer from '@/components/RainLayer.vue'
import { AudioPlayer } from '@/hooks/useAudioPlayer'

const audioPlayer = AudioPlayer()
provide('audioPlayer', audioPlayer)

// 播放状态（ref），用于驱动「播放时下雨、暂停时雨停」
const { isPlaying } = audioPlayer
</script>
<template>
  <!-- <BG /> -->
  <SplashScreen />
  <div class="absolute w-full flex flex-col h-full">
    <div class="w-full flex flex-col h-full overflow-hidden bg-background">
      <Header />
      <div class="flex flex-1 overflow-hidden">
        <Aside />
        <Main />
      </div>
      <Footer />
    </div>
    <!-- 全局克制的氛围雨：播放时下雨、暂停时雨停 -->
    <RainLayer
      :active="isPlaying"
      faint
      :count="30"
      class="fixed inset-0 z-[5] pointer-events-none"
    />
    <!-- 全局悬浮的雨声助手聊天窗 -->
    <AgentChat />
  </div>
</template>
