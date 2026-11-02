<template>
  <div class="profile-container page-enter">
    <div class="profile-header">
      <h2 class="profile-title">个人中心</h2>
      <p class="profile-subtitle">查看与维护你的账号信息</p>
    </div>

    <div class="profile-grid">
      <!-- 左侧：个人信息卡片 -->
      <div class="profile-card card-lift">
        <div class="avatar-wrap">
          <el-avatar :size="88" class="profile-avatar">
            <img v-if="info.avatar" :src="info.avatar" alt="avatar" />
            <span v-else>{{ initial }}</span>
          </el-avatar>
          <el-upload
            class="avatar-upload"
            :show-file-list="false"
            :http-request="handleAvatarUpload"
            accept="image/*"
          >
            <el-button size="small" type="primary" plain icon="Camera">更换头像</el-button>
          </el-upload>
        </div>

        <div class="profile-meta">
          <span class="profile-name">{{ info.realName || info.username }}</span>
          <span class="profile-username">@{{ info.username }}</span>
        </div>

        <el-descriptions :column="1" class="profile-desc" border>
          <el-descriptions-item label="姓名">{{ info.realName || '—' }}</el-descriptions-item>
          <el-descriptions-item label="手机">{{ info.phone || '—' }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag size="small" type="primary" effect="plain">{{ info.role || info.roleCode }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="角色标识">{{ info.roleCode }}</el-descriptions-item>
          <el-descriptions-item label="最后登录">{{ info.lastLogin || '—' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 右侧：编辑资料 + 账号安全 -->
      <div class="profile-side">
        <div class="profile-card card-lift">
          <h3 class="card-title">编辑资料</h3>
          <el-form :model="form" label-width="70px">
            <el-form-item label="姓名">
              <el-input v-model="form.realName" placeholder="请输入姓名" maxlength="20" />
            </el-form-item>
            <el-form-item label="手机">
              <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="profile-card card-lift">
          <h3 class="card-title">账号安全</h3>
          <div class="security-row">
            <span class="security-label">登录密码</span>
            <span class="security-hint">定期修改密码可提升账号安全</span>
            <el-button link type="primary" @click="pwdDialogVisible = true">修改密码</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="420px" append-to-body>
      <el-form :model="pwdForm" label-width="90px">
        <el-form-item label="旧密码">
          <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitChangePwd">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'
import { getUserInfo, setUserInfo, clearAuth } from '@/utils/auth'
import { updateProfile, changePassword } from '@/api/modules/auth'
import { uploadFile } from '@/api/modules/upload'

const router = useRouter()

const info = ref(getUserInfo() || {})
const initial = computed(() => (info.value.realName || info.value.username || 'A').charAt(0))

const form = reactive({ realName: '', phone: '' })
const saving = ref(false)

const pwdDialogVisible = ref(false)
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirm: '' })

onMounted(() => {
  form.realName = info.value.realName || ''
  form.phone = info.value.phone || ''
})

const handleAvatarUpload = async (options) => {
  try {
    const res = await uploadFile(options.file, 'avatars')
    const url = res && res.url
    if (!url) return
    const updated = await updateProfile({ avatar: url })
    applyInfo(updated)
    ElMessage.success('头像已更新')
  } catch {
    // 错误已由拦截器统一处理
  }
}

const applyInfo = (fresh) => {
  if (!fresh) return
  info.value = fresh
  setUserInfo(fresh)
}

const saveProfile = async () => {
  saving.value = true
  try {
    const updated = await updateProfile({ realName: form.realName, phone: form.phone })
    applyInfo(updated)
    ElMessage.success('个人信息已更新')
  } catch {
    // ignore
  } finally {
    saving.value = false
  }
}

const submitChangePwd = async () => {
  if (!pwdForm.oldPassword || !pwdForm.newPassword) {
    ElMessage.warning('请填写旧密码与新密码')
    return
  }
  if (pwdForm.newPassword.length < 6) {
    ElMessage.warning('新密码长度至少6位')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  try {
    await changePassword({ oldPassword: pwdForm.oldPassword, newPassword: pwdForm.newPassword })
    ElMessage.success('密码修改成功，请重新登录')
    pwdDialogVisible.value = false
    clearAuth()
    router.push('/login')
  } catch { /* ignore */ }
}
</script>

<style scoped>
.profile-container {
  max-width: 900px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: var(--space-xl);
}

.profile-title {
  margin: 0;
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.profile-subtitle {
  margin: 6px 0 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
}

.profile-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-card);
  padding: var(--space-xl);
}

.avatar-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.profile-avatar {
  background: var(--color-accent);
  color: #fff;
  font-size: 30px;
  font-weight: var(--font-semibold);
}

.profile-meta {
  text-align: center;
  margin-bottom: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-name {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.profile-username {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.profile-desc {
  margin-bottom: 0;
}

.profile-side {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.card-title {
  margin: 0 0 var(--space-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.security-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.security-label {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.security-hint {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .profile-grid { grid-template-columns: 1fr; }
}
</style>
