<!--
  投诉建议 — Navbar + 下划线式 Tab + 一键投诉 / 我的投诉
-->
<template>
  <view class="page">
    <PageNavbar title="投诉建议" />

    <!-- 子板块切换（下划线式） -->
    <view class="page-tabs">
      <view class="page-tab" :class="{ active: activeTab === 'submit' }" @click="activeTab = 'submit'">
        <SvgIcon name="envelope" :size="18" />
        <text>一键投诉</text>
      </view>
      <view class="page-tab" :class="{ active: activeTab === 'my' }" @click="switchToMy">
        <SvgIcon name="clipboard" :size="18" />
        <text>我的投诉</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body">
      <!-- 一键投诉 -->
      <view v-show="activeTab === 'submit'" class="panel">
        <view class="card">
          <view class="card-head">
            <view class="card-title">
              <SvgIcon name="envelope" :size="20" color="#165DFF" />
              <text>提交投诉建议</text>
            </view>
            <text class="card-desc">如对我们的服务有任何意见或建议，请在此反馈</text>
          </view>

          <view class="form-group">
            <text class="label">投诉类型</text>
            <view class="picker" :class="{ placeholder: !form.type }" @click="showTypeSheet = true">
              <text>{{ form.type || '请选择投诉类型' }}</text>
              <SvgIcon name="caretRight" :size="14" class="arrow" />
            </view>
          </view>

          <view class="form-group">
            <text class="label">投诉标题 <text class="required">*</text></text>
            <input class="input" v-model="form.title" placeholder="简要描述您的问题" placeholder-style="color:#C9CDD4" maxlength="50" />
          </view>

          <view class="form-group">
            <text class="label">详细内容 <text class="required">*</text></text>
            <textarea class="textarea" v-model="form.content" placeholder="请详细描述您遇到的问题或建议..." placeholder-style="color:#C9CDD4" maxlength="500" :auto-height="true" />
            <text class="char-count">{{ form.content.length }}/500</text>
          </view>

          <view class="form-group">
            <text class="label">联系方式（选填）</text>
            <input class="input" v-model="form.contact" placeholder="手机号或邮箱，方便我们回复" placeholder-style="color:#C9CDD4" maxlength="50" />
          </view>
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

    <!-- 底部提交栏（仅一键投诉） -->
    <view class="bottom-bar" v-if="activeTab === 'submit'">
      <button class="primary-btn" :disabled="submitting" @click="handleSubmit">
        <SvgIcon name="envelope" :size="18" color="#fff" />
        <text>{{ submitting ? '提交中...' : '提交投诉' }}</text>
      </button>
    </view>

    <!-- 投诉类型选择 -->
    <PickerSheet v-model="showTypeSheet" title="选择投诉类型" :options="complaintTypeOptions" :value="form.type" @select="onTypeSelect" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { get, post } from '@/utils/request'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import PickerSheet from '@/components/PickerSheet.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const activeTab = ref('submit')
const submitting = ref(false)
const myComplaints = ref([])
const showTypeSheet = ref(false)
const complaintTypes = ['服务态度', '维修质量', '响应速度', '收费问题', '其他建议']
const complaintTypeOptions = complaintTypes.map((t) => ({ label: t, value: t }))

const form = ref({ type: '', title: '', content: '', contact: '' })

// 投诉状态（后端返回中文：待处理 / 处理中 / 已解决）
const statusClass = (s) => ({ 待处理: 'pending', 处理中: 'processing', 已解决: 'resolved' }[s] || 'pending')

const onTypeSelect = (v) => { form.value.type = v }

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
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}

