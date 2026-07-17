/**
 * HTTP 请求封装 — 对标 CMS 前端的 src/utils/request.js
 * 基于 uni.request，自动附加 JWT Token，统一错误处理
 */

const BASE_URL = 'http://localhost:8080/api'

// 请求拦截 — 附加 Token
const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json'
  }
  const token = uni.getStorageSync('token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

/**
 * 统一请求方法
 * @param {string} url     - 接口路径（不含 base）
 * @param {object} options - uni.request 选项
 * @returns {Promise}
 */
const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: { ...getHeaders(), ...(options.header || {}) },
      timeout: 15000,
      success: (res) => {
        const { statusCode, data } = res

        // 401 → token 过期，跳转登录
        if (statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.reLaunch({ url: '/pages/public/login/index' })
          reject(new Error('登录已过期，请重新登录'))
          return
        }

        // 业务错误
        if (statusCode >= 400) {
          const msg = (data && data.message) || '请求失败'
          uni.showToast({ title: msg, icon: 'none', duration: 2000 })
          reject(new Error(msg))
          return
        }

        // 后端统一格式 { code: 200, data: ..., message: "ok" }
        // 自动解包，store 层直接拿业务数据
        if (data && data.code === 200) {
          resolve(data.data)
        } else {
          resolve(data)
        }
      },
      fail: (err) => {
        const msg = err.errMsg || '网络异常，请检查网络连接'
        uni.showToast({ title: msg, icon: 'none', duration: 2000 })
        reject(err)
      }
    })
  })
}

// 便捷方法
const get = (url, params = {}) => {
  const query = Object.keys(params)
    .filter(k => params[k] !== undefined && params[k] !== null && params[k] !== '')
    .map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`)
    .join('&')
  return request(query ? `${url}?${query}` : url, { method: 'GET' })
}

const post = (url, data = {}) => request(url, { method: 'POST', data })
const put = (url, data = {}) => request(url, { method: 'PUT', data })
const patch = (url, data = {}) => request(url, { method: 'PATCH', data })
const del = (url, data = {}) => request(url, { method: 'DELETE', data })

/**
 * 上传文件
 */
const uploadFile = (filePath) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.uploadFile({
      url: BASE_URL + '/upload/file',
      filePath,
      name: 'file',
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          if (res.statusCode === 200) {
            resolve(data)
          } else {
            uni.showToast({ title: data.message || '上传失败', icon: 'none' })
            reject(new Error(data.message))
          }
        } catch {
          reject(new Error('上传响应解析失败'))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

export { get, post, put, patch, del, uploadFile }
export default { get, post, put, patch, del, uploadFile }
