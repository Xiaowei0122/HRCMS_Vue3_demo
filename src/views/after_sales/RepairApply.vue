<template>
  <div class="repair-apply-container">
    <el-card class="form-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title"><el-icon><EditPen /></el-icon> 新增报修工单</span>
          <el-tag type="info" effect="plain">单号自动生成</el-tag>
        </div>
      </template>

      <el-form :model="repairForm" :rules="rules" ref="formRef" label-width="100px" label-position="top">
        <el-row :gutter="40">
          <!-- 左侧：基本信息 -->
          <el-col :span="12" :xs="24">
            <el-form-item label="报修单位" prop="company">
              <el-input v-model="repairForm.company" placeholder="请输入单位全称" />
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="联系人" prop="contact">
                  <el-input v-model="repairForm.contact" placeholder="姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话" prop="phone">
                  <el-input v-model="repairForm.phone" placeholder="手机号" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="用户地址" prop="address">
              <el-input v-model="repairForm.address" type="textarea" :rows="2" placeholder="具体街道、楼层、房间号" />
            </el-form-item>
          </el-col>

          <!-- 右侧：故障描述 -->
          <el-col :span="12" :xs="24">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="报修日期">
                  <el-date-picker v-model="repairForm.date" type="date" style="width: 100%" readonly />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="紧急程度" prop="priority">
                  <el-select v-model="repairForm.priority" style="width: 100%">
                    <el-option label="普通 (24小时内)" value="low" />
                    <el-option label="紧急 (4小时内)" value="medium" />
                    <el-option label="特急 (立即处理)" value="high" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="基本情况 / 故障描述" prop="description">
              <el-input 
                v-model="repairForm.description" 
                type="textarea" 
                :rows="5" 
                placeholder="请详细描述设备故障现象，如：打印有黑线、机器报错代码C-2557等" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-footer">
          <el-button size="large" @click="resetForm">重置</el-button>
          <el-button type="primary" size="large" :loading="submitting" @click="submitRepair">
            立即提交报修
          </el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 提交成功后的弹窗 -->
    <el-dialog v-model="successVisible" title="报修提交成功" width="400px" align-center>
      <div class="success-box">
        <el-result icon="success" title="工单已生成" sub-title="请等待工程师接单">
          <template #extra>
            <p class="order-no">工单号：<strong>{{ generatedOrderNo }}</strong></p>
            <el-button type="primary" @click="goToList">查看我的报修</el-button>
          </template>
        </el-result>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { EditPen } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const formRef = ref(null)
const submitting = ref(false)
const successVisible = ref(false)
const generatedOrderNo = ref('')

// 表单数据
const repairForm = reactive({
  company: '',
  contact: '',
  phone: '',
  address: '',
  date: new Date(),
  priority: 'low',
  description: ''
})

// 校验规则
const rules = {
  company: [{ required: true, message: '请输入报修单位', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入电话', trigger: 'blur' }],
  description: [{ required: true, message: '请填写故障情况', trigger: 'blur' }]
}

// 核心逻辑：生成工单号 (HR + 年月日时分秒 + 5位随机数字)
const generateOrderNumber = () => {
  const now = new Date()
  const dateStr = now.getFullYear().toString() +
    (now.getMonth() + 1).toString().padStart(2, '0') +
    now.getDate().toString().padStart(2, '0') +
    now.getHours().toString().padStart(2, '0') +
    now.getMinutes().toString().padStart(2, '0') +
    now.getSeconds().toString().padStart(2, '0')
  
  const randomStr = Math.floor(Math.random() * 100000).toString().padStart(5, '0')
  return `HR${dateStr}${randomStr}`
}

const submitRepair = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      submitting.value = true
      // 模拟提交数据库
      setTimeout(() => {
        generatedOrderNo.value = generateOrderNumber()
        submitting.value = false
        successVisible.value = true
        console.log('提交的数据：', { ...repairForm, orderNo: generatedOrderNo.value })
      }, 800)
    }
  })
}

const resetForm = () => {
  formRef.value.resetFields()
}

const goToList = () => {
  successVisible.value = false
  // 这里跳转到“我的报修”页面
}
</script>

<style scoped>
.repair-apply-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header .title {
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}
.form-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
}
.success-box {
  text-align: center;
}
.order-no {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  color: #409EFF;
  margin-bottom: 20px;
}
</style>