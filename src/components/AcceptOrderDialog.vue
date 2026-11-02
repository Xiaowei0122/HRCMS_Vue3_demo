<template>
  <el-dialog
    :model-value="modelValue"
    width="420px"
    :show-close="false"
    class="ao-dialog"
    append-to-body
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <div class="ao-body">
      <!-- ── 视图一：接单确认（预约工单：预约时段卡片 + 三按钮）── -->
      <template v-if="view === 'summary'">
        <div class="ao-title">接单确认</div>
        <div class="ao-subtitle">请确认预约时段，或选择改派 / 退回</div>

        <div class="ao-order-summary">
          <div class="ao-os-icon"><el-icon><Document /></el-icon></div>
          <div class="ao-os-info">
            <div class="ao-os-name">{{ summaryName }}</div>
            <div class="ao-os-desc">
              <span>{{ order?.contact || '—' }}</span>
              <span class="ao-urgent">{{ order?.priority || '普通' }}</span>
            </div>
          </div>
        </div>

        <div class="ao-appointment">
          <div class="ao-app-label"><el-icon><Clock /></el-icon> 用户已预约时段</div>
          <div class="ao-app-time">
            <div class="ao-app-date">
              <div class="ao-app-day">{{ reservedDay }}</div>
              <div class="ao-app-week">{{ reservedWeek }}</div>
            </div>
            <div class="ao-app-divider" />
            <div class="ao-app-detail">
              <div class="ao-app-period">{{ reservedSlotInfo?.label || reservedSlot }}</div>
              <div class="ao-app-range">{{ reservedSlotInfo?.range || '' }}</div>
            </div>
          </div>
          <div class="ao-app-tip"><el-icon><WarningFilled /></el-icon> 确认接单后将锁定此时段，请确保能按时上门</div>
        </div>

        <div class="ao-btns">
          <button class="ao-btn-primary" :disabled="confirming" @click="confirmReserved">
            <el-icon><Check /></el-icon>
            {{ confirming ? '接单中...' : `确认接单（${reservedSlotInfo?.range || ''}）` }}
          </button>
          <div class="ao-btn-row">
            <button class="ao-btn-secondary" @click="goPicker"><el-icon><Calendar /></el-icon> 改派时间</button>
            <button class="ao-btn-secondary danger" @click="goReject"><el-icon><Close /></el-icon> 退回工单</button>
          </div>
        </div>
      </template>

      <!-- ── 视图二：选择日期 / 时段（普通接单 或 预约改派）── -->
      <template v-else-if="view === 'picker'">
        <div class="ao-picker-header">
          <div class="ao-back" :class="{ invisible: !isReserved }" @click="backToSummary"><el-icon><ArrowLeft /></el-icon></div>
          <div class="ao-picker-title">{{ isReserved ? '改派时间' : '接单排期' }}</div>
          <div class="ao-back-placeholder" />
        </div>

        <div class="ao-order-summary">
          <div class="ao-os-icon"><el-icon><Document /></el-icon></div>
          <div class="ao-os-info">
            <div class="ao-os-name">{{ summaryName }}</div>
            <div class="ao-os-desc">
              <span>{{ order?.contact || '—' }}</span>
              <span class="ao-urgent">{{ order?.priority || '普通' }}</span>
            </div>
          </div>
        </div>

        <div class="ao-section-title">选择日期</div>
        <div class="ao-date-scroll">
          <div
            v-for="d in days"
            :key="d.date"
            class="ao-date"
            :class="{ active: selectedDate === d.date, today: d.isToday }"
            @click="selectDate(d.date)"
          >
            <div class="ao-date-week">{{ d.week }}</div>
            <div class="ao-date-day">{{ d.day }}</div>
          </div>
        </div>

        <div class="ao-section-title">选择时长</div>
        <div class="ao-duration-row">
          <div
            v-for="t in DURATION_TIERS"
            :key="t.key"
            class="ao-duration"
            :class="{ active: selectedSpan === t.span }"
            @click="selectDuration(t.span)"
          >
            <div class="ao-duration-label">{{ t.label }}</div>
            <div class="ao-duration-hint">{{ t.span }}格</div>
          </div>
        </div>

        <template v-if="selectedSpan === 1">
          <div class="ao-section-title">选择时段</div>
          <div class="ao-time-grid">
            <div
              v-for="s in TIME_SLOTS"
              :key="s.key"
              class="ao-slot"
              :class="{ selected: selectedSlot === s.key, disabled: occupied.includes(s.key) }"
              @click="selectSlot(s)"
            >
              <div class="ao-slot-period">{{ s.label }}</div>
              <div class="ao-slot-range">{{ occupied.includes(s.key) ? '已约' : s.range }}</div>
            </div>
          </div>
        </template>
        <div v-else class="ao-duration-preview"><el-icon><Clock /></el-icon> {{ durationPreviewText }}</div>

        <div class="ao-escalate">
          <div class="ao-escalate-head" @click="escalate = !escalate">
            <div class="ao-escalate-left">
              <div class="ao-escalate-title">加急置顶</div>
              <div class="ao-escalate-desc">排到当天队首，其余顺延</div>
            </div>
            <div class="ao-escalate-switch" :class="{ on: escalate }"><div class="ao-escalate-dot" /></div>
          </div>
          <div v-if="escalate" class="ao-reason">
            <div class="ao-reason-label">加急原因（必填）</div>
            <div class="ao-tags">
              <span
                v-for="r in ESCALATE_REASONS"
                :key="r"
                class="ao-tag"
                :class="{ active: escalateReason === r }"
                @click="escalateReason = escalateReason === r ? '' : r"
              >{{ r }}</span>
            </div>
          </div>
        </div>

        <div v-if="isReserved" class="ao-reason">
          <div class="ao-reason-label">改派原因（选填）</div>
          <div class="ao-tags">
            <span
              v-for="r in RESCHEDULE_REASONS"
              :key="r"
              class="ao-tag"
              :class="{ active: reason === r }"
              @click="reason = reason === r ? '' : r"
            >{{ r }}</span>
          </div>
        </div>

        <button class="ao-btn-primary" :disabled="confirming" @click="confirmPick">
          <el-icon><Check /></el-icon>
          {{ confirming ? '提交中...' : pickerLabel }}
        </button>
      </template>

      <!-- ── 视图三：退回确认 ── -->
      <template v-else>
        <div class="ao-reject-icon"><el-icon><CircleClose /></el-icon></div>
        <div class="ao-title">确认退回工单？</div>
        <div class="ao-reject-text">
          退回后工单将返回调度池，由其他工程师接单。
          <div class="ao-reject-strong">{{ summaryName }}</div>
          <div v-if="reservedDate">预约时段：{{ reservedDate }} {{ reservedSlotInfo?.range || '' }}</div>
        </div>

        <div class="ao-reason">
          <div class="ao-reason-label">退回原因</div>
          <div class="ao-tags">
            <span
              v-for="r in REJECT_REASONS"
              :key="r"
              class="ao-tag"
              :class="{ active: reason === r }"
              @click="reason = reason === r ? '' : r"
            >{{ r }}</span>
          </div>
        </div>

        <div class="ao-btn-row" style="margin-top: 8px">
          <button class="ao-btn-secondary" @click="backToSummary">取消</button>
          <button class="ao-btn-secondary danger-solid" :disabled="rejecting" @click="confirmReject">
            {{ rejecting ? '退回中...' : '确认退回' }}
          </button>
        </div>
      </template>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Calendar, Check, Close, CircleClose, ArrowLeft, WarningFilled, Document } from '@element-plus/icons-vue'
