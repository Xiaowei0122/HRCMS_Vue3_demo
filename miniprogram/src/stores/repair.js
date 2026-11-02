/**
 * 报修工单状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { get, post, patch, del } from '@/utils/request'

export const useRepairStore = defineStore('repair', () => {
  // ── state ──
  const myRepairs = ref([])
  const allOrders = ref([])
  const currentDetail = ref(null)
  const scheduleData = ref([])
  const engineers = ref([])
  const stats = ref({ total: 0, pending: 0, processing: 0, done: 0 })

  // ── 创建报修工单 ──
  const createRepair = async (formData) => {
    return await post('/repairs', formData)
  }

  // 列表查询参数归一化：前端 pageSize → 后端 size，过滤空状态
  const _listQuery = (params = {}) => {
    const q = { page: params.page || 1, size: params.pageSize || params.size || 10 }
    if (params.status) q.status = params.status
    if (params.company) q.company = params.company
    if (params.engineerId) q.engineerId = params.engineerId
    if (params.pendingFor) q.pendingFor = params.pendingFor
    if (params.startDate) q.startDate = params.startDate
    if (params.endDate) q.endDate = params.endDate
    return q
  }

  // ── 我的报修列表 ──
  const fetchMyRepairs = async (params = {}) => {
    const res = await get('/repairs/my', _listQuery(params))
    // backend paginate: { records, total, page, size }
    myRepairs.value = res?.records || res || []
    return myRepairs.value
  }

  // ── 所有工单（工程师端） ──
  const fetchAllOrders = async (params = {}) => {
    const res = await get('/repairs', _listQuery(params))
    allOrders.value = res?.records || res || []
    return allOrders.value
  }

  // ── 我的工单（工程师端）—— 后端 /repairs 按 engineerId 过滤 ──
  const fetchMyOrders = async (params = {}) => {
    const res = await get('/repairs', _listQuery(params))
    myRepairs.value = res?.records || res || []
    return myRepairs.value
  }

  // ── 工单详情 ──
  const fetchDetail = async (repairId) => {
    const res = await get(`/repairs/${repairId}`)
    currentDetail.value = res
    return currentDetail.value
  }

  // ── 工程师接单（自助接单 + 预约日期/时段）──
  const acceptOrder = async (repairId, scheduleData) => {
    return await patch(`/repairs/${repairId}/accept`, scheduleData)
  }

  // ── 退回预约工单（预约工程师退回「已预约」单，返回待接单池）──
  const rejectReservedOrder = async (repairId, data) => {
    return await post(`/repairs/${repairId}/reserve/reject`, data)
  }

  // ── 管理员指派工单（业务工单 → 指派到排期）──
  const assignOrder = async (repairId, scheduleData) => {
    return await patch(`/repairs/${repairId}/assign`, scheduleData)
  }

  // ── 业务/内部人员确认预约 ──
  const reserveOrder = async (repairId) => {
    return await post(`/repairs/${repairId}/reserve`)
  }

  // ── 添加工单进度 ──
  const addProgress = async (repairId, progressData) => {
    return await post(`/repairs/${repairId}/progress`, progressData)
  }

  // ── 完成工单 ──
  const completeOrder = async (repairId) => {
    return await patch(`/repairs/${repairId}/complete`)
  }

  // ── 转单申请 ──
  const transferOrder = async (repairId, targetEngineer) => {
    return await patch(`/repairs/${repairId}/transfer`, targetEngineer)
  }

  // ── 转单处理（接受 / 拒绝 / 取消）──
  // 接受转单需预约日期/时段：{date, timeSlot}
  const acceptTransfer = async (repairId, data) => {
    return await post(`/repairs/${repairId}/transfer/accept`, data)
  }
  // 拒绝转单必填原因：{reason}
  const rejectTransfer = async (repairId, data) => {
    return await post(`/repairs/${repairId}/transfer/reject`, data)
  }
  const cancelTransfer = async (repairId) => {
    return await post(`/repairs/${repairId}/transfer/cancel`)
  }

  // ── 取消工单（工程师，处理中 → 已取消，必填原因）──
  const cancelRepair = async (repairId, data) => {
    return await post(`/repairs/${repairId}/cancel`, data)
  }

  // ── 预约指派（业务/管理员发起预约，工程师接受/拒绝，发起方取消）──
  const reserveAssignRepair = async (repairId, data) => {
    return await post(`/repairs/${repairId}/reserve-assign`, data)
  }
  const acceptReserveAssign = async (repairId, data) => {
    return await post(`/repairs/${repairId}/reserve-assign/accept`, data)
  }
  const rejectReserveAssign = async (repairId, data) => {
    return await post(`/repairs/${repairId}/reserve-assign/reject`, data)
  }
  const cancelReserveAssign = async (repairId) => {
    return await post(`/repairs/${repairId}/reserve-assign/cancel`)
  }

  // ── 排期锁定（培训/驻场/请假/其他，状态=已锁定）──
  const fetchScheduleLocks = async (params = {}) => {
    const res = await get('/repairs/schedule/locks', params)
    return res?.records || res || []
  }
  const createScheduleLock = async (data) => {
    return await post('/repairs/schedule/locks', data)
  }
  const deleteScheduleLock = async (lockId) => {
    return await del(`/repairs/schedule/locks/${lockId}`)
  }

  // ── 技术知识库（免登录，published only，独立于门户新闻中心）──
  const fetchKnowledge = async (params = {}) => {
    const res = await get('/public/knowledge', params)
    return res?.records || res || []
  }
  const fetchKnowledgeDetail = async (articleId) => {
    return await get(`/public/knowledge/${articleId}`)
  }

  // ── 确认人列表（代录工单时供工程师/管理员选择）──
  const fetchConfirmers = async () => {
    const res = await get('/repairs/confirmers')
    return res?.records || res || []
  }

  // ── 单位名匹配（二次录入自动填充）──
  const lookupCompany = async (company) => {
    return await get('/repairs/lookup', { company })
  }

  // ── 费用填写（工程师）──
  const setRepairFee = async (repairId, data) => {
    return await patch(`/repairs/${repairId}/fee`, data)
  }

  // ── 客户/业务确认归档 ──
  const confirmRepair = async (repairId) => {
    return await post(`/repairs/${repairId}/confirm`)
  }

  // ── 返修 ──
  const reworkRepair = async (repairId, data) => {
    return await post(`/repairs/${repairId}/rework`, data)
  }

  // ── 加急置顶（插队）—— 工程师本人当天 / 管理员全局，必填 reason ──
  const escalateOrder = async (repairId, data) => {
    return await post(`/repairs/${repairId}/escalate`, data)
  }

  // ── 排期挪动 —— top/up/down（当天内）或 extend（拉长本单顺延后续）──
  const reorderRepair = async (repairId, data) => {
    return await post(`/repairs/${repairId}/reorder`, data)
  }

  // ── 工程师排期 ──
  const fetchSchedule = async (params = {}) => {
    const res = await get('/repairs/schedule', params)
    scheduleData.value = res?.records || res || []
    return scheduleData.value
  }

  // ── 排期时段占用查询（接单时灰显不可选时段）──
  const fetchScheduleAvailability = async (params = {}) => {
    const res = await get('/repairs/schedule/availability', params)
    return res?.occupied || []
  }

  // ── 创建排期 ──
  const createSchedule = async (data) => {
    return await post('/repairs/schedule', data)
  }

  // ── 删除排期 ──
  const deleteSchedule = async (scheduleId) => {
    return await del(`/repairs/schedule/${scheduleId}`)
  }

  // ── 工程师列表 ──
  const fetchEngineers = async () => {
    const res = await get('/repairs/engineers')
    engineers.value = res?.records || res || []
    return engineers.value
  }

  // ── 统计数据（全局，管理员/工程师/财务）──
  const fetchStats = async () => {
    const res = await get('/repairs/stats')
    stats.value = res || {}
    return stats.value
  }

  // ── 我的报修统计（按当前登录人：工程师按 engineerId，其余按联系人/创建人）──
  const fetchMyStats = async () => {
    const res = await get('/repairs/my/stats')
    return res || {}
  }

  return {
    myRepairs,
    allOrders,
    currentDetail,
    scheduleData,
    engineers,
    stats,
    createRepair,
    fetchMyRepairs,
    fetchAllOrders,
    fetchMyOrders,
    fetchDetail,
    acceptOrder,
    rejectReservedOrder,
    assignOrder,
    reserveOrder,
    addProgress,
    completeOrder,
    transferOrder,
    acceptTransfer,
    rejectTransfer,
    cancelTransfer,
    cancelRepair,
    reserveAssignRepair,
    acceptReserveAssign,
    rejectReserveAssign,
    cancelReserveAssign,
    fetchScheduleAvailability,
    lookupCompany,
    setRepairFee,
    confirmRepair,
    reworkRepair,
    escalateOrder,
    reorderRepair,
    fetchSchedule,
    createSchedule,
    deleteSchedule,
    fetchScheduleLocks,
    createScheduleLock,
    deleteScheduleLock,
    fetchKnowledge,
    fetchKnowledgeDetail,
    fetchConfirmers,
    fetchEngineers,
    fetchStats,
    fetchMyStats
  }
})
