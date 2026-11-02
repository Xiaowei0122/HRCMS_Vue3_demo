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
    <PageNavbar title="工单详情" transparent :back-url="fromSchedule ? '/pages/public/home/index' : ''" :scrolled="scrolled" />
    <scroll-view scroll-y class="page-scroll" @scroll="onScroll">
      <!-- 加载中 -->
      <view v-if="loading" class="loading-box">
        <text class="loading-text">加载中...</text>
      </view>

      <template v-if="detail && !loading">
        <!-- 状态横幅（顶部让位给透明 Navbar） -->
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
              <text class="item-label">工单类型</text>
              <text class="item-value">{{ detail.workOrderType || '售后上门' }}</text>
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
            <view class="info-item full-width" v-if="detail.isRework">
              <text class="item-label">返修信息</text>
              <text class="item-value desc-text">返修自：{{ detail.reworkOf }} · {{ detail.reworkReason || '其他' }}</text>
            </view>
          </view>
        </view>

        <!-- 服务信息（工程师接单后显示） -->
        <view class="info-card" v-if="detail.engineer">
          <view class="card-title-row">
            <SvgIcon name="wrench" :size="32" color="#FF7D00" />
            <text class="card-title">服务信息</text>
            <view v-if="detail.escalated" class="escalated-badge">已加急</view>
          </view>
          <view class="schedule-line" v-if="scheduledText">
            <SvgIcon name="clock" :size="28" color="#165DFF" />
            <text class="schedule-text">预计 {{ scheduledText }} 上门处理</text>
          </view>
          <EngineerCard v-if="serviceEngineer" :engineer="serviceEngineer" :index="0" flat />
        </view>

        <!-- 费用信息（已填时展示） -->
        <view class="info-card" v-if="detail.fee">
          <view class="card-title-row">
            <SvgIcon name="currencyDollar" :size="32" />
            <text class="card-title">费用信息</text>
          </view>
          <view class="fee-row">
            <text class="fee-label">费用金额</text>
            <text class="fee-value">¥{{ detail.fee.amount }}</text>
          </view>
          <view class="fee-row">
            <text class="fee-label">费用方式</text>
            <text class="fee-meta">{{ feeModeLabel(detail.fee.mode) }}</text>
          </view>
          <view class="fee-row" v-if="detail.fee.paidBy">
            <text class="fee-label">支付方</text>
            <text class="fee-meta">{{ detail.fee.paidBy }}</text>
          </view>
          <view class="fee-row" v-if="detail.fee.note">
            <text class="fee-label">备注</text>
            <text class="fee-meta">{{ detail.fee.note }}</text>
          </view>
        </view>

        <!-- 费用录入（工程师，处理中/待确认） -->
        <view class="info-card" v-if="authStore.isEngineer && (detail.status === STATUS.PROCESSING || detail.status === STATUS.CONFIRMING)">
          <view class="card-title-row">
            <SvgIcon name="currencyDollar" :size="32" />
            <text class="card-title">费用录入</text>
          </view>
          <view class="fee-mode-row">
            <view v-for="m in FEE_MODES" :key="m.key" class="fee-mode-btn" :class="{ on: feeMode === m.key }" @click="feeMode = m.key">{{ m.label }}</view>
          </view>
          <input class="fee-input" v-model="feeAmount" type="digit" placeholder="金额（元）" placeholder-style="color:#C9CDD4" />
          <input class="fee-input" v-model="feePaidBy" placeholder="支付方（选填）" placeholder-style="color:#C9CDD4" maxlength="20" />
          <textarea class="fee-textarea" v-model="feeNote" placeholder="费用说明（选填）" placeholder-style="color:#C9CDD4" maxlength="100" :auto-height="true" />
          <button class="btn-fee-submit" :disabled="submittingFee" @click="submitFee">{{ submittingFee ? '保存中...' : '保存费用' }}</button>
        </view>

        <!-- 处理进度 时间轴 -->
        <view class="info-card">
          <view class="card-title-row">
            <SvgIcon name="clock" :size="32" color="#00B42A" />
            <text class="card-title">处理进度</text>
          </view>
          <TimeLine :items="detail.progress || defaultProgress" />
        </view>

        <!-- 工程师操作按钮 -->
        <view class="action-bar" v-if="authStore.isEngineer && (detail.status === STATUS.PENDING || detail.status === STATUS.RESERVED || detail.status === STATUS.PROCESSING)">
          <!-- 待接单/已预约：接单按钮 -->
          <button
            v-if="detail.status === STATUS.PENDING || detail.status === STATUS.RESERVED"
            class="btn-accept"
            @click="handleAccept"
          >
            接 单
          </button>

          <!-- 处理中：优先处理 + 添加进度 + 完成 + 转单 -->
          <view v-if="detail.status === STATUS.PROCESSING" class="action-col">
            <button class="btn-escalate" @click="openEscalatePopup">
              优先处理
            </button>
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
                完结工单
              </button>
            </view>
            <button class="btn-cancel-order" @click="openCancelPopup">
              取消工单
            </button>
          </view>
        </view>

        <!-- 内部人员（业务/管理员）：预约指派 -->
        <view class="action-bar" v-if="canInitiateReserve">
          <button class="btn-reserve-assign" @click="openReserveAssignPopup">
            预约指派
          </button>
        </view>

        <!-- 转单申请处理 -->
        <view class="info-card" v-if="detail.transferRequest && detail.transferRequest.status === 'pending'">
          <view class="card-title-row">
            <SvgIcon name="clock" :size="32" />
            <text class="card-title">转单申请</text>
          </view>
          <view class="transfer-info">
            <text class="transfer-desc">
              {{ detail.transferRequest.fromEngineer }} → {{ detail.transferRequest.toEngineer }}（待处理）
            </text>
          </view>
          <view class="action-row" v-if="isTransferTarget">
            <button class="btn-transfer" @click="handleAcceptTransfer">接受转单</button>
            <button class="btn-complete" @click="handleRejectTransfer">拒绝转单</button>
          </view>
          <view class="action-row" v-else-if="isTransferInitiator">
            <button class="btn-cancel-transfer" @click="handleCancelTransfer">取消转单申请</button>
          </view>
        </view>

        <!-- 预约指派处理 -->
        <view class="info-card" v-if="reservationReq.status === 'pending'">
          <view class="card-title-row">
            <SvgIcon name="clock" :size="32" color="#722ED1" />
            <text class="card-title">预约指派</text>
          </view>
          <view class="transfer-info">
            <text class="transfer-desc">已向工程师 {{ reservationReq.targetEngineerName }} 发起预约{{ reservePreferredText }}</text>
            <text v-if="reservationReq.note" class="transfer-desc note">备注：{{ reservationReq.note }}</text>
          </view>
          <view class="action-row" v-if="isReserveTarget">
            <button class="btn-transfer" @click="handleAcceptReserve">接受预约</button>
            <button class="btn-complete" @click="openRejectReservePopup">退回预约</button>
          </view>
          <view class="action-row" v-else-if="canCancelReserve">
            <button class="btn-cancel-transfer" @click="handleCancelReserve">取消预约指派</button>
          </view>
        </view>

        <!-- 客户/业务操作按钮 -->
        <view class="action-bar" v-if="authStore.canConfirmRepair">
          <button
            v-if="detail.status === STATUS.CONFIRMING && canConfirm"
            class="btn-confirm-archive"
            :disabled="confirming"
            @click="handleConfirm"
          >
            {{ confirming ? '确认中...' : '确认归档' }}
          </button>
          <button
            v-if="isArchivedStatus(detail.status)"
            class="btn-rework"
            @click="showReworkPopup = true"
          >
            返 修
          </button>
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

    <!-- 接单弹窗（复用组件 · 预约/普通两态） -->
    <AcceptOrderPopup
      v-model="showAcceptPopup"
      :order="detail"
      :mode="acceptPopupMode"
      :confirming="accepting"
      :rejecting="rejecting"
      @confirm="onAcceptConfirm"
      @reject="onAcceptReject"
    />

    <!-- 返修弹窗 -->
    <view class="popup-overlay" v-if="showReworkPopup" @click="showReworkPopup = false">
      <view class="popup-card" @click.stop>
        <text class="popup-title">发起返修</text>
        <text class="popup-desc">选择返修原因，将复制原单生成新的工单</text>

        <view class="rework-reason-row">
          <view
            v-for="r in REWORK_REASONS"
            :key="r"
            class="rework-reason-btn"
            :class="{ on: reworkReason === r }"
            @click="reworkReason = r"
          >
            {{ r }}
          </view>
        </view>

        <textarea
          class="progress-input"
          v-model="reworkNote"
          placeholder="补充说明（选填）"
          maxlength="200"
          :auto-height="true"
        />

        <view class="popup-actions">
          <button class="btn-cancel" @click="showReworkPopup = false">取消</button>
          <button class="btn-confirm" :disabled="submittingRework" @click="submitRework">
            {{ submittingRework ? '提交中...' : '确认返修' }}
          </button>
        </view>
      </view>
    </view>

    <!-- 预约指派弹窗 -->
    <view class="popup-overlay" v-if="showReserveAssignPopup" @click="showReserveAssignPopup = false">
      <view class="popup-card" @click.stop>
        <text class="popup-title">预约指派</text>
        <text class="popup-desc">指定工程师发起预约，待其确认处理时段</text>

        <scroll-view scroll-y class="engineer-list">
          <view
            v-for="eng in engineers"
            :key="eng._id || eng.id"
            class="engineer-option"
            :class="{ selected: reserveTargetEngineer === (eng._id || eng.id) }"
            @click="reserveTargetEngineer = eng._id || eng.id"
          >
            <text class="eng-name">{{ eng.name }}</text>
            <text class="eng-phone">{{ eng.phone }}</text>
          </view>
        </scroll-view>

        <view class="accept-date-row" @click="showReserveDateSheet = true">
          <text class="accept-label">期望日期（选填）</text>
          <text class="accept-date-value">{{ reservePreferredDate || '点击选择' }}</text>
        </view>

        <view class="accept-date-row" @click="showReserveSlotSheet = true">
          <text class="accept-label">期望时段（选填）</text>
          <text class="accept-date-value">{{ reserveSlotLabel }}</text>
        </view>

        <input class="fee-input" v-model="reserveNote" placeholder="备注说明（选填）" placeholder-style="color:#C9CDD4" maxlength="100" />

        <view class="popup-actions">
          <button class="btn-cancel" @click="showReserveAssignPopup = false">取消</button>
          <button class="btn-confirm" :disabled="submittingReserve || !reserveTargetEngineer" @click="submitReserveAssign">
            {{ submittingReserve ? '提交中...' : '确认发起' }}
          </button>
        </view>
      </view>
    </view>

    <!-- 通用原因输入弹窗（拒绝转单 / 退回预约 / 取消工单） -->
    <view class="popup-overlay" v-if="showReasonPopup" @click="showReasonPopup = false">
      <view class="popup-card" @click.stop>
        <text class="popup-title">{{ reasonPopupTitle }}</text>
        <textarea
          class="progress-input"
          v-model="reasonText"
          :placeholder="reasonPopupPlaceholder"
          maxlength="200"
          :auto-height="true"
        />
        <view class="popup-actions">
          <button class="btn-cancel" @click="showReasonPopup = false">取消</button>
          <button class="btn-confirm" :disabled="submittingReason" @click="confirmReason">
            {{ submittingReason ? '提交中...' : '确定' }}
          </button>
        </view>
      </view>
    </view>

    <!-- 日期 / 时段选择 -->
    <DatePickerSheet v-model="showReserveDateSheet" title="选择期望日期" :value="reservePreferredDate" :disable-past="true" @select="onReserveDateSelect" />
    <PickerSheet v-model="showReserveSlotSheet" title="选择期望时段" :options="reserveSlotOptions" :value="reservePreferredSlot" @select="onReserveSlotSelect" />
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRepairStore } from '@/stores/repair'
import SvgIcon from '@/components/SvgIcon.vue'
import PageNavbar from '@/components/PageNavbar.vue'
import TimeLine from '@/components/TimeLine.vue'
import EngineerCard from '@/components/EngineerCard.vue'
import DatePickerSheet from '@/components/DatePickerSheet.vue'
import PickerSheet from '@/components/PickerSheet.vue'
import AcceptOrderPopup from '@/components/AcceptOrderPopup.vue'
import { STATUS, statusKey, priorityKey, TIME_SLOTS, slotLabel, isArchivedStatus, feeModeLabel, FEE_MODES, REWORK_REASONS } from '@/utils/repair-status'
import { useScrollHide } from '@/utils/useScrollHide'

