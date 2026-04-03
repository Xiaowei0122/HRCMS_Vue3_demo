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
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          
          <el-radio-group v-model="filterStatus" class="status-filter">
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
      <el-table :data="filteredData" stripe style="width: 100%" v-loading="loading">
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
            <el-button link type="primary">详情</el-button>
            <el-divider direction="vertical" />
            <el-button link type="success" v-if="scope.row.status === '待接单'">指派</el-button>
            <el-button link type="warning" v-else>催办</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination background layout="total, prev, pager, next" :total="mockData.length" />
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
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { 
  Search, Plus, Bell, Pointer, Tools, CircleCheck, Warning, InfoFilled 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// --- 状态变量 ---
const dialogVisible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const filterStatus = ref('全部')

// --- 统计看板数据 ---
const stats = [
  { label: '待接单', value: 12, type: 'danger', icon: Bell },
  { label: '处理中', value: 8, type: 'primary', icon: Pointer },
  { label: '待备件', value: 3, type: 'warning', icon: Tools },
  { label: '今日完成', value: 25, type: 'success', icon: CircleCheck },
  { label: '待处理投诉', value: 1, type: 'info', icon: Warning }
]

// --- 模拟表格数据 ---
const mockData = ref([
  { id: 1, orderNo: 'HR260403001', company: '兴业银行科技部', contact: '张经理', priority: '特急', engineer: '', status: '待接单', createTime: '2026-04-03 09:15' },
  { id: 2, orderNo: 'HR260403002', company: '腾讯滨海大厦 B座', contact: '李小姐', priority: '紧急', engineer: '王小工', status: '处理中', createTime: '2026-04-03 10:20' },
  { id: 3, orderNo: 'HR260403003', company: '鸿瑞大厦3F会议室', contact: '物业王', priority: '普通', engineer: '陈技术', status: '待备件', createTime: '2026-04-02 15:40' },
  { id: 4, orderNo: 'HR260403004', company: '平安保险总部中心', contact: '孙先生', priority: '特急', engineer: '', status: '待接单', createTime: '2026-04-03 11:10' },
  { id: 5, orderNo: 'HR260403005', company: '顺丰速运网点', contact: '周站长', priority: '紧急', engineer: '陈技术', status: '处理中', createTime: '2026-04-03 13:05' },
])

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

// --- 逻辑计算 ---
const filteredData = computed(() => {
  return mockData.value.filter(item => {
    const s = searchQuery.value.toLowerCase()
    const matchSearch = item.company.toLowerCase().includes(s) || item.orderNo.toLowerCase().includes(s)
    const matchStatus = filterStatus.value === '全部' || item.status === filterStatus.value
    return matchSearch && matchStatus
  })
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

// --- 操作方法 ---
const openAddDialog = () => {
  repairForm.orderNo = 'HR' + Date.now().toString().slice(-8)
  dialogVisible.value = true
}

const submitRepair = () => {
  if (!repairForm.company || !repairForm.contact || !repairForm.phone) {
    ElMessage.error('请填写完整的必填信息')
    return
  }
  submitting.value = true
  setTimeout(() => {
    submitting.value = false
    dialogVisible.value = false
    ElMessage.success('工单录入成功！已自动加入任务池。')
  }, 1000)
}
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
</style>