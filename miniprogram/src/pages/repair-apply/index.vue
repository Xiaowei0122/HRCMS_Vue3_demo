<!--
  一键报修 — Navbar + 表单卡片 + 底部固定提交栏
-->
<template>
  <view class="page">
    <PageNavbar title="一键报修" />

    <scroll-view scroll-y class="scroll-body">
      <view class="form-card">
        <view class="form-card-head">
          <view class="form-card-title">
            <SvgIcon name="wrench" :size="22" color="#165DFF" />
            <text>报修信息</text>
          </view>
          <text class="form-card-desc">请详细描述故障情况，以便工程师快速定位问题</text>
        </view>

        <!-- 报修单位 -->
        <view class="form-row">
          <text class="form-row-label"><text class="required">*</text>报修单位</text>
          <input class="form-input" v-model="form.company" placeholder="请输入您的单位名称" placeholder-style="color:#C9CDD4" maxlength="50" @blur="onCompanyBlur" />
        </view>

        <!-- 确认人（非业务/非客户角色本人报修时必选业务对接人，与后端 create_repair 对齐） -->
        <view class="form-row" v-if="showConfirmPicker">
          <text class="form-row-label"><text class="required">*</text>确认人（业务对接人）</text>
          <view class="form-input picker" :class="{ placeholder: !form.confirmUserId && !form.selfOrder }" @click="showConfirmerSheet = true">
            <text>{{ confirmerName || '请选择确认人' }}</text>
            <SvgIcon name="caretRight" :size="14" class="arrow" />
          </view>
          <text v-if="form.selfOrder" class="self-order-hint">工单将直接记入本人名下并开始处理，无需再次接单/指派，确认归档亦由本人完成</text>
        </view>

        <!-- 工单类型 -->
        <view class="form-row">
          <text class="form-row-label"><text class="required">*</text>工单类型</text>
          <view class="radio-group">
            <view v-for="t in workOrderTypes" :key="t" class="radio-item" :class="{ active: form.workOrderType === t }" @click="form.workOrderType = t">{{ t }}</view>
          </view>
        </view>

        <!-- 联系人 / 联系电话 -->
        <view class="form-row-two">
          <view class="form-col">
            <text class="form-row-label"><text class="required">*</text>联系人</text>
            <input class="form-input" v-model="form.contactName" placeholder="联系人姓名" placeholder-style="color:#C9CDD4" maxlength="20" />
          </view>
          <view class="form-col">
            <text class="form-row-label"><text class="required">*</text>联系电话</text>
            <input class="form-input" v-model="form.contactPhone" type="number" placeholder="手机号码" placeholder-style="color:#C9CDD4" maxlength="11" />
          </view>
        </view>

        <!-- 用户地址 -->
        <view class="form-row">
          <view class="form-row-label">
            <text><text class="required">*</text>用户地址</text>
            <text class="locate-btn" @click="getLocation">{{ locating ? '定位中...' : '获取当前位置' }}</text>
          </view>
          <input class="form-input" v-model="form.address" placeholder="请填写设备所在地址，或点击上方定位" placeholder-style="color:#C9CDD4" maxlength="100" />
          <view class="addrbook-link" @click="toggleAddressPicker">
            <SvgIcon name="mapPin" :size="14" color="#165DFF" />
            <text>{{ showAddressPicker ? '收起地址簿' : '从地址簿选择' }}</text>
            <SvgIcon name="caretRight" :size="12" color="#C9CDD4" :class="{ 'addrbook-caret': showAddressPicker }" />
          </view>
          <view v-if="showAddressPicker" class="addrbook-panel">
            <template v-if="addressList.length">
              <view v-for="a in addressList" :key="a.id" class="addrbook-item" @click="pickAddress(a)">
                <view class="addrbook-item-main">
                  <text class="addrbook-name">{{ a.contactName }} · {{ a.contactPhone }}</text>
                  <text class="addrbook-addr">{{ a.address }}</text>
                </view>
                <text v-if="a.isDefault" class="addrbook-default">默认</text>
              </view>
            </template>
            <view v-else class="addrbook-empty" @click="goAddressManage">暂无常用地址，点击去添加</view>
          </view>
        </view>

        <!-- 设备类型 / 紧急程度 -->
        <view class="form-row-two">
          <view class="form-col" v-if="form.workOrderType === '售后上门'">
            <text class="form-row-label"><text class="required">*</text>设备类型</text>
            <view class="form-input picker" :class="{ placeholder: !form.deviceType }" @click="showDeviceSheet = true">
              <text>{{ form.deviceType || '请选择' }}</text>
              <SvgIcon name="caretRight" :size="14" class="arrow" />
            </view>
          </view>
          <view class="form-col">
            <text class="form-row-label"><text class="required">*</text>紧急程度</text>
            <view class="urgency-group">
              <view v-for="it in urgencyLevels" :key="it.value" class="urgency-item" :class="'on-' + it.value" :data-on="form.urgency === it.value" @click="form.urgency = it.value">{{ it.label }}</view>
            </view>
          </view>
        </view>

        <!-- 报修日期 -->
        <view class="form-row">
          <text class="form-row-label"><text class="required">*</text>报修日期</text>
          <view class="form-input picker" :class="{ placeholder: !form.repairDate }" @click="showDateSheet = true">
            <text>{{ form.repairDate || '请选择日期' }}</text>
            <SvgIcon name="calendar" :size="16" class="arrow" />
          </view>
        </view>

        <!-- 基本情况 -->
        <view class="form-row">
          <text class="form-row-label"><text class="required">*</text>基本情况</text>
          <textarea class="form-textarea" v-model="form.description" placeholder="品牌型号、故障现象、期望维修时间等" placeholder-style="color:#C9CDD4" maxlength="500" :auto-height="true" />
          <text class="count">{{ form.description.length }}/500</text>
        </view>

        <!-- 现场照片 -->
        <view class="form-row">
          <text class="form-row-label">现场照片（选填）</text>
          <view class="img-row">
            <view v-for="(img, i) in images" :key="i" class="img-item" @click="previewImage(i)">
              <image :src="img" class="img" mode="aspectFill" />
              <view class="img-del" @click.stop="removeImage(i)"><SvgIcon name="x" :size="14" color="#fff" /></view>
            </view>
            <view v-if="images.length < 3" class="img-add" @click="openPhotoSheet">
              <SvgIcon name="plus" :size="30" color="#C9CDD4" />
              <text class="add-text">添加</text>
            </view>
          </view>
        </view>

        <!-- 预约上门（内部员工可选；不填则进入抢单池） -->
        <template v-if="showReserveSection">
          <view class="reserve-divider">
            <view class="reserve-divider-head">
              <SvgIcon name="calendar" :size="20" color="#165DFF" />
              <text>预约上门（可选）</text>
            </view>
            <text class="reserve-divider-desc">不填则进入抢单池，由工程师自主接单</text>
          </view>

          <view class="form-row">
            <view class="form-row-label">
              <text>预约工程师</text>
              <text v-if="form.engineerId" class="clear-btn" @click="clearEngineer">清除</text>
            </view>
            <view class="form-input picker" :class="{ placeholder: !form.engineerId }" @click="showEngineerSheet = true">
              <text>{{ engineerName || '不选则进入抢单池' }}</text>
              <SvgIcon name="caretRight" :size="14" class="arrow" />
            </view>
          </view>

          <view class="form-row-two">
            <view class="form-col">
              <text class="form-row-label">预约日期</text>
              <view class="form-input picker" :class="{ placeholder: !form.preferredDate }" @click="showReserveDateSheet = true">
                <text>{{ form.preferredDate || '选择日期' }}</text>
                <SvgIcon name="calendar" :size="16" class="arrow" />
              </view>
            </view>
            <view class="form-col">
              <text class="form-row-label">预约时段</text>
              <view class="form-input picker" @click="showSlotSheet = true">
                <text>{{ slotLabelText }}</text>
                <SvgIcon name="caretRight" :size="14" class="arrow" />
              </view>
            </view>
          </view>
        </template>
      </view>
      <view class="safe-bottom" />
    </scroll-view>

    <!-- 底部固定提交栏 -->
    <view class="bottom-bar">
      <button class="primary-btn" :disabled="submitting" @click="handleSubmit">
        <SvgIcon name="wrench" :size="18" color="#fff" />
        <text>{{ submitting ? '提交中...' : '提交报修' }}</text>
      </button>
    </view>

    <!-- 选择器弹层 -->
    <PickerSheet v-model="showConfirmerSheet" title="选择确认人（业务）" :options="confirmerOptions" :value="confirmerPickerValue" @select="onConfirmerSelect" />
    <PickerSheet v-model="showDeviceSheet" title="选择设备类型" :options="deviceOptions" :value="form.deviceType" @select="(v) => form.deviceType = v" />
    <DatePickerSheet v-model="showDateSheet" title="选择报修日期" :value="form.repairDate" @select="(v) => form.repairDate = v" />
    <PickerSheet v-model="showPhotoSheet" title="添加现场照片" :options="photoSourceOptions" value="" @select="onPhotoSourceSelect" />
    <PickerSheet v-model="showEngineerSheet" title="选择预约工程师" :options="engineerOptions" :value="form.engineerId" @select="onEngineerSelect" />
    <DatePickerSheet v-model="showReserveDateSheet" title="选择预约日期" :value="form.preferredDate" :disable-past="true" @select="onReserveDateSelect" />
    <PickerSheet v-model="showSlotSheet" title="选择预约时段" :options="slotOptions" :value="form.preferredTimeSlot" @select="onSlotSelect" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRepairStore } from '@/stores/repair'
