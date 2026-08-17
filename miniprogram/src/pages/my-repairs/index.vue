<!--
  我的报修
-->
<template>
  <view class="page">
    <!-- 状态筛选 -->
    <view class="filter-bar">
      <view v-for="t in statusTabs" :key="t.value" class="f-tab" :class="{ on: currentStatus === t.value }" @click="switchFilter(t.value)">{{ t.label }}</view>
    </view>

    <scroll-view scroll-y class="scroll-body" :refresher-enabled="true" :refresher-triggered="refreshing" @refresherrefresh="onRefresh" @scrolltolower="onLoadMore">
      <view v-if="list.length" class="order-list">
        <view v-for="item in list" :key="item._id || item.id" class="order-card" @click="goDetail(item)">
          <view class="card-top">
            <view class="no-box"><text class="no-label">工单</text><text class="no-val">{{ item.orderNo }}</text></view>
            <view class="o-status" :class="'os-' + statusKey(item.status)">{{ item.status || '待接单' }}</view>
          </view>
          <view class="card-body">
            <view class="info-row"><text class="i-label">报修单位</text><text class="i-val ellipsis">{{ item.company }}</text></view>
            <view class="info-row"><text class="i-label">设备类型</text><text class="i-val">{{ item.deviceType || '未指定' }}</text></view>
            <view class="info-row"><text class="i-label">紧急程度</text><text class="u-tag" :class="'u-' + priorityKey(item.priority)">{{ item.priority || '普通' }}</text></view>
            <view class="info-row"><text class="i-label">报修时间</text><text class="i-val">{{ fmt(item.createTime || item.repairDate) }}</text></view>
          </view>
          <view class="card-foot">
            <view class="eng-info" v-if="item.engineer"><SvgIcon name="hardHat" :size="14" /><text>{{ item.engineer }}</text></view>
            <view class="eng-info wait" v-else><SvgIcon name="clock" :size="14" /><text>等待接单</text></view>
            <view class="arrow"><text>详情</text><SvgIcon name="caretRight" :size="12" /></view>
          </view>
        </view>
      </view>
      <EmptyState v-else icon="clipboard" text="暂无报修记录" sub-text="提交报修后，工单将显示在这里" />
      <view v-if="list.length" class="foot-msg"><text>{{ noMore ? '— 没有更多了 —' : '加载中...' }}</text></view>
    </scroll-view>

    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRepairStore } from '@/stores/repair'
import SvgIcon from '@/components/SvgIcon.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import { STATUS, statusKey, priorityKey } from '@/utils/repair-status'

const repairStore = useRepairStore()
const list = ref([])
const refreshing = ref(false)
const currentStatus = ref('')
const page = ref(1)
const noMore = ref(false)

const statusTabs = [
  { label: '全部', value: '' },
  { label: '待接单', value: STATUS.PENDING },
  { label: '处理中', value: STATUS.PROCESSING },
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

onMounted(() => { loadList() })
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F8FAFC; display: flex; flex-direction: column; }

.filter-bar { display: flex; background: #fff; padding: 16rpx 24rpx; gap: 12rpx; flex-shrink: 0; }
.f-tab { flex: 1; text-align: center; padding: 12rpx 0; font-size: 26rpx; color: #64748B; background: #F1F5F9; border-radius: 8rpx; transition: all .25s; }
.f-tab.on { background: #0F172A; color: #fff; font-weight: 600; }

.scroll-body { flex: 1; }
.order-list { padding: 16rpx 24rpx; }
.order-card { background: #fff; border-radius: 14rpx; padding: 24rpx; margin-bottom: 16rpx; box-shadow: 0 2rpx 12rpx rgba(15,23,42,.06); transition: all .25s; }
.order-card:active { transform: scale(.98); }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.no-label { font-size: 22rpx; color: #64748B; margin-right: 8rpx; }
.no-val { font-size: 24rpx; color: #334155; font-weight: 500; font-family: monospace; }
.o-status { font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 20rpx; font-weight: 500; }
.os-pending { background: #FEF3C7; color: #D97706; }
.os-processing { background: #E0F2FE; color: #0369A1; }
.os-done { background: #DCFCE7; color: #16A34A; }

.card-body { padding: 8rpx 0; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 8rpx 0; }
.i-label { font-size: 26rpx; color: #64748B; }
.i-val { font-size: 26rpx; color: #334155; max-width: 400rpx; text-align: right; }
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.u-tag { font-size: 22rpx; padding: 2rpx 12rpx; border-radius: 4rpx; }
.u-urgent { background: #FEE2E2; color: #DC2626; }
.u-normal { background: #FEF3C7; color: #D97706; }
.u-low { background: #DCFCE7; color: #16A34A; }

.card-foot { display: flex; justify-content: space-between; align-items: center; padding-top: 12rpx; border-top: 1px solid #E2E8F0; }
.eng-info { display: flex; align-items: center; gap: 4rpx; font-size: 24rpx; color: #334155; }
.eng-info.wait { color: #D97706; }
.arrow { display: flex; align-items: center; gap: 4rpx; font-size: 22rpx; color: #0369A1; }

.foot-msg { text-align: center; padding: 32rpx; font-size: 24rpx; color: #94A3B8; }
</style>
