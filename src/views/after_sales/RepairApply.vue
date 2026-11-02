<template>
  <div class="repair-apply-container">
    <el-card class="form-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title"><el-icon><EditPen /></el-icon> 新增报修工单</span>
          <el-tag type="info" effect="plain">单号自动生成</el-tag>
        </div>
      </template>

      <el-form :model="repairForm" :rules="rules" ref="formRef" label-width="100px" label-position="top">
        <el-row :gutter="40">
          <!-- 左侧：基本信息 -->
          <el-col :span="12" :xs="24">
            <el-form-item label="报修单位" prop="company">
              <el-input v-model="repairForm.company" placeholder="请输入单位全称" @blur="onCompanyBlur" />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="工单类型" prop="workOrderType">
                  <el-select v-model="repairForm.workOrderType" style="width: 100%">
                    <el-option v-for="t in workOrderTypes" :key="t" :label="t" :value="t" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12" v-if="repairForm.workOrderType === '售后上门'">
                <el-form-item label="设备类型" prop="deviceType">
                  <el-select v-model="repairForm.deviceType" style="width: 100%">
                    <el-option v-for="d in deviceTypes" :key="d" :label="d" :value="d" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="联系人" prop="contact">
                  <el-input v-model="repairForm.contact" placeholder="姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话" prop="phone">
                  <el-input v-model="repairForm.phone" placeholder="手机号" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="用户地址" prop="address">
              <el-input v-model="repairForm.address" type="textarea" :rows="2" placeholder="具体街道、楼层、房间号" />
            </el-form-item>

            <el-form-item label="上门费用（已协商好，选填）">
              <el-input-number v-model="repairForm.feeAmount" :min="0" :precision="2" :controls="false" placeholder="金额，如已协商好请填写" style="width: 100%" />
            </el-form-item>
          </el-col>

          <!-- 右侧：故障描述 -->
          <el-col :span="12" :xs="24">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="报修日期">
                  <el-date-picker v-model="repairForm.date" type="date" style="width: 100%" readonly />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="紧急程度" prop="priority">
                  <el-select v-model="repairForm.priority" style="width: 100%">
                    <el-option
                      v-for="p in priorityOptions"
                      :key="p"
                      :label="p + (priorityHints[p] || '')"
                      :value="p"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="基本情况 / 故障描述" prop="description">
              <el-input 
                v-model="repairForm.description" 
                type="textarea" 
                :rows="5" 
                placeholder="请详细描述设备故障现象，如：打印有黑线、机器报错代码C-2557等" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 现场照片（选填，最多 3 张） -->
        <el-form-item label="现场照片">
          <div class="img-uploader">
            <div v-for="(img, i) in repairForm.images" :key="i" class="img-item">
              <el-image :src="img" fit="cover" class="img-preview" :preview-src-list="repairForm.images" :initial-index="i" />
              <el-icon class="img-remove" @click="repairForm.images.splice(i, 1)"><Close /></el-icon>
            </div>
            <el-upload v-if="repairForm.images.length < 3" :show-file-list="false" :http-request="handleImgUpload" accept="image/*">
              <div class="img-add"><el-icon><Plus /></el-icon></div>
            </el-upload>
          </div>
        </el-form-item>

        <!-- 预约上门（内部员工/管理员可选；普通用户不可见，不填则进入抢单池） -->
        <el-row v-if="isInternal">
          <el-col :span="24">
            <el-divider content-position="left">预约上门（可选，不填则进入抢单池）</el-divider>
            <EngineerSlotPicker
              v-model:engineer-id="repairForm.engineerId"
              v-model:engineer-name="repairForm.engineerName"
              v-model:date="repairForm.preferredDate"
              v-model:time-slot="repairForm.preferredTimeSlot"
            />
          </el-col>
        </el-row>

        <!-- 确认人（代录：工程师/管理员需指定负责确认的业务） -->
        <el-row v-if="isEngineer || isAdmin">
          <el-col :span="12">
            <el-form-item label="确认人（业务）" required>
              <el-select v-model="repairForm.confirmUserId" placeholder="请选择负责确认的业务" style="width: 100%" filterable>
                <el-option v-if="isEngineer" label="本人工单" value="__self__" />
                <el-option v-for="c in confirmers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
              <div v-if="isSelfOrder" class="self-order-hint">
                工单将直接记入本人名下并开始处理，无需再次接单 / 指派
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-footer">
          <el-button size="large" @click="resetForm">重置</el-button>
          <el-button type="primary" size="large" :loading="submitting" @click="submitRepair">
            立即提交报修
          </el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 提交成功后的弹窗 -->
    <el-dialog v-model="successVisible" title="报修提交成功" width="400px" append-to-body align-center>
      <div class="success-box">
        <el-result icon="success" title="工单已生成" sub-title="请等待工程师接单">
          <template #extra>
            <p class="order-no">工单号：<strong>{{ generatedOrderNo }}</strong></p>
            <el-button type="primary" @click="goToList">查看我的报修</el-button>
          </template>
        </el-result>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { EditPen, Plus, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createRepair, lookupCompany, getServerTime, getConfirmers } from '@/api/modules/repairs'
