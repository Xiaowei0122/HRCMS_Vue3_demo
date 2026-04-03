<template>
  <el-form :model="form" label-position="top" class="embedded-repair-form">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="报修单位" required>
          <el-input v-model="form.company" placeholder="请输入单位全称" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="报修日期">
          <el-date-picker v-model="form.date" type="date" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="联系人" required>
          <el-input v-model="form.contact" placeholder="姓名" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="联系电话" required>
          <el-input v-model="form.phone" placeholder="手机号" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="用户地址">
      <el-input v-model="form.address" placeholder="具体街道、楼层、房间号" />
    </el-form-item>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="紧急程度">
          <el-select v-model="form.priority" style="width: 100%">
            <el-option label="普通 (24小时内)" value="普通" />
            <el-option label="紧急 (4小时内)" value="紧急" />
            <el-option label="特急 (立即响应)" value="特急" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="单号生成">
          <el-input v-model="form.orderNo" disabled placeholder="自动生成" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="基本情况 / 故障描述">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="4"
        placeholder="请描述设备故障现象，如：打印有黑线、机器报错代码C-2557等"
      />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive } from 'vue'

const form = reactive({
  company: '',
  date: new Date(),
  contact: '',
  phone: '',
  address: '',
  priority: '普通',
  orderNo: 'HR' + Date.now().toString().slice(-8),
  description: ''
})

// 暴露给父组件的方法
defineExpose({
  submitForm: () => {
    console.log('提交数据：', form)
    return form
  }
})
</script>

<style scoped>
.embedded-repair-form :deep(.el-form-item__label) {
  font-weight: bold;
  color: #606266;
  padding-bottom: 4px;
}
</style>