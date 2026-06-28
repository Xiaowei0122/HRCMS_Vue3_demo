import request from '@/utils/request'

/** GET /news?page=1&size=10&title=&type= */
export function getNewsList(params) {
  return request.get('/news', { params })
}

/** GET /news/:id */
export function getNewsDetail(id) {
  return request.get(`/news/${id}`)
}

/** POST /news */
export function createNews(data) {
  return request.post('/news', data)
}

/** PUT /news/:id */
export function updateNews(id, data) {
  return request.put(`/news/${id}`, data)
}

/** DELETE /news/:id */
export function deleteNews(id) {
  return request.delete(`/news/${id}`)
}

/** PATCH /news/:id/pin — 置顶/取消置顶 */
export function togglePinNews(id) {
  return request.patch(`/news/${id}/pin`)
}

/** PATCH /news/:id/publish — 发布/撤回 */
export function publishNews(id) {
  return request.patch(`/news/${id}/publish`)
}
