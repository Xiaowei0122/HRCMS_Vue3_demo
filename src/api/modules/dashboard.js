import request from '@/utils/request'

/** GET /dashboard/stats => { visitors, newRepairs, pendingLeads, satisfaction } */
export function getDashboardStats() {
  return request.get('/dashboard/stats')
}

/** GET /dashboard/trends?type=repair|leads => 图表趋势数据 */
export function getDashboardTrends(type) {
  return request.get('/dashboard/trends', { params: { type } })
}

/** GET /dashboard/todos => [{ id, content, urgency, link }] */
export function getDashboardTodos() {
  return request.get('/dashboard/todos')
}
