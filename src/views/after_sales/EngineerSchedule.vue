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
                  :class="['matrix-cell', getStatusClass(date.full, slot.id, slot.range)]"
                  @click="handleCellClick(date.full, slot.id, slot.range)">
                
                <!-- 存在任务且状态不是“已结束”时显示卡片 -->
                <div v-if="getTask(date.full, slot.id) && getTask(date.full, slot.id).status !== '已结束'" class="task-card">
                   <div class="task-inner">
                      <span class="comp-name">{{ getTask(date.full, slot.id).company }}</span>
                      <el-tag size="small" :type="getTagType(getTask(date.full, slot.id))">
                        {{ getTask(date.full, slot.id).type === 'break' ? '状态锁定' : getCurrentNode(getTask(date.full, slot.id)) }}
                      </el-tag>
                   </div>
                </div>

                <!-- 只有真正没任务或锁定已结束时显示可预约 -->
                <div v-else-if="getStatusClass(date.full, slot.id, slot.range) === 'available'" class="empty-slot">
                  <el-icon><Plus /></el-icon> 可预约
                </div>

                <div v-else-if="getStatusClass(date.full, slot.id, slot.range) === 'expired'" class="expired-text">-</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </el-card>

    <!-- 弹窗 A：抽屉 -->
    <el-drawer v-model="drawerVisible" :title="activeTask?.status === '已完成' ? '工单详情 (归档)' : '任务详情'" size="400px">
      <div v-if="activeTask" class="drawer-content">
        <el-alert v-if="activeTask.status === '已完成'" title="该工单已归档，仅供查阅" type="success" :closable="false" show-icon style="margin-bottom: 15px" />
        
        <el-descriptions :column="1" border style="margin-bottom: 20px">
          <el-descriptions-item label="类型">{{ activeTask.type === 'break' ? '非业务锁定' : '业务工单' }}</el-descriptions-item>
          <el-descriptions-item label="客户/备注">{{ activeTask.company }}</el-descriptions-item>
          <el-descriptions-item label="编号">{{ activeTask.orderNo || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预约时段">{{ activeTask.date }} {{ getTimeRange(activeTask.timeSlot) }}</el-descriptions-item>
        </el-descriptions>

        <el-divider v-if="activeTask.type !== 'break'" content-position="left">进度追踪</el-divider>
        <el-timeline v-if="activeTask.type !== 'break'">
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
            <!-- 业务工单操作保持不变 -->
            <el-button 
                v-if="activeTask.status !== '已完成' && activeTask.type === 'business'" 
                type="success" 
                @click="completeOrder(activeTask.id)"
            >       确认完成工单
            </el-button>
            
            <!-- 非业务锁定操作：增加时间判定 -->
            <el-button 
                v-if="activeTask.status !== '已结束' && activeTask.type === 'break'" 
                :type="isEarlyRelease ? 'warning' : 'info'" 
                @click="releaseLock(activeTask.id)"
            >   {{ isEarlyRelease ? '提前结束并释放时段' : '确认结束并归档' }}
            </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 弹窗 B：快速录入 -->
    <el-dialog v-model="addDialogVisible" title="快速指派/报备" width="400px" destroy-on-close>
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="任务类型">
          <el-radio-group v-model="addForm.type">
            <el-radio label="business">业务工单</el-radio>
            <el-radio label="break">异常锁定</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="addForm.type === 'business' ? '客户名称' : '锁定原因'">
          <el-input v-model="addForm.company" placeholder="请输入内容" />
        </el-form-item>
        <el-form-item label="排期时间">
          <el-tag>{{ addForm.date }} {{ addForm.timeSlot }}</el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitQuickAdd">提交录入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowLeft, ArrowRight, Plus, Download } from '@element-plus/icons-vue'
import { useTaskStore } from '../../store/taskStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import * as XLSX from 'xlsx'

const taskStore = useTaskStore()
const selectedEngineer = ref('张工')
const currentMonday = ref(dayjs().startOf('week').add(1, 'day'))
const drawerVisible = ref(false)
const addDialogVisible = ref(false)
const activeTask = ref(null)
const addForm = ref({ type: 'business', company: '', date: '', timeSlot: '' })

const timeSlots = [
  { id: 'AM1', name: '上午 (早)', range: '08:30-10:00' },
  { id: 'AM2', name: '上午 (晚)', range: '10:00-11:50' },
  { id: 'PM1', name: '下午 (早)', range: '13:30-15:00' },
  { id: 'PM2', name: '下午 (中)', range: '15:00-16:30' },
  { id: 'PM3', name: '下午 (晚)', range: '16:30-18:00' },
]

const weeklyStats = computed(() => {
  const tasks = taskStore.allTasks.filter(t => t.engineer === selectedEngineer.value)
  return {
    total: tasks.filter(t => t.type === 'business').length,
    done: tasks.filter(t => t.status === '已完成').length
  }
})

const weekDates = computed(() => {
  return Array.from({ length: 7 }).map((_, i) => {
    const d = currentMonday.value.add(i, 'day')
    return {
      full: d.format('YYYY-MM-DD'),
      label: d.format('MM/DD'),
      labelFull: d.format('YYYY-MM-DD'),
      weekDay: d.format('ddd'),
      isToday: d.isSame(dayjs(), 'day')
    }
  })
})

const getStatusClass = (date, slotId, range) => taskStore.getCellStatus(selectedEngineer.value, date, slotId, range)
const getTask = (date, slotId) => taskStore.getSlotTask(selectedEngineer.value, date, slotId)

const handleCellClick = (date, slotId, range) => {
  const status = getStatusClass(date, slotId, range)
  const task = getTask(date, slotId)
  if (status === 'expired') return

  if (task && task.status !== '已结束') {
    activeTask.value = task
    drawerVisible.value = true
  } else if (status === 'available') {
    addForm.value = { type: 'business', company: '', date, timeSlot: slotId }
    addDialogVisible.value = true
  }
}

const completeOrder = (id) => {
  taskStore.completeTask(id)
  drawerVisible.value = false
  ElMessage.success('工单已完结并归档')
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
  
  // 如果当前时间在结束时间之前，则属于提前结束
  return dayjs().isBefore(taskEndDateTime);
});

const exportToExcel = () => {
  const data = taskStore.allTasks.filter(t => t.engineer === selectedEngineer.value).map(t => ({
    '日期': t.date,
    '时段': getTimeRange(t.timeSlot),
    '内容': t.company,
    '状态': t.status,
    '工单号': t.orderNo || '-'
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "排期报表")
  XLSX.writeFile(wb, `${selectedEngineer.value}_工作报表.xlsx`)
  ElMessage.success('导出成功')
}

const submitQuickAdd = () => {
  taskStore.addTask({ ...addForm.value, engineer: selectedEngineer.value, status: '处理中' })
  addDialogVisible.value = false
}

const getCurrentNode = (task) => {
  if (task.status === '已完成') return '已完成'
  return task.progress?.length > 0 ? task.progress[task.progress.length - 1].node : '待处理'
}

const getTagType = (task) => {
  if (task.type === 'break') return 'info'
  return task.status === '已完成' ? 'success' : 'primary'
}

const getTimeRange = (slotId) => timeSlots.find(s => s.id === slotId)?.range
const changeWeek = (step) => { currentMonday.value = currentMonday.value.add(step, 'week') }
const resetWeek = () => { currentMonday.value = dayjs().startOf('week').add(1, 'day') }
</script>

<style scoped>
.personal-schedule-container { padding: 15px; }
.header-flex { display: flex; justify-content: space-between; align-items: center; }
.matrix-wrapper { margin-top: 20px; border: 1px solid #ebeef5; border-radius: 8px; overflow: hidden; }
.schedule-matrix { width: 100%; border-collapse: collapse; table-layout: fixed; }
.schedule-matrix th, .schedule-matrix td { border: 1px solid #ebeef5; padding: 12px 8px; text-align: center; }
thead th { background: #f8f9fb; color: #606266; font-weight: 600; }
thead th.is-today { background: #ecf5ff; color: #409eff; }
.time-col { width: 120px; }
.time-slot-label { background: #f8f9fb; }
.matrix-cell { height: 100px; vertical-align: middle; transition: all 0.2s; cursor: pointer; position: relative; background-color: #fcfcfc; }

/* 还原上一版浅灰色 UI，不突兀 */
.matrix-cell.available:hover { background: #f0f9eb; }
.matrix-cell.available .empty-slot { color: #c0c4cc; font-size: 12px; }

/* 占用状态 */
.matrix-cell.occupied { background: #ecf5ff; border-left: 4px solid #409eff; }

/* 已完成状态：弱化显示 */
.matrix-cell.finished { background: #f5f7fa; border-left: 4px solid #67c23a; opacity: 0.7; }

/* 锁定状态 */
.matrix-cell.locked { background: #f2f2f2; border-left: 4px solid #909399; }

/* 超时警示 */
.matrix-cell.overtime { background: #fef0f0; border-left: 4px solid #f56c6c; animation: blink-bg 2s infinite; }
@keyframes blink-bg { 50% { background-color: #fff; } }

.matrix-cell.expired { background: #f5f7fa; cursor: not-allowed; }
.expired-text { color: #dcdfe6; }

.task-card { padding: 4px; text-align: left; }
.comp-name { display: block; font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.drawer-content { padding: 0 10px; }
</style>