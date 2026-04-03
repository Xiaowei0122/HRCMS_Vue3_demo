<template>
  <div class="log-container">
    <el-card shadow="never">
      <!-- 搜索工具栏 -->
      <div class="toolbar">
        <el-form :inline="true" :model="logQuery">
          <el-form-item label="操作时间">
            <el-date-picker
              v-model="logQuery.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>
          <el-form-item>
            <el-input v-model="logQuery.user" placeholder="操作人账号" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search">查询</el-button>
            <el-button icon="Refresh">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 日志列表 -->
      <el-table :data="logData" stripe border style="width: 100%">
        <el-table-column prop="time" label="操作时间" width="180" sortable />
        <el-table-column prop="user" label="操作人" width="120" />
        <el-table-column prop="module" label="所属模块" width="120">
          <template #default="{row}">
            <el-tag size="small">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="详细行为" min-width="250" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column prop="result" label="结果" width="100" align="center">
          <template #default="{row}">
            <el-tag :type="row.result === '成功' ? 'success' : 'danger'" effect="dark">
              {{ row.result }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination background layout="total, prev, pager, next" :total="1240" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const logQuery = reactive({ dateRange: [], user: '' })

const logData = ref([
  { time: '2024-04-03 14:20:11', user: 'admin', module: '产品管理', content: '更新了 [理光IMC3000] 的租赁详情页', ip: '124.115.x.x', result: '成功' },
  { time: '2024-04-03 11:05:44', user: 'sale_01', module: '需求线索', content: '导出了近一周的客户联系清单', ip: '1.202.x.x', result: '成功' },
  { time: '2024-04-03 09:12:00', user: 'tech_li', module: '系统管理', content: '尝试修改权限分配 (权限不足)', ip: '113.20.x.x', result: '失败' },
  { time: '2024-04-02 18:30:22', user: 'admin', module: '安全设置', content: '重置了员工 [张三] 的登录密码', ip: '124.115.x.x', result: '成功' }
])
</script>

<style scoped>
.toolbar { margin-bottom: 20px; border-bottom: 1px solid #f0f2f5; padding-bottom: 10px; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>