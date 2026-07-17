<!--
  工单卡片组件 — 用于工单列表中的纵向卡片展示
-->
<template>
  <view class="order-card" @click="$emit('click', order)">
    <!-- 卡片头部 -->
    <view class="card-head">
      <view class="card-engineer" v-if="order.engineerName">
        <text class="eng-icon">👨‍🔧</text>
        <text class="eng-name">{{ order.engineerName }}</text>
      </view>
      <view class="card-date">
        <text class="date-text">{{ formatDate(order.createTime || order.assignTime) }}</text>
      </view>
    </view>

    <!-- 卡片主体 -->
    <view class="card-body">
      <text class="card-company text-ellipsis">{{ order.company || '未填写单位' }}</text>
      <text class="card-desc text-ellipsis-2" v-if="order.description">
        {{ order.description }}
      </text>
    </view>

    <!-- 卡片底部 -->
    <view class="card-foot">
      <view class="foot-left">
        <text class="status-badge" :class="'badge-' + (order.status || 'pending')">
          {{ statusMap[order.status] || '待处理' }}
        </text>
        <text class="urgency-badge" :class="'urgency-' + (order.urgency || 'normal')">
          {{ urgencyMap[order.urgency] || '一般' }}
        </text>
      </view>
      <text class="foot-arrow">→</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  order: { type: Object, default: () => ({}) }
})

defineEmits(['click'])

const statusMap = { pending: '待处理', processing: '处理中', done: '已完成' }
const urgencyMap = { urgent: '紧急', normal: '一般', low: '不急' }

const formatDate = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
</script>

<style lang="scss" scoped>
.order-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
  transition: all 0.3s;

  &:active {
    transform: scale(0.98);
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
  }
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.card-engineer {
  display: flex;
  align-items: center;
}

.eng-icon { font-size: 28rpx; margin-right: 6rpx; }
.eng-name { font-size: 26rpx; color: #333; font-weight: 500; }

.date-text { font-size: 22rpx; color: #999; }

.card-company {
  font-size: 30rpx;
  font-weight: 700;
  color: #222;
  display: block;
  margin-bottom: 6rpx;
}

.card-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
}

.card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12rpx;
  padding-top: 12rpx;
  border-top: 1px solid #F0F0F0;
}

.foot-left {
  display: flex;
  gap: 8rpx;
}

.status-badge {
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 20rpx;

  &.badge-pending    { background: #FFF3E0; color: #E65100; }
  &.badge-processing { background: #E3F2FD; color: #1565C0; }
  &.badge-done       { background: #E8F5E9; color: #2E7D32; }
}

.urgency-badge {
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 4rpx;

  &.urgency-urgent { background: #FFEBEE; color: #C62828; }
  &.urgency-normal { background: #FFF8E1; color: #F57F17; }
  &.urgency-low    { background: #E8F5E9; color: #2E7D32; }
}

.foot-arrow {
  font-size: 28rpx;
  color: #D32223;
}
</style>
