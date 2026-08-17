<template>
  <div class="login-wrapper">
    <div class="bg-grid"></div>
    <div class="bg-gradient-orb orb-1"></div>
    <div class="bg-gradient-orb orb-2"></div>

    <div class="login-box">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="28"><Platform /></el-icon>
        </div>
        <h1 class="title">鸿瑞办公数字化 CMS</h1>
        <p class="subtitle">技术引领办公，数字化赋能未来</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="管理员账号"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="登录密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <div class="extra-actions">
          <el-checkbox v-model="rememberMe">记住账号</el-checkbox>
          <el-button link type="primary">忘记密码？</el-button>
        </div>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            size="large"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '正在验证身份...' : '安全登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>© 2026 西安鸿瑞办公设备有限公司 版权所有</p>
        <p>技术支持：鸿瑞办公技术支持部 | v0.6</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Platform } from '@element-plus/icons-vue'
import { login as apiLogin } from '@/api/modules/auth'
import { setToken, setUserInfo } from '@/utils/auth'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(true)

const loginForm = reactive({
  username: 'admin',
  password: ''
})

const rules = reactive({
  username: [
    { required: true, message: '请输入管理员账号', trigger: 'blur' },
    { min: 3, message: '账号长度至少3位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
})

const handleLogin = async () => {
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) {
    ElMessage.warning('请完善登录信息')
    return
  }

  loading.value = true
  try {
    const res = await apiLogin({
      username: loginForm.username,
      password: loginForm.password
    })
    setToken(res.token)
    setUserInfo(res.userInfo)

    ElNotification({
      title: '登录成功',
      message: `欢迎回来，${res.userInfo?.realName || '管理员'}！`,
      type: 'success',
      duration: 2500
    })

    router.push('/dashboard')
  } catch {
    // 错误信息已由 request.js 拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ═══ 背景 ═══ */
.login-wrapper {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
  position: relative;
  overflow: hidden;
  font-family: var(--font-sans);
}

.bg-grid {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-image: url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath d="M30 0 L30 60 M0 30 L60 30" stroke="rgba(255,255,255,0.03)" stroke-width="0.5" /%3E%3C/svg%3E');
  opacity: 0.6;
}

.bg-gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(3, 105, 161, 0.5), transparent 70%);
  top: -150px; left: -100px;
}

.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.4), transparent 70%);
  bottom: -100px; right: -80px;
}

/* ═══ 登录卡片 ═══ */
.login-box {
  width: 440px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
  padding: 48px 44px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  z-index: 10;
}

/* ═══ 头部 ═══ */
.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  width: 52px;
  height: 52px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent);
  color: #fff;
  border-radius: var(--radius-md);
  box-shadow: 0 0 24px rgba(3, 105, 161, 0.5);
  margin-bottom: 16px;
}

.title {
  color: #fff;
  font-size: 22px;
  margin: 0 0 8px 0;
  font-weight: var(--font-bold);
  letter-spacing: 0.02em;
}

.subtitle {
  color: #94A3B8;
  font-size: var(--text-base);
  margin: 0;
  font-weight: var(--font-normal);
}

/* ═══ 表单 ═══ */
.login-form :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.06) !important;
  box-shadow: none !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.login-form :deep(.el-input.is-focus .el-input__wrapper) {
  border-color: var(--color-accent) !important;
  box-shadow: 0 0 0 2px rgba(3, 105, 161, 0.3) !important;
}

.login-form :deep(.el-input__inner) {
  color: #fff !important;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: #64748B !important;
}

.extra-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: var(--text-sm);
}

:deep(.el-checkbox__label) {
  color: #94A3B8 !important;
}

/* ═══ 登录按钮 ═══ */
.login-btn {
  width: 100%;
  height: 46px;
  background: var(--color-accent) !important;
  border: none !important;
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  letter-spacing: 2px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.login-btn:hover {
  background: var(--color-accent-hover) !important;
  box-shadow: 0 4px 20px rgba(3, 105, 161, 0.4);
}

.login-btn:active {
  transform: scale(0.98);
}

/* ═══ 底部 ═══ */
.login-footer {
  text-align: center;
  margin-top: 36px;
  font-size: var(--text-xs);
  color: #64748B;
  line-height: 1.8;
}
</style>
