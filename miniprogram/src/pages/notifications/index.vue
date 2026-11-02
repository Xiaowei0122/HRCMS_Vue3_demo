<!--
  消息通知 — 站内通知列表（GET /notifications）+ 未读角标 + 已读标记
-->
<template>
  <view class="page">
    <PageNavbar title="消息通知" />

    <scroll-view
      scroll-y
      class="scroll-body"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view class="notify-toolbar">
        <text class="notify-count">{{ list.length ? `共 ${list.length} 条` : '暂无消息' }}</text>
        <text class="notify-read-all" v-if="unreadCount > 0" @click="markAllRead">全部已读</text>
      </view>

      <view v-if="list.length" class="notify-list">
        <view
          v-for="item in list"
          :key="item.id"
          class="notify-card"
          :class="{ unread: !item.read }"
          @click="readOne(item)"
        >
          <view class="notify-head">
            <view class="notify-title-row">
              <view v-if="!item.read" class="notify-dot" />
              <text class="notify-title">{{ item.title }}</text>
            </view>
            <text class="notify-time">{{ item.createdAt }}</text>
          </view>
          <text class="notify-content">{{ item.content }}</text>
          <view v-if="getChip(item)" class="notify-chip-row">
            <view class="notify-chip" :class="getChip(item).cls" @click.stop="goTarget(item)">
              <text>{{ getChip(item).label }}</text>
              <SvgIcon name="caretRight" :size="12" color="currentColor" />
            </view>
          </view>
        </view>
      </view>

      <EmptyState v-else icon="bell" text="暂无消息" sub-text="工单进度会在这里通知你" />
      <view class="safe-bottom" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post } from '@/utils/request'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const router = useRouter()
const list = ref([])
const unreadCount = ref(0)
const refreshing = ref(false)

// 类型 → 醒目直达 chip（颜色用状态色）
const CHIP_ROUTE_MAP = {
  repair_new_pending: { label: '去接单', cls: 'chip-pending', route: '/pages/engineer/my-orders/index?status=' + encodeURIComponent('待接单') },
  repair_new_unassigned: { label: '去指派', cls: 'chip-pending', route: '/pages/engineer/all-orders/index?status=' + encodeURIComponent('待接单') },
  repair_reserve: { label: '去接单', cls: 'chip-reserved', route: '/pages/engineer/my-orders/index?status=' + encodeURIComponent('已预约') },
  repair_assign: { label: '去处理', cls: 'chip-processing', route: '/pages/engineer/my-orders/index?status=' + encodeURIComponent('处理中') },
  repair_confirm: { label: '去确认', cls: 'chip-confirming', route: '/pages/my-repairs/index?status=' + encodeURIComponent('待确认') },
  repair_archived: { label: '去查看', cls: 'chip-archived', route: '/pages/my-repairs/index?status=' + encodeURIComponent('已归档') },
  repair_transfer: { label: '去处理', cls: 'chip-processing', route: '/pages/engineer/my-orders/index?status=' + encodeURIComponent('处理中') },
  repair_reserve_assign: { label: '去处理', cls: 'chip-confirming', route: '/pages/engineer/my-orders/index?status=' + encodeURIComponent('处理中') },
}

const getChip = (item) => {
  const type = item.type || ''
  if (CHIP_ROUTE_MAP[type]) return CHIP_ROUTE_MAP[type]
  // 详情类：从 link 解析 repair-detail/{id}
  const m = (item.link || '').match(/repair-detail\/([0-9a-fA-F]+)/)
  if (m) return { label: '查看工单', cls: 'chip-processing', route: `/pages/repair-detail/index?id=${m[1]}` }
  return null
}

const goTarget = async (item) => {
  const chip = getChip(item)
  if (!chip) return
  if (!item.read) {
    try {
      await post('/notifications/read', { id: item.id })
      item.read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch { /* handled */ }
  }
  router.push(chip.route)
}

const loadList = async () => {
  try {
    const data = await get('/notifications')
    list.value = Array.isArray(data) ? data : (data?.records || [])
    unreadCount.value = list.value.filter((n) => !n.read).length
  } catch {
    list.value = []
  }
}

const loadUnread = async () => {
  try {
    const res = await get('/notifications/unread-count')
    unreadCount.value = res?.count ?? 0
  } catch { /* handled */ }
}

const readOne = async (item) => {
  if (item.read) return
  try {
    await post('/notifications/read', { id: item.id })
    item.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch { /* handled */ }
}

const markAllRead = async () => {
  try {
    await post('/notifications/read', { all: true })
    list.value.forEach((n) => { n.read = true })
    unreadCount.value = 0
    uni.showToast({ title: '已全部标记为已读', icon: 'success' })
  } catch { /* handled */ }
}

const onRefresh = async () => {
  refreshing.value = true
  await Promise.all([loadList(), loadUnread()])
  refreshing.value = false
}

onMounted(() => {
  loadList()
  loadUnread()
})
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}

.scroll-body { flex: 1; }

.notify-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx 8rpx;
}
.notify-count { font-size: 24rpx; color: #86909C; }
.notify-read-all { font-size: 24rpx; color: #165DFF; font-weight: 500; }

.notify-list { padding: 16rpx 24rpx; }

.notify-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);

  &.unread { border-left: 6rpx solid #165DFF; }
}

.notify-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.notify-title-row {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex: 1;
  min-width: 0;
}

.notify-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: #F53F3F;
  flex-shrink: 0;
}

.notify-title {
  font-size: 30rpx;
  color: #1D2129;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notify-time {
  font-size: 22rpx;
  color: #C9CDD4;
  flex-shrink: 0;
  margin-left: 16rpx;
}

.notify-content {
  font-size: 26rpx;
  color: #4E5969;
  line-height: 1.6;
}

.notify-chip-row {
  display: flex;
  margin-top: 16rpx;
}
.notify-chip {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  font-weight: 600;
  padding: 8rpx 22rpx;
  border-radius: 24rpx;

  &.chip-pending    { background: #FFF3E8; color: #FF7D00; }
  &.chip-reserved   { background: #FFF3E8; color: #FF7D00; }
  &.chip-processing { background: #E8F3FF; color: #165DFF; }
  &.chip-confirming { background: #F3E8FF; color: #722ED1; }
  &.chip-archived   { background: #F2F3F5; color: #86909C; }
}

.safe-bottom { height: 40rpx; }
</style>
