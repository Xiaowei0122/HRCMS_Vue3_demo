import request from '@/utils/request'

/** GET /contact/engineers */
export function getContactEngineers() {
  return request.get('/contact/engineers')
}

/** GET /contact/candidates — 所有工程师用户（用于联动筛选） */
export function getContactEngineerCandidates() {
  return request.get('/contact/candidates')
}

/** POST /contact/engineers  { id, avatar, skills, desc, team } */
export function createContactEngineer(data) {
  return request.post('/contact/engineers', data)
}

/** PUT /contact/engineers/:id */
export function updateContactEngineer(id, data) {
  return request.put(`/contact/engineers/${id}`, data)
}

/** DELETE /contact/engineers/:id */
export function deleteContactEngineer(id) {
  return request.delete(`/contact/engineers/${id}`)
}
