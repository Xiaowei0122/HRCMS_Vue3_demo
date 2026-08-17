<!--
  投诉建议 — 一键投诉 + 我的投诉
-->
<template>
  <view class="page">
    <!-- 子板块切换 -->
    <view class="sub-tabs">
      <view class="sub-tab" :class="{ active: activeTab === 'submit' }" @click="activeTab = 'submit'">
        <SvgIcon name="envelope" :size="18" />
        <text>一键投诉</text>
      </view>
      <view class="sub-tab" :class="{ active: activeTab === 'my' }" @click="switchToMy">
        <SvgIcon name="clipboard" :size="18" />
        <text>我的投诉</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body">
      <!-- 一键投诉 -->
      <view v-show="activeTab === 'submit'" class="panel">
        <view class="card">
          <text class="card-title">提交投诉建议</text>
          <text class="card-desc">如对我们的服务有任何意见或建议，请在此反馈</text>

          <view class="form-group">
            <text class="label">投诉类型</text>
            <picker mode="selector" :range="complaintTypes" @change="onTypeChange">
              <view class="picker" :class="{ placeholder: !form.type }">
                <text>{{ form.type || '请选择投诉类型' }}</text>
                <SvgIcon name="caretRight" :size="14" class="arrow" />
              </view>
            </picker>
          </view>

          <view class="form-group">
            <text class="label">投诉标题 <text class="required">*</text></text>
            <input class="input" v-model="form.title" placeholder="简要描述您的问题" placeholder-style="color:#CBD5E1" maxlength="50" />
          </view>

          <view class="form-group">
            <text class="label">详细内容 <text class="required">*</text></text>
            <textarea class="textarea" v-model="form.content" placeholder="请详细描述您遇到的问题或建议..." placeholder-style="color:#CBD5E1" maxlength="500" :auto-height="true" />
            <text class="char-count">{{ form.content.length }}/500</text>
          </view>

          <view class="form-group">
            <text class="label">联系方式（选填）</text>
            <input class="input" v-model="form.contact" placeholder="手机号或邮箱，方便我们回复" placeholder-style="color:#CBD5E1" maxlength="50" />
          </view>

          <button class="btn-primary" :disabled="submitting" @click="handleSubmit">
            {{ submitting ? '提交中...' : '提交投诉' }}
          </button>
        </view>
      </view>

      <!-- 我的投诉 -->
      <view v-show="activeTab === 'my'" class="panel">
        <view v-if="myComplaints.length" class="list">
          <view v-for="item in myComplaints" :key="item._id || item.id" class="list-card">
            <view class="list-card-top">
              <text class="type-tag">{{ item.type || '投诉' }}</text>
              <text class="status" :class="'s-' + statusClass(item.status)">{{ item.status || '待处理' }}</text>
            </view>
            <text class="list-card-title">{{ item.title }}</text>
            <text class="list-card-body">{{ item.content }}</text>
            <view class="list-card-foot">
              <text class="time">{{ formatTime(item.createTime) }}</text>
              <text class="reply" v-if="item.reply">查看回复 →</text>
            </view>
          </view>
        </view>
        <EmptyState v-else icon="envelope" text="暂无投诉记录" sub-text="提交的投诉将在这里显示处理进度" />
      </view>

      <view class="safe-bottom" />
    </scroll-view>

    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { get, post } from '@/utils/request'
import CustomTabBar from '@/components/CustomTabBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const activeTab = ref('submit')
const submitting = ref(false)
const myComplaints = ref([])
const complaintTypes = ['服务态度', '维修质量', '响应速度', '收费问题', '其他建议']

const form = ref({ type: '', title: '', content: '', contact: '' })

// 投诉状态（后端返回中文：待处理 / 处理中 / 已解决）
const statusClass = (s) => ({ 待处理: 'pending', 处理中: 'processing', 已解决: 'resolved' }[s] || 'pending')

const onTypeChange = (e) => { form.value.type = complaintTypes[e.detail.value] }

const handleSubmit = async () => {
  if (!form.value.title.trim()) return uni.showToast({ title: '请填写投诉标题', icon: 'none' })
  if (!form.value.content.trim()) return uni.showToast({ title: '请填写详细内容', icon: 'none' })
  submitting.value = true
  try {
    await post('/complaints', { type: form.value.type, title: form.value.title.trim(), content: form.value.content.trim(), contact: form.value.contact.trim() })
    uni.showToast({ title: '投诉提交成功', icon: 'success' })
    setTimeout(() => { form.value = { type: '', title: '', content: '', contact: '' } }, 500)
  } catch { /* handled */ }
  finally { submitting.value = false }
}

