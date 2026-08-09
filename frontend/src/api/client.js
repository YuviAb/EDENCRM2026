import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ── בקשות יוצאות: מצרף את ה-JWT token ───────────────────────
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('eden_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── תגובות נכנסות: מחלץ שגיאה + מטפל ב-401 ─────────────────
apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('eden_token')
      window.location.href = '/login'
      return Promise.reject(error)
    }
    const data = error.response?.data
    if (data?.detail && typeof data.detail === 'string') {
      error.message = data.detail
    } else if (data?.error) {
      error.message = data.error
    }
    return Promise.reject(error)
  },
)

export default apiClient
