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

/** POST /finance/assets/import (multipart) */
export function importAssets(formData) {
  return request.post('/finance/assets/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
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

// ==================== 车辆管理 ====================

/** GET /finance/vehicles?status=&department=&kw=&page=&size= */
export function getVehicleList(params) {
  return request.get('/finance/vehicles', { params })
}

/** GET /finance/vehicles/expiring?days= */
export function getVehicleExpiring(params) {
  return request.get('/finance/vehicles/expiring', { params })
}

/** GET /finance/vehicles/:id */
export function getVehicleDetail(id) {
  return request.get(`/finance/vehicles/${id}`)
}

/** POST /finance/vehicles */
export function createVehicle(data) {
  return request.post('/finance/vehicles', data)
}

/** PUT /finance/vehicles/:id */
export function updateVehicle(id, data) {
  return request.put(`/finance/vehicles/${id}`, data)
}

/** DELETE /finance/vehicles/:id */
export function deleteVehicle(id) {
  return request.delete(`/finance/vehicles/${id}`)
}

/** POST /finance/vehicles/:id/insurances */
export function addInsurance(id, data) {
  return request.post(`/finance/vehicles/${id}/insurances`, data)
}

/** PUT /finance/vehicles/:id/insurances/:insId */
export function updateInsurance(id, insId, data) {
  return request.put(`/finance/vehicles/${id}/insurances/${insId}`, data)
}

/** DELETE /finance/vehicles/:id/insurances/:insId */
export function deleteInsurance(id, insId) {
  return request.delete(`/finance/vehicles/${id}/insurances/${insId}`)
}

/** POST /finance/vehicles/:id/maintenance */
export function addVehicleMaintenance(id, data) {
  return request.post(`/finance/vehicles/${id}/maintenance`, data)
}

/** DELETE /finance/vehicles/:id/maintenance/:mId */
export function deleteVehicleMaintenance(id, mId) {
  return request.delete(`/finance/vehicles/${id}/maintenance/${mId}`)
}

/** PUT /finance/vehicles/:id/inspection */
export function updateVehicleInspection(id, data) {
  return request.put(`/finance/vehicles/${id}/inspection`, data)
}
