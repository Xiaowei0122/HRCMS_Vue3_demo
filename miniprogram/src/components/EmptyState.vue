<!--  空状态组件 — 使用 SVG 图标  -->
<template>
  <view class="empty-state">
    <view class="empty-icon-wrapper">
      <SvgIcon :name="iconName" :size="40" color="#94A3B8" />
    </view>
    <text class="empty-title">{{ text }}</text>
    <text class="empty-sub" v-if="subText">{{ subText }}</text>
  </view>
</template>

<script setup>
import SvgIcon from './SvgIcon.vue'

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

import { computed } from 'vue'
const iconName = computed(() => iconMap[props.icon] || props.icon || 'tray')
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  animation: fade-in-up 0.5s ease;
}

.empty-icon-wrapper {
  width: 88px; height: 88px;
  border-radius: 50%;
  background: #F1F5F9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.empty-title {
  font-size: 14px;
  color: #64748B;
  display: block;
}

.empty-sub {
  font-size: 12px;
  color: #94A3B8;
  margin-top: 4px;
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
