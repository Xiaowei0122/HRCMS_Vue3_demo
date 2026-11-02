<!--
  我的报修 — Navbar + 下划线式筛选 + 工单卡片列表
-->
<template>
  <view class="page">
    <PageNavbar title="我的报修" :scrolled="scrolled" />

    <!-- 状态筛选（可横向滚动 · 下划线高亮）+ 视图切换 -->
    <view class="filter-bar">
      <view class="filter-tabs">
        <view
          v-for="t in statusTabs"
          :key="t.value"
          class="filter-tab"
          :class="{ active: currentStatus === t.value }"
          @click="switchFilter(t.value)"
        >
          {{ t.label }}
        </view>
      </view>
      <view class="filter-divider" />
      <ViewToggle :mode="viewMode" @toggle="toggleView" />
    </view>

    <scroll-view scroll-y class="scroll-body" :refresher-enabled="true" :refresher-triggered="refreshing" @refresherrefresh="onRefresh" @scrolltolower="onLoadMore" @scroll="onScroll">
      <!-- 详情模式：卡片 -->
      <view v-if="list.length && viewMode === 'detail'" class="order-list">
        <view v-for="item in list" :key="item._id || item.id" class="order-card" @click="goDetail(item)">
          <!-- 头部：工单号 + 状态 -->
          <view class="card-header">
            <text class="order-no">工单 {{ item.orderNo }}</text>
            <text class="order-status" :class="'status-' + statusKey(item.status)">{{ item.status || '待接单' }}</text>
          </view>

          <!-- 信息行 -->
          <view class="card-body">
            <view class="info-row">
              <text class="info-label">报修单位</text>
              <text class="info-value ellipsis">{{ item.company }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">设备类型</text>
              <text class="info-value">{{ item.deviceType || '未指定' }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">紧急程度</text>
              <text class="info-value urgency" :class="'urgency-' + priorityKey(item.priority)">{{ item.priority || '普通' }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">报修时间</text>
              <text class="info-value">{{ fmt(item.createTime || item.repairDate) }}</text>
            </view>
          </view>

          <!-- 底部：工程师 + 详情 -->
          <view class="card-footer">
            <view class="engineer" v-if="item.engineer">
              <view class="engineer-avatar">{{ item.engineer.charAt(0) }}</view>
              <text class="engineer-name">{{ item.engineer }}</text>
            </view>
            <view class="engineer wait" v-else>
              <SvgIcon name="clock" :size="24" color="#FF7D00" />
              <text>等待接单</text>
            </view>
            <view class="detail-btn">
              <text>详情</text>
              <SvgIcon name="caretRight" :size="16" color="#165DFF" />
            </view>
          </view>
        </view>
      </view>

      <!-- 列表模式：紧凑单行 -->
      <view v-else-if="list.length && viewMode === 'list'" class="compact-list">
        <view v-for="item in list" :key="item._id || item.id" class="compact-item" @click="goDetail(item)">
          <view class="compact-main">
            <text class="compact-no">工单 {{ item.orderNo }}</text>
            <text class="compact-company ellipsis">{{ item.company }}</text>
          </view>
          <text class="compact-status" :class="'status-' + statusKey(item.status)">{{ item.status || '待接单' }}</text>
          <text class="compact-time">{{ fmt(item.createTime || item.repairDate) }}</text>
        </view>
      </view>

      <EmptyState v-else icon="clipboard" text="暂无报修记录" sub-text="提交报修后，工单将显示在这里" />
      <view v-if="list.length" class="foot-msg"><text>{{ noMore ? '— 没有更多了 —' : '加载中...' }}</text></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRepairStore } from '@/stores/repair'
import SvgIcon from '@/components/SvgIcon.vue'
import PageNavbar from '@/components/PageNavbar.vue'
import ViewToggle from '@/components/ViewToggle.vue'
import EmptyState from '@/components/EmptyState.vue'
import { STATUS, statusKey, priorityKey } from '@/utils/repair-status'
import { useScrollHide } from '@/utils/useScrollHide'

const repairStore = useRepairStore()
const route = useRoute()
const list = ref([])
const refreshing = ref(false)
const currentStatus = ref('')
const page = ref(1)
const noMore = ref(false)
const { scrolled, onScroll } = useScrollHide()

// 列表/详情视图切换（全域记忆）
const viewMode = ref(uni.getStorageSync('orderViewMode') || 'detail')
const toggleView = () => {
  viewMode.value = viewMode.value === 'list' ? 'detail' : 'list'
  uni.setStorageSync('orderViewMode', viewMode.value)
}

const statusTabs = [
  { label: '全部', value: '' },
  { label: '待处理', value: STATUS.PENDING },
  { label: '已预约', value: STATUS.RESERVED },
  { label: '处理中', value: STATUS.PROCESSING },
  { label: '待确认', value: STATUS.CONFIRMING },
  { label: '已归档', value: STATUS.ARCHIVED },
  { label: '已完成', value: STATUS.DONE }
]

const switchFilter = (v) => { currentStatus.value = v; page.value = 1; noMore.value = false; loadList() }

const loadList = async () => {
  try {
    const data = await repairStore.fetchMyRepairs({ status: currentStatus.value || undefined, page: page.value, pageSize: 20 })
    const items = Array.isArray(data) ? data : (data?.records || [])
    if (page.value === 1) list.value = items; else list.value.push(...items)
    if (items.length < 20) noMore.value = true
  } catch {}
}

const onRefresh = async () => { refreshing.value = true; page.value = 1; noMore.value = false; await loadList(); refreshing.value = false }
const onLoadMore = () => { if (!noMore.value) { page.value++; loadList() } }
const goDetail = (item) => { uni.navigateTo({ url: `/pages/repair-detail/index?id=${item._id || item.id}` }) }

const fmt = (t) => { if (!t) return ''; const d = new Date(t); const p = n => String(n).padStart(2, '0'); return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}` }

onMounted(() => {
  const s = route.query.status
  if (s) currentStatus.value = s
  loadList()
})
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; }

/* 筛选行：可横向滚动 Tab + 固定右侧视图切换图标 */
.filter-bar {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1rpx solid #F2F3F5;
  flex-shrink: 0;
  padding-right: 16rpx;
}

/* 下划线式筛选（可横向滚动） */
.filter-tabs {
  flex: 1;
  min-width: 0;
  display: flex;
  padding: 0 12rpx;
  overflow-x: auto;
  &::-webkit-scrollbar { display: none; }
}

.filter-divider {
  width: 1rpx;
  height: 40rpx;
  background: #E5E6EB;
  flex-shrink: 0;
  margin: 0 12rpx;
}
.filter-tab {
  padding: 24rpx 24rpx;
  font-size: 28rpx;
  color: #4E5969;
  font-weight: 500;
  white-space: nowrap;
  position: relative;
  flex-shrink: 0;

  &.active {
    color: #165DFF;
    font-weight: 700;
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 24rpx;
      right: 24rpx;
      height: 6rpx;
      background: linear-gradient(90deg, #165DFF, #4080FF);
      border-radius: 3rpx;
    }
  }
}

.scroll-body { flex: 1; }
.order-list { padding: 20rpx 24rpx; }

.order-card {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;

  &:active { transform: scale(0.98); }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #F2F3F5;
}
.order-no { font-size: 26rpx; color: #86909C; font-weight: 500; font-family: monospace; }

.order-status {
  font-size: 22rpx;
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
  font-weight: 600;

  &.status-pending    { background: #FFF3E8; color: #FF7D00; }
  &.status-reserved   { background: #FFF3E8; color: #FF7D00; }
  &.status-processing { background: #E8F3FF; color: #165DFF; }
  &.status-confirming { background: #F3E8FF; color: #722ED1; }
  &.status-archived   { background: #F2F3F5; color: #86909C; }
  &.status-done       { background: #E8FFEA; color: #00B42A; }
}

.card-body { padding: 4rpx 0; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 12rpx 0; }
.info-label { font-size: 26rpx; color: #86909C; flex-shrink: 0; }
.info-value { font-size: 26rpx; color: #1D2129; font-weight: 500; max-width: 420rpx; text-align: right; }
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.info-value.urgency {
  &.urgency-urgent { color: #F53F3F; }
  &.urgency-normal { color: #FF7D00; }
  &.urgency-low    { color: #00B42A; }
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #F2F3F5;
}
.engineer { display: flex; align-items: center; gap: 12rpx; }
.engineer-avatar {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 22rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}
.engineer-name { font-size: 24rpx; color: #4E5969; }
.engineer.wait { display: flex; align-items: center; gap: 8rpx; font-size: 24rpx; color: #FF7D00; }

.detail-btn { display: flex; align-items: center; gap: 2rpx; font-size: 24rpx; color: #165DFF; font-weight: 500; }

.foot-msg { text-align: center; padding: 32rpx; font-size: 24rpx; color: #86909C; }

/* ── 列表模式：紧凑单行 ── */
.compact-list { padding: 20rpx 24rpx; }
.compact-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  &:active { transform: scale(0.99); }
}
.compact-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6rpx; }
.compact-no { font-size: 24rpx; color: #86909C; font-family: monospace; font-weight: 500; }
.compact-company { font-size: 26rpx; color: #1D2129; font-weight: 500; max-width: 100%; }
.compact-status {
  font-size: 20rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 600;
  flex-shrink: 0;

  &.status-pending    { background: #FFF3E8; color: #FF7D00; }
  &.status-reserved   { background: #FFF3E8; color: #FF7D00; }
  &.status-processing { background: #E8F3FF; color: #165DFF; }
  &.status-confirming { background: #F3E8FF; color: #722ED1; }
  &.status-archived   { background: #F2F3F5; color: #86909C; }
  &.status-done       { background: #E8FFEA; color: #00B42A; }
  &.status-cancelled  { background: #F2F3F5; color: #86909C; }
}
.compact-time { font-size: 22rpx; color: #C9CDD4; flex-shrink: 0; }
</style>
