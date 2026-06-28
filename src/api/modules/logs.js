import request from '@/utils/request'

/** GET /logs?page=1&size=20&startDate=&endDate=&user= */
export function getLogList(params) {
  return request.get('/logs', { params })
}
