<!--
  接单弹窗（复用组件）— 一套组件覆盖两种接单场景，UI 相近：
    - 预约工单接单（mode="reserve"）：展示「用户已预约时段」卡片 + 确认接单 / 改派时间 / 退回工单 三态交互
    - 普通工单池接单（mode="normal"）：直接进入「选择日期/时段」视图（对应改派时间的 UI）
  props:
    modelValue(是否显示) / order(工单对象) / mode('auto'|'reserve'|'normal')
    confirming(确认中) / rejecting(退回中)
  emits:
    update:modelValue / confirm({date, timeSlot, reason}) / reject({reason})
-->
<template>
  <view v-if="modelValue" class="popup-overlay" @click="close">
    <view class="popup-card" @click.stop>
      <view class="modal-handle" />

      <!-- ── 视图一：接单确认（预约工单：预约时段卡片 + 三按钮）── -->
      <template v-if="view === 'summary'">
        <text class="popup-title">接单确认</text>
        <text class="popup-subtitle">请确认预约时段，或选择改派 / 退回</text>

        <view class="order-summary">
          <view class="order-summary-icon">
            <SvgIcon name="wrench" :size="22" color="#FF7D00" />
          </view>
          <view class="order-summary-info">
            <text class="order-summary-name ellipsis">{{ summaryName }}</text>
            <view class="order-summary-desc">
              <text>{{ order.contact || '—' }}</text>
              <text class="order-summary-urgent">{{ order.priority || '普通' }}</text>
            </view>
          </view>
        </view>

        <view class="appointment-card">
          <view class="appointment-label">
            <SvgIcon name="clock" :size="14" color="#165DFF" />
            <text>用户已预约时段</text>
          </view>
          <view class="appointment-time">
            <view class="appointment-date">
              <text class="appointment-date-day">{{ reservedDateDay }}</text>
              <text class="appointment-date-week">{{ reservedDateWeek }}</text>
            </view>
            <view class="appointment-divider" />
            <view class="appointment-detail">
              <text class="appointment-period">{{ reservedSlotInfo?.label || reservedSlot }}</text>
              <view class="appointment-range">
                <SvgIcon name="clock" :size="13" color="#86909C" />
                <text>{{ reservedSlotInfo?.range || '' }}</text>
              </view>
            </view>
          </view>
          <view class="appointment-tip">
            <SvgIcon name="warning" :size="12" color="#FF7D00" />
            <text>确认接单后将锁定此时段，请确保能按时上门</text>
          </view>
        </view>

        <view class="btn-group">
          <button class="btn-primary" :disabled="confirming" @click="confirmFromSummary">
            <SvgIcon name="check" :size="18" color="#fff" />
            <text>{{ confirming ? '接单中...' : `确认接单（${reservedSlotInfo?.range || ''}）` }}</text>
          </button>
          <view class="btn-secondary-row">
            <button class="btn-secondary" @click="switchToPicker">
              <SvgIcon name="calendar" :size="16" color="#4E5969" />
              <text>改派时间</text>
            </button>
            <button class="btn-secondary danger" @click="switchToReject">
              <SvgIcon name="x" :size="16" color="#F53F3F" />
              <text>退回工单</text>
            </button>
          </view>
        </view>
      </template>

      <!-- ── 视图二：选择日期 / 时段（普通接单 或 预约改派）── -->
      <template v-else-if="view === 'picker'">
        <view class="picker-header">
          <view class="picker-back" :class="{ invisible: !isReserve }" @click="backToSummary">
            <SvgIcon name="caretLeft" :size="18" color="#4E5969" />
          </view>
          <text class="picker-title">{{ isReserve ? '改派时间' : '接单排期' }}</text>
          <view class="picker-placeholder" />
        </view>

        <view class="order-summary" v-if="order && order.company">
          <view class="order-summary-icon">
            <SvgIcon name="wrench" :size="22" color="#FF7D00" />
          </view>
          <view class="order-summary-info">
            <text class="order-summary-name ellipsis">{{ summaryName }}</text>
            <view class="order-summary-desc">
              <text>{{ order.contact || '—' }}</text>
              <text class="order-summary-urgent">{{ order.priority || '普通' }}</text>
            </view>
          </view>
        </view>

        <text class="section-title">选择日期</text>
        <view class="date-scroll">
          <view
            v-for="d in days"
            :key="d.date"
            class="date-item"
            :class="{ active: selectedDate === d.date, today: d.isToday }"
            @click="selectDate(d.date)"
          >
            <text class="date-item-week">{{ d.week }}</text>
            <text class="date-item-day">{{ d.day }}</text>
          </view>
        </view>

        <text class="section-title">选择时长</text>
        <view class="duration-row">
          <view
            v-for="t in DURATION_TIERS"
            :key="t.key"
            class="duration-item"
            :class="{ active: selectedSpan === t.span }"
            @click="selectDuration(t.span)"
          >
            <text class="duration-item-label">{{ t.label }}</text>
            <text class="duration-item-hint">{{ t.span }}格</text>
          </view>
        </view>

        <template v-if="selectedSpan === 1">
          <text class="section-title">选择时段</text>
          <view class="time-grid">
            <view
              v-for="s in TIME_SLOTS"
              :key="s.key"
              class="time-slot"
              :class="{ selected: selectedSlot === s.key, disabled: occupiedSlots.includes(s.key) }"
              @click="selectSlot(s)"
            >
              <text class="time-slot-period">{{ s.label }}</text>
              <text class="time-slot-range">{{ occupiedSlots.includes(s.key) ? '已约' : s.range }}</text>
            </view>
          </view>
        </template>
        <view v-else class="duration-preview">
          <SvgIcon name="clock" :size="14" color="#165DFF" />
          <text>{{ durationPreviewText }}</text>
        </view>

        <view class="escalate-block">
          <view class="escalate-head" @click="escalate = !escalate">
            <view class="escalate-head-left">
              <text class="escalate-title">加急置顶</text>
              <text class="escalate-desc">排到当天队首，其余顺延</text>
            </view>
            <view class="escalate-switch" :class="{ on: escalate }">
              <view class="escalate-switch-dot" />
            </view>
          </view>
          <view class="reason-block" v-if="escalate">
            <text class="reason-label">加急原因（必填）</text>
            <view class="reason-tags">
              <text
                v-for="r in ESCALATE_REASONS"
                :key="r"
                class="reason-tag"
                :class="{ active: escalateReason === r }"
                @click="escalateReason = escalateReason === r ? '' : r"
              >{{ r }}</text>
            </view>
          </view>
        </view>

        <view class="reason-block" v-if="isReserve">
          <text class="reason-label">改派原因（选填）</text>
          <view class="reason-tags">
            <text
              v-for="r in RESCHEDULE_REASONS"
              :key="r"
              class="reason-tag"
              :class="{ active: reason === r }"
              @click="reason = reason === r ? '' : r"
            >{{ r }}</text>
          </view>
        </view>

        <button class="btn-primary" :disabled="confirming" @click="confirmFromPicker">
          <SvgIcon name="check" :size="18" color="#fff" />
          <text>{{ confirming ? '提交中...' : pickerConfirmLabel }}</text>
        </button>
      </template>

      <!-- ── 视图三：退回确认 ── -->
      <template v-else>
        <view class="reject-icon">
          <SvgIcon name="warning" :size="28" color="#F53F3F" />
        </view>
        <text class="popup-title">确认退回工单？</text>
        <view class="reject-text">
          <text>退回后工单将返回调度池，由其他工程师接单。</text>
          <text class="reject-text-strong">{{ summaryName }}</text>
          <text v-if="reservedDate">预约时段：{{ reservedDate }} {{ reservedSlotInfo?.range || '' }}</text>
        </view>

        <view class="reason-block">
          <text class="reason-label">退回原因</text>
          <view class="reason-tags">
            <text
              v-for="r in REJECT_REASONS"
              :key="r"
              class="reason-tag"
              :class="{ active: reason === r }"
              @click="reason = reason === r ? '' : r"
            >{{ r }}</text>
          </view>
        </view>

        <view class="btn-secondary-row" style="margin-top: 8rpx;">
          <button class="btn-secondary" @click="backToSummary">取消</button>
          <button class="btn-secondary danger-solid" :disabled="rejecting" @click="doReject">
            {{ rejecting ? '退回中...' : '确认退回' }}
          </button>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRepairStore } from '@/stores/repair'
