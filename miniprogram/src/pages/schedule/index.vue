<!--
  工程师排期（重新设计版）— 工程师选择面板 + 周视图占用日历 + 当日排期列表
  与 CMS 对齐：五个时间段，可指派工单（仅管理员）
-->
<template>
  <view class="page">
    <PageNavbar title="工程师排期" :scrolled="scrolled" />

    <scroll-view scroll-y class="scroll-body" @scrolltolower="onScrollLower" @scroll="onScroll">
      <!-- 工程师选择器 -->
      <view class="engineer-card" @click="showEngineerPanel = true">
        <view class="eng-avatar">
          <text>{{ avatarChar(selectedEngineer) }}</text>
        </view>
        <view class="eng-info">
          <text class="eng-name">{{ currentEngineer || '选择工程师' }}</text>
          <text class="eng-desc">{{ currentEngineer ? engineerDesc : '点击选择要查看的工程师' }}</text>
        </view>
        <view class="eng-arrow">
          <SvgIcon name="caretRight" :size="16" color="#4E5969" />
        </view>
      </view>

      <!-- Tab 切换 -->
      <view class="page-tabs">
        <view class="page-tab" :class="{ active: activeTab === 'calendar' }" @click="activeTab = 'calendar'">
          <SvgIcon name="calendar" :size="16" :color="activeTab === 'calendar' ? '#165DFF' : '#4E5969'" />
          <text>周排期</text>
        </view>
        <view class="page-tab" :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">
          <SvgIcon name="clipboard" :size="16" :color="activeTab === 'list' ? '#165DFF' : '#4E5969'" />
          <text>工单列表</text>
        </view>
      </view>

      <!-- 周排期 -->
      <view v-show="activeTab === 'calendar'" class="tab-panel">
        <ScheduleTable
          :schedule-data="scheduleList"
          :week-start="weekStart"
          :selected-date="selectedDate"
          @prev-week="prevWeek"
          @next-week="nextWeek"
          @go-today="goToday"
          @select-date="onSelectDate"
        />

        <!-- 当日排期列表 -->
        <view class="day-section">
          <view class="day-header">
            <view class="day-title">
              <view class="day-title-bar" />
              <text>{{ dayTitle }}</text>
              <text class="day-count">{{ selectedDayList.length }} 单</text>
            </view>
          </view>

          <view v-if="selectedDayList.length" class="day-list">
            <view v-for="item in selectedDayList" :key="item.id" class="schedule-item">
              <view class="schedule-item-main">
                <view class="time-block" :class="isLock(item) ? 'lock' : 'biz'">
                  <text class="time-period">{{ slotLabel(item.timeSlot) }}</text>
                  <text class="time-range">{{ slotRange(item.timeSlot) }}</text>
                  <text v-if="!isLock(item) && (item.slotSpan || 1) > 1" class="time-span">预计耗时 · {{ durationLabel(item.slotSpan) }}</text>
                </view>
                <view class="schedule-info">
                  <text class="schedule-customer">{{ itemTitle(item) }}</text>
                  <view class="schedule-meta">
                    <text v-if="!isLock(item) && item.orderNo" class="schedule-order">工单 {{ item.orderNo }}</text>
                    <text v-if="!isLock(item) && item.escalated" class="schedule-escalated">加急</text>
                    <text v-if="!isLock(item) && (item.repairStatus || item.status)" class="schedule-status-tag" :class="'st-' + statusKey(item.repairStatus || item.status)">{{ item.repairStatus || item.status }}</text>
                    <text v-if="isLock(item)" class="schedule-tag">异常锁定 · {{ lockTypeLabel(item.type) }}</text>
                  </view>
                </view>
                <view v-if="authStore.isAdmin" class="schedule-delete" @click="removeSchedule(item)">
                  <SvgIcon name="x" :size="14" color="#F53F3F" />
                </view>
              </view>
              <view v-if="canReorder && canReorderItem(item)" class="schedule-actions">
                <text class="reorder-btn" @click="reorderItem(item, 'top')">置顶</text>
                <text class="reorder-btn" @click="reorderItem(item, 'up')">上移</text>
                <text class="reorder-btn" @click="reorderItem(item, 'down')">下移</text>
                <text class="reorder-btn extend" @click="reorderItem(item, 'extend')">顺延后续</text>
              </view>
            </view>
          </view>
          <view v-else class="day-empty">
            <EmptyState icon="calendar" text="当天暂无排期" sub-text="空闲时段可指派工单" />
          </view>
        </view>

        <view v-if="!authStore.isAdmin" class="view-only-tip">
          <SvgIcon name="lock" :size="16" color="#86909C" />
          <text>仅管理员可指派 / 修改排期</text>
        </view>
      </view>

      <!-- 工单列表 -->
      <view v-show="activeTab === 'list'" class="tab-panel">
        <!-- 时间筛选 -->
        <view class="range-filter">
          <view
            v-for="r in rangeOptions"
            :key="r.value"
            class="range-chip"
            :class="{ active: orderRange === r.value }"
            @click="switchRange(r.value)"
          >
            {{ r.label }}
          </view>
        </view>
        <view v-if="orderRange === 'custom'" class="range-custom">
          <view class="range-date" @click="showStartDateSheet = true">{{ customStart || '开始日期' }}</view>
          <text class="range-sep">至</text>
          <view class="range-date" @click="showEndDateSheet = true">{{ customEnd || '结束日期' }}</view>
        </view>
        <OrderCard v-for="item in orderList" :key="item._id || item.id" :order="item" @click="goDetail(item)" />
        <EmptyState v-if="!orderList.length && !orderLoading" icon="clipboard" text="暂无工单" sub-text="当前时间范围内暂无接单记录" />
        <view v-if="orderList.length" class="foot-msg"><text>{{ orderNoMore ? '— 没有更多了 —' : (orderLoading ? '加载中...' : '上拉加载更多') }}</text></view>
      </view>

      <view class="safe-bottom" />
    </scroll-view>

    <!-- 浮动添加按钮（仅管理员） -->
    <button v-if="authStore.isAdmin" class="add-btn" @click="openScheduleForm">
      <SvgIcon name="plus" :size="18" color="#fff" />
      <text>添加排期</text>
    </button>

    <!-- 自定义时间范围日期选择 -->
    <DatePickerSheet v-model="showStartDateSheet" title="选择开始日期" :value="customStart" @select="onCustomStartSelect" />
    <DatePickerSheet v-model="showEndDateSheet" title="选择结束日期" :value="customEnd" @select="onCustomEndSelect" />

    <!-- 工程师选择面板（底部弹出） -->
    <view v-if="showEngineerPanel" class="panel-mask" @click="showEngineerPanel = false">
      <view class="engineer-panel" @click.stop>
        <view class="panel-handle" />
        <text class="panel-title">选择工程师</text>
        <scroll-view scroll-y class="panel-list">
          <view
            v-for="(e, i) in engineers"
            :key="e.id"
            class="panel-item"
            :class="{ selected: e.id === selectedEngineerId }"
            @click="selectEngineer(e)"
          >
            <view class="panel-avatar" :style="{ background: avatarGradient(i) }">
              <text>{{ avatarChar(e) }}</text>
            </view>
            <view class="panel-info">
              <view class="panel-name-row">
                <text class="panel-name">{{ e.name || e.username }}</text>
                <text v-if="e.username" class="panel-id">{{ e.username }}</text>
              </view>
              <text class="panel-skills">{{ skillsText(e) }}</text>
              <view class="panel-load">
                <view class="load-bar">
                  <view class="load-fill" :style="{ width: weeklyLoad(e.id) + '%', background: loadColor(weeklyLoad(e.id)) }" />
                </view>
                <text class="load-text">本周负载 {{ weeklyLoad(e.id) }}%</text>
              </view>
            </view>
            <view class="panel-check">
              <SvgIcon name="check" :size="14" color="#fff" />
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 添加排期弹窗 -->
    <view class="popup-overlay" v-if="showScheduleForm" @click="closeScheduleForm">
      <view class="popup-card" @click.stop>
        <view class="sheet-viewport">
          <view class="sheet-track" :style="{ transform: `translateX(-${slideIndex * 25}%)` }">
            <!-- Slide 0：主表单 -->
            <view class="sheet-slide" :class="{ active: slideIndex === 0 }">
              <text class="popup-title">添加排期</text>

              <view class="type-seg">
                <view class="type-seg-item" :class="{ active: scheduleForm.type === 'business' }" @click="scheduleForm.type = 'business'">
                  业务工单
                </view>
                <view class="type-seg-item" :class="{ active: scheduleForm.type === 'break' }" @click="scheduleForm.type = 'break'">
                  异常锁定
                </view>
              </view>

              <view class="picker" :class="{ dim: !scheduleForm.date }" @click="goSlide(1)">
                <text>{{ scheduleForm.date || '请选择日期' }}</text>
                <SvgIcon name="caretRight" :size="14" class="arrow" />
              </view>

              <view class="picker" @click="goSlide(2)">
                <text>{{ scheduleForm.timeSlot ? (slotLabel(scheduleForm.timeSlot) + ' ' + slotRange(scheduleForm.timeSlot)) : '请选择时段' }}</text>
                <SvgIcon name="caretRight" :size="14" class="arrow" />
              </view>

              <template v-if="scheduleForm.type === 'business'">
                <view class="order-search">
                  <input class="s-input" v-model="orderSearch" placeholder="搜索未指派工单（单位 / 工单号）" placeholder-style="color:#C9CDD4" />
                </view>
                <scroll-view scroll-y class="order-pick-list">
                  <view
                    v-for="o in filteredUnassignedOrders"
                    :key="o.id || o._id"
                    class="order-pick-item"
                    :class="{ selected: scheduleForm.orderId === (o.id || o._id) }"
                    @click="selectOrder(o)"
                  >
                    <view class="op-main">
                      <text class="op-no">{{ o.orderNo }}</text>
                      <text class="op-company text-ellipsis">{{ o.company }}</text>
                    </view>
                    <view class="op-check" v-if="scheduleForm.orderId === (o.id || o._id)">
                      <SvgIcon name="check" :size="16" color="#FFFFFF" />
                    </view>
                  </view>
                  <view v-if="!filteredUnassignedOrders.length" class="op-empty">
                    <text>{{ orderSearch ? '未找到匹配的未指派工单' : '暂无可指派的未接单工单' }}</text>
                  </view>
                </scroll-view>
              </template>

              <template v-else>
                <view class="picker" @click="goSlide(3)">
                  <text>{{ lockTypeLabel(scheduleForm.lockType) }}</text>
                  <SvgIcon name="caretRight" :size="14" class="arrow" />
                </view>
                <input class="s-input" v-model="scheduleForm.note" placeholder="锁定说明（如：外出培训 / 年假）" placeholder-style="color:#C9CDD4" />
              </template>

              <view class="popup-actions">
                <button class="btn-cancel" @click="closeScheduleForm">取消</button>
                <button class="btn-confirm" :disabled="submittingSchedule" @click="submitSchedule">
                  {{ submittingSchedule ? '保存中...' : '保存' }}
                </button>
              </view>
            </view>

            <!-- Slide 1：日期选择 -->
            <view class="sheet-slide" :class="{ active: slideIndex === 1 }">
              <view class="slide-head">
                <view class="slide-back" @click="goSlide(0)">
                  <SvgIcon name="caretLeft" :size="18" color="#4E5969" />
                </view>
                <text class="slide-title">选择排期日期</text>
                <view class="slide-head-spacer" />
              </view>

              <view class="dp-nav">
                <view class="dp-nav-btn" @click="formPrevMonth">
                  <SvgIcon name="caretLeft" :size="20" color="#4E5969" />
                </view>
                <text class="dp-nav-title">{{ formViewYear }}年{{ formViewMonth }}月</text>
                <view class="dp-nav-btn" @click="formNextMonth">
                  <SvgIcon name="caretRight" :size="20" color="#4E5969" />
                </view>
              </view>

              <view class="dp-week">
                <text v-for="w in formWeeks" :key="w" class="dp-week-item">{{ w }}</text>
              </view>

              <view class="dp-grid">
                <view
                  v-for="(d, i) in formDays"
                  :key="i"
                  class="dp-day"
                  :class="{ empty: !d.day, selected: d.selected, today: d.isToday, disabled: d.disabled }"
                  @click="d.day && !d.disabled && pickFormDate(d)"
                >
                  <text>{{ d.day }}</text>
                </view>
              </view>

              <view class="dp-footer">
                <button class="dp-today" @click="pickFormToday">回到今天</button>
              </view>
            </view>

            <!-- Slide 2：时段选择 -->
            <view class="sheet-slide" :class="{ active: slideIndex === 2 }">
              <view class="slide-head">
                <view class="slide-back" @click="goSlide(0)">
                  <SvgIcon name="caretLeft" :size="18" color="#4E5969" />
                </view>
                <text class="slide-title">选择时段</text>
                <view class="slide-head-spacer" />
              </view>
              <view class="slide-list">
                <view
                  v-for="s in TIME_SLOTS"
                  :key="s.key"
                  class="slide-item"
                  :class="{ active: scheduleForm.timeSlot === s.key }"
                  @click="pickFormSlot(s.key)"
                >
                  <view class="slide-item-main">
                    <text class="slide-item-label">{{ s.label }}</text>
                    <text class="slide-item-sub">{{ s.range }}</text>
                  </view>
                  <SvgIcon v-if="scheduleForm.timeSlot === s.key" name="check" :size="18" color="#165DFF" />
                </view>
              </view>
            </view>

            <!-- Slide 3：锁定类型选择 -->
            <view class="sheet-slide" :class="{ active: slideIndex === 3 }">
              <view class="slide-head">
                <view class="slide-back" @click="goSlide(0)">
                  <SvgIcon name="caretLeft" :size="18" color="#4E5969" />
                </view>
                <text class="slide-title">选择锁定类型</text>
                <view class="slide-head-spacer" />
              </view>
              <view class="slide-list">
                <view
                  v-for="t in lockTypes"
                  :key="t.value"
                  class="slide-item"
                  :class="{ active: scheduleForm.lockType === t.value }"
                  @click="pickFormLock(t.value)"
                >
                  <view class="slide-item-main">
                    <text class="slide-item-label">{{ t.label }}</text>
                  </view>
                  <SvgIcon v-if="scheduleForm.lockType === t.value" name="check" :size="18" color="#165DFF" />
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRepairStore } from '@/stores/repair'
import { useAuthStore } from '@/stores/auth'
import PageNavbar from '@/components/PageNavbar.vue'
import ScheduleTable from '@/components/ScheduleTable.vue'
import OrderCard from '@/components/OrderCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import DatePickerSheet from '@/components/DatePickerSheet.vue'
import SvgIcon from '@/components/SvgIcon.vue'
import { TIME_SLOTS, statusKey, durationLabel } from '@/utils/repair-status'
import { useScrollHide } from '@/utils/useScrollHide'

