<template>
  <div class="vehicle-management">
    <!-- 顶部 KPI -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6">
        <div class="kpi-card">
          <span class="kpi-label">车辆总数</span>
          <span class="kpi-value" style="color: #3B82F6">{{ stats.total }}</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <span class="kpi-label">在用车辆</span>
          <span class="kpi-value" style="color: #059669">{{ stats.inUse }}</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <span class="kpi-label">即将到期（30 天内）</span>
          <span class="kpi-value" style="color: #D97706">{{ stats.soon }}</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <span class="kpi-label">已逾期</span>
          <span class="kpi-value" style="color: #DC2626">{{ stats.overdue }}</span>
        </div>
      </el-col>
    </el-row>

    <!-- 到期提醒条 -->
    <el-card v-if="expiringItems.length" shadow="never" class="expiring-card">
      <template #header>
        <div class="expiring-header">
          <span>到期提醒（{{ expiringItems.length }} 项）</span>
          <el-tag size="small" type="info">{{ expiringDays }} 天内</el-tag>
        </div>
      </template>
      <div class="expiring-list">
        <div v-for="(e, i) in expiringItems" :key="i" class="expiring-item" @click="openDetailById(e.vehicleId)">
          <el-tag :type="e.level === 'overdue' ? 'danger' : 'warning'" size="small" effect="dark">
            {{ e.plateNo }} · {{ e.label }}
          </el-tag>
          <span class="expiring-date">{{ e.dueDate }}（{{ daysText(e.daysLeft) }}）</span>
          <span class="expiring-detail">{{ e.detail }}</span>
        </div>
      </div>
    </el-card>

    <!-- 车辆列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="table-header">
          <div class="left-group">
            <el-input
              v-model="query.kw"
              placeholder="车牌 / 品牌 / 负责人"
              clearable
              style="width: 200px"
              @keyup.enter="fetchList"
              @clear="fetchList"
            />
            <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px; margin-left: 12px" @change="fetchList">
              <el-option v-for="s in STATUS_OPTIONS" :key="s" :label="s" :value="s" />
            </el-select>
            <el-button icon="Search" style="margin-left: 12px" @click="fetchList">查询</el-button>
          </div>
          <el-button type="primary" icon="Plus" @click="openCreate">新增车辆</el-button>
        </div>
      </template>

      <el-table :data="vehicleList" v-loading="loading" size="default">
        <el-table-column prop="plateNo" label="车牌" width="130" />
        <el-table-column label="品牌型号" min-width="150">
          <template #default="{ row }">{{ row.brand }} {{ row.model }}</template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="responsible" label="负责人" width="90" />
        <el-table-column label="下次保养" width="160">
          <template #default="{ row }">
            <template v-if="row.nextMaintenanceDate">
              <div>{{ row.nextMaintenanceDate }}</div>
              <div class="sub">{{ row.nextMaintenanceKm || 0 }} km</div>
            </template>
            <span v-else class="muted">未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="年检到期" width="170">
          <template #default="{ row }">
            <template v-if="row.annualInspectionDate">
              <el-tag :type="dateTagType(row.annualInspectionDate)" size="small">年检</el-tag>
              <div class="sub">{{ dateText(row.annualInspectionDate) }}</div>
            </template>
            <span v-else class="muted">未登记</span>
          </template>
        </el-table-column>
        <el-table-column label="保险到期" width="170">
          <template #default="{ row }">
            <template v-if="nearestInsurance(row.insurances)">
              <el-tag :type="dateTagType(nearestInsurance(row.insurances).endDate)" size="small">
                {{ nearestInsurance(row.insurances).type }}
              </el-tag>
              <div class="sub">{{ dateText(nearestInsurance(row.insurances).endDate) }}</div>
            </template>
            <span v-else class="muted">未登记</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">详情</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="query.size"
        :current-page="query.page"
        @current-change="onPageChange"
      />
    </el-card>

    <!-- 新增 / 编辑车辆 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑车辆' : '新增车辆'" width="640px" append-to-body>
      <el-form :model="form" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="车牌号" required>
              <el-input v-model="form.plateNo" placeholder="例如：粤B·F8K21" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车辆类型">
              <el-select v-model="form.vehicleType" style="width: 100%">
                <el-option v-for="t in VEHICLE_TYPES" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-input v-model="form.brand" placeholder="例如：五菱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="form.model" placeholder="例如：宏光S" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="车架号(VIN)">
              <el-input v-model="form.vin" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发动机号">
              <el-input v-model="form.engineNo" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购买日期">
              <el-date-picker v-model="form.purchaseDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="注册日期">
              <el-date-picker v-model="form.registerDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="使用部门">
              <el-input v-model="form.department" placeholder="例如：售后部" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人">
              <el-input v-model="form.responsible" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="当前里程">
              <el-input-number v-model="form.mileage" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="s in STATUS_OPTIONS" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="保险单">
          <div style="width: 100%">
            <div v-if="form.insurances.length" class="form-insurance-list">
              <el-tag
                v-for="(ins, i) in form.insurances"
                :key="i"
                closable
                class="form-insurance-tag"
                @click="openFormInsurance(i)"
                @close="form.insurances.splice(i, 1)"
              >
                {{ ins.type }} · {{ ins.endDate || '未设到期' }}
              </el-tag>
            </div>
            <el-button size="small" icon="Plus" @click="openFormInsurance()">添加保单</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVehicle">{{ isEdit ? '保存修改' : '保存' }}</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="drawerVisible" :title="detail.plateNo || '车辆详情'" size="620px" append-to-body>
      <el-tabs v-model="detailTab">
        <el-tab-pane label="基本信息" name="info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="车牌号">{{ detail.plateNo }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ detail.vehicleType }}</el-descriptions-item>
            <el-descriptions-item label="品牌型号">{{ detail.brand }} {{ detail.model }}</el-descriptions-item>
            <el-descriptions-item label="状态">{{ detail.status }}</el-descriptions-item>
            <el-descriptions-item label="使用部门">{{ detail.department || '—' }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ detail.responsible || '—' }}</el-descriptions-item>
            <el-descriptions-item label="当前里程">{{ detail.mileage || 0 }} km</el-descriptions-item>
            <el-descriptions-item label="购买日期">{{ detail.purchaseDate || '—' }}</el-descriptions-item>
            <el-descriptions-item label="车架号">{{ detail.vin || '—' }}</el-descriptions-item>
            <el-descriptions-item label="发动机号">{{ detail.engineNo || '—' }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ detail.remark || '—' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="保险" name="insurance">
          <div class="pane-toolbar">
            <span class="pane-title">保单列表</span>
            <el-button size="small" type="primary" icon="Plus" @click="openInsurance()">添加保单</el-button>
          </div>
          <el-table :data="detail.insurances || []" size="small">
            <el-table-column prop="type" label="险种" width="90" />
            <el-table-column prop="insurer" label="保险公司" width="110" />
            <el-table-column prop="policyNo" label="保单号" min-width="130" />
            <el-table-column label="保费" width="90" align="right">
              <template #default="{ row }">￥{{ money(row.premium) }}</template>
            </el-table-column>
            <el-table-column label="有效期" width="190">
              <template #default="{ row }">
                <el-tag :type="dateTagType(row.endDate)" size="small">{{ dateText(row.endDate) }}</el-tag>
                <div class="sub">{{ row.startDate }} ~ {{ row.endDate }}</div>
              </template>
            </el-table-column>
            <el-table-column label="凭证" width="80">
              <template #default="{ row }">
                <el-button v-if="row.certs && row.certs.length" link type="primary" @click="previewCerts(row.certs)">查看</el-button>
                <span v-else class="muted">无</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openInsurance(row)">编辑</el-button>
                <el-button link type="danger" @click="handleDeleteInsurance(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="保养与年检" name="maintenance">
          <div class="pane-toolbar">
            <span class="pane-title">年检</span>
            <el-button size="small" type="primary" icon="Edit" @click="openInspection">更新年检</el-button>
          </div>
          <div class="info-line">
            <el-tag v-if="detail.annualInspectionDate" :type="dateTagType(detail.annualInspectionDate)" size="small">
              {{ dateText(detail.annualInspectionDate) }}
            </el-tag>
            <span v-else class="muted">未登记</span>
            <el-button v-if="detail.annualInspectionCerts && detail.annualInspectionCerts.length" link type="primary" @click="previewCerts(detail.annualInspectionCerts)">
              凭证
            </el-button>
          </div>

          <div class="pane-toolbar" style="margin-top: 20px">
            <span class="pane-title">下次保养</span>
            <el-button size="small" type="primary" icon="Edit" @click="openPlan">设置</el-button>
          </div>
          <div class="info-line">
            <span>{{ detail.nextMaintenanceDate || '未设置' }}</span>
            <span class="sub" style="margin-left: 12px">{{ detail.nextMaintenanceKm || 0 }} km</span>
          </div>

          <div class="pane-toolbar" style="margin-top: 20px">
            <span class="pane-title">保养记录</span>
            <el-button size="small" type="primary" icon="Plus" @click="maintenanceVisible = true">添加记录</el-button>
          </div>
          <el-table :data="detail.maintenance || []" size="small">
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="km" label="里程(km)" width="90" align="right" />
            <el-table-column prop="item" label="项目" min-width="120" />
            <el-table-column label="费用" width="90" align="right">
              <template #default="{ row }">￥{{ money(row.cost) }}</template>
            </el-table-column>
            <el-table-column prop="vendor" label="服务商" width="100" />
            <el-table-column label="操作" width="70" fixed="right">
              <template #default="{ row }">
                <el-button link type="danger" @click="handleDeleteMaintenance(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-drawer>

    <!-- 保单编辑 -->
    <el-dialog v-model="insuranceVisible" :title="insuranceEditingId ? '编辑保单' : '添加保单'" width="560px" append-to-body>
      <el-form :model="insuranceForm" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="险种">
              <el-select v-model="insuranceForm.type" style="width: 100%">
                <el-option v-for="t in INSURANCE_TYPES" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保险公司">
              <el-input v-model="insuranceForm.insurer" placeholder="例如：平安保险" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="保单号">
          <el-input v-model="insuranceForm.policyNo" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="保费(元)">
              <el-input-number v-model="insuranceForm.premium" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注">
              <el-input v-model="insuranceForm.remark" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生效日期">
              <el-date-picker v-model="insuranceForm.startDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到期日期">
              <el-date-picker v-model="insuranceForm.endDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="保险凭证">
          <el-upload :show-file-list="false" :http-request="(opt) => uploadCert(opt, insuranceForm.certs)" accept="image/*,.pdf">
            <el-button size="small" icon="Upload">上传凭证</el-button>
          </el-upload>
          <div v-if="insuranceForm.certs.length" class="cert-list">
            <div v-for="(c, i) in insuranceForm.certs" :key="c" class="cert-item">
              <el-image :src="c" fit="cover" class="cert-img" :preview-src-list="insuranceForm.certs" :initial-index="i" />
              <el-icon class="cert-del" @click="insuranceForm.certs.splice(i, 1)"><Close /></el-icon>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="insuranceVisible = false">取消</el-button>
        <el-button type="primary" @click="saveInsurance">保存</el-button>
      </template>
    </el-dialog>

    <!-- 年检编辑 -->
    <el-dialog v-model="inspectionVisible" title="更新年检" width="500px" append-to-body>
      <el-form :model="inspectionForm" label-width="90px">
        <el-form-item label="年检到期">
          <el-date-picker v-model="inspectionForm.annualInspectionDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="年检凭证">
          <el-upload :show-file-list="false" :http-request="(opt) => uploadCert(opt, inspectionForm.certs)" accept="image/*,.pdf">
            <el-button size="small" icon="Upload">上传凭证</el-button>
          </el-upload>
          <div v-if="inspectionForm.certs.length" class="cert-list">
            <div v-for="(c, i) in inspectionForm.certs" :key="c" class="cert-item">
              <el-image :src="c" fit="cover" class="cert-img" :preview-src-list="inspectionForm.certs" :initial-index="i" />
              <el-icon class="cert-del" @click="inspectionForm.certs.splice(i, 1)"><Close /></el-icon>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="inspectionVisible = false">取消</el-button>
        <el-button type="primary" @click="saveInspection">保存</el-button>
      </template>
    </el-dialog>

    <!-- 保养计划 -->
    <el-dialog v-model="planVisible" title="设置下次保养" width="480px" append-to-body>
      <el-form :model="planForm" label-width="110px">
        <el-form-item label="下次保养日期">
          <el-date-picker v-model="planForm.nextMaintenanceDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="下次保养里程">
          <el-input-number v-model="planForm.nextMaintenanceKm" :min="0" :step="1000" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlan">保存</el-button>
      </template>
    </el-dialog>

    <!-- 保养记录 -->
    <el-dialog v-model="maintenanceVisible" title="添加保养记录" width="520px" append-to-body>
      <el-form :model="maintenanceForm" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="保养日期">
              <el-date-picker v-model="maintenanceForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="里程(km)">
              <el-input-number v-model="maintenanceForm.km" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="保养项目">
          <el-input v-model="maintenanceForm.item" placeholder="例如：更换机油机滤" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="费用(元)">
              <el-input-number v-model="maintenanceForm.cost" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务商">
              <el-input v-model="maintenanceForm.vendor" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="maintenanceForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="maintenanceVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMaintenance">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Upload, Close } from '@element-plus/icons-vue'
import {
  getVehicleList, getVehicleExpiring, getVehicleDetail,
  createVehicle, updateVehicle, deleteVehicle,
  addInsurance, updateInsurance, deleteInsurance,
  addVehicleMaintenance, deleteVehicleMaintenance, updateVehicleInspection
} from '@/api/modules/finance'
import { uploadFile } from '@/api/modules/upload'

const STATUS_OPTIONS = ['在用', '闲置', '维修', '已处置']
const VEHICLE_TYPES = ['面包车', '轿车', 'SUV', '货车', '其他']
const INSURANCE_TYPES = ['交强险', '商业险', '车船税', '其他']
const expiringDays = 30

const loading = ref(false)
const vehicleList = ref([])
const total = ref(0)
const query = reactive({ page: 1, size: 20, status: '', kw: '' })

const stats = reactive({ total: 0, inUse: 0, soon: 0, overdue: 0 })
const expiringItems = ref([])

// 车辆表单
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = reactive({
  plateNo: '', brand: '', model: '', vehicleType: '面包车', vin: '', engineNo: '',
  purchaseDate: '', registerDate: '', department: '', responsible: '',
  mileage: 0, status: '在用', img: '', remark: '', insurances: [],
})

// 详情抽屉
const drawerVisible = ref(false)
const detailTab = ref('info')
const detail = reactive({ id: '', plateNo: '', insurances: [], maintenance: [], annualInspectionCerts: [] })

// 保单
const insuranceVisible = ref(false)
const insuranceEditingId = ref(null)
const insuranceForm = reactive({ type: '商业险', insurer: '', policyNo: '', premium: 0, startDate: '', endDate: '', certs: [], remark: '' })
const insuranceMode = ref('detail')  // 'detail' 详情抽屉 | 'form' 车辆表单
const insuranceFormIndex = ref(null)

// 年检
const inspectionVisible = ref(false)
const inspectionForm = reactive({ annualInspectionDate: '', certs: [] })

// 保养计划
const planVisible = ref(false)
const planForm = reactive({ nextMaintenanceDate: '', nextMaintenanceKm: 0 })

// 保养记录
const maintenanceVisible = ref(false)
const maintenanceForm = reactive({ date: '', km: 0, item: '', cost: 0, vendor: '', remark: '' })

const money = (v) => Number(v || 0).toLocaleString()

const daysLeft = (ymd) => {
  if (!ymd) return null
  const [y, m, d] = ymd.split('-').map(Number)
  const target = new Date(y, m - 1, d)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return Math.round((target - today) / 86400000)
}

const dateTagType = (ymd) => {
  const dl = daysLeft(ymd)
  if (dl === null) return 'info'
  if (dl < 0) return 'danger'
  if (dl <= expiringDays) return 'warning'
  return 'success'
}

const dateText = (ymd) => {
  const dl = daysLeft(ymd)
  if (dl === null) return ymd || '—'
  if (dl < 0) return `${ymd}（已逾期 ${-dl} 天）`
  if (dl === 0) return `${ymd}（今天到期）`
  return `${ymd}（剩 ${dl} 天）`
}

const daysText = (dl) => {
  if (dl < 0) return `已逾期 ${-dl} 天`
  if (dl === 0) return '今天到期'
  return `剩 ${dl} 天`
}

const statusTagType = (s) => {
  return { '在用': 'success', '闲置': 'info', '维修': 'warning', '已处置': 'info' }[s] || 'info'
}

const nearestInsurance = (insurances) => {
  const list = (insurances || []).filter(i => i.endDate)
  if (!list.length) return null
  return [...list].sort((a, b) => a.endDate.localeCompare(b.endDate))[0]
}

const previewCerts = (certs) => {
  // 用浏览器新窗口打开第一张（或直接走 el-image 预览已支持，这里兜底）
  if (certs && certs.length) window.open(certs[0], '_blank')
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getVehicleList({ ...query })
    if (res) {
      vehicleList.value = res.records || []
      total.value = res.total || 0
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const loadExpiring = async () => {
  try {
    const res = await getVehicleExpiring({ days: expiringDays })
    if (res) {
      Object.assign(stats, res.stats || {})
      expiringItems.value = res.items || []
    }
  } catch { /* ignore */ }
}

const onPageChange = (p) => {
  query.page = p
  fetchList()
}

// ── 车辆 CRUD ──
const openCreate = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    plateNo: '', brand: '', model: '', vehicleType: '面包车', vin: '', engineNo: '',
    purchaseDate: '', registerDate: '', department: '', responsible: '',
    mileage: 0, status: '在用', img: '', remark: '', insurances: [],
  })
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    plateNo: row.plateNo || '', brand: row.brand || '', model: row.model || '',
    vehicleType: row.vehicleType || '面包车', vin: row.vin || '', engineNo: row.engineNo || '',
    purchaseDate: row.purchaseDate || '', registerDate: row.registerDate || '',
    department: row.department || '', responsible: row.responsible || '',
    mileage: row.mileage || 0, status: row.status || '在用', img: row.img || '', remark: row.remark || '',
    insurances: [...(row.insurances || [])],
  })
  dialogVisible.value = true
}

