<!--
  一键报修页面
  用户填写报修信息，提交后生成工单号（HR + 年月日时分秒 + 5位随机数）
-->
<template>
  <view class="repair-apply-page">
    <scroll-view scroll-y class="page-scroll">
      <!-- 表单卡片 -->
      <view class="form-card">
        <view class="card-header">
          <text class="card-title">📝 报修信息</text>
          <text class="card-desc">请详细描述故障情况，以便工程师快速定位问题</text>
        </view>

        <!-- 报修单位 -->
        <view class="form-group">
          <text class="form-label">报修单位 <text class="required">*</text></text>
          <input
            class="form-input"
            v-model="form.company"
            placeholder="请输入您的单位名称"
            placeholder-style="color: #ccc"
            maxlength="50"
          />
        </view>

        <!-- 联系人 -->
        <view class="form-row">
          <view class="form-group" style="flex: 1; margin-right: 16rpx;">
            <text class="form-label">联系人 <text class="required">*</text></text>
            <input
              class="form-input"
              v-model="form.contactName"
              placeholder="您的姓名"
              placeholder-style="color: #ccc"
              maxlength="20"
            />
          </view>
          <view class="form-group" style="flex: 1;">
            <text class="form-label">联系电话 <text class="required">*</text></text>
            <input
              class="form-input"
              v-model="form.contactPhone"
              type="number"
              placeholder="手机号码"
              placeholder-style="color: #ccc"
              maxlength="11"
            />
          </view>
        </view>

        <!-- 用户地址 -->
        <view class="form-group">
          <text class="form-label">用户地址 <text class="required">*</text></text>
          <input
            class="form-input"
            v-model="form.address"
            placeholder="请填写设备所在地址"
            placeholder-style="color: #ccc"
            maxlength="100"
          />
        </view>

        <!-- 设备类型 + 紧急程度 -->
        <view class="form-row">
          <view class="form-group" style="flex: 1; margin-right: 16rpx;">
            <text class="form-label">设备类型</text>
            <select class="form-picker" :class="{ placeholder: !form.deviceType }" @change="onDeviceTypeChange">
              <option value="" disabled selected v-if="!form.deviceType">请选择</option>
              <option v-for="(t, idx) in deviceTypes" :key="t" :value="idx">{{ t }}</option>
            </select>
          </view>
          <view class="form-group" style="flex: 1;">
            <text class="form-label">紧急程度 <text class="required">*</text></text>
            <view class="urgency-group">
              <view
                v-for="item in urgencyLevels"
                :key="item.value"
                class="urgency-btn"
                :class="{ active: form.urgency === item.value }"
                @click="form.urgency = item.value"
              >
                {{ item.label }}
              </view>
            </view>
          </view>
        </view>

        <!-- 报修日期 -->
        <view class="form-group">
          <text class="form-label">报修日期 <text class="required">*</text></text>
          <input type="date" class="form-picker" :class="{ placeholder: !form.repairDate }" :value="form.repairDate" @change="onDateChange" />
        </view>

        <!-- 基本情况 -->
        <view class="form-group">
          <text class="form-label">基本情况 <text class="required">*</text></text>
          <textarea
            class="form-textarea"
            v-model="form.description"
            placeholder="请详细描述设备故障情况（品牌型号、故障现象、期望维修时间等）"
            placeholder-style="color: #ccc"
            maxlength="500"
            :auto-height="true"
          />
          <text class="char-count">{{ form.description.length }}/500</text>
        </view>

        <!-- 上传图片 -->
        <view class="form-group">
          <text class="form-label">现场照片（选填）</text>
          <view class="upload-row">
            <view
              v-for="(img, idx) in images"
              :key="idx"
              class="upload-item"
              @click="previewImage(idx)"
            >
              <img :src="img" class="upload-img" style="object-fit: cover" />
              <view class="upload-delete" @click.stop="removeImage(idx)">✕</view>
            </view>
            <view v-if="images.length < 3" class="upload-item upload-add" @click="chooseImage">
              <text class="add-icon">+</text>
              <text class="add-text">添加图片</text>
            </view>
          </view>
        </view>

        <!-- 提交按钮 -->
        <button
          class="btn-submit"
          :class="{ 'btn-loading': submitting }"
          :disabled="submitting"
          @click="handleSubmit"
        >
          {{ submitting ? '提交中...' : '提交报修' }}
        </button>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </scroll-view>

    <!-- 自定义 TabBar -->
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRepairStore } from '@/stores/repair'
import { uploadFile } from '@/utils/request'
import CustomTabBar from '@/components/CustomTabBar.vue'

const authStore = useAuthStore()
const repairStore = useRepairStore()
const submitting = ref(false)
const images = ref([])

const deviceTypes = ['复印机', '打印机', '投影仪', '扫描仪', '电脑', '其他办公设备']
const urgencyLevels = [
  { label: '🔴 紧急', value: 'urgent' },
  { label: '🟡 一般', value: 'normal' },
  { label: '🟢 不急', value: 'low' }
]