const repairStore = useRepairStore()
const authStore = useAuthStore()
const { scrolled, onScroll } = useScrollHide()

const activeTab = ref('calendar')
const engineers = ref([])
const selectedEngineer = ref(null)
const selectedEngineerId = ref('')
const currentEngineer = ref('')
const scheduleList = ref([])
const allScheduleMap = ref({})
const orderList = ref([])

// ── 日期工具（本地时区安全）──
const pad = (n) => String(n).padStart(2, '0')
const fmtLocal = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
function todayStr() { return fmtLocal(new Date()) }
function parseLocal(s) {
  if (!s) return null
  const m = String(s).match(/(\d{4})-(\d{1,2})-(\d{1,2})/)
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : null
}
function getMonday(d = new Date()) {
  const d2 = new Date(d.getFullYear(), d.getMonth(), d.getDate())
  const day = d2.getDay() || 7
  d2.setDate(d2.getDate() - day + 1)
  return fmtLocal(d2)
}
function addDays(dateStr, n) {
  const d = parseLocal(dateStr)
  d.setDate(d.getDate() + n)
  return fmtLocal(d)
}

const weekStart = ref(getMonday())
const selectedDate = ref(todayStr())
const weekEnd = computed(() => addDays(weekStart.value, 6))

// ── 时段 / 锁定类型 映射 ──
const slotByKey = (key) => TIME_SLOTS.find((s) => s.key === key)
const slotLabel = (key) => slotByKey(key)?.label || key || '全天'
const slotRange = (key) => slotByKey(key)?.range || ''

