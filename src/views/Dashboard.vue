<template>
  <div class="dashboard-container page-enter">
    <!-- ═══ KPI 卡片行（按角色渲染）═══ -->
    <div class="kpi-grid">
      <div
        v-for="(item, i) in kpis"
        :key="item.title"
        class="kpi-card card-lift"
        :style="{ animationDelay: `${i * 80}ms` }"
      >
        <div class="kpi-icon" :class="item.colorClass">
          <el-icon :size="22"><component :is="item.icon" /></el-icon>
        </div>
        <div class="kpi-info">
          <span class="kpi-label">{{ item.title }}</span>
          <span class="kpi-value kpi-number">{{ display(item) }}</span>
        </div>
      </div>
    </div>

    <!-- ═══ 图表 + 右侧栏 ═══ -->
    <div class="content-grid">
      <!-- 图表 -->
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">业务趋势 (近7天)</h3>
          <el-radio-group v-model="chartType" size="small">
            <el-radio-button v-for="opt in chartOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
        </div>
        <div ref="chartRef" class="chart-body"></div>
      </div>

      <!-- 快捷操作 + 待办 -->
      <div class="side-section">
        <div class="section-card">
          <div class="section-header">
            <h3 class="section-title">快捷操作</h3>
          </div>
          <div class="quick-actions">
            <button
              v-for="a in quickActions"
              :key="a.text"
              :class="['quick-btn', `quick-btn--${a.color || 'primary'}`]"
              @click="$router.push(a.path)"
            >
              <el-icon><component :is="a.icon" /></el-icon>
              <span>{{ a.text }}</span>
            </button>
          </div>
        </div>

        <div class="section-card" style="margin-top: var(--space-xl)">
          <div class="section-header">
            <h3 class="section-title">待办事项</h3>
          </div>
          <ul class="todo-list" v-if="todoItems.length">
            <li
              v-for="(item, idx) in todoItems"
              :key="idx"
              class="todo-item"
              :class="item.type"
              @click="item.link && $router.push(item.link)"
            >
              <span class="todo-dot"></span>
              <span class="todo-text">{{ item.text }}</span>
              <el-tag :type="item.type === 'danger' ? 'danger' : 'warning'" size="small" effect="light">
                {{ item.tag || '待处理' }}
              </el-tag>
            </li>
          </ul>
          <div v-else class="todo-empty">
            <el-icon :size="40" color="#CBD5E1"><SuccessFilled /></el-icon>
            <p>暂无待办事项</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ 成本概览 + 今日排期 ═══ -->
    <div class="bottom-grid">
      <div v-if="showCost" class="section-card cost-card">
        <div class="section-header">
          <h3 class="section-title">成本概览（已结工单）</h3>
        </div>
        <div class="cost-metrics">
          <div class="cost-metric">
            <span class="cost-label">本月成本</span>
            <span class="cost-value">￥{{ fmtMoney(cost.monthTotal) }}</span>
          </div>
          <div class="cost-metric">
            <span class="cost-label">累计成本</span>
            <span class="cost-value">￥{{ fmtMoney(cost.grandTotal) }}</span>
          </div>
          <div class="cost-metric">
            <span class="cost-label">已归档</span>
            <span class="cost-value">{{ cost.archivedCount || 0 }} 单</span>
          </div>
          <div class="cost-metric">
            <span class="cost-label">待确认</span>
            <span class="cost-value">{{ cost.pendingConfirm || 0 }} 单</span>
          </div>
        </div>
        <div class="cost-modes">
          <div v-for="m in cost.byMode" :key="m.name" class="cost-mode">
            <div class="mode-head">
              <span>{{ m.name }}</span>
              <span>￥{{ fmtMoney(m.value) }}</span>
            </div>
            <el-progress
              :percentage="modePercent(m.value)"
              :stroke-width="8"
              :show-text="false"
              :color="m.name === '已协商好' ? '#059669' : '#D97706'"
            />
          </div>
        </div>
      </div>

      <div v-if="showSchedule" class="section-card schedule-card">
        <div class="section-header">
          <h3 class="section-title">今日排期</h3>
          <el-tag size="small" type="info" effect="plain">{{ scheduleToday.length }} 项</el-tag>
        </div>
        <div v-if="scheduleToday.length" class="schedule-strip">
          <div v-for="s in scheduleToday" :key="s.id" class="schedule-item" :class="s.type">
            <span class="sched-slot">{{ slotLabel(s.timeSlot) }}</span>
            <span class="sched-eng">{{ s.engineer || '未指派' }}</span>
            <span class="sched-company">{{ s.company || '内部锁定' }}</span>
          </div>
        </div>
        <div v-else class="todo-empty">
          <el-icon :size="40" color="#CBD5E1"><Calendar /></el-icon>
          <p>今日暂无排期</p>
        </div>
      </div>

      <div v-if="showVehicles" class="section-card vehicle-card">
        <div class="section-header">
          <h3 class="section-title">车辆到期提醒</h3>
          <el-tag size="small" :type="vehicleOverdue ? 'danger' : 'warning'" effect="plain">
            {{ vehicleOverdue ? `${vehicleOverdue} 项逾期` : '暂无逾期' }}
          </el-tag>
        </div>
        <ul v-if="vehicleItems.length" class="vehicle-list">
          <li
            v-for="v in vehicleItems"
            :key="v.plateNo + v.label + v.dueDate"
            class="vehicle-item"
            @click="$router.push('/finance/vehicles')"
          >
            <span class="vehicle-plate">{{ v.plateNo }}</span>
            <span class="vehicle-label">{{ v.label }}</span>
            <span class="vehicle-due">{{ v.dueDate }}</span>
            <el-tag :type="v.level === 'overdue' ? 'danger' : 'warning'" size="small" effect="light">
              {{ v.level === 'overdue' ? `逾期 ${-v.daysLeft} 天` : (v.daysLeft ? `剩 ${v.daysLeft} 天` : '今日到期') }}
            </el-tag>
          </li>
        </ul>
        <div v-else class="todo-empty">
          <el-icon :size="40" color="#CBD5E1"><Van /></el-icon>
          <p>车辆均处于正常状态</p>
        </div>
        <div class="vehicle-foot" @click="$router.push('/finance/vehicles')">
          <span>前往车辆管理</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  Plus, Edit, Calendar, WarningFilled, SuccessFilled, Download,
  UserFilled, Box, Service, Phone, Wallet, Folder, Cpu, List, Files,
  Suitcase, ChatLineRound, Bell, Pointer, Check, CircleCheck, Briefcase,
  Van, ArrowRight
} from '@element-plus/icons-vue'
import { getDashboardStats, getDashboardTodos, getDashboardTrends, getDashboardCost, getScheduleToday } from '@/api/modules/dashboard'
import { hasPerm } from '@/utils/permission'
import { getUserInfo } from '@/utils/auth'

