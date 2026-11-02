<!--
  私信聊天页
  ?convId=xxx 已有会话直接进入；?peerId=xxx 先创建/获取会话
  peerName 用于导航标题回退显示
-->
<template>
  <view class="page">
    <PageNavbar :title="peerName" />

    <scroll-view scroll-y class="chat-scroll" ref="scrollRef">
      <view v-if="loading" class="loading-box">
        <text class="loading-text">加载中...</text>
      </view>

      <template v-else>
        <EmptyState v-if="!messages.length" icon="envelope" text="开始聊天吧" sub-text="发送第一条消息，工程师会尽快回复" />

        <view v-else class="msg-list">
          <view v-for="m in messages" :key="m.id" class="msg-row" :class="{ mine: m.mine }">
            <view v-if="!m.mine" class="msg-avatar">{{ peerName.charAt(0) }}</view>
            <view class="msg-col">
              <view class="msg-bubble" :class="{ mine: m.mine }">
                <text class="msg-content">{{ m.content }}</text>
              </view>
              <text class="msg-time">{{ fmtTime(m.createdAt) }}</text>
            </view>
          </view>
        </view>
      </template>

      <view class="safe-bottom" />
    </scroll-view>

    <!-- 输入栏 -->
    <view class="input-bar">
      <input
        class="chat-input"
        v-model="inputText"
        type="text"
        placeholder="输入消息..."
        placeholder-style="color:#C9CDD4"
        confirm-type="send"
        :disabled="!conversationId"
        @confirm="send"
      />
      <button class="send-btn" :disabled="sending || !conversationId || !inputText.trim()" @click="send">
        <text>发送</text>
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const messageStore = useMessageStore()

const loading = ref(true)
const inputText = ref('')
const sending = ref(false)
const scrollRef = ref(null)

const conversationId = computed(() => messageStore.conversationId || route.query.convId || '')
const peerName = computed(() => (messageStore.currentPeer?.name) || route.query.peerName || '私信')
const messages = computed(() => messageStore.messages)

let pollTimer = null

const scrollToBottom = () => {
  nextTick(() => {
    const el = scrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

const loadMessages = async () => {
  if (!conversationId.value) return
  await messageStore.fetchMessages(conversationId.value)
  scrollToBottom()
}

const init = async () => {
  loading.value = true
  try {
    // 已有会话 id 直接加载；否则按 peerId 创建/获取
    if (!conversationId.value && route.query.peerId) {
      await messageStore.openConversation(route.query.peerId)
    }
    if (conversationId.value) {
      await loadMessages()
    }
  } catch { /* 已 toast */ }
  finally {
    loading.value = false
  }
}

const send = async () => {
  const text = inputText.value.trim()
  if (!text || !conversationId.value || sending.value) return
  sending.value = true
  try {
    const msg = await messageStore.send(text, conversationId.value)
    messageStore.messages.push(msg)
    inputText.value = ''
    scrollToBottom()
  } catch { /* 已 toast */ }
  finally { sending.value = false }
}

const fmtTime = (t) => {
  if (!t) return ''
  const m = String(t).match(/(\d{2}):(\d{2})/)
  return m ? `${m[1]}:${m[2]}` : String(t)
}

onMounted(async () => {
  await init()
  // 轮询新消息（每 6 秒）
  pollTimer = setInterval(async () => {
    if (!conversationId.value) return
    try {
      const before = messages.value.length
      await messageStore.fetchMessages(conversationId.value)
      if (messages.value.length !== before) scrollToBottom()
    } catch { /* ignore */ }
  }, 6000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; }
.chat-scroll { flex: 1; }

.loading-box { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-text { font-size: 28rpx; color: #86909C; }

.msg-list { padding: 24rpx; display: flex; flex-direction: column; gap: 24rpx; }
.msg-row { display: flex; align-items: flex-start; gap: 16rpx; }
.msg-row.mine { justify-content: flex-end; }

.msg-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.msg-col { display: flex; flex-direction: column; align-items: flex-start; max-width: 72%; }
.msg-row.mine .msg-col { align-items: flex-end; }

.msg-bubble {
  background: #fff;
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}
.msg-bubble.mine {
  background: linear-gradient(135deg, #165DFF, #4080FF);
  box-shadow: 0 4rpx 16rpx rgba(22, 93, 255, 0.25);
}
.msg-content { font-size: 28rpx; line-height: 1.5; color: #1D2129; word-break: break-all; }
.msg-bubble.mine .msg-content { color: #fff; }
.msg-time { font-size: 20rpx; color: #C9CDD4; margin-top: 8rpx; }

/* 输入栏 */
.input-bar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F2F3F5;
}
.chat-input {
  flex: 1;
  height: 76rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 38rpx;
  padding: 0 28rpx;
  font-size: 28rpx;
  color: #1D2129;
  box-sizing: border-box;
}
.send-btn {
  width: 128rpx;
  height: 76rpx;
  border-radius: 38rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  &:active { opacity: 0.9; }
  &[disabled] { background: #C9CDD4; }
}

.safe-bottom { height: 24rpx; }
</style>