const lockTypes = [
  { value: 'training', label: '培训' },
  { value: 'onsite', label: '驻场' },
  { value: 'leave', label: '请假' },
  { value: 'other', label: '其他' },
]
const lockTypeLabel = (v) => lockTypes.find((t) => t.value === v)?.label || v || '其他'
const isLock = (item) => item && item.status === '已锁定'

// ── 工程师选择 ──
const showEngineerPanel = ref(false)
const AVATAR_GRADIENTS = [
  'linear-gradient(135deg, #165DFF, #4080FF)',
  'linear-gradient(135deg, #722ED1, #9254DE)',
  'linear-gradient(135deg, #00B42A, #23C343)',
  'linear-gradient(135deg, #FF7D00, #FF9A2E)',
]
const avatarChar = (eng) => (eng?.name || eng?.realName || eng?.username || '?').charAt(0)
const avatarGradient = (i) => AVATAR_GRADIENTS[i % AVATAR_GRADIENTS.length]
const skillsText = (eng) => {
  const s = eng?.skills
  if (Array.isArray(s) && s.length) return s.join(' · ')
  return eng?.desc || '暂无技能标签'
}

// 本周负载 / 本周排单量（依据当前查看周）
const weeklyLoad = (engId) => {
  const list = allScheduleMap.value[engId] || []
  const occupied = list.filter((s) => {
    const inWeek = s.date >= weekStart.value && s.date <= weekEnd.value
    const hasSlot = s.timeSlot && s.timeSlot !== '全天'
    const active = !['已结束', '已完成', '已归档'].includes(s.status)
    return inWeek && hasSlot && active
  }).length
  return Math.min(100, Math.round((occupied / 35) * 100))
}
const loadColor = (pct) => (pct < 50 ? '#00B42A' : pct < 75 ? '#FF7D00' : '#F53F3F')

