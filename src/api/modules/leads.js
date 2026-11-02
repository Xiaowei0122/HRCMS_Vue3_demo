import request from '@/utils/request'

/** GET /leads?status=&page=1&size=10&startDate=&endDate= */
export function getLeadList(params) {
  return request.get('/leads', { params })
}

/** GET /leads/:id */
export function getLeadDetail(id) {
  return request.get(`/leads/${id}`)
}

/** PUT /leads/:id/progress  { status, remark } */
export function updateLeadProgress(id, data) {
  return request.put(`/leads/${id}/progress`, data)
}

/** POST /leads/:id/convert 一键转工单  { deviceType?, workOrderType?, priority?, description? } */
export function convertLead(id, data) {
  return request.post(`/leads/${id}/convert`, data)
}

/** GET /leads/export (blob) */
export function exportLeads(params) {
  return request.get('/leads/export', { params, responseType: 'blob' })
}
