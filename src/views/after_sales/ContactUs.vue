<template>
  <div class="contact-config-container">
    <el-alert 
      title="配置说明：此处设置的信息将直接展示在微信公众号的“联系我们”页面，请确保信息的准确性与专业性。" 
      type="warning" 
      show-icon 
      :closable="false"
      style="margin-bottom: 20px;"
    />

    <el-card shadow="never">
      <template #header>
        <div class="header-flex">
          <span class="title">展示工程师管理</span>
          <el-button type="primary" :icon="Plus" @click="openAddDialog">添加展示工程师</el-button>
        </div>
      </template>

      <!-- 工程师卡片列表 -->
      <el-row :gutter="20">
        <el-col :span="8" v-for="item in engineerList" :key="item.id" style="margin-bottom: 20px;">
          <el-card class="engineer-card" :body-style="{ padding: '0px' }" hover>
            <div class="card-body">
              <el-avatar :size="70" :src="item.avatar" class="avatar" />
              <div class="info">
                <div class="name-row">
                  <span class="name">{{ item.name }}</span>
                  <el-switch v-model="item.showOnMobile" size="small" active-text="展示" />
                </div>
                <div class="phone"><el-icon><Phone /></el-icon> {{ item.phone }}</div>
                <div class="tags">
                  <el-tag v-for="tag in item.skills" :key="tag" size="small" effect="plain">
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <el-button link type="primary" @click="editEngineer(item)">编辑信息</el-button>
              <el-divider direction="vertical" />
              <el-button link type="danger" @click="removeEngineer(item)">取消展示</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 配置弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑工程师信息' : '添加工程师'" width="500px">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="头像上传">
          <el-upload class="avatar-uploader" action="#" :show-file-list="false">
            <img v-if="form.avatar" :src="form.avatar" class="upload-preview" />
            <el-icon v-else class="uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="展示给客户的名称" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.phone" placeholder="手机号，支持一键拨号" />
        </el-form-item>
        <el-form-item label="擅长领域">
          <el-select v-model="form.skills" multiple filterable allow-create default-first-option placeholder="请输入并回车添加标签">
            <el-option label="变压器维修" value="变压器维修" />
            <el-option label="电路排查" value="电路排查" />
            <el-option label="弱电系统" value="弱电系统" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.desc" type="textarea" placeholder="一句话简介，如：10年行业经验，精通各类复杂电路" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEngineer">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Phone } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getContactEngineers, createContactEngineer,
  updateContactEngineer, deleteContactEngineer
} from '@/api/modules/contact'

const dialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)

const engineerList = ref([])

const form = ref({ name: '', phone: '', skills: [], avatar: '', desc: '' })

const fetchEngineers = async () => {
  loading.value = true
  try {
    const res = await getContactEngineers()
    if (Array.isArray(res)) {
      engineerList.value = res
    } else {
      engineerList.value = res.records || []
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  form.value = { name: '', phone: '', skills: [], avatar: '', desc: '' }
  dialogVisible.value = true
}

const editEngineer = (item) => {
  isEdit.value = true
  form.value = { ...item }
  dialogVisible.value = true
}

const saveEngineer = async () => {
  try {
    if (isEdit.value) {
      await updateContactEngineer(form.value.id, { ...form.value })
    } else {
      await createContactEngineer({ ...form.value })
    }
    ElMessage.success('配置已同步至公众号展示端')
    dialogVisible.value = false
    fetchEngineers()
  } catch { /* ignore */ }
}

const removeEngineer = (item) => {
  ElMessageBox.confirm('确定要从公众号展示页面移除该工程师吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteContactEngineer(item.id)
      ElMessage.success('已下线展示')
      fetchEngineers()
    } catch { /* ignore */ }
  }).catch(() => {})
}

onMounted(() => {
  fetchEngineers()
})
</script>

<style scoped>
.contact-config-container { padding: 20px; background: #f5f7fa; min-height: calc(100vh - 110px); }
.header-flex { display: flex; justify-content: space-between; align-items: center; }
.title { font-weight: bold; border-left: 4px solid #409eff; padding-left: 10px; }

/* 卡片样式 */
.engineer-card { transition: all 0.3s; border-radius: 10px; }
.engineer-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }

.card-body { padding: 20px; display: flex; align-items: center; gap: 15px; }
.info { flex: 1; }
.name-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.name { font-size: 16px; font-weight: bold; color: #303133; }
.phone { font-size: 13px; color: #606266; margin-bottom: 10px; }
.tags { display: flex; flex-wrap: wrap; gap: 5px; }

.card-footer { background: #fafafa; padding: 10px; text-align: center; border-top: 1px solid #f0f0f0; }

/* 上传样式 */
.avatar-uploader { border: 1px dashed #d9d9d9; border-radius: 6px; cursor: pointer; width: 100px; height: 100px; line-height: 100px; text-align: center; }
.upload-preview { width: 100px; height: 100px; border-radius: 6px; object-fit: cover; }
.uploader-icon { font-size: 28px; color: #8c939d; }
</style>