<template>
  <div class="personal-schedule-container">
    <el-card shadow="never">
      <template #header>
        <div class="header-flex">
          <div class="left-tools">
            <el-select v-model="selectedEngineer" placeholder="选择工程师" style="width: 140px; margin-right: 12px">
              <el-option v-for="eng in taskStore.engineers" :key="eng.id" :label="eng.name" :value="eng.name" />
            </el-select>
            <el-button-group>
              <el-button :icon="ArrowLeft" @click="changeWeek(-1)">上一周</el-button>
              <el-button @click="resetWeek">本周</el-button>
              <el-button @click="changeWeek(1)">下一周 <el-icon class="el-icon--right"><ArrowRight /></el-icon></el-button>
            </el-button-group>
            <el-date-picker
              v-model="exportRange"
              type="daterange"
              range-separator="至"
              start-placeholder="导出开始日期"
              end-placeholder="导出结束日期"
              value-format="YYYY-MM-DD"
              size="default"
              style="width: 240px; margin-left: 12px"
            />
            <el-button type="success" :icon="Download" style="margin-left: 12px" @click="exportToExcel">导出报表</el-button>
          </div>
          <div class="right-info">
            <el-tag type="info" effect="plain" style="margin-right: 15px">
              本周汇总：已完成 {{ weeklyStats.done }} / 总计 {{ weeklyStats.total }}
            </el-tag>
            <span class="week-range">{{ weekDates[0]?.labelFull }} ~ {{ weekDates[6]?.labelFull }}</span>
          </div>
        </div>
      </template>

      <div class="matrix-wrapper">
        <table class="schedule-matrix">
          <thead>
            <tr>
              <th class="time-col">时间段</th>
              <th v-for="date in weekDates" :key="date.full" :class="{ 'is-today': date.isToday }">
                {{ date.weekDay }}<br><small>{{ date.label }}</small>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="slot in timeSlots" :key="slot.id">
              <td class="time-slot-label">
                <div class="slot-name">{{ slot.name }}</div>
                <div class="slot-time">{{ slot.range }}</div>
              </td>
              <td v-for="date in weekDates" :key="date.full"
                  :class="['matrix-cell', cellStatus(date.full, slot.id, slot.range)]"
                  @click="handleCellClick(date.full, slot.id, slot.range)">

                <!-- 多格块起始格：显示任务卡片（占多格 / 加急红标） -->
                <div v-if="isBlockStart(date.full, slot.id)" class="task-card">
                   <div class="task-inner">
                      <span class="comp-name">{{ isLockTask(cellTask(date.full, slot.id)) ? lockTypeLabel(cellTask(date.full, slot.id)) : cellTask(date.full, slot.id).company }}</span>
                      <el-tag size="small" :type="getTagType(cellTask(date.full, slot.id))">
                        {{ isLockTask(cellTask(date.full, slot.id)) ? '状态锁定' : getCurrentNode(cellTask(date.full, slot.id)) }}
                      </el-tag>
                      <el-tag v-if="cellTask(date.full, slot.id).escalated" type="danger" size="small" effect="dark" class="schedule-escalated">加急</el-tag>
                   </div>
                   <div v-if="(cellTask(date.full, slot.id).slotSpan || 1) > 1" class="block-span">预计耗时 · {{ durationLabel(cellTask(date.full, slot.id).slotSpan) }}</div>
                </div>

                <!-- 多格块续格（非起始格）：占位标记，不再显示“可预约” -->
                <div v-else-if="isBlockContinuation(date.full, slot.id)" class="block-continuation">↕</div>

                <!-- 只有真正没任务或锁定已结束时显示可预约 -->
                <div v-else-if="cellStatus(date.full, slot.id, slot.range) === 'available'" class="empty-slot">
                  <el-icon><Plus /></el-icon> 可预约
                </div>

                <div v-else-if="cellStatus(date.full, slot.id, slot.range) === 'expired'" class="expired-text">-</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </el-card>

    <!-- 弹窗 A：抽屉 -->
    <el-drawer v-model="drawerVisible" :title="isArchivedStatus(activeTask?.status) ? '工单详情 (归档)' : '任务详情'" size="400px" append-to-body>
      <div v-if="activeTask" class="drawer-content">
        <el-alert v-if="isArchivedStatus(activeTask.status)" title="该工单已归档，仅供查阅" type="success" :closable="false" show-icon style="margin-bottom: 15px" />
        
        <el-descriptions :column="1" border style="margin-bottom: 20px">
          <el-descriptions-item label="类型">{{ isLockTask(activeTask) ? '异常锁定 · ' + lockTypeLabel(activeTask) : '业务工单' }}</el-descriptions-item>
          <el-descriptions-item :label="isLockTask(activeTask) ? '锁定备注' : '客户'">{{ isLockTask(activeTask) ? (activeTask.note || '-') : activeTask.company }}</el-descriptions-item>
          <el-descriptions-item label="编号">{{ activeTask.orderNo || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预约时段">
            {{ activeTask.date }} {{ getTimeRange(activeTask.timeSlot) }}
            <span v-if="(activeTask.slotSpan || 1) > 1" class="drawer-span">（预计耗时 · {{ durationLabel(activeTask.slotSpan) }}）</span>
          </el-descriptions-item>
          <el-descriptions-item v-if="activeTask.escalated" label="加急">
            <el-tag type="danger" size="small" effect="dark">已加急</el-tag>
            <span class="drawer-reason">{{ activeTask.escalateReason || '' }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider v-if="!isLockTask(activeTask)" content-position="left">进度追踪</el-divider>
        <el-timeline v-if="!isLockTask(activeTask)">
          <el-timeline-item
            v-for="(node, index) in activeTask.progress"
            :key="index"
            :type="node.status === 'done' ? 'success' : 'primary'"
            :timestamp="node.time"
          >
            {{ node.node }}
          </el-timeline-item>
        </el-timeline>
        
        <div class="drawer-footer" style="margin-top: 30px; text-align: right;">
            <!-- 排期挪动（置顶/上移/下移）：工程师本人当天 / 管理员全局 -->
            <el-button-group v-if="canReorderTask" class="reorder-group">
              <el-button size="small" type="danger" plain @click="reorderTask('top')">置顶</el-button>
              <el-button size="small" @click="reorderTask('up')">上移</el-button>
              <el-button size="small" @click="reorderTask('down')">下移</el-button>
            </el-button-group>

            <!-- 业务工单操作保持不变（财务只读调阅时隐藏） -->
            <el-button
                v-if="isAdmin && activeTask.status === '处理中' && activeTask.type === 'business'"
                type="success"
                @click="completeOrder"
            >       确认完成工单
            </el-button>

            <!-- 非业务锁定操作：增加时间判定（财务只读调阅时隐藏） -->
            <el-button
                v-if="isAdmin && activeTask.status !== '已结束' && isLockTask(activeTask)"
                :type="isEarlyRelease ? 'warning' : 'info'"
                @click="releaseLock(activeTask.id)"
            >   {{ isEarlyRelease ? '提前结束并释放时段' : '确认结束并归档' }}
            </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 弹窗 B：快速录入 -->
    <el-dialog v-model="addDialogVisible" title="快速指派 / 报备" width="420px" append-to-body destroy-on-close>
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="任务类型">
          <el-radio-group v-model="addForm.type">
            <el-radio value="business">业务工单</el-radio>
            <el-radio value="break">异常锁定</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 业务工单：搜索并选择未指派工单 -->
        <el-form-item v-if="addForm.type === 'business'" label="关联工单">
          <el-select
            v-model="addForm.orderId"
            filterable
            remote
            clearable
            reserve-keyword
            :remote-method="searchUnassignedOrders"
            :loading="orderSearchLoading"
            placeholder="搜索未指派工单（单位 / 工单号）"
            style="width: 100%"
            @visible-change="onOrderSelectVisible"
          >
            <el-option
              v-for="o in unassignedOrders"
              :key="o.id"
              :label="`${o.orderNo} · ${o.company}`"
              :value="o.id"
            >
              <span class="opt-no">{{ o.orderNo }}</span>
              <span class="opt-company">{{ o.company }}</span>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 异常锁定：类型 + 备注 -->
        <template v-else>
          <el-form-item label="锁定类型">
            <el-select v-model="addForm.lockType" style="width: 100%">
              <el-option label="培训" value="training" />
              <el-option label="驻场" value="onsite" />
              <el-option label="请假" value="leave" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="addForm.note" placeholder="备注（可选）" />
          </el-form-item>
        </template>

        <el-form-item label="排期时间">
          <el-tag>{{ addForm.date }} {{ getTimeRange(addForm.timeSlot) }}</el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitQuickAdd">提交录入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ArrowLeft, ArrowRight, Plus, Download } from '@element-plus/icons-vue'
import { useTaskStore } from '../../store/taskStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserInfo } from '../../utils/auth'
import { getRepairList, getServerTime, reorderRepair } from '../../api/modules/repairs'
import dayjs from 'dayjs'
import * as XLSX from 'xlsx'

const taskStore = useTaskStore()
const selectedEngineer = ref('')
// 服务器时间（YYYY-MM-DD HH:mm:ss，含时分秒），用于排期过期判断和本周定位
const serverDate = ref('')
const currentMonday = ref(dayjs().startOf('week').add(1, 'day'))
const drawerVisible = ref(false)
const addDialogVisible = ref(false)
const activeTask = ref(null)
const addForm = ref({ type: 'business', company: '', orderId: '', date: '', timeSlot: '', lockType: 'other', note: '' })
const exportRange = ref([])
const unassignedOrders = ref([])
const orderSearchLoading = ref(false)
const submitting = ref(false)

// 拥有 repair:all 权限（管理员/超管）可指派工单
const isAdmin = computed(() => (getUserInfo()?.rank ?? 99) <= 1)
const isEngineer = computed(() => getUserInfo()?.roleCode === 'engineer')
const myUserId = computed(() => getUserInfo()?.id || '')

// 由选中的工程师名称反查 ID（用于 API 过滤）
const selectedEngineerId = computed(() => {
  const eng = taskStore.engineers.find(e => e.name === selectedEngineer.value)
  return eng?.id || ''
})

// 初始加载 + 切换工程师时刷新排期
const loadSchedule = async () => {
  if (!selectedEngineerId.value) return
  await taskStore.fetchSchedule({ engineerId: selectedEngineerId.value })
}

watch(selectedEngineer, () => {
  loadSchedule()
})

onMounted(async () => {
  // 先获取服务器时间，写入 store 供 getCellStatus 使用
  try {
    const t = await getServerTime()
    if (t?.datetime || t?.date) {
      // 保存完整服务器时间（含时分秒），用于时段过期 / 提前释放判断
      const fullNow = t.datetime || t.date
      serverDate.value = fullNow
      taskStore.serverDate = fullNow
      // 本周起始仍按日期定位
      currentMonday.value = dayjs(t.date || t.datetime).startOf('week').add(1, 'day')
    }
  } catch { /* 后端不可用时回退客户端时间 */ }
  await taskStore.fetchEngineers()
  // 默认选中第一个工程师
  if (taskStore.engineers.length && !selectedEngineer.value) {
    selectedEngineer.value = taskStore.engineers[0].name
  }
  await loadSchedule()
})

// 星期中文标签（dayjs .day() 返回 0=周日 ~ 6=周六）
const WEEK_DAY_LABELS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const timeSlots = [
  { id: 'AM1', name: '上午 (早)', range: '08:30-10:00' },
  { id: 'AM2', name: '上午 (晚)', range: '10:00-11:50' },
  { id: 'PM1', name: '下午 (早)', range: '13:30-15:00' },
  { id: 'PM2', name: '下午 (中)', range: '15:00-16:30' },
  { id: 'PM3', name: '下午 (晚)', range: '16:30-18:00' },
]

const weekDates = computed(() => {
  const today = serverDate.value ? dayjs(serverDate.value) : dayjs()
  return Array.from({ length: 7 }).map((_, i) => {
    const d = currentMonday.value.add(i, 'day')
    return {
      full: d.format('YYYY-MM-DD'),
      label: d.format('MM/DD'),
      labelFull: d.format('YYYY-MM-DD'),
      weekDay: WEEK_DAY_LABELS[d.day()],
      isToday: d.isSame(today, 'day')
    }
  })
})

// 本周汇总：联动「当前查看周 + 选中工程师」，切周/切人/刷新排期后自动更新
const weeklyStats = computed(() => {
  const start = weekDates.value[0]?.full || ''
  const end = weekDates.value[6]?.full || ''
  const tasks = taskStore.allTasks.filter(t =>
    t.engineer === selectedEngineer.value &&
    t.type === 'business' &&
    t.date >= start && t.date <= end
  )
  return {
    total: tasks.length,
    // 「完成」= 已完结 或 已归档（两者均为工单终态）
    done: tasks.filter(t => t.status === '已完成' || t.status === '已归档').length
  }
})

// ── 按块渲染：一个工单可占多格（slotSpan），从起始时段往下覆盖 ──
const SLOT_IDS = ['AM1', 'AM2', 'PM1', 'PM2', 'PM3']
const slotIndexOf = (id) => SLOT_IDS.indexOf(id)

// 时长档位语义化标签（与接单弹窗一致）：1单次 / 2上午半天 / 3下午半天 / 5全天
const durationLabel = (span) => {
  const map = { 1: '单次', 2: '上午半天', 3: '下午半天', 5: '全天' }
  return map[Number(span) || 1] || `${Number(span) || 1} 格`
}

// 返回覆盖该 (date, slotId) 的任务（含多格 span 的续格）
const cellTask = (date, slotId) => {
  const cur = slotIndexOf(slotId)
  const tasks = taskStore.allTasks.filter(t => t.engineer === selectedEngineer.value && t.date === date)
  for (const t of tasks) {
    const start = slotIndexOf(t.timeSlot)
    const span = Math.max(1, Number(t.slotSpan) || 1)
    if (start <= cur && cur < start + span) return t
  }
  return null
}

// 该 (date, slotId) 是否为某个多格块的起始格
const isBlockStart = (date, slotId) => {
  const t = cellTask(date, slotId)
  return t && t.timeSlot === slotId
}

// 该 (date, slotId) 是否为某个多格块的续格（非起始格）
const isBlockContinuation = (date, slotId) => {
  const t = cellTask(date, slotId)
  return t && t.timeSlot !== slotId && t.status !== '已结束'
}

// 块感知的格子状态（覆盖 store 的精确匹配 getter）
const cellStatus = (date, slotId, range) => {
  const task = cellTask(date, slotId)
  const now = taskStore.serverDate ? dayjs(taskStore.serverDate) : dayjs()
  const endTime = range.split('-')[1]
  const slotEndTime = dayjs(`${date} ${endTime}`)
  if (task) {
    if (task.status === '已完成' || task.status === '已归档') return 'finished'
    if (task.status === '已锁定') return 'locked'
    if (now.isAfter(slotEndTime)) return 'overtime'
    return 'occupied'
  }
  if (now.isAfter(slotEndTime)) return 'expired'
  return 'available'
}

const handleCellClick = (date, slotId, range) => {
  const status = cellStatus(date, slotId, range)
  const task = cellTask(date, slotId)
  if (status === 'expired') return

  if (task && task.status !== '已结束') {
    activeTask.value = task
    drawerVisible.value = true
  } else if (status === 'available') {
    if (!isAdmin.value) {
      ElMessage.warning('仅管理员可指派工单')
      return
    }
    addForm.value = { type: 'business', company: '', orderId: '', date, timeSlot: slotId, lockType: 'other', note: '' }
    addDialogVisible.value = true
    searchUnassignedOrders('')
  }
}

const completeOrder = async () => {
  const repairId = activeTask.value?.repairId
  if (!repairId) {
    ElMessage.warning('该记录未关联报修工单')
    return
  }
  try {
    await taskStore.completeTask(repairId)
    await loadSchedule()
    drawerVisible.value = false
    ElMessage.success('工单已完结并归档')
  } catch (e) {
    ElMessage.error(e.message || '完结工单失败')
  }
}

// 排期挪动（置顶/上移/下移）：仅业务工单 · 处理中 · 工程师本人当天 或 管理员
const canReorderTask = computed(() => {
  const t = activeTask.value
  if (!t) return false
  if (t.type !== 'business') return false
  if (t.status !== '处理中') return false
  // 工单完结后（待确认/已完成/已归档/已取消）不再允许挪动排期
  const rs = t.repairStatus || ''
  if (rs && rs !== '处理中') return false
  if (!isAdmin.value && !(isEngineer.value && t.engineerId === myUserId.value)) return false
  return true
})

const reorderTask = async (direction) => {
  const rid = activeTask.value?.repairId
  if (!rid) { ElMessage.warning('该记录未关联报修工单'); return }
  try {
    const res = await reorderRepair(rid, { direction })
    if (res?.overflow > 0) {
      ElMessage.warning(res.message || '排期已调整，有工单溢出顺延')
    } else {
      ElMessage.success('排期已调整')
    }
    await loadSchedule()
    drawerVisible.value = false
  } catch (e) {
    ElMessage.error(e?.message || '操作失败')
  }
}

// 释放锁定逻辑整合
const releaseLock = (id) => {
  ElMessageBox.confirm('确定提前结束该锁定任务并释放该时段吗？', '提示', {
    type: 'warning'
  }).then(() => {
    taskStore.releaseLock(id)
    drawerVisible.value = false
    ElMessage.success('时段已释放，可重新指派业务')
  })
}

/**
 * 判定锁定任务的操作类型
 * 返回 true 表示属于“提前释放”（当前时间早于该时段结束时间）
 * 返回 false 表示属于“过期补录结束”（当前时间已晚于该时段结束时间）
 */
const isEarlyRelease = computed(() => {
  if (!activeTask.value) return false;
  
  // 获取该时段的结束时间，例如 "16:30"
  const slot = timeSlots.find(s => s.id === activeTask.value.timeSlot);
  if (!slot) return false;
  
  const endTimeStr = slot.range.split('-')[1]; // 提取结束时间部分
  const taskEndDateTime = dayjs(`${activeTask.value.date} ${endTimeStr}`);
  
  // 优先使用服务器时间判断，回退客户端时间
  const now = serverDate.value ? dayjs(serverDate.value) : dayjs();
  return now.isBefore(taskEndDateTime);
});

const exportToExcel = () => {
  // 导出日期范围：优先使用用户选择的区间，未选择时默认当前查看周
  let start = ''
  let end = ''
  if (exportRange.value && Array.isArray(exportRange.value) && exportRange.value.length === 2 && exportRange.value[0]) {
    [start, end] = exportRange.value
  } else if (weekDates.value.length) {
    start = weekDates.value[0].full
    end = weekDates.value[6].full
  }

  let list = taskStore.allTasks.filter(t => t.engineer === selectedEngineer.value)
  if (start && end) {
    list = list.filter(t => t.date >= start && t.date <= end)
  }

  const data = list.map(t => ({
    '日期': t.date,
    '时段': getTimeRange(t.timeSlot),
    '内容': t.company,
    '状态': t.status,
    '工单号': t.orderNo || '-'
  }))
  if (!data.length) {
    ElMessage.warning('该时间范围内暂无排期数据')
    return
  }
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "排期报表")
  const rangeSuffix = start && end ? `${start}_${end}` : dayjs().format('YYYY-MM-DD')
  XLSX.writeFile(wb, `${selectedEngineer.value}_工作报表_${rangeSuffix}.xlsx`)
  ElMessage.success('导出成功')
}

const searchUnassignedOrders = async (query) => {
  orderSearchLoading.value = true
  try {
    const res = await getRepairList({ status: '待接单', company: query || '', size: 50 })
    unassignedOrders.value = Array.isArray(res) ? res : (res?.records || [])
  } catch {
    unassignedOrders.value = []
  } finally {
    orderSearchLoading.value = false
  }
}

const onOrderSelectVisible = (visible) => {
  if (visible) searchUnassignedOrders('')
}

const submitQuickAdd = async () => {
  const f = addForm.value
  submitting.value = true
  try {
    if (f.type === 'business') {
      if (!f.orderId) {
        ElMessage.warning('请选择要指派的工单')
        return
      }
      await taskStore.assignOrder(f.orderId, {
        engineerId: selectedEngineerId.value,
        engineerName: selectedEngineer.value,
        timeSlot: f.timeSlot,
        date: f.date,
      })
    } else {
      await taskStore.lockSlot({
        engineerId: selectedEngineerId.value,
        engineer: selectedEngineer.value,
        date: f.date,
        timeSlot: f.timeSlot,
        type: f.lockType || 'other',
        note: (f.note || '').trim(),
      })
    }
    addDialogVisible.value = false
    ElMessage.success('排期已更新')
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const LOCK_TYPE_LABELS = { training: '培训', onsite: '驻场', leave: '请假', other: '其他' }
const isLockTask = (task) => task && task.status === '已锁定'
const lockTypeLabel = (task) => LOCK_TYPE_LABELS[task?.type] || task?.type || '其他'
// 已完结 / 已归档均视为归档态（只读查阅，不再展示操作按钮）
const isArchivedStatus = (s) => s === '已完成' || s === '已归档'

const getCurrentNode = (task) => {
  // 已约格子显示完成状态：优先取后端实时 repairStatus，回退到进度节点
  if (task.repairStatus) return task.repairStatus
  if (task.status === '已完成') return '已完成'
  return task.progress?.length > 0 ? task.progress[task.progress.length - 1].node : (task.status || '待处理')
}

const getTagType = (task) => {
  if (isLockTask(task)) return 'info'
  const s = task.repairStatus || task.status
  if (s === '已完成' || s === '已归档') return 'success'
  if (s === '待确认') return 'warning'
  if (s === '已取消') return 'info'
  return 'primary'
}

const getTimeRange = (slotId) => timeSlots.find(s => s.id === slotId)?.range
const changeWeek = (step) => { currentMonday.value = currentMonday.value.add(step, 'week') }
const resetWeek = () => { currentMonday.value = dayjs().startOf('week').add(1, 'day') }
</script>

<style scoped>
.personal-schedule-container { padding: 15px; }
.header-flex { display: flex; justify-content: space-between; align-items: center; }
.matrix-wrapper { margin-top: 20px; border: 1px solid var(--border-color); border-radius: var(--radius-md); overflow: hidden; }
.schedule-matrix { width: 100%; border-collapse: collapse; table-layout: fixed; }
.schedule-matrix th, .schedule-matrix td { border: 1px solid var(--border-color); padding: 12px 8px; text-align: center; }
thead th { background: var(--bg-muted); color: var(--text-secondary); font-weight: 600; }
thead th.is-today { background: var(--color-info-bg); color: var(--color-accent); }
.time-col { width: 120px; }
.time-slot-label { background: var(--bg-muted); }
.matrix-cell { height: 100px; vertical-align: middle; transition: all 0.2s; cursor: pointer; position: relative; background-color: #fcfcfc; }

/* 还原上一版浅灰色 UI，不突兀 */
.matrix-cell.available:hover { background: var(--color-success-bg); }
.matrix-cell.available .empty-slot { color: #c0c4cc; font-size: 12px; }

/* 占用状态 */
.matrix-cell.occupied { background: var(--color-info-bg); border-left: 4px solid var(--color-accent); }

/* 已完成状态：弱化显示 */
.matrix-cell.finished { background: var(--bg-muted); border-left: 4px solid var(--color-success); opacity: 0.7; }

/* 锁定状态 */
.matrix-cell.locked { background: #f2f2f2; border-left: 4px solid #909399; }

/* 超时警示 */
.matrix-cell.overtime { background: var(--color-danger-bg); border-left: 4px solid var(--color-danger); animation: blink-bg 2s infinite; }
@keyframes blink-bg { 50% { background-color: #fff; } }

.matrix-cell.expired { background: var(--bg-muted); cursor: not-allowed; }
.expired-text { color: #dcdfe6; }

.task-card { padding: 4px; text-align: left; }
.task-inner { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.comp-name { display: block; font-size: 13px; font-weight: bold; margin-bottom: 5px; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.schedule-escalated { margin-left: 2px; }
.block-span { font-size: 11px; color: var(--color-accent); margin-top: 3px; }
.block-continuation { color: var(--color-accent); opacity: 0.55; font-size: 12px; }
.drawer-content { padding: 0 10px; }
.drawer-span { color: var(--text-muted); font-size: 12px; }
.drawer-reason { margin-left: 6px; color: var(--text-secondary); font-size: 12px; }
.reorder-group { margin-right: 10px; }
.opt-no { float: left; color: var(--text-primary); }
.opt-company { float: right; color: var(--text-secondary); font-size: 12px; }
</style>