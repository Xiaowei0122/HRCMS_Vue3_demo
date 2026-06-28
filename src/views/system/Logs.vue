<template>
  <div class="log-container">
    <el-card shadow="never">
      <!-- 搜索工具栏 -->
      <div class="toolbar">
        <el-form :inline="true" :model="logQuery">
          <el-form-item label="操作时间">
            <el-date-picker
              v-model="logQuery.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>
          <el-form-item>
            <el-input v-model="logQuery.user" placeholder="操作人账号" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
            <el-button icon="Refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 日志列表 -->
      <el-table :data="logData" stripe border style="width: 100%" v-loading="loading">
        <el-table-column prop="time" label="操作时间" width="180" sortable />
        <el-table-column prop="user" label="操作人" width="120" />
        <el-table-column prop="module" label="所属模块" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="详细行为" min-width="250" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column prop="result" label="结果" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.result === '成功' ? 'success' : 'danger'" effect="dark">
              {{ row.result }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          v-model:current-page="logQuery.page"
          v-model:page-size="logQuery.size"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { getLogList } from '@/api/modules/logs'

const logQuery = reactive({
  dateRange: [],
  user: '',
  page: 1,
  size: 20
})

const logData = ref([])
const total = ref(0)
const loading = ref(false)

const buildParams = () => {
  const params = {
    page: logQuery.page,
    size: logQuery.size,
    user: logQuery.user || undefined
  }
  if (logQuery.dateRange && logQuery.dateRange.length === 2) {
    params.startDate = logQuery.dateRange[0]
    params.endDate = logQuery.dateRange[1]
  }
  return params
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const params = buildParams()
    const res = await getLogList(params)
    if (Array.isArray(res)) {
      logData.value = res
      total.value = res.length
    } else {
      logData.value = res.records || []
      total.value = res.total || 0
    }
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  logQuery.page = 1
  fetchLogs()
}

const handleReset = () => {
  logQuery.dateRange = []
  logQuery.user = ''
  logQuery.page = 1
  fetchLogs()
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.toolbar { margin-bottom: 20px; border-bottom: 1px solid #f0f2f5; padding-bottom: 10px; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
