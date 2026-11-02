<!--
  首页 — 登录 / 未登录两态
  蓝色渐变主题 · 快捷功能九宫格 · 技术知识库 · 2 栏 TabBar
  未登录：guest 头部 + 登录引导卡 + 九宫格 + 知识库
  已登录：用户头部 + 统计卡 + 九宫格 + 知识库
-->
<template>
  <view class="home-page">
    <!-- ============ 未登录态 ============ -->
    <template v-if="!authStore.isLoggedIn">
      <view class="header">
        <view class="guest-row">
          <view class="guest-avatar">
            <SvgIcon name="user" :size="26" color="rgba(255,255,255,0.7)" />
          </view>
          <view class="guest-info">
            <text class="guest-title">欢迎使用运维报修</text>
            <text class="guest-desc">登录后查看工单进度与专属服务</text>
          </view>
          <button class="login-btn" @click="goLogin">登录 / 注册</button>
        </view>
      </view>

      <!-- 登录引导卡 -->
      <view class="stats-guest">
        <view class="stats-guest-icon">
          <SvgIcon name="bell" :size="22" color="#165DFF" />
        </view>
        <view class="stats-guest-content">
          <text class="stats-guest-title">登录后查看我的报修数据</text>
          <text class="stats-guest-desc">实时追踪处理进度，历史工单一键查询</text>
        </view>
        <button class="stats-guest-btn" @click="goLogin">立即登录</button>
      </view>
    </template>

    <!-- ============ 已登录态 ============ -->
    <template v-else>
      <view class="header">
        <view class="user-row">
          <view class="avatar">
            <text class="avatar-text">{{ authStore.userName.charAt(0) }}</text>
          </view>
          <view class="user-info">
            <text class="user-name">{{ authStore.userName }}</text>
            <text class="user-role">{{ authStore.roleLabel }}</text>
          </view>
          <view class="header-actions">
            <text class="header-btn" @click="openChangePwd">改密</text>
            <text class="header-btn" @click="handleLogout">退出</text>
          </view>
        </view>
      </view>

      <!-- 统计卡片 -->
      <view class="stats-card" :class="{ 'stats-card--admin': authStore.isAdmin }">
        <!-- 管理员：全部工单 7 项全量统计 -->
        <template v-if="authStore.isAdmin">
          <view class="stat-item" @click="goStatus('')">
            <text class="stat-num blue">{{ adminStats.total }}</text>
            <text class="stat-label">全部工单</text>
          </view>
          <view class="stat-item" @click="goStatus(STATUS.PENDING)">
            <text class="stat-num orange">{{ adminStats.pending }}</text>
            <text class="stat-label">待接单</text>
            <view v-if="adminStats.pending > 0" class="stat-badge" />
          </view>
          <view class="stat-item" @click="goStatus(STATUS.RESERVED)">
            <text class="stat-num cyan">{{ adminStats.reserved }}</text>
            <text class="stat-label">已预约</text>
          </view>
          <view class="stat-item" @click="goStatus(STATUS.PROCESSING)">
            <text class="stat-num blue">{{ adminStats.processing }}</text>
            <text class="stat-label">处理中</text>
          </view>
          <view class="stat-item" @click="goStatus(STATUS.CONFIRMING)">
            <text class="stat-num purple">{{ adminStats.confirming }}</text>
            <text class="stat-label">待确认</text>
          </view>
          <view class="stat-item" @click="goStatus(STATUS.ARCHIVED)">
            <text class="stat-num gray">{{ adminStats.archived }}</text>
            <text class="stat-label">已归档</text>
          </view>
          <view class="stat-item" @click="goStatus(STATUS.DONE)">
            <text class="stat-num green">{{ adminStats.done }}</text>
            <text class="stat-label">已完成</text>
          </view>
        </template>
        <!-- 非管理员：我的报修 / 待接单(待处理) / 处理中 / 待确认 / 已完成 -->
        <template v-else>
          <view class="stat-item" @click="goStatus('')">
            <text class="stat-num blue">{{ stats.myRepairCount }}</text>
            <text class="stat-label">我的报修</text>
          </view>
          <view class="stat-item" @click="goStatus(STATUS.PENDING)">
            <text class="stat-num orange">{{ stats.pendingCount }}</text>
            <text class="stat-label">{{ pendingLabel }}</text>
            <view v-if="stats.pendingCount > 0" class="stat-badge" />
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
        </template>
      </view>
    </template>

    <!-- ============ 快捷功能（两态共用） ============ -->
    <view class="section">
      <view class="section-title">快捷功能</view>
      <view class="func-grid">
        <!-- 一键报修 — 所有用户 -->
        <view class="func-item" @click="goPage('/pages/repair-apply/index')">
          <view class="func-icon repair">
            <SvgIcon name="wrench" :size="24" color="#fff" />
          </view>
          <text class="func-label">一键报修</text>
        </view>

        <!-- 我的报修 / 我的工单 -->
        <view class="func-item" @click="goMyRepairs">
          <view class="func-icon mine">
            <SvgIcon name="clipboard" :size="24" color="#fff" />
            <view v-if="badgeCount > 0" class="badge">{{ badgeCount }}</view>
          </view>
          <text class="func-label">{{ authStore.isAdmin ? '工单列表' : (authStore.isEngineer ? '我的工单' : '我的报修') }}</text>
        </view>

        <!-- 工程师排期 — 内部员工/工程师/管理员 -->
        <view v-if="canSeeSchedule" class="func-item" @click="goPage('/pages/schedule/index')">
          <view class="func-icon schedule">
            <SvgIcon name="calendar" :size="24" color="#fff" />
          </view>
          <text class="func-label">工程师排期</text>
        </view>

        <!-- 投诉建议 — 所有用户 -->
        <view class="func-item" @click="goPage('/pages/complaint/index')">
          <view class="func-icon complaint">
            <SvgIcon name="envelope" :size="24" color="#fff" />
          </view>
          <text class="func-label">投诉建议</text>
        </view>

        <!-- 联系我们 — 所有用户 -->
        <view class="func-item" @click="goPage('/pages/contact/index')">
          <view class="func-icon contact">
            <SvgIcon name="phone" :size="24" color="#fff" />
          </view>
          <text class="func-label">联系我们</text>
        </view>

        <!-- 技术知识库 — 所有用户 -->
        <view class="func-item" @click="goPage('/pages/knowledge/index')">
          <view class="func-icon knowledge">
            <SvgIcon name="notePencil" :size="24" color="#fff" />
          </view>
          <text class="func-label">技术知识库</text>
        </view>
      </view>
    </view>

    <!-- ============ 技术知识库（两态共用，首页仅展示置顶） ============ -->
    <view class="section">
      <view class="section-title">
        <text>技术知识库</text>
        <text class="section-more" @click="goPage('/pages/knowledge/index')">查看全部</text>
      </view>
      <view class="article-list">
        <view v-for="a in articles" :key="a.id" class="article-card" @click="openArticle(a)">
          <view class="article-thumb" :class="a.type">
            <img v-if="a.cover" :src="a.cover" class="thumb-img" />
            <template v-else>
            <!-- 驱动安装 -->
            <svg v-if="a.type === 'printer'" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
            <!-- 故障案例 -->
            <svg v-else-if="a.type === 'case'" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <!-- 系统维护 -->
            <svg v-else-if="a.type === 'system'" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            <!-- 网络运维 -->
            <svg v-else-if="a.type === 'network'" viewBox="0 0 24 24"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>
            <!-- 监控安防 -->
            <svg v-else-if="a.type === 'camera'" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
            <!-- 兜底 -->
            <svg v-else viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            </template>
          </view>
          <view class="article-content">
            <view class="article-main">
              <text class="article-title">{{ a.title }}</text>
              <text class="article-desc">{{ a.desc }}</text>
            </view>
            <view class="article-meta">
              <text class="article-tag" :class="a.tagClass">{{ a.tag }}</text>
              <text class="article-views">
                <svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                {{ a.views }}
              </text>
            </view>
          </view>
        </view>
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
import { articleStyle, tagClassFor, formatViews } from '@/utils/knowledge'
import { STATUS } from '@/utils/repair-status'

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

