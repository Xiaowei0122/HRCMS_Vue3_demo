<template>
  <div class="product-management">
    <el-card shadow="never">
      <template #header>
        <div class="product-header">
          <div class="left-group">
            <el-button-group>
              <el-button :type="activeCat === 'all' ? 'primary' : ''" @click="switchCategory('all')">全部设备</el-button>
              <el-button :type="activeCat === 'color' ? 'primary' : ''" @click="switchCategory('color')">彩色办公</el-button>
              <el-button :type="activeCat === 'bw' ? 'primary' : ''" @click="switchCategory('bw')">高效黑白</el-button>
            </el-button-group>
          </div>
          <div class="right-group">
            <el-button type="success" icon="Download" @click="handleExport">导出库存</el-button>
            <el-button type="primary" icon="Plus" @click="openProductModal">新增设备录入</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20" v-loading="loading">
        <el-col :span="6" v-for="item in productList" :key="item.id" style="margin-bottom: 20px">
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
                <span>{{ item.speed }}</span> | <span>{{ item.function }}</span>
              </div>
              <div class="p-actions">
                <el-button size="small" icon="Edit" circle @click="editProduct(item)"></el-button>
                <el-button size="small" type="danger" icon="Delete" circle @click="handleDelete(item)"></el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑设备参数' : '设备详细参数录入'" width="800px" append-to-body>
      <el-form :model="productForm" label-width="100px" style="padding-top: 15px">
        <el-form-item label="设备型号">
          <el-input v-model="productForm.name" placeholder="例如：理光 Ricoh IM C3000" />
        </el-form-item>
        <el-form-item label="展示图片">
          <el-upload
            class="product-uploader"
            :show-file-list="false"
            :http-request="handleImgUpload"
          >
            <img v-if="productForm.img" :src="productForm.img" class="product-img-preview" />
            <el-icon v-else class="product-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="租赁价格">
              <el-input-number v-model="productForm.price" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设备库存">
              <el-input-number v-model="productForm.stock" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分类">
              <el-select v-model="productForm.category" style="width: 100%">
                <el-option label="彩色办公" value="color" />
                <el-option label="高效黑白" value="bw" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="速度">
              <el-input v-model="productForm.speed" placeholder="例如：30页/分" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="功能">
              <el-input v-model="productForm.function" placeholder="例如：打印/复印/扫描" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="技术参数">
          <el-table :data="techSpecs" border size="small">
            <el-table-column prop="attr" label="参数名" width="180">
              <template #default="{row}">
                <el-input v-model="row.attr" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="参数值">
              <template #default="{row}">
                <el-input v-model="row.val" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="scope">
                <el-button link type="danger" @click="techSpecs.splice(scope.$index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button size="small" icon="Plus" @click="techSpecs.push({ attr: '', val: '' })">添加参数</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">{{ isEdit ? '保存修改' : '保存并上架' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getProductList, createProduct, updateProduct, deleteProduct, exportProducts } from '@/api/modules/products'
import { uploadFile } from '@/api/modules/upload'

const activeCat = ref('all')
const dialogVisible = ref(false)
const loading = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const total = ref(0)
const query = reactive({ page: 1, size: 20, category: '', name: '' })

const productList = ref([])
const productForm = reactive({
  name: '', img: '', price: 299, stock: 10,
  speed: '', function: '', category: 'color'
})

const techSpecs = ref([])

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = { page: query.page, size: query.size }
    if (activeCat.value !== 'all') params.category = activeCat.value
    if (query.name) params.name = query.name
    const res = await getProductList(params)
    if (Array.isArray(res)) {
      productList.value = res
    } else {
      productList.value = res.records || []
      total.value = res.total || 0
    }
  } catch { /* ignore */ } finally {
    loading.value = false
  }
}

const switchCategory = (cat) => {
  activeCat.value = cat
  fetchProducts()
}

const openProductModal = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(productForm, { name: '', img: '', price: 299, stock: 10, speed: '', function: '', category: 'color' })
  techSpecs.value = []
  dialogVisible.value = true
}

const editProduct = (item) => {
  isEdit.value = true
  editingId.value = item.id
  Object.assign(productForm, {
    name: item.name || '',
    img: item.img || '',
    price: item.price || 0,
    stock: item.stock || 0,
    speed: item.speed || '',
    function: item.function || '',
    category: item.category || 'color'
  })
  // 后端 techSpecs 为字符串数组，这里拆成可编辑表格
  techSpecs.value = (item.techSpecs || []).map(spec => {
    const [attr, val] = String(spec).split(/[:：]/, 2)
    return { attr: attr || '', val: val || (attr ? '' : String(spec)) }
  })
  dialogVisible.value = true
}

const handleImgUpload = async ({ file, onSuccess, onError }) => {
  try {
    const res = await uploadFile(file, 'products')
    productForm.img = res.url
    onSuccess && onSuccess(res)
  } catch (e) {
    onError && onError(e)
  }
}

const saveProduct = async () => {
  if (!productForm.name.trim()) return ElMessage.warning('请输入设备型号')
  try {
    const payload = {
      ...productForm,
      // 将可编辑表格序列化为后端字符串数组
      techSpecs: techSpecs.value
        .filter(t => t.attr || t.val)
        .map(t => (t.attr && t.val ? `${t.attr}：${t.val}` : (t.attr || t.val)))
    }
    if (isEdit.value) {
      await updateProduct(editingId.value, payload)
      ElMessage.success('产品已更新')
    } else {
      await createProduct(payload)
      ElMessage.success('产品已上架')
    }
    dialogVisible.value = false
    fetchProducts()
  } catch { /* ignore */ }
}

const handleDelete = (item) => {
  ElMessageBox.confirm(`确定删除产品 [${item.name}] 吗？`, '确认删除', { type: 'warning' }).then(async () => {
    try {
      await deleteProduct(item.id)
      ElMessage.success('产品已删除')
      fetchProducts()
    } catch { /* ignore */ }
  }).catch(() => {})
}

const handleExport = async () => {
  try {
    const response = await exportProducts({ category: activeCat.value === 'all' ? '' : activeCat.value })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = 'products.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.product-item-card { transition: all 0.3s; cursor: pointer; position: relative; border-radius: var(--radius-md); }
.product-item-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
.image-wrapper { position: relative; background: var(--bg-muted); }
.tag-float { position: absolute; top: 10px; right: 10px; }
.p-title { font-weight: bold; font-size: 16px; margin-bottom: 8px; color: var(--text-primary); }
.p-price { color: var(--color-danger); margin-bottom: 8px; }
.p-price span { font-size: 20px; font-weight: bold; }
.p-specs { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
.p-actions { display: flex; justify-content: flex-end; gap: 8px; border-top: 1px solid #eee; padding-top: 10px; }

.product-uploader { width: 160px; }
.product-img-preview { width: 160px; height: 100px; object-fit: contain; border-radius: 4px; border: 1px solid var(--border-color); display: block; }
.product-uploader-icon { font-size: 28px; color: #8c939d; width: 160px; height: 100px; text-align: center; line-height: 100px; border: 1px dashed #d9d9d9; border-radius: 4px; }
</style>
