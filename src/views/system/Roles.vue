<template>
  <div class="role-container">
    <el-row :gutter="20">
      <!-- 左侧：角色列表 -->
      <el-col :span="8">
        <el-card shadow="never" class="role-card">
          <template #header>
            <div class="card-header">
              <span>职位角色</span>
              <el-button type="primary" size="small" icon="Plus" @click="addRole">新增</el-button>
            </div>
          </template>
          <el-table 
            :data="roleList" 
            highlight-current-row 
            @current-change="handleRoleSelect"
            style="width: 100%"
          >
            <el-table-column prop="roleName" label="角色名称" />
            <el-table-column prop="code" label="标识码" width="100" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：权限树 -->
      <el-col :span="16">
        <el-card shadow="never" class="perm-card">
          <template #header>
            <div class="card-header">
              <span>权限配置：<b style="color: #409EFF">{{ activeRole.roleName || '请选择角色' }}</b></span>
              <el-button 
                type="success" 
                size="small" 
                :disabled="!activeRole.roleName" 
                @click="savePermissions"
              >保存权限</el-button>
            </div>
          </template>
          
          <div v-if="activeRole.roleName" class="tree-wrapper">
            <el-alert title="勾选下方菜单，赋予该角色访问权限" type="info" :closable="false" show-icon style="margin-bottom: 15px" />
            <el-tree
              ref="treeRef"
              :data="menuData"
              show-checkbox
              node-key="id"
              default-expand-all
              :default-checked-keys="activeRole.permissions"
              :props="{ label: 'label', children: 'children' }"
            />
          </div>
          <el-empty v-else description="请从左侧选择一个角色进行配置" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const treeRef = ref(null)
const activeRole = ref({})

// 模拟角色数据
const roleList = ref([
  { roleName: '超级管理员', code: 'admin', permissions: [1, 2, 3, 4] },
  { roleName: '销售主管', code: 'sale_mgr', permissions: [1, 2] },
  { roleName: '技术维修', code: 'tech', permissions: [1, 3] }
])

// 模拟菜单树
const menuData = [
  { id: 1, label: '工作台 (Dashboard)' },
  { id: 2, label: '需求线索 (Leads)', children: [{ id: 21, label: '线索查看' }, { id: 22, label: '线索处理' }] },
  { id: 3, label: '产品中心 (Products)', children: [{ id: 31, label: '发布产品' }, { id: 32, label: '价格调整' }] },
  { id: 4, label: '系统管理 (System)', children: [{ id: 41, label: '成员管理' }, { id: 42, label: '权限设置' }] }
]

const handleRoleSelect = (row) => {
  if (!row) return
  activeRole.value = row
  // 切换角色时，更新树的勾选状态
  if (treeRef.value) {
    treeRef.value.setCheckedKeys(row.permissions || [])
  }
}

const savePermissions = () => {
  const checkedKeys = treeRef.value.getCheckedKeys()
  ElMessage.success(`[${activeRole.value.roleName}] 权限已成功同步至数据库`)
}
</script>

<style scoped>
.role-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.role-card, .perm-card { height: calc(100vh - 120px); overflow-y: auto; }
</style>