import { getScheduleAvailability } from '@/api/modules/repairs'
import { getUserInfo } from '@/utils/auth'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  order: { type: Object, default: () => ({}) },
  mode: { type: String, default: 'auto' }, // auto | reserve | normal
  confirming: { type: Boolean, default: false },
  rejecting: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'reject'])

// 五个排期时段（与小程序/后端一致）
const TIME_SLOTS = [
  { key: 'AM1', label: '上午（早）', range: '08:30-10:00' },
  { key: 'AM2', label: '上午（晚）', range: '10:00-11:50' },
  { key: 'PM1', label: '下午（早）', range: '13:30-15:00' },
  { key: 'PM2', label: '下午（中）', range: '15:00-16:30' },
  { key: 'PM3', label: '下午（晚）', range: '16:30-18:00' }
]

const RESCHEDULE_REASONS = ['时段冲突', '距离较远', '需要备件', '其他']
const REJECT_REASONS = ['无法按时到达', '技能不匹配', '距离过远', '其他']
const ESCALATE_REASONS = ['灾难性故障', '领导检查', '客户临时要求', '其他']

// 时长档位（与后端 slotSpan 对齐：1/2/3/5）
const DURATION_TIERS = [
  { key: 1, label: '单次', span: 1 },
  { key: 2, label: '上午半天', span: 2 },
  { key: 3, label: '下午半天', span: 3 },
  { key: 5, label: '全天', span: 5 }
]
const START_BY_SPAN = { 1: null, 2: 'AM1', 3: 'PM1', 5: 'AM1' }

