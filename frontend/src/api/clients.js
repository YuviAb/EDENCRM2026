import apiClient from './client'

export const clientsApi = {
  list: (params) => apiClient.get('/clients/', { params }).then((r) => r.data),
  get: (id) => apiClient.get(`/clients/${id}`).then((r) => r.data),
  create: (data) => apiClient.post('/clients/', data).then((r) => r.data),
  update: (id, data) => apiClient.patch(`/clients/${id}`, data).then((r) => r.data),
  delete: (id, force = false) => apiClient.delete(`/clients/${id}`, { params: { force } }),
}
