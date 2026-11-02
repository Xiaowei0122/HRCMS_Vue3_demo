<!--  自定义 TabBar — 2 栏（首页 + 我的）  -->
<template>
  <view class="custom-tabbar safe-area-bottom">
    <view
      v-for="item in tabList"
      :key="item.path"
      class="tabbar-item"
      :class="{ active: currentPath === item.path }"
      @click="switchTab(item.path)"
    >
      <SvgIcon :name="item.icon" :size="24" />
      <text class="tabbar-text">{{ item.text }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import SvgIcon from './SvgIcon.vue'

const router = useRouter()
const route = useRoute()
const currentPath = ref(route.path)

const tabList = [
  { path: '/pages/public/home/index', icon: 'house', text: '首页' },
  { path: '/pages/public/profile/index', icon: 'user', text: '我的' },
]

const switchTab = (path) => {
  if (currentPath.value === path) return
  router.push(path)
}

watch(() => route.path, (p) => { currentPath.value = p })
</script>

<style lang="scss" scoped>
.custom-tabbar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 128rpx;
  display: flex;
  align-items: flex-start;
  padding-top: 12rpx;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1rpx solid #E5E6EB;
  z-index: 999;
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  color: #86909C;
  transition: all 0.2s ease;

  &.active {
    color: #165DFF;
    .tabbar-text { font-weight: 600; }
  }

  &:active { transform: scale(0.92); }
}

.tabbar-text {
  font-size: 22rpx;
}
</style>
