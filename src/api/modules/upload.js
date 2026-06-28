import request from '@/utils/request'

/**
 * 通用文件上传
 * @param {File} file - input / el-upload 获取到的 File 对象
 * @param {string} category - 'product' | 'news' | 'honor' | 'banner' | 'avatar' | 'logo' | 'common'
 * @returns Promise<{ url: string }>
 */
export function uploadFile(file, category = 'common') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)
  return request.post('/upload/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
