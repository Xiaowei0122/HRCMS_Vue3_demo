import request from '@/utils/request'

/** GET /dict/types => [{ type, count }] */
export function getDictTypes() {
  return request.get('/dict/types')
}

/** GET /dict/items?type=xxx => 分组下字典项 */
export function getDictItems(type) {
  return request.get('/dict/items', { params: { type } })
}

/** POST /dict/items  { type, label, value, sort, enabled } */
export function createDictItem(data) {
  return request.post('/dict/items', data)
}

/** PUT /dict/items/:id */
export function updateDictItem(id, data) {
  return request.put(`/dict/items/${id}`, data)
}

/** DELETE /dict/items/:id */
export function deleteDictItem(id) {
  return request.delete(`/dict/items/${id}`)
}

/** GET /dict/options?type=xxx => 启用项 [{ label, value }]（业务下拉读取） */
export function getDictOptions(type) {
  return request.get('/dict/options', { params: { type } })
}
