<!--
  所有工单（工程师端）— Navbar + 下划线式筛选 + 工单卡片
-->
<template>
  <view class="page">
    <PageNavbar title="所有工单" :scrolled="scrolled" />

    <!-- 状态筛选（可横向滚动 · 下划线高亮）+ 视图切换 -->
    <view class="filter-bar">
      <view class="filter-tabs">
        <view
          v-for="tab in statusTabs"
          :key="tab.value"
          class="filter-tab"
          :class="{ active: currentStatus === tab.value }"
          @click="switchTab(tab.value)"
        >
          {{ tab.label }}
          <text v-if="tab.value === STATUS.PENDING && pendingCount > 0" class="badge">{{ pendingCount }}</text>
        </view>
      </view>
      <view class="filter-divider" />
      <ViewToggle :mode="viewMode" @toggle="toggleView" />
    </view>

    <scroll-view
      scroll-y
      class="list-scroll"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <view v-if="list.length > 0 && viewMode === 'detail'" class="order-list">
        <view
          v-for="item in list"
          :key="item._id || item.id"
          class="order-card"
          @click="goDetail(item)"
        >
          <!-- 紧急标识条 -->
          <view class="card-urgency-bar" :class="'bar-' + priorityKey(item.priority)"></view>

          <view class="card-main">
            <view class="card-top">
              <text class="order-no">工单 {{ item.orderNo }}</text>
              <view class="order-status" :class="'status-' + statusKey(item.status)">
                {{ item.status || '待接单' }}
              </view>
            </view>

            <view class="card-body">
              <view class="info-row">
                <text class="info-label">报修单位</text>
                <text class="info-value ellipsis">{{ item.company }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">故障描述</text>
                <text class="info-value ellipsis">{{ item.description }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">联系人</text>
                <text class="info-value">{{ item.contact }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">报修时间</text>
                <text class="info-value">{{ formatDate(item.createTime) }}</text>
              </view>
            </view>

            <view class="card-foot">
              <view class="urgency-label" :class="'urgency-' + priorityKey(item.priority)">
                {{ item.priority || '普通' }}
              </view>
              <view class="detail-btn">
                <text>{{ (item.status === STATUS.PENDING || item.status === STATUS.RESERVED) ? '待接单' : '查看详情' }}</text>
                <SvgIcon name="caretRight" :size="16" color="#165DFF" />
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 列表模式：紧凑单行 -->
      <view v-else-if="list.length > 0 && viewMode === 'list'" class="compact-list">
        <view v-for="item in list" :key="item._id || item.id" class="compact-item" @click="goDetail(item)">
          <view class="compact-main">
            <text class="compact-no">工单 {{ item.orderNo }}</text>
            <text class="compact-company ellipsis">{{ item.company }}</text>
          </view>
          <text class="compact-status" :class="'status-' + statusKey(item.status)">{{ item.status || '待接单' }}</text>
          <text class="compact-time">{{ formatDate(item.createTime) }}</text>
        </view>
      </view>

      <EmptyState
        v-else
        icon="package"
        text="暂无工单"
        sub-text="用户提交报修后，工单将显示在这里"
      />

      <view class="list-footer" v-if="list.length > 0">
        <text class="footer-text">{{ noMore ? '— 没有更多了 —' : '加载中...' }}</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRepairStore } from '@/stores/repair'
import PageNavbar from '@/components/PageNavbar.vue'
import ViewToggle from '@/components/ViewToggle.vue'
import EmptyState from '@/components/EmptyState.vue'
import SvgIcon from '@/components/SvgIcon.vue'
import { STATUS, statusKey, priorityKey } from '@/utils/repair-status'
import { useScrollHide } from '@/utils/useScrollHide'

const repairStore = useRepairStore()
const route = useRoute()
const list = ref([])
const refreshing = ref(false)
const currentStatus = ref('')
const page = ref(1)
const noMore = ref(false)
const pendingCount = ref(0)
const { scrolled, onScroll } = useScrollHide()

// 列表/详情视图切换（全域记忆）
const viewMode = ref(uni.getStorageSync('orderViewMode') || 'detail')
const toggleView = () => {
  viewMode.value = viewMode.value === 'list' ? 'detail' : 'list'
  uni.setStorageSync('orderViewMode', viewMode.value)
}

const statusTabs = [
  { label: '全部', value: '' },
  { label: '待接单', value: STATUS.PENDING },
  { label: '已预约', value: STATUS.RESERVED },
  { label: '处理中', value: STATUS.PROCESSING },
  { label: '待确认', value: STATUS.CONFIRMING },
  { label: '已归档', value: STATUS.ARCHIVED },
  { label: '已完成', value: STATUS.DONE }
]

const switchTab = (val) => {
  currentStatus.value = val
  page.value = 1
  noMore.value = false
  loadList()
}

const loadList = async () => {
  try {
    const data = await repairStore.fetchAllOrders({
      status: currentStatus.value,
      page: page.value,
      pageSize: 20
    })

    const items = Array.isArray(data) ? data : (data?.records || data || [])
    if (page.value === 1) {
      list.value = items
    } else {
      list.value.push(...items)
    }
    if (items.length < 20) noMore.value = true
  } catch { /* handled */ }
}

const onRefresh = async () => {
  refreshing.value = true
  page.value = 1
  noMore.value = false
  await loadList()
  refreshing.value = false
}

const onLoadMore = () => {
  if (noMore.value) return
  page.value++
  loadList()
}

const goDetail = (item) => {
  const id = item._id || item.id
  uni.navigateTo({ url: `/pages/repair-detail/index?id=${id}` })
}

const formatDate = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
}

// 待接单角标数量（全局统计，供「待接单」Tab 红点）
const loadPendingCount = async () => {
  try {
    const g = await repairStore.fetchStats()
    if (g) pendingCount.value = g.pending || 0
  } catch { /* handled */ }
}

onMounted(() => {
  const s = route.query.status
  if (s) currentStatus.value = s
  loadList()
  loadPendingCount()
})
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}

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

