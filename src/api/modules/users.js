import request from '@/utils/request'

/** GET /users?page=1&size=10&name=xxx */
export function getUserList(params) {
  return request.get('/users', { params })
}

/** POST /users  { username, realName, roleCode, phone, password } */
export function createUser(data) {
  return request.post('/users', data)
}

/** PUT /users/:id */
export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

/** DELETE /users/:id */
export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

/** PATCH /users/:id/status  （后端取反，返回新状态 active|disabled） */
export function toggleUserStatus(id) {
  return request.patch(`/users/${id}/status`)
}

/** PATCH /users/:id/approve  （pending → active） */
export function approveUser(id) {
  return request.patch(`/users/${id}/approve`)
}

/** PATCH /users/:id/reject  （pending → disabled） */
export function rejectUser(id) {
  return request.patch(`/users/${id}/reject`)
}

/** PUT /users/:id/password/reset */
export function resetUserPassword(id) {
  return request.put(`/users/${id}/password/reset`)
}
