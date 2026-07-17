<template>
  <router-view />
</template>

<script setup>
// 纯 Vue 3 SPA 模式 — 不使用 uni-app 生命周期
// uni polyfill 已在 main.js 中加载，所有页面组件保持不变
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

/* Toast polyfill 样式 */
.uni-toast-polyfill {
  position: fixed;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.78);
  color: #fff;
  font-size: 14px;
  padding: 10px 24px;
  border-radius: 20px;
  z-index: 99999;
  pointer-events: none;
  transition: opacity 0.3s;
  white-space: nowrap;
}
.uni-toast--fadeout { opacity: 0; }
</style>
