<!--
  移动端日期选择器（日历网格）— 替代小程序 <picker mode="date">
  props: modelValue(是否显示) / title(标题) / value(当前选中 YYYY-MM-DD)
  emits: update:modelValue / select(选中日期 YYYY-MM-DD)
-->
<template>
  <view v-if="modelValue" class="dp-overlay" @click="close">
    <view class="dp-card" @click.stop>
      <view class="dp-head">
        <text class="dp-title">{{ title }}</text>
        <view class="dp-close" @click="close">
          <SvgIcon name="x" :size="18" color="#86909C" />
        </view>
      </view>

      <!-- 年月切换 -->
      <view class="dp-nav">
        <view class="dp-nav-btn" @click="prevMonth">
          <SvgIcon name="caretLeft" :size="20" color="#4E5969" />
        </view>
        <text class="dp-nav-title">{{ viewYear }}年{{ viewMonth }}月</text>
        <view class="dp-nav-btn" @click="nextMonth">
          <SvgIcon name="caretRight" :size="20" color="#4E5969" />
        </view>
      </view>

      <!-- 星期 -->
      <view class="dp-week">
        <text v-for="w in weeks" :key="w" class="dp-week-item">{{ w }}</text>
      </view>

      <!-- 日期网格 -->
      <view class="dp-grid">
        <view
          v-for="(d, i) in days"
          :key="i"
          class="dp-day"
          :class="{ empty: !d.day, selected: d.selected, today: d.isToday, disabled: d.disabled }"
          @click="d.day && !d.disabled && pick(d)"
        >
          <text>{{ d.day }}</text>
        </view>
      </view>

      <!-- 底部快捷 -->
      <view class="dp-footer">
        <button class="dp-today" @click="pickToday">回到今天</button>
      </view>

      <view class="dp-safe" />
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import SvgIcon from './SvgIcon.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '选择日期' },
  value: { type: String, default: '' },
  // 禁止选择过去日期（预约日期场景）
  disablePast: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'select'])

const weeks = ['日', '一', '二', '三', '四', '五', '六']

const pad = (n) => String(n).padStart(2, '0')
const fmt = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const parseDate = (s) => {
  if (!s) return null
  const m = String(s).match(/(\d{4})-(\d{1,2})-(\d{1,2})/)
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : null
}
const daysInMonth = (y, m) => new Date(y, m, 0).getDate()

const today = new Date()
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth() + 1)

// 打开时视图定位到已选日期（或今天）
const initView = () => {
  const d = parseDate(props.value) || today
  viewYear.value = d.getFullYear()
  viewMonth.value = d.getMonth() + 1
}
watch(() => props.modelValue, (v) => { if (v) initView() })

const days = computed(() => {
  const startWeekday = new Date(viewYear.value, viewMonth.value - 1, 1).getDay() // 0=周日
  const total = daysInMonth(viewYear.value, viewMonth.value)
  const todayStr = fmt(today)
  const cells = []
  for (let i = 0; i < startWeekday; i++) cells.push({ day: '', date: '' })
  for (let d = 1; d <= total; d++) {
    const date = `${viewYear.value}-${pad(viewMonth.value)}-${pad(d)}`
    cells.push({
      day: d,
      date,
      isToday: date === todayStr,
      selected: date === props.value,
      disabled: props.disablePast && date < todayStr
    })
  }
  while (cells.length % 7 !== 0) cells.push({ day: '', date: '' })
  return cells
})

const prevMonth = () => {
  if (viewMonth.value === 1) { viewMonth.value = 12; viewYear.value-- }
  else viewMonth.value--
}
const nextMonth = () => {
  if (viewMonth.value === 12) { viewMonth.value = 1; viewYear.value++ }
  else viewMonth.value++
}

const pick = (d) => {
  if (d.disabled) return
  emit('select', d.date)
  emit('update:modelValue', false)
}
const pickToday = () => {
  emit('select', fmt(today))
  emit('update:modelValue', false)
}
const close = () => emit('update:modelValue', false)
</script>

<style lang="scss" scoped>
.dp-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}
.dp-card {
  width: 100%;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  overflow: hidden;
  padding: 0 32rpx;
  animation: dp-in 0.22s ease;
}
@keyframes dp-in {
  from { transform: translateY(40%); opacity: 0.6; }
  to { transform: translateY(0); opacity: 1; }
}

.dp-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 0 20rpx;
  border-bottom: 1rpx solid #F2F3F5;
}
.dp-title { font-size: 32rpx; font-weight: 700; color: #1D2129; }
.dp-close {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F2F3F5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dp-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 0 20rpx;
}
.dp-nav-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: #F7F8FA;
  display: flex;
  align-items: center;
  justify-content: center;
  &:active { background: #EEF0F3; }
}
.dp-nav-title { font-size: 30rpx; font-weight: 600; color: #1D2129; }

.dp-week {
  display: flex;
  padding-bottom: 12rpx;
}
.dp-week-item {
  flex: 1;
  text-align: center;
  font-size: 24rpx;
  color: #86909C;
}

.dp-grid { display: flex; flex-wrap: wrap; }
.dp-day {
  width: calc(100% / 7);
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #1D2129;
  border-radius: 16rpx;

  &.empty { pointer-events: none; }
  &.disabled { color: #C9CDD4; pointer-events: none; }
  &.today { color: #165DFF; font-weight: 600; }
  &.selected {
    background: linear-gradient(135deg, #165DFF, #4080FF);
    color: #fff;
    font-weight: 600;
    box-shadow: 0 4rpx 12rpx rgba(22, 93, 255, 0.3);
  }
  &:active { background: #F0F6FF; }
}

.dp-footer {
  padding: 20rpx 0 28rpx;
  display: flex;
  justify-content: center;
}
.dp-today {
  padding: 16rpx 48rpx;
  border-radius: 40rpx;
  background: #F2F3F5;
  color: #4E5969;
  font-size: 26rpx;
  border: none;
  &:active { opacity: 0.85; }
}

.dp-safe { height: env(safe-area-inset-bottom); }
</style>
