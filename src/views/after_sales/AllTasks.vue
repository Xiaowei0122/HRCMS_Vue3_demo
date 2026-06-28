<template>
  <div class="all-tasks-container">
    <!-- 1. 顶部平铺统计看板 -->
    <div class="stat-row">
      <div v-for="item in stats" :key="item.label" :class="['stat-card', item.type]">
        <div class="stat-content">
          <div class="stat-label">{{ item.label }}</div>
          <div class="stat-number">{{ item.value }}</div>
        </div>
        <el-icon class="stat-icon"><component :is="item.icon" /></el-icon>
      </div>
    </div>

    <!-- 2. 主体表格卡片 -->
    <el-card shadow="never" class="table-card">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="left-group">
          <el-input
            v-model="searchQuery"
            placeholder="搜索单位/工单号/联系人"
            class="search-input"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          
          <el-radio-group v-model="filterStatus" class="status-filter" @change="handleStatusFilter">
            <el-radio-button label="全部" />
            <el-radio-button label="待接单" />
            <el-radio-button label="处理中" />
            <el-radio-button label="已完成" />
          </el-radio-group>
        </div>
        
        <el-button type="primary" size="large" @click="openAddDialog">
          <el-icon><Plus /></el-icon><span>录入报修单</span>
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table :data="repairList" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="orderNo" label="工单编号" width="150" fixed />
        <el-table-column prop="company" label="报修单位" min-width="180" show-overflow-tooltip />
        
        <el-table-column prop="priority" label="紧急程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" effect="dark" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="engineer" label="负责工程师" width="120">
          <template #default="{ row }">
            <span v-if="row.engineer" class="eng-name">{{ row.engineer }}</span>
            <el-tag v-else type="danger" variant="plain" size="small">待指派</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <div class="status-wrapper">
              <span :class="['status-dot', getStatusDotClass(row.status)]"></span>
              {{ row.status }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="报修时间" width="160" />

        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="viewDetail(scope.row)">详情</el-button>
            <el-divider direction="vertical" />
            <el-button link type="success" v-if="scope.row.status === '待接单'" @click="openAssignDialog(scope.row)">指派</el-button>
            <el-button link type="warning" v-else @click="viewDetail(scope.row)">催办</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
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

    <!-- 3. 嵌入式报修表单弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="录入新报修工单"
      width="800px"
      destroy-on-close
      append-to-body
    >
      <div class="dialog-inner">
        <div class="form-notice">
          <el-icon><InfoFilled /></el-icon>
          <span>管理员手动录入的工单将直接进入“待指派”池，系统将实时通知相关工程师。</span>
        </div>

        <!-- 报修表单内部 -->
        <el-form :model="repairForm" label-position="top" class="embedded-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="报修单位" required>
                <el-input v-model="repairForm.company" placeholder="请输入单位全称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="报修日期">
                <el-date-picker v-model="repairForm.date" type="date" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="联系人" required>
                <el-input v-model="repairForm.contact" placeholder="姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话" required>
                <el-input v-model="repairForm.phone" placeholder="手机号" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="用户地址">
            <el-input v-model="repairForm.address" placeholder="具体街道、楼层、房间号" />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="紧急程度">
                <el-select v-model="repairForm.priority" style="width: 100%">
                  <el-option label="普通 (24小时内)" value="普通" />
                  <el-option label="紧急 (4小时内)" value="紧急" />
                  <el-option label="特急 (立即响应)" value="特急" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="单号预览">
                <el-input v-model="repairForm.orderNo" disabled />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="故障详细描述">
            <el-input
              v-model="repairForm.description"
              type="textarea"
              :rows="3"
              placeholder="请详细描述设备故障现象..."
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitRepair">
            确认提交并发布
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 4. 指派工程师弹窗 -->
    <el-dialog
      v-model="assignVisible"
      title="指派工程师"
      width="500px"
      destroy-on-close
      append-to-body
    >
      <div v-if="assigningRepair" class="assign-info">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="工单号">{{ assigningRepair.orderNo }}</el-descriptions-item>
          <el-descriptions-item label="报修单位">{{ assigningRepair.company }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider content-position="left">选择工程师</el-divider>

      <div class="engineer-list">
        <div
          v-for="eng in engineers"
          :key="eng.id"
          class="engineer-option"
          :class="{ selected: selectedEngineerId === eng.id }"
          @click="selectedEngineerId = eng.id"
        >
          <div class="eng-avatar">{{ eng.name?.[0] || '工' }}</div>
          <div class="eng-info">
            <div class="eng-name">{{ eng.name }}</div>
            <div class="eng-detail">{{ eng.phone || '' }} · {{ eng.team || '工号未分组' }}</div>
          </div>
          <el-icon v-if="selectedEngineerId === eng.id" color="#409eff" :size="20"><CircleCheck /></el-icon>
        </div>
      </div>

      <el-empty v-if="!engineers.length" description="暂无可派工程师，请先在「联系我们」中添加" />

      <el-divider content-position="left">预约时间</el-divider>
      <el-select v-model="selectedTimeSlot" style="width: 100%">
        <el-option v-for="opt in timeSlotOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
      </el-select>

      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" :loading="assignLoading" @click="confirmAssign">
          确认指派
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, Plus, Bell, Pointer, Tools, CircleCheck, Warning, InfoFilled, Check
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getRepairList, getRepairStats, createRepair, getEngineerList, assignRepair } from '@/api/modules/repairs'

const router = useRouter()

// --- 状态变量 ---
const dialogVisible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const filterStatus = ref('')

// --- 指派工程师弹窗 ---
const assignVisible = ref(false)
const assignLoading = ref(false)
const assigningRepair = ref(null)
const engineers = ref([])
const selectedEngineerId = ref('')
const selectedTimeSlot = ref('全天')

const timeSlotOptions = [
  { label: '全天', value: '全天' },
  { label: '上午 (早) 08:30-10:00', value: '上午 (早)' },
  { label: '上午 (晚) 10:00-11:50', value: '上午 (晚)' },
  { label: '下午 (早) 13:30-15:00', value: '下午 (早)' },
  { label: '下午 (中) 15:00-16:30', value: '下午 (中)' },
  { label: '下午 (晚) 16:30-18:00', value: '下午 (晚)' },
]

// --- 统计看板数据 ---
const stats = ref([
  { label: '待接单', value: 0, type: 'danger', icon: Bell },
  { label: '处理中', value: 0, type: 'primary', icon: Pointer },
  { label: '已完成', value: 0, type: 'success', icon: CircleCheck },
  { label: '全部工单', value: 0, type: 'info', icon: Warning }
])

// --- 真实表格数据 ---
const repairList = ref([])
const total = ref(0)
const query = reactive({ page: 1, size: 10 })

// --- 报修表单数据 ---
const repairForm = reactive({
  company: '',
  date: new Date(),
  contact: '',
  phone: '',
  address: '',
  priority: '普通',
  orderNo: '',
  description: ''
})

const getPriorityType = (p) => {
  if (p === '特急') return 'danger'
  if (p === '紧急') return 'warning'
  return 'info'
}

const getStatusDotClass = (s) => {
  const map = { '待接单': 'dot-danger', '处理中': 'dot-primary', '待备件': 'dot-warning', '已完成': 'dot-success' }
  return map[s] || 'dot-info'
}

// --- 从后端获取数据 ---
const fetchStats = async () => {
  try {
    const res = await getRepairStats()
    if (res) {
      stats.value[0].value = res.pending || 0
      stats.value[1].value = res.processing || 0
      stats.value[2].value = res.completed || 0
      stats.value[3].value = res.total || 0
    }
  } catch { /* ignore */ }
}

const fetchRepairList = async () => {
  loading.value = true
  try {
    const params = { page: query.page, size: query.size }
    if (filterStatus.value) params.status = filterStatus.value
    if (searchQuery.value) params.company = searchQuery.value
    const res = await getRepairList(params)
    if (Array.isArray(res)) {
      repairList.value = res
    } else {
      repairList.value = res.records || []
      total.value = res.total || 0
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  query.page = 1
  fetchRepairList()
}

const handleStatusFilter = (val) => {
  filterStatus.value = val === '全部' ? '' : val
  query.page = 1
  fetchRepairList()
}

const handlePageChange = (page) => {
  query.page = page
  fetchRepairList()
}

// --- 操作方法 ---
const openAddDialog = () => {
  repairForm.orderNo = '系统自动生成'
  repairForm.company = ''
  repairForm.contact = ''
  repairForm.phone = ''
  repairForm.address = ''
  repairForm.priority = '普通'
  repairForm.description = ''
  dialogVisible.value = true
}

const submitRepair = async () => {
  if (!repairForm.company || !repairForm.contact || !repairForm.phone) {
    ElMessage.error('请填写完整的必填信息')
    return
  }
  submitting.value = true
  try {
    await createRepair({
      company: repairForm.company,
      contact: repairForm.contact,
      phone: repairForm.phone,
      address: repairForm.address,
      priority: repairForm.priority,
      description: repairForm.description
    })
    ElMessage.success('工单录入成功！已自动加入任务池。')
    dialogVisible.value = false
    fetchRepairList()
    fetchStats()
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    submitting.value = false
  }
}

const viewDetail = (row) => {
  router.push(`/after_sales/repair-detail/${row.id}`)
}

// --- 指派工程师 ---
const openAssignDialog = async (row) => {
  assigningRepair.value = row
  selectedEngineerId.value = ''
  selectedTimeSlot.value = '全天'
  assignVisible.value = true
  // 拉取工程师列表
  try {
    const res = await getEngineerList()
    engineers.value = Array.isArray(res) ? res : (res.records || [])
  } catch {
    engineers.value = []
  }
}

const confirmAssign = async () => {
  if (!selectedEngineerId.value) {
    ElMessage.warning('请选择一位工程师')
    return
  }
  const eng = engineers.value.find(e => e.id === selectedEngineerId.value)
  assignLoading.value = true
  try {
    await assignRepair(assigningRepair.value.id, {
      engineerId: selectedEngineerId.value,
      engineerName: eng?.name || '',
      timeSlot: selectedTimeSlot.value
    })
    ElMessage.success(`已指派给 ${eng?.name || '工程师'}`)
    assignVisible.value = false
    fetchRepairList()
    fetchStats()
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    assignLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchRepairList()
})
</script>

<style scoped>
.all-tasks-container { padding: 5px; }

/* 统计看板样式 */
.stat-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  border-left: 5px solid #ccc;
  transition: all 0.3s;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 4px 16px 0 rgba(0,0,0,0.1); }

.danger { border-left-color: #f56c6c; background: linear-gradient(to right, #fffafa, #fff); }
.primary { border-left-color: #409eff; background: linear-gradient(to right, #f5faff, #fff); }
.warning { border-left-color: #e6a23c; background: linear-gradient(to right, #fdfaf5, #fff); }
.success { border-left-color: #67c23a; background: linear-gradient(to right, #f7fdf5, #fff); }
.info { border-left-color: #909399; background: linear-gradient(to right, #f9f9f9, #fff); }

.stat-label { font-size: 14px; color: #606266; margin-bottom: 8px; }
.stat-number { font-size: 28px; font-weight: bold; color: #303133; }
.stat-icon { font-size: 40px; opacity: 0.15; color: inherit; }

/* 表格与工具栏 */
.table-card { border-radius: 8px; border: none; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.left-group { display: flex; align-items: center; gap: 20px; }
.search-input { width: 280px; }

.status-wrapper { display: flex; align-items: center; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; display: inline-block; }
.dot-danger { background: #f56c6c; box-shadow: 0 0 5px #f56c6c; }
.dot-primary { background: #409eff; box-shadow: 0 0 5px #409eff; }
.dot-warning { background: #e6a23c; box-shadow: 0 0 5px #e6a23c; }
.dot-success { background: #67c23a; box-shadow: 0 0 5px #67c23a; }

.eng-name { color: #409eff; font-weight: 500; }
.pagination-container { margin-top: 25px; display: flex; justify-content: flex-end; }

/* 弹窗样式 */
.form-notice {
  background: #f0f9eb;
  color: #67c23a;
  padding: 12px 16px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 25px;
  font-size: 13px;
  border: 1px solid #e1f3d8;
}
.embedded-form :deep(.el-form-item__label) {
  font-weight: bold;
  padding-bottom: 4px;
}

/* 指派工程师弹窗 */
.assign-info { margin-bottom: 10px; }
.engineer-list { width: 100%; display: flex; flex-direction: column; gap: 8px; max-height: 350px; overflow-y: auto; }
.engineer-option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  gap: 12px;
}
.engineer-option:hover { border-color: #409eff; background: #f5faff; }
.engineer-option.selected { border-color: #409eff; background: #ecf5ff; box-shadow: 0 0 0 2px rgba(64,158,255,0.15); }
.eng-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #36d1dc);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: bold; flex-shrink: 0;
}
.eng-info { flex: 1; }
.eng-info .eng-name { font-size: 15px; font-weight: 600; color: #303133; }
.eng-info .eng-detail { font-size: 12px; color: #909399; margin-top: 4px; }
</style>