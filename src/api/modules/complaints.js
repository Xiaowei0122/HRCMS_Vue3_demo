import request from '@/utils/request'

/** GET /complaints?status=&search=&page=1&size=10 */
export function getComplaintList(params) {
  return request.get('/complaints', { params })
}

/** GET /complaints/stats */
export function getComplaintStats() {
  return request.get('/complaints/stats')
}

/** PUT /complaints/:id/process  { type, note } */
export function processComplaint(id, data) {
  return request.put(`/complaints/${id}/process`, data)
}

/** PATCH /complaints/:id/close */
export function closeComplaint(id) {
  return request.patch(`/complaints/${id}/close`)
}
