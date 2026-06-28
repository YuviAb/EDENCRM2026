import apiClient from './client'

export const paymentsApi = {
  list: (params) => apiClient.get('/payments/', { params }).then((res) => res.data),
  get: (id) => apiClient.get(`/payments/${id}`).then((res) => res.data),
  create: (data) => apiClient.post('/payments/', data).then((res) => res.data),
  update: (id, data) => apiClient.patch(`/payments/${id}`, data).then((res) => res.data),
  delete: (id) => apiClient.delete(`/payments/${id}`),
  getClientTotal: (clientId) =>
    apiClient.get(`/payments/client/${clientId}/total`).then((res) => res.data),
}
