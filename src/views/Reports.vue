<template>
  <div class="reports-container">
    <div class="range-toolbar">
      <el-radio-group v-model="range" size="default" @change="onRangeChange">
        <el-radio-button value="month">本月</el-radio-button>
        <el-radio-button value="quarter">本季</el-radio-button>
        <el-radio-button value="year">本年</el-radio-button>
        <el-radio-button value="custom">自定义</el-radio-button>
      </el-radio-group>
      <el-date-picker
        v-if="range === 'custom'"
        v-model="customRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        size="default"
        style="margin-left: 12px; width: 260px"
        @change="onCustomChange"
      />
    </div>
    <el-tabs v-model="activeTab" class="report-tabs">
      <!-- ═══ 总览 ═══ -->
      <el-tab-pane label="总览" name="summary">
        <div v-for="g in kpiGroups" :key="g.title" class="group-section" @click="activeTab = g.targetTab">
          <h3 class="group-title">
            {{ g.title }}
            <span class="group-more">查看 <el-icon><ArrowRight /></el-icon></span>
          </h3>
          <div class="kpi-grid">
            <div v-for="k in g.items" :key="k.label" class="kpi-card">
              <span class="kpi-label">{{ k.label }}</span>
              <span class="kpi-value" :style="{ color: k.color }">
                {{ k.value }}
                <span v-if="k.mom !== null && k.mom !== undefined" class="kpi-mom" :class="k.mom >= 0 ? 'up' : 'down'">
                  {{ k.mom >= 0 ? '↑' : '↓' }}{{ Math.abs(k.mom) }}%
                </span>
              </span>
            </div>
          </div>
        </div>

        <div class="section-card">
          <h3 class="section-title">近 30 天综合趋势</h3>
          <div ref="summaryTrendRef" class="chart-body"></div>
        </div>

        <div class="two-col">
          <div class="section-card">
            <h3 class="section-title">工单状态分布</h3>
            <div class="inprogress-total">在途合计：{{ inprogressTotal }}</div>
            <div v-for="s in summary.statusDist" :key="s.name" class="dist-row">
              <span class="dist-name">{{ s.name }}</span>
              <el-progress :percentage="distPercent(summary.statusDist, s.value)" :stroke-width="14" :color="statusColor(s.name)" />
              <span class="dist-count">{{ s.value }} ({{ distPercent(summary.statusDist, s.value) }}%)</span>
            </div>
          </div>

          <div class="section-card">
            <h3 class="section-title">待办清单</h3>
            <template v-if="hasTodos">
              <div v-if="summary.todos.repairs.length" class="todo-block">
                <div class="todo-head">待接单工单</div>
                <div v-for="t in summary.todos.repairs" :key="t.id" class="todo-item" @click="goTodo('/after_sales/all-tasks')">
                  <span class="todo-title">{{ t.orderNo || '工单' }} · {{ t.company }}</span>
                </div>
              </div>
              <div v-if="summary.todos.confirming.length" class="todo-block">
                <div class="todo-head">待确认归档</div>
                <div v-for="t in summary.todos.confirming" :key="t.id" class="todo-item" @click="goTodo('/after_sales/all-tasks')">
                  <span class="todo-title">{{ t.orderNo || '工单' }} · {{ t.company }}</span>
                </div>
              </div>
              <div v-if="summary.todos.leads.length" class="todo-block">
                <div class="todo-head">待跟进线索</div>
                <div v-for="t in summary.todos.leads" :key="t.id" class="todo-item" @click="goTodo('/leads')">
                  <span class="todo-title">{{ t.name }} · {{ t.category }}</span>
                </div>
              </div>
              <div v-if="summary.todos.complaints.length" class="todo-block">
                <div class="todo-head">待处理投诉</div>
                <div v-for="t in summary.todos.complaints" :key="t.id" class="todo-item" @click="goTodo('/after_sales/complaints')">
                  <span class="todo-title">{{ t.customer }} · {{ t.category }}</span>
                </div>
              </div>
            </template>
            <el-empty v-else description="暂无待办" :image-size="60" />
          </div>
        </div>
      </el-tab-pane>

      <!-- ═══ 工单统计 ═══ -->
      <el-tab-pane label="工单统计" name="repairs">
        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-label">{{ rangeLabel }}完结工单量</span>
            <span class="kpi-value" style="color: #3B82F6">{{ repairs.total }}</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">平均处理时长</span>
            <span class="kpi-value">{{ repairs.avgDurationDays }}<small style="font-size:14px"> 天</small></span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">返修工单数</span>
            <span class="kpi-value" style="color: #D97706">{{ repairs.reworkCount }}</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">活跃工程师</span>
            <span class="kpi-value" style="color: #059669">{{ repairs.activeEngineers }}</span>
          </div>
        </div>

        <div class="section-card">
          <h3 class="section-title">各工程师完结量趋势</h3>
          <div ref="engineerChartRef" class="chart-body"></div>
        </div>

        <div class="two-col">
          <div class="section-card">
            <h3 class="section-title">客户上门次数 Top10</h3>
            <div ref="customerChartRef" class="chart-body"></div>
          </div>
          <div class="section-card">
            <h3 class="section-title">按优先级</h3>
            <div v-for="p in repairs.byPriority" :key="p.name" class="dist-row">
              <span class="dist-name">{{ p.name }}</span>
              <el-progress :percentage="distPercent(repairs.byPriority, p.value)" :stroke-width="12" color="#3B82F6" />
              <span class="dist-count">{{ p.value }}</span>
            </div>
          </div>
        </div>

        <div class="two-col">
          <div class="section-card">
            <h3 class="section-title">按工单类型</h3>
            <div v-for="t in repairs.byWorkOrderType" :key="t.name" class="dist-row">
              <span class="dist-name">{{ t.name }}</span>
              <el-progress :percentage="distPercent(repairs.byWorkOrderType, t.value)" :stroke-width="12" color="#8B5CF6" />
              <span class="dist-count">{{ t.value }}</span>
            </div>
          </div>
          <div class="section-card">
            <h3 class="section-title">按设备类型</h3>
            <div v-for="d in repairs.byDeviceType" :key="d.name" class="dist-row">
              <span class="dist-name">{{ d.name }}</span>
              <el-progress :percentage="distPercent(repairs.byDeviceType, d.value)" :stroke-width="12" color="#0EA5E9" />
              <span class="dist-count">{{ d.value }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ═══ 成本核算 ═══ -->
      <el-tab-pane label="成本核算" name="cost">
        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-label">{{ rangeLabel }}已结成本</span>
            <span class="kpi-value" style="color: #059669">￥{{ money(cost.grand) }}</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">平均客单价</span>
            <span class="kpi-value" style="color: #3B82F6">￥{{ money(cost.avgOrderValue) }}</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">已结工单数</span>
            <span class="kpi-value">{{ cost.settledCount }}</span>
          </div>
        </div>
        <div class="section-card">
          <h3 class="section-title">成本与工单量趋势</h3>
          <div ref="costChartRef" class="chart-body"></div>
        </div>
        <div class="two-col">
          <div class="section-card">
            <h3 class="section-title">按工程师（成本/工单数/单均）</h3>
            <el-table :data="cost.byEngineer" size="small">
              <el-table-column prop="name" label="工程师" />
              <el-table-column label="成本" width="110" align="right">
                <template #default="{ row }">￥{{ money(row.cost) }}</template>
              </el-table-column>
              <el-table-column prop="count" label="工单数" width="80" align="right" />
              <el-table-column label="单均" width="100" align="right">
                <template #default="{ row }">￥{{ money(row.avg) }}</template>
              </el-table-column>
            </el-table>
          </div>
          <div class="section-card">
            <h3 class="section-title">按费用方式</h3>
            <div v-for="m in cost.byMode" :key="m.name" class="dist-row">
              <span class="dist-name">{{ m.name }}</span>
              <span class="dist-count">￥{{ money(m.value) }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ═══ 线索转化 ═══ -->
      <el-tab-pane label="线索转化" name="leads">
        <div class="kpi-grid">
          <div class="kpi-card"><span class="kpi-label">{{ rangeLabel }}线索总数</span><span class="kpi-value">{{ leads.total }}</span></div>
          <div class="kpi-card"><span class="kpi-label">已转化</span><span class="kpi-value" style="color:#059669">{{ leads.converted }}</span></div>
          <div class="kpi-card"><span class="kpi-label">转化率</span><span class="kpi-value" style="color:#3B82F6">{{ leads.conversionRate }}%</span></div>
        </div>
        <div class="section-card">
          <h3 class="section-title">线索量与转化量趋势</h3>
          <div ref="leadsChartRef" class="chart-body"></div>
        </div>
        <div class="two-col">
          <div class="section-card">
            <h3 class="section-title">状态分布</h3>
            <div v-for="s in leads.byStatus" :key="s.name" class="dist-row">
              <span class="dist-name">{{ s.name }}</span>
              <el-progress :percentage="distPercent(leads.byStatus, s.value)" :stroke-width="12" color="#3B82F6" />
              <span class="dist-count">{{ s.value }}</span>
            </div>
          </div>
          <div class="section-card">
            <h3 class="section-title">分类转化率</h3>
            <el-table :data="leads.byCategory" size="small">
              <el-table-column prop="name" label="分类" />
              <el-table-column prop="value" label="线索数" width="80" align="right" />
              <el-table-column prop="converted" label="转化" width="70" align="right" />
              <el-table-column label="转化率" width="90" align="right">
                <template #default="{ row }">{{ row.rate }}%</template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- ═══ 资产盘点 ═══ -->
      <el-tab-pane label="资产盘点" name="assets">
        <div class="kpi-grid">
          <div class="kpi-card"><span class="kpi-label">资产总数</span><span class="kpi-value">{{ assets.total }}</span></div>
        </div>
        <div class="two-col">
          <div class="section-card">
            <h3 class="section-title">分类分布</h3>
            <div v-for="c in assets.byCategory" :key="c.name" class="dist-row">
              <span class="dist-name">{{ c.name }}</span>
              <el-progress :percentage="distPercent(assets.byCategory, c.value)" :stroke-width="12" color="#3B82F6" />
              <span class="dist-count">{{ c.value }}</span>
            </div>
          </div>
          <div class="section-card">
            <h3 class="section-title">状态分布</h3>
            <div v-for="s in assets.byStatus" :key="s.name" class="dist-row">
              <span class="dist-name">{{ s.name }}</span>
              <el-progress :percentage="distPercent(assets.byStatus, s.value)" :stroke-width="12" color="#D97706" />
              <span class="dist-count">{{ s.value }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ═══ 满意度 ═══ -->
      <el-tab-pane label="满意度" name="satisfaction">
        <div class="kpi-grid">
          <div class="kpi-card"><span class="kpi-label">投诉总数</span><span class="kpi-value">{{ satisfaction.total }}</span></div>
          <div class="kpi-card"><span class="kpi-label">已解决</span><span class="kpi-value" style="color:#059669">{{ satisfaction.resolved }}</span></div>
          <div class="kpi-card"><span class="kpi-label">解决率</span><span class="kpi-value" style="color:#3B82F6">{{ satisfaction.resolveRate }}%</span></div>
        </div>
        <div class="section-card">
          <h3 class="section-title">投诉分类分布</h3>
          <div v-for="c in satisfaction.byCategory" :key="c.name" class="dist-row">
            <span class="dist-name">{{ c.name }}</span>
            <el-progress :percentage="distPercent(satisfaction.byCategory, c.value)" :stroke-width="12" color="#DC2626" />
            <span class="dist-count">{{ c.value }}</span>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  getReportSummary, getReportRepairs, getReportCost,
  getReportLeads, getReportAssets, getReportSatisfaction
} from '@/api/modules/reports'

const router = useRouter()

const activeTab = ref('summary')
const range = ref('year')
const customRange = ref([])

const summary = reactive({
  statusDist: [],
  trend: { dates: [], repairs: [], leads: [], costs: [] },
  todos: { repairs: [], confirming: [], leads: [], complaints: [] },
})
const repairs = reactive({
  buckets: [], total: 0, avgDurationDays: 0, reworkCount: 0, activeEngineers: 0,
  engineerSeries: [], topCustomers: [], byPriority: [], byWorkOrderType: [], byDeviceType: []
})
const cost = reactive({ grand: 0, avgOrderValue: 0, settledCount: 0, buckets: [], costMonthly: [], orderMonthly: [], byEngineer: [], byMode: [] })
const leads = reactive({ total: 0, converted: 0, conversionRate: 0, buckets: [], leadSeries: [], convertedSeries: [], byStatus: [], byCategory: [] })
const assets = reactive({ total: 0, byCategory: [], byStatus: [] })
const satisfaction = reactive({ total: 0, resolved: 0, resolveRate: 0, byCategory: [] })

const kpiGroups = computed(() => [
  {
    title: '售后工单', targetTab: 'repairs',
    items: [
      { label: '工单总数', value: summary.repairTotal ?? 0, color: '#3B82F6', mom: summary.repairMoM },
      { label: '待接单', value: summary.pendingAssign ?? 0, color: '#DC2626' },
      { label: '处理中', value: summary.processing ?? 0, color: '#D97706' },
      { label: '待确认', value: summary.pendingConfirm ?? 0, color: '#8B5CF6' },
    ],
  },
  {
    title: '财务', targetTab: 'cost',
    items: [
      { label: '累计已结成本', value: '￥' + money(summary.costTotal), color: '#059669' },
      { label: '本月成本', value: '￥' + money(summary.monthCost), color: '#059669', mom: summary.costMoM },
    ],
  },
  {
    title: '资产', targetTab: 'assets',
    items: [
      { label: '资产总数', value: summary.assetTotal ?? 0, color: '#6366F1' },
    ],
  },
  {
    title: '需求线索', targetTab: 'leads',
    items: [
      { label: '线索总数', value: summary.leadTotal ?? 0, color: '#0EA5E9', mom: summary.leadMoM },
      { label: '待跟进线索', value: summary.pendingLead ?? 0, color: '#DC2626' },
      { label: '投诉待处理', value: summary.pendingComplaint ?? 0, color: '#DC2626' },
    ],
  },
])

const inprogressTotal = computed(() =>
  (summary.pendingAssign ?? 0) + (summary.processing ?? 0) + (summary.pendingConfirm ?? 0)
)

const hasTodos = computed(() =>
  (summary.todos?.repairs?.length || 0) +
  (summary.todos?.confirming?.length || 0) +
  (summary.todos?.leads?.length || 0) +
  (summary.todos?.complaints?.length || 0) > 0
)

const goTodo = (path) => router.push(path)

const money = (v) => Number(v || 0).toLocaleString()

const RANGE_LABELS = { month: '本月', quarter: '本季', year: '本年', custom: '自定义' }
const rangeLabel = computed(() => RANGE_LABELS[range.value] || '本年')

const distPercent = (list, v) => {
  const total = (list || []).reduce((s, x) => s + Number(x.value || 0), 0)
  if (!total) return 0
  return Math.round((Number(v || 0) / total) * 100)
}
const statusColor = (name) => {
  const map = { '待接单': '#DC2626', '处理中': '#D97706', '待确认': '#8B5CF6', '已归档': '#059669' }
  return map[name] || '#3B82F6'
}

// ── 图表 ──
const engineerChartRef = ref(null)
const customerChartRef = ref(null)
const costChartRef = ref(null)
const leadsChartRef = ref(null)
const summaryTrendRef = ref(null)
let engineerChart = null
let customerChart = null
let costChart = null
let leadsChart = null
let summaryTrendChart = null

const renderSummaryTrend = async () => {
  await nextTick()
  if (!summaryTrendRef.value) return
  if (summaryTrendChart) summaryTrendChart.dispose()
  const echarts = await import('echarts')
  summaryTrendChart = echarts.init(summaryTrendRef.value)
  const dates = (summary.trend?.dates || []).map(d => d.slice(5)) // MM-DD
  summaryTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    grid: { top: 40, right: 50, bottom: 30, left: 40 },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: [
      { type: 'value', name: '数量', minInterval: 1 },
      { type: 'value', name: '成本(￥)' },
    ],
    series: [
      { name: '工单量', type: 'line', smooth: true, symbolSize: 5, yAxisIndex: 0, data: summary.trend?.repairs || [], itemStyle: { color: '#3B82F6' } },
      { name: '线索量', type: 'line', smooth: true, symbolSize: 5, yAxisIndex: 0, data: summary.trend?.leads || [], itemStyle: { color: '#0EA5E9' } },
      { name: '成本', type: 'line', smooth: true, symbolSize: 5, yAxisIndex: 1, data: summary.trend?.costs || [], itemStyle: { color: '#059669' } },
    ],
  })
}

