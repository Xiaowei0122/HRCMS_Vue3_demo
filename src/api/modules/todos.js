import request from '@/utils/request'

/** GET /todos => { groups: [{ key, title, subtitle, link, count, items }], roleCode } */
export function getTodos() {
  return request.get('/todos')
}
