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

/** GET /repairs/confirmers 确认人候选（业务用户） */
export function getConfirmers() {
  return request.get('/repairs/confirmers')
}

/** PATCH /repairs/:id/assign  { engineerId, engineerName, timeSlot }  （仅管理员指派） */
export function assignRepair(id, data) {
  return request.patch(`/repairs/${id}/assign`, data)
}

/** PATCH /repairs/:id/accept  { date, timeSlot, reason? }  （工程师接单，预约工单改派可带原因） */
export function acceptRepair(id, data) {
  return request.patch(`/repairs/${id}/accept`, data)
}

/** POST /repairs/:id/reserve/reject  { reason }  （预约工程师退回「已预约」工单，返回待接单池） */
export function rejectReservedOrder(id, data) {
  return request.post(`/repairs/${id}/reserve/reject`, data)
}

/** POST /repairs/:id/reserve  （业务/内部人员确认预约） */
export function reserveRepair(id) {
  return request.post(`/repairs/${id}/reserve`)
}

/** PATCH /repairs/:id/transfer  { toEngineerId, toEngineerName, reason }  （工程师提交转单申请） */
export function transferRepair(id, data) {
  return request.patch(`/repairs/${id}/transfer`, data)
}

/** POST /repairs/:id/transfer/accept  { date, timeSlot }  （目标工程师接受转单，选择时段） */
export function acceptTransfer(id, data) {
  return request.post(`/repairs/${id}/transfer/accept`, data)
}

/** POST /repairs/:id/transfer/reject  { reason }  （目标工程师退回转单，需填写原因） */
export function rejectTransfer(id, data) {
  return request.post(`/repairs/${id}/transfer/reject`, data)
}

/** POST /repairs/:id/transfer/cancel  （发起人取消转单） */
export function cancelTransfer(id) {
  return request.post(`/repairs/${id}/transfer/cancel`)
}

// ==================== 预约指派 ====================

/** POST /repairs/:id/reserve-assign  { targetEngineerId, targetEngineerName, preferredDate, preferredTimeSlot, note } */
export function reserveAssignRepair(id, data) {
  return request.post(`/repairs/${id}/reserve-assign`, data)
}

/** POST /repairs/:id/reserve-assign/accept  { date, timeSlot }  （工程师确认预约时段） */
export function acceptReserveAssign(id, data) {
  return request.post(`/repairs/${id}/reserve-assign/accept`, data)
}

/** POST /repairs/:id/reserve-assign/reject  { reason }  （工程师退回预约） */
export function rejectReserveAssign(id, data) {
  return request.post(`/repairs/${id}/reserve-assign/reject`, data)
}

/** POST /repairs/:id/reserve-assign/cancel  （发起人取消预约） */
export function cancelReserveAssign(id) {
  return request.post(`/repairs/${id}/reserve-assign/cancel`)
}

/** POST /repairs/:id/progress  { node, time, status } */
export function addRepairProgress(id, data) {
  return request.post(`/repairs/${id}/progress`, data)
}

/** POST /repairs/:id/escalate  { reason, targetEngineerId?, targetEngineerName?, targetDate? }  （加急置顶，需填写原因） */
export function escalateOrder(id, data) {
  return request.post(`/repairs/${id}/escalate`, data)
}

/** POST /repairs/:id/reorder  { direction: top|up|down|extend }  （当日排期上下移/置顶/顺延后续） */
export function reorderRepair(id, data) {
  return request.post(`/repairs/${id}/reorder`, data)
}

/** PATCH /repairs/:id/complete */
export function completeRepair(id) {
  return request.patch(`/repairs/${id}/complete`)
}

/** GET /repairs/stats => 统计面板数据 */
export function getRepairStats() {
  return request.get('/repairs/stats')
}

/** GET /repairs/lookup?company= 单位名匹配历史工单（自动填充） */
export function lookupCompany(company) {
  return request.get('/repairs/lookup', { params: { company } })
}

/** GET /repairs/export 导出工单 Excel（blob） */
export function exportRepairs(params) {
  return request.get('/repairs/export', { params, responseType: 'blob' })
}

/** POST /repairs/:id/confirm 客户/业务确认归档 */
export function confirmRepair(id) {
  return request.post(`/repairs/${id}/confirm`)
}

/** PATCH /repairs/:id/fee 工程师填写费用 { mode, amount, note, paidBy } */
export function setRepairFee(id, data) {
  return request.patch(`/repairs/${id}/fee`, data)
}

/** POST /repairs/:id/rework 返修 { reason, note } */
export function reworkRepair(id, data) {
  return request.post(`/repairs/${id}/rework`, data)
}

/** POST /repairs/:id/cancel 取消工单 { reason, note } （工程师取消处理中的工单） */
export function cancelRepair(id, data) {
  return request.post(`/repairs/${id}/cancel`, data)
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

/** GET /repairs/schedule/availability?engineerId=&date= 已占用时间段 */
export function getScheduleAvailability(params) {
  return request.get('/repairs/schedule/availability', { params })
}

/** GET /repairs/schedule/locks?engineerId=&date= 异常锁定列表 */
export function getScheduleLocks(params) {
  return request.get('/repairs/schedule/locks', { params })
}

/** POST /repairs/schedule/locks { engineerId, engineer, date, timeSlot, type, note } */
export function createScheduleLock(data) {
  return request.post('/repairs/schedule/locks', data)
}

/** DELETE /repairs/schedule/locks/:id 释放异常锁定 */
export function deleteScheduleLock(id) {
  return request.delete(`/repairs/schedule/locks/${id}`)
}

/** GET /public/server-time 服务器时间（北京时间） */
export function getServerTime() {
  return request.get('/public/server-time')
}
