/**
 * 报修工单状态 / 优先级 / 工单类型 / 设备类型 常量与映射
 * 与后端 repairs._format_repair 返回的中文字段对齐：
 *   status        待接单 / 处理中 / 待确认 / 已归档 / 已完成(历史) / 已取消
 *   workOrderType 售后上门 / 协助送货
 *   deviceType    电脑/打印机/复印机/投影仪/扫描仪/网络设备/大屏/其他
 *   priority      紧急 / 普通 / 不急
 *   fee.mode      agreed(已协商好) / self(自行协商)
 */

export const STATUS = {
  PENDING: '待接单',
  RESERVED: '已预约',
  RESERVING: '预约中',
  PROCESSING: '处理中',
  CONFIRMING: '待确认',
  ARCHIVED: '已归档',
  DONE: '已完成',
  CANCELLED: '已取消',
}

export const PRIORITY = {
  URGENT: '紧急',
  NORMAL: '普通',
  LOW: '不急',
}

export const WORK_ORDER_TYPES = ['售后上门', '协助送货']

export const DEVICE_TYPES = ['电脑', '打印机', '复印机', '投影仪', '扫描仪', '网络设备', '大屏', '其他']

export const FEE_MODES = [
  { key: 'agreed', label: '已协商好' },
  { key: 'self', label: '自行协商' },
]

export const REWORK_REASONS = ['故障未解决', '故障再次出现', '其他']

// 排期时段（五个时间段，与 CMS EngineerSchedule / 小程序排期表一致）
export const TIME_SLOTS = [
  { key: 'AM1', label: '上午(早)', range: '08:30-10:00' },
  { key: 'AM2', label: '上午(晚)', range: '10:00-11:50' },
  { key: 'PM1', label: '下午(早)', range: '13:30-15:00' },
  { key: 'PM2', label: '下午(中)', range: '15:00-16:30' },
  { key: 'PM3', label: '下午(晚)', range: '16:30-18:00' },
]

export const slotLabel = (key) => TIME_SLOTS.find(s => s.key === key)?.label || key

// 时长档位（接单时选，占用格数；与后端 slotSpan 对齐：1/2/3/5）
export const DURATION_TIERS = [
  { key: 1, label: '单次', span: 1 },
  { key: 2, label: '上午半天', span: 2 },
  { key: 3, label: '下午半天', span: 3 },
  { key: 5, label: '全天', span: 5 },
]
export const durationLabel = (span) => {
  const n = Number(span) || 1
  return DURATION_TIERS.find(t => t.span === n)?.label || `${n}格`
}

// 中文值 → CSS class 用英文 key
const STATUS_KEY = {
  待接单: 'pending',
  已预约: 'reserved',
  预约中: 'reserved',
  处理中: 'processing',
  待确认: 'confirming',
  已归档: 'archived',
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

// 是否已归档（历史「已完成」与新增「已归档」均视为已归档）
export const isArchivedStatus = (s) => s === '已完成' || s === '已归档'

// 费用方式中文标签
export const feeModeLabel = (m) => FEE_MODES.find(x => x.key === m)?.label || m || ''
