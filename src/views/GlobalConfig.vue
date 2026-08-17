<template>
  <div class="config-container">
    <el-tabs v-model="activeTab" type="border-card" class="config-tabs">

      <!-- 1. 基础信息 -->
      <el-tab-pane label="基础信息" name="basic">
        <el-form :model="config.basic" label-width="120px" class="config-form">
          <el-form-item label="网站名称">
            <el-input v-model="config.basic.siteName" placeholder="请输入官网显示的名称" />
          </el-form-item>
          <el-form-item label="网站LOGO">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :http-request="handleLogoUpload"
            >
              <img v-if="config.basic.logo" :src="config.basic.logo" class="logo-preview" />
              <el-icon v-else class="uploader-icon"><Plus /></el-icon>
              <template #tip>
                <div class="el-upload__tip">建议尺寸 200x200px，支持 PNG/JPG</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item label="IPC备案号">
            <el-input v-model="config.basic.icp" placeholder="陕ICP备XXXXXXXX号" />
          </el-form-item>
          <el-form-item label="网安备案号">
            <el-input v-model="config.basic.gongan" placeholder="陕公网安备 XXXXXXXXXXXXXX号" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveConfig('basic')">保存全局设置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 2. 首页轮播图 -->
      <el-tab-pane label="首页轮播图" name="banner">
        <div class="tab-header">
          <el-alert title="建议上传 1920x600px 的高清大图以保证首页展示效果" type="info" show-icon :closable="false" />
          <el-button type="primary" icon="Plus" @click="openBannerDialog()" style="margin: 15px 0">新增轮播图</el-button>
        </div>
        <el-table :data="config.banners" border stripe>
          <el-table-column label="预览" width="200">
            <template #default="{row}">
              <el-image :src="row.url" fit="cover" :preview-src-list="[row.url]" class="table-img" />
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="link" label="跳转链接" />
          <el-table-column label="操作" width="150" align="center">
            <template #default="scope">
              <el-button link type="primary" @click="openBannerDialog(scope.row, scope.$index)">编辑</el-button>
              <el-button link type="danger" @click="handleDeleteBanner(scope.row, scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 3. 联系方式 -->
      <el-tab-pane label="联系方式" name="contact">
        <el-form :model="config.contact" label-width="120px" class="config-form">
          <el-form-item label="服务热线">
            <el-input v-model="config.contact.phone" />
          </el-form-item>
          <el-form-item label="业务电话">
            <el-input v-model="config.contact.businessPhone" placeholder="与售后热线不同时填写，例如销售咨询专线" />
          </el-form-item>
          <el-form-item label="公司邮箱">
            <el-input v-model="config.contact.email" />
          </el-form-item>
          <el-form-item label="营业时间">
            <el-input v-model="config.contact.workingHours" placeholder="例如：周一至周五 9:00-18:00" />
          </el-form-item>
          <el-form-item label="详细地址">
            <el-input v-model="config.contact.address" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveConfig('contact')">更新联系信息</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 4. 地图位置 -->
      <el-tab-pane label="地图位置" name="map">
        <div class="map-layout">
          <div class="map-form">
            <el-form :model="config.map" label-width="100px">
              <el-form-item label="纬度">
                <el-input-number v-model="config.map.latitude" :precision="6" :step="0.001" :controls="false" style="width: 100%" />
              </el-form-item>
              <el-form-item label="经度">
                <el-input-number v-model="config.map.longitude" :precision="6" :step="0.001" :controls="false" style="width: 100%" />
              </el-form-item>
              <el-form-item label="缩放级别">
                <el-slider v-model="config.map.zoom" :min="3" :max="20" show-stops />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveConfig('map')">保存地图设置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div class="map-visual">
            <div class="mock-map-bg">
              <div class="map-marker">
                <el-icon color="var(--color-danger)" size="40"><LocationFilled /></el-icon>
                <div class="marker-label">{{ config.basic.siteName }}</div>
              </div>
              <div class="map-controls">
                <span>+</span>
                <span>-</span>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 5. 服务板块 -->
      <el-tab-pane label="服务板块" name="services">
        <div class="tab-header">
          <el-button type="primary" icon="Plus" @click="addService">新增服务</el-button>
        </div>
        <el-table :data="config.services" border stripe>
          <el-table-column prop="icon" label="图标" width="100" align="center" />
          <el-table-column label="标题" width="200">
            <template #default="{row}">
              <el-input v-model="row.title" placeholder="服务标题" />
            </template>
          </el-table-column>
          <el-table-column label="描述">
            <template #default="{row}">
              <el-input v-model="row.desc" placeholder="服务描述" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" align="center">
            <template #default="scope">
              <el-button link type="danger" @click="config.services.splice(scope.$index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 15px">
          <el-button type="primary" @click="saveServices">保存服务板块</el-button>
        </div>
      </el-tab-pane>

      <!-- 6. 关于我们 -->
      <el-tab-pane label="关于我们" name="about">
        <el-form label-width="120px" class="config-form">
          <el-form-item label="企业简介">
            <el-input v-model="config.about.intro" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>

        <el-divider content-position="left">数据统计</el-divider>
        <el-table :data="config.about.stats" border stripe style="margin-bottom: 15px">
          <el-table-column label="数值" width="200">
            <template #default="{row}">
              <el-input v-model="row.num" placeholder="例如：20+" />
            </template>
          </el-table-column>
          <el-table-column label="说明">
            <template #default="{row}">
              <el-input v-model="row.label" placeholder="例如：全平台服务年限" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" align="center">
            <template #default="scope">
              <el-button link type="danger" @click="config.about.stats.splice(scope.$index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button icon="Plus" @click="addAboutItem('stats')" style="margin-bottom: 15px">新增统计</el-button>

        <el-divider content-position="left">企业文化</el-divider>
        <el-table :data="config.about.culture" border stripe style="margin-bottom: 15px">
          <el-table-column label="图标" width="100" align="center">
            <template #default="{row}">
              <el-input v-model="row.icon" placeholder="🤝" />
            </template>
          </el-table-column>
          <el-table-column label="标题" width="200">
            <template #default="{row}">
              <el-input v-model="row.title" />
            </template>
          </el-table-column>
          <el-table-column label="描述">
            <template #default="{row}">
              <el-input v-model="row.desc" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" align="center">
            <template #default="scope">
              <el-button link type="danger" @click="config.about.culture.splice(scope.$index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button icon="Plus" @click="addAboutItem('culture')" style="margin-bottom: 15px">新增文化条目</el-button>

        <el-divider content-position="left">部门架构</el-divider>
        <el-table :data="config.about.depts" border stripe style="margin-bottom: 15px">
          <el-table-column label="部门名称" width="240">
            <template #default="{row}">
              <el-input v-model="row.name" />
            </template>
          </el-table-column>
          <el-table-column label="职能">
            <template #default="{row}">
              <el-input v-model="row.duty" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" align="center">
            <template #default="scope">
              <el-button link type="danger" @click="config.about.depts.splice(scope.$index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button icon="Plus" @click="addAboutItem('depts')" style="margin-bottom: 15px">新增部门</el-button>

        <div style="margin-top: 15px">
          <el-button type="primary" @click="saveAbout">保存关于内容</el-button>
        </div>
      </el-tab-pane>

    </el-tabs>

    <!-- 轮播图编辑弹窗 -->
    <el-dialog v-model="bannerDialogVisible" :title="bannerEditIndex >= 0 ? '编辑轮播图' : '新增轮播图'" width="520px" append-to-body>
      <el-form :model="bannerForm" label-width="90px">
        <el-form-item label="标题">
          <el-input v-model="bannerForm.title" placeholder="例如：2026 新品发布" />
        </el-form-item>
        <el-form-item label="跳转链接">
          <el-input v-model="bannerForm.link" placeholder="例如：/products 或 https://..." />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            class="banner-uploader"
            :show-file-list="false"
            :http-request="handleBannerUpload"
          >
            <img v-if="bannerForm.url" :src="bannerForm.url" class="banner-preview" />
            <el-icon v-else class="banner-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bannerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBanner">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, LocationFilled } from '@element-plus/icons-vue'