import { useAuthStore } from '@/stores/auth'
import { useAddressStore } from '@/stores/address'
import { useDictStore } from '@/stores/dict'
import { uploadFile } from '@/utils/request'
import SvgIcon from '@/components/SvgIcon.vue'
import PageNavbar from '@/components/PageNavbar.vue'
import PickerSheet from '@/components/PickerSheet.vue'
import DatePickerSheet from '@/components/DatePickerSheet.vue'
import { WORK_ORDER_TYPES, DEVICE_TYPES, TIME_SLOTS } from '@/utils/repair-status'
import { AMAP_KEY, AMAP_REGEO_URL } from '@/utils/config'

const repairStore = useRepairStore()
const authStore = useAuthStore()
const addressStore = useAddressStore()
const dictStore = useDictStore()
const router = useRouter()
const submitting = ref(false)
const locating = ref(false)
const images = ref([])
const workOrderTypes = WORK_ORDER_TYPES
const deviceTypes = ref([...DEVICE_TYPES])
const urgencyLevels = [{ label: '紧急', value: 'urgent' }, { label: '一般', value: 'normal' }, { label: '不急', value: 'low' }]

// 确认人（业务用户）—— 非业务/非客户角色本人报修时必选业务对接人
const confirmers = ref([])
const showConfirmerSheet = ref(false)
const showConfirmPicker = computed(() => !authStore.isBusiness && !authStore.isNormalUser)
const confirmerOptions = computed(() => {
  const list = confirmers.value.map(c => ({ label: c.name || c.username || '', value: c.id }))
  if (authStore.isEngineer) list.unshift({ label: '本人工单', value: '__self__' })
  return list
})
const confirmerPickerValue = computed(() => form.value.selfOrder ? '__self__' : form.value.confirmUserId)
const confirmerName = computed(() => {
  if (form.value.selfOrder) return '本人工单'
  const c = confirmers.value.find(x => x.id === form.value.confirmUserId)
  return c ? (c.name || c.username) : ''
})
const onConfirmerSelect = (v) => {
  if (v === '__self__') {
    form.value.selfOrder = true
    form.value.confirmUserId = ''
  } else {
    form.value.selfOrder = false
    form.value.confirmUserId = v
  }
}
const loadConfirmers = async () => {
  if (!showConfirmPicker.value) return
  try {
    const list = await repairStore.fetchConfirmers()
    confirmers.value = Array.isArray(list) ? list : (list?.records || [])
  } catch {
    confirmers.value = []
  }
}

