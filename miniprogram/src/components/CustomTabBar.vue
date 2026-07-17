<!--
  自定义 TabBar 组件
  根据用户角色动态显示底部导航项
  使用 uni.hideTabBar / uni.showTabBar 配合自定义 tabBar
-->
<template>
  <view class="custom-tabbar safe-area-bottom">
    <view
      v-for="item in tabList"
      :key="item.path"
      class="tabbar-item"
      :class="{ active: currentPath === item.path }"
      @click="switchTab(item)"
    >
      <text class="tabbar-icon">{{ item.icon }}</text>
      <text class="tabbar-text">{{ item.text }}</text>
      <view v-if="item.badge" class="tabbar-badge">{{ item.badge }}</view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const currentPath = ref(route.path)

// 根据角色生成不同的 tabBar 配置
const tabList = computed(() => {
  if (authStore.isEngineer) {
    return [
      { path: '/pages/engineer/all-orders/index', icon: '📦', text: '所有工单' },
      { path: '/pages/engineer/my-orders/index',  icon: '📋', text: '我的工单' },
      { path: '/pages/complaint/index',            icon: '✉️', text: '投诉建议' },
      { path: '/pages/contact/index',              icon: '📞', text: '联系我们' }
    ]
  }

  // normal 和 special 用户基础 tabBar
  const tabs = [
    { path: '/pages/repair-apply/index', icon: '🔧',  text: '一键报修' },
    { path: '/pages/my-repairs/index',    icon: '📋',  text: '我的报修' }
  ]

  // 内部员工：显示"工程师期排"
  if (authStore.isSpecialUser) {
    tabs.push({ path: '/pages/schedule/index', icon: '📅', text: '工程师期排' })
  }

  tabs.push(
    { path: '/pages/complaint/index', icon: '✉️', text: '投诉建议' },
    { path: '/pages/contact/index',   icon: '📞', text: '联系我们' }
  )

  return tabs
})

const switchTab = (item) => {
  if (currentPath.value === item.path) return
  router.push(item.path)
}

// 监听路由变化，更新当前路径
watch(() => route.path, (p) => {
  currentPath.value = p
})
</script>

<style lang="scss" scoped>
.custom-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: #FFFFFF;
  border-top: 1px solid #F0F0F0;
  box-shadow: 0 -2rpx 16rpx rgba(0, 0, 0, 0.04);
  z-index: 999;
  height: 100rpx;
  padding-bottom: env(safe-area-inset-bottom);
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.25s ease;

  &.active {
    .tabbar-text { color: #D32223; font-weight: 600; }
    .tabbar-icon { transform: scale(1.15); }
  }
}

.tabbar-icon {
  font-size: 36rpx;
  transition: transform 0.25s ease;
  margin-bottom: 2rpx;
}

.tabbar-text {
  font-size: 20rpx;
  color: #999;
  transition: color 0.25s;
}

.tabbar-badge {
  position: absolute;
  top: 4rpx;
  right: 50%;
  transform: translateX(200%);
  min-width: 30rpx;
  height: 30rpx;
  line-height: 30rpx;
  background: #F44336;
  color: #FFFFFF;
  font-size: 18rpx;
  border-radius: 50%;
  text-align: center;
  padding: 0 6rpx;
}
</style>