const route = useRoute()
const authStore = useAuthStore()
const repairStore = useRepairStore()

const { scrolled, onScroll } = useScrollHide()

// 从工程师排期进入时，返回键直接回首页（跨级返回）
const fromSchedule = computed(() => route.query.from === 'schedule')

const loading = ref(true)
const detail = ref(null)
const showTransferPopup = ref(false)
const selectedEngineer = ref('')
const engineers = ref([])

// 当前用户 id（用于判断转单申请的发起人/接收人）
const myId = computed(() => authStore.userInfo?.id || authStore.userInfo?._id || '')
const isTransferTarget = computed(() => {
  const tr = detail.value?.transferRequest
  return !!tr && tr.status === 'pending' && tr.toEngineerId && String(tr.toEngineerId) === String(myId.value)
})
const isTransferInitiator = computed(() => {
  const tr = detail.value?.transferRequest
  return !!tr && tr.status === 'pending' && tr.fromEngineerId && String(tr.fromEngineerId) === String(myId.value)
})

// 预约指派（后端 _create_or_all，仅内部人员，排除 normal）
const reservationReq = computed(() => detail.value?.reservationRequest || {})
const reservePreferredText = computed(() => {
  const req = reservationReq.value
  if (!req.preferredDate) return ''
  let s = `，期望 ${req.preferredDate}`
  if (req.preferredTimeSlot) s += ` ${req.preferredTimeSlot}`
  return s
})
const isReserveTarget = computed(() => {
  const req = reservationReq.value
  return req.status === 'pending' && req.targetEngineerId && String(req.targetEngineerId) === String(myId.value)
})
const canInitiateReserve = computed(() =>
  detail.value?.status === STATUS.PENDING && authStore.isInternalUser && authStore.hasPerm('repair:create', 'repair:all')
)
const canCancelReserve = computed(() =>
  reservationReq.value.status === 'pending' && authStore.isInternalUser && authStore.hasPerm('repair:create', 'repair:all')
)