import SvgIcon from './SvgIcon.vue'
import { TIME_SLOTS, DURATION_TIERS } from '@/utils/repair-status'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  order: { type: Object, default: () => ({}) },
  mode: { type: String, default: 'auto' }, // auto | reserve | normal
  confirming: { type: Boolean, default: false },
  rejecting: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'reject'])

const authStore = useAuthStore()
const repairStore = useRepairStore()

const RESCHEDULE_REASONS = ['时段冲突', '距离较远', '需要备件', '其他']
const REJECT_REASONS = ['无法按时到达', '技能不匹配', '距离过远', '其他']
const ESCALATE_REASONS = ['灾难性故障', '领导检查', '客户临时要求', '其他']

// 时长档位 → 起始时段（单次走自由选时段；多格档位固定起始段）
const START_BY_SPAN = { 1: null, 2: 'AM1', 3: 'PM1', 5: 'AM1' }

const WEEK = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const pad = (n) => String(n).padStart(2, '0')
const fmtDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

// ── 预约字段 ──
const reservedDate = computed(() => props.order?.preferredDate || '')
const reservedSlot = computed(() => props.order?.preferredTimeSlot || '')
const reservedSlotInfo = computed(() => TIME_SLOTS.find(s => s.key === reservedSlot.value) || null)

