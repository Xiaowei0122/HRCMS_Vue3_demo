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

/** GET /dashboard/cost => 成本概览（仅已结工单费用） */
export function getDashboardCost() {
  return request.get('/dashboard/cost')
}

/** GET /dashboard/schedule-today => 今日排期 */
export function getScheduleToday() {
  return request.get('/dashboard/schedule-today')
}
