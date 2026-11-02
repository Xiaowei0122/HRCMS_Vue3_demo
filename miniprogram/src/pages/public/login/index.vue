<!--
  登录页面 — 蓝色渐变 · 账号/验证码 tabs · 微信一键登录
  保留原有 authStore.login / wechatLogin 逻辑
-->
<template>
  <view class="login-page">
    <!-- 顶部品牌区 -->
    <view class="login-top">
      <view class="login-close" @click="goHome">
        <SvgIcon name="x" :size="18" color="#fff" />
      </view>
      <view class="login-logo">
        <SvgIcon name="wrench" :size="36" color="#fff" />
      </view>
      <text class="login-title">欢迎登录</text>
      <text class="login-subtitle">IT运维报修服务平台</text>
    </view>

    <!-- 表单卡片 -->
    <view class="login-form-wrap">
      <view class="login-tabs">
        <text class="login-tab" :class="{ active: loginMode === 'account' }" @click="loginMode = 'account'">账号登录</text>
        <text class="login-tab" :class="{ active: loginMode === 'sms' }" @click="loginMode = 'sms'">验证码登录</text>
      </view>

      <!-- 账号登录 -->
      <template v-if="loginMode === 'account'">
        <view class="form-group">
          <text class="form-label">账号</text>
          <view class="form-input-wrap">
            <view class="form-input-icon"><SvgIcon name="user" :size="20" color="#86909C" /></view>
            <input class="form-input" v-model="form.username" placeholder="请输入手机号 / 用户名" placeholder-style="color:#C9CDD4" maxlength="32" />
          </view>
        </view>

        <view class="form-group">
          <text class="form-label">密码</text>
          <view class="form-input-wrap">
            <view class="form-input-icon"><SvgIcon name="lock" :size="20" color="#86909C" /></view>
            <input class="form-input" v-model="form.password" type="password" placeholder="请输入密码" placeholder-style="color:#C9CDD4" maxlength="32" />
          </view>
        </view>
      </template>

      <!-- 验证码登录 -->
      <template v-else>
        <view class="form-group">
          <text class="form-label">手机号</text>
          <view class="form-input-wrap">
            <view class="form-input-icon"><SvgIcon name="phone" :size="20" color="#86909C" /></view>
            <input class="form-input" v-model="form.phone" type="number" placeholder="请输入手机号" placeholder-style="color:#C9CDD4" maxlength="11" />
          </view>
        </view>

        <view class="form-group">
          <text class="form-label">验证码</text>
          <view class="form-input-wrap">
            <view class="form-input-icon"><SvgIcon name="lock" :size="20" color="#86909C" /></view>
            <input class="form-input" v-model="form.code" type="number" placeholder="请输入验证码" placeholder-style="color:#C9CDD4" maxlength="6" />
            <button class="form-code-btn" @click="getCode">获取验证码</button>
          </view>
        </view>
      </template>

      <view class="form-options">
        <view class="form-remember" @click="rememberPwd = !rememberPwd">
          <view class="form-checkbox" :class="{ checked: rememberPwd }">
            <SvgIcon v-if="rememberPwd" name="check" :size="12" color="#fff" />
          </view>
          <text>记住密码</text>
        </view>
        <text class="form-forgot" @click="forgotPwd">忘记密码？</text>
      </view>

      <button class="login-submit" :disabled="loading" @click="handleLogin">
        {{ loading ? '登录中...' : '登 录' }}
      </button>

      <view class="login-divider">
        <view class="login-divider-line"></view>
        <text class="login-divider-text">其他登录方式</text>
        <view class="login-divider-line"></view>
      </view>

      <button class="login-wechat-btn" :disabled="wechatLoading" @click="handleWechatLogin">
        <svg viewBox="0 0 24 24" class="wechat-svg"><path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.027-.407-.03zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z"/></svg>
        <text>{{ wechatLoading ? '微信登录中...' : '微信一键登录' }}</text>
      </button>

      <view class="login-agreement">
        <view class="form-checkbox" :class="{ checked: agreed }" @click="agreed = !agreed">
          <SvgIcon v-if="agreed" name="check" :size="12" color="#fff" />
        </view>
        <text>我已阅读并同意<text class="agreement-link">《用户协议》</text>和<text class="agreement-link">《隐私政策》</text></text>
      </view>
    </view>

    <view class="login-bottom">
      <text>还没有账号？</text><text class="login-bottom-link" @click="goRegister">立即注册</text>
    </view>

    <!-- 测试账号提示 -->
    <view class="test-tips">
      <text class="tips-title">测试账号（密码均为 123456）</text>
      <text class="tips-text">外部人员 user · 工程师 engineer · 管理员 admin</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from '@/components/SvgIcon.vue'

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const wechatLoading = ref(false)
const loginMode = ref('account')
const rememberPwd = ref(true)
const agreed = ref(true)
const form = ref({ username: '', password: '', phone: '', code: '' })

const goHome = () => router.replace('/pages/public/home/index')
const goRegister = () => router.push('/pages/public/register/index')

const getCode = () => uni.showToast({ title: '验证码登录暂未开放', icon: 'none' })
const forgotPwd = () => uni.showToast({ title: '请联系管理员重置密码', icon: 'none' })

const handleLogin = async () => {
  if (loginMode.value === 'sms') {
    return uni.showToast({ title: '验证码登录暂未开放', icon: 'none' })
  }
  if (!form.value.username.trim()) {
    return uni.showToast({ title: '请输入用户名', icon: 'none' })
  }
  if (!form.value.password) {
    return uni.showToast({ title: '请输入密码', icon: 'none' })
  }

  loading.value = true
  try {
    await authStore.login(form.value.username.trim(), form.value.password)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => uni.reLaunch({ url: '/pages/public/home/index' }), 500)
  } catch (err) {
    console.error('登录失败:', err)
  } finally {
    loading.value = false
  }
}

