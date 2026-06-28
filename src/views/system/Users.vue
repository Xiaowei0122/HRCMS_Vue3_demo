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
        <el-table-column prop="role" label="角色" width="150">
          <template #default="{ row }">
            <el-tag :type="row.role === '超级管理员' ? 'danger' : 'success'">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.status" @change="statusChange(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="lastLogin" label="最后登录" min-width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="scope">
            <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button link type="warning" @click="handleResetPwd(scope.row)">重置密码</el-button>
            <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '修改成员信息' : '新增成员账号'" width="450px">
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="登录账号">
          <el-input v-model="userForm.username" :disabled="isEdit" placeholder="建议使用拼音或手机号" />
        </el-form-item>
        <el-form-item label="成员姓名">
          <el-input v-model="userForm.realName" />
        </el-form-item>
        <el-form-item label="分配角色">
          <el-select v-model="userForm.role" placeholder="选择角色" style="width: 100%">
            <el-option label="超级管理员" value="超级管理员" />
            <el-option label="销售主管" value="销售主管" />
            <el-option label="技术支持" value="技术支持" />
            <el-option label="财务经理" value="财务经理" />
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getUserList, createUser, updateUser, deleteUser,
  toggleUserStatus, resetUserPassword
} from '@/api/modules/users'

const query = reactive({ name: '', page: 1, size: 10 })
const dialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const submitting = ref(false)
const userList = ref([])
const total = ref(0)
const editingId = ref(null)

const userForm = reactive({
  username: '', realName: '', role: '', phone: '', password: ''
})

const fetchUserList = async () => {
  loading.value = true
  try {
    const res = await getUserList({ name: query.name, page: query.page, size: query.size })
    // 适配 { records: [], total: N } 或直接返回数组
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
  Object.assign(userForm, { username: '', realName: '', role: '', phone: '', password: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(userForm, {
    username: row.username,
    realName: row.realName,
    role: row.role,
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
      role: userForm.role,
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

const statusChange = async (row) => {
  try {
    await toggleUserStatus(row.id, row.status)
    ElMessage.info(`${row.realName} 的账号已${row.status ? '开启' : '锁定'}`)
  } catch {
    row.status = !row.status // 恢复开关状态
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
})
</script>

<style scoped>
.header-tools { margin-bottom: 20px; }
.page-container { background: transparent; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
