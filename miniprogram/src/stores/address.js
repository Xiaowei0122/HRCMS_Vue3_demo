/**
 * 地址簿状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { get, post, put, del } from '@/utils/request'

export const useAddressStore = defineStore('address', () => {
  const list = ref([])

  const fetchList = async () => {
    const res = await get('/addresses')
    list.value = Array.isArray(res) ? res : (res?.records || [])
    return list.value
  }

  const create = async (data) => await post('/addresses', data)
  const update = async (id, data) => await put(`/addresses/${id}`, data)
  const remove = async (id) => await del(`/addresses/${id}`)
  const setDefault = async (id) => await post(`/addresses/${id}/default`)

  return { list, fetchList, create, update, remove, setDefault }
})