const handleWechatLogin = async () => {
  wechatLoading.value = true
  try {
    await authStore.wechatLogin()
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => uni.reLaunch({ url: '/pages/public/home/index' }), 500)
  } catch (err) {
    console.error('微信登录失败:', err)
  } finally {
    wechatLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
}

/* ═══ 顶部 ═══ */
.login-top {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 60%, #5B8DEF 100%);
  padding: calc(env(safe-area-inset-top) + 120rpx) 48rpx 160rpx;
  position: relative;
  overflow: hidden;
}
.login-top::before {
  content: '';
  position: absolute;
  top: -160rpx;
  right: -120rpx;
  width: 480rpx;
  height: 480rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
}
.login-top::after {
  content: '';
  position: absolute;
  bottom: -200rpx;
  left: -80rpx;
  width: 360rpx;
  height: 360rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}
.login-close {
  position: absolute;
  top: calc(env(safe-area-inset-top) + 40rpx);
  right: 40rpx;
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}
.login-logo {
  width: 128rpx;
  height: 128rpx;
  border-radius: 36rpx;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
  position: relative;
  z-index: 1;
  border: 1rpx solid rgba(255, 255, 255, 0.3);
}
.login-title {
  color: #fff;
  font-size: 52rpx;
  font-weight: 700;
  display: block;
  margin-bottom: 12rpx;
  position: relative;
  z-index: 1;
}
.login-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 28rpx;
  position: relative;
  z-index: 1;
}

/* ═══ 表单卡片 ═══ */
.login-form-wrap {
  flex: 1;
  margin: -100rpx 40rpx 0;
  background: #fff;
  border-radius: 40rpx;
  padding: 56rpx 40rpx 48rpx;
  box-shadow: 0 -8rpx 60rpx rgba(22, 93, 255, 0.1);
  position: relative;
  z-index: 2;
}

.login-tabs {
  display: flex;
  gap: 48rpx;
  margin-bottom: 48rpx;
  border-bottom: 1rpx solid #F2F3F5;
}
.login-tab {
  padding: 20rpx 0;
  font-size: 32rpx;
  font-weight: 500;
  color: #86909C;
  position: relative;
}
.login-tab.active {
  color: #165DFF;
  font-weight: 700;
}
.login-tab.active::after {
  content: '';
  position: absolute;
  bottom: -1rpx;
  left: 0;
  right: 0;
  height: 6rpx;
  background: linear-gradient(90deg, #165DFF, #4080FF);
  border-radius: 4rpx;
}

.form-group { margin-bottom: 32rpx; }
.form-label {
  font-size: 26rpx;
  color: #4E5969;
  font-weight: 500;
  margin-bottom: 16rpx;
  display: block;
}
.form-input-wrap {
  display: flex;
  align-items: center;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 24rpx;
  padding: 0 28rpx;
  height: 100rpx;
  transition: all 0.2s;
}
.form-input-wrap:focus-within {
  border-color: #165DFF;
  background: #fff;
  box-shadow: 0 0 0 8rpx rgba(22, 93, 255, 0.08);
}
.form-input-icon {
  display: flex;
  align-items: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}
.form-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 30rpx;
  color: #1D2129;
}
.form-code-btn {
  padding: 12rpx 24rpx;
  background: #E8F3FF;
  color: #165DFF;
  font-size: 24rpx;
  font-weight: 500;
  border-radius: 16rpx;
  border: none;
  flex-shrink: 0;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 48rpx;
}
.form-remember {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 26rpx;
  color: #4E5969;
}
.form-checkbox {
  width: 32rpx;
  height: 32rpx;
  border-radius: 8rpx;
  border: 1.5px solid #C9CDD4;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.form-checkbox.checked {
  background: #165DFF;
  border-color: #165DFF;
}
.form-forgot {
  font-size: 26rpx;
  color: #165DFF;
}

.login-submit {
  width: 100%;
  height: 100rpx;
  border-radius: 50rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);
  margin-bottom: 40rpx;
  text-align: center;
  line-height: 100rpx;
}
.login-submit[disabled] { background: #94A3B8; }

.login-divider {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 40rpx;
}
.login-divider-line { flex: 1; height: 1rpx; background: #E5E6EB; }
.login-divider-text { font-size: 24rpx; color: #C9CDD4; }

.login-wechat-btn {
  width: 100%;
  height: 100rpx;
  border-radius: 50rpx;
  background: #07C160;
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  box-shadow: 0 12rpx 32rpx rgba(7, 193, 96, 0.25);
  margin-bottom: 48rpx;
  line-height: 100rpx;
}
.login-wechat-btn[disabled] { background: #94A3B8; }
.wechat-svg { width: 44rpx; height: 44rpx; fill: #fff; }

.login-agreement {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  font-size: 24rpx;
  color: #86909C;
  line-height: 1.6;
}
.login-agreement .form-checkbox { margin-top: 4rpx; }
.agreement-link { color: #165DFF; }

.login-bottom {
  text-align: center;
  padding: 32rpx 40rpx;
  font-size: 26rpx;
  color: #86909C;
}
.login-bottom-link {
  color: #165DFF;
  font-weight: 500;
  margin-left: 8rpx;
}

/* 测试账号提示（演示辅助） */
.test-tips {
  margin: 0 40rpx 40rpx;
  padding: 24rpx 32rpx;
  background: #F7F8FA;
  border-radius: 16rpx;
}
.tips-title {
  font-size: 24rpx;
  color: #4E5969;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}
.tips-text {
  font-size: 22rpx;
  color: #86909C;
  display: block;
  line-height: 1.6;
}
</style>