/* 下划线式子 Tab */
.page-tabs {
  display: flex; background: #fff; padding: 0 24rpx; gap: 40rpx;
  border-bottom: 1rpx solid #F2F3F5; flex-shrink: 0;
}
.page-tab {
  display: flex; align-items: center; gap: 8rpx;
  padding: 24rpx 0; font-size: 28rpx; color: #4E5969; font-weight: 500;
  position: relative; transition: color .25s ease;

  &.active {
    color: #165DFF; font-weight: 700;
    &::after {
      content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 6rpx;
      background: linear-gradient(90deg, #165DFF, #4080FF); border-radius: 3rpx;
    }
  }
}

.scroll-body { flex: 1; }
.panel { animation: fadeIn 0.25s ease; }

/* 表单卡片 */
.card {
  margin: 24rpx;
  background: #fff;
  border-radius: 32rpx;
  padding: 36rpx 32rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}
.card-head { margin-bottom: 8rpx; }
.card-title { display: flex; align-items: center; gap: 10rpx; font-size: 34rpx; font-weight: 700; color: #1D2129; margin-bottom: 8rpx; }
.card-desc  { font-size: 24rpx; color: #86909C; display: block; }

.form-group { margin-top: 28rpx; }
.label { font-size: 26rpx; color: #4E5969; font-weight: 500; margin-bottom: 12rpx; display: block; }
.required { color: #F53F3F; }

.input {
  width: 100%; height: 88rpx; background: #F7F8FA; border: 1.5px solid #E5E6EB; border-radius: 16rpx;
  padding: 0 24rpx; font-size: 28rpx; color: #1D2129; box-sizing: border-box;
}
.picker {
  width: 100%; height: 88rpx; background: #F7F8FA; border: 1.5px solid #E5E6EB; border-radius: 16rpx;
  padding: 0 24rpx; font-size: 28rpx; color: #4E5969;
  display: flex; align-items: center; justify-content: space-between; box-sizing: border-box;
  &.placeholder { color: #C9CDD4; }
}
.arrow { color: #86909C; transform: rotate(90deg); }
.textarea {
  width: 100%; min-height: 200rpx; background: #F7F8FA; border: 1.5px solid #E5E6EB; border-radius: 16rpx;
  padding: 20rpx 24rpx; font-size: 28rpx; color: #1D2129; box-sizing: border-box; line-height: 1.6;
}
.char-count { font-size: 22rpx; color: #86909C; text-align: right; display: block; margin-top: 8rpx; }

/* 底部提交栏 */
.bottom-bar {
  flex-shrink: 0;
  padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F2F3F5;
}
.primary-btn {
  width: 100%; height: 92rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF); color: #fff; font-size: 30rpx; font-weight: 600;
  border: none; border-radius: 50rpx;
  display: flex; align-items: center; justify-content: center; gap: 8rpx;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);
  &:active { opacity: .9; transform: scale(.98); }
  &[disabled] { background: #C9CDD4; box-shadow: none; }
}

/* 投诉列表 */
.list { padding: 20rpx 24rpx; }
.list-card {
  background: #fff; border-radius: 28rpx; padding: 28rpx; margin-bottom: 20rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
  &:active { transform: scale(.98); }
}
.list-card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12rpx; }
.type-tag { font-size: 22rpx; color: #165DFF; background: #E8F3FF; padding: 6rpx 16rpx; border-radius: 8rpx; }
.status { font-size: 22rpx; padding: 6rpx 16rpx; border-radius: 20rpx; }
.s-pending    { background: #FFF3E8; color: #FF7D00; }
.s-processing { background: #E8F3FF; color: #165DFF; }
.s-resolved   { background: #E8FFEA; color: #00B42A; }
.list-card-title { font-size: 30rpx; font-weight: 600; color: #1D2129; display: block; margin-bottom: 8rpx; }
.list-card-body  { font-size: 26rpx; color: #4E5969; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; line-height: 1.5; }
.list-card-foot  { display: flex; justify-content: space-between; align-items: center; margin-top: 16rpx; padding-top: 16rpx; border-top: 1rpx solid #F2F3F5; }
.time { font-size: 22rpx; color: #86909C; }
.reply { font-size: 22rpx; color: #165DFF; }

.safe-bottom { height: 24rpx; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12rpx); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
