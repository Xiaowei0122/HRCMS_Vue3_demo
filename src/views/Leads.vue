<template>
  <div class="leads-container">
    <el-card shadow="never" class="header-card">
      <template #header>
        <div class="header-filter">
          <div class="left">
            <el-radio-group v-model="filterStatus" size="default">
              <el-radio-button label="all">全部需求单</el-radio-button>
              <el-radio-button label="pending">待处理</el-radio-button>
              <el-radio-button label="following">跟进中</el-radio-button>
              <el-radio-button label="completed">已成交</el-radio-button>
            </el-radio-group>
          </div>
          <div class="right">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="default"
              style="margin-right: 10px"
            />
            <el-button type="primary" icon="Download">导出报表</el-button>
          </div>
        </div>
      </template>

      
<el-table :data="filteredLeads" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        
        <el-table-column label="客户信息" width="200">
          <template #default="{row}">
            <div class="client-info">
              <div class="name"><strong>{{ row.name }}</strong></div>
              <div class="phone"><el-icon><Phone /></el-icon> {{ row.phone }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="productName" label="意向产品/服务" width="220">
          <template #default="{row}">
            <el-tag size="small" type="info" effect="plain">{{ row.category }}</el-tag>
            <span style="margin-left: 8px; font-size: 13px;">{{ row.productName }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="content" label="留言详情" show-overflow-tooltip />

        
<el-table-column label="当前状态" width="120" align="center">
          <template #default="{row}">
            <el-tag :type="getStatusMap(row.status).type" effect="light" round>
              ● {{ getStatusMap(row.status).label }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="提交时间" width="160" sortable />

        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="scope">
            
<el-button link type="primary" @click="viewDetail(scope.row)" style="font-weight: bold;">
              跟进处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-box">
        <el-pagination background layout="prev, pager, next" :total="leadsList.length" />
      </div>
    </el-card>

    
<el-dialog 
      v-model="detailVisible" 
      title="线索详情与跟进" 
      width="600px"
      custom-class="fancy-dialog"
    >
      <el-row :gutter="20">
        
<el-col :span="16">
          <el-descriptions :column="1" border size="default" class="lead-descriptions">
            <el-descriptions-item label="客户名称">{{ currentLead.name }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ currentLead.phone }}</el-descriptions-item>
            <el-descriptions-item label="具体诉求" class-name="訴求-content">
              {{ currentLead.content }}
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
        
        
<el-col :span="8" class="status-col">
          <div class="status-label">当前状态</div>
          <el-tag :type="getStatusMap(currentLead.status).type" effect="dark" size="large" round class="status-tag">
            {{ getStatusMap(currentLead.status).label }}
          </el-tag>
        </el-col>
      </el-row>

      
<div class="remark-section">
        <p class="section-title">跟进记录</p>
        <el-input 
          v-model="currentLead.remark" 
          type="textarea" 
          :rows="4" 
          placeholder="请输入此次联系的情况，如：已回访，客户下周一来看机型。" 
        />
      </div>

      
<div class="status-change-section">
        <p class="section-title">修改线索状态</p>
        <el-radio-group v-model="currentLead.status" size="default">
          <el-radio-button label="pending">待处理</el-radio-button>
          <el-radio-button label="following">跟进中</el-radio-button>
          <el-radio-button label="completed">已成交</el-radio-button>
          <el-radio-button label="closed">无效/关闭</el-radio-button>
        </el-radio-group>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProgress">保存跟进结果</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Phone } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const filterStatus = ref('all')
const dateRange = ref('')
const detailVisible = ref(false)
const currentLead = ref({})

// 模拟线索数据
const leadsList = ref([
  { id: 1, name: '张经理', phone: '138xxxx8888', category: '设备租赁', productName: '理光彩色复合机租赁', content: '在高新区办新办公室，需要租两台彩机，求报价。', status: 'pending', createTime: '2024-04-03 10:20', remark: '' },
  { id: 2, name: '李老师', phone: '159xxxx2233', category: '设备采购', productName: '佳能绘图仪', content: '学校设计院需要采购一台宽幅绘图仪，需要上门安装服务。', status: 'following', createTime: '2024-04-02 15:45', remark: '已初步沟通，客户在走审批流程。' },
  { id: 3, name: '王小姐', phone: '133xxxx9900', category: '售后维修', productName: '施乐复印机维修', content: '机器报代码E001，请尽快安排技术员。', status: 'completed', createTime: '2024-04-01 09:10', remark: '已成交。' }
])

// 状态映射表（用于颜色和文字）
const getStatusMap = (status) => {
  const map = {
    pending: { label: '待处理', type: 'danger' },   // 红色
    following: { label: '跟进中', type: 'primary' }, // 蓝色
    completed: { label: '已成交', type: 'success' }, // 绿色
    closed: { label: '已关闭', type: 'info' }       // 灰色
  }
  return map[status] || map.pending
}

const filteredLeads = computed(() => {
  if (filterStatus.value === 'all') return leadsList.value
  return leadsList.value.filter(item => item.status === filterStatus.value)
})

const viewDetail = (row) => {
  currentLead.value = { ...row } // 浅拷贝，防止直接修改表格数据
  detailVisible.value = true
}

const saveProgress = () => {
  // 实际项目中这里会调用API保存remark和status
  // 这里仅做模拟：找到原数据并更新
  const index = leadsList.value.findIndex(item => item.id === currentLead.value.id)
  if (index !== -1) {
    leadsList.value[index] = { ...currentLead.value }
  }
  ElMessage.success('跟进记录及状态已保存')
  detailVisible.value = false
}
</script>

<style scoped>
.header-card { margin-bottom: 20px; }
.header-filter { display: flex; justify-content: space-between; align-items: center; }

.client-info .name { color: #303133; margin-bottom: 4px; font-size: 14px; }
.client-info .phone { color: #909399; font-size: 12px; display: flex; align-items: center; gap: 4px; }

:deep(.诉求-content) { color: #606266; font-size: 13px; line-height: 1.6; }

.pagination-box { margin-top: 20px; display: flex; justify-content: flex-end; }

/* --- 弹窗美化样式 --- */
.fancy-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #ebeef5;
  margin-right: 0;
  padding-bottom: 15px;
}

.fancy-dialog :deep(.el-dialog__body) {
  padding: 20px 25px;
}

.lead-descriptions { border-radius: 4px; overflow: hidden; }

.status-col {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border-left: 1px solid #ebeef5; padding-left: 30px !important;
}
.status-label { font-size: 13px; color: #909399; margin-bottom: 10px; }
.status-tag { font-weight: bold; padding: 0 20px; }

.section-title { font-weight: bold; color: #303133; font-size: 14px; margin: 20px 0 10px 0; }

.remark-section :deep(.el-textarea__inner) { background-color: #fcfcfc; }

.status-change-section {
  background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px;
  border: 1px solid #eee;
}
</style>