const saveVehicle = async () => {
  if (!form.plateNo.trim()) return ElMessage.warning('请填写车牌号')
  try {
    if (isEdit.value) {
      await updateVehicle(editingId.value, { ...form })
      ElMessage.success('车辆已更新')
    } else {
      await createVehicle({ ...form })
      ElMessage.success('车辆已录入')
    }
    dialogVisible.value = false
    fetchList()
    loadExpiring()
  } catch { /* ignore */ }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除车辆 [${row.plateNo}] 吗？`, '确认删除', { type: 'warning' }).then(async () => {
    try {
      await deleteVehicle(row.id)
      ElMessage.success('车辆已删除')
      fetchList()
      loadExpiring()
    } catch { /* ignore */ }
  }).catch(() => {})
}

// ── 详情 ──
const openDetail = async (row) => {
  await loadDetail(row.id)
  drawerVisible.value = true
}

const openDetailById = async (id) => {
  await loadDetail(id)
  drawerVisible.value = true
}

const loadDetail = async (id) => {
  try {
    const d = await getVehicleDetail(id)
    if (d) Object.assign(detail, d)
  } catch { /* ignore */ }
}

// ── 保险 ──
const openInsurance = (row) => {
  insuranceMode.value = 'detail'
  if (row) {
    insuranceEditingId.value = row.id
    Object.assign(insuranceForm, {
      type: row.type || '商业险', insurer: row.insurer || '', policyNo: row.policyNo || '',
      premium: row.premium || 0, startDate: row.startDate || '', endDate: row.endDate || '',
      certs: [...(row.certs || [])], remark: row.remark || '',
    })
  } else {
    insuranceEditingId.value = null
    Object.assign(insuranceForm, { type: '商业险', insurer: '', policyNo: '', premium: 0, startDate: '', endDate: '', certs: [], remark: '' })
  }
  insuranceVisible.value = true
}

const openFormInsurance = (index = null) => {
  insuranceMode.value = 'form'
  insuranceFormIndex.value = index
  const row = index !== null ? form.insurances[index] : null
  Object.assign(insuranceForm, {
    type: (row && row.type) || '商业险',
    insurer: (row && row.insurer) || '',
    policyNo: (row && row.policyNo) || '',
    premium: (row && row.premium) || 0,
    startDate: (row && row.startDate) || '',
    endDate: (row && row.endDate) || '',
    certs: [...((row && row.certs) || [])],
    remark: (row && row.remark) || '',
  })
  insuranceVisible.value = true
}

const saveInsurance = async () => {
  if (!insuranceForm.endDate) return ElMessage.warning('请填写到期日期')
  // 车辆表单模式：仅写入本地 form.insurances，随车辆保存一并提交
  if (insuranceMode.value === 'form') {
    const data = { ...insuranceForm }
    if (insuranceFormIndex.value !== null && insuranceFormIndex.value !== undefined) {
      form.insurances[insuranceFormIndex.value] = data
    } else {
      form.insurances.push(data)
    }
    insuranceVisible.value = false
    return
  }
  try {
    if (insuranceEditingId.value) {
      await updateInsurance(detail.id, insuranceEditingId.value, { ...insuranceForm })
      ElMessage.success('保单已更新')
    } else {
      await addInsurance(detail.id, { ...insuranceForm })
      ElMessage.success('保单已添加')
    }
    insuranceVisible.value = false
    await loadDetail(detail.id)
    loadExpiring()
  } catch { /* ignore */ }
}

const handleDeleteInsurance = (row) => {
  ElMessageBox.confirm(`确定删除该「${row.type}」保单吗？`, '确认删除', { type: 'warning' }).then(async () => {
    try {
      await deleteInsurance(detail.id, row.id)
      ElMessage.success('保单已删除')
      await loadDetail(detail.id)
      loadExpiring()
    } catch { /* ignore */ }
  }).catch(() => {})
}

// ── 年检 ──
const openInspection = () => {
  Object.assign(inspectionForm, {
    annualInspectionDate: detail.annualInspectionDate || '',
    certs: [...(detail.annualInspectionCerts || [])],
  })
  inspectionVisible.value = true
}

const saveInspection = async () => {
  try {
    await updateVehicleInspection(detail.id, {
      annualInspectionDate: inspectionForm.annualInspectionDate,
      annualInspectionCerts: inspectionForm.certs,
    })
    ElMessage.success('年检已更新')
    inspectionVisible.value = false
    await loadDetail(detail.id)
    loadExpiring()
  } catch { /* ignore */ }
}

// ── 保养计划 ──
const openPlan = () => {
  Object.assign(planForm, {
    nextMaintenanceDate: detail.nextMaintenanceDate || '',
    nextMaintenanceKm: detail.nextMaintenanceKm || 0,
  })
  planVisible.value = true
}

const savePlan = async () => {
  try {
    await updateVehicle(detail.id, {
      nextMaintenanceDate: planForm.nextMaintenanceDate,
      nextMaintenanceKm: planForm.nextMaintenanceKm,
    })
    ElMessage.success('保养计划已更新')
    planVisible.value = false
    await loadDetail(detail.id)
    loadExpiring()
  } catch { /* ignore */ }
}

// ── 保养记录 ──
const saveMaintenance = async () => {
  if (!maintenanceForm.date) return ElMessage.warning('请填写保养日期')
  try {
    await addVehicleMaintenance(detail.id, { ...maintenanceForm })
    ElMessage.success('保养记录已添加')
    maintenanceVisible.value = false
    Object.assign(maintenanceForm, { date: '', km: 0, item: '', cost: 0, vendor: '', remark: '' })
    await loadDetail(detail.id)
    loadExpiring()
  } catch { /* ignore */ }
}

const handleDeleteMaintenance = (row) => {
  ElMessageBox.confirm('确定删除该保养记录吗？', '确认删除', { type: 'warning' }).then(async () => {
    try {
      await deleteVehicleMaintenance(detail.id, row.id)
      ElMessage.success('保养记录已删除')
      await loadDetail(detail.id)
    } catch { /* ignore */ }
  }).catch(() => {})
}

// ── 上传 ──
const uploadCert = async (opt, target) => {
  try {
    const res = await uploadFile(opt.file, 'vehicles')
    if (res && res.url) target.push(res.url)
    ElMessage.success('凭证上传成功')
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchList()
  loadExpiring()
})
</script>

<style scoped>
.vehicle-management { padding: 4px 0; }

.kpi-row { margin-bottom: var(--space-xl); }
.kpi-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi-label { font-size: var(--text-sm); color: var(--text-muted); }
.kpi-value { font-size: var(--text-2xl); font-weight: var(--font-bold); font-variant-numeric: tabular-nums; }

.expiring-card { margin-bottom: var(--space-xl); }
.expiring-header { display: flex; justify-content: space-between; align-items: center; }
.expiring-list { display: flex; flex-wrap: wrap; gap: 10px; }
.expiring-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-muted);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-sm);
}
.expiring-item:hover { background: var(--bg-hover, #f0f4ff); }
.expiring-date { color: var(--text-secondary); }
.expiring-detail { color: var(--text-muted); }

.table-header { display: flex; justify-content: space-between; align-items: center; }
.left-group { display: flex; align-items: center; }
.pagination { margin-top: var(--space-lg); justify-content: flex-end; }

.sub { font-size: 12px; color: var(--text-muted); }
.muted { color: var(--text-muted); }

.pane-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-md); }
.pane-title { font-weight: var(--font-semibold); color: var(--text-primary); }
.info-line { display: flex; align-items: center; margin-bottom: var(--space-md); }

.cert-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.cert-item { position: relative; }
.cert-img { width: 72px; height: 72px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); }
.cert-del {
  position: absolute;
  top: -6px;
  right: -6px;
  color: #fff;
  background: var(--color-danger, #f56c6c);
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  padding: 2px;
}

.form-insurance-list { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
.form-insurance-tag { cursor: pointer; }
</style>