const renderCostChart = async () => {
  await nextTick()
  if (!costChartRef.value) return
  if (costChart) costChart.dispose()
  const echarts = await import('echarts')
  costChart = echarts.init(costChartRef.value)
  const buckets = (cost.buckets || []).map(b => (b.length === 7 ? b.slice(2) : b.slice(5)))
  costChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0, data: ['成本', '工单量'] },
    grid: { top: 40, right: 50, bottom: 30, left: 60 },
    xAxis: { type: 'category', data: buckets },
    yAxis: [
      { type: 'value', name: '成本(￥)' },
      { type: 'value', name: '工单量', minInterval: 1 },
    ],
    series: [
      { name: '成本', type: 'bar', barWidth: 24, yAxisIndex: 0, data: cost.costMonthly || [], itemStyle: { color: '#047857' } },
      { name: '工单量', type: 'line', yAxisIndex: 1, smooth: true, symbolSize: 6, data: cost.orderMonthly || [], itemStyle: { color: '#F59E0B' } },
    ],
  })
}

const renderLeadsChart = async () => {
  await nextTick()
  if (!leadsChartRef.value) return
  if (leadsChart) leadsChart.dispose()
  const echarts = await import('echarts')
  leadsChart = echarts.init(leadsChartRef.value)
  const buckets = (leads.buckets || []).map(b => (b.length === 7 ? b.slice(2) : b.slice(5)))
  leadsChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    grid: { top: 40, right: 20, bottom: 30, left: 40 },
    xAxis: { type: 'category', data: buckets, boundaryGap: false },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      { name: '线索量', type: 'line', smooth: true, symbolSize: 6, data: leads.leadSeries || [], itemStyle: { color: '#0EA5E9' } },
      { name: '转化量', type: 'line', smooth: true, symbolSize: 6, data: leads.convertedSeries || [], itemStyle: { color: '#059669' } },
    ],
  })
}

