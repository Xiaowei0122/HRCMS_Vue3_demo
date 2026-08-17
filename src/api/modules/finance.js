import request from '@/utils/request'

// ==================== 共享文件 ====================

/** GET /finance/files?category=&page=&size= */
export function getFileList(params) {
  return request.get('/finance/files', { params })
}

/** POST /finance/files (multipart) */
export function uploadFile(formData) {
  return request.post('/finance/files', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/** PUT /finance/files/:id */
export function updateFileMeta(id, data) {
  return request.put(`/finance/files/${id}`, data)
}

/** DELETE /finance/files/:id */
export function deleteFile(id) {
  return request.delete(`/finance/files/${id}`)
}

/** PUT /finance/files/:id/permission */
export function updateFilePermission(id, data) {
  return request.put(`/finance/files/${id}/permission`, data)
}

// ==================== 资产管理 ====================

/** GET /finance/assets?category=&status=&page=&size= */
export function getAssetList(params) {
  return request.get('/finance/assets', { params })
}

/** POST /finance/assets */
export function createAsset(data) {
  return request.post('/finance/assets', data)
}

/** PUT /finance/assets/:id */
export function updateAsset(id, data) {
  return request.put(`/finance/assets/${id}`, data)
}

/** DELETE /finance/assets/:id */
export function deleteAsset(id) {
  return request.delete(`/finance/assets/${id}`)
}

/** PUT /finance/assets/:id/status */
export function updateAssetStatus(id, data) {
  return request.put(`/finance/assets/${id}/status`, data)
}

/** GET /finance/assets/:id/maintenance */
export function getMaintenanceRecords(id) {
  return request.get(`/finance/assets/${id}/maintenance`)
}

/** POST /finance/assets/:id/maintenance */
export function addMaintenanceRecord(id, data) {
  return request.post(`/finance/assets/${id}/maintenance`, data)
}