// 地址簿：从常用地址选择回填
const addressList = ref([])
const showAddressPicker = ref(false)

const loadAddressList = async () => {
  try {
    const list = await addressStore.fetchList()
    addressList.value = Array.isArray(list) ? list : []
  } catch {
    addressList.value = []
  }
}

const toggleAddressPicker = () => {
  showAddressPicker.value = !showAddressPicker.value
  if (showAddressPicker.value && !addressList.value.length) loadAddressList()
}

const pickAddress = (a) => {
  form.value.address = a.address || ''
  form.value.contactName = a.contactName || ''
  form.value.contactPhone = a.contactPhone || ''
  showAddressPicker.value = false
  uni.showToast({ title: '已填充地址', icon: 'none' })
}

const goAddressManage = () => router.push('/pages/address/index')

// 设备类型：优先读数据字典（与 CMS 对齐），字典为空回退内置默认
const showDeviceSheet = ref(false)
const deviceOptions = computed(() => deviceTypes.value.map(d => ({ label: d, value: d })))
const loadDeviceTypes = async () => {
  try {
    const list = await dictStore.fetchOptions('设备类型')
    if (Array.isArray(list) && list.length) deviceTypes.value = list
  } catch { /* 字典不可用时沿用内置默认 */ }
}

// 日期 / 照片来源 弹层
const showDateSheet = ref(false)
const showPhotoSheet = ref(false)

