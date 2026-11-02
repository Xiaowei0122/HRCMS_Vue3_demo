import request from '@/utils/request'

/** GET /system/settings */
export function getSystemSettings() {
  return request.get('/system/settings')
}

/** PUT /system/settings */
export function updateSystemSettings(data) {
  return request.put('/system/settings', data)
}
