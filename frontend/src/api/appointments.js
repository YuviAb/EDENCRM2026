import apiClient from './client'

export const appointmentsApi = {
  list: (params) => apiClient.get('/appointments/', { params }).then((res) => res.data),
  get: (id) => apiClient.get(`/appointments/${id}`).then((res) => res.data),
  create: (data) => apiClient.post('/appointments/', data).then((res) => res.data),
  update: (id, data) => apiClient.patch(`/appointments/${id}`, data).then((res) => res.data),
  delete: (id) => apiClient.delete(`/appointments/${id}`),
}