const todayStr = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const form = ref({ company: '', contactName: '', contactPhone: '', address: '', workOrderType: '售后上门', deviceType: '', urgency: 'normal', repairDate: todayStr(), description: '', latitude: null, longitude: null, confirmUserId: '', selfOrder: false, engineerId: '', engineerName: '', preferredDate: '', preferredTimeSlot: '全天' })

// 现场照片：拍照 / 相册二选一（联动相机 / 文件选择）
const photoSourceOptions = [{ label: '拍照', value: 'camera' }, { label: '从相册选择', value: 'album' }]
const openPhotoSheet = () => { showPhotoSheet.value = true }
const onPhotoSourceSelect = (source) => {
  uni.chooseImage({ count: 3 - images.value.length, sizeType: ['compressed'], sourceType: [source], success: (res) => { images.value.push(...res.tempFilePaths) } })
}
const previewImage = (i) => { uni.previewImage({ urls: images.value, current: i }) }
const removeImage = (i) => { images.value.splice(i, 1) }

// ── 预约上门（内部员工可选：业务/财务/运营/管理员/超管，排除 normal 与 engineer）──
const showReserveSection = computed(() => authStore.isInternalUser)
const engineers = ref([])
const showEngineerSheet = ref(false)
const showReserveDateSheet = ref(false)
const showSlotSheet = ref(false)
const occupiedSlots = ref([])

const engineerOptions = computed(() => engineers.value.map(e => ({ label: e.name || e.username || '', value: e.id, sub: e.team || '' })))
const engineerName = computed(() => {
  const e = engineers.value.find(x => x.id === form.value.engineerId)
  return e ? (e.name || e.username) : ''
})
const slotLabelText = computed(() => {
  if (!form.value.preferredTimeSlot || form.value.preferredTimeSlot === '全天') return '全天'
  const s = TIME_SLOTS.find(x => x.key === form.value.preferredTimeSlot)
  return s ? s.label : form.value.preferredTimeSlot
})
const slotOptions = computed(() => {
  const list = [{ label: '全天（不预约具体时段）', value: '全天' }]
  for (const s of TIME_SLOTS) {
    const occupied = occupiedSlots.value.includes(s.key)
    list.push({
      label: s.label,
      value: s.key,
      sub: occupied ? `${s.range}（已占用）` : s.range,
      disabled: occupied
    })
  }
  return list
})

