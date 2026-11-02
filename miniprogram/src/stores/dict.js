/**
 * 数据字典 — 业务下拉选项读取（与 CMS getDictOptions 对齐）
 * GET /dict/options?type=xxx → [{label, value}]（启用项）
 */
import { defineStore } from 'pinia'
import { get } from '@/utils/request'

export const useDictStore = defineStore('dict', () => {
  const _cache = {}

  // 返回字典项的 value 列表（value 为空时回退 label）
  const fetchOptions = async (type) => {
    if (_cache[type]) return _cache[type]
    const res = await get('/dict/options', { type })
    const list = Array.isArray(res) ? res : (res?.records || [])
    _cache[type] = list.map((o) => o.value || o.label)
    return _cache[type]
  }

  return { fetchOptions }
})
