<!--
  我的工单页面（工程师端）
  显示该工程师已接单的工单列表
-->
<template>
  <view class="my-orders-page">
    <!-- 顶部筛选 -->
    <view class="filter-bar">
      <view
        v-for="tab in statusTabs"
        :key="tab.value"
        class="filter-tab"
        :class="{ active: currentStatus === tab.value }"
        @click="switchTab(tab.value)"
      >
        {{ tab.label }}
      </view>
    </view>

    <scroll-view
      scroll-y
      class="list-scroll"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
    >
      <view v-if="list.length > 0" class="order-list">
        <view
          v-for="item in list"
          :key="item._id || item.id"
          class="order-card"
          @click="goDetail(item)"
        >
          <view class="card-top">
            <view class="order-no">
              <text class="no-text">{{ item.orderNo }}</text>
            </view>
            <view class="order-status" :class="'status-' + (item.status || 'processing')">
              {{ statusMap[item.status] || '处理中' }}
            </view>
          </view>

          <view class="card-body">
            <text class="card-company">{{ item.company }}</text>
            <text class="card-desc text-ellipsis-2">{{ item.description }}</text>
            <view class="card-meta">
              <text class="meta-item">📅 {{ formatDate(item.createTime) }}</text>
              <text class="meta-item">👤 {{ item.contactName }}</text>
              <text class="meta-item" v-if="item.contactPhone">📞 {{ item.contactPhone }}</text>
            </view>
          </view>

          <!-- 进度简述 -->
          <view class="card-progress" v-if="item.progress && item.progress.length">
            <text class="progress-hint">
              最新进度：{{ item.progress[item.progress.length - 1]?.content || '处理中' }}
            </text>
          </view>

          <view class="card-foot">
            <view class="urgency-label" :class="'urgency-' + (item.urgency || 'normal')">
              {{ urgencyMap[item.urgency] || '一般' }}
            </view>
            <text class="card-action">查看详情 →</text>
          </view>
        </view>
      </view>

      <EmptyState
        v-else
        icon="📋"
        text="暂无已接工单"
        sub-text="去"所有工单"接单吧"
      />

      <view class="list-footer" v-if="list.length > 0">
        <text class="footer-text">{{ noMore ? '— 没有更多了 —' : '加载中...' }}</text>
      </view>
    </scroll-view>

    <!-- 自定义 TabBar -->
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRepairStore } from '@/stores/repair'
import CustomTabBar from '@/components/CustomTabBar.vue'
import EmptyState from '@/components/EmptyState.vue'

const repairStore = useRepairStore()
const list = ref([])
const refreshing = ref(false)
const currentStatus = ref('processing')
const page = ref(1)
const noMore = ref(false)

const statusTabs = [
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'done' }
]

const statusMap = { processing: '处理中', done: '已完成' }
const urgencyMap = { urgent: '紧急', normal: '一般', low: '不急' }

const switchTab = (val) => {
  currentStatus.value = val
  page.value = 1
  noMore.value = false
  loadList()
}

const loadList = async () => {
  try {
    // 我的工单：通过 my 接口获取（带状态筛选）
    const data = await repairStore.fetchMyRepairs({
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

onMounted(() => {
  loadList()
})
</script>

<style lang="scss" scoped>
.my-orders-page {
  min-height: 100vh;
  background: #F7F7F7;
  display: flex;
  flex-direction: column;
  padding-bottom: 140rpx;
}

.filter-bar {
  display: flex;
  background: #FFFFFF;
  padding: 16rpx 24rpx;
  gap: 12rpx;
  position: sticky;
  top: 0;
  z-index: 10;
}

.filter-tab {
  flex: 1;
  text-align: center;
  padding: 12rpx 0;
  font-size: 26rpx;
  color: #666;
  background: #F7F7F7;
  border-radius: 8rpx;
  transition: all 0.25s;

  &.active {
    background: #D32223;
    color: #FFFFFF;
    font-weight: 600;
  }
}

.list-scroll { flex: 1; }

.order-list { padding: 16rpx 24rpx; }

.order-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);

  &:active { transform: scale(0.98); }
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.no-text {
  font-size: 24rpx;
  color: #333;
  font-family: monospace;
  font-weight: 500;
}

.order-status {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;

  &.status-processing { background: #E3F2FD; color: #1565C0; }
  &.status-done       { background: #E8F5E9; color: #2E7D32; }
}

.card-company {
  font-size: 30rpx; font-weight: 700; color: #222;
  display: block; margin-bottom: 8rpx;
}

.card-desc {
  font-size: 26rpx; color: #666; line-height: 1.5; margin-bottom: 12rpx;
}

.card-meta {
  display: flex; flex-wrap: wrap; gap: 8rpx 24rpx;
}

.meta-item { font-size: 22rpx; color: #999; }

.card-progress {
  margin-top: 12rpx; padding: 12rpx 16rpx;
  background: #F0F8FF; border-radius: 8rpx;
  border-left: 4rpx solid #2196F3;
}

.progress-hint { font-size: 24rpx; color: #1565C0; }

.card-foot {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 12rpx; padding-top: 12rpx; border-top: 1px solid #F0F0F0;
}

.urgency-label {
  font-size: 22rpx; padding: 4rpx 14rpx; border-radius: 4rpx;

  &.urgency-urgent { background: #FFEBEE; color: #C62828; }
  &.urgency-normal { background: #FFF8E1; color: #F57F17; }
  &.urgency-low    { background: #E8F5E9; color: #2E7D32; }
}

.card-action { font-size: 24rpx; color: #D32223; font-weight: 500; }

.list-footer { text-align: center; padding: 32rpx; }

.footer-text { font-size: 24rpx; color: #ccc; }
</style>
