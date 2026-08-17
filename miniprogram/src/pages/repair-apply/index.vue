<!--
  一键报修
-->
<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-body">
      <view class="card">
        <view class="card-head">
          <view class="head-row">
            <SvgIcon name="wrench" :size="28" />
            <text class="head-title">报修信息</text>
          </view>
          <text class="head-desc">请详细描述故障情况，以便工程师快速定位问题</text>
        </view>

        <view class="form-group">
          <text class="label">报修单位 <text class="req">*</text></text>
          <input class="input" v-model="form.company" placeholder="请输入您的单位名称" placeholder-style="color:#CBD5E1" maxlength="50" />
        </view>

        <view class="row">
          <view class="form-group flex1">
            <text class="label">联系人 <text class="req">*</text></text>
            <input class="input" v-model="form.contactName" placeholder="您的姓名" placeholder-style="color:#CBD5E1" maxlength="20" />
          </view>
          <view class="form-group flex1">
            <text class="label">联系电话 <text class="req">*</text></text>
            <input class="input" v-model="form.contactPhone" type="number" placeholder="手机号码" placeholder-style="color:#CBD5E1" maxlength="11" />
          </view>
        </view>

        <view class="form-group">
          <text class="label">用户地址 <text class="req">*</text></text>
          <input class="input" v-model="form.address" placeholder="请填写设备所在地址" placeholder-style="color:#CBD5E1" maxlength="100" />
        </view>

        <view class="row">
          <view class="form-group flex1">
            <text class="label">设备类型</text>
            <picker mode="selector" :range="deviceTypes" @change="(e) => form.deviceType = deviceTypes[e.detail.value]">
              <view class="picker" :class="{ dim: !form.deviceType }">
                <text>{{ form.deviceType || '请选择' }}</text>
                <SvgIcon name="caretRight" :size="14" class="arrow" />
              </view>
            </picker>
          </view>
          <view class="form-group flex1">
            <text class="label">紧急程度 <text class="req">*</text></text>
            <view class="urgency-row">
              <view v-for="it in urgencyLevels" :key="it.value" class="u-btn" :class="{ on: form.urgency === it.value }" @click="form.urgency = it.value">{{ it.label }}</view>
            </view>
          </view>
        </view>

        <view class="form-group">
          <text class="label">报修日期 <text class="req">*</text></text>
          <picker mode="date" :value="form.repairDate" @change="(e) => form.repairDate = e.detail.value">
            <view class="picker" :class="{ dim: !form.repairDate }">
              <text>{{ form.repairDate || '请选择日期' }}</text>
              <SvgIcon name="calendar" :size="16" class="arrow" />
            </view>
          </picker>
        </view>

        <view class="form-group">
          <text class="label">基本情况 <text class="req">*</text></text>
          <textarea class="textarea" v-model="form.description" placeholder="品牌型号、故障现象、期望维修时间等" placeholder-style="color:#CBD5E1" maxlength="500" :auto-height="true" />
          <text class="count">{{ form.description.length }}/500</text>
        </view>

        <view class="form-group">
          <text class="label">现场照片（选填）</text>
          <view class="img-row">
            <view v-for="(img, i) in images" :key="i" class="img-item" @click="previewImage(i)">
              <image :src="img" class="img" mode="aspectFill" />
              <view class="img-del" @click.stop="removeImage(i)"><SvgIcon name="x" :size="16" color="#fff" /></view>
            </view>
            <view v-if="images.length < 3" class="img-item img-add" @click="chooseImage">
              <SvgIcon name="plus" :size="36" color="#94A3B8" />
              <text class="add-text">添加</text>
            </view>
          </view>
        </view>

        <button class="btn-submit" :disabled="submitting" @click="handleSubmit">
          {{ submitting ? '提交中...' : '提交报修' }}
        </button>
      </view>
      <view class="safe-bottom" />
    </scroll-view>
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useRepairStore } from '@/stores/repair'
import { uploadFile } from '@/utils/request'
import SvgIcon from '@/components/SvgIcon.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'

const repairStore = useRepairStore()
const submitting = ref(false)
const images = ref([])
const deviceTypes = ['复印机', '打印机', '投影仪', '扫描仪', '电脑', '其他']
const urgencyLevels = [{ label: '紧急', value: 'urgent' }, { label: '一般', value: 'normal' }, { label: '不急', value: 'low' }]

const form = ref({ company: '', contactName: '', contactPhone: '', address: '', deviceType: '', urgency: 'normal', repairDate: '', description: '' })

const chooseImage = () => { uni.chooseImage({ count: 3 - images.value.length, sizeType: ['compressed'], sourceType: ['album', 'camera'], success: (res) => { images.value.push(...res.tempFilePaths) } }) }
const previewImage = (i) => { uni.previewImage({ urls: images.value, current: i }) }
const removeImage = (i) => { images.value.splice(i, 1) }

