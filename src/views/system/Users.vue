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
      <el-table :data="userList" border stripe style="width: 100%">
        <el-table-column prop="username" label="登录账号" width="150" />
        <el-table-column prop="realName" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="150">
          <template #default="{row}">
            <el-tag :type="row.role === '超级管理员' ? 'danger' : 'success'">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-switch v-model="row.status" @change="statusChange(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="lastLogin" label="最后登录" min-width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="scope">
            <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button link type="warning">重置密码</el-button>
            <el-button link type="danger" @click="handleDelete(scope.$index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
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
        <el-button type="primary" @click="submitUser">确定提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const query = reactive({ name: '' })
const dialogVisible = ref(false)
const isEdit = ref(false)

const userList = ref([
  { username: 'admin', realName: '王总', role: '超级管理员', phone: '13888888888', status: true, lastLogin: '2024-04-03 10:00' },
  { username: 'sale01', realName: '小张', role: '销售主管', phone: '13999999999', status: true, lastLogin: '2024-04-02 15:30' }
])

const userForm = reactive({ username: '', realName: '', role: '', phone: '', password: '' })

const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const submitUser = () => {
  ElMessage.success('操作成功！')
  dialogVisible.value = false
}

const statusChange = (row) => {
  ElMessage.info(`${row.realName} 的账号已${row.status ? '开启' : '锁定'}`)
}

const handleDelete = (index) => {
  ElMessageBox.confirm('确定要删除该成员账号吗？', '警告', { type: 'error' }).then(() => {
    userList.value.splice(index, 1)
    ElMessage.success('删除成功')
  })
}
</script>

<style scoped>
.header-tools { margin-bottom: 20px; }
.page-container { background: transparent; }
</style>