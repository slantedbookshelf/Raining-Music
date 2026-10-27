<template>
  <div class="splash-screen">
    <div class="flex flex-col items-center">
      <img src="/logo.svg" alt="logo" class="splash-logo w-16 h-16" />
      <h1 class="splash-title font-serif-display">雨声音乐</h1>
      <p class="splash-tagline">RAINING MUSIC</p>
      <!-- 一滴水落下荡开的涟漪 -->
      <div class="splash-ripple" aria-hidden="true">
        <span class="ripple-ring"></span>
        <span class="ripple-ring ripple-ring-2"></span>
        <span class="ripple-drop"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 全屏开场页：Logo + 标题渐显上浮，1.1s 时整体淡出 */
.splash-screen {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f4fbf8;
  pointer-events: none;
  animation: splash-out 0.5s cubic-bezier(0.22, 0.61, 0.36, 1) 1.6s forwards;
}

.splash-logo {
  animation: splash-rise 0.6s cubic-bezier(0.22, 0.61, 0.36, 1) 0.1s both;
}

.splash-title {
  margin-top: 20px;
  font-size: 44px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #15281f;
  animation: splash-rise 0.6s cubic-bezier(0.22, 0.61, 0.36, 1) 0.3s both;
}

.splash-tagline {
  margin-top: 12px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.35em;
  color: var(--primary);
  animation: splash-rise 0.6s cubic-bezier(0.22, 0.61, 0.36, 1) 0.5s both;
}

/* 水滴落下 + 涟漪扩散 */
.splash-ripple {
  position: relative;
  margin-top: 28px;
  width: 60px;
  height: 60px;
}

.ripple-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 8px;
  height: 8px;
  margin: -4px 0 0 -4px;
  border: 1.5px solid rgba(16, 185, 129, 0.5);
  border-radius: 50%;
  animation: ripple-expand 1.4s cubic-bezier(0, 0, 0.2, 1) 0.7s infinite;
}

.ripple-ring-2 {
  animation-delay: 1.05s;
}

.ripple-drop {
  position: absolute;
  left: 50%;
  top: 0;
  width: 6px;
  height: 8px;
  margin-left: -3px;
  border-radius: 50%;
  background: linear-gradient(to bottom, #6ee7b7, #10b981);
  animation: drop-fall 1.4s cubic-bezier(0.22, 0.61, 0.36, 1) infinite;
}

@keyframes ripple-expand {
  0% {
    transform: scale(1);
    opacity: 0.7;
  }
  100% {
    transform: scale(6);
    opacity: 0;
  }
}

@keyframes drop-fall {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  30% {
    opacity: 1;
  }
  80% {
    transform: translateY(26px) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(26px) scale(0.3);
    opacity: 0;
  }
}

@keyframes splash-rise {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes splash-out {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
    visibility: hidden;
  }
}

@media (prefers-reduced-motion: reduce) {
  .splash-screen,
  .splash-logo,
  .splash-title,
  .splash-tagline {
    animation-duration: 0.01s;
    animation-delay: 0s;
  }
  .splash-ripple {
    display: none;
  }
}
</style>
