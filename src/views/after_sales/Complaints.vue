<template>
  <div class="complaints-manage-container">
    <!-- 顶部数据看板：优化为精美卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="item in statCards" :key="item.title">
        <div class="stat-card" :style="{ borderLeftColor: item.color }">
          <div class="stat-info">
            <div class="stat-title">{{ item.title }}</div>
            <div class="stat-value" :style="{ color: item.color }">{{ item.value }}<span class="unit">{{ item.unit }}</span></div>
          </div>
          <el-icon class="stat-icon" :style="{ color: item.color + '33' }"><component :is="item.icon" /></el-icon>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" class="list-card">
      <template #header>
        <div class="header-flex">
          <div class="left">
            <el-radio-group v-model="activeTab" size="default">
              <el-radio-button label="all">全部投诉</el-radio-button>
              <el-radio-button label="pending">待核实</el-radio-button>
              <el-radio-button label="solving">处理中</el-radio-button>
            </el-radio-group>
          </div>
          <div class="right">
            <el-input v-model="search" placeholder="搜索客户名/工程师..." style="width: 240px" :prefix-icon="Search" clearable />
          </div>
        </div>
      </template>

      <!-- 投诉列表 -->
      <el-table :data="filteredData" border style="width: 100%" :header-cell-style="{ background: '#f8f9fb' }">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <el-descriptions title="投诉详情回溯" :column="2" border>
                <el-descriptions-item label="详细诉求" :span="2">
                  <div class="complaint-text">{{ row.content }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="最终处理方案" :span="2">
                  <div v-if="row.result" class="result-text">{{ row.result }}</div>
                  <el-tag v-else type="info">等待管理员录入方案...</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="date" label="投诉时间" width="170" />
        <el-table-column prop="customer" label="投诉客户" width="160" show-overflow-tooltip />
        <el-table-column prop="target" label="被投诉工程师" width="140">
          <template #default="{ row }">
            <el-tag type="danger" effect="light" size="small">{{ row.target }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <span class="category-dot">{{ row.category }}</span>
          </template>
        </el-table-column>
        <el-table-column label="紧急程度" width="110">
          <template #default="{ row }">
            <el-tag :type="row.priority === '紧急' ? 'danger' : 'info'" size="small" effect="dark">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <div class="status-wrapper">
              <span :class="['dot', row.status === '待处理' ? 'dot-blink' : '']" :style="{ background: getStatusColor(row.status) }"></span>
              <span :style="{ color: getStatusColor(row.status), fontWeight: 'bold' }">{{ row.status }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="160">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleProcess(row)">回访核实</el-button>
            <el-divider direction="vertical" />
            <el-button link type="success" v-if="row.status !== '已关闭'" @click="closeComplaint(row)">结案</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 处理弹窗保持原有功能 -->
    <el-dialog v-model="dialogVisible" title="投诉及建议处理" width="480px" border-radius="8px">
      <el-form label-position="top">
        <el-form-item label="当前投诉对象">
          <el-input :value="activeItem?.customer + ' (针对: ' + activeItem?.target + ')'" disabled />
        </el-form-item>
        <el-form-item label="管理决策">
          <el-select v-model="processForm.type" placeholder="请选择处理动作" style="width: 100%">
            <el-option label="内部警示及教育" value="1" />
            <el-option label="致歉并安排补偿维修" value="2" />
            <el-option label="绩效考核扣除" value="3" />
            <el-option label="判定为非工程师责任" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理结果备注 (将记录在案)">
          <el-input v-model="processForm.note" type="textarea" :rows="4" placeholder="请输入详细的处理过程和沟通结果..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmProcess">录入结果</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Warning, List, Timer, Opportunity } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getComplaintList, processComplaint, closeComplaint as apiCloseComplaint } from '@/api/modules/complaints'

const activeTab = ref('all')
const search = ref('')
const dialogVisible = ref(false)
const activeItem = ref(null)
const processForm = ref({ type: '', note: '' })

// 统计看板数据
const statCards = [
  { title: '待处理投诉', value: '3', unit: '单', color: '#F56C6C', icon: Warning },
  { title: '本月累计投诉', value: '28', unit: '单', color: '#409EFF', icon: List },
  { title: '平均响应耗时', value: '1.2', unit: 'h', color: '#67C23A', icon: Timer },
  { title: '客户整体满意度', value: '96.8', unit: '%', color: '#E6A23C', icon: Opportunity },
]

const complaints = ref([])

const fetchComplaints = async () => {
  try {
    const res = await getComplaintList({ page: 1, size: 50 })
    if (Array.isArray(res)) {
      complaints.value = res
    } else {
      complaints.value = res.records || []
    }
  } catch { /* ignore */ }
}

const filteredData = computed(() => {
  return complaints.value.filter(item => {
    const matchTab = activeTab.value === 'all' ||
                    (activeTab.value === 'pending' && item.status === '待处理') ||
                    (activeTab.value === 'solving' && item.status === '处理中');
    const matchSearch = item.customer?.includes(search.value) || item.target?.includes(search.value);
    return matchTab && matchSearch;
  })
})

const getStatusColor = (status) => {
  if (status === '待处理') return '#F56C6C'
  if (status === '处理中') return '#409EFF'
  return '#909399'
}

const handleProcess = (row) => {
  activeItem.value = row
  dialogVisible.value = true
}

const confirmProcess = async () => {
  if (!processForm.value.type) return ElMessage.warning('请选择处理方案')
  try {
    await processComplaint(activeItem.value.id, { type: processForm.value.type, note: processForm.value.note })
    ElMessage.success('核实结果录入成功')
    dialogVisible.value = false
    fetchComplaints()
  } catch { /* ignore */ }
}

const closeComplaint = (row) => {
  ElMessageBox.confirm('结案后该投诉记录将无法修改方案，确认完成？', '确认结案', {
    type: 'warning',
    confirmButtonText: '立即结案'
  }).then(async () => {
    try {
      await apiCloseComplaint(row.id)
      ElMessage.success('已结案归档')
      fetchComplaints()
    } catch { /* ignore */ }
  }).catch(() => {})
}

onMounted(() => {
  fetchComplaints()
})
</script>

<style scoped>
.complaints-manage-container { padding: 20px; background-color: #f5f7fa; min-height: calc(100vh - 100px); }

/* 统计卡片样式 */
.stat-row { margin-bottom: 20px; }
.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 4px solid;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}
.stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-value .unit { font-size: 13px; margin-left: 4px; font-weight: normal; }
.stat-icon { font-size: 40px; }

/* 列表美化 */
.header-flex { display: flex; justify-content: space-between; align-items: center; }
.list-card { border-radius: 8px; }

/* 状态点动画 */
.status-wrapper { display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-blink { animation: blink 1.2s infinite; }
@keyframes blink { 
  0% { opacity: 1; transform: scale(1); } 
  50% { opacity: 0.4; transform: scale(1.2); } 
  100% { opacity: 1; transform: scale(1); } 
}

/* 展开行样式 */
.expand-content { padding: 10px 30px; background: #fcfcfc; }
.complaint-text { color: #606266; line-height: 1.6; padding: 10px 0; }
.result-text { color: #67C23A; font-weight: bold; }

.category-dot { color: #606266; font-size: 13px; }
.category-dot::before { content: '•'; margin-right: 5px; color: #409EFF; font-weight: bold; }
</style>