/* ═══ 角色 ═══ */
const roleCode = computed(() => getUserInfo()?.roleCode || 'normal')

/* ═══ KPI 配置（按角色）═══ */
const ADMIN_KPIS = [
  { key: 'userCount', title: '系统用户', icon: UserFilled, colorClass: 'blue' },
  { key: 'repairCount', title: '报修工单', icon: Service, colorClass: 'amber' },
  { key: 'monthCost', title: '本月成本', icon: Wallet, colorClass: 'green', money: true },
  { key: 'pendingLeads', title: '待跟进线索', icon: Phone, colorClass: 'rose' },
]
const KPI_MAP = {
  super_admin: ADMIN_KPIS,
  admin: ADMIN_KPIS,
  finance: [
    { key: 'monthCost', title: '本月成本', icon: Wallet, colorClass: 'green', money: true },
    { key: 'archived', title: '已归档工单', icon: CircleCheck, colorClass: 'indigo' },
    { key: 'pendingConfirm', title: '待确认归档', icon: Check, colorClass: 'amber' },
    { key: 'assetCount', title: '资产总数', icon: Box, colorClass: 'blue' },
  ],
  engineer: [
    { key: 'pendingAssign', title: '待接单', icon: Bell, colorClass: 'rose' },
    { key: 'processing', title: '处理中', icon: Pointer, colorClass: 'blue' },
    { key: 'todaySchedules', title: '今日排期', icon: Calendar, colorClass: 'amber' },
    { key: 'myAssigned', title: '我的工单', icon: List, colorClass: 'indigo' },
  ],
  operation: [
    { key: 'productCount', title: '产品数量', icon: Box, colorClass: 'blue' },
    { key: 'newsCount', title: '新闻数量', icon: ChatLineRound, colorClass: 'indigo' },
    { key: 'caseCount', title: '案例数量', icon: Briefcase, colorClass: 'amber' },
    { key: 'pendingComplaints', title: '待处理投诉', icon: WarningFilled, colorClass: 'rose' },
  ],
  business: [
    { key: 'pendingLeads', title: '待跟进线索', icon: Phone, colorClass: 'rose' },
    { key: 'pendingAssign', title: '待接单', icon: Bell, colorClass: 'amber' },
    { key: 'pendingConfirm', title: '待确认归档', icon: Check, colorClass: 'blue' },
    { key: 'todayRepairs', title: '今日新增工单', icon: Service, colorClass: 'indigo' },
  ],
  normal: [
    { key: 'myCreated', title: '我的报修', icon: Service, colorClass: 'blue' },
    { key: 'processing', title: '处理中', icon: Pointer, colorClass: 'amber' },
    { key: 'pendingConfirm', title: '待确认', icon: Check, colorClass: 'rose' },
    { key: 'archived', title: '已归档', icon: CircleCheck, colorClass: 'green' },
  ],
}
const kpis = computed(() => KPI_MAP[roleCode.value] || KPI_MAP.normal)