const renderEngineerChart = async () => {
  await nextTick()
  if (!engineerChartRef.value) return
  if (engineerChart) engineerChart.dispose()
  const echarts = await import('echarts')
  engineerChart = echarts.init(engineerChartRef.value)
  // 月度桶显示 YY-MM，日桶显示 MM-DD
  const buckets = (repairs.buckets || []).map(b => (b.length === 7 ? b.slice(2) : b.slice(5)))
  engineerChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    grid: { top: 40, right: 20, bottom: 30, left: 40 },
    xAxis: { type: 'category', data: buckets, boundaryGap: false },
    yAxis: { type: 'value', minInterval: 1 },
    series: (repairs.engineerSeries || []).map(s => ({
      name: s.name,
      type: 'line',
      smooth: true,
      symbolSize: 6,
      data: s.data,
    })),
  })
}

const renderCustomerChart = async () => {
  await nextTick()
  if (!customerChartRef.value) return
  if (customerChart) customerChart.dispose()
  const echarts = await import('echarts')
  customerChart = echarts.init(customerChartRef.value)
  const list = [...(repairs.topCustomers || [])].reverse()
  customerChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 10, right: 30, bottom: 20, left: 120 },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', data: list.map(c => c.name) },
    series: [{
      type: 'bar',
      data: list.map(c => c.value),
      barWidth: 16,
      itemStyle: { color: '#0EA5E9', borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right' },
    }],
  })
}

