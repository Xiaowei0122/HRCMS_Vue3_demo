<template>
  <div class="cases-container">
    <el-tabs v-model="activeTab" type="border-card" class="case-tabs" @tab-change="handleTabChange">

      <!-- ═══ 1. 品牌管理 ═══ -->
      <el-tab-pane label="合作代理品牌" name="brands">
        <div class="tab-header">
          <el-alert title="此处上传展示在官网首页的品牌 Logo，建议尺寸 240x120px，透明背景 PNG 格式最佳。" type="info" show-icon :closable="false" class="tab-alert" />
          <el-button type="primary" :icon="Plus" @click="openBrandDialog()">新增品牌</el-button>
        </div>

        <el-table :data="brandList" border stripe v-loading="brandLoading" style="margin-top: 20px">
          <el-table-column label="品牌Logo" width="150">
            <template #default="{ row }">
              <el-image v-if="row.logo" :src="row.logo" fit="contain" style="width: 100px; height: 44px; background: var(--bg-muted); border-radius: 4px" />
              <span v-else class="no-logo">暂无Logo</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="品牌名称" width="180" />
          <el-table-column prop="level" label="授权等级" width="130">
            <template #default="{ row }">
              <el-tag :type="levelType(row.level)" effect="plain">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="url" label="品牌官网" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <a v-if="row.url" :href="row.url" target="_blank" class="brand-link">{{ row.url }}</a>
              <span v-else style="color: var(--text-muted)">—</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openBrandDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDeleteBrand(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!brandLoading && brandList.length === 0" description="暂无合作品牌，点击上方按钮新增" />
      </el-tab-pane>

      <!-- ═══ 2. 典型销售案例 ═══ -->
      <el-tab-pane label="典型销售案例" name="cases">
        <div class="tab-header">
          <el-input v-model="searchCase" placeholder="搜索客户/行业..." style="width: 260px" clearable @input="filterCases" />
          <el-button type="success" :icon="Plus" @click="openCaseDialog()">发布新案例</el-button>
        </div>

        <div class="case-grid" v-loading="caseLoading">
          <el-row :gutter="20" v-if="filteredCases.length">
            <el-col :xs="24" :sm="12" :lg="8" v-for="(item, index) in filteredCases" :key="item._id || item.id || index">
              <el-card class="case-item card-lift" shadow="hover">
                <template #header>
                  <div class="case-title">
                    <span class="case-client">{{ item.client }}</span>
                    <el-tag size="small" effect="plain">{{ item.industry }}</el-tag>
                  </div>
                </template>
                <div class="case-content">
                  <p><strong>交付设备：</strong>{{ item.device || '—' }}</p>
                  <p><strong>服务模式：</strong>{{ item.mode || '—' }}</p>
                  <p class="desc">{{ item.summary }}</p>
                </div>
                <div class="case-footer">
                  <span class="date">{{ item.date || item.createTime }}</span>
                  <div class="btns">
                    <el-button :icon="Edit" size="small" circle @click="openCaseDialog(item)" />
                    <el-button :icon="Delete" type="danger" size="small" circle @click="handleDeleteCase(item)" />
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          <el-empty v-if="!caseLoading && filteredCases.length === 0" description="暂无销售案例" />
        </div>
      </el-tab-pane>

    </el-tabs>

    <!-- ═══ 品牌编辑弹窗 ═══ -->
    <el-dialog
      v-model="brandDialogVisible"
      :title="editingBrand?._id || editingBrand?.id ? '编辑品牌' : '新增品牌'"
      width="480px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="brandForm" label-position="top" ref="brandFormRef" :rules="brandRules">
        <el-form-item label="品牌名称" prop="name">
          <el-input v-model="brandForm.name" placeholder="例：惠普（HP）" />
        </el-form-item>
        <el-form-item label="Logo 图片地址" prop="logo">
          <el-input v-model="brandForm.logo" placeholder="https://example.com/logo.png" />
        </el-form-item>
        <el-form-item label="授权等级" prop="level">
          <el-select v-model="brandForm.level" style="width: 100%">
            <el-option label="钻石代理商" value="钻石代理商" />
            <el-option label="金牌代理商" value="金牌代理商" />
            <el-option label="银牌代理商" value="银牌代理商" />
            <el-option label="授权经销商" value="授权经销商" />
            <el-option label="核心合作伙伴" value="核心合作伙伴" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌官网" prop="url">
          <el-input v-model="brandForm.url" placeholder="https://www.example.com" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="brandDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="brandSaving" @click="saveBrand">保存</el-button>
      </template>
    </el-dialog>

    <!-- ═══ 案例编辑弹窗 ═══ -->
    <el-dialog
      v-model="caseDialogVisible"
      :title="editingCase?._id || editingCase?.id ? '编辑案例' : '发布新案例'"
      width="550px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="caseForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="客户名称">
              <el-input v-model="caseForm.client" placeholder="例：陕西XX集团" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属行业">
              <el-select v-model="caseForm.industry" style="width: 100%" placeholder="选择行业">
                <el-option label="政府机关" value="政府机关" />
                <el-option label="教育科研" value="教育科研" />
                <el-option label="金融保险" value="金融保险" />
                <el-option label="医疗健康" value="医疗健康" />
                <el-option label="制造业" value="制造业" />
                <el-option label="能源化工" value="能源化工" />
                <el-option label="交通运输" value="交通运输" />
                <el-option label="建筑业" value="建筑业" />
                <el-option label="其他行业" value="其他行业" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="交付设备">
          <el-input v-model="caseForm.device" placeholder="例：HP LaserJet Pro M404dn × 50台" />
        </el-form-item>
        <el-form-item label="服务模式">
          <el-input v-model="caseForm.mode" placeholder="例：按张付费 MPS 全包服务" />
        </el-form-item>
        <el-form-item label="案例简介">
          <el-input v-model="caseForm.summary" type="textarea" :rows="4" placeholder="简要描述项目背景、解决方案与客户收益..." />
        </el-form-item>
        <el-form-item label="成交日期">
          <el-date-picker v-model="caseForm.date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="caseDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="caseSaving" @click="saveCase">保存案例</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import {
  getBrandList, createBrand, updateBrand, deleteBrand,
  getCaseList, createCase, updateCase, deleteCase,
} from '@/api/modules/cases'

// ── Tab ──
const activeTab = ref('brands')

// ── 品牌 ──
const brandList = ref([])
const brandLoading = ref(false)
const brandSaving = ref(false)
const brandDialogVisible = ref(false)
const editingBrand = ref(null)
const brandFormRef = ref(null)
const brandForm = reactive({ name: '', logo: '', level: '授权经销商', url: '' })
const brandRules = {
  name: [{ required: true, message: '请输入品牌名称', trigger: 'blur' }],
}

const levelType = (level) => {
  const map = { '钻石代理商': 'danger', '金牌代理商': 'warning', '银牌代理商': 'info', '授权经销商': '', '核心合作伙伴': 'success' }
  return map[level] || 'info'
}

const fetchBrands = async () => {
  brandLoading.value = true
  try {
    const res = await getBrandList()
    brandList.value = Array.isArray(res) ? res : (res.records || [])
  } catch { /* ignore */ } finally {
    brandLoading.value = false
  }
}

const openBrandDialog = (row) => {
  editingBrand.value = row || null
  if (row) {
    brandForm.name = row.name || ''
    brandForm.logo = row.logo || ''
    brandForm.level = row.level || '授权经销商'
    brandForm.url = row.url || ''
  } else {
    Object.assign(brandForm, { name: '', logo: '', level: '授权经销商', url: '' })
  }
  brandDialogVisible.value = true
}

const saveBrand = async () => {
  const valid = await brandFormRef.value?.validate().catch(() => false)
  if (!valid) return
  brandSaving.value = true
  try {
    const data = { ...brandForm }
    if (editingBrand.value?._id || editingBrand.value?.id) {
      await updateBrand(editingBrand.value._id || editingBrand.value.id, data)
      ElMessage.success('品牌信息已更新')
    } else {
      await createBrand(data)
      ElMessage.success('品牌已添加')
    }
    brandDialogVisible.value = false
    fetchBrands()
  } catch { /* ignore */ } finally {
    brandSaving.value = false
  }
}

const handleDeleteBrand = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除品牌「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteBrand(row._id || row.id)
    ElMessage.success('已删除')
    fetchBrands()
  } catch { /* ignore */ }
}