const loadMyComplaints = async () => {
  try { const res = await get('/complaints/my'); myComplaints.value = Array.isArray(res) ? res : (res?.records || []) } catch { /* handled */ }
}

const switchToMy = () => { activeTab.value = 'my'; loadMyComplaints() }

const formatTime = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
}
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: #F8FAFC;
  display: flex;
  flex-direction: column;
}

/* 子Tabs */
.sub-tabs {
  display: flex;
  background: #fff;
  padding: 16rpx 24rpx;
  gap: 16rpx;
  flex-shrink: 0;
}
.sub-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: #64748B;
  background: #F1F5F9;
  border-radius: 10rpx;
  transition: all 0.25s ease;

  &.active { background: #0F172A; color: #fff; font-weight: 600; }
  &:active { transform: scale(0.96); }
}

.scroll-body { flex: 1; }

.panel { animation: fadeIn 0.25s ease; }

/* 表单卡片 */
.card {
  margin: 20rpx 24rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,.04);
}
.card-title { font-size: 30rpx; font-weight: 700; color: #020617; display: block; }
.card-desc  { font-size: 24rpx; color: #64748B; margin-top: 8rpx; margin-bottom: 28rpx; display: block; }

.form-group { margin-bottom: 22rpx; }
.label { font-size: 26rpx; color: #334155; font-weight: 500; margin-bottom: 8rpx; display: block; }
.required { color: #DC2626; }

.input {
  width: 100%; height: 80rpx; background: #F1F5F9; border-radius: 10rpx;
  padding: 0 20rpx; font-size: 28rpx; color: #334155; box-sizing: border-box;
}
.picker {
  width: 100%; height: 80rpx; background: #F1F5F9; border-radius: 10rpx;
  padding: 0 20rpx; font-size: 28rpx; color: #334155;
  display: flex; align-items: center; justify-content: space-between; box-sizing: border-box;
  &.placeholder { color: #CBD5E1; }
}
.arrow { color: #94A3B8; transform: rotate(90deg); }
.textarea {
  width: 100%; min-height: 200rpx; background: #F1F5F9; border-radius: 10rpx;
  padding: 20rpx; font-size: 28rpx; color: #334155; box-sizing: border-box;
}
.char-count { font-size: 22rpx; color: #CBD5E1; text-align: right; display: block; margin-top: 4rpx; }

.btn-primary {
  width: 100%; height: 88rpx; line-height: 88rpx;
  background: #0F172A; color: #fff; font-size: 30rpx; font-weight: 600;
  border: none; border-radius: 44rpx; text-align: center; margin-top: 8rpx;
  &:active { opacity: .85; transform: scale(.97); }
  &[disabled] { background: #94A3B8; }
}

/* 投诉列表 */
.list { padding: 16rpx 24rpx; }
.list-card {
  background: #fff; border-radius: 14rpx; padding: 24rpx; margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,.04);
  &:active { transform: scale(.98); }
}
.list-card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12rpx; }
.type-tag { font-size: 22rpx; color: #0369A1; background: #F0F9FF; padding: 4rpx 14rpx; border-radius: 6rpx; }
.status { font-size: 22rpx; padding: 4rpx 14rpx; border-radius: 20rpx; }
.s-pending    { background: #FEF3C7; color: #D97706; }
.s-processing { background: #E0F2FE; color: #0369A1; }
.s-resolved   { background: #DCFCE7; color: #16A34A; }
.list-card-title { font-size: 28rpx; font-weight: 600; color: #020617; display: block; margin-bottom: 8rpx; }
.list-card-body  { font-size: 26rpx; color: #334155; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; line-height: 1.5; }
.list-card-foot  { display: flex; justify-content: space-between; align-items: center; margin-top: 12rpx; padding-top: 12rpx; border-top: 1px solid #E2E8F0; }
.time { font-size: 22rpx; color: #94A3B8; }
.reply { font-size: 22rpx; color: #0369A1; }

.safe-bottom { height: 32rpx; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12rpx); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