import { getDictOptions } from '@/api/modules/dict'
import { getUserInfo } from '@/utils/auth'
import { uploadFile } from '@/api/modules/upload'
import EngineerSlotPicker from '@/components/EngineerSlotPicker.vue'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const successVisible = ref(false)
const generatedOrderNo = ref('')

// 角色判定：普通用户（外部）不可见预约工程师区块
const isAdmin = computed(() => (getUserInfo()?.rank ?? 99) <= 1)
const isEngineer = computed(() => getUserInfo()?.roleCode === 'engineer')
const isInternal = computed(() => (getUserInfo()?.roleCode ?? 'normal') !== 'normal')
const isSelfOrder = computed(() => isEngineer.value && repairForm.confirmUserId === '__self__')

// 确认人候选（业务用户，代录时选择）
const confirmers = ref([])
const loadConfirmers = async () => {
  if (!isEngineer.value && !isAdmin.value) return
  try {
    const res = await getConfirmers()
    confirmers.value = Array.isArray(res) ? res : (res.records || [])
  } catch {
    confirmers.value = []
  }
}

// 表单数据
const repairForm = reactive({
  company: '',
  contact: '',
  phone: '',
  address: '',
  date: new Date(),
  priority: '普通',
  description: '',
  workOrderType: '售后上门',
  deviceType: '',
  feeAmount: null,
  preferredDate: '',
  preferredTimeSlot: '全天',
  engineerId: '',
  engineerName: '',
  confirmUserId: '',
  images: []
})

// 业务下拉：优先读数据字典，字典为空时回退内置默认值
const deviceTypes = ref(['电脑', '打印机', '复印机', '投影仪', '扫描仪', '网络设备', '大屏', '其他'])
const workOrderTypes = ref(['售后上门', '协助送货'])
const priorityOptions = ref(['普通', '紧急', '特急'])
const priorityHints = { '普通': ' (24小时内)', '紧急': ' (4小时内)', '特急': ' (立即处理)' }

const loadDicts = async () => {
  try {
    const [dev, wot, pri] = await Promise.all([
      getDictOptions('设备类型'),
      getDictOptions('工单类型'),
      getDictOptions('优先级'),
    ])
    if (Array.isArray(dev) && dev.length) deviceTypes.value = dev.map(o => o.value)
    if (Array.isArray(wot) && wot.length) workOrderTypes.value = wot.map(o => o.value)
    if (Array.isArray(pri) && pri.length) priorityOptions.value = pri.map(o => o.value)
  } catch { /* 字典不可用时沿用内置默认 */ }
}

// 报修日期对齐服务器北京时间（报单时间以服务器为准）
const initServerTime = async () => {
  try {
    const t = await getServerTime()
    if (t?.date) repairForm.date = new Date(t.date + 'T00:00:00')
  } catch { /* 后端不可用时回退本地时间 */ }
}

onMounted(() => {
  loadDicts()
  initServerTime()
  loadConfirmers()
})

