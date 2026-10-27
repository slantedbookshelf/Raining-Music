<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { formatTime } from '@/utils'
import { UserStore } from '@/stores/modules/user'
import { AudioStore } from '@/stores/modules/audio'
import { collectSong, cancelCollectSong } from '@/api/system'
import { ElMessage } from 'element-plus'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useLibraryStore } from '@/stores/modules/library'
import { useArtistStore } from '@/stores/modules/artist'
import { usePlaylistStore } from '@/stores/modules/playlist'

const userStore = UserStore()
const audioStore = AudioStore()
const route = useRoute()
const libraryStore = useLibraryStore()

const {
  isPlaying,
  currentTime,
  duration,
  nextTrack,
  prevTrack,
  togglePlayPause,
  seek,
} = useAudioPlayer()

// 获取当前播放歌曲的喜欢状态
const currentSongLikeStatus = computed(() => {
  const currentTrack = audioStore.trackList[audioStore.currentSongIndex]
  return currentTrack?.likeStatus || 0
})

// 更新所有相同歌曲的喜欢状态
const updateAllSongLikeStatus = (songId: number, status: number) => {
  // 更新播放列表中的状态
  audioStore.trackList.forEach((track) => {
    if (Number(track.id) === songId) {
      track.likeStatus = status
    }
  })

  // 更新当前页面的歌曲列表状态
  if (audioStore.currentPageSongs) {
    audioStore.currentPageSongs.forEach((song) => {
      if (song.songId === songId) {
        song.likeStatus = status
      }
    })
  }

  // 更新曲库页面的数据
  if (route.path === '/library' && libraryStore.tableData?.items) {
    const song = libraryStore.tableData.items.find(
      (song) => song.songId === songId
    )
    if (song) {
      song.likeStatus = status
    }
  }

  // 更新歌手详情页的数据
  if (route.path.startsWith('/artist/')) {
    const artistStore = useArtistStore()
    if (artistStore.artistInfo?.songs) {
      const song = artistStore.artistInfo.songs.find(
        (song) => song.songId === songId
      )
      if (song) {
        song.likeStatus = status
      }
    }
  }

  // 更新歌单详情页的数据
  if (route.path.startsWith('/playlist/')) {
    const playlistStore = usePlaylistStore()
    if (playlistStore.songs) {
      const song = playlistStore.songs.find((song) => song.songId === songId)
      if (song) {
        song.likeStatus = status
      }
    }
  }
}

// 爱心雨滴特效
const likeBurst = ref(false)
const likeBurstId = ref(0)

const triggerLikeBurst = () => {
  likeBurstId.value++
  likeBurst.value = true
  setTimeout(() => {
    likeBurst.value = false
  }, 700)
}

// 处理喜欢/取消喜欢
const handleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  const currentTrack = audioStore.trackList[audioStore.currentSongIndex]
  if (!currentTrack) return

  try {
    const songId = Number(currentTrack.id)
    if (currentSongLikeStatus.value === 0) {
      // 收藏歌曲
      const res = await collectSong(songId)
      if (res.code === 0) {
        updateAllSongLikeStatus(songId, 1)
        triggerLikeBurst()
        ElMessage.success('已添加到我的喜欢')
      } else {
        ElMessage.error(res.message || '添加到我的喜欢失败')
      }
    } else {
      // 取消收藏
      const res = await cancelCollectSong(songId)
      if (res.code === 0) {
        updateAllSongLikeStatus(songId, 0)
        ElMessage.success('已取消喜欢')
      } else {
        ElMessage.error(res.message || '取消喜欢失败')
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 水珠粒子位置（相对爱心按钮散开）
const droplets = [
  { x: -8, y: -10, d: '0s' },
  { x: 6, y: -16, d: '0.08s' },
  { x: -2, y: -22, d: '0.16s' },
  { x: 12, y: -6, d: '0.05s' },
  { x: -14, y: -14, d: '0.12s' },
  { x: 4, y: -4, d: '0.2s' },
]
</script>

<template>
  <div class="flex items-center flex-1">
    <div class="flex items-center mr-2">
      <button
        @click="prevTrack"
        class="p-2 rounded-full hover:bg-hoverMenuBg hover:text-primary transition-all duration-200 hover:scale-110 active:scale-95"
      >
        <icon-solar:skip-previous-bold class="text-lg" />
      </button>
      <button
        @click="togglePlayPause"
        class="p-1.5 rounded-full transition-all duration-200 ease-spring hover:scale-110 active:scale-95 relative group/play"
      >
        <!-- 播放/暂停时的水波纹 -->
        <span
          v-if="isPlaying"
          class="absolute inset-0 rounded-full border-2 border-primary/40 animate-ping-slow pointer-events-none"
        ></span>
        <Icon
          :icon="
            isPlaying ? 'ic:round-pause-circle' : 'material-symbols:play-circle'
          "
          class="text-5xl drop-shadow-sm relative z-10"
          :color="'var(--primary)'"
        />
      </button>
      <button
        @click="nextTrack"
        class="p-2 rounded-full hover:bg-hoverMenuBg hover:text-primary transition-all duration-200 hover:scale-110 active:scale-95"
      >
        <icon-solar:skip-previous-bold class="transform scale-x-[-1] text-lg" />
      </button>
      <button
        class="p-2 rounded-full hover:bg-hoverMenuBg transition-all duration-200 hover:scale-110 active:scale-95 relative"
        @click="handleLike"
      >
        <icon-mdi:cards-heart-outline
          v-if="currentSongLikeStatus === 0"
          class="text-lg"
        />
        <icon-mdi:cards-heart v-else class="text-lg text-primary" />
        <!-- 爱心雨滴特效 -->
        <span
          v-for="(d, i) in droplets"
          v-show="likeBurst"
          :key="`${likeBurstId}-${i}`"
          class="like-drop"
          :style="{
            '--dx': d.x + 'px',
            '--dy': d.y + 'px',
            animationDelay: d.d,
          }"
        ></span>
      </button>
    </div>
    <div class="w-full flex items-center space-x-2">
      <el-slider
        v-model="currentTime"
        :step="1"
        :show-tooltip="false"
        @change="seek"
        :max="duration"
        class="w-full"
        size="small"
      />
      <span class="text-xs text-muted-foreground tabular-nums">{{
        formatTime(currentTime)
      }}</span>
      <span class="text-muted-foreground"> / </span>
      <span class="text-xs text-muted-foreground tabular-nums">{{
        formatTime(duration)
      }}</span>
    </div>
  </div>
</template>

<style scoped>
/* 爱心雨滴：向上迸溅的小水珠 */
.like-drop {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 5px;
  height: 5px;
  margin: -2.5px 0 0 -2.5px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #eafff6, #34d399);
  box-shadow: 0 0 3px rgba(52, 211, 153, 0.6);
  pointer-events: none;
  animation: like-drop 0.65s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

@keyframes like-drop {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(var(--dx), var(--dy)) scale(0.1);
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .like-drop {
    animation: none;
    display: none;
  }
}
</style>
