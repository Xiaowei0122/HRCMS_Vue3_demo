<template>
  <div class="knowledge-container">
    <el-card shadow="never">
      <template #header>
        <div class="header-main">
          <div class="search-area">
            <el-input v-model="searchQuery" placeholder="搜索文章标题..." style="width: 250px; margin-right: 10px" clearable />
            <el-select v-model="typeFilter" placeholder="所有分类" style="width: 150px; margin-right: 10px" clearable>
              <el-option label="驱动安装" value="驱动安装" />
              <el-option label="故障案例" value="故障案例" />
              <el-option label="系统维护" value="系统维护" />
              <el-option label="网络运维" value="网络运维" />
              <el-option label="监控安防" value="监控安防" />
            </el-select>
            <el-button type="primary" :icon="Search" @click="handleSearch">筛选</el-button>
          </div>
          <el-button type="primary" :icon="Plus" @click="openDrawer">录入文章</el-button>
        </div>
      </template>

      <el-table :data="knowledgeList" border stripe v-loading="loading">
        <el-table-column label="封面" width="120">
          <template #default="{ row }">
            <el-image v-if="row.cover" :src="row.cover" fit="cover" style="width: 80px; height: 50px; border-radius: 4px" />
            <span v-else style="color: #C9CDD4;">无封面</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="文章标题" min-width="260" show-overflow-tooltip />
        <el-table-column prop="type" label="分类" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.type" effect="plain">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="阅读量" width="90" align="center" />
        <el-table-column label="置顶" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.isPinned" size="small" type="warning" effect="plain">置顶</el-tag>
            <span v-else style="color: #C9CDD4;">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-badge is-dot :type="row.isPublished ? 'success' : 'info'">
              {{ row.isPublished ? '已发布' : '草稿' }}
            </el-badge>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="editKnowledge(scope.row)">编辑</el-button>
            <el-button link type="warning" @click="handlePin(scope.row)">{{ scope.row.isPinned ? '取消置顶' : '置顶' }}</el-button>
            <el-button link type="success" @click="handlePublish(scope.row)">{{ scope.row.isPublished ? '下架' : '发布' }}</el-button>
            <el-button link type="danger" @click="removeKnowledge(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > query.size"
        style="margin-top: 16px; justify-content: flex-end"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="query.size"
        :current-page="query.page"
        @current-change="onPageChange"
      />
    </el-card>

    <el-drawer v-model="drawerVisible" :title="isEdit ? '编辑文章' : '录入文章'" size="50%" append-to-body>
      <el-form :model="knowledgeForm" label-position="top">
        <el-form-item label="文章标题">
          <el-input v-model="knowledgeForm.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="文章分类">
              <el-select v-model="knowledgeForm.type" style="width: 100%" allow-create filterable default-first-option placeholder="选择或输入分类">
                <el-option label="驱动安装" value="驱动安装" />
                <el-option label="故障案例" value="故障案例" />
                <el-option label="系统维护" value="系统维护" />
                <el-option label="网络运维" value="网络运维" />
                <el-option label="监控安防" value="监控安防" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="封面图（选填）">
              <el-upload class="knowledge-cover-uploader" :show-file-list="false" :http-request="handleCoverUpload">
                <img v-if="knowledgeForm.cover" :src="knowledgeForm.cover" class="knowledge-cover-preview" />
                <el-icon v-else class="knowledge-cover-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文章正文">
          <div class="rich-editor-wrapper">
            <QuillEditor v-model:content="knowledgeForm.content" contentType="html" toolbar="full" :options="editorOptions" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" @click="saveKnowledge">{{ isEdit ? '保存修改' : '保存并发布' }}</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { getKnowledgeList, createKnowledge, updateKnowledge, deleteKnowledge as apiDeleteKnowledge, togglePinKnowledge, publishKnowledge } from '@/api/modules/knowledge'
import { uploadFile } from '@/api/modules/upload'

const editorOptions = {
  modules: {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ color: [] }, { background: [] }],
      [{ list: 'ordered' }, { list: 'bullet' }],
      [{ align: [] }],
      ['blockquote', 'code-block'],
      [{ indent: '-1' }, { indent: '+1' }],
      ['link', 'image'],
      ['clean'],
    ],
  },
  placeholder: '在此输入正文内容...',
}

