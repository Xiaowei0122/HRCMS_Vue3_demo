<template>
  <div class="login-wrapper">
    <div class="background-decor"></div>

    <div class="login-box">
      <div class="login-header">
        <el-icon class="logo-icon" color="#fff" :size="32"><Platform /></el-icon>
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
    // res 已被拦截器解包：{ token, userInfo }
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
.login-wrapper {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0b1c31;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(20, 110, 240, 0.3) 0%, transparent 40%),
    radial-gradient(circle at 80% 80%, rgba(24, 200, 240, 0.2) 0%, transparent 40%);
  position: relative;
  overflow: hidden;
}

.background-decor {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-image: url('data:image/svg+xml,%3Csvg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath d="M10 10 L90 90 M90 10 L10 90" stroke="rgba(255,255,255,0.03)" stroke-width="1" /%3E%3C/svg%3E');
  opacity: 0.5;
}

.login-box {
  width: 480px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 50px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 10;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}
.logo-icon {
  background: rgba(64, 158, 255, 0.8);
  padding: 10px;
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(64, 158, 255, 0.5);
  margin-bottom: 15px;
}
.title {
  color: #fff;
  font-size: 24px;
  margin: 0 0 10px 0;
  font-weight: bold;
}
.subtitle {
  color: #adb5bd;
  font-size: 14px;
  margin: 0;
}

.login-form :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.08) !important;
  box-shadow: none !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 4px;
}
.login-form :deep(.el-input__inner) {
  color: #fff !important;
}
.login-form :deep(.el-input__inner::placeholder) {
  color: #8d97a1 !important;
}

.extra-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  font-size: 13px;
}
:deep(.el-checkbox__label) { color: #adb5bd !important; }

.login-btn {
  width: 100%;
  height: 46px;
  background: linear-gradient(90deg, #409eff, #36d1dc);
  border: none;
  font-size: 16px;
  letter-spacing: 2px;
}
.login-btn:hover {
  filter: brightness(1.1);
}

.login-footer {
  text-align: center;
  margin-top: 40px;
  font-size: 12px;
  color: #8d97a1;
  line-height: 1.8;
}
</style>
