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
              action="#"
              :auto-upload="false"
              :show-file-list="false"
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
            <el-input v-model="config.basic.security" placeholder="陕公网安备 XXXXXXXXXXXXXX号" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveConfig('基础信息')">保存全局设置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 2. 首页轮播图 -->
      <el-tab-pane label="首页轮播图" name="banner">
        <div class="tab-header">
          <el-alert title="建议上传 1920x600px 的高清大图以保证首页展示效果" type="info" show-icon :closable="false" />
          <el-button type="primary" icon="Plus" @click="addBanner" style="margin: 15px 0">新增轮播图</el-button>
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
              <el-button link type="primary">编辑</el-button>
              <el-button link type="danger" @click="config.banners.splice(scope.$index, 1)">删除</el-button>
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
          <el-form-item label="公司邮箱">
            <el-input v-model="config.contact.email" />
          </el-form-item>
          <el-form-item label="详细地址">
            <el-input v-model="config.contact.address" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveConfig('联系方式')">更新联系信息</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 4. 地图配置 (新增) -->
      <el-tab-pane label="地图位置" name="map">
        <div class="map-layout">
          <div class="map-form">
            <el-form :model="config.map" label-width="100px">
              <el-form-item label="地图厂家">
                <el-select v-model="config.map.provider" style="width: 100%">
                  <el-option label="高德地图" value="amap" />
                  <el-option label="百度地图" value="baidu" />
                </el-select>
              </el-form-item>
              <el-form-item label="API Key">
                <el-input v-model="config.map.apiKey" placeholder="请输入开发者 Key" show-password />
              </el-form-item>
              <el-form-item label="地理坐标">
                <el-input v-model="config.map.coordinate" placeholder="经度, 纬度">
                  <template #append>
                    <el-button icon="Location">拾取</el-button>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveConfig('地图配置')">保存地图设置</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <div class="map-visual">
            <div class="mock-map-bg">
              <div class="map-marker">
                <el-icon color="#F56C6C" size="40"><LocationFilled /></el-icon>
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

    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, LocationFilled, Location } from '@element-plus/icons-vue'

const activeTab = ref('basic')

const config = reactive({
  basic: {
    siteName: '西安鸿瑞办公设备有限公司',
    logo: 'https://api.dicebear.com/7.x/initials/svg?seed=HR',
    icp: '陕ICP备12345678号',
    security: '陕公网安备 610100000000号'
  },
  banners: [
    { url: 'https://picsum.photos/1200/600?random=1', title: '理光高端复印机租赁', link: '/products' },
    { url: 'https://picsum.photos/1200/600?random=2', title: '数字化办公解决方案', link: '/cases' }
  ],
  contact: {
    phone: '029-8822xxxx',
    email: 'hr_office@163.com',
    address: '西安市高新区嘉会巷1号'
  },
  map: {
    provider: 'amap',
    apiKey: '**********',
    coordinate: '108.8943, 34.2356'
  }
})

const saveConfig = (type) => {
  ElMessage({
    message: `${type}保存成功，官网已同步更新`,
    type: 'success',
    duration: 2000
  })
}

const addBanner = () => {
  config.banners.push({ url: 'https://picsum.photos/1200/600?random=' + Math.random(), title: '新活动海报', link: '' })
}
</script>

<style scoped>
.config-container { padding: 5px; }
.config-tabs { height: auto; min-height: 600px; }
.config-form { max-width: 700px; padding: 20px 0; }

/* 预览图样式 */
.logo-preview { width: 120px; height: 120px; border-radius: 8px; border: 1px solid #eee; object-fit: contain; }
.uploader-icon { font-size: 28px; color: #8c939d; width: 120px; height: 120px; text-align: center; line-height: 120px; border: 1px dashed #d9d9d9; border-radius: 8px; }
.table-img { width: 160px; height: 80px; border-radius: 4px; display: block; }

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