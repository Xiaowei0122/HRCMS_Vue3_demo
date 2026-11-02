<template>
  <div class="page-container">
    <el-card shadow="never">
      <!-- 搜索与操作栏 -->
      <div class="header-tools">
        <el-form :inline="true" :model="query">
          <el-form-item>
            <el-input v-model="query.name" placeholder="员工姓名/账号" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
            <el-button icon="Plus" @click="handleAdd">新增成员</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table :data="userList" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="username" label="登录账号" width="150" />
        <el-table-column prop="realName" label="姓名" width="120" />
        <el-table-column label="角色" width="150">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row)">{{ row.role || '未分配' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLogin" label="最后登录" min-width="180" />
        <el-table-column label="操作" fixed="right" width="340">
          <template #default="scope">
            <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button v-if="!isSuperAdminUser(scope.row)" link type="primary" @click="openRoleDialog(scope.row)">角色权限</el-button>
            <el-button link type="warning" @click="handleResetPwd(scope.row)">重置密码</el-button>
            <template v-if="isPending(scope.row)">
              <el-button link type="success" @click="handleApprove(scope.row)">审批</el-button>
              <el-button link type="danger" @click="handleReject(scope.row)">驳回</el-button>
            </template>
            <template v-else>
              <el-button v-if="!isSuperAdminUser(scope.row)" link :type="isActive(scope.row) ? 'danger' : 'success'" @click="toggleStatus(scope.row)">
                {{ isActive(scope.row) ? '停用' : '启用' }}
              </el-button>
            </template>
            <el-button v-if="!isSuperAdminUser(scope.row)" link type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          v-model:current-page="query.page"
          v-model:page-size="query.size"
          @current-change="fetchUserList"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '修改成员信息' : '新增成员账号'" width="450px" append-to-body>
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="登录账号">
          <el-input v-model="userForm.username" :disabled="isEdit" placeholder="建议使用拼音或手机号" />
        </el-form-item>
        <el-form-item label="成员姓名">
          <el-input v-model="userForm.realName" />
        </el-form-item>
        <el-form-item label="分配角色">
          <el-select v-model="userForm.roleCode" placeholder="选择角色" style="width: 100%" :disabled="userForm.roleCode === 'super_admin'">
            <el-option
              v-for="r in assignableRoles"
              :key="r.id"
              :label="r.roleName"
              :value="r.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="初始密码" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="默认 123456" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUser" :loading="submitting">确定提交</el-button>
      </template>
    </el-dialog>

    <!-- 编辑角色权限弹窗 -->
    <el-dialog v-model="roleDialogVisible" title="编辑角色权限" width="420px" append-to-body>
      <el-form :model="roleForm" label-width="80px">
        <el-form-item label="成员">
          <el-input :model-value="roleForm.realName" disabled />
        </el-form-item>
        <el-form-item label="角色职位">
          <el-select v-model="roleForm.roleCode" placeholder="选择角色职位" style="width: 100%">
            <el-option
              v-for="r in assignableRoles"
              :key="r.id"
              :label="r.roleName"
              :value="r.code"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRole" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getUserList, createUser, updateUser, deleteUser,
  toggleUserStatus, resetUserPassword, approveUser, rejectUser
} from '@/api/modules/users'
import { getRoleList } from '@/api/modules/roles'
import { getUserInfo } from '@/utils/auth'

const roleTagType = (row) => {
  const map = {
    'super_admin': 'danger',
    'admin': 'warning',
    'business': 'primary',
    'engineer': 'success',
    'logistics': 'info',
    'normal': 'info'
  }
  return map[row.roleCode] || 'info'
}

const isActive = (row) => row.status === 'active' || row.status === true
const isPending = (row) => row.status === 'pending'
const isSuperAdminUser = (row) => row.roleCode === 'super_admin'
const statusText = (status) => {
  if (status === 'active' || status === true) return '正常'
  if (status === 'pending') return '待审批'
  return '停用'
}
const statusTagType = (status) => {
  if (status === 'active' || status === true) return 'success'
  if (status === 'pending') return 'warning'
  return 'danger'
}