watch(activeTab, (t) => {
  if (t === 'summary') renderSummaryTrend()
  if (t === 'repairs') { renderEngineerChart(); renderCustomerChart() }
  if (t === 'cost') renderCostChart()
  if (t === 'leads') renderLeadsChart()
})

const buildRangeParams = () => {
  const params = { range: range.value }
  if (range.value === 'custom' && Array.isArray(customRange.value) && customRange.value.length === 2 && customRange.value[0]) {
    params.start = customRange.value[0]
    params.end = customRange.value[1]
  }
  return params
}

const loadRepairs = async () => {
  try {
    const r = await getReportRepairs(buildRangeParams())
    if (r) Object.assign(repairs, r)
    await nextTick()
    if (activeTab.value === 'repairs') {
      renderEngineerChart()
      renderCustomerChart()
    }
  } catch { /* ignore */ }
}

const loadCost = async () => {
  try {
    const c = await getReportCost(buildRangeParams())
    if (c) Object.assign(cost, c)
    await nextTick()
    if (activeTab.value === 'cost') renderCostChart()
  } catch { /* ignore */ }
}

const loadLeads = async () => {
  try {
    const l = await getReportLeads(buildRangeParams())
    if (l) Object.assign(leads, l)
    await nextTick()
    if (activeTab.value === 'leads') renderLeadsChart()
  } catch { /* ignore */ }
}

