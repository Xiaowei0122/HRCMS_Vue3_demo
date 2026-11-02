<!--
  私信 — 会话列表
-->
<template>
  <view class="page">
    <PageNavbar title="私信" />

    <scroll-view scroll-y class="scroll-body">
      <view v-if="loading" class="loading-box">
        <text class="loading-text">加载中...</text>
      </view>

      <template v-else>
        <view v-if="conversations.length" class="conv-list">
          <view v-for="c in conversations" :key="c.id" class="conv-item" @click="openChat(c)">
            <view class="conv-avatar" :class="'avatar-' + (c._idx % 4)">{{ c.peer.name.charAt(0) }}</view>
            <view class="conv-main">
              <view class="conv-top">
                <text class="conv-name">{{ c.peer.name }}</text>
                <text class="conv-time">{{ fmtTime(c.lastAt) }}</text>
              </view>
              <view class="conv-bottom">
                <text class="conv-msg">{{ c.lastMessage || '开始聊天吧' }}</text>
                <view v-if="c.unread > 0" class="conv-badge">{{ c.unread > 99 ? '99+' : c.unread }}</view>
              </view>
            </view>
          </view>
        </view>

        <EmptyState v-else icon="envelope" text="暂无私信" sub-text="在「联系我们」选择工程师发起私信" />
      </template>

      <view class="safe-bottom" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()
const messageStore = useMessageStore()

const loading = ref(true)
const conversations = ref([])

const loadList = async () => {
  try {
    const list = await messageStore.fetchConversations()
    conversations.value = list.map((c, i) => ({ ...c, _idx: i }))
  } catch {
    conversations.value = []
  } finally {
    loading.value = false
  }
}

const openChat = (c) => {
  router.push(`/pages/chat/index?convId=${c.id}&peerName=${encodeURIComponent(c.peer.name)}`)
}

// 会话时间：今天显示 HH:MM，其余显示 MM-DD
const fmtTime = (t) => {
  if (!t) return ''
  const s = String(t)
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/)
  if (!m) return s
  const now = new Date()
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  const day = `${m[1]}-${m[2]}-${m[3]}`
  return day === today ? `${m[4]}:${m[5]}` : `${m[2]}-${m[3]}`
}

onMounted(loadList)
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; }
.scroll-body { flex: 1; }

.loading-box { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-text { font-size: 28rpx; color: #86909C; }

.conv-list { padding: 24rpx; display: flex; flex-direction: column; gap: 16rpx; }
.conv-item {
  background: #fff;
  border-radius: 28rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
  &:active { opacity: 0.85; }
}
.conv-avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 40rpx;
  font-weight: 700;
  flex-shrink: 0;

  &.avatar-0 { background: linear-gradient(135deg, #165DFF, #4080FF); }
  &.avatar-1 { background: linear-gradient(135deg, #722ED1, #9254DE); }
  &.avatar-2 { background: linear-gradient(135deg, #00B42A, #23C343); }
  &.avatar-3 { background: linear-gradient(135deg, #FF7D00, #FF9A2E); }
}
.conv-main { flex: 1; min-width: 0; }
.conv-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10rpx; }
.conv-name { font-size: 30rpx; font-weight: 600; color: #1D2129; }
.conv-time { font-size: 22rpx; color: #C9CDD4; }
.conv-bottom { display: flex; align-items: center; justify-content: space-between; }
.conv-msg {
  flex: 1;
  font-size: 26rpx;
  color: #86909C;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.conv-badge {
  min-width: 36rpx;
  height: 36rpx;
  border-radius: 18rpx;
  background: #F53F3F;
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
  margin-left: 16rpx;
}

.safe-bottom { height: 24rpx; }
</style>