const form = ref({
  company: '',
  contactName: '',
  contactPhone: '',
  address: '',
  deviceType: '',
  urgency: 'normal',
  repairDate: '',
  description: ''
})

const onDeviceTypeChange = (e) => {
  form.value.deviceType = deviceTypes[parseInt(e.target.value)]
}

const onDateChange = (e) => {
  form.value.repairDate = e.target.value
}

const chooseImage = () => {
  uni.chooseImage({
    count: 3 - images.value.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      images.value.push(...res.tempFilePaths)
    }
  })
}

const previewImage = (idx) => {
  uni.previewImage({
    urls: images.value,
    current: idx
  })
}

const removeImage = (idx) => {
  images.value.splice(idx, 1)
}

const validate = () => {
  const { company, contactName, contactPhone, address, repairDate, description } = form.value
  if (!company.trim()) { uni.showToast({ title: '请填写报修单位', icon: 'none' }); return false }
  if (!contactName.trim()) { uni.showToast({ title: '请填写联系人', icon: 'none' }); return false }
  if (!contactPhone || !/^1\d{10}$/.test(contactPhone)) { uni.showToast({ title: '请填写正确手机号', icon: 'none' }); return false }
  if (!address.trim()) { uni.showToast({ title: '请填写用户地址', icon: 'none' }); return false }
  if (!repairDate) { uni.showToast({ title: '请选择日期', icon: 'none' }); return false }
  if (!description.trim()) { uni.showToast({ title: '请描述基本情况', icon: 'none' }); return false }
  return true
}

const handleSubmit = async () => {
  if (!validate()) return

  submitting.value = true
  try {
    // 先上传图片
    const uploadedUrls = []
    for (const img of images.value) {
      try {
        const res = await uploadFile(img)
        uploadedUrls.push(res.data?.url || res.url || '')
      } catch {
        // 单张上传失败不阻塞
      }
    }

    // 提交报修
    await repairStore.createRepair({
      company: form.value.company.trim(),
      contactName: form.value.contactName.trim(),
      contactPhone: form.value.contactPhone,
      address: form.value.address.trim(),
      deviceType: form.value.deviceType,
      urgency: form.value.urgency,
      repairDate: form.value.repairDate,
      description: form.value.description.trim(),
      images: uploadedUrls
    })

    uni.showToast({ title: '报修提交成功', icon: 'success' })

    // 重置表单
    setTimeout(() => {
      form.value = {
        company: '', contactName: '', contactPhone: '', address: '',
        deviceType: '', urgency: 'normal', repairDate: '', description: ''
      }
      images.value = []
    }, 800)

  } catch (err) {
    console.error('提交失败:', err)
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.repair-apply-page {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 140rpx;
}

.page-scroll {
  height: 100vh;
}

.form-card {
  margin: 20rpx 24rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
}

.card-header {
  margin-bottom: 28rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #222;
  display: block;
}

.card-desc {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.form-group {
  margin-bottom: 24rpx;
}

.form-row {
  display: flex;
}

.form-label {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  margin-bottom: 8rpx;
  display: block;
}

.required {
  color: #D32223;
}

.form-input {
  width: 100%;
  height: 80rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.form-picker {
  width: 100%;
  height: 80rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;

  &.placeholder {
    color: #CCCCCC;
  }
}

.picker-arrow {
  font-size: 20rpx;
  color: #999;
}

.form-textarea {
  width: 100%;
  min-height: 180rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.char-count {
  font-size: 22rpx;
  color: #ccc;
  text-align: right;
  display: block;
  margin-top: 6rpx;
}

.urgency-group {
  display: flex;
  gap: 12rpx;
}

.urgency-btn {
  flex: 1;
  height: 64rpx;
  line-height: 64rpx;
  text-align: center;
  font-size: 22rpx;
  border-radius: 8rpx;
  background: #F7F7F7;
  color: #999;
  transition: all 0.25s;

  &.active {
    background: #FFF0F0;
    color: #D32223;
    border: 1px solid #D32223;
    font-weight: 600;
  }
}

.upload-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.upload-item {
  width: 180rpx;
  height: 180rpx;
  border-radius: 12rpx;
  position: relative;
  overflow: hidden;
}

.upload-img {
  width: 100%;
  height: 100%;
}

.upload-delete {
  position: absolute;
  top: 4rpx;
  right: 4rpx;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-add {
  background: #F7F7F7;
  border: 2rpx dashed #DDD;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.add-icon {
  font-size: 48rpx;
  color: #ccc;
  line-height: 1;
}

.add-text {
  font-size: 20rpx;
  color: #ccc;
  margin-top: 4rpx;
}

.btn-submit {
  width: 100%;
  height: 92rpx;
  line-height: 92rpx;
  background: #D32223;
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  margin-top: 12rpx;
  text-align: center;

  &:active { opacity: 0.85; transform: scale(0.97); }
  &[disabled] { background: #CCCCCC; }
}

.safe-bottom {
  height: 40rpx;
}
</style>