const query = reactive({ name: '', page: 1, size: 10 })
const dialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const submitting = ref(false)
const userList = ref([])
const total = ref(0)
const editingId = ref(null)
const roleList = ref([])
const roleDialogVisible = ref(false)

const userForm = reactive({
  username: '', realName: '', roleCode: '', phone: '', password: ''
})

const roleForm = reactive({ id: '', realName: '', roleCode: '' })

// 当前登录者的 rank（越小越高），用于过滤「我可分配」的角色
const myRank = computed(() => getUserInfo()?.rank ?? 99)
const assignableRoles = computed(() => {
  return roleList.value.filter((r) => myRank.value === 0 || (r.rank ?? 99) > myRank.value)
})

const fetchRoleList = async () => {
  try {
    const res = await getRoleList()
    roleList.value = Array.isArray(res) ? res : (res.records || [])
  } catch {
    // 角色拉取失败时静默降级，不影响成员列表
  }
}

const fetchUserList = async () => {
  loading.value = true
  try {
    const res = await getUserList({ name: query.name, page: query.page, size: query.size })
    if (Array.isArray(res)) {
      userList.value = res
      total.value = res.length
    } else {
      userList.value = res.records || []
      total.value = res.total || 0
    }
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  query.page = 1
  fetchUserList()
}

const handleAdd = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(userForm, { username: '', realName: '', roleCode: '', phone: '', password: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(userForm, {
    username: row.username,
    realName: row.realName,
    roleCode: row.roleCode,
    phone: row.phone,
    password: ''
  })
  dialogVisible.value = true
}

const submitUser = async () => {
  submitting.value = true
  try {
    const payload = {
      username: userForm.username,
      realName: userForm.realName,
      roleCode: userForm.roleCode,
      phone: userForm.phone
    }
    if (!isEdit.value) {
      payload.password = userForm.password || '123456'
    }

    if (isEdit.value) {
      await updateUser(editingId.value, payload)
      ElMessage.success('成员信息已更新')
    } else {
      await createUser(payload)
      ElMessage.success('新成员已创建')
    }
    dialogVisible.value = false
    fetchUserList()
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    submitting.value = false
  }
}

// 停用/启用：后端取反当前状态并返回新状态字符串（active|disabled）
const toggleStatus = async (row) => {
  try {
    const newStatus = await toggleUserStatus(row.id)
    row.status = newStatus
    ElMessage.success(`${row.realName} 的账号已${newStatus === 'active' ? '启用' : '停用'}`)
  } catch {
    fetchUserList()
  }
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定审批通过 [${row.realName}] 的注册请求吗？`, '审批', { type: 'info' })
    await approveUser(row.id)
    ElMessage.success('已审批通过')
    fetchUserList()
  } catch { /* 用户取消或失败 */ }
}

const handleReject = async (row) => {
  try {
    await ElMessageBox.confirm(`确定驳回 [${row.realName}] 的注册请求吗？驳回后该账号将被停用。`, '驳回', { type: 'warning' })
    await rejectUser(row.id)
    ElMessage.success('已驳回')
    fetchUserList()
  } catch { /* 用户取消或失败 */ }
}

const openRoleDialog = (row) => {
  roleForm.id = row.id
  roleForm.realName = row.realName
  roleForm.roleCode = row.roleCode || ''
  roleDialogVisible.value = true
}

const submitRole = async () => {
  if (!roleForm.roleCode) {
    ElMessage.warning('请选择角色职位')
    return
  }
  submitting.value = true
  try {
    await updateUser(roleForm.id, { roleCode: roleForm.roleCode })
    ElMessage.success('角色权限已更新')
    roleDialogVisible.value = false
    fetchUserList()
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    submitting.value = false
  }
}

const handleResetPwd = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要重置 [${row.realName}] 的登录密码吗？`, '警告', { type: 'warning' })
    await resetUserPassword(row.id)
    ElMessage.success('密码已重置')
  } catch {
    // 用户取消或请求失败
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该成员账号吗？', '警告', { type: 'error' })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchUserList()
  } catch {
    // 用户取消或请求失败
  }
}

onMounted(() => {
  fetchUserList()
  fetchRoleList()
})
</script>

<style scoped>
.header-tools { margin-bottom: 20px; }
.page-container { background: transparent; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
