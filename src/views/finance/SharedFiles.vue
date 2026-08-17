<template>
  <div class="shared-files-container">
    <!-- ═══ 顶部操作栏 ═══ -->
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-radio-group v-model="filterCategory" size="default" @change="fetchFiles">
          <el-radio-button value="all">全部文件</el-radio-button>
          <el-radio-button value="invoice">发票登记</el-radio-button>
          <el-radio-button value="report">财务报表</el-radio-button>
          <el-radio-button value="policy">制度文件</el-radio-button>
          <el-radio-button value="contract">合同存档</el-radio-button>
          <el-radio-button value="other">其他</el-radio-button>
        </el-radio-group>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :icon="Upload" @click="openUploadDialog">上传文件</el-button>
      </div>
    </div>

    <!-- ═══ 文件表格 ═══ -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredFiles" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="文件名称" min-width="260">
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon :size="20" :color="getFileColor(row.type)">
                <Document />
              </el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="categoryTagType(row.category)" size="small" effect="plain">
              {{ categoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="可见范围" width="140">
          <template #default="{ row }">
            <el-tag :type="row.visibility === 'public' ? 'success' : 'warning'" size="small" effect="light">
              <el-icon style="margin-right: 2px">
                <Lock v-if="row.visibility !== 'public'" />
                <View v-else />
              </el-icon>
              {{ row.visibility === 'public' ? '全员可见' : '仅财务' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploader" label="上传人" width="110" />
        <el-table-column prop="uploadTime" label="上传时间" width="170" sortable />
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Download" @click="handleDownload(row)">下载</el-button>
            <el-button
              v-if="isFinance"
              link
              type="warning"
              :icon="Setting"
              @click="openPermissionDialog(row)"
            >权限</el-button>
            <el-button
              v-if="isFinance"
              link
              type="danger"
              :icon="Delete"
              @click="handleDeleteFile(row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && filteredFiles.length === 0" description="暂无文件" />
    </el-card>

    <!-- ═══ 上传弹窗 ═══ -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文件"
      width="460px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="uploadForm" label-position="top">
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
          </el-upload>
        </el-form-item>
        <el-form-item label="文件分类">
          <el-select v-model="uploadForm.category" style="width: 100%">
            <el-option label="发票登记" value="invoice" />
            <el-option label="财务报表" value="report" />
            <el-option label="制度文件" value="policy" />
            <el-option label="合同存档" value="contract" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="可见范围">
          <el-radio-group v-model="uploadForm.visibility">
            <el-radio value="public">全员可见（公开）</el-radio>
            <el-radio value="private">仅财务可见</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="confirmUpload">确认上传</el-button>
      </template>
    </el-dialog>

    <!-- ═══ 权限设置弹窗 ═══ -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="设置可见范围"
      width="400px"
      append-to-body
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item label="文件">
          <el-tag>{{ activeFile?.name }}</el-tag>
        </el-form-item>
        <el-form-item label="可见范围">
          <el-radio-group v-model="permissionForm.visibility">
            <el-radio value="public">全员可见（业务/后勤/售后都可查看）</el-radio>
            <el-radio value="private">仅财务角色可见</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePermission">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, Download, Delete, Setting, Document,
  Lock, View, UploadFilled
} from '@element-plus/icons-vue'
import { getUserInfo } from '@/utils/auth'
import {
  getFileList, uploadFile, deleteFile, updateFilePermission
} from '@/api/modules/finance'

// ── 权限判定 ──
const currentUser = computed(() => getUserInfo() || {})
const isFinance = computed(() => {
  const ut = currentUser.value.userType || ''
  const role = currentUser.value.role || currentUser.value.roleName || ''
  // 管理员全部权限，内部员工可访问财务
  if (ut === 'admin' || role === '管理员') return true
  if (ut === 'internal' || role === '内部员工') return true
  // 旧版兼容
  return ['财务', 'admin', 'finance'].some(r => role.includes(r))
})

// ── 分类 ──
const filterCategory = ref('all')
const categoryLabel = (c) => {
  const map = { invoice: '发票登记', report: '财务报表', policy: '制度文件', contract: '合同存档', other: '其他' }
  return map[c] || c
}
const categoryTagType = (c) => {
  const map = { invoice: 'danger', report: 'warning', policy: 'info', contract: 'success', other: '' }
  return map[c] || 'info'
}
const getFileColor = (type) => {
  return '#64748B'
}

// ── 文件列表 ──
const files = ref([])
const loading = ref(false)

const filteredFiles = computed(() => {
  if (filterCategory.value === 'all') return files.value
  return files.value.filter(f => f.category === filterCategory.value)
})

const fetchFiles = async () => {
  loading.value = true
  try {
    const res = await getFileList({ page: 1, size: 100 })
    files.value = Array.isArray(res) ? res : (res.records || [])
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

// ── 上传 ──
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const selectedFile = ref(null)
const uploadForm = reactive({ category: 'invoice', visibility: 'public' })

const openUploadDialog = () => {
  Object.assign(uploadForm, { category: 'invoice', visibility: 'public' })
  selectedFile.value = null
  uploadDialogVisible.value = true
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const confirmUpload = async () => {
  if (!selectedFile.value) return ElMessage.warning('请选择文件')
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    fd.append('category', uploadForm.category)
    fd.append('visibility', uploadForm.visibility)
    await uploadFile(fd)
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    fetchFiles()
  } catch { /* ignore */ } finally {
    uploading.value = false
  }
}

// ── 下载 ──
const handleDownload = (row) => {
  if (row.url) {
    window.open(row.url, '_blank')
  } else {
    ElMessage.info('文件链接暂不可用')
  }
}

// ── 权限 ──
const permissionDialogVisible = ref(false)
const activeFile = ref(null)
const permissionForm = reactive({ visibility: 'public' })

const openPermissionDialog = (row) => {
  activeFile.value = row
  permissionForm.visibility = row.visibility || 'public'
  permissionDialogVisible.value = true
}

const savePermission = async () => {
  try {
    await updateFilePermission(activeFile.value._id || activeFile.value.id, {
      visibility: permissionForm.visibility
    })
    ElMessage.success('权限已更新')
    permissionDialogVisible.value = false
    fetchFiles()
  } catch { /* ignore */ }
}

// ── 删除 ──
const handleDeleteFile = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除文件「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteFile(row._id || row.id)
    ElMessage.success('已删除')
    fetchFiles()
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchFiles()
})
</script>

<style scoped>
.shared-files-container { padding: 4px 0; }

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-card { border-radius: var(--radius-md); }

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-size: var(--text-base);
}

/* 上传区域 */
:deep(.el-upload-dragger) {
  border: 2px dashed var(--border-color-hover);
  border-radius: var(--radius-md);
  padding: 32px;
}
</style>
