import request from '@/utils/request'

// ==================== 报修申请 ====================

/** POST /repairs  提交报修单 */
export function createRepair(data) {
  return request.post('/repairs', data)
}

// ==================== 我的报修 ====================

/** GET /repairs/my?page=1&size=10 */
export function getMyRepairs(params) {
  return request.get('/repairs/my', { params })
}

// ==================== 全部工单 ====================

/** GET /repairs?status=&search=&page=1&size=10 */
export function getRepairList(params) {
  return request.get('/repairs', { params })
}

/** GET /repairs/:id */
export function getRepairDetail(id) {
  return request.get(`/repairs/${id}`)
}

/** PATCH /repairs/:id/assign  { engineerId, engineerName, timeSlot } */
export function assignRepair(id, data) {
  return request.patch(`/repairs/${id}/assign`, data)
}

/** POST /repairs/:id/progress  { node, time, status } */
export function addRepairProgress(id, data) {
  return request.post(`/repairs/${id}/progress`, data)
}

/** PATCH /repairs/:id/complete */
export function completeRepair(id) {
  return request.patch(`/repairs/${id}/complete`)
}

/** GET /repairs/stats => 统计面板数据 */
export function getRepairStats() {
  return request.get('/repairs/stats')
}

// ==================== 工程师排期 ====================

/** GET /engineers */
export function getEngineerList() {
  return request.get('/engineers')
}

/** GET /repairs/schedule?engineerId=&startDate=&endDate= */
export function getEngineerSchedule(params) {
  return request.get('/repairs/schedule', { params })
}

/** POST /repairs/schedule  { engineerId, date, timeSlot, type, company } */
export function createScheduleEntry(data) {
  return request.post('/repairs/schedule', data)
}

/** DELETE /repairs/schedule/:id — 释放锁定 */
export function deleteScheduleEntry(id) {
  return request.delete(`/repairs/schedule/${id}`)
}
