<!--
  时间轴组件 — 展示工单处理进度
  竖直排列的时间节点 + 连线动画
-->
<template>
  <view class="timeline">
    <view
      v-for="(item, index) in items"
      :key="index"
      class="tl-node"
      :class="{
        'tl-done': item.status === 'done' || index < currentActive,
        'tl-active': index === currentActive,
        'tl-waiting': index > currentActive
      }"
    >
      <!-- 时间轴左列：圆点 + 竖线 -->
      <view class="tl-line-col">
        <view class="tl-dot" :class="dotClass(index)">
          <text v-if="index < currentActive" class="dot-check">✓</text>
        </view>
        <view
          v-if="index < items.length - 1"
          class="tl-line"
          :class="{ 'line-done': index < currentActive }"
        ></view>
      </view>

      <!-- 时间轴右列：内容 -->
      <view class="tl-content">
        <text class="tl-time">{{ formatTime(item.time) }}</text>
        <text class="tl-text">{{ item.content }}</text>
        <text class="tl-desc" v-if="item.remark">{{ item.remark }}</text>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-if="!items || items.length === 0" class="tl-empty">
      <text class="empty-text">暂无进度记录</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  // 当前活跃节点索引（最新进度）
  currentActive: { type: Number, default: 0 }
})

const dotClass = (index) => {
  if (index < props.currentActive) return 'dot-done'
  if (index === props.currentActive) return 'dot-active'
  return 'dot-waiting'
}

const formatTime = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<style lang="scss" scoped>
.timeline {
  padding: 8rpx 0;
}

.tl-node {
  display: flex;
  min-height: 80rpx;
}

.tl-line-col {
  width: 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.tl-dot {
  width: 28rpx;
  height: 28rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s ease;
  z-index: 1;

  &.dot-done {
    background: #4CAF50;
    box-shadow: 0 0 0 4rpx rgba(76, 175, 80, 0.2);
  }

  &.dot-active {
    background: #D32223;
    box-shadow: 0 0 0 4rpx rgba(211, 34, 35, 0.2);
    animation: pulse 2s infinite;
  }

  &.dot-waiting {
    background: #DDDDDD;
  }
}

.dot-check {
  font-size: 16rpx;
  color: #FFFFFF;
  font-weight: 700;
}

.tl-line {
  width: 3rpx;
  flex: 1;
  min-height: 40rpx;
  background: #E0E0E0;
  transition: background 0.6s ease;

  &.line-done {
    background: #4CAF50;
  }
}

.tl-content {
  flex: 1;
  padding-left: 16rpx;
  padding-bottom: 28rpx;
  animation: fadeInLeft 0.4s ease;
}

.tl-time {
  font-size: 22rpx;
  color: #999;
  display: block;
  margin-bottom: 4rpx;
}

.tl-text {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  display: block;
}

.tl-desc {
  font-size: 24rpx;
  color: #666;
  margin-top: 4rpx;
  display: block;
}

.tl-empty {
  text-align: center;
  padding: 40rpx 0;
}

.empty-text {
  font-size: 26rpx;
  color: #ccc;
}

/* 活跃节点脉冲动画 */
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 4rpx rgba(211, 34, 35, 0.2); }
  50%      { box-shadow: 0 0 0 12rpx rgba(211, 34, 35, 0.08); }
}

@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-20rpx); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>