.badge {
  display: inline-block;
  min-width: 32rpx;
  height: 32rpx;
  line-height: 32rpx;
  background: #F53F3F;
  color: #fff;
  font-size: 20rpx;
  border-radius: 16rpx;
  text-align: center;
  padding: 0 8rpx;
  margin-left: 6rpx;
  vertical-align: middle;
}

.list-scroll { flex: 1; }

.order-list { padding: 20rpx 24rpx; }

.order-card {
  background: #fff;
  border-radius: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
  overflow: hidden;
  display: flex;
  transition: all 0.25s ease;

  &:active { transform: scale(0.98); }
}

.card-urgency-bar {
  width: 8rpx;
  flex-shrink: 0;

  &.bar-urgent { background: #F53F3F; }
  &.bar-normal { background: #FF7D00; }
  &.bar-low    { background: #00B42A; }
}

.card-main { flex: 1; min-width: 0; padding: 24rpx; }

.card-top {
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
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 12rpx 0; gap: 24rpx; }
.info-label { font-size: 26rpx; color: #86909C; flex-shrink: 0; }
.info-value { font-size: 26rpx; color: #1D2129; font-weight: 500; max-width: 440rpx; text-align: right; }
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #F2F3F5;
}

.urgency-label {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;

  &.urgency-urgent { background: #FFECE8; color: #F53F3F; }
  &.urgency-normal { background: #FFF3E8; color: #FF7D00; }
  &.urgency-low    { background: #E8FFEA; color: #00B42A; }
}

.detail-btn { display: flex; align-items: center; gap: 2rpx; font-size: 24rpx; color: #165DFF; font-weight: 500; }

.list-footer { text-align: center; padding: 32rpx; }
.footer-text { font-size: 24rpx; color: #86909C; }

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
