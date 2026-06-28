import apiClient from './client'

export const dashboardApi = {
  getToday: () => apiClient.get('/dashboard/today').then((r) => r.data),
}
