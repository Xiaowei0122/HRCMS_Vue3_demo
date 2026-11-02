<template>
  <div class="engineer-slot-picker">
    <el-form-item label="预约工程师">
      <el-select
        :model-value="engineerId"
        clearable
        filterable
        placeholder="不选则进入抢单池，由工程师自主接单"
        style="width: 100%"
        @update:model-value="onEngineerChange"
      >
        <el-option v-for="e in engineers" :key="e.id" :label="e.name" :value="e.id" />
      </el-select>
    </el-form-item>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="预约日期">
          <el-date-picker
            :model-value="date"
            type="date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            :disabled-date="disablePastDate"
            @update:model-value="onDateChange"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="预约时段">
          <el-select
            :model-value="timeSlot"
            style="width: 100%"
            placeholder="选择时段"
            @update:model-value="onSlotChange"
          >
            <el-option
              v-for="opt in timeSlotOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
              :disabled="opt.value !== '全天' && occupiedSlots.includes(opt.value)"
            >
              <span>{{ opt.label }}</span>
              <span v-if="opt.value !== '全天' && occupiedSlots.includes(opt.value)" class="occupied-tip">（已占用）</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getEngineerList, getScheduleAvailability } from '@/api/modules/repairs'

const props = defineProps({
  engineerId: { type: String, default: '' },
  engineerName: { type: String, default: '' },
  date: { type: String, default: '' },
  timeSlot: { type: String, default: '全天' }
})
const emit = defineEmits(['update:engineerId', 'update:engineerName', 'update:date', 'update:timeSlot'])

const engineers = ref([])
const occupiedSlots = ref([])

const timeSlotOptions = [
  { label: '全天', value: '全天' },
  { label: '上午 (早) 08:30-10:00', value: 'AM1' },
  { label: '上午 (晚) 10:00-11:50', value: 'AM2' },
  { label: '下午 (早) 13:30-15:00', value: 'PM1' },
  { label: '下午 (中) 15:00-16:30', value: 'PM2' },
  { label: '下午 (晚) 16:30-18:00', value: 'PM3' }
]

const disablePastDate = (d) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return d.getTime() < today.getTime()
}

const onEngineerChange = (val) => {
  const eng = engineers.value.find(e => e.id === val)
  emit('update:engineerId', val || '')
  emit('update:engineerName', eng ? eng.name : '')
  occupiedSlots.value = []
}

const onDateChange = (val) => {
  emit('update:date', val || '')
}

const onSlotChange = (val) => {
  emit('update:timeSlot', val || '全天')
}

const loadAvailability = async () => {
  if (!props.engineerId || !props.date) {
    occupiedSlots.value = []
    return
  }
  try {
    const res = await getScheduleAvailability({ engineerId: props.engineerId, date: props.date })
    occupiedSlots.value = Array.isArray(res?.occupied) ? res.occupied : []
    // 当前已选时段若变为占用，自动回退到「全天」
    if (props.timeSlot !== '全天' && occupiedSlots.value.includes(props.timeSlot)) {
      emit('update:timeSlot', '全天')
    }
  } catch {
    occupiedSlots.value = []
  }
}

watch(() => [props.engineerId, props.date], loadAvailability)

onMounted(async () => {
  try {
    const res = await getEngineerList()
    engineers.value = Array.isArray(res) ? res : (res.records || [])
  } catch {
    engineers.value = []
  }
})
</script>

<style scoped>
.occupied-tip { color: var(--text-muted); font-size: 12px; margin-left: 6px; }
</style>
