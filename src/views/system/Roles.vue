<template>
  <div class="role-container">
    <el-row :gutter="20">
      <!-- 左侧：角色列表 -->
      <el-col :span="10">
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
            <el-table-column label="角色名称">
              <template #default="{ row }">
                <div class="role-name-cell">
                  <el-icon><User /></el-icon>
                  <span>{{ row.roleName }}</span>
                  <el-tag v-if="row.builtin" size="small" type="warning" effect="plain">
                    <el-icon style="vertical-align: -2px"><Lock /></el-icon>
                    内置
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="code" label="标识码" width="90">
              <template #default="{ row }">
                <el-tag size="small" type="info" effect="plain">{{ row.code }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="层级" width="70" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="rankTagType(row.rank)">{{ rankLabel(row.rank) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="已授权" width="70" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="success" effect="light">{{ (row.permissions || []).length }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="editRole(row)">编辑</el-button>
                <el-button v-if="!row.builtin" link type="danger" @click="removeRole(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：权限树配置 -->
      <el-col :span="14">
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
              <div style="display: flex; gap: 8px">
                <el-button
                  size="default"
                  :disabled="!activeRole.roleName || isSuperAdmin"
                  :icon="CopyDocument"
                  @click="openCopy"
                >复制权限</el-button>
                <el-button
                  type="success"
                  size="default"
                  :disabled="!activeRole.roleName || isSuperAdmin"
                  :icon="Check"
                  :loading="savingPerms"
                  @click="savePermissions"
                >保存权限</el-button>
              </div>
            </div>
          </template>

          <div v-if="activeRole.roleName" class="tree-wrapper">
            <el-alert
              v-if="isSuperAdmin"
              title="超级管理员默认拥有全部权限，不可编辑或删除自身权限（防止误关系统设置导致无法登录后台）。"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 20px"
            />
            <el-alert
              v-else
              title="配置说明：勾选主菜单将自动开启该分类下的所有子功能权限。"
              type="warning"
              :closable="false"
              show-icon
              style="margin-bottom: 20px"
            />

            <el-tree
              v-if="!isSuperAdmin"
              ref="treeRef"
              :data="menuData"
              show-checkbox
              node-key="id"
              default-expand-all
              :props="{ label: 'label', children: 'children' }"
            >
              <template #default="{ node, data }">
                <span class="custom-tree-node">
                  <el-icon v-if="data.icon" class="node-icon"><component :is="data.icon" /></el-icon>
                  <span>{{ node.label }}</span>
                  <span v-if="data.code" class="node-code">{{ data.code }}</span>
                  <span v-if="data.children && data.children.length" class="node-actions" @click.stop>
                    <el-button link type="primary" size="small" @click.stop="checkGroup(data)">全选</el-button>
                    <el-button link type="info" size="small" @click.stop="clearGroup(data)">清空</el-button>
                  </span>
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
        <el-form-item label="层级">
          <el-select v-model="roleForm.rank" placeholder="选择层级" style="width: 100%" :disabled="roleEditBuiltin">
            <el-option label="超级管理员 (0)" :value="0" :disabled="!roleEditBuiltin" />
            <el-option label="管理员 (1)" :value="1" :disabled="!roleEditBuiltin" />
            <el-option label="业务层 (2)" :value="2" />
            <el-option label="普通用户 (3)" :value="3" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRole">保存</el-button>
      </template>
    </el-dialog>

    <!-- 从其他角色复制权限弹窗 -->
    <el-dialog v-model="copyDialogVisible" title="从其他角色复制权限" width="440px" append-to-body>
      <el-alert
        title="复制后会在当前角色已勾选基础上套用源角色的权限，仍需点击「保存权限」才生效。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />
      <el-form label-width="90px">
        <el-form-item label="源角色">
          <el-select v-model="copySourceId" placeholder="选择要复制的角色" style="width: 100%">
            <el-option
              v-for="r in copySourceRoles"
              :key="r.id"
              :label="`${r.roleName}（已授权 ${(r.permissions || []).length} 项）`"
              :value="r.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCopy">复制</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, markRaw } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Check, User, Monitor, Document, Headset,
  Box, Setting, Wallet, Lock, CopyDocument,
  DataAnalysis, OfficeBuilding, Tools, Delete, Collection, Cellphone
} from '@element-plus/icons-vue'
import { getRoleList, createRole, updateRole, deleteRole, saveRolePermissions, getPermissionTree } from '@/api/modules/roles'

const treeRef = ref(null)
const activeRole = ref({})
const isSuperAdmin = computed(() => activeRole.value.code === 'super_admin' || activeRole.value.rank === 0)
const roleList = ref([])
const rolesLoading = ref(false)
const savingPerms = ref(false)

// 新增/编辑角色弹窗状态
const roleDialogVisible = ref(false)
const roleEditId = ref(null)
const roleEditBuiltin = ref(false)
const roleForm = ref({ roleName: '', code: '', rank: 2 })

const rankLabel = (rank) => {
  if (rank === 0) return '超管'
  if (rank === 1) return '管理员'
  if (rank === 2) return '业务层'
  return '普通'
}
const rankTagType = (rank) => {
  if (rank === 0) return 'danger'
  if (rank === 1) return 'warning'
  if (rank === 2) return 'primary'
  return 'info'
}

// 叶子 id 集合（父分组 id 仅作树分组，不参与授权）
const collectLeafIds = (nodes) => {
  const ids = new Set()
  const walk = (list) => {
    list.forEach(n => {
      if (n.children && n.children.length) walk(n.children)
      else ids.add(n.id)
    })
  }
  walk(nodes)
  return ids
}
const filterLeafKeys = (keys) => {
  const leafSet = collectLeafIds(menuData.value)
  return (keys || []).filter(id => leafSet.has(id))
}

// 收集单个分组节点下所有叶子 id
const collectLeafIdsOf = (node) => {
  const ids = []
  const walk = (n) => {
    if (n.children && n.children.length) n.children.forEach(walk)
    else ids.push(n.id)
  }
  walk(node)
  return ids
}

// 当前已勾选的叶子 id（getCheckedKeys(true) 排除父分组）
const currentLeafChecked = () => (treeRef.value ? treeRef.value.getCheckedKeys(true) : [])

// 分组级「全选」：勾选该分组下所有叶子
const checkGroup = (node) => {
  const leafIds = collectLeafIdsOf(node)
  const merged = new Set([...currentLeafChecked(), ...leafIds])
  treeRef.value?.setCheckedKeys([...merged])
}

// 分组级「清空」：取消该分组下所有叶子
const clearGroup = (node) => {
  const leafIds = new Set(collectLeafIdsOf(node))
  const rest = currentLeafChecked().filter(id => !leafIds.has(id))
  treeRef.value?.setCheckedKeys(rest)
}

// ── 从其他角色复制权限 ──
const copyDialogVisible = ref(false)
const copySourceId = ref(null)
const copySourceRoles = computed(() => roleList.value.filter(r => r.id !== activeRole.value.id))

const openCopy = () => {
  copySourceId.value = null
  copyDialogVisible.value = true
}

const confirmCopy = () => {
  if (!copySourceId.value) return ElMessage.warning('请选择源角色')
  const src = roleList.value.find(r => r.id === copySourceId.value)
  if (!src) return
  treeRef.value?.setCheckedKeys(filterLeafKeys(src.permissions))
  copyDialogVisible.value = false
  ElMessage.success('已套用源角色权限，请点击「保存权限」生效')
}

// 菜单树数据（后端 /permissions/tree 优先，前端静态树兜底）
// 结构与排序与左侧主菜单一致：概览 需求 售后 产品 门户 报表 财务 系统。
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
      { id: 33, label: '所有工单' },
      { id: 34, label: '工程师排期' },
      { id: 35, label: '投诉建议管理' },
      { id: 37, label: '工单调阅/导出' }
    ]
  },
  {
    id: 12,
    label: '小程序管理',
    icon: markRaw(Cellphone),
    children: [
      { id: 36, label: '联系我们配置' },
      { id: 38, label: '知识库管理' }
    ]
  },
  { id: 4, label: '产品中心', icon: markRaw(Box) },
  {
    id: 8,
    label: '门户网站管理',
    icon: markRaw(Setting),
    children: [
      { id: 81, label: '全局配置' },
      { id: 82, label: '新闻中心' },
      { id: 83, label: '荣誉与相册' },
      { id: 84, label: '合作伙伴与案例' }
    ]
  },
  { id: 11, label: '数据报表', icon: markRaw(DataAnalysis) },
  {
    id: 10,
    label: '财务管理',
    icon: markRaw(Wallet),
    children: [
      { id: 101, label: '共享文件' },
      { id: 102, label: '资产管理' },
      { id: 103, label: '车辆管理' }
    ]
  },
  {
    id: 9,
    label: '系统管理',
    icon: markRaw(Setting),
    children: [
      { id: 91, label: '成员管理' },
      { id: 92, label: '权限设置' },
      { id: 93, label: '操作日志' },
      { id: 94, label: '数据字典', icon: markRaw(Collection) },
      { id: 95, label: '部门管理', icon: markRaw(OfficeBuilding) },
      { id: 96, label: '系统设置', icon: markRaw(Tools) },
      { id: 97, label: '回收站', icon: markRaw(Delete) }
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
      // 重新勾选当前角色的权限（叶子化过滤兜底）
      nextTick(() => {
        if (treeRef.value && activeRole.value.id) {
          treeRef.value.setCheckedKeys(filterLeafKeys(activeRole.value.permissions))
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
      treeRef.value.setCheckedKeys(filterLeafKeys(row.permissions))
    }
  })
}

const savePermissions = async () => {
  // 只保存叶子节点（getCheckedKeys(true) 排除被勾选的父分组 id）
  const checkedKeys = treeRef.value.getCheckedKeys(true)
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
  roleEditBuiltin.value = false
  roleForm.value = { roleName: '', code: '', rank: 2 }
  roleDialogVisible.value = true
}

const editRole = (row) => {
  roleEditId.value = row.id
  roleEditBuiltin.value = !!row.builtin
  roleForm.value = { roleName: row.roleName, code: row.code, rank: row.rank ?? 2 }
  roleDialogVisible.value = true
}

const confirmRole = async () => {
  if (!roleForm.value.roleName.trim()) return ElMessage.warning('请输入角色名称')
  if (!roleForm.value.code.trim()) return ElMessage.warning('请输入标识码')
  try {
    if (roleEditId.value) {
      await updateRole(roleEditId.value, { roleName: roleForm.value.roleName, rank: roleForm.value.rank })
      ElMessage.success('角色已更新')
    } else {
      await createRole({ roleName: roleForm.value.roleName, code: roleForm.value.code, rank: roleForm.value.rank })
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

.role-name-cell { display: flex; align-items: center; gap: 8px; min-width: 0; }
.role-name-cell > span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tree-wrapper { padding: 10px; }

.custom-tree-node { display: flex; align-items: center; gap: 8px; font-size: 14px; flex: 1; min-width: 0; }
.node-icon { font-size: 16px; color: var(--text-secondary); }
.node-code { font-size: 12px; color: var(--text-muted); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.node-actions { margin-left: auto; display: inline-flex; gap: 4px; flex-shrink: 0; }

:deep(.el-tree-node__content) { height: 36px; border-radius: 4px; }
:deep(.el-tree-node__content:hover) { background-color: #f0f7ff; }

:deep(.el-card__body) { height: calc(100% - 60px); overflow-y: auto; }
</style>
