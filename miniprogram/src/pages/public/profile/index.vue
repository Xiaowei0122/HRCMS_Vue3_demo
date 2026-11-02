<!--
  「我的」个人中心 — 登录 / 未登录两态
  已登录：用户卡片 + 统计卡 + 我的服务/常用工具菜单 + 退出登录
  未登录：登录引导卡 + 免登录功能 + 锁定菜单
-->
<template>
  <view class="profile-page">
    <!-- ============ 已登录态 ============ -->
    <template v-if="authStore.isLoggedIn">
      <view class="profile-header">
        <view class="profile-top">
          <text class="profile-top-title">个人中心</text>
          <view class="profile-setting-btn" @click="openSettings">
            <SvgIcon name="gear" :size="20" color="#fff" />
          </view>
        </view>
        <view class="profile-user-row">
          <view class="profile-avatar">{{ authStore.userName.charAt(0) }}</view>
          <view class="profile-user-info">
            <view class="profile-user-name">
              <text>{{ authStore.userName }}</text>
              <text class="profile-role-tag">{{ authStore.roleLabel }}</text>
            </view>
            <text class="profile-user-desc">{{ maskedPhone || authStore.userInfo?.username || '' }}</text>
          </view>
        </view>
      </view>

      <!-- 统计卡片 -->
      <view class="profile-stats">
        <view class="stat-item" @click="goStatus('')">
          <text class="stat-num blue">{{ stats.myRepairCount }}</text>
          <text class="stat-label">我的报修</text>
        </view>
        <view class="stat-item" @click="goStatus(STATUS.PENDING)">
          <text class="stat-num orange">{{ stats.pendingCount }}</text>
          <text class="stat-label">{{ pendingLabel }}</text>
        </view>
        <view class="stat-item" @click="goStatus(STATUS.PROCESSING)">
          <text class="stat-num blue">{{ stats.processingCount }}</text>
          <text class="stat-label">处理中</text>
        </view>
        <view class="stat-item" @click="goStatus(STATUS.CONFIRMING)">
          <text class="stat-num purple">{{ stats.confirmingCount }}</text>
          <text class="stat-label">待确认</text>
        </view>
        <view class="stat-item" @click="goStatus(STATUS.DONE)">
          <text class="stat-num green">{{ stats.doneCount }}</text>
          <text class="stat-label">已完成</text>
        </view>
      </view>

      <!-- 我的服务 -->
      <view class="menu-group">
        <view class="menu-group-title">我的服务</view>
        <view class="menu-item" @click="goMyRepairs">
          <view class="menu-icon blue"><SvgIcon name="clipboard" :size="18" color="#fff" /></view>
          <text class="menu-text">{{ authStore.isAdmin ? '工单列表' : (authStore.isEngineer ? '我的工单' : '我的报修') }}</text>
          <text v-if="stats.processingCount > 0" class="menu-badge">{{ stats.processingCount }}</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
        <view v-if="canSeeSchedule" class="menu-item" @click="goPage('/pages/schedule/index')">
          <view class="menu-icon purple"><SvgIcon name="calendar" :size="18" color="#fff" /></view>
          <text class="menu-text">工程师排期</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="goPage('/pages/complaint/index')">
          <view class="menu-icon red"><SvgIcon name="envelope" :size="18" color="#fff" /></view>
          <text class="menu-text">投诉建议</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="goPage('/pages/contact/index')">
          <view class="menu-icon green"><SvgIcon name="phone" :size="18" color="#fff" /></view>
          <text class="menu-text">联系我们</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="goPage('/pages/messages/index')">
          <view class="menu-icon blue"><SvgIcon name="envelope" :size="18" color="#fff" /></view>
          <text class="menu-text">我的私信</text>
          <text v-if="messageUnread > 0" class="menu-badge">{{ messageUnread > 99 ? '99+' : messageUnread }}</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
      </view>

      <!-- 常用工具 -->
      <view class="menu-group">
        <view class="menu-group-title">常用工具</view>
        <view class="menu-item" @click="openAddress">
          <view class="menu-icon orange"><SvgIcon name="mapPin" :size="18" color="#fff" /></view>
          <text class="menu-text">地址管理</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="openNotify">
          <view class="menu-icon cyan"><SvgIcon name="bell" :size="18" color="#fff" /></view>
          <text class="menu-text">消息通知</text>
          <text v-if="unreadCount > 0" class="menu-badge">{{ unreadCount }}</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="openAbout">
          <view class="menu-icon gray"><SvgIcon name="info" :size="18" color="#fff" /></view>
          <text class="menu-text">关于我们</text>
          <SvgIcon name="caretRight" :size="16" color="#C9CDD4" />
        </view>
      </view>

      <view class="logout-btn" @click="handleLogout">退出登录</view>
    </template>

    <!-- ============ 未登录态 ============ -->
    <template v-else>
      <view class="profile-header">
        <view class="profile-top">
          <text class="profile-top-title">个人中心</text>
          <view class="profile-setting-btn" style="opacity: 0.5;">
            <SvgIcon name="gear" :size="20" color="#fff" />
          </view>
        </view>
      </view>

      <!-- 登录引导卡 -->
      <view class="profile-guest-hero">
        <view class="profile-guest-avatar">
          <SvgIcon name="user" :size="36" color="#C9CDD4" />
        </view>
        <text class="profile-guest-title">您好，请登录</text>
        <text class="profile-guest-desc">登录后查看工单进度、专属服务与个人数据</text>
        <button class="profile-guest-login-btn" @click="goLogin">登录 / 注册</button>
      </view>

      <!-- 免登录可用功能 -->
      <view class="profile-guest-features">
        <view class="profile-guest-feature" @click="goPage('/pages/contact/index')">
          <view class="profile-guest-feature-icon green"><SvgIcon name="phone" :size="20" color="#fff" /></view>
          <text class="profile-guest-feature-label">联系我们</text>
        </view>
        <view class="profile-guest-feature" @click="openHelp">
          <view class="profile-guest-feature-icon blue"><SvgIcon name="info" :size="20" color="#fff" /></view>
          <text class="profile-guest-feature-label">帮助中心</text>
        </view>
        <view class="profile-guest-feature" @click="openAbout">
          <view class="profile-guest-feature-icon gray"><SvgIcon name="info" :size="20" color="#fff" /></view>
          <text class="profile-guest-feature-label">关于我们</text>
        </view>
      </view>

      <!-- 登录后可用（锁定） -->
      <view class="menu-group locked">
        <view class="menu-group-title">登录后可用</view>
        <view class="menu-item" @click="needLogin">
          <view class="menu-icon blue"><SvgIcon name="clipboard" :size="18" color="#fff" /></view>
          <text class="menu-text">我的报修</text>
          <SvgIcon name="lock" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="needLogin">
          <view class="menu-icon purple"><SvgIcon name="calendar" :size="18" color="#fff" /></view>
          <text class="menu-text">工程师排期</text>
          <SvgIcon name="lock" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="needLogin">
          <view class="menu-icon orange"><SvgIcon name="mapPin" :size="18" color="#fff" /></view>
          <text class="menu-text">地址管理</text>
          <SvgIcon name="lock" :size="16" color="#C9CDD4" />
        </view>
        <view class="menu-item" @click="needLogin">
          <view class="menu-icon cyan"><SvgIcon name="bell" :size="18" color="#fff" /></view>
          <text class="menu-text">消息通知</text>
          <SvgIcon name="lock" :size="16" color="#C9CDD4" />
        </view>
      </view>
    </template>

    <!-- 自定义 TabBar -->
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRepairStore } from '@/stores/repair'
import { get } from '@/utils/request'
import { STATUS } from '@/utils/repair-status'
import SvgIcon from '@/components/SvgIcon.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'

