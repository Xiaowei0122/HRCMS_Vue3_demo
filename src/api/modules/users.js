import request from '@/utils/request'

/** GET /users?page=1&size=10&name=xxx */
export function getUserList(params) {
  return request.get('/users', { params })
}

/** POST /users  { username, realName, role, phone, password } */
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

/** PATCH /users/:id/status  { status: true|false } */
export function toggleUserStatus(id, status) {
  return request.patch(`/users/${id}/status`, { status })
}

/** PUT /users/:id/password/reset */
export function resetUserPassword(id) {
  return request.put(`/users/${id}/password/reset`)
}
