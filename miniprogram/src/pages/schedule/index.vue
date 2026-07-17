<!--
  工程师期排页面（仅特定用户 visible）
  子板块 1：课程表式周排期视图
  子板块 2：工单列表（纵向卡片）
-->
<template>
  <view class="schedule-page">
    <!-- 工程师选择器 -->
    <view class="engineer-selector">
      <text class="sel-label">选择工程师：</text>
      <select class="sel-picker" @change="onEngineerChange">
        <option value="" disabled selected v-if="!currentEngineer">请选择</option>
        <option v-for="(name, idx) in engineerNames" :key="name" :value="idx">{{ name }}</option>
      </select>
    </view>

    <!-- 子板块切换 -->
    <view class="sub-tabs">
      <view
        class="sub-tab"
        :class="{ active: activeTab === 'calendar' }"
        @click="activeTab = 'calendar'"
      >
        📅 周排期
      </view>
      <view
        class="sub-tab"
        :class="{ active: activeTab === 'list' }"
        @click="activeTab = 'list'"
      >
        📋 工单列表
      </view>
    </view>

    <scroll-view scroll-y class="page-scroll">
      <!-- 课程表式周排期 -->
      <view v-if="activeTab === 'calendar'" class="calendar-view">
        <ScheduleTable
          :schedule-data="scheduleList"
          :week-start="weekStart"
          @prev-week="prevWeek"
          @next-week="nextWeek"
        />
      </view>

      <!-- 工单列表 -->
      <view v-else class="order-list-view">
        <OrderCard
          v-for="item in orderList"
          :key="item._id || item.id"
          :order="item"
          @click="goDetail(item)"
        />
        <EmptyState
          v-if="orderList.length === 0"
          icon="📋"
          text="暂无工单"
          sub-text="当前工程师暂无接单记录"
        />
      </view>
    </scroll-view>

    <!-- 自定义 TabBar -->
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRepairStore } from '@/stores/repair'
import CustomTabBar from '@/components/CustomTabBar.vue'
import ScheduleTable from '@/components/ScheduleTable.vue'
import OrderCard from '@/components/OrderCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const repairStore = useRepairStore()

const activeTab = ref('calendar')
const currentEngineer = ref('')
const selectedEngineerId = ref('')
const scheduleList = ref([])
const orderList = ref([])
const weekStart = ref(getMonday())

const engineerNames = computed(() => {
  return (repairStore.engineers || []).map(e => e.name || e.realName || '未知')
})

function getMonday(d = new Date()) {
  const day = d.getDay() || 7
  const monday = new Date(d)
  monday.setDate(d.getDate() - day + 1)
  return monday.toISOString().slice(0, 10)
}

const prevWeek = () => {
  const d = new Date(weekStart.value)
  d.setDate(d.getDate() - 7)
  weekStart.value = d.toISOString().slice(0, 10)
  loadSchedule()
}

const nextWeek = () => {
  const d = new Date(weekStart.value)
  d.setDate(d.getDate() + 7)
  weekStart.value = d.toISOString().slice(0, 10)
  loadSchedule()
}

const onEngineerChange = (e) => {
  const idx = parseInt(e.target.value)
  currentEngineer.value = engineerNames.value[idx]
  const eng = repairStore.engineers[idx]
  selectedEngineerId.value = eng?._id || eng?.id || ''
  loadSchedule()
  loadOrders()
}

const loadSchedule = async () => {
  try {
    const data = await repairStore.fetchSchedule({
      engineerId: selectedEngineerId.value,
      weekStart: weekStart.value
    })
    scheduleList.value = Array.isArray(data) ? data : []
  } catch { /* handled */ }
}

const loadOrders = async () => {
  try {
    // 拉取所有工单，过滤当前工程师的
    const all = await repairStore.fetchAllOrders({
      engineerId: selectedEngineerId.value
    })
    orderList.value = Array.isArray(all) ? all : (all?.list || [])
  } catch { /* handled */ }
}

const goDetail = (item) => {
  const id = item._id || item.id
  uni.navigateTo({ url: `/pages/repair-detail/index?id=${id}` })
}

const loadEngineers = async () => {
  await repairStore.fetchEngineers()
  if (repairStore.engineers.length > 0) {
    currentEngineer.value = repairStore.engineers[0].name || repairStore.engineers[0].realName
    selectedEngineerId.value = repairStore.engineers[0]._id || repairStore.engineers[0].id
    loadSchedule()
    loadOrders()
  }
}

// 切换周次时刷新排期
watch(activeTab, (val) => {
  if (val === 'calendar') loadSchedule()
  else loadOrders()
})

onMounted(() => {
  loadEngineers()
})
</script>

<style lang="scss" scoped>
.schedule-page {
  min-height: 100vh;
  background: #F7F7F7;
  display: flex;
  flex-direction: column;
  padding-bottom: 140rpx;
}

.engineer-selector {
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  background: #FFFFFF;
}

.sel-label {
  font-size: 26rpx;
  color: #333;
  margin-right: 16rpx;
}

.sel-picker {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64rpx;
  padding: 0 20rpx;
  background: #F7F7F7;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #333;
}

.sel-arrow {
  font-size: 20rpx;
  color: #999;
}

.sub-tabs {
  display: flex;
  background: #FFFFFF;
  padding: 8rpx 24rpx 16rpx;
  gap: 16rpx;
}

.sub-tab {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
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

.page-scroll {
  flex: 1;
}

.calendar-view {
  padding: 16rpx 24rpx;
}

.order-list-view {
  padding: 16rpx 24rpx;
}
</style>