const authStore = useAuthStore()
const repairStore = useRepairStore()
const router = useRouter()

const stats = ref({
  myRepairCount: 0,
  pendingCount: 0,
  processingCount: 0,
  confirmingCount: 0,
  doneCount: 0
})

const unreadCount = ref(0)
const messageUnread = ref(0)

const maskedPhone = computed(() => {
  const p = authStore.userInfo?.phone || ''
  if (!p) return ''
  if (p.length === 11) return p.slice(0, 3) + '****' + p.slice(7)
  return p
})

// 工程师排期可见：与后端 require_permission("repair:schedule","repair:audit") 对齐
const canSeeSchedule = computed(() => authStore.hasPerm('repair:schedule', 'repair:audit'))

const goPage = (url) => router.push(url)
const goLogin = () => router.push('/pages/public/login/index')

// 非接单角色（业务/财务/运营/外部人员）不接单，统计里的「待接单」改名「待处理」
const pendingLabel = computed(() => (authStore.isEngineer || authStore.isAdmin) ? '待接单' : '待处理')

const goMyRepairs = () => goStatus('')

// 按状态跳转：工程师→我的工单，管理员→全部工单，其余→我的报修
const goStatus = (status) => {
  let url
  if (authStore.isEngineer) {
    url = '/pages/engineer/my-orders/index'
  } else if (authStore.isAdmin) {
    url = '/pages/engineer/all-orders/index'
  } else {
    url = '/pages/my-repairs/index'
  }
  if (status) url += `?status=${encodeURIComponent(status)}`
  router.push(url)
}

