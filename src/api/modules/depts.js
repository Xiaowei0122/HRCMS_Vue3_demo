import request from '@/utils/request'

/** GET /departments => 部门列表 */
export function getDeptList() {
  return request.get('/departments')
}

/** GET /departments/options => 业务下拉 [{ label, value }] */
export function getDeptOptions() {
  return request.get('/departments/options')
}

/** POST /departments */
export function createDept(data) {
  return request.post('/departments', data)
}

/** PUT /departments/:id */
export function updateDept(id, data) {
  return request.put(`/departments/${id}`, data)
}

/** DELETE /departments/:id */
export function deleteDept(id) {
  return request.delete(`/departments/${id}`)
}
