<script setup lang="ts">
/**
 * GrassField —— 底部播放条的「草地」材质层
 * 两层草叶剪影叠出景深，随微风极缓慢摆动。
 * 纯装饰，pointer-events: none。
 */
</script>

<template>
  <div class="grass-field" aria-hidden="true">
    <!-- 雨后湿润的水面反光渐变 -->
    <div class="grass-wet"></div>

    <!-- 远景草（浅，摆动慢） -->
    <svg
      class="grass grass-back"
      viewBox="0 0 1200 60"
      preserveAspectRatio="none"
    >
      <g fill="none">
        <path
          d="M0,60 L0,40 Q20,20 40,42 Q55,24 70,44 Q90,18 110,46 Q130,26 150,44 Q170,20 190,45 Q215,22 240,46 Q265,18 290,44 Q315,24 340,45 Q360,20 380,46 Q405,24 430,44 Q455,18 480,45 Q505,24 530,44 Q555,20 580,45 Q600,22 620,46 Q645,20 670,44 Q695,24 720,45 Q740,18 760,46 Q785,22 810,44 Q835,20 860,45 Q880,24 900,46 Q925,20 950,44 Q975,22 1000,45 Q1025,20 1050,44 Q1070,22 1090,46 Q1115,24 1140,44 Q1160,20 1180,45 Q1190,28 1200,40 L1200,60 Z"
          stroke="#9fd8bf"
          stroke-width="2"
          stroke-linecap="round"
        />
      </g>
    </svg>

    <!-- 近景草（深，摆动略快） -->
    <svg
      class="grass grass-front"
      viewBox="0 0 1200 60"
      preserveAspectRatio="none"
    >
      <g fill="none">
        <path
          d="M0,60 L0,48 Q15,32 30,50 Q45,34 60,52 Q80,30 100,52 Q120,36 140,52 Q160,28 180,50 Q200,34 220,52 Q240,30 260,50 Q280,32 300,52 Q320,28 340,50 Q360,34 380,52 Q400,30 420,50 Q440,32 460,52 Q480,28 500,50 Q520,34 540,52 Q560,30 580,50 Q600,32 620,52 Q640,28 660,50 Q680,34 700,52 Q720,30 740,50 Q760,32 780,52 Q800,28 820,50 Q840,34 860,52 Q880,30 900,50 Q920,32 940,52 Q960,28 980,50 Q1000,34 1020,52 Q1040,30 1060,50 Q1080,32 1100,52 Q1120,28 1140,50 Q1160,34 1180,52 Q1190,30 1200,48 L1200,60 Z"
          stroke="#34a87f"
          stroke-width="2.5"
          stroke-linecap="round"
        />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.grass-field {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 34px;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.grass-wet {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(16, 185, 129, 0.14) 0%,
    rgba(16, 185, 129, 0.04) 60%,
    transparent 100%
  );
}

.grass {
  position: absolute;
  left: 0;
  bottom: -4px;
  width: 100%;
  height: 34px;
  transform-origin: bottom center;
}

.grass-back {
  animation: grass-sway 7s ease-in-out infinite;
}

.grass-front {
  animation: grass-sway 5s ease-in-out infinite reverse;
}

@keyframes grass-sway {
  0%,
  100% {
    transform: skewX(0deg) scaleY(1);
  }
  50% {
    transform: skewX(1.5deg) scaleY(1.03);
  }
}

@media (prefers-reduced-motion: reduce) {
  .grass-back,
  .grass-front {
    animation: none;
  }
}
</style>
