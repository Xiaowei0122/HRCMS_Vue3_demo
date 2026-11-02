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
                  <el-switch v-model="item.showOnMobile" size="small" active-text="展示" @change="toggleShow(item)" />
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑展示信息' : '添加展示工程师'" width="500px" append-to-body>
      <el-form :model="form" label-width="90px" label-position="left">
        <el-form-item v-if="!isEdit" label="选择工程师">
          <el-select v-model="form.id" filterable placeholder="从工程师角色用户中选择" style="width: 100%" @change="onCandidateSelect">
            <el-option v-for="c in candidates" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isEdit" label="姓名">
          <el-input v-model="form.name" disabled />
        </el-form-item>
        <el-form-item v-if="isEdit" label="联系电话">
          <el-input v-model="form.phone" disabled />
        </el-form-item>
        <el-form-item label="头像 URL">
          <el-input v-model="form.avatar" placeholder="头像图片链接" />
        </el-form-item>
        <el-form-item label="擅长领域">
          <el-select v-model="form.skills" multiple filterable allow-create default-first-option placeholder="请输入并回车添加标签">
            <el-option label="门禁维修" value="门禁维修" />
            <el-option label="网络调试" value="网络调试" />
            <el-option label="车牌识别" value="车牌识别" />
            <el-option label="道闸维修" value="道闸维修" />
            <el-option label="人脸识别" value="人脸识别" />
            <el-option label="软件调试" value="软件调试" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属团队">
          <el-input v-model="form.team" placeholder="例如：维保一组" />
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
  getContactEngineers, getContactEngineerCandidates,
  createContactEngineer, updateContactEngineer, deleteContactEngineer
} from '@/api/modules/contact'

const dialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)

const engineerList = ref([])
const candidates = ref([])

const form = ref({ id: '', name: '', phone: '', skills: [], avatar: '', desc: '', team: '', showOnMobile: true })

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

const fetchCandidates = async () => {
  try {
    const res = await getContactEngineerCandidates()
    candidates.value = Array.isArray(res) ? res : (res.records || [])
  } catch { /* ignore */ }
}

const openAddDialog = () => {
  isEdit.value = false
  form.value = { id: '', name: '', phone: '', skills: [], avatar: '', desc: '', team: '', showOnMobile: true }
  fetchCandidates()
  dialogVisible.value = true
}

const onCandidateSelect = (id) => {
  const c = candidates.value.find((x) => x.id === id)
  if (c) {
    form.value.name = c.name
    form.value.phone = c.phone
  }
}

const editEngineer = (item) => {
  isEdit.value = true
  form.value = {
    id: item.id,
    name: item.name,
    phone: item.phone,
    skills: item.skills || [],
    avatar: item.avatar || '',
    desc: item.desc || '',
    team: item.team || '',
    showOnMobile: item.showOnMobile !== false
  }
  dialogVisible.value = true
}

const saveEngineer = async () => {
  try {
    if (isEdit.value) {
      await updateContactEngineer(form.value.id, {
        avatar: form.value.avatar,
        skills: form.value.skills,
        desc: form.value.desc,
        team: form.value.team,
        showOnMobile: form.value.showOnMobile
      })
    } else {
      if (!form.value.id) {
        ElMessage.warning('请选择工程师')
        return
      }
      await createContactEngineer({
        id: form.value.id,
        avatar: form.value.avatar,
        skills: form.value.skills,
        desc: form.value.desc,
        team: form.value.team
      })
    }
    ElMessage.success('配置已同步至公众号展示端')
    dialogVisible.value = false
    fetchEngineers()
  } catch { /* ignore */ }
}

const toggleShow = async (item) => {
  try {
    await updateContactEngineer(item.id, { showOnMobile: item.showOnMobile })
    ElMessage.success(item.showOnMobile ? '已开启展示' : '已关闭展示')
  } catch {
    item.showOnMobile = !item.showOnMobile
    fetchEngineers()
  }
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
.contact-config-container { padding: 20px; background: var(--bg-muted); min-height: calc(100vh - 110px); }
.header-flex { display: flex; justify-content: space-between; align-items: center; }
.title { font-weight: bold; border-left: 4px solid var(--color-accent); padding-left: 10px; }

/* 卡片样式 */
.engineer-card { transition: all 0.3s; border-radius: 10px; }
.engineer-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }

.card-body { padding: 20px; display: flex; align-items: center; gap: 15px; }
.info { flex: 1; }
.name-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.name { font-size: 16px; font-weight: bold; color: var(--text-primary); }
.phone { font-size: 13px; color: var(--text-secondary); margin-bottom: 10px; }
.tags { display: flex; flex-wrap: wrap; gap: 5px; }

.card-footer { background: #fafafa; padding: 10px; text-align: center; border-top: 1px solid #f0f0f0; }
</style>