const WEEK = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const pad = (n) => String(n).padStart(2, '0')
const fmtDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

// 是否为「预约工单接单」：已预约 + 具体日期 + 具体时段（非全天）
const isReserved = computed(() => {
  if (props.mode === 'reserve') return true
  if (props.mode === 'normal') return false
  const o = props.order || {}
  return o.status === '已预约' && !!o.preferredDate && !!o.preferredTimeSlot && o.preferredTimeSlot !== '全天'
})

const reservedDate = computed(() => props.order?.preferredDate || '')
const reservedSlot = computed(() => props.order?.preferredTimeSlot || '')
const reservedSlotInfo = computed(() => TIME_SLOTS.find(s => s.key === reservedSlot.value) || null)

const reservedDay = computed(() => {
  const m = String(reservedDate.value).match(/(\d{4})-(\d{1,2})-(\d{1,2})/)
  return m ? String(Number(m[3])) : '—'
})
const reservedWeek = computed(() => {
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
const occupied = ref([])

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
const pickerLabel = computed(() => {
  const prefix = isReserved.value ? '确认改派' : '确认接单'
  if (selectedSpan.value !== 1) {
    const t = DURATION_TIERS.find(x => x.span === selectedSpan.value)
    return `${prefix}（${selectedDateLabel.value} ${t?.label}）`
  }
  const range = selectedSlotInfo.value?.range || ''
  return `${prefix}（${selectedDateLabel.value} ${range}）`
})

watch(() => props.modelValue, (v) => {
  if (!v) return
  selectedDate.value = todayStr()
  selectedSlot.value = 'AM1'
  selectedSpan.value = 1
  escalate.value = false
  escalateReason.value = ''
  reason.value = ''
  occupied.value = []
  view.value = isReserved.value ? 'summary' : 'picker'
  loadAvailability()
})

const loadAvailability = async () => {
  const myId = getUserInfo()?.id
  if (!myId || !selectedDate.value) return
  try {
    const res = await getScheduleAvailability({ engineerId: myId, date: selectedDate.value })
    occupied.value = Array.isArray(res?.occupied) ? res.occupied : []
    if (occupied.value.includes(selectedSlot.value)) selectedSlot.value = 'AM1'
  } catch { occupied.value = [] }
}

const selectDate = (date) => {
  selectedDate.value = date
  loadAvailability()
}

const selectSlot = (s) => {
  if (occupied.value.includes(s.key)) return
  selectedSlot.value = s.key
}

const selectDuration = (span) => {
  selectedSpan.value = span
}

const goPicker = () => {
  reason.value = ''
  view.value = 'picker'
  loadAvailability()
}

const goReject = () => {
  reason.value = ''
  view.value = 'reject'
}

const backToSummary = () => {
  reason.value = ''
  view.value = 'summary'
}

const confirmReserved = () => {
  const d = props.order?.preferredDate
  const s = props.order?.preferredTimeSlot
  if (!d || !s) { ElMessage.warning('缺少预约时段信息，请改派时间'); return }
  emit('confirm', { date: d, timeSlot: s, slotSpan: 1, escalate: false, escalateReason: '', reason: '' })
}

const confirmPick = () => {
  if (selectedSpan.value === 1 && !selectedSlot.value) { ElMessage.warning('请选择时段'); return }
  if (selectedSpan.value === 1 && occupied.value.includes(selectedSlot.value)) { ElMessage.warning('该时段已被占用，请重新选择'); return }
  if (escalate.value && !escalateReason.value) { ElMessage.warning('请选择加急原因'); return }
  emit('confirm', {
    date: selectedDate.value,
    timeSlot: effectiveStartSlot.value,
    slotSpan: selectedSpan.value,
    escalate: escalate.value,
    escalateReason: escalate.value ? escalateReason.value : '',
    reason: reason.value
  })
}

const confirmReject = () => {
  if (!reason.value) { ElMessage.warning('请选择退回原因'); return }
  emit('reject', { reason: reason.value })
}
</script>

<style scoped>
.ao-body { padding: 26px 22px 26px; }

.ao-title { text-align: center; font-size: 18px; font-weight: 700; color: #1D2129; }
.ao-subtitle { text-align: center; font-size: 13px; color: #86909C; margin: 6px 0 18px; }

/* 工单摘要条 */
.ao-order-summary {
  background: #F7F8FA; border-radius: 12px; padding: 12px 14px; margin-bottom: 14px;
  display: flex; align-items: center; gap: 12px;
}
.ao-os-icon {
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #FFF3E8, #FFE0B8);
  display: flex; align-items: center; justify-content: center; color: #FF7D00; font-size: 20px;
}
.ao-os-info { flex: 1; min-width: 0; }
.ao-os-name { font-size: 14px; font-weight: 600; color: #1D2129; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ao-os-desc { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #86909C; }
.ao-urgent { font-size: 10px; padding: 1px 6px; background: #FFF1F0; color: #F53F3F; border-radius: 4px; font-weight: 600; }

/* 预约时段卡片 */
.ao-appointment {
  background: linear-gradient(135deg, #E8F3FF 0%, #F0F7FF 100%);
  border: 1.5px solid #BEDAFF; border-radius: 14px; padding: 16px; margin-bottom: 14px;
  position: relative; overflow: hidden;
}
.ao-appointment::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #165DFF, #4080FF);
}
.ao-app-label { font-size: 12px; color: #165DFF; font-weight: 600; display: flex; align-items: center; gap: 6px; margin-bottom: 10px; }
.ao-app-time { display: flex; align-items: center; gap: 14px; }
.ao-app-date { text-align: center; flex-shrink: 0; min-width: 44px; }
.ao-app-day { font-size: 28px; font-weight: 900; color: #165DFF; line-height: 1; }
.ao-app-week { font-size: 12px; color: #4E5969; margin-top: 4px; }
.ao-app-divider { width: 1px; height: 40px; background: #BEDAFF; }
.ao-app-detail { flex: 1; }
.ao-app-period { font-size: 16px; font-weight: 700; color: #1D2129; margin-bottom: 4px; }
.ao-app-range { font-size: 13px; color: #4E5969; }
.ao-app-tip {
  margin-top: 10px; padding-top: 10px; border-top: 1px dashed #BEDAFF;
  font-size: 11px; color: #86909C; display: flex; align-items: center; gap: 4px;
}

/* 按钮组 */
.ao-btns { display: flex; flex-direction: column; gap: 10px; }
.ao-btn-primary {
  width: 100%; height: 48px; border-radius: 24px; border: none; cursor: pointer;
  background: linear-gradient(135deg, #165DFF, #4080FF); color: #fff;
  font-size: 15px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 6px 16px rgba(22, 93, 255, 0.3);
}
.ao-btn-primary:disabled { background: #C9CDD4; box-shadow: none; cursor: not-allowed; }
.ao-btn-row { display: flex; gap: 10px; }
.ao-btn-secondary {
  flex: 1; height: 44px; border-radius: 22px; border: none; cursor: pointer;
  background: #F2F3F5; color: #4E5969; font-size: 14px; font-weight: 600;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.ao-btn-secondary.danger { background: #FFF1F0; color: #F53F3F; }
.ao-btn-secondary.danger-solid { background: #F53F3F; color: #fff; }
.ao-btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }

/* 改派/选择视图头部 */
.ao-picker-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.ao-back { width: 32px; height: 32px; border-radius: 50%; background: #F2F3F5; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #4E5969; }
.ao-back.invisible { visibility: hidden; }
.ao-back-placeholder { width: 32px; }
.ao-picker-title { font-size: 17px; font-weight: 700; color: #1D2129; }

.ao-section-title { font-size: 14px; font-weight: 600; color: #1D2129; margin-bottom: 10px; }

/* 日期横向滚动 */
.ao-date-scroll { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; margin-bottom: 14px; }
.ao-date-scroll::-webkit-scrollbar { display: none; }
.ao-date { flex-shrink: 0; width: 56px; padding: 10px 0; border-radius: 12px; background: #F7F8FA; text-align: center; cursor: pointer; }
.ao-date.active { background: linear-gradient(135deg, #165DFF, #4080FF); }
.ao-date-week { font-size: 11px; color: #86909C; margin-bottom: 4px; }
.ao-date.active .ao-date-week { color: rgba(255, 255, 255, 0.8); }
.ao-date-day { font-size: 18px; font-weight: 700; color: #1D2129; }
.ao-date.active .ao-date-day { color: #fff; }
.ao-date.today:not(.active) .ao-date-day { color: #165DFF; }

/* 时段网格 */
.ao-time-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px; }
.ao-slot { padding: 12px 8px; border-radius: 10px; background: #F7F8FA; text-align: center; cursor: pointer; border: 1.5px solid transparent; position: relative; }
.ao-slot.selected { background: #E8F3FF; border-color: #165DFF; }
.ao-slot.disabled { opacity: 0.45; cursor: not-allowed; }
.ao-slot.disabled::after { content: '已约'; position: absolute; top: 4px; right: 6px; font-size: 9px; color: #F53F3F; font-weight: 600; }
.ao-slot-period { font-size: 13px; font-weight: 600; color: #1D2129; margin-bottom: 2px; }
.ao-slot.selected .ao-slot-period { color: #165DFF; }
.ao-slot-range { font-size: 11px; color: #86909C; }
.ao-slot.selected .ao-slot-range { color: #4080FF; }

/* 时长档位 */
.ao-duration-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 14px; }
.ao-duration { padding: 12px 0; border-radius: 10px; background: #F7F8FA; text-align: center; cursor: pointer; border: 1.5px solid transparent; }
.ao-duration.active { background: #E8F3FF; border-color: #165DFF; }
.ao-duration-label { font-size: 13px; font-weight: 600; color: #1D2129; }
.ao-duration-hint { font-size: 11px; color: #86909C; }
.ao-duration.active .ao-duration-label { color: #165DFF; }
.ao-duration.active .ao-duration-hint { color: #4080FF; }

.ao-duration-preview {
  display: flex; align-items: center; gap: 6px;
  padding: 12px 14px; border-radius: 10px; background: #E8F3FF;
  font-size: 13px; color: #165DFF; font-weight: 500; margin-bottom: 14px;
}

/* 加急置顶 */
.ao-escalate { padding: 14px; border-radius: 10px; background: #FFF7F6; border: 1.5px solid #FFD6D3; margin-bottom: 14px; }
.ao-escalate-head { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
.ao-escalate-left { display: flex; flex-direction: column; gap: 2px; }
.ao-escalate-title { font-size: 14px; font-weight: 700; color: #F53F3F; }
.ao-escalate-desc { font-size: 11px; color: #86909C; }
.ao-escalate-switch { width: 42px; height: 24px; border-radius: 12px; background: #E5E6EB; position: relative; transition: background 0.2s; flex-shrink: 0; }
.ao-escalate-switch.on { background: #F53F3F; }
.ao-escalate-dot { position: absolute; top: 2px; left: 2px; width: 20px; height: 20px; border-radius: 50%; background: #fff; transition: left 0.2s; }
.ao-escalate-switch.on .ao-escalate-dot { left: 20px; }
.ao-escalate .ao-reason { margin-top: 10px; margin-bottom: 0; }

/* 原因标签 */
.ao-reason { margin-bottom: 14px; }
.ao-reason-label { font-size: 13px; color: #4E5969; margin-bottom: 8px; font-weight: 500; }
.ao-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.ao-tag { padding: 7px 14px; border-radius: 16px; background: #F7F8FA; font-size: 12px; color: #4E5969; cursor: pointer; }
.ao-tag.active { background: #E8F3FF; color: #165DFF; font-weight: 600; }

/* 退回确认 */
.ao-reject-icon { width: 56px; height: 56px; border-radius: 50%; background: #FFF1F0; display: flex; align-items: center; justify-content: center; margin: 0 auto 14px; color: #F53F3F; font-size: 28px; }
.ao-reject-text { text-align: center; font-size: 13px; color: #4E5969; line-height: 1.6; margin-bottom: 14px; }
.ao-reject-strong { color: #1D2129; font-weight: 600; }
</style>

<style>
/* el-dialog 用 append-to-body 挂到 body 下，scoped 的 data-v 会落在不同元素上，
   改用非 scoped 规则才能可靠命中并隐藏 header / 去掉 body 默认内边距 */
.ao-dialog .el-dialog__header { display: none; }
.ao-dialog .el-dialog__body { padding: 0; }
</style>
