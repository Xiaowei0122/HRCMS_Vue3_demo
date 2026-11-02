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
            <el-radio-button value="全部">全部</el-radio-button>
            <el-radio-button value="待接单">待接单</el-radio-button>
            <el-radio-button value="已预约">已预约</el-radio-button>
            <el-radio-button value="处理中">处理中</el-radio-button>
            <el-radio-button value="待确认">待确认</el-radio-button>
            <el-radio-button value="已归档">已归档</el-radio-button>
            <el-radio-button value="已完成">已完成</el-radio-button>
            <el-radio-button value="已取消">已取消</el-radio-button>
          </el-radio-group>

          <el-select v-model="filterWorkOrderType" class="type-filter" placeholder="工单类型" clearable @change="handleTypeFilter">
            <el-option v-for="t in workOrderTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </div>

        <div class="right-group">
          <el-button size="large" :loading="exporting" @click="openExportDialog">
            <el-icon><Download /></el-icon><span>导出工单</span>
          </el-button>
          <el-button v-if="canCreate" type="primary" size="large" @click="openAddDialog">
            <el-icon><Plus /></el-icon><span>录入报修单</span>
          </el-button>
        </div>
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

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <div class="status-wrapper">
              <span :class="['status-dot', getStatusDotClass(row.status)]"></span>
              {{ row.status }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="workOrderType" label="工单类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.workOrderType === '协助送货'" type="warning" effect="plain" size="small">协助送货</el-tag>
            <el-tag v-else type="info" effect="plain" size="small">{{ row.workOrderType || '售后上门' }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="deviceType" label="设备类型" width="100">
          <template #default="{ row }">{{ row.deviceType || '—' }}</template>
        </el-table-column>

        <el-table-column prop="description" label="报修内容" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.description || '—' }}</template>
        </el-table-column>

        <el-table-column label="费用" width="130">
          <template #default="{ row }">
            <span v-if="row.fee" class="fee-cell">
              <span class="fee-amount">￥{{ row.fee.amount }}</span>
              <el-tag :type="row.fee.mode === 'agreed' ? 'success' : 'warning'" effect="plain" size="small">{{ row.fee.mode === 'agreed' ? '已协商' : '自行协商' }}</el-tag>
            </span>
            <span v-else class="fee-empty">—</span>
          </template>
        </el-table-column>

        <el-table-column label="返修" width="80" align="center">
          <template #default="{ row }">
            <el-tooltip v-if="row.isRework" :content="`原单：${row.reworkOf}`" placement="top">
              <el-tag type="danger" effect="dark" size="small">返修</el-tag>
            </el-tooltip>
            <span v-else>—</span>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="报修时间" width="160" />

        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="viewDetail(scope.row)">详情</el-button>
            <el-button link type="success" v-if="isAdmin && canAssignStatus(scope.row.status)" @click="openAssignDialog(scope.row)">指派</el-button>
            <el-button link type="success" v-if="isEngineer && canAcceptStatus(scope.row)" @click="openAcceptDialog(scope.row)">接单</el-button>
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
          <span>选择「预约工程师 + 日期 + 时段」将直接预约该工程师；未选择则进入抢单池，由工程师自主接单。</span>
        </div>

        <!-- 报修表单内部 -->
        <el-form :model="repairForm" label-position="top" class="embedded-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="报修单位" required>
                <el-input v-model="repairForm.company" placeholder="请输入单位全称" @blur="onCompanyBlur" />
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
              <el-form-item label="工单类型" required>
                <el-select v-model="repairForm.workOrderType" style="width: 100%">
                  <el-option v-for="t in workOrderTypes" :key="t" :label="t" :value="t" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12" v-if="repairForm.workOrderType === '售后上门'">
              <el-form-item label="设备类型" required>
                <el-select v-model="repairForm.deviceType" style="width: 100%">
                  <el-option v-for="d in deviceTypes" :key="d" :label="d" :value="d" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row v-if="isInternal">
            <el-col :span="24">
              <el-divider content-position="left">预约上门（可选，不填则进入抢单池）</el-divider>
              <EngineerSlotPicker
                v-model:engineer-id="repairForm.engineerId"
                v-model:engineer-name="repairForm.engineerName"
                v-model:date="repairForm.preferredDate"
                v-model:time-slot="repairForm.preferredTimeSlot"
              />
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

          <el-row :gutter="20" v-if="isEngineer || isAdmin">
            <el-col :span="12">
              <el-form-item label="确认人（业务）" required>
                <el-select v-model="repairForm.confirmUserId" placeholder="请选择负责确认的业务" style="width: 100%" filterable>
                  <el-option v-if="isEngineer" label="本人工单" value="__self__" />
                  <el-option v-for="c in confirmers" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
                <div v-if="isSelfOrder" class="self-order-hint">
                  工单将直接记入本人名下并开始处理，无需再次接单 / 指派
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="用户地址">
            <el-input v-model="repairForm.address" placeholder="具体街道、楼层、房间号" />
          </el-form-item>

          <el-form-item label="上门费用（已协商好，选填）">
            <el-input-number v-model="repairForm.feeAmount" :min="0" :precision="2" :controls="false" placeholder="金额，如已协商好请填写" style="width: 100%" />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="紧急程度">
                <el-select v-model="repairForm.priority" style="width: 100%">
                  <el-option
                    v-for="p in priorityOptions"
                    :key="p"
                    :label="p + (priorityHints[p] || '')"
                    :value="p"
                  />
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
          @click="selectEngineer(eng)"
        >
          <div class="eng-avatar">{{ eng.name?.[0] || '工' }}</div>
          <div class="eng-info">
            <div class="eng-name">{{ eng.name }}</div>
            <div class="eng-detail">{{ eng.phone || '' }} · {{ eng.team || '工号未分组' }}</div>
          </div>
          <el-icon v-if="selectedEngineerId === eng.id" color="var(--color-accent)" :size="20"><CircleCheck /></el-icon>
        </div>
      </div>

      <el-empty v-if="!engineers.length" description="暂无可派工程师，请先在「联系我们」中添加" />

      <el-divider content-position="left">预约日期</el-divider>
      <el-date-picker
        v-model="assignDate"
        type="date"
        style="width: 100%"
        value-format="YYYY-MM-DD"
        :disabled-date="disablePastDate"
        @change="loadAssignAvailability"
      />

      <el-divider content-position="left">预约时间</el-divider>
      <el-select v-model="selectedTimeSlot" style="width: 100%" placeholder="请选择时段">
        <el-option
          v-for="opt in timeSlotOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
          :disabled="opt.value !== '全天' && assignOccupiedSlots.includes(opt.value)"
        >
          <span>{{ opt.label }}</span>
          <span v-if="opt.value !== '全天' && assignOccupiedSlots.includes(opt.value)" class="occupied-tip">（已占用）</span>
        </el-option>
      </el-select>

      <el-divider content-position="left">优先处理</el-divider>
      <div class="assign-escalate">
        <el-switch v-model="assignEscalate" active-text="加急置顶（当天第一顺位）" />
        <div v-if="assignEscalate" class="assign-escalate-reasons">
          <span class="assign-escalate-label">加急原因</span>
          <el-radio-group v-model="assignEscalateReason" size="small">
            <el-radio-button v-for="r in assignEscalateReasons" :key="r" :value="r">{{ r }}</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" :loading="assignLoading" @click="confirmAssign">
          确认指派
        </el-button>
      </template>
    </el-dialog>

    <!-- 4.5 工程师接单弹窗（复用组件：普通单 / 预约单，预约单支持改派/退回） -->
    <AcceptOrderDialog
      v-model="acceptVisible"
      :order="acceptingRepair"
      :confirming="acceptLoading"
      :rejecting="rejectReservedLoading"
      @confirm="onAcceptConfirm"
      @reject="onAcceptReject"
    />

    <!-- 5. 导出工单弹窗（时间区间筛选，最多一年） -->
    <el-dialog
      v-model="exportVisible"
      title="导出工单"
      width="480px"
      destroy-on-close
      append-to-body
    >
      <div class="export-body">
        <el-radio-group v-model="exportMode" class="export-mode">
          <el-radio-button value="range">自定义区间</el-radio-button>
          <el-radio-button value="year">导出整年</el-radio-button>
        </el-radio-group>

        <div v-if="exportMode === 'year'" class="export-field">
          <span class="field-label">选择年份</span>
          <el-date-picker
            v-model="exportYear"
            type="year"
            value-format="YYYY"
            placeholder="选择年份"
            :clearable="false"
            style="width: 100%"
          />
        </div>

        <div v-else class="export-field">
          <span class="field-label">时间区间（最长一年）</span>
          <el-date-picker
            v-model="exportRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            range-separator="至"
            :clearable="false"
            style="width: 100%"
          />
        </div>

        <div class="export-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>最多导出一年内的工单数据，超出范围请分次导出。</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="exportVisible = false">取消</el-button>
        <el-button type="primary" :loading="exporting" @click="confirmExport">
          开始导出
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import {
  Search, Plus, Bell, Pointer, CircleCheck, Warning, InfoFilled, Check, Download
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getRepairList, getRepairStats, createRepair, getConfirmers, getEngineerList, assignRepair, acceptRepair, rejectReservedOrder, exportRepairs, lookupCompany, getScheduleAvailability, getServerTime } from '@/api/modules/repairs'
import { getDictOptions } from '@/api/modules/dict'
import { hasPerm } from '@/utils/permission'
import { getUserInfo } from '@/utils/auth'
import EngineerSlotPicker from '@/components/EngineerSlotPicker.vue'
import AcceptOrderDialog from '@/components/AcceptOrderDialog.vue'