const validate = () => {
  const f = form.value
  if (!f.company.trim()) return uni.showToast({ title: '请填写报修单位', icon: 'none' }), false
  if (!f.contactName.trim()) return uni.showToast({ title: '请填写联系人', icon: 'none' }), false
  if (!f.contactPhone || !/^1\d{10}$/.test(f.contactPhone)) return uni.showToast({ title: '请填写正确手机号', icon: 'none' }), false
  if (!f.address.trim()) return uni.showToast({ title: '请填写用户地址', icon: 'none' }), false
  if (!f.repairDate) return uni.showToast({ title: '请选择日期', icon: 'none' }), false
  if (!f.description.trim()) return uni.showToast({ title: '请描述基本情况', icon: 'none' }), false
  return true
}

const handleSubmit = async () => {
  if (!validate()) return
  submitting.value = true
  try {
    const urls = []
    for (const img of images.value) { try { const r = await uploadFile(img); urls.push(r.data?.url || r.url || '') } catch {} }
    await repairStore.createRepair({ company: form.value.company.trim(), contactName: form.value.contactName.trim(), contactPhone: form.value.contactPhone, address: form.value.address.trim(), deviceType: form.value.deviceType, urgency: form.value.urgency, repairDate: form.value.repairDate, description: form.value.description.trim(), images: urls })
    uni.showToast({ title: '报修提交成功', icon: 'success' })
    setTimeout(() => { form.value = { company: '', contactName: '', contactPhone: '', address: '', deviceType: '', urgency: 'normal', repairDate: '', description: '' }; images.value = [] }, 800)
  } catch (e) { console.error(e) }
  finally { submitting.value = false }
}
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F8FAFC; display: flex; flex-direction: column; }
.scroll-body { flex: 1; }

.card { margin: 20rpx 24rpx; background: #fff; border-radius: 16rpx; padding: 32rpx; box-shadow: 0 2rpx 12rpx rgba(15,23,42,.06); }
.card-head { margin-bottom: 28rpx; }
.head-row { display: flex; align-items: center; gap: 8rpx; margin-bottom: 8rpx; }
.head-title { font-size: 30rpx; font-weight: 700; color: #020617; }
.head-desc { font-size: 24rpx; color: #64748B; display: block; }

.form-group { margin-bottom: 22rpx; }
.flex1 { flex: 1; }
.row { display: flex; gap: 16rpx; }
.label { font-size: 26rpx; color: #334155; font-weight: 500; margin-bottom: 8rpx; display: block; }
.req { color: #DC2626; }

.input { width: 100%; height: 80rpx; background: #F1F5F9; border-radius: 10rpx; padding: 0 20rpx; font-size: 28rpx; color: #334155; box-sizing: border-box; }
.picker { width: 100%; height: 80rpx; background: #F1F5F9; border-radius: 10rpx; padding: 0 20rpx; font-size: 28rpx; color: #334155; display: flex; align-items: center; justify-content: space-between; box-sizing: border-box; }
.dim { color: #CBD5E1; }
.arrow { color: #94A3B8; }

.urgency-row { display: flex; gap: 8rpx; }
.u-btn { flex: 1; height: 68rpx; line-height: 68rpx; text-align: center; font-size: 24rpx; border-radius: 8rpx; background: #F1F5F9; color: #64748B; transition: all .25s; }
.u-btn.on { background: #0F172A; color: #fff; font-weight: 600; }
.u-btn:active { transform: scale(.95); }

.textarea { width: 100%; min-height: 180rpx; background: #F1F5F9; border-radius: 10rpx; padding: 20rpx; font-size: 28rpx; color: #334155; box-sizing: border-box; }
.count { font-size: 22rpx; color: #94A3B8; text-align: right; display: block; margin-top: 4rpx; }

.img-row { display: flex; flex-wrap: wrap; gap: 16rpx; }
.img-item { width: 180rpx; height: 180rpx; border-radius: 12rpx; position: relative; overflow: hidden; }
.img { width: 100%; height: 100%; }
.img-del { position: absolute; top: 4rpx; right: 4rpx; width: 36rpx; height: 36rpx; border-radius: 50%; background: rgba(15,23,42,.6); display: flex; align-items: center; justify-content: center; }
.img-add { background: #F1F5F9; border: 2rpx dashed #CBD5E1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4rpx; }
.add-text { font-size: 20rpx; color: #94A3B8; }

.btn-submit { width: 100%; height: 92rpx; line-height: 92rpx; background: #0F172A; color: #fff; font-size: 30rpx; font-weight: 600; border: none; border-radius: 46rpx; margin-top: 12rpx; text-align: center; }
.btn-submit:active { opacity: .9; transform: scale(.97); }
.btn-submit[disabled] { background: #94A3B8; }

.safe-bottom { height: 32rpx; }
</style>