const needLogin = () => uni.showToast({ title: '请先登录', icon: 'none' })

// 未实现的功能占位
const openSettings = () => uni.showToast({ title: '设置功能开发中', icon: 'none' })
const openAddress = () => router.push('/pages/address/index')
const openNotify = () => router.push('/pages/notifications/index')
const openHelp = () => uni.showToast({ title: '帮助中心开发中', icon: 'none' })
const openAbout = () => uni.showToast({ title: '关于我们开发中', icon: 'none' })

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
  if (!authStore.isLoggedIn) return
  try {
    const data = await repairStore.fetchMyStats()
    if (data) {
      stats.value = {
        myRepairCount: data.total || 0,
        pendingCount: data.pending || 0,
        processingCount: data.processing || 0,
        confirmingCount: data.confirming || 0,
        doneCount: data.completed || 0
      }
    }
  } catch {
    // 忽略统计数据加载失败
  }
}

const loadUnread = async () => {
  if (!authStore.isLoggedIn) return
  try {
    const res = await get('/notifications/unread-count')
    unreadCount.value = res?.count ?? 0
  } catch {
    // 忽略未读数加载失败
  }
}

const loadMessageUnread = async () => {
  if (!authStore.isLoggedIn) return
  try {
    const res = await get('/messages/unread-count')
    messageUnread.value = res?.count ?? 0
  } catch {
    // 忽略私信未读数加载失败
  }
}

onMounted(() => {
  loadStats()
  loadUnread()
  loadMessageUnread()
})
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 140rpx;
}

/* ═══ 顶部 Header ═══ */
.profile-header {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 60%, #5B8DEF 100%);
  padding: calc(env(safe-area-inset-top) + 56rpx) 40rpx 140rpx;
}
.profile-header::before {
  content: '';
  position: absolute;
  top: -120rpx;
  right: -80rpx;
  width: 400rpx;
  height: 400rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
}
.profile-header::after {
  content: '';
  position: absolute;
  bottom: -160rpx;
  left: -60rpx;
  width: 320rpx;
  height: 320rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}
.profile-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
  margin-bottom: 40rpx;
}
.profile-top-title {
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
}
.profile-setting-btn {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-user-row {
  display: flex;
  align-items: center;
  gap: 28rpx;
  position: relative;
  z-index: 1;
}
.profile-avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 52rpx;
  font-weight: 700;
  border: 6rpx solid rgba(255, 255, 255, 0.35);
  flex-shrink: 0;
}
.profile-user-info { flex: 1; }
.profile-user-name {
  display: flex;
  align-items: center;
  gap: 16rpx;
  color: #fff;
  font-size: 40rpx;
  font-weight: 700;
  margin-bottom: 8rpx;
}
.profile-role-tag {
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
}
.profile-user-desc {
  color: rgba(255, 255, 255, 0.8);
  font-size: 26rpx;
}

