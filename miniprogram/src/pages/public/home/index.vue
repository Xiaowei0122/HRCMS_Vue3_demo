<!--
  登录后主页 — 功能入口九宫格 + 自定义 TabBar
  根据用户角色动态显示不同板块
-->
<template>
  <view class="home-page">
    <!-- 顶部用户信息 -->
    <view class="home-header">
      <view class="header-bg"></view>
      <view class="header-content">
        <view class="user-avatar">
          <text class="avatar-text">{{ authStore.userName.charAt(0) }}</text>
        </view>
        <view class="user-info">
          <text class="user-name">{{ authStore.userName }}</text>
          <text class="user-role">{{ roleLabel }}</text>
        </view>
        <view class="header-actions">
          <text class="action-btn" @click="handleLogout">退出</text>
        </view>
      </view>
    </view>

    <!-- 统计卡片 -->
    <view class="stats-row">
      <view class="stat-card" @click="goMyRepairs">
        <text class="stat-num">{{ stats.myRepairCount }}</text>
        <text class="stat-label">我的报修</text>
      </view>
      <view class="stat-card" @click="goMyRepairs">
        <text class="stat-num processing">{{ stats.processingCount }}</text>
        <text class="stat-label">处理中</text>
      </view>
      <view class="stat-card">
        <text class="stat-num done">{{ stats.doneCount }}</text>
        <text class="stat-label">已完成</text>
      </view>
    </view>

    <!-- 功能入口九宫格 -->
    <view class="feature-grid">
      <!-- 一键报修 — 所有用户可见 -->
      <view class="feature-item" @click="goPage('/pages/repair-apply/index')">
        <view class="feature-icon icon-repair">🔧</view>
        <text class="feature-name">一键报修</text>
        <text class="feature-desc">快速提交报修工单</text>
      </view>

      <!-- 我的报修 / 我的工单 -->
      <view
        class="feature-item"
        @click="goPage(authStore.isEngineer ? '/pages/engineer/my-orders/index' : '/pages/my-repairs/index')"
      >
        <view class="feature-icon icon-list">📋</view>
        <text class="feature-name">{{ authStore.isEngineer ? '我的工单' : '我的报修' }}</text>
        <text class="feature-desc">查看工单处理进度</text>
      </view>

      <!-- 所有工单 — 仅工程师 -->
      <view v-if="authStore.isEngineer" class="feature-item" @click="goPage('/pages/engineer/all-orders/index')">
        <view class="feature-icon icon-all">📦</view>
        <text class="feature-name">所有工单</text>
        <text class="feature-desc">待接单工单池</text>
      </view>

      <!-- 工程师期排 — 仅特定用户 -->
      <view v-if="authStore.isSpecialUser" class="feature-item" @click="goPage('/pages/schedule/index')">
        <view class="feature-icon icon-calendar">📅</view>
        <text class="feature-name">工程师期排</text>
        <text class="feature-desc">查看排期与空闲时间</text>
      </view>

      <!-- 投诉建议 — 所有用户 -->
      <view class="feature-item" @click="goPage('/pages/complaint/index')">
        <view class="feature-icon icon-feedback">✉️</view>
        <text class="feature-name">投诉建议</text>
        <text class="feature-desc">一键投诉 · 我的投诉</text>
      </view>

      <!-- 联系我们 — 所有用户 -->
      <view class="feature-item" @click="goPage('/pages/contact/index')">
        <view class="feature-icon icon-contact">📞</view>
        <text class="feature-name">联系我们</text>
        <text class="feature-desc">工程师信息 · 地图导航</text>
      </view>
    </view>

    <!-- 自定义 TabBar -->
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRepairStore } from '@/stores/repair'
import CustomTabBar from '@/components/CustomTabBar.vue'

const authStore = useAuthStore()
const repairStore = useRepairStore()

const stats = ref({
  myRepairCount: 0,
  processingCount: 0,
  doneCount: 0
})

const roleLabel = computed(() => {
  const map = { normal: '普通用户', special: '内部员工', engineer: '工程师', admin: '管理员' }
  return map[authStore.userType] || '用户'
})

const goPage = (url) => {
  // TabBar 页面使用 switchTab
  const tabPages = ['/pages/repair-apply/index', '/pages/my-repairs/index',
                    '/pages/complaint/index', '/pages/contact/index',
                    '/pages/schedule/index', '/pages/engineer/all-orders/index',
                    '/pages/engineer/my-orders/index']
  if (tabPages.includes(url)) {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}

const goMyRepairs = () => {
  if (authStore.isEngineer) {
    uni.switchTab({ url: '/pages/engineer/my-orders/index' })
  } else {
    uni.switchTab({ url: '/pages/my-repairs/index' })
  }
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) authStore.logout()
    }
  })
}

const loadStats = async () => {
  try {
    const data = await repairStore.fetchStats()
    if (data) {
      stats.value = {
        myRepairCount: data.total || 0,
        processingCount: data.processing || 0,
        doneCount: data.done || 0
      }
    }
  } catch {
    // 忽略统计数据加载失败
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 140rpx;
}

/* 头部 */
.home-header {
  position: relative;
  padding-top: calc(env(safe-area-inset-top));
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 260rpx;
  background: linear-gradient(135deg, #D32223 0%, #B81C1D 100%);
  border-radius: 0 0 40rpx 40rpx;
}

.header-content {
  position: relative;
  display: flex;
  align-items: center;
  padding: 40rpx 32rpx 24rpx;
}

.user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.avatar-text {
  font-size: 36rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #FFFFFF;
  display: block;
}

.user-role {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4rpx;
}

.header-actions {
  display: flex;
}

.action-btn {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  padding: 8rpx 20rpx;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 30rpx;
}

/* 统计卡片 */
.stats-row {
  display: flex;
  margin: -20rpx 24rpx 20rpx;
  position: relative;
  z-index: 1;
}

.stat-card {
  flex: 1;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx 16rpx;
  margin: 0 8rpx;
  text-align: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);

  &:first-child { margin-left: 0; }
  &:last-child { margin-right: 0; }
}

.stat-num {
  font-size: 44rpx;
  font-weight: 800;
  color: #222;
  display: block;

  &.processing { color: #FF9800; }
  &.done { color: #4CAF50; }
}

.stat-label {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
}

/* 功能九宫格 */
.feature-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 0 24rpx;
}

.feature-item {
  width: calc(50% - 16rpx);
  margin: 8rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 32rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.96);
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
  }
}

.feature-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-bottom: 12rpx;

  &.icon-repair    { background: #FFF0F0; }
  &.icon-list      { background: #F0F4FF; }
  &.icon-all       { background: #FFF8F0; }
  &.icon-calendar  { background: #F0FFF4; }
  &.icon-feedback  { background: #FFF8F0; }
  &.icon-contact   { background: #F0F8FF; }
}

.feature-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #222;
  margin-bottom: 4rpx;
}

.feature-desc {
  font-size: 22rpx;
  color: #999;
}
</style>
