<!--
  投诉建议页面
  子板块：一键投诉 + 我的投诉
-->
<template>
  <view class="complaint-page">
    <!-- 子板块切换 -->
    <view class="sub-tabs">
      <view
        class="sub-tab"
        :class="{ active: activeTab === 'submit' }"
        @click="activeTab = 'submit'"
      >
        ✉️ 一键投诉
      </view>
      <view
        class="sub-tab"
        :class="{ active: activeTab === 'my' }"
        @click="switchToMy"
      >
        📋 我的投诉
      </view>
    </view>

    <scroll-view scroll-y class="page-scroll">
      <!-- ====== 一键投诉 ====== -->
      <template v-if="activeTab === 'submit'">
        <view class="form-card">
          <text class="form-title">提交投诉建议</text>
          <text class="form-desc">如对我们的服务有任何意见或建议，请在此反馈</text>

          <view class="form-group">
            <text class="form-label">投诉类型</text>
            <select class="form-picker" :class="{ placeholder: !form.type }" @change="onTypeChange">
              <option value="" disabled selected v-if="!form.type">请选择投诉类型</option>
              <option v-for="(t, idx) in complaintTypes" :key="t" :value="idx">{{ t }}</option>
            </select>
          </view>

          <view class="form-group">
            <text class="form-label">投诉标题 <text class="required">*</text></text>
            <input
              class="form-input"
              v-model="form.title"
              placeholder="简要描述您的问题"
              placeholder-style="color: #ccc"
              maxlength="50"
            />
          </view>

          <view class="form-group">
            <text class="form-label">详细内容 <text class="required">*</text></text>
            <textarea
              class="form-textarea"
              v-model="form.content"
              placeholder="请详细描述您遇到的问题或建议..."
              placeholder-style="color: #ccc"
              maxlength="500"
              :auto-height="true"
            />
            <text class="char-count">{{ form.content.length }}/500</text>
          </view>

          <view class="form-group">
            <text class="form-label">联系方式（选填）</text>
            <input
              class="form-input"
              v-model="form.contact"
              placeholder="手机号或邮箱，方便我们回复"
              placeholder-style="color: #ccc"
              maxlength="50"
            />
          </view>

          <button
            class="btn-submit"
            :class="{ 'btn-loading': submitting }"
            :disabled="submitting"
            @click="handleSubmit"
          >
            {{ submitting ? '提交中...' : '提交投诉' }}
          </button>
        </view>
      </template>

      <!-- ====== 我的投诉 ====== -->
      <template v-else>
        <view v-if="myComplaints.length > 0" class="complaint-list">
          <view
            v-for="item in myComplaints"
            :key="item._id || item.id"
            class="complaint-card"
          >
            <view class="card-header">
              <text class="complaint-type">{{ item.type || '投诉' }}</text>
              <text class="complaint-status" :class="'c-status-' + item.status">
                {{ item.status === 'resolved' ? '已处理' : item.status === 'processing' ? '处理中' : '待处理' }}
              </text>
            </view>
            <text class="complaint-title">{{ item.title }}</text>
            <text class="complaint-content">{{ item.content }}</text>
            <view class="card-footer">
              <text class="complaint-time">{{ formatTime(item.createTime) }}</text>
              <text class="complaint-reply" v-if="item.reply">查看回复 →</text>
            </view>
          </view>
        </view>

        <EmptyState
          v-else
          icon="✉️"
          text="暂无投诉记录"
          sub-text="提交的投诉将在这里显示处理进度"
        />
      </template>
    </scroll-view>

    <!-- 自定义 TabBar -->
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post } from '@/utils/request'
import CustomTabBar from '@/components/CustomTabBar.vue'
import EmptyState from '@/components/EmptyState.vue'

const activeTab = ref('submit')
const submitting = ref(false)
const myComplaints = ref([])

const complaintTypes = ['服务态度', '维修质量', '响应速度', '收费问题', '其他建议']

const form = ref({
  type: '',
  title: '',
  content: '',
  contact: ''
})

const onTypeChange = (e) => {
  form.value.type = complaintTypes[parseInt(e.target.value)]
}

