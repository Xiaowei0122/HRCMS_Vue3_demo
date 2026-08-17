import request from '@/utils/request'

/** GET /config => 完整全局配置（公开平铺结构，供官网/小程序） */
export function getGlobalConfig() {
  return request.get('/config')
}

/** GET /config/full => 管理端结构化配置 */
export function getConfigFull() {
  return request.get('/config/full')
}

/** PUT /config/basic */
export function saveBasicConfig(data) {
  return request.put('/config/basic', data)
}

// ==================== 服务板块 / 关于（官网内容） ====================

/** GET /config/services */
export function getServices() {
  return request.get('/config/services')
}

/** PUT /config/services  { services: [...] } */
export function saveServices(data) {
  return request.put('/config/services', data)
}

/** GET /config/about */
export function getAbout() {
  return request.get('/config/about')
}

/** PUT /config/about  { about: {...} } */
export function saveAbout(data) {
  return request.put('/config/about', data)
}

// ==================== Banner ====================

/** GET /config/banners */
export function getBanners() {
  return request.get('/config/banners')
}

/** POST /config/banners */
export function addBanner(data) {
  return request.post('/config/banners', data)
}

/** PUT /config/banners/:id */
export function updateBanner(id, data) {
  return request.put(`/config/banners/${id}`, data)
}

/** DELETE /config/banners/:id */
export function deleteBanner(id) {
  return request.delete(`/config/banners/${id}`)
}

// ==================== 联系 / 地图 ====================

/** PUT /config/contact */
export function saveContactConfig(data) {
  return request.put('/config/contact', data)
}

/** PUT /config/map */
export function saveMapConfig(data) {
  return request.put('/config/map', data)
}
