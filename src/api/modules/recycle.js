import request from '@/utils/request'

/** GET /recycle?page=&size=&collection= */
export function getRecycleList(params) {
  return request.get('/recycle', { params })
}

/** POST /recycle/:id/restore */
export function restoreItem(id) {
  return request.post(`/recycle/${id}/restore`)
}

/** DELETE /recycle/:id */
export function purgeItem(id) {
  return request.delete(`/recycle/${id}`)
}
