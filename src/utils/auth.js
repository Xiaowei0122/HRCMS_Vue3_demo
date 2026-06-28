/**
 * Token 管理工具
 * 所有 token / 用户信息的读写集中在这里，方便后续切换存储方案
 */

const TOKEN_KEY = 'admin_token'
const USER_KEY = 'admin_user'

// ---------- Token ----------

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

// ---------- 用户信息 ----------

export function getUserInfo() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function setUserInfo(info) {
  localStorage.setItem(USER_KEY, JSON.stringify(info))
}

export function removeUserInfo() {
  localStorage.removeItem(USER_KEY)
}

// ---------- 一次性清除 ----------

export function clearAuth() {
  removeToken()
  removeUserInfo()
}
