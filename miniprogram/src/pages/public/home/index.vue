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
          <text class="action-btn" @click="openChangePwd">改密</text>
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
        <view class="feature-icon icon-repair">
          <SvgIcon name="wrench" :size="20" />
        </view>
        <text class="feature-name">一键报修</text>
        <text class="feature-desc">快速提交报修工单</text>
      </view>

      <!-- 我的报修 / 我的工单 -->
      <view
        class="feature-item"
        @click="goPage(authStore.isEngineer ? '/pages/engineer/my-orders/index' : '/pages/my-repairs/index')"
      >
        <view class="feature-icon icon-list">
          <SvgIcon name="clipboard" :size="20" />
        </view>
        <text class="feature-name">{{ authStore.isEngineer ? '我的工单' : '我的报修' }}</text>
        <text class="feature-desc">查看工单处理进度</text>
      </view>

      <!-- 所有工单 — 仅工程师 -->
      <view v-if="authStore.isEngineer" class="feature-item" @click="goPage('/pages/engineer/all-orders/index')">
        <view class="feature-icon icon-all">
          <SvgIcon name="package" :size="20" />
        </view>
        <text class="feature-name">所有工单</text>
        <text class="feature-desc">待接单工单池</text>
      </view>

      <!-- 工程师期排 — 内部员工、管理员可见 -->
      <view v-if="authStore.isInternalUser || authStore.isAdmin" class="feature-item" @click="goPage('/pages/schedule/index')">
        <view class="feature-icon icon-calendar">
          <SvgIcon name="calendar" :size="20" />
        </view>
        <text class="feature-name">工程师期排</text>
        <text class="feature-desc">查看排期与空闲时间</text>
      </view>

      <!-- 投诉建议 — 所有用户 -->
      <view class="feature-item" @click="goPage('/pages/complaint/index')">
        <view class="feature-icon icon-feedback">
          <SvgIcon name="envelope" :size="20" />
        </view>
        <text class="feature-name">投诉建议</text>
        <text class="feature-desc">一键投诉 · 我的投诉</text>
      </view>

      <!-- 联系我们 — 所有用户 -->
      <view class="feature-item" @click="goPage('/pages/contact/index')">
        <view class="feature-icon icon-contact">
          <SvgIcon name="phone" :size="20" />
        </view>
        <text class="feature-name">联系我们</text>
        <text class="feature-desc">工程师信息 · 地图导航</text>
      </view>
    </view>

    <!-- 自定义 TabBar -->
    <CustomTabBar />

    <!-- 修改密码弹窗 -->
    <view class="popup-overlay" v-if="showPwdPopup" @click="showPwdPopup = false">
      <view class="popup-card" @click.stop>
        <text class="popup-title">修改密码</text>
        <input class="pwd-input" v-model="pwdForm.oldPwd" type="password" placeholder="旧密码" placeholder-style="color:#CBD5E1" />
        <input class="pwd-input" v-model="pwdForm.newPwd" type="password" placeholder="新密码（至少6位）" placeholder-style="color:#CBD5E1" />
        <input class="pwd-input" v-model="pwdForm.confirm" type="password" placeholder="确认新密码" placeholder-style="color:#CBD5E1" />
        <view class="popup-actions">
          <button class="btn-cancel" @click="showPwdPopup = false">取消</button>
          <button class="btn-confirm" :disabled="submittingPwd" @click="submitChangePwd">确认修改</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRepairStore } from '@/stores/repair'
import CustomTabBar from '@/components/CustomTabBar.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const authStore = useAuthStore()
const repairStore = useRepairStore()

const stats = ref({
  myRepairCount: 0,
  processingCount: 0,
  doneCount: 0
})

const roleLabel = computed(() => {
  const map = { normal: '外部人员', internal: '内部员工', engineer: '工程师', admin: '管理员' }
  return map[authStore.userType] || '用户'
})

const router = useRouter()

const goPage = (url) => {
  // 从首页跳转到目标页面
  router.push(url)
}

const goMyRepairs = () => {
  if (authStore.isEngineer) {
    router.push('/pages/engineer/my-orders/index')
  } else {
    router.push('/pages/my-repairs/index')
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

// ── 修改密码 ──
const showPwdPopup = ref(false)
const pwdForm = ref({ oldPwd: '', newPwd: '', confirm: '' })
const submittingPwd = ref(false)

const openChangePwd = () => {
  pwdForm.value = { oldPwd: '', newPwd: '', confirm: '' }
  showPwdPopup.value = true
}

const submitChangePwd = async () => {
  const f = pwdForm.value
  if (!f.oldPwd || !f.newPwd) return uni.showToast({ title: '请填写旧密码与新密码', icon: 'none' })
  if (f.newPwd.length < 6) return uni.showToast({ title: '新密码至少6位', icon: 'none' })
  if (f.newPwd !== f.confirm) return uni.showToast({ title: '两次输入的新密码不一致', icon: 'none' })
  submittingPwd.value = true
  try {
    await authStore.changePassword(f.oldPwd, f.newPwd)
    uni.showToast({ title: '密码修改成功，请重新登录', icon: 'success' })
    showPwdPopup.value = false
    setTimeout(() => authStore.logout(), 800)
  } catch { /* handled */ } finally {
    submittingPwd.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await repairStore.fetchStats()
    if (data) {
      stats.value = {
        myRepairCount: data.total || 0,
        processingCount: data.processing || 0,
        doneCount: data.completed || 0
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
  background: #F8FAFC;
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
  background: linear-gradient(135deg, #0F172A, #1E293B);
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
  background: rgba(255, 255, 255, 0.12);
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
  gap: 12rpx;
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
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);

  &:first-child { margin-left: 0; }
  &:last-child { margin-right: 0; }
}

.stat-num {
  font-size: 44rpx;
  font-weight: 800;
  color: #020617;
  display: block;

  &.processing { color: #D97706; }
  &.done { color: #16A34A; }
}

.stat-label {
  font-size: 22rpx;
  color: #64748B;
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
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.25s ease;

  &:active {
    transform: scale(0.96);
    box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.06);
  }
}

.feature-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;

  &.icon-repair    { background: #FEF3C7; }
  &.icon-list      { background: #F0F9FF; }
  &.icon-all       { background: #FEF3C7; }
  &.icon-calendar  { background: #F0FDF4; }
  &.icon-feedback  { background: #F0F9FF; }
  &.icon-contact   { background: #F0FDF4; }
}

.feature-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #020617;
  margin-bottom: 4rpx;
}

.feature-desc {
  font-size: 22rpx;
  color: #64748B;
}

/* 修改密码弹窗 */
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.popup-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #020617;
  text-align: center;
}

.pwd-input {
  height: 80rpx;
  background: #F1F5F9;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #334155;
}

.popup-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 8rpx;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  border-radius: 50rpx;
  line-height: 80rpx;
  text-align: center;
  border: none;
}

.btn-cancel { background: #F1F5F9; color: #334155; }
.btn-confirm { background: #0F172A; color: #FFFFFF; }
.btn-confirm[disabled] { background: #94A3B8; }
</style>
