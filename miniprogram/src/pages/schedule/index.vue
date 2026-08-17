<!--
  工程师排期 — 周排期 + 工单列表
  与 CMS 保持一致：五个时间段，可指派工单（仅管理员）
-->
<template>
  <view class="page">
    <!-- 工程师选择器 -->
    <view class="engineer-bar">
      <text class="bar-label">工程师</text>
      <picker mode="selector" :range="engineerNames" @change="onEngineerChange">
        <view class="picker">
          <text :class="{ dim: !currentEngineer }">{{ currentEngineer || '请选择' }}</text>
          <SvgIcon name="caretRight" :size="14" class="arrow" />
        </view>
      </picker>
    </view>

    <!-- 子Tab -->
    <view class="sub-tabs">
      <view class="sub-tab" :class="{ active: activeTab === 'calendar' }" @click="activeTab = 'calendar'">
        <SvgIcon name="calendar" :size="18" />
        <text>周排期</text>
      </view>
      <view class="sub-tab" :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">
        <SvgIcon name="clipboard" :size="18" />
        <text>工单列表</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body">
      <view v-show="activeTab === 'calendar'" class="panel">
        <ScheduleTable :schedule-data="scheduleList" :week-start="weekStart" @prev-week="prevWeek" @next-week="nextWeek" />

        <view class="schedule-actions" v-if="authStore.isAdmin">
          <button class="btn-add" @click="openScheduleForm">+ 添加排期</button>
        </view>
        <view v-else class="view-only-tip">
          <SvgIcon name="lock" :size="14" color="#94A3B8" />
          <text>仅管理员可指派工单</text>
        </view>

        <view class="schedule-list" v-if="scheduleList.length">
          <view class="s-item" v-for="item in scheduleList" :key="item.id">
            <view class="s-info">
              <text class="s-date">{{ item.date }}</text>
              <text class="s-slot">{{ slotLabel(item.timeSlot) }}</text>
              <text class="s-company text-ellipsis">{{ item.company }}</text>
            </view>
            <view class="s-del" v-if="authStore.isAdmin" @click="removeSchedule(item)">
              <SvgIcon name="x" :size="16" color="#DC2626" />
            </view>
          </view>
        </view>
      </view>
      <view v-show="activeTab === 'list'" class="panel">
        <OrderCard v-for="item in orderList" :key="item._id || item.id" :order="item" @click="goDetail(item)" />
        <EmptyState v-if="!orderList.length" icon="clipboard" text="暂无工单" sub-text="当前工程师暂无接单记录" />
      </view>
      <view class="safe-bottom" />
    </scroll-view>

    <CustomTabBar />

    <!-- 添加排期弹窗 -->
    <view class="popup-overlay" v-if="showScheduleForm" @click="showScheduleForm = false">
      <view class="popup-card" @click.stop>
        <text class="popup-title">添加排期</text>

        <!-- 类型选择 -->
        <view class="type-seg">
          <view class="type-seg-item" :class="{ active: scheduleForm.type === 'business' }" @click="scheduleForm.type = 'business'">
            业务工单
          </view>
          <view class="type-seg-item" :class="{ active: scheduleForm.type === 'break' }" @click="scheduleForm.type = 'break'">
            异常锁定
          </view>
        </view>

        <!-- 日期 -->
        <picker mode="date" :value="scheduleForm.date" @change="(e) => scheduleForm.date = e.detail.value">
          <view class="picker" :class="{ dim: !scheduleForm.date }">
            <text>{{ scheduleForm.date || '请选择日期' }}</text>
            <SvgIcon name="caretRight" :size="14" class="arrow" />
          </view>
        </picker>

        <!-- 时段（五个时间段） -->
        <picker mode="selector" :range="timeSlotLabels" :value="timeSlotIndex" @change="onTimeSlotChange">
          <view class="picker">
            <text :class="{ dim: !scheduleForm.timeSlot }">{{ slotLabel(scheduleForm.timeSlot) }}</text>
            <SvgIcon name="caretRight" :size="14" class="arrow" />
          </view>
        </picker>

        <!-- 业务工单：搜索并选择未指派工单 -->
        <template v-if="scheduleForm.type === 'business'">
          <view class="order-search">
            <input class="s-input" v-model="orderSearch" placeholder="搜索未指派工单（单位 / 工单号）" placeholder-style="color:#CBD5E1" />
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

        <!-- 异常锁定：手动输入原因 -->
        <template v-else>
          <input class="s-input" v-model="scheduleForm.company" placeholder="锁定原因（如：请假 / 培训 / 外出）" placeholder-style="color:#CBD5E1" />
        </template>

        <view class="popup-actions">
          <button class="btn-cancel" @click="showScheduleForm = false">取消</button>
          <button class="btn-confirm" :disabled="submittingSchedule" @click="submitSchedule">
            {{ submittingSchedule ? '保存中...' : '保存' }}
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRepairStore } from '@/stores/repair'
import { useAuthStore } from '@/stores/auth'
import CustomTabBar from '@/components/CustomTabBar.vue'
import ScheduleTable from '@/components/ScheduleTable.vue'
import OrderCard from '@/components/OrderCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const repairStore = useRepairStore()
const authStore = useAuthStore()
const activeTab = ref('calendar')
const currentEngineer = ref('')
const selectedEngineerId = ref('')
const scheduleList = ref([])
const orderList = ref([])
const weekStart = ref(getMonday())