const router = useRouter()

// 角色判定：管理员（超管/管理员 rank<=1）指派；工程师自助接单；内部人员在录单时直接预约工程师。
// 注意：repair:all 被 admin/business/engineer 同时持有，不能作为“是否管理员”的依据。
const isAdmin = computed(() => (getUserInfo()?.rank ?? 99) <= 1)
const isEngineer = computed(() => getUserInfo()?.roleCode === 'engineer')
const myUserId = computed(() => getUserInfo()?.id || '')
// 内部员工/管理员（非普通用户）可见预约工程师区块
const isInternal = computed(() => (getUserInfo()?.roleCode ?? 'normal') !== 'normal')
const isSelfOrder = computed(() => isEngineer.value && repairForm.confirmUserId === '__self__')
// 拥有 repair:create 权限可录入报修单（财务只读调阅时隐藏）
const canCreate = computed(() => hasPerm('repair:create'))
// 管理员可对「待接单」指派；「已预约」已绑定工程师，退回待接单后才可二次指派
const canAssignStatus = (s) => s === '待接单'
// 工程师可接单：全局「待接单」抢单池 + 指派给自己的「已预约」单
const canAcceptStatus = (row) => {
  if (!row) return false
  if (row.status === '待接单') return true
  if (row.status === '已预约') {
    const rid = row.engineerId || ''
    return !rid || rid === myUserId.value
  }
  return false
}
// --- 状态变量 ---
const dialogVisible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const filterStatus = ref('')
const filterWorkOrderType = ref('')
const exporting = ref(false)
// 导出弹窗状态：整年 / 自定义区间
const exportVisible = ref(false)
const exportMode = ref('range')
const exportYear = ref(dayjs().format('YYYY'))
const exportRange = ref([])
// 业务下拉：优先读数据字典，字典为空时回退内置默认值
const deviceTypes = ref(['电脑', '打印机', '复印机', '投影仪', '扫描仪', '网络设备', '大屏', '其他'])
const workOrderTypes = ref(['售后上门', '协助送货'])
const priorityOptions = ref(['普通', '紧急', '特急'])
const priorityHints = { '普通': ' (24小时内)', '紧急': ' (4小时内)', '特急': ' (立即响应)' }

