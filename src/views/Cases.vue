<template>
  <div class="cases-container">
    <el-tabs v-model="activeTab" type="border-card" class="case-tabs">
      
      <!-- 1. 品牌管理 (上游供应商/授权品牌) -->
      <el-tab-pane label="合作代理品牌" name="brands">
        <div class="tab-header">
          <el-alert title="此处上传展示在官网首页的品牌 Logo，建议尺寸 240x120px，透明背景 PNG 格式最佳。" type="info" show-icon :closable="false" />
          <el-button type="primary" icon="Plus" @click="addBrand">新增品牌链接</el-button>
        </div>

        <el-table :data="brandList" border stripe style="margin-top: 20px">
          <el-table-column label="品牌Logo" width="180">
            <template #default="{row}">
              <el-image :src="row.logo" fit="contain" style="width: 120px; height: 50px; background: #f5f7fa" />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="品牌名称" width="200" />
          <el-table-column prop="level" label="授权等级">
            <template #default="{row}">
              <el-tag effect="plain">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="url" label="品牌官网" show-overflow-tooltip />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button link type="primary">编辑</el-button>
              <el-button link type="danger" @click="brandList.splice(scope.$index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 2. 销售案例 (成功案例/客户见证) -->
      <el-tab-pane label="典型销售案例" name="cases">
        <div class="tab-header">
          <el-input v-model="searchCase" placeholder="搜索案例名称..." style="width: 300px">
            <template #append><el-button icon="Search" /></template>
          </el-input>
          <el-button type="success" icon="CirclePlus" @click="addCase">发布新案例</el-button>
        </div>

        <div class="case-grid">
          <el-row :gutter="20">
            <el-col :span="8" v-for="(item, index) in caseList" :key="index">
              <el-card class="case-item" shadow="hover">
                <template #header>
                  <div class="case-title">
                    <span>{{ item.client }}</span>
                    <el-tag size="small">{{ item.industry }}</el-tag>
                  </div>
                </template>
                <div class="case-content">
                  <p><strong>交付设备：</strong>{{ item.device }}</p>
                  <p><strong>服务模式：</strong>{{ item.mode }}</p>
                  <p class="desc">{{ item.summary }}</p>
                </div>
                <div class="case-footer">
                  <span class="date">{{ item.date }}</span>
                  <div class="btns">
                    <el-button icon="Edit" size="small" circle />
                    <el-button type="danger" icon="Delete" size="small" circle />
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

    </el-tabs>

    <!-- 公用对话框 (略，可根据需求定制上传表单) -->
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('brands')
const searchCase = ref('')

// 品牌数据
const brandList = ref([
  { name: '理光 (Ricoh)', logo: 'https://cdn.worldvectorlogo.com/logos/ricoh-logo.svg', level: '核心代理商', url: 'https://www.ricoh.com.cn' },
  { name: '施乐 (Fuji Xerox)', logo: 'https://cdn.worldvectorlogo.com/logos/fuji-xerox.svg', level: '战略合作伙伴', url: 'https://www.fujifilm.com' },
  { name: '佳能 (Canon)', logo: 'https://cdn.worldvectorlogo.com/logos/canon-1.svg', level: '特约经销商', url: 'https://www.canon.com.cn' }
])

// 案例数据
const caseList = ref([
  { 
    client: '西安某大型国有建筑集团', 
    industry: '建筑业', 
    device: '理光 IM C3000 x 12台', 
    mode: '全包租赁服务', 
    summary: '解决客户多部门分散打印、耗材管理混乱问题，月节省成本约25%。',
    date: '2024-03' 
  },
  { 
    client: '高新区某外语学校', 
    industry: '教育行业', 
    device: '施乐 高速数码复合机 x 5台', 
    mode: '按张计费模式', 
    summary: '针对学校试卷打印量大的特性，提供高可靠性维护方案。',
    date: '2023-12' 
  },
  { 
    client: '某知名设计研究院', 
    industry: '设计/传媒', 
    device: '佳能 彩色宽幅绘图仪', 
    mode: '设备采购+维保', 
    summary: '满足高精度图纸输出需求，提供24小时上门响应服务。',
    date: '2024-01' 
  }
])

const addBrand = () => { /* 弹出新增品牌表单 */ }
const addCase = () => { /* 弹出发布案例表单 */ }
</script>

<style scoped>
.case-tabs { min-height: 500px; }
.tab-header { display: flex; justify-content: space-between; align-items: center; gap: 20px; margin-bottom: 10px; }

.case-grid { margin-top: 20px; }
.case-item { margin-bottom: 20px; }
.case-title { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }

.case-content p { font-size: 13px; margin: 8px 0; color: #606266; }
.case-content .desc { 
  font-style: italic; color: #909399; margin-top: 12px; 
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  line-clamp: 2;
}

.case-footer { 
  margin-top: 15px; padding-top: 10px; border-top: 1px solid #ebeef5;
  display: flex; justify-content: space-between; align-items: center;
}
.case-footer .date { font-size: 12px; color: #999; }
</style>