/* ═══ 快捷操作（按角色 + 按权限过滤）═══ */
const ADMIN_ACTIONS = [
  { text: '新增产品', icon: Plus, path: '/products', perm: 'products', color: 'primary' },
  { text: '发布新闻', icon: Edit, path: '/news', perm: 'news', color: 'success' },
  { text: '录入报修单', icon: Plus, path: '/after_sales/all-tasks', perm: 'repair:create', color: 'warning' },
  { text: '排班管理', icon: Calendar, path: '/after_sales/schedule', perm: 'repair:schedule', color: 'danger' },
]
const QUICK_MAP = {
  super_admin: ADMIN_ACTIONS,
  admin: ADMIN_ACTIONS,
  finance: [
    { text: '导出工单', icon: Download, path: '/after_sales/all-tasks', perm: 'repair:audit', color: 'primary' },
    { text: '归档调阅', icon: List, path: '/after_sales/all-tasks', perm: 'repair:audit', color: 'success' },
    { text: '共享文件', icon: Folder, path: '/finance/files', perm: 'finance:files', color: 'warning' },
    { text: '资产管理', icon: Cpu, path: '/finance/assets', perm: 'finance:assets', color: 'danger' },
  ],
  engineer: [
    { text: '一键报修', icon: Plus, path: '/after_sales/repair-apply', perm: 'repair:create', color: 'primary' },
    { text: '我的工单', icon: List, path: '/after_sales/my-repairs', perm: 'repair:my', color: 'success' },
    { text: '所有工单', icon: Files, path: '/after_sales/all-tasks', perm: 'repair:all', color: 'warning' },
    { text: '工程师排期', icon: Calendar, path: '/after_sales/schedule', perm: 'repair:schedule', color: 'danger' },
  ],
  operation: [
    { text: '新增产品', icon: Plus, path: '/products', perm: 'products', color: 'primary' },
    { text: '发布新闻', icon: Edit, path: '/news', perm: 'news', color: 'success' },
    { text: '录入案例', icon: Briefcase, path: '/cases', perm: 'cases', color: 'warning' },
    { text: '处理投诉', icon: WarningFilled, path: '/after_sales/complaints', perm: 'complaints', color: 'danger' },
  ],
  business: [
    { text: '录入报修单', icon: Plus, path: '/after_sales/all-tasks', perm: 'repair:create', color: 'primary' },
    { text: '跟进线索', icon: Phone, path: '/leads', perm: 'demand', color: 'success' },
    { text: '确认归档', icon: Check, path: '/after_sales/all-tasks', perm: 'repair:all', color: 'warning' },
    { text: '处理投诉', icon: WarningFilled, path: '/after_sales/complaints', perm: 'complaints', color: 'danger' },
  ],
  normal: [
    { text: '一键报修', icon: Plus, path: '/after_sales/repair-apply', perm: 'repair:create', color: 'primary' },
    { text: '我的报修', icon: List, path: '/after_sales/my-repairs', perm: 'repair:my', color: 'success' },
  ],
}
const quickActions = computed(() => (QUICK_MAP[roleCode.value] || []).filter(a => hasPerm(a.perm)))

