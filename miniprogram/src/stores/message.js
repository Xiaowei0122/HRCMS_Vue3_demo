/**
 * 私信（即时消息）状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { get, post } from '@/utils/request'

export const useMessageStore = defineStore('message', () => {
  const conversations = ref([])
  const messages = ref([])
  const currentPeer = ref(null)
  const conversationId = ref('')

  const fetchConversations = async () => {
    const res = await get('/messages/conversations')
    conversations.value = Array.isArray(res) ? res : (res?.records || [])
    return conversations.value
  }

  const fetchUnreadCount = async () => {
    const res = await get('/messages/unread-count')
    return res?.count ?? 0
  }

  // 打开/创建与某用户的会话
  const openConversation = async (peerId) => {
    const res = await post('/messages/conversations', { peerId })
    conversationId.value = res.id
    currentPeer.value = res.peer
    return res
  }

  const fetchMessages = async (id = conversationId.value, limit = 100) => {
    const res = await get(`/messages/conversations/${id}/messages`, { limit })
    messages.value = Array.isArray(res) ? res : []
    return messages.value
  }

  const send = async (content, id = conversationId.value) => {
    return await post(`/messages/conversations/${id}/messages`, { content })
  }

  const markRead = async (id = conversationId.value) => {
    await post(`/messages/conversations/${id}/read`)
  }

  return {
    conversations,
    messages,
    currentPeer,
    conversationId,
    fetchConversations,
    fetchUnreadCount,
    openConversation,
    fetchMessages,
    send,
    markRead
  }
})
