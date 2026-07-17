<!--
  我的报修页面
  用户查看自己的报修记录列表，按时间排序
-->
<template>
  <view class="my-repairs-page">
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

    <!-- 工单列表 -->
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
          <!-- 卡片头部 -->
          <view class="card-top">
            <view class="order-no">
              <text class="no-label">工单号</text>
              <text class="no-value">{{ item.orderNo }}</text>
            </view>
            <view class="order-status" :class="'status-' + (item.status || 'pending')">
              {{ statusMap[item.status] || '待处理' }}
            </view>
          </view>

          <!-- 卡片内容 -->
          <view class="card-body">
            <view class="info-row">
              <text class="info-label">报修单位</text>
              <text class="info-value text-ellipsis">{{ item.company }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">设备类型</text>
              <text class="info-value">{{ item.deviceType || '未指定' }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">紧急程度</text>
              <text class="urgency-tag" :class="'urgency-' + (item.urgency || 'normal')">
                {{ urgencyMap[item.urgency] || '一般' }}
              </text>
            </view>
            <view class="info-row">
              <text class="info-label">报修时间</text>
              <text class="info-value">{{ formatTime(item.createTime || item.repairDate) }}</text>
            </view>
          </view>

          <!-- 卡片底部 -->
          <view class="card-foot">
            <text class="engineer-info" v-if="item.engineerName">
              👨‍🔧 {{ item.engineerName }}
            </text>
            <text class="engineer-info empty" v-else>⏳ 等待接单</text>
            <view class="arrow">查看详情 →</view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <EmptyState
        v-else
        icon="📋"
        text="暂无报修记录"
        sub-text="提交报修后，工单将显示在这里"
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
const currentStatus = ref('')
const page = ref(1)
const noMore = ref(false)

const statusTabs = [
  { label: '全部', value: '' },
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'done' }
]

const statusMap = { pending: '待处理', processing: '处理中', done: '已完成' }
const urgencyMap = { urgent: '紧急', normal: '一般', low: '不急' }

const switchTab = (val) => {
  currentStatus.value = val
  page.value = 1
  noMore.value = false
  loadList()
}

const loadList = async () => {
  try {
    const data = await repairStore.fetchMyRepairs({
      status: currentStatus.value || undefined,
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
  } catch {
    // request.js 已处理
  }
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

const formatTime = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(() => {
  loadList()
})
</script>

<style lang="scss" scoped>
.my-repairs-page {
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

.list-scroll {
  flex: 1;
}

.order-list {
  padding: 16rpx 24rpx;
}

.order-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
  transition: all 0.3s;

  &:active {
    transform: scale(0.98);
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
  }
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.no-label {
  font-size: 22rpx;
  color: #999;
  margin-right: 8rpx;
}

.no-value {
  font-size: 24rpx;
  color: #333;
  font-weight: 500;
  font-family: monospace;
}

.order-status {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;

  &.status-pending    { background: #FFF3E0; color: #E65100; }
  &.status-processing { background: #E3F2FD; color: #1565C0; }
  &.status-done       { background: #E8F5E9; color: #2E7D32; }
}

.card-body {
  padding: 16rpx 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8rpx 0;
}

.info-label {
  font-size: 26rpx;
  color: #999;
}

.info-value {
  font-size: 26rpx;
  color: #333;
  max-width: 400rpx;
  text-align: right;
}

.urgency-tag {
  font-size: 22rpx;
  padding: 2rpx 12rpx;
  border-radius: 4rpx;

  &.urgency-urgent { background: #FFEBEE; color: #C62828; }
  &.urgency-normal { background: #FFF8E1; color: #F57F17; }
  &.urgency-low    { background: #E8F5E9; color: #2E7D32; }
}

.card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12rpx;
  border-top: 1px solid #F0F0F0;
}

.engineer-info {
  font-size: 24rpx;
  color: #666;

  &.empty { color: #F57F17; }
}

.arrow {
  font-size: 24rpx;
  color: #D32223;
}

.list-footer {
  text-align: center;
  padding: 32rpx;
}

.footer-text {
  font-size: 24rpx;
  color: #ccc;
}
</style>
