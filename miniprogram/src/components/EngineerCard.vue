<!--
  工程师卡片（富信息）— 联系我们 / 工单详情「服务信息」共用
  展示：头像 + 在线状态、姓名/工号、电话、技能标签、服务评分/完成工单/平均响应、私信/电话联系
  flat=true 时去掉外层白卡（嵌入工单详情的 info-card 内使用）
-->
<template>
  <view class="engineer-card" :class="{ flat }">
    <!-- 顶部：头像 + 姓名/工号/电话/技能 -->
    <view class="engineer-card-top">
      <view class="engineer-avatar-wrap">
        <view class="engineer-avatar" :class="'avatar-' + colorIndex">{{ initial }}</view>
        <view class="engineer-online-dot" :class="{ offline: offline }"></view>
      </view>
      <view class="engineer-info">
        <view class="engineer-name-row">
          <text class="engineer-name">{{ name }}</text>
          <text class="engineer-id" v-if="empNo">工号 {{ empNo }}</text>
        </view>
        <view class="engineer-phone" v-if="phone">
          <SvgIcon name="phone" :size="14" color="#165DFF" />
          <text>{{ maskedPhone }}</text>
        </view>
        <view class="engineer-skills" v-if="tags.length">
          <text v-for="(t, ti) in tags" :key="ti" class="engineer-skill-tag" :class="tagColor">{{ t }}</text>
        </view>
      </view>
    </view>

    <!-- 数据统计 -->
    <view class="engineer-card-stats">
      <view class="engineer-stat-item">
        <view class="engineer-stat-num">
          <SvgIcon name="star" :size="14" color="#FF7D00" />
          <text>{{ ratingText }}</text>
        </view>
        <text class="engineer-stat-label">服务评分</text>
      </view>
      <view class="engineer-stat-item">
        <view class="engineer-stat-num"><text>{{ completedText }}</text></view>
        <text class="engineer-stat-label">完成工单</text>
      </view>
      <view class="engineer-stat-item">
        <view class="engineer-stat-num" :class="{ fast: isFast }"><text>{{ responseText }}</text></view>
        <text class="engineer-stat-label">平均响应</text>
      </view>
    </view>

    <!-- 操作按钮（本人时隐藏电话/私信，避免联系自己） -->
    <view class="engineer-card-actions">
      <view v-if="isSelf" class="engineer-self-tag">
        <SvgIcon name="user" :size="15" color="#165DFF" />
        <text>本人</text>
      </view>
      <template v-else>
        <button class="engineer-btn engineer-btn-secondary" @click="onChat">
          <SvgIcon name="envelope" :size="15" color="#4E5969" />
          <text>私信</text>
        </button>
        <button class="engineer-btn engineer-btn-primary" @click="onCall">
          <SvgIcon name="phone" :size="15" color="#fff" />
          <text>电话联系</text>
        </button>
      </template>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from './SvgIcon.vue'

const router = useRouter()
const authStore = useAuthStore()

const props = defineProps({
  engineer: { type: Object, default: () => ({}) },
  index: { type: Number, default: 0 },
  flat: { type: Boolean, default: false }
})

const name = computed(() => props.engineer?.name || props.engineer?.realName || '工程师')
const initial = computed(() => name.value.charAt(0))
const colorIndex = computed(() => props.index % 4)
const offline = computed(() => props.engineer?.online === false)
const phone = computed(() => props.engineer?.phone || '')

// 工号：优先取后端字段，缺省按序号生成 HR 编号
const empNo = computed(() =>
  props.engineer?.employeeNo || props.engineer?.workNo || props.engineer?.staffNo ||
  ('HR' + String(props.index + 1).padStart(3, '0'))
)

// 电话脱敏：138****0103
const maskedPhone = computed(() => {
  const s = String(phone.value || '')
  if (s.length < 7) return s
  return s.slice(0, 3) + '****' + s.slice(-4)
})

// 技能标签：支持数组或「、,，/ 」分隔的字符串
const tags = computed(() => {
  const v = props.engineer?.skills || props.engineer?.team
  if (!v) return []
  if (Array.isArray(v)) return v
  return String(v).split(/[、,，/;；\s]+/).filter(Boolean)
})

// 标签配色按工程师轮换（蓝/紫/绿/橙）
const tagColor = computed(() => (['', 'purple', 'green', 'orange'])[props.index % 4])

