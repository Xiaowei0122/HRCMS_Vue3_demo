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
        <el-descriptions-item label="报修时间">{{ detail.createTime }}</el-descriptions-item>
        <el-descriptions-item label="维修地址" :span="2">{{ detail.address }}</el-descriptions-item>
      </el-descriptions>

      <!-- 进度时间线 -->
      <el-timeline style="margin-top: 30px">
        <el-timeline-item
          v-for="(item, index) in detail.progress"
          :key="index"
          :timestamp="item.time"
          :color="item.status === 'done' ? '#0bbd87' : '#409eff'"
        >
          {{ item.node }}
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-empty v-else-if="!loading" description="未找到工单信息" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getRepairDetail } from '@/api/modules/repairs'

const route = useRoute()
const detail = ref(null)
const loading = ref(false)

const statusTagType = computed(() => {
  const map = {
    '待接单': 'info',
    '处理中': 'warning',
    '已完成': 'success',
    '已取消': 'danger'
  }
  return map[detail.value?.status] || 'info'
})

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
</style>
