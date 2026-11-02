import request from '@/utils/request'

/** GET /knowledge?page=1&size=10&title=&type= */
export function getKnowledgeList(params) {
  return request.get('/knowledge', { params })
}

/** GET /knowledge/:id */
export function getKnowledgeDetail(id) {
  return request.get(`/knowledge/${id}`)
}

/** POST /knowledge */
export function createKnowledge(data) {
  return request.post('/knowledge', data)
}

/** PUT /knowledge/:id */
export function updateKnowledge(id, data) {
  return request.put(`/knowledge/${id}`, data)
}

/** DELETE /knowledge/:id */
export function deleteKnowledge(id) {
  return request.delete(`/knowledge/${id}`)
}

/** PATCH /knowledge/:id/pin — 置顶/取消置顶 */
export function togglePinKnowledge(id) {
  return request.patch(`/knowledge/${id}/pin`)
}

/** PATCH /knowledge/:id/publish — 发布/撤回 */
export function publishKnowledge(id) {
  return request.patch(`/knowledge/${id}/publish`)
}
