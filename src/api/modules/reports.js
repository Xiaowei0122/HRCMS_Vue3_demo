import request from '@/utils/request'

/** GET /reports/summary */
export function getReportSummary() {
  return request.get('/reports/summary')
}

/** GET /reports/repairs?months=6 */
export function getReportRepairs(params) {
  return request.get('/reports/repairs', { params })
}

/** GET /reports/cost?months=6 */
export function getReportCost(params) {
  return request.get('/reports/cost', { params })
}

/** GET /reports/leads */
export function getReportLeads() {
  return request.get('/reports/leads')
}

/** GET /reports/assets */
export function getReportAssets() {
  return request.get('/reports/assets')
}

/** GET /reports/satisfaction */
export function getReportSatisfaction() {
  return request.get('/reports/satisfaction')
}
