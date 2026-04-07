<template>
  <div class="dashboard-container">
    <!-- 第一行：核心运营指标 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in topStats" :key="item.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-header">
            <span class="label">{{ item.title }}</span>
            <el-tag :type="item.tagType" size="small" effect="plain">{{ item.tag }}</el-tag>
          </div>
          <div class="stat-body">
            <span class="number">{{ item.value }}</span>
            <span class="trend" :class="item.trend > 0 ? 'up' : 'down'">
              {{ item.trend > 0 ? '↑' : '↓' }} {{ Math.abs(item.trend) }}%
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 左侧：业务趋势图 (ECharts 占位) -->
      <el-col :span="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>业务转化与售后趋势 (近一周)</span>
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button label="repair">报修量</el-radio-button>
                <el-radio-button label="leads">需求线索</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="placeholder-chart">
            <!-- 实际开发中此处嵌入 ECharts -->
            <div class="bar-chart-mock">
              <div v-for="h in [40, 60, 45, 80, 55, 70, 85]" :key="h" :style="{ height: h + '%' }"></div>
            </div>
            <div class="chart-labels">
              <span>周一</span><span>周二</span><span>周三</span><span>周四</span><span>周五</span><span>周六</span><span>周日</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：快捷入口与情报 -->
      <el-col :span="8">
        <el-card shadow="never" class="info-card">
          <template #header><span>快捷管理 / 系统情报</span></template>
          
          <div class="quick-actions">
            <el-button plain icon="Plus" @click="$router.push('/products')">新增产品</el-button>
            <el-button plain type="success" icon="Edit" @click="$router.push('/news')">发布新闻</el-button>
            <el-button plain type="warning" icon="Calendar" @click="$router.push('/schedule')">排班管理</el-button>
            <el-button plain type="danger" icon="Warning" @click="$router.push('/complaints')">处理投诉</el-button>
          </div>

          <el-divider content-position="left">待办事项</el-divider>
          <ul class="todo-list">
            <li class="todo-item danger">
              <span class="dot"></span> 3 条投诉尚未核实回复
            </li>
            <li class="todo-item warning">
              <span class="dot"></span> 今日有 2 名工程师处于调休状态
            </li>
            <li class="todo-item info">
              <span class="dot"></span> 官网产品详情昨日浏览量增长 25%
            </li>
            <li class="todo-item success">
              <span class="dot"></span> 本月售后满意度维持在 98%
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const chartType = ref('repair')

const topStats = ref([
  { title: '全站总访客', value: '1,284', tag: '实时', tagType: 'primary', trend: 12 },
  { title: '新增报修单', value: '15', tag: '今日', tagType: 'danger', trend: 8 },
  { title: '待处理需求', value: '5', tag: '紧急', tagType: 'warning', trend: -2 },
  { title: '完工满意度', value: '98.5', tag: '本月', tagType: 'success', trend: 5 },
])
</script>

<style scoped>
.dashboard-container { padding: 0px; }
.stat-card { border-radius: 8px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.stat-header { display: flex; justify-content: space-between; align-items: center; color: #909399; font-size: 14px; }
.stat-body { margin-top: 15px; display: flex; align-items: baseline; gap: 10px; }
.stat-body .number { font-size: 28px; font-weight: bold; color: #303133; }
.trend { font-size: 12px; }
.trend.up { color: #f56c6c; }
.trend.down { color: #67c23a; }

.chart-card { height: 450px; border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

.placeholder-chart { height: 300px; display: flex; flex-direction: column; justify-content: flex-end; padding-top: 40px; }
.bar-chart-mock { display: flex; align-items: flex-end; justify-content: space-around; height: 100%; padding: 0 20px; }
.bar-chart-mock div { width: 40px; background: linear-gradient(to top, #409eff, #79bbff); border-radius: 4px 4px 0 0; }
.chart-labels { display: flex; justify-content: space-around; margin-top: 15px; color: #909399; font-size: 12px; }

.quick-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
.todo-list { list-style: none; padding: 0; margin: 0; }
.todo-item { display: flex; align-items: center; font-size: 13px; padding: 10px 0; color: #606266; border-bottom: 1px dashed #ebeef5; }
.todo-item .dot { width: 6px; height: 6px; border-radius: 50%; margin-right: 10px; }
.todo-item.danger .dot { background: #f56c6c; }
.todo-item.warning .dot { background: #e6a23c; }
.todo-item.info .dot { background: #409eff; }
.todo-item.success .dot { background: #67c23a; }
</style>