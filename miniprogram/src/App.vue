<template>
  <router-view v-slot="{ Component }">
    <transition name="route" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup>
// 纯 Vue 3 SPA — uni polyfill 在 main.js 中加载
</script>

<style lang="scss">
/* 全局样式 */
@import './uni.scss';

/* ── uni-app 自定义元素 → 浏览器标准行为 ── */
view, uni-view       { display: block; }
text, uni-text       { display: inline; white-space: normal; }
image, uni-image     { display: inline-block; max-width: 100%; }
scroll-view          { display: block; overflow-y: auto; -webkit-overflow-scrolling: touch; }
swiper, uni-swiper   { display: block; overflow: hidden; }
swiper-item          { display: block; }
navigator            { display: block; cursor: pointer; }

/* ── 原生标签重置 ── */
input, textarea, select {
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  border: none;
  outline: none;
  background: transparent;
}

button {
  padding: 0;
  margin: 0;
  border: none;
  background: transparent;
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  cursor: pointer;
  transition: opacity 0.15s ease;

  &::after { display: none; }
  &:active { opacity: 0.8; }
}

/* ── Toast polyfill ── */
.uni-toast-polyfill {
  position: fixed;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(15, 23, 42, 0.88);
  color: #fff;
  font-size: 14px;
  padding: 10px 24px;
  border-radius: 20px;
  z-index: 99999;
  pointer-events: none;
  transition: opacity 0.3s;
  white-space: nowrap;
  backdrop-filter: blur(8px);
}
.uni-toast--fadeout { opacity: 0; }

/* ── 页面切换过渡（覆盖所有页面）── */
.route-enter-active,
.route-leave-active {
  transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.22, 1, 0.36, 1);
}
.route-enter-from {
  opacity: 0;
  transform: translateY(14px);
}
.route-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── 通用可点击块按压反馈（供各页面复用）── */
.tappable {
  transition: transform 0.15s ease, opacity 0.15s ease;
  &:active { transform: scale(0.97); opacity: 0.85; }
}
</style>
