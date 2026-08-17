<!--  自定义 TabBar — 按角色动态切换  -->
<template>
  <view class="custom-tabbar safe-area-bottom">
    <view
      v-for="item in tabList"
      :key="item.path"
      class="tabbar-item"
      :class="{ active: currentPath === item.path }"
      @click="switchTab(item.path)"
    >
      <SvgIcon :name="item.icon" :size="22" />
      <text class="tabbar-text">{{ item.text }}</text>
      <view v-if="item.badge" class="tabbar-badge">{{ item.badge }}</view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from './SvgIcon.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const currentPath = ref(route.path)

const isEng = computed(() => authStore.isEngineer)
const canSeeSchedule = computed(() => authStore.isInternalUser || authStore.isAdmin)

const tabList = computed(() => {
  const homeTab = { path: '/pages/public/home/index', icon: 'house', text: '首页' }

  // 工程师角色
  if (isEng.value) {
    return [
      homeTab,
      { path: '/pages/engineer/all-orders/index', icon: 'package',  text: '工单池' },
      { path: '/pages/engineer/my-orders/index',  icon: 'clipboard', text: '我的' },
      { path: '/pages/complaint/index',            icon: 'envelope', text: '投诉' },
    ]
  }

  // 普通用户 / 内部员工
  const tabs = [
    homeTab,
    { path: '/pages/repair-apply/index', icon: 'wrench',    text: '报修' },
    { path: '/pages/my-repairs/index',   icon: 'clipboard', text: '工单' },
  ]
  if (canSeeSchedule.value) {
    tabs.push({ path: '/pages/schedule/index', icon: 'calendar', text: '排期' })
  }
  tabs.push(
    { path: '/pages/complaint/index', icon: 'envelope', text: '投诉' },
  )
  return tabs
})

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
  display: flex;
  background: #FFFFFF;
  border-top: 1px solid #F1F5F9;
  z-index: 999;
  height: 100rpx;
  padding-bottom: env(safe-area-inset-bottom);
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  gap: 2rpx;
  transition: all 0.2s ease;
  color: #94A3B8;

  &.active {
    color: #0F172A;
    .tabbar-text { font-weight: 600; }
  }

  &:active {
    transform: scale(0.92);
  }
}

.tabbar-text {
  font-size: 20rpx;
}

.tabbar-badge {
  position: absolute;
  top: 6rpx;
  right: 50%;
  transform: translateX(180%);
  min-width: 28rpx; height: 28rpx;
  line-height: 28rpx;
  background: #DC2626;
  color: #fff;
  font-size: 18rpx;
  border-radius: 50%;
  text-align: center;
  padding: 0 4rpx;
  font-weight: 600;
}
</style>
