<!--
  注册页面
  普通用户自主注册，提交后由管理员审核或直接开通
-->
<template>
  <view class="register-page">
    <!-- 头部 -->
    <view class="reg-header">
      <view class="back-btn" @click="goBack">
        <SvgIcon name="caretLeft" :size="20" />
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
          placeholder-style="color: #C9CDD4"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="input-label">真实姓名</text>
        <input
          class="input-field"
          v-model="form.realName"
          placeholder="您的真实姓名"
          placeholder-style="color: #C9CDD4"
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
          placeholder-style="color: #C9CDD4"
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
          placeholder-style="color: #C9CDD4"
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
          placeholder-style="color: #C9CDD4"
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
import SvgIcon from '@/components/SvgIcon.vue'

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
  background: #F5F7FA;
}

.reg-header {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 60%, #5B8DEF 100%);
  padding: 24rpx 32rpx;
  padding-top: calc(88rpx + env(safe-area-inset-top));
  padding-bottom: 72rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}
.reg-header::before {
  content: '';
  position: absolute;
  top: -120rpx;
  right: -100rpx;
  width: 360rpx;
  height: 360rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  position: relative;
  z-index: 1;
}

.header-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #FFFFFF;
  position: relative;
  z-index: 1;
}

.placeholder {
  width: 64rpx;
}

.reg-card {
  margin: -48rpx 24rpx 24rpx;
  background: #FFFFFF;
  border-radius: 32rpx;
  padding: 40rpx 32rpx;
  box-shadow: 0 -8rpx 60rpx rgba(22, 93, 255, 0.1);
  position: relative;
  z-index: 2;
}

.card-desc {
  font-size: 26rpx;
  color: #86909C;
  display: block;
  margin-bottom: 32rpx;
}

.input-group {
  margin-bottom: 24rpx;
}

.input-label {
  font-size: 26rpx;
  color: #4E5969;
  font-weight: 500;
  margin-bottom: 12rpx;
  display: block;
}

.required {
  color: #F53F3F;
}

.input-field {
  width: 100%;
  height: 88rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #1D2129;
  box-sizing: border-box;
}

.btn-register {
  width: 100%;
  height: 92rpx;
  line-height: 92rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  margin-top: 16rpx;
  text-align: center;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);
  transition: all 0.25s ease;

  &:active {
    transform: scale(0.97);
  }
  &[disabled] {
    background: #C9CDD4;
    box-shadow: none;
  }
}

.btn-loading {
  background: #86909C !important;
}

.reg-footer {
  display: flex;
  justify-content: center;
  margin-top: 24rpx;
  font-size: 26rpx;
  color: #86909C;

  .link {
    color: #165DFF;
    margin-left: 8rpx;
  }
}
</style>