// ── 案例 ──
const caseList = ref([])
const caseLoading = ref(false)
const caseSaving = ref(false)
const caseDialogVisible = ref(false)
const editingCase = ref(null)
const searchCase = ref('')
const caseForm = reactive({ client: '', industry: '', device: '', mode: '', summary: '', date: '' })

const filteredCases = computed(() => {
  if (!searchCase.value) return caseList.value
  const kw = searchCase.value.toLowerCase()
  return caseList.value.filter(c =>
    (c.client || '').toLowerCase().includes(kw) ||
    (c.industry || '').toLowerCase().includes(kw) ||
    (c.device || '').toLowerCase().includes(kw)
  )
})

const fetchCases = async () => {
  caseLoading.value = true
  try {
    const res = await getCaseList({ page: 1, size: 50 })
    caseList.value = Array.isArray(res) ? res : (res.records || [])
  } catch { /* ignore */ } finally {
    caseLoading.value = false
  }
}

const openCaseDialog = (row) => {
  editingCase.value = row || null
  if (row) {
    caseForm.client = row.client || ''
    caseForm.industry = row.industry || ''
    caseForm.device = row.device || ''
    caseForm.mode = row.mode || ''
    caseForm.summary = row.summary || ''
    caseForm.date = row.date || ''
  } else {
    Object.assign(caseForm, { client: '', industry: '', device: '', mode: '', summary: '', date: '' })
  }
  caseDialogVisible.value = true
}

