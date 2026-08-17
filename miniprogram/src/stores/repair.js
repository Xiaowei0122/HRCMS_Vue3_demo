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

  // ── 工单详情 ──
  const fetchDetail = async (repairId) => {
    const res = await get(`/repairs/${repairId}`)
    currentDetail.value = res
    return currentDetail.value
  }

  // ── 工程师接单 ──
  const acceptOrder = async (repairId, scheduleData) => {
    return await patch(`/repairs/${repairId}/assign`, scheduleData)
  }

  // ── 管理员指派工单（业务工单 → 指派到排期）──
  const assignOrder = async (repairId, scheduleData) => {
    return await patch(`/repairs/${repairId}/assign`, scheduleData)
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

  // ── 工程师排期 ──
  const fetchSchedule = async (params = {}) => {
    const res = await get('/repairs/schedule', params)
    scheduleData.value = res?.records || res || []
    return scheduleData.value
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

  // ── 统计数据 ──
  const fetchStats = async () => {
    const res = await get('/repairs/stats')
    stats.value = res || {}
    return stats.value
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
    fetchDetail,
    acceptOrder,
    assignOrder,
    addProgress,
    completeOrder,
    transferOrder,
    fetchSchedule,
    createSchedule,
    deleteSchedule,
    fetchEngineers,
    fetchStats
  }
})
