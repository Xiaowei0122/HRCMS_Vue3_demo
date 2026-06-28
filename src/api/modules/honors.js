import request from '@/utils/request'

/** GET /honors?type=all|cert|photo&page=1&size=12 */
export function getHonorList(params) {
  return request.get('/honors', { params })
}

/** POST /honors */
export function createHonor(data) {
  return request.post('/honors', data)
}

/** PUT /honors/:id */
export function updateHonor(id, data) {
  return request.put(`/honors/${id}`, data)
}

/** DELETE /honors/:id */
export function deleteHonor(id) {
  return request.delete(`/honors/${id}`)
}
