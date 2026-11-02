<template>
  <div class="dict-container">
    <el-row :gutter="20">
      <!-- 左侧：字典分组 -->
      <el-col :span="6">
        <el-card shadow="never" class="dict-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">字典分组</span>
              <el-button type="primary" size="small" icon="Plus" @click="openCreate(activeType)">新增项</el-button>
            </div>
          </template>
          <ul class="type-list">
            <li
              v-for="t in types"
              :key="t.type"
              :class="['type-item', { active: t.type === activeType }]"
              @click="selectType(t.type)"
            >
              <span class="type-name">{{ t.type }}</span>
              <el-tag size="small" effect="plain" type="info">{{ t.count }}</el-tag>
            </li>
          </ul>
          <el-empty v-if="!types.length && !loading" :image-size="80" description="暂无字典分组" />
        </el-card>
      </el-col>

      <!-- 右侧：字典项列表 -->
      <el-col :span="18">
        <el-card shadow="never" class="dict-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">
                字典项
                <span v-if="activeType" class="type-indicator">{{ activeType }}</span>
                <span v-else style="color: var(--text-muted); font-size: 13px">请选择左侧分组</span>
              </span>
              <div>
                <el-button v-if="activeType" :icon="Refresh" @click="fetchItems">刷新</el-button>
                <el-button v-if="activeType" type="primary" icon="Plus" @click="openCreate(activeType)">新增字典项</el-button>
              </div>
            </div>
          </template>

          <el-table :data="items" v-loading="loading" border stripe style="width: 100%">
            <el-table-column prop="label" label="名称" min-width="140" />
            <el-table-column prop="value" label="值" min-width="140">
              <template #default="{ row }">
                <el-tag v-if="row.value !== row.label" size="small" effect="plain" type="info">{{ row.value }}</el-tag>
                <span v-else style="color: var(--text-muted)">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="sort" label="排序" width="80" align="center" />
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'info'" size="small" effect="light">
                  {{ row.enabled ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="removeItem(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!items.length && activeType && !loading" :image-size="120" description="该分组下暂无字典项" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增/编辑字典项弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑字典项' : '新增字典项'" width="460px" append-to-body>
      <el-form :model="form" label-width="90px">
        <el-form-item label="所属分组">
          <el-select
            v-model="form.type"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入新分组"
            style="width: 100%"
          >
            <el-option v-for="t in types" :key="t.type" :label="t.type" :value="t.type" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.label" placeholder="例如：门禁设备" />
        </el-form-item>
        <el-form-item label="存储值">
          <el-input v-model="form.value" placeholder="留空则与名称一致" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.enabled" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { getDictTypes, getDictItems, createDictItem, updateDictItem, deleteDictItem } from '@/api/modules/dict'

const types = ref([])
const activeType = ref('')
const items = ref([])
const loading = ref(false)

const dialogVisible = ref(false)
const editId = ref(null)
const form = reactive({ type: '', label: '', value: '', sort: 0, enabled: true })

const fetchTypes = async () => {
  try {
    const res = await getDictTypes()
    types.value = Array.isArray(res) ? res : []
    // 默认选中第一个分组
    if (!activeType.value && types.value.length) {
      selectType(types.value[0].type)
    }
  } catch {
    // 错误已由拦截器统一处理
  }
}

const fetchItems = async () => {
  if (!activeType.value) return
  loading.value = true
  try {
    const res = await getDictItems(activeType.value)
    items.value = Array.isArray(res) ? res : []
  } catch {
    // ignore
  } finally {
    loading.value = false
  }
}

const selectType = (type) => {
  activeType.value = type
  fetchItems()
}

const openCreate = (type) => {
  editId.value = null
  form.type = type || ''
  form.label = ''
  form.value = ''
  form.sort = 0
  form.enabled = true
  dialogVisible.value = true
}

const openEdit = (row) => {
  editId.value = row.id
  form.type = row.type
  form.label = row.label
  form.value = row.value
  form.sort = row.sort
  form.enabled = row.enabled
  dialogVisible.value = true
}

const confirmItem = async () => {
  if (!form.type.trim()) return ElMessage.warning('请选择或输入分组')
  if (!form.label.trim()) return ElMessage.warning('请输入名称')
  const payload = {
    type: form.type.trim(),
    label: form.label.trim(),
    value: (form.value || form.label).trim(),
    sort: form.sort,
    enabled: form.enabled,
  }
  try {
    if (editId.value) {
      await updateDictItem(editId.value, payload)
      ElMessage.success('字典项已更新')
    } else {
      await createDictItem(payload)
      ElMessage.success('字典项已新增')
    }
    dialogVisible.value = false
    // 刷新分组（可能新增了分组）+ 当前分组条目
    await fetchTypes()
    if (!activeType.value || activeType.value !== payload.type) {
      selectType(payload.type)
    } else {
      fetchItems()
    }
  } catch { /* ignore */ }
}

const removeItem = (row) => {
  ElMessageBox.confirm(`确定删除字典项 [${row.label}] 吗？`, '确认删除', {
    type: 'warning',
    confirmButtonText: '删除'
  }).then(async () => {
    try {
      await deleteDictItem(row.id)
      ElMessage.success('已删除')
      fetchItems()
      fetchTypes()
    } catch { /* ignore */ }
  }).catch(() => {})
}

onMounted(fetchTypes)
</script>

<style scoped>
.dict-container { padding: 10px; background-color: var(--bg-muted); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title-text { font-weight: bold; font-size: 16px; }

.dict-card {
  height: calc(100vh - 140px);
  border-radius: var(--radius-md);
}

.type-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
  margin-bottom: 4px;
}

.type-item:hover { background: var(--bg-muted); }
.type-item.active { background: #EFF6FF; color: #3B82F6; font-weight: var(--font-medium); }

.type-name { font-size: 14px; }

.type-indicator {
  margin-left: 8px;
  font-size: 13px;
  color: #3B82F6;
  font-weight: normal;
}

:deep(.el-card__body) { height: calc(100% - 60px); overflow-y: auto; }
</style>
