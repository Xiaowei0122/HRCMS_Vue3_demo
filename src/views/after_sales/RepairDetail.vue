<template>
  <div class="repair-detail" v-loading="loading">
    <el-card v-if="detail" shadow="never">
      <template #header>
        <div class="detail-header">
          <span>工单详情 — {{ detail.orderNo }}</span>
          <el-tag :type="statusTagType">{{ detail.status }}</el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="报修单位">{{ detail.company }}</el-descriptions-item>
        <el-descriptions-item label="报修人">{{ detail.contact }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.phone }}</el-descriptions-item>
        <el-descriptions-item label="指派工程师">{{ detail.engineer || '待指派' }}</el-descriptions-item>
        <el-descriptions-item label="工单类型">{{ detail.workOrderType || '售后上门' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ detail.deviceType || '—' }}</el-descriptions-item>
        <el-descriptions-item label="报修内容" :span="2">{{ detail.description || '—' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ detail.createTime }}</el-descriptions-item>
        <el-descriptions-item label="紧急程度">{{ detail.priority }}</el-descriptions-item>
        <el-descriptions-item label="预计处理" :span="2">
          <template v-if="detail.scheduledDate">
            <span class="schedule-time">{{ detail.scheduledDate }} {{ slotLabel(detail.scheduledTimeSlot) }}</span>
            <el-tag v-if="detail.escalated" type="danger" size="small" effect="dark" class="escalated-badge">已加急</el-tag>
          </template>
          <span v-else>—</span>
        </el-descriptions-item>
        <el-descriptions-item label="维修地址" :span="2">{{ detail.address }}</el-descriptions-item>
        <el-descriptions-item label="上门费用" :span="2">
          <span v-if="detail.fee">￥{{ detail.fee.amount }}（{{ detail.fee.mode === 'agreed' ? '已协商好' : '自行协商' }}）<template v-if="detail.fee.paidBy"> · {{ detail.fee.paidBy }}</template></span>
          <span v-else>未填写</span>
        </el-descriptions-item>
        <el-descriptions-item v-if="detail.isRework" label="返修原单" :span="2">{{ detail.reworkOf }}（{{ detail.reworkReason }}）</el-descriptions-item>
        <el-descriptions-item label="完结信息" :span="2">{{ detail.completedBy ? `${detail.completedBy} · ${detail.completedAt}` : '—' }}</el-descriptions-item>
        <el-descriptions-item label="归档确认" :span="2">{{ detail.confirmedBy ? `${detail.confirmedBy} · ${detail.confirmedAt}` : '—' }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.confirmUserName" label="确认人">{{ detail.confirmUserName }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.cancelledBy" label="取消信息" :span="2">{{ detail.cancelledBy }} · {{ detail.cancelledAt }}（{{ detail.cancelReason }}<template v-if="detail.cancelNote"> · {{ detail.cancelNote }}</template>）</el-descriptions-item>
        <el-descriptions-item v-if="detail.reservedBy" label="预约信息" :span="2">{{ detail.reservedBy }} · {{ detail.reservedAt }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.transferRequest" label="转单申请" :span="2">
          {{ detail.transferRequest.fromEngineer }} → {{ detail.transferRequest.toEngineer }}（{{ transferStatusLabel(detail.transferRequest.status) }}）
        </el-descriptions-item>
        <el-descriptions-item v-if="detail.reservationRequest" label="预约指派" :span="2">
          {{ detail.reservationRequest.targetEngineerName || '—' }} · 期望 {{ detail.reservationRequest.preferredDate || '—' }} {{ detail.reservationRequest.preferredTimeSlot || '—' }}（{{ reservationStatusLabel(detail.reservationRequest.status) }}）
        </el-descriptions-item>
      </el-descriptions>

      <!-- 进度时间线 -->
      <el-timeline style="margin-top: 30px">
        <el-timeline-item
          v-for="(item, index) in detail.progress"
          :key="index"
          :timestamp="item.time"
          :color="item.status === 'done' ? '#0bbd87' : 'var(--color-accent)'"
        >
          {{ item.node }}
        </el-timeline-item>
      </el-timeline>

      <!-- 操作区 -->
      <div class="action-bar">
        <el-button type="warning" v-if="(isAdmin || isConfirmUser) && detail.status === '待确认'" @click="handleConfirm">确认归档</el-button>
        <el-button type="danger" v-if="isAdmin && isArchived(detail.status)" @click="openReworkDialog">发起返修</el-button>
        <el-button type="primary" plain v-if="isAdmin" @click="openFeeDialog">费用录入</el-button>
        <!-- 接单（普通「待接单」抢单池 / 已预约单的预约工程师；预约单弹窗内支持改派/退回） -->
        <el-button type="success" v-if="canAcceptDetail" @click="openAcceptDialog">接单</el-button>
        <!-- 处理操作（工程师/管理员，处理中） -->
        <el-button type="primary" plain v-if="canAddProgressDetail" @click="openProgressDialog">添加节点</el-button>
        <el-button type="success" plain v-if="canCompleteDetail" @click="handleComplete">工单处理完成</el-button>
        <!-- 预约指派 -->
        <el-button type="primary" plain v-if="canReserveAssignDetail" @click="openReserveAssignDialog">预约指派</el-button>
        <el-button type="success" plain v-if="canAcceptReserveAssignDetail" @click="openAcceptReserveAssignDialog">确认预约</el-button>
        <el-button type="danger" plain v-if="canRejectReserveAssignDetail" @click="openRejectReserveAssignDialog">退回预约</el-button>
        <el-button type="info" plain v-if="canCancelReserveAssignDetail" @click="handleCancelReserveAssign">取消预约</el-button>
        <!-- 优先处理（加急置顶，需填写原因） -->
        <el-button type="danger" plain v-if="canManageDetail" @click="openEscalateDialog">优先处理</el-button>
        <!-- 转单操作 -->
        <el-button type="warning" plain v-if="canTransferDetail" @click="openTransferDialog">转单</el-button>
        <el-button type="success" plain v-if="canAcceptTransferDetail" @click="openAcceptTransferDialog">接受转单</el-button>
        <el-button type="danger" plain v-if="canRejectTransferDetail" @click="openRejectTransferDialog">退回转单</el-button>
        <el-button type="info" plain v-if="canCancelTransferDetail" @click="handleCancelTransfer">取消转单</el-button>
        <el-button type="danger" plain v-if="canCancelOrderDetail" @click="openCancelDialog">取消工单</el-button>
      </div>
    </el-card>

    <el-empty v-else-if="!loading" description="未找到工单信息" />

    <!-- 返修弹窗 -->
    <el-dialog v-model="reworkVisible" title="发起返修" width="500px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="返修原因" required>
          <el-radio-group v-model="reworkForm.reason">
            <el-radio value="故障未解决">故障未解决</el-radio>
            <el-radio value="故障再次出现">故障再次出现</el-radio>
            <el-radio value="其他">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="补充说明">
          <el-input v-model="reworkForm.note" type="textarea" :rows="3" placeholder="选填，补充返修具体情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reworkVisible = false">取消</el-button>
        <el-button type="primary" :loading="reworking" @click="confirmRework">确认返修</el-button>
      </template>
    </el-dialog>

    <!-- 添加节点弹窗 -->
    <el-dialog v-model="progressVisible" title="添加节点" width="500px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="节点内容" required>
          <el-input v-model="progressForm.node" type="textarea" :rows="3" placeholder="如：已到达现场，开始检修" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="progressVisible = false">取消</el-button>
        <el-button type="primary" :loading="progressing" @click="confirmAddProgress">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- 取消工单弹窗 -->
    <el-dialog v-model="cancelVisible" title="取消工单" width="500px" destroy-on-close append-to-body>
      <el-alert title="取消后工单进入终态，排期时段将被释放，并抄送发起人与管理员" type="warning" :closable="false" show-icon style="margin-bottom: 12px" />
      <el-form label-position="top">
        <el-form-item label="取消原因" required>
          <el-radio-group v-model="cancelForm.reason">
            <el-radio value="客户不修了">客户不修了</el-radio>
            <el-radio value="价格因素">价格因素</el-radio>
            <el-radio value="故障自行恢复">故障自行恢复</el-radio>
            <el-radio value="其他">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="补充说明">
          <el-input v-model="cancelForm.note" type="textarea" :rows="3" placeholder="选填，补充取消具体情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelVisible = false">取消</el-button>
        <el-button type="danger" :loading="cancelling" @click="confirmCancelOrder">确认取消工单</el-button>
      </template>
    </el-dialog>

    <!-- 优先处理（加急置顶）弹窗 -->
    <el-dialog v-model="escalateVisible" title="优先处理（加急置顶）" width="500px" destroy-on-close append-to-body>
      <el-alert title="加急后该工单将置顶到当天第一顺位，后续工单自动顺延（不向客户推送插队原因）" type="warning" :closable="false" show-icon style="margin-bottom: 12px" />
      <el-form label-position="top">
        <el-form-item label="加急原因" required>
          <el-radio-group v-model="escalateReason">
            <el-radio value="灾难性故障">灾难性故障</el-radio>
            <el-radio value="领导检查">领导检查</el-radio>
            <el-radio value="客户临时要求">客户临时要求</el-radio>
            <el-radio value="其他">其他</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="escalateVisible = false">取消</el-button>
        <el-button type="danger" :loading="escalateLoading" @click="confirmEscalate">确认加急置顶</el-button>
      </template>
    </el-dialog>

    <!-- 费用录入弹窗 -->
    <el-dialog v-model="feeVisible" title="上门费用录入" width="500px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="费用方式" required>
          <el-radio-group v-model="feeForm.mode">
            <el-radio value="agreed">已协商好</el-radio>
            <el-radio value="self">自行协商</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="费用金额（元）" required>
          <el-input-number v-model="feeForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="支付方">
          <el-input v-model="feeForm.paidBy" placeholder="如：客户现金 / 公司转账" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="feeForm.note" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="feeVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingFee" @click="confirmFee">保存</el-button>
      </template>
    </el-dialog>

    <!-- 转单弹窗 -->
    <el-dialog v-model="transferVisible" title="转单申请" width="500px" destroy-on-close append-to-body>
      <div class="assign-info">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="工单号">{{ detail?.orderNo }}</el-descriptions-item>
          <el-descriptions-item label="当前处理人">{{ detail?.engineer }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <el-divider content-position="left">选择目标工程师</el-divider>
      <div class="engineer-list">
        <div
          v-for="eng in transferEngineers"
          :key="eng.id"
          class="engineer-option"
          :class="{ selected: selectedTransferEngineerId === eng.id }"
          @click="selectedTransferEngineerId = eng.id"
        >
          <div class="eng-avatar">{{ eng.name?.[0] || '工' }}</div>
          <div class="eng-info">
            <div class="eng-name">{{ eng.name }}</div>
            <div class="eng-detail">{{ eng.phone || '' }} · {{ eng.team || '工号未分组' }}</div>
          </div>
          <el-icon v-if="selectedTransferEngineerId === eng.id" color="var(--color-accent)" :size="20"><CircleCheck /></el-icon>
        </div>
      </div>
      <el-empty v-if="!transferEngineers.length" description="暂无可转单的工程师" />
      <el-form-item label="转单原因" style="margin-top: 16px">
        <el-input v-model="transferReason" type="textarea" :rows="2" placeholder="请填写转单原因" />
      </el-form-item>
      <template #footer>
        <el-button @click="transferVisible = false">取消</el-button>
        <el-button type="primary" :loading="transferLoading" @click="confirmTransfer">提交转单申请</el-button>
      </template>
    </el-dialog>

    <!-- 接受转单弹窗（选择时段） -->
    <el-dialog v-model="acceptTransferVisible" title="接受转单 — 选择预约时段" width="480px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="预约日期" required>
          <el-date-picker v-model="acceptTransferDate" type="date" value-format="YYYY-MM-DD" :disabled-date="disablePastDate" style="width:100%" @change="loadAcceptTransferAvailability" />
        </el-form-item>
        <el-form-item label="预约时段" required>
          <el-select v-model="acceptTransferSlot" style="width:100%">
            <el-option v-for="opt in timeSlotOptions" :key="opt.value" :label="opt.label" :value="opt.value" :disabled="acceptTransferOccupied.includes(opt.value)" />
          </el-select>
          <div v-if="acceptTransferOccupied.length" style="margin-top:6px;font-size:12px;color:var(--text-muted)">已占用时段：{{ acceptTransferOccupied.join('、') }}</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="acceptTransferVisible = false">取消</el-button>
        <el-button type="primary" :loading="acceptTransferLoading" @click="confirmAcceptTransfer">确认接受</el-button>
      </template>
    </el-dialog>

    <!-- 退回转单弹窗（填写原因） -->
    <el-dialog v-model="rejectTransferVisible" title="退回转单申请" width="480px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="退回原因" required>
          <el-input v-model="rejectTransferReason" type="textarea" :rows="3" placeholder="请填写退回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectTransferVisible = false">取消</el-button>
        <el-button type="primary" :loading="rejectTransferLoading" @click="confirmRejectTransfer">确认退回</el-button>
      </template>
    </el-dialog>

    <!-- 预约指派弹窗 -->
    <el-dialog v-model="reserveAssignVisible" title="预约指派" width="500px" destroy-on-close append-to-body>
      <div class="assign-info">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="工单号">{{ detail?.orderNo }}</el-descriptions-item>
          <el-descriptions-item label="报修单位">{{ detail?.company }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <el-divider content-position="left">选择目标工程师</el-divider>
      <div class="engineer-list">
        <div
          v-for="eng in reserveAssignEngineers"
          :key="eng.id"
          class="engineer-option"
          :class="{ selected: selectedReserveAssignEngineerId === eng.id }"
          @click="selectReserveAssignEngineer(eng)"
        >
          <div class="eng-avatar">{{ eng.name?.[0] || '工' }}</div>
          <div class="eng-info">
            <div class="eng-name">{{ eng.name }}</div>
            <div class="eng-detail">{{ eng.phone || '' }} · {{ eng.team || '工号未分组' }}</div>
          </div>
          <el-icon v-if="selectedReserveAssignEngineerId === eng.id" color="var(--color-accent)" :size="20"><CircleCheck /></el-icon>
        </div>
      </div>
      <el-empty v-if="!reserveAssignEngineers.length" description="暂无可指派的工程师" />
      <el-form-item label="期望上门日期" style="margin-top: 16px">
        <el-date-picker v-model="reserveAssignPreferredDate" type="date" value-format="YYYY-MM-DD" :disabled-date="disablePastDate" style="width:100%" @change="loadReserveAssignAvailability" />
      </el-form-item>
      <el-form-item label="期望时段">
        <el-select v-model="reserveAssignPreferredSlot" style="width:100%" clearable placeholder="选填">
          <el-option
            v-for="opt in timeSlotOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
            :disabled="opt.value !== '全天' && reserveAssignOccupied.includes(opt.value)"
          >
            <span>{{ opt.label }}</span>
            <span v-if="opt.value !== '全天' && reserveAssignOccupied.includes(opt.value)" class="occupied-tip">（已占用）</span>
          </el-option>
        </el-select>
        <div v-if="reserveAssignOccupied.length" style="margin-top:6px;font-size:12px;color:var(--text-muted)">已占用时段：{{ reserveAssignOccupied.join('、') }}</div>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="reserveAssignNote" type="textarea" :rows="2" placeholder="选填，如客户特殊要求" />
      </el-form-item>
      <template #footer>
        <el-button @click="reserveAssignVisible = false">取消</el-button>
        <el-button type="primary" :loading="reserveAssignLoading" @click="confirmReserveAssign">发起预约指派</el-button>
      </template>
    </el-dialog>

    <!-- 确认预约弹窗（工程师选择时段） -->
    <el-dialog v-model="acceptReserveAssignVisible" title="确认预约 — 选择上门时段" width="480px" destroy-on-close append-to-body>
      <div class="assign-info">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="工单号">{{ detail?.orderNo }}</el-descriptions-item>
          <el-descriptions-item label="期望日期">{{ detail?.reservationRequest?.preferredDate || '—' }}</el-descriptions-item>
          <el-descriptions-item label="期望时段">{{ detail?.reservationRequest?.preferredTimeSlot || '—' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <el-form label-position="top" style="margin-top: 12px">
        <el-form-item label="确认日期" required>
          <el-date-picker v-model="acceptReserveAssignDate" type="date" value-format="YYYY-MM-DD" :disabled-date="disableReserveAssignDate" style="width:100%" @change="loadAcceptReserveAssignAvailability" />
        </el-form-item>
        <el-form-item label="确认时段" required>
          <el-select v-model="acceptReserveAssignSlot" style="width:100%">
            <el-option v-for="opt in timeSlotOptions" :key="opt.value" :label="opt.label" :value="opt.value" :disabled="acceptReserveAssignOccupied.includes(opt.value)" />
          </el-select>
          <div v-if="acceptReserveAssignOccupied.length" style="margin-top:6px;font-size:12px;color:var(--text-muted)">已占用时段：{{ acceptReserveAssignOccupied.join('、') }}</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="acceptReserveAssignVisible = false">取消</el-button>
        <el-button type="primary" :loading="acceptReserveAssignLoading" @click="confirmAcceptReserveAssign">确认预约</el-button>
      </template>
    </el-dialog>

    <!-- 退回预约弹窗（填写原因） -->
    <el-dialog v-model="rejectReserveAssignVisible" title="退回预约申请" width="480px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="退回原因" required>
          <el-input v-model="rejectReserveAssignReason" type="textarea" :rows="3" placeholder="请填写退回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectReserveAssignVisible = false">取消</el-button>
        <el-button type="primary" :loading="rejectReserveAssignLoading" @click="confirmRejectReserveAssign">确认退回</el-button>
      </template>
    </el-dialog>

    <!-- 接单弹窗（复用组件：普通单 / 预约单，预约单支持改派/退回） -->
    <AcceptOrderDialog
      v-model="acceptVisible"
      :order="detail"
      :confirming="acceptLoading"
      :rejecting="rejectReservedLoading"
      @confirm="onAcceptConfirm"
      @reject="onAcceptReject"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getRepairDetail, confirmRepair, completeRepair, addRepairProgress, reworkRepair, cancelRepair, setRepairFee, getEngineerList, getScheduleAvailability, transferRepair, acceptTransfer, rejectTransfer, cancelTransfer, reserveAssignRepair, acceptReserveAssign, rejectReserveAssign, cancelReserveAssign, acceptRepair, rejectReservedOrder, escalateOrder } from '@/api/modules/repairs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserInfo } from '@/utils/auth'
import { CircleCheck } from '@element-plus/icons-vue'
import AcceptOrderDialog from '@/components/AcceptOrderDialog.vue'

const route = useRoute()
const detail = ref(null)
const loading = ref(false)

// repair:all 被 admin/business/engineer 同时持有，不能用它判断管理员
const isAdmin = computed(() => (getUserInfo()?.rank ?? 99) <= 1)
const isEngineer = computed(() => getUserInfo()?.roleCode === 'engineer')
const isBusiness = computed(() => getUserInfo()?.roleCode === 'business')
const myUserId = computed(() => getUserInfo()?.id || '')
// 确认人本人（业务/客户）可对名下工单确认归档
const isConfirmUser = computed(() => {
  if (!detail.value) return false
  return detail.value.confirmUserId && detail.value.confirmUserId === myUserId.value
})
const isArchived = (s) => s === '已完成' || s === '已归档'

const transferStatusLabel = (s) => {
  const map = { pending: '待接受', accepted: '已接受', rejected: '已退回', cancelled: '已取消' }
  return map[s] || s
}

const reservationStatusLabel = (s) => {
  const map = { pending: '待确认', accepted: '已确认', rejected: '已退回', cancelled: '已取消' }
  return map[s] || s
}

const SLOT_LABELS = { AM1: '上午(早)', AM2: '上午(晚)', PM1: '下午(早)', PM2: '下午(中)', PM3: '下午(晚)' }
const slotLabel = (slot) => SLOT_LABELS[slot] || slot || ''

const timeSlotOptions = [
  { label: '全天', value: '全天' },
  { label: '上午 (早) 08:30-10:00', value: 'AM1' },
  { label: '上午 (晚) 10:00-11:50', value: 'AM2' },
  { label: '下午 (早) 13:30-15:00', value: 'PM1' },
  { label: '下午 (中) 15:00-16:30', value: 'PM2' },
  { label: '下午 (晚) 16:30-18:00', value: 'PM3' },
]

const serverDate = ref('')
const todayLocal = () => {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
const disablePastDate = (date) => {
  const today = serverDate.value ? new Date(serverDate.value + 'T00:00:00') : new Date()
  today.setHours(0, 0, 0, 0)
  return date.getTime() < today.getTime()
}

// 返修
const reworkVisible = ref(false)
const reworking = ref(false)
const reworkForm = reactive({ reason: '故障未解决', note: '' })

const cancelVisible = ref(false)
const cancelling = ref(false)
const cancelForm = reactive({ reason: '客户不修了', note: '' })

const progressVisible = ref(false)
const progressing = ref(false)
const progressForm = reactive({ node: '' })

// 费用
const feeVisible = ref(false)
const savingFee = ref(false)
const feeForm = reactive({ mode: 'self', amount: 0, paidBy: '', note: '' })

// 优先处理（加急置顶）
const escalateVisible = ref(false)
const escalateLoading = ref(false)
const escalateReason = ref('灾难性故障')

// 转单
const transferVisible = ref(false)
const transferLoading = ref(false)
const transferEngineers = ref([])
const selectedTransferEngineerId = ref('')
const transferReason = ref('')

// 接受转单弹窗（选择时段）
const acceptTransferVisible = ref(false)
const acceptTransferLoading = ref(false)
const acceptTransferDate = ref('')
const acceptTransferSlot = ref('全天')
const acceptTransferOccupied = ref([])

// 退回转单弹窗（填写原因）
const rejectTransferVisible = ref(false)
const rejectTransferLoading = ref(false)
const rejectTransferReason = ref('')

// 预约指派弹窗
const reserveAssignVisible = ref(false)
const reserveAssignLoading = ref(false)
const reserveAssignEngineers = ref([])
const selectedReserveAssignEngineerId = ref('')
const reserveAssignPreferredDate = ref('')
const reserveAssignPreferredSlot = ref('')
const reserveAssignNote = ref('')
const reserveAssignOccupied = ref([])

// 确认预约弹窗（工程师选择时段）
const acceptReserveAssignVisible = ref(false)
const acceptReserveAssignLoading = ref(false)
const acceptReserveAssignDate = ref('')
const acceptReserveAssignSlot = ref('全天')
const acceptReserveAssignOccupied = ref([])

// 退回预约弹窗（填写原因）
const rejectReserveAssignVisible = ref(false)
const rejectReserveAssignLoading = ref(false)
const rejectReserveAssignReason = ref('')

// 接单（普通「待接单」抢单池 / 已预约单；复用 AcceptOrderDialog 组件）
const acceptVisible = ref(false)
const acceptLoading = ref(false)
const rejectReservedLoading = ref(false)

// 工程师可接单：普通「待接单」抢单池 + 指派给自己的「已预约」单
const canAcceptDetail = computed(() => {
  if (!detail.value) return false
  if (!isEngineer.value) return false
  const s = detail.value.status
  if (s === '待接单') return true
  if (s === '已预约') {
    const rid = detail.value.engineerId || ''
    return !rid || rid === myUserId.value
  }
  return false
})

const openAcceptDialog = () => {
  acceptVisible.value = true
}

const onAcceptConfirm = async (payload) => {
  acceptLoading.value = true
  try {
    await acceptRepair(detail.value.id, {
      date: payload.date,
      timeSlot: payload.timeSlot,
      slotSpan: payload.slotSpan || 1,
      escalate: !!payload.escalate,
      escalateReason: payload.escalateReason || '',
      reason: payload.reason || ''
    })
    ElMessage.success('接单成功，已同步排期')
    acceptVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    acceptLoading.value = false
  }
}

const onAcceptReject = async (payload) => {
  rejectReservedLoading.value = true
  try {
    await rejectReservedOrder(detail.value.id, { reason: payload.reason })
    ElMessage.success('已退回，工单返回待接单')
    acceptVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    rejectReservedLoading.value = false
  }
}

// 现场处理动作：仅工程师本人
const canProcessDetail = computed(() => {
  if (!detail.value) return false
  if (!isEngineer.value) return false
  if (detail.value.status !== '处理中') return false
  if (detail.value.engineerId !== myUserId.value) return false
  return true
})

// 调度兜底动作：工程师本人 + 管理员
const canManageDetail = computed(() => {
  if (!detail.value) return false
  if (!isEngineer.value && !isAdmin.value) return false
  if (detail.value.status !== '处理中') return false
  if (isEngineer.value && detail.value.engineerId !== myUserId.value) return false
  return true
})

const canAddProgressDetail = computed(() => canProcessDetail.value)

const canCompleteDetail = computed(() => canProcessDetail.value)

const canTransferDetail = computed(() => {
  if (!canManageDetail.value) return false
  const tr = detail.value.transferRequest
  if (tr && tr.status === 'pending') return false
  return true
})

const canCancelOrderDetail = computed(() => canManageDetail.value)

const canAcceptTransferDetail = computed(() => {
  const tr = detail.value?.transferRequest
  if (!tr || tr.status !== 'pending') return false
  return tr.toEngineerId === myUserId.value
})

const canRejectTransferDetail = computed(() => {
  const tr = detail.value?.transferRequest
  if (!tr || tr.status !== 'pending') return false
  return tr.toEngineerId === myUserId.value
})

const canCancelTransferDetail = computed(() => {
  const tr = detail.value?.transferRequest
  if (!tr || tr.status !== 'pending') return false
  return tr.fromEngineerId === myUserId.value || isAdmin.value
})

const statusTagType = computed(() => {
  const map = {
    '待接单': 'info',
    '已预约': 'warning',
    '处理中': 'warning',
    '待确认': 'warning',
    '已完成': 'success',
    '已归档': 'success',
    '已取消': 'danger'
  }
  return map[detail.value?.status] || 'info'
})

const handleConfirm = async () => {
  try {
    await ElMessageBox.confirm('确认将该工单归档？归档后不可直接修改。', '确认归档', { type: 'warning' })
  } catch { return }
  try {
    await confirmRepair(detail.value.id)
    ElMessage.success('工单已归档')
    fetchDetail()
  } catch { /* ignore */ }
}

const openReworkDialog = () => {
  reworkForm.reason = '故障未解决'
  reworkForm.note = ''
  reworkVisible.value = true
}

const confirmRework = async () => {
  if (!reworkForm.reason) { ElMessage.warning('请选择返修原因'); return }
  reworking.value = true
  try {
    const res = await reworkRepair(detail.value.id, { reason: reworkForm.reason, note: reworkForm.note })
    ElMessage.success(`返修单已创建：${res.orderNo || ''}`)
    reworkVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    reworking.value = false
  }
}

// --- 取消工单 ---
const openCancelDialog = () => {
  cancelForm.reason = '客户不修了'
  cancelForm.note = ''
  cancelVisible.value = true
}

const confirmCancelOrder = async () => {
  if (!cancelForm.reason) { ElMessage.warning('请选择取消原因'); return }
  cancelling.value = true
  try {
    await cancelRepair(detail.value.id, { reason: cancelForm.reason, note: cancelForm.note })
    ElMessage.success('工单已取消')
    cancelVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    cancelling.value = false
  }
}

// --- 添加节点 ---
const openProgressDialog = () => {
  progressForm.node = ''
  progressVisible.value = true
}

const confirmAddProgress = async () => {
  if (!progressForm.node.trim()) { ElMessage.warning('请填写节点内容'); return }
  progressing.value = true
  try {
    await addRepairProgress(detail.value.id, { node: progressForm.node.trim() })
    ElMessage.success('节点已添加')
    progressVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    progressing.value = false
  }
}

// --- 工单处理完成 ---
const handleComplete = async () => {
  try {
    await ElMessageBox.confirm('确认该工单已处理完成？完成后将进入「待确认」，等待客户/业务确认归档。', '工单处理完成', {
      type: 'warning',
      confirmButtonText: '确认完成',
      cancelButtonText: '再等等'
    })
  } catch { return }
  try {
    await completeRepair(detail.value.id)
    ElMessage.success('工单已处理完成，等待客户/业务确认')
    fetchDetail()
  } catch { /* ignore */ }
}

const openFeeDialog = () => {
  feeForm.mode = detail.value.fee?.mode || 'self'
  feeForm.amount = detail.value.fee?.amount || 0
  feeForm.paidBy = detail.value.fee?.paidBy || ''
  feeForm.note = detail.value.fee?.note || ''
  feeVisible.value = true
}

const confirmFee = async () => {
  if (feeForm.amount == null || feeForm.amount < 0) { ElMessage.warning('请填写正确的费用金额'); return }
  savingFee.value = true
  try {
    await setRepairFee(detail.value.id, { mode: feeForm.mode, amount: feeForm.amount, paidBy: feeForm.paidBy, note: feeForm.note })
    ElMessage.success('费用已保存')
    feeVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    savingFee.value = false
  }
}

// --- 优先处理（加急置顶） ---
const openEscalateDialog = () => {
  escalateReason.value = '灾难性故障'
  escalateVisible.value = true
}

const confirmEscalate = async () => {
  if (!escalateReason.value) { ElMessage.warning('请选择加急原因'); return }
  escalateLoading.value = true
  try {
    const res = await escalateOrder(detail.value.id, { reason: escalateReason.value })
    if (res?.overflow > 0) {
      ElMessage.warning(res.message || '已加急置顶，有工单溢出顺延')
    } else {
      ElMessage.success('已加急置顶，后续工单已顺延')
    }
    escalateVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    escalateLoading.value = false
  }
}

// --- 转单操作 ---
const openTransferDialog = async () => {
  selectedTransferEngineerId.value = ''
  transferReason.value = ''
  transferVisible.value = true
  try {
    const res = await getEngineerList()
    const all = Array.isArray(res) ? res : (res.records || [])
    transferEngineers.value = all.filter(e => e.id !== detail.value?.engineerId)
  } catch {
    transferEngineers.value = []
  }
}

const confirmTransfer = async () => {
  if (!selectedTransferEngineerId.value) {
    ElMessage.warning('请选择目标工程师')
    return
  }
  const eng = transferEngineers.value.find(e => e.id === selectedTransferEngineerId.value)
  transferLoading.value = true
  try {
    await transferRepair(detail.value.id, {
      targetEngineerId: selectedTransferEngineerId.value,
      targetEngineerName: eng?.name || '',
      reason: transferReason.value
    })
    ElMessage.success('转单申请已提交')
    transferVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    transferLoading.value = false
  }
}

// --- 接受转单（选择时段） ---
const openAcceptTransferDialog = () => {
  acceptTransferDate.value = serverDate.value || todayLocal()
  acceptTransferSlot.value = '全天'
  acceptTransferOccupied.value = []
  acceptTransferVisible.value = true
  loadAcceptTransferAvailability()
}

const loadAcceptTransferAvailability = async () => {
  if (!acceptTransferDate.value) return
  const myId = getUserInfo()?.id
  if (!myId) return
  try {
    const res = await getScheduleAvailability({ engineerId: myId, date: acceptTransferDate.value })
    acceptTransferOccupied.value = Array.isArray(res?.occupied) ? res.occupied : []
    if (acceptTransferOccupied.value.includes(acceptTransferSlot.value)) acceptTransferSlot.value = '全天'
  } catch { acceptTransferOccupied.value = [] }
}

const confirmAcceptTransfer = async () => {
  if (!acceptTransferDate.value) { ElMessage.warning('请选择预约日期'); return }
  if (!acceptTransferSlot.value) { ElMessage.warning('请选择预约时段'); return }
  const isFullDay = acceptTransferSlot.value === '全天'
  acceptTransferLoading.value = true
  try {
    await acceptTransfer(detail.value.id, {
      date: acceptTransferDate.value,
      timeSlot: isFullDay ? 'AM1' : acceptTransferSlot.value,
      slotSpan: isFullDay ? 5 : 1
    })
    ElMessage.success('已接受转单，工单已转入你的名下')
    acceptTransferVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    acceptTransferLoading.value = false
  }
}

// --- 退回转单（填写原因） ---
const openRejectTransferDialog = () => {
  rejectTransferReason.value = ''
  rejectTransferVisible.value = true
}

const confirmRejectTransfer = async () => {
  if (!rejectTransferReason.value.trim()) { ElMessage.warning('请填写退回原因'); return }
  rejectTransferLoading.value = true
  try {
    await rejectTransfer(detail.value.id, { reason: rejectTransferReason.value.trim() })
    ElMessage.success('转单申请已退回')
    rejectTransferVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    rejectTransferLoading.value = false
  }
}

// --- 取消转单 ---
const handleCancelTransfer = async () => {
  try {
    await ElMessageBox.confirm('确认取消该转单申请？', '取消转单', { type: 'warning' })
  } catch { return }
  try {
    await cancelTransfer(detail.value.id)
    ElMessage.success('转单申请已取消')
    fetchDetail()
  } catch { /* ignore */ }
}

// --- 预约指派 ---
const canReserveAssignDetail = computed(() => {
  if (!detail.value) return false
  if (!isAdmin.value && !isBusiness.value) return false
  if (detail.value.status !== '待接单') return false
  const rr = detail.value.reservationRequest
  if (rr && rr.status === 'pending') return false
  return true
})

const openReserveAssignDialog = async () => {
  selectedReserveAssignEngineerId.value = ''
  reserveAssignPreferredDate.value = ''
  reserveAssignPreferredSlot.value = ''
  reserveAssignNote.value = ''
  reserveAssignOccupied.value = []
  reserveAssignVisible.value = true
  try {
    const res = await getEngineerList()
    reserveAssignEngineers.value = Array.isArray(res) ? res : (res.records || [])
  } catch { reserveAssignEngineers.value = [] }
}

const selectReserveAssignEngineer = (eng) => {
  selectedReserveAssignEngineerId.value = eng.id
  loadReserveAssignAvailability()
}

const loadReserveAssignAvailability = async () => {
  if (!selectedReserveAssignEngineerId.value || !reserveAssignPreferredDate.value) {
    reserveAssignOccupied.value = []
    return
  }
  try {
    const res = await getScheduleAvailability({ engineerId: selectedReserveAssignEngineerId.value, date: reserveAssignPreferredDate.value })
    reserveAssignOccupied.value = Array.isArray(res?.occupied) ? res.occupied : []
    // 已选时段若变为占用，自动回退到空（选填）
    if (reserveAssignOccupied.value.includes(reserveAssignPreferredSlot.value)) reserveAssignPreferredSlot.value = ''
  } catch { reserveAssignOccupied.value = [] }
}

const confirmReserveAssign = async () => {
  if (!selectedReserveAssignEngineerId.value) { ElMessage.warning('请选择目标工程师'); return }
  const eng = reserveAssignEngineers.value.find(e => e.id === selectedReserveAssignEngineerId.value)
  reserveAssignLoading.value = true
  try {
    await reserveAssignRepair(detail.value.id, {
      targetEngineerId: selectedReserveAssignEngineerId.value,
      targetEngineerName: eng?.name || '',
      preferredDate: reserveAssignPreferredDate.value,
      preferredTimeSlot: reserveAssignPreferredSlot.value,
      note: reserveAssignNote.value
    })
    ElMessage.success('预约指派已发起')
    reserveAssignVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    reserveAssignLoading.value = false
  }
}

// --- 确认预约（工程师选择时段） ---
const canAcceptReserveAssignDetail = computed(() => {
  const rr = detail.value?.reservationRequest
  if (!rr || rr.status !== 'pending') return false
  return rr.targetEngineerId === myUserId.value
})

const openAcceptReserveAssignDialog = () => {
  const rr = detail.value?.reservationRequest || {}
  acceptReserveAssignDate.value = rr.preferredDate || serverDate.value || todayLocal()
  acceptReserveAssignSlot.value = '全天'
  acceptReserveAssignOccupied.value = []
  acceptReserveAssignVisible.value = true
  loadAcceptReserveAssignAvailability()
}

const loadAcceptReserveAssignAvailability = async () => {
  if (!acceptReserveAssignDate.value) return
  const myId = getUserInfo()?.id
  if (!myId) return
  try {
    const res = await getScheduleAvailability({ engineerId: myId, date: acceptReserveAssignDate.value })
    acceptReserveAssignOccupied.value = Array.isArray(res?.occupied) ? res.occupied : []
    if (acceptReserveAssignOccupied.value.includes(acceptReserveAssignSlot.value)) acceptReserveAssignSlot.value = '全天'
  } catch { acceptReserveAssignOccupied.value = [] }
}

const disableReserveAssignDate = (date) => {
  const rr = detail.value?.reservationRequest
  const preferred = rr?.preferredDate
  if (!preferred) return disablePastDate(date)
  const minDate = new Date(preferred + 'T00:00:00')
  const maxDate = new Date(minDate.getTime() + 14 * 86400000)
  return date.getTime() < minDate.getTime() || date.getTime() > maxDate.getTime()
}

const confirmAcceptReserveAssign = async () => {
  if (!acceptReserveAssignDate.value) { ElMessage.warning('请选择确认日期'); return }
  if (!acceptReserveAssignSlot.value) { ElMessage.warning('请选择确认时段'); return }
  const isFullDay = acceptReserveAssignSlot.value === '全天'
  acceptReserveAssignLoading.value = true
  try {
    await acceptReserveAssign(detail.value.id, {
      date: acceptReserveAssignDate.value,
      timeSlot: isFullDay ? 'AM1' : acceptReserveAssignSlot.value,
      slotSpan: isFullDay ? 5 : 1
    })
    ElMessage.success('预约已确认，工单进入处理中')
    acceptReserveAssignVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    acceptReserveAssignLoading.value = false
  }
}

// --- 退回预约（填写原因） ---
const canRejectReserveAssignDetail = computed(() => {
  const rr = detail.value?.reservationRequest
  if (!rr || rr.status !== 'pending') return false
  return rr.targetEngineerId === myUserId.value
})

const openRejectReserveAssignDialog = () => {
  rejectReserveAssignReason.value = ''
  rejectReserveAssignVisible.value = true
}

const confirmRejectReserveAssign = async () => {
  if (!rejectReserveAssignReason.value.trim()) { ElMessage.warning('请填写退回原因'); return }
  rejectReserveAssignLoading.value = true
  try {
    await rejectReserveAssign(detail.value.id, { reason: rejectReserveAssignReason.value.trim() })
    ElMessage.success('预约申请已退回')
    rejectReserveAssignVisible.value = false
    fetchDetail()
  } catch { /* ignore */ } finally {
    rejectReserveAssignLoading.value = false
  }
}

// --- 取消预约 ---
const canCancelReserveAssignDetail = computed(() => {
  const rr = detail.value?.reservationRequest
  if (!rr || rr.status !== 'pending') return false
  return isAdmin.value || isBusiness.value
})

const handleCancelReserveAssign = async () => {
  try {
    await ElMessageBox.confirm('确认取消该预约申请？', '取消预约', { type: 'warning' })
  } catch { return }
  try {
    await cancelReserveAssign(detail.value.id)
    ElMessage.success('预约申请已取消')
    fetchDetail()
  } catch { /* ignore */ }
}

const fetchDetail = async () => {
  const id = route.params.id
  if (!id) return

  loading.value = true
  try {
    detail.value = await getRepairDetail(id)
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.repair-detail { padding: 10px; }
.detail-header { display: flex; justify-content: space-between; align-items: center; }
.action-bar { margin-top: 20px; display: flex; justify-content: flex-end; gap: 12px; flex-wrap: wrap; }

/* 工程师选择列表（转单弹窗复用） */
.assign-info { margin-bottom: 12px; }
.engineer-list { display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow-y: auto; }
.engineer-option {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px;
  border: 1px solid var(--border-color); border-radius: var(--radius-sm);
  cursor: pointer; transition: all 0.2s;
}
.engineer-option:hover { border-color: var(--color-accent); background: var(--color-info-bg); }
.engineer-option.selected { border-color: var(--color-accent); background: var(--color-info-bg); }
.eng-avatar {
  width: 36px; height: 36px; border-radius: 50%; background: var(--color-accent);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; flex-shrink: 0;
}
.eng-info { flex: 1; min-width: 0; }
.eng-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.eng-detail { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.occupied-tip { color: var(--text-muted); font-size: 12px; margin-left: 6px; }
.schedule-time { color: var(--color-accent); font-weight: 500; }
.escalated-badge { margin-left: 8px; }
</style>