const searchQuery = ref('')
const typeFilter = ref('')
const drawerVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const loading = ref(false)
const total = ref(0)
const query = reactive({ page: 1, size: 10 })

const knowledgeList = ref([])
const knowledgeForm = reactive({ title: '', type: '', content: '', cover: '' })

const fetchKnowledge = async () => {
  loading.value = true
  try {
    const params = { page: query.page, size: query.size }
    if (typeFilter.value) params.type = typeFilter.value
    if (searchQuery.value) params.title = searchQuery.value
    const res = await getKnowledgeList(params)
    if (Array.isArray(res)) {
      knowledgeList.value = res
      total.value = res.length
    } else {
      knowledgeList.value = res.records || []
      total.value = res.total || 0
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  query.page = 1
  fetchKnowledge()
}

const onPageChange = (p) => {
  query.page = p
  fetchKnowledge()
}

const openDrawer = () => {
  isEdit.value = false
  editingId.value = null
  knowledgeForm.title = ''
  knowledgeForm.type = '驱动安装'
  knowledgeForm.content = ''
  knowledgeForm.cover = ''
  drawerVisible.value = true
}

const editKnowledge = (row) => {
  isEdit.value = true
  editingId.value = row.id
  knowledgeForm.title = row.title || ''
  knowledgeForm.type = row.type || ''
  knowledgeForm.content = row.content || ''
  knowledgeForm.cover = row.cover || ''
  drawerVisible.value = true
}

const handleCoverUpload = async ({ file, onSuccess, onError }) => {
  try {
    const res = await uploadFile(file, 'knowledge')
    knowledgeForm.cover = res.url
    onSuccess && onSuccess(res)
  } catch (e) {
    onError && onError(e)
  }
}

const saveKnowledge = async () => {
  if (!knowledgeForm.title.trim()) {
    ElMessage.warning('请输入文章标题')
    return
  }
  try {
    if (isEdit.value) {
      await updateKnowledge(editingId.value, { ...knowledgeForm })
      ElMessage.success('文章已更新')
    } else {
      await createKnowledge({ ...knowledgeForm, isPublished: true })
      ElMessage.success('文章已发布')
    }
    drawerVisible.value = false
    fetchKnowledge()
  } catch { /* ignore */ }
}

const removeKnowledge = (row) => {
  ElMessageBox.confirm('确定删除该文章吗？').then(async () => {
    try {
      await apiDeleteKnowledge(row.id)
      ElMessage.success('已删除')
      fetchKnowledge()
    } catch { /* ignore */ }
  }).catch(() => {})
}

const handlePin = async (row) => {
  try {
    await togglePinKnowledge(row.id)
    ElMessage.success(row.isPinned ? '已取消置顶' : '已置顶')
    fetchKnowledge()
  } catch { /* ignore */ }
}

const handlePublish = async (row) => {
  try {
    await publishKnowledge(row.id)
    ElMessage.success('发布状态已切换')
    fetchKnowledge()
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchKnowledge()
})
</script>

<style scoped>
.header-main { display: flex; justify-content: space-between; align-items: center; }
.search-area { display: flex; align-items: center; }
.rich-editor-wrapper {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.rich-editor-wrapper :deep(.ql-toolbar) {
  border: none;
  border-bottom: 1px solid var(--border-color-light, #F1F5F9);
  background: var(--bg-muted);
}
.rich-editor-wrapper :deep(.ql-container) {
  border: none;
  font-size: var(--text-base);
}
.rich-editor-wrapper :deep(.ql-editor) {
  min-height: 320px;
}
.rich-editor-wrapper :deep(.ql-editor.ql-blank::before) {
  color: var(--text-muted);
  font-style: normal;
}

.knowledge-cover-uploader { width: 120px; }
.knowledge-cover-preview { width: 120px; height: 90px; object-fit: cover; border-radius: 4px; border: 1px solid var(--border-color); display: block; }
.knowledge-cover-icon { font-size: 28px; color: #8c939d; width: 120px; height: 90px; text-align: center; line-height: 90px; border: 1px dashed #d9d9d9; border-radius: 4px; }
</style>