const engineerDesc = computed(() => {
  const list = allScheduleMap.value[selectedEngineerId.value] || []
  const n = list.filter((s) => s.date >= weekStart.value && s.date <= weekEnd.value && s.type === 'business').length
  const id = selectedEngineer.value?.username || ''
  const parts = []
  if (id) parts.push(`工号 ${id}`)
  parts.push(`本周已排 ${n} 单`)
  return parts.join(' · ')
})

// ── 当日排期列表 ──
const selectedDayList = computed(() => {
  const date = selectedDate.value
  if (!date) return []
  return scheduleList.value.filter((s) => s.date === date)
})
const dayTitle = computed(() => {
  const d = parseLocal(selectedDate.value || todayStr())
  const wd = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()]
  return `${d.getMonth() + 1}月${d.getDate()}日 周${wd}排期`
})
const itemTitle = (item) => {
  if (isLock(item)) return item.note || lockTypeLabel(item.type)
  return item.company || item.orderNo || '未命名工单'
}

// 能否调整排期：管理员全局；工程师仅本人当天
const canReorder = computed(() => {
  if (authStore.isAdmin) return true
  const myId = authStore.userInfo?.id || authStore.userInfo?._id || ''
  return authStore.isEngineer && !!myId && myId === selectedEngineerId.value
})

// 单条排期是否可挪动：工单完结后（待确认/已完成/已归档/已取消）或排期已结束/锁定，隐藏挪动按钮
const canReorderItem = (item) => {
  if (!item || isLock(item)) return false
  if (!item.repairId) return false
  if (item.status !== '处理中') return false
  const rs = item.repairStatus || ''
  if (rs && rs !== '处理中') return false
  return true
}

// ── 数据加载 ──
const loadScheduleData = async () => {
  try {
    const all = await repairStore.fetchSchedule({})
    const arr = Array.isArray(all) ? all : []
    const map = {}
    for (const s of arr) {
      const id = s.engineerId || ''
      if (!id) continue
      if (!map[id]) map[id] = []
      map[id].push(s)
    }
    allScheduleMap.value = map
  } catch {
    allScheduleMap.value = {}
  }
  scheduleList.value = allScheduleMap.value[selectedEngineerId.value] || []
}

// ── 工单列表时间筛选 + 懒加载 ──
const orderRange = ref('week')
const customStart = ref('')
const customEnd = ref('')
const showStartDateSheet = ref(false)
const showEndDateSheet = ref(false)
const orderPage = ref(1)
const orderLoading = ref(false)
const orderNoMore = ref(false)
const PAGE_SIZE = 20

const rangeOptions = [
  { label: '近一周', value: 'week' },
  { label: '近一月', value: 'month' },
  { label: '近三月', value: 'quarter' },
  { label: '自定义', value: 'custom' },
]

const computeRange = () => {
  const end = new Date()
  if (orderRange.value === 'custom') {
    return { startDate: customStart.value || '', endDate: customEnd.value || '' }
  }
  const days = orderRange.value === 'week' ? 7 : orderRange.value === 'month' ? 30 : 90
  const start = new Date()
  start.setDate(start.getDate() - days + 1)
  return { startDate: fmtLocal(start), endDate: fmtLocal(end) }
}

