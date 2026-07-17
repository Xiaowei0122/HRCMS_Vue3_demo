<!--
  课程表式周排期组件
  横向：周一 ~ 周日
  纵向：上午 / 下午
  每个格子显示工单或"空闲"
-->
<template>
  <view class="schedule-table">
    <!-- 周切换 -->
    <view class="week-switcher">
      <view class="week-btn" @click="$emit('prevWeek')">◀</view>
      <text class="week-label">{{ weekRangeText }}</text>
      <view class="week-btn" @click="$emit('nextWeek')">▶</view>
    </view>

    <!-- 表格 -->
    <scroll-view scroll-x class="table-scroll" v-if="scheduleGrid.length > 0">
      <view class="table-wrapper">
        <!-- 表头 -->
        <view class="table-row table-header">
          <view class="header-cell time-col">时段</view>
          <view
            v-for="day in dayHeaders"
            :key="day.date"
            class="header-cell"
            :class="{ 'is-today': day.isToday }"
          >
            <text class="day-label">{{ day.weekday }}</text>
            <text class="date-label">{{ day.dateStr }}</text>
          </view>
        </view>

        <!-- 上午 -->
        <view class="table-row">
          <view class="time-cell">上午</view>
          <view
            v-for="(slot, idx) in scheduleGrid[0]"
            :key="idx"
            class="data-cell"
            :class="slot.occupied ? 'cell-occupied' : 'cell-free'"
          >
            <text v-if="slot.occupied" class="cell-order-no">{{ slot.orderNo || '有工单' }}</text>
            <text v-else class="cell-free-text">空闲</text>
            <text v-if="slot.occupied && slot.company" class="cell-company text-ellipsis">
              {{ slot.company }}
            </text>
          </view>
        </view>

        <!-- 下午 -->
        <view class="table-row">
          <view class="time-cell">下午</view>
          <view
            v-for="(slot, idx) in scheduleGrid[1]"
            :key="idx"
            class="data-cell"
            :class="slot.occupied ? 'cell-occupied' : 'cell-free'"
          >
            <text v-if="slot.occupied" class="cell-order-no">{{ slot.orderNo || '有工单' }}</text>
            <text v-else class="cell-free-text">空闲</text>
            <text v-if="slot.occupied && slot.company" class="cell-company text-ellipsis">
              {{ slot.company }}
            </text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 无数据 -->
    <view v-else class="table-empty">
      <text class="empty-text">暂无排期数据</text>
      <text class="empty-hint">选择工程师后可查看一周内的工单安排</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  scheduleData: { type: Array, default: () => [] },
  weekStart: { type: String, default: '' }
})

defineEmits(['prevWeek', 'nextWeek'])

const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

// 生成 7 天表头
const dayHeaders = computed(() => {
  const start = new Date(props.weekStart || new Date())
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return {
      weekday: weekdays[i],
      dateStr: `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`,
      date: dateStr,
      isToday: dateStr === todayStr
    }
  })
})

const weekRangeText = computed(() => {
  if (!props.weekStart) return ''
  const start = new Date(props.weekStart)
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  const fmt = d => `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
  return `${fmt(start)} - ${fmt(end)}`
})

// 生成 2行 x 7列 的排期网格
const scheduleGrid = computed(() => {
  const grid = [
    Array.from({ length: 7 }, () => ({ occupied: false })),
    Array.from({ length: 7 }, () => ({ occupied: false }))
  ]

  const start = new Date(props.weekStart || new Date())
  const schedule = props.scheduleData || []

  schedule.forEach(entry => {
    const entryDate = entry.date || entry.scheduleDate || ''
    const d = new Date(entryDate)
    const dayIdx = Math.floor((d - start) / (1000 * 60 * 60 * 24))
    if (dayIdx < 0 || dayIdx > 6) return

    const period = entry.period || entry.timeSlot || 'am' // am / pm
    const rowIdx = period === 'pm' ? 1 : 0

    grid[rowIdx][dayIdx] = {
      occupied: true,
      orderNo: entry.orderNo,
      company: entry.company,
      repairId: entry.repairId || entry._id
    }
  })

  return grid
})
</script>

<style lang="scss" scoped>
.schedule-table {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
}

.week-switcher {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.week-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F7F7F7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #666;

  &:active { background: #E8E8E8; }
}

.week-label {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  margin: 0 24rpx;
}

.table-scroll {
  width: 100%;
}

.table-wrapper {
  min-width: 700rpx;
}

.table-row {
  display: flex;
}

.table-header {
  border-bottom: 2rpx solid #F0F0F0;
}

.header-cell {
  flex: 1;
  text-align: center;
  padding: 12rpx 8rpx;

  &.time-col {
    flex: 0 0 80rpx;
    font-size: 22rpx;
    color: #999;
  }

  &.is-today {
    background: #FFF0F0;
    border-radius: 8rpx;

    .day-label, .date-label { color: #D32223; font-weight: 600; }
  }
}

.day-label  { font-size: 24rpx; color: #333; display: block; }
.date-label { font-size: 22rpx; color: #999; display: block; margin-top: 2rpx; }

.time-cell {
  width: 80rpx;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #666;
  font-weight: 500;
  border-right: 2rpx solid #F0F0F0;
}

.data-cell {
  flex: 1;
  min-height: 100rpx;
  padding: 8rpx 6rpx;
  margin: 4rpx;
  border-radius: 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.cell-occupied {
  background: #FFF0F0;
  border: 1px solid #FFCDD2;
}

.cell-free {
  background: #F5FFF5;
  border: 1px solid #C8E6C9;
}

.cell-order-no {
  font-size: 22rpx;
  color: #D32223;
  font-weight: 600;
  font-family: monospace;
}

.cell-company {
  font-size: 20rpx;
  color: #666;
  margin-top: 2rpx;
  max-width: 100%;
}

.cell-free-text {
  font-size: 22rpx;
  color: #4CAF50;
  font-weight: 500;
}

.table-empty {
  text-align: center;
  padding: 60rpx 0;
}

.empty-text { font-size: 28rpx; color: #ccc; display: block; }
.empty-hint { font-size: 24rpx; color: #ddd; margin-top: 8rpx; }
</style>