const loadDicts = async () => {
  try {
    const [dev, wot, pri] = await Promise.all([
      getDictOptions('设备类型'),
      getDictOptions('工单类型'),
      getDictOptions('优先级'),
    ])
    if (Array.isArray(dev) && dev.length) deviceTypes.value = dev.map(o => o.value)
    if (Array.isArray(wot) && wot.length) workOrderTypes.value = wot.map(o => o.value)
    if (Array.isArray(pri) && pri.length) priorityOptions.value = pri.map(o => o.value)
  } catch { /* 字典不可用时沿用内置默认 */ }
}

// --- 指派工程师弹窗 ---
const assignVisible = ref(false)
const assignLoading = ref(false)
const assigningRepair = ref(null)
const engineers = ref([])
const confirmers = ref([])
const selectedEngineerId = ref('')
const selectedTimeSlot = ref('全天')
const assignDate = ref('')
const assignOccupiedSlots = ref([])
const assignEscalate = ref(false)
const assignEscalateReason = ref('')
const assignEscalateReasons = ['灾难性故障', '领导检查', '客户临时要求', '其他']

// --- 工程师接单（复用 AcceptOrderDialog 组件） ---
const acceptVisible = ref(false)
const acceptLoading = ref(false)
const rejectReservedLoading = ref(false)
const acceptingRepair = ref(null)