// 确认归档：仅管理员或工单指定确认人（confirmUserId === 本人）
const canConfirm = computed(() =>
  authStore.isAdmin || (detail.value?.confirmUserId && String(detail.value.confirmUserId) === String(myId.value))
)

// 接单（复用 AcceptOrderPopup）—— 自助接单 / 接受转单 / 接受预约 三种确认
const showAcceptPopup = ref(false)
const acceptMode = ref('accept') // accept | transfer | reserve
const accepting = ref(false)
const rejecting = ref(false)

// 预约工单（已预约 + 具体时段）走「预约接单」态；其余（待接单 / 转单 / 预约指派）走「普通接单」态
const acceptPopupMode = computed(() => {
  if (acceptMode.value !== 'accept') return 'normal'
  const d = detail.value || {}
  return (d.status === STATUS.RESERVED && d.preferredDate && d.preferredTimeSlot && d.preferredTimeSlot !== '全天')
    ? 'reserve' : 'normal'
})

// 添加进度
const showProgressForm = ref(false)
const progressInput = ref('')
const submittingProgress = ref(false)

// 费用录入（工程师）
const feeMode = ref('agreed')
const feeAmount = ref('')
const feeNote = ref('')
const feePaidBy = ref('')
const submittingFee = ref(false)

// 确认归档 / 返修（客户/业务）
const confirming = ref(false)
const showReworkPopup = ref(false)
const reworkReason = ref('故障未解决')
const reworkNote = ref('')
const submittingRework = ref(false)