const engineerNames = computed(() => (repairStore.engineers || []).map(e => e.name || e.realName || '未知'))

// 五个时间段（与 CMS 保持一致）
const timeSlots = [
  { value: 'AM1', label: '上午 (早) 08:30-10:00' },
  { value: 'AM2', label: '上午 (晚) 10:00-11:50' },
  { value: 'PM1', label: '下午 (早) 13:30-15:00' },
  { value: 'PM2', label: '下午 (中) 15:00-16:30' },
  { value: 'PM3', label: '下午 (晚) 16:30-18:00' },
]
const timeSlotLabels = timeSlots.map(s => s.label)
const slotLabel = (v) => timeSlots.find(s => s.value === v)?.label || v

function getMonday(d = new Date()) {
  const day = d.getDay() || 7
  const d2 = new Date(d); d2.setDate(d.getDate() - day + 1)
  return d2.toISOString().slice(0, 10)
}

const prevWeek = () => { const d = new Date(weekStart.value); d.setDate(d.getDate() - 7); weekStart.value = d.toISOString().slice(0, 10); loadSchedule() }
const nextWeek = () => { const d = new Date(weekStart.value); d.setDate(d.getDate() + 7); weekStart.value = d.toISOString().slice(0, 10); loadSchedule() }

const onEngineerChange = (e) => {
  const idx = e.detail.value
  currentEngineer.value = engineerNames.value[idx]
  const eng = repairStore.engineers[idx]
  selectedEngineerId.value = eng?._id || eng?.id || ''
  loadSchedule(); loadOrders()
}

const loadSchedule = async () => {
  try { const data = await repairStore.fetchSchedule({ engineerId: selectedEngineerId.value }); scheduleList.value = Array.isArray(data) ? data : [] } catch {}
}
const loadOrders = async () => {
  try { const all = await repairStore.fetchAllOrders({ engineerId: selectedEngineerId.value }); orderList.value = Array.isArray(all) ? all : (all?.list || []) } catch {}
}
const goDetail = (item) => { uni.navigateTo({ url: `/pages/repair-detail/index?id=${item._id || item.id}` }) }

const loadEngineers = async () => {
  await repairStore.fetchEngineers()
  const list = repairStore.engineers || []
  if (!list.length) return

  // 工程师登录时默认定位到自己的排期（按 username 关联）
  let idx = 0
  if (authStore.isEngineer && authStore.userInfo?.username) {
    const found = list.findIndex(e => e.username === authStore.userInfo.username)
    if (found >= 0) idx = found
  }

  currentEngineer.value = list[idx].name || list[idx].realName
  selectedEngineerId.value = list[idx]._id || list[idx].id
  loadSchedule(); loadOrders()
}

// ── 排期创建 / 删除 ──
const showScheduleForm = ref(false)
const scheduleForm = ref({ type: 'business', date: '', timeSlot: 'AM1', company: '', orderId: '', orderNo: '' })
const submittingSchedule = ref(false)

// 未指派工单搜索
const unassignedOrders = ref([])
const orderSearch = ref('')
const filteredUnassignedOrders = computed(() => {
  const kw = orderSearch.value.trim().toLowerCase()
  if (!kw) return unassignedOrders.value
  return unassignedOrders.value.filter(o =>
    (o.orderNo || '').toLowerCase().includes(kw) ||
    (o.company || '').toLowerCase().includes(kw)
  )
})

const timeSlotIndex = computed(() => {
  const i = timeSlots.findIndex(s => s.value === scheduleForm.value.timeSlot)
  return i < 0 ? 0 : i
})

const onTimeSlotChange = (e) => {
  scheduleForm.value.timeSlot = timeSlots[e.detail.value]?.value || 'AM1'
}

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
  scheduleForm.value = { type: 'business', date: weekStart.value, timeSlot: 'AM1', company: '', orderId: '', orderNo: '' }
  orderSearch.value = ''
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
    if (!f.company.trim()) return uni.showToast({ title: '请填写锁定原因', icon: 'none' })
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
      await repairStore.createSchedule({
        engineerId: selectedEngineerId.value,
        engineer: currentEngineer.value,
        date: f.date,
        timeSlot: f.timeSlot,
        type: 'break',
        company: f.company.trim(),
        status: '处理中',
      })
    }
    uni.showToast({ title: '排期已创建', icon: 'success' })
    showScheduleForm.value = false
    loadSchedule()
  } catch { /* handled */ } finally {
    submittingSchedule.value = false
  }
}

const removeSchedule = (item) => {
  uni.showModal({
    title: '删除排期',
    content: `确定删除 ${item.date} ${slotLabel(item.timeSlot)} 的排期吗？`,
    success: async (res) => {
      if (!res.confirm) return
      try {
        await repairStore.deleteSchedule(item.id)
        uni.showToast({ title: '排期已删除', icon: 'success' })
        loadSchedule()
      } catch { /* handled */ }
    }
  })
}