// 管理员全局统计（7 项全量）
const adminStats = ref({
  total: 0,
  pending: 0,
  reserved: 0,
  processing: 0,
  confirming: 0,
  archived: 0,
  done: 0
})

// 技术知识库 — 接入 /public/knowledge（免登录，仅 published；首页只取置顶）
const articles = ref([])

const loadKnowledge = async () => {
  try {
    const data = await repairStore.fetchKnowledge({ page: 1, size: 6, pinned: true })
    const records = Array.isArray(data) ? data : (data?.records || [])
    articles.value = records.map((n) => {
      const style = articleStyle(n)
      return {
        id: n.id,
        type: style,
        tag: n.type || '技术知识',
        tagClass: tagClassFor(style),
        title: n.title,
        desc: n.summary || '',
        views: formatViews(n.views),
        cover: n.cover || '',
      }
    })
  } catch {
    // 加载失败保留空列表
  }
}

// 未登录时无统计数据，角标归零；工程师/管理员看「待接单」抢单池，其余看「处理中」
const badgeCount = computed(() => {
  if (!authStore.isLoggedIn) return 0
  if (authStore.isAdmin) return adminStats.value.pending
  if (authStore.isEngineer) return stats.value.pendingCount
  return stats.value.processingCount
})

// 非接单角色（业务/财务/运营/外部人员）不接单，统计里的「待接单」改名「待处理」
const pendingLabel = computed(() => (authStore.isEngineer || authStore.isAdmin) ? '待接单' : '待处理')