const loadEngineers = async () => {
  if (!showReserveSection.value) return
  try {
    engineers.value = await repairStore.fetchEngineers()
  } catch { engineers.value = [] }
}
const onEngineerSelect = (id) => {
  const e = engineers.value.find(x => x.id === id)
  form.value.engineerId = id || ''
  form.value.engineerName = e ? (e.name || e.username) : ''
  loadAvailability()
}
const clearEngineer = () => {
  form.value.engineerId = ''
  form.value.engineerName = ''
  occupiedSlots.value = []
}
const onReserveDateSelect = (d) => {
  form.value.preferredDate = d || ''
  loadAvailability()
}
const onSlotSelect = (key) => { form.value.preferredTimeSlot = key }
const loadAvailability = async () => {
  occupiedSlots.value = []
  if (!form.value.engineerId || !form.value.preferredDate) return
  try {
    const occ = await repairStore.fetchScheduleAvailability({ engineerId: form.value.engineerId, date: form.value.preferredDate })
    occupiedSlots.value = Array.isArray(occ) ? occ : []
    if (form.value.preferredTimeSlot !== '全天' && occupiedSlots.value.includes(form.value.preferredTimeSlot)) {
      form.value.preferredTimeSlot = '全天'
    }
  } catch { occupiedSlots.value = [] }
}

// 单位名失焦：匹配历史工单自动填充基础信息（仅填空字段，用户可改）
const onCompanyBlur = async () => {
  const company = form.value.company.trim()
  if (!company) return
  try {
    const info = await repairStore.lookupCompany(company)
    if (info && info.found) {
      if (!form.value.contactName && info.contact) form.value.contactName = info.contact
      if (!form.value.contactPhone && info.phone) form.value.contactPhone = info.phone
      if (!form.value.address && info.address) form.value.address = info.address
      if (!form.value.deviceType && info.deviceType) form.value.deviceType = info.deviceType
      uni.showToast({ title: '已自动填充历史信息', icon: 'none' })
    }
  } catch { /* handled */ }
}

// 获取当前位置 → 高德逆地理编码回填地址
const getLocation = () => {
  locating.value = true
  uni.getLocation({
    type: 'gcj02',
    isHighAccuracy: true,
    success: (res) => {
      form.value.latitude = res.latitude
      form.value.longitude = res.longitude
      reverseGeocode(res.longitude, res.latitude)
    },
    fail: () => {
      uni.showToast({ title: '定位失败，请检查定位权限', icon: 'none' })
    },
    complete: () => { locating.value = false }
  })
}

const reverseGeocode = (lng, lat) => {
  if (!AMAP_KEY) {
    uni.showToast({ title: '定位成功，请手动填写地址', icon: 'none' })
    return
  }
  uni.request({
    url: `${AMAP_REGEO_URL}?location=${lng},${lat}&key=${AMAP_KEY}`,
    success: (res) => {
      const addr = res.data && res.data.regeocode && res.data.regeocode.formatted_address
      if (addr) {
        form.value.address = addr
        uni.showToast({ title: '地址已回填', icon: 'none' })
      }
    },
    fail: () => {
      uni.showToast({ title: '地址解析失败，请手动填写', icon: 'none' })
    }
  })
}