watch(activeTab, (v) => { v === 'calendar' ? loadSchedule() : loadOrders() })
onMounted(() => { loadEngineers() })
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: #F8FAFC;
  display: flex;
  flex-direction: column;
}

/* 工程师选择 */
.engineer-bar {
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  background: #fff;
  flex-shrink: 0;
}
.bar-label { font-size: 26rpx; color: #334155; margin-right: 16rpx; flex-shrink: 0; font-weight: 500; }
.picker {
  flex: 1;
  display: flex; align-items: center; justify-content: space-between;
  height: 64rpx; padding: 0 20rpx;
  background: #F1F5F9; border-radius: 8rpx;
  font-size: 26rpx; color: #334155;
}
.dim { color: #94A3B8; }
.arrow { color: #94A3B8; transform: rotate(90deg); }

/* 子Tab */
.sub-tabs {
  display: flex; background: #fff; padding: 8rpx 24rpx 16rpx; gap: 16rpx; flex-shrink: 0;
}
.sub-tab {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 8rpx;
  padding: 16rpx 0; font-size: 26rpx; color: #64748B;
  background: #F1F5F9; border-radius: 10rpx;
  transition: all 0.25s ease;

  &.active { background: #0F172A; color: #fff; font-weight: 600; }
  &:active { transform: scale(.96); }
}

.scroll-body { flex: 1; }
.panel { animation: fadeIn .25s ease; padding: 16rpx 24rpx; }
.safe-bottom { height: 32rpx; }

/* 排期创建 / 列表 */
.schedule-actions { margin-top: 16rpx; }

.btn-add {
  width: 100%;
  height: 76rpx;
  background: #0F172A;
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
  border: none;
  border-radius: 10rpx;
  text-align: center;
  line-height: 76rpx;

  &:active { opacity: 0.9; }
}

.view-only-tip {
  margin-top: 16rpx;
  display: flex; align-items: center; justify-content: center; gap: 8rpx;
  font-size: 24rpx; color: #94A3B8;
  padding: 20rpx 0;
}

.schedule-list { margin-top: 20rpx; }

.s-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 10rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 12rpx;
  box-shadow: 0 1px 3px rgba(2,6,23,0.05);
}

.s-info { display: flex; align-items: center; gap: 16rpx; flex: 1; min-width: 0; }

.s-date { font-size: 26rpx; color: #334155; font-family: monospace; flex-shrink: 0; }
.s-slot { font-size: 22rpx; color: #0369A1; background: #F0F9FF; padding: 2rpx 12rpx; border-radius: 4rpx; flex-shrink: 0; }
.s-company { font-size: 26rpx; color: #64748B; flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }

.s-del { width: 56rpx; height: 56rpx; border-radius: 50%; background: #FEE2E2; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

/* 添加排期弹窗 */
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.popup-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  max-height: 80vh;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #020617;
  text-align: center;
}

/* 类型分段选择 */
.type-seg {
  display: flex;
  background: #F1F5F9;
  border-radius: 10rpx;
  padding: 4rpx;
  gap: 4rpx;
}
.type-seg-item {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  font-size: 26rpx;
  color: #64748B;
  border-radius: 8rpx;
  transition: all 0.25s ease;

  &.active { background: #0F172A; color: #fff; font-weight: 600; }
}

.picker {
  width: 100%;
  height: 80rpx;
  background: #F1F5F9;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #334155;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.s-input {
  width: 100%;
  height: 80rpx;
  background: #F1F5F9;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #334155;
  box-sizing: border-box;
}

/* 未指派工单列表 */
.order-search { margin-top: -4rpx; }
.order-pick-list {
  max-height: 360rpx;
  border: 1px solid #E2E8F0;
  border-radius: 10rpx;
  background: #F8FAFC;
}
.order-pick-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 24rpx;
  border-bottom: 1px solid #EEF2F7;

  &:last-child { border-bottom: none; }
  &.selected { background: #F0F9FF; }
}
.op-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4rpx; }
.op-no { font-size: 24rpx; color: #334155; font-family: monospace; font-weight: 600; }
.op-company { font-size: 24rpx; color: #64748B; max-width: 100%; }
.op-check {
  width: 40rpx; height: 40rpx; border-radius: 50%;
  background: #0369A1; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-left: 16rpx;
}
.op-empty {
  padding: 40rpx 0;
  text-align: center;
  font-size: 24rpx;
  color: #94A3B8;
}

.popup-actions { display: flex; gap: 16rpx; margin-top: 8rpx; }

.btn-cancel, .btn-confirm {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  border-radius: 50rpx;
  line-height: 80rpx;
  text-align: center;
  border: none;
}

.btn-cancel { background: #F1F5F9; color: #334155; }
.btn-confirm { background: #0F172A; color: #FFFFFF; }
.btn-confirm[disabled] { background: #94A3B8; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12rpx); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