const handleSubmit = async () => {
  if (!form.value.title.trim()) {
    uni.showToast({ title: '请填写投诉标题', icon: 'none' })
    return
  }
  if (!form.value.content.trim()) {
    uni.showToast({ title: '请填写详细内容', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await post('/complaints', {
      type: form.value.type,
      title: form.value.title.trim(),
      content: form.value.content.trim(),
      contact: form.value.contact.trim()
    })

    uni.showToast({ title: '投诉提交成功', icon: 'success' })
    setTimeout(() => {
      form.value = { type: '', title: '', content: '', contact: '' }
    }, 500)
  } catch { /* handled */ }
  finally { submitting.value = false }
}

const loadMyComplaints = async () => {
  try {
    const res = await get('/complaints/my')
    myComplaints.value = Array.isArray(res) ? res : (res?.records || [])
  } catch { /* handled */ }
}

const switchToMy = () => {
  activeTab.value = 'my'
  loadMyComplaints()
}

const formatTime = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
}

onMounted(() => {
  // 默认展示"一键投诉"
})
</script>

<style lang="scss" scoped>
.complaint-page {
  min-height: 100vh;
  background: #F7F7F7;
  display: flex;
  flex-direction: column;
  padding-bottom: 140rpx;
}

.sub-tabs {
  display: flex;
  background: #FFFFFF;
  padding: 12rpx 24rpx;
  gap: 16rpx;
}

.sub-tab {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  font-size: 26rpx;
  color: #666;
  background: #F7F7F7;
  border-radius: 8rpx;
  transition: all 0.25s;

  &.active { background: #D32223; color: #FFFFFF; font-weight: 600; }
}

.page-scroll { flex: 1; }

/* 投诉表单 */
.form-card {
  margin: 16rpx 24rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
}

.form-title { font-size: 32rpx; font-weight: 700; color: #222; display: block; }
.form-desc  { font-size: 24rpx; color: #999; margin-top: 8rpx; margin-bottom: 28rpx; display: block; }

.form-group { margin-bottom: 24rpx; }
.form-label { font-size: 26rpx; color: #333; font-weight: 500; margin-bottom: 8rpx; display: block; }
.required   { color: #D32223; }

.form-input {
  width: 100%; height: 80rpx;
  background: #F7F7F7; border-radius: 12rpx;
  padding: 0 20rpx; font-size: 28rpx; color: #333;
  box-sizing: border-box;
}

.form-picker {
  width: 100%; height: 80rpx;
  background: #F7F7F7; border-radius: 12rpx;
  padding: 0 20rpx; font-size: 28rpx; color: #333;
  display: flex; align-items: center; justify-content: space-between;
  box-sizing: border-box;
  &.placeholder { color: #CCC; }
}

.picker-arrow { font-size: 20rpx; color: #999; }

.form-textarea {
  width: 100%; min-height: 200rpx;
  background: #F7F7F7; border-radius: 12rpx;
  padding: 20rpx; font-size: 28rpx; color: #333;
  box-sizing: border-box;
}

.char-count { font-size: 22rpx; color: #ccc; text-align: right; display: block; margin-top: 6rpx; }

.btn-submit {
  width: 100%; height: 88rpx; line-height: 88rpx;
  background: #D32223; color: #FFFFFF;
  font-size: 30rpx; font-weight: 600;
  border: none; border-radius: 50rpx; text-align: center;
  &:active { opacity: 0.85; transform: scale(0.97); }
  &[disabled] { background: #CCCCCC; }
}

/* 我的投诉列表 */
.complaint-list { padding: 16rpx 24rpx; }

.complaint-card {
  background: #FFFFFF; border-radius: 16rpx;
  padding: 24rpx; margin-bottom: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12rpx;
}

.complaint-type {
  font-size: 22rpx; color: #D32223;
  background: #FFF0F0; padding: 4rpx 14rpx; border-radius: 4rpx;
}

.complaint-status {
  font-size: 22rpx; padding: 4rpx 14rpx; border-radius: 20rpx;
  &.c-status-pending    { background: #FFF3E0; color: #E65100; }
  &.c-status-processing { background: #E3F2FD; color: #1565C0; }
  &.c-status-resolved   { background: #E8F5E9; color: #2E7D32; }
}

.complaint-title {
  font-size: 28rpx; font-weight: 600; color: #222;
  display: block; margin-bottom: 8rpx;
}

.complaint-content {
  font-size: 26rpx; color: #666;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2;
  overflow: hidden; line-height: 1.5;
}

.card-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 12rpx; padding-top: 12rpx; border-top: 1px solid #F0F0F0;
}

.complaint-time { font-size: 22rpx; color: #ccc; }
.complaint-reply { font-size: 22rpx; color: #D32223; }
</style>