// 是否为「预约工单接单」：已预约 + 有具体日期 + 具体时段（非全天）
const isReserve = computed(() => {
  if (props.mode === 'reserve') return true
  if (props.mode === 'normal') return false
  const o = props.order || {}
  return o.status === '已预约' && !!o.preferredDate && !!o.preferredTimeSlot && o.preferredTimeSlot !== '全天'
})

// 解析预约日期 → 日 / 周
const reservedDateDay = computed(() => {
  const m = String(reservedDate.value).match(/(\d{4})-(\d{1,2})-(\d{1,2})/)
  return m ? String(Number(m[3])) : '—'
})
const reservedDateWeek = computed(() => {
  const m = String(reservedDate.value).match(/(\d{4})-(\d{1,2})-(\d{1,2})/)
  if (!m) return ''
  return WEEK[new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])).getDay()]
})

const summaryName = computed(() => {
  const o = props.order || {}
  const kind = o.deviceType || o.workOrderType || (o.description ? '报修' : '')
  return [o.company, kind].filter(Boolean).join(' · ') || '工单'
})

// ── 视图状态：summary(预约确认) / picker(选日期时段) / reject(退回) ──
const view = ref('picker')
const selectedDate = ref('')
const selectedSlot = ref('AM1')
const selectedSpan = ref(1)
const escalate = ref(false)
const escalateReason = ref('')
const reason = ref('')
const occupiedSlots = ref([])

const todayStr = () => fmtDate(new Date())

const days = computed(() => {
  const arr = []
  const base = new Date()
  for (let i = 0; i < 7; i++) {
    const d = new Date(base.getFullYear(), base.getMonth(), base.getDate() + i)
    let week
    if (i === 0) week = '今天'
    else if (i === 1) week = '明天'
    else week = WEEK[d.getDay()]
    arr.push({ date: fmtDate(d), week, day: d.getDate(), isToday: i === 0 })
  }
  return arr
})

const formatMonthDay = (dateStr) => {
  const m = String(dateStr || '').match(/(\d{4})-(\d{1,2})-(\d{1,2})/)
  if (!m) return dateStr
  return `${Number(m[2])}月${Number(m[3])}日`
}