// 工程师排期可见：与后端 require_permission("repair:schedule","repair:audit") 对齐
const canSeeSchedule = computed(() => authStore.hasPerm('repair:schedule', 'repair:audit'))

const goPage = (url) => router.push(url)
const goLogin = () => router.push('/pages/public/login/index')

// 文章详情 — 跳转知识库详情页
const openArticle = (a) => router.push(`/pages/knowledge-detail/index?id=${a.id}`)

const goMyRepairs = () => goStatus('')

// 统计卡按状态跳转：工程师 → 我的工单，管理员 → 全部工单，客户/业务 → 我的报修
const goStatus = (status) => {
  const q = status ? `?status=${encodeURIComponent(status)}` : ''
  if (authStore.isEngineer) {
    router.push(`/pages/engineer/my-orders/index${q}`)
  } else if (authStore.isAdmin) {
    router.push(`/pages/engineer/all-orders/index${q}`)
  } else {
    router.push(`/pages/my-repairs/index${q}`)
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
  if (!authStore.isLoggedIn) return
  // 管理员：全局统计（7 项全量）
  if (authStore.isAdmin) {
    try {
      const g = await repairStore.fetchStats()
      if (g) {
        adminStats.value = {
          total: g.total || 0,
          pending: g.pending || 0,
          reserved: g.reserved || 0,
          processing: g.processing || 0,
          confirming: g.confirming || 0,
          archived: g.archived || 0,
          done: g.done || 0
        }
      }
    } catch {
      // 忽略全局统计失败
    }
    return
  }
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
  // 工程师的「待接单」是全局抢单池，需额外拉全局统计（本人 my/stats 不含未指派单）
  if (authStore.isEngineer) {
    try {
      const g = await repairStore.fetchStats()
      if (g) stats.value.pendingCount = g.pending || 0
    } catch {
      // 忽略全局统计失败
    }
  }
}

onMounted(() => {
  loadStats()
  loadKnowledge()
})
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 140rpx;
}

/* ═══ 顶部渐变 Header ═══ */
.header {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 60%, #5B8DEF 100%);
  padding: calc(env(safe-area-inset-top) + 56rpx) 40rpx 160rpx;
}
.header::before {
  content: '';
  position: absolute;
  top: -120rpx;
  right: -80rpx;
  width: 400rpx;
  height: 400rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
}
.header::after {
  content: '';
  position: absolute;
  bottom: -160rpx;
  left: -60rpx;
  width: 320rpx;
  height: 320rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}

/* 未登录 header */
.guest-row {
  display: flex;
  align-items: center;
  gap: 28rpx;
  position: relative;
  z-index: 1;
}
.guest-avatar {
  width: 104rpx;
  height: 104rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: 2rpx dashed rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.guest-info { flex: 1; }
.guest-title {
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
  display: block;
  margin-bottom: 6rpx;
}
.guest-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 24rpx;
}
.login-btn {
  padding: 20rpx 44rpx;
  border-radius: 48rpx;
  background: #fff;
  color: #165DFF;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

/* 已登录 header */
.user-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  position: relative;
  z-index: 1;
}
.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}
.avatar-text {
  color: #fff;
  font-size: 40rpx;
  font-weight: 700;
}
.user-info { flex: 1; }
.user-name {
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
  display: block;
  margin-bottom: 4rpx;
}
.user-role {
  color: rgba(255, 255, 255, 0.75);
  font-size: 24rpx;
}
.header-actions {
  display: flex;
  gap: 16rpx;
}
.header-btn {
  padding: 12rpx 28rpx;
  border-radius: 40rpx;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  font-size: 24rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.25);
}

/* ═══ 未登录登录引导卡 ═══ */
.stats-guest {
  margin: -120rpx 32rpx 0;
  background: #fff;
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  box-shadow: 0 16rpx 60rpx rgba(22, 93, 255, 0.12);
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 28rpx;
}
.stats-guest-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #E8F3FF, #D4E6FF);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stats-guest-content { flex: 1; min-width: 0; }
.stats-guest-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1D2129;
  display: block;
  margin-bottom: 4rpx;
}
.stats-guest-desc {
  font-size: 24rpx;
  color: #86909C;
}
.stats-guest-btn {
  padding: 16rpx 32rpx;
  border-radius: 36rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 24rpx;
  font-weight: 500;
  border: none;
  flex-shrink: 0;
}

