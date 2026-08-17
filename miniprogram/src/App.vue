<template>
  <router-view />
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

  &::after { display: none; }
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
</style>