// 单位名失焦：匹配历史工单自动填充（仅填空字段，可修改）
const onCompanyBlur = async () => {
  const company = repairForm.company.trim()
  if (!company) return
  try {
    const info = await lookupCompany(company)
    if (info?.found) {
      if (!repairForm.contact && info.contact) repairForm.contact = info.contact
      if (!repairForm.phone && info.phone) repairForm.phone = info.phone
      if (!repairForm.address && info.address) repairForm.address = info.address
      if (!repairForm.deviceType && info.deviceType) repairForm.deviceType = info.deviceType
      ElMessage.success('已自动填充历史信息')
    }
  } catch { /* ignore */ }
}

const handleImgUpload = async ({ file, onSuccess, onError }) => {
  try {
    const res = await uploadFile(file, 'repairs')
    console.log('[repair upload] 结果:', res)
    if (res && res.url) {
      repairForm.images.push(res.url)
      onSuccess && onSuccess(res)
    } else {
      console.warn('[repair upload] 未返回 url')
      onError && onError(new Error('no url'))
    }
  } catch (e) {
    console.error('[repair upload] 失败:', e)
    onError && onError(e)
  }
}

// 校验规则
const rules = {
  company: [{ required: true, message: '请输入报修单位', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入电话', trigger: 'blur' }],
  description: [{ required: true, message: '请填写故障情况', trigger: 'blur' }]
}

const submitRepair = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请完善报修信息')
    return
  }
  if (repairForm.workOrderType === '售后上门' && !repairForm.deviceType) {
    ElMessage.warning('请选择设备类型')
    return
  }

  if ((isEngineer.value || isAdmin.value) && !repairForm.confirmUserId) {
    ElMessage.warning('请选择确认人')
    return
  }
  const selfOrder = isSelfOrder.value
  submitting.value = true
  try {
    const confirmUser = selfOrder ? null : confirmers.value.find(c => c.id === repairForm.confirmUserId)
    const payload = {
      company: repairForm.company,
      contact: repairForm.contact,
      phone: repairForm.phone,
      address: repairForm.address,
      priority: repairForm.priority,
      description: repairForm.description,
      workOrderType: repairForm.workOrderType,
      deviceType: repairForm.deviceType,
      preferredTimeSlot: repairForm.preferredTimeSlot,
      preferredDate: repairForm.preferredDate || '',
      engineerId: repairForm.engineerId || '',
      engineerName: repairForm.engineerName || '',
      images: repairForm.images,
      ...(selfOrder
        ? { selfOrder: true }
        : { confirmUserId: repairForm.confirmUserId, confirmUserName: confirmUser?.name || '' })
    }
    if (repairForm.feeAmount != null && repairForm.feeAmount !== '') {
      payload.fee = { mode: 'agreed', amount: Number(repairForm.feeAmount) }
    }
    const res = await createRepair(payload)
    generatedOrderNo.value = res.orderNo
    successVisible.value = true
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  formRef.value.resetFields()
  repairForm.priority = '普通'
  repairForm.workOrderType = '售后上门'
  repairForm.deviceType = ''
  repairForm.feeAmount = null
  repairForm.preferredDate = ''
  repairForm.preferredTimeSlot = '全天'
  repairForm.engineerId = ''
  repairForm.engineerName = ''
  repairForm.confirmUserId = ''
  repairForm.images = []
}

const goToList = () => {
  successVisible.value = false
  router.push('/after_sales/my-repairs')
}
</script>

<style scoped>
.repair-apply-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header .title {
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}
.form-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
}
.self-order-hint {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--color-accent);
  background: var(--color-info-bg, #E8F3FF);
  padding: 6px 10px;
  border-radius: 4px;
}
.success-box {
  text-align: center;
}
.order-no {
  background: var(--bg-muted);
  padding: 10px;
  border-radius: 4px;
  color: var(--color-accent);
  margin-bottom: 20px;
}

.img-uploader { display: flex; flex-wrap: wrap; gap: 12px; }
.img-item { position: relative; }
.img-preview { width: 96px; height: 96px; border-radius: 6px; border: 1px solid var(--border-color); }
.img-remove { position: absolute; top: -6px; right: -6px; color: #fff; background: var(--color-danger, #f56c6c); border-radius: 50%; cursor: pointer; font-size: 12px; padding: 2px; }
.img-add { width: 96px; height: 96px; border: 1px dashed #d9d9d9; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #8c939d; font-size: 28px; cursor: pointer; }
.img-add:hover { border-color: #165DFF; color: #165DFF; }
</style>