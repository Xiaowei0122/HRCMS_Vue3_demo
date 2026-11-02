<!--
  工程师排期 · 周视图日历（重新设计版）
  时间段列 + 7 天列；空闲/占用着色；点击日期选中该列；图例
-->
<template>
  <view class="cal-card">
    <!-- 周切换 -->
    <view class="cal-nav">
      <view class="cal-nav-btn" @click="$emit('prevWeek')">
        <SvgIcon name="caretLeft" :size="16" color="#4E5969" />
      </view>
      <text class="cal-nav-title">{{ weekRangeText }}</text>
      <view class="cal-today-btn" @click="$emit('goToday')">今天</view>
      <view class="cal-nav-btn" @click="$emit('nextWeek')">
        <SvgIcon name="caretRight" :size="16" color="#4E5969" />
      </view>
    </view>

    <!-- 网格：时间段列 + 7 天列 -->
    <view class="cal-grid">
      <view class="cal-corner" />
      <view
        v-for="d in dayHeaders"
        :key="d.date"
        class="cal-day-head"
        :class="{ today: d.isToday, selected: d.date === selectedDate }"
        @click="$emit('selectDate', d.date)"
      >
        <text class="cal-week">{{ d.weekday }}</text>
        <text class="cal-date">{{ d.dateNum }}</text>
      </view>

      <template v-for="(slot, sIdx) in slots" :key="slot.key">
        <view class="cal-time-label">
          <text class="cal-period">{{ slot.label }}</text>
          <text class="cal-range">{{ slot.range }}</text>
        </view>
        <view
          v-for="(cell, idx) in grid[sIdx]"
          :key="idx"
          class="cal-cell"
          :class="[cell.occupied ? 'busy' : 'free', idx === selectedDayIdx ? 'sel-col' : '', cell.past ? 'past' : '']"
        >
          <template v-if="cell.occupied">
            <text class="cal-customer" :class="{ cont: cell.continuation }">{{ cell.label || '已占用' }}</text>
            <text v-if="cell.status && cell.status !== 'lock'" class="cal-cell-status" :class="'st-' + statusKey(cell.status)">{{ cell.status }}</text>
          </template>
          <text v-else-if="cell.past" class="cal-free-text past">已过</text>
          <text v-else class="cal-free-text">空闲</text>
        </view>
      </template>
    </view>

    <!-- 图例 -->
    <view class="cal-legend">
      <view class="legend-item">
        <view class="legend-dot free" />
        <text>空闲可约</text>
      </view>
      <view class="legend-item">
        <view class="legend-dot busy" />
        <text>已占用</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import SvgIcon from './SvgIcon.vue'
import { TIME_SLOTS, statusKey } from '@/utils/repair-status'

const props = defineProps({
  scheduleData: { type: Array, default: () => [] },
  weekStart: { type: String, default: '' },
  selectedDate: { type: String, default: '' }
})
defineEmits(['prevWeek', 'nextWeek', 'goToday', 'selectDate'])

const slots = TIME_SLOTS
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const SLOT_ROWS = { AM1: 0, AM2: 1, PM1: 2, PM2: 3, PM3: 4 }
const LOCK_TYPE_LABELS = { training: '培训', onsite: '驻场', leave: '请假', other: '其他' }

const pad = (n) => String(n).padStart(2, '0')
const fmtDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

const dayHeaders = computed(() => {
  const start = parseLocal(props.weekStart) || new Date()
  const todayStr = fmtDate(new Date())
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    const date = fmtDate(d)
    return {
      weekday: weekdays[i],
      dateNum: String(d.getDate()).padStart(2, '0'),
      date,
      isToday: date === todayStr
    }
  })
})

const selectedDayIdx = computed(() => dayHeaders.value.findIndex((d) => d.date === props.selectedDate))

const weekRangeText = computed(() => {
  if (!props.weekStart) return ''
  const start = parseLocal(props.weekStart)
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  return `${fmtDate(start).replace(/-/g, '/')} - ${fmtDate(end).replace(/-/g, '/')}`
})

function parseLocal(s) {
  if (!s) return null
  const m = String(s).match(/(\d{4})-(\d{1,2})-(\d{1,2})/)
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : null
}

const addDays = (d, n) => { const nd = new Date(d); nd.setDate(nd.getDate() + n); return nd }

// 时段结束时间（分钟）：8:30-10:00 → 10:00 后不可约
const slotEndMinutes = (key) => {
  const s = TIME_SLOTS.find((x) => x.key === key)
  const end = (s?.range || '').split('-')[1]
  if (!end) return 24 * 60
  const [h, m] = end.split(':').map(Number)
  return h * 60 + m
}
const isPastSlot = (dateStr, key, now) => {
  const d = parseLocal(dateStr)
  if (!d) return false
  const min = slotEndMinutes(key)
  d.setHours(Math.floor(min / 60), min % 60, 0, 0)
  return d <= now
}

