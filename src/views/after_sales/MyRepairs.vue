<template>
  <div class="my-repairs-container">
    <el-card shadow="never">
      <template #header>
        <div class="header-flex">
          <span class="card-title">我的报修进度查询</span>
          <el-button type="primary" size="small" @click="handleNewRepair">+ 发起新报修</el-button>
        </div>
      </template>

      <!-- 简洁的列表 -->
      <el-table :data="myOrders" style="width: 100%" border stripe v-loading="loading">
        <el-table-column prop="orderNo" label="工单编号" width="140" />
        <el-table-column prop="company" label="报修内容" min-width="150" />
        <el-table-column label="负责工程师" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.engineer" effect="plain" type="info">{{ row.engineer }}</el-tag>
            <span v-else style="color: #909399; font-size: 12px;">待指派</span>
          </template>
        </el-table-column>
        <el-table-column label="当前状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最新动态" min-width="200">
          <template #default="{ row }">
            <span class="latest-node">{{ getCurrentNode(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewProgress(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper" style="margin-top: 16px; display: flex; justify-content: flex-end;">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          v-model:current-page="query.page"
          v-model:page-size="query.size"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情弹窗：侧重进度追踪 -->
    <el-dialog v-model="detailsVisible" title="工单实时进度" width="500px" destroy-on-close>
      <div v-if="activeOrder" class="progress-details">
        <!-- 顶部摘要 -->
        <div class="order-summary">
          <div class="summary-item"><strong>报修编号：</strong>{{ activeOrder.orderNo }}</div>
          <div class="summary-item"><strong>报修日期：</strong>{{ activeOrder.date }}</div>
        </div>

        <el-divider content-position="left">处理时间轴</el-divider>
        
        <!-- 时间线：直观展示进度 -->
        <el-timeline style="margin-top: 20px">
          <el-timeline-item
            v-for="(step, index) in activeOrder.progress"
            :key="index"
            :type="step.status === 'done' ? 'success' : 'primary'"
            :timestamp="step.time"
            :hollow="step.status === 'doing'"
          >
            <h4 style="margin: 0">{{ step.node }}</h4>
            <p v-if="step.operator" style="font-size: 12px; color: #909399; margin-top: 5px">
              操作人：{{ step.operator }}
            </p>
          </el-timeline-item>
        </el-timeline>

        <div v-if="activeOrder.status === '待指派'" class="waiting-area">
          <el-result icon="info" title="等待后台派单中" sub-title="您的报修已提交，管理员将尽快安排工程师。">
          </el-result>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMyRepairs, getRepairDetail } from '@/api/modules/repairs'

const router = useRouter()
const detailsVisible = ref(false)
const activeOrder = ref(null)
const myOrders = ref([])
const loading = ref(false)
const total = ref(0)
const query = ref({ page: 1, size: 10 })

const fetchMyRepairs = async () => {
  loading.value = true
  try {
    const res = await getMyRepairs({ page: query.value.page, size: query.value.size })
    if (Array.isArray(res)) {
      myOrders.value = res
    } else {
      myOrders.value = res.records || []
      total.value = res.total || 0
    }
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    loading.value = false
  }
}

const viewProgress = async (row) => {
  try {
    const detail = await getRepairDetail(row.id)
    activeOrder.value = detail
    detailsVisible.value = true
  } catch {
    // 兜底使用列表数据
    activeOrder.value = row
    detailsVisible.value = true
  }
}

const getStatusTag = (status) => {
  if (status === '已完成') return 'success'
  if (status === '处理中') return 'primary'
  return 'info'
}

const getCurrentNode = (row) => {
  if (!row.progress || row.progress.length === 0) return '已提交报修'
  return row.progress[row.progress.length - 1].node
}

const handleNewRepair = () => {
  router.push('/after_sales/repair-apply')
}

const handlePageChange = (page) => {
  query.value.page = page
  fetchMyRepairs()
}

onMounted(() => {
  fetchMyRepairs()
})
</script>

<style scoped>
.header-flex { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: bold; color: #303133; }
.latest-node { font-size: 13px; color: #606266; }
.order-summary { background: #f8f9fb; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
.summary-item { font-size: 14px; margin-bottom: 8px; }
.progress-details { padding: 0 10px; }
.waiting-area { padding: 20px 0; }
</style>