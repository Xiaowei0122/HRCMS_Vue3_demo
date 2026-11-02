import axios from 'axios'
import { getToken, clearAuth } from './auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000
})

// 避免并发请求同时 401 时重复弹窗 / 重复跳转登录
let isRedirectingToLogin = false

// ===================== 请求拦截器 =====================
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ===================== 响应拦截器 =====================
service.interceptors.response.use(
  (response) => {
    // 二进制流 / 文件下载：原样返回整个 response
    if (response.config.responseType === 'blob') {
      return response
    }

    const res = response.data

    // 后端未使用 { code, data, message } 包裹，直接透传
    if (res.code === undefined) {
      return res
    }

    // 后端包裹格式：{ code: 200 | 0, data: ..., message: ... }
    if (res.code === 200 || res.code === 0) {
      return res.data
    }

    // 数据库连接失败：后端可达但数据库不可用
    if (res.code === 503) {
      ElMessage.error('无法连接数据库')
      return Promise.reject(new Error(res.message || '数据库连接失败'))
    }

    // 业务错误
    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || 'Error'))
  },
  (error) => {
    const { response } = error

    if (response) {
      // 数据库连接失败：后端可达但数据库不可用
      if (response.status === 503 || response.data?.code === 503) {
        ElMessage.error('无法连接数据库')
        return Promise.reject(error)
      }

      switch (response.status) {
        case 401:
          if (!isRedirectingToLogin) {
            isRedirectingToLogin = true
            ElMessage.error('登录已过期，请重新登录')
            clearAuth()
            router.push('/login').finally(() => { isRedirectingToLogin = false })
          }
          break
        case 403:
          ElMessage.error('没有操作权限')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(
            response.data?.message || `请求失败(${response.status})`
          )
      }
    } else if (error.message?.includes('timeout')) {
      ElMessage.error('请求超时，请检查网络连接')
    } else {
      ElMessage.error('请检查后端服务是否已启动')
    }

    return Promise.reject(error)
  }
)

export default service
