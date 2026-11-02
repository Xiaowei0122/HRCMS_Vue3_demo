<!--
  页面导航栏 — 二级页统一使用
  - 默认：蓝色渐变底 + 返回键 + 居中标题（作为页面顶部，flex 布局 flex-shrink:0）
  - transparent：透明浮层，压在页面顶部的渐变 hero 之上（工单详情 / 联系我们）
-->
<template>
  <view class="pnav" :class="{ 'pnav--transparent': transparent }">
    <view v-if="back" class="pnav-back" @click="goBack">
      <SvgIcon name="caretLeft" :size="22" color="#fff" />
    </view>
    <text class="pnav-title" :class="{ 'is-hidden': scrolled }">{{ title }}</text>
    <view v-if="$slots.right" class="pnav-right">
      <slot name="right" />
    </view>
  </view>
</template>

<script setup>
import SvgIcon from './SvgIcon.vue'

const props = defineProps({
  title: { type: String, default: '' },
  back: { type: Boolean, default: true },
  transparent: { type: Boolean, default: false },
  // 返回时直接跳到指定页面（reLaunch），用于「排期→详情→返回主页」等跨级返回
  backUrl: { type: String, default: '' },
  // 内容上滑时隐藏标题（返回键保留）
  scrolled: { type: Boolean, default: false }
})

const goBack = () => {
  if (props.backUrl) {
    uni.reLaunch({ url: props.backUrl })
  } else {
    uni.navigateBack()
  }
}
</script>

<style lang="scss" scoped>
.pnav {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: calc(env(safe-area-inset-top) + 24rpx) 0;
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);

  /* 透明浮层：压在页面顶部 hero 之上，不占文档流 */
  &.pnav--transparent {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    z-index: 10;
    background: transparent;
  }
}

.pnav-title {
  color: #fff;
  font-size: 34rpx;
  font-weight: 600;
  letter-spacing: 1rpx;
  transition: opacity 0.25s ease, transform 0.25s ease;

  &.is-hidden {
    opacity: 0;
    transform: translateY(-8rpx);
    pointer-events: none;
  }
}

.pnav-back {
  position: absolute;
  left: 24rpx;
  bottom: 20rpx;
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  border: 1rpx solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);

  &:active { opacity: 0.7; }
}

.pnav-right {
  position: absolute;
  right: 24rpx;
  bottom: 20rpx;
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  border: 1rpx solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);

  &:active { opacity: 0.7; }
}
</style>