const validate = () => {
  const f = form.value
  if (!f.company.trim()) return uni.showToast({ title: '请填写报修单位', icon: 'none' }), false
  if (!f.contactName.trim()) return uni.showToast({ title: '请填写联系人', icon: 'none' }), false
  if (!f.contactPhone || !/^1\d{10}$/.test(f.contactPhone)) return uni.showToast({ title: '请填写正确手机号', icon: 'none' }), false
  if (!f.address.trim()) return uni.showToast({ title: '请填写用户地址', icon: 'none' }), false
  if (f.workOrderType === '售后上门' && !f.deviceType) return uni.showToast({ title: '请选择设备类型', icon: 'none' }), false
  if (!f.repairDate) return uni.showToast({ title: '请选择日期', icon: 'none' }), false
  if (!f.description.trim()) return uni.showToast({ title: '请描述基本情况', icon: 'none' }), false
  if (showConfirmPicker.value && !f.selfOrder && !f.confirmUserId) return uni.showToast({ title: '请选择确认人', icon: 'none' }), false
  return true
}

const handleSubmit = async () => {
  if (!validate()) return
  submitting.value = true
  try {
    const urls = []
    for (const img of images.value) { try { const r = await uploadFile(img); urls.push(r.data?.url || r.url || '') } catch {} }
    await repairStore.createRepair({
      company: form.value.company.trim(),
      contactName: form.value.contactName.trim(),
      contactPhone: form.value.contactPhone,
      address: form.value.address.trim(),
      workOrderType: form.value.workOrderType,
      deviceType: form.value.deviceType,
      latitude: form.value.latitude,
      longitude: form.value.longitude,
      urgency: form.value.urgency,
      repairDate: form.value.repairDate,
      description: form.value.description.trim(),
      images: urls,
      confirmUserId: form.value.confirmUserId || undefined,
      confirmUserName: form.value.selfOrder ? undefined : confirmerName.value,
      selfOrder: form.value.selfOrder || undefined,
      engineerId: form.value.engineerId,
      engineerName: form.value.engineerName,
      preferredDate: form.value.preferredDate,
      preferredTimeSlot: form.value.preferredTimeSlot || '全天'
    })
    uni.showToast({ title: '报修提交成功', icon: 'success' })
    setTimeout(() => { form.value = { company: '', contactName: '', contactPhone: '', address: '', workOrderType: '售后上门', deviceType: '', urgency: 'normal', repairDate: todayStr(), description: '', latitude: null, longitude: null, confirmUserId: '', selfOrder: false, engineerId: '', engineerName: '', preferredDate: '', preferredTimeSlot: '全天' }; images.value = []; occupiedSlots.value = [] }, 800)
  } catch (e) { console.error(e) }
  finally { submitting.value = false }
}

onMounted(() => {
  loadConfirmers()
  loadDeviceTypes()
  loadEngineers()
})
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; }
.scroll-body { flex: 1; }

.form-card {
  margin: 24rpx;
  background: #fff;
  border-radius: 32rpx;
  padding: 36rpx 32rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}

