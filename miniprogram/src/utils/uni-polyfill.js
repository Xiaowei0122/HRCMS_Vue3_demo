/**
 * uni-app API → 浏览器 Polyfill
 *
 * 模拟微信小程序 uni.* 接口，让页面组件无需修改即可在纯 Vue 3 SPA 中运行。
 * 在 main.js 中挂载到 window.uni，全局可用。
 */

import router from '@/router'

// ==================== Storage ====================
function getStorageSync(key) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : ''
  } catch {
    return ''
  }
}

function setStorageSync(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch { /* quota exceeded */ }
}

function removeStorageSync(key) {
  try {
    localStorage.removeItem(key)
  } catch { /* ignore */ }
}

// ==================== Navigation ====================
function navigateTo({ url }) {
  router.push(url).catch(() => {})
}

function reLaunch({ url }) {
  // 用 replace 清空历史栈，不整页刷新（保留 Pinia store 状态）
  router.replace(url).catch(() => {})
}

function switchTab({ url }) {
  router.push(url).catch(() => {})
}

function navigateBack({ delta = 1 } = {}) {
  // vue-router 的 go 直接对应 history.go
  router.go(-delta)
}

// ==================== Toast ====================
let toastTimer = null
function showToast({ title, icon = 'none', duration = 2000 }) {
  // 移除旧 toast
  const old = document.querySelector('.uni-toast-polyfill')
  if (old) old.remove()
  if (toastTimer) clearTimeout(toastTimer)

  const el = document.createElement('div')
  el.className = 'uni-toast-polyfill'
  el.innerHTML = `<span>${icon === 'success' ? '✅' : icon === 'error' ? '❌' : ''} ${title}</span>`
  document.body.appendChild(el)

  toastTimer = setTimeout(() => {
    el.classList.add('uni-toast--fadeout')
    setTimeout(() => el.remove(), 300)
  }, duration)
}

// ==================== Modal ====================
function showModal({ title = '提示', content = '', showCancel = true, success } = {}) {
  return new Promise((resolve) => {
    let result
    if (showCancel) {
      const ok = window.confirm(`${title}\n\n${content}`)
      result = { confirm: ok, cancel: !ok }
    } else {
      window.alert(`${title}\n\n${content}`)
      result = { confirm: true, cancel: false }
    }
    if (typeof success === 'function') {
      success(result)
    }
    resolve(result)
  })
}

// ==================== Image ====================
function previewImage({ urls, current = '' }) {
  const idx = urls.indexOf(current)
  const url = idx >= 0 ? current : urls[0]
  if (url) window.open(url, '_blank')
}

function chooseImage({ count = 1, sourceType = ['album', 'camera'] } = {}) {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.multiple = count > 1
    input.style.display = 'none'
    document.body.appendChild(input)

    input.addEventListener('change', () => {
      const files = Array.from(input.files || [])
      document.body.removeChild(input)
      if (files.length > 0) {
        resolve({
          tempFilePaths: files.map(f => URL.createObjectURL(f)),
          tempFiles: files.map(f => ({ path: URL.createObjectURL(f), size: f.size }))
        })
      } else {
        resolve({ tempFilePaths: [], tempFiles: [] })
      }
    })

    input.click()
  })
}

// ==================== Device ====================
function makePhoneCall({ phoneNumber }) {
  window.open(`tel:${phoneNumber}`, '_self')
}

function openLocation({ latitude, longitude, name = '', address = '' }) {
  const label = name || address || 'Location'
  const url = `https://uri.amap.com/marker?position=${longitude},${latitude}&name=${encodeURIComponent(label)}`
  window.open(url, '_blank')
}

// ==================== Network ====================
function request(options) {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data = {}, header = {}, timeout = 15000 } = options

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeout)

    const fetchOptions = {
      method,
      headers: { 'Content-Type': 'application/json', ...header },
      signal: controller.signal
    }

    if (method !== 'GET' && method !== 'HEAD') {
      fetchOptions.body = JSON.stringify(data)
    }

    let fetchUrl = url
    if (method === 'GET' && Object.keys(data).length > 0) {
      const params = new URLSearchParams(data).toString()
      fetchUrl += (url.includes('?') ? '&' : '?') + params
    }

    fetch(fetchUrl, fetchOptions)
      .then(async (res) => {
        clearTimeout(timer)
        const body = await res.json().catch(() => null)
        const result = { statusCode: res.status, data: body }
        // 兼容传统的 success 回调模式（request.js 依赖此回调）
        if (typeof options.success === 'function') {
          options.success(result)
        }
        resolve(result)
      })
      .catch((err) => {
        clearTimeout(timer)
        const error = { errMsg: err.message || '网络异常' }
        // 兼容传统的 fail 回调模式
        if (typeof options.fail === 'function') {
          options.fail(error)
        }
        reject(error)
      })
  })
}

function uploadFile(options) {
  return new Promise((resolve, reject) => {
    const { url, filePath, name = 'file', header = {} } = options

    const onSuccess = (result) => {
      if (typeof options.success === 'function') options.success(result)
      resolve(result)
    }
    const onFail = (error) => {
      if (typeof options.fail === 'function') options.fail(error)
      reject(error)
    }

    // filePath 可能是 blob URL 或 File 对象
    const formData = new FormData()
    if (typeof filePath === 'string') {
      // 从 blob URL 获取 blob
      fetch(filePath)
        .then(r => r.blob())
        .then(blob => {
          formData.append(name, blob, 'image.jpg')
          return doUpload(url, formData, header)
        })
        .then(onSuccess)
        .catch(onFail)
    } else {
      formData.append(name, filePath)
      doUpload(url, formData, header).then(onSuccess).catch(onFail)
    }
  })
}

function doUpload(url, formData, header) {
  return fetch(url, {
    method: 'POST',
    headers: header,
    body: formData
  }).then(async (res) => {
    const data = await res.json().catch(() => null)
    return { statusCode: res.status, data: JSON.stringify(data) }
  })
}

// ==================== TabBar ====================
function hideTabBar() {
  const tabbar = document.querySelector('.custom-tabbar')
  if (tabbar) tabbar.style.display = 'none'
}

function showTabBar() {
  const tabbar = document.querySelector('.custom-tabbar')
  if (tabbar) tabbar.style.display = ''
}

// ==================== 导出 ====================
const uni = {
  getStorageSync,
  setStorageSync,
  removeStorageSync,
  navigateTo,
  reLaunch,
  switchTab,
  navigateBack,
  showToast,
  showModal,
  previewImage,
  chooseImage,
  makePhoneCall,
  openLocation,
  request,
  uploadFile,
  hideTabBar,
  showTabBar,
}

// 挂载到全局
if (typeof window !== 'undefined') {
  window.uni = uni
}

export default uni