const loadOrders = async (reset = true) => {
  if (reset) {
    orderPage.value = 1
    orderNoMore.value = false
  }
  orderLoading.value = true
  try {
    const { startDate, endDate } = computeRange()
    const data = await repairStore.fetchAllOrders({
      engineerId: selectedEngineerId.value,
      startDate,
      endDate,
      page: orderPage.value,
      pageSize: PAGE_SIZE,
    })
    const items = Array.isArray(data) ? data : (data?.records || data?.list || [])
    orderList.value = reset ? items : orderList.value.concat(items)
    if (items.length < PAGE_SIZE) orderNoMore.value = true
  } catch {
    if (reset) orderList.value = []
  } finally {
    orderLoading.value = false
  }
}

const switchRange = (v) => {
  if (v === orderRange.value) return
  orderRange.value = v
  if (v === 'custom' && !customStart.value) {
    const s = new Date()
    s.setDate(s.getDate() - 6)
    customStart.value = fmtLocal(s)
    customEnd.value = fmtLocal(new Date())
  }
  loadOrders(true)
}

const onCustomStartSelect = (v) => { customStart.value = v; loadOrders(true) }
const onCustomEndSelect = (v) => { customEnd.value = v; loadOrders(true) }

const loadMoreOrders = () => {
  if (orderNoMore.value || orderLoading.value) return
  orderPage.value++
  loadOrders(false)
}

const onScrollLower = () => {
  if (activeTab.value === 'list') loadMoreOrders()
}

const applyEngineer = (eng) => {
  if (!eng) return
  selectedEngineer.value = eng
  selectedEngineerId.value = eng.id || eng._id || ''
  currentEngineer.value = eng.name || eng.realName || eng.username || ''
  scheduleList.value = allScheduleMap.value[selectedEngineerId.value] || []
  loadOrders(true)
}

const loadEngineers = async () => {
  try {
    const list = await repairStore.fetchEngineers()
    engineers.value = Array.isArray(list) ? list : []
  } catch {
    engineers.value = []
  }
  if (!engineers.value.length) return

  let idx = 0
  if (authStore.isEngineer && authStore.userInfo?.username) {
    const found = engineers.value.findIndex((e) => e.username === authStore.userInfo.username)
    if (found >= 0) idx = found
  }
  applyEngineer(engineers.value[idx])
}

const selectEngineer = (eng) => {
  applyEngineer(eng)
  showEngineerPanel.value = false
}

// ── 周切换 / 日期选择 ──
const prevWeek = () => { weekStart.value = addDays(weekStart.value, -7) }
const nextWeek = () => { weekStart.value = addDays(weekStart.value, 7) }
const goToday = () => { weekStart.value = getMonday(); selectedDate.value = todayStr() }
const onSelectDate = (d) => { selectedDate.value = d }

const goDetail = (item) => { uni.navigateTo({ url: `/pages/repair-detail/index?id=${item._id || item.id}&from=schedule` }) }

// ── 排期创建 / 删除 ──
const showScheduleForm = ref(false)
const slideIndex = ref(0)
const scheduleForm = ref({ type: 'business', date: '', timeSlot: 'AM1', company: '', orderId: '', orderNo: '', lockType: 'training', note: '' })
const submittingSchedule = ref(false)

// ── 内联日期日历（横向滑动面板内，与主表单同层级）──
const formWeeks = ['日', '一', '二', '三', '四', '五', '六']
const formViewYear = ref(new Date().getFullYear())
const formViewMonth = ref(new Date().getMonth() + 1)
const formDays = computed(() => {
  const startWeekday = new Date(formViewYear.value, formViewMonth.value - 1, 1).getDay()
  const total = new Date(formViewYear.value, formViewMonth.value, 0).getDate()
  const today = todayStr()
  const cells = []
  for (let i = 0; i < startWeekday; i++) cells.push({ day: '', date: '' })
  for (let d = 1; d <= total; d++) {
    const date = `${formViewYear.value}-${pad(formViewMonth.value)}-${pad(d)}`
    cells.push({ day: d, date, isToday: date === today, selected: date === scheduleForm.value.date, disabled: date < today })
  }
  while (cells.length % 7 !== 0) cells.push({ day: '', date: '' })
  return cells
})
const initFormCalendar = () => {
  const d = parseLocal(scheduleForm.value.date) || new Date()
  formViewYear.value = d.getFullYear()
  formViewMonth.value = d.getMonth() + 1
}
const formPrevMonth = () => {
  if (formViewMonth.value === 1) { formViewMonth.value = 12; formViewYear.value-- }
  else formViewMonth.value--
}
const formNextMonth = () => {
  if (formViewMonth.value === 12) { formViewMonth.value = 1; formViewYear.value++ }
  else formViewMonth.value++
}
const goSlide = (i) => {
  if (i === 1) initFormCalendar()
  slideIndex.value = i
}
const pickFormDate = (d) => {
  if (d.disabled) return
  scheduleForm.value.date = d.date
  slideIndex.value = 0
}
const pickFormToday = () => {
  scheduleForm.value.date = todayStr()
  slideIndex.value = 0
}
const pickFormSlot = (key) => { scheduleForm.value.timeSlot = key; slideIndex.value = 0 }
const pickFormLock = (type) => { scheduleForm.value.lockType = type; slideIndex.value = 0 }
const closeScheduleForm = () => { showScheduleForm.value = false }

const unassignedOrders = ref([])
const orderSearch = ref('')
const filteredUnassignedOrders = computed(() => {
  const kw = orderSearch.value.trim().toLowerCase()
  if (!kw) return unassignedOrders.value
  return unassignedOrders.value.filter((o) =>
    (o.orderNo || '').toLowerCase().includes(kw) ||
    (o.company || '').toLowerCase().includes(kw)
  )
})

