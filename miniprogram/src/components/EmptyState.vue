<!--
  空状态组件 — 列表为空时的占位展示
-->
<template>
  <view class="empty-state">
    <view class="empty-icon-wrapper">
      <text class="empty-icon">{{ icon }}</text>
    </view>
    <text class="empty-title">{{ text }}</text>
    <text class="empty-sub" v-if="subText">{{ subText }}</text>
  </view>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  text: { type: String, default: '暂无数据' },
  subText: { type: String, default: '' }
})
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 40rpx;
  animation: fadeInUp 0.5s ease;
}

.empty-icon-wrapper {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: #F0F0F0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.empty-icon {
  font-size: 56rpx;
}

.empty-title {
  font-size: 28rpx;
  color: #999;
  display: block;
}

.empty-sub {
  font-size: 24rpx;
  color: #ccc;
  margin-top: 8rpx;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(40rpx); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
