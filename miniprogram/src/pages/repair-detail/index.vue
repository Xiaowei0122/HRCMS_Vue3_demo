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
        <view class="status-banner" :class="'banner-' + statusKey(detail.status)">
          <text class="banner-status">{{ detail.status || '待接单' }}</text>
          <text class="banner-no">工单号：{{ detail.orderNo }}</text>
        </view>

        <!-- 工单信息 -->
        <view class="info-card">
          <view class="card-title-row">
            <SvgIcon name="clipboard" :size="32" />
            <text class="card-title">工单信息</text>
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
              <text class="item-value">{{ detail.contact }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">联系电话</text>
              <text class="item-value mono">{{ detail.phone }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">设备类型</text>
              <text class="item-value">{{ detail.deviceType || '未指定' }}</text>
            </view>
            <view class="info-item">
              <text class="item-label">紧急程度</text>
              <text class="urgency-tag" :class="'urgency-' + priorityKey(detail.priority)">
                {{ detail.priority || '普通' }}
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

        <!-- 服务信息（工程师接单后显示） -->
        <view class="info-card" v-if="detail.engineer">
          <view class="card-title-row">
            <SvgIcon name="wrench" :size="32" />
            <text class="card-title">服务信息</text>
          </view>
          <view class="info-grid">
            <view class="info-item">
              <text class="item-label">服务工程师</text>
              <view class="item-value engineer-value">
                <SvgIcon name="hardHat" :size="28" />
                <text>{{ detail.engineer }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 处理进度 时间轴 -->
        <view class="info-card">
          <view class="card-title-row">
            <SvgIcon name="clock" :size="32" />
            <text class="card-title">处理进度</text>
          </view>
          <TimeLine :items="detail.progress || defaultProgress" />
        </view>

        <!-- 工程师操作按钮 -->
        <view class="action-bar" v-if="authStore.isEngineer && detail.status !== STATUS.DONE">
          <!-- 待接单：接单按钮 -->
          <button
            v-if="detail.status === STATUS.PENDING"
            class="btn-accept"
            @click="handleAccept"
          >
            接 单
          </button>

          <!-- 处理中：添加进度 + 完成 + 转单 -->
          <view v-if="detail.status === STATUS.PROCESSING" class="action-col">
            <button class="btn-add-progress" @click="showProgressForm = !showProgressForm">
              {{ showProgressForm ? '收起' : '添加进度' }}
            </button>

            <view v-if="showProgressForm" class="progress-form">
              <textarea
                class="progress-input"
                v-model="progressInput"
                placeholder="填写当前处理进度，如：已上门检测，等待配件到货"
                maxlength="200"
                :auto-height="true"
              />
              <button class="btn-progress-submit" :disabled="submittingProgress" @click="submitProgress">
                {{ submittingProgress ? '提交中...' : '提交进度' }}
              </button>
            </view>

            <view class="action-row">
              <button class="btn-transfer" @click="showTransferPopup = true">
                转单申请
              </button>
              <button class="btn-complete" @click="handleComplete">
                标记完成
              </button>
            </view>
          </view>
        </view>

        <!-- 现场图片 -->
        <view class="info-card" v-if="detail.images && detail.images.length">
          <view class="card-title-row">
            <SvgIcon name="image" :size="32" />
            <text class="card-title">现场照片</text>
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

    <!-- 接单排期弹窗 -->
    <view class="popup-overlay" v-if="showAcceptPopup" @click="showAcceptPopup = false">
      <view class="popup-card" @click.stop>
        <text class="popup-title">接单排期</text>
        <text class="popup-desc">选择排期时间后确认接单</text>

        <view class="accept-date-row">
          <text class="accept-label">排期日期</text>
          <picker mode="date" :value="acceptDate" @change="onAcceptDateChange">
            <view class="accept-date-value">{{ acceptDate }}</view>
          </picker>
        </view>

        <view class="slot-grid">
          <view
            v-for="s in TIME_SLOTS"
            :key="s.key"
            class="slot-chip"
            :class="{ selected: acceptSlot === s.key }"
            @click="acceptSlot = s.key"
          >
            <text class="slot-chip-label">{{ s.label }}</text>
            <text class="slot-chip-range">{{ s.range }}</text>
          </view>
        </view>

        <view class="popup-actions">
          <button class="btn-cancel" @click="showAcceptPopup = false">取消</button>
          <button class="btn-confirm" @click="confirmAccept" :disabled="accepting">
            {{ accepting ? '接单中...' : '确认接单' }}
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
import SvgIcon from '@/components/SvgIcon.vue'
import TimeLine from '@/components/TimeLine.vue'
import { STATUS, statusKey, priorityKey, TIME_SLOTS } from '@/utils/repair-status'

const route = useRoute()
const authStore = useAuthStore()
const repairStore = useRepairStore()

const loading = ref(true)
const detail = ref(null)
const showTransferPopup = ref(false)
const selectedEngineer = ref('')
const engineers = ref([])

// 接单排期（选择时间）
const showAcceptPopup = ref(false)
const acceptDate = ref('')
const acceptSlot = ref('AM1')
const accepting = ref(false)

// 添加进度
const showProgressForm = ref(false)
const progressInput = ref('')
const submittingProgress = ref(false)

// 今天日期（接单默认排期）
const todayStr = () => {
  const d = new Date()
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

// 默认空进度
const defaultProgress = computed(() => {
  if (!detail.value) return []
  return [{
    time: detail.value.createTime,
    node: '工单已提交',
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

// 工程师接单：先选择排期时间，再确认
const handleAccept = () => {
  acceptDate.value = todayStr()
  acceptSlot.value = 'AM1'
  showAcceptPopup.value = true
}

const confirmAccept = async () => {
  if (!acceptSlot.value) {
    uni.showToast({ title: '请选择时段', icon: 'none' })
    return
  }
  accepting.value = true
  try {
    await repairStore.acceptOrder(detail.value._id || detail.value.id, {
      date: acceptDate.value,
      timeSlot: acceptSlot.value
    })
    uni.showToast({ title: '接单成功', icon: 'success' })
    showAcceptPopup.value = false
    setTimeout(() => loadDetail(), 500)
  } catch {
    // handled
  } finally {
    accepting.value = false
  }
}

const onAcceptDateChange = (e) => {
  acceptDate.value = e.detail.value
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

// 添加进度
const submitProgress = async () => {
  const node = progressInput.value.trim()
  if (!node) {
    uni.showToast({ title: '请输入进度内容', icon: 'none' })
    return
  }
  submittingProgress.value = true
  try {
    await repairStore.addProgress(detail.value._id || detail.value.id, { node, status: 'doing' })
    uni.showToast({ title: '进度已添加', icon: 'success' })
    progressInput.value = ''
    showProgressForm.value = false
    setTimeout(() => loadDetail(), 500)
  } catch { /* handled */ } finally {
    submittingProgress.value = false
  }
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
  background: #F8FAFC;
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
  color: #64748B;
}

/* 状态横幅 */
.status-banner {
  padding: 40rpx 32rpx;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
  align-items: center;

  &.banner-pending    { background: linear-gradient(135deg, #F59E0B, #D97706); }
  &.banner-processing { background: linear-gradient(135deg, #0369A1, #0284C7); }
  &.banner-done       { background: linear-gradient(135deg, #16A34A, #15803D); }
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
  border-radius: 14rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.06);
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 16rpx;
  padding-bottom: 12rpx;
  border-bottom: 1px solid #E2E8F0;
}

.card-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #020617;
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
  color: #64748B;
  display: block;
  margin-bottom: 4rpx;
}

.item-value {
  font-size: 26rpx;
  color: #334155;

  &.mono { font-family: monospace; }
  &.desc-text { line-height: 1.6; font-size: 28rpx; }
}

.engineer-value {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.urgency-tag {
  font-size: 22rpx;
  padding: 2rpx 12rpx;
  border-radius: 4rpx;
  display: inline-block;

  &.urgency-urgent { background: #FEE2E2; color: #DC2626; }
  &.urgency-normal { background: #FEF3C7; color: #D97706; }
  &.urgency-low    { background: #DCFCE7; color: #16A34A; }
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
  color: #64748B;
}

.fee-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #0F172A;
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

.action-col {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.btn-add-progress {
  width: 100%;
  height: 80rpx;
  background: #FFFFFF;
  color: #0369A1;
  font-size: 28rpx;
  font-weight: 600;
  border: 1px solid #0369A1;
  border-radius: 50rpx;
  text-align: center;
  line-height: 80rpx;

  &:active { opacity: 0.85; }
}

.progress-form {
  background: #F8FAFC;
  border-radius: 12rpx;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.progress-input {
  width: 100%;
  min-height: 120rpx;
  background: #FFFFFF;
  border-radius: 10rpx;
  padding: 16rpx;
  font-size: 26rpx;
  color: #334155;
  box-sizing: border-box;
  border: 1px solid #E2E8F0;
}

.btn-progress-submit {
  width: 100%;
  height: 76rpx;
  background: #0F172A;
  color: #FFFFFF;
  font-size: 26rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 76rpx;

  &:active { opacity: 0.9; }
  &[disabled] { background: #94A3B8; }
}

.btn-accept {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #0369A1, #0284C7);
  color: #FFFFFF;
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
  color: #0369A1;
  border: 1px solid #0369A1;
}

.btn-complete {
  background: linear-gradient(135deg, #16A34A, #15803D);
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
  color: #020617;
  text-align: center;
}

.popup-desc {
  font-size: 24rpx;
  color: #64748B;
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
  border-radius: 10rpx;
  margin-bottom: 8rpx;
  background: #F1F5F9;

  &.selected {
    background: #F0F9FF;
    border: 1px solid #0369A1;
  }
}

.eng-name { font-size: 28rpx; color: #334155; font-weight: 500; }
.eng-phone { font-size: 24rpx; color: #64748B; }

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

.btn-cancel { background: #F1F5F9; color: #334155; }
.btn-confirm { background: #0F172A; color: #FFFFFF; }
.btn-confirm[disabled] { background: #94A3B8; }

/* 接单排期弹窗 */
.accept-date-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 16rpx;
  background: #F1F5F9;
  border-radius: 10rpx;
  margin-bottom: 16rpx;
}

.accept-label {
  font-size: 26rpx;
  color: #64748B;
}

.accept-date-value {
  font-size: 28rpx;
  color: #0F172A;
  font-weight: 600;
}

.slot-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.slot-chip {
  width: calc((100% - 32rpx) / 3);
  box-sizing: border-box;
  padding: 16rpx 8rpx;
  border-radius: 10rpx;
  background: #F1F5F9;
  border: 1px solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;

  &.selected {
    background: #F0F9FF;
    border-color: #0369A1;
  }
}

.slot-chip-label {
  font-size: 26rpx;
  color: #334155;
  font-weight: 600;
}

.slot-chip-range {
  font-size: 20rpx;
  color: #64748B;
}

.safe-bottom { height: 60rpx; }

@keyframes fadeIn  { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
</style>
