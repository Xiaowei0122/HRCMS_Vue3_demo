import request from '@/utils/request'

/** POST /auth/login  { username, password } => { token, userInfo } */
export function login(data) {
  return request.post('/auth/login', data)
}

/** POST /auth/logout */
export function logout() {
  return request.post('/auth/logout')
}

/** GET /auth/userinfo => 当前登录用户信息 */
export function getUserInfo() {
  return request.get('/auth/userinfo')
}

/** PUT /auth/password  { oldPassword, newPassword } */
export function changePassword(data) {
  return request.put('/auth/password', data)
}
