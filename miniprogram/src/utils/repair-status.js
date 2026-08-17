/**
 * 报修工单状态 / 优先级 中文常量与映射
 * 与后端 repairs._format_repair 返回的中文字段对齐：
 *   status   待接单 / 处理中 / 已完成 / 已取消
 *   priority 紧急 / 普通 / 不急
 *   progress 项结构 { node, time, status }
 */

export const STATUS = {
  PENDING: '待接单',
  PROCESSING: '处理中',
  DONE: '已完成',
  CANCELLED: '已取消',
}

export const PRIORITY = {
  URGENT: '紧急',
  NORMAL: '普通',
  LOW: '不急',
}

// 排期时段（五个时间段，与 CMS EngineerSchedule / 小程序排期表一致）
export const TIME_SLOTS = [
  { key: 'AM1', label: '上午(早)', range: '08:30-10:00' },
  { key: 'AM2', label: '上午(晚)', range: '10:00-11:50' },
  { key: 'PM1', label: '下午(早)', range: '13:30-15:00' },
  { key: 'PM2', label: '下午(中)', range: '15:00-16:30' },
  { key: 'PM3', label: '下午(晚)', range: '16:30-18:00' },
]

export const slotLabel = (key) => TIME_SLOTS.find(s => s.key === key)?.label || key

// 中文值 → CSS class 用英文 key
const STATUS_KEY = {
  待接单: 'pending',
  处理中: 'processing',
  已完成: 'done',
  已取消: 'cancelled',
}
const PRIORITY_KEY = {
  紧急: 'urgent',
  普通: 'normal',
  不急: 'low',
}

export const statusKey = (s) => STATUS_KEY[s] || 'pending'
export const priorityKey = (p) => PRIORITY_KEY[p] || 'normal'
