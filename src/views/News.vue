<template>
  <div class="news-container">
    <el-card shadow="never">
      <template #header>
        <div class="header-main">
          <div class="search-area">
            <el-input v-model="searchQuery" placeholder="搜索新闻标题..." style="width: 250px; margin-right: 10px" clearable />
            <el-select v-model="typeFilter" placeholder="所有分类" style="width: 150px; margin-right: 10px">
              <el-option label="公司新闻" value="company" />
              <el-option label="行业资讯" value="industry" />
              <el-option label="技术支持" value="tech" />
            </el-select>
            <el-button type="primary" icon="Search">筛选</el-button>
          </div>
          <el-button type="primary" icon="Plus" @click="openDrawer">发布新闻</el-button>
        </div>
      </template>

      <el-table :data="newsList" border stripe>
        <el-table-column label="封面" width="120">
          <template #default="{row}">
            <el-image :src="row.cover" fit="cover" style="width: 80px; height: 50px; border-radius: 4px" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="新闻标题" min-width="250" show-overflow-tooltip />
        <el-table-column prop="type" label="分类" width="120">
          <template #default="{row}">
            <el-tag>{{ typeNameMap[row.type] || row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="阅读量" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{row}">
            <el-badge is-dot :type="row.isPublished ? 'success' : 'info'">
              {{ row.isPublished ? '已发布' : '草稿' }}
            </el-badge>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="发布时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="editNews(scope.row)">编辑</el-button>
            <el-button link type="warning" @click="handlePin(scope.row)">置顶</el-button>
            <el-button link type="success" @click="handlePublish(scope.row)">{{ scope.row.isPublished ? '下架' : '发布' }}</el-button>
            <el-button link type="danger" @click="deleteNews(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="drawerVisible" :title="isEdit ? '编辑新闻' : '撰写新文章'" size="50%" append-to-body>
      <el-form :model="newsForm" label-position="top">
        <el-form-item label="文章标题">
          <el-input v-model="newsForm.title" placeholder="请输入引人入胜的标题" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="文章分类">
              <el-select v-model="newsForm.type" style="width: 100%">
                <el-option label="公司新闻" value="company" />
                <el-option label="行业资讯" value="industry" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="封面图">
              <el-upload
                class="news-cover-uploader"
                :show-file-list="false"
                :http-request="handleCoverUpload"
              >
                <img v-if="newsForm.cover" :src="newsForm.cover" class="news-cover-preview" />
                <el-icon v-else class="news-cover-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文章正文">
          <div class="rich-editor-wrapper">
            <QuillEditor
              v-model:content="newsForm.content"
              contentType="html"
              toolbar="full"
              :options="editorOptions"
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNews">立即发布</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { getNewsList, createNews, updateNews, deleteNews as apiDeleteNews, togglePinNews, publishNews } from '@/api/modules/news'
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

const newsList = ref([])
const newsForm = reactive({ title: '', type: 'company', content: '', cover: '' })

const typeNameMap = { company: '公司新闻', industry: '行业资讯', tech: '技术支持' }

const fetchNews = async () => {
  loading.value = true
  try {
    const params = { page: query.page, size: query.size }
    if (typeFilter.value) params.type = typeFilter.value
    if (searchQuery.value) params.title = searchQuery.value
    const res = await getNewsList(params)
    if (Array.isArray(res)) {
      newsList.value = res
    } else {
      newsList.value = res.records || []
      total.value = res.total || 0
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const openDrawer = () => {
  isEdit.value = false
  editingId.value = null
  newsForm.title = ''
  newsForm.type = 'company'
  newsForm.content = ''
  newsForm.cover = ''
  drawerVisible.value = true
}

const editNews = (row) => {
  isEdit.value = true
  editingId.value = row.id
  newsForm.title = row.title || ''
  newsForm.type = row.type || 'company'
  newsForm.content = row.content || ''
  newsForm.cover = row.cover || ''
  drawerVisible.value = true
}

const handleCoverUpload = async ({ file, onSuccess, onError }) => {
  try {
    const res = await uploadFile(file, 'news')
    newsForm.cover = res.url
    onSuccess && onSuccess(res)
  } catch (e) {
    onError && onError(e)
  }
}

const saveNews = async () => {
  try {
    if (isEdit.value) {
      await updateNews(editingId.value, { ...newsForm })
      ElMessage.success('文章已更新')
    } else {
      await createNews({ ...newsForm })
      ElMessage.success('文章已发布')
    }
    drawerVisible.value = false
    fetchNews()
  } catch { /* ignore */ }
}

const deleteNews = (row) => {
  ElMessageBox.confirm('确定删除该文章吗？').then(async () => {
    try {
      await apiDeleteNews(row.id)
      ElMessage.success('已删除')
      fetchNews()
    } catch { /* ignore */ }
  }).catch(() => {})
}

const handlePin = async (row) => {
  try {
    await togglePinNews(row.id)
    ElMessage.success('置顶状态已切换')
    fetchNews()
  } catch { /* ignore */ }
}

const handlePublish = async (row) => {
  try {
    await publishNews(row.id)
    ElMessage.success('发布状态已切换')
    fetchNews()
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchNews()
})
</script>

<style scoped>
.header-main { display: flex; justify-content: space-between; align-items: center; }
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

.news-cover-uploader { width: 120px; }
.news-cover-preview { width: 120px; height: 90px; object-fit: cover; border-radius: 4px; border: 1px solid var(--border-color); display: block; }
.news-cover-icon { font-size: 28px; color: #8c939d; width: 120px; height: 90px; text-align: center; line-height: 90px; border: 1px dashed #d9d9d9; border-radius: 4px; }
</style>