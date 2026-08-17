<template>
  <div class="dashboard-container page-enter">
    <!-- ═══ KPI 卡片行 ═══ -->
    <div class="kpi-grid">
      <div
        v-for="(item, i) in topStats"
        :key="item.title"
        class="kpi-card card-lift"
        :style="{ animationDelay: `${i * 80}ms` }"
      >
        <div class="kpi-icon" :class="item.colorClass">
          <el-icon :size="22"><component :is="item.icon" /></el-icon>
        </div>
        <div class="kpi-info">
          <span class="kpi-label">{{ item.title }}</span>
          <span class="kpi-value kpi-number">{{ item.displayValue }}</span>
          <span class="kpi-trend" :class="item.trend >= 0 ? 'up' : 'down'">
            <el-icon :size="12">
              <CaretTop v-if="item.trend >= 0" />
              <CaretBottom v-else />
            </el-icon>
            {{ Math.abs(item.trend) }}% 较上月
          </span>
        </div>
      </div>
    </div>

    <!-- ═══ 图表 + 待办双栏 ═══ -->
    <div class="content-grid">
      <!-- 图表 -->
      <div class="chart-section">
        <div class="section-card">
          <div class="section-header">
            <h3 class="section-title">业务趋势 (近7天)</h3>
            <el-radio-group v-model="chartType" size="small">
              <el-radio-button value="repair">报修量</el-radio-button>
              <el-radio-button value="leads">需求线索</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="chartRef" class="chart-body"></div>
        </div>
      </div>

      <!-- 待办 + 快捷操作 -->
      <div class="side-section">
        <div class="section-card">
          <div class="section-header">
            <h3 class="section-title">快捷操作</h3>
          </div>
          <div class="quick-actions">
            <button class="quick-btn quick-btn--primary" @click="$router.push('/products')">
              <el-icon><Plus /></el-icon>
              <span>新增产品</span>
            </button>
            <button class="quick-btn quick-btn--success" @click="$router.push('/news')">
              <el-icon><Edit /></el-icon>
              <span>发布新闻</span>
            </button>
            <button class="quick-btn quick-btn--warning" @click="$router.push('/after_sales/schedule')">
              <el-icon><Calendar /></el-icon>
              <span>排班管理</span>
            </button>
            <button class="quick-btn quick-btn--danger" @click="$router.push('/after_sales/complaints')">
              <el-icon><WarningFilled /></el-icon>
              <span>处理投诉</span>
            </button>
          </div>

          <el-divider />

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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  Plus, Edit, Calendar, WarningFilled, SuccessFilled,
  CaretTop, CaretBottom, UserFilled, Box, Service, Phone
} from '@element-plus/icons-vue'
import { getDashboardStats, getDashboardTodos, getDashboardTrends } from '@/api/modules/dashboard'

/* ═══ 图表 ═══ */
const chartType = ref('repair')
const chartRef = ref(null)
let chartInstance = null

// 兜底数据（后端趋势接口不可用时使用）
const fallbackChartData = {
  repair: [40, 60, 45, 80, 55, 70, 85],
  leads: [30, 45, 55, 40, 65, 50, 70],
}

const fallbackLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

// 后端 /dashboard/trends 返回 { dates, repairs, leads }
const trendData = ref({ dates: [], repairs: [], leads: [] })

async function initChart() {
  await nextTick()
  if (!chartRef.value) return
  const echarts = await import('echarts')
  if (chartInstance) chartInstance.dispose()

  chartInstance = echarts.init(chartRef.value)

  const dates = trendData.value.dates?.length
    ? trendData.value.dates.map(d => (d || '').slice(5))
    : fallbackLabels
  const data = trendData.value[chartType.value]?.length
    ? trendData.value[chartType.value]
    : fallbackChartData[chartType.value]
  const isRepair = chartType.value === 'repair'

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#E2E8F0',
      textStyle: { color: '#020617', fontSize: 13 },
      boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
    },
    grid: { top: 20, right: 20, bottom: 30, left: 40 },
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
        color: isRepair
          ? { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [{ offset: 0, color: '#0369A1' }, { offset: 1, color: '#38BDF8' }] }
          : { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [{ offset: 0, color: '#D97706' }, { offset: 1, color: '#FBBF24' }] },
      },
      emphasis: {
        itemStyle: {
          color: isRepair ? '#0369A1' : '#D97706',
        },
      },
      animationDuration: 800,
      animationEasing: 'cubicOut',
    }],
  })
}

watch(chartType, () => initChart())

/* ═══ 数据加载 ═══ */
const topStats = reactive([
  { title: '系统用户', value: 0, displayValue: '0', tag: '总量', tagType: 'primary', trend: 12, colorClass: 'blue', icon: 'UserFilled' },
  { title: '产品数量', value: 0, displayValue: '0', tag: '在售', tagType: 'info', trend: 5, colorClass: 'indigo', icon: 'Box' },
  { title: '报修工单', value: 0, displayValue: '0', tag: '全部', tagType: 'warning', trend: 18, colorClass: 'amber', icon: 'Service' },
  { title: '待跟进线索', value: 0, displayValue: '0', tag: '紧急', tagType: 'danger', trend: -3, colorClass: 'rose', icon: 'Phone' },
])

const todoItems = ref([])

function animateValue(key, target) {
  const item = topStats.find(s => s.title === key)
  if (!item) return
  const duration = 600
  const start = performance.now()
  const from = 0
  const to = target || 0
  function step(now) {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    item.value = Math.round(from + (to - from) * eased)
    item.displayValue = item.value.toLocaleString()
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

async function loadDashboard() {
  try {
    const stats = await getDashboardStats()
    if (stats) {
      animateValue('系统用户', stats.userCount || 0)
      animateValue('产品数量', stats.productCount || 0)
      animateValue('报修工单', stats.repairCount || 0)
      animateValue('待跟进线索', stats.pendingLeads || 0)
    }
  } catch { /* ignore */ }

  try {
    const todos = await getDashboardTodos()
    if (todos) {
      const items = []
      ;(todos.repairs || []).forEach(r => items.push({ type: 'danger', tag: '待接单', text: `${r.orderNo} · ${r.company}`, link: '/after_sales/all-tasks' }))
      ;(todos.leads || []).forEach(l => items.push({ type: 'warning', tag: '待跟进', text: `${l.name} · ${l.category}`, link: '/leads' }))
      ;(todos.complaints || []).forEach(c => items.push({ type: 'danger', tag: '待处理', text: `${c.customer} · ${c.category}`, link: '/after_sales/complaints' }))
      todoItems.value = items
    }
  } catch { /* ignore */ }

  try {
    const trends = await getDashboardTrends()
    if (trends && Array.isArray(trends.dates)) {
      trendData.value = {
        dates: trends.dates,
        repairs: trends.repairs || [],
        leads: trends.leads || [],
      }
      initChart()
    }
  } catch { /* ignore */ }
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

.kpi-trend {
  font-size: var(--text-xs);
  display: flex;
  align-items: center;
  gap: 2px;
}

.kpi-trend.up   { color: var(--color-success); }
.kpi-trend.down { color: var(--color-danger); }

/* ═══ 双栏布局 ═══ */
.content-grid {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: var(--space-xl);
}

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

/* ═══ 响应式 ═══ */
@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .content-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .quick-actions { grid-template-columns: 1fr; }
}
</style>
