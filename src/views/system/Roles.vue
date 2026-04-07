<template>
  <div class="role-container">
    <el-row :gutter="20">
      <!-- 左侧：角色列表 -->
      <el-col :span="8">
        <el-card shadow="never" class="role-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">职位角色</span>
              <el-button type="primary" size="small" icon="Plus" @click="addRole">新增</el-button>
            </div>
          </template>
          <el-table 
            :data="roleList" 
            highlight-current-row 
            @current-change="handleRoleSelect"
            style="width: 100%"
            class="role-table"
          >
            <el-table-column prop="roleName" label="角色名称">
              <template #default="{ row }">
                <div class="role-name-cell">
                  <el-icon><User /></el-icon>
                  <span>{{ row.roleName }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="code" label="标识码" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="info" effect="plain">{{ row.code }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：权限树配置 -->
      <el-col :span="16">
        <el-card shadow="never" class="perm-card">
          <template #header>
            <div class="card-header">
              <span>
                权限配置：
                <el-tag v-if="activeRole.roleName" effect="dark" size="large">
                  {{ activeRole.roleName }}
                </el-tag>
                <span v-else style="color: #909399; font-size: 14px">请选择左侧角色</span>
              </span>
              <el-button 
                type="success" 
                size="default" 
                :disabled="!activeRole.roleName" 
                :icon="Check"
                @click="savePermissions"
              >保存权限</el-button>
            </div>
          </template>
          
          <div v-if="activeRole.roleName" class="tree-wrapper">
            <el-alert 
              title="配置说明：勾选主菜单将自动开启该分类下的所有子功能权限。" 
              type="warning" 
              :closable="false" 
              show-icon 
              style="margin-bottom: 20px" 
            />
            
            <el-tree
              ref="treeRef"
              :data="menuData"
              show-checkbox
              node-key="id"
              default-expand-all
              check-strictly
              :props="{ label: 'label', children: 'children' }"
            >
              <template #default="{ node, data }">
                <span class="custom-tree-node">
                  <el-icon v-if="data.icon" class="node-icon"><component :is="data.icon" /></el-icon>
                  <span>{{ node.label }}</span>
                </span>
              </template>
            </el-tree>
          </div>
          <el-empty v-else :image-size="200" description="点击左侧角色列表，开始分配系统权限" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Plus, Check, User, Monitor, Document, Headset, 
  Box, ChatDotSquare, Trophy, Briefcase, Setting 
} from '@element-plus/icons-vue'

const treeRef = ref(null)
const activeRole = ref({})

// 1. 同步最新的角色数据 (增加 permissions 初始值)
const roleList = ref([
  { roleName: '超级管理员', code: 'admin', permissions: [1, 2, 3, 31, 32, 33, 34, 35, 36, 4, 5, 6, 7, 8, 9, 91, 92] },
  { roleName: '业务部(报修员)', code: 'business', permissions: [1, 3, 31, 32] },
  { roleName: '商务部(信息维护)', code: 'business_support', permissions: [1, 3, 36, 4, 5, 6, 7, 8] },
  { roleName: '工程部(工程师)', code: 'engineer', permissions: [1, 3, 32, 33, 34] }
])

// 2. 同步最新的菜单树结构 (对应你的截图)
const menuData = [
  { id: 1, label: '系统概览', icon: Monitor },
  { id: 2, label: '需求单管理', icon: Document },
  {
    id: 3,
    label: '售后报修管理',
    icon: Headset,
    children: [
      { id: 31, label: '一键报修' },
      { id: 32, label: '我的报修 / 工单' },
      { id: 33, label: '所有工单 (抢单池)' },
      { id: 34, label: '工程师期排' },
      { id: 35, label: '投诉建议管理' },
      { id: 36, label: '联系我们配置' }
    ]
  },
  { id: 4, label: '产品中心', icon: Box },
  { id: 5, label: '新闻中心', icon: ChatDotSquare },
  { id: 6, label: '荣誉与相册', icon: Trophy },
  { id: 7, label: '合作伙伴与案例', icon: Briefcase },
  { id: 8, label: '门户全局配置', icon: Setting },
  {
    id: 9,
    label: '系统管理',
    icon: Setting,
    children: [
      { id: 91, label: '成员管理' },
      { id: 92, label: '权限设置' }
    ]
  }
]

const handleRoleSelect = (row) => {
  if (!row) return
  activeRole.value = row
  
  // 必须使用 nextTick，确保 Tree 组件已渲染完毕
  nextTick(() => {
    if (treeRef.value) {
      treeRef.value.setCheckedKeys(row.permissions || [])
    }
  })
}

const savePermissions = () => {
  const checkedKeys = treeRef.value.getCheckedKeys()
  // 模拟保存逻辑
  activeRole.value.permissions = checkedKeys
  ElMessage.success(`角色 [${activeRole.value.roleName}] 权限更新成功！`)
}

const addRole = () => {
  ElMessage.info('触发新增角色弹窗')
}
</script>

<style scoped>
.role-container { padding: 10px; background-color: #f5f7fa; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title-text { font-weight: bold; font-size: 16px; }

.role-card, .perm-card { 
  height: calc(100vh - 140px); 
  border-radius: 8px;
}

.role-name-cell { display: flex; align-items: center; gap: 8px; }
.tree-wrapper { padding: 10px; }

/* 权限树样式美化 */
.custom-tree-node { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.node-icon { font-size: 16px; color: #606266; }

:deep(.el-tree-node__content) { height: 36px; border-radius: 4px; }
:deep(.el-tree-node__content:hover) { background-color: #f0f7ff; }

/* 解决高度溢出 */
:deep(.el-card__body) { height: calc(100% - 60px); overflow-y: auto; }
</style>