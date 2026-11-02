<template>
  <div class="settings-container">
    <el-card shadow="never" class="settings-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title-text">系统设置</span>
          <el-button type="primary" :icon="Check" :loading="saving" @click="save">保存设置</el-button>
        </div>
      </template>

      <el-form :model="form" label-width="140px" class="settings-form">
        <el-divider content-position="left">基础信息</el-divider>
        <el-form-item label="系统名称">
          <el-input v-model="form.siteName" placeholder="系统名称" style="max-width: 360px" />
        </el-form-item>
        <el-form-item label="系统 Logo 地址">
          <el-input v-model="form.logo" placeholder="图片 URL（选填）" style="max-width: 360px" />
        </el-form-item>

        <el-divider content-position="left">登录与审批</el-divider>
        <el-form-item label="登录策略">
          <el-radio-group v-model="form.loginStrategy">
            <el-radio value="password">账号密码登录</el-radio>
            <el-radio value="approval">注册需审批</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="新用户审批">
          <el-switch v-model="form.approvalSwitch" active-text="开启" inactive-text="关闭" />
          <span class="field-hint">开启后新注册用户需管理员审批通过方可登录</span>
        </el-form-item>

        <el-divider content-position="left">密码策略</el-divider>
        <el-form-item label="最小密码长度">
          <el-input-number v-model="form.passwordPolicy.minLength" :min="4" :max="32" />
        </el-form-item>
        <el-form-item label="密码有效期(天)">
          <el-input-number v-model="form.passwordPolicy.expireDays" :min="0" :max="3650" />
          <span class="field-hint">0 表示永不过期</span>
        </el-form-item>

        <el-divider content-position="left">通知与数据保留</el-divider>
        <el-form-item label="站内通知">
          <el-switch v-model="form.notificationSwitch" active-text="开启" inactive-text="关闭" />
        </el-form-item>
        <el-form-item label="工单保留(天)">
          <el-input-number v-model="form.dataRetention.repairDays" :min="0" :max="3650" />
        </el-form-item>
        <el-form-item label="日志保留(天)">
          <el-input-number v-model="form.dataRetention.logDays" :min="0" :max="3650" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import { getSystemSettings, updateSystemSettings } from '@/api/modules/settings'

const loading = ref(false)
const saving = ref(false)
const form = reactive({
  siteName: '鸿瑞办公CMS',
  logo: '',
  loginStrategy: 'password',
  approvalSwitch: false,
  notificationSwitch: true,
  passwordPolicy: { minLength: 6, expireDays: 0 },
  dataRetention: { repairDays: 365, logDays: 180 },
})

const load = async () => {
  loading.value = true
  try {
    const res = await getSystemSettings()
    if (res) {
      form.siteName = res.siteName ?? form.siteName
      form.logo = res.logo ?? ''
      form.loginStrategy = res.loginStrategy ?? 'password'
      form.approvalSwitch = !!res.approvalSwitch
      form.notificationSwitch = res.notificationSwitch !== false
      form.passwordPolicy = { ...form.passwordPolicy, ...(res.passwordPolicy || {}) }
      form.dataRetention = { ...form.dataRetention, ...(res.dataRetention || {}) }
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const save = async () => {
  saving.value = true
  try {
    await updateSystemSettings({ ...form })
    ElMessage.success('系统设置已保存')
  } catch { /* ignore */ } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.settings-container { padding: 10px; background-color: var(--bg-muted); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title-text { font-weight: bold; font-size: 16px; }
.settings-card { border-radius: var(--radius-md); }
.settings-form { max-width: 640px; padding-top: 8px; }
.field-hint { margin-left: 12px; font-size: 12px; color: var(--text-muted); }
</style>
