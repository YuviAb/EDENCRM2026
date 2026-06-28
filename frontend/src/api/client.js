import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// מחלץ הודעת שגיאה ברורה מהפורמט האחיד של הבקבנד
apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
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
