<!--  空状态组件 — 使用 SVG 图标（蓝色主题 / rpx）  -->
<template>
  <view class="empty-state">
    <view class="empty-icon-wrapper">
      <SvgIcon :name="iconName" :size="40" color="#165DFF" />
    </view>
    <text class="empty-title">{{ text }}</text>
    <text class="empty-sub" v-if="subText">{{ subText }}</text>
  </view>
</template>

<script setup>
import SvgIcon from './SvgIcon.vue'
import { computed } from 'vue'

const props = defineProps({
  icon: { type: String, default: 'tray' },
  text: { type: String, default: '暂无数据' },
  subText: { type: String, default: '' }
})

// Map old emoji → SVG icon name
const iconMap = {
  '📋': 'clipboard', '📦': 'package', '✉️': 'envelope',
  '📭': 'tray', '🔧': 'wrench', '📞': 'phone'
}

const iconName = computed(() => iconMap[props.icon] || props.icon || 'tray')
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 20rpx;
  animation: fade-in-up 0.5s ease;
}

.empty-icon-wrapper {
  width: 140rpx; height: 140rpx;
  border-radius: 50%;
  background: #E8F3FF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.empty-title {
  font-size: 28rpx;
  color: #4E5969;
  display: block;
}

.empty-sub {
  font-size: 24rpx;
  color: #86909C;
  margin-top: 8rpx;
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(20rpx); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
