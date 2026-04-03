<template>
  <div class="dashboard-container">
    <!-- 第一行：核心数据卡片 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in topStats" :key="card.title">
        <el-card shadow="never" class="stat-card">
          <div class="stat-header">
            <span class="title">{{ card.title }}</span>
            <el-tag :type="card.type" size="small">{{ card.tag }}</el-tag>
          </div>
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-footer">
            <span class="trend">较昨日 <i :class="card.trendIcon"></i> {{ card.ratio }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：图表与待办 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <el-card shadow="never" header="业务转化趋势 (近一周)">
          <div class="chart-placeholder">
            <!-- 这里以后放 Echarts -->
            <div class="mock-chart">
              <div v-for="h in [40, 70, 45, 90, 65, 80, 95]" :key="h" 
                   class="bar" :style="{ height: h + '%' }"></div>
            </div>
            <div class="chart-labels">
              <span>周一</span><span>周二</span><span>周三</span><span>周四</span><span>周五</span><span>周六</span><span>周日</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="never" header="快捷指令">
          <div class="quick-actions">
            <el-button type="primary" plain icon="Plus">新增产品</el-button>
            <el-button type="success" plain icon="Edit">发布新闻</el-button>
            <el-button type="warning" plain icon="Camera">上传案例</el-button>
            <el-button type="info" plain icon="Share">生成海报</el-button>
          </div>
          <el-divider content-position="left">系统情报</el-divider>
          <ul class="info-list">
            <li><el-badge is-dot type="danger" /> 3 条新线索尚未及时回访</li>
            <li><el-badge is-dot type="warning" /> 官网收录量昨日增长 12%</li>
            <li><el-badge is-dot type="primary" /> AI 已为您准备好 5 篇行业资讯</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
const topStats = [
  { title: '全站访客', value: '1,284', tag: '实时', type: '', ratio: '12%', trendIcon: 'el-icon-caret-top' },
  { title: '意向客户', value: '42', tag: '新增', type: 'success', ratio: '8%', trendIcon: 'el-icon-caret-top' },
  { title: '待办线索', value: '5', tag: '加急', type: 'danger', ratio: '2%', trendIcon: 'el-icon-caret-bottom' },
  { title: '产品曝光', value: '8,902', tag: '周计', type: 'warning', ratio: '25%', trendIcon: 'el-icon-caret-top' }
]
</script>

<style scoped>
.dashboard-container { padding: 0; }
.mt-20 { margin-top: 20px; }

.stat-card { border: 1px solid #eef0f7 !important; }
.stat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.stat-header .title { font-size: 14px; color: #606266; }
.stat-value { font-size: 28px; font-weight: bold; color: #303133; margin-bottom: 10px; }
.stat-footer { font-size: 12px; color: #909399; }
.trend { color: #67c23a; }

.chart-placeholder { height: 300px; display: flex; flex-direction: column; justify-content: flex-end; }
.mock-chart { height: 240px; display: flex; align-items: flex-end; justify-content: space-around; padding: 0 20px; border-bottom: 1px solid #eee; }
.bar { width: 30px; background: linear-gradient(to top, #409eff, #79bbff); border-radius: 4px 4px 0 0; transition: 0.3s; cursor: pointer; }
.bar:hover { filter: brightness(1.1); }
.chart-labels { display: flex; justify-content: space-around; padding-top: 10px; color: #909399; font-size: 12px; }

.quick-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.info-list { list-style: none; padding: 0; margin-top: 15px; }
.info-list li { font-size: 13px; color: #606266; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
</style>