import {
  getConfigFull, saveBasicConfig, saveContactConfig, saveMapConfig,
  getBanners, addBanner as apiAddBanner, updateBanner, deleteBanner,
  getServices, saveServices as apiSaveServices, getAbout, saveAbout as apiSaveAbout
} from '@/api/modules/config'
import { uploadFile } from '@/api/modules/upload'

const activeTab = ref('basic')

const config = reactive({
  basic: { siteName: '', logo: '', icp: '', gongan: '' },
  banners: [],
  contact: { phone: '', businessPhone: '', email: '', workingHours: '', address: '' },
  map: { latitude: 0, longitude: 0, zoom: 15 },
  services: [],
  about: { intro: '', stats: [], culture: [], depts: [] }
})

const bannerDialogVisible = ref(false)
const bannerEditIndex = ref(-1)
const bannerForm = reactive({ title: '', link: '', url: '' })

const fetchConfig = async () => {
  try {
    const res = await getConfigFull()
    if (!res) return
    if (res.basic) config.basic = { ...config.basic, ...res.basic }
    if (Array.isArray(res.banners)) config.banners = res.banners
    if (res.contact) config.contact = { ...config.contact, ...res.contact }
    if (res.map) config.map = { ...config.map, ...res.map }
    if (Array.isArray(res.services)) config.services = res.services
    if (res.about) config.about = { ...config.about, ...res.about }
  } catch { /* ignore */ }
}

