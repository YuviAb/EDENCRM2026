import apiClient from './client'

export const photosApi = {
  listForClient: (clientId) =>
    apiClient.get(`/photos/client/${clientId}`).then((res) => res.data),

  upload: (clientId, file, { caption, appointmentId } = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    if (caption) formData.append('caption', caption)
    if (appointmentId) formData.append('appointment_id', appointmentId)

    return apiClient
      .post(`/photos/client/${clientId}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((res) => res.data)
  },

  delete: (photoId) => apiClient.delete(`/photos/${photoId}`),
}
