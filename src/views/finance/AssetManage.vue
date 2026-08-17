<template>
  <div class="asset-manage-container">
    <!-- ═══ 统计卡片 ═══ -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="12" :sm="6" v-for="item in statCards" :key="item.label">
        <div class="stat-mini-card">
          <div class="stat-num" :style="{ color: item.color }">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- ═══ 筛选 + 操作 ═══ -->
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-select v-model="filterCategory" placeholder="资产分类" style="width: 140px" clearable @change="fetchAssets">
          <el-option label="全部类别" value="" />
          <el-option label="车辆" value="车辆" />
          <el-option label="设备" value="设备" />
          <el-option label="办公家具" value="办公家具" />
          <el-option label="IT设备" value="IT设备" />
          <el-option label="其他" value="其他" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="使用状态" style="width: 140px; margin-left: 12px" clearable @change="fetchAssets">
          <el-option label="全部状态" value="" />
          <el-option label="在用" value="在用" />
          <el-option label="维修中" value="维修中" />
          <el-option label="闲置" value="闲置" />
          <el-option label="已报废" value="已报废" />
        </el-select>
      </div>
      <el-button type="primary" :icon="Plus" @click="openAssetDialog()">录入资产</el-button>
    </div>

    <!-- ═══ 资产表格 ═══ -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredAssets" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="资产名称" min-width="160">
          <template #default="{ row }">
            <div class="asset-name-cell">
              <el-icon :size="18" color="#64748B"><component :is="categoryIcon(row.category)" /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="110">
          <template #default="{ row }">
            <el-tag :type="catTagType(row.category)" size="small" effect="plain">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="型号/规格" width="160" show-overflow-tooltip />
        <el-table-column prop="department" label="所属部门" width="120" />
        <el-table-column prop="location" label="存放位置" width="120" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <span class="status-dot" :class="statusClass(row.status)"></span>
            {{ row.status || '在用' }}
          </template>
        </el-table-column>
        <el-table-column prop="purchaseDate" label="采购日期" width="120" sortable />
        <el-table-column prop="supplier" label="供应商" width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Edit" @click="openAssetDialog(row)">编辑</el-button>
            <el-button link type="success" :icon="SetUp" @click="openMaintenanceDialog(row)">维修</el-button>
            <el-button link type="danger" :icon="Delete" @click="handleDeleteAsset(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && filteredAssets.length === 0" description="暂无资产记录" />
    </el-card>

    <!-- ═══ 资产编辑弹窗 ═══ -->
    <el-dialog
      v-model="assetDialogVisible"
      :title="editingAsset?._id || editingAsset?.id ? '编辑资产' : '录入资产'"
      width="580px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="assetForm" label-position="top" ref="assetFormRef" :rules="assetRules">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="资产名称" prop="name">
              <el-input v-model="assetForm.name" placeholder="例：丰田卡罗拉 陕A·XXXXX" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="资产分类" prop="category">
              <el-select v-model="assetForm.category" style="width: 100%">
                <el-option label="车辆" value="车辆" />
                <el-option label="设备" value="设备" />
                <el-option label="办公家具" value="办公家具" />
                <el-option label="IT设备" value="IT设备" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="型号/规格">
              <el-input v-model="assetForm.model" placeholder="型号/车牌号/规格" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="序列号/编号">
              <el-input v-model="assetForm.serialNo" placeholder="SN 或公司编号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="所属部门">
              <el-select v-model="assetForm.department" style="width: 100%">
                <el-option label="总经办" value="总经办" />
                <el-option label="财务部" value="财务部" />
                <el-option label="销售部" value="销售部" />
                <el-option label="售后部" value="售后部" />
                <el-option label="行政部" value="行政部" />
                <el-option label="技术部" value="技术部" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="存放位置">
              <el-input v-model="assetForm.location" placeholder="具体位置" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="使用状态">
              <el-select v-model="assetForm.status" style="width: 100%">
                <el-option label="在用" value="在用" />
                <el-option label="维修中" value="维修中" />
                <el-option label="闲置" value="闲置" />
                <el-option label="已报废" value="已报废" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="采购日期">
              <el-date-picker v-model="assetForm.purchaseDate" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="供应商">
              <el-input v-model="assetForm.supplier" placeholder="供应商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="质保截止日">
              <el-date-picker v-model="assetForm.warrantyExpiry" type="date" placeholder="选填" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="assetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="assetSaving" @click="saveAsset">保存</el-button>
      </template>
    </el-dialog>

    <!-- ═══ 维修记录弹窗 ═══ -->
    <el-dialog
      v-model="maintenanceDialogVisible"
      :title="`维修记录 — ${maintenanceTarget?.name || ''}`"
      width="650px"
      append-to-body
      destroy-on-close
    >
      <div class="maintenance-header">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="资产">{{ maintenanceTarget?.name }}</el-descriptions-item>
          <el-descriptions-item label="型号">{{ maintenanceTarget?.model || '—' }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="maintenanceTarget?.status === '已报废' ? 'info' : 'success'" size="small">
              {{ maintenanceTarget?.status || '在用' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider content-position="left">
        历史记录
        <el-button
          v-if="maintenanceTarget?.status !== '已报废'"
          size="small"
          type="primary"
          :icon="Plus"
          style="margin-left: 12px"
          @click="addRecordVisible = true"
        >新增记录</el-button>
      </el-divider>

      <el-timeline v-if="maintenanceRecords.length">
        <el-timeline-item
          v-for="(r, i) in maintenanceRecords"
          :key="i"
          :type="r.type === '维修' ? 'warning' : r.type === '保养' ? 'primary' : 'success'"
          :timestamp="r.date"
        >
          <div class="record-item">
            <el-tag :type="r.type === '维修' ? 'warning' : r.type === '保养' ? '' : 'success'" size="small" effect="plain">
              {{ r.type }}
            </el-tag>
            <span class="record-desc">{{ r.description }}</span>
            <span class="record-meta" v-if="r.cost">费用：¥{{ r.cost }}</span>
            <span class="record-meta" v-if="r.vendor">服务商：{{ r.vendor }}</span>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无维修/保养记录" :image-size="80" />

      <template #footer>
        <el-button @click="maintenanceDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ═══ 新增维修记录弹窗 ═══ -->
    <el-dialog
      v-model="addRecordVisible"
      title="新增维修/保养记录"
      width="450px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="recordForm" label-position="top">
        <el-form-item label="记录类型">
          <el-radio-group v-model="recordForm.type">
            <el-radio value="维修">维修</el-radio>
            <el-radio value="保养">保养</el-radio>
            <el-radio value="检查">检查</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="recordForm.date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="详情描述">
          <el-input v-model="recordForm.description" type="textarea" :rows="3" placeholder="维修/保养内容..." />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="费用 (¥)">
              <el-input-number v-model="recordForm.cost" :min="0" :precision="2" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务商">
              <el-input v-model="recordForm.vendor" placeholder="维修服务商" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="维修后状态">
          <el-select v-model="recordForm.newStatus" style="width: 100%">
            <el-option label="恢复在用" value="在用" />
            <el-option label="继续维修" value="维修中" />
            <el-option label="建议报废" value="已报废" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addRecordVisible = false">取消</el-button>
        <el-button type="primary" :loading="recordSaving" @click="saveRecord">保存记录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, SetUp, Van, Cpu, OfficeBuilding, Monitor, More } from '@element-plus/icons-vue'
import {
  getAssetList, createAsset, updateAsset, deleteAsset, updateAssetStatus,
  getMaintenanceRecords, addMaintenanceRecord
} from '@/api/modules/finance'

// ── 统计 ──
const statCards = computed(() => {
  const total = assetList.value.length
  const inUse = assetList.value.filter(a => a.status === '在用').length
  const repairing = assetList.value.filter(a => a.status === '维修中').length
  const scrapped = assetList.value.filter(a => a.status === '已报废').length
  return [
    { label: '资产总数', value: total, color: '#3B82F6' },
    { label: '正常在用', value: inUse, color: '#059669' },
    { label: '维修中', value: repairing, color: '#D97706' },
    { label: '已报废', value: scrapped, color: '#94A3B8' },
  ]
})

// ── 图标 ──
const categoryIcon = (cat) => {
  const map = { '车辆': Van, '设备': Cpu, '办公家具': OfficeBuilding, 'IT设备': Monitor }
  return map[cat] || More
}
const catTagType = (cat) => {
  const map = { '车辆': 'danger', '设备': 'warning', '办公家具': 'info', 'IT设备': 'success' }
  return map[cat] || ''
}
const statusClass = (s) => {
  const map = { '在用': 'status-green', '维修中': 'status-orange', '闲置': 'status-gray', '已报废': 'status-red' }
  return map[s] || ''
}

// ── 列表 ──
const assetList = ref([])
const loading = ref(false)
const filterCategory = ref('')
const filterStatus = ref('')

const filteredAssets = computed(() => {
  let list = assetList.value
  if (filterCategory.value) list = list.filter(a => a.category === filterCategory.value)
  if (filterStatus.value) list = list.filter(a => a.status === filterStatus.value)
  return list
})

const fetchAssets = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterCategory.value) params.category = filterCategory.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await getAssetList(params)
    assetList.value = Array.isArray(res) ? res : (res.records || [])
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

// ── 编辑资产 ──
const assetDialogVisible = ref(false)
const assetSaving = ref(false)
const editingAsset = ref(null)
const assetFormRef = ref(null)
const assetForm = reactive({
  name: '', category: '设备', model: '', serialNo: '',
  department: '', location: '', status: '在用',
  purchaseDate: '', supplier: '', warrantyExpiry: ''
})
const assetRules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

const openAssetDialog = (row) => {
  editingAsset.value = row || null
  if (row) {
    Object.keys(assetForm).forEach(k => { assetForm[k] = row[k] || '' })
  } else {
    Object.assign(assetForm, {
      name: '', category: '设备', model: '', serialNo: '',
      department: '', location: '', status: '在用',
      purchaseDate: '', supplier: '', warrantyExpiry: ''
    })
  }
  assetDialogVisible.value = true
}

const saveAsset = async () => {
  const valid = await assetFormRef.value?.validate().catch(() => false)
  if (!valid) return
  assetSaving.value = true
  try {
    const data = { ...assetForm }
    if (editingAsset.value?._id || editingAsset.value?.id) {
      await updateAsset(editingAsset.value._id || editingAsset.value.id, data)
      ElMessage.success('资产已更新')
    } else {
      await createAsset(data)
      ElMessage.success('资产已录入')
    }
    assetDialogVisible.value = false
    fetchAssets()
  } catch { /* ignore */ } finally {
    assetSaving.value = false
  }
}

const handleDeleteAsset = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除资产「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteAsset(row._id || row.id)
    ElMessage.success('已删除')
    fetchAssets()
  } catch { /* ignore */ }
}

