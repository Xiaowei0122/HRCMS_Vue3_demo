<!--
  注册页面
  普通用户自主注册，提交后由管理员审核或直接开通
-->
<template>
  <view class="register-page">
    <!-- 头部 -->
    <view class="reg-header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="header-title">注册账号</text>
      <view class="placeholder"></view>
    </view>

    <!-- 注册表单 -->
    <view class="reg-card">
      <text class="card-desc">注册后可使用一键报修、投诉建议等功能</text>

      <view class="input-group">
        <text class="input-label">用户名 <text class="required">*</text></text>
        <input
          class="input-field"
          v-model="form.username"
          placeholder="用于登录的用户名（4-20位）"
          placeholder-style="color: #ccc"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="input-label">真实姓名</text>
        <input
          class="input-field"
          v-model="form.realName"
          placeholder="您的真实姓名"
          placeholder-style="color: #ccc"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="input-label">手机号码 <text class="required">*</text></text>
        <input
          class="input-field"
          v-model="form.phone"
          type="number"
          placeholder="用于联系您的手机号"
          placeholder-style="color: #ccc"
          maxlength="11"
        />
      </view>

      <view class="input-group">
        <text class="input-label">密码 <text class="required">*</text></text>
        <input
          class="input-field"
          v-model="form.password"
          type="password"
          placeholder="6-20位登录密码"
          placeholder-style="color: #ccc"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="input-label">确认密码 <text class="required">*</text></text>
        <input
          class="input-field"
          v-model="form.confirmPassword"
          type="password"
          placeholder="再次输入密码"
          placeholder-style="color: #ccc"
          maxlength="20"
        />
      </view>

      <button
        class="btn-register"
        :class="{ 'btn-loading': loading }"
        :disabled="loading"
        @click="handleRegister"
      >
        {{ loading ? '注册中...' : '注 册' }}
      </button>

      <view class="reg-footer">
        <text>已有账号？</text>
        <text class="link" @click="goLogin">返回登录</text>
      </view>
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
  realName: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

const validate = () => {
  const { username, phone, password, confirmPassword } = form.value
  if (!username.trim() || username.trim().length < 4) {
    uni.showToast({ title: '用户名至少4位', icon: 'none' })
    return false
  }
  if (!phone || !/^1\d{10}$/.test(phone)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return false
  }
  if (!password || password.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' })
    return false
  }
  if (password !== confirmPassword) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' })
    return false
  }
  return true
}

const handleRegister = async () => {
  if (!validate()) return

  loading.value = true
  try {
    await authStore.register({
      username: form.value.username.trim(),
      realName: form.value.realName.trim(),
      phone: form.value.phone,
      password: form.value.password,
      userType: 'normal'
    })

    uni.showToast({ title: '注册成功，请登录', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 800)
  } catch (err) {
    console.error('注册失败:', err)
  } finally {
    loading.value = false
  }
}

const goBack = () => uni.navigateBack()
const goLogin = () => uni.navigateBack()
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  background: #F7F7F7;
}

.reg-header {
  background: #D32223;
  padding: 24rpx 32rpx;
  padding-top: calc(88rpx + env(safe-area-inset-top));
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 40rpx;
  color: #FFFFFF;
  font-weight: 300;
}

.header-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #FFFFFF;
}

.placeholder {
  width: 60rpx;
}

.reg-card {
  margin: 24rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 36rpx 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.card-desc {
  font-size: 26rpx;
  color: #999;
  display: block;
  margin-bottom: 32rpx;
}

.input-group {
  margin-bottom: 24rpx;
}

.input-label {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  margin-bottom: 8rpx;
  display: block;
}

.required {
  color: #D32223;
}

.input-field {
  width: 100%;
  height: 80rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.btn-register {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #D32223;
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  margin-top: 16rpx;
  text-align: center;

  &:active { opacity: 0.85; }
  &[disabled] { background: #CCCCCC; }
}

.reg-footer {
  display: flex;
  justify-content: center;
  margin-top: 24rpx;
  font-size: 26rpx;
  color: #999;

  .link { color: #D32223; margin-left: 8rpx; }
}
</style>
