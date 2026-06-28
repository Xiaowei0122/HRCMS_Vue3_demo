import { defineStore } from 'pinia'
import dayjs from 'dayjs'
import {
  getEngineerList, getEngineerSchedule,
  createScheduleEntry, deleteScheduleEntry,
  createRepair, completeRepair as apiCompleteRepair
} from '@/api/modules/repairs'

export const useTaskStore = defineStore('task', {
  state: () => ({
    // 工程师列表
    engineers: [
      { id: 1, name: '张工', team: '维保一组' },
      { id: 2, name: '李工', team: '维保二组' },
      { id: 3, name: '王工', team: '维保一组' }
    ],

    // 核心任务池
    allTasks: [],

    // 加载状态
    loading: false
  }),

  getters: {
    // 获取指定位置的任务
    getSlotTask: (state) => (engName, date, slotId) => {
      return state.allTasks.find(t =>
        t.engineer === engName && t.date === date && t.timeSlot === slotId
      )
    },

    // 计算格子的视觉状态
    getCellStatus: (state) => (engName, date, slotId, range) => {
      const task = state.allTasks.find(t =>
        t.engineer === engName && t.date === date && t.timeSlot === slotId
      )
      const now = dayjs()
      const [_, endTime] = range.split('-')
      const slotEndTime = dayjs(`${date} ${endTime}`)

      if (task) {
        if (task.status === '已完成') return 'finished'
        if (task.type === 'break') return 'locked'
        if (now.isAfter(slotEndTime)) return 'overtime'
        return 'occupied'
      }

      if (now.isAfter(slotEndTime)) return 'expired'
      return 'available'
    }
  },

  actions: {
    /**
     * 从后端拉取工程师列表
     */
    async fetchEngineers() {
      try {
        const res = await getEngineerList()
        if (Array.isArray(res)) {
          this.engineers = res
        } else if (res?.records) {
          this.engineers = res.records
        }
      } catch {
        // 保留本地兜底数据
      }
    },

    /**
     * 从后端拉取排期数据
     */
    async fetchSchedule(params = {}) {
      this.loading = true
      try {
        const res = await getEngineerSchedule(params)
        const list = Array.isArray(res) ? res : (res?.records || [])
        this.allTasks = list
      } catch {
        // 保留已有数据
      } finally {
        this.loading = false
      }
    },

    /**
     * 新增任务（业务报修 或 锁定时段）
     */
    async addTask(payload) {
      try {
        if (payload.type === 'business') {
          // 业务报修走 createRepair 接口（由后端生成单号）
          await createRepair(payload)
        } else {
          // 锁定时段走排期接口
          await createScheduleEntry(payload)
        }
        // 成功后刷新列表
        await this.fetchSchedule()
      } catch {
        throw new Error('操作失败')
      }
    },

    /**
     * 完结工单
     */
    async completeTask(taskId) {
      try {
        await apiCompleteRepair(taskId)
        // 乐观更新本地
        const task = this.allTasks.find(t => t.id === taskId)
        if (task) {
          task.status = '已完成'
          task.progress.push({
            node: '工单已处理完成，系统自动归档',
            time: dayjs().format('HH:mm'),
            status: 'done'
          })
        }
      } catch {
        throw new Error('完结工单失败')
      }
    },

    /**
     * 释放锁定
     */
    async releaseLock(taskId) {
      try {
        await deleteScheduleEntry(taskId)
        const index = this.allTasks.findIndex(t => t.id === taskId)
        if (index !== -1) {
          this.allTasks.splice(index, 1)
        }
      } catch {
        throw new Error('释放锁定失败')
      }
    }
  }
})
