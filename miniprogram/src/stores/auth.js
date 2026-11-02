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
  const userType = computed(() => userInfo.value?.roleCode || userInfo.value?.userType || 'normal')
  // 权限码列表（与后端 build_user_info.permissions 对齐；super_admin 通配）
  const permissions = computed(() => {
    const info = userInfo.value
    if (!info) return []
    if (info.roleCode === 'super_admin' || info.userType === 'super_admin') return ['*']
    return info.permissions || []
  })
  // 权限判断（镜像后端 require_permission：任一命中即通过）
  const hasPerm = (...codes) => {
    const perms = permissions.value
    if (perms.includes('*')) return true
    return codes.some((c) => perms.includes(c))
  }

  const isNormalUser = computed(() => userType.value === 'normal')
  const isBusiness = computed(() => userType.value === 'business')
  const isEngineer = computed(() => userType.value === 'engineer')
  const isFinance = computed(() => userType.value === 'finance')
  const isOperation = computed(() => userType.value === 'operation')
  const isAdmin = computed(() => userType.value === 'super_admin' || userType.value === 'admin')
  const isSuperAdmin = computed(() => userType.value === 'super_admin')
  // 内部员工 = 除外部人员/工程师外的所有角色
  const isInternalUser = computed(() => !['normal', 'engineer'].includes(userType.value))
  // 可确认归档/发起返修的角色（客户 + 业务 + 管理员，工程师/财务/运营除外）
  const canConfirmRepair = computed(() => ['normal', 'business', 'admin', 'super_admin'].includes(userType.value))
  const userName = computed(() => userInfo.value?.realName || userInfo.value?.username || '用户')

  // 角色中文标签
  const roleLabel = computed(() => {
    const map = {
      super_admin: '超级管理员',
      admin: '管理员',
      business: '业务',
      finance: '财务',
      operation: '运营',
      engineer: '工程师',
      normal: '外部人员'
    }
    return map[userType.value] || '外部人员'
  })

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

  // ── 微信一键登录（uni.login → code → 后端换 openid/unionid 自动注册/登录）──
  const wechatLogin = async (profile = {}) => {
    const code = await new Promise((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: (res) => resolve(res.code || ''),
        fail: (err) => reject(err)
      })
    })
    if (!code) {
      throw new Error('获取微信登录凭证失败')
    }
    const u = await post('/auth/wechat-login', {
      code,
      nickname: profile.nickname || '',
      avatar: profile.avatar || ''
    })

    token.value = u.token
    userInfo.value = u.userInfo
    isLoggedIn.value = true

    uni.setStorageSync('token', u.token)
    uni.setStorageSync('userInfo', u.userInfo)

    return u.userInfo
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
    permissions,
    hasPerm,
    isNormalUser,
    isBusiness,
    isEngineer,
    isFinance,
    isOperation,
    isAdmin,
    isSuperAdmin,
    isInternalUser,
    canConfirmRepair,
    userName,
    roleLabel,
    checkLogin,
    login,
    register,
    wechatLogin,
    logout,
    changePassword
  }
})