const saveCase = async () => {
  if (!caseForm.client) return ElMessage.warning('请输入客户名称')
  caseSaving.value = true
  try {
    const data = { ...caseForm }
    if (editingCase.value?._id || editingCase.value?.id) {
      await updateCase(editingCase.value._id || editingCase.value.id, data)
      ElMessage.success('案例已更新')
    } else {
      await createCase(data)
      ElMessage.success('案例已发布')
    }
    caseDialogVisible.value = false
    fetchCases()
  } catch { /* ignore */ } finally {
    caseSaving.value = false
  }
}

const handleDeleteCase = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除案例「${row.client}」？`, '确认删除', { type: 'warning' })
    await deleteCase(row._id || row.id)
    ElMessage.success('已删除')
    fetchCases()
  } catch { /* ignore */ }
}

const handleTabChange = (name) => {
  if (name === 'cases' && caseList.value.length === 0) fetchCases()
}

onMounted(() => {
  fetchBrands()
})
</script>

<style scoped>
.cases-container { padding: 4px 0; }

.case-tabs { min-height: 500px; }

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.tab-alert { flex: 1; min-width: 280px; }

/* ── 品牌表格 ── */
.no-logo {
  color: var(--text-muted);
  font-size: 12px;
}

.brand-link {
  color: var(--color-accent);
  font-size: 13px;
}

/* ── 案例卡片 ── */
.case-grid { margin-top: 20px; }

.case-item {
  margin-bottom: 20px;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.case-item:hover {
  transform: translateY(-2px);
}

.case-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.case-client {
  font-weight: var(--font-semibold);
  font-size: var(--text-lg);
  color: var(--text-primary);
}

.case-content p {
  font-size: 13px;
  margin: 8px 0;
  color: var(--text-secondary);
}

.case-content .desc {
  font-style: italic;
  color: var(--text-muted);
  margin-top: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.case-footer {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.case-footer .date {
  font-size: 12px;
  color: var(--text-muted);
}
</style>