/* ═══ 待办（按角色选取哪些类别）═══ */
const TODO_MAP = {
  super_admin: ['repairs', 'confirming', 'leads', 'complaints'],
  admin: ['repairs', 'confirming', 'leads', 'complaints'],
  finance: ['confirming'],
  business: ['confirming', 'leads', 'complaints'],
  engineer: ['repairs'],
  operation: ['complaints'],
  normal: [],
}
const showCost = computed(() => hasPerm('repair:audit'))
const showSchedule = computed(() => hasPerm('repair:schedule') || hasPerm('repair:audit'))

/* ═══ 图表 ═══ */
const chartRef = ref(null)
let chartInstance = null
const trendData = reactive({ dates: [], repairs: [], leads: [], costs: [] })

const chartOptions = computed(() => {
  const opts = [{ value: 'repair', label: '报修量' }]
  if (roleCode.value === 'finance') {
    opts.push({ value: 'cost', label: '成本' })
  } else {
    opts.push({ value: 'leads', label: '需求线索' })
    if (roleCode.value === 'super_admin' || roleCode.value === 'admin') {
      opts.push({ value: 'cost', label: '成本' })
    }
  }
  return opts
})
const chartType = ref(roleCode.value === 'finance' ? 'cost' : 'repair')

const CHART_COLORS = {
  repair: { start: '#0369A1', end: '#38BDF8' },
  leads: { start: '#D97706', end: '#FBBF24' },
  cost: { start: '#047857', end: '#34D399' },
}

// chartType 值（repair/leads/cost）→ trendData 中的实际字段名（repairs/leads/costs）
const CHART_DATA_KEY = {
  repair: 'repairs',
  leads: 'leads',
  cost: 'costs',
}

async function initChart() {
  await nextTick()
  if (!chartRef.value) return
  const echarts = await import('echarts')
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)

  const dates = trendData.dates?.length ? trendData.dates.map(d => (d || '').slice(5)) : []
  const data = trendData[CHART_DATA_KEY[chartType.value]] || []
  const color = CHART_COLORS[chartType.value] || CHART_COLORS.repair

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#E2E8F0',
      textStyle: { color: '#020617', fontSize: 13 },
      boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
    },
    grid: { top: 20, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisTick: { show: false },
      axisLabel: { color: '#64748B', fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F1F5F9', type: 'dashed' } },
      axisLabel: { color: '#64748B', fontSize: 12 },
    },
    series: [{
      data,
      type: 'bar',
      barWidth: 36,
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: color.start }, { offset: 1, color: color.end }] },
      },
      emphasis: { itemStyle: { color: color.start } },
      animationDuration: 800,
      animationEasing: 'cubicOut',
    }],
  })
}
watch(chartType, () => initChart())

/* ═══ 数据 ═══ */
const stats = ref({})
const cost = reactive({ monthTotal: 0, grandTotal: 0, archivedCount: 0, pendingConfirm: 0, byMode: [] })
const todoItems = ref([])
const scheduleToday = ref([])
const vehicleItems = ref([])

