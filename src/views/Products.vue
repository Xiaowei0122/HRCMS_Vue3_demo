<template>
  <div class="product-management">
    <el-card shadow="never">
      <template #header>
        <div class="product-header">
          <div class="left-group">
            <el-button-group>
              <el-button :type="activeCat === 'all' ? 'primary' : ''" @click="activeCat = 'all'">全部设备</el-button>
              <el-button :type="activeCat === 'color' ? 'primary' : ''" @click="activeCat = 'color'">彩色办公</el-button>
              <el-button :type="activeCat === 'bw' ? 'primary' : ''" @click="activeCat = 'bw'">高效黑白</el-button>
            </el-button-group>
          </div>
          <div class="right-group">
            <el-button type="success" icon="Download">导出库存</el-button>
            <el-button type="primary" icon="Plus" @click="openProductModal">新增设备录入</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6" v-for="(item, index) in productList" :key="index" style="margin-bottom: 20px">
          <el-card :body-style="{ padding: '0px' }" class="product-item-card">
            <div class="image-wrapper">
              <el-image :src="item.img" fit="contain" style="width: 100%; height: 180px" />
              <div class="tag-float">
                <el-tag effect="dark" :type="item.stock > 0 ? 'success' : 'danger'">
                  {{ item.stock > 0 ? '库存:' + item.stock : '缺货' }}
                </el-tag>
              </div>
            </div>
            <div style="padding: 14px">
              <div class="p-title">{{ item.name }}</div>
              <div class="p-price">
                <small>月租：</small><span>￥{{ item.price }}</span><small>/月起</small>
              </div>
              <div class="p-specs">
                <span>{{ item.speed }}页/分</span> | <span>{{ item.function }}</span>
              </div>
              <div class="p-actions">
                <el-button size="small" icon="Edit" circle @click="editProduct(item)"></el-button>
                <el-button size="small" type="warning" icon="Star" circle></el-button>
                <el-button size="small" type="danger" icon="Delete" circle></el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="dialogVisible" title="设备详细参数录入" width="800px">
      <el-tabs type="border-card">
        <el-tab-pane label="基本信息">
          <el-form label-width="100px" style="padding-top: 15px">
            <el-form-item label="设备型号"><el-input placeholder="例如：理光 Ricoh IM C3000" /></el-form-item>
            <el-form-item label="展示图片">
               <el-upload action="#" list-type="picture-card">
                  <el-icon><Plus /></el-icon>
               </el-upload>
            </el-form-item>
            <el-row>
              <el-col :span="12">
                <el-form-item label="租赁价格"><el-input-number v-model="tempPrice" /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="设备库存"><el-input-number v-model="tempStock" /></el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="技术参数">
          <el-table :data="techSpecs" border size="small">
            <el-table-column prop="attr" label="参数名" width="150" />
            <el-table-column label="参数值">
              <template #default="{row}">
                <el-input v-model="row.val" size="small" />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogVisible = false">保存并上架</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeCat = ref('all')
const dialogVisible = ref(false)
const tempPrice = ref(299)
const tempStock = ref(10)

const productList = ref([
  { name: '理光 IM C3000', price: 299, speed: '30', function: '彩印/复印/扫描', stock: 15, img: 'https://picsum.photos/300/300?random=21' },
  { name: '施乐 VersaLink C7020', price: 380, speed: '20', function: '高速彩印', stock: 8, img: 'https://picsum.photos/300/300?random=22' },
  { name: '佳能 iR-ADV C3525', price: 450, speed: '25', function: '智能办公', stock: 0, img: 'https://picsum.photos/300/300?random=23' },
  { name: '柯尼卡美能达 C226', price: 199, speed: '22', function: '黑白/彩色', stock: 20, img: 'https://picsum.photos/300/300?random=24' }
])

const techSpecs = ref([
  { attr: '打印分辨率', val: '1200 x 1200 dpi' },
  { attr: '首张复印时间', val: '4.5秒 (黑白)' },
  { attr: '预热时间', val: '21秒以下' },
  { attr: '内存容量', val: '2GB + 320GB 硬盘' }
])

const openProductModal = () => { dialogVisible.value = true }
</script>

<style scoped>
.product-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.product-item-card { transition: all 0.3s; cursor: pointer; position: relative; border-radius: 8px; }
.product-item-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
.image-wrapper { position: relative; background: #f9f9f9; }
.tag-float { position: absolute; top: 10px; right: 10px; }
.p-title { font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #303133; }
.p-price { color: #f56c6c; margin-bottom: 8px; }
.p-price span { font-size: 20px; font-weight: bold; }
.p-specs { font-size: 12px; color: #909399; margin-bottom: 12px; }
.p-actions { display: flex; justify-content: flex-end; gap: 8px; border-top: 1px solid #eee; padding-top: 10px; }
</style>