const loadUnassignedOrders = async () => {
  try {
    const all = await repairStore.fetchAllOrders({ status: '待接单', pageSize: 100 })
    unassignedOrders.value = Array.isArray(all) ? all : (all?.records || all || [])
  } catch {
    unassignedOrders.value = []
  }
}

const selectOrder = (o) => {
  scheduleForm.value.orderId = o.id || o._id
  scheduleForm.value.orderNo = o.orderNo || ''
}

const openScheduleForm = () => {
  scheduleForm.value = { type: 'business', date: selectedDate.value || todayStr(), timeSlot: 'AM1', company: '', orderId: '', orderNo: '', lockType: 'training', note: '' }
  orderSearch.value = ''
  slideIndex.value = 0
  showScheduleForm.value = true
  loadUnassignedOrders()
}

const submitSchedule = async () => {
  const f = scheduleForm.value
  if (!selectedEngineerId.value) return uni.showToast({ title: '请先选择工程师', icon: 'none' })
  if (!f.date) return uni.showToast({ title: '请选择日期', icon: 'none' })
  if (!f.timeSlot) return uni.showToast({ title: '请选择时段', icon: 'none' })
  if (f.type === 'business') {
    if (!f.orderId) return uni.showToast({ title: '请选择要指派的工单', icon: 'none' })
  } else {
    if (!(f.note || '').trim()) return uni.showToast({ title: '请填写锁定说明', icon: 'none' })
  }
  submittingSchedule.value = true
  try {
    if (f.type === 'business') {
      await repairStore.assignOrder(f.orderId, {
        engineerId: selectedEngineerId.value,
        engineerName: currentEngineer.value,
        timeSlot: f.timeSlot,
        date: f.date,
      })
    } else {
      await repairStore.createScheduleLock({
        engineerId: selectedEngineerId.value,
        engineer: currentEngineer.value,
        date: f.date,
        timeSlot: f.timeSlot,
        type: f.lockType,
        note: (f.note || '').trim(),
      })
    }
    uni.showToast({ title: f.type === 'business' ? '排期已创建' : '异常锁定已创建', icon: 'success' })
    showScheduleForm.value = false
    loadScheduleData()
  } catch { /* handled */ } finally {
    submittingSchedule.value = false
  }
}

const removeSchedule = (item) => {
  const isLockItem = item.status === '已锁定'
  uni.showModal({
    title: isLockItem ? '解除锁定' : '删除排期',
    content: `确定${isLockItem ? '解除' : '删除'} ${item.date} ${slotLabel(item.timeSlot)} 的${isLockItem ? '锁定' : '排期'}吗？`,
    success: async (res) => {
      if (!res.confirm) return
      try {
        if (isLockItem) await repairStore.deleteScheduleLock(item.id)
        else await repairStore.deleteSchedule(item.id)
        uni.showToast({ title: isLockItem ? '锁定已解除' : '排期已删除', icon: 'success' })
        loadScheduleData()
      } catch { /* handled */ }
    }
  })
}

// 排期挪动（置顶/上移/下移/顺延后续）
const reordering = ref(false)
const reorderItem = async (item, direction) => {
  if (!item?.repairId) return
  reordering.value = true
  try {
    await repairStore.reorderRepair(item.repairId, { direction })
    uni.showToast({ title: '排期已调整', icon: 'success' })
    await loadScheduleData()
  } catch { /* handled */ } finally {
    reordering.value = false
  }
}

onMounted(async () => {
  await loadScheduleData()
  await loadEngineers()
})
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}
.scroll-body { flex: 1; }
.safe-bottom { height: 32rpx; }

/* ── 工程师选择器 ── */
.engineer-card {
  margin: 28rpx 32rpx 0;
  background: #fff;
  border-radius: 28rpx;
  padding: 24rpx 28rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}