.form-card-head { margin-bottom: 8rpx; }
.form-card-title {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #1D2129;
  margin-bottom: 8rpx;
}
.form-card-desc { font-size: 24rpx; color: #86909C; display: block; }

.form-row { margin-top: 28rpx; }
.form-row-two { display: flex; gap: 16rpx; margin-top: 28rpx; }
.form-col { flex: 1; min-width: 0; }

.form-row-label {
  font-size: 26rpx;
  color: #4E5969;
  font-weight: 500;
  margin-bottom: 12rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.required { color: #F53F3F; }
.locate-btn { font-size: 22rpx; color: #165DFF; font-weight: 500; }
.self-order-hint {
  display: block;
  margin-top: 12rpx;
  font-size: 22rpx;
  color: #165DFF;
  line-height: 1.5;
}

/* 地址簿 */
.addrbook-link {
  display: flex;
  align-items: center;
  gap: 6rpx;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #165DFF;
  font-weight: 500;
}
.addrbook-caret { transform: rotate(90deg); }
.addrbook-panel {
  margin-top: 16rpx;
  background: #F7F8FA;
  border: 1px solid #E5E6EB;
  border-radius: 16rpx;
  overflow: hidden;
}
.addrbook-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid #EEF0F3;
  &:last-child { border-bottom: none; }
  &:active { background: #EFF3FB; }
}
.addrbook-item-main { flex: 1; min-width: 0; margin-right: 16rpx; }
.addrbook-name { font-size: 26rpx; color: #1D2129; font-weight: 500; display: block; }
.addrbook-addr {
  font-size: 22rpx;
  color: #86909C;
  display: block;
  margin-top: 6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.addrbook-default {
  flex-shrink: 0;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  color: #165DFF;
  background: #E8F3FF;
  font-weight: 600;
}
.addrbook-empty {
  padding: 28rpx 24rpx;
  font-size: 24rpx;
  color: #86909C;
  text-align: center;
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #1D2129;
  box-sizing: border-box;
}
.form-input.picker { display: flex; align-items: center; justify-content: space-between; }
.form-input.placeholder { color: #C9CDD4; }
.arrow { color: #86909C; transform: rotate(90deg); flex-shrink: 0; }

/* 工单类型 — 分段选择 */
.radio-group { display: flex; background: #F2F3F5; border-radius: 16rpx; padding: 6rpx; gap: 6rpx; }
.radio-item {
  flex: 1;
  text-align: center;
  padding: 18rpx 0;
  font-size: 26rpx;
  color: #4E5969;
  border-radius: 12rpx;
  font-weight: 500;
  transition: all 0.25s ease;
  &.active {
    background: linear-gradient(135deg, #165DFF, #4080FF);
    color: #fff;
    font-weight: 600;
    box-shadow: 0 4rpx 12rpx rgba(22, 93, 255, 0.3);
  }
}

/* 紧急程度 — 按等级着色描边胶囊 */
.urgency-group { display: flex; gap: 8rpx; }
.urgency-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 24rpx;
  color: #4E5969;
  border-radius: 14rpx;
  border: 1.5px solid #E5E6EB;
  background: #fff;
  font-weight: 500;
  transition: all 0.2s ease;

  &[data-on='true'] { font-weight: 600; }
  &.on-urgent[data-on='true']  { background: #FFF1F0; border-color: #F53F3F; color: #F53F3F; }
  &.on-normal[data-on='true']  { background: #E8F3FF; border-color: #165DFF; color: #165DFF; }
  &.on-low[data-on='true']     { background: #E8FFEA; border-color: #00B42A; color: #00B42A; }
}

.form-textarea {
  width: 100%;
  min-height: 180rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  color: #1D2129;
  box-sizing: border-box;
  line-height: 1.6;
}
.count { font-size: 22rpx; color: #86909C; text-align: right; display: block; margin-top: 8rpx; }

.img-row { display: flex; flex-wrap: wrap; gap: 16rpx; }
.img-item { width: 200rpx; height: 200rpx; border-radius: 16rpx; position: relative; overflow: hidden; }
.img { width: 100%; height: 100%; }
.img-del { position: absolute; top: 8rpx; right: 8rpx; width: 40rpx; height: 40rpx; border-radius: 50%; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; }
.img-add { width: 200rpx; height: 200rpx; border-radius: 16rpx; background: #F7F8FA; border: 2rpx dashed #C9CDD4; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8rpx; }
.add-text { font-size: 22rpx; color: #86909C; }

/* 底部固定提交栏 */
.bottom-bar {
  flex-shrink: 0;
  padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F2F3F5;
}
.primary-btn {
  width: 100%;
  height: 92rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);
  &:active { opacity: 0.9; transform: scale(0.98); }
  &[disabled] { background: #C9CDD4; box-shadow: none; }
}

.safe-bottom { height: 24rpx; }

/* 预约上门分区 */
.reserve-divider {
  margin-top: 36rpx;
  padding: 24rpx;
  background: #F0F6FF;
  border-radius: 16rpx;
}
.reserve-divider-head {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #1D2129;
}
.reserve-divider-desc {
  display: block;
  font-size: 22rpx;
  color: #86909C;
  margin-top: 8rpx;
}
.clear-btn {
  font-size: 24rpx;
  color: #165DFF;
  font-weight: 500;
}
</style>
