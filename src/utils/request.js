import axios from 'axios'
import { getToken, clearAuth } from './auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000
})

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

    // 业务错误
    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || 'Error'))
  },
  (error) => {
    const { response } = error

    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          clearAuth()
          router.push('/login')
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
      ElMessage.error('网络异常，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default service