const selectedSlotInfo = computed(() => TIME_SLOTS.find(s => s.key === selectedSlot.value) || null)
const selectedDateLabel = computed(() => formatMonthDay(selectedDate.value))

// 多格档位的固定起始段；单次回退到自由选时段
const effectiveStartSlot = computed(() => START_BY_SPAN[selectedSpan.value] || selectedSlot.value)
const durationPreviewText = computed(() => {
  const t = DURATION_TIERS.find(x => x.span === selectedSpan.value)
  const startKey = START_BY_SPAN[selectedSpan.value]
  if (!startKey) return ''
  const startIdx = TIME_SLOTS.findIndex(x => x.key === startKey)
  const end = TIME_SLOTS[startIdx + selectedSpan.value - 1]
  const startTime = TIME_SLOTS[startIdx]?.range?.split('-')[0] || ''
  const endTime = end?.range?.split('-')[1] || ''
  return `${t?.label} · ${startTime} - ${endTime}`
})
const pickerConfirmLabel = computed(() => {
  const prefix = isReserve.value ? '确认改派' : '确认接单'
  if (selectedSpan.value !== 1) {
    const t = DURATION_TIERS.find(x => x.span === selectedSpan.value)
    return `${prefix}（${selectedDateLabel.value} ${t?.label}）`
  }
  const range = selectedSlotInfo.value?.range || ''
  return `${prefix}（${selectedDateLabel.value} ${range}）`
})

// ── 打开时重置状态 ──
watch(() => props.modelValue, (v) => {
  if (!v) return
  selectedDate.value = todayStr()
  selectedSlot.value = 'AM1'
  selectedSpan.value = 1
  escalate.value = false
  escalateReason.value = ''
  reason.value = ''
  occupiedSlots.value = []
  view.value = isReserve.value ? 'summary' : 'picker'
  loadAvailability()
})

const close = () => emit('update:modelValue', false)

const loadAvailability = async () => {
  const myId = authStore.userInfo?.id || authStore.userInfo?._id
  if (!myId || !selectedDate.value) return
  try {
    occupiedSlots.value = await repairStore.fetchScheduleAvailability({
      engineerId: myId,
      date: selectedDate.value
    })
    if (occupiedSlots.value.includes(selectedSlot.value)) selectedSlot.value = 'AM1'
  } catch {
    occupiedSlots.value = []
  }
}

const selectDate = (date) => {
  selectedDate.value = date
  loadAvailability()
}

const selectSlot = (s) => {
  if (occupiedSlots.value.includes(s.key)) return
  selectedSlot.value = s.key
}

const selectDuration = (span) => {
  selectedSpan.value = span
}

const switchToPicker = () => {
  reason.value = ''
  view.value = 'picker'
  loadAvailability()
}

const switchToReject = () => {
  reason.value = ''
  view.value = 'reject'
}

const backToSummary = () => {
  reason.value = ''
  view.value = 'summary'
}

const confirmFromSummary = () => {
  emit('confirm', { date: reservedDate.value, timeSlot: reservedSlot.value, slotSpan: 1, escalate: false, escalateReason: '', reason: '' })
}

const confirmFromPicker = () => {
  if (selectedSpan.value === 1 && !selectedSlot.value) {
    uni.showToast({ title: '请选择时段', icon: 'none' })
    return
  }
  if (selectedSpan.value === 1 && occupiedSlots.value.includes(selectedSlot.value)) {
    uni.showToast({ title: '该时段已被占用，请重新选择', icon: 'none' })
    return
  }
  if (escalate.value && !escalateReason.value) {
    uni.showToast({ title: '请选择加急原因', icon: 'none' })
    return
  }
  emit('confirm', {
    date: selectedDate.value,
    timeSlot: effectiveStartSlot.value,
    slotSpan: selectedSpan.value,
    escalate: escalate.value,
    escalateReason: escalate.value ? escalateReason.value : '',
    reason: reason.value
  })
}

const doReject = () => {
  if (!reason.value) {
    uni.showToast({ title: '请选择退回原因', icon: 'none' })
    return
  }
  emit('reject', { reason: reason.value })
}
</script>