const saveConfig = async (type) => {
  try {
    if (type === 'basic') await saveBasicConfig(config.basic)
    else if (type === 'contact') await saveContactConfig(config.contact)
    else if (type === 'map') await saveMapConfig(config.map)
    ElMessage.success('保存成功，官网已同步更新')
  } catch { /* ignore */ }
}

// ── Logo 上传 ─────────────────────────────────────
const handleLogoUpload = async ({ file, onSuccess, onError }) => {
  try {
    const res = await uploadFile(file, 'logos')
    config.basic.logo = res.url
    onSuccess && onSuccess(res)
    ElMessage.success('Logo 上传成功，记得保存基础信息')
  } catch (e) {
    onError && onError(e)
  }
}

// ── Banner 增删改 ─────────────────────────────────
const openBannerDialog = (row, index) => {
  if (row) {
    bannerEditIndex.value = index
    bannerForm.title = row.title || ''
    bannerForm.link = row.link || ''
    bannerForm.url = row.url || ''
  } else {
    bannerEditIndex.value = -1
    bannerForm.title = ''
    bannerForm.link = ''
    bannerForm.url = ''
  }
  bannerDialogVisible.value = true
}

const handleBannerUpload = async ({ file, onSuccess, onError }) => {
  try {
    const res = await uploadFile(file, 'banners')
    bannerForm.url = res.url
    onSuccess && onSuccess(res)
  } catch (e) {
    onError && onError(e)
  }
}

const confirmBanner = async () => {
  try {
    const data = { title: bannerForm.title, link: bannerForm.link, url: bannerForm.url }
    if (bannerEditIndex.value >= 0) {
      const row = config.banners[bannerEditIndex.value]
      await updateBanner(row._id || row.id, data)
      Object.assign(row, data)
      ElMessage.success('Banner 已更新')
    } else {
      const res = await apiAddBanner(data)
      config.banners.push(res || { _id: Date.now().toString(), ...data })
      ElMessage.success('Banner 已添加')
    }
    bannerDialogVisible.value = false
  } catch { /* ignore */ }
}

const handleDeleteBanner = async (banner, index) => {
  try {
    await deleteBanner(banner._id || banner.id)
    config.banners.splice(index, 1)
    ElMessage.success('Banner 已删除')
  } catch { /* ignore */ }
}

// ── 服务板块 ─────────────────────────────────────
const addService = () => {
  config.services.push({ id: '', icon: '🔧', title: '', desc: '' })
}

const saveServices = async () => {
  try {
    await apiSaveServices({ services: config.services })
    ElMessage.success('服务板块已保存')
  } catch { /* ignore */ }
}

// ── 关于我们 ─────────────────────────────────────
const addAboutItem = (key) => {
  const templates = {
    stats: { num: '', label: '' },
    culture: { title: '', desc: '', icon: '' },
    depts: { name: '', duty: '' },
  }
  config.about[key].push({ ...templates[key] })
}

const saveAbout = async () => {
  try {
    await apiSaveAbout({ about: config.about })
    ElMessage.success('关于内容已保存')
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.config-container { padding: 5px; }
.config-tabs { height: auto; min-height: 600px; }
.config-form { max-width: 700px; padding: 20px 0; }

/* 预览图样式 */
.logo-preview { width: 120px; height: 120px; border-radius: var(--radius-md); border: 1px solid var(--border-color); object-fit: contain; }
.uploader-icon { font-size: 28px; color: #8c939d; width: 120px; height: 120px; text-align: center; line-height: 120px; border: 1px dashed #d9d9d9; border-radius: var(--radius-md); }
.table-img { width: 160px; height: 80px; border-radius: 4px; display: block; }

.banner-uploader { width: 320px; }
.banner-preview { width: 320px; height: 100px; object-fit: cover; border-radius: 4px; border: 1px solid var(--border-color); display: block; }
.banner-uploader-icon { font-size: 28px; color: #8c939d; width: 320px; height: 100px; text-align: center; line-height: 100px; border: 1px dashed #d9d9d9; border-radius: 4px; }

/* 地图布局样式 */
.map-layout { display: grid; grid-template-columns: 400px 1fr; gap: 30px; padding: 20px 0; }
.mock-map-bg {
  width: 100%; height: 350px; background-color: #e5e3df; border-radius: 12px;
  position: relative; border: 1px solid #dcdfe6;
  background-image: radial-gradient(#d0d0d0 1px, transparent 0);
  background-size: 20px 20px;
}
.map-marker { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -100%); text-align: center; }
.marker-label { background: white; padding: 4px 12px; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-size: 12px; margin-top: 5px; white-space: nowrap; }
.map-controls { position: absolute; right: 20px; bottom: 20px; display: flex; flex-direction: column; gap: 5px; }
.map-controls span { width: 30px; height: 30px; background: white; border: 1px solid #ccc; display: flex; align-items: center; justify-content: center; cursor: pointer; border-radius: 4px; font-weight: bold; }
</style>