/* ═══ 统计卡片 ═══ */
.stats-card {
  margin: -120rpx 32rpx 0;
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
.stat-badge {
  position: absolute;
  top: -4rpx;
  right: 24rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #F53F3F;
  border: 2rpx solid #fff;
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
  &.cyan   { color: #14C9C9; }
  &.gray   { color: #86909C; }
}

/* 管理员 7 项统计：4 列网格折 2 行 */
.stats-card--admin {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding: 32rpx 0;
}
.stats-card--admin .stat-item {
  padding: 16rpx 0;
}
.stats-card--admin .stat-item::after {
  display: none;
}
.stat-label {
  font-size: 24rpx;
  color: #86909C;
  margin-top: 8rpx;
}

/* ═══ 快捷功能 ═══ */
.section {
  padding: 40rpx 32rpx 0;
}
.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1D2129;
  margin-bottom: 28rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.section-title::before {
  content: '';
  width: 8rpx;
  height: 32rpx;
  background: linear-gradient(180deg, #165DFF, #4080FF);
  border-radius: 4rpx;
}
.section-more {
  margin-left: auto;
  font-size: 24rpx;
  color: #86909C;
  font-weight: 400;
}

.func-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16rpx;
  background: #fff;
  border-radius: 32rpx;
  padding: 40rpx 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}
.func-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}
.func-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &.repair    { background: linear-gradient(135deg, #FF7D00, #FF9A2E); }
  &.mine      { background: linear-gradient(135deg, #165DFF, #4080FF); }
  &.schedule  { background: linear-gradient(135deg, #722ED1, #9254DE); }
  &.complaint { background: linear-gradient(135deg, #F53F3F, #F76560); }
  &.contact   { background: linear-gradient(135deg, #00B42A, #23C343); }
  &.knowledge { background: linear-gradient(135deg, #0FC6C2, #36CFC9); }
}
.func-icon .badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  background: #F53F3F;
  color: #fff;
  font-size: 20rpx;
  min-width: 32rpx;
  height: 32rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8rpx;
  font-weight: 600;
  border: 4rpx solid #fff;
  box-sizing: content-box;
}
.func-label {
  font-size: 24rpx;
  color: #4E5969;
  font-weight: 500;
  text-align: center;
}

/* ═══ 技术知识库 ═══ */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.article-card {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  display: flex;
  gap: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}
.article-thumb {
  width: 180rpx;
  height: 180rpx;
  border-radius: 20rpx;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  &.printer { background: linear-gradient(135deg, #E8F3FF, #BEDAFF); }
  &.case    { background: linear-gradient(135deg, #FFF3E8, #FFD8A8); }
  &.system  { background: linear-gradient(135deg, #E8FFEA, #A8E6B0); }
  &.network { background: linear-gradient(135deg, #F0E8FF, #D4BFFF); }
  &.camera  { background: linear-gradient(135deg, #FFE8E8, #FFC8C8); }
}
.thumb-img { width: 100%; height: 100%; object-fit: cover; border-radius: 20rpx; }

.article-thumb svg {
  width: 80rpx;
  height: 80rpx;
  stroke-width: 1.5;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.article-thumb.printer svg { stroke: #165DFF; }
.article-thumb.case svg    { stroke: #FF7D00; }
.article-thumb.system svg  { stroke: #00B42A; }
.article-thumb.network svg { stroke: #722ED1; }
.article-thumb.camera svg  { stroke: #F53F3F; }

.article-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}
.article-main { display: flex; flex-direction: column; }
.article-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1D2129;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.article-desc {
  font-size: 24rpx;
  color: #86909C;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 8rpx;
}
.article-meta {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-top: 16rpx;
}
.article-tag {
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: 500;
}
.tag-tutorial { background: #E8F3FF; color: #165DFF; }
.tag-case     { background: #FFF3E8; color: #FF7D00; }
.tag-guide    { background: #E8FFEA; color: #00B42A; }
.tag-network  { background: #F0E8FF; color: #722ED1; }
.tag-camera   { background: #FFE8E8; color: #F53F3F; }
.article-views {
  font-size: 22rpx;
  color: #C9CDD4;
  display: flex;
  align-items: center;
  gap: 6rpx;
}
.article-views svg {
  width: 24rpx;
  height: 24rpx;
  stroke: #C9CDD4;
  fill: none;
  stroke-width: 2;
}

/* ═══ 修改密码弹窗 ═══ */
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
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.popup-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1D2129;
  text-align: center;
}
.pwd-input {
  height: 88rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #4E5969;
  box-sizing: border-box;
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
.btn-cancel { background: #F5F7FA; color: #4E5969; }
.btn-confirm { background: linear-gradient(135deg, #165DFF, #4080FF); color: #fff; box-shadow: 0 8rpx 24rpx rgba(22, 93, 255, 0.28); }
.btn-confirm[disabled] { background: #C9CDD4; box-shadow: none; }
</style>
