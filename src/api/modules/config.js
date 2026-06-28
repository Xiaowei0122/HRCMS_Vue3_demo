import request from '@/utils/request'

/** GET /config => 完整全局配置 */
export function getGlobalConfig() {
  return request.get('/config')
}

/** PUT /config/basic */
export function saveBasicConfig(data) {
  return request.put('/config/basic', data)
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
