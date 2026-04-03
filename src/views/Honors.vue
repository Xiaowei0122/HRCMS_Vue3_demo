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
        v-for="(item, index) in filteredList" 
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
              <el-button type="danger" icon="Delete" circle @click="handleDelete(index)" />
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
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const currentTab = ref('all')
const dialogVisible = ref(false)
const isEdit = ref(false)

const form = ref({ title: '', type: 'cert', url: '' })

// 模拟数据
const honorList = ref([
  { title: '理光(Ricoh)年度优秀经销商', type: 'cert', url: 'https://picsum.photos/400/600?random=1', date: '2024-01' },
  { title: '西安办公设备协会理事单位', type: 'cert', url: 'https://picsum.photos/400/550?random=2', date: '2023-11' },
  { title: '公司十周年庆典合影', type: 'photo', url: 'https://picsum.photos/600/400?random=3', date: '2024-02' },
  { title: 'AAA级信用企业证书', type: 'cert', url: 'https://picsum.photos/400/580?random=4', date: '2023-05' },
  { title: '技术部售后服务培训', type: 'photo', url: 'https://picsum.photos/600/450?random=5', date: '2024-03' },
  { title: '佳能授权维修中心', type: 'cert', url: 'https://picsum.photos/400/560?random=6', date: '2023-08' },
])

// 过滤逻辑
const filteredList = computed(() => {
  if (currentTab.value === 'all') return honorList.value
  return honorList.value.filter(item => item.type === currentTab.value)
})

const openUpload = () => {
  isEdit.value = false
  form.value = { title: '', type: 'cert' }
  dialogVisible.value = true
}

const handleSave = () => {
  ElMessage.success('操作成功')
  dialogVisible.value = false
}

const handleDelete = (index) => {
  ElMessageBox.confirm('确定要删除这张照片吗？').then(() => {
    honorList.value.splice(index, 1)
    ElMessage.success('已删除')
  })
}
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