.eng-avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
  flex-shrink: 0;
}
.eng-info { flex: 1; min-width: 0; }
.eng-name { font-size: 30rpx; font-weight: 600; color: #1D2129; display: block; }
.eng-desc { font-size: 24rpx; color: #86909C; display: block; margin-top: 4rpx; }
.eng-arrow {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F2F3F5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transform: rotate(90deg);
}

/* ── Tab（分段控制器）── */
.page-tabs {
  display: flex;
  margin: 28rpx 32rpx 0;
  background: #F2F3F5;
  border-radius: 20rpx;
  padding: 8rpx;
  flex-shrink: 0;
}
.page-tab {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 28rpx;
  color: #4E5969;
  font-weight: 500;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  transition: all 0.25s ease;
  &.active {
    background: #fff;
    color: #165DFF;
    font-weight: 700;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  }
}

.tab-panel { padding: 28rpx 32rpx 0; }

/* ── 工单列表时间筛选 + 懒加载 ── */
.range-filter {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
  margin-bottom: 20rpx;
}
.range-chip {
  padding: 12rpx 28rpx;
  border-radius: 28rpx;
  font-size: 24rpx;
  color: #4E5969;
  background: #F2F3F5;
  font-weight: 500;
  transition: all 0.2s ease;
  &.active { background: linear-gradient(135deg, #165DFF, #4080FF); color: #fff; font-weight: 600; }
}
.range-custom {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}
.range-date {
  padding: 12rpx 24rpx;
  border-radius: 20rpx;
  background: #F2F3F5;
  font-size: 24rpx;
  color: #4E5969;
}
.range-sep { font-size: 24rpx; color: #86909C; }
.foot-msg {
  text-align: center;
  font-size: 22rpx;
  color: #C9CDD4;
  padding: 24rpx 0;
}

/* ── 当日排期列表 ── */
.day-section { margin-top: 32rpx; }
.day-header { margin-bottom: 24rpx; }
.day-title {
  display: flex;
  align-items: center;
  gap: 16rpx;
  font-size: 32rpx;
  font-weight: 700;
  color: #1D2129;
}
.day-title-bar {
  width: 8rpx;
  height: 36rpx;
  background: linear-gradient(180deg, #165DFF, #4080FF);
  border-radius: 4rpx;
}
.day-count {
  font-size: 24rpx;
  color: #165DFF;
  background: #E8F3FF;
  padding: 4rpx 20rpx;
  border-radius: 20rpx;
  font-weight: 600;
}

.day-list {}
.schedule-item {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
  position: relative;
}
.schedule-item-main { display: flex; gap: 24rpx; }
.time-block {
  width: 140rpx;
  flex-shrink: 0;
  border-radius: 20rpx;
  padding: 20rpx 12rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4rpx;
  &.biz { background: linear-gradient(135deg, #E8F3FF, #D4E6FF); }
  &.lock { background: linear-gradient(135deg, #FFF3E8, #FFE0B8); }
}
.time-period { font-size: 22rpx; color: #165DFF; font-weight: 700; }
.time-block.lock .time-period { color: #FF7D00; }
.time-range { font-size: 20rpx; color: #4E5969; font-weight: 500; }
.time-span { font-size: 18rpx; color: #165DFF; font-weight: 600; margin-top: 2rpx; }
.schedule-info { flex: 1; min-width: 0; }
.schedule-customer { font-size: 30rpx; font-weight: 600; color: #1D2129; margin-bottom: 8rpx; display: block; }
.schedule-meta { display: flex; align-items: center; gap: 20rpx; flex-wrap: wrap; }
.schedule-order { font-size: 22rpx; color: #86909C; font-family: monospace; }
.schedule-escalated {
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  background: #FFF1F0;
  color: #F53F3F;
  font-weight: 600;
}
.schedule-tag {
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  background: #FFF3E8;
  color: #FF7D00;
  font-weight: 500;
}
.schedule-status-tag {
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-weight: 500;
  &.st-pending    { background: #FFF3E8; color: #FF7D00; }
  &.st-reserved   { background: #FFF3E8; color: #FF7D00; }
  &.st-processing { background: #E8F3FF; color: #165DFF; }
  &.st-confirming { background: #F3E8FF; color: #722ED1; }
  &.st-archived   { background: #F2F3F5; color: #86909C; }
  &.st-done       { background: #E8FFEA; color: #00B42A; }
  &.st-cancelled  { background: #F2F3F5; color: #86909C; }
}
.schedule-delete {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #FFF1F0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  align-self: center;
}
.schedule-actions {
  display: flex;
  gap: 12rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #F2F3F5;
}
.reorder-btn {
  flex: 1;
  text-align: center;
  padding: 12rpx 0;
  font-size: 24rpx;
  color: #165DFF;
  background: #E8F3FF;
  border-radius: 12rpx;
  font-weight: 500;
  &:active { opacity: 0.8; }
  &.extend { background: #FFF3E8; color: #FF7D00; }
}
.day-empty { margin-top: 8rpx; }

.view-only-tip {
  margin-top: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #86909C;
  padding: 24rpx 0;
}

/* ── 浮动添加按钮 ── */
.add-btn {
  position: fixed;
  bottom: 40rpx;
  left: 50%;
  transform: translateX(-50%);
  padding: 24rpx 56rpx;
  border-radius: 48rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.35);
  display: flex;
  align-items: center;
  gap: 12rpx;
  z-index: 10;
}

/* ── 弹层通用进入动效 ── */
@keyframes overlay-fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes card-up {
  from { transform: translateY(48%); opacity: 0.6; }
  to { transform: translateY(0); opacity: 1; }
}

/* ── 工程师选择面板 ── */
.panel-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: overlay-fade 0.25s ease;
}
.engineer-panel {
  width: 100%;
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  padding: 24rpx 32rpx calc(24rpx + env(safe-area-inset-bottom));
  max-height: 70%;
  display: flex;
  flex-direction: column;
  animation: card-up 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
.panel-handle {
  width: 80rpx;
  height: 8rpx;
  background: #E5E6EB;
  border-radius: 4rpx;
  margin: 0 auto 24rpx;
}
.panel-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #1D2129;
  text-align: center;
  margin-bottom: 24rpx;
}
.panel-list { max-height: 60vh; }
.panel-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx;
  border-radius: 24rpx;
  margin-bottom: 16rpx;
  border: 1.5px solid transparent;
  &.selected { background: #E8F3FF; border-color: #165DFF; }
  &:not(.selected):active { background: #F7F8FA; }
}
.panel-avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
  flex-shrink: 0;
}
.panel-info { flex: 1; min-width: 0; }
.panel-name-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 4rpx; }
.panel-name { font-size: 30rpx; font-weight: 600; color: #1D2129; }
.panel-id {
  font-size: 22rpx;
  color: #86909C;
  background: #F2F3F5;
  padding: 2rpx 12rpx;
  border-radius: 8rpx;
}
.panel-skills {
  font-size: 24rpx;
  color: #86909C;
  display: block;
  margin-bottom: 12rpx;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.panel-load { display: flex; align-items: center; gap: 12rpx; }
.load-bar {
  width: 120rpx;
  height: 8rpx;
  background: #F2F3F5;
  border-radius: 4rpx;
  overflow: hidden;
  flex-shrink: 0;
}
.load-fill { height: 100%; border-radius: 4rpx; transition: width 0.3s; }
.load-text { font-size: 22rpx; color: #86909C; }
.panel-check {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  border: 2px solid #E5E6EB;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: transparent;
}
.panel-item.selected .panel-check { background: #165DFF; border-color: #165DFF; }

/* ── 添加排期弹窗 ── */
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: overlay-fade 0.25s ease;
}
.popup-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 40rpx 40rpx 0 0;
  overflow: hidden;
  max-height: 82vh;
  display: flex;
  flex-direction: column;
  animation: card-up 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
.popup-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #1D2129;
  text-align: center;
}

/* ── 横向滑动面板（主表单 / 日期 / 时段 / 锁定类型，同一层级）── */
.sheet-viewport { width: 100%; overflow: hidden; }
.sheet-track {
  display: flex;
  width: 400%;
  transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1);
}
.sheet-slide {
  width: 25%;
  flex-shrink: 0;
  box-sizing: border-box;
  max-height: 74vh;
  overflow-y: auto;
  padding: 40rpx 32rpx calc(32rpx + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  opacity: 0.4;
  transform: scale(0.97);
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
  &.active { opacity: 1; transform: scale(1); }
}
.slide-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8rpx;
}
.slide-back {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #F2F3F5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  &:active { background: #E8F3FF; }
}
.slide-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1D2129;
  flex: 1;
  text-align: center;
}
.slide-head-spacer { width: 64rpx; flex-shrink: 0; }

.slide-list { display: flex; flex-direction: column; }
.slide-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 8rpx;
  border-bottom: 1rpx solid #F2F3F5;
  &:active { background: #F7F8FA; }
  &.active { background: #F0F6FF; border-radius: 16rpx; }
}
.slide-item-main { flex: 1; min-width: 0; margin-right: 16rpx; }
.slide-item-label { font-size: 30rpx; color: #1D2129; }
.slide-item.active .slide-item-label { color: #165DFF; font-weight: 600; }
.slide-item-sub { display: block; font-size: 24rpx; color: #86909C; margin-top: 4rpx; }

/* ── 内联日历 ── */
.dp-nav { display: flex; align-items: center; justify-content: space-between; }
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
.dp-week { display: flex; }
.dp-week-item { flex: 1; text-align: center; font-size: 24rpx; color: #86909C; }
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
  box-sizing: border-box;
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
.dp-footer { display: flex; justify-content: center; padding-top: 8rpx; }
.dp-today {
  padding: 16rpx 48rpx;
  border-radius: 40rpx;
  background: #F2F3F5;
  color: #4E5969;
  font-size: 26rpx;
  border: none;
  &:active { opacity: 0.85; }
}

.type-seg {
  display: flex;
  background: #F5F7FA;
  border-radius: 16rpx;
  padding: 6rpx;
  gap: 6rpx;
}
.type-seg-item {
  flex: 1;
  text-align: center;
  padding: 18rpx 0;
  font-size: 26rpx;
  color: #86909C;
  border-radius: 12rpx;
  transition: all 0.25s ease;
  &.active { background: linear-gradient(135deg, #165DFF, #4080FF); color: #fff; font-weight: 600; }
}

.picker {
  width: 100%;
  height: 88rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #4E5969;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  transition: background 0.2s ease, transform 0.15s ease;
  &:active { background: #EEF1F5; transform: scale(0.99); }
}
.picker.dim { color: #C9CDD4; }
.arrow { color: #86909C; transform: rotate(90deg); }

.s-input {
  width: 100%;
  height: 88rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #4E5969;
  box-sizing: border-box;
}

.order-search { margin-top: -4rpx; }
.order-pick-list {
  max-height: 360rpx;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  background: #F7F8FA;
}
.order-pick-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  border-bottom: 1rpx solid #F2F3F5;
  &:last-child { border-bottom: none; }
  &.selected { background: #E8F3FF; }
}
.op-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6rpx; }
.op-no { font-size: 24rpx; color: #4E5969; font-family: monospace; font-weight: 600; }
.op-company { font-size: 24rpx; color: #86909C; max-width: 100%; }
.op-check {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: #165DFF;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: 16rpx;
}
.op-empty {
  padding: 48rpx 0;
  text-align: center;
  font-size: 24rpx;
  color: #86909C;
}

.popup-actions { display: flex; gap: 16rpx; margin-top: 8rpx; }
.btn-cancel, .btn-confirm {
  flex: 1;
  height: 88rpx;
  font-size: 28rpx;
  border-radius: 50rpx;
  line-height: 88rpx;
  text-align: center;
  border: none;
  transition: transform 0.15s ease, opacity 0.15s ease;
}
.btn-cancel { background: #F5F7FA; color: #4E5969; }
.btn-confirm { background: linear-gradient(135deg, #165DFF, #4080FF); color: #FFFFFF; box-shadow: 0 8rpx 24rpx rgba(22, 93, 255, 0.28); }
.btn-confirm[disabled] { background: #C9CDD4; box-shadow: none; }
.btn-cancel:active, .btn-confirm:active { transform: scale(0.97); opacity: 0.9; }
</style>
