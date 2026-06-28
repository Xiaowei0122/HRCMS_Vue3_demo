<template>
  <div class="honors-container">
    <el-card shadow="never" class="header-card">
      <template #header>
        <div class="header-main">
          <div class="left">
            <el-radio-group v-model="currentTab" size="default">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="cert">资质证书</el-radio-button>
              <el-radio-button label="photo">公司风采</el-radio-button>
            </el-radio-group>
          </div>
          <el-button type="primary" icon="Plus" @click="openUpload">上传新荣誉/照片</el-button>
        </div>
      </template>

    <!-- 瀑布流/网格布局 -->
    <el-row :gutter="20">
      <el-col 
        v-for="item in filteredList" :key="item.id"
        :key="index" 
        :xs="12" :sm="8" :md="6" :lg="4"
        style="margin-bottom: 20px"
      >
        <el-card :body-style="{ padding: '0px' }" class="honor-card">
          <div class="image-box">
            <el-image 
              :src="item.url" 
              :preview-src-list="[item.url]"
              fit="cover" 
              class="honor-image"
              lazy
            />
            <div class="mask">
              <el-button type="primary" icon="Edit" circle @click="editHonor(item)" />
              <el-button type="danger" icon="Delete" circle @click="handleDelete(item)" />
              <el-button type="primary" icon="Edit" circle @click="handleEdit(item)" />
            </div>
          </div>
          <div class="info">
            <div class="title">{{ item.title }}</div>
            <div class="date-tag">
              <el-tag size="small" :type="item.type === 'cert' ? 'warning' : 'success'">
                {{ item.type === 'cert' ? '资质' : '风采' }}
              </el-tag>
              <span>{{ item.date }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    </el-card>

    <!-- 上传/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑信息' : '添加新荣誉'" width="450px">
      <el-form :model="form" label-position="top">
        <el-form-item label="名称/标题">
          <el-input v-model="form.title" placeholder="如：理光核心代理商证书" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="资质证书" value="cert" />
            <el-option label="公司风采" value="photo" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择图片">
          <el-upload
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :limit="1"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确认保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHonorList, createHonor, updateHonor, deleteHonor } from '@/api/modules/honors'

const currentTab = ref('all')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const loading = ref(false)

const form = ref({ title: '', type: 'cert', url: '' })

const honorList = ref([])

// 过滤逻辑
const filteredList = computed(() => {
  if (currentTab.value === 'all') return honorList.value
  return honorList.value.filter(item => item.type === currentTab.value)
})

const fetchHonors = async () => {
  loading.value = true
  try {
    const params = { page: 1, size: 50 }
    if (currentTab.value !== 'all') params.type = currentTab.value
    const res = await getHonorList(params)
    if (Array.isArray(res)) {
      honorList.value = res
    } else {
      honorList.value = res.records || []
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

watch(currentTab, () => { fetchHonors() })

const openUpload = () => {
  isEdit.value = false
  editingId.value = null
  form.value = { title: '', type: 'cert', url: '' }
  dialogVisible.value = true
}

const editHonor = (item) => {
  isEdit.value = true
  editingId.value = item.id
  form.value = { title: item.title || '', type: item.type || 'cert', url: item.url || '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  try {
    if (isEdit.value) {
      await updateHonor(editingId.value, { ...form.value })
    } else {
      await createHonor({ ...form.value })
    }
    ElMessage.success('操作成功')
    dialogVisible.value = false
    fetchHonors()
  } catch { /* ignore */ }
}

const handleDelete = (item) => {
  ElMessageBox.confirm('确定要删除这条记录吗？').then(async () => {
    try {
      await deleteHonor(item.id)
      ElMessage.success('已删除')
      fetchHonors()
    } catch { /* ignore */ }
  }).catch(() => {})
}

onMounted(() => {
  fetchHonors()
})
</script>

<style scoped>
.header-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }

.honor-card {
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.honor-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.15);
}

.image-box {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.honor-image {
  width: 100%;
  height: 100%;
  cursor: zoom-in;
}

.mask {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-box:hover .mask {
  opacity: 1;
}

.info {
  padding: 12px;
}

.title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.date-tag {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}
</style>