<style lang="scss" scoped>
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.25s ease;
}

.popup-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 40rpx 40rpx 0 0;
  padding: 20rpx 32rpx calc(32rpx + env(safe-area-inset-bottom));
  max-height: 86vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-handle {
  width: 72rpx;
  height: 8rpx;
  background: #E5E6EB;
  border-radius: 4rpx;
  margin: 0 auto 20rpx;
}

.popup-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #1D2129;
  text-align: center;
}
.popup-subtitle {
  display: block;
  font-size: 24rpx;
  color: #86909C;
  text-align: center;
  margin: 8rpx 0 24rpx;
}

/* 工单摘要条 */
.order-summary {
  background: #F7F8FA;
  border-radius: 24rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.order-summary-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #FFF3E8, #FFE0B8);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.order-summary-info { flex: 1; min-width: 0; }
.order-summary-name {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 4rpx;
}
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.order-summary-desc {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 24rpx;
  color: #86909C;
}
.order-summary-urgent {
  font-size: 20rpx;
  padding: 2rpx 12rpx;
  background: #FFF1F0;
  color: #F53F3F;
  border-radius: 8rpx;
  font-weight: 600;
}

/* 预约时段卡片 */
.appointment-card {
  background: linear-gradient(135deg, #E8F3FF 0%, #F0F7FF 100%);
  border: 1.5px solid #BEDAFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  position: relative;
  overflow: hidden;
}
.appointment-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 6rpx;
  background: linear-gradient(90deg, #165DFF, #4080FF);
}
.appointment-label {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 24rpx;
  color: #165DFF;
  font-weight: 600;
  margin-bottom: 20rpx;
}
.appointment-time { display: flex; align-items: center; gap: 24rpx; }
.appointment-date { text-align: center; flex-shrink: 0; min-width: 80rpx; }
.appointment-date-day { display: block; font-size: 56rpx; font-weight: 900; color: #165DFF; line-height: 1; }
.appointment-date-week { display: block; font-size: 24rpx; color: #4E5969; margin-top: 8rpx; font-weight: 500; }
.appointment-divider { width: 2rpx; height: 72rpx; background: #BEDAFF; }
.appointment-detail { flex: 1; }
.appointment-period { display: block; font-size: 32rpx; font-weight: 700; color: #1D2129; margin-bottom: 8rpx; }
.appointment-range { display: flex; align-items: center; gap: 6rpx; font-size: 26rpx; color: #4E5969; }
.appointment-tip {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1px dashed #BEDAFF;
  font-size: 22rpx;
  color: #86909C;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

/* 按钮组 */
.btn-group { display: flex; flex-direction: column; gap: 20rpx; }
.btn-primary {
  width: 100%;
  height: 96rpx;
  border-radius: 48rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);
  margin-top: 8rpx;
  &[disabled] { background: #C9CDD4; box-shadow: none; }
}
.btn-secondary-row { display: flex; gap: 20rpx; }
.btn-secondary {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  background: #F2F3F5;
  color: #4E5969;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  &.danger { background: #FFF1F0; color: #F53F3F; }
  &.danger-solid { background: #F53F3F; color: #fff; }
  &[disabled] { opacity: 0.6; }
}

/* 改派/选择视图头部 */
.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}
.picker-back {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #F2F3F5;
  display: flex;
  align-items: center;
  justify-content: center;
  &.invisible { visibility: hidden; }
}
.picker-title { font-size: 34rpx; font-weight: 700; color: #1D2129; }
.picker-placeholder { width: 64rpx; }

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 16rpx;
}

/* 日期横向滚动 */
.date-scroll {
  display: flex;
  white-space: nowrap;
  overflow-x: auto;
  margin-bottom: 28rpx;
  &::-webkit-scrollbar { display: none; }
}
.date-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 110rpx;
  padding: 20rpx 0;
  border-radius: 24rpx;
  background: #F7F8FA;
  margin-right: 16rpx;
}
.date-item.active { background: linear-gradient(135deg, #165DFF, #4080FF); }
.date-item-week { font-size: 22rpx; color: #86909C; margin-bottom: 8rpx; }
.date-item-day { font-size: 36rpx; font-weight: 700; color: #1D2129; }
.date-item.active .date-item-week { color: rgba(255, 255, 255, 0.8); }
.date-item.active .date-item-day { color: #fff; }
.date-item.today:not(.active) .date-item-day { color: #165DFF; }

/* 时段网格 */
.time-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.time-slot {
  padding: 24rpx 16rpx;
  border-radius: 20rpx;
  background: #F7F8FA;
  text-align: center;
  border: 1.5px solid transparent;
  position: relative;
  &.selected { background: #E8F3FF; border-color: #165DFF; }
  &.disabled { opacity: 0.45; }
  &.disabled::after {
    content: '已约';
    position: absolute;
    top: 8rpx; right: 12rpx;
    font-size: 20rpx;
    color: #F53F3F;
    font-weight: 600;
  }
}
.time-slot-period { display: block; font-size: 26rpx; font-weight: 600; color: #1D2129; margin-bottom: 6rpx; }
.time-slot-range { font-size: 22rpx; color: #86909C; }
.time-slot.selected .time-slot-period { color: #165DFF; }
.time-slot.selected .time-slot-range { color: #4080FF; }

/* 时长档位 */
.duration-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.duration-item {
  padding: 20rpx 0;
  border-radius: 20rpx;
  background: #F7F8FA;
  text-align: center;
  border: 1.5px solid transparent;
  &.active { background: #E8F3FF; border-color: #165DFF; }
}
.duration-item-label { display: block; font-size: 26rpx; font-weight: 600; color: #1D2129; margin-bottom: 4rpx; }
.duration-item-hint { font-size: 20rpx; color: #86909C; }
.duration-item.active .duration-item-label { color: #165DFF; }
.duration-item.active .duration-item-hint { color: #4080FF; }

/* 多格时长预览 */
.duration-preview {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 24rpx 28rpx;
  border-radius: 20rpx;
  background: #E8F3FF;
  font-size: 26rpx;
  color: #165DFF;
  font-weight: 500;
  margin-bottom: 24rpx;
}

/* 加急置顶 */
.escalate-block {
  padding: 24rpx 28rpx;
  border-radius: 20rpx;
  background: #FFF7F6;
  border: 1.5px solid #FFD6D3;
  margin-bottom: 24rpx;
}
.escalate-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.escalate-head-left { display: flex; flex-direction: column; gap: 6rpx; }
.escalate-title { font-size: 28rpx; font-weight: 700; color: #F53F3F; }
.escalate-desc { font-size: 22rpx; color: #86909C; }
.escalate-switch {
  width: 84rpx;
  height: 48rpx;
  border-radius: 24rpx;
  background: #E5E6EB;
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
  &.on { background: #F53F3F; }
}
.escalate-switch-dot {
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #fff;
  transition: left 0.2s;
}
.escalate-switch.on .escalate-switch-dot { left: 40rpx; }

/* 原因标签 */
.reason-block { margin-bottom: 24rpx; }
.reason-label { display: block; font-size: 26rpx; color: #4E5969; margin-bottom: 16rpx; font-weight: 500; }
.reason-tags { display: flex; flex-wrap: wrap; gap: 16rpx; }
.reason-tag {
  padding: 14rpx 28rpx;
  border-radius: 32rpx;
  background: #F7F8FA;
  font-size: 24rpx;
  color: #4E5969;
  font-weight: 500;
  &.active { background: #E8F3FF; color: #165DFF; font-weight: 600; }
}

/* 退回确认 */
.reject-icon {
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  background: #FFF1F0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 8rpx auto 24rpx;
}
.reject-text {
  text-align: center;
  font-size: 26rpx;
  color: #4E5969;
  line-height: 1.6;
  margin-bottom: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}
.reject-text-strong { color: #1D2129; font-weight: 600; }

@keyframes fadeIn  { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
</style>
