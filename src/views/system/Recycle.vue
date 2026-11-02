<template>
  <div class="recycle-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title-text">回收站</span>
          <el-select
            v-model="filterCollection"
            placeholder="全部类型"
            clearable
            style="width: 160px"
            @change="fetchList"
          >
            <el-option label="产品" value="products" />
            <el-option label="新闻" value="news" />
            <el-option label="荣誉" value="honors" />
            <el-option label="品牌" value="brands" />
            <el-option label="案例" value="cases" />
            <el-option label="共享文件" value="finance_files" />
            <el-option label="资产" value="finance_assets" />
          </el-select>
        </div>
      </template>

      <el-alert
        title="删除的数据会暂存于此，可恢复或彻底删除。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />

      <el-table :data="list" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="label" label="内容" min-width="220" show-overflow-tooltip />
        <el-table-column prop="collectionName" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.collectionName }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="删除人" width="120">
          <template #default="{ row }">{{ row.operator || '—' }}</template>
        </el-table-column>
        <el-table-column prop="deletedAt" label="删除时间" width="180" />
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="restore(row)">恢复</el-button>
            <el-button link type="danger" @click="purge(row)">彻底删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && !list.length" :image-size="120" description="回收站为空" />

      <div class="pagination-wrap" v-if="total > size">
        <el-pagination
          layout="prev, pager, next, total"
          :total="total"
          :page-size="size"
          :current-page="page"
          @current-change="onPageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRecycleList, restoreItem, purgeItem } from '@/api/modules/recycle'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const size = 20
const total = ref(0)
const filterCollection = ref('')

const fetchList = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size }
    if (filterCollection.value) params.collection = filterCollection.value
    const res = await getRecycleList(params)
    list.value = res.records || []
    total.value = res.total || 0
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const onPageChange = (p) => {
  page.value = p
  fetchList()
}

const restore = async (row) => {
  try {
    await restoreItem(row.id)
    ElMessage.success('已恢复')
    fetchList()
  } catch { /* ignore */ }
}

const purge = (row) => {
  ElMessageBox.confirm(`彻底删除 [${row.label}] 后不可恢复，确定？`, '彻底删除', {
    type: 'warning',
    confirmButtonText: '彻底删除'
  }).then(async () => {
    try {
      await purgeItem(row.id)
      ElMessage.success('已彻底删除')
      fetchList()
    } catch { /* ignore */ }
  }).catch(() => {})
}

onMounted(fetchList)
</script>

<style scoped>
.recycle-container { padding: 10px; background-color: var(--bg-muted); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title-text { font-weight: bold; font-size: 16px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
