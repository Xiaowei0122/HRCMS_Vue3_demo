import request from '@/utils/request'

/** GET /contact/engineers */
export function getContactEngineers() {
  return request.get('/contact/engineers')
}

/** POST /contact/engineers */
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