const loadRangeData = () => {
  loadRepairs()
  loadCost()
  loadLeads()
}

const onRangeChange = () => {
  if (range.value === 'custom') return // 等用户选择日期区间
  loadRangeData()
}

const onCustomChange = () => {
  if (range.value === 'custom' && Array.isArray(customRange.value) && customRange.value.length === 2) {
    loadRangeData()
  }
}

const loadSummary = async () => {
  try {
    const s = await getReportSummary()
    if (s) Object.assign(summary, s)
    await nextTick()
    if (activeTab.value === 'summary') renderSummaryTrend()
  } catch { /* ignore */ }
}

async function loadAll() {
  await loadSummary()
  loadRangeData()
  try {
    const a = await getReportAssets()
    if (a) Object.assign(assets, a)
  } catch { /* ignore */ }
  try {
    const st = await getReportSatisfaction()
    if (st) Object.assign(satisfaction, st)
  } catch { /* ignore */ }
}

onMounted(loadAll)
onUnmounted(() => {
  engineerChart?.dispose()
  customerChart?.dispose()
  costChart?.dispose()
  leadsChart?.dispose()
  summaryTrendChart?.dispose()
})
</script>

<style scoped>
.reports-container { padding: 4px 0; }
.range-toolbar { display: flex; align-items: center; margin-bottom: var(--space-lg); }
.report-tabs :deep(.el-tabs__item) { font-weight: var(--font-medium); }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}
.kpi-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi-label { font-size: var(--text-sm); color: var(--text-muted); }
.kpi-value { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--text-primary); font-variant-numeric: tabular-nums; }

