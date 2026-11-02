/**
 * 技术知识库 — 共享分类/缩略图/标签映射
 * 首页与知识库列表页共用，保证分类样式一致
 */

// 分类顺序（与后台录入分类对齐）
export const CATEGORIES = ['驱动安装', '故障案例', '系统维护', '网络运维', '监控安防']

// 分类 → 缩略图/标签样式 key
const TYPE_STYLE = {
  '驱动安装': 'printer',
  '故障案例': 'case',
  '系统维护': 'system',
  '网络运维': 'network',
  '监控安防': 'camera'
}

// 根据分类（优先精确匹配）或标题关键字映射样式
export const articleStyle = (n = {}) => {
  const type = n.type || ''
  if (TYPE_STYLE[type]) return TYPE_STYLE[type]
  const t = `${type}${n.title || ''}`
  if (/打印机|驱动|打印|复印/.test(t)) return 'printer'
  if (/故障|案例|排查/.test(t)) return 'case'
  if (/监控|安防|门禁|摄像头/.test(t)) return 'camera'
  if (/网络|poe|网线|ip|交换机/.test(t)) return 'network'
  return 'system'
}

// 样式 key → 标签 class
const TAG_CLASS = {
  printer: 'tag-tutorial',
  case: 'tag-case',
  system: 'tag-guide',
  network: 'tag-network',
  camera: 'tag-camera'
}
export const tagClassFor = (style) => TAG_CLASS[style] || 'tag-tutorial'

// 阅读量格式化（1.2k）
export const formatViews = (v) => {
  if (!v) return '0'
  if (v >= 1000) return `${(v / 1000).toFixed(1).replace('.0', '')}k`
  return String(v)
}