// 预约指派（业务/管理员发起，工程师确认时段）
const showReserveAssignPopup = ref(false)
const showReserveDateSheet = ref(false)
const showReserveSlotSheet = ref(false)
const reserveTargetEngineer = ref('')
const reservePreferredDate = ref('')
const reservePreferredSlot = ref('')
const reserveNote = ref('')
const submittingReserve = ref(false)
const reserveSlotOptions = [
  { label: '全天', value: '' },
  ...TIME_SLOTS.map(s => ({ label: `${s.label} ${s.range}`, value: s.key }))
]
const reserveSlotLabel = computed(() => reservePreferredSlot.value
  ? (TIME_SLOTS.find(s => s.key === reservePreferredSlot.value)?.label || reservePreferredSlot.value)
  : '全天')
const onReserveDateSelect = (v) => { reservePreferredDate.value = v }
const onReserveSlotSelect = (v) => { reservePreferredSlot.value = v }

// 通用原因输入弹窗（拒绝转单 / 退回预约 / 取消工单）
const showReasonPopup = ref(false)
const reasonPopupTitle = ref('')
const reasonPopupPlaceholder = ref('')
const reasonText = ref('')
const reasonAction = ref('') // rejectTransfer | rejectReserve | cancel
const submittingReason = ref(false)

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

// 服务工程师：从工程师列表按姓名匹配，补全电话 / 技能 / 评分等
const matchedEngineer = computed(() => {
  const name = detail.value?.engineer
  if (!name) return null
  return (engineers.value || []).find(e => (e.name || e.realName) === name) || null
})

const serviceEngineer = computed(() => {
  const name = detail.value?.engineer
  if (!name) return null
  const eng = matchedEngineer.value || {}
  return { ...eng, name: eng.name || name }
})

// 预计处理时间（客户可见的已定时间，插队/顺延时静默更新）
const scheduledText = computed(() => {
  const d = detail.value
  if (!d?.scheduledDate) return ''
  let s = d.scheduledDate
  if (d.scheduledTimeSlot) s += ` ${slotLabel(d.scheduledTimeSlot)}`
  return s
})

// 工程师接单：先选择排期时间，再确认
const handleAccept = () => {
  acceptMode.value = 'accept'
  showAcceptPopup.value = true
}