const showVehicles = computed(() => hasPerm('finance:vehicle'))
const vehicleOverdue = computed(() => vehicleItems.value.filter(v => v.level === 'overdue').length)

const display = (item) => {
  const v = stats.value[item.key] ?? 0
  if (item.money) return '￥' + Number(v).toLocaleString()
  return Number(v).toLocaleString()
}
const fmtMoney = (v) => Number(v || 0).toLocaleString()
const modePercent = (v) => {
  const total = (cost.byMode || []).reduce((s, m) => s + Number(m.value || 0), 0)
  if (!total) return 0
  return Math.round((Number(v || 0) / total) * 100)
}

const SLOT_LABELS = {
  '全天': '全天', 'AM1': '上午早', 'AM2': '上午晚',
  'PM1': '下午早', 'PM2': '下午中', 'PM3': '下午晚',
}
const slotLabel = (s) => SLOT_LABELS[s] || s || '全天'

async function loadDashboard() {
  try {
    const s = await getDashboardStats()
    if (s) stats.value = s
  } catch { /* ignore */ }

  try {
    const t = await getDashboardTrends()
    if (t && Array.isArray(t.dates)) {
      trendData.dates = t.dates
      trendData.repairs = t.repairs || []
      trendData.leads = t.leads || []
      trendData.costs = t.costs || []
      initChart()
    }
  } catch { /* ignore */ }

  try {
    const todos = await getDashboardTodos()
    if (todos) {
      const cats = TODO_MAP[roleCode.value] || []
      const items = []
      if (cats.includes('repairs')) (todos.repairs || []).forEach(r => items.push({ type: 'danger', tag: '待接单', text: `${r.orderNo} · ${r.company}`, link: '/after_sales/all-tasks' }))
      if (cats.includes('confirming')) (todos.confirming || []).forEach(r => items.push({ type: 'warning', tag: '待确认', text: `${r.orderNo} · ${r.company}`, link: '/after_sales/all-tasks' }))
      if (cats.includes('leads')) (todos.leads || []).forEach(l => items.push({ type: 'warning', tag: '待跟进', text: `${l.name} · ${l.category}`, link: '/leads' }))
      if (cats.includes('complaints')) (todos.complaints || []).forEach(c => items.push({ type: 'danger', tag: '待处理', text: `${c.customer} · ${c.category}`, link: '/after_sales/complaints' }))
      todoItems.value = items
      vehicleItems.value = Array.isArray(todos.vehicles) ? todos.vehicles : []
    }
  } catch { /* ignore */ }

  if (showCost.value) {
    try {
      const c = await getDashboardCost()
      if (c) {
        cost.monthTotal = c.monthTotal || 0
        cost.grandTotal = c.grandTotal || 0
        cost.archivedCount = c.archivedCount || 0
        cost.pendingConfirm = c.pendingConfirm || 0
        cost.byMode = c.byMode || []
      }
    } catch { /* ignore */ }
  }

  if (showSchedule.value) {
    try {
      const s = await getScheduleToday()
      scheduleToday.value = Array.isArray(s) ? s : []
    } catch { /* ignore */ }
  }
}

onMounted(() => {
  loadDashboard()
  initChart()
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* ═══ KPI 卡片 ═══ */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-xl);
  margin-bottom: var(--space-xl);
}

.kpi-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  display: flex;
  align-items: flex-start;
  gap: var(--space-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-card);
  animation: slide-up-fade 0.4s ease-out both;
}