.section-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  padding: var(--space-lg);
  margin-bottom: var(--space-xl);
}
.section-title { margin: 0 0 var(--space-lg); font-size: var(--text-base); font-weight: var(--font-semibold); color: var(--text-primary); }

.dist-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}
.dist-name { width: 80px; flex-shrink: 0; font-size: var(--text-sm); color: var(--text-secondary); }
.dist-count { width: 60px; text-align: right; font-size: var(--text-sm); color: var(--text-primary); font-weight: var(--font-semibold); }

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
}
.chart-body { width: 100%; height: 300px; }

.group-section {
  margin-bottom: var(--space-xl);
  padding: var(--space-lg);
  background: var(--bg-muted);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.group-section:hover { box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06); }
.group-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 0 var(--space-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}
.group-more {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  color: var(--text-muted);
}
.group-section .kpi-grid { margin-bottom: 0; }

.kpi-mom { font-size: var(--text-sm); font-weight: var(--font-semibold); margin-left: 6px; }
.kpi-mom.up { color: #DC2626; }
.kpi-mom.down { color: #059669; }

.inprogress-total {
  margin-bottom: var(--space-lg);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.todo-block { margin-bottom: var(--space-lg); }
.todo-head {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  margin-bottom: var(--space-sm);
  padding-bottom: 4px;
  border-bottom: 1px dashed var(--border-color);
}
.todo-item {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-primary);
  transition: background 0.15s;
}
.todo-item:hover { background: var(--bg-muted); }
.todo-title { font-size: var(--text-sm); }

@media (max-width: 900px) {
  .two-col { grid-template-columns: 1fr; }
}
</style>