// 接单确认（复用组件回调）—— 按模式分发到不同接口
const onAcceptConfirm = async (payload) => {
  if (!payload.timeSlot) {
    uni.showToast({ title: '请选择时段', icon: 'none' })
    return
  }
  accepting.value = true
  const id = detail.value._id || detail.value.id
  const data = {
    date: payload.date,
    timeSlot: payload.timeSlot,
    slotSpan: payload.slotSpan || 1,
    escalate: !!payload.escalate,
    escalateReason: payload.escalateReason || ''
  }
  if (payload.reason) data.reason = payload.reason
  try {
    if (acceptMode.value === 'transfer') {
      await repairStore.acceptTransfer(id, data)
      uni.showToast({ title: '已接受转单', icon: 'success' })
    } else if (acceptMode.value === 'reserve') {
      await repairStore.acceptReserveAssign(id, data)
      uni.showToast({ title: '已确认预约', icon: 'success' })
    } else {
      await repairStore.acceptOrder(id, data)
      uni.showToast({ title: '接单成功', icon: 'success' })
    }
    showAcceptPopup.value = false
    setTimeout(() => loadDetail(), 500)
  } catch {
    // handled
  } finally {
    accepting.value = false
  }
}

// 退回预约工单（复用组件回调）—— 返回待接单调度池
const onAcceptReject = async (payload) => {
  rejecting.value = true
  const id = detail.value._id || detail.value.id
  try {
    await repairStore.rejectReservedOrder(id, { reason: payload.reason })
    uni.showToast({ title: '已退回，工单返回待接单', icon: 'success' })
    showAcceptPopup.value = false
    setTimeout(() => loadDetail(), 500)
  } catch {
    // handled
  } finally {
    rejecting.value = false
  }
}

// 完结工单（工程师）→ 待确认
const handleComplete = () => {
  uni.showModal({
    title: '完结工单',
    content: '确认完结工单？完结后将等待客户/业务确认归档。',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await repairStore.completeOrder(detail.value._id || detail.value.id)
        uni.showToast({ title: '工单已完结，等待确认', icon: 'success' })
        setTimeout(() => loadDetail(), 500)
      } catch { /* handled */ }
    }
  })
}

// 确认归档（客户/业务）
const handleConfirm = () => {
  uni.showModal({
    title: '确认归档',
    content: '确认此工单已处理完成并归档？',
    success: async (res) => {
      if (!res.confirm) return
      confirming.value = true
      try {
        await repairStore.confirmRepair(detail.value._id || detail.value.id)
        uni.showToast({ title: '工单已归档', icon: 'success' })
        setTimeout(() => loadDetail(), 500)
      } catch { /* handled */ } finally {
        confirming.value = false
      }
    }
  })
}

// 保存费用（工程师）
const submitFee = async () => {
  const amount = Number(feeAmount.value)
  if (!feeAmount.value || isNaN(amount) || amount < 0) {
    uni.showToast({ title: '请填写正确的费用金额', icon: 'none' })
    return
  }
  submittingFee.value = true
  try {
    await repairStore.setRepairFee(detail.value._id || detail.value.id, {
      mode: feeMode.value,
      amount,
      note: feeNote.value.trim(),
      paidBy: feePaidBy.value.trim()
    })
    uni.showToast({ title: '费用已保存', icon: 'success' })
    setTimeout(() => loadDetail(), 500)
  } catch { /* handled */ } finally {
    submittingFee.value = false
  }
}

// 发起返修（客户/业务）
const submitRework = async () => {
  submittingRework.value = true
  try {
    const res = await repairStore.reworkRepair(detail.value._id || detail.value.id, {
      reason: reworkReason.value,
      note: reworkNote.value.trim()
    })
    uni.showToast({ title: '返修单已创建', icon: 'success' })
    showReworkPopup.value = false
    const newId = res && (res.id || res._id)
    setTimeout(() => {
      if (newId) {
        uni.navigateTo({ url: `/pages/repair-detail/index?id=${newId}` })
      } else {
        loadDetail()
      }
    }, 500)
  } catch { /* handled */ } finally {
    submittingRework.value = false
  }
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
    setTimeout(() => loadDetail(), 500)
  } catch { /* handled */ }
}

// 接受转单（目标工程师）—— 选择排期时段后确认
const handleAcceptTransfer = () => {
  acceptMode.value = 'transfer'
  showAcceptPopup.value = true
}

// 拒绝转单（目标工程师）—— 必填原因
const handleRejectTransfer = () => {
  reasonAction.value = 'rejectTransfer'
  reasonPopupTitle.value = '拒绝转单'
  reasonPopupPlaceholder.value = '请填写拒绝原因（必填）'
  reasonText.value = ''
  showReasonPopup.value = true
}

// 接受预约指派（目标工程师）—— 选择排期时段后确认
const handleAcceptReserve = () => {
  acceptMode.value = 'reserve'
  showAcceptPopup.value = true
}