// 服务器北京时间（对齐报单时间）
const serverDate = ref('')
const todayLocal = () => {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
const disablePastDate = (date) => {
  const today = serverDate.value ? new Date(serverDate.value + 'T00:00:00') : new Date()
  today.setHours(0, 0, 0, 0)
  return date.getTime() < today.getTime()
}

const timeSlotOptions = [
  { label: '全天', value: '全天' },
  { label: '上午 (早) 08:30-10:00', value: 'AM1' },
  { label: '上午 (晚) 10:00-11:50', value: 'AM2' },
  { label: '下午 (早) 13:30-15:00', value: 'PM1' },
  { label: '下午 (中) 15:00-16:30', value: 'PM2' },
  { label: '下午 (晚) 16:30-18:00', value: 'PM3' },
]

// --- 统计看板数据 ---
const stats = ref([
  { label: '待接单', value: 0, type: 'danger', icon: Bell },
  { label: '已预约', value: 0, type: 'warning', icon: Check },
  { label: '处理中', value: 0, type: 'primary', icon: Pointer },
  { label: '待确认', value: 0, type: 'warning', icon: Check },
  { label: '已归档', value: 0, type: 'info', icon: CircleCheck },
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
  description: '',
  workOrderType: '售后上门',
  deviceType: '',
  feeAmount: null,
  preferredTimeSlot: '全天',
  preferredDate: '',
  engineerId: '',
  engineerName: '',
  confirmUserId: ''
})

const getPriorityType = (p) => {
  if (p === '特急') return 'danger'
  if (p === '紧急') return 'warning'
  return 'info'
}

const getStatusDotClass = (s) => {
  const map = { '待接单': 'dot-danger', '已预约': 'dot-warning', '处理中': 'dot-primary', '待备件': 'dot-warning', '待确认': 'dot-warning', '已归档': 'dot-success', '已完成': 'dot-success', '已取消': 'dot-info' }
  return map[s] || 'dot-info'
}

// --- 从后端获取数据 ---
const fetchStats = async () => {
  try {
    const res = await getRepairStats()
    if (res) {
      stats.value[0].value = res.pending || 0
      stats.value[1].value = res.reserved || 0
      stats.value[2].value = res.processing || 0
      stats.value[3].value = res.confirming || 0
      stats.value[4].value = res.archived || 0
      stats.value[5].value = res.completed || 0
      stats.value[6].value = res.total || 0
    }
  } catch { /* ignore */ }
}

const fetchRepairList = async () => {
  loading.value = true
  try {
    const params = { page: query.page, size: query.size }
    if (filterStatus.value) params.status = filterStatus.value
    if (searchQuery.value) params.company = searchQuery.value
    if (filterWorkOrderType.value) params.workOrderType = filterWorkOrderType.value
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

const handleTypeFilter = () => {
  query.page = 1
  fetchRepairList()
}

const handlePageChange = (page) => {
  query.page = page
  fetchRepairList()
}

// --- 操作方法 ---
const openAddDialog = async () => {
  repairForm.orderNo = '系统自动生成'
  repairForm.company = ''
  repairForm.contact = ''
  repairForm.phone = ''
  repairForm.address = ''
  repairForm.priority = '普通'
  repairForm.description = ''
  repairForm.workOrderType = '售后上门'
  repairForm.deviceType = ''
  repairForm.feeAmount = null
  repairForm.preferredTimeSlot = '全天'
  repairForm.preferredDate = ''
  repairForm.engineerId = ''
  repairForm.engineerName = ''
  repairForm.confirmUserId = ''
  dialogVisible.value = true
  if (isEngineer.value || isAdmin.value) {
    try {
      const res = await getConfirmers()
      confirmers.value = Array.isArray(res) ? res : (res.records || [])
    } catch {
      confirmers.value = []
    }
  }
}

// 单位名失焦：匹配历史工单自动填充（仅填空字段，可修改）
const onCompanyBlur = async () => {
  const company = repairForm.company.trim()
  if (!company) return
  try {
    const info = await lookupCompany(company)
    if (info?.found) {
      if (!repairForm.contact && info.contact) repairForm.contact = info.contact
      if (!repairForm.phone && info.phone) repairForm.phone = info.phone
      if (!repairForm.address && info.address) repairForm.address = info.address
      if (!repairForm.deviceType && info.deviceType) repairForm.deviceType = info.deviceType
      ElMessage.success('已自动填充历史信息')
    }
  } catch { /* ignore */ }
}

const submitRepair = async () => {
  if (!repairForm.company || !repairForm.contact || !repairForm.phone) {
    ElMessage.error('请填写完整的必填信息')
    return
  }
  if ((isEngineer.value || isAdmin.value) && !repairForm.confirmUserId) {
    ElMessage.error('请选择确认人')
    return
  }
  const selfOrder = isSelfOrder.value
  submitting.value = true
  try {
    const confirmUser = selfOrder ? null : confirmers.value.find(c => c.id === repairForm.confirmUserId)
    const payload = {
      company: repairForm.company,
      contact: repairForm.contact,
      phone: repairForm.phone,
      address: repairForm.address,
      priority: repairForm.priority,
      description: repairForm.description,
      workOrderType: repairForm.workOrderType,
      deviceType: repairForm.deviceType,
      preferredTimeSlot: repairForm.preferredTimeSlot,
      preferredDate: repairForm.preferredDate || '',
      engineerId: repairForm.engineerId || '',
      engineerName: repairForm.engineerName || '',
      ...(selfOrder
        ? { selfOrder: true }
        : { confirmUserId: repairForm.confirmUserId, confirmUserName: confirmUser?.name || '' })
    }
    if (repairForm.feeAmount != null && repairForm.feeAmount !== '') {
      payload.fee = { mode: 'agreed', amount: Number(repairForm.feeAmount) }
    }
    await createRepair(payload)
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

// --- 导出工单（弹窗选择时间区间） ---
const openExportDialog = () => {
  exportYear.value = dayjs().format('YYYY')
  exportRange.value = []
  exportVisible.value = true
}

const confirmExport = async () => {
  let startDate = ''
  let endDate = ''
  if (exportMode.value === 'year') {
    if (!exportYear.value) {
      ElMessage.warning('请选择年份')
      return
    }
    startDate = `${exportYear.value}-01-01`
    endDate = `${exportYear.value}-12-31`
  } else {
    if (!Array.isArray(exportRange.value) || exportRange.value.length !== 2) {
      ElMessage.warning('请选择时间区间')
      return
    }
    startDate = exportRange.value[0]
    endDate = exportRange.value[1]
  }

  // 最多导出一年内的数据
  const start = dayjs(startDate)
  const end = dayjs(endDate)
  if (!start.isValid() || !end.isValid()) {
    ElMessage.error('日期无效')
    return
  }
  if (end.isBefore(start)) {
    ElMessage.error('结束日期不能早于开始日期')
    return
  }
  if (end.diff(start, 'day') > 366) {
    ElMessage.error('时间区间不能超过一年（最多 366 天），请分次导出')
    return
  }

  exporting.value = true
  try {
    const params = { startDate, endDate }
    if (filterStatus.value) params.status = filterStatus.value
    if (searchQuery.value) params.company = searchQuery.value
    if (filterWorkOrderType.value) params.workOrderType = filterWorkOrderType.value
    const res = await exportRepairs(params)
    // 后端若返回 JSON 错误（而非 Excel），content-type 为 application/json
    const contentType = res.headers?.['content-type'] || ''
    if (contentType.includes('application/json')) {
      let msg = '导出失败'
      try {
        const text = await res.data.text()
        msg = JSON.parse(text).message || msg
      } catch { /* ignore */ }
      ElMessage.error(msg)
      return
    }
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `工单导出_${startDate}_${endDate}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
    exportVisible.value = false
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    exporting.value = false
  }
}

// --- 指派工程师 ---
const openAssignDialog = async (row) => {
  assigningRepair.value = row
  selectedEngineerId.value = ''
  selectedTimeSlot.value = '全天'
  assignDate.value = serverDate.value || todayLocal()
  assignOccupiedSlots.value = []
  assignEscalate.value = false
  assignEscalateReason.value = ''
  assignVisible.value = true
  // 拉取工程师列表
  try {
    const res = await getEngineerList()
    engineers.value = Array.isArray(res) ? res : (res.records || [])
  } catch {
    engineers.value = []
  }
}

const selectEngineer = (eng) => {
  selectedEngineerId.value = eng.id
  loadAssignAvailability()
}

const loadAssignAvailability = async () => {
  if (!selectedEngineerId.value || !assignDate.value) {
    assignOccupiedSlots.value = []
    return
  }
  try {
    const res = await getScheduleAvailability({ engineerId: selectedEngineerId.value, date: assignDate.value })
    assignOccupiedSlots.value = Array.isArray(res?.occupied) ? res.occupied : []
    if (assignOccupiedSlots.value.includes(selectedTimeSlot.value)) selectedTimeSlot.value = '全天'
  } catch {
    assignOccupiedSlots.value = []
  }
}

const confirmAssign = async () => {
  if (!selectedEngineerId.value) {
    ElMessage.warning('请选择一位工程师')
    return
  }
  if (!assignDate.value) {
    ElMessage.warning('请选择预约日期')
    return
  }
  if (assignEscalate.value && !assignEscalateReason.value) {
    ElMessage.warning('加急置顶必须填写原因')
    return
  }
  const eng = engineers.value.find(e => e.id === selectedEngineerId.value)
  // 「全天」映射为 span=5（AM1 起）；单时段 span=1
  const isFullDay = selectedTimeSlot.value === '全天'
  assignLoading.value = true
  try {
    await assignRepair(assigningRepair.value.id, {
      engineerId: selectedEngineerId.value,
      engineerName: eng?.name || '',
      date: assignDate.value,
      timeSlot: isFullDay ? 'AM1' : selectedTimeSlot.value,
      slotSpan: isFullDay ? 5 : 1,
      escalate: assignEscalate.value,
      escalateReason: assignEscalate.value ? assignEscalateReason.value : ''
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

// --- 工程师接单 ---
const openAcceptDialog = (row) => {
  acceptingRepair.value = row
  acceptVisible.value = true
}

const onAcceptConfirm = async (payload) => {
  acceptLoading.value = true
  try {
    await acceptRepair(acceptingRepair.value.id, {
      date: payload.date,
      timeSlot: payload.timeSlot,
      slotSpan: payload.slotSpan || 1,
      escalate: !!payload.escalate,
      escalateReason: payload.escalateReason || '',
      reason: payload.reason || ''
    })
    ElMessage.success('接单成功，已同步排期')
    acceptVisible.value = false
    fetchRepairList()
    fetchStats()
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    acceptLoading.value = false
  }
}

const onAcceptReject = async (payload) => {
  rejectReservedLoading.value = true
  try {
    await rejectReservedOrder(acceptingRepair.value.id, { reason: payload.reason })
    ElMessage.success('已退回，工单返回待接单')
    acceptVisible.value = false
    fetchRepairList()
    fetchStats()
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    rejectReservedLoading.value = false
  }
}

// --- 服务器时间对齐 ---
const initServerTime = async () => {
  try {
    const t = await getServerTime()
    if (t?.date) {
      serverDate.value = t.date
      repairForm.date = new Date(t.date + 'T00:00:00')
    } else {
      ElMessage.warning('获取服务器时间失败，已使用本地时间，接单日期可能不准确')
    }
  } catch {
    ElMessage.warning('获取服务器时间失败，已使用本地时间，接单日期可能不准确')
  }
}

onMounted(() => {
  fetchStats()
  fetchRepairList()
  loadDicts()
  initServerTime()
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
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-card);
  border-left: 5px solid #ccc;
  transition: all 0.3s;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 4px 16px 0 rgba(0,0,0,0.1); }

.danger { border-left-color: var(--color-danger); background: linear-gradient(to right, #fffafa, #fff); }
.primary { border-left-color: var(--color-accent); background: linear-gradient(to right, #f5faff, #fff); }
.warning { border-left-color: var(--color-warning); background: linear-gradient(to right, #fdfaf5, #fff); }
.success { border-left-color: var(--color-success); background: linear-gradient(to right, #f7fdf5, #fff); }
.info { border-left-color: var(--text-muted); background: linear-gradient(to right, #f9f9f9, #fff); }

.stat-label { font-size: 14px; color: var(--text-secondary); margin-bottom: 8px; }
.stat-number { font-size: 28px; font-weight: bold; color: var(--text-primary); }
.stat-icon { font-size: 40px; opacity: 0.15; color: inherit; }

/* 表格与工具栏 */
.table-card { border-radius: var(--radius-md); border: none; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.left-group { display: flex; align-items: center; gap: 20px; }
.right-group { display: flex; align-items: center; gap: 12px; }
.search-input { width: 280px; }
.type-filter { width: 140px; }
.fee-cell { display: inline-flex; align-items: center; gap: 6px; }
.fee-amount { color: var(--color-warning); font-weight: 600; }
.fee-empty { color: var(--text-muted); }

.status-wrapper { display: flex; align-items: center; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; display: inline-block; }
.dot-danger { background: var(--color-danger); box-shadow: 0 0 5px var(--color-danger); }
.dot-primary { background: var(--color-accent); box-shadow: 0 0 5px var(--color-accent); }
.dot-warning { background: var(--color-warning); box-shadow: 0 0 5px var(--color-warning); }
.dot-success { background: var(--color-success); box-shadow: 0 0 5px var(--color-success); }

.eng-name { color: var(--color-accent); font-weight: 500; }
.pagination-container { margin-top: 25px; display: flex; justify-content: flex-end; }

/* 修复固定列 hover 时与滚动列内容重叠 */
:deep(.el-table__fixed-right .el-table__fixed-body-wrapper .el-table__body tbody tr td) {
  background-color: #fff;
}
:deep(.el-table__fixed .el-table__fixed-body-wrapper .el-table__body tbody tr td) {
  background-color: #fff;
}
/* 斑马纹行 */
:deep(.el-table--striped .el-table__fixed-right .el-table__fixed-body-wrapper .el-table__body tbody tr.el-table__row--striped td) {
  background-color: #fafafa;
}
:deep(.el-table--striped .el-table__fixed .el-table__fixed-body-wrapper .el-table__body tbody tr.el-table__row--striped td) {
  background-color: #fafafa;
}
/* hover 行 */
:deep(.el-table__fixed-right .el-table__fixed-body-wrapper .el-table__body tbody tr:hover > td) {
  background-color: rgba(3, 105, 161, 0.03);
}
:deep(.el-table__fixed .el-table__fixed-body-wrapper .el-table__body tbody tr:hover > td) {
  background-color: rgba(3, 105, 161, 0.03);
}

/* 弹窗样式 */
.form-notice {
  background: var(--color-success-bg);
  color: var(--color-success);
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
.self-order-hint {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--color-accent);
  background: var(--color-info-bg, #E8F3FF);
  padding: 6px 10px;
  border-radius: 4px;
}

/* 指派工程师弹窗 */
.assign-info { margin-bottom: 10px; }
.engineer-list { width: 100%; display: flex; flex-direction: column; gap: 8px; max-height: 350px; overflow-y: auto; }
.engineer-option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  gap: 12px;
}
.engineer-option:hover { border-color: var(--color-accent); background: var(--color-info-bg); }
.engineer-option.selected { border-color: var(--color-accent); background: var(--color-info-bg); box-shadow: 0 0 0 2px rgba(64,158,255,0.15); }
.eng-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent), #36d1dc);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: bold; flex-shrink: 0;
}
.eng-info { flex: 1; }
.eng-info .eng-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.eng-info .eng-detail { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.occupied-tip { color: var(--text-muted); font-size: 12px; margin-left: 6px; }
.assign-escalate { display: flex; flex-direction: column; gap: 12px; }
.assign-escalate-reasons { display: flex; flex-direction: column; gap: 8px; }
.assign-escalate-label { font-size: 13px; color: var(--text-secondary); font-weight: var(--font-medium); }

/* 导出工单弹窗 */
.export-body { display: flex; flex-direction: column; gap: 18px; }
.export-mode { display: flex; }
.export-mode :deep(.el-radio-button__inner) { min-width: 130px; }
.export-field { display: flex; flex-direction: column; gap: 8px; }
.field-label { font-size: 13px; color: var(--text-secondary); font-weight: var(--font-medium); }
.export-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-info-bg);
  color: var(--text-secondary);
  font-size: 12px;
}
</style>