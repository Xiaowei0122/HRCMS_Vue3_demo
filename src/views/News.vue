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
            <el-tag>{{ row.typeName }}</el-tag>
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button link type="primary">编辑</el-button>
            <el-button link type="warning">置顶</el-button>
            <el-button link type="danger" @click="deleteNews(scope.$index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="drawerVisible" :title="isEdit ? '编辑新闻' : '撰写新文章'" size="50%">
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
              <el-upload action="#" :auto-upload="false" list-type="picture-card" :limit="1">
                <el-icon><Plus /></el-icon>
              </el-upload>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文章正文">
          <div class="editor-placeholder">
             <el-input type="textarea" :rows="15" placeholder="在此输入正文内容，支持 HTML 格式..." v-model="newsForm.content" />
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
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const searchQuery = ref('')
const typeFilter = ref('')
const drawerVisible = ref(false)
const newsForm = ref({ title: '', type: 'company', content: '' })

const newsList = ref([
  { title: '鸿瑞办公正式通过ISO质量管理体系认证', typeName: '公司新闻', cover: 'https://picsum.photos/200/100?random=10', views: 1240, isPublished: true, date: '2024-04-01 10:00' },
  { title: '2024款理光彩色复印机租赁优惠活动开启', typeName: '行业资讯', cover: 'https://picsum.photos/200/100?random=11', views: 856, isPublished: true, date: '2024-03-28 14:30' },
  { title: '如何通过数字化办公降低30%的纸张成本？', typeName: '技术支持', cover: 'https://picsum.photos/200/100?random=12', views: 432, isPublished: false, date: '2024-03-25 09:15' }
])

const openDrawer = () => { drawerVisible.value = true }
const saveNews = () => { ElMessage.success('文章已进入审核流程'); drawerVisible.value = false }
const deleteNews = (index) => {
  ElMessageBox.confirm('确定删除该文章吗？').then(() => {
    newsList.value.splice(index, 1)
    ElMessage.success('已删除')
  })
}
</script>

<style scoped>
.header-main { display: flex; justify-content: space-between; align-items: center; }
.editor-placeholder { border: 1px solid #dcdfe6; border-radius: 4px; padding: 10px; }
</style>