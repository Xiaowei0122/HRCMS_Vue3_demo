import request from '@/utils/request'

/** GET /products?category=&page=1&size=10 */
export function getProductList(params) {
  return request.get('/products', { params })
}

/** GET /products/:id */
export function getProductDetail(id) {
  return request.get(`/products/${id}`)
}

/** POST /products */
export function createProduct(data) {
  return request.post('/products', data)
}

/** PUT /products/:id */
export function updateProduct(id, data) {
  return request.put(`/products/${id}`, data)
}

/** DELETE /products/:id */
export function deleteProduct(id) {
  return request.delete(`/products/${id}`)
}

/** GET /products/export  (blob) */
export function exportProducts(params) {
  return request.get('/products/export', { params, responseType: 'blob' })
}
