/**
 * 认证状态管理 — Pinia
 * 管理登录态、用户信息、角色判断
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { post, get, put } from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  // ── state ──
  const token = ref('')
  const userInfo = ref(null)
  const isLoggedIn = ref(false)

  // ── getters ──
  const userType = computed(() => userInfo.value?.userType || 'normal')
  const isNormalUser = computed(() => userType.value === 'normal')
  const isSpecialUser = computed(() => userType.value === 'special')
  const isEngineer = computed(() => userType.value === 'engineer')
  const isAdmin = computed(() => userType.value === 'admin')
  const userName = computed(() => userInfo.value?.realName || userInfo.value?.username || '用户')

  // ── 初始化：从本地存储恢复登录态 ──
  const checkLogin = () => {
    const savedToken = uni.getStorageSync('token')
    const savedUser = uni.getStorageSync('userInfo')
    if (savedToken && savedUser) {
      token.value = savedToken
      userInfo.value = savedUser
      isLoggedIn.value = true
    }
  }

  // ── 登录 ──
  const login = async (username, password) => {
    const u = await post('/auth/login', { username, password })
    // request.js 已自动解包 { code, data, message } → data

    token.value = u.token
    userInfo.value = u.userInfo
    isLoggedIn.value = true

    // 持久化存储
    uni.setStorageSync('token', u.token)
    uni.setStorageSync('userInfo', u.userInfo)

    return u.userInfo
  }

  // ── 注册 ──
  const register = async (formData) => {
    return await post('/auth/register', formData)
  }

  // ── 退出登录 ──
  const logout = async () => {
    try {
      await post('/auth/logout')
    } catch {
      // 忽略接口错误
    }
    // 清除本地状态
    token.value = ''
    userInfo.value = null
    isLoggedIn.value = false
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
    uni.reLaunch({ url: '/pages/public/login/index' })
  }

  // ── 修改密码 ──
  const changePassword = async (oldPwd, newPwd) => {
    return await put('/auth/password', {
      oldPassword: oldPwd,
      newPassword: newPwd
    })
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    userType,
    isNormalUser,
    isSpecialUser,
    isEngineer,
    isAdmin,
    userName,
    checkLogin,
    login,
    register,
    logout,
    changePassword
  }
})
