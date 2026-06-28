import request from '@/utils/request'

// ==================== 品牌 ====================

/** GET /brands */
export function getBrandList() {
  return request.get('/brands')
}

/** POST /brands */
export function createBrand(data) {
  return request.post('/brands', data)
}

/** PUT /brands/:id */
export function updateBrand(id, data) {
  return request.put(`/brands/${id}`, data)
}

/** DELETE /brands/:id */
export function deleteBrand(id) {
  return request.delete(`/brands/${id}`)
}

// ==================== 案例 ====================

/** GET /cases?search=&page=1&size=9 */
export function getCaseList(params) {
  return request.get('/cases', { params })
}

/** POST /cases */
export function createCase(data) {
  return request.post('/cases', data)
}

/** PUT /cases/:id */
export function updateCase(id, data) {
  return request.put(`/cases/${id}`, data)
}

/** DELETE /cases/:id */
export function deleteCase(id) {
  return request.delete(`/cases/${id}`)
}
