import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const KEY  = 'eden_token'

export const authApi = {
  login: async (username, password) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    const { data } = await axios.post(`${BASE}/auth/login`, form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem(KEY, data.access_token)
    return data
  },

  logout: () => {
    localStorage.removeItem(KEY)
  },

  getToken: ()         => localStorage.getItem(KEY),
  isAuthenticated: ()  => !!localStorage.getItem(KEY),
}
