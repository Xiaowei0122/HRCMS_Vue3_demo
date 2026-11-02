<!--  工单卡片组件 v3 — 蓝色主题 / rpx 移动适配  -->
<template>
  <view class="order-card" @click="$emit('click', order)">
    <!-- 头部：工程师 + 日期 -->
    <view class="card-head">
      <view class="card-engineer" v-if="order.engineer">
        <SvgIcon name="hardHat" :size="28" color="#86909C" />
        <text class="eng-name">{{ order.engineer }}</text>
      </view>
      <view v-else />
      <text class="date-text">{{ formatDate(order.createTime || order.assignTime) }}</text>
    </view>

    <!-- 主体 -->
    <view class="card-body">
      <text class="card-company text-ellipsis">{{ order.company || '未填写单位' }}</text>
      <text class="card-desc text-ellipsis-2" v-if="order.description">{{ order.description }}</text>
    </view>

    <!-- 底部：状态 + 紧急程度 + 箭头 -->
    <view class="card-foot">
      <view class="foot-left">
        <view class="status-badge" :class="'badge-' + statusKey(order.status)">
          <view class="status-dot" :class="'dot-' + statusKey(order.status)" />
          {{ order.status || '待接单' }}
        </view>
        <view class="urgency-badge" :class="'urgency-' + priorityKey(order.priority)">
          {{ order.priority || '普通' }}
        </view>
      </view>
      <SvgIcon name="caretRight" :size="28" color="#165DFF" />
    </view>
  </view>
</template>

<script setup>
import SvgIcon from './SvgIcon.vue'
import { statusKey, priorityKey } from '@/utils/repair-status'

defineProps({ order: { type: Object, default: () => ({}) } })
defineEmits(['click'])

const formatDate = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
</script>

<style lang="scss" scoped>
.order-card {
  background: #fff;
  border-radius: 32rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;

  &:active {
    transform: scale(0.985);
    box-shadow: 0 8rpx 32rpx rgba(22, 93, 255, 0.08);
  }
}

.card-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12rpx;
}
.card-engineer { display: flex; align-items: center; gap: 8rpx; }
.eng-name { font-size: 24rpx; color: #4E5969; font-weight: 500; }
.date-text { font-size: 22rpx; color: #86909C; }

.card-company {
  font-size: 30rpx; font-weight: 700; color: #1D2129;
  display: block; margin-bottom: 8rpx;
}
.card-desc {
  font-size: 26rpx; color: #4E5969; line-height: 1.5;
}

.card-foot {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 16rpx; padding-top: 16rpx;
  border-top: 1rpx solid #F2F3F5;
}
.foot-left { display: flex; gap: 12rpx; }

.status-badge {
  display: flex; align-items: center; gap: 8rpx;
  font-size: 22rpx; padding: 6rpx 20rpx; border-radius: 20rpx; font-weight: 600;

  &.badge-pending    { background: #FFF3E8; color: #FF7D00; }
  &.badge-reserved   { background: #FFF3E8; color: #FF7D00; }
  &.badge-processing { background: #E8F3FF; color: #165DFF; }
  &.badge-done       { background: #E8FFEA; color: #00B42A; }
}
.status-dot {
  width: 10rpx; height: 10rpx; border-radius: 50%;
  &.dot-pending    { background: #FF7D00; }
  &.dot-reserved   { background: #FF7D00; }
  &.dot-processing { background: #165DFF; }
  &.dot-done       { background: #00B42A; }
}

.urgency-badge {
  font-size: 22rpx; padding: 6rpx 16rpx; border-radius: 8rpx; font-weight: 600;

  &.urgency-urgent { background: #FFECE8; color: #F53F3F; }
  &.urgency-normal { background: #FFF3E8; color: #FF7D00; }
  &.urgency-low    { background: #E8FFEA; color: #00B42A; }
}
</style>
