import { defineStore } from 'pinia';
import dayjs from 'dayjs';

export const useTaskStore = defineStore('task', {
  state: () => ({
    // 工程师列表
    engineers: [
      { id: 1, name: '张工', team: '维保一组' },
      { id: 2, name: '李工', team: '维保二组' },
      { id: 3, name: '王工', team: '维保一组' }
    ],

    // 核心任务池
    allTasks: [
      {
        id: 101,
        engineer: '张工',
        date: '2026-04-07',
        timeSlot: 'AM1',
        company: '中国银行大厦',
        status: '已完成',
        type: 'business',
        orderNo: 'HR20260407101',
        progress: [
          { node: '工程师已接单', time: '08:35', status: 'done' },
          { node: '正在处理', time: '09:00', status: 'done' },
          { node: '工单已处理完成，系统自动归档', time: '09:50', status: 'done' }
        ]
      },
      {
        id: 102,
        engineer: '张工',
        date: '2026-04-07',
        timeSlot: 'AM2',
        company: '华润万象城',
        status: '已完成',
        type: 'business',
        orderNo: 'HR20260407102',
        progress: [
          { node: '正在处理', time: '10:30', status: 'done' },
          { node: '工单已处理完成，系统自动归档', time: '11:40', status: 'done' }
        ]
      },
      {
        id: 103,
        engineer: '张工',
        date: '2026-04-07',
        timeSlot: 'PM2', // 15:00-16:30
        company: '车辆例行保养',
        status: '锁定中',
        type: 'break',
        orderNo: '-',
        progress: []
      }
    ]
  }),

  getters: {
    // 获取指定位置的任务
    getSlotTask: (state) => (engName, date, slotId) => {
      return state.allTasks.find(t => 
        t.engineer === engName && t.date === date && t.timeSlot === slotId
      );
    },

    // 计算格子的视觉状态
    getCellStatus: (state) => (engName, date, slotId, range) => {
      const task = state.allTasks.find(t => t.engineer === engName && t.date === date && t.timeSlot === slotId);
      const now = dayjs();
      const [_, endTime] = range.split('-');
      const slotEndTime = dayjs(`${date} ${endTime}`);

      if (task) {
        if (task.status === '已完成') return 'finished';
        if (task.type === 'break') return 'locked';
        // 超时判定：当前时间超过时段结束时间且未完成
        if (now.isAfter(slotEndTime)) return 'overtime';
        return 'occupied';
      }

      // 过期判定
      if (now.isAfter(slotEndTime)) return 'expired';
      return 'available';
    }
  },

  actions: {
    /**
     * 新增任务（业务或锁定）
     */
    addTask(payload) {
      const newTask = {
        id: Date.now(),
        orderNo: payload.type === 'business' ? 'HR' + dayjs().format('YYYYMMDDHHmmss') : '-',
        progress: payload.type === 'business' ? [
          { node: '工程师已接单', time: dayjs().format('HH:mm'), status: 'done' },
          { node: '正在处理', time: dayjs().format('HH:mm'), status: 'doing' }
        ] : [],
        ...payload
      };
      this.allTasks.push(newTask);
    },

    /**
     * 完结工单逻辑：添加归档节点并设为已完成
     */
    completeTask(taskId) {
      const task = this.allTasks.find(t => t.id === taskId);
      if (task) {
        task.status = '已完成';
        task.progress.push({
          node: '工单已处理完成，系统自动归档',
          time: dayjs().format('HH:mm'),
          status: 'done'
        });
      }
    },

    /**
     * 释放锁定：删除非业务锁定记录，腾出期排
     */
    releaseLock(taskId) {
      const index = this.allTasks.findIndex(t => t.id === taskId);
      if (index !== -1) {
        this.allTasks.splice(index, 1);
      }
    }
  }
});