const grid = computed(() => {
  const g = slots.map(() => Array.from({ length: 7 }, () => ({ occupied: false, label: '', status: '', past: false })))
  const start = parseLocal(props.weekStart)
  if (!start) return g
  const now = new Date()
  ;(props.scheduleData || []).forEach((entry) => {
    const entryDate = entry.date || entry.scheduleDate || ''
    const d = parseLocal(entryDate)
    if (!d) return
    const dayIdx = Math.round((d - start) / (1000 * 60 * 60 * 24))
    if (dayIdx < 0 || dayIdx > 6) return
    const ts = entry.timeSlot || entry.period || 'AM1'
    const rowIdx = SLOT_ROWS[ts] ?? 0
    // 一单可占连续多格（slotSpan），向下覆盖，与 CMS 矩阵按块展示保持一致
    const span = Math.max(1, Number(entry.slotSpan) || 1)
    const isLock = entry.status === '已锁定'
    const label = isLock
      ? (LOCK_TYPE_LABELS[entry.type] || entry.type || '锁定')
      : (entry.company || entry.orderNo || '已占用')
    const status = isLock ? 'lock' : (entry.repairStatus || entry.status || '')
    for (let k = 0; k < span; k++) {
      const r = rowIdx + k
      if (r >= slots.length) break
      g[r][dayIdx] = {
        occupied: true,
        label: k === 0 ? label : '↕',
        status: k === 0 ? status : '',
        continuation: k > 0,
      }
    }
  })
  // 标记已过时段（不可约）
  for (let r = 0; r < slots.length; r++) {
    for (let c = 0; c < 7; c++) {
      const date = fmtDate(addDays(start, c))
      g[r][c].past = isPastSlot(date, slots[r].key, now)
    }
  }
  return g
})
</script>

<style lang="scss" scoped>
.cal-card {
  background: #fff;
  border-radius: 32rpx;
  padding: 32rpx 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.05);
}

.cal-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28rpx;
  padding: 0 8rpx;
}
.cal-nav-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: #F2F3F5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  &:active { background: #E8F3FF; }
}
.cal-nav-title { font-size: 30rpx; font-weight: 700; color: #1D2129; margin: 0 16rpx; flex: 1; text-align: center; }
.cal-today-btn {
  font-size: 24rpx;
  color: #165DFF;
  padding: 10rpx 20rpx;
  background: #E8F3FF;
  border-radius: 12rpx;
  font-weight: 500;
  flex-shrink: 0;
  &:active { opacity: 0.8; }
}

.cal-grid {
  display: grid;
  grid-template-columns: 88rpx repeat(7, 1fr);
  gap: 6rpx;
}
.cal-corner {}

.cal-day-head {
  text-align: center;
  padding-bottom: 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 8rpx;
  &.selected { background: #E8F3FF; border-radius: 8rpx 8rpx 0 0; }
  &.today .cal-date {
    color: #fff;
    background: linear-gradient(135deg, #165DFF, #4080FF);
    width: 48rpx;
    height: 48rpx;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-top: 4rpx;
  }
}
.cal-week { font-size: 22rpx; color: #86909C; font-weight: 500; }
.cal-day-head.today .cal-week { color: #165DFF; }
.cal-day-head.selected .cal-week { color: #165DFF; font-weight: 700; }
.cal-date { font-size: 26rpx; color: #1D2129; font-weight: 600; margin-top: 4rpx; }

.cal-time-label {
  font-size: 18rpx;
  color: #86909C;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  line-height: 1.2;
  font-weight: 500;
}
.cal-period { font-size: 20rpx; color: #4E5969; font-weight: 600; margin-bottom: 2rpx; }
.cal-range { font-size: 16rpx; color: #C9CDD4; }

.cal-cell {
  height: 76rpx;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
  position: relative;
  padding: 0 4rpx;
  overflow: hidden;
}
.cal-cell.free { background: #F0FAF1; border: 1rpx solid #D4EDDA; }
.cal-cell.busy { background: #FFF1F0; border: 1rpx solid #FFCCC7; }
.cal-cell.sel-col { box-shadow: 0 0 0 2px #165DFF; }
.cal-cell.past { background: #F2F3F5; border: 1rpx solid #E5E6EB; }
.cal-free-text { font-size: 20rpx; color: #00B42A; font-weight: 600; }
.cal-free-text.past { color: #C9CDD4; }
.cal-customer {
  font-size: 18rpx;
  color: #F53F3F;
  font-weight: 600;
  line-height: 1.1;
  text-align: center;
  max-width: 100%;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  &.cont { color: #FFB3AD; font-weight: 500; }
}
.cal-cell-status {
  font-size: 16rpx;
  font-weight: 600;
  line-height: 1;
  margin-top: 2rpx;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;

  &.st-pending    { color: #FF7D00; }
  &.st-reserved   { color: #FF7D00; }
  &.st-processing { color: #165DFF; }
  &.st-confirming { color: #722ED1; }
  &.st-archived   { color: #86909C; }
  &.st-done       { color: #00B42A; }
  &.st-cancelled  { color: #86909C; }
}

.cal-legend {
  display: flex;
  justify-content: center;
  gap: 40rpx;
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #F2F3F5;
}
.legend-item { display: flex; align-items: center; gap: 10rpx; font-size: 22rpx; color: #86909C; }
.legend-dot { width: 24rpx; height: 24rpx; border-radius: 6rpx; }
.legend-dot.free { background: #F0FAF1; border: 1rpx solid #D4EDDA; }
.legend-dot.busy { background: #FFF1F0; border: 1rpx solid #FFCCC7; }
</style>
