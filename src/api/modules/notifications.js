import request from '@/utils/request'

/** GET /notifications?limit=20 我的通知列表 */
export function getNotifications(limit = 20) {
  return request.get('/notifications', { params: { limit } })
}

/** GET /notifications/unread-count 未读数量 */
export function getUnreadCount() {
  return request.get('/notifications/unread-count')
}

/** POST /notifications/read  { id } 单条 或 { all: true } 全部 */
export function markNotificationRead(data) {
  return request.post('/notifications/read', data)
}
