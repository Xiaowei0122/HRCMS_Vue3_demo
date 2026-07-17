<!--
  工单详情页面（所有角色共用）
  - 工单信息（工单号、创建时间）
  - 服务信息（服务类型、产品、工程师）— 工程师接单后填写
  - 费用明细（服务费用）— 工程师端填写
  - 处理进度时间轴
  - 角色相关操作按钮（接单/转单/完成）
-->
<template>
  <view class="detail-page">
    <scroll-view scroll-y class="page-scroll">
      <!-- 加载中 -->
      <view v-if="loading" class="loading-box">
        <text class="loading-text">加载中...</text>
      </view>

      <template v-if="detail && !loading">
        <!-- 状态横幅 -->
        <view class="status-banner" :class="'banner-' + (detail.status || 'pending')">
          <text class="banner-status">{{ statusMap[detail.status] || '待处理' }}</text>
          <text class="banner-no">工单号：{{ detail.orderNo }}</text>
        </view>

        <!-- 工单信息 -->
        <view class="info-card">
          <view class="card-title-row">
            <text class="card-title">📋 工单信息</text>
          </view>
          <view class="info-grid">
            <view class="info-item">
              <text class="item-label">工单号</text>
              <text class="item-value mono">{{ detail.orderNo }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">创建时间</text>
              <text class="item-value">{{ formatTime(detail.createTime) }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">报修单位</text>
              <text class="item-value">{{ detail.company }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">联系人</text>
              <text class="item-value">{{ detail.contactName }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">联系电话</text>
              <text class="item-value mono">{{ detail.contactPhone }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">设备类型</text>
              <text class="item-value">{{ detail.deviceType || '未指定' }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">紧急程度</text>
              <text class="urgency-tag" :class="'urgency-' + (detail.urgency || 'normal')">
                {{ urgencyMap[detail.urgency] || '一般' }}
              </text>
            </view>
            <view class="info-item full-width">
              <text class="item-label">用户地址</text>
              <text class="item-value">{{ detail.address }}</text>
            </view>
            <view class="info-item full-width">
              <text class="item-label">基本情况</text>
              <text class="item-value desc-text">{{ detail.description }}</text>
            </view>
          </view>
        </view>

        <!-- 服务信息 -->
        <view class="info-card" v-if="detail.serviceType || detail.engineerName">
          <view class="card-title-row">
            <text class="card-title">🔧 服务信息</text>
          </view>
          <view class="info-grid">
            <view class="info-item" v-if="detail.serviceType">
              <text class="item-label">服务类型</text>
              <text class="item-value">{{ detail.serviceType }}</text>
            </view>
            <view class="info-item" v-if="detail.serviceProduct">
              <text class="item-label">服务产品</text>
              <text class="item-value">{{ detail.serviceProduct }}</text>
            </view>
            <view class="info-item" v-if="detail.engineerName">
              <text class="item-label">服务工程师</text>
              <text class="item-value">👨‍🔧 {{ detail.engineerName }}</text>
            </view>
          </view>
        </view>

        <!-- 费用明细 -->
        <view class="info-card" v-if="detail.serviceFee !== undefined">
          <view class="card-title-row">
            <text class="card-title">💰 费用明细</text>
          </view>
          <view class="fee-row">
            <text class="fee-label">服务费用</text>
            <text class="fee-value">¥{{ Number(detail.serviceFee).toFixed(2) }}</text>
          </view>
        </view>

        <!-- 处理进度 时间轴 -->
        <view class="info-card">
          <view class="card-title-row">
            <text class="card-title">📌 处理进度</text>
          </view>
          <TimeLine :items="detail.progress || defaultProgress" />
        </view>

        <!-- 工程师操作按钮 -->
        <view class="action-bar" v-if="authStore.isEngineer && detail.status !== 'done'">
          <!-- 待接单：接单按钮 -->
          <button
            v-if="detail.status === 'pending'"
            class="btn-accept"
            @click="handleAccept"
          >
            接 单
          </button>

          <!-- 处理中：完成 + 转单 -->
          <view v-if="detail.status === 'processing'" class="action-row">
            <button class="btn-transfer" @click="showTransferPopup = true">
              转单申请
            </button>
            <button class="btn-complete" @click="handleComplete">
              标记完成
            </button>
          </view>
        </view>

        <!-- 现场图片 -->
        <view class="info-card" v-if="detail.images && detail.images.length">
          <view class="card-title-row">
            <text class="card-title">🖼️ 现场照片</text>
          </view>
          <view class="image-grid">
            <img
              v-for="(img, idx) in detail.images"
              :key="idx"
              :src="img"
              class="detail-image"
              style="object-fit: cover"
              @click="previewDetailImage(idx)"
            />
          </view>
        </view>
      </template>

      <view class="safe-bottom"></view>
    </scroll-view>

    <!-- 转单弹窗 -->
    <view class="popup-overlay" v-if="showTransferPopup" @click="showTransferPopup = false">
      <view class="popup-card" @click.stop>
        <text class="popup-title">转单申请</text>
        <text class="popup-desc">选择要转给哪位工程师</text>

        <scroll-view scroll-y class="engineer-list">
          <view
            v-for="eng in engineers"
            :key="eng._id || eng.id"
            class="engineer-option"
            :class="{ selected: selectedEngineer === (eng._id || eng.id) }"
            @click="selectedEngineer = eng._id || eng.id"
          >
            <text class="eng-name">{{ eng.name }}</text>
            <text class="eng-phone">{{ eng.phone }}</text>
          </view>
        </scroll-view>

        <view class="popup-actions">
          <button class="btn-cancel" @click="showTransferPopup = false">取消</button>
          <button class="btn-confirm" @click="handleTransfer" :disabled="!selectedEngineer">
            确认转单
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRepairStore } from '@/stores/repair'
import TimeLine from '@/components/TimeLine.vue'

const route = useRoute()
const authStore = useAuthStore()
const repairStore = useRepairStore()

const loading = ref(true)
const detail = ref(null)
const showTransferPopup = ref(false)
const selectedEngineer = ref('')
const engineers = ref([])

const statusMap = { pending: '待处理', processing: '处理中', done: '已完成' }
const urgencyMap = { urgent: '紧急', normal: '一般', low: '不急' }

// 默认空进度
const defaultProgress = computed(() => {
  if (!detail.value) return []
  return [{
    time: detail.value.createTime,
    content: '工单已提交',
    status: 'done'
  }]
})

const formatTime = (t) => {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const previewDetailImage = (idx) => {
  uni.previewImage({
    urls: detail.value.images,
    current: idx
  })
}

// 工程师接单
const handleAccept = () => {
  uni.showModal({
    title: '确认接单',
    content: '接单后工单将进入"我的工单"列表',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await repairStore.acceptOrder(detail.value._id || detail.value.id)
        uni.showToast({ title: '接单成功', icon: 'success' })
        setTimeout(() => loadDetail(), 500)
      } catch { /* handled */ }
    }
  })
}

// 完成工单
const handleComplete = () => {
  uni.showModal({
    title: '确认完成',
    content: '确认将此工单标记为已完成？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await repairStore.completeOrder(detail.value._id || detail.value.id)
        uni.showToast({ title: '工单已完成', icon: 'success' })
        setTimeout(() => loadDetail(), 500)
      } catch { /* handled */ }
    }
  })
}

// 转单
const handleTransfer = async () => {
  if (!selectedEngineer.value) return
  try {
    await repairStore.transferOrder(detail.value._id || detail.value.id, {
      targetEngineerId: selectedEngineer.value
    })
    uni.showToast({ title: '转单申请已提交', icon: 'success' })
    showTransferPopup.value = false
  } catch { /* handled */ }
}

const loadDetail = async () => {
  loading.value = true
  try {
    // 通过 Vue Router 获取 URL 参数
    const id = route.query.id || route.params.id

    if (!id) {
      uni.showToast({ title: '缺少工单ID', icon: 'none' })
      return
    }

    detail.value = await repairStore.fetchDetail(id)

    // 如果是工程师，预载工程师列表（用于转单）
    if (authStore.isEngineer) {
      engineers.value = await repairStore.fetchEngineers()
    }
  } catch {
    // handled
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background: #F7F7F7;
}

.page-scroll {
  height: 100vh;
}

.loading-box {
  display: flex;
  justify-content: center;
  padding: 100rpx 0;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}

/* 状态横幅 */
.status-banner {
  padding: 40rpx 32rpx;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
  align-items: center;

  &.banner-pending    { background: linear-gradient(135deg, #FF9800, #F57C00); }
  &.banner-processing { background: linear-gradient(135deg, #2196F3, #1976D2); }
  &.banner-done       { background: linear-gradient(135deg, #4CAF50, #388E3C); }
}

.banner-status {
  font-size: 36rpx;
  font-weight: 700;
}

.banner-no {
  font-size: 24rpx;
  opacity: 0.85;
  margin-top: 8rpx;
  font-family: monospace;
}

/* 信息卡片 */
.info-card {
  margin: 16rpx 24rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
}

.card-title-row {
  margin-bottom: 16rpx;
  padding-bottom: 12rpx;
  border-bottom: 1px solid #F0F0F0;
}

.card-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #222;
}

.info-grid {
  display: flex;
  flex-wrap: wrap;
}

.info-item {
  width: 50%;
  padding: 8rpx 0;

  &.full-width { width: 100%; }
}

.item-label {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 4rpx;
}

.item-value {
  font-size: 26rpx;
  color: #333;

  &.mono { font-family: monospace; }
  &.desc-text { line-height: 1.6; font-size: 28rpx; }
}

.urgency-tag {
  font-size: 22rpx;
  padding: 2rpx 12rpx;
  border-radius: 4rpx;
  display: inline-block;

  &.urgency-urgent { background: #FFEBEE; color: #C62828; }
  &.urgency-normal { background: #FFF8E1; color: #F57F17; }
  &.urgency-low    { background: #E8F5E9; color: #2E7D32; }
}

/* 费用 */
.fee-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8rpx 0;
}

.fee-label {
  font-size: 26rpx;
  color: #999;
}

.fee-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #D32223;
}

/* 图片 */
.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.detail-image {
  width: 200rpx;
  height: 200rpx;
  border-radius: 8rpx;
}

/* 工程师操作栏 */
.action-bar {
  margin: 16rpx 24rpx;
}

.btn-accept {
  width: 100%;
  height: 88rpx;
  background: #2196F3;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 88rpx;

  &:active { opacity: 0.85; }
}

.action-row {
  display: flex;
  gap: 16rpx;
}

.btn-transfer, .btn-complete {
  flex: 1;
  height: 88rpx;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 88rpx;
}

.btn-transfer {
  background: #FFFFFF;
  color: #FF9800;
  border: 1px solid #FF9800;
}

.btn-complete {
  background: #4CAF50;
  color: #FFFFFF;
}

/* 转单弹窗 */
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.25s ease;
}

.popup-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #222;
  text-align: center;
}

.popup-desc {
  font-size: 24rpx;
  color: #999;
  text-align: center;
  margin: 8rpx 0 20rpx;
}

.engineer-list {
  max-height: 400rpx;
}

.engineer-option {
  display: flex;
  justify-content: space-between;
  padding: 20rpx 16rpx;
  border-radius: 12rpx;
  margin-bottom: 8rpx;
  background: #F7F7F7;

  &.selected {
    background: #FFF0F0;
    border: 1px solid #D32223;
  }
}

.eng-name { font-size: 28rpx; color: #333; font-weight: 500; }
.eng-phone { font-size: 24rpx; color: #999; }

.popup-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 24rpx;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  border-radius: 50rpx;
  line-height: 80rpx;
  text-align: center;
  border: none;
}

.btn-cancel { background: #F7F7F7; color: #666; }
.btn-confirm { background: #D32223; color: #FFFFFF; }
.btn-confirm[disabled] { background: #CCCCCC; }

.safe-bottom { height: 60rpx; }

@keyframes fadeIn  { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
</style>
