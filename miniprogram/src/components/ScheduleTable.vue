<!--  周排期表组件 v3 — 五个时间段，与 CMS 保持一致  -->
<template>
  <view class="schedule-table">
    <!-- 周切换 -->
    <view class="week-switcher">
      <view class="week-btn" @click="$emit('prevWeek')">
        <SvgIcon name="caretLeft" :size="16" color="#334155" />
      </view>
      <text class="week-label">{{ weekRangeText }}</text>
      <view class="week-btn" @click="$emit('nextWeek')">
        <SvgIcon name="caretRight" :size="16" color="#334155" />
      </view>
    </view>

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

        <!-- 五个时间段 -->
        <view class="table-row" v-for="(slot, sIdx) in slots" :key="slot.key">
          <view class="time-cell">
            <text class="time-label">{{ slot.label }}</text>
            <text class="time-range">{{ slot.range }}</text>
          </view>
          <view
            v-for="(cell, idx) in scheduleGrid[sIdx]"
            :key="idx"
            class="data-cell"
            :class="cell.occupied ? 'cell-occupied' : 'cell-free'"
          >
            <text v-if="cell.occupied" class="cell-order-no">{{ cell.orderNo || '有工单' }}</text>
            <text v-else class="cell-free-text">空闲</text>
            <text v-if="cell.occupied && cell.company" class="cell-company text-ellipsis">{{ cell.company }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <view v-else class="table-empty">
      <text class="empty-text">暂无排期数据</text>
      <text class="empty-hint">选择工程师后可查看一周内的工单安排</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import SvgIcon from './SvgIcon.vue'

const props = defineProps({
  scheduleData: { type: Array, default: () => [] },
  weekStart: { type: String, default: '' }
})
defineEmits(['prevWeek', 'nextWeek'])

const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

// 五个时间段（与 CMS EngineerSchedule 一致）
const slots = [
  { key: 'AM1', label: '上午(早)', range: '08:30-10:00' },
  { key: 'AM2', label: '上午(晚)', range: '10:00-11:50' },
  { key: 'PM1', label: '下午(早)', range: '13:30-15:00' },
  { key: 'PM2', label: '下午(中)', range: '15:00-16:30' },
  { key: 'PM3', label: '下午(晚)', range: '16:30-18:00' },
]

// timeSlot → 行索引（兼容旧值）
const SLOT_ROWS = { AM1: 0, AM2: 1, PM1: 2, PM2: 3, PM3: 4 }
const legacyRow = (ts) => {
  if (ts === 'pm' || ts === '下午') return 2
  return 0
}

const dayHeaders = computed(() => {
  const start = new Date(props.weekStart || new Date())
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start); d.setDate(d.getDate() + i)
    const dateStr = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    return {
      weekday: weekdays[i],
      dateStr: `${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}`,
      date: dateStr,
      isToday: dateStr === todayStr
    }
  })
})

const weekRangeText = computed(() => {
  if (!props.weekStart) return ''
  const start = new Date(props.weekStart)
  const end = new Date(start); end.setDate(end.getDate() + 6)
  const fmt = d => `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}`
  return `${fmt(start)} - ${fmt(end)}`
})

const scheduleGrid = computed(() => {
  const grid = slots.map(() => Array.from({ length: 7 }, () => ({ occupied: false })))
  const start = new Date(props.weekStart || new Date())
  ;(props.scheduleData || []).forEach(entry => {
    const entryDate = entry.date || entry.scheduleDate || ''
    const d = new Date(entryDate)
    const dayIdx = Math.floor((d - start) / (1000*60*60*24))
    if (dayIdx < 0 || dayIdx > 6) return
    const ts = entry.timeSlot || entry.period || 'AM1'
    const rowIdx = SLOT_ROWS[ts] ?? legacyRow(ts)
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
  background: #fff;
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(2,6,23,0.05);
  border: 1px solid #F1F5F9;
}

.week-switcher {
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 12px;
}
.week-btn {
  width: 28px; height: 28px; border-radius: 50%;
  background: #F1F5F9; display: flex; align-items: center; justify-content: center;

  &:active { background: #E2E8F0; }
}
.week-label {
  font-size: 13px; color: #334155; font-weight: 600; margin: 0 12px;
}

.table-scroll { width: 100%; }
.table-wrapper { min-width: 360px; }
.table-row { display: flex; }
.table-header { border-bottom: 1px solid #F1F5F9; }

.header-cell {
  flex: 1; text-align: center; padding: 8px 4px;

  &.time-col { flex: 0 0 52px; font-size: 11px; color: #94A3B8; }

  &.is-today {
    background: #F0F9FF; border-radius: 6px;
    .day-label, .date-label { color: #0369A1; font-weight: 600; }
  }
}
.day-label  { font-size: 12px; color: #334155; display: block; }
.date-label { font-size: 11px; color: #94A3B8; display: block; margin-top: 1px; }

.time-cell {
  width: 52px; flex-shrink: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border-right: 1px solid #F1F5F9;
  padding: 2px;
}
.time-label { font-size: 11px; color: #64748B; font-weight: 500; }
.time-range { font-size: 9px; color: #94A3B8; margin-top: 1px; }

.data-cell {
  flex: 1; min-height: 52px; padding: 4px 3px; margin: 2px;
  border-radius: 6px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; transition: all 0.25s;
}
.cell-occupied { background: #FEF2F2; border: 1px solid #FECACA; }
.cell-free      { background: #F0FDF4; border: 1px solid #BBF7D0; }
.cell-order-no { font-size: 11px; color: #0F172A; font-weight: 600; font-family: monospace; }
.cell-company  { font-size: 10px; color: #64748B; margin-top: 1px; max-width: 100%; }
.cell-free-text { font-size: 11px; color: #16A34A; font-weight: 500; }

.table-empty { text-align: center; padding: 30px 0; }
.empty-text { font-size: 14px; color: #CBD5E1; display: block; }
.empty-hint { font-size: 12px; color: #E2E8F0; margin-top: 4px; }
</style>