// 退回预约（目标工程师）—— 必填原因
const openRejectReservePopup = () => {
  reasonAction.value = 'rejectReserve'
  reasonPopupTitle.value = '退回预约'
  reasonPopupPlaceholder.value = '请填写退回原因（必填）'
  reasonText.value = ''
  showReasonPopup.value = true
}

// 取消预约指派（发起方）
const handleCancelReserve = () => {
  uni.showModal({
    title: '取消预约指派',
    content: '确认取消该预约指派？工单将回到「待接单」。',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await repairStore.cancelReserveAssign(detail.value._id || detail.value.id)
        uni.showToast({ title: '已取消预约', icon: 'success' })
        setTimeout(() => loadDetail(), 500)
      } catch { /* handled */ }
    }
  })
}

// 打开预约指派弹窗
const openReserveAssignPopup = () => {
  reserveTargetEngineer.value = ''
  reservePreferredDate.value = ''
  reservePreferredSlot.value = ''
  reserveNote.value = ''
  showReserveAssignPopup.value = true
}

// 提交预约指派
const submitReserveAssign = async () => {
  if (!reserveTargetEngineer.value) {
    uni.showToast({ title: '请选择目标工程师', icon: 'none' })
    return
  }
  const target = engineers.value.find(e => (e._id || e.id) === reserveTargetEngineer.value)
  submittingReserve.value = true
  try {
    await repairStore.reserveAssignRepair(detail.value._id || detail.value.id, {
      targetEngineerId: reserveTargetEngineer.value,
      targetEngineerName: target?.name || target?.realName || '',
      preferredDate: reservePreferredDate.value,
      preferredTimeSlot: reservePreferredSlot.value,
      note: reserveNote.value.trim(),
    })
    uni.showToast({ title: '预约指派已发起', icon: 'success' })
    showReserveAssignPopup.value = false
    setTimeout(() => loadDetail(), 500)
  } catch { /* handled */ } finally {
    submittingReserve.value = false
  }
}

// 优先处理（加急置顶）—— 工程师本人当天 / 管理员全局，必填原因
const openEscalatePopup = () => {
  reasonAction.value = 'escalate'
  reasonPopupTitle.value = '优先处理（加急置顶）'
  reasonPopupPlaceholder.value = '请填写加急原因（必填），如：灾难性故障 / 领导检查 / 客户临时要求'
  reasonText.value = ''
  showReasonPopup.value = true
}

// 取消工单（工程师，处理中）—— 必填原因
const openCancelPopup = () => {
  reasonAction.value = 'cancel'
  reasonPopupTitle.value = '取消工单'
  reasonPopupPlaceholder.value = '请填写取消原因（必填）'
  reasonText.value = ''
  showReasonPopup.value = true
}

// 通用原因弹窗确认
const confirmReason = async () => {
  const reason = reasonText.value.trim()
  if (!reason) {
    uni.showToast({ title: '请填写原因', icon: 'none' })
    return
  }
  submittingReason.value = true
  const id = detail.value._id || detail.value.id
  try {
    if (reasonAction.value === 'rejectTransfer') {
      await repairStore.rejectTransfer(id, { reason })
      uni.showToast({ title: '已拒绝转单', icon: 'success' })
    } else if (reasonAction.value === 'rejectReserve') {
      await repairStore.rejectReserveAssign(id, { reason })
      uni.showToast({ title: '已退回预约', icon: 'success' })
    } else if (reasonAction.value === 'cancel') {
      await repairStore.cancelRepair(id, { reason })
      uni.showToast({ title: '工单已取消', icon: 'success' })
    } else if (reasonAction.value === 'escalate') {
      await repairStore.escalateOrder(id, { reason })
      uni.showToast({ title: '已加急置顶', icon: 'success' })
    }
    showReasonPopup.value = false
    setTimeout(() => loadDetail(), 500)
  } catch { /* handled */ } finally {
    submittingReason.value = false
  }
}

// 取消转单（发起人）
const handleCancelTransfer = () => {
  uni.showModal({
    title: '取消转单',
    content: '确认取消该转单申请？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await repairStore.cancelTransfer(detail.value._id || detail.value.id)
        uni.showToast({ title: '已取消转单', icon: 'success' })
        setTimeout(() => loadDetail(), 500)
      } catch { /* handled */ }
    }
  })
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

    // 预填费用（若已有）
    if (detail.value.fee) {
      feeMode.value = detail.value.fee.mode || 'agreed'
      feeAmount.value = detail.value.fee.amount != null ? String(detail.value.fee.amount) : ''
      feeNote.value = detail.value.fee.note || ''
      feePaidBy.value = detail.value.fee.paidBy || ''
    }

    // 预载工程师列表（转单选择 + 服务信息里的工程师电话/技能）
    try {
      engineers.value = await repairStore.fetchEngineers()
    } catch { /* handled */ }
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
  background: #F5F7FA;
  position: relative;
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
  color: #86909C;
}