.kpi-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon.blue   { background: #EFF6FF; color: #3B82F6; }
.kpi-icon.indigo { background: #EEF2FF; color: #6366F1; }
.kpi-icon.amber  { background: #FFFBEB; color: #D97706; }
.kpi-icon.rose   { background: #FFF1F2; color: #E11D48; }
.kpi-icon.green  { background: #ECFDF5; color: #059669; }

.kpi-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.kpi-label {
  font-size: var(--text-sm);
  color: var(--text-muted);
  font-weight: var(--font-medium);
}

.kpi-value {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

/* ═══ 双栏布局 ═══ */
.content-grid {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: var(--space-xl);
}

.side-section { display: flex; flex-direction: column; }

.section-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-card);
  padding: var(--space-xl);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

/* ═══ 图表 ═══ */
.chart-body {
  width: 100%;
  height: 320px;
}

/* ═══ 快捷操作 ═══ */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-btn:active { transform: scale(0.97); }

.quick-btn--primary  { background: #EFF6FF; color: #3B82F6; }
.quick-btn--primary:hover  { background: #DBEAFE; }
.quick-btn--success  { background: #ECFDF5; color: #059669; }
.quick-btn--success:hover  { background: #D1FAE5; }
.quick-btn--warning  { background: #FFFBEB; color: #D97706; }
.quick-btn--warning:hover  { background: #FEF3C7; }
.quick-btn--danger   { background: #FEF2F2; color: #DC2626; }
.quick-btn--danger:hover   { background: #FEE2E2; }

/* ═══ 待办列表 ═══ */
.todo-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-sm);
  border-bottom: 1px solid var(--border-color-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.todo-item:hover { background: var(--bg-muted); }

.todo-item:last-child { border-bottom: none; }

.todo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.todo-item.danger .todo-dot  { background: #DC2626; }
.todo-item.warning .todo-dot { background: #D97706; }

.todo-text {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.todo-empty {
  text-align: center;
  padding: var(--space-3xl) 0;
  color: var(--text-muted);
}

.todo-empty p {
  margin-top: var(--space-md);
  font-size: var(--text-base);
}

/* ═══ 底部：成本 + 排期 ═══ */
.bottom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: var(--space-xl);
  margin-top: var(--space-xl);
}

.cost-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.cost-metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: var(--space-md);
  background: var(--bg-muted);
  border-radius: var(--radius-md);
}

.cost-label { font-size: var(--text-xs); color: var(--text-muted); }
.cost-value { font-size: var(--text-xl); font-weight: var(--font-bold); color: var(--text-primary); }

.cost-modes { display: flex; flex-direction: column; gap: var(--space-md); }
.cost-mode { display: flex; flex-direction: column; gap: 8px; }
.mode-head { display: flex; justify-content: space-between; font-size: var(--text-sm); color: var(--text-secondary); }

/* ═══ 今日排期 ═══ */
.schedule-strip { display: flex; flex-direction: column; gap: var(--space-sm); }
.schedule-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  background: var(--bg-muted);
  border-left: 4px solid var(--color-accent);
}
.schedule-item.break { border-left-color: #909399; opacity: 0.75; }
.sched-slot { font-size: var(--text-xs); color: var(--text-muted); width: 56px; flex-shrink: 0; }
.sched-eng { font-weight: var(--font-semibold); color: var(--text-primary); flex-shrink: 0; }
.sched-company { font-size: var(--text-sm); color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ═══ 车辆到期提醒 ═══ */
.vehicle-list { list-style: none; padding: 0; margin: 0; }
.vehicle-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  background: var(--bg-muted);
  margin-bottom: var(--space-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.vehicle-item:hover { background: var(--border-color-light); }
.vehicle-item:last-child { margin-bottom: 0; }
.vehicle-plate { font-weight: var(--font-semibold); color: var(--text-primary); flex-shrink: 0; }
.vehicle-label { font-size: var(--text-sm); color: var(--text-secondary); flex-shrink: 0; }
.vehicle-due { flex: 1; font-size: var(--text-xs); color: var(--text-muted); text-align: right; }
.vehicle-foot {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  font-size: var(--text-sm);
  color: var(--color-accent);
  cursor: pointer;
  transition: color var(--transition-fast);
}
.vehicle-foot:hover { color: var(--color-accent-hover, #0369A1); }

/* ═══ 响应式 ═══ */
@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .content-grid { grid-template-columns: 1fr; }
  .cost-metrics { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .quick-actions { grid-template-columns: 1fr; }
}
</style>
