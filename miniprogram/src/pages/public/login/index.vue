<!--
  登录页面
  品牌红色头部 + 白色表单卡片 + 动画过渡
-->
<template>
  <view class="login-page">
    <!-- 头部品牌区域 -->
    <view class="login-header">
      <view class="logo-circle">
        <text class="logo-text">鸿瑞</text>
      </view>
      <text class="company-name">鸿瑞办公售后服务中心</text>
      <text class="company-desc">专业办公设备维修 · 高效响应</text>
    </view>

    <!-- 登录表单卡片 -->
    <view class="login-card">
      <text class="card-title">用户登录</text>

      <!-- 用户名 -->
      <view class="input-group">
        <view class="input-icon">👤</view>
        <input
          class="input-field"
          v-model="form.username"
          placeholder="请输入用户名"
          placeholder-style="color: #ccc"
          maxlength="32"
        />
      </view>

      <!-- 密码 -->
      <view class="input-group">
        <view class="input-icon">🔒</view>
        <input
          class="input-field"
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          placeholder-style="color: #ccc"
          maxlength="32"
        />
      </view>

      <!-- 登录按钮 -->
      <button
        class="btn-login"
        :class="{ 'btn-loading': loading }"
        :disabled="loading"
        @click="handleLogin"
      >
        {{ loading ? '登录中...' : '登 录' }}
      </button>

      <!-- 底部链接 -->
      <view class="login-footer">
        <text class="link" @click="goRegister">还没有账号？立即注册</text>
      </view>
    </view>

    <!-- 测试账号提示 -->
    <view class="test-tips">
      <text class="tips-title">📌 测试账号</text>
      <text class="tips-text">普通用户：user / 123456</text>
      <text class="tips-text">内部员工：suser / 123456</text>
      <text class="tips-text">工程师：engineer / 123456</text>
      <text class="tips-text">管理员：admin / 123456</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  // 校验
  if (!form.value.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!form.value.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const userInfo = await authStore.login(form.value.username.trim(), form.value.password)

    uni.showToast({ title: '登录成功', icon: 'success' })

    // 根据角色跳转主页
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/public/home/index' })
    }, 500)
  } catch (err) {
    // request.js 已处理 toast
    console.error('登录失败:', err)
  } finally {
    loading.value = false
  }
}

const goRegister = () => {
  uni.navigateTo({ url: '/pages/public/register/index' })
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #D32223 0%, #B81C1D 50%, #8B1516 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 40rpx 40rpx;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
  animation: fadeInDown 0.6s ease;
}

.logo-circle {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  backdrop-filter: blur(10px);
}

.logo-text {
  font-size: 36rpx;
  font-weight: 800;
  color: #FFFFFF;
}

.company-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 8rpx;
}

.company-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.75);
}

.login-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 48rpx 36rpx 36rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.15);
  animation: fadeInUp 0.6s ease;
}

.card-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #222;
  text-align: center;
  display: block;
  margin-bottom: 40rpx;
}

.input-group {
  display: flex;
  align-items: center;
  background: #F7F7F7;
  border-radius: 12rpx;
  padding: 0 20rpx;
  margin-bottom: 24rpx;
  transition: all 0.3s;

  &:focus-within {
    background: #FFF0F0;
    box-shadow: 0 0 0 2rpx #D32223 inset;
  }
}

.input-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
}

.input-field {
  flex: 1;
  height: 88rpx;
  font-size: 28rpx;
  color: #333;
}

.btn-login {
  width: 100%;
  height: 92rpx;
  line-height: 92rpx;
  background: #D32223;
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  margin-top: 20rpx;
  transition: all 0.3s ease;
  text-align: center;

  &:active {
    background: #B81C1D;
    transform: scale(0.97);
  }

  &[disabled] {
    background: #CCCCCC;
  }
}

.btn-loading {
  background: #E88888 !important;
}

.login-footer {
  display: flex;
  justify-content: center;
  margin-top: 32rpx;
}

.link {
  font-size: 26rpx;
  color: #D32223;
}

.test-tips {
  margin-top: 40rpx;
  padding: 24rpx 32rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12rpx;
  backdrop-filter: blur(10px);
  width: 100%;
  animation: fadeInUp 0.8s ease;
}

.tips-title {
  font-size: 24rpx;
  color: #FFFFFF;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}

.tips-text {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
  display: block;
  line-height: 1.6;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-40rpx); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(40rpx); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