/* 状态横幅 */
.status-banner {
  padding: calc(env(safe-area-inset-top) + 130rpx) 32rpx 52rpx;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
  align-items: center;

  &.banner-pending    { background: linear-gradient(135deg, #FF7D00, #FF9A2E); }
  &.banner-reserved   { background: linear-gradient(135deg, #FF7D00, #FF9A2E); }
  &.banner-processing { background: linear-gradient(135deg, #165DFF, #4080FF); }
  &.banner-confirming { background: linear-gradient(135deg, #722ED1, #9254DE); }
  &.banner-archived   { background: linear-gradient(135deg, #86909C, #A9AEB8); }
  &.banner-done       { background: linear-gradient(135deg, #00B42A, #23C343); }
}

.banner-status {
  font-size: 40rpx;
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
  border-radius: 32rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #F2F3F5;
  color: #165DFF;
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1D2129;
}

.escalated-badge {
  margin-left: auto;
  font-size: 20rpx;
  font-weight: 600;
  color: #F53F3F;
  background: #FFF1F0;
  padding: 4rpx 16rpx;
  border-radius: 16rpx;
}

.schedule-line {
  display: flex;
  align-items: center;
  gap: 10rpx;
  background: #E8F3FF;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  margin-bottom: 16rpx;
}
.schedule-text {
  font-size: 26rpx;
  color: #165DFF;
  font-weight: 600;
}

.info-grid {
  display: flex;
  flex-wrap: wrap;
}

.info-item {
  width: 50%;
  padding: 10rpx 0;

  &.full-width { width: 100%; }
}

.item-label {
  font-size: 24rpx;
  color: #86909C;
  display: block;
  margin-bottom: 6rpx;
}

.item-value {
  font-size: 26rpx;
  color: #4E5969;

  &.mono { font-family: monospace; }
  &.desc-text { line-height: 1.6; font-size: 28rpx; }
}

.engineer-value {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.urgency-tag {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  display: inline-block;

  &.urgency-urgent { background: #FFECE8; color: #F53F3F; }
  &.urgency-normal { background: #FFF3E8; color: #FF7D00; }
  &.urgency-low    { background: #E8FFEA; color: #00B42A; }
}

/* 费用 */
.fee-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10rpx 0;
}

.fee-label {
  font-size: 26rpx;
  color: #86909C;
}

.fee-value {
  font-size: 40rpx;
  font-weight: 800;
  color: #165DFF;
}

.fee-meta {
  font-size: 26rpx;
  color: #4E5969;
}

.fee-mode-row {
  display: flex;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.fee-mode-btn {
  flex: 1;
  height: 72rpx;
  line-height: 72rpx;
  text-align: center;
  font-size: 24rpx;
  border-radius: 14rpx;
  background: #F5F7FA;
  color: #86909C;
  transition: all .25s;

  &.on {
    background: linear-gradient(135deg, #165DFF, #4080FF);
    color: #fff;
    font-weight: 600;
  }
}

.fee-input {
  width: 100%;
  height: 88rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #4E5969;
  box-sizing: border-box;
  margin-bottom: 16rpx;
}

.fee-textarea {
  width: 100%;
  min-height: 100rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 16rpx 24rpx;
  font-size: 26rpx;
  color: #4E5969;
  box-sizing: border-box;
  margin-bottom: 16rpx;
}

.btn-fee-submit {
  width: 100%;
  height: 80rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #FFFFFF;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 80rpx;
  box-shadow: 0 8rpx 24rpx rgba(22, 93, 255, 0.28);

  &[disabled] { background: #C9CDD4; box-shadow: none; }
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
  border-radius: 16rpx;
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
  color: #165DFF;
  font-size: 28rpx;
  font-weight: 600;
  border: 1.5px solid #165DFF;
  border-radius: 50rpx;
  text-align: center;
  line-height: 80rpx;

  &:active { opacity: 0.85; }
}

.btn-escalate {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #F53F3F, #FF7D00);
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 700;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 88rpx;
  box-shadow: 0 8rpx 24rpx rgba(245, 63, 63, 0.28);

  &:active { opacity: 0.88; }
}

.progress-form {
  background: #F5F7FA;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.progress-input {
  width: 100%;
  min-height: 120rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 20rpx;
  font-size: 26rpx;
  color: #4E5969;
  box-sizing: border-box;
  border: 1.5px solid #E5E6EB;
}

.btn-progress-submit {
  width: 100%;
  height: 80rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #FFFFFF;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 80rpx;

  &:active { opacity: 0.9; }
  &[disabled] { background: #C9CDD4; }
}

.btn-accept {
  width: 100%;
  height: 92rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #FFFFFF;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 92rpx;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);

  &:active { opacity: 0.85; }
}

.action-row {
  display: flex;
  gap: 16rpx;
}

.btn-transfer, .btn-complete {
  flex: 1;
  height: 92rpx;
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 92rpx;
}

.btn-transfer {
  background: #FFFFFF;
  color: #165DFF;
  border: 1.5px solid #165DFF;
}

.btn-complete {
  background: linear-gradient(135deg, #00B42A, #23C343);
  color: #FFFFFF;
}

.btn-confirm-archive {
  width: 100%;
  height: 92rpx;
  background: linear-gradient(135deg, #722ED1, #9254DE);
  color: #FFFFFF;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 92rpx;
  box-shadow: 0 12rpx 32rpx rgba(114, 46, 209, 0.28);

  &[disabled] { background: #C9CDD4; box-shadow: none; }
}

.btn-rework {
  width: 100%;
  height: 92rpx;
  background: #FFFFFF;
  color: #F53F3F;
  font-size: 32rpx;
  font-weight: 600;
  border: 1.5px solid #F53F3F;
  border-radius: 50rpx;
  text-align: center;
  line-height: 92rpx;
}

.btn-cancel-order {
  width: 100%;
  height: 88rpx;
  background: #FFFFFF;
  color: #F53F3F;
  font-size: 28rpx;
  font-weight: 600;
  border: 1.5px solid #F53F3F;
  border-radius: 50rpx;
  text-align: center;
  line-height: 88rpx;

  &:active { opacity: 0.85; }
}

.btn-reserve-assign {
  width: 100%;
  height: 92rpx;
  background: linear-gradient(135deg, #722ED1, #9254DE);
  color: #FFFFFF;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  text-align: center;
  line-height: 92rpx;
  box-shadow: 0 12rpx 32rpx rgba(114, 46, 209, 0.28);

  &:active { opacity: 0.85; }
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
  border-radius: 40rpx 40rpx 0 0;
  padding: 40rpx 32rpx calc(32rpx + env(safe-area-inset-bottom));
  max-height: 76vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.popup-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #1D2129;
  text-align: center;
}

.popup-desc {
  font-size: 24rpx;
  color: #86909C;
  text-align: center;
  margin: 8rpx 0 24rpx;
}

.engineer-list {
  max-height: 400rpx;
}

.engineer-option {
  display: flex;
  justify-content: space-between;
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
  background: #F5F7FA;

  &.selected {
    background: #E8F3FF;
    border: 1.5px solid #165DFF;
  }
}

.eng-name { font-size: 28rpx; color: #4E5969; font-weight: 500; }
.eng-phone { font-size: 24rpx; color: #86909C; }

.popup-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 28rpx;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  height: 88rpx;
  font-size: 28rpx;
  border-radius: 50rpx;
  line-height: 88rpx;
  text-align: center;
  border: none;
}

.btn-cancel { background: #F5F7FA; color: #4E5969; }
.btn-confirm { background: linear-gradient(135deg, #165DFF, #4080FF); color: #FFFFFF; box-shadow: 0 8rpx 24rpx rgba(22, 93, 255, 0.28); }
.btn-confirm[disabled] { background: #C9CDD4; box-shadow: none; }

/* 预约指派弹窗（日期 / 时段选择行） */
.accept-date-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  background: #F5F7FA;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
}

.accept-label {
  font-size: 26rpx;
  color: #86909C;
}

.accept-date-value {
  font-size: 28rpx;
  color: #1D2129;
  font-weight: 600;
}

.transfer-info {
  margin-bottom: 20rpx;
}

.transfer-desc {
  font-size: 26rpx;
  color: #4E5969;
}

.transfer-desc.note {
  display: block;
  margin-top: 8rpx;
  color: #86909C;
}

.btn-cancel-transfer {
  width: 100%;
  height: 88rpx;
  background: #FFFFFF;
  color: #86909C;
  font-size: 28rpx;
  font-weight: 600;
  border: 1.5px solid #E5E6EB;
  border-radius: 50rpx;
  text-align: center;
  line-height: 88rpx;
}

.rework-reason-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.rework-reason-btn {
  padding: 16rpx 32rpx;
  border-radius: 16rpx;
  background: #F5F7FA;
  border: 1.5px solid transparent;
  font-size: 26rpx;
  color: #4E5969;

  &.on {
    background: #E8F3FF;
    border-color: #165DFF;
    color: #165DFF;
  }
}

.safe-bottom { height: 60rpx; }

@keyframes fadeIn  { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
</style>
