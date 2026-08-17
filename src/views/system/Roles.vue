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
            v-loading="rolesLoading"
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
            <el-table-column label="操作" width="130" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="editRole(row)">编辑</el-button>
                <el-button link type="danger" @click="removeRole(row)">删除</el-button>
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
                <span v-else style="color: var(--text-muted); font-size: 14px">请选择左侧角色</span>
              </span>
              <el-button
                type="success"
                size="default"
                :disabled="!activeRole.roleName"
                :icon="Check"
                :loading="savingPerms"
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

    <!-- 新增/编辑角色弹窗 -->
    <el-dialog v-model="roleDialogVisible" :title="roleEditId ? '编辑角色' : '新增角色'" width="420px" append-to-body>
      <el-form :model="roleForm" label-width="90px">
        <el-form-item label="角色名称">
          <el-input v-model="roleForm.roleName" placeholder="例如：运营专员" />
        </el-form-item>
        <el-form-item label="标识码">
          <el-input v-model="roleForm.code" placeholder="例如：operator" :disabled="!!roleEditId" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRole">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, markRaw } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Check, User, Monitor, Document, Headset,
  Box, ChatDotSquare, Trophy, Briefcase, Setting, Wallet
} from '@element-plus/icons-vue'
import { getRoleList, createRole, updateRole, deleteRole, saveRolePermissions, getPermissionTree } from '@/api/modules/roles'

const treeRef = ref(null)
const activeRole = ref({})
const roleList = ref([])
const rolesLoading = ref(false)
const savingPerms = ref(false)

// 新增/编辑角色弹窗状态
const roleDialogVisible = ref(false)
const roleEditId = ref(null)
const roleForm = ref({ roleName: '', code: '' })

// 菜单树数据（后端 /permissions/tree 优先，前端静态树兜底）
const menuData = ref([
  { id: 1, label: '系统概览', icon: markRaw(Monitor) },
  { id: 2, label: '需求单管理', icon: markRaw(Document) },
  {
    id: 3,
    label: '售后报修管理',
    icon: markRaw(Headset),
    children: [
      { id: 31, label: '一键报修' },
      { id: 32, label: '我的报修 / 工单' },
      { id: 33, label: '所有工单 (抢单池)' },
      { id: 34, label: '工程师期排' },
      { id: 35, label: '投诉建议管理' },
      { id: 36, label: '联系我们配置' }
    ]
  },
  { id: 4, label: '产品中心', icon: markRaw(Box) },
  { id: 5, label: '新闻中心', icon: markRaw(ChatDotSquare) },
  { id: 6, label: '荣誉与相册', icon: markRaw(Trophy) },
  { id: 7, label: '合作伙伴与案例', icon: markRaw(Briefcase) },
  { id: 8, label: '门户全局配置', icon: markRaw(Setting) },
  {
    id: 9,
    label: '系统管理',
    icon: markRaw(Setting),
    children: [
      { id: 91, label: '成员管理' },
      { id: 92, label: '权限设置' },
      { id: 93, label: '操作日志' }
    ]
  },
  {
    id: 10,
    label: '财务管理',
    icon: markRaw(Wallet),
    children: [
      { id: 101, label: '共享文件' },
      { id: 102, label: '资产管理' }
    ]
  }
])

const fetchRoles = async () => {
  rolesLoading.value = true
  try {
    const res = await getRoleList()
    roleList.value = Array.isArray(res) ? res : (res.records || [])
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    rolesLoading.value = false
  }
}

const fetchPermissionTree = async () => {
  try {
    const tree = await getPermissionTree()
    if (tree && tree.length) {
      // 后端菜单树优先，前端静态树作为兜底
      menuData.value = tree
      // 重新勾选当前角色的权限
      nextTick(() => {
        if (treeRef.value && activeRole.value.id) {
          treeRef.value.setCheckedKeys(activeRole.value.permissions || [])
        }
      })
    }
  } catch {
    // 菜单树使用前端默认数据
  }
}

const handleRoleSelect = (row) => {
  if (!row) return
  activeRole.value = row

  nextTick(() => {
    if (treeRef.value) {
      treeRef.value.setCheckedKeys(row.permissions || [])
    }
  })
}

const savePermissions = async () => {
  const checkedKeys = treeRef.value.getCheckedKeys()
  savingPerms.value = true
  try {
    await saveRolePermissions(activeRole.value.id, checkedKeys)
    activeRole.value.permissions = checkedKeys
    ElMessage.success(`角色 [${activeRole.value.roleName}] 权限更新成功！`)
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    savingPerms.value = false
  }
}

const addRole = () => {
  roleEditId.value = null
  roleForm.value = { roleName: '', code: '' }
  roleDialogVisible.value = true
}

const editRole = (row) => {
  roleEditId.value = row.id
  roleForm.value = { roleName: row.roleName, code: row.code }
  roleDialogVisible.value = true
}

const confirmRole = async () => {
  if (!roleForm.value.roleName.trim()) return ElMessage.warning('请输入角色名称')
  if (!roleForm.value.code.trim()) return ElMessage.warning('请输入标识码')
  try {
    if (roleEditId.value) {
      await updateRole(roleEditId.value, { roleName: roleForm.value.roleName })
      ElMessage.success('角色已更新')
    } else {
      await createRole({ roleName: roleForm.value.roleName, code: roleForm.value.code })
      ElMessage.success('角色已创建')
    }
    roleDialogVisible.value = false
    fetchRoles()
  } catch { /* ignore */ }
}

const removeRole = (row) => {
  ElMessageBox.confirm(`确定删除角色 [${row.roleName}] 吗？该操作不可恢复。`, '确认删除', {
    type: 'warning',
    confirmButtonText: '删除'
  }).then(async () => {
    try {
      await deleteRole(row.id)
      ElMessage.success('角色已删除')
      if (activeRole.value.id === row.id) activeRole.value = {}
      fetchRoles()
    } catch { /* ignore */ }
  }).catch(() => {})
}

onMounted(() => {
  fetchRoles()
  fetchPermissionTree()
})
</script>

<style scoped>
.role-container { padding: 10px; background-color: var(--bg-muted); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title-text { font-weight: bold; font-size: 16px; }

.role-card, .perm-card {
  height: calc(100vh - 140px);
  border-radius: var(--radius-md);
}

.role-name-cell { display: flex; align-items: center; gap: 8px; }
.tree-wrapper { padding: 10px; }

.custom-tree-node { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.node-icon { font-size: 16px; color: var(--text-secondary); }

:deep(.el-tree-node__content) { height: 36px; border-radius: 4px; }
:deep(.el-tree-node__content:hover) { background-color: #f0f7ff; }

:deep(.el-card__body) { height: calc(100% - 60px); overflow-y: auto; }
</style>
