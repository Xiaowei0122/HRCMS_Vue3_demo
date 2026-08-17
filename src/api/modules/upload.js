import request from '@/utils/request'

/**
 * 通用文件上传
 * @param {File} file - input / el-upload 获取到的 File 对象
 * @param {string} category - 'products' | 'news' | 'honors' | 'banners' | 'avatars' | 'logos'
 * @returns Promise<{ url: string, filename: string }>
 */
export function uploadFile(file, category = 'products') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)
  return request.post('/upload/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
