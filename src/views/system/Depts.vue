<template>
  <div class="dept-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title-text">部门管理</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增部门</el-button>
        </div>
      </template>

      <el-table :data="deptList" v-loading="loading" border stripe style="width: 100%">
        <el-table-column prop="name" label="部门名称" min-width="180" />
        <el-table-column label="上级部门" min-width="160">
          <template #default="{ row }">
            <span v-if="row.parentId">{{ parentName(row.parentId) }}</span>
            <el-tag v-else size="small" effect="plain" type="info">顶级部门</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="leader" label="负责人" width="140">
          <template #default="{ row }">{{ row.leader || '—' }}</template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="90" align="center" />
        <el-table-column label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="removeDept(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !deptList.length" :image-size="120" description="暂无部门，点击右上角新增" />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑部门' : '新增部门'" width="440px" append-to-body>
      <el-form :model="form" label-width="90px">
        <el-form-item label="部门名称">
          <el-input v-model="form.name" placeholder="例如：技术部" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="form.parentId" placeholder="留空为顶级部门" clearable style="width: 100%">
            <el-option
              v-for="d in parentCandidates"
              :key="d.id"
              :label="d.name"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.leader" placeholder="选填" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmDept">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getDeptList, createDept, updateDept, deleteDept } from '@/api/modules/depts'

const deptList = ref([])
const loading = ref(false)

const dialogVisible = ref(false)
const editId = ref(null)
const form = reactive({ name: '', parentId: '', leader: '', sort: 0 })

const parentName = (id) => deptList.value.find(d => d.id === id)?.name || id

// 上级部门候选：排除自身（避免自引用）
const parentCandidates = computed(() => deptList.value.filter(d => d.id !== editId.value))

const fetchDepts = async () => {
  loading.value = true
  try {
    const res = await getDeptList()
    deptList.value = Array.isArray(res) ? res : []
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editId.value = null
  Object.assign(form, { name: '', parentId: '', leader: '', sort: 0 })
  dialogVisible.value = true
}

const openEdit = (row) => {
  editId.value = row.id
  Object.assign(form, {
    name: row.name,
    parentId: row.parentId || '',
    leader: row.leader || '',
    sort: row.sort ?? 0,
  })
  dialogVisible.value = true
}

const confirmDept = async () => {
  if (!form.name.trim()) return ElMessage.warning('请输入部门名称')
  const payload = {
    name: form.name.trim(),
    parentId: form.parentId || null,
    leader: form.leader.trim(),
    sort: form.sort,
  }
  try {
    if (editId.value) {
      await updateDept(editId.value, payload)
      ElMessage.success('部门已更新')
    } else {
      await createDept(payload)
      ElMessage.success('部门已创建')
    }
    dialogVisible.value = false
    fetchDepts()
  } catch { /* ignore */ }
}

const removeDept = (row) => {
  ElMessageBox.confirm(`确定删除部门 [${row.name}] 吗？`, '确认删除', {
    type: 'warning',
    confirmButtonText: '删除'
  }).then(async () => {
    try {
      await deleteDept(row.id)
      ElMessage.success('已删除')
      fetchDepts()
    } catch { /* ignore */ }
  }).catch(() => {})
}

onMounted(fetchDepts)
</script>

<style scoped>
.dept-container { padding: 10px; background-color: var(--bg-muted); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title-text { font-weight: bold; font-size: 16px; }
</style>
