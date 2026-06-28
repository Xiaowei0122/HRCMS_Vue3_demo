import request from '@/utils/request'

/** GET /roles */
export function getRoleList() {
  return request.get('/roles')
}

/** POST /roles */
export function createRole(data) {
  return request.post('/roles', data)
}

/** PUT /roles/:id */
export function updateRole(id, data) {
  return request.put(`/roles/${id}`, data)
}

/** DELETE /roles/:id */
export function deleteRole(id) {
  return request.delete(`/roles/${id}`)
}

/** GET /roles/:id/permissions */
export function getRolePermissions(id) {
  return request.get(`/roles/${id}/permissions`)
}

/** PUT /roles/:id/permissions  { permissionIds: [1,2,3] } */
export function saveRolePermissions(id, permissionIds) {
  return request.put(`/roles/${id}/permissions`, { permissionIds })
}

/** GET /permissions/tree => 完整菜单树 */
export function getPermissionTree() {
  return request.get('/permissions/tree')
}