// ── 维修记录 ──
const maintenanceDialogVisible = ref(false)
const maintenanceTarget = ref(null)
const maintenanceRecords = ref([])

const openMaintenanceDialog = async (row) => {
  maintenanceTarget.value = row
  maintenanceDialogVisible.value = true
  try {
    const res = await getMaintenanceRecords(row._id || row.id)
    maintenanceRecords.value = Array.isArray(res) ? res : (res.records || [])
  } catch {
    maintenanceRecords.value = []
  }
}

// ── 新增维修记录 ──
const addRecordVisible = ref(false)
const recordSaving = ref(false)
const recordForm = reactive({
  type: '维修', date: '', description: '', cost: null, vendor: '', newStatus: '在用'
})

const saveRecord = async () => {
  if (!recordForm.description) return ElMessage.warning('请输入维修详情')
  recordSaving.value = true
  try {
    const data = { ...recordForm }
    const assetId = maintenanceTarget.value._id || maintenanceTarget.value.id
    await addMaintenanceRecord(assetId, data)

    // 同步更新资产状态
    if (data.newStatus) {
      await updateAssetStatus(assetId, { status: data.newStatus })
    }

    ElMessage.success('记录已保存')
    addRecordVisible.value = false
    // 刷新维修记录
    const res = await getMaintenanceRecords(assetId)
    maintenanceRecords.value = Array.isArray(res) ? res : (res.records || [])
    fetchAssets()
  } catch { /* ignore */ } finally {
    recordSaving.value = false
  }
}

onMounted(() => {
  fetchAssets()
})
</script>

<style scoped>
.asset-manage-container { padding: 4px 0; }

/* ── 统计卡片 ── */
.stat-row { margin-bottom: 20px; }
.stat-mini-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 20px;
  text-align: center;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-card);
}
.stat-num { font-size: 28px; font-weight: var(--font-bold); }
.stat-label { font-size: var(--text-sm); color: var(--text-muted); margin-top: 4px; }

/* ── 工具栏 ── */
.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-card { border-radius: var(--radius-md); }

.asset-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

/* ── 状态点 ── */
.status-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
.status-green  { background: #059669; }
.status-orange { background: #D97706; }
.status-gray   { background: #94A3B8; }
.status-red    { background: #DC2626; }

/* ── 维修记录 ── */
.maintenance-header { margin-bottom: 10px; }

.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.record-desc { color: var(--text-secondary); font-size: var(--text-base); }
.record-meta {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: var(--bg-muted);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}
</style>
