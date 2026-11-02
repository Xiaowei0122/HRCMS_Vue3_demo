<!--
  地址编辑 — 新增 / 编辑服务地址
  ?id=xxx 时为编辑模式
-->
<template>
  <view class="page">
    <PageNavbar :title="isEdit ? '编辑地址' : '新增地址'" />

    <scroll-view scroll-y class="scroll-body">
      <view class="form-card">
        <view class="form-row">
          <text class="form-row-label"><text class="required">*</text>联系人</text>
          <input class="form-input" v-model="form.contactName" placeholder="收件人姓名" placeholder-style="color:#C9CDD4" maxlength="20" />
        </view>

        <view class="form-row">
          <text class="form-row-label"><text class="required">*</text>联系电话</text>
          <input class="form-input" v-model="form.contactPhone" type="number" placeholder="手机号码" placeholder-style="color:#C9CDD4" maxlength="11" />
        </view>

        <view class="form-row">
          <text class="form-row-label"><text class="required">*</text>详细地址</text>
          <textarea class="form-textarea" v-model="form.address" placeholder="省市区 / 街道 / 门牌号等" placeholder-style="color:#C9CDD4" maxlength="100" :auto-height="true" />
          <text class="count">{{ form.address.length }}/100</text>
        </view>

        <view class="form-row">
          <view class="switch-row" @click="form.isDefault = !form.isDefault">
            <view class="switch-text">
              <text class="switch-label">设为默认地址</text>
              <text class="switch-desc">报修时优先使用该地址</text>
            </view>
            <view class="switch" :class="{ on: form.isDefault }">
              <view class="switch-dot" />
            </view>
          </view>
        </view>
      </view>
      <view class="safe-bottom" />
    </scroll-view>

    <view class="bottom-bar">
      <button class="primary-btn" :disabled="saving" @click="handleSave">
        <SvgIcon name="check" :size="18" color="#fff" />
        <text>{{ saving ? '保存中...' : '保存地址' }}</text>
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAddressStore } from '@/stores/address'
import PageNavbar from '@/components/PageNavbar.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const router = useRouter()
const route = useRoute()
const addressStore = useAddressStore()

const isEdit = computed(() => !!route.query.id)
const saving = ref(false)
const form = ref({ contactName: '', contactPhone: '', address: '', isDefault: false })

const loadEdit = async () => {
  if (!isEdit.value) return
  try {
    const list = await addressStore.fetchList()
    const cur = list.find((a) => a.id === route.query.id)
    if (cur) {
      form.value = {
        contactName: cur.contactName,
        contactPhone: cur.contactPhone,
        address: cur.address,
        isDefault: !!cur.isDefault
      }
    }
  } catch { /* 已 toast */ }
}

const handleSave = async () => {
  const f = form.value
  if (!f.contactName.trim()) return uni.showToast({ title: '请填写联系人', icon: 'none' })
  if (!/^1\d{10}$/.test(f.contactPhone)) return uni.showToast({ title: '请填写正确手机号', icon: 'none' })
  if (!f.address.trim()) return uni.showToast({ title: '请填写详细地址', icon: 'none' })

  saving.value = true
  try {
    const payload = {
      contactName: f.contactName.trim(),
      contactPhone: f.contactPhone,
      address: f.address.trim(),
      isDefault: f.isDefault
    }
    if (isEdit.value) await addressStore.update(route.query.id, payload)
    else await addressStore.create(payload)
    uni.showToast({ title: '已保存', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 600)
  } catch { /* 已 toast */ }
  finally { saving.value = false }
}

onMounted(loadEdit)
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; }
.scroll-body { flex: 1; }

.form-card {
  margin: 24rpx;
  background: #fff;
  border-radius: 32rpx;
  padding: 36rpx 32rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
}
.form-row { margin-top: 28rpx; }
.form-row:first-child { margin-top: 0; }
.form-row-label {
  font-size: 26rpx;
  color: #4E5969;
  font-weight: 500;
  margin-bottom: 12rpx;
  display: block;
}
.required { color: #F53F3F; }

.form-input {
  width: 100%;
  height: 88rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #1D2129;
  box-sizing: border-box;
}
.form-textarea {
  width: 100%;
  min-height: 140rpx;
  background: #F7F8FA;
  border: 1.5px solid #E5E6EB;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  color: #1D2129;
  box-sizing: border-box;
  line-height: 1.6;
}
.count { font-size: 22rpx; color: #86909C; text-align: right; display: block; margin-top: 8rpx; }

/* 默认地址开关 */
.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
}
.switch-text { display: flex; flex-direction: column; gap: 4rpx; }
.switch-label { font-size: 28rpx; color: #1D2129; font-weight: 500; }
.switch-desc { font-size: 22rpx; color: #86909C; }
.switch {
  width: 88rpx;
  height: 48rpx;
  border-radius: 24rpx;
  background: #E5E6EB;
  position: relative;
  transition: background 0.2s ease;
  flex-shrink: 0;
}
.switch.on { background: #165DFF; }
.switch-dot {
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s ease;
  box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.15);
}
.switch.on .switch-dot { transform: translateX(40rpx); }

/* 底部按钮 */
.bottom-bar {
  flex-shrink: 0;
  padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F2F3F5;
}
.primary-btn {
  width: 100%;
  height: 92rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);
  &:active { opacity: 0.9; transform: scale(0.98); }
  &[disabled] { background: #C9CDD4; box-shadow: none; }
}

.safe-bottom { height: 24rpx; }
</style>