const ratingText = computed(() => (props.engineer?.rating != null ? props.engineer.rating : '—'))
const completedText = computed(() => (props.engineer?.completed != null ? props.engineer.completed : '—'))
const responseText = computed(() => props.engineer?.avgResponse || props.engineer?.responseTime || '—')
const isFast = computed(() => /(min|分钟)/.test(String(props.engineer?.avgResponse || props.engineer?.responseTime || '')))

// 本人：工程师查看自己的服务信息时，不展示电话/私信
const isSelf = computed(() => {
  const me = authStore.userInfo?.id || authStore.userInfo?._id || authStore.userInfo?.username || ''
  const engId = props.engineer?.id || props.engineer?._id || props.engineer?.username || ''
  if (!me || !engId) return false
  return String(me) === String(engId)
})

const onCall = () => {
  if (phone.value) uni.makePhoneCall({ phoneNumber: phone.value })
  else uni.showToast({ title: '暂无联系方式', icon: 'none' })
}
const onChat = () => {
  const peerId = props.engineer?.id || props.engineer?._id
  if (!peerId) return uni.showToast({ title: '暂无法私信', icon: 'none' })
  if (!authStore.isLoggedIn) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    router.push('/pages/public/login/index')
    return
  }
  router.push(`/pages/chat/index?peerId=${peerId}&peerName=${encodeURIComponent(name.value)}`)
}
</script>

<style lang="scss" scoped>
.engineer-card {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;

  &:active { transform: scale(0.98); }

  &.flat {
    background: transparent;
    box-shadow: none;
    border-radius: 0;
    padding: 0;
    margin-bottom: 0;

    &:active { transform: none; }
  }
}

.engineer-card-top { display: flex; align-items: flex-start; gap: 24rpx; margin-bottom: 24rpx; }
.engineer-avatar-wrap { position: relative; flex-shrink: 0; }
.engineer-avatar {
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 44rpx;
  font-weight: 700;

  &.avatar-0 { background: linear-gradient(135deg, #165DFF, #4080FF); }
  &.avatar-1 { background: linear-gradient(135deg, #722ED1, #9254DE); }
  &.avatar-2 { background: linear-gradient(135deg, #00B42A, #23C343); }
  &.avatar-3 { background: linear-gradient(135deg, #FF7D00, #FF9A2E); }
}
.engineer-online-dot {
  position: absolute;
  bottom: 4rpx;
  right: 4rpx;
  width: 28rpx;
  height: 28rpx;
  border-radius: 50%;
  background: #00B42A;
  border: 4rpx solid #fff;

  &.offline { background: #C9CDD4; }
}
.engineer-info { flex: 1; min-width: 0; }
.engineer-name-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 8rpx; }
.engineer-name { font-size: 34rpx; font-weight: 700; color: #1D2129; }
.engineer-id {
  font-size: 22rpx;
  color: #86909C;
  background: #F2F3F5;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-weight: 500;
}
.engineer-phone {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #4E5969;
  margin-bottom: 16rpx;
}
.engineer-skills { display: flex; flex-wrap: wrap; gap: 10rpx; }
.engineer-skill-tag {
  padding: 6rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
  font-weight: 500;
  background: #E8F3FF;
  color: #165DFF;

  &.purple { background: #F5E8FF; color: #722ED1; }
  &.green  { background: #E8FFEA; color: #00B42A; }
  &.orange { background: #FFF3E8; color: #FF7D00; }
}

.engineer-card-stats {
  display: flex;
  gap: 40rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #F2F3F5;
  margin-bottom: 24rpx;
}
.engineer-stat-item { display: flex; flex-direction: column; gap: 6rpx; }
.engineer-stat-num {
  font-size: 32rpx;
  font-weight: 700;
  color: #1D2129;
  display: flex;
  align-items: center;
  gap: 4rpx;

  &.fast { color: #00B42A; }
}
.engineer-stat-label { font-size: 22rpx; color: #86909C; }

.engineer-card-actions { display: flex; gap: 20rpx; }
.engineer-self-tag {
  flex: 1;
  height: 76rpx;
  border-radius: 38rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #165DFF;
  background: #E8F3FF;
}
.engineer-btn {
  flex: 1;
  height: 76rpx;
  border-radius: 38rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  font-size: 26rpx;
  font-weight: 600;
  border: none;
}
.engineer-btn-primary {
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  box-shadow: 0 3rpx 10rpx rgba(22, 93, 255, 0.25);
}
.engineer-btn-secondary { background: #F2F3F5; color: #4E5969; }
</style>
