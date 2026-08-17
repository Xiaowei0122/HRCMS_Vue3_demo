<!--  工单卡片组件 v2 — 企业级设计  -->
<template>
  <view class="order-card" @click="$emit('click', order)">
    <!-- 头部：工程师 + 日期 -->
    <view class="card-head">
      <view class="card-engineer" v-if="order.engineer">
        <SvgIcon name="hardHat" :size="16" color="#64748B" />
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
      <SvgIcon name="caretRight" :size="16" color="#0369A1" />
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
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(2,6,23,0.05);
  transition: all 0.25s ease;
  border: 1px solid #F1F5F9;

  &:active {
    transform: scale(0.985);
    box-shadow: 0 4px 12px rgba(2,6,23,0.08);
  }
}

.card-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px;
}
.card-engineer { display: flex; align-items: center; gap: 4px; }
.eng-name { font-size: 13px; color: #334155; font-weight: 500; }
.date-text { font-size: 11px; color: #94A3B8; }

.card-company {
  font-size: 15px; font-weight: 700; color: #020617;
  display: block; margin-bottom: 4px;
}
.card-desc {
  font-size: 13px; color: #64748B; line-height: 1.5;
}

.card-foot {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 10px; padding-top: 10px;
  border-top: 1px solid #F1F5F9;
}
.foot-left { display: flex; gap: 6px; }

.status-badge {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; padding: 3px 10px; border-radius: 10px; font-weight: 600;

  &.badge-pending    { background: #FEF3C7; color: #92400E; }
  &.badge-processing { background: #E0F2FE; color: #075985; }
  &.badge-done       { background: #DCFCE7; color: #166534; }
}
.status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  &.dot-pending    { background: #D97706; }
  &.dot-processing { background: #0369A1; }
  &.dot-done       { background: #16A34A; }
}

.urgency-badge {
  font-size: 11px; padding: 3px 10px; border-radius: 4px; font-weight: 600;

  &.urgency-urgent { background: #FEE2E2; color: #991B1B; }
  &.urgency-normal { background: #FEF3C7; color: #92400E; }
  &.urgency-low    { background: #DCFCE7; color: #166534; }
}
</style>