/* ═══ 统计卡片 ═══ */
.profile-stats {
  margin: -100rpx 32rpx 0;
  background: #fff;
  border-radius: 32rpx;
  padding: 40rpx 0;
  display: flex;
  box-shadow: 0 16rpx 60rpx rgba(22, 93, 255, 0.12);
  position: relative;
  z-index: 2;
}
.stat-item {
  flex: 1;
  text-align: center;
  position: relative;
}
.stat-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 1rpx;
  height: 64rpx;
  background: #E5E6EB;
}
.stat-num {
  font-size: 52rpx;
  font-weight: 700;
  line-height: 1.2;
  display: block;

  &.blue   { color: #165DFF; }
  &.orange { color: #FF7D00; }
  &.green  { color: #00B42A; }
  &.purple { color: #722ED1; }
}
.stat-label {
  font-size: 24rpx;
  color: #86909C;
  margin-top: 8rpx;
}

/* ═══ 菜单分组 ═══ */
.menu-group {
  margin: 32rpx 32rpx 0;
  background: #fff;
  border-radius: 28rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}
.menu-group-title {
  padding: 28rpx 32rpx 16rpx;
  font-size: 26rpx;
  color: #86909C;
  font-weight: 500;
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 32rpx;
  gap: 24rpx;
  border-bottom: 1rpx solid #F2F3F5;
}
.menu-item:last-child { border-bottom: none; }
.menu-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.blue   { background: linear-gradient(135deg, #165DFF, #4080FF); }
  &.orange { background: linear-gradient(135deg, #FF7D00, #FF9A2E); }
  &.purple { background: linear-gradient(135deg, #722ED1, #9254DE); }
  &.red    { background: linear-gradient(135deg, #F53F3F, #F76560); }
  &.green  { background: linear-gradient(135deg, #00B42A, #23C343); }
  &.cyan   { background: linear-gradient(135deg, #14C9C9, #36CFC9); }
  &.gray   { background: linear-gradient(135deg, #86909C, #A9AEB8); }
}
.menu-text {
  flex: 1;
  font-size: 30rpx;
  color: #1D2129;
  font-weight: 500;
}
.menu-badge {
  background: #F53F3F;
  color: #fff;
  font-size: 20rpx;
  min-width: 36rpx;
  height: 36rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
  font-weight: 600;
  margin-right: 8rpx;
}

/* ═══ 退出登录 ═══ */
.logout-btn {
  margin: 48rpx 32rpx 80rpx;
  padding: 28rpx;
  background: #fff;
  border-radius: 28rpx;
  text-align: center;
  color: #F53F3F;
  font-size: 30rpx;
  font-weight: 500;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}

/* ═══ 未登录引导卡 ═══ */
.profile-guest-hero {
  margin: -100rpx 32rpx 0;
  background: #fff;
  border-radius: 32rpx;
  padding: 56rpx 40rpx;
  box-shadow: 0 16rpx 60rpx rgba(22, 93, 255, 0.12);
  position: relative;
  z-index: 2;
  text-align: center;
}
.profile-guest-avatar {
  width: 144rpx;
  height: 144rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #F2F3F5, #E5E6EB);
  border: 6rpx solid #fff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 28rpx;
}
.profile-guest-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1D2129;
  display: block;
  margin-bottom: 12rpx;
}
.profile-guest-desc {
  font-size: 26rpx;
  color: #86909C;
  display: block;
  margin-bottom: 36rpx;
}
.profile-guest-login-btn {
  display: inline-block;
  padding: 24rpx 96rpx;
  border-radius: 48rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  box-shadow: 0 8rpx 28rpx rgba(22, 93, 255, 0.35);
}

/* ═══ 免登录功能 ═══ */
.profile-guest-features {
  margin: 40rpx 32rpx 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24rpx;
}
.profile-guest-feature {
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx 16rpx;
  text-align: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
}
.profile-guest-feature-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 20rpx;
  margin: 0 auto 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  &.blue  { background: linear-gradient(135deg, #165DFF, #4080FF); }
  &.green { background: linear-gradient(135deg, #00B42A, #23C343); }
  &.gray  { background: linear-gradient(135deg, #86909C, #A9AEB8); }
}
.profile-guest-feature-label {
  font-size: 24rpx;
  color: #4E5969;
  font-weight: 500;
}

/* ═══ 锁定菜单 ═══ */
.menu-group.locked {
  opacity: 0.6;
}
</style>
